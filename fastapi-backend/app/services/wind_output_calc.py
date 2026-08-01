import os
import math
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATA_PATH = os.path.join(
	BASE_DIR,
	"fastapi-backend",
	"app",
	"services",
	"local_data",
	"wind_products_joined_betz.csv",
)

def load_wind_averages(csv_path: str = DATA_PATH) -> dict:
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


load_wind_averages = load_wind_averages()
avg_rotor_radius_m = load_wind_averages["avg_rotor_radius_m"]
avg_power_coefficient = load_wind_averages["avg_power_coefficient"]
avg_rotos_summary= load_wind_averages["summary_rotor"]
avg_cp_summary = load_wind_averages["summary_cp"]


def calculate_wind_output(
    wind_speed_mps: float,
    days_in_month: int,
    air_density: float,
    rotor_radius_m: float = avg_rotor_radius_m,
    cp: float = avg_power_coefficient / 100,
    efficiency: float = 0.90,
    capacity_factor: float = 0.30,  # NEW: 30% typical for small turbines [Baker et al., 2023]
    operating_hours_per_day: int = 24,
) -> dict:
    """
    Calculate wind turbine power output and energy production.
    
    Based on the fundamental wind power equation:
    P = 0.5 × ρ × A × V³ × Cp × η 
    - Fahim, A., Al-Mamun, A., & Hassan, M. A. (2024). 
    Toward a physics-based model of power coefficient in horizontal-axis wind turbines. 
    Wind Engineering, 48(3), 245–262. https://doi.org/10.1177/0309524X241263600
    
    Args:
        rotor_radius_m: Rotor radius in meters
        wind_speed_mps: Wind speed in m/s (from ws10m in schema)
        air_density: Air density in kg/m³ (from rhoa in schema, default 1.225) [Kumar et al., 2022]
        cp: Power coefficient (0.40 typical for HAWT, 0.10-0.25 for VAWT) [Alam & Jin, 2023]
        efficiency: Mechanical/electrical efficiency (0.85-0.95 typical) [Andersen & Jonassen, 2025]
        capacity_factor: Fraction of time turbine produces at rated power (0.20-0.40 typical) [Baker et al., 2023]
        operating_hours_per_day: Hours per day (typically 24)
        days_in_month: Days in month (typically 30)
    
    Returns:
        Dictionary with swept area, power, and energy estimates
    """
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
    
    # Calculate rated power: P = 0.5 × ρ × A × V³ × Cp × η [Fahim et al., 2024]
    power_watts = (
        0.5 *
        air_density *
        swept_area *
        (wind_speed_mps ** 3) *
        cp *
        efficiency
    )
    
    power_kw = power_watts / 1000.0
    
    # Apply capacity factor for realistic energy production [Baker et al., 2023]
    # Without capacity factor: assumes 100% operation at rated power (unrealistic)
    # With capacity factor: accounts for variable wind, maintenance, cut-in/out speeds
    effective_hours_per_day = operating_hours_per_day * capacity_factor
    
    daily_energy_kwh = power_kw * effective_hours_per_day
    monthly_energy_kwh = daily_energy_kwh * days_in_month
    
    return {
        "swept_area_m2": round(swept_area, 4),
        "rated_power_kw": round(power_kw, 4),
        "capacity_factor": capacity_factor,
        "effective_operating_hours_per_day": round(effective_hours_per_day, 2),
        "daily_energy_kwh": round(daily_energy_kwh, 4),
        "monthly_energy_kwh": round(monthly_energy_kwh, 4),
    }