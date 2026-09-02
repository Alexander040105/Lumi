"""Scrape wind and hydro power plants from Wikipedia.

Usage:
    python scripts/ingest_wind_hydro_plants.py

Output:
    app/services/local_data/ph_wind_plants.json
    app/services/local_data/ph_hydro_plants.json
"""

from __future__ import annotations

import io
import json
import math
import re
from pathlib import Path

import pandas as pd
import requests

URL = "https://en.wikipedia.org/wiki/List_of_power_plants_in_the_Philippines"

# Provinces that are commonly listed as a single community with no comma.
# Used as a fallback to avoid treating a province as a city.
_PH_PROVINCES = {
    "catanduanes",
    "oriental mindoro",
    "occidental mindoro",
    "marinduque",
    "romblon",
    "siquijor",
    "biliran",
    "guimaras",
    "batanes",
    "camiguin",
    "dinagat islands",
    "lanao del sur",
    "lanao del norte",
    "surigao del sur",
    "surigao del norte",
    "sultan kudarat",
    "north cotabato",
    "south cotabato",
    "davao del sur",
    "davao del norte",
    "davao de oro",
    "davao oriental",
    "davao occidental",
    "cotabato",
    "basilan",
    "sulu",
    "tawi-tawi",
    "abra",
    "apayao",
    "benguet",
    "ifugao",
    "kalinga",
    "mountain province",
    "metro manila",
    "national capital region",
}


def _dms_to_decimal(degrees: int, minutes: int, seconds: float, direction: str) -> float:
    """Convert DMS (degrees/minutes/seconds) to decimal degrees."""
    decimal = degrees + minutes / 60.0 + seconds / 3600.0
    if direction in ("S", "W"):
        decimal = -decimal
    return decimal


def _extract_coordinates(coord_text: str | float) -> tuple[float | None, float | None]:
    """Parse Wikipedia-style coordinate strings into decimal lat/lon.

    Handles formats such as:
        18°30′58″N 120°38′46″E
        18.51611°N 120.64611°E
        13.7089° N, 124.2422° E
    """
    if not isinstance(coord_text, str) or not coord_text.strip():
        return None, None

    text = coord_text.strip().replace("﻿", "")  # remove zero-width chars

    # Decimal degrees with direction, possibly comma-separated
    m = re.search(
        r"([0-9.]+)\s*°?\s*([NS])[^0-9.,]+([0-9.]+)\s*°?\s*([EW])",
        text,
        re.IGNORECASE,
    )
    if m:
        lat = float(m.group(1))
        lon = float(m.group(3))
        if m.group(2).upper() == "S":
            lat = -lat
        if m.group(4).upper() == "W":
            lon = -lon
        return lat, lon

    # DMS: 18°30′58″N 120°38′46″E
    dms_pattern = (
        r"([0-9]+)\s*°\s*([0-9]+)\s*[′']\s*([0-9.]+)\s*[″\"]?\s*([NS])"
        r"\s+"
        r"([0-9]+)\s*°\s*([0-9]+)\s*[′']\s*([0-9.]+)\s*[″\"]?\s*([EW])"
    )
    m = re.search(dms_pattern, text, re.IGNORECASE)
    if m:
        lat = _dms_to_decimal(
            int(m.group(1)), int(m.group(2)), float(m.group(3)), m.group(4).upper()
        )
        lon = _dms_to_decimal(
            int(m.group(5)), int(m.group(6)), float(m.group(7)), m.group(8).upper()
        )
        return lat, lon

    return None, None


def _status_from_notes(raw_notes: str, has_commissioned_year: bool = False) -> str:
    """Map Wikipedia notes text to a normalized status."""
    text = ""
    if isinstance(raw_notes, str):
        text = raw_notes.lower()
    elif isinstance(raw_notes, (int, float)) and not math.isnan(raw_notes):
        text = str(int(raw_notes))

    if "operational" in text or "operating" in text:
        return "operating"
    if "under construction" in text:
        return "construction"
    if "proposed" in text:
        return "proposed"
    if any(x in text for x in ("cancelled", "shelved", "retired")):
        return "retired"

    # Hydro plants with a commissioning year and no negative note are treated
    # as operating because the table lists completed plants.
    if has_commissioned_year:
        return "operating"

    return "unknown"


def _parse_community(community: str) -> tuple[str | None, str | None]:
    """Split a Wikipedia community string into city and province."""
    if not isinstance(community, str) or not community.strip():
        return None, None
    text = community.strip()
    parts = [p.strip() for p in text.split(",")]
    if len(parts) >= 2:
        city = parts[0]
        province = parts[-1]
        return city, province

    # Single value: guess whether it is a province or a city.
    if parts[0].lower() in _PH_PROVINCES:
        return None, parts[0]

    # Heuristic: known province names that are sometimes listed alone.
    return parts[0], None


