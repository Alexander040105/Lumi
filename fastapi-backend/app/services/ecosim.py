import calendar
import datetime as dt
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import HTTPException, status
from postgrest.exceptions import APIError
from app.schemas.ecosim import PostHouse
from app.services.data_cache import cache_get_sync, cache_set_sync
from app.services.supabase_service import get_supabase_client
from app.services.redis_client import (
    _ECOSIM_TTL,
    get_ecosim_cache_sync,
    set_ecosim_cache_sync,
)
from app.config.settings import get_settings
from app.services.solar_output_calc import (
    calculate_temperature_factor,
    calculate_performance_ratio,
    solar_calc,
    solar_calc_pvout,
    solar_calc_advanced,
    calculate_dust_loss_from_wind,
    calculate_degradation_from_humidity,
)
from app.services.hydro_output_calc import calculate_hydropower, estimated_flow_rate
from app.services.wind_output_calc import load_wind_averages, calculate_wind_output, extrapolate_wind_speed
from app.services.atlas_data import (
    get_atlas_for_municipality,
    get_atlas_for_municipality_ids,
    get_atlas_for_province,
    get_era5_for_municipality,
    get_era5_for_province,
)
from app.services.catchment_data import get_catchment_for_municipality
from app.services.geothermal.features import (
    compute_geothermal_suitability,
    compute_geothermal_output,
)
from app.services.geothermal.plants import (
    calculate_proximity_boost,
    get_plants_near,
)
from app.services.wind_plants import (
    calculate_wind_proximity_boost,
    calculate_wind_generation_scale,
    get_wind_plants_near,
)
from app.services.hydro_plants import (
    calculate_hydro_proximity_boost,
    calculate_hydro_generation_scale,
    calculate_hydro_plant_floor,
    get_hydro_plants_near,
)
from app.services.financials import FinancialInputs, analyze_financials, to_dict as financials_to_dict
from app.services.confidence import ConfidenceFactors, calculate_confidence
logger = logging.getLogger(__name__)
_LOCAL_DATA_DIR = Path(__file__).resolve().parent / "local_data"
_CLIMATE_CSV = _LOCAL_DATA_DIR / "municipality_climate_averages.csv"
_climate_df: pd.DataFrame | None = None


def _load_climate_csv() -> pd.DataFrame | None:
    """Load the bundled climate CSV as an emergency fallback."""
    global _climate_df
    if _climate_df is not None:
        return _climate_df
    if not _CLIMATE_CSV.exists():
        return None
    _climate_df = pd.read_csv(str(_CLIMATE_CSV))
    return _climate_df


def _get_climate_for_municipality(municipality_id: int) -> list[dict[str, Any]]:
    """Load climate averages for a single municipality from Supabase or local CSV."""
    cache_key = f"climate:municipality:{municipality_id}"
    cached = cache_get_sync(cache_key)
    if cached is not None:
        return cached

    client = get_supabase_client()
    try:
        resp = (
            client.table("municipality_climate_averages")
            .select("*")
            .eq("municipality_id", municipality_id)
            .execute()
        )
        rows = resp.data or []
        if rows:
            cache_set_sync(cache_key, rows, ttl=86400)
            return rows
    except Exception as exc:
        logger.warning(
            "Failed to load climate for municipality %s from Supabase: %s",
            municipality_id,
            exc,
        )

    df = _load_climate_csv()
    if df is not None:
        rows = df[df["municipality_id"] == municipality_id].to_dict(orient="records")
        if rows:
            cache_set_sync(cache_key, rows, ttl=86400)
            return rows

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No climate average data found for this municipality.",
    )


def _get_climate_for_municipality_ids(municipality_ids: list[int]) -> list[dict[str, Any]]:
    """Load climate averages for a list of municipality IDs from Supabase or local CSV."""
    if not municipality_ids:
        return []

    client = get_supabase_client()
    try:
        rows: list[dict] = []
        for i in range(0, len(municipality_ids), 500):
            chunk = municipality_ids[i : i + 500]
            resp = (
                client.table("municipality_climate_averages")
                .select("*")
                .in_("municipality_id", chunk)
                .execute()
            )
            rows.extend(resp.data or [])
        if rows:
            return rows
    except Exception as exc:
        logger.warning(
            "Failed to load climate for municipality ids from Supabase: %s", exc
        )

    df = _load_climate_csv()
    if df is not None:
        return df[df["municipality_id"].isin(municipality_ids)].to_dict(orient="records")

    return []

COST_PER_KW_SOLAR = 60000.0
COST_PER_KW_WIND = 80000.0
COST_PER_KW_HYDRO = 100000.0
# Geothermal installation cost derived from BOI Green Lane Certificate projects
# (Jan 2024) reported by the Philippine Board of Investments:
#   - Daklan (51 MW):  P6.66 B  -> ~130,588 PHP/kW
#   - Mt. Labo (105 MW): P7.58 B  -> ~72,190 PHP/kW
#   - Mt. Malinao (50 MW): P5.03 B  -> ~100,600 PHP/kW
# Average of the three full-project costs ≈ 101,000 PHP/kW.
# Source: BOI, "BOI grants Green Lane Certificates for new Geothermal Projects
# in the Philippines" (Jan 2024); Manila Bulletin, "P244 B worth of RE investments
# granted green lane processing" (Feb 2024).
# URL: https://boi.gov.ph/boi-grants-green-lane-certificates-for-new-geothermal-projects-in-the-philippines/
COST_PER_KW_GEOTHERMAL = 100000.0
# Philippines DOE 2019–2021 National Grid Emission Factor (Luzon–Visayas grid).
# Official Operating Margin EF = 0.6835 kg CO2 / kWh (DOE, 2022).
# See: ecosim_economic_formula_references.md
CO2_KG_PER_KWH = 0.6835
GEOTHERMAL_CITATION = (
    "Based on IHFC heat-flow measurements, Zenodo aquifer properties, "
    "the Global Energy Monitor (GEM) Philippines geothermal tracker, "
    "and NASA POWER temperature."
)


def get_municipality_terrain_data(
    municipality: str, municipality_id: int | None = None
) -> dict | None:
    """
    Fetches pre-computed terrain metrics for a municipality.
    Returns None if unavailable so callers can degrade gracefully.

    Expected table: municipality_terrain_metrics
    Columns used:
    hydraulic_head_m, runoff_potential, gravity_flow_potential,
    watershed_gradient, terrain_ruggedness, hydro_suitability_score,
    estimated_hydropower_potential_kw, mean_slope_deg, elevation_range_m
    """
    client = get_supabase_client()
    try:
        query = client.table("hydropower_suitability").select()
        if municipality_id is not None:
            query = query.eq("municipality_id", municipality_id)
        else:
            query = query.eq("municipality_name", municipality.upper())
        result = query.single().execute()
        return result.data or None
    except APIError:
        return None  # terrain data is optional; degrade gracefully

def get_municipality_data(
    municipality: str, municipality_id: int | None = None, source: str = "auto"
):
    """Return climate data for a municipality, optionally enriched with atlas data.

    If municipality_id is provided, only the province lookup uses the
    municipalities table; climate data is still fetched directly.
    """
    client = get_supabase_client()

    if municipality_id is None:
        try:
            municipality_result = (
                client
                .table("municipalities")
                .select("municipality_id,name,lat,lon,province_id")
                .eq("name", municipality.upper())
                .limit(1)
                .single()
                .execute()
            )
        except APIError as exc:
            error = getattr(exc, "args", [{}])[0]
            if isinstance(error, dict) and error.get("code") == "PGRST116":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Municipality not found",
                )
            raise

        if not municipality_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Municipality not found",
            )

        municipality_id = municipality_result.data["municipality_id"]
        municipality_name = municipality_result.data.get("name", municipality).upper()
        province_id = municipality_result.data.get("province_id")
    else:
        municipality_name = municipality.upper()

    municipality_data = _get_climate_for_municipality(municipality_id)

    if not municipality_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No climate average data found for this municipality.",
        )

    # Avoid mutating the cached climate row.
    municipality_data = [municipality_data[0].copy()]

    municipality_data[0]["municipality_id"] = municipality_id
    municipality_data[0]["name"] = municipality_name

    # Merge Global Solar Atlas / Global Wind Atlas values unless NASA-only is requested.
    source = source.lower()
    if source in ("auto", "atlas"):
        atlas = get_atlas_for_municipality(municipality_id)
        if atlas:
            municipality_data[0].update(atlas)
            municipality_data[0]["data_source"] = atlas.get("data_source", "Global Solar Atlas / Global Wind Atlas")
        elif source == "atlas":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Atlas data not available for this municipality.",
            )

    if source == "era5" or (source == "auto" and "wind_speed_100m_ms" not in municipality_data[0]):
        # ERA5 only has 10m wind in this file; use it when explicitly requested or as an auto fallback.
        era5 = get_era5_for_municipality(municipality_id)
        if era5:
            # Capture the pre-existing source and strip the generic one from the ERA5 row.
            previous_source = municipality_data[0].get("data_source", "NASA POWER")
            era5.pop("data_source", None)
            municipality_data[0].update(era5)
            # Only re-label the source when ERA5 is explicitly requested.
            if source == "era5":
                municipality_data[0]["data_source"] = (
                    f"ERA5 (wind, 10m) + {previous_source}"
                    if "era5_wind_speed_10m_ms" in municipality_data[0]
                    else previous_source
                )
        elif source == "era5" or (source == "auto" and "wind_speed_100m_ms" not in municipality_data[0]):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ERA5 data not available for this municipality.",
            )

    return municipality_data


def list_municipalities() -> list[dict]:
    cache_key = "lumi:ecosim:municipalities"
    cached = cache_get_sync(cache_key)
    if cached is not None:
        return cached

    client = get_supabase_client()
    items = []
    batch_size = 1000
    offset = 0
    try:
        while True:
            result = (
                client
                .table("municipalities")
                .select("municipality_id,name,province_id")
                .order("name")
                .range(offset, offset + batch_size - 1)
                .execute()
            )
            batch = result.data or []
            items.extend(batch)
            if len(batch) < batch_size:
                break
            offset += batch_size
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict):
            message = error.get("message") or "Failed to load municipalities"
        else:
            message = "Failed to load municipalities"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=message,
        )

    # Build province_id → province_name map from cached province list
    province_map = {p["province_id"]: p["name"] for p in list_provinces()}

    output = sorted(
        (
            {
                "municipality_id": item.get("municipality_id"),
                "name": item.get("name"),
                "province_name": province_map.get(item.get("province_id")),
            }
            for item in items
            if item.get("municipality_id") and item.get("name")
        ),
        key=lambda item: item["name"].upper(),
    )
    cache_set_sync(cache_key, output, ttl=86400)
    return output


