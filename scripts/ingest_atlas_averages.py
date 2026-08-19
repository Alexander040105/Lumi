"""Upsert municipality atlas averages from the extracted CSV into Supabase.

Usage (from repo root, with .venv activated):
    .venv\\Scripts\\python.exe scripts/ingest_atlas_averages.py
"""
from __future__ import annotations

import csv
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from supabase import Client, create_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

CSV_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "gap_output"
    / "municipality_atlas_averages.csv"
)
BATCH_SIZE = 500

ATLAS_FLOAT_FIELDS = [
    "centroid_lat",
    "centroid_lon",
    "solar_ghi_kwh_m2_day",
    "solar_dni_kwh_m2_day",
    "solar_dif_kwh_m2_day",
    "solar_gti_kwh_m2_day",
    "solar_pvout_annual_kwh_kwp",
    "solar_pvout_daily_kwh_kwp",
    "solar_temp_c",
    "solar_optimal_tilt_deg",
    "wind_speed_10m_ms",
    "wind_speed_50m_ms",
    "wind_speed_100m_ms",
]

INTEGER_FIELDS = ["municipality_id", "province_id"]


def _clean_row(row: dict[str, str]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {"data_source": "Global Solar Atlas / Global Wind Atlas"}
    for key, value in row.items():
        if key == "data_source":
            cleaned[key] = value
        elif key in INTEGER_FIELDS:
            cleaned[key] = int(value) if value else None
        elif key in ATLAS_FLOAT_FIELDS:
            cleaned[key] = float(value) if value else None
        else:
            cleaned[key] = value
    return cleaned


def _fetch_valid_municipality_ids(client: Client) -> set[int]:
    valid_ids: set[int] = set()
    page_size = 1000
    offset = 0
    while True:
        resp = (
            client.table("municipalities")
            .select("municipality_id")
            .limit(page_size)
            .offset(offset)
            .execute()
        )
        data = resp.data or []
        if not data:
            break
        valid_ids.update(r["municipality_id"] for r in data)
        offset += page_size
    return valid_ids


def main() -> None:
    load_dotenv()

    url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
    key = (
        os.getenv("SUPABASE_JWT_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_SERVICE_KEY")
        or os.getenv("SUPABASE_KEY")
    )
    if not url or not key:
        raise RuntimeError("Set SUPABASE_URL and a Supabase service role key.")

    client = create_client(url, key)

    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        rows = [_clean_row(r) for r in csv.DictReader(f)]
    logger.info("Loaded %d rows from %s", len(rows), CSV_PATH)

    valid_ids = _fetch_valid_municipality_ids(client)
    valid_rows = [r for r in rows if r["municipality_id"] in valid_ids]
    skipped = len(rows) - len(valid_rows)
    logger.info("Matched %d rows to municipalities; %d skipped (FK mismatch)", len(valid_rows), skipped)

    for i in range(0, len(valid_rows), BATCH_SIZE):
        batch = valid_rows[i : i + BATCH_SIZE]
        try:
            client.table("municipality_atlas_averages").upsert(batch).execute()
            logger.info("Upserted rows %d-%d", i, i + len(batch) - 1)
        except Exception as exc:
            logger.error("Failed to upsert rows %d-%d: %s", i, i + len(batch) - 1, exc)
            raise

    logger.info("Done. Total upserted: %d", len(valid_rows))


if __name__ == "__main__":
    main()
