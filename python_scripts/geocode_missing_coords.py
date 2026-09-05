"""Geocode missing lat/lon for municipalities using Nominatim + direct Supabase REST API.

Usage (from repo root with .venv activated):
    python python_scripts/geocode_missing_coords.py
"""
from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path

import httpx
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

USER_AGENT = "lumi-geocoder/1.0 (alexanderjonsolis0401@gmail.com)"
RATE_LIMIT_SECONDS = 1.1  # Nominatim requires >= 1s between requests
PAGE_SIZE = 1000


def load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


load_env_file(Path(".env"))

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_JWT_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_JWT_ANON_KEY")
    or os.environ.get("SUPABASE_ANON_KEY")
    or os.environ.get("SUPABASE_KEY")
    or ""
)
NOMINATIM_EMAIL = os.environ.get("NOMINATIM_EMAIL", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise SystemExit("Missing SUPABASE_URL or SUPABASE_KEY.")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Prefer": "return=minimal",
}

# Nominatim session with retry
session = httpx.Client(timeout=20.0)
retry_strategy = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    raise_on_status=False,
)


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


def fetch_missing_ids(table: str, id_field: str) -> list[int]:
    missing: list[int] = []
    offset = 0
    while True:
        params = {
            "select": id_field,
            "or": "(lat.is.null,lon.is.null)",
            "offset": str(offset),
            "limit": str(PAGE_SIZE),
        }
        rows = _rest_get(table, params)
        if not rows:
            break
        for row in rows:
            missing.append(int(row[id_field]))
        if len(rows) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return missing


def geocode(query: str, cache: dict) -> tuple[float | None, float | None]:
    if query in cache:
        return cache[query]

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": USER_AGENT}
    if NOMINATIM_EMAIL:
        params["email"] = NOMINATIM_EMAIL
        headers["From"] = NOMINATIM_EMAIL

    for attempt in range(1, 4):
        try:
            resp = httpx.get(url, params=params, headers=headers, timeout=20.0)
        except Exception as exc:
            logger.warning("HTTP error for %r (attempt %d): %s", query, attempt, exc)
            time.sleep(5)
            continue

        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 60))
            logger.warning("Rate limited for %r. Waiting %ds...", query, wait)
            time.sleep(wait)
            continue

        if not resp.is_success:
            logger.warning("HTTP %s for %r: %s", resp.status_code, query, resp.text[:200])
            cache[query] = (None, None)
            return None, None

        data = resp.json()
        if not data:
            logger.warning("No results for: %r", query)
            cache[query] = (None, None)
            return None, None

        lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
        cache[query] = (lat, lon)
        return lat, lon

    logger.error("Exhausted retries for: %r", query)
    cache[query] = (None, None)
    return None, None


def update_coords(table: str, id_field: str, id_value: int, lat, lon) -> None:
    if lat is None or lon is None:
        return
    _rest_patch(table, id_field, id_value, {"lat": lat, "lon": lon})


def main() -> int:
    # Load CSVs
    csv_dir = Path("regionalData")
    regions = pd.read_csv(csv_dir / "regions.csv")
    provinces = pd.read_csv(csv_dir / "provinces.csv").rename(columns={"Name": "name"})
    municipalities = pd.read_csv(csv_dir / "municipalities.csv")

    region_by_id = regions.set_index("region_id")
    prov_by_id = provinces.set_index("province_id")
    mun_by_id = municipalities.set_index("municipality_id")

    cache: dict[str, tuple] = {}

    # --- Regions ---
    missing_region_ids = fetch_missing_ids("regions", "region_id")
    logger.info("Regions missing coords: %d", len(missing_region_ids))
    for _, row in regions.iterrows():
        if int(row["region_id"]) not in missing_region_ids:
            continue
        query = f"{row['name']}, Philippines"
        lat, lon = geocode(query, cache)
        if lat and lon:
            update_coords("regions", "region_id", int(row["region_id"]), lat, lon)
        time.sleep(RATE_LIMIT_SECONDS)

    # --- Provinces ---
    missing_province_ids = fetch_missing_ids("provinces", "province_id")
    logger.info("Provinces missing coords: %d", len(missing_province_ids))
    for _, row in provinces.iterrows():
        if int(row["province_id"]) not in missing_province_ids:
            continue
        region = region_by_id.loc[row["region_id"]]
        query = f"{row['name']}, {region['name']}, Philippines"
        lat, lon = geocode(query, cache)
        if lat and lon:
            update_coords("provinces", "province_id", int(row["province_id"]), lat, lon)
        time.sleep(RATE_LIMIT_SECONDS)

    # --- Municipalities ---
    missing_muni_ids = fetch_missing_ids("municipalities", "municipality_id")
    logger.info("Municipalities missing coords: %d", len(missing_muni_ids))
    total = len(missing_muni_ids)
    for idx, row in municipalities.iterrows():
        mid = int(row["municipality_id"])
        if mid not in missing_muni_ids:
            continue
        prov = prov_by_id.loc[row["province_id"]]
        query = f"{row['name']}, {prov['name']}, Philippines"
        lat, lon = geocode(query, cache)
        if lat and lon:
            update_coords("municipalities", "municipality_id", mid, lat, lon)
        if (idx + 1) % 50 == 0 or idx == total - 1:
            logger.info("Geocoded %d/%d municipalities", idx + 1, total)
        time.sleep(RATE_LIMIT_SECONDS)

    logger.info("Done updating coordinates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
