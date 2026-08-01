import json
import logging
from pathlib import Path
from functools import lru_cache
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AliasChoices, Field, field_validator

logger = logging.getLogger(__name__)

ENV_FILE = Path(__file__).resolve().parents[3] / ".env"
logger.info("Loading settings from: %s", ENV_FILE)
load_dotenv(ENV_FILE)


class Settings(BaseSettings):
    # App / network
    app_name: str = "Lumi API"
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:5173"]
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # Supabase
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
    supabase_oauth_callback_url: str | None = None

    # Direct Postgres password (kept for compatibility / local dev)
    supabase_db_password: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SUPABASE_DB_PASSWORD", "SUPABSE_DB_PASSWORD"),
    )

    # Redis / caching
    upstash_redis_url: str | None = None
    redis_ttl_seconds: int = 300
    use_redis_cache: bool = True

    # AI / LLM
    gemini_api_key: str | None = None
    gemini_debug: bool = False
    groq_api_key: str | None = None
    groq_temperature: float = 0.5
    embedding_model: str = "all-MiniLM-L6-v2"
    rag_score_threshold: float = 0.25
    rag_top_k: int = 5

    # External services
    nominatim_email: str | None = None
    psgc_api_code: str | None = None

    # Hydrology / GIS
    hydrobasins_dir: Path | None = None
    hydrobasins_level: int = 6
    hydrology_batch_size: int = 500
    hydrology_runoff_coeff: float = 0.35
    hydrology_use_bbox_filter: bool = True
    hydrology_dem_path: Path | None = None
    hydrology_source: str = "Derived Hydrology Data"

    # Browser automation (scraping helpers)
    brave_binary: Path | None = None
    chromedriver_path: Path | None = None

    # Feature toggles
    use_supabase_api: bool = True
    enable_rag: bool = True
    enable_forecast: bool = True

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
    logger.info("Settings env file path: %s", ENV_FILE)
    return Settings()
