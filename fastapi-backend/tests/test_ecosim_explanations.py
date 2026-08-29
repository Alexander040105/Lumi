"""Unit tests for EcoSim deterministic renewable-source explanations."""
from __future__ import annotations

import pytest

from app.services.ecosim import _build_static_renewable_explanations, _get_or_build_explanations


def test_build_static_renewable_explanations_embeds_output_numbers() -> None:
    """The deterministic explanation text must echo the exact monthly outputs."""
    results = {
        "climate": {
            "avg_allsky_sfc_sw_dwn": 4.34,
            "avg_cloud_amt": 77.1,
            "avg_t2m": 25.6,
            "avg_ws10m": 2.55,
            "avg_prectotcorr": 4.73,
            "elevation": 11.0,
        },
        "solar_output": {"monthly_solar_output": 128.4},
        "wind_output": {"monthly_energy_kwh": 64.2},
        "hydro_output": {"monthly_hydro_output": 0.28},
        "geothermal_output": {
            "annual_energy_gwh": 0.0,
            "classification": "Unknown",
        },
    }

    explanations = _build_static_renewable_explanations(results)

    assert "128.4" in explanations["solar"]
    assert "64.2" in explanations["wind"]
    # Hydro output 0.28 is formatted to one decimal place in the UI text.
    assert "0.3" in explanations["hydro"]
    assert "0.28" not in explanations["hydro"]


def test_build_static_renewable_explanations_zero_output_omits_number() -> None:
    """When a source has no monthly output, the explanation should not invent a number."""
    results = {
        "climate": {
            "avg_allsky_sfc_sw_dwn": 0.0,
            "avg_cloud_amt": 100.0,
            "avg_t2m": 25.0,
            "avg_ws10m": 0.0,
            "avg_prectotcorr": 0.0,
            "elevation": 5.0,
        },
        "solar_output": {"monthly_solar_output": 0.0},
        "wind_output": {"monthly_energy_kwh": 0.0},
        "hydro_output": {"monthly_hydro_output": 0.0},
        "geothermal_output": {
            "annual_energy_gwh": 0.0,
            "classification": "Unknown",
        },
    }

    explanations = _build_static_renewable_explanations(results)

    # Solar text should say "negligible" and not embed a monthly number.
    assert "negligible" in explanations["solar"].lower()
    # Wind text should say "minimal" and not embed a monthly number.
    assert "minimal" in explanations["wind"].lower()
    # Hydro text should say "minimal" and not embed a monthly number.
    assert "minimal" in explanations["hydro"].lower()


def test_get_or_build_explanations_returns_generated_without_municipality_id() -> None:
    """Without a municipality_id, the guard should just return generated text."""
    results = {
        "climate": {"avg_prectotcorr": 4.73, "elevation": 11.0},
        "solar_output": {"monthly_solar_output": 100.0},
        "wind_output": {"monthly_energy_kwh": 50.0},
        "hydro_output": {"monthly_hydro_output": 0.28},
        "geothermal_output": {"annual_energy_gwh": 0.0},
    }
    explanations = _get_or_build_explanations(municipality_id=None, results=results)
    assert "100.0" in explanations["solar"]
    assert "0.3" in explanations["hydro"]
