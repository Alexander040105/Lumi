"""
Groq LLM client — free-tier alternative to Gemini.

Groq free tier (as of 2026):
  - 20 requests / minute
  - 200,000 tokens / minute
  - 500,000 tokens / day
  - 6,000 requests / day

Sign up at https://console.groq.com to get a free API key.

Model stack (updated July 2026 — llama-3.3-70b-versatile deprecated Aug 16, 2026):
  Primary: qwen/qwen3-32b (60 RPM, 500K TPD)
  Fallback 1: meta-llama/llama-4-scout-17b-16e-instruct (30K TPM, 500K TPD)
  Fallback 2: llama-3.1-8b-instant (14.4K RPD, fast)
  Emergency: openai/gpt-oss-120b (high quality, lower TPD)
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3-32b")
DEFAULT_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.3"))
DEFAULT_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "4000"))

# Free-tier Groq models — updated July 2026 after llama-3.3-70b-versatile deprecation
FALLBACK_GROQ_MODELS = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-120b",
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
                                "You are a friendly energy advisor speaking to a Filipino homeowner who has NO technical background. "
                                "You must always return valid JSON. Do not include markdown formatting, explanations, or anything outside the JSON object. "
                                "Rules for all text you generate inside the JSON:"
                                "\n- Use plain English. Avoid jargon. If you must use a technical term, explain it immediately in simple words."
                                "\n- Example: Instead of 'solar irradiance is 5.8 kWh/m²/day', say 'Your area gets plenty of sunlight — about 5.8 hours of strong sun each day, which is excellent for solar panels.'"
                                "\n- Example: Instead of 'capacity factor', say 'how efficiently the system runs compared to its best possible performance.'"
                                "\n- Always explain WHY something matters to the user's wallet or home."
                                "\n- Keep sentences short and conversational."
                                "\n- Use everyday comparisons: 'That's like leaving 10 light bulbs on all day.'"
                                "\n- Never assume the user knows what kWh, MW, GWh, or capacity factor mean."
                                "\n- If giving a number, always pair it with a plain-English interpretation."
                                "\n- The target audience includes teenagers and homeowners with zero engineering knowledge."
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
