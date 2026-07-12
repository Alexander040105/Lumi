"""Insert geospatial metadata from CSVs into Supabase.

Reads centroid CSVs produced by extract_centroids.py and upserts them
into the geospatial_metadata table using the Supabase REST API.

Usage:
    .venv\\Scripts\\python.exe scripts/insert_geospatial_metadata.py
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
GAP_DIR = REPO_ROOT / "scripts" / "gap_output"


class SupabaseRestClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        }
        self.http = httpx.Client(timeout=60.0)

    def upsert_batch(self, table: str, rows: list[dict]) -> tuple[int, str]:
        if not rows:
            return 0, ""
        url = f"{self.base_url}/rest/v1/{table}"
        try:
            resp = self.http.post(url, json=rows, headers=self.headers)
            resp.raise_for_status()
            return len(rows), ""
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500] if exc.response else ""
            return 0, f"HTTP {exc.response.status_code}: {body}"
        except Exception as exc:
            return 0, str(exc)

    def fetch_existing_keys(self, table: str, select: str) -> set[str]:
        """Fetch existing geo keys to skip duplicates."""
        rows = []
        offset = 0
        batch = 1000
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
        keys = set()
        for r in rows:
            for col in ["region_id", "province_id", "municipality_id", "barangay_id"]:
                val = r.get(col)
                if val is not None:
                    keys.add(f"{col}:{val}")
        return keys


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


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
    batch_size = 500
    total_inserted = 0

    # Check existing entries to avoid duplicates
    print("Fetching existing geospatial_metadata keys...")
    try:
        existing_keys = client.fetch_existing_keys(
            "geospatial_metadata",
            "region_id,province_id,municipality_id,barangay_id",
        )
        print(f"  {len(existing_keys)} existing entries")
    except Exception as exc:
        print(f"  Warning: could not fetch existing keys ({exc}), will attempt all")
        existing_keys = set()

    # --- Province centroids ---
    print("\n--- Province centroids ---")
    provinces = read_csv(GAP_DIR / "geospatial_province_centroids.csv")
    print(f"  {len(provinces)} rows in CSV")

    rows = []
    skipped = 0
    for p in provinces:
        pid = int(p["province_id"])
        geo_key = f"province_id:{pid}"
        if geo_key in existing_keys:
            skipped += 1
            continue
        rows.append(
            {
                "province_id": pid,
                "centroid_lat": float(p["centroid_lat"]),
                "centroid_lon": float(p["centroid_lon"]),
                "area_km2": float(p["area_km2"]) if p.get("area_km2") else None,
                "source": p.get("source", "GeoJSON centroid"),
            }
        )

    print(f"  Skipped (already exist): {skipped}")
    print(f"  To insert: {len(rows)}")

    inserted = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        count, err = client.upsert_batch("geospatial_metadata", batch)
        inserted += count
        if err:
            print(f"  Batch {i // batch_size + 1} error: {err}")
        else:
            print(f"  Batch {i // batch_size + 1}: {count} inserted")
    total_inserted += inserted
    print(f"  Province centroids inserted: {inserted}")

    # --- Municipality centroids ---
    print("\n--- Municipality centroids ---")
    munis = read_csv(GAP_DIR / "geospatial_municipality_centroids.csv")
    print(f"  {len(munis)} rows in CSV")

    rows = []
    skipped = 0
    for m in munis:
        mid = int(m["municipality_id"])
        geo_key = f"municipality_id:{mid}"
        if geo_key in existing_keys:
            skipped += 1
            continue
        rows.append(
            {
                "municipality_id": mid,
                "centroid_lat": float(m["centroid_lat"]),
                "centroid_lon": float(m["centroid_lon"]),
                "area_km2": float(m["area_km2"]) if m.get("area_km2") else None,
                "source": m.get("source", "GeoJSON centroid"),
            }
        )

    print(f"  Skipped (already exist): {skipped}")
    print(f"  To insert: {len(rows)}")

    inserted = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        count, err = client.upsert_batch("geospatial_metadata", batch)
        inserted += count
        if err:
            print(f"  Batch {i // batch_size + 1} error: {err}")
        else:
            print(f"  Batch {i // batch_size + 1}: {count} inserted")
    total_inserted += inserted
    print(f"  Municipality centroids inserted: {inserted}")

    print(f"\n{'='*60}")
    print(f"TOTAL INSERTED: {total_inserted}")
    print(f"{'='*60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
