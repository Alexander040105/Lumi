import json
from pathlib import Path
from functools import lru_cache
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AliasChoices, Field, field_validator


ENV_FILE = Path(__file__).resolve().parents[3] / ".env"
print(f"Loading settings from: {ENV_FILE}")
load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    app_name: str = "Lumi API"
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:5173"]

    supabase_url: str
    supabase_anon_key: str = Field(
        validation_alias=AliasChoices("SUPABASE_JWT_ANON_KEY", "SUPABASE_ANON_KEY")
    )
    supabase_service_role_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "SUPABASE_JWT_SERVICE_ROLE_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
        ),
    )
    supabase_jwt_secret: str | None = None

    model_config = SettingsConfigDict(extra="ignore")

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
    print(f"Settings env file path: {ENV_FILE}")
    return Settings()
