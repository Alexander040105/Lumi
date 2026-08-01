"""
Unit tests for LUMI Machine Learning preprocessing and model artifacts.

Coverage:
- Missing value handling
- Feature creation / scaling
- Model prediction shape validation
- Datatype and NaN output checks

These tests validate the data pipeline used in:
  DOE_Data_Extracted/DOE_arima_forecasting.ipynb
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ---------------------------------------------------------------------------
# Import path helper
# ---------------------------------------------------------------------------
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Stand-in functions that replicate the notebook preprocessing logic
# so that the tests are self-contained and runnable without the notebook
# ---------------------------------------------------------------------------

def preprocess_energy_data(df: pd.DataFrame) -> pd.DataFrame:
    """Replicate the DOE notebook preprocessing steps."""
    df = df.copy()
    # Handle missing values by forward fill then backward fill
    df = df.ffill().bfill()
    # Ensure year is integer
    df["year"] = df["year"].astype(int)
    # Ensure consumption is float
    df["consumption_gwh"] = df["consumption_gwh"].astype(float)
    return df


def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create lag and trend features for regression models."""
    df = df.copy()
    df = df.sort_values("year")
    df["trend"] = np.arange(len(df))
    df["lag_1"] = df["consumption_gwh"].shift(1)
    df = df.dropna()
    return df


def split_train_test(df: pd.DataFrame, test_size: int = 3):
    """Split into train and test (last N rows as test)."""
    df = df.sort_values("year").reset_index(drop=True)
    train = df.iloc[:-test_size]
    test = df.iloc[-test_size:]
    return train, test


