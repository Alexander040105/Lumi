import pandas as pd
import os
import datetime as dt
import calendar
from fastapi import HTTPException, status
from postgrest.exceptions import APIError
from app.schemas.ecosim import PostHouse
from app.services.supabase_service import get_supabase_client
current_dir = os.getcwd()
df = pd.read_csv(f'{current_dir}\\app\\services\\local_data\\municipality_climate_averages.csv')

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
    
def solar_calc(panel_wattage, number_of_panels, solar_irradiance, performance_ratio):
    system_kwp = (
        (panel_wattage * number_of_panels) / 1000
    )

    daily_solar_output = (
        system_kwp *
        solar_irradiance *
        performance_ratio
    )

    monthly_solar_output = (
        daily_solar_output * 30
    )
    return {
        "system_kwp": system_kwp,
        "daily_solar_output": daily_solar_output,
        "monthly_solar_output": monthly_solar_output
    }

def renewable_energy_calculator(
    municipality: str,
    current_electricity_bill: float,
    electricity_rate: float,
    desired_savings: float,
):
    solar_panel_default_config = {
        "panel_wattage": 550,               # Watts
        "panel_efficiency": 0.20,           # 20%
        "system_efficiency": 0.80,          # Base system efficiency
        "number_of_panels": 2
    }

    temperature_loss = 0.95
    dust_loss = 0.97
    inverter_efficiency = 0.96

    # Combined Performance Ratio
    performance_ratio = (
        solar_panel_default_config["system_efficiency"] *
        temperature_loss *
        dust_loss *
        inverter_efficiency
    )

    municipality_results = get_municipality_data(municipality)
    consumption_results = consumption_calculator(
        current_electricity_bill,
        electricity_rate,
        desired_savings,
    )
    municipality_data = municipality_results[0]
    solar_irradiance = municipality_data['avg_allsky_sfc_sw_dwn']           # kWh/m²/day
    wind_speed = municipality_data['avg_ws10m']              # m/s
    rainfall = municipality_data['avg_prectotcorr']       # mm/year      
    solar_output = solar_calc(
        panel_wattage=solar_panel_default_config["panel_wattage"],
        number_of_panels=solar_panel_default_config["number_of_panels"],
        solar_irradiance=solar_irradiance,
        performance_ratio=performance_ratio
    )

    
    return {
        "solar_output": solar_output,
        "consumption_results": consumption_results
    }