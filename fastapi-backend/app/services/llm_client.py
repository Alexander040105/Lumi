"""
Unified LLM client.

Switch provider via the ``LLM_PROVIDER`` environment variable:
  - ``gemini``  (default) — uses Google Gemini with retry + model fallback
  - ``groq``    — uses Groq free tier (llama-3.3-70b, mixtral, etc.)

Env vars:
  LLM_PROVIDER        gemini | groq
  GEMINI_API_KEY      required if provider=gemini
  GROQ_API_KEY        required if provider=groq
  GEMINI_MODEL        default: gemini-2.5-flash
  GROQ_MODEL          default: llama-3.3-70b-versatile
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower().strip()


def generate_response(
    content: str,
    *,
    model: str | None = None,
    temperature: float | None = None,
    max_output_tokens: int | None = None,
    max_retries: int = 3,
) -> str:
    """
    Generate a response from the configured LLM provider.

    Drop-in replacement for ``generate_gemini_response``.

    If the configured provider is Gemini and *all* Gemini models fail,
    we automatically fall back to Groq when GROQ_API_KEY is present.
    """
    if LLM_PROVIDER == "groq":
        from app.services.groq_client import generate_groq_response
        return generate_groq_response(
            content,
            model=model,
            temperature=temperature,
            max_tokens=max_output_tokens,
            max_retries=max_retries,
        )

    # Default: Gemini (with built-in retry + model fallback)
    from app.services.gemini_funcs import generate_gemini_response
    try:
        return generate_gemini_response(
            content,
            model=model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            max_retries=max_retries,
        )
    except Exception:
        # All Gemini models failed — try Groq as emergency fallback
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            logger.warning(
                "All Gemini models failed; falling back to Groq emergency path."
            )
            from app.services.groq_client import generate_groq_response
            return generate_groq_response(
                content,
                model=None,
                temperature=temperature,
                max_tokens=max_output_tokens,
                max_retries=max_retries,
            )
        raise


def parse_json_response(text: str) -> dict[str, Any]:
    """Parse a JSON response — works for both Gemini and Groq."""
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        import re
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON block from LLM response")
        return {}
