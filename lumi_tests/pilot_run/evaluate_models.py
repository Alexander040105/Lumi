"""
Pilot Run: Model Validation Script for LUMI Energy Demand Forecasting.

This script evaluates multiple forecasting models on the DOE Philippine
national energy demand dataset using a held-out test set.

Models Evaluated:
- ARIMA/SARIMA (statsmodels)
- Linear Trend Regression (scikit-learn)
- Holt-Winters Exponential Smoothing (statsmodels)
- SARIMAX (statsmodels)
- Random Forest Regressor (scikit-learn) — controlled experiment

Metrics Calculated:
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- MAPE (Mean Absolute Percentage Error)
- R² Score

Usage:
    python evaluate_models.py

Prerequisites:
    pip install pandas numpy matplotlib scikit-learn statsmodels

Outputs (written to pilot_results/):
    - forecast_comparison.csv
    - model_metrics.csv
    - forecast_plot.png
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
DOE_DIR = REPO_ROOT / "DOE_Data_Extracted"
OUTPUT_DIR = Path(__file__).parent / "pilot_results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TRAIN_END_YEAR = 2023  # Training data ends here
TEST_YEAR = 2024       # Held-out test year
FORECAST_HORIZON = 6   # 2025–2030


def load_or_generate_data() -> pd.DataFrame:
    """Load DOE energy data from CSV or generate synthetic fixture data."""
    csv_candidates = [
        DOE_DIR / "national_energy_2003_2024.csv",
        DOE_DIR / "DOE_energy_data.csv",
    ]
    for csv_path in csv_candidates:
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            if "year" in df.columns and "consumption_gwh" in df.columns:
                return df

    # Synthetic fixture matching DOE structure (22 years: 2003–2024)
    print("[WARN] DOE CSV not found. Using synthetic fixture data.")
    years = list(range(2003, 2025))
    np.random.seed(42)
    base = 45000
    trend = np.array([base + i * 1500 for i in range(len(years))])
    noise = np.random.normal(0, 400, len(years))
    consumption = trend + noise
    return pd.DataFrame({
        "year": years,
        "consumption_gwh": consumption,
    })


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and sort the time series."""
    df = df.copy()
    df = df.sort_values("year").reset_index(drop=True)
    df = df.dropna(subset=["consumption_gwh"])
    df["consumption_gwh"] = df["consumption_gwh"].astype(float)
    return df


def split_train_test(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split into train (≤2023) and test (2024)."""
    train = df[df["year"] <= TRAIN_END_YEAR].copy()
    test = df[df["year"] == TEST_YEAR].copy()
    return train, test


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Percentage Error (safe for zero values)."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    mask = y_true != 0
    if not mask.any():
        return np.nan
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def calculate_all_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Compute MAE, RMSE, MAPE, and R²."""
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(mean_squared_error(y_true, y_pred, squared=False)),
        "mape": calculate_mape(y_true, y_pred),
        "r2": float(r2_score(y_true, y_pred)),
    }


# ---------------------------------------------------------------------------
# Model wrappers
# ---------------------------------------------------------------------------

def fit_linear_trend(train: pd.DataFrame) -> dict[str, Any]:
    """Fit a simple linear regression on year (trend)."""
    X = train[["year"]].values
    y = train["consumption_gwh"].values
    model = LinearRegression()
    model.fit(X, y)
    return {"model": model, "name": "Linear Trend Regression"}


def fit_arima(train: pd.DataFrame) -> dict[str, Any]:
    """Fit ARIMA(1,1,1) on the consumption series."""
    series = train["consumption_gwh"].values
    try:
        model = ARIMA(series, order=(1, 1, 1))
        fitted = model.fit()
        return {"model": fitted, "name": "ARIMA(1,1,1)"}
    except Exception as exc:
        print(f"[WARN] ARIMA fit failed: {exc}")
        return {"model": None, "name": "ARIMA(1,1,1) — FAILED"}


def fit_holt(train: pd.DataFrame) -> dict[str, Any]:
    """Fit Holt-Winters exponential smoothing."""
    series = train["consumption_gwh"].values
    try:
        model = ExponentialSmoothing(series, trend="add", damped_trend=False)
        fitted = model.fit()
        return {"model": fitted, "name": "Holt Smoothing"}
    except Exception as exc:
        print(f"[WARN] Holt fit failed: {exc}")
        return {"model": None, "name": "Holt Smoothing — FAILED"}


def fit_random_forest(train: pd.DataFrame) -> dict[str, Any]:
    """Fit Random Forest as a controlled experiment (demonstrates overfitting)."""
    # Use lag features to give RF something to learn from
    df = train.copy()
    df["trend"] = np.arange(len(df))
    df["lag_1"] = df["consumption_gwh"].shift(1)
    df = df.dropna()
    if len(df) < 5:
        return {"model": None, "name": "Random Forest — INSUFFICIENT DATA"}
    X = df[["trend", "lag_1"]].values
    y = df["consumption_gwh"].values
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return {"model": model, "name": "Random Forest"}


# ---------------------------------------------------------------------------
# Prediction wrappers
# ---------------------------------------------------------------------------

def predict_linear(model_dict: dict, years: np.ndarray) -> np.ndarray:
    m = model_dict["model"]
    return m.predict(years.reshape(-1, 1))


def predict_arima(model_dict: dict, steps: int) -> np.ndarray:
    m = model_dict["model"]
    if m is None:
        return np.full(steps, np.nan)
    fc = m.forecast(steps)
    return np.asarray(fc)


