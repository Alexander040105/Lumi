"""Regression tests for the DEF-01 -> DEF-06 boundary hardening fixes."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.requests import Request

from app.dependencies.auth import _get_user_status
from app.dependencies.quota import _in_memory_counts, _in_memory_last
from app.dependencies.auth import require_admin
from app.middleware.rate_limit import RateLimitMiddleware
from app.routes.etl import validate_table
from app.utils.network import _direct_peer_ip, _is_localhost, get_client_id
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


class TestClientIdTrust:
    def test_xff_is_ignored_from_untrusted_peer(self):
        scope = {
            "type": "http",
            "client": ("192.168.1.50", 12345),
            "headers": [(b"x-forwarded-for", b"127.0.0.1")],
        }
        request = Request(scope)
        assert _is_localhost(_direct_peer_ip(request)) is False
        assert get_client_id(request) == "192.168.1.50"

    def test_vercel_headers_are_trusted(self):
        scope = {
            "type": "http",
            "client": ("vercel-edge", 12345),
            "headers": [
                (b"x-vercel-forwarded-for", b"203.0.113.1, vercel-edge"),
                (b"x-real-ip", b"203.0.113.1"),
            ],
        }
        request = Request(scope)
        assert get_client_id(request) == "203.0.113.1"
        assert _is_localhost(_direct_peer_ip(request)) is False

    def test_localhost_direct_peer_is_exempt(self):
        scope = {
            "type": "http",
            "client": ("127.0.0.1", 12345),
            "headers": [(b"x-forwarded-for", b"10.0.0.1")],
        }
        request = Request(scope)
        assert _is_localhost(_direct_peer_ip(request)) is True


class TestUserStatusFailClosed:
    def test_pgrst116_missing_profile_is_active(self, monkeypatch):
        from postgrest.exceptions import APIError

        class FakeTable:
            def select(self, *_args, **_kwargs):
                return self

            def eq(self, *_args, **_kwargs):
                return self

            def single(self):
                return self

            def execute(self):
                raise APIError({"code": "PGRST116", "message": "exactly one row expected"})

        class FakeClient:
            def table(self, _name):
                return FakeTable()

        monkeypatch.setattr("app.dependencies.auth.get_supabase_client", lambda: FakeClient())
        assert _get_user_status("test-user-id") is True

    def test_db_error_fails_closed(self, monkeypatch):
        from postgrest.exceptions import APIError

        class FakeTable:
            def select(self, *_args, **_kwargs):
                return self

            def eq(self, *_args, **_kwargs):
                return self

            def single(self):
                return self

            def execute(self):
                raise APIError({"code": "PGRST212", "message": "connection failed"})

        class FakeClient:
            def table(self, _name):
                return FakeTable()

        monkeypatch.setattr("app.dependencies.auth.get_supabase_client", lambda: FakeClient())
        assert _get_user_status("test-user-id") is False

    def test_generic_exception_fails_closed(self, monkeypatch):
        class FakeTable:
            def select(self, *_args, **_kwargs):
                return self

            def eq(self, *_args, **_kwargs):
                return self

            def single(self):
                return self

            def execute(self):
                raise RuntimeError("network down")

        class FakeClient:
            def table(self, _name):
                return FakeTable()

        monkeypatch.setattr("app.dependencies.auth.get_supabase_client", lambda: FakeClient())
        assert _get_user_status("test-user-id") is False


class TestRateLimitMergedCounters:
    def test_flapping_redis_merges_counters(self, monkeypatch):
        """A flapping Redis must not split the local and remote counters."""

        class FlakyPipeline:
            def __init__(self, raise_after: int):
                self.calls = 0
                self.raise_after = raise_after

            async def execute(self) -> tuple:
                self.calls += 1
                if self.calls > self.raise_after:
                    raise RuntimeError("Redis connection flapping")
                # count is the number of entries already in the window
                return (None, self.calls - 1, None, None)

        class FlakyRedis:
            def __init__(self, raise_after: int):
                self._raise_after = raise_after

            def pipeline(self):
                return FlakyPipeline(self._raise_after)

        monkeypatch.setattr(
            "app.middleware.rate_limit.get_redis", lambda: FlakyRedis(30)
        )

        app = MagicMock()
        middleware = RateLimitMiddleware(app, requests_per_minute=60)
        request = MagicMock()
        request.url.path = "/api/v1/ecosim/"
        request.headers = {}
        request.client.host = "1.2.3.4"
        call_next = AsyncMock(return_value="ok")

        async def run() -> tuple[int, int]:
            allowed = 0
            denied = 0
            for _ in range(70):
                resp = await middleware.dispatch(request, call_next)
                if resp == "ok":
                    allowed += 1
                else:
                    denied += 1
            return allowed, denied

        allowed, denied = asyncio.run(run())
        # 60 allowed then 10 denied; the 30 Redis + 40 memory requests all
        # feed the same in-memory counter.
        assert allowed == 60
        assert denied == 10

    def test_redis_and_memory_counters_merge(self, monkeypatch):
        """Redis successes also update the local memory counter."""

        class HealthyPipeline:
            def __init__(self):
                self.calls = 0

            async def execute(self) -> tuple:
                self.calls += 1
                return (None, self.calls - 1, None, None)

        class HealthyRedis:
            def pipeline(self):
                return HealthyPipeline()

        monkeypatch.setattr(
            "app.middleware.rate_limit.get_redis", lambda: HealthyRedis()
        )

        app = MagicMock()
        middleware = RateLimitMiddleware(app, requests_per_minute=60)
        request = MagicMock()
        request.url.path = "/api/v1/ecosim/"
        request.headers = {}
        request.client.host = "1.2.3.4"
        call_next = AsyncMock(return_value="ok")

        async def run() -> tuple[int, int]:
            allowed = 0
            denied = 0
            for _ in range(65):
                resp = await middleware.dispatch(request, call_next)
                if resp == "ok":
                    allowed += 1
                else:
                    denied += 1
            return allowed, denied

        allowed, denied = asyncio.run(run())
        assert allowed == 60
        assert denied == 5


class TestAdminCreateUser:
    def test_create_user_response_does_not_leak_temp_password(self, monkeypatch):
        app.dependency_overrides[require_admin] = lambda: {
            "sub": "admin-id",
            "role": "admin",
        }

        class FakeAdminAuth:
            def create_user(self, _data: dict) -> Any:
                return type("Resp", (), {"user": type("User", (), {"id": "new-user-id"})()})()

        class FakeTable:
            def upsert(self, _data: dict | None = None):
                return self

            def execute(self):
                return type("Resp", (), {"data": []})()

        class FakeClient:
            def __init__(self):
                self.auth = type("Auth", (), {"admin": FakeAdminAuth()})()

            def table(self, _name: str) -> FakeTable:
                return FakeTable()

        monkeypatch.setattr(
            "app.routes.admin.get_supabase_client", lambda: FakeClient()
        )

        from fastapi.testclient import TestClient

        client = TestClient(app)
        try:
            response = client.post(
                "/api/v1/admin/users",
                json={"email": "test@example.com", "role": "user"},
                headers={
                    "x-vercel-forwarded-for": "10.0.0.1",
                    "x-real-ip": "10.0.0.1",
                },
            )
            assert response.status_code == 200
            body = response.json()
            assert "temp_password" not in body
            assert not any(
                key.endswith("_password") or key.endswith("_secret")
                for key in body.keys()
            )
        finally:
            app.dependency_overrides.pop(require_admin, None)


class TestProductionDocsAndBanner:
    def test_docs_and_openapi_disabled_in_non_debug_mode(self):
        from fastapi.testclient import TestClient

        client = TestClient(app)
        for path in ("/docs", "/redoc", "/openapi.json"):
            response = client.get(path)
            assert response.status_code == 404, f"{path} should not be exposed"

    def test_server_header_is_masked(self):
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/api/v1/")
        assert response.headers.get("server") != "uvicorn"


class TestETLTableAllowlist:
    @pytest.mark.asyncio
    async def test_validate_table_rejects_injection_names(self):
        with pytest.raises(HTTPException) as exc_info:
            await validate_table("users; DROP TABLE users")
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_validate_table_accepts_allowed_table(self, monkeypatch):
        class FakeClient:
            def table(self, name: str):
                assert name == "provinces"
                return self

            def select(self, *_, **__):
                return self

            def limit(self, _n: int):
                return self

            def execute(self):
                return type("Resp", (), {"data": [{"province_id": 1}]})()

        monkeypatch.setattr(
            "app.services.supabase_service.get_supabase_client", lambda: FakeClient()
        )
        result = await validate_table("provinces")
        assert result["table"] == "provinces"
        assert result["valid"] is True
