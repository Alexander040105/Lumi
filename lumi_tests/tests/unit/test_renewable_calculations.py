"""
Unit tests for LUMI renewable energy calculation modules.

Coverage:
- Solar: temperature factor, dust loss, humidity degradation, performance ratio, solar_calc
- Wind: load_wind_averages, calculate_wind_output (Betz-limit validation)
- Hydro: normalize, runoff coefficient, flow estimation, hydropower calculation
- Edge cases: None inputs, boundary values, invalid inputs
"""

from __future__ import annotations

import math
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Import LUMI calculation modules (adjust PYTHONPATH or use repo root)
# ---------------------------------------------------------------------------
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
FASTAPI_SERVICES = REPO_ROOT / "fastapi-backend" / "app" / "services"
sys.path.insert(0, str(FASTAPI_SERVICES))

import solar_output_calc
import wind_output_calc
import hydro_output_calc


# =============================================================================
# SOLAR TESTS
# =============================================================================

class TestSolarTemperatureFactor:
    """Tests for calculate_temperature_factor()."""

    def test_none_returns_one(self):
        assert solar_output_calc.calculate_temperature_factor(None) == 1.0

    def test_reference_temp(self):
        """At 25°C the factor should be exactly 1.0."""
        assert solar_output_calc.calculate_temperature_factor(25.0) == pytest.approx(1.0)

    def test_hot_temp_reduces_factor(self):
        """Above 25°C the factor should decrease (negative coefficient)."""
        result = solar_output_calc.calculate_temperature_factor(35.0)
        assert result < 1.0
        assert result > 0.0

    def test_cold_temp_increases_factor(self):
        """Below 25°C the factor should increase."""
        result = solar_output_calc.calculate_temperature_factor(15.0)
        assert result > 1.0

    def test_floor_at_zero(self):
        """Extreme heat should floor at 0, not negative."""
        result = solar_output_calc.calculate_temperature_factor(300.0)
        assert result == pytest.approx(0.0)


class TestSolarDustLoss:
    """Tests for calculate_dust_loss_from_wind()."""

    def test_none_returns_base(self):
        assert solar_output_calc.calculate_dust_loss_from_wind(None) == pytest.approx(0.97)

    def test_moderate_wind(self):
        """3 m/s is the baseline; dust loss should be near the base."""
        result = solar_output_calc.calculate_dust_loss_from_wind(3.0)
        assert result == pytest.approx(0.97, rel=1e-2)

    def test_high_wind_reduces_loss(self):
        """Higher wind increases dust accumulation → lower dust_loss factor."""
        low = solar_output_calc.calculate_dust_loss_from_wind(2.0)
        high = solar_output_calc.calculate_dust_loss_from_wind(8.0)
        assert high < low

    def test_bounds(self):
        """Dust loss should always stay within [0.80, 1.0]."""
        for ws in [0.0, 3.0, 10.0, 20.0]:
            result = solar_output_calc.calculate_dust_loss_from_wind(ws)
            assert 0.80 <= result <= 1.0


class TestSolarHumidityDegradation:
    """Tests for calculate_degradation_from_humidity()."""

    def test_none_returns_base(self):
        assert solar_output_calc.calculate_degradation_from_humidity(None) == pytest.approx(0.99)

    def test_low_humidity(self):
        assert solar_output_calc.calculate_degradation_from_humidity(50.0) == pytest.approx(0.99)

    def test_high_humidity_reduces_degradation(self):
        low = solar_output_calc.calculate_degradation_from_humidity(60.0)
        high = solar_output_calc.calculate_degradation_from_humidity(80.0)
        assert high < low


class TestSolarPerformanceRatio:
    """Tests for calculate_performance_ratio()."""

    def test_default_params(self):
        pr = solar_output_calc.calculate_performance_ratio()
        # 0.80 * 1.0 * 0.97 * 0.96 * 0.98 * 0.98 * 0.99
        expected = 0.80 * 1.0 * 0.97 * 0.96 * 0.98 * 0.98 * 0.99
        assert pr == pytest.approx(expected, rel=1e-4)

    def test_zero_result_floored(self):
        """If any factor is zero, PR should floor at 0."""
        pr = solar_output_calc.calculate_performance_ratio(system_efficiency=0.0)
        assert pr == pytest.approx(0.0)


