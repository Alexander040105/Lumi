import asyncio
import hashlib
import json
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from datetime import datetime, timedelta, timezone
from typing import Any

from app.services.data_cache import cache_get_sync, cache_set_sync


def _import_genai():
    """Lazy import google-genai so Vercel can omit it when not in use."""
    try:
        from google import genai
    except ImportError as exc:
        raise ImportError(
            "google-genai is not installed. Set LLM_PROVIDER=groq or install google-genai."
        ) from exc
    return genai


def _import_genai_errors():
    """Lazy import google-genai error classes."""
    try:
        from google.genai import errors
    except ImportError as exc:
        raise ImportError(
            "google-genai is not installed. Set LLM_PROVIDER=groq or install google-genai."
        ) from exc
    return errors

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

# EcoSim AI analysis cache settings.
# Cache successful analyses for 7 days and cap the LLM call at 5 seconds
# so Vercel's 10-second function limit is never breached.
_AI_CACHE_TTL = int(os.getenv("ECOSIM_AI_CACHE_TTL", "604800"))  # 7 days
_AI_CACHE_VERSION = os.getenv("ECOSIM_AI_CACHE_VERSION", "v2")
_AI_CALL_TIMEOUT = float(os.getenv("ECOSIM_AI_CALL_TIMEOUT", "4.0"))
_AI_MAX_OUTPUT_TOKENS = int(os.getenv("ECOSIM_AI_MAX_OUTPUT_TOKENS", "2500"))
_AI_MAX_RETRIES = int(os.getenv("ECOSIM_AI_MAX_RETRIES", "1"))

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower().strip()
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "groq/compound-mini")


def _default_llm_model() -> str:
    """Return the default model for the configured LLM provider."""
    if LLM_PROVIDER == "groq":
        return DEFAULT_GROQ_MODEL
    return DEFAULT_GEMINI_MODEL


_client: Any | None = None


def _municipality_id_from_payload(analysis_payload: dict[str, Any]) -> int | None:
    try:
        municipality_data = analysis_payload.get("municipality_data")
        if isinstance(municipality_data, list) and municipality_data:
            return municipality_data[0].get("municipality_id")
        if isinstance(municipality_data, dict):
            return municipality_data.get("municipality_id")
    except Exception:
        pass
    return None


def _backend_recommendation_from_payload(analysis_payload: dict[str, Any]) -> tuple[str, float]:
    """Return the backend's household-scale recommendation and its generation."""
    renewable = analysis_payload.get("renewable_energy_results") or {}
    household_sources = [
        ("solar", renewable.get("solar_output") or {}, "monthly_solar_output"),
        ("wind", renewable.get("wind_output") or {}, "monthly_energy_kwh"),
        ("hydro", renewable.get("hydro_output") or {}, "monthly_hydro_output"),
    ]
    best_source = "none"
    best_value = 0.0
    for key, output, value_key in household_sources:
        try:
            value = float(output.get(value_key, 0.0) or 0.0)
        except (TypeError, ValueError):
            value = 0.0
        if value > best_value:
            best_value = value
            best_source = key
    return best_source, best_value


def _compute_ai_cache_key(analysis_payload: dict[str, Any]) -> str:
    """Deterministic cache key for an EcoSim AI analysis request."""
    model = _default_llm_model()
    version = f"{_AI_CACHE_VERSION}:{LLM_PROVIDER}:{model}"
    payload = {
        "analysis_payload": analysis_payload,
        "provider": LLM_PROVIDER,
        "model": model,
        "version": _AI_CACHE_VERSION,
    }
    h = hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return f"ecosim_ai:{version}:{h}"


