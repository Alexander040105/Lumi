"""Municipality-level renewable energy suitability builder.

Computes per-municipality suitability scores for solar, wind, hydro,
geothermal, and composite, then persists them to Supabase and
invalidates the Redis cache.

Usage (from repo root, with .venv activated):
    python -m app.services.municipality_suitability_builder --action build
    python -m app.services.municipality_suitability_builder --action refresh --municipality-ids 123 456
"""

from __future__ import annotations

import argparse
import json
import logging
import math
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from app.services.supabase_service import get_supabase_client
from app.services.redis_client import get_redis

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------

_CLASSIFICATION_THRESHOLDS = [
    (81, "Very High"),
    (61, "High"),
    (41, "Moderate"),
    (21, "Low"),
    (0, "Very Low"),
]


def get_classification(score: float | None) -> str | None:
    if score is None:
        return None
    for threshold, label in _CLASSIFICATION_THRESHOLDS:
        if score >= threshold:
            return label
    return "Very Low"


# ---------------------------------------------------------------------------
# Score computation
# ---------------------------------------------------------------------------

def _estimate_solar_from_lat(lat: float) -> tuple[float, float]:
    """Estimate solar irradiance (kWh/m2/day) and temperature (C) from latitude.
    Philippines: ~5-20°N. Lower latitudes = higher irradiance.
    """
    abs_lat = abs(lat)
    irradiance = max(5.0 - (abs_lat / 20.0) * 1.5, 3.5)
    temperature = 26.0 + (abs_lat / 20.0) * 4.0
    return round(irradiance, 2), round(temperature, 1)


def _estimate_wind_from_lat(lat: float, lon: float) -> float:
    """Estimate wind speed from coordinates. Philippines average ~3.2 m/s."""
    return 3.2


def _compute_solar_score(irradiance: float | None, temperature: float | None) -> tuple[float | None, dict[str, Any]]:
    if irradiance is None:
        return None, {}
    score = min((irradiance / 5.0) * 100, 100.0)
    factors = {"irradiance_kwh_m2_day": round(irradiance, 2)}
    if temperature is not None:
        factors["avg_temperature_c"] = round(temperature, 1)
    return round(score, 2), factors


def _compute_wind_score(wind_speed: float | None) -> tuple[float | None, dict[str, Any]]:
    if wind_speed is None:
        return None, {}
    score = min((wind_speed / 7.0) * 100, 100.0)
    factors = {"wind_speed_ms": round(wind_speed, 2)}
    return round(score, 2), factors


def _compute_hydro_score(hydro_suitability: float | None, hydraulic_head: float | None) -> tuple[float | None, dict[str, Any]]:
    if hydro_suitability is None:
        return None, {}
    score = min(hydro_suitability * 100, 100.0)
    factors = {"hydro_suitability_raw": round(hydro_suitability, 4)}
    if hydraulic_head is not None:
        factors["hydraulic_head_m"] = round(hydraulic_head, 1)
    return round(score, 2), factors


def _compute_geothermal_score(
    geothermal_score: float | None,
    reservoir_temp: float | None,
    temperature_score: float | None = None,
) -> tuple[float | None, dict[str, Any]]:
    if geothermal_score is None:
        return None, {}
    score = min(geothermal_score * 100, 100.0)
    factors = {"geothermal_score_raw": round(geothermal_score, 4)}
    if reservoir_temp is not None:
        factors["reservoir_temperature_c"] = round(reservoir_temp, 1)
    elif temperature_score is not None:
        factors["temperature_score"] = round(temperature_score, 4)
    return round(score, 2), factors


def _compute_composite(scores: dict[str, float | None]) -> tuple[float | None, dict[str, Any]]:
    available = [v for v in scores.values() if v is not None]
    if not available:
        return None, {}
    avg = sum(available) / len(available)
    factors = {k: v for k, v in scores.items() if v is not None}
    return round(avg, 2), factors


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def _fetch_all_municipalities(client) -> list[dict[str, Any]]:
    all_rows: list[dict[str, Any]] = []
    start = 0
    batch = 1000
    while True:
        resp = (
            client.table("municipalities")
            .select("municipality_id, name, province_id, lat, lon, provinces(name)")
            .range(start, start + batch - 1)
            .execute()
        )
        rows = resp.data or []
        for r in rows:
            province_obj = r.pop("provinces", None)
            r["province_name"] = province_obj.get("name", "") if province_obj else ""
        all_rows.extend(rows)
        if len(rows) < batch:
            break
        start += batch
    return all_rows


