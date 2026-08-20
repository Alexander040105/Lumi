"""Solar output calculation module for LUMI EcoSim.

Improved with:
- NOCT-based temperature correction (replaces simple linear factor)
- Soiling model (dust + humidity + rainfall interaction)
- GHI-only fallback when DNI/DHI unavailable
- Air density correction from surface pressure
"""
from __future__ import annotations

import math
from typing import Any


def calculate_noct_cell_temp(
    avg_temp_c: float,
    irradiance_w_m2: float,
    noct_c: float = 45.0,
    wind_speed_ms: float = 1.0,
) -> float:
    """Estimate cell temperature using NOCT model.

    T_cell = T_amb + (NOCT - 20) * (G / 800) / (1 + wind_factor)

    Based on IEC 61853 and King et al. (2004).

    Args:
        avg_temp_c: Ambient temperature in °C
        irradiance_w_m2: Plane-of-array irradiance in W/m²
        noct_c: Nominal Operating Cell Temperature (default 45°C for standard modules)
        wind_speed_ms: Wind speed at 10m in m/s

    Returns:
        Estimated cell temperature in °C
    """
    if irradiance_w_m2 <= 0:
        return avg_temp_c

    wind_factor = max(0.5, 1.0 + 0.1 * wind_speed_ms)

    t_cell = avg_temp_c + (noct_c - 20.0) * (irradiance_w_m2 / 800.0) / wind_factor
    return t_cell


def calculate_temperature_factor_noct(
    avg_temp_c: float,
    irradiance_w_m2: float,
    temp_coeff_per_c: float = -0.004,
    noct_c: float = 45.0,
    wind_speed_ms: float = 1.0,
) -> float:
    """Temperature derating factor using NOCT cell temperature model.

    Args:
        avg_temp_c: Ambient temperature
        irradiance_w_m2: Solar irradiance in W/m²
        temp_coeff_per_c: Module temperature coefficient (default -0.4%/°C)
        noct_c: NOCT rating of module
        wind_speed_ms: Wind speed for cooling

    Returns:
        Temperature derating factor (0-1)
    """
    t_cell = calculate_noct_cell_temp(avg_temp_c, irradiance_w_m2, noct_c, wind_speed_ms)
    reference_temp = 25.0
    factor = 1.0 + temp_coeff_per_c * (t_cell - reference_temp)
    return max(factor, 0.0)


def calculate_temperature_factor(avg_temp_c: float | None, temp_coeff_per_c: float = -0.004) -> float:
    """Legacy simple temperature factor (kept for backward compatibility)."""
    if avg_temp_c is None:
        return 1.0
    reference_temp_c = 25.0
    factor = 1 + (temp_coeff_per_c * (avg_temp_c - reference_temp_c))
    return max(factor, 0.0)


def calculate_soiling_loss(
    ws10m: float | None = None,
    rh2m: float | None = None,
    prectotcorr_mm: float | None = None,
    days_since_cleaning: int = 30,
) -> float:
    """Estimate soiling loss ratio from environmental factors.

    Soiling model considers:
    - Dust accumulation (wind-driven, increases with dry windy conditions)
    - Humidity (high humidity can both bind dust and cause fungal growth)
    - Rainfall (natural cleaning effect)

    Returns:
        Soiling loss ratio (0-1, where 1.0 = no loss, 0.85 = 15% loss)
    """
    base_soiling = 0.97

    if ws10m is not None and prectotcorr_mm is not None:
        if prectotcorr_mm < 10:  # Dry conditions
            dust_factor = 1.0 + 0.003 * max(ws10m - 2.0, 0) * (days_since_cleaning / 30)
            base_soiling = base_soiling / dust_factor

    if prectotcorr_mm is not None and prectotcorr_mm > 50:
        rain_cleaning = 1.0 + 0.001 * min(prectotcorr_mm - 50, 100)
        base_soiling = min(base_soiling * rain_cleaning, 0.99)

    if rh2m is not None and rh2m > 80:
        base_soiling *= 0.995

    return max(min(base_soiling, 1.0), 0.80)


def calculate_dust_loss_from_wind(ws10m: float | None, base_dust_loss: float = 0.97) -> float:
    """Legacy dust loss calculation (kept for backward compatibility)."""
    if ws10m is None:
        return base_dust_loss
    wind_factor = 1 + 0.02 * (ws10m - 3.0)
    return max(min(base_dust_loss / wind_factor, 1.0), 0.80)


