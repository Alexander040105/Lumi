"""Centralized plan limit enforcement for LUMI subscription tiers.

This module provides:
- Plan limit resolution from the feature_permissions table (with fallback defaults)
- Usage counting per user per feature type per month
- Feature access checking with remaining quota
- Usage logging to the usage_tracking table
- FastAPI dependency factories for minimum plan requirements
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, HTTPException, status

from app.dependencies.auth import get_current_user_with_role_and_plan, get_verified_user
from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Fallback defaults (used if feature_permissions table is unavailable)
# ---------------------------------------------------------------------------

DEFAULT_LIMITS: dict[str, dict[str, int]] = {
    "free": {"simulations": 3, "chat_messages": 5, "ai_insights": 1},
    "pro": {"simulations": 20, "chat_messages": 50, "ai_insights": 5},
    "premium": {"simulations": 999_999, "chat_messages": 200, "ai_insights": 20},
}

DEFAULT_FEATURES: dict[str, dict[str, bool]] = {
    "free": {"chat_persistence": False, "data_export": False, "batch_compare": False, "priority_response": False},
    "pro": {"chat_persistence": True, "data_export": False, "batch_compare": False, "priority_response": False},
    "premium": {"chat_persistence": True, "data_export": True, "batch_compare": True, "priority_response": True},
}


def _get_month_bounds() -> tuple[str, str]:
    """Return ISO-format start and end of the current UTC month."""
    now = datetime.now(timezone.utc)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if now.month == 12:
        end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        end = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return start.isoformat(), end.isoformat()


# ---------------------------------------------------------------------------
# Plan limit resolution
# ---------------------------------------------------------------------------

def get_plan_limits(plan: str) -> dict[str, Any]:
    """Return limits and features for a given plan from the database or fallback defaults.

    Args:
        plan: One of "free", "pro", "premium".

    Returns:
        Dict with "limits" and "features" keys.
    """
    normalized = (plan or "free").lower()
    if normalized not in ("free", "pro", "premium"):
        normalized = "free"

    client = get_supabase_client()
    try:
        resp = (
            client.table("feature_permissions")
            .select("limits, features")
            .eq("plan", normalized)
            .single()
            .execute()
        )
        if resp.data:
            return {
                "limits": resp.data.get("limits") or DEFAULT_LIMITS.get(normalized, {}),
                "features": resp.data.get("features") or DEFAULT_FEATURES.get(normalized, {}),
            }
    except Exception as exc:
        logger.warning("Failed to fetch feature_permissions for plan=%s: %s", normalized, exc)

    return {
        "limits": DEFAULT_LIMITS.get(normalized, DEFAULT_LIMITS["free"]),
        "features": DEFAULT_FEATURES.get(normalized, DEFAULT_FEATURES["free"]),
    }


# ---------------------------------------------------------------------------
# Usage tracking
# ---------------------------------------------------------------------------

def get_usage_this_month(user_id: str, feature_type: str) -> int:
    """Count how many times a user has used a feature this month.

    Args:
        user_id: The user's UUID (from auth.users).
        feature_type: One of "chat", "simulation", "ai_insight_ecosim", "ai_insight_energyhub".

    Returns:
        Integer count of usage events this month.
    """
    if not user_id:
        return 0

    start_iso, end_iso = _get_month_bounds()
    client = get_supabase_client()
    try:
        resp = (
            client.table("usage_tracking")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .eq("feature_type", feature_type)
            .gte("created_at", start_iso)
            .lt("created_at", end_iso)
            .execute()
        )
        return resp.count or 0
    except Exception as exc:
        logger.warning("Failed to count usage for user=%s feature=%s: %s", user_id, feature_type, exc)
        return 0


def increment_usage(
    user_id: str,
    feature_type: str,
    tokens_input: int = 0,
    tokens_output: int = 0,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Log a usage event for a gated feature.

    Args:
        user_id: The user's UUID.
        feature_type: One of "chat", "simulation", "ai_insight_ecosim", "ai_insight_energyhub".
        tokens_input: Number of input tokens (for LLM-based features).
        tokens_output: Number of output tokens (for LLM-based features).
        metadata: Optional JSON metadata.
    """
    if not user_id:
        return

    client = get_supabase_client()
    try:
        client.table("usage_tracking").insert({
            "user_id": user_id,
            "feature_type": feature_type,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "metadata": metadata or {},
        }).execute()
    except Exception as exc:
        logger.warning("Failed to log usage for user=%s feature=%s: %s", user_id, feature_type, exc)


