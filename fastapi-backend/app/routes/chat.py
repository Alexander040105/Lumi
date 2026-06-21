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

from fastapi import APIRouter, HTTPException, status

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
    """Call Groq directly (no Gemini, no JSON mode) for fast chat responses."""
    import os
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY is not set")
        return "I'm sorry, I couldn't generate a response at this time. Our AI service is temporarily unavailable — please try again later."

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": (
                    "You are LUMI, a Renewable Energy Decision Support Assistant for the Philippines.\n\n"
                    "CRITICAL INSTRUCTION — FOLLOW THIS EXACT ORDER:\n"
                    "STEP 1: Check if the user's message is ONLY a greeting (hello, hi, good morning, how are you, etc.). If YES, respond warmly and normally.\n"
                    "STEP 2: If the message contains ANY question or topic unrelated to energy, climate, or sustainability, you MUST decline with ONLY this exact response — do NOT answer the question, do NOT use context:\n"
                    '\"I\'m LUMI, a Renewable Energy Decision Support Assistant for the Philippines. I\'m not able to help with that topic. Let me know if you have questions about solar, wind, geothermal, energy policy, or sustainability!\"\n'
                    "STEP 3: Only if the question IS about renewable energy, energy policy, solar, wind, geothermal, hydro, biomass, energy efficiency, power grids, electricity, climate change, sustainability, or the Philippines energy sector, then answer using ONLY the provided Retrieved Context below.\n"
                    "STEP 4: If the Retrieved Context does not contain the answer, say so clearly.\n"
                    "STEP 5: Cite sources using [Source N: Title] notation (e.g., [Source 1: DOE Renewable Energy Plan]).\n"
                    "STEP 6: Answer in plain text (not JSON)."
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
) -> dict[str, Any]:
    """Receive a chat message, run RAG retrieval, generate AI response, and persist.

    Payload:
        message: str (required)
        session_id: str | None (optional; creates new session if omitted)
    """
    message_text = payload.get("message", "").strip()

    if not message_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message is required")

    # NOTE: persistence skipped in MVP public mode (no user_id without auth)
    session_id = None

    # Retrieve context (RAG) — gracefully falls back to empty list if RAG is unavailable
    chunks = _retrieve_context(message_text)
    rag_used = bool(chunks)

    # Build prompt and generate
    prompt = _build_chat_prompt(message_text, chunks)
    response_text = _generate_response(prompt)

    return {
        "session_id": session_id,
        "role": "assistant",
        "message": response_text,
        "rag_used": rag_used,
        "retrieved_chunks": chunks,
    }


@router.get("/sessions")
async def list_sessions() -> dict[str, Any]:
    """List all chat sessions (MVP public — returns empty)."""
    return {"sessions": []}


@router.get("/sessions/{session_id}")
async def get_session_messages(session_id: str) -> dict[str, Any]:
    """Get all messages for a specific chat session (MVP public — returns empty)."""
    return {"messages": []}
