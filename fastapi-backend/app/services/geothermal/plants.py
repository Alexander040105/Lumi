"""Philippines geothermal power plant data loader and proximity utilities.

Loads the Global Energy Monitor (GEM) geothermal power tracker dataset
for the Philippines and provides helpers to boost suitability scores
for municipalities near operating plants.
"""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Earth radius in km
R_EARTH_KM = 6371.0
# Default boost radius
DEFAULT_BOOST_RADIUS_KM = 25.0


# ---------------------------------------------------------------------------
# Cached in-memory plant list (loaded once at first access)
# ---------------------------------------------------------------------------
_plants: list[dict[str, Any]] | None = None


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance between two lat/lon points in kilometres."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R_EARTH_KM * c


def _load_plants() -> list[dict[str, Any]]:
    """Load the Philippines geothermal plant JSON once and cache it."""
    global _plants
    if _plants is not None:
        return _plants

    repo_root = Path(__file__).resolve().parents[4]
    json_path = (
        repo_root
        / "fastapi-backend"
        / "app"
        / "services"
        / "local_data"
        / "ph_geothermal_plants.json"
    )

    if not json_path.exists():
        logger.warning("Geothermal plant data not found at %s", json_path)
        _plants = []
        return _plants

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            _plants = json.load(f)
    except Exception as exc:
        logger.warning("Failed to load geothermal plant data: %s", exc)
        _plants = []

    return _plants


def get_all_ph_geothermal_plants() -> list[dict[str, Any]]:
    """Return the full list of Philippines geothermal power plants."""
    return _load_plants()


def get_operating_plants() -> list[dict[str, Any]]:
    """Return only plants with status == 'operating'."""
    return [p for p in _load_plants() if p.get("status") == "operating"]


def get_plants_near(
    lat: float,
    lon: float,
    radius_km: float = DEFAULT_BOOST_RADIUS_KM,
    only_operating: bool = True,
) -> list[dict[str, Any]]:
    """Return plants within *radius_km* of the given lat/lon.

    Each returned dict includes an extra key ``distance_km``.
    """
    plants = get_operating_plants() if only_operating else _load_plants()
    nearby = []
    for p in plants:
        d = _haversine(lat, lon, p["latitude"], p["longitude"])
        if d <= radius_km:
            entry = {**p, "distance_km": round(d, 2)}
            nearby.append(entry)
    # Sort by distance
    nearby.sort(key=lambda x: x["distance_km"])
    return nearby


def calculate_proximity_boost(
    lat: float,
    lon: float,
    base_score: float,
    radius_km: float = DEFAULT_BOOST_RADIUS_KM,
    max_bonus: float = 30.0,
) -> tuple[float, list[dict[str, Any]]]:
    """Boost a geothermal suitability score based on proximity to operating plants.

    The bonus is linearly tapered from *max_bonus* at 0 km down to 0 at *radius_km*.
    The final score is capped at 100.

    Returns:
        (boosted_score, nearby_plants)
    """
    nearby = get_plants_near(lat, lon, radius_km, only_operating=True)
    if not nearby:
        return base_score, []

    # Use the closest plant for the bonus calculation
    closest = nearby[0]
    distance = closest["distance_km"]

    # Linear taper: bonus = max_bonus * (1 - distance / radius_km)
    bonus = max_bonus * (1.0 - distance / radius_km)
    bonus = max(0.0, bonus)

    boosted = min(base_score + bonus, 100.0)
    return round(boosted, 2), nearby
