"""
Performance tests for LUMI backend and ML pipeline.

Measures:
1. Dataset loading time
2. Prediction / inference time
3. API response time
4. EnergyHub map data loading time
5. FAISS RAG retrieval time

Target thresholds:
- API response: < 2 seconds
- Prediction inference: < 5 seconds
- Dataset loading: < 3 seconds
- RAG retrieval: < 1 second
- Map data aggregation: < 2 seconds

Requirements:
    pip install pytest

Run:
    pytest tests/integration/performance_test.py -v --tb=short
    # Or with benchmark plugin:
    # pip install pytest-benchmark
    # pytest tests/integration/performance_test.py --benchmark-only

Note: Tests marked @pytest.mark.benchmark require a live backend.
Tests marked @pytest.mark.local can run offline.
"""

from __future__ import annotations

import os
import time
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
DOE_DIR = REPO_ROOT / "DOE_Data_Extracted"
FASTAPI_SERVICES = REPO_ROOT / "fastapi-backend" / "app" / "services"

import sys

if str(FASTAPI_SERVICES) not in sys.path:
    sys.path.insert(0, str(FASTAPI_SERVICES))


# ---------------------------------------------------------------------------
# Target thresholds (adjust based on deployment environment)
# ---------------------------------------------------------------------------
THRESHOLDS = {
    "api_response_ms": 2000,       # 2 seconds
    "prediction_ms": 5000,          # 5 seconds
    "dataset_load_ms": 3000,      # 3 seconds
    "rag_retrieval_ms": 1000,     # 1 second
    "map_aggregation_ms": 2000,   # 2 seconds
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_doe_csv(tmp_path) -> Path:
    """Create a temporary DOE-like CSV for timing tests."""
    csv_path = tmp_path / "doe_energy.csv"
    years = list(range(2003, 2025))
    rows = []
    for i, year in enumerate(years):
        rows.append({
            "year": year,
            "consumption_gwh": 45000 + i * 1500,
            "peak_demand_mw": 10000 + i * 300,
            "generation_gwh": 47000 + i * 1550,
            "coal_pct": 43.1,
            "renewable_pct": 29.5,
            "natural_gas_pct": 18.0,
            "oil_pct": 9.4,
        })
    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def mock_faiss_index():
    """Create a small in-memory FAISS-like mock for timing tests."""
    class MockIndex:
        def __init__(self, n_vectors: int = 1000, dim: int = 384):
            self.vectors = np.random.randn(n_vectors, dim).astype("float32")
            self.vectors /= np.linalg.norm(self.vectors, axis=1, keepdims=True)
            self.chunks = [
                {"text": f"Chunk {i}", "renewable_type": "solar" if i % 2 == 0 else "wind"}
                for i in range(n_vectors)
            ]

        def search(self, query: np.ndarray, k: int):
            # Simple dot-product search
            scores = np.dot(self.vectors, query.flatten())
            idx = np.argsort(scores)[::-1][:k]
            return scores[idx].reshape(1, -1), idx.reshape(1, -1)

    return MockIndex(n_vectors=1000, dim=384)


@pytest.fixture
def sample_municipality_df() -> pd.DataFrame:
    """Create a DataFrame representing 1,600 municipalities for map timing."""
    np.random.seed(42)
    n = 1600
    return pd.DataFrame({
        "municipality_id": range(1, n + 1),
        "province_id": np.random.randint(1, 82, n),
        "name": [f"Municipality {i}" for i in range(1, n + 1)],
        "lat": np.random.uniform(5.0, 20.0, n),
        "lon": np.random.uniform(117.0, 127.0, n),
        "solar_score": np.random.uniform(0, 100, n),
        "wind_score": np.random.uniform(0, 100, n),
        "hydro_score": np.random.uniform(0, 100, n),
    })


# ---------------------------------------------------------------------------
# DATASET LOADING PERFORMANCE
# ---------------------------------------------------------------------------

class TestDatasetLoadingPerformance:
    """Measure time to load and parse DOE CSV files."""

    @pytest.mark.local
    def test_doe_csv_load_time(self, sample_doe_csv):
        start = time.perf_counter()
        df = pd.read_csv(sample_doe_csv)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert len(df) == 22  # 2003-2024
        assert elapsed_ms < THRESHOLDS["dataset_load_ms"], (
            f"CSV load took {elapsed_ms:.1f}ms, threshold: {THRESHOLDS['dataset_load_ms']}ms"
        )

    @pytest.mark.local
    def test_large_csv_load_time(self, tmp_path):
        """Test with a larger synthetic dataset (10 years × 12 months)."""
        csv_path = tmp_path / "large_climate.csv"
        n_rows = 1600 * 12 * 5  # 1,600 municipalities × 12 months × 5 years
        df = pd.DataFrame({
            "municipality_id": np.random.randint(1, 1601, n_rows),
            "year": np.random.randint(2020, 2025, n_rows),
            "month": np.random.randint(1, 13, n_rows),
            "t2m": np.random.uniform(20, 35, n_rows),
            "allsky_sfc_sw_dwn": np.random.uniform(3, 7, n_rows),
        })
        df.to_csv(csv_path, index=False)

        start = time.perf_counter()
        loaded = pd.read_csv(csv_path)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert len(loaded) == n_rows
        assert elapsed_ms < THRESHOLDS["dataset_load_ms"] * 3, (
            f"Large CSV load took {elapsed_ms:.1f}ms"
        )


# ---------------------------------------------------------------------------
# PREDICTION / INFERENCE PERFORMANCE
# ---------------------------------------------------------------------------

class TestPredictionPerformance:
    """Measure ML model prediction and inference times."""

    @pytest.mark.local
    def test_linear_regression_inference_time(self):
        """Time to predict 6 years of forecast using linear regression."""
        from sklearn.linear_model import LinearRegression
        # Training data
        X_train = np.arange(22).reshape(-1, 1)
        y_train = 45000 + X_train.flatten() * 1500 + np.random.normal(0, 500, 22)
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Inference
        X_test = np.arange(22, 28).reshape(-1, 1)
        start = time.perf_counter()
        preds = model.predict(X_test)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert len(preds) == 6
        assert elapsed_ms < THRESHOLDS["prediction_ms"], (
            f"Linear regression inference took {elapsed_ms:.1f}ms"
        )

    @pytest.mark.local
    def test_preprocessing_pipeline_time(self, sample_doe_csv):
        """Time to run the full preprocessing + feature engineering pipeline."""
        df = pd.read_csv(sample_doe_csv)
        start = time.perf_counter()
        df = df.dropna()
        df["trend"] = np.arange(len(df))
        df["lag_1"] = df["consumption_gwh"].shift(1)
        df["rolling_mean_3"] = df["consumption_gwh"].rolling(3, min_periods=1).mean()
        df = df.dropna()
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < THRESHOLDS["prediction_ms"], (
            f"Preprocessing pipeline took {elapsed_ms:.1f}ms"
        )


# ---------------------------------------------------------------------------
# API RESPONSE TIME PERFORMANCE
# ---------------------------------------------------------------------------

class TestApiResponsePerformance:
    """Measure FastAPI endpoint response times."""

    @pytest.mark.benchmark
    def test_health_endpoint_response_time(self):
        """GET /api/v1/health should respond in < 500ms."""
        pytest.importorskip("httpx")
        import httpx
        base_url = os.getenv("LUMI_API_URL", "http://127.0.0.1:8000/api/v1")
        start = time.perf_counter()
        resp = httpx.get(f"{base_url}/health", timeout=5.0)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert resp.status_code == 200
        assert elapsed_ms < 500, f"Health check took {elapsed_ms:.1f}ms"

    @pytest.mark.benchmark
    def test_energyhub_overview_response_time(self):
        """GET /api/v1/energyhub/overview should respond in < 2s."""
        pytest.importorskip("httpx")
        import httpx
        base_url = os.getenv("LUMI_API_URL", "http://127.0.0.1:8000/api/v1")
        start = time.perf_counter()
        resp = httpx.get(f"{base_url}/energyhub/overview", timeout=10.0)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert resp.status_code == 200
        assert elapsed_ms < THRESHOLDS["api_response_ms"], (
            f"Overview endpoint took {elapsed_ms:.1f}ms"
        )

    @pytest.mark.benchmark
    def test_ecosim_response_time(self):
        """GET /api/v1/ecosim/?municipality_id=123&monthly_consumption=350 should respond in < 3s."""
        pytest.importorskip("httpx")
        import httpx
        base_url = os.getenv("LUMI_API_URL", "http://127.0.0.1:8000/api/v1")
        params = {"municipality_id": 123, "monthly_consumption": 350}
        start = time.perf_counter()
        resp = httpx.get(f"{base_url}/ecosim/", params=params, timeout=10.0)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert resp.status_code in (200, 422)
        assert elapsed_ms < THRESHOLDS["api_response_ms"] * 1.5, (
            f"EcoSim endpoint took {elapsed_ms:.1f}ms"
        )


# ---------------------------------------------------------------------------
# MAP DATA AGGREGATION PERFORMANCE
# ---------------------------------------------------------------------------

class TestMapAggregationPerformance:
    """Measure time to aggregate municipality data for choropleth map."""

    @pytest.mark.local
    def test_province_aggregation_time(self, sample_municipality_df):
        """Group 1,600 municipalities by province and compute mean scores."""
        start = time.perf_counter()
        aggregated = (
            sample_municipality_df
            .groupby("province_id")
            .agg({
                "solar_score": "mean",
                "wind_score": "mean",
                "hydro_score": "mean",
                "lat": "first",
                "lon": "first",
            })
            .reset_index()
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert len(aggregated) <= 82  # 81 provinces + possibly unknown
        assert elapsed_ms < THRESHOLDS["map_aggregation_ms"], (
            f"Province aggregation took {elapsed_ms:.1f}ms"
        )

    @pytest.mark.local
    def test_renewable_potential_computation_time(self, sample_municipality_df):
        """Compute composite renewable potential score for all municipalities."""
        start = time.perf_counter()
        sample_municipality_df["renewable_potential"] = (
            sample_municipality_df["solar_score"] * 0.4 +
            sample_municipality_df["wind_score"] * 0.3 +
            sample_municipality_df["hydro_score"] * 0.3
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 500, f"Renewable potential computation took {elapsed_ms:.1f}ms"


# ---------------------------------------------------------------------------
# RAG RETRIEVAL PERFORMANCE
# ---------------------------------------------------------------------------

class TestRagRetrievalPerformance:
    """Measure FAISS-based retrieval times."""

    @pytest.mark.local
    def test_faiss_search_time(self, mock_faiss_index):
        """Search a 1,000-vector FAISS mock index should take < 1s."""
        query = np.random.randn(384).astype("float32")
        query /= np.linalg.norm(query)

        start = time.perf_counter()
        scores, indices = mock_faiss_index.search(query, k=5)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert len(indices.flatten()) == 5
        assert elapsed_ms < THRESHOLDS["rag_retrieval_ms"], (
            f"FAISS search took {elapsed_ms:.1f}ms"
        )

    @pytest.mark.local
    def test_chunk_filtering_time(self, mock_faiss_index):
        """Filter retrieved chunks by renewable_type should be fast."""
        query = np.random.randn(384).astype("float32")
        query /= np.linalg.norm(query)
        scores, indices = mock_faiss_index.search(query, k=10)

        start = time.perf_counter()
        chunks = [mock_faiss_index.chunks[i] for i in indices.flatten()]
        solar_chunks = [c for c in chunks if c.get("renewable_type") == "solar"]
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert elapsed_ms < 100, f"Chunk filtering took {elapsed_ms:.1f}ms"


# ---------------------------------------------------------------------------
# MEMORY USAGE PERFORMANCE
# ---------------------------------------------------------------------------

class TestMemoryPerformance:
    """Measure approximate memory usage of key operations."""

    @pytest.mark.local
    def test_dataframe_memory_footprint(self, sample_municipality_df):
        """The municipality DataFrame should be under a reasonable memory limit."""
        mem_mb = sample_municipality_df.memory_usage(deep=True).sum() / (1024 ** 2)
        assert mem_mb < 10, f"DataFrame uses {mem_mb:.2f}MB"

    @pytest.mark.local
    def test_faiss_index_memory_footprint(self, mock_faiss_index):
        """A 1,000-vector FAISS index should use < 5MB."""
        mem_mb = mock_faiss_index.vectors.nbytes / (1024 ** 2)
        assert mem_mb < 5, f"FAISS mock index uses {mem_mb:.2f}MB"
