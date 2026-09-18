"""Regression tests for the pre-launch audit fixes on /protected/simulations.

M2: missing or non-owned simulations must return 404 (not 500) — PostgREST
    raises APIError(PGRST116) for empty .single() results.
L1: municipality_id / province_id must be non-negative.
L2: simulation labels are plain text — angle brackets stripped, empty rejected.
L4: a missing profile row must deny access (fail closed).
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from postgrest.exceptions import APIError
from pydantic import ValidationError

from app.dependencies.auth import (
    _get_user_status,
    get_current_user_with_role_and_plan,
    get_verified_user,
)
from app.middleware.rate_limit import RateLimitMiddleware
from app.routes.simulations import SimulationCreate, SimulationUpdate
from main import app

_NOT_FOUND = APIError({"code": "PGRST116", "message": "exactly one row expected"})


def _clear_rate_limit_hits() -> None:
    """Reset the in-memory rate-limit buckets on the live middleware stack.

    Protected writes are limited to 10/min; other test files consume that
    budget before this file runs, so clear it per-test for determinism.
    """
    stack = getattr(app, "middleware_stack", None)
    while stack is not None:
        if isinstance(stack, RateLimitMiddleware):
            stack._hits.clear()
            return
        stack = getattr(stack, "app", None)


@pytest.fixture
def client():
    app.dependency_overrides[get_verified_user] = lambda: {"sub": "user-1"}
    app.dependency_overrides[get_current_user_with_role_and_plan] = lambda: {"sub": "user-1"}
    with TestClient(app) as c:
        c.get("/api/v1/health")  # force the middleware stack to build
        _clear_rate_limit_hits()
        yield c
    app.dependency_overrides.clear()


def _client_with_missing_row():
    """Supabase mock whose .single().execute() raises PGRST116."""
    mock_client = MagicMock()
    (
        mock_client.table.return_value
        .select.return_value
        .eq.return_value
        .eq.return_value
        .single.return_value
        .execute.side_effect
    ) = _NOT_FOUND
    return mock_client


class TestSimulationNotFound:
    """M2: .single() on a missing/foreign row must surface 404, not 500."""

    def test_get_missing_returns_404(self, client, monkeypatch):
        monkeypatch.setattr(
            "app.routes.simulations.get_supabase_client",
            lambda: _client_with_missing_row(),
        )
        resp = client.get("/api/v1/protected/simulations/nonexistent-id")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    def test_patch_missing_returns_404(self, client, monkeypatch):
        monkeypatch.setattr(
            "app.routes.simulations.get_supabase_client",
            lambda: _client_with_missing_row(),
        )
        resp = client.patch(
            "/api/v1/protected/simulations/nonexistent-id",
            json={"label": "new label"},
        )
        assert resp.status_code == 404

    def test_delete_missing_returns_404(self, client, monkeypatch):
        monkeypatch.setattr(
            "app.routes.simulations.get_supabase_client",
            lambda: _client_with_missing_row(),
        )
        resp = client.delete("/api/v1/protected/simulations/nonexistent-id")
        assert resp.status_code == 404


class TestSimulationInputValidation:
    """L1/L2: id bounds and plain-text label sanitization."""

    def test_negative_municipality_id_rejected(self):
        with pytest.raises(ValidationError):
            SimulationCreate(label="ok", municipality_id=-5)

    def test_negative_province_id_rejected(self):
        with pytest.raises(ValidationError):
            SimulationCreate(label="ok", province_id=-1)

    def test_html_in_label_is_stripped(self):
        sim = SimulationCreate(label="<script>alert(1)</script>My Sim")
        assert "<" not in sim.label and ">" not in sim.label
        assert sim.label == "scriptalert(1)/scriptMy Sim"

    def test_update_html_in_label_is_stripped(self):
        upd = SimulationUpdate(label="<b>Renamed</b>")
        assert upd.label == "bRenamed/b"

    def test_bracket_only_label_rejected(self):
        with pytest.raises(ValidationError):
            SimulationCreate(label="<><>")


class TestMissingProfileFailsClosed:
    """L4: no profile row -> deny (on_auth_user_created guarantees one)."""

    def test_missing_profile_denies(self, monkeypatch):
        mock_client = MagicMock()
        (
            mock_client.table.return_value
            .select.return_value
            .eq.return_value
            .single.return_value
            .execute.side_effect
        ) = _NOT_FOUND
        monkeypatch.setattr(
            "app.dependencies.auth.get_supabase_client",
            lambda: mock_client,
        )
        assert _get_user_status("ghost-user") is False
