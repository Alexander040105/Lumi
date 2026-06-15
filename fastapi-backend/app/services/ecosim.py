import calendar
import datetime as dt
import logging
import os

import pandas as pd
from fastapi import HTTPException, status
from postgrest.exceptions import APIError
from app.schemas.ecosim import PostHouse
from app.services.supabase_service import get_supabase_client
from app.services.solar_output_calc import calculate_temperature_factor, calculate_performance_ratio, solar_calc, calculate_dust_loss_from_wind, calculate_degradation_from_humidity    
from app.services.hydro_output_calc import calculate_hydropower, estimated_flow_rate
from app.services.wind_output_calc import load_wind_averages, calculate_wind_output
logger = logging.getLogger(__name__)
current_dir = os.getcwd()
df = pd.read_csv(f'{current_dir}\\app\\services\\local_data\\municipality_climate_averages.csv')

COST_PER_KW_SOLAR = 60000.0
COST_PER_KW_WIND = 80000.0
COST_PER_KW_HYDRO = 100000.0
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
            .single()
            .execute()
        )
    except APIError as exc:
        # Robust extraction: postgrest stores error data in different
        # shapes depending on the library version.
        err_code = None
        arg0 = getattr(exc, "args", [{}])[0]
        if isinstance(arg0, dict):
            err_code = arg0.get("code")
        if not err_code and hasattr(exc, "code"):
            err_code = exc.code
        if not err_code:
            import ast, re
            m = re.search(r"'code':\s*'([^']+)'", str(exc))
            if m:
                err_code = m.group(1)
        if err_code == "PGRST116":
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
        message = "Failed to load municipalities"
        arg0 = getattr(exc, "args", [{}])[0]
        if isinstance(arg0, dict):
            message = arg0.get("message") or message
        elif hasattr(exc, "message"):
            message = exc.message or message
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
        err_code = None
        arg0 = getattr(exc, "args", [{}])[0]
        if isinstance(arg0, dict):
            err_code = arg0.get("code")
        if not err_code and hasattr(exc, "code"):
            err_code = exc.code
        if not err_code:
            import re
            m = re.search(r"'code':\s*'([^']+)'", str(exc))
            if m:
                err_code = m.group(1)
        if err_code == "PGRST116":
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
) -> dict:
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
        "hydro_score": hydro_output_raw.get("hydro_score", 0.0),
    }
    
    #NOTE: WIND CALCULATIONS
    wind_output = calculate_wind_output(wind_speed_mps=wind_speed, days_in_month=days_in_month, air_density=air_density)

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
                "renewable_analysis": {"solar": "", "wind": "", "hydro": ""},
                "recommendation": {"best_option": "", "reason": ""},
                "cost_estimation": {"solar": {}, "wind": {}, "hydro": {}},
                "environmental_impact": "",
            }

    return {
        "municipality_data": municipality_results,
        "consumption_results": consumption_results,
        "renewable_energy_results": renewable_energy_results,
        "ai_analysis": ai_analysis,
    }


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
    # 30 days × 4 equivalent peak-sun hours ≈ 120 kWh/kWp/month (conservative PH estimate)
    system_kw = generation_kwh / 30.0 / 4.0 if generation_kwh > 0 else 0.0
    installation_cost = system_kw * installation_cost_per_kw
    payback_years = (
        installation_cost / (monthly_savings * 12.0)
        if monthly_savings > 0
        else None
    )
    energy_ratio = min(generation_kwh / consumption_kwh, 1.0) if consumption_kwh > 0 else 0.0
    suitability_score = round((0.6 * energy_ratio) + (0.4 * source_score), 3)
    carbon_reduction = usable_kwh * CO2_KG_PER_KWH
    independence_score = round(energy_ratio * 100, 2)

    return {
        "source": source,
        "suitability_score": suitability_score,
        "estimated_generation_kwh": generation_kwh,
        "monthly_savings": monthly_savings,
        "installation_cost": installation_cost,
        "payback_years": payback_years,
        "carbon_reduction": carbon_reduction,
        "independence_score": independence_score,
    }


def get_monthly_climate_data(municipality_id: int) -> list[dict]:
    """Fetch the latest year of monthly climate data for a municipality."""
    client = get_supabase_client()
    try:
        result = (
            client
            .table("municipality_climate_monthly")
            .select("*")
            .eq("municipality_id", municipality_id)
            .order("year", desc=True)
            .limit(12)
            .execute()
        )
        items = result.data or []
        if not items:
            return []
        max_year = max(item["year"] for item in items)
        return [item for item in items if item["year"] == max_year]
    except APIError:
        return []


