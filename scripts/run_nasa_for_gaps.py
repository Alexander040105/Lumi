"""
Fetch NASA POWER climate data for municipalities that lack it.
Loads gap municipalities from gap_output/ CSVs, fetches climate data,
and inserts into municipality_climate_monthly.
"""
from __future__ import annotations

import csv
import json
import logging
import os
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "scripts" / "gap_output"
NASA_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"
PARAMETERS = [
    "T2M", "T2M_MAX", "T2M_MIN", "RH2M", "RHOA",
    "PRECTOTCORR", "WS10M", "ALLSKY_SFC_SW_DWN", "CLOUD_AMT", "PS",
]
MISSING_VALUES = {-999, -999.0, -9999, -9999.0}


class SupabaseRestClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.http = httpx.Client(timeout=30.0)

    def table(self, table_name: str):
        return SupabaseRestQuery(self, table_name)


class SupabaseRestQuery:
    def __init__(self, client: SupabaseRestClient, table: str):
        self._client = client
        self._table = table
        self._select_cols = "*"
        self._filters: list[tuple[str, str, str]] = []
        self._order: str | None = None
        self._range: tuple[int, int] | None = None

    def select(self, columns: str = "*") -> "SupabaseRestQuery":
        self._select_cols = columns
        return self

    def eq(self, column: str, value: str | int) -> "SupabaseRestQuery":
        self._filters.append((column, "eq", str(value)))
        return self

    def in_(self, column: str, values: list) -> "SupabaseRestQuery":
        self._filters.append((column, "in", f"({','.join(str(v) for v in values)})"))
        return self

    def not_(self) -> "SupabaseRestQuery":
        self._negate_next = True
        return self

    def is_(self, column: str, value: str) -> "SupabaseRestQuery":
        op = "is"
        if getattr(self, "_negate_next", False):
            op = "not.is"
            self._negate_next = False
        self._filters.append((column, op, str(value)))
        return self

    def not_is(self, column: str, value: str) -> "SupabaseRestQuery":
        self._filters.append((column, "not.is", str(value)))
        return self

    def order(self, column: str, desc: bool = False) -> "SupabaseRestQuery":
        self._order = f"{column}.{'desc' if desc else 'asc'}"
        return self

    def range(self, start: int, end: int) -> "SupabaseRestQuery":
        self._range = (start, end)
        return self

    def insert(self, rows: list[dict]) -> "SupabaseRestQuery":
        self._rows = rows
        return self

    def execute(self):
        if hasattr(self, "_rows"):
            url = f"{self._client.base_url}/rest/v1/{self._table}"
            response = self._client.http.post(url, json=self._rows, headers=self._client.headers)
            response.raise_for_status()
            return type("Response", (), {"data": response.json() if response.text else []})()

        params: dict[str, str] = {"select": self._select_cols}
        for column, op, value in self._filters:
            params[column] = f"{op}.{value}"
        if self._order:
            params["order"] = self._order
        url = f"{self._client.base_url}/rest/v1/{self._table}"
        headers = dict(self._client.headers)
        if self._range:
            headers["Range"] = f"{self._range[0]}-{self._range[1]}"
        response = self._client.http.get(url, params=params, headers=headers)
        response.raise_for_status()
        return type("Response", (), {"data": response.json()})()


