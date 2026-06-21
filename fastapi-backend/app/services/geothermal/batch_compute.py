"""Batch pre-computation script for geothermal suitability and output.

Usage (run once from project root with .venv activated):
    python -m app.services.geothermal.batch_compute

This script:
1. Loads all municipalities from Supabase.
2. For each municipality, computes geothermal suitability and output.
3. Upserts rows into geothermal_suitability and geothermal_output tables.

Requires:
    - KMZ extraction already done (run extract_kmz.py first)
    - Supabase credentials in environment
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from app.services.geothermal.features import (
    load_geothermal_datasets,
    compute_geothermal_suitability,
    compute_geothermal_output,
)
from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def fetch_municipalities() -> list[dict]:
    client = get_supabase_client()
    all_rows: list[dict] = []
    offset = 0
    while True:
        resp = (
            client.table("municipalities")
            .select("municipality_id,name,lat,lon")
            .limit(1000)
            .offset(offset)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < 1000:
            break
        offset += 1000
    return all_rows


def fetch_all_climate() -> dict[int, float]:
    """Fetch climate temperatures (2010 annual data) and map by municipality_id."""
    client = get_supabase_client()
    mapping: dict[int, float] = {}
    offset = 0
    while True:
        resp = (
            client.table("municipality_climate_monthly")
            .select("municipality_id,t2m")
            .eq("year", 2010)
            .limit(1000)
            .offset(offset)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            break
        for row in rows:
            mid = row.get("municipality_id")
            if mid is not None:
                mapping[mid] = float(row.get("t2m", 0))
        if len(rows) < 1000:
            break
        offset += 1000
    return mapping


def batch_upsert(table: str, rows: list[dict], chunk_size: int = 100) -> None:
    """Upsert rows in batches to minimize API round-trips."""
    client = get_supabase_client()
    total = len(rows)
    for i in range(0, total, chunk_size):
        chunk = rows[i : i + chunk_size]
        try:
            client.table(table).upsert(chunk).execute()
        except Exception as exc:
            logger.warning("Batch upsert to %s failed for chunk %d-%d: %s", table, i, i + len(chunk), exc)
        if (i + chunk_size) % 500 == 0 or (i + chunk_size) >= total:
            logger.info("Upserted %d/%d rows to %s", min(i + chunk_size, total), total, table)


def main() -> None:
    logger.info("Loading geothermal datasets...")
    datasets = load_geothermal_datasets()
    logger.info("Datasets loaded.")

    municipalities = fetch_municipalities()
    total = len(municipalities)
    logger.info("Found %d municipalities to process.", total)

    logger.info("Fetching all climate data in one query...")
    climate_map = fetch_all_climate()
    logger.info("Loaded climate for %d municipalities.", len(climate_map))

    suit_rows: list[dict] = []
    output_rows: list[dict] = []

    for idx, muni in enumerate(municipalities, start=1):
        mid = muni.get("municipality_id")
        name = muni.get("name", "")
        lat = muni.get("lat")
        lon = muni.get("lon")

        if lat is None or lon is None:
            logger.warning("Skipping %s (%s) — missing coordinates", name, mid)
            continue

        surface_temp = climate_map.get(mid)

        suit = compute_geothermal_suitability(lat, lon, surface_temp, datasets)
        output = compute_geothermal_output(
            surface_temp,
            suit.get("_gradient_c_km"),
            suit.get("aquifer_score"),
            suit.get("_perm_log10"),
        )

        suit_rows.append({
            "municipality_id": mid,
            "heat_flow_score": suit.get("heat_flow_score"),
            "fault_density": suit.get("fault_density"),
            "fault_distance_km": suit.get("fault_distance_km"),
            "volcano_distance_km": suit.get("volcano_distance_km"),
            "aquifer_score": suit.get("aquifer_score"),
            "temperature_score": suit.get("temperature_score"),
            "geothermal_score": suit.get("geothermal_score"),
            "geothermal_score_mcda": suit.get("geothermal_score"),
            "classification": suit.get("classification"),
        })

        output_rows.append({
            "municipality_id": mid,
            "reservoir_temperature_c": output.get("reservoir_temperature_c"),
            "estimated_flow_rate_kg_s": output.get("estimated_flow_rate_kg_s"),
            "thermal_power_mw": output.get("thermal_power_mw"),
            "electric_power_mw": output.get("electric_power_mw"),
            "annual_energy_gwh": output.get("annual_energy_gwh"),
            "confidence_score": output.get("confidence_score"),
            "source": output.get("source"),
            "assumption": output.get("assumption"),
        })

        if idx % 100 == 0 or idx == total:
            logger.info("Computed %d/%d municipalities", idx, total)

    logger.info("Batch upserting %d suitability rows...", len(suit_rows))
    batch_upsert("geothermal_suitability", suit_rows, chunk_size=100)

    logger.info("Batch upserting %d output rows...", len(output_rows))
    batch_upsert("geothermal_output", output_rows, chunk_size=100)

    logger.info("Batch pre-computation complete.")


if __name__ == "__main__":
    main()
