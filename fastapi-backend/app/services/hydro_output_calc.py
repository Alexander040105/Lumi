def normalize(value, min_value, max_value):
    if value is None:
        return 0.0
    if max_value == min_value:
        return 0.0
    return max(0.0, min(1.0, (value - min_value) / (max_value - min_value)))


def estimate_runoff_coefficient(slope_deg: float | None) -> float:
    """
    Simple runoff coefficient approximation.

    ```
    Based on terrain slope literature.
    """
    if slope_deg is None:
        return 0.45
    if slope_deg < 3:
        return 0.30
    if slope_deg < 10:
        return 0.45
    if slope_deg < 20:
        return 0.60
    return 0.75

def estimated_flow_rate(rainfall_mm_monthly: float, runoff_potential: float, watershed_gradient: float,
    mean_slope_deg: float, gravity_flow_potential: float) -> float:
    """
    Terrain-weighted discharge proxy.

    Returns estimated flow rate (m³/s).

    This is NOT gauge-measured discharge.
    It is a terrain-assisted hydrological proxy.
    
    Function Parameter	    Database Column
    rainfall_mm_monthly	    municipality_climate_monthly.prectotcorr
    runoff_potential	    hydropower_suitability.runoff_potential
    watershed_gradient	    hydropower_suitability.watershed_gradient
    mean_slope_deg	        hydropower_suitability.mean_slope_deg
    gravity_flow_potential	hydropower_suitability.gravity_flow_potential
    """
    rainfall_factor = (rainfall_mm_monthly / 300.0)
    slope_factor = normalize( mean_slope_deg, 0, 45 )
    gradient_factor = normalize(watershed_gradient, 0,0.25)
    flow_index = (0.40 * runoff_potential + 0.25 * gravity_flow_potential 
                + 0.20 * slope_factor
                + 0.15 * gradient_factor)
    estimated_flow_rate = (rainfall_factor * flow_index * 25)

    return round(max(estimated_flow_rate, 0.1),4)

def estimate_discharge(rainfall_mm_monthly: float, basin_area_km2: float, runoff_coefficient: float ) -> float:
    """
    Rational-method inspired runoff estimation.
    Q = (P × A × C) / seconds_year
    """
    annual_precip_m = (rainfall_mm_monthly * 12) / 1000.0
    basin_area_m2 = (basin_area_km2 * 1_000_000)
    q = (annual_precip_m * basin_area_m2 *runoff_coefficient) / 31_536_000
    
    return max(q, 0.0)

def calculate_hydropower(days_in_month: int, flow_rate_cms: float, head_m: float,
        water_density: float = 1000.0, gravity: float = 9.81,
        turbine_efficiency: float = 0.85, generator_efficiency: float = 0.95) -> dict:
    """
    Hydropower equation:
    P = ρ . g . h . Q
    
    Source: https://www.irejournals.com/formatedpaper/1704572.pdf Page 8 hehe
    """
    # flow_rate_cms is yung galing sa estimated_flow_rate function, which should already be non-negative, but we safeguard here just in case
    if flow_rate_cms < 0:
        flow_rate_cms = 0.0
    # hydraulic_head_m is yung galing sa municipality_terrain_metrics table, which should also be non-negative, but we safeguard here as well
    if head_m < 0:
        head_m = 0.0
    power_kw = (water_density * gravity * head_m * flow_rate_cms) / 1000.0  # convert to kW
    overall_efficiency = turbine_efficiency * generator_efficiency
    effective_power_kw = power_kw * overall_efficiency
    daily_hydro_output = effective_power_kw * 24.0
    monthly_hydro_output = daily_hydro_output * days_in_month
    hydro_score = min((flow_rate_cms / 10.0) * 100, 100)  # simplistic scoring based on flow rate, capped at 100
    return {
        "system_kwp": power_kw,
        "daily_hydro_output": daily_hydro_output,
        "monthly_hydro_output": monthly_hydro_output,
        "hydro_score": hydro_score
    }

