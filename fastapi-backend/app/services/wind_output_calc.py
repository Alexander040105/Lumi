import logging
import math
import os
import pandas as pd

from app.services.data_cache import cache_get_sync, cache_set_sync
from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATA_PATH = os.path.join(
	BASE_DIR,
	"fastapi-backend",
	"app",
	"services",
	"local_data",
	"wind_products_joined_betz.csv",
)

_wind_summary: dict | None = None


def _compute_wind_averages(csv_path: str) -> dict:
	df = pd.read_csv(csv_path)
	df["rotor_radius_m"] = pd.to_numeric(df["rotor_radius_m"], errors="coerce")
	df["power_coefficient"] = pd.to_numeric(df["power_coefficient"], errors="coerce")

	rotor_series = df["rotor_radius_m"].dropna()
	cp_series = df["power_coefficient"].dropna()

	avg_rotor_radius_m = float(rotor_series.mean()) if not rotor_series.empty else 0.0
	avg_power_coefficient = float(cp_series.mean()) if not cp_series.empty else 0.0

	summary_rotor = (
		"Average rotor radius (m): "
		f"{avg_rotor_radius_m:.3f} from {len(rotor_series)} rows where a blade diameter was parsed "
		"from text (m/cm/mm/in/ft), then divided by 2."
	)
	summary_cp = (
		"Average power coefficient: "
		f"{avg_power_coefficient:.3f} from {len(cp_series)} rows with both parsed power (W/kW/MW) and diameter; "
		"uses Cp = P / (0.5 * 1.225 * A * V^3) with V=12.0 m/s unless a m/s value is present."
	)

	return {
		"avg_rotor_radius_m": avg_rotor_radius_m,
		"avg_power_coefficient": avg_power_coefficient * 100,
		"rotor_count": len(rotor_series),
		"cp_count": len(cp_series),
		"summary_rotor": summary_rotor,
		"summary_cp": summary_cp,
	}


def load_wind_averages(csv_path: str | None = None) -> dict:
	global _wind_summary
	if _wind_summary is not None:
		return _wind_summary

	cache_key = "wind:summary:betz"
	cached = cache_get_sync(cache_key)
	if cached is not None:
		_wind_summary = cached
		return _wind_summary

	try:
		client = get_supabase_client()
		resp = (
			client.table("wind_products_summary")
			.select("*")
			.eq("variant", "betz")
			.single()
			.execute()
		)
		if resp.data:
			_wind_summary = resp.data
			cache_set_sync(cache_key, resp.data, ttl=86400)
			return _wind_summary
	except Exception as exc:
		logger.warning("Failed to load wind summary from Supabase: %s", exc)

	if os.getenv("USE_LOCAL_DATA_FALLBACK", "").lower() == "true":
		path = csv_path or DATA_PATH
		if os.path.exists(path):
			_wind_summary = _compute_wind_averages(path)
			return _wind_summary

	logger.warning("Wind summary unavailable; using default Betz parameters")
	_wind_summary = {
		"avg_rotor_radius_m": 6.2,
		"avg_power_coefficient": 35.0,
		"rotor_count": 0,
		"cp_count": 0,
		"summary_rotor": "Using default residential rotor radius; no product data could be loaded.",
		"summary_cp": "Using default power coefficient; no product data could be loaded.",
	}
	return _wind_summary


avg_rotor_radius_m = None
avg_power_coefficient = None
avg_rotos_summary = None
avg_cp_summary = None


def extrapolate_wind_speed(
    wind_speed_ref: float,
    ref_height_m: float,
    target_height_m: float,
    shear_exponent: float = 0.143,
) -> float:
    """Extrapolate wind speed from reference height to target height using the power law.

    V(h) = V_ref × (h / h_ref)^α

    Uses the 1/7 power law (α=0.143) per the NREL Wind Energy Resource Atlas
    of the Philippines, which chose 30m as the reference height for Philippine
    wind resource classification — a compromise between utility-scale (30–60m)
    and small rural wind turbines (15–30m).
    """
    if wind_speed_ref <= 0 or ref_height_m <= 0 or target_height_m <= 0:
        return 0.0
    return wind_speed_ref * (target_height_m / ref_height_m) ** shear_exponent


