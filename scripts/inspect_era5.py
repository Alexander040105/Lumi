"""Inspect the ERA5 GRIB file and write a metadata summary.

Usage (from repo root, with .venv activated):
    .venv\\Scripts\\python.exe scripts/inspect_era5.py
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import cfgrib

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

GRIB_PATH = (
    Path(__file__).resolve().parents[1]
    / "newDataPointsToExtract"
    / "ERA5_copernicusData.grib"
)
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "scripts" / "gap_output"


def main() -> int:
    if not GRIB_PATH.exists():
        logger.error("GRIB not found: %s", GRIB_PATH)
        return 1

    logger.info("Opening %s with cfgrib...", GRIB_PATH)
    try:
        # cfgrib.open_datasets splits the grib into one xarray Dataset per hypercube.
        dss = cfgrib.open_datasets(str(GRIB_PATH))
    except Exception as exc:
        logger.error("Could not open GRIB: %s", exc)
        return 1

    logger.info("Found %d dataset(s)", len(dss))
    summary: list[dict] = []
    for i, ds in enumerate(dss):
        logger.info("Dataset %d dimensions: %s", i, dict(ds.dims))
        logger.info("Dataset %d coordinates: %s", list(ds.coords))

        vars_info: list[dict] = []
        for name, var in ds.data_vars.items():
            info: dict = {
                "name": name,
                "dims": list(var.dims),
                "shape": list(var.shape),
                "attrs": {k: str(v) for k, v in var.attrs.items()},
            }
            logger.info(
                "  var=%s dims=%s shape=%s attrs=%s",
                name,
                info["dims"],
                info["shape"],
                info["attrs"],
            )
            vars_info.append(info)

        summary.append(
            {
                "dataset_index": i,
                "dims": dict(ds.dims),
                "coords": {c: str(ds.coords[c].values[:5].tolist()) if ds.coords[c].size > 5 else str(ds.coords[c].values.tolist()) for c in ds.coords},
                "data_vars": vars_info,
                "attrs": {k: str(v) for k, v in ds.attrs.items()},
            }
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "era5_metadata.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    logger.info("Wrote metadata to %s", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
