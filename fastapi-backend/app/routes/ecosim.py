from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.ecosim import (
    EcosimDashboardResponse,
    EcosimQueryParams,
    EcosimResponse,
    GetHouse,
    MunicipalityListResponse,
    PostHouse,
)
from app.dependencies.auth import get_current_user_with_role_and_plan
from app.dependencies.plan_limits import (
    check_feature_access,
    increment_usage,
)
from app.services.ecosim import build_ecosim_dashboard_response, list_municipalities, renewable_energy_calculator
router = APIRouter()


def _check_ai_insight(user: dict | None, include_ai: bool) -> tuple[bool, dict]:
    """Check if AI insight is allowed for the user. Returns (allowed, info dict)."""
    if not include_ai:
        return False, {"ai_insight_remaining": None, "ai_insight_limit": None}

    # For unauthenticated users on public endpoints, allow without AI
    if user is None:
        return False, {
            "ai_insight_remaining": 0,
            "ai_insight_limit": 0,
            "message": "Sign in to access AI insights.",
        }

    access = check_feature_access(user, "ai_insight")
    return access["allowed"], {
        "ai_insight_remaining": access["remaining"],
        "ai_insight_limit": access["limit"],
        "message": access["message"] if not access["allowed"] else "",
    }


@router.get("/", response_model=EcosimDashboardResponse)
async def get_ecosim_results(
    params: EcosimQueryParams = Depends(),
    include_ai: bool = False,
    use_rag: bool = False,
    rag_query: str | None = None,
    user: dict | None = Depends(get_current_user_with_role_and_plan),
):
    allowed, ai_info = _check_ai_insight(user, include_ai)
    result = build_ecosim_dashboard_response(
        municipality_id=params.municipality_id,
        monthly_consumption=params.monthly_consumption,
        monthly_bill=params.monthly_bill,
        desired_savings=params.desired_savings,
        include_ai=allowed,
        use_rag=use_rag,
        rag_query=rag_query,
    )
    result["ai_insight_info"] = ai_info
    return result


@router.get("/municipalities", response_model=MunicipalityListResponse)
async def get_municipalities():
    return {"items": list_municipalities()}


@router.post("/", response_model=EcosimResponse, status_code=status.HTTP_201_CREATED)
async def post_item(
    body: PostHouse,
    include_ai: bool = True,
    use_rag: bool = True,
    rag_query: str | None = None,
    user: dict = Depends(get_current_user_with_role_and_plan),
):
    allowed, ai_info = _check_ai_insight(user, include_ai)
    response_data = renewable_energy_calculator(
        body.house_name,
        body.municipality,
        body.current_electricity_bill,
        body.electricity_rate,
        body.desired_savings,
        include_ai=allowed,
        use_rag=use_rag,
        rag_query=rag_query,
    )
    response_data["ai_insight_info"] = ai_info

    # Log AI insight usage if it was generated
    if allowed and user:
        increment_usage(
            user_id=user.get("sub"),
            feature_type="ai_insight_ecosim",
            tokens_input=2500,
            tokens_output=500,
            metadata={"municipality": body.municipality, "use_rag": use_rag},
        )

    return response_data
