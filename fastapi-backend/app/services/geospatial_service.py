"""Geospatial metadata service for centroid and area queries.

Provides access to the geospatial_metadata table for retrieving
centroid coordinates, area, and elevation at any administrative level.
Uses Redis caching for frequently accessed data.
"""
from __future__ import annotations

import logging
from typing import Any

from app.services.data_cache import cache_get_sync, cache_set_sync
from app.services.redis_client import (
    get_centroid_cache_sync,
    set_centroid_cache_sync,
)
from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Single-unit lookup
# ---------------------------------------------------------------------------

_GEO_COL_MAP = {
    "region": "region_id",
    "province": "province_id",
    "municipality": "municipality_id",
    "barangay": "barangay_id",
}


def get_geospatial_metadata(
    level: str,
    geo_id: int,
) -> dict[str, Any] | None:
    """Fetch geospatial metadata for a single admin unit.

    Returns dict with centroid_lat, centroid_lon, area_km2, elevation_m, etc.
    or None if not found.
    """
    if level not in _GEO_COL_MAP:
        logger.warning("Unknown geospatial level: %s", level)
        return None

    cache_key = f"lumi:geospatial:{level}:{geo_id}"
    cached = cache_get_sync(cache_key)
    if cached is not None:
        logger.debug("Geospatial metadata cache hit: %s/%s", level, geo_id)
        return cached

    fk_col = _GEO_COL_MAP[level]
    client = get_supabase_client()

    try:
        resp = (
            client.table("geospatial_metadata")
            .select("*")
            .eq(fk_col, str(geo_id))
            .limit(1)
            .execute()
        )
        if resp.data:
            result = resp.data[0]
            cache_set_sync(cache_key, result, ttl=86400)
            return result
    except Exception as exc:
        logger.warning("Geospatial metadata query failed for %s/%s: %s", level, geo_id, exc)

    return None


def get_centroid(level: str, geo_id: int) -> tuple[float, float] | None:
    """Get (lat, lon) centroid for an admin unit. Returns None if not found."""
    meta = get_geospatial_metadata(level, geo_id)
    if meta and meta.get("centroid_lat") and meta.get("centroid_lon"):
        return (float(meta["centroid_lat"]), float(meta["centroid_lon"]))
    return None


# ---------------------------------------------------------------------------
# Bulk lookups (with Redis caching)
# ---------------------------------------------------------------------------


def get_all_centroids(level: str, use_cache: bool = True) -> list[dict[str, Any]]:
    """Fetch all centroids for a given level.

    Returns list of dicts with geo_id, name, centroid_lat, centroid_lon, area_km2.
    """
    if level not in _GEO_COL_MAP:
        logger.warning("Unknown geospatial level: %s", level)
        return []

    if use_cache:
        cached = get_centroid_cache_sync(level)
        if cached:
            return cached

    fk_col = _GEO_COL_MAP[level]
    admin_table = f"{level}s"  # regions, provinces, municipalities, barangays
    admin_pk = f"{level}_id"

    client = get_supabase_client()

    try:
        # Join admin table with geospatial_metadata
        select_cols = f"{admin_pk},name,geospatial_metadata(centroid_lat,centroid_lon,area_km2,elevation_m)"
        resp = (
            client.table(admin_table)
            .select(select_cols)
            .execute()
        )
        rows = resp.data or []

        result = []
        for r in rows:
            geo = r.get("geospatial_metadata")
            if isinstance(geo, list):
                geo = geo[0] if geo else None
            if geo and geo.get("centroid_lat"):
                result.append({
                    "geo_id": r.get(admin_pk),
                    "name": r.get("name"),
                    "centroid_lat": float(geo["centroid_lat"]),
                    "centroid_lon": float(geo["centroid_lon"]),
                    "area_km2": geo.get("area_km2"),
                    "elevation_m": geo.get("elevation_m"),
                })

        if use_cache and result:
            set_centroid_cache_sync(level, result)

        return result

    except Exception as exc:
        logger.warning("Bulk centroid query failed for %s: %s", level, exc)
        return []


# ---------------------------------------------------------------------------
# Fallback: get centroid from admin table's lat/lon columns
# ---------------------------------------------------------------------------


def get_centroid_fallback(level: str, geo_id: int) -> tuple[float, float] | None:
    """Fallback: get lat/lon directly from admin table if geospatial_metadata is empty.

    The admin tables (regions, provinces, municipalities, barangays) still
    have lat/lon columns from the original schema. Use these as a fallback
    when geospatial_metadata has no entry.
    """
    admin_table = f"{level}s"
    admin_pk = f"{level}_id"

    client = get_supabase_client()

    try:
        resp = (
            client.table(admin_table)
            .select(f"{admin_pk},lat,lon")
            .eq(admin_pk, str(geo_id))
            .limit(1)
            .execute()
        )
        if resp.data:
            row = resp.data[0]
            lat = row.get("lat")
            lon = row.get("lon")
            if lat is not None and lon is not None:
                return (float(lat), float(lon))
    except Exception as exc:
        logger.debug("Centroid fallback query failed for %s/%s: %s", level, geo_id, exc)

    return None


def get_centroid_with_fallback(level: str, geo_id: int) -> tuple[float, float] | None:
    """Get centroid from geospatial_metadata, falling back to admin table lat/lon."""
    centroid = get_centroid(level, geo_id)
    if centroid:
        return centroid
    return get_centroid_fallback(level, geo_id)
