"""Tests for catchment enrichment data and hydro calculation integration.

Tests cover:
  - Enrichment CSV data quality (row count, no nulls, valid ranges)
  - catchment_data loader (CSV fallback path)
  - hydro_output_calc with enrichment parameters
  - Stream feasibility penalty behavior
  - Flow floor behavior with/without enrichment
"""
from __future__ import annotations

import os
from pathlib import Path

# Suppress Redis and satisfy pydantic-settings before app imports.
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_JWT_ANON_KEY", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test")
os.environ.setdefault("USE_REDIS_CACHE", "false")

import pandas as pd
import pytest

from app.services.hydro_output_calc import (
    calculate_hydropower,
    estimated_flow_rate,
    estimate_runoff_coefficient,
)


# ---------------------------------------------------------------------------
# CSV data quality tests
# ---------------------------------------------------------------------------

ENRICHMENT_CSV = (
    Path(__file__).resolve().parents[1]
    / "app"
    / "services"
    / "local_data"
    / "municipality_catchment_enrichment.csv"
)


@pytest.fixture(scope="module")
def enrichment_df():
    """Load the enrichment CSV once for all tests."""
    if not ENRICHMENT_CSV.exists():
        pytest.skip(f"Enrichment CSV not found at {ENRICHMENT_CSV}")
    return pd.read_csv(ENRICHMENT_CSV)


def test_enrichment_csv_has_all_municipalities(enrichment_df):
    """CSV should have exactly 1376 rows (one per municipality in the atlas)."""
    assert len(enrichment_df) == 1376, f"Expected 1376 rows, got {len(enrichment_df)}"


def test_enrichment_csv_no_duplicate_municipality_ids(enrichment_df):
    """Each municipality_id should appear exactly once."""
    dupes = enrichment_df["municipality_id"].duplicated().sum()
    assert dupes == 0, f"Found {dupes} duplicate municipality_ids"


def test_enrichment_csv_no_nulls_in_key_columns(enrichment_df):
    """Key columns should have no null values."""
    key_cols = [
        "municipality_id",
        "province_id",
        "catchment_name",
        "catchment_match_method",
        "catchment_area_km2",
        "stream_head_m",
        "stream_feasibility_penalty",
        "effective_catchment_area_km2",
        "enriched_runoff_coefficient",
    ]
    for col in key_cols:
        null_count = enrichment_df[col].isnull().sum()
        assert null_count == 0, f"Column '{col}' has {null_count} nulls"


def test_enrichment_match_methods_are_valid(enrichment_df):
    """catchment_match_method should only be 'within' or 'nearest'."""
    methods = enrichment_df["catchment_match_method"].unique()
    assert set(methods) <= {"within", "nearest"}, f"Invalid methods: {set(methods) - {'within', 'nearest'}}"


def test_enrichment_within_count_matches_expected(enrichment_df):
    """Approximately 46% of municipalities should be 'within' a catchment."""
    within_count = (enrichment_df["catchment_match_method"] == "within").sum()
    assert 600 <= within_count <= 660, f"Within count {within_count} outside expected range 600-660"


def test_enrichment_stream_head_non_negative(enrichment_df):
    """Stream head should be non-negative (gradient × penstock ≥ 0)."""
    assert (enrichment_df["stream_head_m"] >= 0).all(), "Negative stream_head_m found"


def test_enrichment_stream_head_within_physical_bounds(enrichment_df):
    """Stream head should not exceed 50 m (gradient × 100m penstock)."""
    assert (enrichment_df["stream_head_m"] <= 50).all(), "stream_head_m exceeds 50m"


def test_enrichment_feasibility_penalty_in_range(enrichment_df):
    """Feasibility penalty should be between 0.1 and 1.0."""
    penalties = enrichment_df["stream_feasibility_penalty"]
    assert (penalties >= 0.1).all(), "Feasibility penalty below 0.1"
    assert (penalties <= 1.0).all(), "Feasibility penalty above 1.0"


def test_enrichment_effective_catchment_area_in_range(enrichment_df):
    """Effective catchment area should be between 0 and 1.0 km²."""
    areas = enrichment_df["effective_catchment_area_km2"]
    assert (areas >= 0).all(), "Negative effective catchment area"
    assert (areas <= 1.0).all(), "Effective catchment area exceeds 1.0 km²"


