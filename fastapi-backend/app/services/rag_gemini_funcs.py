import json
import logging
from pathlib import Path
from typing import Any

from app.services.llm_client import generate_response, parse_json_response
from app.services import rag_pipeline

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Prompt construction with strong grounding rules
# ---------------------------------------------------------------------------

def _build_rag_prompt(
    analysis_payload: dict[str, Any],
    user_query: str,
    retrieved_context: list[dict[str, Any]],
) -> str:
    simulation_payload = json.dumps(analysis_payload, ensure_ascii=True, indent=2)
    context_payload = json.dumps(retrieved_context, ensure_ascii=True, indent=2)

    return (
        "You are LUMI, an AI assistant for renewable energy analysis in the Philippines.\n\n"
        "GROUNDING RULES (STRICT):\n"
        "1. ALL facts, figures, and data in your response MUST come from the RETRIEVED KNOWLEDGE below.\n"
        "2. If the retrieved knowledge does not contain a specific number or fact, say so—do NOT hallucinate.\n"
        "3. Cite the relevant category when using data (e.g., 'solar panel equipment cost', 'national_energy_statistics', 'municipality_climate', 'terrain_metrics').\n"
        "4. Use the ECOSIM DATA to tailor recommendations to the municipality's climate and generation potential.\n"
        "5. Use NATIONAL ENERGY STATISTICS for context on Philippine energy trends, grid composition, and peak demand.\n"
        "6. Use MUNICIPALITY CLIMATE data to discuss local solar, wind, and temperature conditions.\n"
        "7. Use TERRAIN METRICS when discussing hydropower suitability or site-specific topography.\n"
        "8. Do not use your internal parametric knowledge for Philippine-specific data—rely only on the retrieved knowledge.\n\n"
        "OUTPUT FORMAT: Return ONLY valid JSON with this exact structure:\n"
        "{\n"
        '  "recommended_energy_source": "solar|wind|hydro",\n'
        '  "estimated_budget": {\n'
        '    "equipment": ["item: price range (source)"],\n'
        '    "installation": "range or statement with source",\n'
        '    "maintenance": "annual estimate with source"\n'
        '  },\n'
        '  "cost_range": "total system cost range in PHP",\n'
        '  "explanation": "concise reasoning based on climate + retrieved knowledge + national energy context",\n'
        '  "limitations": "caveats, missing data, or site-specific requirements"\n'
        "}\n\n"
        "SYSTEM CONTEXT: LUMI renewable energy decision support\n\n"
        "ECOSIM DATA (municipality climate + generation estimates):\n"
        f"{simulation_payload}\n\n"
        "RETRIEVED KNOWLEDGE (use ONLY this for all facts and figures in your response):\n"
        f"{context_payload}\n\n"
        "USER QUESTION:\n"
        f"{user_query}\n"
    )


# ---------------------------------------------------------------------------
# Output normalisation
# ---------------------------------------------------------------------------

def _normalize_rag_output(data: dict[str, Any]) -> dict[str, Any]:
    """
    Normalise the RAG JSON into the shape expected by the ecosim layer,
    while preserving the richer RAG-specific fields.
    """
    output: dict[str, Any] = {
        "recommended_energy_source": "",
        "estimated_budget": {
            "equipment": [],
            "installation": "",
            "maintenance": "",
        },
        "cost_range": "",
        "explanation": "",
        "limitations": "",
        # backward-compatible keys so callers that expect the old shape still get something reasonable
        "summary": "",
        "renewable_analysis": {"solar": "", "wind": "", "hydro": ""},
        "recommendation": {"best_option": "", "reason": ""},
        "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}},
        "environmental_impact": "",
    }

    if not isinstance(data, dict):
        return output

    # Map new keys -> output
    for key in ("recommended_energy_source", "cost_range", "explanation", "limitations"):
        if key in data:
            output[key] = data[key]

    if isinstance(data.get("estimated_budget"), dict):
        output["estimated_budget"].update(data["estimated_budget"])

    # Build backward-compatible fields from the new RAG fields
    output["summary"] = output["explanation"]
    output["recommendation"]["best_option"] = output["recommended_energy_source"]
    output["recommendation"]["reason"] = output["explanation"]

    # Populate cost_estimation for the recommended source
    source = output["recommended_energy_source"]
    if source:
        output["cost_estimation"][source] = {
            "equipment": output["estimated_budget"].get("equipment", []),
            "installation": output["estimated_budget"].get("installation", ""),
            "maintenance": output["estimated_budget"].get("maintenance", ""),
            "total_range": output["cost_range"],
        }

    return output


# ---------------------------------------------------------------------------
# Retrieval helpers
# ---------------------------------------------------------------------------

def _smart_retrieve(
    user_query: str,
    analysis_payload: dict[str, Any],
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Retrieve context using the new pipeline, with an optional boost for the
    best-scoring renewable source found in the simulation data.
    """
    # Ensure the knowledge base & index are ready
    rag_pipeline.ensure_index_built()

    # Try to detect which renewable source the query is about
    renewable_hint: str | None = None
    query_lower = user_query.lower()
    if "solar" in query_lower or "sun" in query_lower or "pv" in query_lower:
        renewable_hint = "solar"
    elif "wind" in query_lower or "turbine" in query_lower:
        renewable_hint = "wind"
    elif "hydro" in query_lower or "water" in query_lower or "hydropower" in query_lower:
        renewable_hint = "hydro"

    results = rag_pipeline.retrieve_context(user_query, top_k=top_k)

    # If we have a hint and not enough strong matches, do a second targeted retrieval
    if renewable_hint and len(results) < top_k:
        filtered = rag_pipeline.retrieve_with_filter(
            user_query,
            top_k=top_k,
            renewable_type=renewable_hint,
        )
        # Merge without duplicates (by text)
        seen = {r["text"] for r in results}
        for r in filtered:
            if r["text"] not in seen:
                results.append(r)
                seen.add(r["text"])
        results = results[:top_k]

    return results


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_with_rag(
    analysis_payload: dict[str, Any],
    user_query: str,
    top_k: int = 5,
) -> dict[str, Any]:
    try:
        retrieved_context = _smart_retrieve(user_query, analysis_payload, top_k=top_k)

        if not retrieved_context:
            logger.warning("RAG retrieved zero relevant chunks for query: %s", user_query)

        prompt = _build_rag_prompt(analysis_payload, user_query, retrieved_context)
        response_text = generate_response(prompt)
        parsed = parse_json_response(response_text)
        return _normalize_rag_output(parsed)
    except Exception:
        logger.exception("LLM RAG analysis failed")
        return {
            "recommended_energy_source": "",
            "estimated_budget": {"equipment": [], "installation": "", "maintenance": ""},
            "cost_range": "",
            "explanation": "LLM RAG analysis failed.",
            "limitations": "",
            "summary": "LLM RAG analysis failed.",
            "renewable_analysis": {"solar": "", "wind": "", "hydro": ""},
            "recommendation": {"best_option": "", "reason": ""},
            "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}},
            "environmental_impact": "",
        }
