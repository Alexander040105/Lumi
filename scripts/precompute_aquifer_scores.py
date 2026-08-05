#!/usr/bin/env python3
"""
Precompute aquifer scores for every municipality and write them into
public.geothermal_suitability.

Run from the repo root after migrating the rest of the data:
    python scripts/precompute_aquifer_scores.py

Required environment variables (from the repo root .env):
    SUPABASE_URL
    SUPABASE_SERVICE_ROLE_KEY
"""

from __future__ import annotations

import json
import logging
import math
import os
import re
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from shapely.geometry import Point
from supabase import Client, create_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE, override=True)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")

AQUIFER_PATH = ROOT / "fastapi-backend/app/services/local_data/aquifers_ph.geojson"
BATCH_SIZE = 500

# Fallback options: only use the nearest aquifer if it is within this distance.
AQUIFER_FALLBACK_BUFFER_KM = 10.0
# UTM 51N is a reasonable metric projection for the Philippines.  The script
# uses it only for the fallback distance check, so the ~0.2% scale error at
# the country edges is acceptable for a 10 km buffer.
AQUIFER_PROJECTED_CRS = "EPSG:32651"


_JWT_PATTERN = re.compile(r"^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$")


def _is_jwt_key(key: str) -> bool:
    return bool(key) and _JWT_PATTERN.match(key) is not None


def _resolve_service_role_key() -> str:
    """Return a JWT-formatted key the supabase-py client can use.

    Falls back from SUPABASE_SERVICE_ROLE_KEY to the explicit
    SUPABASE_JWT_SERVICE_ROLE_KEY if the primary value is not a JWT.
    """
    for env_name in (
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_JWT_SERVICE_ROLE_KEY",
        "SUPABASE_ANON_KEY",
    ):
        value = os.environ.get(env_name)
        if value and _is_jwt_key(value):
            return value
    raise RuntimeError(
        "No JWT-formatted Supabase key found. "
        "Set SUPABASE_SERVICE_ROLE_KEY to a valid eyJ... JWT, or set "
        "SUPABASE_JWT_SERVICE_ROLE_KEY to the service_role JWT."
    )


def _get_client() -> Client:
    return create_client(SUPABASE_URL, _resolve_service_role_key())


def _load_aquifer_gdf() -> tuple[Any, Any]:
    """Load the aquifer GeoJSON as a GeoDataFrame in EPSG:4326 and a metric CRS."""
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise RuntimeError(
            "geopandas is required for aquifer precomputation. "
            "Install it with: pip install geopandas"
        ) from exc

    gdf = gpd.read_file(AQUIFER_PATH)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    else:
        gdf = gdf.to_crs("EPSG:4326")
    gdf_projected = gdf.to_crs(AQUIFER_PROJECTED_CRS)
    return gdf, gdf_projected