def test_enrichment_runoff_coefficient_in_range(enrichment_df):
    """Enriched runoff coefficient should be between 0.2 and 0.85."""
    coeffs = enrichment_df["enriched_runoff_coefficient"]
    assert (coeffs >= 0.2).all(), "Runoff coefficient below 0.2"
    assert (coeffs <= 0.85).all(), "Runoff coefficient above 0.85"


# ---------------------------------------------------------------------------
# catchment_data loader tests
# ---------------------------------------------------------------------------

def test_catchment_loader_returns_data_for_known_municipality():
    """Loader should return enrichment data for a municipality in the CSV."""
    from app.services.catchment_data import get_catchment_for_municipality

    # municipality_id 5145 is the first in the atlas CSV
    data = get_catchment_for_municipality(5145)
    assert data is not None, "Loader returned None for municipality 5145"
    assert "catchment_name" in data
    assert "stream_head_m" in data
    assert "effective_catchment_area_km2" in data


def test_catchment_loader_returns_none_for_unknown_municipality():
    """Loader should return None for a municipality not in the CSV."""
    from app.services.catchment_data import get_catchment_for_municipality

    data = get_catchment_for_municipality(999999)
    assert data is None, "Loader should return None for non-existent municipality"


# ---------------------------------------------------------------------------
# hydro_output_calc tests with enrichment parameters
# ---------------------------------------------------------------------------

def test_estimated_flow_rate_with_runoff_override():
    """runoff_coefficient_override should replace slope-based coefficient.
    When an override is provided, terrain modifiers are skipped (the enriched
    RC already incorporates terrain morphology)."""
    # With override=0.6, the flow should differ from slope-based 0.45
    flow_override = estimated_flow_rate(
        rainfall_mm_monthly=200,
        runoff_potential=0.5,
        watershed_gradient=0.5,
        mean_slope_deg=5,  # slope-based C would be 0.45
        gravity_flow_potential=0.5,
        catchment_area_km2=1.0,
        runoff_coefficient_override=0.6,
    )
    flow_default = estimated_flow_rate(
        rainfall_mm_monthly=200,
        runoff_potential=0.5,
        watershed_gradient=0.5,
        mean_slope_deg=5,
        gravity_flow_potential=0.5,
        catchment_area_km2=1.0,
    )
    assert flow_override != flow_default, "Override should change flow rate"
    assert flow_override > 0, "Flow with override should be positive"
    # With override=0.6 and no terrain modifiers, flow should be higher than
    # the default path which applies terrain modifiers that reduce the coefficient.
    # Default: C=0.45 * (0.5+0.5*0.5) * (0.7+0.3*0.5) = 0.45 * 0.75 * 0.85 = 0.287
    # Override: C=0.6 (no modifiers) = 0.6
    assert flow_override > flow_default, (
        f"Override flow ({flow_override}) should be higher than default ({flow_default}) "
        f"because terrain modifiers are skipped when enriched RC is provided"
    )


def test_estimated_flow_rate_no_floor_allows_zero():
    """apply_flow_floor=False should allow 0 flow for dry areas."""
    flow = estimated_flow_rate(
        rainfall_mm_monthly=0,  # no rain
        runoff_potential=0.5,
        watershed_gradient=0.5,
        mean_slope_deg=5,
        gravity_flow_potential=0.5,
        catchment_area_km2=1.0,
        apply_flow_floor=False,
    )
    assert flow == 0.0, f"Expected 0 flow for 0 rain (no floor), got {flow}"


def test_estimated_flow_rate_with_floor_returns_minimum():
    """apply_flow_floor=True (default) should floor at 0.001 m³/s."""
    flow = estimated_flow_rate(
        rainfall_mm_monthly=0,
        runoff_potential=0.5,
        watershed_gradient=0.5,
        mean_slope_deg=5,
        gravity_flow_potential=0.5,
        catchment_area_km2=1.0,
        apply_flow_floor=True,
    )
    assert flow == 0.001, f"Expected 0.001 floor, got {flow}"


def test_calculate_hydropower_with_feasibility_penalty():
    """feasibility_penalty should reduce energy output."""
    base = calculate_hydropower(
        days_in_month=30,
        flow_rate_cms=0.1,
        head_m=50,
    )
    penalized = calculate_hydropower(
        days_in_month=30,
        flow_rate_cms=0.1,
        head_m=50,
        feasibility_penalty=0.1,
    )
    assert penalized["monthly_energy_kwh"] < base["monthly_energy_kwh"], \
        "Penalized output should be lower"
    assert penalized["monthly_energy_kwh"] <= base["monthly_energy_kwh"] * 0.11, \
        "0.1 penalty should reduce output to ~10%"


