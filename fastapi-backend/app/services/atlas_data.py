"""Atlas data loader for Global Solar Atlas / Global Wind Atlas values.

Tries Supabase first, then falls back to the bundled local CSV so EcoSim can
use atlas values even when the `municipality_atlas_averages` table has not yet
been created in the target database.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)

LOCAL_ATLAS_CSV = Path(__file__).resolve().parent / "local_data" / "municipality_atlas_averages.csv"


def _load_csv() -> pd.DataFrame:
    if not LOCAL_ATLAS_CSV.exists():
        raise FileNotFoundError(f"Atlas CSV not found at {LOCAL_ATLAS_CSV}")
    df = pd.read_csv(LOCAL_ATLAS_CSV)
    df.set_index("municipality_id", inplace=True)
    return df


def _df_row_to_dict(row: pd.Series) -> dict[str, Any]:
    return {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}


def get_atlas_for_municipality(municipality_id: int) -> dict[str, Any] | None:
    """Return atlas values for a single municipality, or None if unavailable."""
    # Supabase fast path (production)
    try:
        client = get_supabase_client()
        resp = (
            client.table("municipality_atlas_averages")
            .select("*")
            .eq("municipality_id", municipality_id)
            .maybe_single()
            .execute()
        )
        if resp.data:
            return resp.data
    except Exception as exc:
        logger.warning("Could not fetch atlas data from Supabase: %s", exc)

    # CSV fallback
    df = _load_csv()
    if municipality_id in df.index:
        return _df_row_to_dict(df.loc[municipality_id])
    return None


def get_atlas_for_municipality_ids(municipality_ids: list[int]) -> dict[int, dict[str, Any]]:
    """Return atlas values for many municipalities keyed by ID."""
    # Supabase fast path
    try:
        client = get_supabase_client()
        resp = (
            client.table("municipality_atlas_averages")
            .select("*")
            .in_("municipality_id", municipality_ids)
            .execute()
        )
        if resp.data:
            return {r["municipality_id"]: r for r in resp.data}
    except Exception as exc:
        logger.warning("Could not fetch atlas data from Supabase: %s", exc)

    # CSV fallback
    df = _load_csv()
    common = df.loc[df.index.intersection(municipality_ids)]
    return {int(idx): _df_row_to_dict(row) for idx, row in common.iterrows()}


def get_atlas_for_province(province_id: int) -> dict[str, Any]:
    """Return simple mean atlas values for all municipalities in a province."""
    # Supabase fast path
    try:
        client = get_supabase_client()
        resp = (
            client.table("municipality_atlas_averages")
            .select("*")
            .eq("province_id", province_id)
            .execute()
        )
        if resp.data:
            return _mean_rows(resp.data)
    except Exception as exc:
        logger.warning("Could not fetch atlas data from Supabase: %s", exc)

    # CSV fallback
    df = _load_csv()
    province_df = df[df["province_id"] == province_id]
    if province_df.empty:
        return {}
    return _mean_rows(province_df.reset_index().to_dict("records"))


def _mean_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute the arithmetic mean of all numeric atlas columns."""
    if not rows:
        return {}
    numeric_cols = [k for k, v in rows[0].items() if isinstance(v, (int, float))]
    result: dict[str, Any] = {"municipality_count": len(rows), "data_source": "Global Solar Atlas / Global Wind Atlas"}
    for col in numeric_cols:
        values = [r[col] for r in rows if r[col] is not None]
        if values:
            result[col] = round(sum(values) / len(values), 4)
        else:
            result[col] = None
    return result
