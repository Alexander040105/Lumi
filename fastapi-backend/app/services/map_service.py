"""Map data service for LUMI GIS/mapping.

Provides:
- Generic map endpoint backing: fetch suitability scores + centroids
  for any renewable type at any admin level
- Materialized view integration: mv_province_map_data, mv_municipality_map_data
- PSGC join support: join admin units with climate and suitability data
- Projection validation: ensure all coordinates are WGS84 (EPSG:4326)
"""
from __future__ import annotations

import logging
from typing import Any

from app.services.redis_client import (
    get_suitability_cache_sync,
    set_suitability_cache_sync,
)
from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Suitability table mapping
# ---------------------------------------------------------------------------

_SUITABILITY_TABLES: dict[str, dict[str, str]] = {
    "solar": {
        "table": "solar_suitability",
        "score_col": "solar_score",
        "id_col": "municipality_id",
    },
    "wind": {
        "table": "wind_suitability",
        "score_col": "wind_score",
        "id_col": "municipality_id",
    },
    "hydro": {
        "table": "hydropower_suitability",
        "score_col": "hydro_suitability_score",
        "id_col": "municipality_id",
    },
    "geothermal": {
        "table": "geothermal_suitability",
        "score_col": "geothermal_score",
        "id_col": "municipality_id",
    },
}

# Materialized views by level
_MV_TABLES: dict[str, str] = {
    "province": "mv_province_map_data",
    "municipality": "mv_municipality_map_data",
}


# ---------------------------------------------------------------------------
# Projection validation
# ---------------------------------------------------------------------------

def validate_wgs84(lat: float, lon: float) -> bool:
    """Validate that coordinates are within WGS84 (EPSG:4326) bounds.

    Philippine bounds: lat [4.5, 21.5], lon [116.0, 127.0]
    """
    if lat is None or lon is None:
        return False
    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (TypeError, ValueError):
        return False

    # Global WGS84 bounds
    if not (-90 <= lat_f <= 90):
        return False
    if not (-180 <= lon_f <= 180):
        return False

    # Philippine bounds (with small margin)
    if not (4.0 <= lat_f <= 22.0):
        logger.warning("Latitude %s outside Philippine bounds", lat_f)
        return False
    if not (115.0 <= lon_f <= 128.0):
        logger.warning("Longitude %s outside Philippine bounds", lon_f)
        return False

    return True


# ---------------------------------------------------------------------------
# Generic map data retrieval
# ---------------------------------------------------------------------------

def get_map_data(
    renewable_type: str,
    level: str = "municipality",
    use_cache: bool = True,
    use_materialized_view: bool = True,
) -> list[dict[str, Any]]:
    """Fetch map data (suitability scores + centroids) for a renewable type.

    Tries materialized view first, falls back to direct table joins.

    Args:
        renewable_type: solar, wind, hydro, or geothermal
        level: municipality or province
        use_cache: Whether to use Redis cache
        use_materialized_view: Whether to try MV first

    Returns:
        List of dicts with geo_id, name, lat, lon, score, and other fields
    """
    # Check cache
    if use_cache:
        cached = get_suitability_cache_sync(renewable_type, level)
        if cached:
            return cached

    # Try materialized view first
    if use_materialized_view and level in _MV_TABLES:
        mv_data = _fetch_from_materialized_view(renewable_type, level)
        if mv_data:
            if use_cache:
                set_suitability_cache_sync(renewable_type, level, mv_data)
            return mv_data

    # Fall back to direct table joins
    data = _fetch_from_table_join(renewable_type, level)
    if use_cache and data:
        set_suitability_cache_sync(renewable_type, level, data)
    return data


def _fetch_from_materialized_view(
    renewable_type: str,
    level: str,
) -> list[dict[str, Any]]:
    """Fetch from materialized view (mv_municipality_map_data or mv_province_map_data).

    These views join admin boundaries with suitability scores and centroids.
    """
    mv_table = _MV_TABLES.get(level)
    if not mv_table:
        return []

    score_col_map = {
        "solar": "solar_score",
        "wind": "wind_score",
        "hydro": "hydro_score",
        "geothermal": "geothermal_score",
    }
    score_col = score_col_map.get(renewable_type)
    if not score_col:
        return []

    client = get_supabase_client()
    try:
        # Select all columns from the MV
        resp = (
            client.table(mv_table)
            .select(f"*")
            .limit(50000)
            .execute()
        )
        rows = resp.data or []

        # Filter to rows where the relevant score is not null
        filtered = [r for r in rows if r.get(score_col) is not None]

        # Validate coordinates
        result = []
        for r in filtered:
            lat = r.get("lat") or r.get("centroid_lat")
            lon = r.get("lon") or r.get("centroid_lon")
            if lat and lon and validate_wgs84(float(lat), float(lon)):
                result.append(r)

        return result

    except Exception as exc:
        logger.warning("Materialized view fetch failed for %s/%s: %s", renewable_type, level, exc)
        return []


