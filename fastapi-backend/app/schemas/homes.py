from uuid import UUID

from pydantic import BaseModel, Field


class HomeCreate(BaseModel):
    name: str = Field(default="My Home", min_length=1, max_length=100)
    municipality_id: int = Field(..., gt=0)
    monthly_consumption_kwh: float = Field(..., gt=0)
    monthly_bill_php: float = Field(..., gt=0)
    desired_savings_pct: float = Field(default=0.50, ge=0.0, le=1.0)


class HomeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    municipality_id: int | None = Field(default=None, gt=0)


class HomeEnergyProfileCreate(BaseModel):
    monthly_consumption_kwh: float = Field(..., gt=0)
    monthly_bill_php: float = Field(..., gt=0)
    desired_savings_pct: float = Field(default=0.50, ge=0.0, le=1.0)


class HomeResponse(BaseModel):
    home_id: UUID
    user_id: UUID
    name: str
    municipality_id: int
    municipality_name: str | None = None
    created_at: str
    updated_at: str | None = None


class HomeDetailResponse(BaseModel):
    home_id: UUID
    user_id: UUID
    name: str
    municipality_id: int
    municipality_name: str | None = None
    latest_profile: dict | None = None
    total_simulations: int
    total_carbon_reduction_kg: float
    avg_independence_score: float | None = None
    created_at: str
    updated_at: str | None = None


class HomeListResponse(BaseModel):
    items: list[HomeResponse]


class SimulationCreate(BaseModel):
    simulation_name: str = Field(default="Simulation", max_length=200)
    panel_wattage: int = Field(default=400, gt=0)
    number_of_panels: int = Field(default=2, ge=0)
    include_battery: bool = False
    battery_kwh: float = Field(default=0, ge=0)
    # outputs from ecosim engine
    recommended_source: str
    suitability_score: float
    estimated_generation_kwh: float
    monthly_savings_php: float
    installation_cost_php: float
    payback_years: float
    carbon_reduction_kg: float
    independence_score: float
    results_json: dict | None = None
    ai_analysis_json: dict | None = None


class SimulationResponse(BaseModel):
    simulation_id: UUID
    home_id: UUID
    simulation_name: str
    recommended_source: str | None = None
    suitability_score: float | None = None
    estimated_generation_kwh: float | None = None
    monthly_savings_php: float | None = None
    installation_cost_php: float | None = None
    payback_years: float | None = None
    carbon_reduction_kg: float | None = None
    independence_score: float | None = None
    created_at: str


class SimulationListResponse(BaseModel):
    items: list[SimulationResponse]


class SimulationDetailResponse(SimulationResponse):
    results_json: dict | None = None
    ai_analysis_json: dict | None = None


class SimulationComparisonCreate(BaseModel):
    comparison_name: str = Field(default="Comparison", max_length=200)
    simulation_ids: list[UUID] = Field(..., min_length=2, max_length=3)


class SimulationComparisonResponse(BaseModel):
    comparison_id: UUID
    home_id: UUID
    comparison_name: str
    simulation_ids: list[UUID]
    created_at: str


class DashboardStatsResponse(BaseModel):
    total_homes: int
    total_simulations: int
    total_carbon_reduction_kg: float
    avg_independence_score: float
    best_recommended_source: str | None = None
    latest_simulation_date: str | None = None
