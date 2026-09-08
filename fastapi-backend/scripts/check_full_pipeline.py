"""
Full pipeline test — RAG + Groq + Gemini fallback.
Run from repo root:  python -m fastapi-backend.app.services.test_full_pipeline
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_repo / "fastapi-backend"))

# ------------------------------------------------------------------
# 1. Load fresh env vars (user just edited .env)
# ------------------------------------------------------------------
from dotenv import load_dotenv
load_dotenv(dotenv_path=_repo / ".env")

print("=" * 60)
print("ENV CHECK")
print("=" * 60)
print(f"  GROQ_API_KEY   : {'SET' if os.getenv('GROQ_API_KEY') else 'MISSING'}")
print(f"  GEMINI_API_KEY : {'SET' if os.getenv('GEMINI_API_KEY') else 'MISSING'}")
print(f"  LLM_PROVIDER   : {os.getenv('LLM_PROVIDER', 'gemini')}")

# ------------------------------------------------------------------
# 2. Test Groq client standalone
# ------------------------------------------------------------------
print("\n" + "=" * 60)
print("TEST 1 — Groq client (direct)")
print("=" * 60)
try:
    from app.services.groq_client import generate_groq_response
    text = generate_groq_response(
        "Return a JSON object with one key: {'status': 'ok'}",
        max_tokens=200,
    )
    parsed = json.loads(text)
    print(f"  SUCCESS: {parsed}")
except Exception as exc:
    print(f"  FAILED: {exc}")

# ------------------------------------------------------------------
# 3. Test unified LLM client
# ------------------------------------------------------------------
print("\n" + "=" * 60)
print("TEST 2 — Unified LLM client")
print("=" * 60)
try:
    from app.services.llm_client import generate_response, parse_json_response, LLM_PROVIDER
    print(f"  Provider detected: {LLM_PROVIDER}")
    text = generate_response(
        'Return ONLY valid JSON: {"status": "ok", "provider": "' + LLM_PROVIDER + '"}',
        max_output_tokens=200,
    )
    parsed = parse_json_response(text)
    print(f"  SUCCESS: {parsed}")
except Exception as exc:
    print(f"  FAILED: {exc}")

# ------------------------------------------------------------------
# 4. Test RAG retrieval
# ------------------------------------------------------------------
print("\n" + "=" * 60)
print("TEST 3 — RAG retrieval")
print("=" * 60)
try:
    from app.services import rag_pipeline
    rag_pipeline.ensure_index_built()

    queries = [
        "solar installation cost",
        "hydro turbine price",
        "wind system components",
    ]
    for q in queries:
        results = rag_pipeline.retrieve_context(q, top_k=2)
        print(f"\n  Query: {q}")
        for r in results:
            print(f"    [{r['renewable_type']}/{r['category']}] score={r['score']:.3f}")
except Exception as exc:
    print(f"  FAILED: {exc}")

# ------------------------------------------------------------------
# 5. Test RAG end-to-end (with real LLM)
# ------------------------------------------------------------------
print("\n" + "=" * 60)
print("TEST 4 — End-to-end RAG + LLM")
print("=" * 60)

analysis_payload = {
    "municipality_data": [{"municipality_id": 1, "avg_t2m": 27.5, "avg_ws10m": 3.2}],
    "consumption_results": {"monthly_consumption_kwh": 300.0},
    "renewable_energy_results": {
        "municipality": "TEST_MUNICIPALITY",
        "solar_output": {"system_kwp": 1.1, "monthly_solar_output": 105.0},
        "hydro_output": {"system_kwp": 0.5, "monthly_hydro_output": 60.0, "hydro_score": 0.3},
        "wind_output": {"rated_power_kw": 1.0, "monthly_energy_kwh": 87.0},
    },
}

test_cases = [
    ("Solar budget", "Estimate my solar installation budget."),
    ("Hydro equipment", "What equipment is needed for a small hydro system?"),
    ("Solar vs Wind", "Should I choose solar or wind for my home?"),
]

try:
    from app.services.rag_gemini_funcs import analyze_with_rag
    for name, query in test_cases:
        print(f"\n  --- {name} ---")
        result = analyze_with_rag(analysis_payload, query, top_k=5)
        print(f"    recommended: {result.get('recommended_energy_source', 'N/A')}")
        print(f"    cost_range : {result.get('cost_range', 'N/A')}")
        print(f"    explanation: {result.get('explanation', 'N/A')[:120]}...")
except Exception as exc:
    print(f"  FAILED: {exc}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETE")
print("=" * 60)
