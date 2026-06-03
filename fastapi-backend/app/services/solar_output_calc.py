
def calculate_temperature_factor(avg_temp_c: float | None, temp_coeff_per_c: float = -0.004) -> float:
    if avg_temp_c is None:
        return 1.0
    reference_temp_c = 25.0
    factor = 1 + (temp_coeff_per_c * (avg_temp_c - reference_temp_c))
    return max(factor, 0.0)

def calculate_dust_loss_from_wind(ws10m: float | None, base_dust_loss: float = 0.97) -> float:
    """Adjust dust loss based on wind speed at 10m"""
    if ws10m is None:
        return base_dust_loss
    # Higher wind speeds increase dust accumulation
    wind_factor = 1 + 0.02 * (ws10m - 3.0)  # 3 m/s is moderate wind
    return max(min(base_dust_loss / wind_factor, 1.0), 0.80)

def calculate_degradation_from_humidity(rh2m: float | None, base_degradation: float = 0.99) -> float:
    """Adjust degradation loss based on relative humidity"""
    if rh2m is None:
        return base_degradation
    if rh2m > 70:  # High humidity increases degradation
        return base_degradation * 0.995
    return base_degradation

def calculate_performance_ratio(
    system_efficiency: float = 0.80,
    temperature_factor: float = 1.0,
    dust_loss: float = 0.97,
    inverter_efficiency: float = 0.96,
    mismatch_loss: float = 0.98,
    wiring_loss: float = 0.98,
    degradation_loss: float = 0.99,
) -> float:
    pr = (
        system_efficiency
        * temperature_factor
        * dust_loss
        * inverter_efficiency
        * mismatch_loss
        * wiring_loss
        * degradation_loss
    )
    return max(pr, 0.0)

def solar_calc( panel_wattage: float, number_of_panels: int, solar_irradiance: float, 
            performance_ratio: float, days_in_month: int ):
    system_kwp = (panel_wattage * number_of_panels) / 1000.0
    daily_solar_output = system_kwp * solar_irradiance * performance_ratio
    monthly_solar_output = daily_solar_output * days_in_month
    solar_score = min((solar_irradiance /6.0) * 100, 100)
    return {
        "system_kwp": system_kwp,
        "daily_solar_output": daily_solar_output,
        "monthly_solar_output": monthly_solar_output,
        "solar_score": solar_score
    }