def load_gap_municipality_ids() -> set[int]:
    ids: set[int] = set()
    # From null_scores.csv
    null_path = OUTPUT_DIR / "null_scores.csv"
    if null_path.exists():
        with open(null_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                mid = row.get("municipality_id")
                if mid:
                    ids.add(int(mid))
    # From missing_from_db.csv (use geo_psgc as ID since we just inserted them)
    missing_path = OUTPUT_DIR / "missing_from_db.csv"
    if missing_path.exists():
        with open(missing_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                mid = row.get("geo_psgc")
                if mid:
                    ids.add(int(mid))
    return ids


def fetch_db_gap_municipalities(client: SupabaseRestClient) -> list[dict]:
    """Find all municipalities that have coordinates but no climate data.

    Queries the DB for municipalities with lat/lon that don't have
    any rows in municipality_climate_monthly. This catches newly inserted
    municipalities from the PSGC sync.
    """
    # 1. Fetch all municipalities with lat/lon
    all_munis: list[dict] = []
    start = 0
    batch = 1000
    while True:
        resp = (
            client.table("municipalities")
            .select("municipality_id,name,lat,lon")
            .not_is("lat", "null")
            .range(start, start + batch - 1)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            break
        all_munis.extend(rows)
        if len(rows) < batch:
            break
        start += batch

    # 2. Fetch all municipality_ids that already have climate data
    climate_ids: set[int] = set()
    start = 0
    while True:
        resp = (
            client.table("municipality_climate_monthly")
            .select("municipality_id")
            .range(start, start + batch - 1)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            break
        for r in rows:
            mid = r.get("municipality_id")
            if mid is not None:
                climate_ids.add(int(mid))
        if len(rows) < batch:
            break
        start += batch

    # 3. Return municipalities without climate data
    gaps = []
    for m in all_munis:
        if m["municipality_id"] not in climate_ids:
            gaps.append({
                "municipality_id": m["municipality_id"],
                "name": m.get("name", ""),
                "lat": float(m["lat"]),
                "lon": float(m["lon"]),
            })
    return gaps


def fetch_gap_municipalities(client: SupabaseRestClient, ids: set[int]) -> list[dict]:
    all_rows = []
    id_list = sorted(ids)
    batch = 100
    for i in range(0, len(id_list), batch):
        chunk = id_list[i : i + batch]
        resp = (
            client.table("municipalities")
            .select("municipality_id,name,lat,lon")
            .in_("municipality_id", chunk)
            .execute()
        )
        rows = resp.data or []
        for r in rows:
            if r.get("lat") is not None and r.get("lon") is not None:
                all_rows.append({
                    "municipality_id": r["municipality_id"],
                    "name": r.get("name", ""),
                    "lat": float(r["lat"]),
                    "lon": float(r["lon"]),
                })
    return all_rows


def fetch_nasa_data(lat: float, lon: float) -> dict | None:
    params = {
        "parameters": ",".join(PARAMETERS),
        "community": "RE",
        "format": "JSON",
        "latitude": f"{lat:.6f}",
        "longitude": f"{lon:.6f}",
        "start": "2010",
        "end": "2023",
    }
    try:
        resp = httpx.get(NASA_URL, params=params, timeout=30.0)
        if resp.status_code == 200:
            return resp.json()
        logging.warning("NASA HTTP %s for lat=%s lon=%s", resp.status_code, lat, lon)
    except Exception as exc:
        logging.warning("NASA request failed: %s", exc)
    return None


def coerce_value(value) -> float | None:
    if value in MISSING_VALUES or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_climate_rows(municipality_id: int, payload: dict) -> list[dict]:
    parameter_map = payload.get("properties", {}).get("parameter", {})
    rows = []
    for year in range(2010, 2024):
        for month in range(1, 13):
            key = f"{year}{month:02d}"
            row = {
                "municipality_id": municipality_id,
                "year": year,
                "month": month,
                "t2m": coerce_value(parameter_map.get("T2M", {}).get(key)),
                "t2m_max": coerce_value(parameter_map.get("T2M_MAX", {}).get(key)),
                "t2m_min": coerce_value(parameter_map.get("T2M_MIN", {}).get(key)),
                "rh2m": coerce_value(parameter_map.get("RH2M", {}).get(key)),
                "prectotcorr": coerce_value(parameter_map.get("PRECTOTCORR", {}).get(key)),
                "ws10m": coerce_value(parameter_map.get("WS10M", {}).get(key)),
                "allsky_sfc_sw_dwn": coerce_value(parameter_map.get("ALLSKY_SFC_SW_DWN", {}).get(key)),
                "cloud_amt": coerce_value(parameter_map.get("CLOUD_AMT", {}).get(key)),
            }
            rows.append(row)
    return rows


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Fetch NASA POWER climate data for gap municipalities")
    parser.add_argument("--db-only", action="store_true", help="Query DB for gaps instead of using CSV files")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
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

    if args.db_only:
        print("Querying DB for municipalities without climate data...")
        munis = fetch_db_gap_municipalities(client)
    else:
        gap_ids = load_gap_municipality_ids()
        print(f"Gap municipalities from CSVs: {len(gap_ids)}")
        munis = fetch_gap_municipalities(client, gap_ids)

    print(f"Municipalities to process (with coordinates): {len(munis)}")

    if not munis:
        print("No gap municipalities found. All municipalities have climate data.")
        return 0

    processed = 0
    failed = 0
    for i, m in enumerate(munis, 1):
        mid = m["municipality_id"]
        payload = fetch_nasa_data(m["lat"], m["lon"])
        if not payload:
            failed += 1
            continue

        rows = build_climate_rows(mid, payload)
        if rows:
            try:
                client.table("municipality_climate_monthly").insert(rows).execute()
                processed += 1
                if i % 50 == 0:
                    print(f"  Progress: {i}/{len(munis)} (processed={processed}, failed={failed})")
            except Exception as exc:
                logging.warning("Insert failed for municipality %s: %s", mid, exc)
                failed += 1
        time.sleep(0.6)  # NASA rate limit

    print(f"\nDone. Processed: {processed}, Failed: {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
