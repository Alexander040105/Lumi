"""Confidence and uncertainty scoring for LUMI EcoSim.

Propagates data quality and model uncertainty into a confidence score
(0-100) for each energy type assessment. Higher = more confident.

Factors:
- Data coverage: how many climate variables are available
- Data recency: how recent is the climate data
- Spatial resolution: NASA POWER ~0.5° vs high-res source
- Model maturity: empirical vs physics-based
- Input completeness: were user inputs provided or defaulted
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConfidenceFactors:
    """Factors that influence confidence score."""
    has_climate_data: bool = False
    climate_variables_count: int = 0
    climate_data_year: int | None = None
    has_terrain_data: bool = False
    has_population_data: bool = False
    has_tariff_data: bool = False
    user_provided_inputs: bool = False
    energy_type: str = ""


def _score_data_coverage(f: ConfidenceFactors) -> float:
    """Score 0-1 based on how much data is available."""
    score = 0.0
    max_vars = 10  # T2M, T2M_MAX, T2M_MIN, RH2M, PRECTOTCORR, WS10M, ALLSKY_SFC_SW_DWN, CLOUD_AMT, PS, RHOA

    if f.has_climate_data:
        score += 0.3
        score += 0.3 * min(f.climate_variables_count / max_vars, 1.0)

    if f.has_terrain_data:
        score += 0.15

    if f.has_population_data:
        score += 0.1

    if f.has_tariff_data:
        score += 0.1

    if f.user_provided_inputs:
        score += 0.05

    return min(score, 1.0)


def _score_data_recency(f: ConfidenceFactors) -> float:
    """Score 0-1 based on how recent the climate data is."""
    if f.climate_data_year is None:
        return 0.3  # Unknown recency — low confidence

    current_year = 2025
    age = current_year - f.climate_data_year
    if age <= 2:
        return 1.0
    if age <= 5:
        return 0.8
    if age <= 10:
        return 0.6
    return 0.4


def _score_model_maturity(energy_type: str) -> float:
    """Score 0-1 based on model sophistication."""
    maturity = {
        "solar": 0.85,      # Well-established irradiance → output models
        "wind": 0.70,       # Good but wind is inherently more variable
        "hydro": 0.65,      # Improved with catchment enrichment (Boothroyd et al. 2023)
        "geothermal": 0.40, # Sparse data, IDW interpolation
    }
    return maturity.get(energy_type, 0.5)


def _score_spatial_resolution(energy_type: str) -> float:
    """Score 0-1 based on spatial resolution of source data."""
    # NASA POWER is ~0.5° (~50km) — coarse for municipal-level assessment
    # This is the same for all types currently
    return 0.55


def calculate_confidence(f: ConfidenceFactors) -> dict[str, Any]:
    """Calculate overall confidence score and contributing factors.

    Args:
        f: ConfidenceFactors describing data availability

    Returns:
        Dict with overall_score (0-100), factor breakdown, and confidence label
    """
    coverage = _score_data_coverage(f)
    recency = _score_data_recency(f)
    maturity = _score_model_maturity(f.energy_type)
    resolution = _score_spatial_resolution(f.energy_type)

    # Weighted average
    weights = {
        "coverage": 0.35,
        "recency": 0.15,
        "model_maturity": 0.30,
        "spatial_resolution": 0.20,
    }

    overall = (
        coverage * weights["coverage"]
        + recency * weights["recency"]
        + maturity * weights["model_maturity"]
        + resolution * weights["spatial_resolution"]
    )

    score = round(overall * 100, 1)

    if score >= 75:
        label = "High"
    elif score >= 55:
        label = "Moderate"
    elif score >= 35:
        label = "Low"
    else:
        label = "Very Low"

    return {
        "confidence_score": score,
        "confidence_label": label,
        "factors": {
            "data_coverage": round(coverage * 100, 1),
            "data_recency": round(recency * 100, 1),
            "model_maturity": round(maturity * 100, 1),
            "spatial_resolution": round(resolution * 100, 1),
        },
        "weights": weights,
        "recommendations": _generate_recommendations(f, coverage, recency, maturity, resolution),
    }


def _generate_recommendations(
    f: ConfidenceFactors,
    coverage: float,
    recency: float,
    maturity: float,
    resolution: float,
) -> list[str]:
    """Generate actionable recommendations to improve confidence."""
    recs: list[str] = []

    if not f.has_climate_data:
        recs.append("Fetch NASA POWER climate data for this municipality to enable energy calculations.")
    elif f.climate_variables_count < 8:
        recs.append(f"Only {f.climate_variables_count}/10 climate variables available. Fetch complete NASA POWER data.")

    if recency < 0.6:
        recs.append("Climate data is outdated. Re-fetch from NASA POWER for the latest period.")

    if not f.has_terrain_data and f.energy_type in ("hydro", "wind"):
        recs.append("Add DEM-derived terrain data (slope, elevation) for more accurate site assessment.")

    if not f.has_tariff_data:
        recs.append("Add DU tariff data for accurate financial savings calculations.")

    if resolution < 0.7:
        recs.append("Consider higher-resolution data sources (Global Solar Atlas, Global Wind Atlas) for improved accuracy.")

    if f.energy_type == "hydro" and maturity < 0.6:
        recs.append("Rational method provides rough estimates only. Consider streamflow data for reliable hydro assessment.")

    if f.energy_type == "geothermal" and maturity < 0.5:
        recs.append("Geothermal assessment is limited by sparse heat-flow data. Consult PHIVOLCS/DOE prospectivity maps.")

    return recs
