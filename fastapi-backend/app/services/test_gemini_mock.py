import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "fastapi-backend"))

from app.services.rag_gemini_funcs import _smart_retrieve, _build_rag_prompt
from app.services import rag_pipeline

rag_pipeline.ensure_index_built()

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
    ("Test 1 — Solar budget", "Estimate my solar installation budget."),
    ("Test 2 — Hydro equipment", "What equipment is needed for a small hydro system?"),
    ("Test 3 — Solar vs Wind", "Should I choose solar or wind for my home?"),
]

for name, query in test_cases:
    print(f"\n{'='*60}")
    print(f"{name}")
    print(f"{'='*60}")
    ctx = _smart_retrieve(query, analysis_payload, top_k=5)
    print(f"Retrieved {len(ctx)} chunks")
    for i, c in enumerate(ctx, 1):
        print(f"  {i}. [{c['renewable_type']}/{c['category']}] score={c['score']}")
        print(f"     {c['text'][:150]}...")
    
    prompt = _build_rag_prompt(analysis_payload, query, ctx)
    print(f"\nPrompt length: {len(prompt)} chars")
    print("Prompt snippet (first 800 chars):")
    print(prompt[:800])
