import math
from typing import Optional

BETZ_LIMIT = 16 / 27


def compute_power_coefficient(
    power_w: float,
    diameter_m: float,
    wind_speed_mps: float,
    air_density: float = 1.225,
    clamp_to_betz: bool = False,
) -> Optional[float]:
    if power_w <= 0 or diameter_m <= 0 or wind_speed_mps <= 0:
        return None
    if not 0.9 <= air_density <= 1.3:
        return None

    radius_m = diameter_m / 2.0
    area = math.pi * radius_m ** 2
    available_wind_power = 0.5 * air_density * area * (wind_speed_mps ** 3)
    if available_wind_power <= 0:
        return None

    cp = power_w / available_wind_power

    if clamp_to_betz:
        return min(cp, BETZ_LIMIT)

    return None if cp > BETZ_LIMIT else cp


def validate_power_coefficient(cp: Optional[float]) -> dict:
    if cp is None:
        return {"valid": False, "category": "invalid", "message": "Calculation failed"}
    if cp <= 0:
        return {"valid": False, "category": "impossible", "message": "Cp must be positive"}
    if cp > BETZ_LIMIT:
        return {
            "valid": False,
            "category": "exceeds_betz",
            "message": f"Cp ({cp:.3f}) exceeds Betz limit ({BETZ_LIMIT:.3f})",
        }

    if cp < 0.25:
        category = "low_efficiency"
    elif cp < 0.35:
        category = "moderate_efficiency"
    elif cp < 0.45:
        category = "good_efficiency"
    elif cp < 0.50:
        category = "excellent_efficiency"
    else:
        category = "near_betz_limit"

    return {
        "valid": True,
        "category": category,
        "cp_decimal": cp,
        "cp_percent": cp * 100,
        "betz_ratio": cp / BETZ_LIMIT,
    }
