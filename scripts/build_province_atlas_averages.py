"""Build province-level atlas averages from municipal aggregation and direct centroid sampling.

Usage (from repo root, with .venv activated):
    .venv\\Scripts\\python.exe scripts/build_province_atlas_averages.py
"""
from __future__ import annotations

import csv
import logging
import math
from pathlib import Path
from typing import Any

import pandas as pd
import rasterio
from rasterio.sample import sample_gen

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "newDataPointsToExtract"
GSA_DAILY_DIR = (
    DATA_DIR
    / "GlobalSolarAtlasGIS"
    / "Philippines_GISdata_LTAym_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF (1)"
    / "Philippines_GISdata_LTAy_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF"
)
GSA_YEARLY_DIR = (
    DATA_DIR
    / "GlobalSolarAtlasGIS"
    / "Philippines_GISdata_LTAym_YearlyMonthlyTotals_GlobalSolarAtlas-v2_GEOTIFF (1)"
    / "Philippines_GISdata_LTAy_YearlyMonthlyTotals_GlobalSolarAtlas-v2_GEOTIFF"
)
OUTPUT_DIR = REPO_ROOT / "scripts" / "gap_output"
LOCAL_DATA_DIR = REPO_ROOT / "fastapi-backend" / "app" / "services" / "local_data"

# Solar layers: (csv_name, tif_name, min, max, is_daily)
SOLAR_DAILY_LAYERS = [
    ("solar_ghi_kwh_m2_day", "GHI.tif", 0.0, 10.0),
    ("solar_dni_kwh_m2_day", "DNI.tif", 0.0, 10.0),
    ("solar_dif_kwh_m2_day", "DIF.tif", 0.0, 10.0),
    ("solar_gti_kwh_m2_day", "GTI.tif", 0.0, 10.0),
    ("solar_pvout_daily_kwh_kwp", "PVOUT.tif", 0.0, 15.0),
    ("solar_temp_c", "TEMP.tif", 0.0, 60.0),
    ("solar_optimal_tilt_deg", "OPTA.tif", -90.0, 90.0),
]
SOLAR_YEARLY_LAYERS = [
    ("solar_pvout_annual_kwh_kwp", "PVOUT.tif", 0.0, 2500.0),
]
WIND_LAYERS = [
    ("wind_speed_10m_ms", DATA_DIR / "GlobalWindAtlas_PHL_wind-speed_10m.tif", 0.0, 60.0),
    ("wind_speed_50m_ms", DATA_DIR / "GlobalWindAtlas_PHL_wind-speed_50m.tif", 0.0, 60.0),
    ("wind_speed_100m_ms", DATA_DIR / "GlobalWindAtlas_PHL_wind-speed_100m.tif", 0.0, 60.0),
]


def sample_points(tif_path: Path, points: list[tuple[float, float]]) -> list[float | None]:
    if not tif_path.exists():
        logger.warning("Missing raster: %s", tif_path)
        return [None] * len(points)
    values: list[float | None] = []
    with rasterio.open(tif_path) as src:
        for v in sample_gen(src, points):
            val = v[0]
            if val is None or (src.nodata is not None and math.isclose(val, src.nodata)):
                values.append(None)
            else:
                values.append(float(val))
    return values


def clamp(val: float | None, min_v: float, max_v: float) -> float | None:
    if val is None or math.isnan(val):
        return None
    if val < min_v or val > max_v:
        return None
    return val


def weighted_mean(group: pd.DataFrame, col: str, weight_col: str) -> float | None:
    rows = group[group[col].notna() & group[weight_col].notna()]
    if rows.empty:
        return None
    return float((rows[col] * rows[weight_col]).sum() / rows[weight_col].sum())


