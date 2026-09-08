"""Unit tests for LUMI geothermal calculation modules.

Coverage:
- Distance: haversine formula
- Normalization: _normalize helper
- Fault/volcano distance calculations
- Heat flow scoring and gradient
- Aquifer composite scoring
- Reservoir temperature estimation
- Flow rate estimation
- Geothermal suitability (overall score + classification)
- Geothermal energy output (thermal + electric power)
- Edge cases: None inputs, zero values, missing data, fallback temp
"""

from __future__ import annotations

import math
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Import LUMI geothermal module (adjust PYTHONPATH)
# ---------------------------------------------------------------------------
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
GEOTHERMAL_DIR = REPO_ROOT / "fastapi-backend" / "app" / "services" / "geothermal"
sys.path.insert(0, str(GEOTHERMAL_DIR))

import features as geothermal


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_faults() -> list[dict]:
    """Mock fault dataset."""
    return [
        {"lat": 14.5, "lon": 120.9, "length_km": 45.0},
        {"lat": 14.6, "lon": 121.0, "length_km": 30.0},
        {"lat": 15.0, "lon": 121.5, "length_km": 20.0},
    ]


@pytest.fixture
def sample_volcanoes() -> list[dict]:
    """Mock volcano dataset."""
    return [
        {"lat": 14.0, "lon": 120.99, "name": "Taal"},
        {"lat": 13.25, "lon": 123.68, "name": "Mayon"},
    ]


@pytest.fixture
def sample_heatflow_df() -> pd.DataFrame:
    """Mock heat-flow DataFrame."""
    return pd.DataFrame({
        "lat": [14.5, 14.6, 15.0],
        "lon": [120.9, 121.0, 121.5],
        "heat_flow_mw_m2": [80.0, 65.0, 45.0],
    })


@pytest.fixture
def sample_aquifer_df() -> pd.DataFrame:
    """Mock aquifer DataFrame for Philippines."""
    return pd.DataFrame({
        "Country": ["Philippines", "Philippines", "Philippines"],
        "Permeability": [-14.0, -13.5, -12.0],
        "Porosity": [0.15, 0.20, 0.30],
        "Aquifer_thickness": [500.0, 800.0, 1200.0],
    })


@pytest.fixture
def mock_datasets(sample_faults, sample_volcanoes, sample_heatflow_df, sample_aquifer_df) -> dict:
    """Fully mocked geothermal datasets dict."""
    return {
        "faults": sample_faults,
        "volcanoes": sample_volcanoes,
        "heatflow": sample_heatflow_df,
        "aquifers": sample_aquifer_df,
    }


# =============================================================================
# DISTANCE & NORMALIZATION HELPERS
# =============================================================================

class TestHaversine:
    """Tests for _haversine distance formula."""

    def test_same_point(self):
        """Distance from a point to itself must be 0."""
        assert geothermal._haversine(14.5, 120.9, 14.5, 120.9) == pytest.approx(0.0, abs=1e-6)

    def test_known_distance(self):
        """~1 degree of latitude ≈ 111 km at the equator."""
        dist = geothermal._haversine(14.0, 120.0, 15.0, 120.0)
        assert dist == pytest.approx(111.0, rel=0.05)

    def test_symmetry(self):
        """Distance A→B must equal distance B→A."""
        d1 = geothermal._haversine(14.5, 120.9, 13.25, 123.68)
        d2 = geothermal._haversine(13.25, 123.68, 14.5, 120.9)
        assert d1 == pytest.approx(d2, abs=1e-6)

    def test_positive(self):
        """All distances must be non-negative."""
        assert geothermal._haversine(0.0, 0.0, 45.0, 45.0) > 0.0


