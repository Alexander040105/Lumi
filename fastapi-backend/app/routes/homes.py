from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.dependencies.auth import get_current_user
from app.schemas.homes import (
    DashboardStatsResponse,
    HomeCreate,
    HomeDetailResponse,
    HomeEnergyProfileCreate,
    HomeListResponse,
    HomeResponse,
    HomeUpdate,
    SimulationComparisonCreate,
    SimulationComparisonResponse,
    SimulationCreate,
    SimulationDetailResponse,
    SimulationListResponse,
    SimulationResponse,
)
from app.services.homes import (
    create_comparison,
    create_energy_profile,
    create_home,
    create_simulation,
    delete_home,
    get_dashboard_stats,
    get_home,
    get_simulation,
    list_comparisons,
    list_homes,
    list_simulations,
    update_home,
)

router = APIRouter()


# ========================================================================
# Homes
# ========================================================================

@router.post("", response_model=HomeResponse, status_code=status.HTTP_201_CREATED)
async def post_home(
    body: HomeCreate,
    user: dict = Depends(get_current_user),
):
    user_id = UUID(user["sub"])
    return create_home(user_id, body)


@router.get("", response_model=HomeListResponse)
async def get_homes(
    user: dict = Depends(get_current_user),
):
    user_id = UUID(user["sub"])
    return {"items": list_homes(user_id)}


@router.get("/{home_id}", response_model=HomeDetailResponse)
async def get_home_detail(
    home_id: UUID,
    user: dict = Depends(get_current_user),
):
    user_id = UUID(user["sub"])
    return get_home(user_id, home_id)


@router.put("/{home_id}", response_model=HomeResponse)
async def put_home(
    home_id: UUID,
    body: HomeUpdate,
    user: dict = Depends(get_current_user),
):
    user_id = UUID(user["sub"])
    return update_home(user_id, home_id, body)


@router.delete("/{home_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_home_route(
    home_id: UUID,
    user: dict = Depends(get_current_user),
):
    user_id = UUID(user["sub"])
    delete_home(user_id, home_id)
    return None


# ========================================================================
# Energy Profiles
# ========================================================================

@router.post("/{home_id}/profiles", response_model=dict, status_code=status.HTTP_201_CREATED)
async def post_energy_profile(
    home_id: UUID,
    body: HomeEnergyProfileCreate,
    user: dict = Depends(get_current_user),
):
    user_id = UUID(user["sub"])
    # Ownership verified inside service via RLS, but we also check here
    get_home(user_id, home_id)  # raises 404 if not owned
    return create_energy_profile(home_id, body)


# ========================================================================
# Simulations
# ========================================================================

@router.post("/{home_id}/simulations", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
async def post_simulation(
    home_id: UUID,
    body: SimulationCreate,
    user: dict = Depends(get_current_user),
):
    user_id = UUID(user["sub"])
    return create_simulation(user_id, home_id, body)


@router.get("/{home_id}/simulations", response_model=SimulationListResponse)
async def get_simulations(
    home_id: UUID,
    user: dict = Depends(get_current_user),
):
    user_id = UUID(user["sub"])
    return {"items": list_simulations(user_id, home_id)}


@router.get("/{home_id}/simulations/{simulation_id}", response_model=SimulationDetailResponse)
async def get_simulation_detail(
    home_id: UUID,
    simulation_id: UUID,
    user: dict = Depends(get_current_user),
):
    user_id = UUID(user["sub"])
    return get_simulation(user_id, simulation_id)


# ========================================================================
# Simulation Comparisons
# ========================================================================

@router.post("/{home_id}/comparisons", response_model=SimulationComparisonResponse, status_code=status.HTTP_201_CREATED)
async def post_comparison(
    home_id: UUID,
    body: SimulationComparisonCreate,
    user: dict = Depends(get_current_user),
):
    user_id = UUID(user["sub"])
    return create_comparison(user_id, home_id, body)


@router.get("/{home_id}/comparisons", response_model=list[SimulationComparisonResponse])
async def get_comparisons(
    home_id: UUID,
    user: dict = Depends(get_current_user),
):
    user_id = UUID(user["sub"])
    return list_comparisons(user_id, home_id)


# ========================================================================
# Dashboard Stats
# ========================================================================

@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_user_dashboard_stats(
    user: dict = Depends(get_current_user),
):
    user_id = UUID(user["sub"])
    return get_dashboard_stats(user_id)
