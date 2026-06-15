import logging
from uuid import UUID

from fastapi import HTTPException, status
from postgrest.exceptions import APIError

from app.schemas.homes import HomeCreate, HomeEnergyProfileCreate, HomeUpdate, SimulationComparisonCreate, SimulationCreate
from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)


def _get_supabase():
    return get_supabase_client()


# ========================================================================
# Homes CRUD
# ========================================================================

def create_home(user_id: UUID, data: HomeCreate) -> dict:
    """Create a new home and its initial energy profile."""
    client = _get_supabase()

    # Verify municipality exists
    try:
        muni_result = (
            client
            .table("municipalities")
            .select("name")
            .eq("municipality_id", data.municipality_id)
            .single()
            .execute()
        )
        if not muni_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Municipality not found",
            )
    except APIError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Municipality not found",
        ) from exc

    # Insert home
    try:
        home_result = (
            client
            .table("user_homes")
            .insert({
                "user_id": str(user_id),
                "name": data.name,
                "municipality_id": data.municipality_id,
            })
            .execute()
        )
    except APIError as exc:
        logger.exception("Failed to create home")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create home",
        ) from exc

    home = home_result.data[0] if isinstance(home_result.data, list) else home_result.data
    home_id = home["home_id"]

    # Insert initial energy profile
    try:
        (
            client
            .table("home_energy_profiles")
            .insert({
                "home_id": home_id,
                "monthly_consumption_kwh": data.monthly_consumption_kwh,
                "monthly_bill_php": data.monthly_bill_php,
                "desired_savings_pct": data.desired_savings_pct,
            })
            .execute()
        )
    except APIError as exc:
        logger.exception("Failed to create energy profile")
        # Best-effort: home exists even if profile fails

    # Enrich with municipality name
    home["municipality_name"] = muni_result.data.get("name")
    return home


def list_homes(user_id: UUID) -> list[dict]:
    """List all homes for a user with municipality names."""
    client = _get_supabase()
    try:
        result = (
            client
            .table("user_homes")
            .select("*, municipalities(name)")
            .eq("user_id", str(user_id))
            .execute()
        )
    except APIError as exc:
        logger.exception("Failed to list homes")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list homes",
        ) from exc

    items = result.data or []
    for item in items:
        if "municipalities" in item and item["municipalities"]:
            item["municipality_name"] = item["municipalities"]["name"]
            del item["municipalities"]
    return items


def get_home(user_id: UUID, home_id: UUID) -> dict:
    """Get a single home with latest profile and aggregate stats."""
    client = _get_supabase()
    try:
        home_result = (
            client
            .table("user_homes")
            .select("*, municipalities(name)")
            .eq("home_id", str(home_id))
            .eq("user_id", str(user_id))
            .single()
            .execute()
        )
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict) and error.get("code") == "PGRST116":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Home not found",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch home",
        ) from exc

    if not home_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Home not found",
        )

    home = home_result.data
    if "municipalities" in home and home["municipalities"]:
        home["municipality_name"] = home["municipalities"]["name"]
        del home["municipalities"]

    # Fetch latest energy profile
    try:
        profile_result = (
            client
            .table("home_energy_profiles")
            .select("*")
            .eq("home_id", str(home_id))
            .order("created_at", desc=True)
            .limit(1)
            .single()
            .execute()
        )
        home["latest_profile"] = profile_result.data
    except APIError:
        home["latest_profile"] = None

    # Aggregate simulation stats
    try:
        sims_result = (
            client
            .table("home_simulations")
            .select("carbon_reduction_kg, independence_score")
            .eq("home_id", str(home_id))
            .execute()
        )
        sims = sims_result.data or []
        home["total_simulations"] = len(sims)
        home["total_carbon_reduction_kg"] = sum(
            s.get("carbon_reduction_kg", 0) or 0 for s in sims
        )
        if sims:
            home["avg_independence_score"] = sum(
                s.get("independence_score", 0) or 0 for s in sims
            ) / len(sims)
        else:
            home["avg_independence_score"] = None
    except APIError:
        home["total_simulations"] = 0
        home["total_carbon_reduction_kg"] = 0.0
        home["avg_independence_score"] = None

    return home