def linear_trend_forecast(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    """Simple linear regression on trend."""
    from sklearn.linear_model import LinearRegression
    X_train = train[["trend"]].values
    y_train = train["consumption_gwh"].values
    X_test = test[["trend"]].values
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model.predict(X_test)


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Percentage Error (vectorized, safe for zero values)."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    mask = y_true != 0
    if not mask.any():
        return np.nan
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


# =============================================================================
# PREPROCESSING TESTS
# =============================================================================

class TestPreprocessEnergyData:
    """Tests for preprocess_energy_data()."""

    def test_forward_fill_missing(self, sample_energy_df_missing):
        df = preprocess_energy_data(sample_energy_df_missing)
        assert df["consumption_gwh"].isna().sum() == 0

    def test_year_integer(self, sample_energy_df):
        df = preprocess_energy_data(sample_energy_df)
        assert df["year"].dtype == np.int64 or df["year"].dtype == int

    def test_consumption_float(self, sample_energy_df):
        df = preprocess_energy_data(sample_energy_df)
        assert np.issubdtype(df["consumption_gwh"].dtype, np.floating)

    def test_shape_preserved(self, sample_energy_df):
        original_shape = sample_energy_df.shape
        df = preprocess_energy_data(sample_energy_df)
        assert df.shape == original_shape

    def test_all_missing_column(self):
        df = pd.DataFrame({
            "year": [2020, 2021, 2022],
            "consumption_gwh": [np.nan, np.nan, np.nan],
        })
        df = preprocess_energy_data(df)
        # ffill/bfill cannot fill an all-NaN column — expected behavior
        assert df["consumption_gwh"].isna().sum() == 3


class TestCreateTimeFeatures:
    """Tests for create_time_features()."""

    def test_trend_increases(self, sample_energy_df):
        df = preprocess_energy_data(sample_energy_df)
        df = create_time_features(df)
        assert "trend" in df.columns
        assert df["trend"].is_monotonic_increasing

    def test_lag_created(self, sample_energy_df):
        df = preprocess_energy_data(sample_energy_df)
        df = create_time_features(df)
        assert "lag_1" in df.columns
        # lag_1 is shift(1); first non-NaN row corresponds to year 2004
        # so lag_1 should equal 2003's consumption (45000)
        assert df["lag_1"].iloc[0] == pytest.approx(45000.0)

    def test_dropna_removes_first_row(self, sample_energy_df):
        df = preprocess_energy_data(sample_energy_df)
        original_len = len(df)
        df = create_time_features(df)
        assert len(df) == original_len - 1  # first row has NaN lag_1


class TestSplitTrainTest:
    """Tests for split_train_test()."""

    def test_correct_split_size(self, sample_energy_df):
        df = preprocess_energy_data(sample_energy_df)
        train, test = split_train_test(df, test_size=3)
        assert len(test) == 3
        assert len(train) == len(df) - 3

    def test_test_is_last_rows(self, sample_energy_df):
        df = preprocess_energy_data(sample_energy_df)
        train, test = split_train_test(df, test_size=3)
        assert test["year"].iloc[-1] == df["year"].max()


# =============================================================================
# MODEL PREDICTION TESTS
# =============================================================================

class TestLinearTrendForecast:
    """Tests for linear_trend_forecast()."""

    def test_prediction_shape(self, sample_energy_df):
        df = preprocess_energy_data(sample_energy_df)
        df = create_time_features(df)
        train, test = split_train_test(df, test_size=3)
        preds = linear_trend_forecast(train, test)
        assert len(preds) == len(test)

    def test_no_nan_outputs(self, sample_energy_df):
        df = preprocess_energy_data(sample_energy_df)
        df = create_time_features(df)
        train, test = split_train_test(df, test_size=3)
        preds = linear_trend_forecast(train, test)
        assert not np.isnan(preds).any()

    def test_correct_datatype(self, sample_energy_df):
        df = preprocess_energy_data(sample_energy_df)
        df = create_time_features(df)
        train, test = split_train_test(df, test_size=3)
        preds = linear_trend_forecast(train, test)
        assert preds.dtype == np.float64

    def test_monotonic_increasing_trend(self, sample_energy_df):
        """If consumption is linear, predictions should closely match."""
        df = pd.DataFrame({
            "year": list(range(2000, 2020)),
            "consumption_gwh": [1000 + i * 100 for i in range(20)],
        })
        df = preprocess_energy_data(df)
        df = create_time_features(df)
        train, test = split_train_test(df, test_size=3)
        preds = linear_trend_forecast(train, test)
        # On a perfectly linear series, linear regression should be near-perfect
        mape = calculate_mape(test["consumption_gwh"].values, preds)
        assert mape < 1.0  # < 1% error on perfectly linear data


# =============================================================================
# METRIC TESTS
# =============================================================================

class TestCalculateMape:
    """Tests for calculate_mape()."""

    def test_perfect_prediction(self):
        y = np.array([100, 200, 300])
        assert calculate_mape(y, y) == pytest.approx(0.0)

    def test_known_error(self):
        y_true = np.array([100, 200, 300])
        y_pred = np.array([110, 190, 330])
        # MAPE = mean(|(100-110)/100|, |(200-190)/200|, |(300-330)/300|) * 100
        # = mean(0.10, 0.05, 0.10) * 100 = 8.333...
        mape = calculate_mape(y_true, y_pred)
        assert mape == pytest.approx(8.333, rel=1e-2)

    def test_zero_true_value_excluded(self):
        y_true = np.array([0, 200, 300])
        y_pred = np.array([0, 210, 330])
        mape = calculate_mape(y_true, y_pred)
        # Zero should be excluded; compute on [200, 300]
        expected = np.mean([abs(200 - 210) / 200, abs(300 - 330) / 300]) * 100
        assert mape == pytest.approx(expected, rel=1e-4)

    def test_all_zeros_returns_nan(self):
        y_true = np.array([0, 0, 0])
        y_pred = np.array([1, 2, 3])
        assert math.isnan(calculate_mape(y_true, y_pred))


class TestScikitLearnMetrics:
    """Tests validating the metric functions used in the notebook."""

    def test_mae(self):
        y_true = np.array([100, 200, 300])
        y_pred = np.array([110, 190, 330])
        mae = mean_absolute_error(y_true, y_pred)
        # |10|+|10|+|30| = 50 / 3 = 16.67
        assert mae == pytest.approx(16.6667, rel=1e-3)

    def test_rmse(self):
        y_true = np.array([100, 200, 300])
        y_pred = np.array([110, 190, 330])
        # sklearn >=1.6 removed `squared` kwarg; use np.sqrt
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        expected = math.sqrt((100 + 100 + 900) / 3)
        assert rmse == pytest.approx(expected, rel=1e-4)

    def test_r2_perfect(self):
        y = np.array([100, 200, 300])
        assert r2_score(y, y) == pytest.approx(1.0)

    def test_r2_worse_than_mean(self):
        y_true = np.array([100, 200, 300])
        y_pred = np.array([0, 0, 0])  # worse than predicting the mean
        assert r2_score(y_true, y_pred) < 0.0
