"""Upsert province atlas averages from the computed CSV into Supabase.

Usage (from repo root, with .venv activated):
    .venv\\Scripts\\python.exe scripts/ingest_province_atlas_averages.py

Run this after creating the province_atlas_averages table via
supabase_tables_scripts/province_atlas_schema.sql.
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
    / "province_atlas_averages.csv"
)
BATCH_SIZE = 500


def _clean_row(row: dict[str, str]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in row.items():
        if value == "":
            cleaned[key] = None
        elif key == "province_id" or key == "muni_count":
            cleaned[key] = int(value)
        elif key == "province_name" or key == "data_source" or key == "reconciliation_note":
            cleaned[key] = value
        else:
            try:
                cleaned[key] = float(value) if value is not None else None
            except ValueError:
                cleaned[key] = value
    return cleaned


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

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        try:
            client.table("province_atlas_averages").upsert(batch).execute()
            logger.info("Upserted province rows %d-%d", i, i + len(batch) - 1)
        except Exception as exc:
            logger.error("Failed to upsert province rows %d-%d: %s", i, i + len(batch) - 1, exc)
            raise

    logger.info("Done. Total upserted: %d", len(rows))


if __name__ == "__main__":
    main()
