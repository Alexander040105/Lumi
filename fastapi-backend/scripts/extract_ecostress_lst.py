"""Extract ECOSTRESS L2G LSTE surface temperature for Philippine municipalities.

ECOSTRESS L2G products are provided in HDF-EOS5 format with:
    - LST (Land Surface Temperature): uint16, scale_factor=0.02, units=K
    - valid_range: [7500, 65535] (raw uint16)

The georeferencing metadata in these files uses HDF-EOS grid structures.
For Philippine applicability we attempt a basic affine transform from the
embedded UpperLeft / LowerRight corner points.

Usage (from repo root with .venv activated):
    python fastapi-backend/scripts/extract_ecostress_lst.py

Output:
    fastapi-backend/app/services/local_data/ecostress_lst_sample.csv
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_H5 = (
    REPO_ROOT
    / "data"
    / "GeothermalDatasets"
    / "ECOv003_L2G_LSTE_45056_033_20260616T160816_02.h5"
)
OUTPUT_CSV = (
    REPO_ROOT
    / "fastapi-backend"
    / "app"
    / "services"
    / "local_data"
    / "ecostress_lst_sample.csv"
)

# Philippine bounding box (WGS84)
PH_BOUNDS = {"lat_min": 4.0, "lat_max": 21.5, "lon_min": 116.0, "lon_max": 127.0}


def read_lst_array(h5_path: Path) -> tuple[np.ndarray, dict] | None:
    """Read raw LST uint16 array and metadata from ECOSTRESS L2G HDF5.

    Returns:
        (raw_lst_array, meta_dict) or None on error.
    """
    if not h5_path.exists():
        logger.error("HDF5 file not found: %s", h5_path)
        return None

    try:
        with h5py.File(h5_path, "r") as f:
            lst_ds = f["HDFEOS"]["GRIDS"]["ECO_L2G_LSTE_70m"]["Data Fields"]["LST"]
            raw = lst_ds[()]

            meta = {
                "scale_factor": float(lst_ds.attrs["scale_factor"][0]),
                "add_offset": float(lst_ds.attrs["add_offset"][0]),
                "units": lst_ds.attrs["units"].decode("utf-8"),
                "fill_value": int(lst_ds.attrs["_FillValue"][0]),
                "valid_min": int(lst_ds.attrs["valid_range"][0]),
                "valid_max": int(lst_ds.attrs["valid_range"][1]),
                "shape": raw.shape,
            }
            logger.info("LST array shape: %s | dtype: %s", raw.shape, raw.dtype)
            logger.info(
                "Scale factor: %s | Offset: %s | Units: %s",
                meta["scale_factor"],
                meta["add_offset"],
                meta["units"],
            )
            return raw, meta
    except Exception as exc:
        logger.error("Failed to read LST from HDF5: %s", exc)
        return None


def extract_spatial_extent(h5_path: Path) -> dict | None:
    """Parse HDF-EOS StructMetadata to get corner coordinates.

    NOTE: ECOSTRESS L2G metadata projection interpretation can be
    ambiguous. This function extracts raw values for manual review.
    """
    try:
        with h5py.File(h5_path, "r") as f:
            meta_bytes = f["HDFEOS INFORMATION"]["StructMetadata.0"][()]
            meta = meta_bytes.decode("utf-8")
    except Exception as exc:
        logger.error("Failed to read metadata: %s", exc)
        return None

    import re

    extent = {}
    # UpperLeft
    m = re.search(r"UpperLeftPointMtrs=\(([-\d.]+),\s*([-\d.]+)\)", meta)
    if m:
        extent["upper_left_x"] = float(m.group(1))
        extent["upper_left_y"] = float(m.group(2))

    # LowerRight
    m = re.search(r"LowerRightMtrs=\(([-\d.]+),\s*([-\d.]+)\)", meta)
    if m:
        extent["lower_right_x"] = float(m.group(1))
        extent["lower_right_y"] = float(m.group(2))

    # Projection
    m = re.search(r'Projection=(\w+)', meta)
    if m:
        extent["projection"] = m.group(1)

    # Pixel size (if available)
    m = re.search(r"PixelSize=\(([-\d.]+),\s*([-\d.]+)\)", meta)
    if m:
        extent["pixel_size_x"] = float(m.group(1))
        extent["pixel_size_y"] = float(m.group(2))

    logger.info("Spatial extent from metadata: %s", extent)
    return extent


def build_affine_transform(extent: dict, shape: tuple) -> dict | None:
    """Build a simple affine transform assuming geographic coverage.

    WARNING: ECOSTRESS L2G metadata projection values can be misleading.
    This is a best-effort linear transform for Philippine coverage.
    For production use, verify against NASA AppEEARS or official tools.
    """
    if not extent or "upper_left_x" not in extent:
        return None

    rows, cols = shape
    ul_x = extent["upper_left_x"]
    ul_y = extent["upper_left_y"]
    lr_x = extent["lower_right_x"]
    lr_y = extent["lower_right_y"]

    # Some ECOSTRESS L2G files have metadata in units of 1E-6 degrees
    # when projection says GEO. Detect and rescale if needed.
    if abs(ul_x) > 180 or abs(lr_x) > 180:
        logger.warning("Coordinates exceed +/-180; rescaling by 1e-6")
        ul_x *= 1e-6
        lr_x *= 1e-6
        ul_y *= 1e-6
        lr_y *= 1e-6

    pixel_width = (lr_x - ul_x) / cols
    pixel_height = (lr_y - ul_y) / rows  # usually negative

    return {
        "ul_x": ul_x,
        "ul_y": ul_y,
        "pixel_width": pixel_width,
        "pixel_height": pixel_height,
        "rows": rows,
        "cols": cols,
    }


def extract_temperature_at(
    lat: float,
    lon: float,
    raw_lst: np.ndarray,
    transform: dict,
    meta: dict,
) -> float | None:
    """Extract scaled LST (°C) at a given lat/lon using bilinear lookup.

    Returns:
        Surface temperature in °C, or None if out of bounds / invalid.
    """
    ul_x = transform["ul_x"]
    ul_y = transform["ul_y"]
    pw = transform["pixel_width"]
    ph = transform["pixel_height"]
    rows = transform["rows"]
    cols = transform["cols"]

    # Map lat/lon to array indices (approximate)
    col_f = (lon - ul_x) / pw
    row_f = (lat - ul_y) / ph

    c0 = int(np.floor(col_f))
    r0 = int(np.floor(row_f))

    if not (0 <= c0 < cols - 1 and 0 <= r0 < rows - 1):
        return None

    # Simple bilinear interpolation
    dc = col_f - c0
    dr = row_f - r0
    vals = raw_lst[r0 : r0 + 2, c0 : c0 + 2].astype(float)

    fill = meta["fill_value"]
    valid_min = meta["valid_min"]
    valid_max = meta["valid_max"]
    scale = meta["scale_factor"]
    offset = meta["add_offset"]

    # Mask invalid values
    vals[(vals == fill) | (vals < valid_min) | (vals > valid_max)] = np.nan

    if np.all(np.isnan(vals)):
        return None

    # Bilinear interpolation (handling NaNs gracefully)
    top = np.nansum([vals[0, 0] * (1 - dc), vals[0, 1] * dc])
    bot = np.nansum([vals[1, 0] * (1 - dc), vals[1, 1] * dc])
    raw = top * (1 - dr) + bot * dr

    if np.isnan(raw):
        return None

    # Convert to Celsius
    temp_k = raw * scale + offset
    temp_c = temp_k - 273.15
    return round(float(temp_c), 2)


def main() -> int:
    raw_lst, meta = read_lst_array(INPUT_H5)
    if raw_lst is None:
        return 1

    extent = extract_spatial_extent(INPUT_H5)
    transform = build_affine_transform(extent, meta["shape"]) if extent else None

    if transform is None:
        logger.error("Could not build spatial transform; aborting sample extraction")
        return 1

    # Check if scene actually covers the Philippines
    scene_lon_min = min(transform["ul_x"], transform["ul_x"] + transform["pixel_width"] * transform["cols"])
    scene_lon_max = max(transform["ul_x"], transform["ul_x"] + transform["pixel_width"] * transform["cols"])
    scene_lat_min = min(transform["ul_y"], transform["ul_y"] + transform["pixel_height"] * transform["rows"])
    scene_lat_max = max(transform["ul_y"], transform["ul_y"] + transform["pixel_height"] * transform["rows"])

    logger.info(
        "Scene coverage: lon %.3f-%.3f, lat %.3f-%.3f",
        scene_lon_min, scene_lon_max, scene_lat_min, scene_lat_max,
    )

    # Philippine bounds
    ph_lon = (PH_BOUNDS["lon_min"], PH_BOUNDS["lon_max"])
    ph_lat = (PH_BOUNDS["lat_min"], PH_BOUNDS["lat_max"])

    overlaps = not (
        scene_lon_max < ph_lon[0]
        or scene_lon_min > ph_lon[1]
        or scene_lat_max < ph_lat[0]
        or scene_lat_min > ph_lat[1]
    )

    if not overlaps:
        logger.warning(
            "This ECOSTRESS scene does NOT overlap the Philippines. "
            "Scene: lon %.1f-%.1f, lat %.1f-%.1f | PH: lon %.1f-%.1f, lat %.1f-%.1f",
            scene_lon_min, scene_lon_max, scene_lat_min, scene_lat_max,
            ph_lon[0], ph_lon[1], ph_lat[0], ph_lat[1],
        )
        logger.info("Skipping extraction. Obtain a scene covering 116-127°E, 4-21°N for Philippine use.")
        return 0

    # Extract a grid of sample points within PH bounds (intersecting scene only)
    lat_min = max(PH_BOUNDS["lat_min"], scene_lat_min)
    lat_max = min(PH_BOUNDS["lat_max"], scene_lat_max)
    lon_min = max(PH_BOUNDS["lon_min"], scene_lon_min)
    lon_max = min(PH_BOUNDS["lon_max"], scene_lon_max)

    lats = np.linspace(lat_min, lat_max, 20)
    lons = np.linspace(lon_min, lon_max, 20)

    samples = []
    for lat in lats:
        for lon in lons:
            temp_c = extract_temperature_at(lat, lon, raw_lst, transform, meta)
            if temp_c is not None:
                samples.append({"lat": round(lat, 4), "lon": round(lon, 4), "surface_temp_c": temp_c})

    if not samples:
        logger.warning("No valid ECOSTRESS samples extracted for Philippine bounds")
        return 0

    df = pd.DataFrame(samples)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    logger.info(
        "Wrote %d ECOSTRESS LST samples to %s (range: %.1f - %.1f °C)",
        len(df),
        OUTPUT_CSV,
        df["surface_temp_c"].min(),
        df["surface_temp_c"].max(),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