def calculate_degradation_from_humidity(rh2m: float | None, base_degradation: float = 0.99) -> float:
    """Legacy humidity degradation (kept for backward compatibility)."""
    if rh2m is None:
        return base_degradation
    if rh2m > 70:
        return base_degradation * 0.995
    return base_degradation


def calculate_air_density_correction(
    surface_pressure_pa: float | None,
    avg_temp_c: float | None,
) -> float:
    """Air density correction factor for solar panel output.

    Returns:
        Correction factor (typically 0.98-1.02)
    """
    if surface_pressure_pa is None or avg_temp_c is None:
        return 1.0

    p0 = 101325.0
    temp_k = avg_temp_c + 273.15
    rho_ratio = (surface_pressure_pa / p0) * (288.15 / temp_k)

    correction = 1.0 + 0.01 * (rho_ratio - 1.0)
    return max(min(correction, 1.02), 0.98)


def calculate_performance_ratio(
    system_efficiency: float = 0.80,
    temperature_factor: float = 1.0,
    dust_loss: float = 0.97,
    inverter_efficiency: float = 0.96,
    mismatch_loss: float = 0.98,
    wiring_loss: float = 0.98,
    degradation_loss: float = 0.99,
    soiling_loss: float | None = None,
    air_density_correction: float | None = None,
) -> float:
    """Calculate overall performance ratio with optional advanced factors."""
    pr = (
        system_efficiency
        * temperature_factor
        * (soiling_loss if soiling_loss is not None else dust_loss)
        * inverter_efficiency
        * mismatch_loss
        * wiring_loss
        * degradation_loss
    )
    if air_density_correction is not None:
        pr *= air_density_correction
    return max(pr, 0.0)


def solar_calc(
    panel_wattage: float,
    number_of_panels: int,
    solar_irradiance: float,
    performance_ratio: float,
    days_in_month: int,
) -> dict[str, Any]:
    """Legacy solar calculation (kept for backward compatibility)."""
    system_kwp = (panel_wattage * number_of_panels) / 1000.0
    daily_solar_output = system_kwp * solar_irradiance * performance_ratio
    monthly_solar_output = daily_solar_output * days_in_month
    solar_score = min((solar_irradiance / 6.0) * 100, 100)
    return {
        "system_kwp": system_kwp,
        "daily_solar_output": daily_solar_output,
        "monthly_solar_output": monthly_solar_output,
        "solar_score": solar_score,
    }


