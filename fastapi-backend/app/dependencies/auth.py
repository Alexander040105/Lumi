from fastapi import Depends, HTTPException, Request, status

from app.auth.jwt import verify_jwt
from app.services.supabase_service import get_supabase_public_client


def get_bearer_token(request: Request) -> str:
    header = request.headers.get("Authorization")
    if not header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    parts = header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return parts[1]


def get_current_user(token: str = Depends(get_bearer_token)) -> dict:
    try:
        return verify_jwt(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def _extract_confirmed_at(user_data) -> str | None:
    if not user_data:
        return None
    if isinstance(user_data, dict):
        return user_data.get("email_confirmed_at") or user_data.get("confirmed_at")
    return getattr(user_data, "email_confirmed_at", None) or getattr(user_data, "confirmed_at", None)


def get_verified_user(token: str = Depends(get_bearer_token)) -> dict:
    try:
        claims = verify_jwt(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    confirmed_at = claims.get("email_confirmed_at") or claims.get("confirmed_at")
    if confirmed_at:
        return claims

    client = get_supabase_public_client()
    user_response = client.auth.get_user(token)
    user_data = getattr(user_response, "user", None) or getattr(user_response, "data", None)
    if isinstance(user_data, dict) and "user" in user_data:
        user_data = user_data["user"]

    confirmed_at = _extract_confirmed_at(user_data)
    if not confirmed_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address not verified"
        )

    return claims


# ---------------------------------------------------------------------------
# Role-aware dependencies
# ---------------------------------------------------------------------------

def _get_user_role(user_id: str) -> str:
    """Fetch the user's role from the user_roles table."""
    client = get_supabase_public_client()
    try:
        res = client.table("user_roles").select("role").eq("user_id", user_id).single().execute()
        data = getattr(res, "data", None)
        if isinstance(data, dict):
            return data.get("role", "user")
        return "user"
    except Exception:
        return "user"


def get_current_user_with_role(user: dict = Depends(get_verified_user)) -> dict:
    """Return the verified user dict enriched with their role."""
    user["role"] = _get_user_role(user.get("sub"))
    return user


def _get_effective_plan(user_id: str) -> str:
    """Return the user's effective plan. Admins/devs are always premium."""
    role = _get_user_role(user_id)
    if role in ("admin", "dev"):
        return "premium"
    # For normal users, fetch from profiles
    client = get_supabase_public_client()
    try:
        res = client.table("profiles").select("plan").eq("id", user_id).single().execute()
        data = getattr(res, "data", None)
        if isinstance(data, dict):
            return data.get("plan", "free")
        return "free"
    except Exception:
        return "free"


def get_current_user_with_role_and_plan(user: dict = Depends(get_verified_user)) -> dict:
    """Return the verified user dict enriched with their role and effective plan."""
    user["role"] = _get_user_role(user.get("sub"))
    user["plan"] = _get_effective_plan(user.get("sub"))
    return user


def require_admin(user: dict = Depends(get_verified_user)) -> dict:
    """Require the authenticated user to have an admin or dev role."""
    role = _get_user_role(user.get("sub"))
    if role not in ("admin", "dev"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    user["role"] = role
    user["plan"] = "premium"
    return user
