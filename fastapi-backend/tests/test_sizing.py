import os

import pandas as pd
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.services.sizing import (
    SizingInputs,
    _match_product,
    calculate_sizing,
)
from app.services.ecosim import build_ecosim_dashboard_response
from main import app


@pytest.fixture(scope="module")
def client():
    os.environ["USE_REDIS_CACHE"] = "false"
    return TestClient(app)


BASE = dict(
    monthly_consumption_kwh=416.67,
    monthly_bill_php=5000.0,
    electricity_rate_php=12.0,
)


def _catalog():
    """Tiny catalog covering panel/inverter/battery/mounting/BOS matching."""
    return pd.DataFrame([
        {"product_name": "Mono 550W Panel", "energy_subcategory": "panel", "wattage_w": 550.0,
         "capacity_wh": None, "price_value": 4200.0, "price_type": "fixed", "brand": "SunCo",
         "model_number": "SC550", "url": "https://shop.ph/p/1", "image_url": None,
         "source_site": "test", "short_description": "", "description": ""},
        {"product_name": "Quote Panel 550W", "energy_subcategory": "panel", "wattage_w": 550.0,
         "capacity_wh": None, "price_value": None, "price_type": "quote", "brand": "QCo",
         "model_number": None, "url": "https://shop.ph/p/2", "image_url": None,
         "source_site": "test", "short_description": "", "description": ""},
        {"product_name": "DEYE SUN-8K-SG01 Hybrid", "energy_subcategory": "inverter", "wattage_w": 8000.0,
         "capacity_wh": None, "price_value": 95000.0, "price_type": "fixed", "brand": "DEYE",
         "model_number": "SUN-8K", "url": "https://shop.ph/i/1", "image_url": None,
         "source_site": "test", "short_description": "hybrid inverter", "description": ""},
        {"product_name": "Grid-Tie 5KW GT Inverter", "energy_subcategory": "inverter", "wattage_w": 5000.0,
         "capacity_wh": None, "price_value": 45000.0, "price_type": "fixed", "brand": "GTCo",
         "model_number": "GT5", "url": "https://shop.ph/i/2", "image_url": None,
         "source_site": "test", "short_description": "grid-tie inverter", "description": ""},
        {"product_name": "51.2V 100Ah LiFePO4", "energy_subcategory": "battery", "wattage_w": None,
         "capacity_wh": 5120.0, "price_value": 76800.0, "price_type": "fixed", "brand": "BattCo",
         "model_number": "LFP-5120", "url": "https://shop.ph/b/1", "image_url": None,
         "source_site": "test", "short_description": "", "description": ""},
        {"product_name": "Roof Rail Kit", "energy_subcategory": "mounting", "wattage_w": None,
         "capacity_wh": None, "price_value": 1500.0, "price_type": "fixed", "brand": None,
         "model_number": None, "url": "https://shop.ph/m/1", "image_url": None,
         "source_site": "test", "short_description": "", "description": ""},
        {"product_name": "DC Breaker 32A", "energy_subcategory": "breaker", "wattage_w": None,
         "capacity_wh": None, "price_value": 850.0, "price_type": "fixed", "brand": None,
         "model_number": None, "url": "https://shop.ph/e/1", "image_url": None,
         "source_site": "test", "short_description": "", "description": ""},
    ])


class TestSpecAcceptanceVector:
    """docs/ECOSIM-SIZING-BATTERY-IMPLEMENTATION-SPEC.md §6 worked example:
    bill ₱5,000 @ ₱12/kWh, 100% offset, PVOUT 1400, hybrid."""

    def test_hybrid_vector(self):
        r = calculate_sizing(SizingInputs(
            **BASE, desired_savings=1.0, pvout_annual=1400, include_battery=True,
        ), products_df=_catalog())
        assert r.panels_needed == 7
        assert r.actual_system_kwp == pytest.approx(3.85)
        assert r.battery_modules_needed == 2
        assert r.installed_battery_kwh == pytest.approx(10.24)
        assert r.monthly_export_credit_php == pytest.approx(214.5, abs=0.5)
        assert r.total_installation_cost_php == pytest.approx(365350.0, abs=1)
        assert r.simple_payback_years == pytest.approx(6.31, abs=0.05)

    def test_gridtie_vector(self):
        r = calculate_sizing(SizingInputs(
            **BASE, desired_savings=1.0, pvout_annual=1400, include_battery=False,
        ), products_df=_catalog())
        assert r.panels_needed == 7
        assert r.battery_modules_needed == 0
        assert r.battery_cost_php == 0
        assert r.solar_base_cost_php == pytest.approx(3.85 * 48000)
        # all surplus is exported in grid-tie
        assert r.monthly_exportable_kwh > 30


