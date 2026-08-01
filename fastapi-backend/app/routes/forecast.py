"""Forecasting API routes for LUMI EnergyHub.

Provides endpoints for:
- /forecast/run — trigger a new SARIMA/ARIMAX forecast
- /forecast/backtest — run walk-forward backtesting
- /forecast/models — list model runs from registry
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Query

from app.ml.predictor import get_energyhub_ml
from app.services.forecasting import (
    SARIMAConfig,
    backtest_walk_forward,
    log_model_run,
    run_forecast_pipeline,
    reconcile_forecast_cache,
)
import pandas as pd

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/run")
async def run_forecast(
    metric: str = Query(default="consumption", description="consumption or peak_demand"),
    order_p: int = Query(default=1, description="AR order"),
    order_d: int = Query(default=1, description="Differencing order"),
    order_q: int = Query(default=1, description="MA order"),
    forecast_to: int = Query(default=2030, description="Forecast end year"),
) -> dict[str, Any]:
    """Run a SARIMA forecast on demand.

    Uses DOE historical data loaded by EnergyHubML.
    """
    ml = get_energyhub_ml()
    if ml._historical is None or ml._historical.empty:
        return {"error": "Historical data not available"}

    target_col = "total_consumption_gwh" if metric == "consumption" else "total_peak_demand_mw"

    config = SARIMAConfig(order=(order_p, order_d, order_q))
    forecast_years = list(range(2025, forecast_to + 1))

    result = run_forecast_pipeline(
        df=ml._historical,
        target_col=target_col,
        forecast_years=forecast_years,
        config=config,
    )

    # Log to model registry
    log_model_run(
        model_name=result.model_name,
        target_variable=target_col,
        metrics=result.metrics or {},
        hyperparameters={"order": list(config.order), "seasonal_order": list(config.seasonal_order)},
        run_type="train",
    )

    # Reconcile with cached forecast
    cached = ml.get_forecast(metric)
    reconciled = reconcile_forecast_cache(result, cached)

    return reconciled


@router.get("/backtest")
async def run_backtest(
    metric: str = Query(default="consumption"),
    train_end_year: int = Query(default=2020),
    order_p: int = Query(default=1),
    order_d: int = Query(default=1),
    order_q: int = Query(default=1),
) -> dict[str, Any]:
    """Run walk-forward backtesting on historical data."""
    ml = get_energyhub_ml()
    if ml._historical is None or ml._historical.empty:
        return {"error": "Historical data not available"}

    target_col = "total_consumption_gwh" if metric == "consumption" else "total_peak_demand_mw"
    df = ml._historical.sort_values("year").reset_index(drop=True)
    series = df.set_index("year")[target_col]

    config = SARIMAConfig(order=(order_p, order_d, order_q))
    train_end_idx = (df["year"] <= train_end_year).sum()

    if train_end_idx >= len(series):
        return {"error": f"train_end_year {train_end_year} is at or after the end of data"}

    bt = backtest_walk_forward(series, train_end_idx, config)

    log_model_run(
        model_name=bt.model_name,
        target_variable=target_col,
        metrics=bt.metrics,
        hyperparameters={"order": list(config.order)},
        run_type="backtest",
    )

    return {
        "model_name": bt.model_name,
        "train_period": bt.train_period,
        "test_period": bt.test_period,
        "actual_values": bt.actual_values,
        "predicted_values": bt.predicted_values,
        "metrics": bt.metrics,
        "residuals": bt.residuals,
    }


@router.get("/models")
async def list_model_runs(
    limit: int = Query(default=20, le=100),
) -> dict[str, Any]:
    """List recent model runs from the forecast_model_runs registry."""
    try:
        from app.services.supabase_service import get_supabase_client
        client = get_supabase_client()
        resp = (
            client.table("forecast_model_runs")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return {"items": resp.data or []}
    except Exception as exc:
        logger.warning("Failed to fetch model runs: %s", exc)
        return {"items": [], "error": str(exc)}
