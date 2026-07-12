"""Climate data service for multi-resolution geographic queries.

Provides climate data retrieval at province, municipality, and barangay levels
with fallback strategies when data at a given level is unavailable.

Resolution hierarchy: barangay → municipality → province
Fallback: If barangay data is missing, use parent municipality.
          If municipality data is missing, use province.
          If province data is missing, return empty.
"""
from __future__ import annotations

import logging
from typing import Any

from app.services.redis_client import (
    get_climate_cache_sync,
    set_climate_cache_sync,
)
from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Resolution detection
# ---------------------------------------------------------------------------

def determine_resolution(
    province_id: int | None = None,
    municipality_id: int | None = None,
    barangay_id: int | None = None,
) -> str:
    """Determine the finest available geographic resolution."""
    if barangay_id is not None:
        return "barangay"
    if municipality_id is not None:
        return "municipality"
    if province_id is not None:
        return "province"
    return "national"


# ---------------------------------------------------------------------------
# Climate table mapping
# ---------------------------------------------------------------------------

_CLIMATE_TABLES = {
    "province": "province_climate_monthly",
    "municipality": "municipality_climate_monthly",
    "barangay": "barangay_climate_monthly",
}

_CLIMATE_FK_COL = {
    "province": "province_id",
    "municipality": "municipality_id",
    "barangay": "barangay_id",
}


# ---------------------------------------------------------------------------
# Climate data retrieval with fallback
# ---------------------------------------------------------------------------


def get_climate_data(
    level: str,
    geo_id: int,
    year: int | None = None,
    use_cache: bool = True,
) -> list[dict[str, Any]]:
    """Fetch climate data for a geographic unit at a given level.

    Args:
        level: 'province', 'municipality', or 'barangay'
        geo_id: The ID for the given level
        year: Optional year filter. If None, returns all years.
        use_cache: Whether to use Redis cache.

    Returns:
        List of monthly climate records.
    """
    if level not in _CLIMATE_TABLES:
        logger.warning("Unknown climate level: %s", level)
        return []

    # Try cache first
    cache_year = year if year else "all"
    if use_cache:
        cached = get_climate_cache_sync(level, geo_id, cache_year)
        if cached:
            logger.debug("Climate cache hit: %s/%s/%s", level, geo_id, cache_year)
            return cached

    # Query Supabase
    table = _CLIMATE_TABLES[level]
    fk_col = _CLIMATE_FK_COL[level]
    client = get_supabase_client()

    try:
        query = client.table(table).select("*").eq(fk_col, str(geo_id))
        if year is not None:
            query = query.eq("year", str(year))
        query = query.order("year", desc=False).order("month", desc=False)
        resp = query.execute()
        rows = resp.data or []
    except Exception as exc:
        logger.warning("Climate query failed for %s/%s: %s", level, geo_id, exc)
        return []

    if use_cache and rows:
        set_climate_cache_sync(level, geo_id, cache_year, rows)

    return rows


def get_climate_with_fallback(
    barangay_id: int | None = None,
    municipality_id: int | None = None,
    province_id: int | None = None,
    year: int | None = None,
) -> tuple[str, int, list[dict[str, Any]]]:
    """Fetch climate data with automatic fallback.

    Tries barangay → municipality → province resolution.
    Returns (actual_level, actual_geo_id, climate_records).

    Fallback strategy:
    1. Try the finest available level (barangay > municipality > province)
    2. If no data at that level, fall back to the next coarser level
    3. If no data at any level, return empty list
    """
    # Build resolution chain
    chain: list[tuple[str, int]] = []
    if barangay_id is not None:
        chain.append(("barangay", barangay_id))
    if municipality_id is not None:
        chain.append(("municipality", municipality_id))
    if province_id is not None:
        chain.append(("province", province_id))

    if not chain:
        logger.warning("No geographic IDs provided for climate lookup")
        return ("none", 0, [])

    for level, gid in chain:
        data = get_climate_data(level, gid, year)
        if data:
            logger.debug("Climate data found at %s level (id=%s): %s records", level, gid, len(data))
            return (level, gid, data)

    # All levels returned empty
    logger.info(
        "No climate data found at any level for barangay=%s, muni=%s, prov=%s",
        barangay_id, municipality_id, province_id,
    )
    return (chain[0][0], chain[0][1], [])


# ---------------------------------------------------------------------------
# Province climate aggregation from municipality data
# ---------------------------------------------------------------------------


def get_or_compute_province_climate(
    province_id: int,
    year: int,
    client=None,
) -> list[dict[str, Any]]:
    """Get province climate from dedicated table, or compute from municipalities.

    If province_climate_monthly has data for this province/year, return it.
    Otherwise, aggregate from municipality_climate_monthly for all
    municipalities in the province.
    """
    # Try province table first
    data = get_climate_data("province", province_id, year)
    if data:
        return data

    # Fall back to aggregating from municipalities
    if client is None:
        client = get_supabase_client()

    try:
        # Get all municipality IDs in this province
        muni_resp = (
            client.table("municipalities")
            .select("municipality_id")
            .eq("province_id", str(province_id))
            .execute()
        )
        muni_ids = [r["municipality_id"] for r in (muni_resp.data or [])]
        if not muni_ids:
            return []

        # Fetch all municipality climate data for the year
        all_rows = []
        for mid in muni_ids:
            rows = get_climate_data("municipality", mid, year)
            all_rows.extend(rows)

        if not all_rows:
            return []

        # Aggregate by month
        from collections import defaultdict
        import statistics

        monthly: dict[int, list[dict]] = defaultdict(list)
        for r in all_rows:
            month = r.get("month")
            if month is not None:
                monthly[month].append(r)

        aggregated = []
        climate_cols = [
            "t2m", "t2m_max", "t2m_min", "rh2m", "prectotcorr",
            "ws10m", "allsky_sfc_sw_dwn", "cloud_amt", "surface_pressure",
            "elevation", "rhoa",
        ]
        for month in sorted(monthly.keys()):
            records = monthly[month]
            agg = {
                "province_id": province_id,
                "year": year,
                "month": month,
                "source": "aggregated_from_municipalities",
            }
            for col in climate_cols:
                values = [r.get(col) for r in records if r.get(col) is not None]
                if values:
                    agg[col] = round(statistics.mean(values), 4)
                else:
                    agg[col] = None
            aggregated.append(agg)

        return aggregated

    except Exception as exc:
        logger.warning("Province climate aggregation failed for %s/%s: %s", province_id, year, exc)
        return []


# ---------------------------------------------------------------------------
# Barangay fallback to municipality
# ---------------------------------------------------------------------------


def get_barangay_climate_or_fallback(
    barangay_id: int,
    municipality_id: int,
    province_id: int,
    year: int | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Get barangay climate data, falling back to municipality then province.

    Returns (source_level, climate_records).
    """
    # 1. Try barangay table
    data = get_climate_data("barangay", barangay_id, year)
    if data:
        return ("barangay", data)

    # 2. Fall back to municipality
    data = get_climate_data("municipality", municipality_id, year)
    if data:
        logger.info("Barangay %s climate falling back to municipality %s", barangay_id, municipality_id)
        return ("municipality", data)

    # 3. Fall back to province
    data = get_or_compute_province_climate(province_id, year or 2024)
    if data:
        logger.info("Barangay %s climate falling back to province %s", barangay_id, province_id)
        return ("province", data)

    return ("none", [])
