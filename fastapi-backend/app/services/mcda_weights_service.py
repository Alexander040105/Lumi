"""MCDA weights loader.

Fetches AHP-derived criterion weights from Supabase and exposes them
as a simple dict for the scoring modules.

If the database table is unavailable or empty, falls back to hard-coded
defaults so the scoring pipeline never breaks.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_WEIGHTS: dict[str, dict[str, float]] = {
    "geothermal": {
        "heat_flow": 0.30,
        "fault": 0.15,
        "volcano": 0.10,
        "aquifer": 0.15,
        "temperature": 0.10,
    },
    "solar": {
        "irradiance": 0.40,
        "temperature": 0.20,
        "cloud_cover": 0.20,
        "terrain_slope": 0.10,
        "land_use": 0.10,
    },
    "wind": {
        "wind_speed": 0.40,
        "terrain_roughness": 0.20,
        "elevation": 0.20,
        "land_use": 0.10,
        "air_density": 0.10,
    },
    "hydro": {
        "rainfall": 0.30,
        "watershed_slope": 0.25,
        "catchment_area": 0.25,
        "hydraulic_head": 0.20,
    },
}

_weights_cache: dict[str, dict[str, float]] | None = None


def load_mcda_weights(client=None) -> dict[str, dict[str, float]]:
    """Fetch active MCDA weights from Supabase or return defaults.

    Args:
        client: Optional Supabase client. If None, a new client is created.

    Returns:
        Dict mapping energy_type -> {criterion: weight}
    """
    global _weights_cache

    if _weights_cache is not None:
        return _weights_cache

    try:
        if client is None:
            from app.services.supabase_service import get_supabase_client
            client = get_supabase_client()

        resp = (
            client.table("mcda_weights")
            .select("energy_type, criterion, weight")
            .eq("is_active", True)
            .execute()
        )
        rows = resp.data or []

        weights: dict[str, dict[str, float]] = {}
        for r in rows:
            etype = r.get("energy_type")
            crit = r.get("criterion")
            w = r.get("weight")
            if etype and crit and w is not None:
                weights.setdefault(etype, {})[crit] = float(w)

        if weights:
            logger.info("Loaded MCDA weights from DB for %s energy types", len(weights))
            _weights_cache = weights
            return weights
    except Exception as exc:
        logger.warning("Failed to load MCDA weights from DB: %s. Using defaults.", exc)

    _weights_cache = _DEFAULT_WEIGHTS
    return _DEFAULT_WEIGHTS


def get_weights(energy_type: str, client=None) -> dict[str, float]:
    """Return weights for a specific energy type.

    Args:
        energy_type: e.g. 'geothermal', 'solar', 'wind', 'hydro'
        client: Optional Supabase client.

    Returns:
        Dict mapping criterion -> weight. Falls back to defaults.
    """
    all_weights = load_mcda_weights(client)
    return all_weights.get(energy_type, _DEFAULT_WEIGHTS.get(energy_type, {}))


def invalidate_weights_cache() -> None:
    """Clear the in-memory weights cache (call after admin updates)."""
    global _weights_cache
    _weights_cache = None
    logger.info("MCDA weights cache invalidated")