def _fetch_climate_data(client) -> dict[int, dict[str, Any]]:
    """Fetch multi-year annual averages per municipality (all available years)."""
    resp = client.table("municipality_climate_monthly").select(
        "municipality_id, allsky_sfc_sw_dwn, ws10m, t2m, cloud_amt"
    ).limit(10000).execute()
    rows = resp.data or []
    data: dict[int, dict[str, Any]] = defaultdict(dict)
    for r in rows:
        mid = r.get("municipality_id")
        if mid is None:
            continue
        entry = data[mid]
        for key in ("allsky_sfc_sw_dwn", "ws10m", "t2m", "cloud_amt"):
            val = r.get(key)
            if val is not None:
                entry.setdefault(key, []).append(float(val))
    # Average across all months/years
    averaged: dict[int, dict[str, Any]] = {}
    for mid, vals in data.items():
        averaged[mid] = {}
        for key, arr in vals.items():
            if arr:
                averaged[mid][key] = sum(arr) / len(arr)
    return averaged


def _fetch_hydro_data(client) -> dict[int, dict[str, Any]]:
    resp = client.table("hydropower_suitability").select(
        "municipality_id, hydro_suitability_score, hydraulic_head_m"
    ).limit(10000).execute()
    rows = resp.data or []
    data: dict[int, dict[str, Any]] = {}
    for r in rows:
        mid = r.get("municipality_id")
        if mid is not None:
            data[mid] = {
                "hydro_suitability_score": r.get("hydro_suitability_score"),
                "hydraulic_head_m": r.get("hydraulic_head_m"),
            }
    return data


def _fetch_geothermal_data(client) -> dict[int, dict[str, Any]]:
    # 1. Fetch suitability scores (geothermal_score, temperature_score, mcda)
    resp = client.table("geothermal_suitability").select(
        "municipality_id, geothermal_score, geothermal_score_mcda, temperature_score"
    ).limit(10000).execute()
    rows = resp.data or []
    data: dict[int, dict[str, Any]] = {}
    for r in rows:
        mid = r.get("municipality_id")
        if mid is not None:
            data[mid] = {
                "geothermal_score": r.get("geothermal_score"),
                "geothermal_score_mcda": r.get("geothermal_score_mcda"),
                "temperature_score": r.get("temperature_score"),
            }

    # 2. Fetch actual reservoir temperature from geothermal_output
    try:
        out_resp = client.table("geothermal_output").select(
            "municipality_id, reservoir_temperature_c"
        ).limit(10000).execute()
        out_rows = out_resp.data or []
        for r in out_rows:
            mid = r.get("municipality_id")
            if mid is not None and mid in data:
                data[mid]["reservoir_temperature_c"] = r.get("reservoir_temperature_c")
    except Exception:
        # geothermal_output may not exist or have no data; skip gracefully
        pass

    return data


# ---------------------------------------------------------------------------
# Build & persist
# ---------------------------------------------------------------------------

