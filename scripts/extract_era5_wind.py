"""Extract ERA5 10-metre wind at municipality and province centroids.

Usage (from repo root, with .venv activated):
    .venv\\Scripts\\python.exe scripts/extract_era5_wind.py
"""
from __future__ import annotations

import csv
import logging
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import scipy.interpolate
import xarray as xr

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
GRIB_PATH = REPO_ROOT / "data" / "newDataPointsToExtract" / "ERA5_copernicusData.grib"
OUTPUT_DIR = REPO_ROOT / "scripts" / "gap_output"
LOCAL_DATA_DIR = REPO_ROOT / "fastapi-backend" / "app" / "services" / "local_data"


def sample_gridded(ds: xr.Dataset, points: list[tuple[float, float]]) -> dict[str, list[float | None]]:
    """Sample a 2D mean-wind xarray DataArray at (lat, lon) points using bilinear interpolation."""
    lats = ds.latitude.values.astype(float)
    lons = ds.longitude.values.astype(float)

    # RegularGridInterpolator wants ascending coordinates.
    if lats[0] > lats[-1]:
        lats = lats[::-1]
        values_u = ds["u10_mean"].values[::-1, :]
        values_v = ds["v10_mean"].values[::-1, :]
    else:
        values_u = ds["u10_mean"].values
        values_v = ds["v10_mean"].values

    interp_u = scipy.interpolate.RegularGridInterpolator(
        (lats, lons), values_u, bounds_error=False, fill_value=None
    )
    interp_v = scipy.interpolate.RegularGridInterpolator(
        (lats, lons), values_v, bounds_error=False, fill_value=None
    )

    arr = np.array(points)
    u_vals = interp_u(arr)
    v_vals = interp_v(arr)
    ws = np.sqrt(u_vals**2 + v_vals**2)

    results: dict[str, list[float | None]] = {
        "era5_u10_ms": [],
        "era5_v10_ms": [],
        "era5_wind_speed_10m_ms": [],
    }
    for i, (lat, lon) in enumerate(points):
        u, v, w = float(u_vals[i]), float(v_vals[i]), float(ws[i])
        # Clamp to reasonable bounds; the PH domain is 0-40 m/s.
        if not (0.0 <= w <= 60.0) or math.isnan(w):
            results["era5_u10_ms"].append(None)
            results["era5_v10_ms"].append(None)
            results["era5_wind_speed_10m_ms"].append(None)
        else:
            results["era5_u10_ms"].append(round(u, 4))
            results["era5_v10_ms"].append(round(v, 4))
            results["era5_wind_speed_10m_ms"].append(round(w, 4))
    return results


def main() -> int:
    logger.info("Opening %s with xarray/cfgrib...", GRIB_PATH)
    ds = xr.open_dataset(GRIB_PATH, engine="cfgrib")
    logger.info("Dataset: %s", ds)

    # Compute long-term means over the time dimension.
    # The file contains u/v 10m components; we convert to scalar speed.
    logger.info("Computing time means for u10 and v10...")
    ds["u10_mean"] = ds["u10"].mean(dim="time").astype(float)
    ds["v10_mean"] = ds["v10"].mean(dim="time").astype(float)

    # Load municipality points from the atlas CSV (already deduped and matched to DB IDs)
    muni_csv = OUTPUT_DIR / "municipality_atlas_averages.csv"
    muni = pd.read_csv(muni_csv)
    muni_points = [(float(r["centroid_lat"]), float(r["centroid_lon"])) for _, r in muni.iterrows()]
    muni_results = sample_gridded(ds, muni_points)

    muni_rows: list[dict[str, Any]] = []
    for i, (_, r) in enumerate(muni.iterrows()):
        muni_rows.append(
            {
                "municipality_id": int(r["municipality_id"]),
                "province_id": int(r["province_id"]),
                "centroid_lat": round(float(r["centroid_lat"]), 6),
                "centroid_lon": round(float(r["centroid_lon"]), 6),
                "era5_u10_ms": muni_results["era5_u10_ms"][i],
                "era5_v10_ms": muni_results["era5_v10_ms"][i],
                "era5_wind_speed_10m_ms": muni_results["era5_wind_speed_10m_ms"][i],
                "data_source": "ERA5 (Copernicus)",
            }
        )

    # Province points from the deduped centroid CSV
    prov_cent_csv = OUTPUT_DIR / "geospatial_province_centroids.csv"
    prov_cent = pd.read_csv(prov_cent_csv)
    prov_cent["area_km2"] = pd.to_numeric(prov_cent["area_km2"], errors="coerce")
    prov_cent = (
        prov_cent.sort_values("area_km2", ascending=False)
        .drop_duplicates(subset="province_id", keep="first")
        .sort_values("province_id")
        .reset_index(drop=True)
    )
    prov_points = [(float(r["centroid_lat"]), float(r["centroid_lon"])) for _, r in prov_cent.iterrows()]
    prov_results = sample_gridded(ds, prov_points)

    prov_rows: list[dict[str, Any]] = []
    for i, (_, r) in enumerate(prov_cent.iterrows()):
        prov_rows.append(
            {
                "province_id": int(r["province_id"]),
                "province_name": r["name"].strip().upper(),
                "centroid_lat": round(float(r["centroid_lat"]), 6),
                "centroid_lon": round(float(r["centroid_lon"]), 6),
                "era5_u10_ms": prov_results["era5_u10_ms"][i],
                "era5_v10_ms": prov_results["era5_v10_ms"][i],
                "era5_wind_speed_10m_ms": prov_results["era5_wind_speed_10m_ms"][i],
                "data_source": "ERA5 (Copernicus)",
            }
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for rows, name in [(muni_rows, "municipality_era5_averages"), (prov_rows, "province_era5_averages")]:
        path = OUTPUT_DIR / f"{name}.csv"
        local_path = LOCAL_DATA_DIR / f"{name}.csv"
        fieldnames = list(rows[0].keys())
        for p in (path, local_path):
            with open(p, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        logger.info("Wrote %d %s rows to %s and %s", len(rows), name, path, local_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