class TestNormalize:
    """Tests for _normalize helper."""

    def test_midpoint(self):
        assert geothermal._normalize(50.0, 0.0, 100.0) == pytest.approx(0.5)

    def test_at_min(self):
        assert geothermal._normalize(0.0, 0.0, 100.0) == pytest.approx(0.0)

    def test_at_max(self):
        assert geothermal._normalize(100.0, 0.0, 100.0) == pytest.approx(1.0)

    def test_none_returns_zero(self):
        assert geothermal._normalize(None, 0.0, 100.0) == pytest.approx(0.0)

    def test_clamped_below(self):
        assert geothermal._normalize(-10.0, 0.0, 100.0) == pytest.approx(0.0)

    def test_clamped_above(self):
        assert geothermal._normalize(200.0, 0.0, 100.0) == pytest.approx(1.0)

    def test_divide_by_zero(self):
        """Equal min and max should return 0.0 to avoid ZeroDivisionError."""
        assert geothermal._normalize(50.0, 100.0, 100.0) == pytest.approx(0.0)


# =============================================================================
# FAULT & VOLCANO DISTANCE
# =============================================================================

class TestFaultDistance:
    """Tests for calculate_fault_distance."""

    def test_with_mock_faults(self, sample_faults):
        """Should return the distance to the nearest fault."""
        result = geothermal.calculate_fault_distance(14.5, 120.9, sample_faults)
        assert result is not None
        assert result >= 0.0
        # First fault is exactly at (14.5, 120.9) → distance ~0 km
        assert result == pytest.approx(0.0, abs=1.0)

    def test_no_faults(self):
        """Empty fault list should return None."""
        assert geothermal.calculate_fault_distance(14.5, 120.9, []) is None

    def test_none_faults_loads_from_file(self):
        """When faults=None, function attempts to load from _FAULTS_JSON."""
        # If the file does not exist, it should return None gracefully
        result = geothermal.calculate_fault_distance(14.5, 120.9, None)
        assert result is None or isinstance(result, float)


class TestFaultDensity:
    """Tests for calculate_fault_density."""

    def test_typical(self):
        result = geothermal.calculate_fault_density(45.0, 150.0)
        assert result is not None
        assert result > 0.0
        assert result == pytest.approx(0.3, rel=1e-2)

    def test_zero_area_returns_none(self):
        assert geothermal.calculate_fault_density(45.0, 0.0) is None

    def test_negative_area_returns_none(self):
        assert geothermal.calculate_fault_density(45.0, -10.0) is None

    def test_none_area_returns_none(self):
        assert geothermal.calculate_fault_density(45.0, None) is None


class TestVolcanoDistance:
    """Tests for calculate_volcano_distance."""

    def test_with_mock_volcanoes(self, sample_volcanoes):
        result = geothermal.calculate_volcano_distance(14.0, 120.99, sample_volcanoes)
        assert result is not None
        assert result >= 0.0
        # First volcano is exactly at (14.0, 120.99)
        assert result == pytest.approx(0.0, abs=1.0)

    def test_no_volcanoes(self):
        assert geothermal.calculate_volcano_distance(14.0, 120.99, []) is None


# =============================================================================
# HEAT FLOW & GRADIENT
# =============================================================================

class TestHeatflowScore:
    """Tests for calculate_heatflow_score."""

    def test_none_returns_none(self):
        assert geothermal.calculate_heatflow_score(None) is None

    def test_midrange(self):
        """80 mW/m2 is midpoint of 40-120 range → should be ~0.5."""
        result = geothermal.calculate_heatflow_score(80.0)
        assert result == pytest.approx(0.5, abs=0.05)

    def test_at_min(self):
        result = geothermal.calculate_heatflow_score(40.0)
        assert result == pytest.approx(0.0, abs=0.01)

    def test_at_max(self):
        result = geothermal.calculate_heatflow_score(120.0)
        assert result == pytest.approx(1.0, abs=0.01)

    def test_below_min_clamped(self):
        result = geothermal.calculate_heatflow_score(20.0)
        assert result == pytest.approx(0.0, abs=0.01)

    def test_above_max_clamped(self):
        result = geothermal.calculate_heatflow_score(150.0)
        assert result == pytest.approx(1.0, abs=0.01)


