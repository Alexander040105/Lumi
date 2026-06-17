from pydantic import BaseModel, Field
from typing import Any


class GeothermalSuitabilityResponse(BaseModel):
    municipality_id: int
    heat_flow_score: float | None = None
    fault_density: float | None = None
    fault_distance_km: float | None = None
    volcano_distance_km: float | None = None
    aquifer_score: float | None = None
    temperature_score: float | None = None
    geothermal_score: float | None = None
    classification: str | None = None


class GeothermalOutputResponse(BaseModel):
    municipality_id: int
    reservoir_temperature_c: float | None = None
    estimated_flow_rate_kg_s: float | None = None
    thermal_power_mw: float | None = None
    electric_power_mw: float | None = None
    annual_energy_gwh: float | None = None
    confidence_score: float | None = None
    source: str | None = None
    assumption: str | None = None


class GeothermalAnalysisResponse(BaseModel):
    suitability: GeothermalSuitabilityResponse | None = None
    output: GeothermalOutputResponse | None = None


class GeothermalSimulationParams(BaseModel):
    municipality_id: int = Field(..., gt=0)
    heat_flow_score: float | None = None
    fault_distance_km: float | None = None
    volcano_distance_km: float | None = None
    aquifer_score: float | None = None
    reservoir_temperature_c: float | None = None
    estimated_flow_rate_kg_s: float | None = None
    classification: str | None = None


class GeothermalDashboardSummary(BaseModel):
    province: str
    avg_geothermal_score: float
    total_electric_potential_mw: float
    classification_counts: dict[str, int]
