import logging
from typing import Any

from fastapi import Depends, HTTPException, status

from app.dependencies.auth import get_current_user_with_role_and_plan
from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)


def _get_limits(plan: str) -> dict[str, Any]:
    """Fetch plan limits from the database."""
    client = get_supabase_client()
    try:
        res = client.table("plans_config").select("limits").eq("plan", plan).single().execute()
        if res.data:
            return res.data.get("limits", {})
    except Exception as exc:
        logger.warning("Failed to fetch plan limits for %s: %s", plan, exc)
    return {}


def _get_usage(user_id: str) -> dict[str, Any]:
    """Fetch current usage for a user."""
    client = get_supabase_client()
    try:
        res = client.table("user_usage_limits").select("*").eq("user_id", user_id).single().execute()
        return res.data or {}
    except Exception as exc:
        logger.warning("Failed to fetch usage for %s: %s", user_id, exc)
    return {}


def _ensure_usage_row(user_id: str) -> None:
    """Ensure a user_usage_limits row exists for the user."""
    client = get_supabase_client()
    try:
        client.table("user_usage_limits").upsert({"user_id": user_id}).execute()
    except Exception as exc:
        logger.warning("Failed to ensure usage row for %s: %s", user_id, exc)


def _increment_usage(user_id: str, column: str) -> None:
    """Increment a usage counter column for a user."""
    _ensure_usage_row(user_id)
    client = get_supabase_client()
    try:
        client.rpc("increment_usage", {"p_user_id": user_id, "p_column": column}).execute()
    except Exception as exc:
        logger.error("Failed to increment usage %s for %s: %s", column, user_id, exc)


class PlanGate:
    """FastAPI dependency that enforces plan-based usage limits.

    Usage:
        @router.post("/expensive-endpoint")
        async def endpoint(user: dict = Depends(PlanGate("chat_messages"))):
            ...
    """

    def __init__(self, feature: str):
        self.feature = feature

    def __call__(self, user: dict = Depends(get_current_user_with_role_and_plan)) -> dict:
        plan = user.get("plan", "free")
        # Premium / admin / dev bypass all limits
        if plan in ("premium", "admin", "dev"):
            return user

        limits = _get_limits(plan)
        limit = limits.get(self.feature)
        if limit is None:
            # No limit configured for this feature on this plan -> allow
            return user

        usage = _get_usage(user.get("sub"))
        current = usage.get(f"{self.feature}_this_month", 0)
        if current >= limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": f"Monthly limit reached for {self.feature}.",
                    "limit": limit,
                    "current": current,
                    "upgrade": True,
                },
            )

        _increment_usage(user.get("sub"), f"{self.feature}_this_month")
        return user
