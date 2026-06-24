"""
Test script for the LUMI RAG pipeline.

Run from repo root:
    python -m fastapi-backend.app.services.test_rag_pipeline
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

# Add repo root to path so imports work when running standalone
_repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_repo_root / "fastapi-backend"))

from app.services.rag_knowledge_builder import build_knowledge_base, save_knowledge_base
from app.services import rag_pipeline
from app.services.rag_ai_funcs import analyze_with_rag

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def _build_index() -> None:
    logger.info("=== Building knowledge base ===")
    docs = build_knowledge_base()
    save_knowledge_base(docs)

    logger.info("=== Building FAISS index ===")
    meta = rag_pipeline.build_faiss_index(docs)
    logger.info("Index metadata: %s", meta)


def _test_retrieval() -> None:
    queries = [
        "How much would solar installation cost for this municipality?",
        "Which renewable source is cheaper?",
        "How much does a small hydro system usually require?",
        "Compare solar vs wind vs hydro costs.",
        "What equipment is needed for a wind system?",
        "Solar panel price range",
        "Hydro turbine equipment cost",
    ]

    logger.info("\n=== Retrieval tests ===")
    for q in queries:
        results = rag_pipeline.retrieve_context(q, top_k=3)
        logger.info("\nQuery: %s", q)
        for i, r in enumerate(results, 1):
            logger.info(
                "  %s. [score=%s] [%s/%s] %s",
                i,
                r["score"],
                r.get("renewable_type", "?"),
                r.get("category", "?"),
                r["text"][:200].replace("\n", " "),
            )


def _test_end_to_end() -> None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.warning("GROQ_API_KEY not set — skipping end-to-end LLM tests.")
        return

    # Minimal ecosim payload for testing
    analysis_payload = {
        "municipality_data": [
            {
                "municipality_id": 1,
                "avg_t2m": 27.5,
                "avg_t2m_max": 32.0,
                "avg_t2m_min": 23.0,
                "avg_rh2m": 78.0,
                "avg_rhoa": 1.18,
                "avg_prectotcorr": 180.0,
                "avg_ws10m": 3.2,
                "avg_allsky_sfc_sw_dwn": 5.2,
                "avg_cloud_amt": 65.0,
                "avg_surface_pressure": 1010.0,
            }
        ],
        "consumption_results": {
            "monthly_consumption_kwh": 300.0,
            "daily_consumption_kwh": 10.0,
            "target_monthly_consumption_kwh": 150.0,
        },
        "renewable_energy_results": {
            "municipality": "TEST_MUNICIPALITY",
            "climate": {
                "avg_t2m": 27.5,
                "avg_ws10m": 3.2,
                "avg_prectotcorr": 180.0,
                "avg_allsky_sfc_sw_dwn": 5.2,
            },
            "solar_output": {
                "system_kwp": 1.1,
                "daily_solar_output": 3.5,
                "monthly_solar_output": 105.0,
            },
            "hydro_output": {
                "system_kwp": 0.5,
                "daily_hydro_output": 2.0,
                "monthly_hydro_output": 60.0,
                "hydro_score": 0.3,
            },
            "wind_output": {
                "swept_area_m2": 2.5,
                "rated_power_kw": 1.0,
                "capacity_factor": 0.12,
                "daily_energy_kwh": 2.9,
                "monthly_energy_kwh": 87.0,
            },
            "consumption_results": {
                "monthly_consumption_kwh": 300.0,
                "daily_consumption_kwh": 10.0,
                "target_monthly_consumption_kwh": 150.0,
            },
        },
    }

    test_cases = [
        ("Test 1 — Solar budget", "Estimate my solar installation budget."),
        ("Test 2 — Hydro equipment", "What equipment is needed for a small hydro system?"),
        ("Test 3 — Solar vs Wind", "Should I choose solar or wind for my home?"),
    ]

    logger.info("\n=== End-to-end RAG + Groq tests ===")
    for name, query in test_cases:
        logger.info("\n%s", name)
        result = analyze_with_rag(analysis_payload, query, top_k=5)
        logger.info("Result:\n%s", json.dumps(result, indent=2, ensure_ascii=False))


def main() -> None:
    _build_index()
    _test_retrieval()
    _test_end_to_end()


if __name__ == "__main__":
    main()
