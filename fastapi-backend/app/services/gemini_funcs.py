import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai

_repo_root = Path(__file__).resolve().parents[3]
load_dotenv(dotenv_path=_repo_root / ".env")

logger = logging.getLogger(__name__)

DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DEFAULT_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
DEFAULT_MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "3000"))
GEMINI_DEBUG = os.getenv("GEMINI_DEBUG", "false").lower() in {"1", "true", "yes"}
if GEMINI_DEBUG:
    logger.setLevel(logging.INFO)

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


def generate_gemini_response(
    content: str,
    *,
    model: str | None = None,
    temperature: float | None = None,
    max_output_tokens: int | None = None,
) -> str:
    client = _get_gemini_client()
    model_name = model or DEFAULT_GEMINI_MODEL
    temp_value = DEFAULT_TEMPERATURE if temperature is None else temperature
    token_limit = DEFAULT_MAX_OUTPUT_TOKENS if max_output_tokens is None else max_output_tokens

    try:
        config = genai.types.GenerateContentConfig(
            temperature=temp_value,
            max_output_tokens=token_limit,
            response_mime_type="application/json",
        )
    except AttributeError:
        config = {
            "temperature": temp_value,
            "max_output_tokens": token_limit,
            "response_mime_type": "application/json",
        }

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
        },
        "recommendation": {
            "best_option": "",
            "reason": "",
        },
        "cost_estimation": {
            "solar": {},
            "wind": {},
            "hydro": {},
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
    payload = json.dumps(analysis_payload, ensure_ascii=True, indent=2)

    return (
        "You are LUMI, an environmental intelligence assistant. "
        "Summarize the simulation results concisely without changing calculations.\n\n"
        "RULES:\n"
        "- Return ONLY valid JSON. No markdown.\n"
        "- Keep each text field under 300 characters.\n"
        "- Use short sentences, no bullet lists.\n"
        "- Mention key drivers: solar irradiance, wind speed, rainfall, elevation, "
        "temperature, humidity, cloud coverage.\n"
        "- Cost estimates must be labeled as estimates.\n\n"
        "OUTPUT FORMAT (exact keys):\n"
        "{\n"
        "  \"summary\": \"\",\n"
        "  \"renewable_analysis\": {\"solar\": \"\", \"wind\": \"\", \"hydro\": \"\"},\n"
        "  \"recommendation\": {\"best_option\": \"\", \"reason\": \"\"},\n"
        "  \"cost_estimation\": {\n"
        "    \"solar\": {\"panels\": \"\", \"inverter\": \"\", \"battery\": \"\", \"installation\": \"\"},\n"
        "    \"wind\": {\"turbine\": \"\", \"tower\": \"\", \"controller\": \"\", \"installation\": \"\"},\n"
        "    \"hydro\": {\"turbine\": \"\", \"generator\": \"\", \"civil_works\": \"\", \"installation\": \"\"}\n"
        "  },\n"
        "  \"environmental_impact\": \"\"\n"
        "}\n\n"
        "SIMULATION DATA (FULL CONTEXT):\n"
        f"{payload}\n"
    )


def analyze_renewable_results(analysis_payload: dict[str, Any]) -> dict[str, Any]:
    try:
        prompt = _build_renewable_analysis_prompt(analysis_payload)
        response_text = generate_gemini_response(prompt)
        if GEMINI_DEBUG:
            snippet = response_text[:500] if response_text else ""
            logger.info("Gemini prompt chars=%s response chars=%s", len(prompt), len(response_text))
            logger.info("Gemini response snippet=%s", snippet)
        parsed = parse_gemini_json_response(response_text)
        if not parsed:
            logger.warning("Gemini returned empty or invalid JSON")
            if response_text:
                fallback = _normalize_analysis_output({})
                fallback["summary"] = _extract_summary(response_text)
                return fallback
        return _normalize_analysis_output(parsed)
    except Exception as exc:
        logger.exception("Gemini analysis failed")
        return {
            "summary": "Gemini analysis failed.",
            "renewable_analysis": {"solar": "", "wind": "", "hydro": ""},
            "recommendation": {"best_option": "", "reason": ""},
            "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}},
            "environmental_impact": "",
            "error": str(exc),
        }


async def analyze_renewable_results_async(
    analysis_payload: dict[str, Any],
) -> dict[str, Any]:
    return await asyncio.to_thread(analyze_renewable_results, analysis_payload)