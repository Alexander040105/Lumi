"""Map API routes for LUMI GIS/mapping.

Provides:
- /map/{renewable_type} — suitability map data (scores + centroids)
- /map/psgc/hierarchy — PSGC administrative hierarchy
- /map/coverage — data coverage summary
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.services.map_service import (
    get_coverage_summary,
    get_map_data,
    get_psgc_hierarchy,
)

router = APIRouter()


def _normalize_level(level: str | None) -> str:
    """Strip trailing IDs (e.g. 'municipality:1') and validate the level."""
    normalized = (level or "municipality").split(":")[0].lower().strip()
    return normalized if normalized in {"municipality", "province"} else "municipality"


@router.get("/psgc/hierarchy")
async def psgc_hierarchy(
    municipality_id: int | None = Query(default=None),
    province_id: int | None = Query(default=None),
) -> dict[str, Any]:
    """Fetch PSGC administrative hierarchy.

    Provide either municipality_id or province_id to get the full
    administrative chain (region → province → municipality → barangays).
    """
    if not municipality_id and not province_id:
        return {
            "error": "Provide either municipality_id or province_id"
        }

    hierarchy = get_psgc_hierarchy(
        municipality_id=municipality_id,
        province_id=province_id,
    )
    return hierarchy


@router.get("/coverage")
async def coverage_summary(
    level: str = Query(
        default="municipality",
        description="Geographic level: municipality or province",
    ),
) -> dict[str, Any]:
    """Return data coverage summary for a given admin level.

    Shows how many geographic units have climate data, suitability scores, etc.
    """
    return get_coverage_summary(level=_normalize_level(level))


@router.get("/{renewable_type}")
async def get_suitability_map(
    renewable_type: str,
    level: str = Query(
        default="municipality",
        description="Geographic level: municipality or province",
    ),
    use_cache: bool = Query(default=True),
) -> dict[str, Any]:
    """Return suitability map data for a renewable type.

    Returns a list of geographic units with their suitability scores
    and centroid coordinates, suitable for choropleth map rendering.
    """
    valid_types = {"solar", "wind", "hydro", "geothermal"}
    if renewable_type not in valid_types:
        return {
            "error": f"Invalid renewable_type '{renewable_type}'. Must be one of: {', '.join(valid_types)}"
        }

    normalized_level = _normalize_level(level)
    data = get_map_data(renewable_type, level=normalized_level, use_cache=use_cache)
    return {
        "renewable_type": renewable_type,
        "level": normalized_level,
        "count": len(data),
        "items": data,
    }