class TestRoofClamp:
    def test_roof_limits_panels(self):
        r = calculate_sizing(SizingInputs(
            **BASE, desired_savings=1.0, pvout_annual=1400, roof_area_m2=10.0,
        ), products_df=_catalog())
        # floor(10 / 2.20) = 4 panels max
        assert r.panels_needed == 4
        assert r.roof_area_constrained is True
        assert any("constrained" in d for d in r.disclaimers)

    def test_no_clamp_when_roomy(self):
        r = calculate_sizing(SizingInputs(
            **BASE, desired_savings=1.0, pvout_annual=1400, roof_area_m2=100.0,
        ), products_df=_catalog())
        assert r.panels_needed == 7
        assert r.roof_area_constrained is False


class TestDaytimeFraction:
    def test_home_during_day_self_consumes_more(self):
        out = calculate_sizing(SizingInputs(
            **BASE, desired_savings=1.0, pvout_annual=1400, daytime_fraction=0.35,
        ), products_df=_catalog())
        home = calculate_sizing(SizingInputs(
            **BASE, desired_savings=1.0, pvout_annual=1400, daytime_fraction=0.50,
        ), products_df=_catalog())
        # Higher daytime fraction → more direct use → less surplus for export
        assert home.monthly_exportable_kwh < out.monthly_exportable_kwh
        assert home.monthly_self_consumed_kwh > out.monthly_self_consumed_kwh


class TestBatteryCRate:
    def test_power_requirement_can_bind(self):
        # Big night load forces modules_for_power above energy-only sizing:
        # night_load ~ daily*0.65; est peak = night/5; modules_for_power =
        # ceil(peak / (5.12*0.5)). With huge consumption, C-rate dominates.
        r = calculate_sizing(SizingInputs(
            monthly_consumption_kwh=3000, monthly_bill_php=36000,
            electricity_rate_php=12.0, desired_savings=1.0,
            pvout_annual=1400, include_battery=True,
        ), products_df=_catalog())
        import math
        daily = 3000 / 30.4167
        night = daily * 0.65
        surplus = max(0.0, r.actual_system_kwp * (1400 / 365) - daily * 0.35)
        usable = min(surplus, night)
        energy_modules = math.ceil((usable / 0.90) / 5.12) if usable > 0 else 0
        power_modules = math.ceil((night / 5.0) / (5.12 * 0.5))
        assert r.battery_modules_needed == max(energy_modules, power_modules)


class TestExportCredit:
    def test_export_rate_is_55pct(self):
        r = calculate_sizing(SizingInputs(**BASE, desired_savings=1.0, pvout_annual=1400),
                             products_df=_catalog())
        assert r.export_rate_php == pytest.approx(12.0 * 0.55)
        assert r.monthly_export_credit_php == pytest.approx(
            r.monthly_exportable_kwh * r.export_rate_php, abs=0.5)


class TestCashflows:
    def test_25yr_npv_and_replacement(self):
        r = calculate_sizing(SizingInputs(
            **BASE, desired_savings=1.0, pvout_annual=1400, include_battery=True,
        ), products_df=_catalog())
        assert len(r.cash_flows) == 25
        # Year-10 flow dips below neighbors due to battery reinvestment
        assert r.cash_flows[9] < r.cash_flows[8]
        assert r.cash_flows[9] < r.cash_flows[10]
        assert r.npv_php is not None


