from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import get_verified_user
from app.schemas.ecosim import (
    BarangayListResponse,
    EcosimDashboardResponse,
    EcosimQueryParams,
    EcosimResponse,
    GetHouse,
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
router = APIRouter()


@router.get("/", response_model=EcosimDashboardResponse)
async def get_ecosim_results(
    params: EcosimQueryParams = Depends(),
    include_ai: bool = False,
    use_rag: bool = False,
    rag_query: str | None = None,
):
    return build_ecosim_dashboard_response(
        municipality_id=params.municipality_id,
        monthly_consumption=params.monthly_consumption,
        monthly_bill=params.monthly_bill,
        electricity_rate=params.electricity_rate,
        desired_savings=params.desired_savings,
        include_ai=include_ai,
        use_rag=use_rag,
        rag_query=rag_query,
        mode=params.mode,
    )


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
    user: dict = Depends(get_verified_user),
    include_ai: bool = True,
    use_rag: bool = True,
    rag_query: str | None = None,
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
    )
    return response_data