class TestSolarCalc:
    """Tests for the main solar_calc() function."""

    def test_typical_scenario(self, solar_valid_params):
        result = solar_output_calc.solar_calc(**solar_valid_params)
        assert result["system_kwp"] == pytest.approx(1.1, rel=1e-4)
        assert result["daily_solar_output"] > 0
        assert result["monthly_solar_output"] > 0
        assert 0 <= result["solar_score"] <= 100

    def test_score_capped_at_100(self):
        """Solar score should never exceed 100 even with extreme irradiance."""
        result = solar_output_calc.solar_calc(
            panel_wattage=550.0,
            number_of_panels=2,
            solar_irradiance=10.0,  # unrealistically high
            performance_ratio=0.9,
            days_in_month=30,
        )
        assert result["solar_score"] == pytest.approx(100.0)

    def test_zero_panels(self):
        result = solar_output_calc.solar_calc(
            panel_wattage=550.0,
            number_of_panels=0,
            solar_irradiance=5.0,
            performance_ratio=0.75,
            days_in_month=30,
        )
        assert result["system_kwp"] == pytest.approx(0.0)
        assert result["daily_solar_output"] == pytest.approx(0.0)


# =============================================================================
# WIND TESTS
# =============================================================================

class TestWindLoadAverages:
    """Tests for load_wind_averages()."""

    def test_returns_dict_with_expected_keys(self):
        result = wind_output_calc.load_wind_averages
        assert isinstance(result, dict)
        assert "avg_rotor_radius_m" in result
        assert "avg_power_coefficient" in result
        assert "rotor_count" in result
        assert "cp_count" in result

    def test_avg_power_coefficient_within_betz(self):
        """Average Cp should be below the Betz limit of 0.593 (59.3%)."""
        avg_cp = wind_output_calc.avg_power_coefficient
        assert avg_cp <= 59.3  # stored as percentage

    def test_avg_rotor_radius_positive(self):
        assert wind_output_calc.avg_rotor_radius_m > 0.0


class TestWindCalculateOutput:
    """Tests for calculate_wind_output()."""

    def test_typical_scenario(self, wind_valid_params):
        result = wind_output_calc.calculate_wind_output(**wind_valid_params)
        assert result["swept_area_m2"] > 0
        assert result["rated_power_kw"] > 0
        assert result["daily_energy_kwh"] > 0
        assert result["monthly_energy_kwh"] > 0
        assert 0 <= result["capacity_factor"] <= 1

    def test_power_proportional_to_cubed_wind_speed(self):
        """Doubling wind speed should increase power by ~8× (cubed relationship)."""
        base = wind_output_calc.calculate_wind_output(
            wind_speed_mps=3.0, days_in_month=30, air_density=1.18,
            rotor_radius_m=2.5, cp=0.35, efficiency=0.90,
            capacity_factor=0.30, operating_hours_per_day=24,
        )
        doubled = wind_output_calc.calculate_wind_output(
            wind_speed_mps=6.0, days_in_month=30, air_density=1.18,
            rotor_radius_m=2.5, cp=0.35, efficiency=0.90,
            capacity_factor=0.30, operating_hours_per_day=24,
        )
        ratio = doubled["rated_power_kw"] / base["rated_power_kw"]
        assert ratio == pytest.approx(8.0, rel=0.15)  # within 15% due to CF

    def test_invalid_rotor_radius_raises(self):
        with pytest.raises(ValueError, match="positive"):
            wind_output_calc.calculate_wind_output(
                wind_speed_mps=4.0, days_in_month=30, air_density=1.18,
                rotor_radius_m=0.0,
            )

    def test_invalid_wind_speed_raises(self):
        with pytest.raises(ValueError, match="positive"):
            wind_output_calc.calculate_wind_output(
                wind_speed_mps=0.0, days_in_month=30, air_density=1.18,
                rotor_radius_m=2.5,
            )

    def test_cp_exceeds_betz_raises(self):
        with pytest.raises(ValueError, match="Betz"):
            wind_output_calc.calculate_wind_output(
                wind_speed_mps=4.0, days_in_month=30, air_density=1.18,
                rotor_radius_m=2.5, cp=0.60,  # exceeds 0.593
            )

    def test_unrealistic_air_density_raises(self):
        with pytest.raises(ValueError, match="Air density"):
            wind_output_calc.calculate_wind_output(
                wind_speed_mps=4.0, days_in_month=30, air_density=0.5,
                rotor_radius_m=2.5,
            )

    def test_capacity_factor_bounds(self):
        with pytest.raises(ValueError, match="Capacity factor"):
            wind_output_calc.calculate_wind_output(
                wind_speed_mps=4.0, days_in_month=30, air_density=1.18,
                rotor_radius_m=2.5, cp=0.35, capacity_factor=1.5,
            )

    def test_low_speed_scenario(self, wind_low_speed_params):
        result = wind_output_calc.calculate_wind_output(**wind_low_speed_params)
        assert result["rated_power_kw"] >= 0
        assert result["monthly_energy_kwh"] >= 0


# =============================================================================
# HYDRO TESTS
# =============================================================================

