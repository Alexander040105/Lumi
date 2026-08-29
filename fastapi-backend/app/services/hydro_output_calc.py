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
    catchment_area_km2: float = 1.0,
    runoff_coefficient_override: float | None = None,
    apply_flow_floor: bool = True,
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
        runoff_coefficient_override: If provided, use this C instead of
            computing from slope. Used when catchment enrichment data
            (drainage density, hypsometric integral) is available.
        apply_flow_floor: If True (default), apply the 0.001 m³/s floor.
            Set to False when enrichment data is used so genuinely dry
            areas show 0 hydro instead of a fake floor.

    Returns:
        Design flow rate in m³/s suitable for a micro-hydro intake.
    """
    # Small-catchment area (m²) — typical household micro-hydro
    # draws from 0.05–1.0 km² (Butchers et al., 2021; Feyissa et al., 2024)
    catchment_area_m2 = catchment_area_km2 * 1_000_000

    # Monthly precipitation depth (m)
    monthly_precip_m = rainfall_mm_monthly / 1000.0

    # Base runoff coefficient: use override if provided (enrichment data),
    # otherwise compute from slope (Javadinejad et al., 2022)
    if runoff_coefficient_override is not None:
        # Enriched RC already incorporates terrain morphology (drainage density,
        # hypsometric integral, catchment slope from Boothroyd et al. 2023).
        # Applying municipal terrain modifiers on top would double-count
        # terrain effects, artificially suppressing the coefficient.
        c_effective = runoff_coefficient_override
    else:
        c_base = estimate_runoff_coefficient(mean_slope_deg)
        # Adjust by terrain suitability factors for non-enriched path.
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
    # When enrichment data is used (apply_flow_floor=False), allow 0 so
    # genuinely dry areas show 0 hydro instead of a fake floor.
    if apply_flow_floor:
        return round(max(min(design_flow_cms, 0.5), 0.001), 6)
    return round(max(min(design_flow_cms, 0.5), 0.0), 6)


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
    head_factor: float = 0.20,
    feasibility_penalty: float | None = None,
    head_already_realistic: bool = False,
):
    """
    Micro-hydropower output calculation.

    P_elec = η_turbine × η_generator × ρ × g × Q × H

    Standard hydropower equation for run-of-river micro-hydro
    (Feyissa et al., 2024; Wang et al., 2025).

    Args:
        days_in_month: Days in current month
        flow_rate_cms: Design flow rate (m³/s)
        head_m: Hydraulic head (m) — DEM-derived municipal elevation drop,
            or stream-gradient-derived head if head_already_realistic=True
        water_density: 1000 kg/m³
        gravity: 9.81 m/s²
        turbine_efficiency: 0.70–0.85 for micro-hydro turbines
        generator_efficiency: 0.85–0.95
        feasibility_penalty: 0.1–1.0 multiplier from stream distance.
            If provided, multiplies final energy output.
        head_already_realistic: If True, head_m is already a realistic
            household-scale head (from stream gradient × penstock length)
            and should not be scaled by head_factor.

    Returns:
        Dict with available_power_kw, daily_energy_kwh, monthly_energy_kwh,
        hydro_score, design_flow_cms, and realistic_head_m.
    """
    # Realistic bounds for household micro-hydro.
    # Typical run-of-river micro-hydro: 0.001 – 0.5 m³/s
    # (Butchers et al., 2021; Lillo et al., 2021)
    flow_rate_cms = min(max(flow_rate_cms, 0.0), 0.5)

    # Realistic household-accessible head.
    if head_already_realistic:
        # Head was computed from stream gradient × penstock length —
        # already at household scale. Just clamp to physical bounds.
        realistic_head_m = min(max(head_m, 0.0), 50.0)
    else:
        # DEM-derived municipal head is scaled to a local intake-to-turbine drop.
        # Typical micro-hydro head: 2–25 m (Feyissa et al., 2024).
        # We assume only ~20 % of maximum municipal elevation drop is usable
        # for a single household run-of-river scheme (configurable via settings).
        realistic_head_m = min(max(head_m * head_factor, 2.0), 25.0)

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

    # Apply stream feasibility penalty (from catchment enrichment).
    # Reflects that a household far from the nearest stream cannot
    # economically build a penstock to reach it.
    if feasibility_penalty is not None and 0.0 <= feasibility_penalty <= 1.0:
        daily_energy *= feasibility_penalty
        monthly_energy *= feasibility_penalty

    # Hydro suitability score (0–100).
    # Normalise against 100 kWh/month — a realistic "good" household micro-hydro
    # output in the Philippines. Most sites produce 0–5 kWh/month with catchment
    # enrichment; 100 kWh represents an excellent site with good head and flow.
    # (Feyissa et al. 2024 report 500–2000 kWh/month for ideal sites; we use a
    # conservative PH-specific baseline since most catchments have very low gradient.)
    hydro_score = normalize(monthly_energy, 0, 100) * 100

    return {
        "available_power_kw": round(electrical_power_kw, 3),
        "daily_energy_kwh": round(daily_energy, 3),
        "monthly_energy_kwh": round(monthly_energy, 3),
        "hydro_score": round(hydro_score, 2),
        "design_flow_cms": round(flow_rate_cms, 6),
        "realistic_head_m": round(realistic_head_m, 2),
    }