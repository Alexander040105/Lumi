import asyncio
import json
import logging
from typing import Any

from app.services.llm_client import generate_response
from app.services.llm_sanitizer import sanitize_llm_output, extract_prescriptive_recommendation

logger = logging.getLogger(__name__)


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
        response_text = generate_response(prompt, json_mode=False)

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
