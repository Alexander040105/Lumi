"""Regenerate province-level atlas and ERA5 fallback CSVs from municipalities.

The script loads the existing ``province_atlas_averages.csv`` and
``province_era5_averages.csv`` files, finds province IDs that appear in the
municipality CSVs but are missing from the province CSVs, computes a simple
arithmetic mean for all numeric columns, and appends the new rows.  It is
idempotent: running it again will not create duplicates.
"""
from __future__ import annotations

import csv
import os
import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_DATA_DIR = REPO_ROOT / "fastapi-backend" / "app" / "services" / "local_data"


def _load_or_empty(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def _get_supabase_province_names(province_ids: set[int]) -> dict[int, str]:
    """Fetch province names from Supabase, if available."""
    try:
        sys.path.insert(0, str(REPO_ROOT / "fastapi-backend"))
        from app.services.supabase_service import get_supabase_client

        client = get_supabase_client()
        resp = client.table("provinces").select("province_id,name").limit(1000).execute()
        rows = resp.data or []
        return {int(r["province_id"]): r.get("name", "").upper() for r in rows}
    except Exception as exc:
        print(f"Could not fetch province names from Supabase: {exc}", file=sys.stderr)
        return {}


def _regenerate_atlas() -> None:
    province_path = LOCAL_DATA_DIR / "province_atlas_averages.csv"
    muni_path = LOCAL_DATA_DIR / "municipality_atlas_averages.csv"

    province_df = _load_or_empty(province_path)
    muni_df = _load_or_empty(muni_path)

    if muni_df.empty:
        print(f"Municipality atlas CSV not found at {muni_path}; skipping.", file=sys.stderr)
        return

    existing_ids = set(int(x) for x in province_df["province_id"].dropna().unique()) if not province_df.empty else set()
    muni_ids = set(int(x) for x in muni_df["province_id"].dropna().unique())
    missing_ids = sorted(muni_ids - existing_ids)

    if not missing_ids:
        print("No missing province atlas rows.")
        return

    print(f"Generating province atlas rows for {len(missing_ids)} missing province IDs: {missing_ids}")

    # Province name lookup from Supabase, plus a tiny hard-coded safety net for
    # local development without a Supabase client.
    name_map = _get_supabase_province_names(set(missing_ids))
    name_map.setdefault(271, "QUEZON")
    name_map.setdefault(308, "COMPOSTELA VALLEY")
    name_map.setdefault(309, "DAVAO (DAVAO DEL NORTE)")
    name_map.setdefault(324, "MAGUINDANAO")
    name_map.setdefault(339, "NCR - 4TH DISTRICT")
    name_map.setdefault(340, "NCR - 1ST DISTRICT (MANILA)")
    name_map.setdefault(341, "NCR - 2ND DISTRICT")
    name_map.setdefault(342, "NCR - 3RD DISTRICT")

    # Identify numeric columns to average (exclude ID and coordinate columns).
    exclude = {"municipality_id", "province_id", "centroid_lat", "centroid_lon"}
    numeric_cols = [c for c in muni_df.columns if c not in exclude and pd.api.types.is_numeric_dtype(muni_df[c])]

    # Build the existing columns set from the province CSV, or the municipality
    # columns with the extra province fields if the province CSV is new.
    if province_df.empty:
        base_cols = ["province_id", "province_name", "centroid_lat", "centroid_lon", *numeric_cols]
    else:
        base_cols = list(province_df.columns)

    new_rows: list[dict] = []
    for pid in missing_ids:
        group = muni_df[muni_df["province_id"] == pid]
        if group.empty:
            continue

        centroid_lat = float(group["centroid_lat"].mean())
        centroid_lon = float(group["centroid_lon"].mean())
        muni_count = len(group)

        row: dict[str, object] = {
            "province_id": pid,
            "province_name": name_map.get(pid, f"PROVINCE {pid}"),
            "centroid_lat": round(centroid_lat, 6),
            "centroid_lon": round(centroid_lon, 6),
            "muni_count": int(muni_count),
            "reconciliation_note": f"Generated from {muni_count} municipality averages.",
            "data_source": "Global Solar Atlas / Global Wind Atlas",
        }

        # Compute means for every numeric column that exists in the province CSV.
        for col in base_cols:
            if col in numeric_cols:
                mean_val = group[col].mean()
                row[col] = round(float(mean_val), 6) if pd.notna(mean_val) else None

        # For the existing province CSV, ensure the prefixed and final columns
        # line up with the municipality averages so downstream code is happy.
        for col in numeric_cols:
            if f"muni_avg_{col}" in base_cols:
                row[f"muni_avg_{col}"] = row.get(col)
            if f"centroid_{col}" in base_cols:
                row[f"centroid_{col}"] = row.get(col)

        new_rows.append(row)

    if new_rows:
        new_df = pd.DataFrame(new_rows)
        combined = pd.concat([province_df, new_df], ignore_index=True)
        combined.to_csv(province_path, index=False)
        print(f"Wrote {len(new_rows)} new rows to {province_path}")


def _regenerate_era5() -> None:
    province_path = LOCAL_DATA_DIR / "province_era5_averages.csv"
    muni_path = LOCAL_DATA_DIR / "municipality_era5_averages.csv"

    province_df = _load_or_empty(province_path)
    muni_df = _load_or_empty(muni_path)

    if muni_df.empty:
        print(f"Municipality ERA5 CSV not found at {muni_path}; skipping.", file=sys.stderr)
        return

    existing_ids = set(int(x) for x in province_df["province_id"].dropna().unique()) if not province_df.empty else set()
    muni_ids = set(int(x) for x in muni_df["province_id"].dropna().unique())
    missing_ids = sorted(muni_ids - existing_ids)

    if not missing_ids:
        print("No missing province ERA5 rows.")
        return

    print(f"Generating province ERA5 rows for {len(missing_ids)} missing province IDs: {missing_ids}")

    name_map = _get_supabase_province_names(set(missing_ids))
    name_map.setdefault(271, "QUEZON")
    name_map.setdefault(308, "COMPOSTELA VALLEY")
    name_map.setdefault(309, "DAVAO (DAVAO DEL NORTE)")
    name_map.setdefault(324, "MAGUINDANAO")
    name_map.setdefault(339, "NCR - 4TH DISTRICT")
    name_map.setdefault(340, "NCR - 1ST DISTRICT (MANILA)")
    name_map.setdefault(341, "NCR - 2ND DISTRICT")
    name_map.setdefault(342, "NCR - 3RD DISTRICT")

    exclude = {"municipality_id", "province_id", "centroid_lat", "centroid_lon", "data_source"}
    numeric_cols = [c for c in muni_df.columns if c not in exclude and pd.api.types.is_numeric_dtype(muni_df[c])]

    new_rows: list[dict] = []
    for pid in missing_ids:
        group = muni_df[muni_df["province_id"] == pid]
        if group.empty:
            continue

        row: dict[str, object] = {
            "province_id": pid,
            "province_name": name_map.get(pid, f"PROVINCE {pid}"),
            "centroid_lat": round(float(group["centroid_lat"].mean()), 6),
            "centroid_lon": round(float(group["centroid_lon"].mean()), 6),
            "data_source": "ERA5 (Copernicus)",
        }

        for col in numeric_cols:
            mean_val = group[col].mean()
            row[col] = round(float(mean_val), 6) if pd.notna(mean_val) else None

        new_rows.append(row)

    if new_rows:
        new_df = pd.DataFrame(new_rows)
        combined = pd.concat([province_df, new_df], ignore_index=True)
        combined.to_csv(province_path, index=False)
        print(f"Wrote {len(new_rows)} new rows to {province_path}")


def main() -> None:
    os.chdir(REPO_ROOT)
    _regenerate_atlas()
    _regenerate_era5()


if __name__ == "__main__":
    main()
