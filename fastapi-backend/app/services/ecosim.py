import calendar
import datetime as dt
import logging
import os
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import HTTPException, status
from postgrest.exceptions import APIError
from app.schemas.ecosim import PostHouse
from app.services.supabase_service import get_supabase_client
from app.services.solar_output_calc import calculate_temperature_factor, calculate_performance_ratio, solar_calc, calculate_dust_loss_from_wind, calculate_degradation_from_humidity    
from app.services.hydro_output_calc import calculate_hydropower, estimated_flow_rate
from app.services.wind_output_calc import load_wind_averages, calculate_wind_output
from app.services.geothermal.features import (
    compute_geothermal_suitability,
    compute_geothermal_output,
)
from app.services.geothermal.plants import (
    calculate_proximity_boost,
    get_plants_near,
)
logger = logging.getLogger(__name__)
_LOCAL_DATA_DIR = Path(__file__).resolve().parent / "local_data"
_CLIMATE_CSV = _LOCAL_DATA_DIR / "municipality_climate_averages.csv"
df = pd.read_csv(str(_CLIMATE_CSV))

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


def get_municipality_terrain_data(municipality: str) -> dict | None:
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
        result = (
            client
            .table("hydropower_suitability")
            .select()
            .eq("municipality_name", municipality.upper())
            .single()
            .execute()
        )
        return result.data or None
    except APIError:
        return None  # terrain data is optional; degrade gracefully

def get_municipality_data(municipality: str):
    client = get_supabase_client()
    try:
        municipality_result = (
            client
            .table("municipalities")
            .select()
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

    municipality_id = (
        municipality_result.data["municipality_id"]
    )

    municipality_data = (
        df[df["municipality_id"] == municipality_id]
        .to_dict(orient="records")
    )

    if not municipality_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No climate average data found for this municipality.",
        )
        
    return municipality_data


def list_municipalities() -> list[dict]:
    client = get_supabase_client()
    try:
        result = (
            client
            .table("municipalities")
            .select("municipality_id,name")
            .order("name")
            .limit(20000)
            .execute()
        )
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

    items = result.data or []
    return sorted(
        (
            {
                "municipality_id": item.get("municipality_id"),
                "name": item.get("name"),
            }
            for item in items
            if item.get("municipality_id") and item.get("name")
        ),
        key=lambda item: item["name"].upper(),
    )


