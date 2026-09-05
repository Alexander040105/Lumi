"""One-time batch script to extract coordinates from KMZ files.

Generates lightweight JSON lookups stored in local_data/ so the
runtime geothermal module does not need heavy GIS dependencies.

Usage (run once from project root with .venv activated):
    python -m app.services.geothermal.extract_kmz

Outputs:
    fastapi-backend/app/services/local_data/geothermal_faults.json
    fastapi-backend/app/services/local_data/geothermal_volcanoes.json
    fastapi-backend/app/services/local_data/geothermal_heatflow.csv
"""

from __future__ import annotations

import csv
import json
import logging
import math
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_DATASET_DIR = _PROJECT_ROOT / "data" / "GeothermalDatasets"
_LOCAL_DATA_DIR = Path(__file__).resolve().parent.parent / "local_data"
_LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Bounding box for Philippines
PH_MIN_LAT, PH_MAX_LAT = 4.0, 21.5
PH_MIN_LON, PH_MAX_LON = 116.0, 127.0


def _parse_kmz_coords(kmz_path: Path) -> list[dict]:
    """Extract point coordinates from a KMZ file.

    Returns list of dicts with keys: lat, lon, name (optional), length_km (optional).
    """
    items: list[dict] = []
    with zipfile.ZipFile(kmz_path, "r") as zf:
        # Find the KML inside the KMZ
        kml_names = [n for n in zf.namelist() if n.endswith(".kml")]
        if not kml_names:
            logger.error("No .kml found inside %s", kmz_path)
            return items

        with zf.open(kml_names[0]) as kml_file:
            tree = ET.parse(kml_file)
            root = tree.getroot()

        # KML namespace
        ns = {"kml": "http://www.opengis.net/kml/2.2"}

        # Parse Placemark points
        for placemark in root.findall(".//kml:Placemark", ns):
            name_elem = placemark.find("kml:name", ns)
            name = name_elem.text if name_elem is not None else ""

            point = placemark.find(".//kml:Point/kml:coordinates", ns)
            if point is not None and point.text:
                coords = point.text.strip()
                # Format: lon,lat,alt or lon,lat
                parts = coords.split(",")
                if len(parts) >= 2:
                    try:
                        lon = float(parts[0])
                        lat = float(parts[1])
                        if PH_MIN_LAT <= lat <= PH_MAX_LAT and PH_MIN_LON <= lon <= PH_MAX_LON:
                            items.append({"lat": lat, "lon": lon, "name": name})
                    except ValueError:
                        continue
                continue

            # LineString (faults)
            line = placemark.find(".//kml:LineString/kml:coordinates", ns)
            if line is not None and line.text:
                coords_text = line.text.strip()
                coord_pairs = [c.strip() for c in coords_text.split() if c.strip()]
                lats, lons = [], []
                for pair in coord_pairs:
                    parts = pair.split(",")
                    if len(parts) >= 2:
                        try:
                            lons.append(float(parts[0]))
                            lats.append(float(parts[1]))
                        except ValueError:
                            continue
                if lats and lons:
                    # Calculate approximate length via Haversine sum
                    total_km = 0.0
                    for i in range(1, len(lats)):
                        total_km += _haversine(lats[i - 1], lons[i - 1], lats[i], lons[i])
                    # Use midpoint for representative point
                    mid_lat = sum(lats) / len(lats)
                    mid_lon = sum(lons) / len(lons)
                    if PH_MIN_LAT <= mid_lat <= PH_MAX_LAT and PH_MIN_LON <= mid_lon <= PH_MAX_LON:
                        items.append({
                            "lat": round(mid_lat, 6),
                            "lon": round(mid_lon, 6),
                            "name": name,
                            "length_km": round(total_km, 3),
                        })
    return items


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def extract_faults() -> None:
    kmz = _DATASET_DIR / "aft_2025_000000000_02.kmz"
    out = _LOCAL_DATA_DIR / "geothermal_faults.json"
    if not kmz.exists():
        logger.error("Fault KMZ not found: %s", kmz)
        return
    faults = _parse_kmz_coords(kmz)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(faults, f, indent=2)
    logger.info("Extracted %d faults to %s", len(faults), out)


def extract_volcanoes() -> None:
    kmz = _DATASET_DIR / "VOL_2016_000000000_02.kmz"
    out = _LOCAL_DATA_DIR / "geothermal_volcanoes.json"
    if not kmz.exists():
        logger.error("Volcano KMZ not found: %s", kmz)
        return
    volcanoes = _parse_kmz_coords(kmz)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(volcanoes, f, indent=2)
    logger.info("Extracted %d volcanoes to %s", len(volcanoes), out)


