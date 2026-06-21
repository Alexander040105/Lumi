import logging
import re
from typing import Any

import httpx
from supabase import Client, create_client

from app.config.settings import get_settings

logger = logging.getLogger(__name__)

_JWT_PATTERN = re.compile(r"^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$")


def _is_jwt_key(key: str | None) -> bool:
    return bool(key) and _JWT_PATTERN.match(key) is not None


class SupabaseResponse:
    def __init__(self, data: Any):
        self.data = data


class SupabaseRestQuery:
    def __init__(self, client: "SupabaseRestClient", table: str):
        self._client = client
        self._table = table
        self._select = "*"
        self._filters: list[tuple[str, str]] = []
        self._single = False
        self._limit: int | None = None

    def select(self, columns: str = "*") -> "SupabaseRestQuery":
        self._select = columns
        return self

    def eq(self, column: str, value: str) -> "SupabaseRestQuery":
        self._filters.append((column, value))
        return self

    def limit(self, n: int) -> "SupabaseRestQuery":
        self._limit = n
        return self

    def offset(self, n: int) -> "SupabaseRestQuery":
        self._offset = n
        return self

    def single(self) -> "SupabaseRestQuery":
        self._single = True
        return self

    def execute(self) -> SupabaseResponse:
        params: dict[str, str] = {"select": self._select}
        for column, value in self._filters:
            params[column] = f"eq.{value}"
        if self._single:
            params["limit"] = "1"
        elif self._limit is not None:
            params["limit"] = str(self._limit)
        if getattr(self, "_offset", None) is not None:
            params["offset"] = str(self._offset)

        url = f"{self._client.base_url}/rest/v1/{self._table}"
        response = self._client.http.get(url, params=params, headers=self._client.headers)
        response.raise_for_status()
        data = response.json()
        if self._single:
            data = data[0] if data else None
        return SupabaseResponse(data)


class SupabaseRestClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
        }
        self.http = httpx.Client(timeout=10.0)

    def table(self, table_name: str) -> SupabaseRestQuery:
        return SupabaseRestQuery(self, table_name)


def get_supabase_client() -> Client | SupabaseRestClient:
    settings = get_settings()
    key = settings.supabase_service_role_key or settings.supabase_anon_key
    key_source = "service_role" if settings.supabase_service_role_key else "anon"
    if not key:
        raise ValueError("Supabase key is missing. Check your .env and environment overrides.")
    if _is_jwt_key(key):
        logger.debug(
            "Supabase settings loaded: url=%s key_source=%s key_present=%s key_len=%s",
            settings.supabase_url,
            key_source,
            bool(key),
            len(key),
        )
        return create_client(settings.supabase_url, key)

    logger.warning(
        "Supabase key is not JWT; using REST client fallback for table queries only."
    )
    logger.debug(
        "Supabase settings loaded: url=%s key_source=%s key_present=%s key_len=%s",
        settings.supabase_url,
        key_source,
        bool(key),
        len(key),
    )
    return SupabaseRestClient(settings.supabase_url, key)


def get_supabase_public_client() -> Client | SupabaseRestClient:
    settings = get_settings()
    if not settings.supabase_anon_key:
        raise ValueError("Supabase anon key is missing. Check your .env and environment overrides.")
    if _is_jwt_key(settings.supabase_anon_key):
        logger.debug(
            "Supabase public settings loaded: url=%s key_present=%s key_len=%s",
            settings.supabase_url,
            bool(settings.supabase_anon_key),
            len(settings.supabase_anon_key),
        )
        return create_client(settings.supabase_url, settings.supabase_anon_key)

    logger.warning(
        "Supabase anon key is not JWT; using REST client fallback for table queries only."
    )
    logger.debug(
        "Supabase public settings loaded: url=%s key_present=%s key_len=%s",
        settings.supabase_url,
        bool(settings.supabase_anon_key),
        len(settings.supabase_anon_key),
    )
    return SupabaseRestClient(settings.supabase_url, settings.supabase_anon_key)
