import calendar
import datetime as dt
import datetime


def normalize(value, min_value, max_value):
    if value is None:
        return 0.0
    if max_value == min_value:
        return 0.0
    return max(0.0, min(1.0, (value - min_value) / (max_value - min_value)))


def estimate_runoff_coefficient(slope_deg: float | None) -> float:
    """
    Runoff coefficient for small catchments.

    Based on terrain slope literature (Javadinejad et al., 2022):
    - Gentle slopes (<3°): C = 0.30 (forested/pasture)
    - Moderate slopes (3–10°): C = 0.45 (mixed land use)
    - Steep slopes (10–20°): C = 0.60 (cultivated/hilly)
    - Very steep (>20°): C = 0.75 (rocky/urban)
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


def estimated_flow_rate(
    rainfall_mm_monthly: float,
    runoff_potential: float,
    watershed_gradient: float,
    mean_slope_deg: float,
    gravity_flow_potential: float,
    catchment_area_km2: float = 0.5,
) -> float:
    """
    Small-catchment runoff estimation for household micro-hydro.

    Uses a rational-method inspired approach adapted for
    ungauged small catchments (Javadinejad et al., 2022):

        Q_design = (C × P × A) / seconds_month × design_factor

    where:
        C = runoff coefficient (0.30–0.75)
        P = monthly precipitation (m)
        A = catchment area (m²)
        design_factor = fraction of flow usable for power
                        (accounts for environmental reserve)

    Args:
        rainfall_mm_monthly: Monthly rainfall in mm (NASA POWER prectotcorr)
        runoff_potential: Terrain runoff potential (0–1)
        watershed_gradient: Watershed steepness proxy (0–1)
        mean_slope_deg: Mean terrain slope in degrees
        gravity_flow_potential: Gravity flow feasibility (0–1)
        catchment_area_km2: Small local catchment in km² (default 0.5)

    Returns:
        Design flow rate in m³/s suitable for a micro-hydro intake.
    """
    # Small-catchment area (m²) — typical household micro-hydro
    # draws from 0.05–1.0 km² (Butchers et al., 2021; Feyissa et al., 2024)
    catchment_area_m2 = catchment_area_km2 * 1_000_000

    # Monthly precipitation depth (m)
    monthly_precip_m = rainfall_mm_monthly / 1000.0

    # Base runoff coefficient from slope (Javadinejad et al., 2022)
    c_base = estimate_runoff_coefficient(mean_slope_deg)

    # Adjust by terrain suitability factors.
    # Runoff potential and watershed gradient moderate the coefficient.
    c_effective = c_base * (0.5 + 0.5 * runoff_potential) * (0.7 + 0.3 * watershed_gradient)

    # Total monthly runoff volume (m³)
    monthly_runoff_m3 = c_effective * monthly_precip_m * catchment_area_m2

    # Average flow over the month (m³/s)
    seconds_month = 30 * 24 * 3600  # ~30 days
    avg_flow_cms = monthly_runoff_m3 / seconds_month

    # Design flow = 40 % of average flow × gravity-flow feasibility.
    # 40–60 % environmental flow reserve is standard for run-of-river
    # (Wang et al., 2025; Lillo et al., 2021)
    design_flow_cms = avg_flow_cms * 0.40 * max(gravity_flow_potential, 0.1)

    # Realistic bounds for household micro-hydro intake.
    # Typical small streams: 0.001 – 0.5 m³/s (Butchers et al., 2021)
    return round(max(min(design_flow_cms, 0.5), 0.001), 6)


def estimate_discharge(
    rainfall_mm_monthly: float,
    basin_area_km2: float,
    runoff_coefficient: float,
) -> float:
    """
    Rational-method inspired runoff estimation.

    Q = (P × A × C) / seconds_month
    """
    monthly_precip_m = rainfall_mm_monthly / 1000.0

    basin_area_m2 = basin_area_km2 * 1_000_000
    today = dt.datetime.now()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    seconds_month = datetime.timedelta(days=days_in_month).total_seconds()

    q = (
        monthly_precip_m *
        basin_area_m2 *
        runoff_coefficient
    ) / seconds_month

    return max(q, 0.0)


def calculate_hydropower(
    days_in_month: int,
    flow_rate_cms: float,
    head_m: float,
    water_density: float = 1000.0,
    gravity: float = 9.81,
    turbine_efficiency: float = 0.75,
    generator_efficiency: float = 0.90,
):
    """
    Micro-hydropower output calculation.

    P_elec = η_turbine × η_generator × ρ × g × Q × H

    Standard hydropower equation for run-of-river micro-hydro
    (Feyissa et al., 2024; Wang et al., 2025).

    Args:
        days_in_month: Days in current month
        flow_rate_cms: Design flow rate (m³/s)
        head_m: Hydraulic head (m) — DEM-derived municipal elevation drop
        water_density: 1000 kg/m³
        gravity: 9.81 m/s²
        turbine_efficiency: 0.70–0.85 for micro-hydro turbines
        generator_efficiency: 0.85–0.95

    Returns:
        Dict with available_power_kw, daily_energy_kwh, monthly_energy_kwh,
        hydro_score, design_flow_cms, and realistic_head_m.
    """
    # Realistic bounds for household micro-hydro.
    # Typical run-of-river micro-hydro: 0.001 – 0.5 m³/s
    # (Butchers et al., 2021; Lillo et al., 2021)
    flow_rate_cms = min(max(flow_rate_cms, 0.0), 0.5)

    # Realistic household-accessible head.
    # DEM-derived municipal head is scaled to a local intake-to-turbine drop.
    # Typical micro-hydro head: 2–25 m (Feyissa et al., 2024).
    # We assume only ~12 % of maximum municipal elevation drop is usable
    # for a single household run-of-river scheme.
    realistic_head_m = min(max(head_m * 0.12, 2.0), 25.0)

    # Hydraulic power (kW) = ρ × g × Q × H / 1000
    hydraulic_power_kw = (
        water_density * gravity * flow_rate_cms * realistic_head_m
    ) / 1000.0

    # Overall efficiency = turbine × generator.
    # Micro-hydro systems typically achieve 0.50–0.70 overall
    # (Feyissa et al., 2024; Wang et al., 2025)
    overall_efficiency = turbine_efficiency * generator_efficiency

    # Electrical power output (kW)
    electrical_power_kw = hydraulic_power_kw * overall_efficiency

    # Daily and monthly energy (kWh)
    daily_energy = electrical_power_kw * 24.0
    monthly_energy = daily_energy * days_in_month

    # Hydro suitability score (0–100).
    # Normalise against a realistic "excellent" micro-hydro output
    # of ~1 000 kWh/month for a household system.
    # (Feyissa et al., 2024 report 500–2 000 kWh/month for rural homes)
    hydro_score = normalize(monthly_energy, 0, 1000) * 100

    return {
        "available_power_kw": round(electrical_power_kw, 3),
        "daily_energy_kwh": round(daily_energy, 3),
        "monthly_energy_kwh": round(monthly_energy, 3),
        "hydro_score": round(hydro_score, 2),
        "design_flow_cms": round(flow_rate_cms, 6),
        "realistic_head_m": round(realistic_head_m, 2),
    }