def _year(value) -> int | None:
    if isinstance(value, (int, float)):
        if not math.isnan(value):
            return int(value)
    if isinstance(value, str):
        digits = re.findall(r"\b(19\d{2}|20\d{2})\b", value)
        if digits:
            return int(digits[0])
    return None


def _capacity(value) -> float | None:
    if isinstance(value, (int, float)):
        if not math.isnan(value):
            return float(value)
    return None


def _extract_wiki_url(station_text: str) -> str | None:
    """Return the embedded wiki link from a station name if one exists."""
    if not isinstance(station_text, str):
        return None
    m = re.search(r"href=\"(/wiki/[^\"]+)\"", station_text)
    if m:
        return "https://en.wikipedia.org" + m.group(1)
    return None


def _clean_table(df: pd.DataFrame, energy_type: str) -> list[dict]:
    """Convert a Wikipedia table DataFrame to the standard plant schema."""
    records = []
    for _, row in df.iterrows():
        station = str(row.get("Station", "")) if pd.notna(row.get("Station")) else ""
        community = str(row.get("Community", "")) if pd.notna(row.get("Community")) else ""
        coords_raw = row.get("Coordinates")
        capacity_raw = row.get("Capacity (MW)") if "Capacity (MW)" in row.index else row.get("Capacity")
        commissioned = row.get("Commissioned") if "Commissioned" in row.index else None
        notes = row.get("Notes") if "Notes" in row.index else ""

        lat, lon = _extract_coordinates(coords_raw)
        city, province = _parse_community(community)

        start_year = _year(commissioned)

        # Build raw status from the available note/source columns.
        raw_status_parts: list[str] = []
        if isinstance(commissioned, str):
            raw_status_parts.append(commissioned)
        if isinstance(notes, str) and notes.strip():
            raw_status_parts.append(notes.strip())
        raw_status = "; ".join(raw_status_parts)

        status = _status_from_notes(raw_status, has_commissioned_year=start_year is not None)

        # Skip obviously empty rows.
        if not station.strip() or not (capacity_raw or community or start_year or lat or lon):
            continue

        records.append(
            {
                "project_name": station.strip() or None,
                "unit_name": None,
                "capacity_mw": _capacity(capacity_raw),
                "technology": energy_type,
                "status": status,
                "raw_status": raw_status.strip() if raw_status else "",
                "latitude": lat,
                "longitude": lon,
                "province": province,
                "city": city,
                "start_year": start_year,
                "wiki_url": _extract_wiki_url(station) or None,
            }
        )
    return records


def _find_tables(tables: list[pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Locate the hydro and wind tables from the list of DataFrames."""
    hydro_table: pd.DataFrame | None = None
    wind_table: pd.DataFrame | None = None

    for table in tables:
        cols = [str(c) for c in table.columns]
        if "Station" not in cols or "Community" not in cols:
            continue

        # The first cell often contains the energy type in the station name.
        first_station = str(table.iloc[0].get("Station", "")).lower()

        if "hydro" in first_station and hydro_table is None:
            hydro_table = table
        elif "wind" in first_station and wind_table is None:
            wind_table = table

    if hydro_table is None or wind_table is None:
        raise RuntimeError(
            f"Could not locate hydropower and wind tables. Found {len(tables)} tables."
        )

    return hydro_table, wind_table


def main():
    repo_root = Path(__file__).resolve().parents[2]
    out_dir = repo_root / "fastapi-backend" / "app" / "services" / "local_data"
    out_dir.mkdir(parents=True, exist_ok=True)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
        )
    }
    response = requests.get(URL, headers=headers, timeout=60)
    response.raise_for_status()

    tables = pd.read_html(io.StringIO(response.text))
    hydro_table, wind_table = _find_tables(tables)

    hydro_plants = _clean_table(hydro_table, "hydro")
    wind_plants = _clean_table(wind_table, "wind")

    (out_dir / "ph_hydro_plants.json").write_text(
        json.dumps(hydro_plants, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "ph_wind_plants.json").write_text(
        json.dumps(wind_plants, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Wrote {len(hydro_plants)} hydro plants to {out_dir / 'ph_hydro_plants.json'}")
    print(f"Wrote {len(wind_plants)} wind plants to {out_dir / 'ph_wind_plants.json'}")

    operating_hydro = sum(1 for p in hydro_plants if p["status"] == "operating")
    operating_wind = sum(1 for p in wind_plants if p["status"] == "operating")
    print(f"Operating hydro: {operating_hydro}")
    print(f"Operating wind: {operating_wind}")


if __name__ == "__main__":
    main()
