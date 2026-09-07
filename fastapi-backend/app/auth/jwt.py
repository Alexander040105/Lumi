import jwt

from app.config.settings import get_settings


def verify_jwt(token: str) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        return payload
    except jwt.InvalidTokenError as exc:
        raise ValueError("Invalid token") from exc
