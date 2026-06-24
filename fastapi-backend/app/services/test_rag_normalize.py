import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "fastapi-backend"))

from app.services.rag_ai_funcs import _normalize_rag_output

# Simulate a perfect LLM response
mock_llm = {
    "recommended_energy_source": "solar",
    "estimated_budget": {
        "equipment": ["Solar panels: PHP 1,291 - 5,782", "Inverter: PHP 15,816", "Mounting: PHP 3,000"],
        "installation": "PHP 10,000 - 20,000 (30-50% of equipment)",
        "maintenance": "PHP 500 - 1,000/year (0.5-1% of system cost)",
    },
    "cost_range": "PHP 35,000 - 70,000 for a 1.1 kWp system",
    "explanation": "Solar is recommended because the municipality receives 5.2 kWh/m²/day solar irradiance.",
    "limitations": "Output drops during cloudy months. Battery needed for off-grid use.",
}

result = _normalize_rag_output(mock_llm)

print("=== Normalized Output ===")
import json
print(json.dumps(result, indent=2, ensure_ascii=False))

# Verify backward-compatible fields exist
assert result["recommended_energy_source"] == "solar"
assert result["summary"] == result["explanation"]
assert result["recommendation"]["best_option"] == "solar"
assert "solar" in result["cost_estimation"]
assert result["cost_estimation"]["solar"]["total_range"] == "PHP 35,000 - 70,000 for a 1.1 kWp system"
print("\nAll assertions passed.")
