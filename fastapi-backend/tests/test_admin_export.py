import pytest
from fastapi.testclient import TestClient

from app.dependencies.auth import require_admin
from main import app


class _FakeResponse:
    def __init__(self, data):
        self.data = data


class _FakeQuery:
    """Minimal stand-in for a supabase table query chain."""

    def __init__(self, data):
        self._data = data

    def select(self, *args, **kwargs):
        return self

    def order(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def offset(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def insert(self, *args, **kwargs):
        return self

    def execute(self):
        return _FakeResponse(self._data)


class _FakeRpc:
    def __init__(self, data):
        self._data = data

    def execute(self):
        return _FakeResponse(self._data)


class FakeSupabaseClient:
    def __init__(self, rpc_data=None, table_data=None):
        self._rpc_data = rpc_data or []
        self._table_data = table_data or []

    def rpc(self, *args, **kwargs):
        return _FakeRpc(self._rpc_data)

    def table(self, name):
        return _FakeQuery(self._table_data)


@pytest.fixture
def client():
    app.dependency_overrides.clear()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_client():
    app.dependency_overrides.clear()
    app.dependency_overrides[require_admin] = lambda: {"sub": "admin-1", "role": "admin"}
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_usage_export_returns_csv(admin_client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.admin.get_supabase_client",
        lambda: FakeSupabaseClient(
            rpc_data=[
                {
                    "id": "u1",
                    "full_name": "Doe, John",
                    "email": "john@example.com",
                    "role": "user",
                    "is_active": True,
                    "total_simulations": 2,
                    "simulations_this_month": 1,
                    "total_ecosim": 5,
                    "ecosim_this_month": 3,
                    "last_active": "2026-09-17T10:00:00Z",
                },
                {
                    "id": "u2",
                    "full_name": None,
                    "email": "jane@example.com",
                    "role": "admin",
                    "is_active": False,
                    "total_simulations": 0,
                    "simulations_this_month": 0,
                    "total_ecosim": 0,
                    "ecosim_this_month": 0,
                    "last_active": None,
                },
            ]
        ),
    )

    resp = admin_client.get("/api/v1/admin/usage/export")

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "attachment" in resp.headers["content-disposition"]
    assert "user-usage-" in resp.headers["content-disposition"]

    lines = resp.text.splitlines()
    assert lines[0] == (
        "user_id,full_name,email,role,status,total_simulations,"
        "simulations_this_month,total_ecosim,ecosim_this_month,last_active"
    )
    assert '"Doe, John"' in resp.text  # comma in name is quoted
    assert "john@example.com" in resp.text
    assert "active" in resp.text
    assert "banned" in resp.text


def test_logs_export_returns_csv(admin_client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.admin.get_supabase_client",
        lambda: FakeSupabaseClient(
            table_data=[
                {
                    "id": "l1",
                    "created_at": "2026-09-17T10:00:00Z",
                    "admin_id": "admin-1",
                    "action": "ban_user",
                    "target_user_id": "u9",
                    "details": {"is_active": False},
                },
                {
                    "id": "l2",
                    "created_at": "2026-09-16T09:00:00Z",
                    "admin_id": "admin-2",
                    "action": "update_config",
                    "target_user_id": None,
                    "details": {"free_sim_limit": 3},
                },
            ]
        ),
    )

    resp = admin_client.get("/api/v1/admin/logs/export")

    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "attachment" in resp.headers["content-disposition"]
    assert "admin-audit-logs-" in resp.headers["content-disposition"]

    lines = resp.text.splitlines()
    assert lines[0] == "id,created_at,admin_id,action,target_user_id,details"
    assert "ban_user" in resp.text
    assert "update_config" in resp.text
    assert "is_active" in resp.text  # details serialised as JSON


def test_usage_export_requires_auth(client):
    resp = client.get("/api/v1/admin/usage/export")
    assert resp.status_code == 401


def test_logs_export_requires_auth(client):
    resp = client.get("/api/v1/admin/logs/export")
    assert resp.status_code == 401