class TestGeothermalGradient:
    """Tests for calculate_geothermal_gradient."""

    def test_none_returns_none(self):
        assert geothermal.calculate_geothermal_gradient(None) is None

    def test_typical(self):
        """q = 80 mW/m2 = 0.08 W/m2; k = 2.5 W/mK → G = 0.032 C/m = 32 C/km."""
        result = geothermal.calculate_geothermal_gradient(80.0, 2.5)
        assert result is not None
        assert result > 0.0
        assert result == pytest.approx(32.0, rel=0.05)

    def test_lower_conductivity_higher_gradient(self):
        """Lower thermal conductivity → higher gradient for same heat flow."""
        g1 = geothermal.calculate_geothermal_gradient(80.0, 2.5)
        g2 = geothermal.calculate_geothermal_gradient(80.0, 1.5)
        assert g2 > g1

    def test_zero_conductivity_returns_none(self):
        assert geothermal.calculate_geothermal_gradient(80.0, 0.0) is None

    def test_negative_conductivity_returns_none(self):
        assert geothermal.calculate_geothermal_gradient(80.0, -1.0) is None


# =============================================================================
# RESERVOIR TEMPERATURE
# =============================================================================

class TestReservoirTemperature:
    """Tests for calculate_reservoir_temperature."""

    def test_none_surface_temp(self):
        assert geothermal.calculate_reservoir_temperature(None, 30.0) is None

    def test_none_gradient(self):
        assert geothermal.calculate_reservoir_temperature(27.0, None) is None

    def test_typical(self):
        """Ts = 27 C, G = 30 C/km, depth = 2000 m = 2 km → T = 27 + 30*2 = 87 C."""
        result = geothermal.calculate_reservoir_temperature(27.0, 30.0, 2000.0)
        assert result is not None
        assert result == pytest.approx(87.0, abs=1.0)

    def test_shallower_depth(self):
        """1000 m depth → half the gradient contribution."""
        result = geothermal.calculate_reservoir_temperature(27.0, 30.0, 1000.0)
        assert result == pytest.approx(57.0, abs=1.0)

    def test_default_depth(self):
        """Default depth is 2000 m."""
        result_default = geothermal.calculate_reservoir_temperature(27.0, 30.0)
        result_explicit = geothermal.calculate_reservoir_temperature(27.0, 30.0, 2000.0)
        assert result_default == pytest.approx(result_explicit, abs=0.1)


# =============================================================================
# AQUIFER SCORING
# =============================================================================

class TestAquiferScore:
    """Tests for calculate_aquifer_score."""

    def test_none_inputs(self):
        assert geothermal.calculate_aquifer_score(None, 0.2, 500.0) is None
        assert geothermal.calculate_aquifer_score(-14.0, None, 500.0) is None
        assert geothermal.calculate_aquifer_score(-14.0, 0.2, None) is None

    def test_typical(self):
        """Permeability -14.0, porosity 0.20, thickness 800 m → mid-range score."""
        result = geothermal.calculate_aquifer_score(-14.0, 0.20, 800.0)
        assert result is not None
        assert 0.0 <= result <= 1.0

    def test_bounds(self):
        """Maxed-out inputs should give score ≈ 1.0."""
        result = geothermal.calculate_aquifer_score(-11.0, 0.35, 2000.0)
        assert result == pytest.approx(1.0, abs=0.1)

    def test_min_inputs(self):
        """Minimum inputs should give score ≈ 0.0."""
        result = geothermal.calculate_aquifer_score(-17.0, 0.0, 0.0)
        assert result == pytest.approx(0.0, abs=0.1)


# =============================================================================
# FLOW RATE ESTIMATION
# =============================================================================

