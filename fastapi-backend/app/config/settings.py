import json
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    app_name: str = "Lumi API"
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:5173"]

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str | None = None
    supabase_jwt_secret: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, list):
            return value
        if isinstance(value, str) and value.strip():
            return json.loads(value)
        return ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