def list_provinces() -> list[dict]:
    cache_key = "lumi:ecosim:provinces"
    cached = cache_get_sync(cache_key)
    if cached is not None:
        return cached

    client = get_supabase_client()
    try:
        result = (
            client
            .table("provinces")
            .select("province_id,name")
            .order("name")
            .limit(1000)
            .execute()
        )
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict):
            message = error.get("message") or "Failed to load provinces"
        else:
            message = "Failed to load provinces"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=message,
        )

    items = result.data or []
    output = sorted(
        (
            {
                "province_id": item.get("province_id"),
                "name": item.get("name"),
            }
            for item in items
            if item.get("province_id") and item.get("name")
        ),
        key=lambda item: item["name"].upper(),
    )
    cache_set_sync(cache_key, output, ttl=86400)
    return output


def list_barangays(municipality_id: int | None = None) -> list[dict]:
    """List barangays, optionally filtered by municipality_id."""
    cache_key = f"lumi:ecosim:barangays:{municipality_id or 'all'}"
    cached = cache_get_sync(cache_key)
    if cached is not None:
        return cached

    client = get_supabase_client()
    try:
        query = (
            client.table("barangays")
            .select("barangay_id,name,municipality_id")
            .order("name")
            .limit(50000)
        )
        if municipality_id is not None:
            query = query.eq("municipality_id", str(municipality_id))
        result = query.execute()
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict):
            message = error.get("message") or "Failed to load barangays"
        else:
            message = "Failed to load barangays"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=message,
        )

    items = result.data or []
    output = sorted(
        (
            {
                "barangay_id": item.get("barangay_id"),
                "name": item.get("name"),
                "municipality_id": item.get("municipality_id"),
            }
            for item in items
            if item.get("barangay_id") and item.get("name")
        ),
        key=lambda item: item["name"].upper(),
    )
    cache_set_sync(cache_key, output, ttl=86400)
    return output


def _compute_municipality_wind_output_kwh(municipality_data: dict) -> float:
    """Compute monthly wind output (kWh) for a single municipality record.

    Mirrors the wind speed selection and output calculation used in
    renewable_energy_calculator so province aggregation can collect
    per-municipality outputs rather than computing output from an averaged
    wind speed.
    """
    settings = get_settings()
    hub_height = float(settings.household_wind_hub_height_m)
    alpha = float(settings.wind_shear_exponent)
    wind_rotor_radius = settings.household_wind_rotor_radius_m
    wind_cp = settings.household_wind_power_coefficient

    wind_speed_50m = (
        municipality_data.get("wind_speed_50m_ms")
        or municipality_data.get("muni_avg_wind_speed_50m_ms")
    )
    if wind_speed_50m and float(wind_speed_50m) > 0:
        wind_speed = extrapolate_wind_speed(
            float(wind_speed_50m), 50.0, hub_height, alpha
        )
    else:
        wind_speed_10m = (
            municipality_data.get("wind_speed_10m_ms")
            or municipality_data.get("era5_wind_speed_10m_ms")
            or municipality_data.get("avg_ws10m")
            or 0.0
        )
        wind_speed = extrapolate_wind_speed(
            float(wind_speed_10m), 10.0, hub_height, alpha
        )

    if wind_speed <= 0:
        return 0.0

    air_density = municipality_data.get("avg_rhoa")
    if air_density is None:
        air_density = 1.225

    days_in_month = calendar.monthrange(dt.datetime.now().year, dt.datetime.now().month)[1]
    try:
        output = calculate_wind_output(
            wind_speed_mps=wind_speed,
            days_in_month=days_in_month,
            air_density=air_density,
            rotor_radius_m=wind_rotor_radius,
            cp=wind_cp,
        )
        return float(output.get("monthly_energy_kwh") or 0.0)
    except Exception:
        return 0.0