def predict_holt(model_dict: dict, steps: int) -> np.ndarray:
    m = model_dict["model"]
    if m is None:
        return np.full(steps, np.nan)
    fc = m.forecast(steps)
    return np.asarray(fc)


def predict_rf(model_dict: dict, last_train: pd.DataFrame, years: np.ndarray) -> np.ndarray:
    m = model_dict["model"]
    if m is None:
        return np.full(len(years), np.nan)
    n_train = len(last_train)
    preds = []
    last_val = last_train["consumption_gwh"].iloc[-1]
    for i, year in enumerate(years):
        trend = n_train + i
        X = np.array([[trend, last_val]])
        pred = m.predict(X)[0]
        preds.append(pred)
        last_val = pred
    return np.array(preds)


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

def plot_forecasts(
    train: pd.DataFrame,
    test: pd.DataFrame,
    forecasts: dict[str, np.ndarray],
    forecast_years: np.ndarray,
    output_path: Path,
) -> None:
    """Generate a forecast comparison plot."""
    plt.figure(figsize=(12, 6))
    plt.plot(train["year"], train["consumption_gwh"], "o-", label="Training (2003–2023)", color="black")
    if not test.empty:
        plt.plot(test["year"], test["consumption_gwh"], "s--", label=f"Actual ({TEST_YEAR})", color="green")

    colors = ["blue", "red", "orange", "purple"]
    for (name, preds), color in zip(forecasts.items(), colors):
        plt.plot(forecast_years, preds, "o-", label=f"Forecast: {name}", color=color, alpha=0.8)

    plt.xlabel("Year")
    plt.ylabel("Consumption (GWh)")
    plt.title("LUMI Energy Demand Forecast Comparison (Pilot Run)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"[INFO] Forecast plot saved to: {output_path}")


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("LUMI Pilot Run: Energy Demand Forecast Model Validation")
    print("=" * 60)

    # Load data
    df = load_or_generate_data()
    df = preprocess(df)
    train, test = split_train_test(df)

    print(f"[INFO] Training samples: {len(train)} ({train['year'].min()}–{train['year'].max()})")
    print(f"[INFO] Test samples: {len(test)} ({TEST_YEAR})")

    # Fit models
    models = [
        fit_linear_trend(train),
        fit_arima(train),
        fit_holt(train),
        fit_random_forest(train),
    ]

    # Forecast years: 2025–2030
    forecast_years = np.arange(TRAIN_END_YEAR + 1, TRAIN_END_YEAR + 1 + FORECAST_HORIZON)

    # Generate forecasts
    forecasts: dict[str, np.ndarray] = {}
    for m in models:
        name = m["name"]
        if "Linear Trend" in name:
            forecasts[name] = predict_linear(m, forecast_years)
        elif "ARIMA" in name:
            forecasts[name] = predict_arima(m, FORECAST_HORIZON)
        elif "Holt" in name:
            forecasts[name] = predict_holt(m, FORECAST_HORIZON)
        elif "Random Forest" in name:
            forecasts[name] = predict_rf(m, train, forecast_years)
        else:
            forecasts[name] = np.full(FORECAST_HORIZON, np.nan)

    # Evaluate on test set (2024)
    metrics_records = []
    if not test.empty:
        y_true = test["consumption_gwh"].values
        for m in models:
            name = m["name"]
            if "Linear Trend" in name:
                y_pred = predict_linear(m, test["year"].values)
            elif "ARIMA" in name and m["model"] is not None:
                y_pred = predict_arima(m, len(test))
            elif "Holt" in name and m["model"] is not None:
                y_pred = predict_holt(m, len(test))
            elif "Random Forest" in name and m["model"] is not None:
                y_pred = predict_rf(m, train, test["year"].values)
            else:
                y_pred = np.full(len(test), np.nan)

            if not np.isnan(y_pred).all():
                metrics = calculate_all_metrics(y_true, y_pred)
                metrics["model"] = name
                metrics_records.append(metrics)
                print(f"\n{name}:")
                print(f"  MAE:  {metrics['mae']:.2f} GWh")
                print(f"  RMSE: {metrics['rmse']:.2f} GWh")
                print(f"  MAPE: {metrics['mape']:.2f}%")
                print(f"  R²:   {metrics['r2']:.4f}")
            else:
                print(f"\n{name}: SKIPPED (fit failed)")

    # Save metrics
    if metrics_records:
        metrics_df = pd.DataFrame(metrics_records)
        metrics_path = OUTPUT_DIR / "model_metrics.csv"
        metrics_df.to_csv(metrics_path, index=False)
        print(f"\n[INFO] Model metrics saved to: {metrics_path}")

    # Save forecast comparison
    forecast_df = pd.DataFrame({"year": forecast_years})
    for name, preds in forecasts.items():
        forecast_df[name] = preds
    forecast_path = OUTPUT_DIR / "forecast_comparison.csv"
    forecast_df.to_csv(forecast_path, index=False)
    print(f"[INFO] Forecast comparison saved to: {forecast_path}")

    # Generate plot
    plot_path = OUTPUT_DIR / "forecast_plot.png"
    plot_forecasts(train, test, forecasts, forecast_years, plot_path)

    # Summary
    print("\n" + "=" * 60)
    print("Pilot Run Complete")
    print("=" * 60)
    print(f"Outputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
