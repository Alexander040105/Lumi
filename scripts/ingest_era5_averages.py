"""Upsert ERA5 10m wind averages from CSV into Supabase.

Usage (from repo root, with .venv activated):
    .venv\\Scripts\\python.exe scripts/ingest_era5_averages.py

Run this after creating the tables with
supabase/table_scripts/municipality_era5_schema.sql and
supabase/table_scripts/province_era5_schema.sql.
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

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "gap_output"
BATCH_SIZE = 500


def _clean_row(row: dict[str, str]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in row.items():
        if value == "":
            cleaned[key] = None
        elif key == "municipality_id" or key == "province_id":
            cleaned[key] = int(value)
        elif key == "province_name" or key == "data_source":
            cleaned[key] = value
        else:
            try:
                cleaned[key] = float(value) if value is not None else None
            except ValueError:
                cleaned[key] = value
    return cleaned


def _ingest_table(client: Client, table: str, csv_name: str) -> None:
    path = OUTPUT_DIR / csv_name
    with path.open(newline="", encoding="utf-8") as f:
        rows = [_clean_row(r) for r in csv.DictReader(f)]
    logger.info("Loaded %d rows from %s", len(rows), path)

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        try:
            client.table(table).upsert(batch).execute()
            logger.info("Upserted %s rows %d-%d", table, i, i + len(batch) - 1)
        except Exception as exc:
            logger.error("Failed to upsert %s rows %d-%d: %s", table, i, i + len(batch) - 1, exc)
            raise

    logger.info("Done. Total upserted into %s: %d", table, len(rows))


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
    _ingest_table(client, "municipality_era5_averages", "municipality_era5_averages.csv")
    _ingest_table(client, "province_era5_averages", "province_era5_averages.csv")
    logger.info("ERA5 ingestion complete")


if __name__ == "__main__":
    main()
