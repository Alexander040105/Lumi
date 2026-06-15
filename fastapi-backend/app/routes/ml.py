from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.ml.registry import ModelRegistry
from app.ml.trainer import Trainer, MODEL_TYPES

router = APIRouter()


@router.post("/train", status_code=status.HTTP_202_ACCEPTED)
async def train_models(
    target_variable: str = "total_consumption_gwh",
    model_type: str | None = None,
    train_end_year: int = 2020,
    test_years: int = 4,
    horizon_years: int = 6,
):
    """Trigger model training pipeline.

    If model_type is provided, only that model is trained.
    Otherwise, all supported models are trained and the best
    one (lowest MAPE) is automatically activated.
    """
    trainer = Trainer(
        target_variable=target_variable,
        train_end_year=train_end_year,
        test_years=test_years,
        horizon_years=horizon_years,
    )

    if model_type:
        if model_type not in MODEL_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid model_type. Choose from: {MODEL_TYPES}",
            )
        result = trainer.train_single(model_type)
        return {"status": "trained", "results": [result]}

    results = trainer.train_all()
    return {"status": "trained", "results": results}


@router.get("/models")
async def list_models(target_variable: str | None = None):
    """List all registered models from the ml_model_registry table."""
    registry = ModelRegistry()
    return {"items": registry.list_models(target_variable)}


@router.put("/models/{model_id}/activate")
async def activate_model(model_id: UUID):
    """Activate a specific model version for its target variable."""
    registry = ModelRegistry()
    try:
        registry.activate_model(model_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return {"status": "activated", "model_id": str(model_id)}


@router.get("/forecast")
async def get_ml_forecast(
    target_variable: str = "total_consumption_gwh",
    horizon_years: int = 6,
):
    """Fetch the cached forecast for the currently active model."""
    registry = ModelRegistry()
    cached = registry.get_forecast_from_cache(
        target_variable=target_variable,
        horizon_years=horizon_years,
    )
    if not cached:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cached forecast found. Run training first.",
        )
    return {
        "target_variable": target_variable,
        "forecast_years": [c["forecast_year"] for c in cached],
        "forecast_values": [float(c["predicted_value"]) for c in cached],
        "model_id": cached[0]["model_id"],
    }
