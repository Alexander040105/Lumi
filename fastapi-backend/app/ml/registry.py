"""
LUMI Model Registry
===================
Persist and version trained forecasting models using Supabase.

Tables used:
- ml_model_registry (metadata, metrics, active flag)
- forecast_cache (per-model cached predictions)
"""

import logging
import pickle
from datetime import date
from pathlib import Path
from uuid import UUID

from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)

_ARTIFACT_DIR = Path(__file__).resolve().parents[3] / "ml_artifacts"
_ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


class ModelRegistry:
    """Supabase-backed model registry with local artifact storage."""

    def register_model(
        self,
        model_name: str,
        model_version: str,
        model_type: str,
        target_variable: str,
        train_date: date,
        metrics: dict,
        artifact_bytes: bytes | None = None,
    ) -> UUID:
        """Insert a new model record and persist artifact to disk."""
        client = get_supabase_client()

        payload = {
            "model_name": model_name,
            "model_version": model_version,
            "model_type": model_type,
            "target_variable": target_variable,
            "train_date": train_date.isoformat(),
            "metrics": metrics,
            "is_active": False,
        }

        result = (
            client
            .table("ml_model_registry")
            .insert(payload)
            .execute()
        )
        row = result.data[0] if isinstance(result.data, list) else result.data
        model_id = UUID(row["model_id"])

        if artifact_bytes:
            artifact_path = _ARTIFACT_DIR / f"{model_id}.pkl"
            artifact_path.write_bytes(artifact_bytes)
            # Store relative path in model_path
            (
                client
                .table("ml_model_registry")
                .update({"model_path": str(artifact_path.relative_to(_ARTIFACT_DIR.parent))})
                .eq("model_id", str(model_id))
                .execute()
            )

        logger.info("Registered model %s (%s)", model_id, model_type)
        return model_id

    def activate_model(self, model_id: UUID) -> None:
        """Set is_active=false for all models of the same target, then activate the chosen one."""
        client = get_supabase_client()

        # Get target variable for this model
        row_result = (
            client
            .table("ml_model_registry")
            .select("target_variable")
            .eq("model_id", str(model_id))
            .single()
            .execute()
        )
        if not row_result.data:
            raise ValueError("Model not found")
        target = row_result.data["target_variable"]

        # Deactivate all models for this target
        (
            client
            .table("ml_model_registry")
            .update({"is_active": False})
            .eq("target_variable", target)
            .execute()
        )

        # Activate chosen model
        (
            client
            .table("ml_model_registry")
            .update({"is_active": True})
            .eq("model_id", str(model_id))
            .execute()
        )
        logger.info("Activated model %s for target %s", model_id, target)

    def load_active_model(self, target_variable: str):
        """Load the currently active model artifact from disk."""
        client = get_supabase_client()
        result = (
            client
            .table("ml_model_registry")
            .select("model_id, model_path")
            .eq("target_variable", target_variable)
            .eq("is_active", True)
            .single()
            .execute()
        )
        if not result.data:
            return None
        model_path = result.data.get("model_path")
        if not model_path:
            return None
        full_path = _ARTIFACT_DIR.parent / model_path
        if not full_path.exists():
            return None
        return pickle.loads(full_path.read_bytes())

    def list_models(self, target_variable: str | None = None) -> list[dict]:
        """List all models, optionally filtered by target variable."""
        client = get_supabase_client()
        query = client.table("ml_model_registry").select("*")
        if target_variable:
            query = query.eq("target_variable", target_variable)
        result = query.order("train_date", desc=True).execute()
        return result.data or []

    def save_forecast_cache(
        self,
        model_id: UUID,
        target_variable: str,
        horizon_years: int,
        years: list[int],
        predicted_values: list[float],
    ) -> None:
        """Write forecast points to the forecast_cache table."""
        client = get_supabase_client()
        rows = [
            {
                "model_id": str(model_id),
                "target_variable": target_variable,
                "horizon_years": horizon_years,
                "forecast_year": int(year),
                "predicted_value": float(value),
            }
            for year, value in zip(years, predicted_values)
        ]
        if rows:
            (
                client
                .table("forecast_cache")
                .insert(rows)
                .execute()
            )

    def get_forecast_from_cache(
        self,
        target_variable: str,
        horizon_years: int | None = None,
    ) -> list[dict]:
        """Fetch cached forecast for the active model."""
        client = get_supabase_client()
        active = (
            client
            .table("ml_model_registry")
            .select("model_id")
            .eq("target_variable", target_variable)
            .eq("is_active", True)
            .single()
            .execute()
        )
        if not active.data:
            return []
        model_id = active.data["model_id"]

        query = (
            client
            .table("forecast_cache")
            .select("*")
            .eq("model_id", model_id)
            .order("forecast_year")
        )
        if horizon_years:
            query = query.eq("horizon_years", horizon_years)
        result = query.execute()
        return result.data or []