def build_suitability_for_municipality(
    muni: dict[str, Any],
    climate: dict[int, dict[str, Any]],
    hydro: dict[int, dict[str, Any]],
    geo: dict[int, dict[str, Any]],
) -> dict[str, Any] | None:
    mid = muni["municipality_id"]
    c = climate.get(mid, {})
    h = hydro.get(mid, {})
    g = geo.get(mid, {})

    # Use actual NASA POWER data if available; otherwise fall back to lat-based estimates
    irradiance = c.get("allsky_sfc_sw_dwn")
    temperature = c.get("t2m")
    wind_speed = c.get("ws10m")

    if irradiance is None or temperature is None:
        lat = muni.get("lat")
        if lat is not None:
            est_irr, est_temp = _estimate_solar_from_lat(float(lat))
            if irradiance is None:
                irradiance = est_irr
            if temperature is None:
                temperature = est_temp

    if wind_speed is None:
        lat = muni.get("lat")
        lon = muni.get("lon")
        if lat is not None and lon is not None:
            wind_speed = _estimate_wind_from_lat(float(lat), float(lon))

    solar_score, solar_factors = _compute_solar_score(irradiance, temperature)
    wind_score, wind_factors = _compute_wind_score(wind_speed)
    hydro_score, hydro_factors = _compute_hydro_score(
        h.get("hydro_suitability_score"), h.get("hydraulic_head_m")
    )
    geo_score, geo_factors = _compute_geothermal_score(
        g.get("geothermal_score"),
        g.get("reservoir_temperature_c"),
        g.get("temperature_score"),
    )

    composite, composite_factors = _compute_composite({
        "solar": solar_score,
        "wind": wind_score,
        "hydro": hydro_score,
        "geothermal": geo_score,
    })

    return {
        "municipality_id": mid,
        "solar_suitability_score": solar_score,
        "solar_classification": get_classification(solar_score),
        "solar_factors": json.dumps(solar_factors) if solar_factors else None,
        "wind_suitability_score": wind_score,
        "wind_classification": get_classification(wind_score),
        "wind_factors": json.dumps(wind_factors) if wind_factors else None,
        "hydro_suitability_score": hydro_score,
        "hydro_classification": get_classification(hydro_score),
        "hydro_factors": json.dumps(hydro_factors) if hydro_factors else None,
        "geothermal_suitability_score": geo_score,
        "geothermal_classification": get_classification(geo_score),
        "geothermal_score_mcda": g.get("geothermal_score_mcda"),
        "geothermal_factors": json.dumps(geo_factors) if geo_factors else None,
        "composite_suitability_score": composite,
        "composite_classification": get_classification(composite),
        "suitability_updated_at": datetime.now(timezone.utc).isoformat(),
    }


def persist_batch(client, updates: list[dict[str, Any]]) -> None:
    if not updates:
        return
    for up in updates:
        mid = up.pop("municipality_id")
        client.table("municipalities").update(up).eq("municipality_id", mid).execute()
    logger.info("Persisted %s municipality suitability records", len(updates))


def invalidate_suitability_cache() -> None:
    try:
        from app.services.redis_client import get_redis_sync
        redis = get_redis_sync()
        keys = redis.keys("lumi:suitability:*")
        if keys:
            redis.delete(*keys)
            logger.info("Invalidated %s suitability cache keys", len(keys))
    except Exception as exc:
        logger.warning("Cache invalidation failed (non-critical): %s", exc)


def warm_suitability_cache(client) -> None:
    """Pre-populate Redis cache for all renewable types after build."""
    from app.services.redis_client import set_suitability_cache_sync
    prefixes = {
        "solar": "solar",
        "wind": "wind",
        "hydro": "hydro",
        "geothermal": "geothermal",
        "composite": "renewable_potential",
    }
    for prefix, metric_name in prefixes.items():
        try:
            score_col = f"{prefix}_suitability_score"
            class_col = f"{prefix}_classification"
            factors_col = f"{prefix}_factors"
            has_factors = prefix != "composite"
            select_cols = (
                f"municipality_id, name, province_id, lat, lon, "
                f"provinces(name), {score_col}, {class_col}"
            )
            if has_factors:
                select_cols += f", {factors_col}"

            # Paginate through all municipalities with scores
            all_rows = []
            offset = 0
            batch = 1000
            while True:
                resp = (
                    client.table("municipalities")
                    .select(select_cols)
                    .not_.is_(score_col, "null")
                    .range(offset, offset + batch - 1)
                    .execute()
                )
                rows = resp.data or []
                if not rows:
                    break
                all_rows.extend(rows)
                if len(rows) < batch:
                    break
                offset += batch

            items = []
            for r in all_rows:
                province_obj = r.get("provinces")
                province_name = province_obj.get("name", "") if province_obj else ""
                items.append({
                    "region": "",
                    "province": province_name,
                    "municipality": r.get("name"),
                    "municipality_id": r.get("municipality_id"),
                    "value": float(r.get(score_col) or 0),
                    "classification": r.get(class_col),
                    "factors": r.get(factors_col) if has_factors else None,
                    "metric": metric_name,
                    "lat": r.get("lat"),
                    "lon": r.get("lon"),
                })
            set_suitability_cache_sync(metric_name, "municipality", items)
            logger.info("Warmed cache for %s with %s items", metric_name, len(items))
        except Exception as exc:
            logger.warning("Cache warm failed for %s: %s", metric_name, exc)


