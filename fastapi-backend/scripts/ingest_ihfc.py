"""Parse IHFC Global Heat Flow Database and extract Philippines-relevant data.

Reads the tab-delimited IHFC text file, filters for quality-controlled
measurements near the Philippines, and outputs a clean CSV for IDW
interpolation in the geothermal suitability pipeline.

Usage (from repo root with .venv activated):
    python fastapi-backend/scripts/ingest_ihfc.py

Output:
    fastapi-backend/app/services/local_data/geothermal_heatflow.csv
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

# Add repo root to path so we can import from backend
REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "fastapi-backend"
sys.path.insert(0, str(BACKEND_DIR))

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
IHFC_PATH = REPO_ROOT / "data" / "GeothermalDatasets" / "IHFC_2024_GHFDB_v.2026.03.txt"
OUTPUT_CSV = BACKEND_DIR / "app" / "services" / "local_data" / "geothermal_heatflow.csv"

# Geographic bounds: Philippines + generous buffer for IDW interpolation
MIN_LAT, MAX_LAT = 0.0, 25.0
MIN_LON, MAX_LON = 110.0, 135.0

# Quality filter: keep only measurements with reliable quality codes.
# IHFC quality scores are strings like "A1.B2.C3..."; we keep entries where
# the first character (overall quality) is 'A' or 'B'.
ALLOWED_QUALITY_PREFIXES = ("A", "B", "a", "b")

# Minimum/maximum physically plausible heat flow values (mW/m²)
Q_MIN, Q_MAX = 10.0, 250.0


def parse_ihfc(path: Path) -> pd.DataFrame | None:
    """Read IHFC text file and return a cleaned DataFrame."""
    if not path.exists():
        logger.error("IHFC file not found: %s", path)
        return None

    logger.info("Reading IHFC data from %s ...", path)
    # The first 12 lines are comments / unit headers; line 12 is the column header.
    df = pd.read_csv(
        path,
        sep="\t",
        encoding="latin-1",
        skiprows=12,
        low_memory=False,
    )

    # Keep only columns we need
    needed = {"q", "lat_NS", "long_EW", "elevation", "environment", "Quality_Score_Parent"}
    cols = [c for c in needed if c in df.columns]
    df = df[cols].copy()

    # Coerce numeric columns
    for col in ("q", "lat_NS", "long_EW", "elevation"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with missing coords or heat flow
    df = df.dropna(subset=["lat_NS", "long_EW", "q"])

    logger.info("Total measurements after basic cleaning: %d", len(df))
    return df


def filter_bounds(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only rows within the Philippines + buffer bounding box.

    NOTE: IHFC 2024 release uses 'U' (unclassified) quality codes
    for all entries, so we skip quality filtering and rely on
    physical bounds and the IDW interpolation radius instead.
    """
    mask = (
        (df["lat_NS"] >= MIN_LAT)
        & (df["lat_NS"] <= MAX_LAT)
        & (df["long_EW"] >= MIN_LON)
        & (df["long_EW"] <= MAX_LON)
        & (df["q"] >= Q_MIN)
        & (df["q"] <= Q_MAX)
    )
    filtered = df[mask].copy()
    logger.info(
        "Bounds filter (%0.1f-%0.1fN, %0.1f-%0.1fE, q %d-%d): %d rows kept",
        MIN_LAT,
        MAX_LAT,
        MIN_LON,
        MAX_LON,
        Q_MIN,
        Q_MAX,
        len(filtered),
    )
    return filtered


def main() -> int:
    if not IHFC_PATH.exists():
        logger.error("Cannot find IHFC source file: %s", IHFC_PATH)
        return 1

    df = parse_ihfc(IHFC_PATH)
    if df is None or df.empty:
        logger.error("No data parsed from IHFC file")
        return 1

    df = filter_bounds(df)

    if df.empty:
        logger.error("No measurements passed bounds filters")
        return 1

    # Rename columns for downstream compatibility
    df = df.rename(
        columns={
            "lat_NS": "lat",
            "long_EW": "lon",
            "q": "heat_flow_mw_m2",
        }
    )

    # Reorder columns
    out_cols = ["lat", "lon", "heat_flow_mw_m2", "elevation", "environment"]
    out_cols = [c for c in out_cols if c in df.columns]
    df = df[out_cols].copy()

    # Sort by lat/lon for readability
    df = df.sort_values(["lat", "lon"]).reset_index(drop=True)

    # Ensure output directory exists
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)

    logger.info("Wrote %d heat-flow measurements to %s", len(df), OUTPUT_CSV)
    logger.info("Lat range: %0.3f - %0.3f", df["lat"].min(), df["lat"].max())
    logger.info("Lon range: %0.3f - %0.3f", df["lon"].min(), df["lon"].max())
    logger.info("Heat-flow range: %0.1f - %0.1f mW/m²", df["heat_flow_mw_m2"].min(), df["heat_flow_mw_m2"].max())

    return 0


if __name__ == "__main__":
    sys.exit(main())