def _median(values: list[float]) -> float:
    """Return the median of a list of floats."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0
    return sorted_vals[mid]


def get_province_data(province_name: str, source: str = "auto") -> dict:
    """Aggregate municipality climate data for a province.

    Returns a dict with the same structure as a single municipality record
    so it can be used interchangeably in renewable_energy_calculator.
    When source is 'atlas' or 'auto', Global Solar/Wind Atlas values are used.
    """
    client = get_supabase_client()
    try:
        prov_resp = (
            client.table("provinces")
            .select("province_id,name,lat,lon")
            .ilike("name", province_name.upper())
            .single()
            .execute()
        )
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict) and error.get("code") == "PGRST116":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Province not found",
            )
        raise

    if not prov_resp.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Province not found",
        )

    province_id = prov_resp.data["province_id"]
    province_name = prov_resp.data.get("name", province_name).upper()
    province_lat = prov_resp.data.get("lat")
    province_lon = prov_resp.data.get("lon")

    # Fetch all municipalities in this province
    muni_resp = (
        client.table("municipalities")
        .select("municipality_id,name,lat,lon")
        .eq("province_id", province_id)
        .limit(20000)
        .execute()
    )
    muni_rows = muni_resp.data or []
    municipality_ids = [m["municipality_id"] for m in muni_rows if m.get("municipality_id")]

    if not municipality_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No municipalities found for this province.",
        )

    # Aggregate climate data
    climate_rows = _get_climate_for_municipality_ids(municipality_ids)
    if not climate_rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No climate average data found for this province.",
        )

    province_df = pd.DataFrame(climate_rows)
    numeric_cols = [
        "avg_t2m", "avg_t2m_max", "avg_t2m_min", "avg_rh2m",
        "avg_prectotcorr", "avg_ws10m", "avg_allsky_sfc_sw_dwn",
        "avg_cloud_amt", "avg_surface_pressure", "avg_rhoa", "elevation",
    ]

    aggregated = {
        "municipality_id": province_id,
        "name": province_name.upper(),
        "province_id": province_id,
        "province": province_name.upper(),
    }
    for col in numeric_cols:
        if col in province_df.columns:
            aggregated[col] = round(float(province_df[col].mean()), 2)
        else:
            aggregated[col] = None

    # Terrain aggregation (optional, from hydropower_suitability)
    try:
        terrain_resp = (
            client.table("hydropower_suitability")
            .select("hydraulic_head_m,runoff_potential,watershed_gradient,mean_slope_deg,gravity_flow_potential")
            .in_("municipality_id", municipality_ids)
            .execute()
        )
        terrain_rows = terrain_resp.data or []
        if terrain_rows:
            terrain = {}
            for key in ["hydraulic_head_m", "runoff_potential", "watershed_gradient", "mean_slope_deg", "gravity_flow_potential"]:
                vals = [r[key] for r in terrain_rows if r.get(key) is not None]
                terrain[key] = round(sum(vals) / len(vals), 2) if vals else 0.0
            aggregated["terrain"] = terrain
    except Exception:
        aggregated["terrain"] = None

    # Catchment enrichment aggregation (Boothroyd et al. 2023)
    # Aggregate enrichment data across all municipalities in the province.
    try:
        from app.services.catchment_data import get_catchment_for_municipality_ids
        enrichment_map = get_catchment_for_municipality_ids(municipality_ids)
        if enrichment_map:
            enrichment_rows = list(enrichment_map.values())
            numeric_fields = [
                "effective_catchment_area_km2",
                "stream_head_m",
                "stream_feasibility_penalty",
                "enriched_runoff_coefficient",
                "catchment_area_km2",
                "catchment_mean_slope_deg",
                "distance_to_nearest_stream_m",
                "nearest_stream_gradient_m_m",
            ]
            agg_enrichment = {}
            for field in numeric_fields:
                vals = [float(r[field]) for r in enrichment_rows if r.get(field) is not None]
                if vals:
                    agg_enrichment[field] = round(sum(vals) / len(vals), 4)

            # Use the most common catchment name
            catchment_names = [r.get("catchment_name") for r in enrichment_rows if r.get("catchment_name")]
            if catchment_names:
                from collections import Counter
                agg_enrichment["catchment_name"] = Counter(catchment_names).most_common(1)[0][0]

            # Aggregate stream feasibility as the median (not mean) to avoid
            # a few far-away municipalities dragging down the whole province
            penalties = [float(r["stream_feasibility_penalty"]) for r in enrichment_rows if r.get("stream_feasibility_penalty") is not None]
            if penalties:
                penalties.sort()
                mid = len(penalties) // 2
                agg_enrichment["stream_feasibility_penalty"] = penalties[mid]

            if agg_enrichment:
                aggregated["catchment_enrichment"] = agg_enrichment
        else:
            logger.debug("Catchment enrichment: no entries found for province %s", province_id)
    except Exception as exc:
        logger.debug("Catchment enrichment aggregation failed: %s", exc)

    # Prefer Global Solar Atlas / Global Wind Atlas for province aggregation when available.
    source = source.lower()
    if source in ("auto", "atlas"):
        province_atlas = get_atlas_for_province(province_id)
        if province_atlas:
            aggregated.update(province_atlas)
            aggregated["data_source"] = province_atlas.get("data_source", "Global Solar Atlas / Global Wind Atlas")
        elif source == "atlas":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Atlas data not available for this province.",
            )

    if source == "era5" or (source == "auto" and "wind_speed_100m_ms" not in aggregated):
        province_era5 = get_era5_for_province(province_id)
        if province_era5:
            previous_source = aggregated.get("data_source", "NASA POWER")
            province_era5.pop("data_source", None)
            aggregated.update(province_era5)
            if source == "era5":
                aggregated["data_source"] = (
                    f"ERA5 (wind, 10m) + {previous_source}"
                    if "era5_wind_speed_10m_ms" in aggregated
                    else previous_source
                )
        elif source == "era5" or (source == "auto" and "wind_speed_100m_ms" not in aggregated):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ERA5 data not available for this province.",
            )

    # Province wind aggregation: compute wind output for each municipality
    # and take the median. Wind power is cubic in speed, so a single
    # averaged wind speed overestimates/underestimates the typical household
    # output. Using the median of municipality outputs reduces outlier
    # influence (e.g. one large, windy municipality dominating a province).
    try:
        muni_atlas_map = get_atlas_for_municipality_ids(municipality_ids)
        climate_map = {row.get("municipality_id"): row for row in climate_rows if row.get("municipality_id")}
        wind_outputs = []
        for mid in municipality_ids:
            muni_data = {}
            if mid in climate_map:
                muni_data.update(climate_map[mid])
            if mid in muni_atlas_map:
                muni_data.update(muni_atlas_map[mid])
            if muni_data:
                output = _compute_municipality_wind_output_kwh(muni_data)
                if output > 0:
                    wind_outputs.append(output)

        if wind_outputs:
            wind_outputs.sort()
            aggregated["muni_mean_wind_output_kwh"] = round(sum(wind_outputs) / len(wind_outputs), 4)
            aggregated["muni_median_wind_output_kwh"] = round(_median(wind_outputs), 4)
            aggregated["muni_wind_output_count"] = len(wind_outputs)
    except Exception as exc:
        logger.debug("Could not aggregate municipality wind outputs for province %s: %s", province_id, exc)

    return aggregated


def get_geothermal_data(municipality_name: str, municipality_data: dict) -> dict:
    """
    Fetch pre-computed geothermal output from Supabase.
    Falls back to on-the-fly estimation if pre-computed row is missing.
    """
    client = get_supabase_client()
    mid = municipality_data.get("municipality_id")
    try:
        output_result = (
            client
            .table("geothermal_output")
            .select("*")
            .eq("municipality_id", mid)
            .single()
            .execute()
        )
        if output_result.data:
            data = output_result.data
            # Fetch true geothermal suitability score and classification
            geo_score = 0.0
            classification = "Unknown"
            try:
                suit_result = (
                    client
                    .table("geothermal_suitability")
                    .select("geothermal_score,classification")
                    .eq("municipality_id", mid)
                    .single()
                    .execute()
                )
                if suit_result.data:
                    geo_score = suit_result.data.get("geothermal_score") or 0.0
                    classification = suit_result.data.get("classification", "Unknown")
            except APIError:
                pass
            assumption = data.get("assumption", "") or GEOTHERMAL_CITATION
            return {
                "energy_type": "geothermal",
                "suitability_score": round(geo_score * 100, 2),
                "classification": classification,
                "reservoir_temperature_c": data.get("reservoir_temperature_c"),
                "thermal_power_mw": data.get("thermal_power_mw"),
                "electric_power_mw": data.get("electric_power_mw"),
                "annual_energy_gwh": data.get("annual_energy_gwh"),
                "confidence": data.get("confidence_score"),
                "source": data.get("source", "Supabase pre-computed"),
                "assumption": assumption,
                "citation": GEOTHERMAL_CITATION,
                "source_type": "utility",
            }
    except APIError:
        pass

    # Fallback: compute on-the-fly using NASA POWER surface temp
    surface_temp = municipality_data.get("avg_t2m")
    lat = municipality_data.get("lat")
    lon = municipality_data.get("lon")

    if lat is None or lon is None:
        return {
            "energy_type": "geothermal",
            "suitability_score": 0.0,
            "thermal_power_mw": None,
            "electric_power_mw": None,
            "annual_energy_gwh": None,
            "confidence": 0.0,
            "source": "Fallback on-the-fly estimation",
            "assumption": "Pre-computed data unavailable; using measured NASA POWER temperature and inferred aquifer/heatflow.",
            "citation": GEOTHERMAL_CITATION,
            "source_type": "utility",
        }

    suitability = compute_geothermal_suitability(lat, lon, surface_temp, municipality_id=mid)
    output = compute_geothermal_output(
        surface_temp,
        suitability.get("_gradient_c_km"),
        suitability.get("aquifer_score"),
        suitability.get("_perm_log10"),
    )

    return {
        "energy_type": "geothermal",
        "suitability_score": round(suitability.get("geothermal_score", 0) * 100, 2),
        "classification": suitability.get("classification", "Unknown"),
        "reservoir_temperature_c": output.get("reservoir_temperature_c"),
        "thermal_power_mw": output.get("thermal_power_mw"),
        "electric_power_mw": output.get("electric_power_mw"),
        "annual_energy_gwh": output.get("annual_energy_gwh"),
        "confidence": output.get("confidence_score"),
        "source": output.get("source"),
        "assumption": output.get("assumption") or GEOTHERMAL_CITATION,
        "citation": GEOTHERMAL_CITATION,
        "source_type": "utility",
    }


def get_municipality_name_by_id(municipality_id: int) -> str:
    client = get_supabase_client()
    try:
        municipality_result = (
            client
            .table("municipalities")
            .select("name")
            .eq("municipality_id", municipality_id)
            .single()
            .execute()
        )
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict) and error.get("code") == "PGRST116":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Municipality not found",
            )
        raise

    if not municipality_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Municipality not found",
        )

    return municipality_result.data["name"]


def get_province_name_by_id(province_id: int) -> str:
    client = get_supabase_client()
    try:
        result = (
            client
            .table("provinces")
            .select("name")
            .eq("province_id", province_id)
            .single()
            .execute()
        )
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict) and error.get("code") == "PGRST116":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Province not found",
            )
        raise

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Province not found",
        )

    return result.data["name"]


def consumption_calculator(current_electricity_bill: float, electricity_rate: float, desired_savings: float):
    monthly_consumption_kwh = current_electricity_bill / electricity_rate
    today = dt.datetime.now()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    daily_consumption_kwh = monthly_consumption_kwh / days_in_month
    target_monthly_consumption_kwh = monthly_consumption_kwh * (1 - desired_savings)
    return {
        "monthly_consumption_kwh": monthly_consumption_kwh,
        "daily_consumption_kwh": daily_consumption_kwh,
        "target_monthly_consumption_kwh": target_monthly_consumption_kwh
    }
    
    
# | LUMI Variable      | NASA POWER Column       | Use Case                          |
# | ------------------ | ----------------------- | --------------------------------- |
# | `solar_irradiance` | `avg_allsky_sfc_sw_dwn` | Solar energy calculations         |
# | `wind_speed`       | `avg_ws10m`             | Wind energy calculations          |
# | `rainfall`         | `avg_prectotcorr`       | Hydropower suitability            |
# | `temperature`      | `avg_t2m`               | Solar efficiency adjustments      |
# | `humidity`         | `avg_rh2m`              | Environmental/climate scoring     |
# | `cloud_cover`      | `avg_cloud_amt`         | Solar suitability penalties       |
# | `surface_pressure` | `avg_surface_pressure`  | Advanced wind analysis (optional) |



def renewable_energy_calculator(
    house: str,
    municipality: str,
    current_electricity_bill: float,
    electricity_rate: float,
    desired_savings: float,
    include_ai: bool = False,
    use_rag: bool = False,
    rag_query: str | None = None,
    nearby_geo_plants: list[dict[str, Any]] | None = None,
    mode: str = "municipality",
    municipality_id: int | None = None,
    data_source: str = "auto",
    use_cache: bool = True,
) -> dict:
    # NOTE: Data fetching
    if mode == "province":
        municipality_data = get_province_data(municipality, source=data_source)
        municipality_results = [municipality_data]
        terrain_data = municipality_data.get("terrain")
    else:
        municipality_results = get_municipality_data(
            municipality, municipality_id=municipality_id, source=data_source
        )
        municipality_data = municipality_results[0]
        terrain_data = get_municipality_terrain_data(
            municipality, municipality_id=municipality_id
        )

    # Try Redis cache for the full EcoSim result
    geo_id = municipality_data.get("municipality_id")
    params_hash: str | None = None
    if use_cache and geo_id:
        _s = get_settings()
        cache_payload = {
            "house": house,
            "municipality": municipality,
            "mode": mode,
            "current_electricity_bill": current_electricity_bill,
            "electricity_rate": electricity_rate,
            "desired_savings": desired_savings,
            "include_ai": include_ai,
            "use_rag": use_rag,
            "rag_query": rag_query,
            "data_source": data_source,
            "household_solar_size_kwp": _s.household_solar_size_kwp,
            "household_wind_hub_height_m": _s.household_wind_hub_height_m,
            "wind_shear_exponent": _s.wind_shear_exponent,
            "household_wind_rated_power_kw": _s.household_wind_rated_power_kw,
            "household_wind_rotor_radius_m": _s.household_wind_rotor_radius_m,
            "household_wind_capacity_factor": _s.household_wind_capacity_factor,
            "household_hydro_head_factor": _s.household_hydro_head_factor,
            "household_hydro_catchment_km2": _s.household_hydro_catchment_km2,
            "household_hydro_design_flow_factor": _s.household_hydro_design_flow_factor,
            "household_hydro_max_head_m": _s.household_hydro_max_head_m,
            "household_hydro_turbine_efficiency": _s.household_hydro_turbine_efficiency,
            "household_hydro_generator_efficiency": _s.household_hydro_generator_efficiency,
            "catchment_enrichment_enabled": _s.catchment_enrichment_enabled,
            "catchment_enrichment_version": _s.catchment_enrichment_version,
            "wind_plants_boost_enabled": _s.wind_plants_boost_enabled,
            "wind_plants_boost_radius_km": _s.wind_plants_boost_radius_km,
            "wind_plants_max_bonus": _s.wind_plants_max_bonus,
            "wind_plants_generation_scale_factor": _s.wind_plants_generation_scale_factor,
            "wind_plants_max_generation_scale": _s.wind_plants_max_generation_scale,
            "hydro_plants_boost_enabled": _s.hydro_plants_boost_enabled,
            "hydro_plants_boost_radius_km": _s.hydro_plants_boost_radius_km,
            "hydro_plants_max_bonus": _s.hydro_plants_max_bonus,
            "hydro_plants_generation_scale_factor": _s.hydro_plants_generation_scale_factor,
            "hydro_plants_max_generation_scale": _s.hydro_plants_max_generation_scale,
            "wind_hydro_plant_boost_mode": _s.wind_hydro_plant_boost_mode,
            "hydro_plant_floor_enabled": _s.hydro_plant_floor_enabled,
            "hydro_plant_floor_factor": _s.hydro_plant_floor_factor,
            "hydro_plant_max_floor_kwh": _s.hydro_plant_max_floor_kwh,
            "hydro_plant_absolute_cap_kwh": _s.hydro_plant_absolute_cap_kwh,
            "hydro_plant_floor_provinces_hash": hashlib.md5(
                ",".join(sorted(p.lower() for p in _s.hydro_plant_floor_provinces)).encode("utf-8")
            ).hexdigest()[:8],
            "scoring_version": "v5",  # v5: hydro plant output floor
        }
        params_hash = hashlib.md5(
            json.dumps(cache_payload, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()[:24]
        cached = get_ecosim_cache_sync("municipality", geo_id, params_hash)
        if cached:
            logger.info("EcoSim cache hit for %s (geo_id=%s)", municipality, geo_id)
            return cached

    consumption_results = consumption_calculator(
        current_electricity_bill,
        electricity_rate,
        desired_savings,
    )
    # Prefer atlas values when they were merged into municipality_data; otherwise use NASA POWER.
    solar_irradiance = municipality_data.get("solar_ghi_kwh_m2_day") or municipality_data.get("avg_allsky_sfc_sw_dwn") or 0.0
    avg_temp = municipality_data.get("solar_temp_c") or municipality_data.get("avg_t2m")
    cloud_amt = municipality_data.get("avg_cloud_amt")
    rainfall = municipality_data.get("avg_prectotcorr")
    # Load settings early — needed for wind hub height and hydro parameters.
    settings = get_settings()
    # Wind speed: use Global Wind Atlas 50m data, extrapolate to household hub
    # height via the 1/7 power law (NREL Philippines Wind Atlas methodology).
    # Fallback chain: atlas 50m → atlas 10m → ERA5 10m → NASA POWER 10m.
    hub_height = float(settings.household_wind_hub_height_m)
    alpha = float(settings.wind_shear_exponent)
    wind_speed_50m = (
        municipality_data.get("wind_speed_50m_ms")
        or municipality_data.get("muni_avg_wind_speed_50m_ms")
    )
    wind_speed_source_height_m = 50
    if wind_speed_50m and float(wind_speed_50m) > 0:
        wind_speed = extrapolate_wind_speed(
            float(wind_speed_50m), 50.0, hub_height, alpha
        )
    else:
        # Fallback: extrapolate from 10m wind speed
        wind_speed_10m = (
            municipality_data.get("wind_speed_10m_ms")
            or municipality_data.get("era5_wind_speed_10m_ms")
            or municipality_data.get("avg_ws10m")
            or 0.0
        )
        wind_speed = extrapolate_wind_speed(
            float(wind_speed_10m), 10.0, hub_height, alpha
        )
        wind_speed_source_height_m = 10
    humidity = municipality_data.get("avg_rh2m")
    surface_pressure = municipality_data.get("avg_surface_pressure")
    air_density = municipality_data.get("avg_rhoa")
    elevation = municipality_data.get("elevation") or municipality_data.get("avg_elevation")
    pvout_annual = municipality_data.get("solar_pvout_annual_kwh_kwp")
    today = dt.datetime.now()
    days_in_month = calendar.monthrange(today.year, today.month)[1]

    # NOTE: SOLAR CALCULATIONS:
    # NOTE: this default config is estimated based on typical residential solar panel setups and can be adjusted in the future for more customization or to reflect different market conditions. It is currently hardcoded for simplicity and to provide a baseline for calculations.
    household_solar_size_kwp = float(settings.household_solar_size_kwp)
    solar_panel_default_config = {
        "panel_wattage": 400,
        "system_efficiency": 0.80,
        "temp_coeff_per_c": -0.004,
        "dust_loss": 0.97,
        "inverter_efficiency": 0.96,
        "mismatch_loss": 0.98,
        "wiring_loss": 0.98,
        "degradation_loss": 0.99,
    }
    number_of_panels = max(
        round((household_solar_size_kwp * 1000.0) / solar_panel_default_config["panel_wattage"]),
        1,
    )
    solar_panel_default_config["number_of_panels"] = number_of_panels
    temperature_factor = calculate_temperature_factor(
        avg_temp_c=avg_temp,
        temp_coeff_per_c=solar_panel_default_config["temp_coeff_per_c"],
    )
    performance_ratio = calculate_performance_ratio(
        system_efficiency=solar_panel_default_config["system_efficiency"],
        temperature_factor=temperature_factor,
        dust_loss=calculate_dust_loss_from_wind(ws10m=wind_speed, base_dust_loss=solar_panel_default_config["dust_loss"]),
        inverter_efficiency=solar_panel_default_config["inverter_efficiency"],
        mismatch_loss=solar_panel_default_config["mismatch_loss"],
        wiring_loss=solar_panel_default_config["wiring_loss"],
        degradation_loss=calculate_degradation_from_humidity(rh2m=humidity, base_degradation=solar_panel_default_config["degradation_loss"]),
    )
    latitude = municipality_data.get("centroid_lat") or municipality_data.get("lat") or 14.0
    panel_tilt_deg = municipality_data.get("solar_optimal_tilt_deg") or 15.0
    panel_azimuth_deg = 180.0

    if pvout_annual:
        # Global Solar Atlas PVOUT already includes all system losses.
        solar_output = solar_calc_pvout(
            panel_wattage=solar_panel_default_config["panel_wattage"],
            number_of_panels=number_of_panels,
            pvout_annual_kwh_kwp=pvout_annual,
            days_in_month=days_in_month,
        )
    elif municipality_data.get("solar_dni_kwh_m2_day") and municipality_data.get("solar_dif_kwh_m2_day"):
        solar_output = solar_calc_advanced(
            panel_wattage=solar_panel_default_config["panel_wattage"],
            number_of_panels=number_of_panels,
            ghi_kwh_m2_day=solar_irradiance,
            dni_kwh_m2_day=municipality_data.get("solar_dni_kwh_m2_day"),
            dhi_kwh_m2_day=municipality_data.get("solar_dif_kwh_m2_day"),
            avg_temp_c=avg_temp,
            rh2m=humidity,
            ws10m=wind_speed,
            prectotcorr_mm=rainfall,
            surface_pressure_pa=surface_pressure,
            panel_tilt_deg=panel_tilt_deg,
            panel_azimuth_deg=panel_azimuth_deg,
            latitude_deg=latitude,
            days_in_month=days_in_month,
        )
    else:
        solar_output = solar_calc(
            panel_wattage=solar_panel_default_config["panel_wattage"],
            number_of_panels=number_of_panels,
            solar_irradiance=solar_irradiance,
            performance_ratio=performance_ratio,
            days_in_month=days_in_month,
        )
    solar_output["annual_solar_output"] = (solar_output.get("monthly_solar_output") or 0.0) * 12.0

    # NOTE: HYDRO CALCULATIONS
    # Catchment enrichment overlay (Boothroyd et al. 2023, PMC9994713).
    # When enrichment data is available, replace fixed assumptions with
    # real catchment morphology and nearest-stream data.
    catchment_enrichment = None
    if settings.catchment_enrichment_enabled:
        # In province mode, use pre-aggregated enrichment from municipality_data.
        # In municipality mode, look up by municipality_id.
        if mode == "province" and municipality_data.get("catchment_enrichment"):
            catchment_enrichment = municipality_data["catchment_enrichment"]
        elif geo_id:
            try:
                catchment_enrichment = get_catchment_for_municipality(int(geo_id))
            except Exception as exc:
                logger.debug("Catchment enrichment lookup failed for %s: %s", geo_id, exc)

    if catchment_enrichment:
        # Use real catchment area (household fraction) instead of fixed 1.0 km².
        # Recompute at runtime so settings.household_hydro_catchment_fraction and
        # household_hydro_catchment_km2 can be tuned without rebuilding the CSV.
        catchment_area = catchment_enrichment.get("catchment_area_km2")
        if catchment_area is not None:
            catchment_area_km2 = min(
                float(catchment_area) * float(settings.household_hydro_catchment_fraction),
                float(settings.household_hydro_catchment_km2),
            )
        else:
            catchment_area_km2 = float(settings.household_hydro_catchment_km2)

        # Use stream-gradient-derived head instead of DEM-derived municipal head
        stream_head = catchment_enrichment.get("stream_head_m")
        if stream_head is not None and float(stream_head) > 0:
            hydraulic_head_m = float(stream_head)
            head_already_realistic = True
        else:
            hydraulic_head_m = terrain_data.get("hydraulic_head_m") if terrain_data else 0.0
            head_already_realistic = False

        # Compute gravity flow potential from stream gradient when available.
        # The stream gradient (m/m) directly indicates whether gravity-fed
        # hydropower is feasible — a steeper stream means more head per unit
        # penstock length. This is more accurate than the municipal terrain
        # average, which dilutes mountainous terrain with flat lowlands.
        stream_penalty = catchment_enrichment.get("stream_feasibility_penalty")
        stream_gradient = catchment_enrichment.get("nearest_stream_gradient_m_m")
        if stream_gradient is not None and float(stream_gradient) > 0:
            # Map stream gradient to a 0-1 gravity flow potential:
            # 0.00 m/m (flat) → 0.0
            # 0.02 m/m (2% grade) → 0.4
            # 0.05 m/m (5% grade) → 0.7
            # 0.10+ m/m (10% grade) → 1.0
            # NOTE: The stream feasibility penalty is NOT applied here — it is
            # applied once on the final energy output in calculate_hydropower.
            # Applying it here AND there would double-count the penalty.
            grad = float(stream_gradient)
            gravity_flow_potential = min(grad / 0.10, 1.0)
        elif stream_penalty is not None:
            base_gravity = terrain_data.get("gravity_flow_potential") if terrain_data else 0.0
            gravity_flow_potential = float(base_gravity)
        else:
            gravity_flow_potential = terrain_data.get("gravity_flow_potential") if terrain_data else 0.0

        # Use enriched runoff coefficient (refined by drainage density + hypsometric)
        enriched_rc = catchment_enrichment.get("enriched_runoff_coefficient")
        runoff_coeff_override = float(enriched_rc) if enriched_rc is not None else None

        flow_rate_cms = estimated_flow_rate(
            rainfall_mm_monthly=rainfall,
            runoff_potential=terrain_data.get("runoff_potential") if terrain_data else 0.0,
            watershed_gradient=terrain_data.get("watershed_gradient") if terrain_data else 0.0,
            mean_slope_deg=terrain_data.get("mean_slope_deg") if terrain_data else 0.0,
            gravity_flow_potential=gravity_flow_potential,
            catchment_area_km2=catchment_area_km2,
            runoff_coefficient_override=runoff_coeff_override,
            apply_flow_floor=False,  # no fake floor when enrichment is used
            design_flow_factor=float(settings.household_hydro_design_flow_factor),
        )
        hydro_output_raw = calculate_hydropower(
            flow_rate_cms=flow_rate_cms,
            head_m=hydraulic_head_m,
            days_in_month=days_in_month,
            head_factor=float(settings.household_hydro_head_factor),
            max_head_m=float(settings.household_hydro_max_head_m),
            turbine_efficiency=float(settings.household_hydro_turbine_efficiency),
            generator_efficiency=float(settings.household_hydro_generator_efficiency),
            feasibility_penalty=float(stream_penalty) if stream_penalty is not None else None,
            head_already_realistic=head_already_realistic,
        )
        hydro_data_source = "Boothroyd et al. 2023 catchment geodatabase"
        hydro_catchment_name = catchment_enrichment.get("catchment_name")
        hydro_stream_dist = catchment_enrichment.get("distance_to_nearest_stream_m")
        if hydro_stream_dist is not None:
            if float(hydro_stream_dist) <= 2000:
                hydro_stream_feasibility = "high"
            elif float(hydro_stream_dist) <= 5000:
                hydro_stream_feasibility = "moderate"
            elif float(hydro_stream_dist) <= 10000:
                hydro_stream_feasibility = "low"
            else:
                hydro_stream_feasibility = "none"
        else:
            hydro_stream_feasibility = "unknown"
    else:
        # Fallback: original fixed-assumption model (no enrichment data)
        hydraulic_head_m = terrain_data.get("hydraulic_head_m") if terrain_data else 0.0
        flow_rate_cms = estimated_flow_rate(
            rainfall_mm_monthly=rainfall,
            runoff_potential=terrain_data.get("runoff_potential") if terrain_data else 0.0,
            watershed_gradient=terrain_data.get("watershed_gradient") if terrain_data else 0.0,
            mean_slope_deg=terrain_data.get("mean_slope_deg") if terrain_data else 0.0,
            gravity_flow_potential=terrain_data.get("gravity_flow_potential") if terrain_data else 0.0,
            catchment_area_km2=float(settings.household_hydro_catchment_km2),
            design_flow_factor=float(settings.household_hydro_design_flow_factor),
        )
        hydro_output_raw = calculate_hydropower(
            flow_rate_cms=flow_rate_cms,
            head_m=hydraulic_head_m,
            days_in_month=days_in_month,
            head_factor=float(settings.household_hydro_head_factor),
            max_head_m=float(settings.household_hydro_max_head_m),
            turbine_efficiency=float(settings.household_hydro_turbine_efficiency),
            generator_efficiency=float(settings.household_hydro_generator_efficiency),
        )
        hydro_data_source = "default terrain data"
        hydro_catchment_name = None
        hydro_stream_feasibility = None

    hydro_output = {
        "system_kwp": hydro_output_raw.get("available_power_kw", 0.0),
        "daily_hydro_output": hydro_output_raw.get("daily_energy_kwh", 0.0),
        "monthly_hydro_output": hydro_output_raw.get("monthly_energy_kwh", 0.0),
        "annual_hydro_output": (hydro_output_raw.get("monthly_energy_kwh") or 0.0) * 12.0,
        "hydro_score": hydro_output_raw.get("hydro_score", 0.0),
    }

    # NOTE: GEOTHERMAL CALCULATIONS
    geothermal_output = get_geothermal_data(municipality, municipality_data)
    # Add daily/monthly/annual kWh for card standardization
    geo_annual_gwh = geothermal_output.get("annual_energy_gwh") or 0.0
    geo_annual_kwh = geo_annual_gwh * 1_000_000.0
    geothermal_output["annual_energy_kwh"] = round(geo_annual_kwh, 2) if geo_annual_kwh > 0 else None
    geothermal_output["monthly_energy_kwh"] = round(geo_annual_kwh / 12.0, 2) if geo_annual_kwh > 0 else None
    geothermal_output["daily_energy_kwh"] = round(geo_annual_kwh / 365.0, 2) if geo_annual_kwh > 0 else None

    #NOTE: WIND CALCULATIONS
    wind_speed = float(wind_speed or 0.0)
    wind_output = calculate_wind_output(
        wind_speed_mps=wind_speed,
        days_in_month=days_in_month,
        air_density=air_density,
        rotor_radius_m=settings.household_wind_rotor_radius_m,
        cp=settings.household_wind_power_coefficient,
    )
    wind_output["annual_wind_output_kwh"] = (wind_output.get("monthly_energy_kwh") or 0.0) * 12.0

    # Province mode: use the median of municipality wind outputs instead of
    # the output from an area-weighted wind speed. This avoids one large,
    # windy municipality dominating the entire province recommendation.
    if mode == "province" and municipality_data.get("muni_median_wind_output_kwh"):
        median_kwh = float(municipality_data["muni_median_wind_output_kwh"])
        if median_kwh > 0:
            wind_output["monthly_energy_kwh"] = round(median_kwh, 4)
            wind_output["annual_wind_output_kwh"] = round(median_kwh * 12.0, 4)

    province = municipality_data.get("province")

    active_source = municipality_data.get("data_source", "NASA POWER")
    province = municipality_data.get("province")

    renewable_energy_results = {
        "municipality": municipality.upper(),
        "municipality_id": municipality_data.get("municipality_id"),
        "province": province,
        "data_source": active_source,
        #json climate data coming from the NASA Power or the Global Solar/Wind Atlas
        "climate": {
            "avg_t2m": avg_temp,
            "avg_t2m_max": municipality_data.get("avg_t2m_max"),
            "avg_t2m_min": municipality_data.get("avg_t2m_min"),
            "avg_rh2m": humidity,
            "avg_rhoa": air_density,
            "avg_prectotcorr": rainfall,
            "avg_ws10m": wind_speed,
            "avg_wind_hub_ms": round(wind_speed, 4),
            "avg_allsky_sfc_sw_dwn": solar_irradiance,
            "avg_cloud_amt": cloud_amt,
            "avg_surface_pressure": surface_pressure,
            "elevation": elevation,
            "solar_pvout_annual_kwh_kwp": pvout_annual,
            "wind_speed_100m_ms": municipality_data.get("wind_speed_100m_ms"),
            "era5_wind_speed_10m_ms": municipality_data.get("era5_wind_speed_10m_ms"),
        },
        #json estimates and assumptions for the renewable energy calculations, which can be used for transparency and future adjustments
        "assumptions": {
            "data_source": active_source,
            "temperature_factor": temperature_factor,
            "performance_ratio": performance_ratio,
            "days_in_month": days_in_month,
            "panel_wattage": solar_panel_default_config["panel_wattage"],
            "number_of_panels": solar_panel_default_config["number_of_panels"],
            "wind_speed_height_m": hub_height,
            "wind_speed_mps": round(wind_speed, 4),
            "wind_speed_source_height_m": wind_speed_source_height_m,
            "wind_shear_exponent": alpha,
            "household_wind_rated_power_kw": settings.household_wind_rated_power_kw,
            "household_wind_rotor_radius_m": settings.household_wind_rotor_radius_m,
            "household_wind_cut_in_mps": settings.household_wind_cut_in_mps,
            "household_wind_rated_mps": settings.household_wind_rated_mps,
            "household_wind_cut_out_mps": settings.household_wind_cut_out_mps,
            "household_wind_capacity_factor": settings.household_wind_capacity_factor,
            "solar_system_kwp": household_solar_size_kwp,
            # Hydro enrichment (Boothroyd et al. 2023 catchment geodatabase)
            "hydro_data_source": hydro_data_source,
            "hydro_catchment_name": hydro_catchment_name,
            "hydro_stream_feasibility": hydro_stream_feasibility,
            "household_hydro_head_factor": settings.household_hydro_head_factor,
            "household_hydro_design_flow_factor": settings.household_hydro_design_flow_factor,
            "household_hydro_max_head_m": settings.household_hydro_max_head_m,
            "household_hydro_turbine_efficiency": settings.household_hydro_turbine_efficiency,
            "household_hydro_generator_efficiency": settings.household_hydro_generator_efficiency,
            # Scoring baselines (for transparency and calibration)
            "solar_score_baseline_pvout": 1800.0,
            "wind_score_baseline_kwh": 300.0,
            "hydro_score_baseline_kwh": 100.0,
            # Wikipedia power-plant recalibration settings
            "wind_plants_boost_enabled": settings.wind_plants_boost_enabled,
            "wind_plants_boost_radius_km": settings.wind_plants_boost_radius_km,
            "wind_plants_max_bonus": settings.wind_plants_max_bonus,
            "wind_plants_generation_scale_factor": settings.wind_plants_generation_scale_factor,
            "wind_plants_max_generation_scale": settings.wind_plants_max_generation_scale,
            "hydro_plants_boost_enabled": settings.hydro_plants_boost_enabled,
            "hydro_plants_boost_radius_km": settings.hydro_plants_boost_radius_km,
            "hydro_plants_max_bonus": settings.hydro_plants_max_bonus,
            "hydro_plants_generation_scale_factor": settings.hydro_plants_generation_scale_factor,
            "hydro_plants_max_generation_scale": settings.hydro_plants_max_generation_scale,
            "wind_hydro_plant_boost_mode": settings.wind_hydro_plant_boost_mode,
            "hydro_plant_floor_enabled": settings.hydro_plant_floor_enabled,
            "hydro_plant_floor_factor": settings.hydro_plant_floor_factor,
            "hydro_plant_max_floor_kwh": settings.hydro_plant_max_floor_kwh,
            "hydro_plant_absolute_cap_kwh": settings.hydro_plant_absolute_cap_kwh,
        },
        # json for the solar outputs
        "solar_output": solar_output,
        "hydro_output": hydro_output,
        "wind_output": wind_output,
        "geothermal_output": geothermal_output,
        # json for the consumption calculations
        "consumption_results": consumption_results,
    }
    
    ai_analysis = None
    if include_ai:
        try:
            analysis_payload = {
                "municipality_data": municipality_results,
                "consumption_results": consumption_results,
                "renewable_energy_results": renewable_energy_results,
                "nearby_geothermal_plants": nearby_geo_plants or [],
                "mode": mode,
            }

            if use_rag and rag_query:
                from app.services.rag_gemini_funcs import analyze_with_rag

                ai_analysis = analyze_with_rag(analysis_payload, rag_query)
            else:
                from app.services.gemini_funcs import analyze_renewable_results

                ai_analysis = analyze_renewable_results(analysis_payload)
        except Exception:
            logger.exception("AI analysis failed in Ecosim")
            ai_analysis = {
                "summary": "AI analysis failed.",
                "renewable_analysis": {"solar": "", "wind": "", "hydro": "", "geothermal": ""},
                "recommendation": {"best_option": "", "reason": ""},
                "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}, "geothermal": {}},
                "environmental_impact": "",
            }

    # Build/persist deterministic per-source explanations for the UI fallback.
    explanations = _get_or_build_explanations(municipality_id, renewable_energy_results)

    # Merge fallback explanations so every renewable type always has text.
    if ai_analysis:
        ra = ai_analysis.get("renewable_analysis") or {}
        for key, text in explanations.items():
            if not ra.get(key):
                ra[key] = text
        ai_analysis["renewable_analysis"] = ra
    else:
        ai_analysis = {
            "summary": "",
            "renewable_analysis": explanations,
            "recommendation": {"best_option": "", "reason": ""},
            "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}, "geothermal": {}},
            "environmental_impact": "",
        }

    result = {
        "municipality_data": municipality_results,
        "consumption_results": consumption_results,
        "renewable_energy_results": renewable_energy_results,
        "ai_analysis": ai_analysis,
        "explanations": explanations,
        "terrain_data": terrain_data,
        "province": province,
    }

    if use_cache and geo_id and params_hash:
        # Don't persist a fallback AI summary for the full 30-minute window;
        # once the worker thread completes and writes the AI cache, a fresh
        # request should be able to pick up the real analysis.
        cache_ttl = (
            60
            if include_ai and (ai_analysis or {}).get("error")
            else _ECOSIM_TTL
        )
        set_ecosim_cache_sync("municipality", geo_id, params_hash, result, ttl=cache_ttl)

    return result


def _build_static_renewable_explanations(results: dict) -> dict[str, str]:
    """Create deterministic fallback explanations with causal reasoning.
    Every renewable type MUST produce a multi-sentence explanation even when
    specific output numbers are zero or unavailable."""
    climate = results.get("climate") or {}
    solar = results.get("solar_output") or {}
    wind = results.get("wind_output") or {}
    hydro = results.get("hydro_output") or {}
    geo = results.get("geothermal_output") or {}

    explanations: dict[str, str] = {}

    # Solar — always explain irradiance, cloud, temperature physics
    if solar:
        irradiance = climate.get("avg_allsky_sfc_sw_dwn")
        cloud = climate.get("avg_cloud_amt")
        temp = climate.get("avg_t2m")
        parts: list[str] = []
        parts.append(
            "Solar panels convert photons into electricity: higher irradiance means more photons strike the silicon cells, freeing more electrons and raising current."
        )
        if irradiance is not None:
            parts.append(
                f"This location receives {float(irradiance):.2f} kWh/m²/day on average."
            )
        if cloud is not None:
            parts.append(
                f"Cloud coverage at {float(cloud):.1f}% reduces effective irradiance because water droplets scatter and absorb incoming sunlight before it reaches the panels, directly lowering generation."
            )
        if temp is not None:
            parts.append(
                f"High surface temperatures ({float(temp):.1f}°C) also reduce efficiency: silicon cells lose about 0.4% output per degree above 25°C, so tropical heat partially offsets the benefit of strong sun."
            )
        monthly = solar.get("monthly_solar_output")
        if monthly:
            parts.append(f"The simulated system produces {float(monthly):.1f} kWh/month under these combined conditions.")
        else:
            parts.append("Simulated output is negligible given these atmospheric conditions.")
        explanations["solar"] = " ".join(parts)

    # Wind — always explain V³ physics and capacity factor
    if wind:
        ws = climate.get("avg_ws10m")
        parts: list[str] = []
        parts.append(
            "Wind turbines extract kinetic energy from moving air. Because kinetic energy scales with the cube of velocity (P ∝ V³), even a small increase in wind speed produces a disproportionately large jump in power output."
        )
        if ws is not None:
            parts.append(
                f"This location averages {float(ws):.2f} m/s."
            )
        cf = wind.get("capacity_factor")
        if cf is not None:
            parts.append(
                f"The capacity factor ({float(cf):.2f}) matters because turbines rarely run at full rated power in practice: variable winds, maintenance downtime, and cut-in/cut-out speeds mean actual output is a fraction of the theoretical maximum."
            )
        monthly = wind.get("monthly_energy_kwh")
        if monthly:
            parts.append(f"Realistically, the simulated turbine generates {float(monthly):.1f} kWh/month after accounting for these operational constraints.")
        else:
            parts.append("Simulated wind output is minimal at this average wind speed.")
        explanations["wind"] = " ".join(parts)

    # Hydro — always explain rainfall + head physics
    if hydro:
        rainfall = climate.get("avg_prectotcorr")
        elevation = climate.get("elevation")
        parts: list[str] = []
        parts.append(
            "Micro-hydro depends on two things: water flow and hydraulic head. Rainfall feeds the watershed and increases stream flow rate, which directly raises the kinetic energy available to spin the turbine."
        )
        if rainfall is not None:
            parts.append(
                f"This location averages {float(rainfall):.2f} mm/day of precipitation."
            )
        if elevation is not None:
            parts.append(
                f"Elevation at {float(elevation):.0f} m creates hydraulic head: water falling from a greater height carries more gravitational potential energy (mgh), which converts to higher pressure and more power at the turbine."
            )
        monthly = hydro.get("monthly_hydro_output")
        if monthly:
            parts.append(f"The simulated micro-hydro system is estimated to produce {float(monthly):.1f} kWh monthly given these water and head conditions.")
        else:
            parts.append("Simulated hydro output is minimal because the combination of rainfall and elevation at this site does not produce sufficient flow or head for meaningful generation.")
        explanations["hydro"] = " ".join(parts)

    # Geothermal — ALWAYS explain the four key subsurface drivers, even with zero data
    if geo:
        reservoir_temp = geo.get("reservoir_temperature_c")
        thermal = geo.get("thermal_power_mw")
        electric = geo.get("electric_power_mw")
        annual = geo.get("annual_energy_gwh")
        confidence = geo.get("confidence")
        classification = geo.get("classification")
        surface_temp = climate.get("avg_t2m")
        parts: list[str] = []

        # Always start with the fundamental physics
        parts.append(
            "Geothermal energy depends on four subsurface factors: surface heat flow (how much heat escapes the crust), proximity to faults or volcanoes (which channel hot fluids upward), aquifer permeability (whether water can circulate through hot rock), and the geothermal gradient (how fast temperature rises with depth)."
        )

        if surface_temp is not None:
            parts.append(
                f"The average surface temperature here is {float(surface_temp):.1f}°C."
            )

        if reservoir_temp is not None:
            parts.append(
                f"The estimated reservoir temperature is {float(reservoir_temp):.1f}°C. This is critical because extractable thermal energy equals mass flow × specific heat × temperature drop (Q = m·Cp·ΔT). A hotter reservoir means a larger ΔT and therefore more usable heat per kilogram of fluid circulated."
            )
        else:
            parts.append(
                "Without measured heat-flow data, the reservoir temperature cannot be reliably estimated. Low or absent heat-flow measurements usually indicate either low crustal heat production or insufficient survey coverage for this area."
            )

        if classification and classification != "Unknown":
            parts.append(
                f"Site classification is {classification}, reflecting the combined subsurface heat and permeability conditions."
            )
        else:
            parts.append(
                "Without subsurface data the site cannot be classified, but Philippine locations far from active volcanic arcs or major fault systems typically have lower geothermal potential."
            )

        if thermal is not None and electric is not None and (thermal > 0 or electric > 0):
            parts.append(
                f"Estimated thermal power is {float(thermal):.3f} MW and convertible electric power is {float(electric):.3f} MW, limited by the efficiency of the binary or flash cycle (typically 10–15%)."
            )
        else:
            parts.append(
                "No meaningful thermal or electric power is estimated for this site because the subsurface temperature or permeability is too low to sustain a viable geothermal plant."
            )

        if annual is not None and annual > 0:
            parts.append(f"This yields {float(annual):.3f} GWh annually.")
        else:
            parts.append(
                "Annual energy yield is effectively zero under current assumptions, meaning geothermal is not a practical option at this location."
            )

        if confidence is not None:
            parts.append(
                f"Data confidence is {float(confidence):.2f}, indicating how complete the measured heat-flow and aquifer datasets are for this municipality."
            )
        explanations["geothermal"] = " ".join(parts)

    return explanations


def _get_or_build_explanations(
    municipality_id: int | None,
    results: dict,
) -> dict[str, str]:
    """Return cached per-source explanations, regenerating and persisting them if stale."""
    generated = _build_static_renewable_explanations(results)
    if not municipality_id:
        return generated

    client = get_supabase_client()
    try:
        resp = (
            client.table("municipality_renewable_explanations")
            .select("*")
            .eq("municipality_id", str(municipality_id))
            .single()
            .execute()
        )
        row = resp.data
        if row:
            # Cached text is stale if any source differs from the freshly
            # generated explanation. This prevents outdated rows from being
            # served after calculation/settings changes.
            stale = any(
                row.get(k) != generated.get(k, "")
                for k in ("solar", "wind", "hydro", "geothermal")
            )
            if not stale:
                return {
                    k: row.get(k) or generated.get(k, "")
                    for k in ("solar", "wind", "hydro", "geothermal")
                }
    except Exception as exc:
        logger.warning("Failed to load cached explanations for municipality %s: %s", municipality_id, exc)

    try:
        client.table("municipality_renewable_explanations").upsert({
            "municipality_id": municipality_id,
            "solar": generated.get("solar"),
            "wind": generated.get("wind"),
            "hydro": generated.get("hydro"),
            "geothermal": generated.get("geothermal"),
        }).execute()
    except Exception as exc:
        logger.warning("Failed to cache explanations for municipality %s: %s", municipality_id, exc)

    return generated


def _calculate_option_summary(
    source: str,
    estimated_generation_kwh: float,
    source_score: float,
    monthly_consumption_kwh: float,
    electricity_rate: float,
    installation_cost_per_kw: float,
) -> dict:
    """
    Compute economic and environmental indicators for a single renewable option.

    Formulas and their academic support (APA 7th):
    ------------------------------------------------------------------------
    1. Simple Payback Period (SPP)
       SPP = installation_cost / (monthly_savings × 12)
       Source: Ngwakwe (2025) — quasi-systematic review confirming SPP as the
       dominant first-screening metric in residential PV techno-economic studies.
       Also applied by Huda et al. (2024) for Indonesian PV systems.

    2. CO₂ displacement
       carbon_reduction = usable_kwh × CO2_KG_PER_KWH
       Uses the Philippines DOE 2019–2021 National Grid Emission Factor
       (Luzon–Visayas OMEF = 0.6835 kg CO₂/kWh) (DOE, 2022).

    3. System-size proxy (for cost estimation)
       system_kw = monthly_generation / 30 days / 4.0 equivalent peak-sun hrs
       The 4 hr/day figure is a conservative Philippines national estimate;
       Taduran & Piao (2025) measured 3.01 kWh/kWp/day (Final Yield) in
       Tarlac City, while NREL data show 4.0–6.0 kWh/m²/day nationwide.

    4. Weighted suitability score (0–100 scale)
       score = source_score × (0.4 + 0.6 × energy_ratio) × 100
       Multiplicative scoring ensures source quality (climate/resource conditions)
       is the primary driver. A source with poor climate conditions cannot win
       simply because its energy output is high. This prevents misleading
       recommendations where, for example, wind is chosen over solar despite
       clearly inferior wind speeds.

    References
    ----------
    Asadi, M., Pourhossein, K., Noorollahi, Y., Marzband, M., & Iglesias, G. (2023).
        A new decision framework for hybrid solar and wind power plant site selection
        using linear regression modeling based on GIS-AHP. Sustainability, 15(10), 8359.
        https://doi.org/10.3390/su15108359

    Department of Energy (Philippines). (2022). 2019–2021 National Grid Emission Factor.
        Energy Regulatory Commission. https://www.foi.gov.ph/requests/national-grid-emission-factor/

    Huda, A., Kurniawan, I., Purba, K. F., Ichwani, R., Aryansyah, & Fionasari, R. (2024).
        Techno-economic assessment of residential and farm-based photovoltaic systems in Indonesia.
        Renewable Energy, 219, Article 119886. https://doi.org/10.1016/j.renene.2023.119886

    Ngwakwe, C. C. (2025). Estimating the financial payback period for renewable energy
        investment: A quasi-systematic review. Oblik i finansi, (1), 59–66.
        https://ideas.repec.org/a/iaf/journl/y2025i1p59-66.html

    Taduran, A. J. R., & Piao, L. P. (2025). Analyzing the performance of a 2.72 kWp rooftop
        grid-tied photovoltaic system in Tarlac City, Philippines. International Journal of
        Engineering Trends and Technology, 73(9), 318–327.
        https://doi.org/10.14445/22315381/IJETT-V73I9P127
    """
    generation_kwh = max(float(estimated_generation_kwh or 0.0), 0.0)
    consumption_kwh = max(float(monthly_consumption_kwh or 0.0), 0.0)
    usable_kwh = min(generation_kwh, consumption_kwh)
    monthly_savings = usable_kwh * electricity_rate

    # Source-specific system sizing so costs reflect real-world installs
    source_lower = (source or "").lower()
    if "geothermal" in source_lower:
        # Utility-scale plant: cost based on plant MW capacity, not household kW
        # Approximate PHP per kW for utility geothermal in the Philippines
        system_kw = generation_kwh / 30.0 / 24.0 if generation_kwh > 0 else 0.0
        installation_cost = system_kw * installation_cost_per_kw
        payback_years = None
        scale = "utility"
    elif "wind" in source_lower:
        # Residential wind CF ~25 % (PH small-turbine range 15–35 %)
        system_kw = generation_kwh / (30.0 * 24.0 * 0.25) if generation_kwh > 0 else 0.0
        installation_cost = system_kw * installation_cost_per_kw
        payback_years = (
            installation_cost / (monthly_savings * 12.0)
            if monthly_savings > 0
            else None
        )
        scale = "residential"
    elif "hydro" in source_lower:
        # Micro-hydro CF ~50 % (run-of-river / micro range 40–60 %)
        system_kw = generation_kwh / (30.0 * 24.0 * 0.50) if generation_kwh > 0 else 0.0
        installation_cost = system_kw * installation_cost_per_kw
        payback_years = (
            installation_cost / (monthly_savings * 12.0)
            if monthly_savings > 0
            else None
        )
        scale = "residential"
    else:
        # Solar: 4.5 peak-sun hrs/day ≈ 135 kWh/kWp/month (PH conservative)
        system_kw = generation_kwh / (30.0 * 4.5) if generation_kwh > 0 else 0.0
        installation_cost = system_kw * installation_cost_per_kw
        payback_years = (
            installation_cost / (monthly_savings * 12.0)
            if monthly_savings > 0
            else None
        )
        scale = "residential"

    energy_ratio = min(generation_kwh / consumption_kwh, 1.0) if consumption_kwh > 0 else 0.0
    # Multiplicative scoring: source quality is primary, energy coverage is secondary.
    # This prevents poor-quality sources from winning just because they generate more energy.
    source_score = float(source_score or 0.0)
    suitability_score = round(source_score * (0.4 + 0.6 * energy_ratio) * 100, 1)

    # Output-based generation score (what % of consumption this source can offset).
    # This is the unbiased, user-facing score for household options; geothermal stays reference only.
    source_type = "household" if scale != "utility" else "utility"
    if source_type == "household" and consumption_kwh > 0:
        generation_score = round(min(generation_kwh / consumption_kwh * 100, 100.0), 1)
    else:
        generation_score = None

    carbon_reduction = usable_kwh * CO2_KG_PER_KWH

    # Financial analysis (NPV, IRR, LCOE, discounted payback)
    annual_energy = generation_kwh * 12.0
    fin_inputs = FinancialInputs(
        system_capacity_kw=round(system_kw, 3),
        annual_energy_kwh=annual_energy,
        capital_cost_php=installation_cost,
        annual_om_cost_php=installation_cost * 0.01,  # 1% of CapEx annually
        electricity_tariff_php_kwh=electricity_rate,
        discount_rate=0.10,
        system_lifetime_years=25 if scale == "residential" else 30,
        degradation_rate=0.005,
    )
    fin_results = analyze_financials(fin_inputs)
    financials = financials_to_dict(fin_results)

    return {
        "source": source,
        "suitability_score": suitability_score,
        "estimated_generation_kwh": generation_kwh,
        "monthly_output": generation_kwh,
        "generation_score": generation_score,
        "source_type": source_type,
        "monthly_savings": monthly_savings,
        "installation_cost": installation_cost,
        "payback_years": payback_years,
        "discounted_payback_years": financials["discounted_payback_years"],
        "npv_php": financials["npv_php"],
        "irr": financials["irr"],
        "lcoe_php_kwh": financials["lcoe_php_kwh"],
        "benefit_cost_ratio": financials["benefit_cost_ratio"],
        "carbon_reduction": carbon_reduction,
        "system_kw": round(system_kw, 3),
        "scale": scale,
    }


def build_ecosim_dashboard_response(
    municipality_id: int,
    monthly_consumption: float,
    monthly_bill: float,
    electricity_rate: float | None = None,
    desired_savings: float = 0.5,
    include_ai: bool = False,
    use_rag: bool = False,
    rag_query: str | None = None,
    mode: str = "municipality",
    data_source: str = "auto",
) -> dict:
    if monthly_consumption <= 0 or monthly_bill <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Monthly consumption and monthly bill must be greater than zero.",
        )

    if electricity_rate is None or electricity_rate <= 0:
        electricity_rate = monthly_bill / monthly_consumption

    effective_consumption_kwh = monthly_bill / electricity_rate
    user_consumption_kwh = monthly_consumption
    input_warning = False
    if monthly_consumption > 0:
        consumption_mismatch = abs(monthly_consumption - effective_consumption_kwh) / effective_consumption_kwh
        if consumption_mismatch > 0.20:
            input_warning = True
            monthly_consumption = effective_consumption_kwh

    # Fetch name, lat/lon, and province in a single query to avoid extra round-trips.
    muni_lat: float | None = None
    muni_lon: float | None = None
    municipality_name: str | None = None
    province: str | None = None
    try:
        client = get_supabase_client()
        if mode == "province":
            prov_resp = (
                client.table("provinces")
                .select("name,lat,lon")
                .eq("province_id", municipality_id)
                .single()
                .execute()
            )
            if prov_resp.data:
                municipality_name = prov_resp.data.get("name")
                province = municipality_name
                muni_lat = prov_resp.data.get("lat")
                muni_lon = prov_resp.data.get("lon")
        else:
            muni_resp = (
                client.table("municipalities")
                .select("name,lat,lon,province_id")
                .eq("municipality_id", municipality_id)
                .single()
                .execute()
            )
            if muni_resp.data:
                municipality_name = muni_resp.data.get("name")
                muni_lat = muni_resp.data.get("lat")
                muni_lon = muni_resp.data.get("lon")
                province_id = muni_resp.data.get("province_id")
                province = (
                    get_province_name_by_id(province_id) if province_id else None
                )
    except Exception as exc:
        logger.warning("Municipality name/lat/lon/province fetch failed: %s", exc)

    if municipality_name is None:
        entity = "province" if mode == "province" else "municipality"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The selected {entity} was not found.",
        )

    nearby_geo_plants: list[dict[str, Any]] = []
    base_results = renewable_energy_calculator(
        house="Ecosim",
        municipality=municipality_name,
        current_electricity_bill=monthly_bill,
        electricity_rate=electricity_rate,
        desired_savings=desired_savings,
        include_ai=include_ai,
        use_rag=use_rag,
        rag_query=rag_query,
        nearby_geo_plants=nearby_geo_plants,
        mode=mode,
        municipality_id=municipality_id,
        data_source=data_source,
    )

    renewable_results = base_results["renewable_energy_results"]
    solar_output = renewable_results.get("solar_output", {})
    wind_output = renewable_results.get("wind_output", {})
    hydro_output = renewable_results.get("hydro_output", {})
    geothermal_output = renewable_results.get("geothermal_output", {})
    geothermal_output["citation"] = geothermal_output.get("citation") or GEOTHERMAL_CITATION
    geothermal_output["source_type"] = geothermal_output.get("source_type") or "utility"

    solar_score = float(solar_output.get("solar_score", 0.0)) / 100.0
    hydro_score = float(hydro_output.get("hydro_score", 0.0)) / 100.0
    # Wind score: output-based normalization (same approach as solar/hydro).
    # A 1.5 kW household turbine at an excellent Philippine site (5 m/s @ 30m,
    # CF ~25%) produces ~270 kWh/month. Use 300 kWh/month as the "excellent"
    # baseline so wind is directly comparable to solar and hydro scores.
    wind_monthly_kwh = float(wind_output.get("monthly_energy_kwh", 0.0))
    raw_wind_score = min(wind_monthly_kwh / 300.0, 1.0)

    _s = get_settings()

    # Wikipedia wind-plant suitability recalibration.
    nearby_wind_plants: list[dict[str, Any]] = []
    wind_generation_scale = 1.0
    if _s.wind_plants_boost_enabled:
        if _s.wind_hydro_plant_boost_mode == "suitability":
            boosted_wind_score, nearby_wind_plants = calculate_wind_proximity_boost(
                muni_lat,
                muni_lon,
                raw_wind_score * 100.0,
                province=province,
                radius_km=_s.wind_plants_boost_radius_km,
                max_bonus=_s.wind_plants_max_bonus,
            )
            wind_score = boosted_wind_score / 100.0
        else:
            # Approach C: scale household wind output by proven plant capacity.
            wind_generation_scale, nearby_wind_plants = calculate_wind_generation_scale(
                muni_lat,
                muni_lon,
                province=province,
                radius_km=_s.wind_plants_boost_radius_km,
                scale_factor=_s.wind_plants_generation_scale_factor,
                max_scale=_s.wind_plants_max_generation_scale,
            )
            scaled_wind_kwh = wind_monthly_kwh * wind_generation_scale
            wind_output["monthly_energy_kwh"] = round(scaled_wind_kwh, 4)
            wind_output["annual_wind_output_kwh"] = round(scaled_wind_kwh * 12.0, 4)
            wind_score = min(scaled_wind_kwh / 300.0, 1.0)
    else:
        wind_score = raw_wind_score

    # Wikipedia hydro-plant suitability recalibration.
    nearby_hydro_plants: list[dict[str, Any]] = []
    hydro_generation_scale = 1.0
    if _s.hydro_plants_boost_enabled:
        if _s.wind_hydro_plant_boost_mode == "suitability":
            boosted_hydro_score, nearby_hydro_plants = calculate_hydro_proximity_boost(
                muni_lat,
                muni_lon,
                hydro_score * 100.0,
                province=province,
                radius_km=_s.hydro_plants_boost_radius_km,
                max_bonus=_s.hydro_plants_max_bonus,
            )
            hydro_score = boosted_hydro_score / 100.0
        else:
            # Approach C: scale household hydro output by proven plant capacity.
            hydro_generation_scale, nearby_hydro_plants = calculate_hydro_generation_scale(
                muni_lat,
                muni_lon,
                province=province,
                radius_km=_s.hydro_plants_boost_radius_km,
                scale_factor=_s.hydro_plants_generation_scale_factor,
                max_scale=_s.hydro_plants_max_generation_scale,
            )
            hydro_monthly_kwh = float(hydro_output.get("monthly_hydro_output", 0.0))
            scaled_hydro_kwh = hydro_monthly_kwh * hydro_generation_scale

            # Apply a capacity-linked output floor for proven hydro provinces so
            # that large utility plants do not imply a negligible household
            # resource. The floor is only active for the configured province list
            # and is capped to avoid unphysical household output.
            hydro_output_floor = 0.0
            if (
                _s.hydro_plant_floor_enabled
                and province
                and any(
                    province.strip().lower() == p.strip().lower()
                    for p in _s.hydro_plant_floor_provinces
                )
            ):
                hydro_output_floor, _ = calculate_hydro_plant_floor(
                    muni_lat,
                    muni_lon,
                    province=province,
                    radius_km=_s.hydro_plants_boost_radius_km,
                    floor_factor=_s.hydro_plant_floor_factor,
                    max_floor_kwh=_s.hydro_plant_max_floor_kwh,
                )
            final_hydro_kwh = max(scaled_hydro_kwh, hydro_output_floor)
            final_hydro_kwh = min(final_hydro_kwh, _s.hydro_plant_absolute_cap_kwh)

            hydro_output["monthly_hydro_output"] = round(final_hydro_kwh, 4)
            hydro_output["annual_hydro_output"] = round(final_hydro_kwh * 12.0, 4)
            hydro_output["hydro_output_floor"] = round(hydro_output_floor, 2)
            hydro_score = min(final_hydro_kwh / 100.0, 1.0)
    else:
        hydro_score = hydro_score

    # Apply proximity boost to geothermal score if municipality is near an operating plant
    raw_geo_score = float(geothermal_output.get("suitability_score", 0.0))
    if muni_lat is not None and muni_lon is not None:
        boosted_score, nearby_geo_plants = calculate_proximity_boost(
            float(muni_lat), float(muni_lon), raw_geo_score
        )
        geo_score = boosted_score / 100.0
    else:
        geo_score = raw_geo_score / 100.0

    # Geothermal is utility-scale; convert annual GWh to monthly kWh for comparison
    geo_annual_gwh = geothermal_output.get("annual_energy_gwh") or 0.0
    geo_monthly_kwh = (geo_annual_gwh * 1_000_000) / 12.0

    options = [
        _calculate_option_summary(
            source="Solar",
            estimated_generation_kwh=solar_output.get("monthly_solar_output", 0.0),
            source_score=solar_score,
            monthly_consumption_kwh=monthly_consumption,
            electricity_rate=electricity_rate,
            installation_cost_per_kw=COST_PER_KW_SOLAR,
        ),
        _calculate_option_summary(
            source="Wind",
            estimated_generation_kwh=wind_output.get("monthly_energy_kwh", 0.0),
            source_score=wind_score,
            monthly_consumption_kwh=monthly_consumption,
            electricity_rate=electricity_rate,
            installation_cost_per_kw=COST_PER_KW_WIND,
        ),
        _calculate_option_summary(
            source="Hydropower",
            estimated_generation_kwh=hydro_output.get("monthly_hydro_output", 0.0),
            source_score=hydro_score,
            monthly_consumption_kwh=monthly_consumption,
            electricity_rate=electricity_rate,
            installation_cost_per_kw=COST_PER_KW_HYDRO,
        ),
        _calculate_option_summary(
            source="Geothermal",
            estimated_generation_kwh=geo_monthly_kwh,
            source_score=geo_score,
            monthly_consumption_kwh=monthly_consumption,
            electricity_rate=electricity_rate,
            installation_cost_per_kw=COST_PER_KW_GEOTHERMAL,
        ),
    ]

    for option in options:
        gen = option["estimated_generation_kwh"]
        pct = (gen / monthly_consumption * 100) if monthly_consumption > 0 else 0
        if option.get("source_type") == "utility":
            score = option["suitability_score"]
            if score >= 80:
                rating = "Excellent"
                why = "This location has ideal conditions for this type of energy."
            elif score >= 60:
                rating = "Good"
                why = "This location has favorable conditions, but may need some planning."
            elif score >= 40:
                rating = "Moderate"
                why = "This location can work, but it may not be the most cost-effective option."
            else:
                rating = "Fair"
                why = "Conditions at this location are not ideal for this type of energy."
            option["explanation"] = (
                f"{rating} reference-only match — {why} With a typical {option['source'].lower()} "
                f"system, this could generate about {gen:.0f} kWh per month at utility scale."
            )
        else:
            score = option["generation_score"]
            if score is None:
                rating, why = "Reference", "No household-scale estimate available."
            elif score >= 80:
                rating = "Excellent"
                why = "This source can offset most of your monthly electricity use."
            elif score >= 50:
                rating = "Good"
                why = "This source can offset a meaningful share of your monthly electricity use."
            elif score >= 25:
                rating = "Moderate"
                why = "This source can offset some of your monthly electricity use."
            else:
                rating = "Fair"
                why = "This source offsets a small share of your monthly electricity use."
            option["explanation"] = (
                f"{rating} match — {why} With your effective usage, this system could generate about "
                f"{gen:.0f} kWh per month, covering roughly {pct:.0f}% of your electricity needs."
            )

    # Confidence scoring per energy type
    climate_data = renewable_results.get("climate", {})
    climate_vars_available = sum(1 for v in climate_data.values() if v is not None)
    for option in options:
        src_lower = (option["source"] or "").lower()
        energy_type = "solar" if "solar" in src_lower else "wind" if "wind" in src_lower else "hydro" if "hydro" in src_lower else "geothermal"
        conf_factors = ConfidenceFactors(
            has_climate_data=climate_vars_available > 0,
            climate_variables_count=climate_vars_available,
            climate_data_year=2024,
            has_terrain_data=base_results.get("terrain_data") is not None,
            has_population_data=False,
            has_tariff_data=electricity_rate > 0,
            user_provided_inputs=monthly_consumption > 0,
            energy_type=energy_type,
        )
        option["confidence"] = calculate_confidence(conf_factors)

    # Recommend only household-scale sources (exclude utility-scale geothermal).
    # Cap the recommendation key at the user's consumption: a larger raw output does
    # not provide more household value. Use suitability_score as the tie-breaker so
    # the best natural resource wins when multiple sources can meet the need.
    household_options = [o for o in options if o.get("source_type") != "utility"]
    if household_options:

        def _recommendation_key(item: dict) -> tuple:
            usable_output = min(item["monthly_output"], monthly_consumption)
            return (usable_output, item["suitability_score"])

        recommended = max(household_options, key=_recommendation_key)

        # Hidden alternative: highest suitability score (for future reactivation).
        # This picks the source with the best resource quality × energy coverage,
        # regardless of raw kWh output. Stored but not shown to the user.
        suitability_recommended = max(household_options, key=lambda o: o["suitability_score"])
    else:
        recommended = {
            "source": "None",
            "suitability_score": 0.0,
            "generation_score": None,
            "source_type": None,
            "estimated_generation_kwh": 0.0,
            "monthly_output": 0.0,
            "monthly_savings": None,
            "installation_cost": None,
            "payback_years": None,
            "carbon_reduction": 0.0,
        }
        suitability_recommended = None

    # Optional AI override only when a reason is provided
    ai_analysis = base_results.get("ai_analysis") or {}
    if include_ai and ai_analysis:
        ai_rec = (ai_analysis.get("recommendation") or {}).get("best_option")
        ai_reason = (ai_analysis.get("recommendation") or {}).get("reason")
        ai_source_map = {
            "solar": "Solar",
            "wind": "Wind",
            "hydro": "Hydropower",
            "hydropower": "Hydropower",
        }
        if ai_rec and ai_reason:
            normalized = str(ai_rec).strip().lower()
            if normalized in ai_source_map:
                ai_match = next((o for o in household_options if o["source"].lower() == normalized), None)
                if ai_match:
                    recommended = ai_match
                    recommended["ai_reason"] = ai_reason

    rec_gen = recommended["estimated_generation_kwh"]
    rec_pct = (rec_gen / monthly_consumption * 100) if monthly_consumption > 0 else 0

    if recommended["source"] == "None":
        explanation = (
            "No household-scale renewable source has a meaningful output for this location. "
            "Please check the detailed estimates below or try a different municipality."
        )
    else:
        ai_note = recommended.get("ai_reason")
        ai_text = f" AI note: {ai_note}" if ai_note else ""
        explanation = (
            f"Based on the calculated monthly output, {recommended['source']} energy is the best home-scale match. "
            f"A typical {recommended['source'].lower()} system here could generate about {rec_gen:.0f} kWh per month, "
            f"covering roughly {rec_pct:.0f}% of your effective electricity usage.{ai_text}"
        )

    # Hide financial/LCOE fields until cost data is reliable
    for option in options:
        option["monthly_savings"] = None
        option["installation_cost"] = None
        option["payback_years"] = None
        option["discounted_payback_years"] = None
        option["npv_php"] = None
        option["irr"] = None
        option["lcoe_php_kwh"] = None
        option["benefit_cost_ratio"] = None
        option["system_kw"] = None
        # Populate generation_score on the raw output dicts used by technical cards
        if option["source"] == "Solar":
            solar_output["generation_score"] = option["generation_score"]
        elif option["source"] == "Wind":
            wind_output["generation_score"] = option["generation_score"]
            wind_output["wind_score"] = round(wind_score * 100, 2)
        elif option["source"] == "Hydropower":
            hydro_output["generation_score"] = option["generation_score"]
            hydro_output["hydro_score"] = round(hydro_score * 100, 2)

    renewable_results["solar_output"] = solar_output
    renewable_results["wind_output"] = wind_output
    renewable_results["hydro_output"] = hydro_output
    renewable_results["geothermal_output"] = geothermal_output

    # Record the actual generation scales and floor used in the calculation.
    if "assumptions" in renewable_results:
        renewable_results["assumptions"]["wind_generation_scale"] = round(wind_generation_scale, 3)
        renewable_results["assumptions"]["hydro_generation_scale"] = round(hydro_generation_scale, 3)
        renewable_results["assumptions"]["hydro_output_floor"] = round(hydro_output.get("hydro_output_floor", 0.0), 2)

    # For province mode, geothermal household data is not meaningful; null it.
    if mode == "province":
        renewable_results["geothermal_output"] = None

    return {
        "municipality": municipality_name.upper(),
        "municipality_id": municipality_id,
        "province": province,
        "mode": mode,
        "monthly_consumption_kwh": monthly_consumption,
        "user_consumption_kwh": user_consumption_kwh,
        "effective_consumption_kwh": effective_consumption_kwh,
        "monthly_bill": monthly_bill,
        "input_warning": input_warning,
        "recommended_source": recommended["source"],
        "suitability_score": recommended["suitability_score"],
        "generation_score": recommended["generation_score"],
        "source_type": recommended["source_type"],
        "estimated_generation_kwh": recommended["estimated_generation_kwh"],
        # Hidden: suitability-score-based recommendation (for future reactivation).
        # This picks the source with the highest suitability_score (resource quality
        # × energy coverage) rather than the highest raw generation output.
        "suitability_recommended_source": suitability_recommended["source"] if suitability_recommended else None,
        "suitability_recommended_score": suitability_recommended["suitability_score"] if suitability_recommended else None,
        "monthly_savings": None,
        "installation_cost": None,
        "payback_years": None,
        "carbon_reduction": recommended["carbon_reduction"],
        "explanation": explanation,
        "options": options,
        "comparison": None,
        "climate": renewable_results.get("climate"),
        "renewable_energy_results": renewable_results,
        "consumption_results": base_results.get("consumption_results"),
        "municipality_data": base_results.get("municipality_data"),
        "explanations": base_results.get("explanations"),
        "ai_analysis": ai_analysis if include_ai else None,
        "nearby_geothermal_plants": nearby_geo_plants,
        "nearby_wind_plants": nearby_wind_plants,
        "nearby_hydro_plants": nearby_hydro_plants,
        "remaining_anonymous_requests": None,
    }
