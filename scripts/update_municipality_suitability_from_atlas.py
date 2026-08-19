"""Update municipality solar/wind suitability scores from the atlas CSV.

This is a one-off migration script for the live map. It does not require the
municipality_atlas_averages table; it uses the extracted CSV directly.

Usage (from repo root, with .venv activated):
    .venv\\Scripts\\python.exe scripts/update_municipality_suitability_from_atlas.py
"""
from __future__ import annotations

import csv
import json
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
CENTROID_CSV = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "gap_output"
    / "geospatial_municipality_centroids.csv"
)
BATCH_SIZE = 500


def _solar_score(pvout_annual: float | None) -> float:
    if not pvout_annual:
        return 0.0
    # 1800 kWh/kWp/year is an excellent PH site.
    return round(min(float(pvout_annual) / 1800.0 * 100.0, 100.0), 2)


def _wind_score(wind_100m: float | None) -> float:
    if not wind_100m:
        return 0.0
    # ~10 m/s at 100 m is a strong PH wind site.
    return round(min(float(wind_100m) / 10.0 * 100.0, 100.0), 2)


def load_centroids() -> dict[int, dict[str, str]]:
    with open(CENTROID_CSV, newline="", encoding="utf-8") as f:
        return {
            int(row["municipality_id"]): row
            for row in csv.DictReader(f)
            if row.get("municipality_id")
        }


def build_upsert_rows() -> list[dict[str, Any]]:
    centroids = load_centroids()
    rows: list[dict[str, Any]] = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            muni_id = int(r["municipality_id"])
            if muni_id not in centroids:
                continue
            meta = centroids[muni_id]
            pvout = float(r["solar_pvout_annual_kwh_kwp"]) if r.get("solar_pvout_annual_kwh_kwp") else None
            wind_100m = float(r["wind_speed_100m_ms"]) if r.get("wind_speed_100m_ms") else None
            ghi = float(r["solar_ghi_kwh_m2_day"]) if r.get("solar_ghi_kwh_m2_day") else None

            solar_score = _solar_score(pvout)
            wind_score = _wind_score(wind_100m)

            rows.append(
                {
                    "municipality_id": muni_id,
                    "name": meta.get("name", "").upper(),
                    "province_id": int(meta["province_id"]) if meta.get("province_id") else None,
                    "solar_suitability_score": solar_score,
                    "wind_suitability_score": wind_score,
                    "solar_factors": json.dumps(
                        {
                            "source": "Global Solar Atlas",
                            "solar_pvout_annual_kwh_kwp": pvout,
                            "solar_ghi_kwh_m2_day": ghi,
                            "score": solar_score,
                        }
                    ),
                    "wind_factors": json.dumps(
                        {
                            "source": "Global Wind Atlas",
                            "wind_speed_100m_ms": wind_100m,
                            "score": wind_score,
                        }
                    ),
                }
            )
    return rows


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
    rows = build_upsert_rows()
    logger.info("Prepared %d municipality score rows", len(rows))

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        try:
            client.table("municipalities").upsert(batch).execute()
            logger.info("Upserted scores %d-%d", i, i + len(batch) - 1)
        except Exception as exc:
            logger.error("Failed to upsert scores %d-%d: %s", i, i + len(batch) - 1, exc)
            raise

    logger.info("Done. Updated %d municipalities", len(rows))


if __name__ == "__main__":
    main()