def _get_cached_ai_analysis(cache_key: str) -> dict[str, Any] | None:
    """Return a cached AI analysis if it has not expired.

    Redis is checked first (fast, in-memory L1); Supabase is the durable L2.
    """
    redis_cached = cache_get_sync(cache_key)
    if redis_cached is not None:
        if isinstance(redis_cached, dict):
            return redis_cached

    from app.services.supabase_service import get_supabase_client

    client = get_supabase_client()
    if client is None:
        return None
    try:
        # Select without .gt() so the REST fallback client can also read it.
        resp = (
            client.table("ecosim_ai_cache")
            .select("ai_result,expires_at")
            .eq("cache_key", cache_key)
            .limit(1)
            .execute()
        )
        rows = resp.data
        if isinstance(rows, dict):
            rows = [rows]
        if not rows:
            return None
        row = rows[0]
        expires_at = row.get("expires_at")
        if not expires_at:
            ai_result = row.get("ai_result")
            if ai_result:
                cache_set_sync(cache_key, ai_result, ttl=_AI_CACHE_TTL)
            return ai_result
        ts = expires_at.replace("Z", "+00:00") if isinstance(expires_at, str) else expires_at
        if datetime.fromisoformat(ts) > datetime.now(timezone.utc):
            ai_result = row.get("ai_result")
            if ai_result:
                cache_set_sync(cache_key, ai_result, ttl=_AI_CACHE_TTL)
            return ai_result
    except Exception as exc:
        logger.debug("Failed to read EcoSim AI cache for %s: %s", cache_key[:32], exc)
    return None


def _set_cached_ai_analysis(
    cache_key: str,
    municipality_id: int | None,
    result: dict[str, Any],
    ttl: int = _AI_CACHE_TTL,
) -> None:
    """Persist a successful AI analysis in Redis (L1) and Supabase (L2)."""
    cache_set_sync(cache_key, result, ttl=ttl)

    from app.services.supabase_service import get_supabase_client

    client = get_supabase_client()
    if client is None or not hasattr(client.table("ecosim_ai_cache"), "upsert"):
        return
    try:
        expires_at = (datetime.now(timezone.utc) + timedelta(seconds=ttl)).isoformat()
        record = {
            "cache_key": cache_key,
            "municipality_id": municipality_id,
            "inputs_hash": cache_key.split(":")[-1],
            "ai_result": result,
            "model_version": f"{LLM_PROVIDER}:{_default_llm_model()}",
            "expires_at": expires_at,
        }
        client.table("ecosim_ai_cache").upsert(record).execute()
    except Exception as exc:
        logger.warning("Failed to write EcoSim AI cache for %s: %s", cache_key[:32], exc)


def _strip_geothermal_for_province(text: str) -> str:
    """Remove any geothermal section or bullet that the model might still emit."""
    # Drop a `## Geothermal` section through the next `## ` header or end of text.
    text = re.sub(r"##\s*Geothermal\b.*?(?=##\s|\Z)", "", text, flags=re.IGNORECASE | re.DOTALL)
    # Drop bullet lines that start with `- **Geothermal**`.
    text = re.sub(r"^-?\s*\*\*Geothermal\*\*.*$", "", text, flags=re.IGNORECASE | re.MULTILINE)
    # Remove any standalone sentence that starts with and mentions geothermal.
    text = re.sub(r"\b[Gg]eothermal\b[^.!?]*[.!?]", "", text)
    return text.strip()


def _build_renewable_analysis_result(analysis_payload: dict[str, Any]) -> dict[str, Any]:
    """Run the LLM prompt and return a normalized analysis dict."""
    prompt = _build_renewable_analysis_prompt(analysis_payload)
    from app.services.llm_client import generate_response
    from app.services.llm_sanitizer import sanitize_llm_output, extract_prescriptive_recommendation

    response_text = generate_response(
        prompt,
        max_output_tokens=_AI_MAX_OUTPUT_TOKENS,
        max_retries=_AI_MAX_RETRIES,
    )
    if GEMINI_DEBUG:
        snippet = response_text[:500] if response_text else ""
        logger.info("LLM prompt chars=%s response chars=%s", len(prompt), len(response_text))
        logger.info("LLM response snippet=%s", snippet)

    cleaned = sanitize_llm_output(response_text)
    if not cleaned:
        logger.warning("LLM returned empty response after sanitization")
        return _normalize_analysis_output({})

    if analysis_payload.get("mode") == "province":
        cleaned = _strip_geothermal_for_province(cleaned)

    prescriptive = extract_prescriptive_recommendation(cleaned)
    backend_best, _ = _backend_recommendation_from_payload(analysis_payload)
    backend_best = backend_best if backend_best != "none" else ""

    return {
        "summary": cleaned,
        "renewable_analysis": {"solar": "", "wind": "", "hydro": "", "geothermal": ""},
        "recommendation": {
            "best_option": backend_best,
            "reason": prescriptive.get("reason") or prescriptive.get("recommendation", ""),
        },
        "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}, "geothermal": {}},
        "environmental_impact": "",
        "prescriptive_recommendation": prescriptive,
    }


