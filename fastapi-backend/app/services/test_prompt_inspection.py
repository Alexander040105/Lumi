import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "fastapi-backend"))

from app.services.rag_ai_funcs import _smart_retrieve, _build_rag_prompt
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

query = "Estimate my solar installation budget."
ctx = _smart_retrieve(query, analysis_payload, top_k=3)

print("=== Retrieved Context ===")
for i, c in enumerate(ctx, 1):
    print(f"{i}. [{c['renewable_type']}/{c['category']}] score={c['score']}")
    print(f"   {c['text'][:200]}...")
    print()

prompt = _build_rag_prompt(analysis_payload, query, ctx)
print("=== PROMPT (first 2000 chars) ===")
print(prompt[:2000])
print("\n...")
print(f"=== PROMPT total length: {len(prompt)} chars ===")
