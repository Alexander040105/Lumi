from fastapi import APIRouter, Depends, Query, status
import logging

from app.dependencies.quota import get_optional_user_or_quota
from app.schemas.ecosim import (
    BarangayListResponse,
    EcosimAIResponse,
    EcosimDashboardResponse,
    EcosimQueryParams,
    EcosimResponse,
    MunicipalityListResponse,
    PostHouse,
    ProvinceListResponse,
)
from app.services.ecosim import (
    build_ecosim_dashboard_response,
    list_barangays,
    list_municipalities,
    list_provinces,
    renewable_energy_calculator,
)
from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)
router = APIRouter()


def _log_ecosim_request(user: dict, municipality_id: int | None) -> None:
    """Persist a lightweight usage log for authenticated EcoSim requests."""
    if not user:
        return
    client = get_supabase_client()
    try:
        client.table("user_ecosim_logs").insert({
            "user_id": user.get("sub"),
            "municipality_id": municipality_id,
        }).execute()
        logger.info("EcoSim request logged for user=%s municipality=%s", user.get("sub"), municipality_id)
    except Exception as exc:
        logger.warning("Failed to log ecosim request for user=%s: %s", user.get("sub"), exc)


@router.get("/", response_model=EcosimDashboardResponse)
async def get_ecosim_results(
    params: EcosimQueryParams = Depends(),
    include_ai: bool = False,
    use_rag: bool = False,
    rag_query: str | None = None,
    data_source: str = Query(default="auto", description="nasa | atlas | auto"),
    auth: dict = Depends(get_optional_user_or_quota),
):
    result = build_ecosim_dashboard_response(
        municipality_id=params.municipality_id,
        monthly_consumption=params.monthly_consumption,
        monthly_bill=params.monthly_bill,
        electricity_rate=params.electricity_rate,
        desired_savings=params.desired_savings,
        include_ai=include_ai,
        use_rag=use_rag,
        rag_query=rag_query,
        mode=params.mode,
        data_source=data_source,
    )
    _log_ecosim_request(auth.get("user"), params.municipality_id)
    result["remaining_anonymous_requests"] = auth["remaining_anonymous_requests"]
    result["remaining_usage"] = auth.get("remaining_usage")
    return result


@router.get("/ai", response_model=EcosimAIResponse)
async def get_ecosim_ai(
    params: EcosimQueryParams = Depends(),
    use_rag: bool = False,
    rag_query: str | None = None,
    data_source: str = Query(default="auto", description="nasa | atlas | auto"),
    auth: dict = Depends(get_optional_user_or_quota),
):
    result = build_ecosim_dashboard_response(
        municipality_id=params.municipality_id,
        monthly_consumption=params.monthly_consumption,
        monthly_bill=params.monthly_bill,
        electricity_rate=params.electricity_rate,
        desired_savings=params.desired_savings,
        include_ai=True,
        use_rag=use_rag,
        rag_query=rag_query,
        mode=params.mode,
        data_source=data_source,
    )
    _log_ecosim_request(auth.get("user"), params.municipality_id)
    return {
        "ai_analysis": result.get("ai_analysis"),
        "remaining_anonymous_requests": auth["remaining_anonymous_requests"],
        "remaining_usage": auth.get("remaining_usage"),
    }


@router.get("/municipalities", response_model=MunicipalityListResponse)
async def get_municipalities():
    return {"items": list_municipalities()}


@router.get("/provinces", response_model=ProvinceListResponse)
async def get_provinces():
    return {"items": list_provinces()}


@router.get("/barangays", response_model=BarangayListResponse)
async def get_barangays(
    municipality_id: int | None = Query(default=None, description="Filter by municipality ID"),
):
    return {"items": list_barangays(municipality_id)}


@router.post("/", response_model=EcosimResponse, status_code=status.HTTP_201_CREATED)
async def post_item(
    body: PostHouse,
    auth: dict = Depends(get_optional_user_or_quota),
    include_ai: bool = True,
    use_rag: bool = True,
    rag_query: str | None = None,
    data_source: str = Query(default="auto", description="nasa | atlas | auto"),
):
    response_data = renewable_energy_calculator(
        body.house_name,
        body.municipality,
        body.current_electricity_bill,
        body.electricity_rate,
        body.desired_savings,
        include_ai=include_ai,
        use_rag=use_rag,
        rag_query=rag_query,
        mode=body.mode,
        data_source=data_source,
    )
    _log_ecosim_request(auth.get("user"), None)
    response_data["remaining_anonymous_requests"] = auth["remaining_anonymous_requests"]
    return response_data