def test_enriched_rc_not_modified_by_terrain_factors():
    """When runoff_coefficient_override is provided (enrichment data), terrain
    modifiers should NOT be applied — the enriched RC already incorporates
    terrain morphology (drainage density, hypsometric integral)."""
    # Same RC override, but very different terrain values
    flow_good_terrain = estimated_flow_rate(
        rainfall_mm_monthly=200,
        runoff_potential=0.8,
        watershed_gradient=0.7,
        mean_slope_deg=15,
        gravity_flow_potential=0.5,
        catchment_area_km2=1.0,
        runoff_coefficient_override=0.6,
    )
    flow_poor_terrain = estimated_flow_rate(
        rainfall_mm_monthly=200,
        runoff_potential=0.05,
        watershed_gradient=0.02,
        mean_slope_deg=1,
        gravity_flow_potential=0.5,
        catchment_area_km2=1.0,
        runoff_coefficient_override=0.6,
    )
    # With the fix, both should be identical because terrain modifiers are
    # skipped when an override is provided.
    assert flow_good_terrain == flow_poor_terrain, (
        f"Enriched RC should not be modified by terrain factors. "
        f"Good terrain: {flow_good_terrain}, Poor terrain: {flow_poor_terrain}"
    )


def test_calculate_hydropower_head_already_realistic():
    """head_already_realistic=True should skip head_factor scaling."""
    # With head_already_realistic=True, head_m=10 should be used as-is (clamped to 0-50)
    result = calculate_hydropower(
        days_in_month=30,
        flow_rate_cms=0.1,
        head_m=10,
        head_factor=0.20,  # would give 2.0 if applied
        head_already_realistic=True,
    )
    # realistic_head_m should be 10, not 2.0
    assert result["realistic_head_m"] == 10.0, \
        f"Expected 10.0 (no scaling), got {result['realistic_head_m']}"


def test_calculate_hydropower_head_scaled_by_factor():
    """head_already_realistic=False (default) should apply head_factor."""
    result = calculate_hydropower(
        days_in_month=30,
        flow_rate_cms=0.1,
        head_m=50,
        head_factor=0.20,
        head_already_realistic=False,
    )
    # 50 * 0.20 = 10.0, but floored at 2.0
    assert result["realistic_head_m"] == 10.0, \
        f"Expected 10.0 (50*0.20), got {result['realistic_head_m']}"


def test_calculate_hydropower_123_ceiling_broken_with_realistic_head():
    """With stream-gradient head (not floored at 2.0), low-head areas
    should produce less than the old 123.2 kWh ceiling."""
    # Simulate a flat area: stream_head = 0.5m, flow = 0.001
    result = calculate_hydropower(
        days_in_month=31,
        flow_rate_cms=0.001,
        head_m=0.5,
        head_already_realistic=True,
        feasibility_penalty=0.5,
    )
    assert result["monthly_energy_kwh"] < 123.2, \
        f"Expected < 123.2 kWh (ceiling broken), got {result['monthly_energy_kwh']}"


# ---------------------------------------------------------------------------
# Integration: enrichment data produces different hydro than fixed assumptions
# ---------------------------------------------------------------------------

def test_enrichment_breaks_123_ceiling_for_some_municipalities(enrichment_df):
    """At least some municipalities should have stream_head that would
    produce hydro output different from the old 123.2 kWh ceiling."""
    # The old ceiling was: flow=0.001, head=25 (max), efficiency=0.675
    # = 9.81 * 0.001 * 25 * 0.675 * 24 * 31 = 123.2 kWh
    # With enrichment, stream_head varies 0-41.77m and feasibility varies 0.1-1.0
    # So many municipalities should produce different output.

    # Municipalities with stream_head < 25 (would have been capped at 25 before)
    low_head = enrichment_df[enrichment_df["stream_head_m"] < 25]
    assert len(low_head) > 100, \
        f"Expected >100 municipalities with stream_head < 25, got {len(low_head)}"

    # Municipalities with feasibility_penalty < 1.0 (would reduce output)
    penalized = enrichment_df[enrichment_df["stream_feasibility_penalty"] < 1.0]
    assert len(penalized) > 100, \
        f"Expected >100 municipalities with penalty < 1.0, got {len(penalized)}"
