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

from app.services.data_cache import cache_get_sync, cache_set_sync
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

def _format_score(score: Any) -> float:
    """Scale normalized (0-1) scores to 0-100; leave percentage scores as-is."""
    try:
        s = float(score)
    except (TypeError, ValueError):
        return 0.0
    return round(s * 100, 2) if s <= 1.0 else round(s, 2)


def _aggregate_to_province(
    client,
    municipality_rows: list[dict[str, Any]],
    renewable_type: str,
) -> list[dict[str, Any]]:
    """Group municipality scores by province and average them."""
    province_scores: dict[int, list[float]] = {}
    for row in municipality_rows:
        pid = row.get("province_id")
        if pid is None:
            continue
        pid = int(pid)
        province_scores.setdefault(pid, []).append(float(row["score"]))

    if not province_scores:
        return []

    try:
        resp = client.table("provinces").select("province_id,name,lat,lon").limit(50000).execute()
        province_lookup = {
            p["province_id"]: p for p in (resp.data or []) if p.get("province_id") is not None
        }
    except Exception as exc:
        logger.warning("Failed to fetch provinces for aggregation: %s", exc)
        return []

    result = []
    for pid, scores in province_scores.items():
        prov = province_lookup.get(pid)
        if not prov:
            continue
        lat = prov.get("lat")
        lon = prov.get("lon")
        if not (lat and lon and validate_wgs84(float(lat), float(lon))):
            continue
        result.append({
            "geo_id": pid,
            "name": prov.get("name"),
            "lat": float(lat),
            "lon": float(lon),
            "score": round(sum(scores) / len(scores), 2),
            "renewable_type": renewable_type,
            "level": "province",
            "province_id": None,
        })
    return result


def _fetch_municipality_scores(
    client,
    renewable_type: str,
) -> list[dict[str, Any]]:
    """Return municipality-level rows with name, lat, lon, score, and province_id."""
    score_source = {
        "solar": (None, "solar_suitability_score"),
        "wind": (None, "wind_suitability_score"),
        "hydro": ("hydropower_suitability", "hydro_suitability_score"),
        "geothermal": ("geothermal_suitability", "geothermal_score"),
    }.get(renewable_type)

    if not score_source:
        logger.warning("Unknown renewable type: %s", renewable_type)
        return []

    suit_table, score_col = score_source

    if suit_table is None:
        # solar / wind: scores live directly on the municipalities table
        resp = client.table("municipalities").select(
            f"municipality_id,name,lat,lon,province_id,{score_col}"
        ).limit(50000).execute()
        rows = resp.data or []
        result = []
        for r in rows:
            score = r.get(score_col)
            lat = r.get("lat")
            lon = r.get("lon")
            if score is None or lat is None or lon is None:
                continue
            if not validate_wgs84(float(lat), float(lon)):
                continue
            result.append({
                "geo_id": r.get("municipality_id"),
                "name": r.get("name"),
                "lat": float(lat),
                "lon": float(lon),
                "score": _format_score(score),
                "renewable_type": renewable_type,
                "level": "municipality",
                "province_id": r.get("province_id"),
            })
        return result

    # hydro / geothermal: separate source table, joined to municipalities
    suit_resp = client.table(suit_table).select(
        f"municipality_id,{score_col}"
    ).limit(50000).execute()
    suit_rows = {
        r.get("municipality_id"): r.get(score_col)
        for r in (suit_resp.data or [])
        if r.get(score_col) is not None
    }

    if not suit_rows:
        return []

    muni_resp = client.table("municipalities").select(
        "municipality_id,name,lat,lon,province_id"
    ).limit(50000).execute()
    muni_lookup = {
        r.get("municipality_id"): r
        for r in (muni_resp.data or [])
        if r.get("municipality_id") is not None
    }

    result = []
    for muni_id, score in suit_rows.items():
        muni = muni_lookup.get(muni_id)
        if not muni:
            continue
        lat = muni.get("lat")
        lon = muni.get("lon")
        if lat is None or lon is None:
            continue
        if not validate_wgs84(float(lat), float(lon)):
            continue
        result.append({
            "geo_id": muni_id,
            "name": muni.get("name"),
            "lat": float(lat),
            "lon": float(lon),
            "score": _format_score(score),
            "renewable_type": renewable_type,
            "level": "municipality",
            "province_id": muni.get("province_id"),
        })
    return result


