"""RAG-powered chat backend for LUMI AI Assistant.

Endpoints:
    POST /chat           — send a message, get AI response
    GET  /chat/sessions  — list user's chat sessions
    GET  /chat/sessions/{id} — get messages for a session
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import get_current_user_with_role_and_plan
from app.dependencies.quota import check_authenticated_usage

logger = logging.getLogger(__name__)
router = APIRouter()


def _build_chat_prompt(query: str, chunks: list[dict], user_context: dict | None = None) -> str:
    """Assemble the user prompt with retrieved context and source metadata."""
    def _source_label(i: int, chunk: dict) -> str:
        srcs = chunk.get("sources", [])
        if srcs and isinstance(srcs[0], dict):
            title = srcs[0].get("title") or srcs[0].get("name") or ""
            url = srcs[0].get("url") or ""
            if title:
                return f"[Source {i+1}: {title}]"
        return f"[Source {i+1}]"

    context_lines = []
    for i, c in enumerate(chunks):
        label = _source_label(i, c)
        text = c.get("text", "").strip()
        context_lines.append(f"{label}\n{text}")

    sections = [
        "Retrieved Context:",
        "\n\n".join(context_lines) or "(No relevant documents found.)",
    ]

    if user_context:
        sections.extend([
            "",
            "User Context:",
            json.dumps(user_context, indent=2, ensure_ascii=False),
        ])

    sections.extend(["", f"User Question: {query}"])
    return "\n".join(sections)


def _retrieve_context(query: str, top_k: int = 5) -> list[dict]:
    """Hybrid retrieval: semantic + keyword search with reranking."""
    try:
        from app.services.rag_hybrid import hybrid_search, rerank_results
        results = hybrid_search(query, top_k=top_k * 2)
        results = rerank_results(query, results, top_k=top_k)
        return results
    except Exception as exc:
        logger.warning("Hybrid RAG retrieval failed, falling back to semantic: %s", exc)
        try:
            from app.services.rag_pipeline import retrieve_context
            return retrieve_context(query=query, top_k=top_k)
        except Exception as exc2:
            logger.warning("Semantic RAG retrieval also failed: %s", exc2)
            return []


def _generate_response(prompt: str) -> str:
    """Call Groq directly (no Gemini, no JSON mode) for fast chat responses."""
    try:
        from app.services.groq_client import _get_groq_client
        client = _get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": (
                    "You are LUMI, a Renewable Energy Decision Support Assistant for the Philippines.\n\n"
                    "CRITICAL INSTRUCTION — FOLLOW THIS EXACT ORDER:\n"
                    "STEP 1: Check if the user's message is ONLY a greeting (hello, hi, good morning, how are you, etc.). If YES, respond warmly and normally.\n"
                    "STEP 2: If the message contains ANY question or topic completely unrelated to energy, climate, the Philippines, or sustainability (e.g., sports, celebrities, cooking, gaming), you MUST decline with ONLY this exact response — do NOT answer the question, do NOT use context:\n"
                    '\"I\'m LUMI, a Renewable Energy Decision Support Assistant for the Philippines. I\'m not able to help with that topic. Let me know if you have questions about solar, wind, geothermal, energy policy, or sustainability!\"\n'
                    "STEP 3: If the question IS about the Philippines — including its geography, climate, weather, temperature, or general environment — treat it as on-topic because climate knowledge is essential for renewable-energy decisions. Answer using the Retrieved Context and your general knowledge.\n"
                    "STEP 4: Only if the question IS about renewable energy, energy policy, solar, wind, geothermal, hydro, biomass, energy efficiency, power grids, electricity, climate change, sustainability, or the Philippines energy sector, then answer using ONLY the provided Retrieved Context below.\n"
                    "STEP 5: If the Retrieved Context does not contain the answer, say so clearly.\n"
                    "STEP 6: Cite sources using [Source N: Title] notation (e.g., [Source 1: DOE Renewable Energy Plan]).\n"
                    "STEP 7: Answer in plain text (not JSON)."
                )},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=1024,
        )
        text = response.choices[0].message.content or ""
        return text.strip()
    except Exception as exc:
        logger.warning("Groq chat generation failed: %s", exc)
        return "I'm sorry, I couldn't generate a response at this time. Our AI service is temporarily unavailable — please try again later."


@router.post("/")
async def chat_message(
    payload: dict,
    user: dict = Depends(get_current_user_with_role_and_plan),
) -> dict[str, Any]:
    """Receive a chat message, run hybrid RAG retrieval, generate AI response.

    Includes input guardrails, hybrid search + reranking, citation verification,
    output sanitization, and chat history persistence.

    Payload:
        message: str (required)
        session_id: str | None (optional; creates new session if omitted)
    """
    await check_authenticated_usage(user, action="chat_message")
    from app.services.rag_hybrid import (
        validate_input,
        sanitize_output,
        verify_citations,
        save_chat_message,
        create_chat_session,
        get_chat_history,
    )

    message_text = payload.get("message", "").strip()

    if not message_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message is required")

    # Input guardrails
    is_valid, error_msg = validate_input(message_text)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    # Session management
    session_id = payload.get("session_id")
    if not session_id:
        session_id = create_chat_session()

    # Save user message
    if session_id:
        save_chat_message(session_id, "user", message_text)

    # Retrieve context with hybrid search + reranking
    chunks = _retrieve_context(message_text)

    # Build prompt with chat history for multi-turn context
    history = get_chat_history(session_id, limit=10) if session_id else []
    prompt = _build_chat_prompt(message_text, chunks)

    # Generate response
    response_text = _generate_response(prompt)

    # Output sanitization
    response_text = sanitize_output(response_text)

    # Citation verification
    citation_result = verify_citations(response_text, chunks) if chunks else None

    # Save assistant message
    if session_id:
        save_chat_message(
            session_id,
            "assistant",
            response_text,
            retrieved_chunks=chunks,
            citation_verification=citation_result,
        )

    return {
        "session_id": session_id,
        "role": "assistant",
        "message": response_text,
        "retrieved_chunks": chunks,
        "citations": citation_result,
    }


@router.get("/sessions")
async def list_sessions(user: dict = Depends(get_verified_user)) -> dict[str, Any]:
    """List recent chat sessions for the authenticated user."""
    try:
        from app.services.supabase_service import get_supabase_client
        client = get_supabase_client()
        resp = (
            client.table("chat_sessions")
            .select("id,created_at")
            .eq("user_id", user.get("sub"))
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )
        return {"sessions": resp.data or []}
    except Exception as exc:
        logger.warning("Failed to list chat sessions: %s", exc)
        return {"sessions": []}


@router.get("/sessions/{session_id}")
async def get_session_messages(
    session_id: str,
    user: dict = Depends(get_verified_user),
) -> dict[str, Any]:
    """Get all messages for a specific chat session (owner only)."""
    from app.services.supabase_service import get_supabase_client
    from app.services.rag_hybrid import get_chat_history

    # Verify session ownership
    client = get_supabase_client()
    try:
        resp = (
            client.table("chat_sessions")
            .select("user_id")
            .eq("id", session_id)
            .single()
            .execute()
        )
        if not resp.data or resp.data.get("user_id") != user.get("sub"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Failed to verify session ownership: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve session")

    messages = get_chat_history(session_id, limit=50)
    return {"messages": messages}