def _fetch_from_table_join(
    renewable_type: str,
    level: str,
) -> list[dict[str, Any]]:
    """Fetch map data by joining admin table with suitability table.

    Fallback when materialized views are not available or empty.
    """
    suit_info = _SUITABILITY_TABLES.get(renewable_type)
    if not suit_info:
        logger.warning("Unknown renewable type: %s", renewable_type)
        return []

    suit_table = suit_info["table"]
    score_col = suit_info["score_col"]
    id_col = suit_info["id_col"]

    if level == "province":
        admin_table = "provinces"
        admin_pk = "province_id"
        select_cols = f"{admin_pk},name,lat,lon"
    else:
        admin_table = "municipalities"
        admin_pk = "municipality_id"
        select_cols = f"{admin_pk},name,lat,lon,province_id"

    client = get_supabase_client()

    try:
        # Fetch admin units with lat/lon
        admin_resp = (
            client.table(admin_table)
            .select(select_cols)
            .limit(50000)
            .execute()
        )
        admin_rows = admin_resp.data or []
        if not admin_rows:
            return []

        # Fetch suitability scores
        suit_resp = (
            client.table(suit_table)
            .select(f"{id_col},{score_col}")
            .limit(50000)
            .execute()
        )
        suit_rows = suit_resp.data or []

        # Build score lookup
        score_lookup: dict[int, float] = {}
        for row in suit_rows:
            geo_id = row.get(id_col)
            score = row.get(score_col)
            if geo_id is not None and score is not None:
                score_lookup[int(geo_id)] = float(score)

        # Join
        result = []
        for row in admin_rows:
            geo_id = row.get(admin_pk)
            lat = row.get("lat")
            lon = row.get("lon")
            score = score_lookup.get(int(geo_id)) if geo_id else None

            if score is None:
                continue
            if not (lat and lon and validate_wgs84(float(lat), float(lon))):
                continue

            result.append({
                "geo_id": geo_id,
                "name": row.get("name"),
                "lat": float(lat),
                "lon": float(lon),
                "score": round(score * 100, 2) if score <= 1.0 else round(score, 2),
                "renewable_type": renewable_type,
                "level": level,
                "province_id": row.get("province_id") if level == "municipality" else None,
            })

        return result

    except Exception as exc:
        logger.warning("Table join fetch failed for %s/%s: %s", renewable_type, level, exc)
        return []


# ---------------------------------------------------------------------------
# PSGC join support
# ---------------------------------------------------------------------------

def get_psgc_hierarchy(
    municipality_id: int | None = None,
    province_id: int | None = None,
) -> dict[str, Any]:
    """Fetch PSGC administrative hierarchy for a given unit.

    Returns the full chain: region → province → municipality → barangays

    Args:
        municipality_id: Optional municipality ID
        province_id: Optional province ID

    Returns:
        Dict with hierarchy levels and metadata
    """
    client = get_supabase_client()
    hierarchy: dict[str, Any] = {}

    try:
        if municipality_id:
            # Fetch municipality with province and region
            resp = (
                client.table("municipalities")
                .select("municipality_id,name,lat,lon,provinces(province_id,name,regions(region_id,name))")
                .eq("municipality_id", str(municipality_id))
                .single()
                .execute()
            )
            if resp.data:
                muni = resp.data
                prov = muni.get("provinces") or {}
                region = prov.get("regions") or {}

                hierarchy["municipality"] = {
                    "id": muni.get("municipality_id"),
                    "name": muni.get("name"),
                    "lat": muni.get("lat"),
                    "lon": muni.get("lon"),
                }
                hierarchy["province"] = {
                    "id": prov.get("province_id"),
                    "name": prov.get("name"),
                }
                hierarchy["region"] = {
                    "id": region.get("region_id"),
                    "name": region.get("name"),
                }

                # Fetch barangays
                brgy_resp = (
                    client.table("barangays")
                    .select("barangay_id,name,lat,lon")
                    .eq("municipality_id", str(municipality_id))
                    .order("name")
                    .execute()
                )
                hierarchy["barangays"] = brgy_resp.data or []

        elif province_id:
            resp = (
                client.table("provinces")
                .select("province_id,name,lat,lon,regions(region_id,name)")
                .eq("province_id", str(province_id))
                .single()
                .execute()
            )
            if resp.data:
                prov = resp.data
                region = prov.get("regions") or {}

                hierarchy["province"] = {
                    "id": prov.get("province_id"),
                    "name": prov.get("name"),
                    "lat": prov.get("lat"),
                    "lon": prov.get("lon"),
                }
                hierarchy["region"] = {
                    "id": region.get("region_id"),
                    "name": region.get("name"),
                }

                # Fetch municipalities
                muni_resp = (
                    client.table("municipalities")
                    .select("municipality_id,name,lat,lon")
                    .eq("province_id", str(province_id))
                    .order("name")
                    .execute()
                )
                hierarchy["municipalities"] = muni_resp.data or []

    except Exception as exc:
        logger.warning("PSGC hierarchy fetch failed: %s", exc)

    return hierarchy


# ---------------------------------------------------------------------------
# Coverage summary
# ---------------------------------------------------------------------------

def get_coverage_summary(level: str = "municipality") -> dict[str, Any]:
    """Fetch data coverage summary for a given admin level.

    Returns counts of units with/without climate data, suitability scores, etc.
    """
    client = get_supabase_client()

    try:
        resp = (
            client.table("coverage_summary")
            .select("*")
            .eq("level", level)
            .execute()
        )
        rows = resp.data or []
        if rows:
            return {"level": level, "items": rows}

        # Fallback: compute on-the-fly
        if level == "municipality":
            total_resp = client.table("municipalities").select("municipality_id", count="exact").execute()
            total = total_resp.count or 0

            climate_resp = (
                client.table("municipality_climate_monthly")
                .select("municipality_id", count="exact")
                .execute()
            )
            with_climate = climate_resp.count or 0

            return {
                "level": level,
                "total_units": total,
                "with_climate_data": with_climate,
                "coverage_pct": round(with_climate / total * 100, 1) if total else 0,
            }

    except Exception as exc:
        logger.warning("Coverage summary fetch failed: %s", exc)

    return {"level": level, "items": []}