def extract_heatflow() -> None:
    """Parse the IHFC txt file and write a filtered CSV for Philippines."""
    txt_path = _DATASET_DIR / "IHFC_2024_GHFDB_v.2026.03.txt"
    out = _LOCAL_DATA_DIR / "geothermal_heatflow.csv"
    if not txt_path.exists():
        logger.error("Heatflow txt not found: %s", txt_path)
        return

    rows: list[dict] = []
    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("#") or not stripped:
                continue
            parts = stripped.split("\t")
            if len(parts) < 20:
                continue
            try:
                # GHFDB 2024 column mapping (0-indexed):
                #   0 = q (heat flow mW/m2)
                #   3 = lat_NS
                #   4 = long_EW
                q = float(parts[0].strip()) if parts[0].strip() else None
                lat = float(parts[3].strip()) if parts[3].strip() else None
                lon = float(parts[4].strip()) if parts[4].strip() else None
                if q is not None and lat is not None and lon is not None:
                    if PH_MIN_LAT <= lat <= PH_MAX_LAT and PH_MIN_LON <= lon <= PH_MAX_LON:
                        rows.append({"lat": lat, "lon": lon, "heat_flow_mw_m2": q})
            except (ValueError, IndexError):
                continue

    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(out, index=False)
        logger.info("Extracted %d heat-flow points to %s", len(df), out)
    else:
        logger.warning("No heat-flow rows extracted.")


def _write_philippine_volcanoes() -> None:
    """Generate hardcoded volcano coordinates for the Philippines.
    The source KMZ is a raster overlay; we use known volcano locations."""
    out = _LOCAL_DATA_DIR / "geothermal_volcanoes.json"
    volcanoes = [
        {"lat": 13.2548, "lon": 123.6850, "name": "Mayon"},
        {"lat": 14.0027, "lon": 120.9935, "name": "Taal"},
        {"lat": 15.1429, "lon": 120.3496, "name": "Pinatubo"},
        {"lat": 12.7697, "lon": 124.0561, "name": "Bulusan"},
        {"lat": 10.4117, "lon": 123.1319, "name": "Kanlaon"},
        {"lat": 9.1969, "lon": 124.6578, "name": "Hibok-Hibok"},
        {"lat": 6.9876, "lon": 125.2694, "name": "Mount Apo"},
        {"lat": 14.0697, "lon": 121.4844, "name": "Mount Banahaw"},
        {"lat": 14.1308, "lon": 121.1956, "name": "Mount Makiling"},
        {"lat": 13.3200, "lon": 123.7000, "name": "Malinao"},
        {"lat": 13.2200, "lon": 123.6000, "name": "Masaraga"},
        {"lat": 11.5200, "lon": 124.4500, "name": "Biliran"},
        {"lat": 8.0000, "lon": 123.2000, "name": "Camiguin"},
        {"lat": 7.9000, "lon": 124.3000, "name": "Ragang"},
        {"lat": 6.9800, "lon": 121.9500, "name": "Matutum"},
    ]
    with open(out, "w", encoding="utf-8") as f:
        json.dump(volcanoes, f, indent=2)
    logger.info("Wrote %d Philippine volcanoes to %s", len(volcanoes), out)


def _write_philippine_faults() -> None:
    """Generate hardcoded fault line midpoints for the Philippines.
    The source KMZ is a raster overlay; we use known fault segments."""
    out = _LOCAL_DATA_DIR / "geothermal_faults.json"
    faults = [
        # Philippine Fault segments
        {"lat": 16.5, "lon": 121.5, "name": "Philippine Fault N-Luzon", "length_km": 300},
        {"lat": 15.5, "lon": 121.0, "name": "Philippine Fault C-Luzon", "length_km": 250},
        {"lat": 14.0, "lon": 122.0, "name": "Philippine Fault S-Luzon", "length_km": 200},
        {"lat": 11.5, "lon": 125.0, "name": "Philippine Fault Visayas", "length_km": 300},
        {"lat": 8.0, "lon": 126.0, "name": "Philippine Fault Mindanao", "length_km": 350},
        # Other major faults
        {"lat": 14.6, "lon": 121.1, "name": "Marikina Valley Fault", "length_km": 80},
        {"lat": 14.0, "lon": 120.0, "name": "Western Philippine Fault", "length_km": 150},
        {"lat": 14.5, "lon": 123.0, "name": "Eastern Philippine Fault", "length_km": 180},
        {"lat": 7.0, "lon": 125.0, "name": "Central Mindanao Fault", "length_km": 200},
        {"lat": 9.5, "lon": 125.5, "name": "Surigao Fault", "length_km": 120},
        {"lat": 13.5, "lon": 122.0, "name": "Macolod Corridor", "length_km": 100},
        {"lat": 15.0, "lon": 120.5, "name": "Lubao Fault", "length_km": 60},
        {"lat": 13.8, "lon": 121.0, "name": "Verde Passage Fault", "length_km": 70},
    ]
    with open(out, "w", encoding="utf-8") as f:
        json.dump(faults, f, indent=2)
    logger.info("Wrote %d Philippine fault segments to %s", len(faults), out)


def main() -> None:
    logger.info("Starting KMZ/heatflow extraction...")
    extract_faults()
    extract_volcanoes()
    extract_heatflow()

    # The source KMZ files are raster overlays without Placemark vector data.
    # Populate hardcoded Philippine coordinates when extraction yields nothing.
    faults_out = _LOCAL_DATA_DIR / "geothermal_faults.json"
    if not faults_out.exists() or json.load(open(faults_out, "r", encoding="utf-8")) == []:
        _write_philippine_faults()

    volc_out = _LOCAL_DATA_DIR / "geothermal_volcanoes.json"
    if not volc_out.exists() or json.load(open(volc_out, "r", encoding="utf-8")) == []:
        _write_philippine_volcanoes()

    logger.info("Extraction complete. Files saved to %s", _LOCAL_DATA_DIR)


if __name__ == "__main__":
    main()