def list_provinces() -> list[dict]:
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
    return sorted(
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


def get_province_data(province_name: str) -> dict:
    """Aggregate municipality climate data for a province.

    Returns a dict with the same structure as a single municipality record
    so it can be used interchangeably in renewable_energy_calculator.
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

    # Aggregate climate data from the CSV
    province_df = df[df["municipality_id"].isin(municipality_ids)]
    if province_df.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No climate average data found for this province.",
        )

    numeric_cols = [
        "avg_t2m", "avg_t2m_max", "avg_t2m_min", "avg_rh2m",
        "avg_prectotcorr", "avg_ws10m", "avg_allsky_sfc_sw_dwn",
        "avg_cloud_amt", "avg_surface_pressure", "avg_rhoa", "avg_elevation",
    ]

    aggregated = {"municipality_id": province_id, "name": province_name.upper()}
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
            .in_("municipality_id", municipality_ids[:500])  # limit batch
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
                "assumption": data.get("assumption", ""),
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
        }

    suitability = compute_geothermal_suitability(lat, lon, surface_temp)
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
        "assumption": output.get("assumption"),
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
) -> dict:
    # NOTE: Data fetching
    if mode == "province":
        municipality_data = get_province_data(municipality)
        municipality_results = [municipality_data]
        terrain_data = municipality_data.get("terrain")
    else:
        municipality_results = get_municipality_data(municipality)
        municipality_data = municipality_results[0]
        terrain_data = get_municipality_terrain_data(municipality)
    consumption_results = consumption_calculator(
        current_electricity_bill,
        electricity_rate,
        desired_savings,
    )
    solar_irradiance = municipality_data.get("avg_allsky_sfc_sw_dwn") or 0.0
    avg_temp = municipality_data.get("avg_t2m")
    cloud_amt = municipality_data.get("avg_cloud_amt")
    rainfall = municipality_data.get("avg_prectotcorr")
    wind_speed = municipality_data.get("avg_ws10m")
    humidity = municipality_data.get("avg_rh2m")
    surface_pressure = municipality_data.get("avg_surface_pressure")
    air_density = municipality_data.get("avg_rhoa")
    elevation = municipality_data.get("avg_elevation")
    today = dt.datetime.now()
    days_in_month = calendar.monthrange(today.year, today.month)[1]

    # NOTE: SOLAR CALCULATIONS:
    # NOTE: this default config is estimated based on typical residential solar panel setups and can be adjusted in the future for more customization or to reflect different market conditions. It is currently hardcoded for simplicity and to provide a baseline for calculations.   
    solar_panel_default_config = {
        "panel_wattage": 400,
        "number_of_panels": 2,
        "system_efficiency": 0.80,
        "temp_coeff_per_c": -0.004,
        "dust_loss": 0.97,
        "inverter_efficiency": 0.96,
        "mismatch_loss": 0.98,
        "wiring_loss": 0.98,
        "degradation_loss": 0.99,
    }
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
    solar_output = solar_calc(
        panel_wattage=solar_panel_default_config["panel_wattage"],
        number_of_panels=solar_panel_default_config["number_of_panels"],
        solar_irradiance=solar_irradiance,
        performance_ratio=performance_ratio,
        days_in_month=days_in_month,
    )
    solar_output["annual_solar_output"] = (solar_output.get("monthly_solar_output") or 0.0) * 12.0

    # NOTE: HYDRO CALCULATIONS
    hydraulic_head_m = terrain_data.get("hydraulic_head_m") if terrain_data else 0.0
    flow_rate_cms = estimated_flow_rate(
        rainfall_mm_monthly=rainfall,
        runoff_potential=terrain_data.get("runoff_potential") if terrain_data else 0.0,
        watershed_gradient=terrain_data.get("watershed_gradient") if terrain_data else 0.0,
        mean_slope_deg=terrain_data.get("mean_slope_deg") if terrain_data else 0.0,
        gravity_flow_potential=terrain_data.get("gravity_flow_potential") if terrain_data else 0.0,
    )
    hydro_output_raw = calculate_hydropower(
        flow_rate_cms=flow_rate_cms,
        head_m=hydraulic_head_m,
        days_in_month=days_in_month
    )
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
    wind_output = calculate_wind_output(wind_speed_mps=wind_speed, days_in_month=days_in_month, air_density=air_density)
    wind_output["annual_wind_output_kwh"] = (wind_output.get("monthly_energy_kwh") or 0.0) * 12.0

    renewable_energy_results = {
        "municipality": municipality.upper(),
        "municipality_id": municipality_data.get("municipality_id"),
        #json climate data coming from the NASA Power
        "climate": {
            "avg_t2m": avg_temp,
            "avg_t2m_max": municipality_data.get("avg_t2m_max"),
            "avg_t2m_min": municipality_data.get("avg_t2m_min"),
            "avg_rh2m": humidity,
            "avg_rhoa": air_density,
            "avg_prectotcorr": rainfall,
            "avg_ws10m": wind_speed,
            "avg_allsky_sfc_sw_dwn": solar_irradiance,
            "avg_cloud_amt": cloud_amt,
            "avg_surface_pressure": surface_pressure,
            "elevation": elevation,
        },
        #json estimates and assumptions for the renewable energy calculations, which can be used for transparency and future adjustments
        "assumptions": {
            "temperature_factor": temperature_factor,
            "performance_ratio": performance_ratio,
            "days_in_month": days_in_month,
            "panel_wattage": solar_panel_default_config["panel_wattage"],
            "number_of_panels": solar_panel_default_config["number_of_panels"],
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
            }

            if use_rag and rag_query:
                from app.services.rag_gemini_funcs import analyze_with_rag

                ai_analysis = analyze_with_rag(analysis_payload, rag_query)
            else:
                from app.services.gemini_funcs import analyze_renewable_results

                ai_analysis = analyze_renewable_results(analysis_payload)
        except Exception:
            logger.exception("Gemini analysis failed in Ecosim")
            ai_analysis = {
                "summary": "Gemini analysis failed.",
                "renewable_analysis": {"solar": "", "wind": "", "hydro": "", "geothermal": ""},
                "recommendation": {"best_option": "", "reason": ""},
                "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}, "geothermal": {}},
                "environmental_impact": "",
            }

    # Merge static fallback explanations so every renewable type always has text
    if ai_analysis:
        static_explanations = _build_static_renewable_explanations(renewable_energy_results)
        ra = ai_analysis.get("renewable_analysis") or {}
        for key, text in static_explanations.items():
            if not ra.get(key):
                ra[key] = text
        ai_analysis["renewable_analysis"] = ra

    return {
        "municipality_data": municipality_results,
        "consumption_results": consumption_results,
        "renewable_energy_results": renewable_energy_results,
        "ai_analysis": ai_analysis,
    }


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

    4. Weighted suitability score
       score = 0.6 × energy_ratio + 0.4 × source_score
       Standard weighted linear combination (WLC) used in GIS-MCDA
       renewable-energy site-selection (Asadi et al., 2023).

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
    suitability_score = round((0.6 * energy_ratio) + (0.4 * source_score), 3)
    carbon_reduction = usable_kwh * CO2_KG_PER_KWH

    return {
        "source": source,
        "suitability_score": suitability_score,
        "estimated_generation_kwh": generation_kwh,
        "monthly_savings": monthly_savings,
        "installation_cost": installation_cost,
        "payback_years": payback_years,
        "carbon_reduction": carbon_reduction,
        "system_kw": round(system_kw, 3),
        "scale": scale,
    }


def build_ecosim_dashboard_response(
    municipality_id: int,
    monthly_consumption: float,
    monthly_bill: float,
    desired_savings: float = 0.5,
    include_ai: bool = False,
    use_rag: bool = False,
    rag_query: str | None = None,
    mode: str = "municipality",
) -> dict:
    if monthly_consumption <= 0 or monthly_bill <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="monthly_consumption and monthly_bill must be greater than zero",
        )

    electricity_rate = monthly_bill / monthly_consumption
    if mode == "province":
        municipality_name = get_province_name_by_id(municipality_id)
    else:
        municipality_name = get_municipality_name_by_id(municipality_id)

    # Fetch municipality lat/lon for proximity boost
    muni_lat: float | None = None
    muni_lon: float | None = None
    try:
        client = get_supabase_client()
        if mode == "province":
            # For province mode, lat/lon come from the provinces table
            prov_resp = (
                client.table("provinces")
                .select("lat,lon")
                .eq("province_id", municipality_id)
                .single()
                .execute()
            )
            if prov_resp.data:
                muni_lat = prov_resp.data.get("lat")
                muni_lon = prov_resp.data.get("lon")
        else:
            muni_resp = (
                client.table("municipalities")
                .select("lat,lon")
                .eq("municipality_id", municipality_id)
                .single()
                .execute()
            )
            if muni_resp.data:
                muni_lat = muni_resp.data.get("lat")
                muni_lon = muni_resp.data.get("lon")
    except Exception:
        pass

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
    )

    renewable_results = base_results["renewable_energy_results"]
    solar_output = renewable_results.get("solar_output", {})
    wind_output = renewable_results.get("wind_output", {})
    hydro_output = renewable_results.get("hydro_output", {})
    geothermal_output = renewable_results.get("geothermal_output", {})

    solar_score = float(solar_output.get("solar_score", 0.0)) / 100.0
    hydro_score = float(hydro_output.get("hydro_score", 0.0)) / 100.0
    wind_score = min(float(wind_output.get("capacity_factor", 0.0)) * 1.5, 1.0)

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
        option["explanation"] = (
            f"Estimated {option['estimated_generation_kwh']:.0f} kWh/month with "
            f"{option['suitability_score']:.2f} suitability score."
        )

    # Recommend only household-scale sources (exclude utility-scale geothermal)
    household_options = [o for o in options if o.get("scale") != "utility"]
    recommended = max(
        household_options,
        key=lambda item: (item["suitability_score"], item["estimated_generation_kwh"]),
    )

    net_consumption = max(monthly_consumption - recommended["estimated_generation_kwh"], 0.0)
    net_bill = net_consumption * electricity_rate

    explanation = (
        f"{recommended['source']} scores highest for this municipality based on climate data and "
        "expected generation compared with your monthly usage."
    )

    return {
        "municipality": municipality_name.upper(),
        "municipality_id": municipality_id,
        "monthly_consumption_kwh": monthly_consumption,
        "monthly_bill": monthly_bill,
        "recommended_source": recommended["source"],
        "suitability_score": recommended["suitability_score"],
        "estimated_generation_kwh": recommended["estimated_generation_kwh"],
        "monthly_savings": recommended["monthly_savings"],
        "installation_cost": recommended["installation_cost"],
        "payback_years": recommended["payback_years"],
        "carbon_reduction": recommended["carbon_reduction"],
        "explanation": explanation,
        "options": options,
        "comparison": {
            "current_monthly_consumption_kwh": monthly_consumption,
            "current_monthly_bill": monthly_bill,
            "renewable_monthly_consumption_kwh": net_consumption,
            "renewable_monthly_bill": net_bill,
        },
        "climate": renewable_results.get("climate"),
        "renewable_energy_results": renewable_results,
        "consumption_results": base_results.get("consumption_results"),
        "municipality_data": base_results.get("municipality_data"),
        "ai_analysis": base_results.get("ai_analysis"),
        "nearby_geothermal_plants": nearby_geo_plants,
    }