def update_home(user_id: UUID, home_id: UUID, data: HomeUpdate) -> dict:
    """Update home name or municipality."""
    client = _get_supabase()

    update_payload = {}
    if data.name is not None:
        update_payload["name"] = data.name
    if data.municipality_id is not None:
        update_payload["municipality_id"] = data.municipality_id

    if not update_payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    try:
        result = (
            client
            .table("user_homes")
            .update(update_payload)
            .eq("home_id", str(home_id))
            .eq("user_id", str(user_id))
            .execute()
        )
    except APIError as exc:
        logger.exception("Failed to update home")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update home",
        ) from exc

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Home not found",
        )

    return result.data[0] if isinstance(result.data, list) else result.data


def delete_home(user_id: UUID, home_id: UUID) -> None:
    """Delete a home (cascades to profiles, simulations, comparisons)."""
    client = _get_supabase()
    try:
        result = (
            client
            .table("user_homes")
            .delete()
            .eq("home_id", str(home_id))
            .eq("user_id", str(user_id))
            .execute()
        )
    except APIError as exc:
        logger.exception("Failed to delete home")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete home",
        ) from exc

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Home not found",
        )


# ========================================================================
# Energy Profiles
# ========================================================================

def create_energy_profile(home_id: UUID, data: HomeEnergyProfileCreate) -> dict:
    """Create a new energy profile snapshot for a home."""
    client = _get_supabase()
    try:
        result = (
            client
            .table("home_energy_profiles")
            .insert({
                "home_id": str(home_id),
                "monthly_consumption_kwh": data.monthly_consumption_kwh,
                "monthly_bill_php": data.monthly_bill_php,
                "desired_savings_pct": data.desired_savings_pct,
            })
            .execute()
        )
    except APIError as exc:
        logger.exception("Failed to create energy profile")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create energy profile",
        ) from exc

    return result.data[0] if isinstance(result.data, list) else result.data


# ========================================================================
# Simulations
# ========================================================================

def create_simulation(user_id: UUID, home_id: UUID, data: SimulationCreate) -> dict:
    """Save a simulation result to a home."""
    client = _get_supabase()

    # Verify home ownership
    try:
        home_result = (
            client
            .table("user_homes")
            .select("home_id")
            .eq("home_id", str(home_id))
            .eq("user_id", str(user_id))
            .single()
            .execute()
        )
        if not home_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Home not found",
            )
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict) and error.get("code") == "PGRST116":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Home not found",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify home ownership",
        ) from exc

    payload = {
        "home_id": str(home_id),
        "simulation_name": data.simulation_name,
        "panel_wattage": data.panel_wattage,
        "number_of_panels": data.number_of_panels,
        "include_battery": data.include_battery,
        "battery_kwh": data.battery_kwh,
        "recommended_source": data.recommended_source,
        "suitability_score": data.suitability_score,
        "estimated_generation_kwh": data.estimated_generation_kwh,
        "monthly_savings_php": data.monthly_savings_php,
        "installation_cost_php": data.installation_cost_php,
        "payback_years": data.payback_years,
        "carbon_reduction_kg": data.carbon_reduction_kg,
        "independence_score": data.independence_score,
        "results_json": data.results_json,
        "ai_analysis_json": data.ai_analysis_json,
    }

    try:
        result = (
            client
            .table("home_simulations")
            .insert(payload)
            .execute()
        )
    except APIError as exc:
        logger.exception("Failed to save simulation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save simulation",
        ) from exc

    return result.data[0] if isinstance(result.data, list) else result.data


def list_simulations(user_id: UUID, home_id: UUID | None = None) -> list[dict]:
    """List simulations for a user, optionally filtered by home."""
    client = _get_supabase()

    query = (
        client
        .table("home_simulations")
        .select(
            "simulation_id, home_id, simulation_name, recommended_source, "
            "suitability_score, estimated_generation_kwh, monthly_savings_php, "
            "installation_cost_php, payback_years, carbon_reduction_kg, "
            "independence_score, created_at"
        )
    )

    if home_id:
        query = query.eq("home_id", str(home_id))
    else:
        # Only fetch simulations belonging to user's homes
        try:
            homes_result = (
                client
                .table("user_homes")
                .select("home_id")
                .eq("user_id", str(user_id))
                .execute()
            )
            home_ids = [h["home_id"] for h in (homes_result.data or [])]
            if not home_ids:
                return []
            query = query.in_("home_id", home_ids)
        except APIError:
            return []

    query = query.order("created_at", desc=True)

    try:
        result = query.execute()
    except APIError as exc:
        logger.exception("Failed to list simulations")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list simulations",
        ) from exc

    return result.data or []


