import asyncio
import json
import logging
import os
import re
import time
from typing import Any

from google import genai
from google.genai import errors as genai_errors

logger = logging.getLogger(__name__)

DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DEFAULT_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.3"))
DEFAULT_MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "3000"))
GEMINI_DEBUG = os.getenv("GEMINI_DEBUG", "false").lower() in {"1", "true", "yes"}
if GEMINI_DEBUG:
    logger.setLevel(logging.INFO)

# Fallback chain when the primary model is overloaded.
# Verified working models for this API version / key:
#   gemini-2.5-flash   -> works but often 503
#   gemini-2.0-flash   -> works but may 429 (rate limit)
# Others (1.5-flash, 1.5-flash-8b, 1.5-pro) return 404 for v1beta.
FALLBACK_GEMINI_MODELS = [
    "gemini-2.0-flash",
]

_client: genai.Client | None = None


def _get_gemini_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY is not set")
            raise ValueError("GEMINI_API_KEY is not set")
        _client = genai.Client(api_key=api_key)
    return _client


def _generate_once(
    client: genai.Client,
    model_name: str,
    content: str,
    config: Any,
) -> str:
    """Single Gemini call — no retry logic here."""
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=content,
            config=config,
        )
    except TypeError:
        response = client.models.generate_content(
            model=model_name,
            contents=content,
        )

    if GEMINI_DEBUG:
        finish_reasons = []
        for candidate in getattr(response, "candidates", None) or []:
            finish_reasons.append(getattr(candidate, "finish_reason", None))
        logger.info("Gemini finish_reasons=%s", finish_reasons)

    text = getattr(response, "text", "") or ""
    if text:
        return text

    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content_obj = getattr(candidate, "content", None)
        parts = getattr(content_obj, "parts", None) or []
        for part in parts:
            part_text = getattr(part, "text", "")
            if part_text:
                return part_text

    if GEMINI_DEBUG:
        finish_reasons = []
        for candidate in candidates:
            finish_reasons.append(getattr(candidate, "finish_reason", None))
        logger.warning("Gemini returned an empty response; finish_reasons=%s", finish_reasons)
    else:
        logger.warning("Gemini returned an empty response")
    return ""


def generate_gemini_response(
    content: str,
    *,
    model: str | None = None,
    temperature: float | None = None,
    max_output_tokens: int | None = None,
    max_retries: int = 3,
) -> str:
    """
    Generate a response from Gemini with retry + model fallback.

    If the primary model returns 503 UNAVAILABLE, we retry with exponential
    backoff and then fall back to less-loaded free models.
    """
    client = _get_gemini_client()
    model_name = model or DEFAULT_GEMINI_MODEL
    temp_value = DEFAULT_TEMPERATURE if temperature is None else temperature
    token_limit = DEFAULT_MAX_OUTPUT_TOKENS if max_output_tokens is None else max_output_tokens

    try:
        config = genai.types.GenerateContentConfig(
            temperature=temp_value,
            max_output_tokens=token_limit,
            response_mime_type="text/plain",
        )
    except AttributeError:
        config = {
            "temperature": temp_value,
            "max_output_tokens": token_limit,
            "response_mime_type": "text/plain",
        }

    # Build the full fallback chain: primary -> fallback models
    models_to_try = [model_name]
    for fallback in FALLBACK_GEMINI_MODELS:
        if fallback not in models_to_try:
            models_to_try.append(fallback)

    last_error: Exception | None = None

    for attempt_model in models_to_try:
        for attempt in range(1, max_retries + 1):
            try:
                if GEMINI_DEBUG:
                    logger.info(
                        "Gemini attempt %s/%s on model=%s",
                        attempt,
                        max_retries,
                        attempt_model,
                    )
                return _generate_once(client, attempt_model, content, config)
            except genai_errors.ServerError as exc:
                last_error = exc
                # 503 / 529 — back off and retry
                if attempt < max_retries:
                    wait = 2 ** attempt  # 2, 4, 8 seconds
                    logger.warning(
                        "Gemini model=%s attempt=%s failed (%s). "
                        "Retrying in %ss...",
                        attempt_model,
                        attempt,
                        exc,
                        wait,
                    )
                    time.sleep(wait)
                else:
                    logger.warning(
                        "Gemini model=%s exhausted all %s retries.",
                        attempt_model,
                        max_retries,
                    )
            except genai_errors.ClientError as exc:
                last_error = exc
                code = getattr(exc, "code", None)
                # 429 RESOURCE_EXHAUSTED is transient — retry it
                if code == 429 and attempt < max_retries:
                    wait = 2 ** attempt
                    logger.warning(
                        "Gemini model=%s rate-limited (429). "
                        "Retrying in %ss...",
                        attempt_model,
                        wait,
                    )
                    time.sleep(wait)
                else:
                    logger.error(
                        "Gemini model=%s client error: %s",
                        attempt_model,
                        exc,
                    )
                    break
            except Exception as exc:
                # Non-retryable error (auth, bad request, etc.)
                last_error = exc
                logger.error(
                    "Gemini model=%s non-retryable error: %s",
                    attempt_model,
                    exc,
                )
                break

    # All models exhausted
    raise last_error or RuntimeError("All Gemini models failed")