class TestEstimateFlowRate:
    """Tests for estimate_flow_rate."""

    def test_none_inputs(self):
        assert geothermal.estimate_flow_rate(None, -14.0) is None
        assert geothermal.estimate_flow_rate(0.5, None) is None

    def test_typical(self):
        """Mid-range aquifer_score and permeability → flow between 10 and 500 kg/s."""
        result = geothermal.estimate_flow_rate(0.5, -14.0)
        assert result is not None
        assert result >= 10.0
        assert result <= 500.0

    def test_high_score_high_perm(self):
        """Maxed inputs → higher flow."""
        result = geothermal.estimate_flow_rate(1.0, -11.0)
        assert result > 100.0

    def test_low_score_low_perm(self):
        """Min inputs → base flow ~10 kg/s."""
        result = geothermal.estimate_flow_rate(0.0, -17.0)
        assert result == pytest.approx(10.0, abs=5.0)


# =============================================================================
# GEOTHERMAL SUITABILITY (OVERALL)
# =============================================================================

class TestComputeGeothermalSuitability:
    """Tests for compute_geothermal_suitability."""

    def test_with_mock_datasets(self, mock_datasets):
        """Full integration with mocked datasets should return expected keys."""
        result = geothermal.compute_geothermal_suitability(
            muni_lat=14.5,
            muni_lon=120.9,
            surface_temp_c=28.0,
            datasets=mock_datasets,
            municipality_area_km2=150.0,
        )
        assert isinstance(result, dict)
        assert "geothermal_score" in result
        assert "classification" in result
        assert "heat_flow_score" in result
        assert "fault_distance_km" in result
        assert "volcano_distance_km" in result
        assert "aquifer_score" in result
        assert "temperature_score" in result
        assert "fault_density" in result

    def test_classification_high(self):
        """If all indicators maxed, classification should be 'High'."""
        perfect = {
            "faults": [{"lat": 14.5, "lon": 120.9, "length_km": 100.0}],
            "volcanoes": [{"lat": 14.5, "lon": 120.9, "name": "Perfect"}],
            "heatflow": pd.DataFrame({
                "lat": [14.5], "lon": [120.9], "heat_flow_mw_m2": [120.0],
            }),
            "aquifers": pd.DataFrame({
                "Country": ["Philippines"],
                "Permeability": [-11.0],
                "Porosity": [0.35],
                "Aquifer_thickness": [2000.0],
            }),
        }
        result = geothermal.compute_geothermal_suitability(
            muni_lat=14.5, muni_lon=120.9, surface_temp_c=35.0,
            datasets=perfect, municipality_area_km2=150.0,
        )
        assert result["classification"] == "High"
        assert result["geothermal_score"] >= 0.80

    def test_classification_low(self):
        """With missing or minimal data, classification should be 'Low'."""
        empty = {"faults": [], "volcanoes": [], "heatflow": None, "aquifers": None}
        result = geothermal.compute_geothermal_suitability(
            muni_lat=14.5, muni_lon=120.9, surface_temp_c=None,
            datasets=empty, municipality_area_km2=150.0,
        )
        assert result["classification"] == "Low"
        assert result["geothermal_score"] == pytest.approx(0.0, abs=0.1)

    def test_missing_surface_temp(self, mock_datasets):
        """None surface_temp should set temperature_score to None."""
        result = geothermal.compute_geothermal_suitability(
            muni_lat=14.5, muni_lon=120.9, surface_temp_c=None,
            datasets=mock_datasets,
        )
        assert result["temperature_score"] is None

    def test_fault_density_calculation(self, mock_datasets):
        """Fault density should be computed when faults are present."""
        result = geothermal.compute_geothermal_suitability(
            muni_lat=14.5, muni_lon=120.9, surface_temp_c=28.0,
            datasets=mock_datasets, municipality_area_km2=100.0,
        )
        assert result["fault_density"] is not None
        assert result["fault_density"] > 0.0


# =============================================================================
# GEOTHERMAL ENERGY OUTPUT
# =============================================================================

