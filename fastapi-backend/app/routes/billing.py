"""Stub billing endpoints for Stripe / PayMongo integration.

TODO:
    - Replace checkout stub with real Stripe Checkout Session or PayMongo Link.
    - Implement webhook signature verification.
    - On successful payment, update profiles.plan to 'premium'.
"""

from typing import Any

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user_with_role_and_plan

router = APIRouter()


@router.post("/checkout")
async def create_checkout_session(
    user: dict = Depends(get_current_user_with_role_and_plan),
) -> dict[str, Any]:
    """Create a checkout session for Premium upgrade.

    Returns a payment provider URL when configured; otherwise returns a stub.
    """
    return {
        "url": None,
        "message": "Billing provider not configured yet. Contact admin for upgrade.",
        "user_id": user.get("sub"),
        "plan_requested": "premium",
    }


@router.post("/webhook")
async def billing_webhook(payload: dict) -> dict[str, Any]:
    """Receive payment provider webhooks.

    TODO: Verify Stripe / PayMongo signature and upgrade the user's plan.
    """
    return {"received": True, "note": "No-op stub — integrate real provider here."}
