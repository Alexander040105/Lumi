"""
Unified LLM client — Groq-only.

All LLM traffic routes through Groq. No Gemini support.

Env vars:
  GROQ_API_KEY        required
  GROQ_MODEL          default: llama-3.1-8b-instant
  GROQ_TEMPERATURE    default: 0.3
  GROQ_MAX_TOKENS     default: 4000
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

_repo_root = Path(__file__).resolve().parents[3]
load_dotenv(dotenv_path=_repo_root / ".env")

logger = logging.getLogger(__name__)


def generate_response(
    content: str,
    *,
    model: str | None = None,
    temperature: float | None = None,
    max_output_tokens: int | None = None,
    max_retries: int = 3,
    json_mode: bool = False,
) -> str:
    """
    Generate a response via Groq.

    Args:
        json_mode: If True, forces JSON output. Use False for plain-text
                   prompts (Ecosim, Chat, EnergyHub).
    """
    from app.services.groq_client import generate_groq_response
    return generate_groq_response(
        content,
        model=model,
        temperature=temperature,
        max_tokens=max_output_tokens,
        max_retries=max_retries,
        json_mode=json_mode,
    )


def parse_json_response(text: str) -> dict[str, Any]:
    """Parse a JSON response from the LLM."""
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
