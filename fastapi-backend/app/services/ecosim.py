import supabase
import pandas as pd
import os
from datetime import datatime as dt
current_dir = os.getcwd()
df = pd.read_csv(f'{current_dir}/local_data/municipality_climate_averages.csv')

def get_municipality_data(municipality: str):
    municipality_result = (
        supabase
        .table("municipalities")
        .select()
        .eq("name", municipality)
        .single()
        .execute()
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
    daily_consumption_kwh = (
        monthly_consumption_kwh / dt.now().days_in_month
    )
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
    
def renewable_energy_calculator():
    pass