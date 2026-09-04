import os

import pytest
from fastapi.testclient import TestClient

from app.services.atlas_data import (
    get_atlas_for_municipality,
    get_atlas_for_municipality_ids,
    get_atlas_for_province,
    get_era5_for_municipality,
    get_era5_for_province,
    get_province_atlas,
)
from app.services.ecosim import build_ecosim_dashboard_response, get_municipality_data, get_province_data
from main import app


@pytest.fixture(scope="module")
def client():
    # Keep cache disabled for route tests so each request exercises the full stack.
    os.environ["USE_REDIS_CACHE"] = "false"
    return TestClient(app)


class _FailingQuery:
    def select(self, *_a, **_kw):
        return self

    def eq(self, *_a, **_kw):
        return self

    def in_(self, *_a, **_kw):
        return self

    def limit(self, *_a, **_kw):
        return self

    def maybe_single(self, *_a, **_kw):
        return self

    def single(self, *_a, **_kw):
        return self

    def execute(self, *_a, **_kw):
        raise RuntimeError("Supabase unavailable")


class _FailingClient:
    def table(self, _name):
        return _FailingQuery()


def _patch_supabase(monkeypatch):
    """Make atlas/era5 loaders think Supabase is down so the CSV fallback is used."""
    import app.services.atlas_data as atlas

    monkeypatch.setattr(atlas, "get_supabase_client", lambda: _FailingClient())


def test_quezon_province_no_500(client):
    """QUEZON province must not return a 500 or a generic server error."""
    resp = client.get(
        "/api/v1/ecosim/?municipality_id=271&monthly_consumption=350"
        "&monthly_bill=5000&electricity_rate=14.29&desired_savings=0.5&mode=province"
    )
    assert resp.status_code != 500
    assert resp.status_code != 503
    if resp.status_code == 200:
        data = resp.json()
        assert data["municipality"] == "QUEZON"
        assert data["mode"] == "province"
        assert data["recommended_source"] in ("Solar", "Wind", "Hydro")
    else:
        # 404 is acceptable if data is genuinely missing; 401/429 are quota/auth.
        assert resp.status_code in (200, 401, 404, 429)


def test_quezon_municipality_no_500(client):
    """A QUEZON municipality must not return a 500 or a generic server error."""
    # Use Lucena City, a known Quezon municipality (municipality_id 5354 is the
    # first municipality in the Quezon atlas CSV).
    resp = client.get(
        "/api/v1/ecosim/?municipality_id=5354&monthly_consumption=350"
        "&monthly_bill=5000&electricity_rate=14.29&desired_savings=0.5&mode=municipality"
    )
    assert resp.status_code != 500
    assert resp.status_code != 503
    if resp.status_code == 200:
        data = resp.json()
        assert data["municipality_id"] == 5354
        assert data["mode"] == "municipality"
    else:
        assert resp.status_code in (200, 401, 404, 429)


def test_build_ecosim_dashboard_quezon_province():
    """Direct service call for QUEZON must return a valid dashboard."""
    result = build_ecosim_dashboard_response(
        municipality_id=271,
        monthly_consumption=350,
        monthly_bill=5000,
        electricity_rate=14.29,
        desired_savings=0.5,
        include_ai=False,
        mode="province",
        data_source="auto",
    )
    assert result["municipality"] == "QUEZON"
    assert result["municipality_id"] == 271
    assert result["recommended_source"] in ("Solar", "Wind", "Hydro")
    assert isinstance(result["estimated_generation_kwh"], (int, float))


def test_get_province_data_quezon():
    """QUEZON province aggregation should not raise."""
    data = get_province_data("QUEZON", source="auto")
    assert data["municipality_id"] == 271
    assert data["province"] == "QUEZON"
    assert "avg_allsky_sfc_sw_dwn" in data


def test_get_municipality_data_quezon():
    """A QUEZON municipality should not raise."""
    rows = get_municipality_data(None, municipality_id=5354, source="auto")
    assert rows
    assert rows[0]["municipality_id"] == 5354
    assert rows[0]["name"]


def test_missing_csv_fallbacks_return_none_or_empty(monkeypatch):
    """If local CSVs are missing, loaders must not crash."""
    import app.services.atlas_data as atlas

    _patch_supabase(monkeypatch)
    monkeypatch.setattr(atlas, "LOCAL_ATLAS_CSV", atlas.LOCAL_ATLAS_CSV.with_name("missing.csv"))
    monkeypatch.setattr(atlas, "LOCAL_PROVINCE_ATLAS_CSV", atlas.LOCAL_PROVINCE_ATLAS_CSV.with_name("missing.csv"))
    monkeypatch.setattr(atlas, "LOCAL_MUNI_ERA5_CSV", atlas.LOCAL_MUNI_ERA5_CSV.with_name("missing.csv"))
    monkeypatch.setattr(atlas, "LOCAL_PROVINCE_ERA5_CSV", atlas.LOCAL_PROVINCE_ERA5_CSV.with_name("missing.csv"))

    assert get_province_atlas(271) is None
    assert get_atlas_for_municipality(5354) is None
    assert get_atlas_for_municipality_ids([5354, 5355]) == {}
    assert get_atlas_for_province(271) == {}
    assert get_era5_for_municipality(5354) is None
    assert get_era5_for_province(271) is None