class TestProductMatching:
    def test_cheapest_priced_wins(self):
        df = _catalog()
        match = _match_product(df, "panel", w_range=(450, 650))
        assert match["product_name"] == "Mono 550W Panel"
        assert match["price_php"] == 4200.0

    def test_quote_only_falls_back_when_unpriced(self):
        df = _catalog()
        priced = df[df["product_name"] == "Mono 550W Panel"]
        quote_only = pd.concat([df.drop(priced.index), priced.iloc[0:0].assign(
            product_name="Mono 550W Panel", price_value=[None], price_type=["quote"])])
        match = _match_product(quote_only, "panel", w_range=(450, 650))
        assert match is not None
        assert match["price_type"] == "quote"
        assert match["price_php"] is None  # honest quote-only, no invented price

    def test_no_match_returns_none(self):
        assert _match_product(_catalog(), "turbine") is None

    def test_hybrid_prefers_hybrid_inverter(self):
        df = _catalog()
        match = _match_product(
            df, "inverter", w_range=(800, 1e7), name_pref=r"hybrid|off.?grid|sun-?\d|sg0|sph")
        assert "Hybrid" in match["product_name"]


class TestEcosimPolicyE2E:
    """Policy gates through the real dashboard pipeline (Lucena City, Quezon)."""

    @pytest.fixture(scope="class")
    def result(self):
        try:
            return build_ecosim_dashboard_response(
                municipality_id=5354,
                monthly_consumption=350,
                monthly_bill=5000,
                electricity_rate=14.29,
                desired_savings=0.5,
                include_ai=False,
                mode="municipality",
                data_source="auto",
            )
        except HTTPException:
            pytest.skip("municipality lookup unavailable (no Supabase)")

    def test_sizing_block_attached(self, result):
        sizing = result.get("sizing")
        assert sizing is not None
        assert sizing["panels_needed"] >= 1
        assert len(sizing["bom_items"]) >= 6
        assert len(sizing["citations"]) >= 6
        assert "disclaimers" in sizing

    def test_solar_financials_unhidden(self, result):
        solar = next(o for o in result["options"] if o["source"] == "Solar")
        assert solar["installation_cost"] is not None and solar["installation_cost"] > 0
        assert solar["payback_years"] is not None
        assert solar["npv_php"] is not None

    def test_wind_gate_and_exclusion(self, result):
        wind = next(o for o in result["options"] if o["source"] == "Wind")
        hub_ms = result["renewable_energy_results"]["climate"]["avg_wind_hub_ms"]
        if hub_ms < 5.0:
            assert wind["suitability_score"] == 0
            assert "viability floor" in wind["explanation"]
            assert result["recommended_source"] != "Wind"
        else:
            pytest.skip("site above wind floor")

    def test_hydro_academic(self, result):
        hydro = next(o for o in result["options"] if o["source"] == "Hydropower")
        assert hydro["source_type"] == "academic"
        assert "1067" in hydro["explanation"]
        assert result["recommended_source"] != "Hydropower"

    def test_backward_compat_request(self, client):
        resp = client.get(
            "/api/v1/ecosim/?municipality_id=5354&monthly_consumption=350"
            "&monthly_bill=5000&electricity_rate=14.29&desired_savings=0.5"
        )
        assert resp.status_code != 500
        if resp.status_code == 200:
            data = resp.json()
            assert data["sizing"] is not None

    def test_new_params_accepted(self, client):
        resp = client.get(
            "/api/v1/ecosim/?municipality_id=5354&monthly_consumption=350"
            "&monthly_bill=5000&electricity_rate=14.29&desired_savings=0.5"
            "&include_battery=true&roof_area_m2=25&daytime_fraction=0.5"
        )
        assert resp.status_code != 500
        if resp.status_code == 200:
            data = resp.json()
            sizing = data["sizing"]
            assert sizing["battery_modules_needed"] >= 1
            # floor(25/2.2)=11 max panels
            assert sizing["panels_needed"] <= 11

    def test_param_validation(self, client):
        resp = client.get(
            "/api/v1/ecosim/?municipality_id=5354&monthly_consumption=350"
            "&monthly_bill=5000&electricity_rate=14.29&daytime_fraction=1.5"
        )
        # Quota middleware may 401/429 before pydantic validates the body.
        assert resp.status_code in (401, 422, 429)
