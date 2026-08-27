import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

logger = logging.getLogger(__name__)
from pydantic import BaseModel, Field, field_validator

from app.dependencies.auth import get_current_user_with_role_and_plan, get_verified_user
from app.services.data_cache import cache_delete, cache_get, cache_set
from app.services.redis_client import get_redis
from app.services.supabase_service import get_supabase_client

router = APIRouter()

_SESSION_MAX_TTL_SECONDS = 86_400  # 1 day
_SESSION_MAX_PAYLOAD_BYTES = 10_000


class SessionPayload(BaseModel):
    data: dict = Field(default_factory=dict, max_length=50)


class ProfileUpdatePayload(BaseModel):
    """Validated profile update payload."""

    full_name: str | None = Field(None, max_length=120)
    organization: str | None = Field(None, max_length=120)
    location: str | None = Field(None, max_length=120)
    preferred_municipality_id: str | None = Field(None, max_length=40)
    avatar_url: str | None = Field(None, max_length=500)

    model_config = {"extra": "forbid"}

    @field_validator("full_name", "organization", "location", "preferred_municipality_id", "avatar_url")
    @classmethod
    def strip_or_none(cls, v: str | None) -> str | None:
        if isinstance(v, str):
            v = v.strip()
            return v if v else None
        return v


@router.get("/me")
async def read_me(user=Depends(get_current_user_with_role_and_plan)):
    return {"user": user}


@router.get("/profile")
async def get_profile(user: dict = Depends(get_verified_user)) -> dict:
    """Return the authenticated user's extended profile."""
    user_id = user.get("sub")
    cache_key = f"lumi:profile:{user_id}"
    cached = await cache_get(cache_key)
    if cached is not None:
        logger.debug("get_profile: cache hit for user_id=%s", user_id)
        return {"profile": cached}

    client = get_supabase_client()
    resp = (
        client.table("profiles")
        .select("*")
        .eq("id", user_id)
        .single()
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    await cache_set(cache_key, resp.data, ttl=300)
    return {"profile": resp.data}


@router.put("/profile")
async def update_profile(payload: ProfileUpdatePayload, user: dict = Depends(get_verified_user)) -> dict:
    """Update the authenticated user's profile fields."""
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid fields to update")

    client = get_supabase_client()
    resp = (
        client.table("profiles")
        .update(updates)
        .eq("id", user.get("sub"))
        .execute()
    )
    await cache_delete(f"lumi:profile:{user.get('sub')}")
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

    await cache_delete(f"lumi:profile:{user_id}")
    return {"avatar_url": avatar_url, "full_name": full_name}


@router.post("/session")
async def store_session(payload: SessionPayload, ttl_seconds: int = 3600, user=Depends(get_verified_user)):
    if ttl_seconds <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="TTL must be positive")
    ttl_seconds = min(ttl_seconds, _SESSION_MAX_TTL_SECONDS)

    redis = get_redis()
    user_id = user.get("sub")
    key = f"user:{user_id}:session"
    serialized = json.dumps(payload.data)
    if len(serialized) > _SESSION_MAX_PAYLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Session payload too large")
    await redis.set(key, serialized, ex=ttl_seconds)
    return {"stored": True, "key": key, "ttl_seconds": ttl_seconds}


@router.delete("/me")
async def delete_account(user: dict = Depends(get_verified_user)) -> dict:
    """Delete the authenticated user's auth record (cascading to profile data)."""
    user_id = user.get("sub")
    client = get_supabase_client()
    try:
        client.auth.admin.delete_user(user_id)
    except Exception as exc:
        logger.warning("Delete user failed for %s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete account",
        ) from exc
    return {"deleted": True}
