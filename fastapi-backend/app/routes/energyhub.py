from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.dependencies.auth import get_verified_user_optional
from app.dependencies.quota import check_anonymous_quota, get_client_id, get_optional_user_or_quota
from app.schemas.energyhub import (
    AiInsightResponse,
    AnalyzeChartRequest,
    AnalyzeChartResponse,
    ForecastResponse,
    GridBreakdownResponse,
    MapExplanationResponse,
    IrenaOverviewResponse,
    MapDataResponse,
    MeralcoRateResponse,
    ModelComparisonResponse,
    MunicipalDemandResponse,
    OverviewResponse,
    ProvincialDemandResponse,
    SolarAtlasResponse,
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
    metric: str = Query(default="consumption", description="Metric to forecast: consumption, peak_demand, or renewable_generation"),
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
        description="Geographic level: province, municipality, or barangay. Municipality/barangay require pre-computed suitability scores.",
    ),
):
    """Return geographic data points for the choropleth map.

    All metrics use sub-national data:
    - Province-level: aggregated from municipality climate/terrain/suitability scores.
    - Municipality-level: pre-computed suitability scores from Supabase.
    - Barangay-level: inherits parent municipality suitability scores with barangay centroids.
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
async def get_model_comparison(
    metric: str = Query(default="consumption", description="Metric for model comparison: consumption, peak_demand, or renewable_generation"),
):
    """Return test-set performance metrics for all trained models."""
    svc = get_energyhub_service()
    return {"items": svc._ml.get_model_comparison(metric)}


@router.get("/ai-insight", response_model=AiInsightResponse)
async def get_ai_insight(
    request: Request,
    use_llm: bool = Query(default=False, description="Use LLM (Gemini/Groq) for dynamic analysis instead of static text"),
    user: dict | None = Depends(get_verified_user_optional),
):
    """Return a data-backed narrative insight and recommendation.

    Set use_llm=true to get a dynamically generated analysis from
    the configured LLM (Gemini or Groq) based on the latest energy
    statistics, generation mix, and ARIMA forecast.
    """
    remaining = None
    if use_llm and not user:
        allowed, remaining = await check_anonymous_quota(get_client_id(request))
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please log in to continue using EcoSim.",
            )

    svc = get_energyhub_service()
    response = svc.get_ai_insight(use_llm=use_llm)
    response["remaining_anonymous_requests"] = remaining
    return response


@router.post("/analyze-chart", response_model=AnalyzeChartResponse)
async def analyze_chart(
    payload: AnalyzeChartRequest,
    auth: dict = Depends(get_optional_user_or_quota),
    force_refresh: bool = Query(default=False, description="Bypass cache and generate a fresh LLM response"),
):
    """Send chart data to the LLM and receive a narrative explanation.

    Use this endpoint to get AI-powered interpretations of specific
    visualizations (trends, source breakdown, or map).

    Set force_refresh=true to bypass the database cache and generate a
    brand-new explanation (useful for rotating responses).
    """
    svc = get_energyhub_service()
    response = svc.analyze_chart(payload.chart_type, payload.chart_data, force_refresh=force_refresh)
    response["remaining_anonymous_requests"] = auth["remaining_anonymous_requests"]
    return response


@router.get("/map-explanation", response_model=MapExplanationResponse)
async def get_map_explanation(
    metric: str = Query(..., description="Map metric: renewable_potential, solar_potential, wind_potential, hydro_potential, or geothermal_potential"),
    level: str = Query(default="province", description="Geographic level: province or municipality"),
    force_refresh: bool = Query(default=False, description="Bypass cache and generate a fresh LLM response"),
    auth: dict = Depends(get_optional_user_or_quota),
):
    """Return a Groq-generated, data-grounded explanation for the current map.

    The explanation is cached in chart_ai_insights and rotated up to 3
    variants per map data hash; force_refresh generates a new variant.
    """
    svc = get_energyhub_service()
    response = svc.get_map_explanation(metric, level, force_refresh=force_refresh)
    response["remaining_anonymous_requests"] = auth["remaining_anonymous_requests"]
    return response


@router.get("/provincial-demand", response_model=ProvincialDemandResponse)
async def get_provincial_demand(
    region: str | None = Query(default=None, description="Filter by region code (e.g., IV-A, NCR)"),
):
    """Return DOE Annex 8 provincial/regional consumption breakdown."""
    svc = get_energyhub_service()
    return svc.get_provincial_consumption(region)


@router.get("/municipal-demand/{province_id}", response_model=MunicipalDemandResponse)
async def get_municipal_demand(
    province_id: int,
):
    """Return population-weighted municipal demand estimates for a province.

    Requires PSA population data to be loaded in the municipal_population table.
    If population data is missing, returns an empty list with a data-gap note.
    """
    svc = get_energyhub_service()
    return svc.estimate_municipal_demand(province_id)


@router.get("/irena/overview", response_model=IrenaOverviewResponse)
async def get_irena_overview():
    """Return IRENA capacity, generation, and renewable share statistics.

    Displayed alongside DOE data for cross-validation and ASEAN benchmarking.
    """
    svc = get_energyhub_service()
    return svc.build_irena_overview()


@router.get("/irena/capacity")
async def get_irena_capacity(year: int | None = Query(default=None)):
    """Return IRENA Philippines electricity capacity by technology."""
    svc = get_energyhub_service()
    return svc.get_irena_capacity(year)


@router.get("/irena/generation")
async def get_irena_generation(year: int | None = Query(default=None)):
    """Return IRENA Philippines electricity generation by technology."""
    svc = get_energyhub_service()
    return svc.get_irena_generation(year)


@router.get("/irena/renewable-share")
async def get_irena_renewable_share():
    """Return year-by-year renewable share of electricity generation (%)."""
    svc = get_energyhub_service()
    return svc.get_irena_renewable_share()


@router.get("/meralco-rate", response_model=MeralcoRateResponse)
async def get_meralco_rate(year: int | None = Query(default=None)):
    """Return Meralco residential generation charge rate for a given year.

    Note: this is the generation charge component only. The total
    residential rate includes transmission, distribution, and other charges.
    """
    svc = get_energyhub_service()
    return svc.get_meralco_rate(year)


@router.get("/solar-atlas", response_model=SolarAtlasResponse)
async def get_solar_atlas(location: str | None = Query(default=None)):
    """Return Global Solar Atlas v2 data for Philippine locations.

    High-resolution solar irradiance (GHI, DNI, DIF) and PV power
    output sampled at key cities. Supplements NASA POWER data in EcoSim.
    """
    svc = get_energyhub_service()
    return svc.get_solar_atlas(location)
