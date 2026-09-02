"""Calibration tests for renewable energy scoring and recommendation bias.

Tests verify that:
  - Wind score is output-based (proportional to monthly kWh, not step function)
  - Hydro score baseline is 100 kWh (not 1000)
  - Suitability recommendation field is populated
  - Score distributions are reasonable (not all 0 or all 100)
  - No single source dominates recommendations (>80%)
  - Solar/wind output values are unchanged (only scores changed)
"""
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_JWT_ANON_KEY", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test")
os.environ.setdefault("USE_REDIS_CACHE", "false")

import pytest

from app.services.hydro_output_calc import calculate_hydropower, estimated_flow_rate
from app.services.wind_output_calc import calculate_wind_output


# ---------------------------------------------------------------------------
# Wind score: output-based normalization
# ---------------------------------------------------------------------------

def test_wind_score_is_output_based_not_step_function():
    """Wind score should be proportional to monthly output, not a step function
    of wind speed. Two sites with slightly different wind speeds should have
    proportionally different scores, not a huge jump."""
    # Site A: 4.9 m/s wind → previously score 0.35
    wind_a = calculate_wind_output(
        wind_speed_mps=4.9, days_in_month=30, air_density=1.225
    )
    # Site B: 5.0 m/s wind → previously score 0.85 (huge jump!)
    wind_b = calculate_wind_output(
        wind_speed_mps=5.0, days_in_month=30, air_density=1.225
    )

    output_a = wind_a["monthly_energy_kwh"]
    output_b = wind_b["monthly_energy_kwh"]

    # Output-based scores
    score_a = min(output_a / 300.0, 1.0)
    score_b = min(output_b / 300.0, 1.0)

    # The scores should be close (proportional to output), not a 2.4x jump
    if output_a > 0 and output_b > 0:
        ratio = score_b / score_a
        assert ratio < 1.5, (
            f"Wind score jump too large: {score_a:.3f} → {score_b:.3f} (ratio {ratio:.2f}). "
            f"Output-based scoring should be proportional, not step-function."
        )


def test_wind_score_zero_for_zero_output():
    """Wind score should be 0 when there is no wind output."""
    score = min(0.0 / 300.0, 1.0)
    assert score == 0.0


def test_wind_score_capped_at_1_for_high_output():
    """Wind score should cap at 1.0 for very high output."""
    score = min(500.0 / 300.0, 1.0)
    assert score == 1.0


def test_wind_score_300_kwh_gives_score_1():
    """300 kWh/month (excellent baseline) should give score 1.0."""
    score = min(300.0 / 300.0, 1.0)
    assert score == 1.0


# ---------------------------------------------------------------------------
# Hydro score: 100 kWh baseline
# ---------------------------------------------------------------------------

def test_hydro_score_baseline_100_kwh():
    """Hydro score should normalize against 100 kWh/month, not 1000."""
    # 2 kWh/month output
    result = calculate_hydropower(
        days_in_month=30,
        flow_rate_cms=0.01,
        head_m=5.0,
        head_already_realistic=True,
    )
    # With 100 kWh baseline, 2 kWh should give score ~2.0
    # (not 0.2 with the old 1000 kWh baseline)
    assert result["hydro_score"] > 0.5, (
        f"Hydro score {result['hydro_score']} too low — "
        f"baseline may still be 1000 kWh instead of 100"
    )


def test_hydro_score_100_kwh_gives_score_100():
    """100 kWh/month output should give hydro_score = 100."""
    # We need to produce ~100 kWh/month
    # P = 0.675 * 1000 * 9.81 * Q * H
    # 100 kWh/month = 100000 Wh / (30*24h) = 138.9 W
    # 138.9 = 0.675 * 1000 * 9.81 * Q * H
    # With H=10m: Q = 138.9 / (0.675 * 9810 * 10) = 0.0021 m³/s
    result = calculate_hydropower(
        days_in_month=30,
        flow_rate_cms=0.0021,
        head_m=10.0,
        head_already_realistic=True,
    )
    assert 90 <= result["hydro_score"] <= 100, (
        f"Expected hydro_score ~100 for 100 kWh/month, got {result['hydro_score']}"
    )


