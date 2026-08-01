"""Extract centroid coordinates and area from GeoJSON boundary files.

Reads the province-level and municipality-level GeoJSON files, computes
centroids and areas using shapely, matches features to DB admin units by
normalized name, and outputs CSVs for insertion into geospatial_metadata.

Also fetches existing province/municipality IDs from Supabase to build
the mapping between GeoJSON feature names and DB records.

Outputs:
    scripts/gap_output/geospatial_province_centroids.csv
    scripts/gap_output/geospatial_municipality_centroids.csv

Usage:
    .venv\\Scripts\\python.exe scripts/extract_centroids.py
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv
from shapely.geometry import shape
from shapely.ops import unary_union

REPO_ROOT = Path(__file__).resolve().parents[1]
GEOJSON_DIR = REPO_ROOT / "react-frontend" / "public"
OUTPUT_DIR = REPO_ROOT / "scripts" / "gap_output"

PROVINCE_GEOJSON = GEOJSON_DIR / "philippine_geojson_file_per_region.json"
MUNICIPALITY_GEOJSON = GEOJSON_DIR / "philippine_geojson_file_per_provinces.min.json"


# ---------------------------------------------------------------------------
# Name normalization — must match the norm() used in identify_gaps.py
# ---------------------------------------------------------------------------

_CITY_SUFFIXES = re.compile(r"\s+(City|City of)$", re.IGNORECASE)
_MUNI_SUFFIXES = re.compile(
    r"\s+(Municipality|Municipio|Town|Capital|Poblacion)$", re.IGNORECASE
)
_PARENTHETICAL = re.compile(r"\s*\([^)]*\)\s*", re.IGNORECASE)
_MULTI_SPACE = re.compile(r"\s+")


def norm(name: str) -> str:
    """Normalize a geographic name for matching."""
    s = name.strip().lower()
    s = _PARENTHETICAL.sub(" ", s)
    s = _CITY_SUFFIXES.sub("", s)
    s = _MUNI_SUFFIXES.sub("", s)
    s = s.replace("city of ", "").strip()
    s = _MULTI_SPACE.sub(" ", s)
    return s


# ---------------------------------------------------------------------------
# GeoJSON processing
# ---------------------------------------------------------------------------


def compute_centroid_and_area(feature: dict) -> tuple[float, float, float]:
    """Compute centroid (lat, lon) and area_km2 from a GeoJSON feature.

    Uses shapely to compute the geometric centroid. Area is computed
    using a simple equirectangular approximation centered on the polygon.
    """
    geom = shape(feature["geometry"])

    # Centroid — shapely gives (lon, lat) in EPSG:4326
    centroid = geom.centroid
    lon = centroid.x
    lat = centroid.y

    # Area approximation: equirectangular projection
    # R_earth = 6371 km
    # area = (lon_range * cos(lat_avg) * lat_range) * (pi/180)^2 * R^2
    # But shapely doesn't do geodesic. Use the property from GeoJSON if available.
    props = feature.get("properties", {})
    area_km2 = props.get("area_km2")
    if area_km2 is None:
        # Fallback: rough equirectangular approximation
        minx, miny, maxx, maxy = geom.bounds
        lat_rad = lat * 3.141592653589793 / 180.0
        lon_range_km = (maxx - minx) * 111.32 * cos(lat_rad)
        lat_range_km = (maxy - miny) * 110.574
        area_km2 = lon_range_km * lat_range_km

    return round(lat, 6), round(lon, 6), round(float(area_km2), 2)


def cos(x: float) -> float:
    import math

    return math.cos(x)


def process_geojson(
    filepath: Path, name_property: str
) -> list[dict]:
    """Process a GeoJSON file and return list of centroid records.

    Each record: {name, centroid_lat, centroid_lon, area_km2, psgc}
    """
    print(f"Loading {filepath.name}...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])
    print(f"  {len(features)} features found")

    records = []
    for feat in features:
        props = feat.get("properties", {})
        name = props.get(name_property, "")
        if not name:
            continue

        lat, lon, area = compute_centroid_and_area(feat)
        psgc = props.get(f"{name_property.split('_')[0]}_psgc")

        records.append(
            {
                "name": name,
                "normalized_name": norm(name),
                "centroid_lat": lat,
                "centroid_lon": lon,
                "area_km2": area,
                "psgc": psgc,
            }
        )

    return records


# ---------------------------------------------------------------------------
# Supabase ID lookup
# ---------------------------------------------------------------------------


class SupabaseRestClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
        }
        self.http = httpx.Client(timeout=60.0)

    def fetch_all(self, table: str, select: str, batch: int = 1000) -> list[dict]:
        """Fetch all rows from a table with pagination."""
        rows = []
        offset = 0
        while True:
            url = f"{self.base_url}/rest/v1/{table}"
            params = {"select": select, "limit": str(batch), "offset": str(offset)}
            resp = self.http.get(url, params=params, headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                break
            rows.extend(data)
            if len(data) < batch:
                break
            offset += batch
        return rows


def build_province_lookup(client: SupabaseRestClient) -> dict[str, dict]:
    """Build normalized name → province record mapping."""
    print("Fetching provinces from Supabase...")
    rows = client.fetch_all("provinces", "province_id,name,region_id,lat,lon")
    print(f"  {len(rows)} provinces found")
    lookup = {}
    for r in rows:
        key = norm(r["name"])
        lookup[key] = r
        # Also add the raw name lowercased as an alias
        lookup[r["name"].lower().strip()] = r
    return lookup


def build_municipality_lookup(client: SupabaseRestClient) -> dict[str, dict]:
    """Build normalized name → municipality record mapping."""
    print("Fetching municipalities from Supabase...")
    rows = client.fetch_all(
        "municipalities", "municipality_id,name,province_id,lat,lon"
    )
    print(f"  {len(rows)} municipalities found")
    lookup = {}
    for r in rows:
        key = norm(r["name"])
        # If duplicate normalized names exist, keep the first
        if key not in lookup:
            lookup[key] = r
        # Also add raw name
        raw_key = r["name"].lower().strip()
        if raw_key not in lookup:
            lookup[raw_key] = r
    return lookup


# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------


def write_csv(filepath: Path, rows: list[dict], fieldnames: list[str]) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Written {len(rows)} rows to {filepath.name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    load_dotenv(dotenv_path=REPO_ROOT / ".env", override=False)

    url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_KEY")
        or os.getenv("VITE_SUPABASE_ANON_KEY")
    )
    if not url or not key:
        print("ERROR: Missing Supabase credentials", file=sys.stderr)
        return 1

    client = SupabaseRestClient(url, key)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Province centroids ---
    print("\n=== Processing province GeoJSON ===")
    province_records = process_geojson(PROVINCE_GEOJSON, "adm2_en")
    province_lookup = build_province_lookup(client)

    province_matches = []
    province_unmatched = []
    for rec in province_records:
        match = province_lookup.get(rec["normalized_name"]) or province_lookup.get(
            rec["name"].lower().strip()
        )
        if match:
            province_matches.append(
                {
                    "province_id": match["province_id"],
                    "name": match["name"],
                    "centroid_lat": rec["centroid_lat"],
                    "centroid_lon": rec["centroid_lon"],
                    "area_km2": rec["area_km2"],
                    "source": "GeoJSON centroid",
                }
            )
        else:
            province_unmatched.append(rec)

    print(f"  Matched: {len(province_matches)}, Unmatched: {len(province_unmatched)}")
    if province_unmatched:
        print("  Unmatched provinces:")
        for u in province_unmatched[:10]:
            print(f"    {u['name']} (norm: {u['normalized_name']})")

    write_csv(
        OUTPUT_DIR / "geospatial_province_centroids.csv",
        province_matches,
        ["province_id", "name", "centroid_lat", "centroid_lon", "area_km2", "source"],
    )

    # --- Municipality centroids ---
    print("\n=== Processing municipality GeoJSON ===")
    muni_records = process_geojson(MUNICIPALITY_GEOJSON, "adm3_en")
    muni_lookup = build_municipality_lookup(client)

    muni_matches = []
    muni_unmatched = []
    for rec in muni_records:
        match = muni_lookup.get(rec["normalized_name"]) or muni_lookup.get(
            rec["name"].lower().strip()
        )
        if match:
            muni_matches.append(
                {
                    "municipality_id": match["municipality_id"],
                    "name": match["name"],
                    "province_id": match.get("province_id", ""),
                    "centroid_lat": rec["centroid_lat"],
                    "centroid_lon": rec["centroid_lon"],
                    "area_km2": rec["area_km2"],
                    "source": "GeoJSON centroid",
                }
            )
        else:
            muni_unmatched.append(rec)

    print(f"  Matched: {len(muni_matches)}, Unmatched: {len(muni_unmatched)}")
    if muni_unmatched:
        print(f"  (showing first 10 of {len(muni_unmatched)} unmatched)")
        for u in muni_unmatched[:10]:
            print(f"    {u['name']} (norm: {u['normalized_name']})")

    write_csv(
        OUTPUT_DIR / "geospatial_municipality_centroids.csv",
        muni_matches,
        [
            "municipality_id",
            "name",
            "province_id",
            "centroid_lat",
            "centroid_lon",
            "area_km2",
            "source",
        ],
    )

    # --- Summary ---
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"  Province centroids:  {len(province_matches)} matched")
    print(f"  Municipality centroids: {len(muni_matches)} matched")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"{'='*60}")
    print("\nNext step: Run insert_geospatial_metadata.py to insert into Supabase.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
