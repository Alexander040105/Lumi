import json

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_verified_user
from app.services.redis_client import get_redis

router = APIRouter()


@router.get("/me")
async def read_me(user=Depends(get_verified_user)):
    return {"user": user}


@router.post("/session")
async def store_session(payload: dict, ttl_seconds: int = 3600, user=Depends(get_verified_user)):
    redis = get_redis()
    user_id = user.get("sub")
    key = f"user:{user_id}:session"
    await redis.set(key, json.dumps(payload), ex=ttl_seconds)
    return {"stored": True, "key": key}