def get_map_data(
    renewable_type: str,
    level: str = "municipality",
    use_cache: bool = True,
    use_materialized_view: bool = True,
) -> list[dict[str, Any]]:
    """Fetch map data (suitability scores + centroids) for a renewable type.

    Uses the actual Supabase schema:
    - solar/wind scores are columns on municipalities
    - hydro scores are in hydropower_suitability
    - geothermal scores are in geothermal_suitability
    """
    normalized_level = (level or "municipality").split(":")[0].lower().strip()
    if normalized_level not in {"municipality", "province"}:
        normalized_level = "municipality"

    if use_cache:
        cached = get_suitability_cache_sync(renewable_type, normalized_level)
        if cached:
            return cached

    try:
        client = get_supabase_client()
        municipality_rows = _fetch_municipality_scores(client, renewable_type)

        if normalized_level == "province":
            data = _aggregate_to_province(client, municipality_rows, renewable_type)
        else:
            data = municipality_rows

        if use_cache and data:
            set_suitability_cache_sync(renewable_type, normalized_level, data)
        return data

    except Exception as exc:
        logger.warning("Map data fetch failed for %s/%s: %s", renewable_type, normalized_level, exc)
        return []


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
    target = municipality_id if municipality_id is not None else province_id
    cache_key = f"lumi:psgc:{target}"
    cached = cache_get_sync(cache_key)
    if cached is not None:
        return cached

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

    if hierarchy:
        cache_set_sync(cache_key, hierarchy, ttl=86400)
    return hierarchy


# ---------------------------------------------------------------------------
# Coverage summary
# ---------------------------------------------------------------------------

def get_coverage_summary(level: str = "municipality") -> dict[str, Any]:
    """Fetch data coverage summary for a given admin level.

    Returns counts of units with/without climate data, suitability scores, etc.
    """
    normalized_level = (level or "municipality").split(":")[0].lower().strip()
    if normalized_level not in {"municipality", "province"}:
        normalized_level = "municipality"

    cache_key = f"lumi:coverage:{normalized_level}"
    cached = cache_get_sync(cache_key)
    if cached is not None:
        return cached

    client = get_supabase_client()

    # Try a pre-computed coverage_summary table first
    try:
        resp = (
            client.table("coverage_summary")
            .select("*")
            .eq("level", normalized_level)
            .execute()
        )
        rows = resp.data or []
        if rows:
            result = {"level": normalized_level, "items": rows}
            cache_set_sync(cache_key, result, ttl=3600)
            return result
    except Exception as exc:
        logger.warning("Pre-computed coverage_summary not available: %s", exc)

    # Fallback: compute on-the-fly for municipalities
    if normalized_level == "municipality":
        try:
            total_resp = client.table("municipalities").select("municipality_id", count="exact").execute()
            total = getattr(total_resp, "count", None) or len(total_resp.data or [])

            climate_resp = client.table("municipalities").select(
                "municipality_id,municipality_climate_monthly!inner(municipality_id)",
                count="exact",
            ).execute()
            with_climate = getattr(climate_resp, "count", None) or len(climate_resp.data or [])

            result = {
                "level": normalized_level,
                "total_units": total,
                "with_climate_data": with_climate,
                "coverage_pct": round(with_climate / total * 100, 1) if total else 0,
            }
            cache_set_sync(cache_key, result, ttl=3600)
            return result
        except Exception as exc:
            logger.warning("Coverage on-the-fly count failed: %s", exc)

    result = {"level": normalized_level, "items": []}
    cache_set_sync(cache_key, result, ttl=3600)
    return result