def main() -> int:
    muni_csv = OUTPUT_DIR / "municipality_atlas_averages.csv"
    muni_centroid_csv = OUTPUT_DIR / "geospatial_municipality_centroids.csv"
    prov_centroid_csv = OUTPUT_DIR / "geospatial_province_centroids.csv"

    muni = pd.read_csv(muni_csv)
    muni_cent = pd.read_csv(muni_centroid_csv)
    prov_cent = pd.read_csv(prov_centroid_csv)
    # Some GeoJSON features can map to the same province_id (e.g., Isabela province + Isabela City).
    # Keep the largest-area match as the true province.
    prov_cent["area_km2"] = pd.to_numeric(prov_cent["area_km2"], errors="coerce")
    prov_cent = (
        prov_cent.sort_values("area_km2", ascending=False)
        .drop_duplicates(subset="province_id", keep="first")
        .sort_values("province_id")
        .reset_index(drop=True)
    )

    # Merge area_km2 into muni
    muni = muni.merge(
        muni_cent[["municipality_id", "area_km2"]],
        on="municipality_id",
        how="left",
    )
    muni["area_km2"] = muni["area_km2"].fillna(1.0)

    numeric_cols = [c for c, _, _, _ in SOLAR_DAILY_LAYERS] + [c for c, _, _, _ in SOLAR_YEARLY_LAYERS] + [c for c, _, _, _ in WIND_LAYERS]

    # Area-weighted municipal averages per province
    logger.info("Computing area-weighted municipal averages per province...")
    prov_muni: dict[int, dict[str, Any]] = {}
    for province_id, group in muni.groupby("province_id"):
        row: dict[str, Any] = {
            "muni_count": int(group["municipality_id"].nunique()),
        }
        for col in numeric_cols:
            row[f"muni_avg_{col}"] = weighted_mean(group, col, "area_km2")
        prov_muni[int(province_id)] = row

    # Direct centroid sample for each province
    points = [(float(r["centroid_lon"]), float(r["centroid_lat"])) for _, r in prov_cent.iterrows()]
    prov_centroid: dict[int, dict[str, Any]] = {}

    for key, tif_name, min_v, max_v in SOLAR_DAILY_LAYERS:
        vals = sample_points(GSA_DAILY_DIR / tif_name, points)
        for i, (_, r) in enumerate(prov_cent.iterrows()):
            pid = int(r["province_id"])
            prov_centroid.setdefault(pid, {})[f"centroid_{key}"] = clamp(vals[i], min_v, max_v)

    for key, tif_name, min_v, max_v in SOLAR_YEARLY_LAYERS:
        vals = sample_points(GSA_YEARLY_DIR / tif_name, points)
        for i, (_, r) in enumerate(prov_cent.iterrows()):
            pid = int(r["province_id"])
            prov_centroid[pid][f"centroid_{key}"] = clamp(vals[i], min_v, max_v)

    for key, tif_path, min_v, max_v in WIND_LAYERS:
        vals = sample_points(tif_path, points)
        for i, (_, r) in enumerate(prov_cent.iterrows()):
            pid = int(r["province_id"])
            prov_centroid[pid][f"centroid_{key}"] = clamp(vals[i], min_v, max_v)

    # Reconcile: use muni_avg as final; record notes where centroid differs >5%
    logger.info("Reconciling municipal averages and centroid samples...")
    output_rows: list[dict[str, Any]] = []
    for _, r in prov_cent.iterrows():
        province_id = int(r["province_id"])
        province_name = r["name"].strip().upper()
        centroid_lat = round(float(r["centroid_lat"]), 6)
        centroid_lon = round(float(r["centroid_lon"]), 6)

        row: dict[str, Any] = {
            "province_id": province_id,
            "province_name": province_name,
            "centroid_lat": centroid_lat,
            "centroid_lon": centroid_lon,
        }
        row.update(prov_muni.get(province_id, {}))
        row.update(prov_centroid.get(province_id, {}))

        notes: list[str] = []
        for col in numeric_cols:
            muni_col = f"muni_avg_{col}"
            cent_col = f"centroid_{col}"
            m_val = row.get(muni_col)
            c_val = row.get(cent_col)
            final = m_val if m_val is not None else c_val
            row[col] = final
            if m_val is not None and c_val is not None and c_val != 0:
                diff = abs(m_val - c_val) / max(abs(m_val), abs(c_val)) * 100.0
                if diff > 5.0:
                    notes.append(f"{col}: muni={m_val:.3f} vs centroid={c_val:.3f} ({diff:.1f}%)")

        row["reconciliation_note"] = "; ".join(notes) if notes else None

        output_rows.append(row)

    # Build flat CSV
    fieldnames = ["province_id", "province_name", "centroid_lat", "centroid_lon"]
    for col in numeric_cols:
        fieldnames.append(f"muni_avg_{col}")
    for col in numeric_cols:
        fieldnames.append(f"centroid_{col}")
    for col in numeric_cols:
        fieldnames.append(col)
    fieldnames += ["muni_count", "reconciliation_note", "data_source"]

    for row in output_rows:
        row.setdefault("data_source", "Global Solar Atlas / Global Wind Atlas")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

    out_path = OUTPUT_DIR / "province_atlas_averages.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(output_rows)

    local_path = LOCAL_DATA_DIR / "province_atlas_averages.csv"
    with open(local_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(output_rows)

    logger.info("Wrote %d province rows to %s and %s", len(output_rows), out_path, local_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