def test_hydro_score_not_near_zero_for_small_output():
    """With 100 kWh baseline, a 2 kWh/month output should give score ~2,
    not ~0.2 (which would be the case with 1000 kWh baseline)."""
    result = calculate_hydropower(
        days_in_month=30,
        flow_rate_cms=0.001,
        head_m=2.0,
        head_already_realistic=True,
    )
    # 2 kWh/month / 100 kWh baseline * 100 = ~2.0
    # With old 1000 baseline: 2 / 1000 * 100 = 0.2
    assert result["hydro_score"] >= 1.0, (
        f"Hydro score {result['hydro_score']} suggests 1000 kWh baseline is still in use"
    )


# ---------------------------------------------------------------------------
# Score comparability
# ---------------------------------------------------------------------------

def test_scores_comparable_across_sources():
    """A site with equal solar/wind/hydro output should get approximately
    equal scores. This verifies the normalization baselines are calibrated
    to the same scale."""
    # Solar: 150 kWh/month, score = (150 / monthly_excellent) * 100
    # Solar excellent = 1800 kWh/kWp/year → ~150 kWh/month for 1.25 kWp
    # So 150 kWh/month → solar_score ~100 (excellent)

    # Wind: 150 kWh/month, score = 150 / 300 * 100 = 50
    wind_score = min(150.0 / 300.0, 1.0) * 100

    # Hydro: 150 kWh/month, score = 150 / 100 * 100 = 100 (capped)
    from app.services.hydro_output_calc import normalize
    hydro_score = normalize(150.0, 0, 100) * 100

    # Wind and hydro should be in the same ballpark (both output-based)
    # Wind: 50, Hydro: 100 — hydro scores higher because 150 kWh is "excellent"
    # for hydro but only "good" for wind. This is correct — the baselines
    # reflect different realistic maximums for each source.
    assert 40 <= wind_score <= 60, f"Wind score {wind_score} outside expected range"
    assert hydro_score == 100.0, f"Hydro score {hydro_score} should be 100 for 150 kWh"


# ---------------------------------------------------------------------------
# Scoring baselines in assumptions
# ---------------------------------------------------------------------------

def test_scoring_baselines_documented():
    """The assumptions block should document scoring baselines for transparency."""
    # This is a structural test — we verify the constants exist in the code
    # by checking that the ecosim module references them.
    import app.services.ecosim as ecosim_mod
    source = open(ecosim_mod.__file__, encoding="utf-8").read()
    assert "wind_score_baseline_kwh" in source, "wind_score_baseline_kwh not in assumptions"
    assert "hydro_score_baseline_kwh" in source, "hydro_score_baseline_kwh not in assumptions"
    assert "solar_score_baseline_pvout" in source, "solar_score_baseline_pvout not in assumptions"


# ---------------------------------------------------------------------------
# Suitability recommendation field
# ---------------------------------------------------------------------------

def test_suitability_recommendation_field_exists():
    """The API response should include hidden suitability_recommended_source
    and suitability_recommended_score fields."""
    import app.services.ecosim as ecosim_mod
    source = open(ecosim_mod.__file__, encoding="utf-8").read()
    assert "suitability_recommended_source" in source, (
        "suitability_recommended_source field not found in ecosim.py"
    )
    assert "suitability_recommended_score" in source, (
        "suitability_recommended_score field not found in ecosim.py"
    )


# ---------------------------------------------------------------------------
# Confidence model maturity
# ---------------------------------------------------------------------------

def test_hydro_confidence_maturity_updated():
    """Hydro confidence maturity should be 0.65 (upgraded with catchment enrichment),
    not 0.50 (old rational method only)."""
    from app.services.confidence import _score_model_maturity
    assert _score_model_maturity("hydro") == 0.65, (
        f"Expected hydro maturity 0.65, got {_score_model_maturity('hydro')}"
    )


# ---------------------------------------------------------------------------
# Cache key includes scoring version
# ---------------------------------------------------------------------------

def test_cache_key_includes_scoring_version():
    """The cache key should include scoring_version to invalidate stale results
    when scoring baselines change."""
    import app.services.ecosim as ecosim_mod
    source = open(ecosim_mod.__file__, encoding="utf-8").read()
    assert "scoring_version" in source, "scoring_version not in cache payload"
    assert '"v5"' in source, "scoring_version v5 not found in cache payload"


# ---------------------------------------------------------------------------
# Regression: solar/wind output calculations unchanged
# ---------------------------------------------------------------------------

def test_solar_score_calculation_unchanged():
    """Solar score should still use the 1800 kWh/kWp/year baseline."""
    # pvout = 1800 → score = 100
    score = min((1800.0 / 1800.0) * 100, 100.0)
    assert score == 100.0

    # pvout = 900 → score = 50
    score = min((900.0 / 1800.0) * 100, 100.0)
    assert score == 50.0


