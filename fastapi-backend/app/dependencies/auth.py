from fastapi import Depends, HTTPException, Request, status

import logging

from app.services.data_cache import cache_get_sync, cache_set_sync
from app.services.supabase_service import get_supabase_client, get_supabase_public_client

logger = logging.getLogger(__name__)


def get_bearer_token(request: Request) -> str:
    header = request.headers.get("Authorization")
    if not header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    parts = header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return parts[1]


def get_optional_bearer_token(request: Request) -> str | None:
    """Extract bearer token if present; return None if missing/invalid."""
    header = request.headers.get("Authorization")
    if not header:
        return None
    parts = header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]


def _extract_user_data(user_response):
    """Extract user dict from Supabase auth.get_user response."""
    user_data = getattr(user_response, "user", None)
    if not user_data and hasattr(user_response, "data"):
        user_data = user_response.data
    if isinstance(user_data, dict) and "user" in user_data:
        user_data = user_data["user"]
    return user_data


def _build_user_claims(user_data) -> dict:
    """Build a claims dict from Supabase User object or dict."""
    if isinstance(user_data, dict):
        return {
            "sub": user_data.get("id"),
            "email": user_data.get("email"),
            "email_confirmed_at": user_data.get("email_confirmed_at") or user_data.get("confirmed_at"),
            "user_metadata": user_data.get("user_metadata", {}),
        }
    # Handle Supabase User object
    return {
        "sub": getattr(user_data, "id", None),
        "email": getattr(user_data, "email", None),
        "email_confirmed_at": getattr(user_data, "email_confirmed_at", None) or getattr(user_data, "confirmed_at", None),
        "user_metadata": getattr(user_data, "user_metadata", {}) or {},
    }


def get_current_user(token: str = Depends(get_bearer_token)) -> dict:
    client = get_supabase_public_client()
    try:
        user_response = client.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_data = _extract_user_data(user_response)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return _build_user_claims(user_data)


def get_verified_user(token: str = Depends(get_bearer_token)) -> dict:
    client = get_supabase_public_client()
    try:
        user_response = client.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_data = _extract_user_data(user_response)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    confirmed_at = (
        getattr(user_data, "email_confirmed_at", None)
        or getattr(user_data, "confirmed_at", None)
        or (isinstance(user_data, dict) and (user_data.get("email_confirmed_at") or user_data.get("confirmed_at")))
    )
    if not confirmed_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address not verified"
        )

    return _build_user_claims(user_data)


def get_verified_user_optional(token: str | None = Depends(get_optional_bearer_token)) -> dict | None:
    """Return verified user if a valid token is provided, otherwise None."""
    if not token:
        return None
    client = get_supabase_public_client()
    try:
        user_response = client.auth.get_user(token)
    except Exception:
        return None

    user_data = _extract_user_data(user_response)
    if not user_data:
        return None

    confirmed_at = (
        getattr(user_data, "email_confirmed_at", None)
        or getattr(user_data, "confirmed_at", None)
        or (isinstance(user_data, dict) and (user_data.get("email_confirmed_at") or user_data.get("confirmed_at")))
    )
    if not confirmed_at:
        return None

    return _build_user_claims(user_data)


# ---------------------------------------------------------------------------
# Role-aware dependencies
# ---------------------------------------------------------------------------

def _get_user_role(user_id: str) -> str:
    """Fetch the user's role from the user_roles table using service_role (bypasses RLS).

    The result is cached in Redis with a short TTL to avoid hitting Supabase on every
    protected request.
    """
    cache_key = f"lumi:auth:{user_id}:role"
    cached = cache_get_sync(cache_key)
    if isinstance(cached, str):
        logger.debug("_get_user_role: cache hit for user_id=%s", user_id)
        return cached

    client = get_supabase_client()
    try:
        res = client.table("user_roles").select("role").eq("user_id", user_id).single().execute()
        data = getattr(res, "data", None)
        if isinstance(data, dict):
            role = data.get("role", "user")
            logger.debug("_get_user_role: user_id=%s role=%s", user_id, role)
            cache_set_sync(cache_key, role, ttl=300)
            return role
        logger.warning("_get_user_role: no data returned for user_id=%s", user_id)
        return "user"
    except Exception as exc:
        # NOTE: Returning "user" on DB failure fails safely (no privilege escalation),
        # but legitimate admins will be denied access during outages.
        logger.error("_get_user_role DB failure for user_id=%s: %s", user_id, exc)
        return "user"


def get_current_user_with_role(user: dict = Depends(get_verified_user)) -> dict:
    """Return the verified user dict enriched with their role."""
    user["role"] = _get_user_role(user.get("sub"))
    return user


def _get_effective_plan(user_id: str, role: str | None = None) -> str:
    """Return the user's effective plan. Admins/devs are always premium.

    Cached in Redis with a short TTL to match role caching.
    """
    cache_key = f"lumi:auth:{user_id}:plan"
    cached = cache_get_sync(cache_key)
    if isinstance(cached, str):
        logger.debug("_get_effective_plan: cache hit for user_id=%s", user_id)
        return cached

    if role is None:
        role = _get_user_role(user_id)
    if role in ("admin", "dev"):
        plan = "premium"
    else:
        # For normal users, fetch from profiles using service_role
        client = get_supabase_client()
        try:
            res = client.table("profiles").select("plan").eq("id", user_id).single().execute()
            data = getattr(res, "data", None)
            plan = data.get("plan", "free") if isinstance(data, dict) else "free"
        except Exception as exc:
            logger.error("_get_effective_plan failed for user_id=%s: %s", user_id, exc)
            plan = "free"
    cache_set_sync(cache_key, plan, ttl=300)
    return plan


def get_current_user_with_role_and_plan(user: dict = Depends(get_verified_user)) -> dict:
    """Return the verified user dict enriched with their role and effective plan."""
    role = _get_user_role(user.get("sub"))
    user["role"] = role
    user["plan"] = _get_effective_plan(user.get("sub"), role=role)
    return user


def require_admin(user: dict = Depends(get_verified_user)) -> dict:
    """Require the authenticated user to have an admin or dev role."""
    role = _get_user_role(user.get("sub"))
    if role not in ("admin", "dev"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    user["role"] = role
    user["plan"] = "premium"
    return user
