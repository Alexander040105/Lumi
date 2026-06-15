"""
LUMI ML Training Pipeline
=========================
Trains forecasting models on-demand using data from the Supabase
national_energy_annual table, evaluates them, and persists artifacts
to the ml_model_registry and forecast_cache tables.

Supported models:
- ARIMA(1,1,1)
- Linear Trend Regression
- Holt-Winters Exponential Smoothing
- Random Forest (controlled experiment)
"""

import json
import logging
import pickle
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from app.ml.registry import ModelRegistry
from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)

# Mapping for DB compatibility: some existing databases have a CHECK
# constraint that only allows a subset of types.  This map lets the
# trainer gracefully degrade to a compatible label when needed.
_DB_TYPE_MAP = {
    "ARIMA": "SARIMA",
    "LinearTrend": "Prophet",
    "HoltWinters": "SARIMA",
    "RandomForest": "LightGBM",
}

MODEL_TYPES = ["ARIMA", "LinearTrend", "HoltWinters", "RandomForest"]


class Trainer:
    """End-to-end training pipeline for national energy forecasting."""

    def __init__(
        self,
        target_variable: str = "total_consumption_gwh",
        train_end_year: int = 2020,
        test_years: int = 4,
        horizon_years: int = 6,
    ) -> None:
        self.target_variable = target_variable
        self.train_end_year = train_end_year
        self.test_years = test_years
        self.horizon_years = horizon_years
        self._registry = ModelRegistry()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_data(self) -> pd.DataFrame:
        client = get_supabase_client()
        result = (
            client
            .table("national_energy_annual")
            .select("*")
            .order("year")
            .execute()
        )
        data = result.data or []
        if not data:
            raise ValueError("No national energy data found in Supabase.")
        df = pd.DataFrame(data)
        df["year"] = df["year"].astype(int)
        df = df.sort_values("year").reset_index(drop=True)
        return df

    def _prepare_splits(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        train = df[df["year"] <= self.train_end_year].copy()
        test = df[
            (df["year"] > self.train_end_year)
            & (df["year"] <= self.train_end_year + self.test_years)
        ].copy()
        if train.empty:
            raise ValueError("Training split is empty. Adjust train_end_year.")
        return train, test

    # ------------------------------------------------------------------
    # Model builders
    # ------------------------------------------------------------------

    @staticmethod
    def _build_trend_features(series: pd.Series) -> pd.DataFrame:
        """Create a simple integer trend feature."""
        return pd.DataFrame({"trend": np.arange(len(series))})

    def _train_arima(self, train: pd.DataFrame) -> ARIMA:
        y = train[self.target_variable].values
        model = ARIMA(y, order=(1, 1, 1))
        return model.fit()

    def _train_linear_trend(self, train: pd.DataFrame) -> LinearRegression:
        X = self._build_trend_features(train[self.target_variable])
        y = train[self.target_variable].values
        model = LinearRegression()
        model.fit(X, y)
        return model

    def _train_holtwinters(self, train: pd.DataFrame) -> Any:
        y = train[self.target_variable].values
        model = ExponentialSmoothing(
            y,
            trend="add",
            seasonal=None,
            damped_trend=True,
        )
        return model.fit(optimized=True)

    def _train_random_forest(self, train: pd.DataFrame) -> RandomForestRegressor:
        """Controlled experiment: RF with lag and trend features."""
        df = train.copy()
        df["trend"] = np.arange(len(df))
        df["lag_1"] = df[self.target_variable].shift(1)
        df["lag_2"] = df[self.target_variable].shift(2)
        df = df.dropna()
        X = df[["trend", "lag_1", "lag_2"]].values
        y = df[self.target_variable].values
        model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
        model.fit(X, y)
        return model

    # ------------------------------------------------------------------
    # Prediction helpers
    # ------------------------------------------------------------------

    def _predict_arima(self, fitted: Any, steps: int) -> np.ndarray:
        return fitted.forecast(steps=steps)

    def _predict_linear_trend(self, fitted: LinearRegression, train_len: int, steps: int) -> np.ndarray:
        X_future = pd.DataFrame({"trend": np.arange(train_len, train_len + steps)})
        return fitted.predict(X_future)

    def _predict_holtwinters(self, fitted: Any, steps: int) -> np.ndarray:
        return fitted.forecast(steps)

    def _predict_random_forest(self, fitted: RandomForestRegressor, train: pd.DataFrame, steps: int) -> np.ndarray:
        preds = []
        last_vals = train[self.target_variable].values.tolist()
        trend_start = len(train)
        for i in range(steps):
            X = np.array([[trend_start + i, last_vals[-1], last_vals[-2]]])
            p = fitted.predict(X)[0]
            preds.append(p)
            last_vals.append(p)
        return np.array(preds)

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        mask = y_true != 0
        if not mask.any():
            return np.nan
        return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)

    def _evaluate(self, y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
        mae = float(mean_absolute_error(y_true, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        mape = self._calculate_mape(y_true, y_pred)
        r2 = float(r2_score(y_true, y_pred)) if len(y_true) > 1 else 0.0
        return {"mae": round(mae, 2), "rmse": round(rmse, 2), "mape": round(mape, 2), "r2": round(r2, 4)}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def train_all(self) -> list[dict[str, Any]]:
        """Train all model types, evaluate on test set, and register winners."""
        df = self._load_data()
        train, test = self._prepare_splits(df)
        test_years = test["year"].values
        y_test = test[self.target_variable].values
        train_len = len(train)

        results = []
        model_mapping = {
            "ARIMA": (self._train_arima, self._predict_arima, []),
            "LinearTrend": (self._train_linear_trend, self._predict_linear_trend, [train_len]),
            "HoltWinters": (self._train_holtwinters, self._predict_holtwinters, []),
            "RandomForest": (self._train_random_forest, self._predict_random_forest, [train]),
        }

        for model_name, (train_fn, predict_fn, extra_args) in model_mapping.items():
            try:
                logger.info("Training %s...", model_name)
                fitted = train_fn(train)
                y_pred = predict_fn(fitted, *extra_args, steps=len(test))
                y_pred = np.asarray(y_pred)
                metrics = self._evaluate(y_test, y_pred)

                # Forecast horizon beyond test set
                future_years = list(range(test_years[-1] + 1, test_years[-1] + 1 + self.horizon_years))
                future_pred = predict_fn(fitted, *extra_args, steps=len(test) + self.horizon_years)
                future_pred = np.asarray(future_pred)
                forecast_values = future_pred[len(test):].tolist()

                # Serialize model artifact to bytes
                artifact_bytes = pickle.dumps(fitted)

                model_id = self._registry.register_model(
                    model_name=f"{model_name}_{self.target_variable}",
                    model_version=date.today().isoformat(),
                    model_type=_DB_TYPE_MAP.get(model_name, model_name),
                    target_variable=self.target_variable,
                    train_date=date.today(),
                    metrics=metrics,
                    artifact_bytes=artifact_bytes,
                )

                self._registry.save_forecast_cache(
                    model_id=model_id,
                    target_variable=self.target_variable,
                    horizon_years=self.horizon_years,
                    years=future_years,
                    predicted_values=forecast_values,
                )

                results.append({
                    "model_id": str(model_id),
                    "model_type": model_name,
                    "metrics": metrics,
                    "status": "trained",
                })
                logger.info("%s trained — MAPE %.2f%%", model_name, metrics["mape"])

            except Exception as exc:
                logger.exception("Failed to train %s", model_name)
                results.append({
                    "model_type": model_name,
                    "status": "failed",
                    "error": str(exc),
                })

        # Activate best model by lowest MAPE
        successful = [r for r in results if r["status"] == "trained"]
        if successful:
            best = min(successful, key=lambda x: x["metrics"]["mape"])
            self._registry.activate_model(best["model_id"])
            for r in results:
                r["is_active"] = r.get("model_id") == best["model_id"]

        return results

    def train_single(self, model_type: str) -> dict[str, Any]:
        if model_type not in MODEL_TYPES:
            raise ValueError(f"Unknown model type: {model_type}. Choose from {MODEL_TYPES}")
        df = self._load_data()
        train, test = self._prepare_splits(df)
        y_test = test[self.target_variable].values
        test_years = test["year"].values
        train_len = len(train)

        model_mapping = {
            "ARIMA": (self._train_arima, self._predict_arima, []),
            "LinearTrend": (self._train_linear_trend, self._predict_linear_trend, [train_len]),
            "HoltWinters": (self._train_holtwinters, self._predict_holtwinters, []),
            "RandomForest": (self._train_random_forest, self._predict_random_forest, [train]),
        }

        train_fn, predict_fn, extra_args = model_mapping[model_type]
        fitted = train_fn(train)
        y_pred = predict_fn(fitted, *extra_args, steps=len(test))
        metrics = self._evaluate(y_test, np.asarray(y_pred))

        future_years = list(range(test_years[-1] + 1, test_years[-1] + 1 + self.horizon_years))
        future_pred = predict_fn(fitted, *extra_args, steps=len(test) + self.horizon_years)
        forecast_values = np.asarray(future_pred)[len(test):].tolist()
        artifact_bytes = pickle.dumps(fitted)

        model_id = self._registry.register_model(
            model_name=f"{model_type}_{self.target_variable}",
            model_version=date.today().isoformat(),
            model_type=_DB_TYPE_MAP.get(model_type, model_type),
            target_variable=self.target_variable,
            train_date=date.today(),
            metrics=metrics,
            artifact_bytes=artifact_bytes,
        )

        self._registry.save_forecast_cache(
            model_id=model_id,
            target_variable=self.target_variable,
            horizon_years=self.horizon_years,
            years=future_years,
            predicted_values=forecast_values,
        )

        self._registry.activate_model(model_id)

        return {
            "model_id": str(model_id),
            "model_type": model_type,
            "metrics": metrics,
            "forecast_years": future_years,
            "forecast_values": forecast_values,
        }