# ---------------------------------------------------------------------------
# Public orchestrators
# ---------------------------------------------------------------------------

def build_all_municipality_suitability(batch_size: int = 200) -> dict[str, Any]:
    logger.info("Starting full municipality suitability build...")
    client = get_supabase_client()

    municipalities = _fetch_all_municipalities(client)
    logger.info("Fetched %s municipalities", len(municipalities))

    climate = _fetch_climate_data(client)
    hydro = _fetch_hydro_data(client)
    geo = _fetch_geothermal_data(client)

    updates: list[dict[str, Any]] = []
    all_updates: list[dict[str, Any]] = []
    processed = 0
    for muni in municipalities:
        up = build_suitability_for_municipality(muni, climate, hydro, geo)
        if up:
            updates.append(up)
            all_updates.append(up)
        processed += 1
        if len(updates) >= batch_size:
            persist_batch(client, updates)
            updates = []
            logger.info("Progress: %s/%s municipalities", processed, len(municipalities))

    persist_batch(client, updates)
    invalidate_suitability_cache()
    warm_suitability_cache(client)

    summary = {
        "total_municipalities": len(municipalities),
        "processed": processed,
        "with_solar": sum(1 for u in all_updates if u.get("solar_suitability_score") is not None),
        "with_wind": sum(1 for u in all_updates if u.get("wind_suitability_score") is not None),
        "with_hydro": sum(1 for u in all_updates if u.get("hydro_suitability_score") is not None),
        "with_geothermal": sum(1 for u in all_updates if u.get("geothermal_suitability_score") is not None),
    }
    logger.info("Build complete: %s", summary)
    return summary


def refresh_municipality_suitability(municipality_ids: list[int]) -> dict[str, Any]:
    logger.info("Refreshing suitability for %s municipalities", len(municipality_ids))
    client = get_supabase_client()

    municipalities = []
    for mid in municipality_ids:
        resp = client.table("municipalities").select(
            "municipality_id, name, province_id, provinces(name)"
        ).eq("municipality_id", mid).execute()
        row = resp.data[0] if resp.data else None
        if row:
            province_obj = row.pop("provinces", None)
            row["province_name"] = province_obj.get("name", "") if province_obj else ""
            municipalities.append(row)

    climate = _fetch_climate_data(client)
    hydro = _fetch_hydro_data(client)
    geo = _fetch_geothermal_data(client)

    updates = []
    for muni in municipalities:
        up = build_suitability_for_municipality(muni, climate, hydro, geo)
        if up:
            updates.append(up)

    persist_batch(client, updates)
    invalidate_suitability_cache()

    return {
        "refreshed": len(updates),
        "requested": len(municipality_ids),
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Build or refresh municipality suitability scores")
    parser.add_argument("--action", choices=["build", "refresh"], default="build",
                        help="build = full rebuild, refresh = selective update")
    parser.add_argument("--municipality-ids", nargs="+", type=int, default=None,
                        help="Specific municipality IDs to refresh (only for --action refresh)")
    args = parser.parse_args()

    if args.action == "build":
        build_all_municipality_suitability()
    elif args.action == "refresh":
        if not args.municipality_ids:
            logger.error("--municipality-ids required for refresh action")
            return
        refresh_municipality_suitability(args.municipality_ids)


if __name__ == "__main__":
    main()
