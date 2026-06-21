"""Fill missing municipality lat/lon from Philippine GeoJSON centroids.

This script:
1. Loads the Philippine municipality GeoJSON (per-provinces file).
2. Calculates centroids for each municipality polygon.
3. Fuzzy-matches GeoJSON municipality names to DB municipality names.
4. Updates Supabase with the centroid coordinates.

Usage:
    python python_scripts/fill_missing_coords_from_geojson.py
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

import httpx
import pandas as pd
from shapely.geometry import shape

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

GEOJSON_PATH = Path("philippine_geojson/philippine_geojson_file_per_provinces.json")
CSV_MUNI_PATH = Path("regionalData/municipalities.csv")
CSV_PROV_PATH = Path("regionalData/provinces.csv")

# Supabase REST config
load_env = Path(".env")
if load_env.is_file():
    with open(load_env, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_JWT_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_JWT_ANON_KEY")
    or os.environ.get("SUPABASE_ANON_KEY")
    or os.environ.get("SUPABASE_KEY")
    or ""
)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Prefer": "return=minimal",
}


def _rest_get(table: str, params: dict) -> list[dict]:
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = httpx.get(url, params=params, headers=HEADERS, timeout=30.0)
    resp.raise_for_status()
    return resp.json() or []


def _rest_patch(table: str, pk_col: str, pk_val: int, data: dict) -> None:
    url = f"{SUPABASE_URL}/rest/v1/{table}?{pk_col}=eq.{pk_val}"
    resp = httpx.patch(url, json=data, headers={**HEADERS, "Prefer": "return=minimal"}, timeout=30.0)
    if resp.status_code not in (200, 204):
        logger.warning("PATCH failed for %s.%s=%s: %s %s", table, pk_col, pk_val, resp.status_code, resp.text[:200])


def normalize_name(name: str) -> str:
    """Normalize municipality name for matching."""
    return (
        name.upper()
        .replace(" CITY", "")
        .replace(" (POB.)", "")
        .replace(" (CAPITAL)", "")
        .replace(" (", " ")
        .replace(")", " ")
        .replace(".", "")
        .strip()
    )


def compute_centroids(geojson_path: Path) -> dict[str, tuple[float, float]]:
    """Compute centroid lat/lon for each municipality in GeoJSON."""
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    centroids: dict[str, tuple[float, float]] = {}
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        name = props.get("adm3_en", "").strip()
        if not name:
            continue
        geom = feat.get("geometry")
        if not geom:
            continue
        try:
            poly = shape(geom)
            centroid = poly.centroid
            centroids[normalize_name(name)] = (round(centroid.y, 6), round(centroid.x, 6))
        except Exception:
            continue

    logger.info("Computed %d centroids from GeoJSON", len(centroids))
    return centroids


def main() -> int:
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("Missing SUPABASE_URL or SUPABASE_KEY")
        return 1

    if not GEOJSON_PATH.exists():
        logger.error("GeoJSON not found: %s", GEOJSON_PATH)
        return 1

    # 1. Load GeoJSON centroids
    logger.info("Loading GeoJSON centroids...")
    centroids = compute_centroids(GEOJSON_PATH)

    # 2. Load municipalities CSV for name mapping
    logger.info("Loading municipalities CSV...")
    municipalities = pd.read_csv(CSV_MUNI_PATH)
    provinces = pd.read_csv(CSV_PROV_PATH).rename(columns={"Name": "name"})
    prov_map = dict(zip(provinces["province_id"], provinces["name"]))

    # 3. Fetch missing municipality IDs from Supabase
    logger.info("Fetching municipalities missing lat/lon...")
    missing_ids: list[int] = []
    offset = 0
    while True:
        params = {
            "select": "municipality_id,name",
            "or": "(lat.is.null,lon.is.null)",
            "offset": str(offset),
            "limit": "1000",
        }
        rows = _rest_get("municipalities", params)
        if not rows:
            break
        for row in rows:
            missing_ids.append(int(row["municipality_id"]))
        if len(rows) < 1000:
            break
        offset += 1000

    logger.info("Found %d municipalities missing coordinates", len(missing_ids))

    # 4. Build name -> (lat, lon) map from GeoJSON centroids
    updated = 0
    failed = 0
    for _, row in municipalities.iterrows():
        mid = int(row["municipality_id"])
        if mid not in missing_ids:
            continue

        name = str(row["name"])
        norm = normalize_name(name)

        # Try exact normalized match first
        coords = centroids.get(norm)

        # If no match, try without parenthetical suffix
        if not coords and "(" in norm:
            alt = norm.split("(")[0].strip()
            coords = centroids.get(alt)

        if not coords:
            logger.warning("No GeoJSON match for: %s (normalized: %s)", name, norm)
            failed += 1
            continue

        lat, lon = coords
        _rest_patch("municipalities", "municipality_id", mid, {"lat": lat, "lon": lon})
        updated += 1
        if updated % 100 == 0:
            logger.info("Updated %d/%d municipalities", updated, len(missing_ids))

    logger.info("Done. Updated: %d, Failed: %d, Total missing: %d", updated, failed, len(missing_ids))
    return 0


if __name__ == "__main__":
    sys.exit(main())
