from fastapi import APIRouter, Query

from app.schemas.energyhub import (
    AiInsightResponse,
    AnalyzeChartRequest,
    AnalyzeChartResponse,
    ForecastResponse,
    GridBreakdownResponse,
    MapDataResponse,
    ModelComparisonResponse,
    OverviewResponse,
    SourceBreakdownResponse,
    TrendsResponse,
)
from app.services.energyhub import get_energyhub_service

router = APIRouter()


@router.get("/overview", response_model=OverviewResponse)
async def get_overview():
    """Return the EnergyHub overview: latest statistics, forecast summary,
    and model comparison results."""
    svc = get_energyhub_service()
    return svc.build_overview()


@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
    metric: str = Query(default="consumption", description="Metric to forecast: consumption or peak_demand")
):
    """Return the ML forecast (2025-2030) with confidence intervals.

    The underlying model is ARIMA(1,1,1) trained on 2003-2020 data
    and evaluated on 2021-2024. Pre-computed forecasts are served
    directly without runtime retraining.
    """
    svc = get_energyhub_service()
    return svc.get_forecast(metric)


@router.get("/trends", response_model=TrendsResponse)
async def get_trends():
    """Return historical trends, forecast overlay, source breakdown,
    and grid-level breakdown for charting."""
    svc = get_energyhub_service()
    return svc.build_trends()


@router.get("/map-data", response_model=MapDataResponse)
async def get_map_data(
    metric: str = Query(
        default="renewable_potential",
        description=(
            "Metric for choropleth coloring. "
            "Options: renewable_potential, energy_consumption, peak_demand, generation, forecasted_demand"
        ),
    )
):
    """Return geographic data points for the choropleth map.

    *renewable_potential* uses municipality-level climate and terrain
    data from Supabase aggregated to province level.
    *energy_consumption*, *peak_demand*, *generation*, and
    *forecasted_demand* return national-level values (the DOE dataset
    does not include sub-national consumption statistics).
    """
    svc = get_energyhub_service()
    return svc.build_map_data(metric)


@router.get("/source-breakdown", response_model=SourceBreakdownResponse)
async def get_source_breakdown(year: int | None = Query(default=None, description="Year (defaults to latest)")):
    """Return generation by plant type for a given year."""
    svc = get_energyhub_service()
    return svc._ml.get_source_breakdown(year)


@router.get("/grid-breakdown", response_model=GridBreakdownResponse)
async def get_grid_breakdown(year: int | None = Query(default=None, description="Year (defaults to latest)")):
    """Return generation by grid (Luzon, Visayas, Mindanao) for a given year."""
    svc = get_energyhub_service()
    return svc._ml.get_grid_breakdown(year)


@router.get("/model-comparison", response_model=ModelComparisonResponse)
async def get_model_comparison():
    """Return test-set performance metrics for all trained models."""
    svc = get_energyhub_service()
    return {"items": svc._ml.get_model_comparison()}


@router.get("/ai-insight", response_model=AiInsightResponse)
async def get_ai_insight(
    use_llm: bool = Query(default=False, description="Use LLM (Gemini/Groq) for dynamic analysis instead of static text")
):
    """Return a data-backed narrative insight and recommendation.

    Set use_llm=true to get a dynamically generated analysis from
    the configured LLM (Gemini or Groq) based on the latest energy
    statistics, generation mix, and ARIMA forecast.
    """
    svc = get_energyhub_service()
    return svc.get_ai_insight(use_llm=use_llm)


@router.post("/analyze-chart", response_model=AnalyzeChartResponse)
async def analyze_chart(
    payload: AnalyzeChartRequest,
    force_refresh: bool = Query(default=False, description="Bypass cache and generate a fresh LLM response"),
):
    """Send chart data to the LLM and receive a narrative explanation.

    Use this endpoint to get AI-powered interpretations of specific
    visualizations (trends, source breakdown, or map).

    Set force_refresh=true to bypass the database cache and generate a
    brand-new explanation (useful for rotating responses).
    """
    svc = get_energyhub_service()
    return svc.analyze_chart(payload.chart_type, payload.chart_data, force_refresh=force_refresh)
