"""Catchment enrichment data loader for EcoSim hydro calculations.

Loads per-municipality catchment morphology and nearest-stream data from
the Boothroyd et al. (2023) national-scale geodatabase. Tries Supabase
first, then falls back to the bundled local CSV so EcoSim can use
enrichment data even when the `municipality_catchment_enrichment` table
has not yet been created in the target database.

Data source (CC-BY 4.0):
  Boothroyd, R.J., Williams, R.D., Hoey, T.B., et al. (2023).
  National-scale geodatabase of catchment characteristics in the
  Philippines for river management applications.
  PLOS ONE, 18(3), e0281933.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC9994713/
"""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)

LOCAL_ENRICHMENT_CSV = (
    Path(__file__).resolve().parent / "local_data" / "municipality_catchment_enrichment.csv"
)


@lru_cache(maxsize=1)
def _load_csv() -> pd.DataFrame:
    if not LOCAL_ENRICHMENT_CSV.exists():
        raise FileNotFoundError(f"Catchment enrichment CSV not found at {LOCAL_ENRICHMENT_CSV}")
    df = pd.read_csv(LOCAL_ENRICHMENT_CSV)
    df["municipality_id"] = df["municipality_id"].astype(int)
    df.set_index("municipality_id", inplace=True)
    return df


def _df_row_to_dict(row: pd.Series) -> dict[str, Any]:
    return {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}


def get_catchment_for_municipality(municipality_id: int) -> dict[str, Any] | None:
    """Return catchment enrichment data for a single municipality, or None.

    Tries Supabase first (production), then falls back to the bundled CSV
    (local dev / no DB).
    """
    # Supabase fast path (production)
    try:
        client = get_supabase_client()
        resp = (
            client.table("municipality_catchment_enrichment")
            .select("*")
            .eq("municipality_id", municipality_id)
            .maybe_single()
            .execute()
        )
        if resp.data:
            return resp.data
    except Exception as exc:
        logger.debug("Could not fetch catchment enrichment from Supabase: %s", exc)

    # CSV fallback
    try:
        df = _load_csv()
    except FileNotFoundError:
        logger.warning("Catchment enrichment CSV not found; enrichment disabled")
        return None

    if municipality_id in df.index:
        return _df_row_to_dict(df.loc[municipality_id])
    return None


def get_catchment_for_municipality_ids(
    municipality_ids: list[int],
) -> dict[int, dict[str, Any]]:
    """Bulk lookup for multiple municipalities. Returns {id: data_dict}."""
    if not municipality_ids:
        return {}

    result: dict[int, dict[str, Any]] = {}

    # Supabase fast path
    try:
        client = get_supabase_client()
        resp = (
            client.table("municipality_catchment_enrichment")
            .select("*")
            .in_("municipality_id", municipality_ids)
            .execute()
        )
        if resp.data:
            for row in resp.data:
                mid = row.get("municipality_id")
                if mid is not None:
                    result[int(mid)] = row
            if len(result) == len(municipality_ids):
                return result
    except Exception as exc:
        logger.debug("Could not bulk fetch catchment enrichment from Supabase: %s", exc)

    # CSV fallback for any missing IDs
    try:
        df = _load_csv()
    except FileNotFoundError:
        return result

    for mid in municipality_ids:
        if mid in result:
            continue
        if mid in df.index:
            result[mid] = _df_row_to_dict(df.loc[mid])

    return result
