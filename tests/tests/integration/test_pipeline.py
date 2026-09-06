"""
End-to-end pipeline tests for LUMI.

Simulates the complete data flow:
    DOE Dataset → Preprocessing → ML Model → Prediction → FastAPI → React Data

Coverage:
- DOE CSV loading and cleaning
- Feature engineering
- Model artifact loading
- Forecast generation
- API response formatting
- Output consistency checks
- Failure handling at each stage

Requirements:
    pip install pytest pandas numpy scikit-learn

Run:
    pytest tests/integration/test_pipeline.py -v
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]
DOE_DIR = REPO_ROOT / "data" / "DOE_Data_Extracted"
FASTAPI_SERVICES = REPO_ROOT / "fastapi-backend" / "app" / "services"

import sys

if str(FASTAPI_SERVICES) not in sys.path:
    sys.path.insert(0, str(FASTAPI_SERVICES))


# ---------------------------------------------------------------------------
# Pipeline stage functions (replicate the DOE notebook logic)
# ---------------------------------------------------------------------------

def load_doe_energy_data(csv_path: Path | None = None) -> pd.DataFrame:
    """Load DOE energy data from CSV or create synthetic fixture data."""
    if csv_path and csv_path.exists():
        return pd.read_csv(csv_path)
    # Synthetic fixture data matching DOE structure
    years = list(range(2003, 2025))
    consumption = [45000 + i * 1500 + np.random.normal(0, 500) for i in range(len(years))]
    return pd.DataFrame({
        "year": years,
        "consumption_gwh": consumption,
        "peak_demand_mw": [c * 0.22 + np.random.normal(0, 200) for c in consumption],
        "generation_gwh": [c * 1.05 + np.random.normal(0, 300) for c in consumption],
    })


def preprocess_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate the raw DOE data."""
    df = df.copy()
    # Remove rows with missing consumption
    df = df.dropna(subset=["consumption_gwh"])
    # Forward fill remaining missing values
    df = df.ffill().bfill()
    # Ensure monotonic year
    df = df.sort_values("year").reset_index(drop=True)
    # Validate data types
    df["year"] = df["year"].astype(int)
    df["consumption_gwh"] = df["consumption_gwh"].astype(float)
    return df


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Create lag and trend features for ML models."""
    df = df.copy()
    df["trend"] = np.arange(len(df))
    df["lag_1"] = df["consumption_gwh"].shift(1)
    df["lag_2"] = df["consumption_gwh"].shift(2)
    df["rolling_mean_3"] = df["consumption_gwh"].rolling(window=3, min_periods=1).mean()
    df["yoy_growth"] = df["consumption_gwh"].pct_change(periods=1) * 100
    df = df.dropna().reset_index(drop=True)
    return df


def train_linear_trend_model(df: pd.DataFrame) -> dict[str, Any]:
    """Train a simple linear regression on trend."""
    from sklearn.linear_model import LinearRegression
    X = df[["trend"]].values
    y = df["consumption_gwh"].values
    model = LinearRegression()
    model.fit(X, y)
    return {"model": model, "coef": model.coef_[0], "intercept": model.intercept_}


def generate_forecast(model_dict: dict, start_year: int, n_years: int) -> pd.DataFrame:
    """Generate forecast for n_years starting from start_year."""
    model = model_dict["model"]
    train_len = model_dict.get("train_len", 22)
    trend_values = np.arange(train_len, train_len + n_years).reshape(-1, 1)
    predictions = model.predict(trend_values)
    forecast_years = list(range(start_year, start_year + n_years))
    return pd.DataFrame({
        "year": forecast_years,
        "forecast_consumption_gwh": predictions,
        "ci_lower": predictions * 0.95,
        "ci_upper": predictions * 1.05,
    })


def format_api_response(forecast_df: pd.DataFrame) -> dict[str, Any]:
    """Format the forecast DataFrame into the FastAPI response structure."""
    return {
        "metric": "consumption",
        "forecast": [
            {
                "year": int(row["year"]),
                "value": round(row["forecast_consumption_gwh"], 2),
                "ci_lower": round(row["ci_lower"], 2),
                "ci_upper": round(row["ci_upper"], 2),
            }
            for _, row in forecast_df.iterrows()
        ],
        "model": "Linear Trend Regression",
        "source": "DOE Energy Statistics",
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def raw_doe_data() -> pd.DataFrame:
    return load_doe_energy_data()


@pytest.fixture
def preprocessed_data(raw_doe_data) -> pd.DataFrame:
    return preprocess_pipeline(raw_doe_data)


@pytest.fixture
def featured_data(preprocessed_data) -> pd.DataFrame:
    return feature_engineering(preprocessed_data)


@pytest.fixture
def trained_model(featured_data) -> dict[str, Any]:
    model_dict = train_linear_trend_model(featured_data)
    model_dict["train_len"] = len(featured_data)
    return model_dict


@pytest.fixture
def forecast_2025_2030(trained_model) -> pd.DataFrame:
    return generate_forecast(trained_model, start_year=2025, n_years=6)


# ---------------------------------------------------------------------------
# PIPELINE STAGE TESTS
# ---------------------------------------------------------------------------

class TestDataLoading:
    """Stage 1: DOE dataset loading."""

    def test_load_returns_dataframe(self, raw_doe_data):
        assert isinstance(raw_doe_data, pd.DataFrame)
        assert len(raw_doe_data) > 0

    def test_load_has_required_columns(self, raw_doe_data):
        required = {"year", "consumption_gwh"}
        assert required.issubset(raw_doe_data.columns)

    def test_load_year_range(self, raw_doe_data):
        assert raw_doe_data["year"].min() >= 2003
        assert raw_doe_data["year"].max() <= 2024


class TestPreprocessing:
    """Stage 2: Data cleaning and validation."""

    def test_no_missing_consumption(self, preprocessed_data):
        assert preprocessed_data["consumption_gwh"].isna().sum() == 0

    def test_years_are_sorted(self, preprocessed_data):
        years = preprocessed_data["year"].tolist()
        assert years == sorted(years)

    def test_no_duplicate_years(self, preprocessed_data):
        assert preprocessed_data["year"].duplicated().sum() == 0

    def test_consumption_positive(self, preprocessed_data):
        assert (preprocessed_data["consumption_gwh"] > 0).all()


class TestFeatureEngineering:
    """Stage 3: Feature creation."""

    def test_trend_feature_created(self, featured_data):
        assert "trend" in featured_data.columns
        assert featured_data["trend"].is_monotonic_increasing

    def test_lag_features_created(self, featured_data):
        assert "lag_1" in featured_data.columns
        assert "lag_2" in featured_data.columns

    def test_rolling_mean_created(self, featured_data):
        assert "rolling_mean_3" in featured_data.columns
        assert featured_data["rolling_mean_3"].notna().all()

    def test_yoy_growth_created(self, featured_data):
        assert "yoy_growth" in featured_data.columns

    def test_featured_data_no_nan(self, featured_data):
        assert featured_data.isna().sum().sum() == 0


class TestModelTraining:
    """Stage 4: Model training."""

    def test_model_exists(self, trained_model):
        assert "model" in trained_model
        assert "coef" in trained_model

    def test_coefficient_positive(self, trained_model):
        """Consumption should increase over time (positive trend)."""
        assert trained_model["coef"] > 0

    def test_model_can_predict(self, trained_model, featured_data):
        X = featured_data[["trend"]].values
        preds = trained_model["model"].predict(X)
        assert len(preds) == len(featured_data)
        assert not np.isnan(preds).any()


class TestForecastGeneration:
    """Stage 5: Forecast generation."""

    def test_forecast_has_6_years(self, forecast_2025_2030):
        assert len(forecast_2025_2030) == 6

    def test_forecast_years_correct(self, forecast_2025_2030):
        expected_years = list(range(2025, 2031))
        assert forecast_2025_2030["year"].tolist() == expected_years

    def test_forecast_values_positive(self, forecast_2025_2030):
        assert (forecast_2025_2030["forecast_consumption_gwh"] > 0).all()

    def test_confidence_intervals_ordered(self, forecast_2025_2030):
        for _, row in forecast_2025_2030.iterrows():
            assert row["ci_lower"] <= row["forecast_consumption_gwh"] <= row["ci_upper"]

    def test_forecast_monotonic_increasing(self, forecast_2025_2030):
        """With a positive trend, forecasts should generally increase."""
        values = forecast_2025_2030["forecast_consumption_gwh"].tolist()
        assert values[-1] > values[0]


class TestApiFormatting:
    """Stage 6: FastAPI response formatting."""

    def test_response_is_dict(self, forecast_2025_2030):
        response = format_api_response(forecast_2025_2030)
        assert isinstance(response, dict)

    def test_response_has_forecast_array(self, forecast_2025_2030):
        response = format_api_response(forecast_2025_2030)
        assert "forecast" in response
        assert isinstance(response["forecast"], list)
        assert len(response["forecast"]) == 6

    def test_each_forecast_item_has_required_fields(self, forecast_2025_2030):
        response = format_api_response(forecast_2025_2030)
        required = {"year", "value", "ci_lower", "ci_upper"}
        for item in response["forecast"]:
            assert required.issubset(item.keys())

    def test_response_model_field(self, forecast_2025_2030):
        response = format_api_response(forecast_2025_2030)
        assert response["model"] == "Linear Trend Regression"


class TestCompletePipeline:
    """Full pipeline execution from raw data to API response."""

    def test_end_to_end_no_exceptions(self, raw_doe_data):
        """The entire pipeline should execute without exceptions."""
        df = preprocess_pipeline(raw_doe_data)
        df = feature_engineering(df)
        model = train_linear_trend_model(df)
        model["train_len"] = len(df)
        forecast = generate_forecast(model, start_year=2025, n_years=6)
        response = format_api_response(forecast)
        assert response is not None
        assert len(response["forecast"]) == 6

    def test_output_consistency(self, raw_doe_data):
        """Running the pipeline twice should produce identical results (deterministic)."""
        # Set random seed for reproducibility
        np.random.seed(42)
        df1 = load_doe_energy_data()
        df1 = preprocess_pipeline(df1)
        df1 = feature_engineering(df1)
        model1 = train_linear_trend_model(df1)
        model1["train_len"] = len(df1)
        forecast1 = generate_forecast(model1, 2025, 6)

        np.random.seed(42)
        df2 = load_doe_energy_data()
        df2 = preprocess_pipeline(df2)
        df2 = feature_engineering(df2)
        model2 = train_linear_trend_model(df2)
        model2["train_len"] = len(df2)
        forecast2 = generate_forecast(model2, 2025, 6)

        pd.testing.assert_frame_equal(forecast1, forecast2)


class TestFailureHandling:
    """Tests for graceful failure at each pipeline stage."""

    def test_empty_dataframe_handling(self):
        """An empty DataFrame should return an empty result after preprocessing."""
        empty_df = pd.DataFrame(columns=["year", "consumption_gwh"])
        result = feature_engineering(empty_df)
        assert len(result) == 0

    def test_missing_consumption_column(self):
        """DataFrame without 'consumption_gwh' should fail gracefully."""
        bad_df = pd.DataFrame({"year": [2020, 2021]})
        with pytest.raises(Exception):
            preprocess_pipeline(bad_df)

    def test_single_row_cannot_create_lag(self):
        """A single-row DataFrame loses all rows after lag dropna."""
        df = pd.DataFrame({
            "year": [2020],
            "consumption_gwh": [50000.0],
        })
        df = preprocess_pipeline(df)
        result = feature_engineering(df)
        assert len(result) == 0  # lag_1 NaN -> dropna removes the only row

    def test_corrupted_csv_file(self, tmp_path):
        """A corrupted CSV should raise during preprocessing when astype(float) fails."""
        bad_csv = tmp_path / "bad.csv"
        bad_csv.write_text("year,consumption_gwh\n2020,abc\n2021,50000")
        df = pd.read_csv(bad_csv)
        # "abc" is read as string, not NaN
        assert not df["consumption_gwh"].isna().any()
        # astype(float) on "abc" should raise ValueError
        with pytest.raises((ValueError, TypeError)):
            preprocess_pipeline(df)
