"""SARIMA/ARIMAX forecasting module for LUMI EnergyHub.

Provides:
- SARIMA(p,d,q)(P,D,Q,s) fitting and forecasting
- ARIMAX with exogenous variables
- Walk-forward backtesting
- Model registry integration (forecast_model_runs table)
- Forecast cache reconciliation

Uses statsmodels for the underlying ARIMA/SARIMAX implementation.
"""
from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Suppress statsmodels convergence warnings for production
warnings.filterwarnings("ignore", category=Warning, module="statsmodels")


@dataclass
class SARIMAConfig:
    """SARIMA model configuration."""
    order: tuple[int, int, int] = (1, 1, 1)
    seasonal_order: tuple[int, int, int, int] = (0, 0, 0, 0)  # no seasonality for annual data
    trend: str | None = None


@dataclass
class BacktestResult:
    """Result of a walk-forward backtest."""
    model_name: str
    train_period: str
    test_period: str
    actual_values: list[float]
    predicted_values: list[float]
    metrics: dict[str, float]
    residuals: list[float] = field(default_factory=list)


@dataclass
class ForecastResult:
    """Result of a forecast."""
    model_name: str
    forecast_years: list[int]
    forecast_values: list[float]
    ci_lower: list[float]
    ci_upper: list[float]
    training_period: str
    test_period: str
    metrics: dict[str, float] | None = None


def _safe_float(val: Any) -> float | None:
    """Convert to float, returning None for NaN/Inf."""
    try:
        f = float(val)
        if np.isnan(f) or np.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


def fit_sarima(
    series: pd.Series,
    config: SARIMAConfig | None = None,
) -> Any:
    """Fit a SARIMA model to a time series.

    Args:
        series: Pandas Series with datetime index or integer year index
        config: SARIMA configuration

    Returns:
        Fitted SARIMAXResults object
    """
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    if config is None:
        config = SARIMAConfig()

    model = SARIMAX(
        series,
        order=config.order,
        seasonal_order=config.seasonal_order,
        trend=config.trend,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    return model.fit(disp=False)


def fit_arimax(
    series: pd.Series,
    exog: pd.DataFrame | None = None,
    order: tuple[int, int, int] = (1, 1, 1),
) -> Any:
    """Fit an ARIMAX model with exogenous variables.

    Args:
        series: Target time series
        exog: Exogenous variables DataFrame (must align with series index)
        order: ARIMA order (p, d, q)

    Returns:
        Fitted SARIMAXResults object
    """
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    model = SARIMAX(
        series,
        exog=exog,
        order=order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    return model.fit(disp=False)


def forecast_sarima(
    fitted_model: Any,
    steps: int = 6,
    exog: pd.DataFrame | None = None,
    ci_alpha: float = 0.05,
) -> dict[str, list[float | None]]:
    """Generate forecast with confidence intervals from a fitted SARIMA model.

    Args:
        fitted_model: Fitted SARIMAXResults
        steps: Number of periods to forecast
        exog: Exogenous variables for forecast period
        ci_alpha: Confidence interval alpha (0.05 = 95% CI)

    Returns:
        Dict with forecast_values, ci_lower, ci_upper
    """
    forecast = fitted_model.get_forecast(steps=steps, exog=exog)
    pred_mean = forecast.predicted_mean
    ci = forecast.conf_int(alpha=ci_alpha)

    values = [_safe_float(v) for v in pred_mean.values]
    lower = [_safe_float(v) for v in ci.iloc[:, 0].values]
    upper = [_safe_float(v) for v in ci.iloc[:, 1].values]

    return {
        "forecast_values": values,
        "ci_lower": lower,
        "ci_upper": upper,
    }


def backtest_walk_forward(
    series: pd.Series,
    train_end_idx: int,
    config: SARIMAConfig | None = None,
    exog: pd.DataFrame | None = None,
) -> BacktestResult:
    """Walk-forward backtesting: train on [0:train_end], predict one step,
    add actual to training set, retrain, repeat.

    Args:
        series: Full time series
        train_end_idx: Index where training ends (test starts at train_end_idx)
        config: SARIMA config
        exog: Optional exogenous variables

    Returns:
        BacktestResult with actuals, predictions, and metrics
    """
    if config is None:
        config = SARIMAConfig()

    train = series.iloc[:train_end_idx]
    test = series.iloc[train_end_idx:]

    actuals: list[float] = []
    predictions: list[float] = []

    history = train.copy()

    for i in range(len(test)):
        try:
            exog_train = exog.iloc[:train_end_idx + i] if exog is not None else None
            exog_forecast = exog.iloc[[train_end_idx + i]] if exog is not None else None

            if exog is not None:
                model = fit_arimax(history, exog=exog_train, order=config.order)
                fc = forecast_sarima(model, steps=1, exog=exog_forecast)
            else:
                model = fit_sarima(history, config)
                fc = forecast_sarima(model, steps=1)

            pred = fc["forecast_values"][0] if fc["forecast_values"] else None
            if pred is None:
                pred = float(history.iloc[-1])  # naive fallback

            predictions.append(pred)
            actuals.append(float(test.iloc[i]))

            # Add actual to history for next iteration
            history = pd.concat([history, test.iloc[[i]]])

        except Exception as exc:
            logger.warning("Backtest step %d failed: %s", i, exc)
            predictions.append(float(history.iloc[-1]))
            actuals.append(float(test.iloc[i]))
            history = pd.concat([history, test.iloc[[i]]])

    metrics = calculate_metrics(actuals, predictions)
    residuals = [a - p for a, p in zip(actuals, predictions)]

    train_years = f"{int(series.index[0])}-{int(series.index[train_end_idx - 1])}"
    test_years = f"{int(series.index[train_end_idx])}-{int(series.index[-1])}"

    return BacktestResult(
        model_name=f"SARIMA{config.order}{config.seasonal_order}",
        train_period=train_years,
        test_period=test_years,
        actual_values=actuals,
        predicted_values=predictions,
        metrics=metrics,
        residuals=residuals,
    )


def calculate_metrics(actuals: list[float], predictions: list[float]) -> dict[str, float]:
    """Calculate standard forecast accuracy metrics."""
    if not actuals or not predictions:
        return {"mae": 0, "rmse": 0, "mape": 0, "smape": 0}

    errors = [a - p for a, p in zip(actuals, predictions)]
    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(np.square(errors))))

    # MAPE with zero-guard
    mape_values = [abs(e / a) * 100 for a, e in zip(actuals, errors) if abs(a) > 1e-8]
    mape = float(np.mean(mape_values)) if mape_values else 0.0

    # sMAPE (symmetric MAPE)
    smape_values = [abs(e) / ((abs(a) + abs(p)) / 2) * 100 for a, p, e in zip(actuals, predictions, errors) if (abs(a) + abs(p)) > 1e-8]
    smape = float(np.mean(smape_values)) if smape_values else 0.0

    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "mape": round(mape, 2),
        "smape": round(smape, 2),
    }


