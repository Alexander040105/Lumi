"""Philippines hydro power plant data loader and proximity utilities.

Loads the Wikipedia list of hydropower plants for the Philippines
and provides helpers to boost hydro suitability scores for
municipalities or provinces near operating hydro plants.
"""

from __future__ import annotations

import json
import logging
import math
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

R_EARTH_KM = 6371.0
DEFAULT_BOOST_RADIUS_KM = 50.0
DEFAULT_MAX_BONUS = 25.0

_plants: list[dict[str, Any]] | None = None


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return the great-circle distance between two lat/lon points in km."""
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
    """Load the Philippines hydro plant JSON once and cache it."""
    global _plants
    if _plants is not None:
        return _plants

    module_dir = Path(__file__).resolve().parent  # app/services/
    repo_root = Path(__file__).resolve().parents[3]  # Lumi/
    candidates = [
        module_dir / "local_data" / "ph_hydro_plants.json",
        repo_root / "fastapi-backend" / "app" / "services" / "local_data" / "ph_hydro_plants.json",
        repo_root / "app" / "services" / "local_data" / "ph_hydro_plants.json",
    ]
    env_path = os.getenv("PH_HYDRO_PLANTS_PATH")
    if env_path:
        candidates.insert(0, Path(env_path))

    json_path = None
    for candidate in candidates:
        if candidate.exists():
            json_path = candidate
            break

    if not json_path:
        logger.warning("Hydro plant data not found at any of %s", [str(c) for c in candidates])
        _plants = []
        return _plants

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            _plants = json.load(f)
    except Exception as exc:
        logger.warning("Failed to load hydro plant data: %s", exc)
        _plants = []

    return _plants


def get_all_hydro_plants() -> list[dict[str, Any]]:
    """Return the full list of Philippines hydropower plants."""
    return _load_plants()


def get_operating_hydro_plants() -> list[dict[str, Any]]:
    """Return only plants with status == 'operating'."""
    return [p for p in _load_plants() if p.get("status") == "operating"]


def get_hydro_plants_near(
    lat: float,
    lon: float,
    radius_km: float = DEFAULT_BOOST_RADIUS_KM,
    only_operating: bool = True,
) -> list[dict[str, Any]]:
    """Return operating hydro plants within *radius_km* of the given point.

    Each returned dict includes an extra ``distance_km`` key.
    """
    plants = get_operating_hydro_plants() if only_operating else _load_plants()
    nearby = []
    for p in plants:
        p_lat = p.get("latitude")
        p_lon = p.get("longitude")
        if p_lat is None or p_lon is None:
            continue
        d = _haversine(lat, lon, float(p_lat), float(p_lon))
        if d <= radius_km:
            entry = {**p, "distance_km": round(d, 2)}
            nearby.append(entry)
    nearby.sort(key=lambda x: x["distance_km"])
    return nearby


def get_hydro_plants_in_province(
    province: str,
    only_operating: bool = True,
) -> list[dict[str, Any]]:
    """Return operating hydro plants whose province field matches the input."""
    province_norm = province.strip().lower() if province else ""
    if not province_norm:
        return []
    plants = get_operating_hydro_plants() if only_operating else _load_plants()
    matched = []
    for p in plants:
        p_province = (p.get("province") or "").strip().lower()
        if p_province == province_norm:
            matched.append(p)
    return matched


def calculate_hydro_proximity_boost(
    lat: float | None,
    lon: float | None,
    base_score: float,
    province: str | None = None,
    radius_km: float = DEFAULT_BOOST_RADIUS_KM,
    max_bonus: float = DEFAULT_MAX_BONUS,
    province_bonus_fraction: float = 0.5,
) -> tuple[float, list[dict[str, Any]]]:
    """Boost a hydro suitability score based on nearby operating hydro plants.

    The bonus is linearly tapered from *max_bonus* at 0 km to 0 at *radius_km*.
    The larger default radius reflects that hydro resources are watershed-scale.
    If no lat/lon is provided, a province match applies a reduced bonus.
    The final score is capped at 100.

    Returns:
        (boosted_score, nearby_plants)
    """
    nearby: list[dict[str, Any]] = []

    if lat is not None and lon is not None:
        nearby = get_hydro_plants_near(float(lat), float(lon), radius_km, only_operating=True)

    if not nearby and province:
        nearby = get_hydro_plants_in_province(province, only_operating=True)
        if nearby:
            bonus = max_bonus * province_bonus_fraction
            boosted = min(base_score + bonus, 100.0)
            return round(boosted, 2), nearby

    if not nearby:
        return base_score, []

    closest = nearby[0]
    distance = closest["distance_km"]
    bonus = max_bonus * (1.0 - distance / radius_km)
    bonus = max(0.0, bonus)
    boosted = min(base_score + bonus, 100.0)
    return round(boosted, 2), nearby


def calculate_hydro_generation_scale(
    lat: float | None,
    lon: float | None,
    province: str | None = None,
    radius_km: float = DEFAULT_BOOST_RADIUS_KM,
    scale_factor: float = 0.4,
    max_scale: float = 2.0,
) -> tuple[float, list[dict[str, Any]]]:
    """Return a multiplier for household hydro output based on nearby operating hydro plants.

    The multiplier uses the total capacity (MW) of nearby operating plants and a
    log-scaled boost so that very large plants do not completely dominate. The
    larger default scale factor for hydro reflects that a utility hydro plant
    validates a persistent watershed, which is a strong signal for micro-hydro
    feasibility. It is capped at *max_scale*. If no lat/lon is provided, a
    province match is used.

    Returns:
        (scale, nearby_plants)
    """
    nearby: list[dict[str, Any]] = []

    if lat is not None and lon is not None:
        nearby = get_hydro_plants_near(float(lat), float(lon), radius_km, only_operating=True)

    if not nearby and province:
        nearby = get_hydro_plants_in_province(province, only_operating=True)

    if not nearby:
        return 1.0, []

    total_capacity = sum(float(p.get("capacity_mw") or 0.0) for p in nearby)
    scale = 1.0 + scale_factor * math.log1p(total_capacity / 100.0)
    scale = min(scale, max_scale)
    return round(scale, 3), nearby
