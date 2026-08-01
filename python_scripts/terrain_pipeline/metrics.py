from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class SuitabilityWeights:
    head: float
    slope: float
    ruggedness: float


@dataclass(frozen=True)
class NormalizationCaps:
    head_m: float
    slope_deg: float
    ruggedness_m: float


def normalize(value: Optional[float], max_value: float) -> float:
    if value is None or np.isnan(value) or max_value <= 0:
        return 0.0
    return max(0.0, min(1.0, value / max_value))


def slope_classification(
    slope_deg: float,
    flat: float,
    gentle: float,
    moderate: float,
    steep: float,
) -> str:
    if np.isnan(slope_deg):
        return "unknown"
    if slope_deg < flat:
        return "flat"
    if slope_deg < gentle:
        return "gentle"
    if slope_deg < moderate:
        return "moderate"
    if slope_deg < steep:
        return "steep"
    return "very_steep"


def elevation_classification(elevation_m: float, low: float, mid: float, high: float) -> str:
    if np.isnan(elevation_m):
        return "unknown"
    if elevation_m < low:
        return "low"
    if elevation_m < mid:
        return "mid"
    if elevation_m < high:
        return "high"
    return "very_high"


def terrain_flatness(slope_deg: float, max_slope_deg: float) -> float:
    return 1.0 - normalize(slope_deg, max_slope_deg)


def runoff_potential(slope_deg: float, elevation_m: float, caps: NormalizationCaps) -> float:
    return normalize(slope_deg, caps.slope_deg) * normalize(elevation_m, caps.head_m)


def gravity_flow_potential(head_m: float, slope_deg: float, caps: NormalizationCaps) -> float:
    return normalize(head_m, caps.head_m) * normalize(slope_deg, caps.slope_deg)


def hydro_suitability_score(
    head_m: float,
    slope_deg: float,
    ruggedness_m: float,
    weights: SuitabilityWeights,
    caps: NormalizationCaps,
) -> float:
    head_score = normalize(head_m, caps.head_m)
    slope_score = normalize(slope_deg, caps.slope_deg)
    rugged_score = normalize(ruggedness_m, caps.ruggedness_m)
    total = weights.head * head_score + weights.slope * slope_score + weights.ruggedness * rugged_score
    return max(0.0, min(1.0, total))


def terrain_exposure_index(max_elev: float, mean_elev: float, ruggedness_m: float) -> float:
    if np.isnan(max_elev) or np.isnan(mean_elev) or np.isnan(ruggedness_m):
        return float("nan")
    return float((max_elev - mean_elev) / (ruggedness_m + 1e-6))
