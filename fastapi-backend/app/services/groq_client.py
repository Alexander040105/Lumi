"""
Groq LLM client — free-tier alternative to Gemini.

Groq free tier (as of 2025):
  - 20 requests / minute
  - 200,000 tokens / minute
  - 500,000 tokens / day
  - 6,000 requests / day

Sign up at https://console.groq.com to get a free API key.
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

DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
DEFAULT_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.3"))
DEFAULT_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "4000"))

# Free-tier Groq models that work well for structured JSON output
FALLBACK_GROQ_MODELS = [
    "llama-3.1-70b-versatile",
    "mixtral-8x7b-32768",
    "llama-3.1-8b-instant",
]

_groq_client: Any | None = None


def _get_groq_client() -> Any:
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY is not set")
            raise ValueError("GROQ_API_KEY is not set")
        try:
            from groq import Groq
        except ImportError as exc:
            raise ImportError("groq package is not installed. Run: pip install groq") from exc
        _groq_client = Groq(api_key=api_key)
    return _groq_client


def generate_groq_response(
    content: str,
    *,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    max_retries: int = 3,
) -> str:
    """
    Generate a response from Groq with retry + model fallback.
    Forces JSON output via response_format.
    """
    client = _get_groq_client()
    model_name = model or DEFAULT_GROQ_MODEL
    temp_value = DEFAULT_TEMPERATURE if temperature is None else temperature
    token_limit = DEFAULT_MAX_TOKENS if max_tokens is None else max_tokens

    models_to_try = [model_name]
    for fallback in FALLBACK_GROQ_MODELS:
        if fallback not in models_to_try:
            models_to_try.append(fallback)

    last_error: Exception | None = None

    for attempt_model in models_to_try:
        for attempt in range(1, max_retries + 1):
            try:
                logger.info("Groq attempt %s/%s on model=%s", attempt, max_retries, attempt_model)
                response = client.chat.completions.create(
                    model=attempt_model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful assistant that always returns "
                                "valid JSON. Do not include markdown formatting, "
                                "explanations, or anything outside the JSON object."
                            ),
                        },
                        {"role": "user", "content": content},
                    ],
                    temperature=temp_value,
                    max_tokens=token_limit,
                    response_format={"type": "json_object"},
                )
                text = response.choices[0].message.content or ""
                if text:
                    return text
                logger.warning("Groq returned empty content for model=%s", attempt_model)
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Groq model=%s attempt=%s failed: %s",
                    attempt_model,
                    attempt,
                    exc,
                )
                if attempt < max_retries:
                    import time
                    time.sleep(2 ** attempt)
                else:
                    logger.warning("Groq model=%s exhausted retries.", attempt_model)

    raise last_error or RuntimeError("All Groq models failed")
