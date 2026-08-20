"""Extract solar and wind atlas values at Philippine municipality centroids.

Samples Global Solar Atlas and Global Wind Atlas rasters at the centroids
produced by extract_centroids.py and writes a CSV for ingestion into Supabase.

Usage (from repo root, with .venv activated):
    .venv\\Scripts\\python.exe scripts/extract_atlas_values.py
"""
from __future__ import annotations

import csv
import logging
import math
from pathlib import Path
from typing import Any

import rasterio
from rasterio.sample import sample_gen

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "newDataPointsToExtract"
GSA_DIR = (
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

GSA_DAILY_LAYERS = {
    "solar_ghi_kwh_m2_day": "GHI.tif",
    "solar_dni_kwh_m2_day": "DNI.tif",
    "solar_dif_kwh_m2_day": "DIF.tif",
    "solar_gti_kwh_m2_day": "GTI.tif",
    "solar_pvout_daily_kwh_kwp": "PVOUT.tif",
    "solar_temp_c": "TEMP.tif",
    "solar_optimal_tilt_deg": "OPTA.tif",
}

GSA_YEARLY_LAYERS = {
    "solar_pvout_annual_kwh_kwp": "PVOUT.tif",
}

WIND_LAYERS = {
    "wind_speed_10m_ms": DATA_DIR / "GlobalWindAtlas_PHL_wind-speed_10m.tif",
    "wind_speed_50m_ms": DATA_DIR / "GlobalWindAtlas_PHL_wind-speed_50m.tif",
    "wind_speed_100m_ms": DATA_DIR / "GlobalWindAtlas_PHL_wind-speed_100m.tif",
}


def load_centroids(path: Path) -> list[dict[str, Any]]:
    """Load centroid CSV with municipality_id, province_id, centroid_lat, centroid_lon."""
    if not path.exists():
        raise FileNotFoundError(f"Centroids file not found: {path}")
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sample_points(tif_path: Path, points: list[tuple[float, float]]) -> list[float | None]:
    """Sample a GeoTIFF at (lon, lat) points. Returns list of values or None for nodata."""
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


def clamp_or_none(value: float | None, min_val: float, max_val: float) -> float | None:
    if value is None or math.isnan(value):
        return None
    if value < min_val or value > max_val:
        logger.warning("Value %s out of range [%.3f, %.3f]; returning None", value, min_val, max_val)
        return None
    return value


def main() -> int:
    centroid_csv = OUTPUT_DIR / "geospatial_municipality_centroids.csv"
    rows = load_centroids(centroid_csv)
    logger.info("Loaded %s centroids", len(rows))

    # Build (lon, lat) point list for rasterio.sample
    points = [(float(r["centroid_lon"]), float(r["centroid_lat"])) for r in rows]

    # GSA daily layers
    daily_values: dict[str, list[float | None]] = {}
    for key, filename in GSA_DAILY_LAYERS.items():
        p = GSA_DIR / filename
        daily_values[key] = sample_points(p, points)
        logger.info("Sampled %s (%s) from %s", key, filename, p)

    # GSA yearly layers
    yearly_values: dict[str, list[float | None]] = {}
    for key, filename in GSA_YEARLY_LAYERS.items():
        p = GSA_YEARLY_DIR / filename
        yearly_values[key] = sample_points(p, points)
        logger.info("Sampled %s (%s) from %s", key, filename, p)

    # Wind layers
    wind_values: dict[str, list[float | None]] = {}
    for key, p in WIND_LAYERS.items():
        wind_values[key] = sample_points(p, points)
        logger.info("Sampled %s from %s", key, p)

    output_rows = []
    for i, r in enumerate(rows):
        province_id = int(r["province_id"]) if r.get("province_id") else None
        if province_id is None:
            continue

        row: dict[str, Any] = {
            "municipality_id": int(r["municipality_id"]),
            "province_id": province_id,
            "centroid_lat": round(float(r["centroid_lat"]), 6),
            "centroid_lon": round(float(r["centroid_lon"]), 6),
        }

        # Solar daily values with per-variable ranges
        solar_daily_ranges = {
            "solar_ghi_kwh_m2_day": (0.0, 10.0),
            "solar_dni_kwh_m2_day": (0.0, 10.0),
            "solar_dif_kwh_m2_day": (0.0, 10.0),
            "solar_gti_kwh_m2_day": (0.0, 10.0),
            "solar_pvout_daily_kwh_kwp": (0.0, 15.0),
            "solar_temp_c": (0.0, 60.0),
            "solar_optimal_tilt_deg": (-90.0, 90.0),
        }
        for key in GSA_DAILY_LAYERS:
            min_v, max_v = solar_daily_ranges[key]
            row[key] = clamp_or_none(daily_values[key][i], min_v, max_v)

        # Solar yearly values
        for key in GSA_YEARLY_LAYERS:
            val = yearly_values[key][i]
            row[key] = clamp_or_none(val, 0.0, 2500.0)

        # Wind values
        for key in WIND_LAYERS:
            val = wind_values[key][i]
            row[key] = clamp_or_none(val, 0.0, 60.0)

        # Consistency: derive daily from annual if one is missing
        if row.get("solar_pvout_daily_kwh_kwp") is None and row.get("solar_pvout_annual_kwh_kwp"):
            row["solar_pvout_daily_kwh_kwp"] = row["solar_pvout_annual_kwh_kwp"] / 365.0

        output_rows.append(row)

    # Deduplicate by municipality_id in case the centroid CSV contains multiple matches.
    seen_ids = set()
    unique_rows = []
    for row in output_rows:
        mid = row["municipality_id"]
        if mid not in seen_ids:
            seen_ids.add(mid)
            unique_rows.append(row)
    output_rows = unique_rows

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "municipality_atlas_averages.csv"
    fieldnames = [
        "municipality_id",
        "province_id",
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

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(output_rows)

    logger.info("Wrote %s rows to %s", len(output_rows), out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
