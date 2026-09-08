"""
pytest configuration and shared fixtures for LUMI unit tests.

All fixtures are scoped to the ``function`` level unless noted otherwise.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[4]
FASTAPI_DIR = REPO_ROOT / "fastapi-backend"
SERVICES_DIR = FASTAPI_DIR / "app" / "services"
LOCAL_DATA_DIR = SERVICES_DIR / "local_data"


# ---------------------------------------------------------------------------
# Generic fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_climate_row() -> dict[str, Any]:
    """A representative climate row for a Philippine municipality."""
    return {
        "municipality_id": 1234,
        "name": "Test Municipality",
        "province": "Cavite",
        "t2m": 28.5,            # °C
        "t2m_max": 33.0,
        "t2m_min": 24.0,
        "rh2m": 78.0,           # %
        "prectotcorr": 12.5,    # mm/day
        "ws10m": 3.8,           # m/s
        "allsky_sfc_sw_dwn": 5.2,  # kWh/m²/day
        "rhoa": 1.18,           # kg/m³
        "elevation": 150.0,     # m
    }


@pytest.fixture
def sample_municipality() -> dict[str, Any]:
    """A representative municipality record."""
    return {
        "municipality_id": 1234,
        "province_id": 21,
        "name": "Test Municipality",
        "lat": 14.4793,
        "lon": 120.8970,
    }


# ---------------------------------------------------------------------------
# Solar fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def solar_valid_params() -> dict[str, Any]:
    """Typical solar calculation parameters for the Philippines."""
    return {
        "panel_wattage": 550.0,
        "number_of_panels": 2,
        "solar_irradiance": 5.2,
        "performance_ratio": 0.75,
        "days_in_month": 30,
    }


@pytest.fixture
def solar_high_temp_params() -> dict[str, Any]:
    """High-temperature scenario to test temperature derating."""
    return {
        "panel_wattage": 550.0,
        "number_of_panels": 2,
        "solar_irradiance": 5.2,
        "performance_ratio": 0.70,  # lower PR due to heat
        "days_in_month": 30,
    }


# ---------------------------------------------------------------------------
# Wind fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def wind_valid_params() -> dict[str, Any]:
    """Typical wind calculation parameters."""
    return {
        "wind_speed_mps": 4.5,
        "days_in_month": 30,
        "air_density": 1.18,
        "rotor_radius_m": 2.5,
        "cp": 0.35,
        "efficiency": 0.90,
        "capacity_factor": 0.30,
        "operating_hours_per_day": 24,
    }


@pytest.fixture
def wind_low_speed_params() -> dict[str, Any]:
    """Low wind speed edge case."""
    return {
        "wind_speed_mps": 1.0,
        "days_in_month": 30,
        "air_density": 1.18,
        "rotor_radius_m": 2.5,
        "cp": 0.35,
        "efficiency": 0.90,
        "capacity_factor": 0.20,
        "operating_hours_per_day": 24,
    }


# ---------------------------------------------------------------------------
# Hydro fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def hydro_valid_params() -> dict[str, Any]:
    """Typical micro-hydro calculation parameters."""
    return {
        "days_in_month": 30,
        "flow_rate_cms": 0.05,
        "head_m": 15.0,
        "water_density": 1000.0,
        "gravity": 9.81,
        "turbine_efficiency": 0.75,
        "generator_efficiency": 0.90,
    }


@pytest.fixture
def hydro_flow_params() -> dict[str, Any]:
    """Parameters for flow-rate estimation."""
    return {
        "rainfall_mm_monthly": 350.0,
        "runoff_potential": 0.6,
        "watershed_gradient": 0.5,
        "mean_slope_deg": 8.0,
        "gravity_flow_potential": 0.7,
        "catchment_area_km2": 0.5,
    }


# ---------------------------------------------------------------------------
# ML fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_energy_df() -> pd.DataFrame:
    """A minimal DOE-like energy demand DataFrame."""
    return pd.DataFrame({
        "year": list(range(2003, 2025)),
        "consumption_gwh": [
            45000, 46500, 48000, 49500, 51000, 52500, 54000, 55500,
            57000, 58500, 60000, 61500, 63000, 64500, 66000, 67500,
            69000, 70500, 72000, 73500, 75000, 76500,
        ],
    })


@pytest.fixture
def sample_energy_df_missing() -> pd.DataFrame:
    """A minimal DOE-like DataFrame with missing values."""
    df = pd.DataFrame({
        "year": list(range(2003, 2025)),
        "consumption_gwh": [
            45000, 46500, np.nan, 49500, 51000, 52500, 54000, 55500,
            57000, 58500, 60000, 61500, np.nan, 64500, 66000, 67500,
            69000, 70500, 72000, 73500, 75000, 76500,
        ],
    })
    return df


# ---------------------------------------------------------------------------
# AI / Gemini fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_gemini_response() -> str:
    """A mock Gemini JSON response matching the expected schema."""
    return json.dumps({
        "recommended_energy_source": "solar",
        "cost_range": "PHP 80,000 – 120,000",
        "explanation": "High solar irradiance and moderate temperatures make solar the most viable option.",
        "caveats": "Seasonal cloud cover may reduce output during the rainy season.",
        "environmental_impact": "Estimated CO₂ reduction of 1.2 tonnes/year.",
    })


@pytest.fixture
def mock_gemini_invalid_response() -> str:
    """A malformed Gemini response (missing required field)."""
    return json.dumps({
        "cost_range": "PHP 50,000",
        "explanation": "Incomplete data.",
    })


@pytest.fixture
def mock_ecosim_payload() -> dict[str, Any]:
    """A representative EcoSim payload for AI prompt construction."""
    return {
        "municipality": "Tagaytay City",
        "province": "Cavite",
        "solar": {
            "monthly_output_kwh": 320.0,
            "solar_score": 78.5,
            "system_kwp": 1.1,
        },
        "wind": {
            "monthly_output_kwh": 45.0,
            "wind_score": 32.0,
            "rated_power_kw": 0.12,
        },
        "hydro": {
            "monthly_output_kwh": 120.0,
            "hydro_score": 55.0,
            "design_flow_cms": 0.03,
            "realistic_head_m": 8.0,
        },
        "monthly_consumption": 350.0,
        "estimated_cost_php": 95000.0,
        "payback_years": 4.5,
    }


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_climate_records() -> list[dict[str, Any]]:
    """Sample climate records for database insertion testing."""
    return [
        {
            "municipality_id": 1,
            "year": 2020,
            "month": 1,
            "t2m": 26.5,
            "t2m_max": 31.0,
            "t2m_min": 22.0,
            "rh2m": 75.0,
            "prectotcorr": 8.5,
            "ws10m": 3.2,
            "allsky_sfc_sw_dwn": 4.8,
            "source": "NASA POWER",
        },
        {
            "municipality_id": 1,
            "year": 2020,
            "month": 2,
            "t2m": 27.0,
            "t2m_max": 32.0,
            "t2m_min": 23.0,
            "rh2m": 72.0,
            "prectotcorr": 6.0,
            "ws10m": 3.5,
            "allsky_sfc_sw_dwn": 5.5,
            "source": "NASA POWER",
        },
    ]


# ---------------------------------------------------------------------------
# Temporary directory fixture for file I/O tests
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_csv_file():
    """Yield a temporary CSV file path and clean up after the test."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        path = Path(f.name)
    yield path
    if path.exists():
        path.unlink()