def solar_calc_advanced(
    panel_wattage: float,
    number_of_panels: int,
    ghi_kwh_m2_day: float,
    dni_kwh_m2_day: float | None = None,
    dhi_kwh_m2_day: float | None = None,
    avg_temp_c: float | None = None,
    rh2m: float | None = None,
    ws10m: float | None = None,
    prectotcorr_mm: float | None = None,
    surface_pressure_pa: float | None = None,
    panel_tilt_deg: float = 15.0,
    panel_azimuth_deg: float = 180.0,
    latitude_deg: float = 14.0,
    noct_c: float = 45.0,
    temp_coeff_per_c: float = -0.004,
    inverter_efficiency: float = 0.96,
    mismatch_loss: float = 0.98,
    wiring_loss: float = 0.98,
    degradation_loss: float = 0.99,
    days_in_month: int = 30,
    days_since_cleaning: int = 30,
) -> dict[str, Any]:
    """Advanced solar output calculation with NOCT, soiling, and transposition.

    Uses GHI as primary input. If DNI and DHI are available, uses
    transposition model for tilted surface irradiance. Otherwise,
    applies a tilt correction factor to GHI.

    Args:
        ghi_kwh_m2_day: Global Horizontal Irradiance in kWh/m²/day
        dni_kwh_m2_day: Direct Normal Irradiance (optional)
        dhi_kwh_m2_day: Diffuse Horizontal Irradiance (optional)
        panel_tilt_deg: Panel tilt angle (default 15° for PH latitude)
        panel_azimuth_deg: Panel azimuth (180° = south)
        latitude_deg: Site latitude
        noct_c: Module NOCT rating

    Returns:
        Dict with detailed solar output and loss breakdown
    """
    system_kwp = (panel_wattage * number_of_panels) / 1000.0

    # Transposition: calculate plane-of-array (POA) irradiance
    if dni_kwh_m2_day is not None and dhi_kwh_m2_day is not None:
        tilt_rad = math.radians(panel_tilt_deg)
        aoi_cos = max(0.0, math.cos(tilt_rad) * 0.95)
        poa = (
            dhi_kwh_m2_day * (1 + math.cos(tilt_rad)) / 2
            + dni_kwh_m2_day * aoi_cos
            + ghi_kwh_m2_day * 0.2 * (1 - math.cos(tilt_rad)) / 2
        )
        poa = max(poa, ghi_kwh_m2_day * 0.9)
        transposition_source = "hay_davies"
    else:
        tilt_gain = 1.0 + 0.05 * math.cos(math.radians(panel_tilt_deg - latitude_deg))
        poa = ghi_kwh_m2_day * tilt_gain
        transposition_source = "ghi_tilt_correction"

    poa_w_m2 = poa * 1000 / 24

    if avg_temp_c is not None:
        temp_factor = calculate_temperature_factor_noct(
            avg_temp_c=avg_temp_c,
            irradiance_w_m2=poa_w_m2,
            temp_coeff_per_c=temp_coeff_per_c,
            noct_c=noct_c,
            wind_speed_ms=ws10m or 1.0,
        )
    else:
        temp_factor = 1.0

    soiling = calculate_soiling_loss(
        ws10m=ws10m,
        rh2m=rh2m,
        prectotcorr_mm=prectotcorr_mm,
        days_since_cleaning=days_since_cleaning,
    )

    air_density = calculate_air_density_correction(surface_pressure_pa, avg_temp_c)

    pr = calculate_performance_ratio(
        temperature_factor=temp_factor,
        soiling_loss=soiling,
        air_density_correction=air_density,
        inverter_efficiency=inverter_efficiency,
        mismatch_loss=mismatch_loss,
        wiring_loss=wiring_loss,
        degradation_loss=degradation_loss,
    )

    daily_solar_output = system_kwp * poa * pr
    monthly_solar_output = daily_solar_output * days_in_month

    solar_score = min((ghi_kwh_m2_day / 6.0) * 100, 100)

    return {
        "system_kwp": round(system_kwp, 4),
        "poa_irradiance_kwh_m2_day": round(poa, 4),
        "transposition_source": transposition_source,
        "daily_solar_output": round(daily_solar_output, 4),
        "monthly_solar_output": round(monthly_solar_output, 4),
        "solar_score": round(solar_score, 2),
        "performance_ratio": round(pr, 4),
        "loss_breakdown": {
            "temperature_factor": round(temp_factor, 4),
            "soiling_loss": round(soiling, 4),
            "air_density_correction": round(air_density, 4),
            "inverter_efficiency": inverter_efficiency,
            "mismatch_loss": mismatch_loss,
            "wiring_loss": wiring_loss,
            "degradation_loss": degradation_loss,
        },
        "cell_temp_c": round(calculate_noct_cell_temp(avg_temp_c or 25, poa_w_m2, noct_c, ws10m or 1.0), 2) if avg_temp_c else None,
    }


def solar_calc_pvout(
    panel_wattage: float,
    number_of_panels: int,
    pvout_annual_kwh_kwp: float,
    days_in_month: int = 30,
) -> dict[str, Any]:
    """Solar output using Global Solar Atlas PVOUT (kWh/kWp/year).

    PVOUT already includes temperature, soiling, and system losses, so we do
    not double-apply a performance ratio.

    Args:
        panel_wattage: Watts per panel.
        number_of_panels: Number of panels.
        pvout_annual_kwh_kwp: Annual PV specific yield from GSA.
        days_in_month: Days in the calculation month.

    Returns:
        Dict with daily, monthly, and annual solar output and score.
    """
    system_kwp = (panel_wattage * number_of_panels) / 1000.0
    daily_kwh = system_kwp * (pvout_annual_kwh_kwp / 365.0)
    monthly_kwh = daily_kwh * days_in_month
    annual_kwh = system_kwp * pvout_annual_kwh_kwp
    # Suitability score based on annual specific yield; 1800 kWh/kWp/year is excellent for the PH.
    solar_score = min((pvout_annual_kwh_kwp / 1800.0) * 100, 100.0)
    return {
        "system_kwp": round(system_kwp, 4),
        "pvout_annual_kwh_kwp": round(pvout_annual_kwh_kwp, 4),
        "daily_solar_output": round(daily_kwh, 4),
        "monthly_solar_output": round(monthly_kwh, 4),
        "annual_solar_output": round(annual_kwh, 4),
        "solar_score": round(solar_score, 2),
        "performance_ratio": 1.0,
        "loss_breakdown": {
            "note": "PVOUT from Global Solar Atlas includes temperature, soiling, and system losses.",
        },
    }