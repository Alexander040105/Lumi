"""Pre-process aquifer shapefile for fast point-in-polygon queries.

Extracts Philippines polygons, reprojects to WGS84 (EPSG:4326),
and saves as a lightweight GeoJSON for the geothermal scoring pipeline.

Usage (from repo root with .venv activated):
    python fastapi-backend/scripts/prepare_aquifer_spatial.py

Output:
    fastapi-backend/app/services/local_data/aquifers_ph.geojson
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import geopandas as gpd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_SHP = (
    REPO_ROOT
    / "GeothermalDatasets"
    / "shapefilesForAquiferProperties"
    / "All_merged.shp"
)
OUTPUT_GEOJSON = (
    REPO_ROOT
    / "fastapi-backend"
    / "app"
    / "services"
    / "local_data"
    / "aquifers_ph.geojson"
)


def main() -> int:
    if not INPUT_SHP.exists():
        logger.error("Shapefile not found: %s", INPUT_SHP)
        return 1

    logger.info("Reading aquifer shapefile...")
    gdf = gpd.read_file(INPUT_SHP)
    logger.info("Total polygons: %d | CRS: %s", len(gdf), gdf.crs)

    # Filter Philippines
    ph = gdf[gdf["COUNTRY"].str.contains("Philippines", case=False, na=False)].copy()
    logger.info("Philippines polygons: %d", len(ph))

    if ph.empty:
        logger.error("No Philippines polygons found")
        return 1

    # Reproject to WGS84 for lat/lon queries
    if ph.crs is not None and ph.crs.to_epsg() != 4326:
        logger.info("Reprojecting from %s to EPSG:4326...", ph.crs)
        ph = ph.to_crs(epsg=4326)

    # Keep only columns we need to reduce file size
    keep_cols = [
        "OBJECTID",
        "MEAN_Poros",
        "MEAN_Perme",
        "MEAN_thk_m",
        "MEAN_Depth",
        "COUNTRY",
        "Basin_na_2",
        "geometry",
    ]
    ph = ph[[c for c in keep_cols if c in ph.columns]].copy()

    # Rename columns to snake_case for consistency
    rename = {
        "MEAN_Poros": "porosity",
        "MEAN_Perme": "permeability_log10",
        "MEAN_thk_m": "thickness_m",
        "MEAN_Depth": "depth_m",
        "Basin_na_2": "basin_name",
    }
    ph = ph.rename(columns=rename)

    OUTPUT_GEOJSON.parent.mkdir(parents=True, exist_ok=True)
    ph.to_file(OUTPUT_GEOJSON, driver="GeoJSON")
    logger.info("Wrote %s (%d polygons)", OUTPUT_GEOJSON, len(ph))

    return 0


if __name__ == "__main__":
    sys.exit(main())
