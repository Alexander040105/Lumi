"""Extract volcano and fault KMZ raster overlays for EnergyHub map.

The KMZ files contain GroundOverlay PNG images (not vector data).
This script extracts the PNG images and writes a JSON manifest with
LatLonBox bounds so the frontend can render them as Leaflet image overlays.

Usage (from repo root with .venv activated):
    python fastapi-backend/scripts/extract_kmz_to_geojson.py

Reads:
    data/GeothermalDatasets/VOL_2016_000000000_02.kmz  (volcanoes)
    data/GeothermalDatasets/aft_2025_000000000_02.kmz   (faults)

Outputs:
    react-frontend/public/geothermal_overlays.json
    react-frontend/public/geothermal_volcanoes.png
    react-frontend/public/geothermal_faults.png
"""
from __future__ import annotations

import json
import logging
import shutil
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = REPO_ROOT / "data" / "GeothermalDatasets"
OUTPUT_DIR = REPO_ROOT / "react-frontend" / "public"

KML_NS = "http://www.opengis.net/kml/2.2"


def extract_overlay_manifest(kmz_path: Path, kind: str) -> dict | None:
    """Extract PNG + bounds from a raster GroundOverlay KMZ.

    Returns a dict with:
        png_filename: str
        bounds: {"north", "south", "east", "west"}
    """
    if not kmz_path.exists():
        logger.error("KMZ file not found: %s", kmz_path)
        return None

    try:
        with zipfile.ZipFile(kmz_path, "r") as zf:
            kml_names = [n for n in zf.namelist() if n.lower().endswith(".kml")]
            if not kml_names:
                logger.error("No .kml file inside %s", kmz_path)
                return None

            # Parse KML for LatLonBox bounds
            with zf.open(kml_names[0]) as kml_file:
                kml_text = kml_file.read().decode("utf-8")
                root = ET.fromstring(kml_text.encode("utf-8"))

            # Find the first LatLonBox (GroundOverlay bounds)
            latlonbox = root.find(f".//{{{KML_NS}}}LatLonBox")
            if latlonbox is None:
                # Fallback: try LatLonAltBox
                latlonbox = root.find(f".//{{{KML_NS}}}LatLonAltBox")
            if latlonbox is None:
                logger.error("No LatLonBox found in %s", kmz_path)
                return None

            def _text(tag: str) -> str | None:
                el = latlonbox.find(f"{{{KML_NS}}}{tag}") if latlonbox is not None else None
                return el.text if el is not None else None

            north = _text("north")
            south = _text("south")
            east = _text("east")
            west = _text("west")
            if not all([north, south, east, west]):
                logger.error("Incomplete LatLonBox in %s", kmz_path)
                return None

            bounds = {
                "north": float(north),
                "south": float(south),
                "east": float(east),
                "west": float(west),
            }

            # Find the PNG href in the first GroundOverlay
            icon_href = None
            for overlay in root.iter(f"{{{KML_NS}}}GroundOverlay"):
                icon = overlay.find(f".//{{{KML_NS}}}Icon/{{{KML_NS}}}href")
                if icon is not None and icon.text:
                    icon_href = icon.text
                    break

            if not icon_href:
                logger.error("No GroundOverlay icon href found in %s", kmz_path)
                return None

            # Extract PNG to public dir
            png_members = [n for n in zf.namelist() if n.lower().endswith(".png")]
            if not png_members:
                logger.error("No PNG found inside %s", kmz_path)
                return None

            # Use the first PNG that matches or just the first PNG
            png_name = png_members[0]
            out_png = OUTPUT_DIR / f"geothermal_{kind}.png"
            with zf.open(png_name) as src, open(out_png, "wb") as dst:
                shutil.copyfileobj(src, dst)
            logger.info("Extracted %s -> %s", png_name, out_png)

            return {
                "png_filename": out_png.name,
                "bounds": bounds,
                "kind": kind,
            }
    except Exception as exc:
        logger.error("Failed to process %s: %s", kmz_path, exc)
        return None


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {}

    # --- Volcanoes ---
    vol = extract_overlay_manifest(INPUT_DIR / "VOL_2016_000000000_02.kmz", "volcanoes")
    if vol:
        manifest["volcanoes"] = vol

    # --- Faults ---
    fault = extract_overlay_manifest(INPUT_DIR / "aft_2025_000000000_02.kmz", "faults")
    if fault:
        manifest["faults"] = fault

    # Write manifest JSON
    manifest_path = OUTPUT_DIR / "geothermal_overlays.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info("Wrote overlay manifest to %s", manifest_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
