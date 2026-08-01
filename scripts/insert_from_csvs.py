"""Insert missing geographic entries from CSVs into Supabase.

Reads CSVs from scripts/gap_output/ and inserts in FK order:
    1. missing_regions.csv
    2. missing_provinces.csv
    3. missing_municipalities.csv
    4. missing_barangays.csv

Usage:
    py scripts/insert_from_csvs.py
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

    def insert_batch(self, table: str, rows: list[dict]) -> tuple[int, str]:
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

    # --- 1. Regions ---
    print("Reading missing_regions.csv...")
    regions = read_csv(GAP_DIR / "missing_regions.csv")
    print(f"  {len(regions)} regions to insert")
    inserted = 0
    for i in range(0, len(regions), batch_size):
        batch = regions[i : i + batch_size]
        # Convert types
        rows = [{"region_id": int(r["region_id"]), "name": r["name"]} for r in batch]
        count, err = client.insert_batch("regions", rows)
        inserted += count
        if err:
            print(f"  Batch {i // batch_size + 1} error: {err}")
        else:
            print(f"  Batch {i // batch_size + 1}: {count} inserted")
    total_inserted += inserted
    print(f"  Regions inserted: {inserted}")

    # --- 2. Provinces ---
    print("\nReading missing_provinces.csv...")
    provinces = read_csv(GAP_DIR / "missing_provinces.csv")
    print(f"  {len(provinces)} provinces to insert")
    inserted = 0
    for i in range(0, len(provinces), batch_size):
        batch = provinces[i : i + batch_size]
        rows = [
            {"province_id": int(p["province_id"]), "region_id": int(p["region_id"]), "name": p["name"]}
            for p in batch
        ]
        count, err = client.insert_batch("provinces", rows)
        inserted += count
        if err:
            print(f"  Batch {i // batch_size + 1} error: {err}")
        else:
            print(f"  Batch {i // batch_size + 1}: {count} inserted")
    total_inserted += inserted
    print(f"  Provinces inserted: {inserted}")

    # --- 3. Municipalities ---
    print("\nReading missing_municipalities.csv...")
    munis = read_csv(GAP_DIR / "missing_municipalities.csv")
    print(f"  {len(munis)} municipalities to insert")
    inserted = 0
    for i in range(0, len(munis), batch_size):
        batch = munis[i : i + batch_size]
        rows = [
            {
                "municipality_id": int(m["municipality_id"]),
                "province_id": int(m["province_id"]),
                "name": m["name"],
            }
            for m in batch
        ]
        count, err = client.insert_batch("municipalities", rows)
        inserted += count
        if err:
            print(f"  Batch {i // batch_size + 1} error: {err}")
        else:
            print(f"  Batch {i // batch_size + 1}: {count} inserted")
    total_inserted += inserted
    print(f"  Municipalities inserted: {inserted}")

    # --- 4. Barangays ---
    print("\nReading missing_barangays.csv...")
    barangays = read_csv(GAP_DIR / "missing_barangays.csv")
    print(f"  {len(barangays)} barangays to insert")
    inserted = 0
    # Smaller batches for barangays due to volume
    brgy_batch = 200
    for i in range(0, len(barangays), brgy_batch):
        batch = barangays[i : i + brgy_batch]
        rows = [
            {
                "barangay_id": int(b["barangay_id"]),
                "municipality_id": int(b["municipality_id"]),
                "name": b["name"],
            }
            for b in batch
        ]
        count, err = client.insert_batch("barangays", rows)
        inserted += count
        if err:
            print(f"  Batch {i // brgy_batch + 1} error: {err}")
        else:
            print(f"  Batch {i // brgy_batch + 1}: {count} inserted")
    total_inserted += inserted
    print(f"  Barangays inserted: {inserted}")

    print(f"\n{'='*60}")
    print(f"TOTAL INSERTED: {total_inserted}")
    print(f"{'='*60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
