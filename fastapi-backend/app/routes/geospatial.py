"""Geospatial API routes for centroid and climate data.

Provides endpoints for:
- /geospatial/centroids — bulk centroid lookup by admin level
- /geospatial/centroids/{level}/{geo_id} — single unit centroid
- /geospatial/climate — climate data by geographic level and ID
- /geospatial/climate/hierarchy — climate with automatic fallback
"""
from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.services.geospatial_service import (
    get_all_centroids,
    get_centroid_with_fallback,
    get_geospatial_metadata,
)
from app.services.climate_service import (
    get_climate_data,
    get_climate_with_fallback,
    get_or_compute_province_climate,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class CentroidItem(BaseModel):
    geo_id: int
    name: str | None = None
    centroid_lat: float
    centroid_lon: float
    area_km2: float | None = None
    elevation_m: float | None = None


class CentroidListResponse(BaseModel):
    level: str
    items: list[CentroidItem]


class CentroidResponse(BaseModel):
    level: str
    geo_id: int
    centroid_lat: float | None = None
    centroid_lon: float | None = None
    area_km2: float | None = None
    elevation_m: float | None = None
    source: str | None = None


class ClimateRecord(BaseModel):
    month: int
    year: int
    t2m: float | None = None
    t2m_max: float | None = None
    t2m_min: float | None = None
    rh2m: float | None = None
    prectotcorr: float | None = None
    ws10m: float | None = None
    allsky_sfc_sw_dwn: float | None = None
    cloud_amt: float | None = None
    surface_pressure: float | None = None
    elevation: float | None = None


class ClimateResponse(BaseModel):
    level: str
    geo_id: int
    year: int | None = None
    source: str | None = None
    records: list[dict]


class ClimateFallbackResponse(BaseModel):
    requested_level: str
    actual_level: str
    geo_id: int
    year: int | None = None
    records: list[dict]


# ---------------------------------------------------------------------------
# Centroid endpoints
# ---------------------------------------------------------------------------

@router.get("/centroids", response_model=CentroidListResponse)
async def get_centroids(
    level: str = Query(
        default="province",
        description="Geographic level: region, province, municipality, or barangay",
    ),
):
    """Return all centroids for a given administrative level.

    Data is sourced from geospatial_metadata table with Redis caching.
    """
    items = get_all_centroids(level)
    return {"level": level, "items": items}


@router.get("/centroids/{level}/{geo_id}", response_model=CentroidResponse)
async def get_single_centroid(
    level: str,
    geo_id: int,
):
    """Return centroid metadata for a single administrative unit.

    Falls back to lat/lon columns in the admin table if geospatial_metadata
    has no entry.
    """
    meta = get_geospatial_metadata(level, geo_id)
    if meta:
        return {
            "level": level,
            "geo_id": geo_id,
            "centroid_lat": meta.get("centroid_lat"),
            "centroid_lon": meta.get("centroid_lon"),
            "area_km2": meta.get("area_km2"),
            "elevation_m": meta.get("elevation_m"),
            "source": meta.get("source", "geospatial_metadata"),
        }

    # Fallback to admin table lat/lon
    centroid = get_centroid_with_fallback(level, geo_id)
    if centroid:
        return {
            "level": level,
            "geo_id": geo_id,
            "centroid_lat": centroid[0],
            "centroid_lon": centroid[1],
            "area_km2": None,
            "elevation_m": None,
            "source": "admin_table_fallback",
        }

    return {
        "level": level,
        "geo_id": geo_id,
        "centroid_lat": None,
        "centroid_lon": None,
        "area_km2": None,
        "elevation_m": None,
        "source": None,
    }


# ---------------------------------------------------------------------------
# Climate endpoints
# ---------------------------------------------------------------------------

@router.get("/climate", response_model=ClimateResponse)
async def get_climate(
    level: str = Query(
        default="municipality",
        description="Geographic level: province, municipality, or barangay",
    ),
    geo_id: int = Query(..., description="Geographic unit ID"),
    year: int | None = Query(default=None, description="Year filter (e.g., 2024). Returns all years if omitted."),
):
    """Return monthly climate data for a geographic unit at a specific level.

    Data is sourced from the level-specific climate table:
    - province → province_climate_monthly
    - municipality → municipality_climate_monthly
    - barangay → barangay_climate_monthly
    """
    records = get_climate_data(level, geo_id, year)
    return {
        "level": level,
        "geo_id": geo_id,
        "year": year,
        "source": f"{level}_climate_monthly",
        "records": records,
    }


@router.get("/climate/hierarchy", response_model=ClimateFallbackResponse)
async def get_climate_hierarchy(
    barangay_id: int | None = Query(default=None, description="Barangay ID"),
    municipality_id: int | None = Query(default=None, description="Municipality ID"),
    province_id: int | None = Query(default=None, description="Province ID"),
    year: int | None = Query(default=None, description="Year filter"),
):
    """Return climate data with automatic fallback through the geographic hierarchy.

    Tries barangay → municipality → province resolution.
    Returns the actual level used and the climate records.
    """
    actual_level, actual_geo_id, records = get_climate_with_fallback(
        barangay_id=barangay_id,
        municipality_id=municipality_id,
        province_id=province_id,
        year=year,
    )
    requested = "barangay" if barangay_id else ("municipality" if municipality_id else "province")
    return {
        "requested_level": requested,
        "actual_level": actual_level,
        "geo_id": actual_geo_id,
        "year": year,
        "records": records,
    }


@router.get("/climate/province-aggregate", response_model=ClimateResponse)
async def get_province_climate_aggregate(
    province_id: int = Query(..., description="Province ID"),
    year: int = Query(..., description="Year"),
):
    """Return province climate data, aggregating from municipalities if needed.

    If province_climate_monthly has no data for the given province/year,
    this endpoint computes averages from all municipalities in the province.
    """
    records = get_or_compute_province_climate(province_id, year)
    return {
        "level": "province",
        "geo_id": province_id,
        "year": year,
        "source": "province_climate_monthly_or_aggregated",
        "records": records,
    }