def calculate_wind_output(
    wind_speed_mps: float,
    days_in_month: int,
    air_density: float,
    rotor_radius_m: float | None = None,
    cp: float | None = None,
    efficiency: float = 0.90,
    capacity_factor: float | None = None,
    operating_hours_per_day: int = 24,
    cut_in_speed_mps: float | None = None,
    rated_speed_mps: float | None = None,
    cut_out_speed_mps: float | None = None,
    rated_power_kw: float | None = None,
) -> dict:
    """
    Calculate wind turbine power output and energy production using a
    household-scale power curve.

    The power curve has three regions:
    - Below cut-in speed: 0 W
    - Between cut-in and rated: physical cubic power P = 0.5 × ρ × A × V³ × Cp × η,
      capped at rated power
    - Between rated and cut-out: rated power
    - Above cut-out: 0 W

    References:
    - Fahim, A., Al-Mamun, A., & Hassan, M. A. (2024). Toward a physics-based
      model of power coefficient in horizontal-axis wind turbines. Wind
      Engineering, 48(3), 245–262.
    - Baker et al. (2023). Small wind turbine capacity factors.

    Args:
        rotor_radius_m: Rotor radius in meters. Defaults to the household
            wind-product average if not provided.
        wind_speed_mps: Wind speed at hub height in m/s.
        air_density: Air density in kg/m³ (default 1.225) [Kumar et al., 2022].
        cp: Power coefficient (0.10–0.45 typical for small turbines).
        efficiency: Mechanical/electrical efficiency (0.85–0.95 typical).
        capacity_factor: Fraction of time the turbine is producing usable power
            (0.20–0.40 typical for small turbines).
        operating_hours_per_day: Hours per day (typically 24).
        days_in_month: Days in month (typically 30).
        cut_in_speed_mps: Cut-in wind speed (default 3 m/s).
        rated_speed_mps: Rated wind speed (default 11 m/s).
        cut_out_speed_mps: Cut-out wind speed (default 25 m/s).
        rated_power_kw: Rated power cap (default 1.2 kW).

    Returns:
        Dictionary with swept area, rated power, capacity factor, and energy.
    """
    # Load defaults from settings for any power-curve parameter not provided.
    if capacity_factor is None or cut_in_speed_mps is None or rated_speed_mps is None or cut_out_speed_mps is None or rated_power_kw is None:
        from app.config.settings import get_settings
        defaults = get_settings()
        if capacity_factor is None:
            capacity_factor = float(defaults.household_wind_capacity_factor)
        if cut_in_speed_mps is None:
            cut_in_speed_mps = float(defaults.household_wind_cut_in_mps)
        if rated_speed_mps is None:
            rated_speed_mps = float(defaults.household_wind_rated_mps)
        if cut_out_speed_mps is None:
            cut_out_speed_mps = float(defaults.household_wind_cut_out_mps)
        if rated_power_kw is None:
            rated_power_kw = float(defaults.household_wind_rated_power_kw)

    if rotor_radius_m is None or cp is None:
        summary = load_wind_averages()
        if rotor_radius_m is None:
            rotor_radius_m = float(summary["avg_rotor_radius_m"])
        if cp is None:
            cp = float(summary["avg_power_coefficient"]) / 100

    # Validate inputs
    if rotor_radius_m <= 0 or wind_speed_mps <= 0:
        raise ValueError("Rotor radius and wind speed must be positive values")

    if not 0.9 <= air_density <= 1.3:
        raise ValueError("Air density should be in realistic range (0.9-1.3 kg/m³)")

    if cp > 0.593:
        raise ValueError(f"Cp ({cp}) exceeds Betz limit (0.593) [González-Hernández & Salas-Cabrera, 2021]")

    if not 0 <= capacity_factor <= 1:
        raise ValueError("Capacity factor must be between 0 and 1")

    # Calculate swept area: A = π × r² [Fahim et al., 2024]
    swept_area = math.pi * (rotor_radius_m ** 2)

    # Instantaneous power from the physical cubic equation.
    # This is the *potential* power at the given wind speed before the
    # power-curve cap is applied.
    raw_power_watts = (
        0.5 *
        air_density *
        swept_area *
        (wind_speed_mps ** 3) *
        cp *
        efficiency
    )
    raw_power_kw = raw_power_watts / 1000.0

    # Apply household power curve.
    if wind_speed_mps < cut_in_speed_mps or wind_speed_mps >= cut_out_speed_mps:
        power_kw = 0.0
    elif wind_speed_mps >= rated_speed_mps:
        power_kw = rated_power_kw
    else:
        # Between cut-in and rated: use the smaller of the physical power
        # and the rated-power cap. This keeps the cubic shape but prevents
        # unrealistic overproduction at low wind for large rotors.
        power_kw = min(raw_power_kw, rated_power_kw)

    # Apply capacity factor for realistic energy production [Baker et al., 2023].
    # The capacity factor accounts for the turbine being below cut-in, above
    # cut-out, or down for maintenance, not for the rated-power cap itself.
    effective_hours_per_day = operating_hours_per_day * capacity_factor

    daily_energy_kwh = power_kw * effective_hours_per_day
    monthly_energy_kwh = daily_energy_kwh * days_in_month

    return {
        "swept_area_m2": round(swept_area, 4),
        "raw_rated_power_kw": round(raw_power_kw, 4),
        "rated_power_kw": round(power_kw, 4),
        "capacity_factor": capacity_factor,
        "effective_operating_hours_per_day": round(effective_hours_per_day, 2),
        "daily_energy_kwh": round(daily_energy_kwh, 4),
        "monthly_energy_kwh": round(monthly_energy_kwh, 4),
    }