def run_forecast_pipeline(
    df: pd.DataFrame,
    target_col: str = "total_consumption_gwh",
    year_col: str = "year",
    forecast_years: list[int] | None = None,
    train_end_year: int = 2020,
    config: SARIMAConfig | None = None,
    exog_cols: list[str] | None = None,
) -> ForecastResult:
    """Full forecasting pipeline: train, backtest, forecast future.

    Args:
        df: DataFrame with historical data
        target_col: Column to forecast
        year_col: Column with year values
        forecast_years: Years to forecast (default: 2025-2030)
        train_end_year: Last year in training set for backtesting
        config: SARIMA configuration
        exog_cols: Optional exogenous variable column names

    Returns:
        ForecastResult with forecast values, CIs, and backtest metrics
    """
    if forecast_years is None:
        forecast_years = list(range(2025, 2031))

    if config is None:
        config = SARIMAConfig()

    # Prepare series
    df = df.sort_values(year_col).reset_index(drop=True)
    series = df.set_index(year_col)[target_col]

    # Exogenous variables
    exog = df.set_index(year_col)[exog_cols] if exog_cols else None

    # Backtest
    train_end_idx = (df[year_col] <= train_end_year).sum()
    if train_end_idx < len(series):
        bt = backtest_walk_forward(series, train_end_idx, config, exog)
        metrics = bt.metrics
        train_period = bt.train_period
        test_period = bt.test_period
    else:
        metrics = {}
        train_period = f"{int(series.index[0])}-{train_end_year}"
        test_period = f"{train_end_year + 1}-{int(series.index[-1])}"

    # Full model fit
    if exog is not None:
        fitted = fit_arimax(series, exog=exog, order=config.order)
        # Forecast future exog (naive: use last values)
        future_exog = pd.DataFrame(
            {col: [exog[col].iloc[-1]] * len(forecast_years) for col in exog.columns},
            index=forecast_years,
        )
        fc = forecast_sarima(fitted, steps=len(forecast_years), exog=future_exog)
    else:
        fitted = fit_sarima(series, config)
        fc = forecast_sarima(fitted, steps=len(forecast_years))

    return ForecastResult(
        model_name=f"SARIMA{config.order}{config.seasonal_order}",
        forecast_years=forecast_years,
        forecast_values=fc["forecast_values"],
        ci_lower=fc["ci_lower"],
        ci_upper=fc["ci_upper"],
        training_period=f"{int(series.index[0])}-{int(series.index[-1])}",
        test_period=test_period,
        metrics=metrics,
    )