def _monthly_renewable_calculation(
    monthly_data: dict,
    terrain_data: dict | None,
    days_in_month: int,
) -> dict:
    """Run renewable calculations for a single month."""
    solar_irradiance = monthly_data.get("allsky_sfc_sw_dwn") or 0.0
    avg_temp = monthly_data.get("t2m")
    cloud_amt = monthly_data.get("cloud_amt")
    rainfall = monthly_data.get("prectotcorr")
    wind_speed = monthly_data.get("ws10m")
    humidity = monthly_data.get("rh2m")
    surface_pressure = monthly_data.get("surface_pressure")
    air_density = monthly_data.get("rhoa")

    temperature_factor = calculate_temperature_factor(
        avg_temp_c=avg_temp,
        temp_coeff_per_c=-0.004,
    )
    performance_ratio = calculate_performance_ratio(
        system_efficiency=0.80,
        temperature_factor=temperature_factor,
        dust_loss=calculate_dust_loss_from_wind(ws10m=wind_speed, base_dust_loss=0.97),
        inverter_efficiency=0.96,
        mismatch_loss=0.98,
        wiring_loss=0.98,
        degradation_loss=calculate_degradation_from_humidity(rh2m=humidity, base_degradation=0.99),
    )
    solar = solar_calc(
        panel_wattage=400,
        number_of_panels=2,
        solar_irradiance=solar_irradiance,
        performance_ratio=performance_ratio,
        days_in_month=days_in_month,
    )

    hydraulic_head_m = terrain_data.get("hydraulic_head_m") if terrain_data else 0.0
    flow_rate = estimated_flow_rate(
        rainfall_mm_monthly=rainfall,
        runoff_potential=terrain_data.get("runoff_potential") if terrain_data else 0.0,
        watershed_gradient=terrain_data.get("watershed_gradient") if terrain_data else 0.0,
        mean_slope_deg=terrain_data.get("mean_slope_deg") if terrain_data else 0.0,
        gravity_flow_potential=terrain_data.get("gravity_flow_potential") if terrain_data else 0.0,
    )
    hydro_raw = calculate_hydropower(flow_rate_cms=flow_rate, head_m=hydraulic_head_m, days_in_month=days_in_month)
    hydro = {
        "system_kwp": hydro_raw.get("available_power_kw", 0.0),
        "daily_hydro_output": hydro_raw.get("daily_energy_kwh", 0.0),
        "monthly_hydro_output": hydro_raw.get("monthly_energy_kwh", 0.0),
    }

    wind = calculate_wind_output(wind_speed_mps=wind_speed, days_in_month=days_in_month, air_density=air_density)

    return {
        "month": monthly_data.get("month"),
        "year": monthly_data.get("year"),
        "solar_output_kwh": solar.get("monthly_solar_output", 0.0),
        "wind_output_kwh": wind.get("monthly_energy_kwh", 0.0),
        "hydro_output_kwh": hydro.get("monthly_hydro_output", 0.0),
        "solar_irradiance": solar_irradiance,
        "wind_speed": wind_speed,
        "rainfall": rainfall,
        "temperature": avg_temp,
    }


def build_seasonal_ecosim_response(municipality_id: int) -> list[dict]:
    """Build a 12-month seasonal breakdown of renewable generation."""
    municipality_name = get_municipality_name_by_id(municipality_id)
    terrain_data = get_municipality_terrain_data(municipality_name)
    monthly_climate = get_monthly_climate_data(municipality_id)

    if not monthly_climate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No monthly climate data found for this municipality.",
        )

    monthly_climate.sort(key=lambda x: x["month"])
    results = []
    for data in monthly_climate:
        month = int(data.get("month", 1))
        year = int(data.get("year", 2024))
        days_in_month = calendar.monthrange(year, month)[1]
        result = _monthly_renewable_calculation(data, terrain_data, days_in_month)
        results.append(result)
    return results


def build_ecosim_dashboard_response(
    municipality_id: int,
    monthly_consumption: float,
    monthly_bill: float,
    include_ai: bool = False,
    use_rag: bool = False,
    rag_query: str | None = None,
) -> dict:
    if monthly_consumption <= 0 or monthly_bill <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="monthly_consumption and monthly_bill must be greater than zero",
        )

    electricity_rate = monthly_bill / monthly_consumption
    municipality_name = get_municipality_name_by_id(municipality_id)

    base_results = renewable_energy_calculator(
        house="Ecosim",
        municipality=municipality_name,
        current_electricity_bill=monthly_bill,
        electricity_rate=electricity_rate,
        desired_savings=0.5,
        include_ai=include_ai,
        use_rag=use_rag,
        rag_query=rag_query,
    )

    renewable_results = base_results["renewable_energy_results"]
    solar_output = renewable_results.get("solar_output", {})
    wind_output = renewable_results.get("wind_output", {})
    hydro_output = renewable_results.get("hydro_output", {})

    solar_score = float(solar_output.get("solar_score", 0.0)) / 100.0
    hydro_score = float(hydro_output.get("hydro_score", 0.0)) / 100.0
    wind_score = min(float(wind_output.get("capacity_factor", 0.0)) * 1.5, 1.0)

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
    ]

    for option in options:
        option["explanation"] = (
            f"Estimated {option['estimated_generation_kwh']:.0f} kWh/month with "
            f"{option['suitability_score']:.2f} suitability score."
        )

    recommended = max(
        options,
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
        "independence_score": recommended["independence_score"],
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
    }