def _extract_json_block(text: str) -> str | None:
    if not text:
        return None
    match = re.search(r"\{[\s\S]*\}", text)
    return match.group(0) if match else None


def parse_gemini_json_response(text: str) -> dict[str, Any]:
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        json_block = _extract_json_block(text)
        if json_block:
            try:
                return json.loads(json_block)
            except json.JSONDecodeError:
                logger.warning("Failed to parse Gemini JSON block")
        return {}


def _extract_summary(text: str) -> str:
    match = re.search(r"\"summary\"\s*:\s*\"([\s\S]*?)\"", text)
    if match:
        return match.group(1).strip()
    return text.strip()


def _normalize_analysis_output(data: dict[str, Any]) -> dict[str, Any]:
    output = {
        "summary": "",
        "renewable_analysis": {
            "solar": "",
            "wind": "",
            "hydro": "",
            "geothermal": "",
        },
        "recommendation": {
            "best_option": "",
            "reason": "",
        },
        "cost_estimation": {
            "solar": {},
            "wind": {},
            "hydro": {},
            "geothermal": {},
        },
        "environmental_impact": "",
    }

    if not isinstance(data, dict):
        return output

    output.update({k: v for k, v in data.items() if k in output})

    if isinstance(data.get("renewable_analysis"), dict):
        output["renewable_analysis"].update(data["renewable_analysis"])

    if isinstance(data.get("recommendation"), dict):
        output["recommendation"].update(data["recommendation"])

    if isinstance(data.get("cost_estimation"), dict):
        output["cost_estimation"].update(data["cost_estimation"])

    return output


