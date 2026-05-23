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
