"""RAG-powered chat backend for LUMI AI Assistant.

Endpoints:
    POST /chat           — send a message, get AI response
    GET  /chat/sessions  — list user's chat sessions
    GET  /chat/sessions/{id} — get messages for a session

Auth: Required for all endpoints. Chat is gated by plan limits.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import get_current_user_with_role_and_plan
from app.dependencies.plan_limits import (
    check_feature_access,
    get_plan_limits,
    increment_usage,
)
from app.services.supabase_service import get_supabase_client

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
    """Call the existing RAG pipeline to retrieve relevant chunks."""
    try:
        from app.services.rag_pipeline import retrieve_context
        return retrieve_context(query=query, top_k=top_k)
    except Exception as exc:
        logger.warning("RAG retrieval failed: %s", exc)
        return []


def _generate_response(prompt: str) -> str:
    """Generate a chat response via the unified LLM client (Groq-only)."""
    try:
        from app.services.llm_client import generate_response as llm_generate
        system_prompt = (
            "You are LUMI, a Renewable Energy Decision Support Assistant for the Philippines.\n\n"
            "CRITICAL INSTRUCTION — FOLLOW THIS EXACT ORDER:\n"
            "STEP 1: Check if the user's message is ONLY a greeting (hello, hi, good morning, how are you, etc.). If YES, respond warmly and normally.\n"
            "STEP 2: If the message contains ANY question or topic completely unrelated to energy, climate, the Philippines, or sustainability (e.g., sports, celebrities, cooking, gaming), you MUST decline with ONLY this exact response — do NOT answer the question, do NOT use context:\n"
            '"I\'m LUMI, a Renewable Energy Decision Support Assistant for the Philippines. I\'m not able to help with that topic. Let me know if you have questions about solar, wind, geothermal, energy policy, or sustainability!"\n'
            "STEP 3: If the question IS about the Philippines — including its geography, climate, weather, temperature, or general environment — treat it as on-topic because climate knowledge is essential for renewable-energy decisions. Answer using the Retrieved Context and your general knowledge.\n"
            "STEP 4: Only if the question IS about renewable energy, energy policy, solar, wind, geothermal, hydro, biomass, energy efficiency, power grids, electricity, climate change, sustainability, or the Philippines energy sector, then answer using ONLY the provided Retrieved Context below.\n"
            "STEP 5: If the Retrieved Context does not contain the answer, say so clearly.\n"
            "STEP 6: Cite sources using [Source N: Title] notation (e.g., [Source 1: DOE Renewable Energy Plan]).\n"
            "STEP 7: Answer in plain text (not JSON)."
        )
        text = llm_generate(
            system_prompt + "\n\n" + prompt,
            model="llama-3.1-8b-instant",
            temperature=0.5,
            max_output_tokens=1024,
            json_mode=False,
        )
        return text.strip()
    except Exception as exc:
        logger.warning("LLM chat generation failed: %s", exc)
        return "I'm sorry, I couldn't generate a response at this time. Our AI service is temporarily unavailable — please try again later."


def _persist_chat_message(
    user_id: str,
    session_id: str | None,
    role: str,
    content: str,
    sources: list[dict] | None = None,
) -> str | None:
    """Persist a chat message to the database and return the message ID."""
    if not user_id:
        return None
    client = get_supabase_client()
    try:
        if not session_id:
            session_resp = client.table("chat_sessions").insert({
                "user_id": user_id,
                "title": content[:50] + "..." if len(content) > 50 else content,
            }).execute()
            session_id = session_resp.data[0]["id"] if session_resp.data else None

        msg_resp = client.table("chat_messages").insert({
            "session_id": session_id,
            "role": role,
            "content": content,
            "sources_json": sources or [],
        }).execute()
        return msg_resp.data[0]["id"] if msg_resp.data else None
    except Exception as exc:
        logger.warning("Failed to persist chat message: %s", exc)
        return None


@router.post("/")
async def chat_message(
    payload: dict,
    user: dict = Depends(get_current_user_with_role_and_plan),
) -> dict[str, Any]:
    """Receive a chat message, run RAG retrieval, generate AI response, and persist.

    Payload:
        message: str (required)
        session_id: str | None (optional; creates new session if omitted)
    """
    message_text = payload.get("message", "").strip()

    if not message_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message is required")

    user_id = user.get("sub")
    plan = user.get("plan", "free")

    # Plan limit check
    access = check_feature_access(user, "chat")
    if not access["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": access["message"],
                "limit": access["limit"],
                "used": access["limit"] - access["remaining"],
                "remaining": access["remaining"],
                "upgrade": True,
            },
        )

    session_id = payload.get("session_id")

    # Retrieve context
    chunks = _retrieve_context(message_text)

    # Build prompt and generate
    prompt = _build_chat_prompt(message_text, chunks)

    # Premium users get slightly faster/optimized generation
    limits_data = get_plan_limits(plan)
    features = limits_data.get("features", {})
    priority = features.get("priority_response", False)
    temperature = 0.3 if priority else 0.5
    max_tokens = 1200 if priority else 1024

    response_text = _generate_response(prompt, temperature=temperature, max_output_tokens=max_tokens)

    # Persist messages
    _persist_chat_message(user_id, session_id, "user", message_text)
    msg_id = _persist_chat_message(user_id, session_id, "assistant", response_text, chunks)

    # Log usage
    increment_usage(
        user_id=user_id,
        feature_type="chat",
        tokens_input=2850,
        tokens_output=300,
        metadata={"session_id": session_id, "message_id": msg_id},
    )

    return {
        "session_id": session_id,
        "role": "assistant",
        "message": response_text,
        "retrieved_chunks": chunks,
        "remaining_messages": access["remaining"] - 1,
        "plan": plan,
    }


@router.get("/sessions")
async def list_sessions(
    user: dict = Depends(get_current_user_with_role_and_plan),
) -> dict[str, Any]:
    """List all chat sessions for the authenticated user."""
    user_id = user.get("sub")
    client = get_supabase_client()
    try:
        resp = (
            client.table("chat_sessions")
            .select("id, title, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return {"sessions": resp.data or []}
    except Exception as exc:
        logger.warning("Failed to list chat sessions: %s", exc)
        return {"sessions": []}


@router.get("/sessions/{session_id}")
async def get_session_messages(
    session_id: str,
    user: dict = Depends(get_current_user_with_role_and_plan),
) -> dict[str, Any]:
    """Get all messages for a specific chat session (owner only)."""
    user_id = user.get("sub")
    client = get_supabase_client()
    try:
        # Verify ownership
        sess_resp = (
            client.table("chat_sessions")
            .select("id")
            .eq("id", session_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        if not sess_resp.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or access denied",
            )

        msg_resp = (
            client.table("chat_messages")
            .select("id, role, content, sources_json, created_at")
            .eq("session_id", session_id)
            .order("created_at")
            .execute()
        )
        return {"messages": msg_resp.data or []}
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Failed to get session messages: %s", exc)
        return {"messages": []}
