import pytest
from fastapi.testclient import TestClient

from app.dependencies.auth import get_verified_user_optional
from app.dependencies.quota import _in_memory_counts, _in_memory_last
from main import app


def _sample_dashboard(**_):
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
        "comparison": None,
        "climate": {},
        "renewable_energy_results": {
            "municipality": "CALAMBA",
            "municipality_id": 1,
            "climate": {},
            "assumptions": {},
            "consumption_results": {
                "monthly_consumption_kwh": 295.0,
                "daily_consumption_kwh": 9.83,
                "target_monthly_consumption_kwh": 295.0,
            },
            "solar_output": {
                "system_kwp": 1.5,
                "daily_solar_output": 6.0,
                "monthly_solar_output": 177.0,
                "annual_solar_output": 2124.0,
                "solar_score": 80.0,
                "generation_score": 60.0,
            },
            "wind_output": {
                "swept_area_m2": 5.0,
                "rated_power_kw": 1.0,
                "capacity_factor": 0.25,
                "daily_energy_kwh": 3.0,
                "monthly_energy_kwh": 90.0,
                "annual_wind_output_kwh": 1080.0,
                "generation_score": 30.0,
            },
            "hydro_output": {
                "system_kwp": 0.5,
                "daily_hydro_output": 2.0,
                "monthly_hydro_output": 60.0,
                "annual_hydro_output": 720.0,
                "hydro_score": 50.0,
                "generation_score": 20.0,
            },
            "geothermal_output": {
                "energy_type": "geothermal",
                "suitability_score": 80.0,
                "classification": "Good",
                "annual_energy_gwh": 100.0,
                "confidence": 0.8,
                "source": "Supabase pre-computed",
                "citation": "Test citation",
            },
        },
        "consumption_results": {
            "monthly_consumption_kwh": 295.0,
            "daily_consumption_kwh": 9.83,
            "target_monthly_consumption_kwh": 295.0,
        },
        "municipality_data": [],
        "ai_analysis": None,
        "nearby_geothermal_plants": [],
    }


def _sample_calculator(*args, **kwargs):
    return _sample_dashboard()


class MockEnergyHubService:
    def get_ai_insight(self, use_llm=False):
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


@pytest.fixture
def client(monkeypatch):
    _in_memory_counts.clear()
    _in_memory_last.clear()

    monkeypatch.setattr(
        "app.routes.ecosim.build_ecosim_dashboard_response",
        _sample_dashboard,
    )
    monkeypatch.setattr(
        "app.routes.ecosim.renewable_energy_calculator",
        _sample_calculator,
    )
    monkeypatch.setattr(
        "app.routes.energyhub.get_energyhub_service",
        lambda: MockEnergyHubService(),
    )
    app.dependency_overrides.clear()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def authed_client(client):
    app.dependency_overrides[get_verified_user_optional] = lambda: {
        "sub": "test-user",
        "email": "test@example.com",
    }
    return client


def test_ecosim_get_anonymous_first_request(client):
    response = client.get(
        "/api/v1/ecosim/?municipality_id=1&monthly_consumption=350&monthly_bill=5000"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["input_warning"] is True
    assert data["generation_score"] == 60.0
    assert data["monthly_savings"] is None
    assert data["installation_cost"] is None
    assert data["payback_years"] is None
    assert data["comparison"] is None
    assert data["remaining_anonymous_requests"] == 0


def test_ecosim_get_anonymous_second_request_blocked(client):
    client.get(
        "/api/v1/ecosim/?municipality_id=1&monthly_consumption=350&monthly_bill=5000"
    )
    response = client.get(
        "/api/v1/ecosim/?municipality_id=1&monthly_consumption=350&monthly_bill=5000"
    )
    assert response.status_code == 401
    assert "log in" in response.json()["detail"].lower()


def test_ecosim_get_authenticated_no_quota(authed_client):
    response = authed_client.get(
        "/api/v1/ecosim/?municipality_id=1&monthly_consumption=350&monthly_bill=5000"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["remaining_anonymous_requests"] is None


def test_ecosim_post_anonymous_first_request(client):
    payload = {
        "house_name": "Test",
        "municipality": "CALAMBA",
        "current_electricity_bill": 5000,
        "electricity_rate": 16.95,
        "desired_savings": 0.5,
        "mode": "municipality",
    }
    response = client.post("/api/v1/ecosim/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["remaining_anonymous_requests"] == 0


def test_ecosim_post_anonymous_second_request_blocked(client):
    """Anonymous second POST should be blocked."""
    payload = {
        "house_name": "Test",
        "municipality": "CALAMBA",
        "current_electricity_bill": 5000,
        "electricity_rate": 16.95,
        "desired_savings": 0.5,
        "mode": "municipality",
    }
    client.post("/api/v1/ecosim/", json=payload)
    response = client.post("/api/v1/ecosim/", json=payload)
    assert response.status_code == 401


def test_energyhub_ai_insight_static_no_quota(client):
    for _ in range(3):
        response = client.get("/api/v1/energyhub/ai-insight?use_llm=false")
        assert response.status_code == 200
        data = response.json()
        assert data["insight"] == "Test insight"
        assert data["remaining_anonymous_requests"] is None


def test_energyhub_ai_insight_llm_anonymous_quota(client):
    response = client.get("/api/v1/energyhub/ai-insight?use_llm=true")
    assert response.status_code == 200
    assert response.json()["remaining_anonymous_requests"] == 0

    response = client.get("/api/v1/energyhub/ai-insight?use_llm=true")
    assert response.status_code == 401


def test_energyhub_analyze_chart_anonymous_quota(client):
    payload = {"chart_type": "trends", "chart_data": {}}
    response = client.post("/api/v1/energyhub/analyze-chart", json=payload)
    assert response.status_code == 200
    assert response.json()["remaining_anonymous_requests"] == 0

    response = client.post("/api/v1/energyhub/analyze-chart", json=payload)
    assert response.status_code == 401


def test_energyhub_authenticated_bypass_quota(authed_client):
    payload = {"chart_type": "trends", "chart_data": {}}
    for _ in range(3):
        response = authed_client.post("/api/v1/energyhub/analyze-chart", json=payload)
        assert response.status_code == 200
        assert response.json()["remaining_anonymous_requests"] is None