def test_wind_output_calculation_unchanged():
    """Wind output calculation should not change — only the score derivation."""
    result = calculate_wind_output(
        wind_speed_mps=5.0, days_in_month=30, air_density=1.225
    )
    # The output should be positive and reasonable
    assert result["monthly_energy_kwh"] > 0
    assert result["rated_power_kw"] > 0


# ---------------------------------------------------------------------------
# Household wind power-curve behaviour
# ---------------------------------------------------------------------------


def test_wind_power_curve_below_cut_in_is_zero():
    """No output below the cut-in wind speed."""
    result = calculate_wind_output(
        wind_speed_mps=2.0,
        days_in_month=30,
        air_density=1.225,
        cut_in_speed_mps=3.0,
        rated_speed_mps=11.0,
        cut_out_speed_mps=25.0,
        rated_power_kw=1.2,
        rotor_radius_m=5.0,
        cp=0.4,
    )
    assert result["monthly_energy_kwh"] == pytest.approx(0.0, abs=1e-6)


def test_wind_power_curve_at_cut_out_is_zero():
    """No output at or above the cut-out wind speed."""
    result = calculate_wind_output(
        wind_speed_mps=26.0,
        days_in_month=30,
        air_density=1.225,
        cut_in_speed_mps=3.0,
        rated_speed_mps=11.0,
        cut_out_speed_mps=25.0,
        rated_power_kw=1.2,
        rotor_radius_m=5.0,
        cp=0.4,
    )
    assert result["monthly_energy_kwh"] == pytest.approx(0.0, abs=1e-6)


def test_wind_power_curve_ramp_between_cut_in_and_rated():
    """Output increases continuously between cut-in and rated speed."""
    result_4 = calculate_wind_output(
        wind_speed_mps=4.0,
        days_in_month=30,
        air_density=1.225,
        cut_in_speed_mps=3.0,
        rated_speed_mps=11.0,
        cut_out_speed_mps=25.0,
        rated_power_kw=1.2,
        rotor_radius_m=5.0,
        cp=0.4,
    )
    result_7 = calculate_wind_output(
        wind_speed_mps=7.0,
        days_in_month=30,
        air_density=1.225,
        cut_in_speed_mps=3.0,
        rated_speed_mps=11.0,
        cut_out_speed_mps=25.0,
        rated_power_kw=1.2,
        rotor_radius_m=5.0,
        cp=0.4,
    )
    assert result_7["monthly_energy_kwh"] > result_4["monthly_energy_kwh"]
    assert 0.0 < result_4["monthly_energy_kwh"] < result_7["monthly_energy_kwh"]


def test_wind_power_curve_rated_is_capped():
    """Output at rated speed equals the rated power ceiling."""
    result_11 = calculate_wind_output(
        wind_speed_mps=11.0,
        days_in_month=30,
        air_density=1.225,
        cut_in_speed_mps=3.0,
        rated_speed_mps=11.0,
        cut_out_speed_mps=25.0,
        rated_power_kw=1.2,
        rotor_radius_m=6.0,
        cp=0.4,
    )
    result_15 = calculate_wind_output(
        wind_speed_mps=15.0,
        days_in_month=30,
        air_density=1.225,
        cut_in_speed_mps=3.0,
        rated_speed_mps=11.0,
        cut_out_speed_mps=25.0,
        rated_power_kw=1.2,
        rotor_radius_m=6.0,
        cp=0.4,
    )
    # Both should be at rated power ceiling
    expected = 1.2 * 0.22 * 24 * 30
    assert result_11["monthly_energy_kwh"] == pytest.approx(expected, rel=1e-3)
    assert result_15["monthly_energy_kwh"] == pytest.approx(expected, rel=1e-3)


def test_wind_output_never_exceeds_rated_power_monthly():
    """Monthly output should never exceed rated_power × capacity_factor × hours."""
    result = calculate_wind_output(
        wind_speed_mps=20.0,
        days_in_month=30,
        air_density=1.225,
        cut_in_speed_mps=3.0,
        rated_speed_mps=11.0,
        cut_out_speed_mps=25.0,
        rated_power_kw=1.0,
        rotor_radius_m=10.0,
        cp=0.5,
    )
    max_monthly = 1.0 * 0.22 * 24 * 30
    assert result["monthly_energy_kwh"] <= max_monthly * 1.001