def _get_gemini_client() -> Any:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY is not set")
            raise ValueError("GEMINI_API_KEY is not set")
        genai = _import_genai()
        _client = genai.Client(api_key=api_key)
    return _client


def _generate_once(
    client: Any,
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


SIMPLE_VOCABULARY_INSTRUCTION = (
    "You are a friendly energy advisor speaking to a Filipino homeowner who has NO technical background. "
    "Rules for all text you generate:"
    "\n- Use plain English. Avoid jargon. If you must use a technical term, explain it immediately in simple words."
    "\n- Example: Instead of 'solar irradiance is 5.8 kWh/m²/day', say 'Your area gets plenty of sunlight — about 5.8 hours of strong sun each day, which is excellent for solar panels.'"
    "\n- Example: Instead of 'capacity factor', say 'how efficiently the system runs compared to its best possible performance.'"
    "\n- Always explain WHY something matters to the user's wallet or home."
    "\n- Keep sentences short and conversational."
    "\n- Use everyday comparisons: 'That's like leaving 10 light bulbs on all day.'"
    "\n- Never assume the user knows what kWh, MW, GWh, or capacity factor mean."
    "\n- If giving a number, always pair it with a plain-English interpretation."
    "\n- The target audience includes teenagers and homeowners with zero engineering knowledge."
    "\n\n"
)


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

    genai = _import_genai()
    genai_errors = _import_genai_errors()

    # Prepend simple-vocabulary instruction to all content
    full_content = SIMPLE_VOCABULARY_INSTRUCTION + content

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
                return _generate_once(client, attempt_model, full_content, config)
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
    mode = analysis_payload.get("mode", "municipality")
    is_province = mode == "province"

    # Work on a deep copy so we can drop geothermal fields for province mode
    # without mutating the payload used elsewhere (cache key, etc.).
    prompt_payload = json.loads(json.dumps(analysis_payload, default=str))
    nearby_plants = prompt_payload.pop("nearby_geothermal_plants", None)
    if is_province:
        prompt_payload.get("renewable_energy_results", {}).pop("geothermal_output", None)

    payload = json.dumps(prompt_payload, ensure_ascii=True, indent=2)

    plant_context = ""
    if nearby_plants and not is_province:
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

    recommended_source, recommended_kwh = _backend_recommendation_from_payload(analysis_payload)
    recommended_source = recommended_source.title() if recommended_source != "none" else "None"

    if is_province:
        source_rule = "- Cover ONLY the following renewable types: solar, wind, hydro. Do NOT mention geothermal.\n"
        interpretation_header = (
            "For each of solar, wind, and hydro, write ONE short paragraph (2-3 sentences max). "
            "Mention whether it is viable and cite the numbers from SIMULATION DATA:\n"
        )
        interpretation_bullets = (
            "- **Solar**: irradiance, cloud cover, estimated output.\n"
            "- **Wind**: wind speed, capacity factor, estimated output.\n"
            "- **Hydro**: rainfall, elevation, estimated output.\n\n"
        )
        reason_header = (
            "In 2-3 sentences, compare the top 2-3 options among solar, wind, and hydro using the actual numbers, "
            "explain why the backend recommendation wins, and why the others are less suitable.\n\n"
        )
    else:
        source_rule = "- NEVER skip any renewable type (solar, wind, hydro, geothermal).\n"
        interpretation_header = (
            "For EACH renewable source, write ONE short paragraph (2-3 sentences max). "
            "Mention whether it is viable and cite the numbers from SIMULATION DATA:\n"
        )
        interpretation_bullets = (
            "- **Solar**: irradiance, cloud cover, estimated output.\n"
            "- **Wind**: wind speed, capacity factor, estimated output.\n"
            "- **Hydro**: rainfall, elevation, estimated output.\n"
            "- **Geothermal**: subsurface heat indicators, estimated output.\n\n"
        )
        reason_header = (
            "In 2-3 sentences, compare the top 2-3 options using the actual numbers, "
            "explain why the backend recommendation wins, and why the others are less suitable.\n\n"
        )

    return (
        "You are LUMI, an environmental intelligence assistant helping Filipino households choose renewable energy. "
        "IMPORTANT: Respond entirely in English only. Do not use Filipino, Tagalog, or any other language.\n\n"
        + plant_context
        + "CRITICAL RULES:\n"
        "- Use ONLY markdown headers (## Section Name) to separate sections.\n"
        "- Keep each section to 1-2 short paragraphs. Avoid long walls of text.\n"
        "- Use bullet points (dash + space) for lists only when helpful.\n"
        + source_rule
        + "- Do NOT use JSON, code blocks, or raw data dumps.\n"
        "- Do NOT invent numbers. Use ONLY values that appear in SIMULATION DATA. If a value is missing, say it is unavailable.\n"
        "- The BEST option has already been calculated by the backend. You MUST NOT recommend a different source.\n\n"
        f"BACKEND RECOMMENDATION: {recommended_source}"
        + (f" (about {recommended_kwh:,.0f} kWh/month).\n\n" if recommended_kwh > 0 else ".\n\n")
        + "STRUCTURE YOUR RESPONSE IN THESE EXACT SECTIONS (use ## headers):\n\n"
        "## Observation\n"
        "2-3 sentences describing the municipality's climate: temperature, humidity, solar irradiance, wind speed, rainfall, elevation.\n\n"
        "## Interpretation\n"
        + interpretation_header
        + interpretation_bullets
        + "## Recommendation\n"
        f"Confirm that the backend recommendation is {recommended_source}. Then give 2-3 short, actionable bullets (system size if known, next step, permit/net-metering). Do NOT invent cost or generation numbers.\n\n"
        "## Reason\n"
        + reason_header
        + "SIMULATION DATA:\n"
        f"{payload}\n"
    )


def analyze_renewable_results(analysis_payload: dict[str, Any]) -> dict[str, Any]:
    """Analyze renewable results with a persistent Supabase cache and a hard timeout."""
    cache_key = _compute_ai_cache_key(analysis_payload)
    cached = _get_cached_ai_analysis(cache_key)
    if cached is not None:
        logger.info("EcoSim AI cache hit for key=%s", cache_key[:32])
        return cached

    municipality_id = _municipality_id_from_payload(analysis_payload)

    # If the LLM call completes quickly, we return its result and it is cached.
    # If it takes longer than _AI_CALL_TIMEOUT, we return a fallback and the
    # worker thread continues so the next identical request can hit the cache.
    def _worker() -> dict[str, Any]:
        try:
            result = _build_renewable_analysis_result(analysis_payload)
            _set_cached_ai_analysis(cache_key, municipality_id, result)
            return result
        except Exception:
            logger.exception("EcoSim AI worker failed for key=%s", cache_key[:32])
            raise

    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(_worker)
    try:
        result = future.result(timeout=_AI_CALL_TIMEOUT)
        executor.shutdown(wait=False)
        return result
    except FutureTimeoutError:
        logger.warning(
            "EcoSim AI call timed out after %ss for key=%s; returning fallback",
            _AI_CALL_TIMEOUT,
            cache_key[:32],
        )
        executor.shutdown(wait=False)
    except Exception:
        logger.exception("EcoSim AI call failed for key=%s", cache_key[:32])
        executor.shutdown(wait=False)

    return {
        "summary": "AI analysis is taking longer than expected. A simplified summary is shown instead.",
        "renewable_analysis": {"solar": "", "wind": "", "hydro": "", "geothermal": ""},
        "recommendation": {"best_option": "", "reason": ""},
        "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}, "geothermal": {}},
        "environmental_impact": "",
        "error": "AI analysis timed out",
    }


async def analyze_renewable_results_async(
    analysis_payload: dict[str, Any],
) -> dict[str, Any]:
    return await asyncio.to_thread(analyze_renewable_results, analysis_payload)