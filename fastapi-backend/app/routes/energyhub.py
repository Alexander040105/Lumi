from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

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
from app.dependencies.auth import get_current_user_with_role_and_plan, get_optional_user
from app.dependencies.plan_limits import (
    check_feature_access,
    increment_usage,
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
    metric: str = Query(default="consumption", description="Metric to forecast: consumption or peak_demand"),
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
            "Options: renewable_potential, solar_potential, wind_potential, "
            "hydro_potential, geothermal_potential"
        ),
    ),
    level: str = Query(
        default="province",
        description="Geographic level: province or municipality. Municipality requires pre-computed suitability scores.",
    ),
):
    """Return geographic data points for the choropleth map.

    All metrics use sub-national data:
    - Province-level: aggregated from municipality climate/terrain/suitability scores.
    - Municipality-level: pre-computed suitability scores from Supabase.
    """
    svc = get_energyhub_service()
    return svc.build_map_data(metric, level)


@router.get("/source-breakdown", response_model=SourceBreakdownResponse)
async def get_source_breakdown(
    year: int | None = Query(default=None, description="Year (defaults to latest)"),
):
    """Return generation by plant type for a given year."""
    svc = get_energyhub_service()
    return svc._ml.get_source_breakdown(year)


@router.get("/grid-breakdown", response_model=GridBreakdownResponse)
async def get_grid_breakdown(
    year: int | None = Query(default=None, description="Year (defaults to latest)"),
):
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
    request: Request,
    use_llm: bool = Query(default=False, description="Use LLM (Gemini/Groq) for dynamic analysis instead of static text"),
    user: dict | None = Depends(get_optional_user),
):
    """Return a data-backed narrative insight and recommendation.

    Set use_llm=true to get a dynamically generated analysis from
    the configured LLM (Gemini or Groq) based on the latest energy
    statistics, generation mix, and ARIMA forecast.

    LLM-generated insights are gated by plan limits. Free tier: 1/mo,
    Pro: 5/mo, Premium: 20/mo. Static insights are always available.
    """
    svc = get_energyhub_service()

    # Static insights are always free (no auth required)
    if not use_llm:
        return svc.get_ai_insight(use_llm=False)

    # LLM insights require authentication
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for LLM insights. Please log in.",
        )

    # Check plan limit for LLM insights
    access = check_feature_access(user, "ai_insight")
    if not access["allowed"]:
        # Return static insight with upgrade info
        static = svc.get_ai_insight(use_llm=False)
        static["upgrade_info"] = {
            "message": access["message"],
            "limit": access["limit"],
            "used": access["limit"] - access["remaining"],
            "remaining": access["remaining"],
            "upgrade": True,
        }
        return static

    result = svc.get_ai_insight(use_llm=True)
    result["remaining_insights"] = access["remaining"] - 1

    # Log usage
    increment_usage(
        user_id=user.get("sub"),
        feature_type="ai_insight_energyhub",
        tokens_input=2000,
        tokens_output=400,
        metadata={"type": "ai_insight"},
    )
    return result


@router.post("/analyze-chart", response_model=AnalyzeChartResponse)
async def analyze_chart(
    payload: AnalyzeChartRequest,
    force_refresh: bool = Query(default=False, description="Bypass cache and generate a fresh LLM response"),
    user: dict = Depends(get_current_user_with_role_and_plan),
):
    """Send chart data to the LLM and receive a narrative explanation.

    Use this endpoint to get AI-powered interpretations of specific
    visualizations (trends, source breakdown, or map).

    Set force_refresh=true to bypass the database cache and generate a
    brand-new explanation (useful for rotating responses).

    Chart analysis counts against the AI insight monthly limit.
    """
    svc = get_energyhub_service()

    # Check plan limit (counts as ai_insight)
    access = check_feature_access(user, "ai_insight")
    if not access["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": access["message"],
                "limit": access["limit"],
                "used": access["limit"] - access["remaining"],
                "remaining": access["remaining"],
                "upgrade": True,
            },
        )

    result = svc.analyze_chart(payload.chart_type, payload.chart_data, force_refresh=force_refresh)
    result["remaining_insights"] = access["remaining"] - 1

    # Log usage
    increment_usage(
        user_id=user.get("sub"),
        feature_type="ai_insight_energyhub",
        tokens_input=2000,
        tokens_output=400,
        metadata={"type": "analyze_chart", "chart_type": payload.chart_type},
    )
    return result