def reconcile_forecast_cache(
    forecast_result: ForecastResult,
    cached_forecast: dict[str, Any] | None,
) -> dict[str, Any]:
    """Reconcile a new forecast with cached forecast data.

    If cached data exists and covers the same years, merge by taking
    the newer forecast. If years differ, extend with new years.

    Args:
        forecast_result: New ForecastResult
        cached_forecast: Dict from cache or None

    Returns:
        Reconciled forecast dict ready for API response
    """
    new_data = {
        "forecast_years": forecast_result.forecast_years,
        "forecast_values": forecast_result.forecast_values,
        "ci_lower": forecast_result.ci_lower,
        "ci_upper": forecast_result.ci_upper,
        "model": forecast_result.model_name,
        "training_period": forecast_result.training_period,
        "test_period": forecast_result.test_period,
        "metrics": forecast_result.metrics,
    }

    if not cached_forecast or not cached_forecast.get("forecast_years"):
        return new_data

    cached_years = set(cached_forecast.get("forecast_years", []))
    new_years = set(forecast_result.forecast_years)

    # If new forecast covers all cached years, replace entirely
    if new_years >= cached_years:
        return new_data

    # Otherwise merge: use cached for overlapping, new for new years
    merged_years = sorted(cached_years | new_years)
    merged_values: list[float | None] = []
    merged_lower: list[float | None] = []
    merged_upper: list[float | None] = []

    new_map = {
        y: (v, l, u)
        for y, v, l, u in zip(
            forecast_result.forecast_years,
            forecast_result.forecast_values,
            forecast_result.ci_lower,
            forecast_result.ci_upper,
        )
    }
    cached_map = {
        y: (v, l, u)
        for y, v, l, u in zip(
            cached_forecast.get("forecast_years", []),
            cached_forecast.get("forecast_values", []),
            cached_forecast.get("ci_lower", []),
            cached_forecast.get("ci_upper", []),
        )
    }

    for y in merged_years:
        if y in new_map:
            v, l, u = new_map[y]
        else:
            v, l, u = cached_map.get(y, (None, None, None))
        merged_values.append(v)
        merged_lower.append(l)
        merged_upper.append(u)

    return {
        "forecast_years": merged_years,
        "forecast_values": merged_values,
        "ci_lower": merged_lower,
        "ci_upper": merged_upper,
        "model": forecast_result.model_name,
        "training_period": forecast_result.training_period,
        "test_period": forecast_result.test_period,
        "metrics": forecast_result.metrics,
    }


def log_model_run(
    model_name: str,
    target_variable: str,
    metrics: dict[str, float],
    hyperparameters: dict[str, Any] | None = None,
    run_type: str = "train",
    status: str = "success",
) -> str | None:
    """Log a model run to the forecast_model_runs table.

    Args:
        model_name: Name of the model
        target_variable: What was forecasted
        metrics: Performance metrics dict
        hyperparameters: Model hyperparameters
        run_type: 'train', 'backtest', 'retrain', or 'evaluate'
        status: 'success', 'failed', 'running'

    Returns:
        Run ID if logged successfully, None otherwise
    """
    try:
        from app.services.supabase_service import get_supabase_client
        import json as _json
        from datetime import datetime, timezone

        client = get_supabase_client()
        resp = (
            client.table("forecast_model_runs")
            .insert({
                "run_type": run_type,
                "target_variable": target_variable,
                "hyperparameters": _json.dumps(hyperparameters or {}),
                "metrics": _json.dumps(metrics),
                "started_at": datetime.now(timezone.utc).isoformat(),
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "status": status,
            })
            .execute()
        )
        if resp.data:
            return resp.data[0].get("id")
    except Exception as exc:
        logger.warning("Failed to log model run: %s", exc)
    return None
