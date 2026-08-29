"""Upload municipality catchment enrichment CSV to Supabase.

Run this after applying 0022_catchment_enrichment.sql to populate
the municipality_catchment_enrichment table from the bundled CSV.

Usage:
  python fastapi-backend/app/services/load_catchment_to_supabase.py
"""
from __future__ import annotations

import logging
import time
from pathlib import Path

import pandas as pd

from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

CSV_PATH = (
    Path(__file__).resolve().parent
    / "local_data"
    / "municipality_catchment_enrichment.csv"
)

BATCH_SIZE = 200


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Enrichment CSV not found at {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    logger.info("Loaded %d rows from %s", len(df), CSV_PATH)

    # Convert NaN to None for Supabase
    df = df.where(pd.notna(df), None)

    # Convert to list of dicts
    rows = df.to_dict(orient="records")

    # Cast integer columns
    for row in rows:
        row["municipality_id"] = int(row["municipality_id"])
        row["province_id"] = int(row["province_id"])
        if row.get("nearest_stream_order") is not None:
            row["nearest_stream_order"] = int(row["nearest_stream_order"])

    client = get_supabase_client()

    # Check if data already exists
    existing = client.table("municipality_catchment_enrichment").select(
        "municipality_id"
    ).limit(1).execute()
    if existing.data:
        logger.info("Table already has data. Truncating ...")
        # Delete all rows (admin policy required)
        client.table("municipality_catchment_enrichment").delete().neq(
            "municipality_id", -1
        ).execute()

    # Insert in batches
    total_inserted = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        resp = client.table("municipality_catchment_enrichment").insert(batch).execute()
        inserted = len(resp.data) if resp.data else 0
        total_inserted += inserted
        logger.info(
            "  Batch %d/%d: inserted %d rows (total: %d)",
            i // BATCH_SIZE + 1,
            (len(rows) + BATCH_SIZE - 1) // BATCH_SIZE,
            inserted,
            total_inserted,
        )
        time.sleep(0.2)  # avoid rate limiting

    logger.info("=" * 60)
    logger.info("UPLOAD COMPLETE: %d rows inserted", total_inserted)
    logger.info("=" * 60)

    # Verify
    verify = (
        client.table("municipality_catchment_enrichment")
        .select("municipality_id", count="exact")
        .execute()
    )
    count = verify.count if hasattr(verify, "count") else len(verify.data or [])
    logger.info("Verification: %d rows in table", count)


if __name__ == "__main__":
    main()
