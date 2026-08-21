from pydantic import BaseModel, Field
from typing import Any


class AnalyzeChartRequest(BaseModel):
    chart_type: str = Field(..., description="Type of chart to analyze: trends, sources, or map")
    chart_data: dict[str, Any] = Field(default_factory=dict, description="Contextual data for the chart")


class AnalyzeChartResponse(BaseModel):
    insight: str
    recommendation: str = ""
    data_year: int
    chart_type: str = ""
    remaining_anonymous_requests: int | None = None


class MapExplanationResponse(BaseModel):
    insight: str
    recommendation: str = ""
    data_year: int
    chart_type: str = ""
    remaining_anonymous_requests: int | None = None


class LatestStatisticsResponse(BaseModel):
    year: int
    total_consumption_gwh: float
    total_peak_demand_mw: float
    total_generation_gwh: float
    renewable_generation_gwh: float
    renewable_share_pct: float
    capacity_margin_mw: float | None = None
    capacity_margin_pct: float | None = None


class HistoricalTrendsResponse(BaseModel):
    years: list[int]
    series: dict[str, list[float | None]]


class ForecastResponse(BaseModel):
    forecast_years: list[int]
    forecast_values: list[float | None]
    ci_lower: list[float | None]
    ci_upper: list[float | None]
    model: str
    training_period: str
    test_period: str


class ModelComparisonItem(BaseModel):
    model: str
    mae: float
    rmse: float
    mape: float


class ModelComparisonResponse(BaseModel):
    items: list[ModelComparisonItem]


class SourceBreakdownResponse(BaseModel):
    year: int
    total_generation_gwh: float
    generation_gwh: dict[str, float]
    share_pct: dict[str, float]


class GridBreakdownResponse(BaseModel):
    year: int
    total_generation_gwh: float
    generation_gwh: dict[str, float]
    share_pct: dict[str, float]


class AiInsightResponse(BaseModel):
    insight: str
    recommendation: str
    data_year: int
    remaining_anonymous_requests: int | None = None


class OverviewResponse(BaseModel):
    latest: LatestStatisticsResponse
    forecast_summary: dict[str, Any]
    model_comparison: list[ModelComparisonItem]


class MapDataItem(BaseModel):
    region: str
    province: str | None = None
    municipality: str | None = None
    municipality_id: int | None = None
    value: float | None = None
    classification: str | None = None
    factors: Any = None
    metric: str
    lat: float | None = None
    lon: float | None = None
    nearby_plants: list[dict[str, Any]] | None = None


class MapDataResponse(BaseModel):
    items: list[MapDataItem]
    metric: str
    level: str = "province"


class TrendsResponse(BaseModel):
    years: list[int]
    series: dict[str, list[float | None]]
    forecast: ForecastResponse | None = None
    forecast_peak: ForecastResponse | None = None
    forecast_renewable: ForecastResponse | None = None
    source_breakdown: SourceBreakdownResponse | None = None
    grid_breakdown: GridBreakdownResponse | None = None


class ProvincialConsumptionItem(BaseModel):
    region: str
    sector: str
    value_mwh: float
    year: int


class ProvincialDemandResponse(BaseModel):
    items: list[ProvincialConsumptionItem]
    region: str | None = None
    note: str = "Values in MWh from DOE Annex 8 (2025)."


class MunicipalDemandEstimate(BaseModel):
    municipality_id: int
    municipality_name: str
    province_name: str
    estimated_demand_mwh: float
    method: str = "population_weighted_disaggregation"
    note: str = "Estimated from provincial DOE data using PSA population ratios. Actual demand may vary."


class MunicipalDemandResponse(BaseModel):
    items: list[MunicipalDemandEstimate]
    province: str | None = None
    note: str = ""


class IrenaCapacityItem(BaseModel):
    technology: str
    grid_connection: str
    year: int
    capacity_mw: float


class IrenaGenerationItem(BaseModel):
    technology: str
    grid_connection: str
    year: int
    generation_gwh: float


class IrenaRenewableShareItem(BaseModel):
    year: int
    renewable_share_pct: float


class IrenaOverviewResponse(BaseModel):
    capacity: list[IrenaCapacityItem]
    generation: list[IrenaGenerationItem]
    renewable_share: list[IrenaRenewableShareItem]
    note: str = "Data from IRENA. Displayed alongside DOE for benchmarking purposes."


class MeralcoRateResponse(BaseModel):
    rate_php_per_kwh: float | None
    year: int | None
    customer_class: str = "Residential"
    charge_component: str = "Generation Energy Charge"
    note: str = ""


class SolarAtlasItem(BaseModel):
    location: str
    lat: float
    lon: float
    ghi_kwh_m2_day: float | None
    dni_kwh_m2_day: float | None
    dif_kwh_m2_day: float | None
    pvout_kwh_kW_day: float | None
    temp_c: float | None


class SolarAtlasResponse(BaseModel):
    items: list[SolarAtlasItem]
    note: str = ""