class TestComputeGeothermalOutput:
    """Tests for compute_geothermal_output."""

    def test_typical_binary(self):
        """Typical inputs for a binary plant."""
        result = geothermal.compute_geothermal_output(
            surface_temp_c=27.0,
            gradient_c_km=30.0,
            aquifer_score=0.5,
            permeability_log10_m2=-14.0,
            depth_m=2000.0,
            plant_type="binary",
        )
        assert result["reservoir_temperature_c"] is not None
        assert result["estimated_flow_rate_kg_s"] is not None
        assert result["thermal_power_mw"] is not None
        assert result["electric_power_mw"] is not None
        assert result["annual_energy_gwh"] is not None
        assert result["confidence_score"] > 0.0
        assert result["source"] == "IHFC heat flow (measured), Zenodo aquifer properties (measured), NASA POWER temperature (measured)."

    def test_flash_plant(self):
        """Flash plant has higher efficiency (0.15 vs 0.12)."""
        result_flash = geothermal.compute_geothermal_output(
            surface_temp_c=27.0, gradient_c_km=30.0,
            aquifer_score=0.5, permeability_log10_m2=-14.0,
            plant_type="flash",
        )
        result_binary = geothermal.compute_geothermal_output(
            surface_temp_c=27.0, gradient_c_km=30.0,
            aquifer_score=0.5, permeability_log10_m2=-14.0,
            plant_type="binary",
        )
        # Same thermal power, but flash produces more electric power
        assert result_flash["electric_power_mw"] > result_binary["electric_power_mw"]

    def test_missing_data_returns_insufficient(self):
        """Missing gradient or aquifer should return 'Insufficient data'."""
        result = geothermal.compute_geothermal_output(
            surface_temp_c=27.0, gradient_c_km=None,
            aquifer_score=0.5, permeability_log10_m2=-14.0,
        )
        assert result["source"] == "Insufficient data"
        assert result["confidence_score"] == 0.0
        assert result["thermal_power_mw"] is None

    def test_fallback_temperature(self):
        """When surface_temp_c is None but gradient exists, use Philippine average 27 C."""
        result = geothermal.compute_geothermal_output(
            surface_temp_c=None, gradient_c_km=30.0,
            aquifer_score=0.5, permeability_log10_m2=-14.0,
        )
        assert result["reservoir_temperature_c"] is not None
        # Should note the fallback in the assumption or source
        assert "fallback" in result["source"].lower() or "average 27" in result["source"].lower()

    def test_zero_delta_t_handling(self):
        """If reservoir temp <= reinjection temp, delta_t should floor at 1.0."""
        result = geothermal.compute_geothermal_output(
            surface_temp_c=20.0, gradient_c_km=1.0,
            aquifer_score=0.5, permeability_log10_m2=-14.0,
            depth_m=1000.0, plant_type="binary",
        )
        # Very low gradient + shallow depth → reservoir temp near surface temp
        # delta_t = T_res - 70; if T_res <= 70, delta_t floors at 1.0
        assert result["thermal_power_mw"] is not None
        assert result["thermal_power_mw"] > 0.0

    def test_annual_energy_calculation(self):
        """Annual energy = electric_power_mw * 8760 / 1000."""
        result = geothermal.compute_geothermal_output(
            surface_temp_c=27.0, gradient_c_km=30.0,
            aquifer_score=0.5, permeability_log10_m2=-14.0,
            plant_type="binary",
        )
        expected_gwh = (result["electric_power_mw"] * 8760.0) / 1000.0
        assert result["annual_energy_gwh"] == pytest.approx(expected_gwh, rel=1e-3)

    def test_confidence_with_fallback(self):
        """Using fallback temp reduces confidence vs measured temp."""
        result_fallback = geothermal.compute_geothermal_output(
            surface_temp_c=None, gradient_c_km=30.0,
            aquifer_score=0.5, permeability_log10_m2=-14.0,
        )
        result_measured = geothermal.compute_geothermal_output(
            surface_temp_c=27.0, gradient_c_km=30.0,
            aquifer_score=0.5, permeability_log10_m2=-14.0,
        )
        assert result_fallback["confidence_score"] < result_measured["confidence_score"]
