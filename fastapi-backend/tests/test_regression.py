"""Regression tests for calculation accuracy after optimizations.

These tests are deliberately dependency-light and exercise the pure/aggregating
functions so we can be sure the climate, scoring, and geospatial math did not
change when we added Redis caching or batch Supabase queries.
"""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import MagicMock

# Suppress Redis and satisfy pydantic-settings before app imports.
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_JWT_ANON_KEY", "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test")
os.environ.setdefault("USE_REDIS_CACHE", "false")

import pytest

from app.services.climate_service import _aggregate_municipality_climate
from app.services.map_service import _aggregate_to_province, _format_score


def test_format_score_scales_normalized_and_preserves_percentage():
    """_format_score must scale 0-1 scores to 0-100 and leave 0-100 as-is."""
    assert _format_score(0.5123) == 51.23
    assert _format_score(0.5) == 50.0
    assert _format_score(0.0) == 0.0
    assert _format_score(1.0) == 100.0
    assert _format_score(75.5) == 75.5
    assert _format_score(None) == 0.0
    assert _format_score("not a number") == 0.0


def test_aggregate_municipality_climate_monthly_means():
    """Province-level climate aggregation must compute the mean for each month."""
    rows = [
        {"municipality_id": 1, "month": 1, "year": 2024, "t2m": 25.0, "rh2m": 80.0},
        {"municipality_id": 2, "month": 1, "year": 2024, "t2m": 27.0, "rh2m": 70.0},
        {"municipality_id": 1, "month": 2, "year": 2024, "t2m": 26.0, "rh2m": None},
        {"municipality_id": 2, "month": 2, "year": 2024, "t2m": 28.0, "rh2m": 75.0},
    ]
    result = _aggregate_municipality_climate(rows, province_id=10, year=2024)

    assert len(result) == 2
    jan = next(r for r in result if r["month"] == 1)
    feb = next(r for r in result if r["month"] == 2)

    assert jan["province_id"] == 10
    assert jan["year"] == 2024
    assert jan["source"] == "aggregated_from_municipalities"
    assert jan["t2m"] == 26.0
    assert jan["rh2m"] == 75.0

    assert feb["t2m"] == 27.0
    assert feb["rh2m"] == 75.0  # None excluded, only one value


def test_aggregate_municipality_climate_empty_input():
    assert _aggregate_municipality_climate([], province_id=1, year=2024) == []


def _mock_query_response(data: list[dict[str, Any]]):
    """Return a builder chain that ends with .execute() returning data."""
    builder = MagicMock()
    builder.select.return_value = builder
    builder.eq.return_value = builder
    builder.in_.return_value = builder
    builder.limit.return_value = builder
    builder.order.return_value = builder
    builder.single.return_value = builder
    builder.execute.return_value = MagicMock(data=data)
    return builder


def _mock_supabase_client(tables: dict[str, Any]) -> MagicMock:
    """Create a mock Supabase client that dispatches table names to builders."""
    client = MagicMock()

    def _table(name: str) -> Any:
        return tables.get(name, _mock_query_response([]))

    client.table.side_effect = _table
    return client


def test_get_or_compute_province_climate_batches_and_aggregates(monkeypatch):
    """Province climate fallback must fetch municipality data in batches and aggregate."""
    from app.services import climate_service

    # Province table is empty, so it falls back to municipalities.
    monkeypatch.setattr(
        climate_service,
        "get_climate_data",
        lambda level, geo_id, year: [],
    )

    muni_rows = [
        {"municipality_id": 101},
        {"municipality_id": 102},
    ]
    climate_rows = [
        {"municipality_id": 101, "month": 1, "year": 2024, "t2m": 25.0},
        {"municipality_id": 102, "month": 1, "year": 2024, "t2m": 27.0},
    ]

    tables = {
        "municipalities": _mock_query_response(muni_rows),
        "municipality_climate_monthly": _mock_query_response(climate_rows),
    }
    monkeypatch.setattr(
        climate_service,
        "get_supabase_client",
        lambda: _mock_supabase_client(tables),
    )

    result = climate_service.get_or_compute_province_climate(province_id=10, year=2024)

    assert len(result) == 1
    assert result[0]["t2m"] == 26.0
    assert result[0]["province_id"] == 10
    assert result[0]["source"] == "aggregated_from_municipalities"


def test_aggregate_to_province_averages_municipality_scores():
    """Province map aggregation must average municipality scores per province."""
    muni_rows = [
        {"municipality_id": 1, "province_id": 10, "score": 80.0, "lat": 14.5, "lon": 121.0},
        {"municipality_id": 2, "province_id": 10, "score": 90.0, "lat": 14.6, "lon": 121.1},
        {"municipality_id": 3, "province_id": 20, "score": 60.0, "lat": 15.0, "lon": 122.0},
    ]
    client = _mock_supabase_client({"provinces": _mock_query_response([
        {"province_id": 10, "name": "Test Province", "lat": 14.55, "lon": 121.05},
    ])})

    from app.services.map_service import _aggregate_to_province
    result = _aggregate_to_province(client, muni_rows, "solar")

    assert len(result) == 1
    assert result[0]["geo_id"] == 10
    assert result[0]["name"] == "Test Province"
    assert result[0]["score"] == 85.0
    assert result[0]["lat"] == 14.55
    assert result[0]["lon"] == 121.05
