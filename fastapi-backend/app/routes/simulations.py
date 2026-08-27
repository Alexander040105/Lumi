import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user_with_role_and_plan, get_verified_user
from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)
router = APIRouter()


class SimulationCreate(BaseModel):
    label: str = Field(..., min_length=1, max_length=200)
    municipality_id: int
    inputs: dict = Field(default_factory=dict)
    results: dict = Field(default_factory=dict)


class SimulationUpdate(BaseModel):
    label: str = Field(..., min_length=1, max_length=200)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_simulation(
    payload: SimulationCreate,
    user: dict = Depends(get_current_user_with_role_and_plan),
) -> dict[str, Any]:
    """Save a new simulation for the authenticated user."""
    user_id = user.get("sub")

    client = get_supabase_client()
    try:
        resp = (
            client.table("saved_simulations")
            .insert({
                "user_id": user_id,
                "label": payload.label,
                "municipality_id": payload.municipality_id,
                "inputs": payload.inputs,
                "results": payload.results,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            .execute()
        )
        return {"simulation": resp.data[0] if resp.data else None}
    except Exception as exc:
        logger.error("Failed to save simulation for user=%s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save simulation",
        )


@router.get("")
async def list_simulations(
    user: dict = Depends(get_verified_user),
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """List saved simulations for the authenticated user."""
    user_id = user.get("sub")
    client = get_supabase_client()
    try:
        resp = (
            client.table("saved_simulations")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .offset(offset)
            .execute()
        )
        return {"simulations": resp.data or [], "limit": limit, "offset": offset}
    except Exception as exc:
        logger.error("Failed to fetch simulations for user=%s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch simulations",
        )


@router.get("/{simulation_id}")
async def get_simulation(
    simulation_id: str,
    user: dict = Depends(get_verified_user),
) -> dict[str, Any]:
    """Get a single saved simulation by ID (owner only)."""
    user_id = user.get("sub")
    client = get_supabase_client()
    try:
        resp = (
            client.table("saved_simulations")
            .select("*")
            .eq("id", simulation_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        if not resp.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation not found or access denied",
            )
        return {"simulation": resp.data}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to fetch simulation %s for user=%s: %s", simulation_id, user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch simulation",
        )


@router.patch("/{simulation_id}")
async def update_simulation(
    simulation_id: str,
    payload: SimulationUpdate,
    user: dict = Depends(get_verified_user),
) -> dict[str, Any]:
    """Update a saved simulation's label (owner only)."""
    user_id = user.get("sub")
    client = get_supabase_client()
    try:
        # Verify ownership
        existing = (
            client.table("saved_simulations")
            .select("id")
            .eq("id", simulation_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation not found or access denied",
            )

        resp = (
            client.table("saved_simulations")
            .update({"label": payload.label})
            .eq("id", simulation_id)
            .eq("user_id", user_id)
            .execute()
        )
        return {"simulation": resp.data[0] if resp.data else None}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to update simulation %s for user=%s: %s", simulation_id, user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update simulation",
        )


@router.delete("/{simulation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_simulation(
    simulation_id: str,
    user: dict = Depends(get_verified_user),
) -> None:
    """Delete a saved simulation (owner only)."""
    user_id = user.get("sub")
    client = get_supabase_client()
    try:
        # Verify ownership
        existing = (
            client.table("saved_simulations")
            .select("id")
            .eq("id", simulation_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation not found or access denied",
            )

        client.table("saved_simulations").delete().eq("id", simulation_id).execute()
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to delete simulation %s for user=%s: %s", simulation_id, user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete simulation",
        )
