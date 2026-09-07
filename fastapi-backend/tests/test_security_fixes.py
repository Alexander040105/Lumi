"""Regression tests for the DEF-01 -> DEF-06 boundary hardening fixes."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.dependencies.quota import _in_memory_counts, _in_memory_last
from main import app


@pytest.fixture(autouse=True)
def _clear_quota():
    """Reset in-memory quota state between tests so each test gets one fresh request."""
    _in_memory_counts.clear()
    _in_memory_last.clear()
    yield
    _in_memory_counts.clear()
    _in_memory_last.clear()


@pytest.fixture
def client():
    """Unmocked TestClient for boundary/validation tests."""
    app.dependency_overrides.clear()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestGeothermalNotFound:
    """DEF-01: /geothermal/{municipality_id} should return 404, not 500."""

    def test_bad_municipality_id_returns_404(self, client, monkeypatch):
        """A missing municipality must raise a clean 404."""
        from postgrest.exceptions import APIError

        mock_client = MagicMock()
        error = APIError({"code": "PGRST116", "message": "exactly one row expected"})
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = error

        monkeypatch.setattr(
            "app.routes.geothermal.get_supabase_client",
            lambda: mock_client,
        )

        response = client.get("/api/v1/geothermal/999999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Municipality not found"


class TestMapValidation:
    """DEF-02: /map/{invalid_type} and /map/coverage?level=... should 422."""

    def test_invalid_renewable_type_returns_422(self, client):
        response = client.get("/api/v1/map/nuclear")
        assert response.status_code == 422

    def test_invalid_map_level_returns_422(self, client):
        response = client.get("/api/v1/map/coverage?level=country")
        assert response.status_code == 422

    def test_valid_map_type_returns_200(self, client):
        response = client.get("/api/v1/map/solar")
        assert response.status_code == 200


class TestEnergyHubForecastValidation:
    """DEF-03: /energyhub/forecast must reject an unknown metric."""

    def test_invalid_forecast_metric_returns_422(self, client):
        response = client.get("/api/v1/energyhub/forecast?metric=bogus")
        assert response.status_code == 422

    def test_valid_forecast_metric_returns_200(self, client):
        response = client.get("/api/v1/energyhub/forecast?metric=consumption")
        assert response.status_code == 200

    def test_model_comparison_invalid_metric_returns_422(self, client):
        response = client.get("/api/v1/energyhub/model-comparison?metric=bogus")
        assert response.status_code == 422


class TestForecastRunValidation:
    """DEF-04: /forecast/run and /forecast/backtest must reject an unknown metric."""

    def test_run_invalid_metric_returns_422(self, client):
        response = client.get("/api/v1/forecast/run?metric=' OR '1'='1")
        assert response.status_code == 422

    def test_backtest_invalid_metric_returns_422(self, client):
        response = client.get("/api/v1/forecast/backtest?metric=' OR '1'='1")
        assert response.status_code == 422

    def test_run_valid_metric_returns_200(self, client):
        response = client.get("/api/v1/forecast/run?metric=consumption")
        assert response.status_code == 200


class TestProductsValidation:
    """DEF-05: /products/recommend must reject an unknown energy_type and not echo input."""

    def test_invalid_energy_type_returns_422(self, client):
        injection = "solar' OR '1'='1"
        response = client.get(f"/api/v1/products/recommend?energy_type={injection}")
        assert response.status_code == 422
        # The response must be a validation error, never a successful products payload.
        data = response.json()
        assert "items" not in data
        assert any(err.get("loc") == ["query", "energy_type"] for err in data.get("detail", []))

    def test_valid_energy_type_returns_200(self, client):
        response = client.get("/api/v1/products/recommend?energy_type=solar")
        assert response.status_code == 200


class TestQuotaMessage:
    """DEF-06: anonymous-quota 401 messages must name the correct product."""

    @pytest.fixture
    def mock_energyhub_service(self, monkeypatch):
        class MockEnergyHub:
            def get_ai_insight(self, use_llm: bool = False):
                return {
                    "insight": "Test insight",
                    "recommendation": "Test recommendation",
                    "data_year": 2024,
                }

            def analyze_chart(self, chart_type, chart_data, force_refresh=False):
                return {
                    "insight": "Test chart insight",
                    "recommendation": "Test chart recommendation",
                    "data_year": 2024,
                    "chart_type": chart_type,
                }

            def get_map_explanation(self, metric, level, force_refresh=False):
                return {
                    "insight": "Test map explanation",
                    "recommendation": "",
                    "data_year": 2024,
                    "chart_type": f"map_{metric}",
                }

        monkeypatch.setattr(
            "app.routes.energyhub.get_energyhub_service",
            lambda: MockEnergyHub(),
        )

    def test_energyhub_ai_insight_quota_message(self, client, mock_energyhub_service):
        # First anonymous request consumes the quota.
        response = client.get("/api/v1/energyhub/ai-insight?use_llm=true")
        assert response.status_code == 200

        # Second anonymous request should be rejected with the EnergyHub message.
        response = client.get("/api/v1/energyhub/ai-insight?use_llm=true")
        assert response.status_code == 401
        assert "EnergyHub" in response.json()["detail"]
        assert "EcoSim" not in response.json()["detail"]

    def test_energyhub_analyze_chart_quota_message(self, client, mock_energyhub_service):
        payload = {"chart_type": "trends", "chart_data": {"years": [2020]}}
        response = client.post("/api/v1/energyhub/analyze-chart", json=payload)
        assert response.status_code == 200

        response = client.post("/api/v1/energyhub/analyze-chart", json=payload)
        assert response.status_code == 401
        assert "EnergyHub" in response.json()["detail"]
        assert "EcoSim" not in response.json()["detail"]

    def test_energyhub_map_explanation_quota_message(self, client, mock_energyhub_service):
        params = {"metric": "renewable_potential", "level": "province"}
        response = client.get("/api/v1/energyhub/map-explanation", params=params)
        assert response.status_code == 200

        response = client.get("/api/v1/energyhub/map-explanation", params=params)
        assert response.status_code == 401
        assert "EnergyHub" in response.json()["detail"]
        assert "EcoSim" not in response.json()["detail"]

    def test_ecosim_quota_message(self, client, monkeypatch):
        params = {
            "municipality_id": 1,
            "monthly_consumption": 350,
            "monthly_bill": 5000,
        }

        def _fake_dashboard(*args, **kwargs):
            return {
                "municipality": "CALAMBA",
                "municipality_id": 1,
                "monthly_consumption_kwh": 295.0,
                "user_consumption_kwh": 350.0,
                "effective_consumption_kwh": 295.0,
                "monthly_bill": 5000.0,
                "input_warning": True,
                "recommended_source": "Solar",
                "suitability_score": 0.0,
                "generation_score": 60.0,
                "source_type": "household",
                "estimated_generation_kwh": 177.0,
                "monthly_savings": None,
                "installation_cost": None,
                "payback_years": None,
                "carbon_reduction": 120.0,
                "explanation": "Test explanation",
                "options": [],
            }

        monkeypatch.setattr("app.routes.ecosim.build_ecosim_dashboard_response", _fake_dashboard)

        response = client.get("/api/v1/ecosim/", params=params)
        assert response.status_code == 200

        response = client.get("/api/v1/ecosim/", params=params)
        assert response.status_code == 401
        assert "EcoSim" in response.json()["detail"]
