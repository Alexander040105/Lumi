import json

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import get_verified_user
from app.services.redis_client import get_redis
from app.services.supabase_service import get_supabase_client

router = APIRouter()


@router.get("/me")
async def read_me(user=Depends(get_verified_user)):
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


@router.post("/session")
async def store_session(payload: dict, ttl_seconds: int = 3600, user=Depends(get_verified_user)):
    redis = get_redis()
    user_id = user.get("sub")
    key = f"user:{user_id}:session"
    await redis.set(key, json.dumps(payload), ex=ttl_seconds)
    return {"stored": True, "key": key}