# ---------------------------------------------------------------------------
# Feature access checking
# ---------------------------------------------------------------------------

def check_feature_access(
    user: dict[str, Any],
    feature_type: str,
) -> dict[str, Any]:
    """Check whether a user can access a gated feature.

    Args:
        user: The user dict (must contain "sub" and "plan" keys).
        feature_type: One of "chat", "simulation", "ai_insight".

    Returns:
        Dict with:
            - allowed (bool): Whether the user can proceed.
            - remaining (int): How many uses remain this month.
            - limit (int): The monthly limit for this feature.
            - plan (str): The user's effective plan.
            - message (str): Human-readable message if not allowed.
    """
    user_id = user.get("sub")
    plan = user.get("plan", "free")
    limits_data = get_plan_limits(plan)
    limits = limits_data.get("limits", {})

    # Map feature_type to limit key
    limit_key = {
        "chat": "chat_messages",
        "simulation": "simulations",
        "ai_insight": "ai_insights",
        "ai_insight_ecosim": "ai_insights",
        "ai_insight_energyhub": "ai_insights",
    }.get(feature_type, feature_type)

    limit = limits.get(limit_key, 0)
    if limit == 0:
        return {
            "allowed": False,
            "remaining": 0,
            "limit": 0,
            "plan": plan,
            "message": f"This feature is not available on your plan ({plan}).",
        }

    used = get_usage_this_month(user_id, feature_type)
    remaining = max(limit - used, 0)

    if remaining <= 0:
        return {
            "allowed": False,
            "remaining": 0,
            "limit": limit,
            "plan": plan,
            "message": (
                f"You have reached your monthly limit ({limit}) for this feature. "
                "Upgrade your plan to continue using it."
            ),
        }

    return {
        "allowed": True,
        "remaining": remaining,
        "limit": limit,
        "plan": plan,
        "message": "",
    }


def get_feature_limit(user: dict[str, Any], feature_type: str) -> int:
    """Return the monthly limit for a feature type for the user's plan."""
    plan = user.get("plan", "free")
    limits_data = get_plan_limits(plan)
    limits = limits_data.get("limits", {})
    limit_key = {
        "chat": "chat_messages",
        "simulation": "simulations",
        "ai_insight": "ai_insights",
        "ai_insight_ecosim": "ai_insights",
        "ai_insight_energyhub": "ai_insights",
    }.get(feature_type, feature_type)
    return limits.get(limit_key, 0)


# ---------------------------------------------------------------------------
# FastAPI dependency factories
# ---------------------------------------------------------------------------

def require_plan(min_plan: str):
    """Factory that returns a FastAPI dependency requiring a minimum plan.

    Usage:
        @router.get("/premium-only")
        async def premium_endpoint(
            user: dict = Depends(require_plan("premium")),
        ):
            ...
    """
    plan_hierarchy = {"free": 0, "pro": 1, "premium": 2}
    min_level = plan_hierarchy.get(min_plan, 0)

    def _check_plan(user: dict = Depends(get_current_user_with_role_and_plan)) -> dict[str, Any]:
        plan = user.get("plan", "free")
        user_level = plan_hierarchy.get(plan, 0)
        if user_level < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": f"This feature requires a {min_plan.title()} plan or higher.",
                    "current_plan": plan,
                    "required_plan": min_plan,
                    "upgrade": True,
                },
            )
        return user

    return _check_plan