def get_simulation(user_id: UUID, simulation_id: UUID) -> dict:
    """Get a single simulation with full details."""
    client = _get_supabase()
    try:
        result = (
            client
            .table("home_simulations")
            .select("*")
            .eq("simulation_id", str(simulation_id))
            .single()
            .execute()
        )
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict) and error.get("code") == "PGRST116":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation not found",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch simulation",
        ) from exc

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found",
        )

    # Verify ownership via home
    sim = result.data
    try:
        home_result = (
            client
            .table("user_homes")
            .select("user_id")
            .eq("home_id", sim["home_id"])
            .single()
            .execute()
        )
        if not home_result.data or home_result.data.get("user_id") != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation not found",
            )
    except APIError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found",
        )

    return sim


# ========================================================================
# Simulation Comparisons
# ========================================================================

def create_comparison(user_id: UUID, home_id: UUID, data: SimulationComparisonCreate) -> dict:
    """Create a comparison of 2-3 simulations."""
    client = _get_supabase()

    # Verify home ownership
    try:
        home_result = (
            client
            .table("user_homes")
            .select("home_id")
            .eq("home_id", str(home_id))
            .eq("user_id", str(user_id))
            .single()
            .execute()
        )
        if not home_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Home not found",
            )
    except APIError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Home not found",
        )

    # Verify all simulations belong to this home
    sim_ids = [str(sid) for sid in data.simulation_ids]
    try:
        sims_result = (
            client
            .table("home_simulations")
            .select("simulation_id")
            .eq("home_id", str(home_id))
            .in_("simulation_id", sim_ids)
            .execute()
        )
        found_ids = {s["simulation_id"] for s in (sims_result.data or [])}
        if len(found_ids) != len(sim_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more simulations do not belong to this home",
            )
    except APIError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify simulations",
        ) from exc

    try:
        result = (
            client
            .table("simulation_comparisons")
            .insert({
                "home_id": str(home_id),
                "comparison_name": data.comparison_name,
                "simulation_ids": sim_ids,
            })
            .execute()
        )
    except APIError as exc:
        logger.exception("Failed to create comparison")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create comparison",
        ) from exc

    return result.data[0] if isinstance(result.data, list) else result.data


def list_comparisons(user_id: UUID, home_id: UUID) -> list[dict]:
    """List all comparisons for a home."""
    client = _get_supabase()
    try:
        result = (
            client
            .table("simulation_comparisons")
            .select("*")
            .eq("home_id", str(home_id))
            .order("created_at", desc=True)
            .execute()
        )
    except APIError as exc:
        logger.exception("Failed to list comparisons")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list comparisons",
        ) from exc

    return result.data or []


# ========================================================================
# Dashboard Stats
# ========================================================================

def get_dashboard_stats(user_id: UUID) -> dict:
    """Get aggregated dashboard statistics for a user."""
    client = _get_supabase()
    try:
        result = (
            client
            .table("user_dashboard_stats")
            .select("*")
            .eq("user_id", str(user_id))
            .single()
            .execute()
        )
    except APIError as exc:
        error = getattr(exc, "args", [{}])[0]
        if isinstance(error, dict) and error.get("code") == "PGRST116":
            return {
                "total_homes": 0,
                "total_simulations": 0,
                "total_carbon_reduction_kg": 0.0,
                "avg_independence_score": 0.0,
                "best_recommended_source": None,
                "latest_simulation_date": None,
            }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard stats",
        ) from exc

    return result.data or {
        "total_homes": 0,
        "total_simulations": 0,
        "total_carbon_reduction_kg": 0.0,
        "avg_independence_score": 0.0,
        "best_recommended_source": None,
        "latest_simulation_date": None,
    }