def _build_renewable_analysis_prompt(analysis_payload: dict[str, Any]) -> str:
    # Extract nearby plants so they appear at the top of the prompt
    nearby_plants = analysis_payload.pop("nearby_geothermal_plants", None)
    payload = json.dumps(analysis_payload, ensure_ascii=True, indent=2)

    plant_context = ""
    if nearby_plants:
        lines = []
        for p in nearby_plants[:5]:
            lines.append(
                f"- {p.get('project_name', 'Unknown')} ({p.get('capacity_mw', '?')} MW, "
                f"{p.get('technology', 'unknown')}, {p.get('status', 'unknown')}) — "
                f"{p.get('distance_km', '?')} km away"
            )
        plant_context = (
            "IMPORTANT CONTEXT: This municipality is near the following operating geothermal power plant(s):\n"
            + "\n".join(lines)
            + "\n\n"
        )

    return (
        "You are LUMI, an environmental intelligence assistant helping Filipino households choose renewable energy. "
        "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
        + plant_context
        + "CRITICAL RULES:\n"
        "- Use ONLY markdown headers (## Section Name) to separate sections.\n"
        "- Write in short, clear paragraphs suitable for non-technical users.\n"
        "- Use bullet points (dash + space) for lists, not long walls of text.\n"
        "- NEVER skip any renewable type (solar, wind, hydro, geothermal).\n"
        "- Do NOT use JSON, code blocks, or raw data dumps.\n\n"
        "STRUCTURE YOUR RESPONSE IN THESE EXACT SECTIONS (use ## headers):\n\n"
        "## Observation\n"
        "2-3 sentences describing the municipality's climate: temperature, humidity, solar irradiance, wind speed, rainfall, elevation.\n\n"
        "## Interpretation\n"
        "For EACH renewable source, write ONE short paragraph (2-3 sentences max):\n"
        "- **Solar**: Explain if the irradiance and cloud cover make solar viable.\n"
        "- **Wind**: Explain if the wind speed is strong enough for turbines.\n"
        "- **Hydro**: Explain if rainfall and elevation support micro-hydro.\n"
        "- **Geothermal**: Explain if subsurface heat indicators are present.\n\n"
        "## Recommendation\n"
        "State the BEST renewable option for this household. Then give 3-4 BULLET POINTS of SPECIFIC, ACTIONABLE advice:\n"
        "- What size or type of system to install (e.g., '4-panel 400W rooftop solar')\n"
        "- Estimated monthly generation and what % of their bill it covers\n"
        "- Rough installation cost range in PHP\n"
        "- First step they should take (e.g., 'Contact a DOE-accredited solar installer for site assessment')\n"
        "- Any permit or net-metering application they should file\n\n"
        "## Reason\n"
        "Briefly compare the top 2-3 options. Explain why the recommended one wins and why the others are less suitable, using the actual numbers.\n\n"
        "SIMULATION DATA:\n"
        f"{payload}\n"
    )


def analyze_renewable_results(analysis_payload: dict[str, Any]) -> dict[str, Any]:
    try:
        prompt = _build_renewable_analysis_prompt(analysis_payload)
        # Use unified client so Groq fallback works when Gemini is rate-limited
        from app.services.llm_client import generate_response
        from app.services.llm_sanitizer import sanitize_llm_output, extract_prescriptive_recommendation

        response_text = generate_response(prompt)
        if GEMINI_DEBUG:
            snippet = response_text[:500] if response_text else ""
            logger.info("Gemini prompt chars=%s response chars=%s", len(prompt), len(response_text))
            logger.info("Gemini response snippet=%s", snippet)

        cleaned = sanitize_llm_output(response_text)
        if not cleaned:
            logger.warning("LLM returned empty response after sanitization")
            return _normalize_analysis_output({})

        prescriptive = extract_prescriptive_recommendation(cleaned)

        return {
            "summary": cleaned,
            "renewable_analysis": {"solar": "", "wind": "", "hydro": "", "geothermal": ""},
            "recommendation": {
                "best_option": prescriptive.get("recommendation", ""),
                "reason": prescriptive.get("reason", ""),
            },
            "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}, "geothermal": {}},
            "environmental_impact": "",
            "prescriptive_recommendation": prescriptive,
        }
    except Exception as exc:
        logger.exception("LLM analysis failed")
        return {
            "summary": "LLM analysis failed.",
            "renewable_analysis": {"solar": "", "wind": "", "hydro": "", "geothermal": ""},
            "recommendation": {"best_option": "", "reason": ""},
            "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}, "geothermal": {}},
            "environmental_impact": "",
            "error": str(exc),
        }


async def analyze_renewable_results_async(
    analysis_payload: dict[str, Any],
) -> dict[str, Any]:
    return await asyncio.to_thread(analyze_renewable_results, analysis_payload)