def _sanitize(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    return value


def _penalised_score(raw_score: float | None, distance_km: float) -> float | None:
    """Apply a linear distance decay so the score is conservative for fallback matches.

    At 0 km from the polygon the raw score is kept; at the buffer edge it drops to 0.
    """
    if raw_score is None or raw_score <= 0.0:
        return None
    if AQUIFER_FALLBACK_BUFFER_KM <= 0:
        return raw_score
    factor = max(0.0, 1.0 - distance_km / AQUIFER_FALLBACK_BUFFER_KM)
    return round(max(0.0, min(1.0, raw_score * factor)), 6)


def _compute_aquifer_score(props: dict[str, Any], stats: dict[str, Any]) -> float:
    """
    Composite 0-1 aquifer score from porosity, permeability and thickness.
    Higher values mean a more suitable aquifer for geothermal reinjection/storage.
    """
    porosity = _sanitize(props.get("porosity")) or 0.0
    perm_log10 = _sanitize(props.get("permeability_log10"))
    thickness = _sanitize(props.get("thickness_m")) or 0.0

    porosity_score = max(0.0, min(1.0, porosity))

    if perm_log10 is not None and stats.get("perm_range") is not None:
        pmin, pmax = stats["perm_range"]
        if pmax != pmin:
            perm_score = max(0.0, min(1.0, (perm_log10 - pmin) / (pmax - pmin)))
        else:
            perm_score = 0.0
    else:
        perm_score = 0.0

    thickness_min = stats.get("thickness_min", 0.0)
    thickness_max = stats.get("thickness_max", 1.0)
    denom = thickness_max - thickness_min if thickness_max != thickness_min else 1.0
    thickness_score = max(0.0, min(1.0, (thickness - thickness_min) / denom))

    # Weights: porosity most important for storage, permeability for flow,
    # thickness for reservoir volume.
    score = 0.4 * porosity_score + 0.3 * perm_score + 0.3 * thickness_score
    return round(max(0.0, min(1.0, score)), 6)


def _aquifer_stats(gdf: Any) -> dict[str, Any]:
    """Pre-compute normalisation bounds from the aquifer dataset."""
    perms = [
        float(row["permeability_log10"])
        for _, row in gdf.iterrows()
        if pd.notnull(row.get("permeability_log10"))
    ]
    thicknesses = [
        float(row["thickness_m"])
        for _, row in gdf.iterrows()
        if pd.notnull(row.get("thickness_m"))
    ]
    return {
        "perm_range": (min(perms), max(perms)) if perms else (0.0, 1.0),
        "thickness_min": min(thicknesses) if thicknesses else 0.0,
        "thickness_max": max(thicknesses) if thicknesses else 1.0,
    }


def _reset_geothermal_suitability(client: Client) -> None:
    """Delete every row in geothermal_suitability before re-seeding.

    Previous runs left orphan, duplicate and mismatched rows.  Because we are
    about to re-insert freshly computed records, the safest step is a full table
    wipe.  Deleting in pages of 1000 with offset=0 works because the table
    shrinks as rows are removed.
    """
    resp = client.table("geothermal_suitability").select("*", count="exact").limit(1).execute()
    start_count = getattr(resp, "count", 0) or 0
    if start_count == 0:
        return

    logger.info("Resetting geothermal_suitability (current rows=%s)", start_count)

    # Try a single bulk delete of every row.  gte(0) works for both numeric and
    # text municipality_id values, and skips any nulls on the off chance they
    # exist (the column is a primary key, so there should not be any).
    try:
        client.table("geothermal_suitability").delete().gte("municipality_id", "0").execute()
    except Exception as exc:
        logger.warning("Bulk delete failed, will delete per row: %s", exc)

    # Confirm the table is empty; if not, delete the remaining rows one by one.
    # Always read from offset 0 because rows are being deleted; the next page
    # becomes the new page 0.
    page_size = 1000
    while True:
        resp = client.table("geothermal_suitability").select("municipality_id", count="exact").limit(1).execute()
        remaining = getattr(resp, "count", 0) or 0
        if remaining == 0:
            break

        batch = client.table("geothermal_suitability").select("municipality_id").limit(page_size).offset(0).execute().data or []
        if not batch:
            break
        for row in batch:
            try:
                client.table("geothermal_suitability").delete().eq("municipality_id", row["municipality_id"]).execute()
            except Exception as exc:
                logger.warning("Failed to delete row %s: %s", row.get("municipality_id"), exc)

    logger.info("geothermal_suitability reset complete")


def main() -> None:
    client = _get_client()
    logger.info("Loading aquifer GeoJSON from %s", AQUIFER_PATH)
    gdf, gdf_projected = _load_aquifer_gdf()
    stats = _aquifer_stats(gdf)

    logger.info("Fetching municipalities from Supabase")
    municipalities: list[dict[str, Any]] = []
    offset = 0
    page_size = 1000
    while True:
        resp = client.table("municipalities").select("municipality_id,lat,lon").limit(page_size).offset(offset).execute()
        batch = resp.data or []
        if not batch:
            break
        municipalities.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size
    logger.info("Found %s municipalities", len(municipalities))

    _reset_geothermal_suitability(client)

    updates: list[dict[str, Any]] = []
    unmatched_records: list[dict[str, Any]] = []
    primary_matched = 0
    fallback_matched = 0
    unmatched = 0
    fallback_distances: list[float] = []

    # Pre-project municipality points to the metric CRS for fast distance checks.
    valid_munis = [
        m for m in municipalities
        if m.get("lat") is not None and m.get("lon") is not None and m.get("municipality_id") is not None
    ]
    if valid_munis:
        import geopandas as gpd

        points_gdf = gpd.GeoDataFrame(
            {"municipality_id": [m["municipality_id"] for m in valid_munis]},
            geometry=[Point(m["lon"], m["lat"]) for m in valid_munis],
            crs="EPSG:4326",
        ).to_crs(AQUIFER_PROJECTED_CRS)
        points_indexed = points_gdf.set_index("municipality_id")["geometry"]
    else:
        points_indexed = None

    for muni in municipalities:
        muni_id = muni.get("municipality_id")
        lat = muni.get("lat")
        lon = muni.get("lon")
        if muni_id is None:
            continue
        if lat is None or lon is None:
            unmatched += 1
            unmatched_records.append(
                {
                    "municipality_id": muni_id,
                    "aquifer_score": None,
                    "aquifer_porosity": None,
                    "aquifer_permeability_log10": None,
                    "aquifer_thickness_m": None,
                    "aquifer_depth_m": None,
                    "aquifer_basin_name": None,
                    "aquifer_fallback": None,
                    "aquifer_distance_km": None,
                    "updated_at": "now()",
                }
            )
            continue

        point = Point(lon, lat)
        matches = gdf[gdf.geometry.contains(point)]

        fallback = False
        distance_km: float | None = None

        if matches.empty:
            # Strict nearest-aquifer fallback: only accept if within the buffer.
            if points_indexed is not None and muni_id in points_indexed.index:
                point_proj = points_indexed.at[muni_id]
                distances = gdf_projected.geometry.distance(point_proj)
                min_distance_m = float(distances.min())
                distance_km = min_distance_m / 1000.0

                if distance_km <= AQUIFER_FALLBACK_BUFFER_KM:
                    nearest_idx = distances.idxmin()
                    row = gdf.loc[nearest_idx]
                    fallback = True
                    fallback_matched += 1
                    fallback_distances.append(distance_km)
                else:
                    unmatched += 1
                    unmatched_records.append(
                        {
                            "municipality_id": muni_id,
                            "aquifer_score": None,
                            "aquifer_porosity": None,
                            "aquifer_permeability_log10": None,
                            "aquifer_thickness_m": None,
                            "aquifer_depth_m": None,
                            "aquifer_basin_name": None,
                            "aquifer_fallback": None,
                            "aquifer_distance_km": None,
                            "updated_at": "now()",
                        }
                    )
                    continue
            else:
                unmatched += 1
                unmatched_records.append(
                    {
                        "municipality_id": muni_id,
                        "aquifer_score": None,
                        "aquifer_porosity": None,
                        "aquifer_permeability_log10": None,
                        "aquifer_thickness_m": None,
                        "aquifer_depth_m": None,
                        "aquifer_basin_name": None,
                        "aquifer_fallback": None,
                        "aquifer_distance_km": None,
                        "updated_at": "now()",
                    }
                )
                continue
        else:
            # If several polygons overlap, pick the one with the highest thickness.
            row = matches.loc[matches["thickness_m"].idxmax()]
            primary_matched += 1

        props = row.to_dict()
        raw_score = _compute_aquifer_score(props, stats)
        aquifer_score = _penalised_score(raw_score, distance_km) if fallback else raw_score

        updates.append(
            {
                "municipality_id": muni_id,
                "aquifer_score": aquifer_score,
                "aquifer_porosity": _sanitize(props.get("porosity")),
                "aquifer_permeability_log10": _sanitize(props.get("permeability_log10")),
                "aquifer_thickness_m": _sanitize(props.get("thickness_m")),
                "aquifer_depth_m": _sanitize(props.get("depth_m")),
                "aquifer_basin_name": str(props.get("basin_name")) if props.get("basin_name") else None,
                "aquifer_fallback": fallback,
                "aquifer_distance_km": _sanitize(distance_km),
                "updated_at": "now()",
            }
        )

    # The table was just reset, so batch insert is safe and much faster than
    # 1000 sequential PATCH/POST calls.  Split into 500-row inserts because that
    # is below the 1000-row API cap and keeps responses manageable.
    all_updates = updates + unmatched_records
    # Defensive deduplication: the municipalities table should be unique, but
    # mixed types (int vs string) can make two rows look different to Python
    # while clashing on the database primary key.
    deduped: dict[str, dict[str, Any]] = {}
    for record in all_updates:
        key = str(record["municipality_id"])
        deduped[key] = record
    all_updates = list(deduped.values())

    for i in range(0, len(all_updates), BATCH_SIZE):
        batch = all_updates[i : i + BATCH_SIZE]
        try:
            resp = client.table("geothermal_suitability").insert(batch).execute()
            logger.info(
                "Inserted batch %s-%s: %s rows",
                i,
                min(i + BATCH_SIZE, len(all_updates)),
                len(resp.data) if resp.data else 0,
            )
        except Exception as exc:
            logger.error("Failed to insert batch %s-%s: %s", i, i + BATCH_SIZE, exc)

    logger.info(
        "Precomputed aquifer scores: primary=%s, fallback=%s, unmatched=%s (total=%s)",
        primary_matched,
        fallback_matched,
        unmatched,
        len(municipalities),
    )
    if fallback_distances:
        logger.info(
            "Fallback distances: max=%.2f km, avg=%.2f km",
            max(fallback_distances),
            sum(fallback_distances) / len(fallback_distances),
        )


if __name__ == "__main__":
    main()
