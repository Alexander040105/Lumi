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


class LatestStatisticsResponse(BaseModel):
    year: int
    total_consumption_gwh: float
    total_peak_demand_mw: float
    total_generation_gwh: float
    renewable_generation_gwh: float
    renewable_share_pct: float
    capacity_margin_mw: float
    capacity_margin_pct: float


class HistoricalTrendsResponse(BaseModel):
    years: list[int]
    series: dict[str, list[float]]


class ForecastResponse(BaseModel):
    forecast_years: list[int]
    forecast_values: list[float]
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


class OverviewResponse(BaseModel):
    latest: LatestStatisticsResponse
    forecast_summary: dict[str, Any]
    model_comparison: list[ModelComparisonItem]


class MapDataItem(BaseModel):
    region: str
    province: str | None = None
    municipality: str | None = None
    value: float | None = None
    metric: str
    lat: float | None = None
    lon: float | None = None


class MapDataResponse(BaseModel):
    items: list[MapDataItem]
    metric: str


class TrendsResponse(BaseModel):
    years: list[int]
    series: dict[str, list[float]]
    forecast: ForecastResponse | None = None
    source_breakdown: SourceBreakdownResponse | None = None
    grid_breakdown: GridBreakdownResponse | None = None
