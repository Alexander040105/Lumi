import pandas as pd
import os
import datetime as dt
import calendar
from fastapi import HTTPException, status
from postgrest.exceptions import APIError
from app.schemas.ecosim import PostHouse
from app.services.supabase_service import get_supabase_client
from app.services.solar_output_calc import calculate_temperature_factor, calculate_performance_ratio, solar_calc, calculate_dust_loss_from_wind, calculate_degradation_from_humidity    
from app.services.hydro_output_calc import calculate_hydropower, estimated_flow_rate
current_dir = os.getcwd()
df = pd.read_csv(f'{current_dir}\\app\\services\\local_data\\municipality_climate_averages.csv')


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



def renewable_energy_calculator(municipality: str, current_electricity_bill: float, electricity_rate: float, desired_savings: float) -> dict:
    # NOTE: Data fetching 
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
    elevation = municipality_data.get("avg_elevation")
    today = dt.datetime.now()
    days_in_month = calendar.monthrange(today.year, today.month)[1]

    # NOTE: SOLAR CALCULATIONS:
    # NOTE: this default config is estimated based on typical residential solar panel setups and can be adjusted in the future for more customization or to reflect different market conditions. It is currently hardcoded for simplicity and to provide a baseline for calculations.   
    solar_panel_default_config = {
        "panel_wattage": 550,
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

    # NOTE: HYDRO CALCULATIONS
    hydraulic_head_m = terrain_data.get("hydraulic_head_m") if terrain_data else 0.0
    flow_rate_cms = estimated_flow_rate(
        rainfall_mm_monthly=rainfall,
        runoff_potential=terrain_data.get("runoff_potential") if terrain_data else 0.0,
        watershed_gradient=terrain_data.get("watershed_gradient") if terrain_data else 0.0,
        mean_slope_deg=terrain_data.get("mean_slope_deg") if terrain_data else 0.0,
        gravity_flow_potential=terrain_data.get("gravity_flow_potential") if terrain_data else 0.0,
    )
    hydro_output = calculate_hydropower(
        flow_rate_cms=flow_rate_cms,
        head_m=hydraulic_head_m,
        days_in_month=days_in_month
    )
    renewable_energy_results = {
        "municipality": municipality.upper(),
        "municipality_id": municipality_data.get("municipality_id"),
        #json climate data coming from the NASA Power
        "climate": {
            "avg_t2m": avg_temp,
            "avg_t2m_max": municipality_data.get("avg_t2m_max"),
            "avg_t2m_min": municipality_data.get("avg_t2m_min"),
            "avg_rh2m": humidity,
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
        # json for the consumption calculations
        "consumption_results": consumption_results,
    }
    
    return {
        "municipality_data": municipality_results,
        "consumption_results": consumption_results,
        "renewable_energy_results": renewable_energy_results,
    }