class TestHydroNormalize:
    """Tests for normalize()."""

    def test_midpoint(self):
        assert hydro_output_calc.normalize(50, 0, 100) == pytest.approx(0.5)

    def test_at_min(self):
        assert hydro_output_calc.normalize(0, 0, 100) == pytest.approx(0.0)

    def test_at_max(self):
        assert hydro_output_calc.normalize(100, 0, 100) == pytest.approx(1.0)

    def test_none_returns_zero(self):
        assert hydro_output_calc.normalize(None, 0, 100) == pytest.approx(0.0)

    def test_clamped_below_zero(self):
        assert hydro_output_calc.normalize(-10, 0, 100) == pytest.approx(0.0)

    def test_clamped_above_one(self):
        assert hydro_output_calc.normalize(200, 0, 100) == pytest.approx(1.0)

    def test_divide_by_zero(self):
        """Equal min and max should return 0.0."""
        assert hydro_output_calc.normalize(50, 100, 100) == pytest.approx(0.0)


class TestHydroRunoffCoefficient:
    """Tests for estimate_runoff_coefficient()."""

    def test_none_returns_default(self):
        assert hydro_output_calc.estimate_runoff_coefficient(None) == pytest.approx(0.45)

    def test_gentle_slope(self):
        assert hydro_output_calc.estimate_runoff_coefficient(2.0) == pytest.approx(0.30)

    def test_moderate_slope(self):
        assert hydro_output_calc.estimate_runoff_coefficient(5.0) == pytest.approx(0.45)

    def test_steep_slope(self):
        assert hydro_output_calc.estimate_runoff_coefficient(15.0) == pytest.approx(0.60)

    def test_very_steep(self):
        assert hydro_output_calc.estimate_runoff_coefficient(25.0) == pytest.approx(0.75)


class TestHydroFlowRate:
    """Tests for estimated_flow_rate()."""

    def test_typical_scenario(self, hydro_flow_params):
        result = hydro_output_calc.estimated_flow_rate(**hydro_flow_params)
        assert 0.001 <= result <= 0.5  # bounds per implementation

    def test_zero_rainfall(self):
        result = hydro_output_calc.estimated_flow_rate(
            rainfall_mm_monthly=0.0,
            runoff_potential=0.5,
            watershed_gradient=0.5,
            mean_slope_deg=5.0,
            gravity_flow_potential=0.5,
        )
        assert result == pytest.approx(0.001, rel=1e-2)  # clamped to min

    def test_high_rainfall_steep_slope(self):
        result = hydro_output_calc.estimated_flow_rate(
            rainfall_mm_monthly=800.0,
            runoff_potential=0.9,
            watershed_gradient=0.9,
            mean_slope_deg=25.0,
            gravity_flow_potential=0.9,
        )
        assert 0.001 <= result <= 0.5


class TestHydroCalculate:
    """Tests for calculate_hydropower()."""

    def test_typical_scenario(self, hydro_valid_params):
        result = hydro_output_calc.calculate_hydropower(**hydro_valid_params)
        assert result["available_power_kw"] > 0
        assert result["daily_energy_kwh"] > 0
        assert result["monthly_energy_kwh"] > 0
        assert 0 <= result["hydro_score"] <= 100
        assert 2.0 <= result["realistic_head_m"] <= 25.0

    def test_zero_flow(self):
        result = hydro_output_calc.calculate_hydropower(
            days_in_month=30,
            flow_rate_cms=0.0,
            head_m=15.0,
        )
        assert result["available_power_kw"] == pytest.approx(0.0)
        assert result["monthly_energy_kwh"] == pytest.approx(0.0)
        assert result["hydro_score"] == pytest.approx(0.0)

    def test_head_clamped(self):
        """Very high head should be clamped to 25 m."""
        result = hydro_output_calc.calculate_hydropower(
            days_in_month=30,
            flow_rate_cms=0.1,
            head_m=500.0,
        )
        assert result["realistic_head_m"] == pytest.approx(25.0)

    def test_flow_clamped_to_max(self):
        result = hydro_output_calc.calculate_hydropower(
            days_in_month=30,
            flow_rate_cms=10.0,  # way above max
            head_m=15.0,
        )
        assert result["design_flow_cms"] == pytest.approx(0.5)


class TestHydroDischarge:
    """Tests for estimate_discharge()."""

    def test_typical(self):
        result = hydro_output_calc.estimate_discharge(
            rainfall_mm_monthly=300.0,
            basin_area_km2=0.5,
            runoff_coefficient=0.45,
        )
        assert result >= 0.0

    def test_zero_rainfall(self):
        result = hydro_output_calc.estimate_discharge(
            rainfall_mm_monthly=0.0,
            basin_area_km2=0.5,
            runoff_coefficient=0.45,
        )
        assert result == pytest.approx(0.0)
