import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.dependencies.auth import get_current_user_with_role_and_plan, get_verified_user
from app.services.redis_client import get_redis
from app.services.supabase_service import get_supabase_client

router = APIRouter()


class SessionPayload(BaseModel):
    data: dict = Field(default_factory=dict, max_length=50)


@router.get("/me")
async def read_me(user=Depends(get_current_user_with_role_and_plan)):
    return {"user": user}


@router.get("/profile")
async def get_profile(user: dict = Depends(get_verified_user)) -> dict:
    """Return the authenticated user's extended profile."""
    client = get_supabase_client()
    resp = (
        client.table("profiles")
        .select("*")
        .eq("id", user.get("sub"))
        .single()
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return {"profile": resp.data}


@router.put("/profile")
async def update_profile(payload: dict, user: dict = Depends(get_verified_user)) -> dict:
    """Update the authenticated user's profile fields."""
    allowed_fields = {"full_name", "organization", "location", "preferred_municipality_id", "avatar_url"}
    updates = {k: v for k, v in payload.items() if k in allowed_fields}
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields to update")

    client = get_supabase_client()
    resp = (
        client.table("profiles")
        .update(updates)
        .eq("id", user.get("sub"))
        .execute()
    )
    return {"profile": resp.data[0] if resp.data else None}


@router.post("/sync-avatar")
async def sync_avatar(user: dict = Depends(get_verified_user)) -> dict:
    """Sync avatar_url from auth.user_metadata into public.profiles.

    Creates a minimal profile row if one doesn't exist yet.
    """
    client = get_supabase_client()
    user_id = user.get("sub")
    metadata = user.get("user_metadata") or {}
    avatar_url = metadata.get("avatar_url") or metadata.get("picture")
    full_name = metadata.get("full_name") or metadata.get("name")

    # Check if profile exists
    existing = client.table("profiles").select("id").eq("id", user_id).single().execute()

    if existing.data:
        updates: dict[str, Any] = {}
        if avatar_url:
            updates["avatar_url"] = avatar_url
        if full_name:
            updates["full_name"] = full_name
        if updates:
            client.table("profiles").update(updates).eq("id", user_id).execute()
    else:
        client.table("profiles").insert({
            "id": user_id,
            "full_name": full_name,
            "avatar_url": avatar_url,
            "plan": "free",
            "is_active": True,
        }).execute()

    return {"avatar_url": avatar_url, "full_name": full_name}


@router.post("/session")
async def store_session(payload: SessionPayload, ttl_seconds: int = 3600, user=Depends(get_verified_user)):
    redis = get_redis()
    user_id = user.get("sub")
    key = f"user:{user_id}:session"
    serialized = json.dumps(payload.data)
    if len(serialized) > 10_000:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Session payload too large")
    await redis.set(key, serialized, ex=ttl_seconds)
    return {"stored": True, "key": key}
