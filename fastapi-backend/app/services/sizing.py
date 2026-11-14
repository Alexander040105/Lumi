"""app/services/sizing.py

Sizing and dispatch service for Solar PV, LiFePO4 batteries, and Net-Metering export.
Directly grounded in peer-reviewed studies and regulatory mandates (2021-2026).
See docs/ECOSIM-SIZING-BATTERY-IMPLEMENTATION-SPEC.md for the full derivation.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from app.config.citations import CITATION_REGISTRY

# Sourced Engineering Constants (2021-2026)
PANEL_WATTAGE: int = 550                      # PSSEA (2024)
PANEL_AREA_M2: float = 2.20                   # Jinko Solar (2024); LONGi (2023)
PANEL_COST_PHP: float = 4200.0                # PSSEA (2024)
PHP_PER_KWP_GRID_TIE: float = 48000.0         # Dela Cruz & Santos (2023); ICSC (2023)
PHP_PER_KWP_HYBRID_BASE: float = 55000.0      # PSSEA (2024); IRENA (2023)
SOLAR_PR_FALLBACK: float = 0.77               # World Bank & Solargis (2021)

UNIT_BATTERY_KWH: float = 5.12                # Deye Inverter Technology (2024)
PHP_PER_KWH_BATTERY: float = 15000.0          # BloombergNEF (2023); ADB (2022)
DEPTH_OF_DISCHARGE: float = 0.90              # Preger et al. (2021); ADB (2022)
ROUND_TRIP_EFFICIENCY: float = 0.88           # ADB (2022); Deye (2024)
BATTERY_MAX_C_RATE: float = 0.50              # Deye (2024); Preger et al. (2021)
BATTERY_LIFETIME_YEARS: int = 10              # ADB (2022)
BATTERY_REPLACEMENT_FACTOR: float = 0.60      # BloombergNEF (2023)

DEFAULT_EXPORT_FRACTION: float = 0.55         # ERC (2021); Meralco (2024)
DAYTIME_FRACTION_DEFAULT: float = 0.35        # Mendoza & Tan (2022); PSA & DOE (2022)
GRID_EMISSION_FACTOR: float = 0.6835          # DOE (2023a)

DEGRADATION_RATE: float = 0.005               # per year
TARIFF_ESCALATION: float = 0.03               # per year
OM_FRACTION: float = 0.01                     # of CapEx per year
DISCOUNT_RATE: float = 0.10                   # per year
HORIZON_YEARS: int = 25

BOM_SHARES_SOLAR: dict[str, float] = {
    "panels": 0.35,                           # PSSEA (2024)
    "inverter": 0.22,                         # PSSEA (2024)
    "mounting": 0.10,                         # ICSC (2023)
    "electrical_bos": 0.10,                   # ICSC (2023)
    "labor": 0.15,                            # Dela Cruz & Santos (2023)
    "permits": 0.08,                          # Meralco (2023); ERC (2021)
}

# Statutory consumer notice required when net-metering export applies (ERC 2021).
NET_METERING_NOTICE = (
    "Export credits are computed using your local utility's blended generation "
    "charge (typically 50%–60% of retail rate). Non-bypassable distribution and "
    "government charges still apply."
)


@dataclass(frozen=True)
class SizingInputs:
    monthly_consumption_kwh: float
    monthly_bill_php: float
    electricity_rate_php: float
    desired_savings: float = 0.50
    pvout_annual: float | None = None
    ghi_kwh_m2_day: float | None = None
    roof_area_m2: float | None = None
    daytime_fraction: float = DAYTIME_FRACTION_DEFAULT
    include_battery: bool = False


@dataclass(frozen=True)
class SizingResults:
    target_monthly_kwh: float
    daily_consumption_kwh: float
    daily_target_kwh: float
    required_kwp: float
    actual_system_kwp: float
    panels_needed: int
    daily_solar_generation_kwh: float
    monthly_solar_generation_kwh: float
    roof_area_required_m2: float
    roof_area_constrained: bool
    usable_storage_kwh: float
    nameplate_storage_kwh: float
    battery_modules_needed: int
    installed_battery_kwh: float
    daily_storage_loss_kwh: float
    daily_self_consumed_kwh: float
    monthly_self_consumed_kwh: float
    daily_exportable_kwh: float
    monthly_exportable_kwh: float
    export_rate_php: float
    monthly_export_credit_php: float
    monthly_direct_savings_php: float
    total_monthly_benefit_php: float
    solar_base_cost_php: float
    battery_cost_php: float
    total_installation_cost_php: float
    simple_payback_years: float | None
    npv_php: float | None
    discounted_payback_years: int | None
    cash_flows: list[float]
    annual_co2_avoided_kg: float
    bom_items: list[dict[str, Any]]
    disclaimers: list[str]
    citations: list[dict[str, Any]]


def _products_df():
    """Catalog dataframe via the cached products service; None on any failure."""
    try:
        from app.services.products import _load_products
        return _load_products()
    except Exception:
        return None


def _match_product(df, subcategory, *, w_range=None, cap_range=None,
                   name_pref: str | None = None) -> dict | None:
    """Deterministic catalog pick for a BOM line: cheapest priced candidate
    matching the subcategory (+wattage/capacity/name hints), else None."""
    if df is None or df.empty or "energy_subcategory" not in df:
        return None
    subs = [subcategory] if isinstance(subcategory, str) else list(subcategory)
    cand = df[df["energy_subcategory"].isin(subs)].copy()
    for col in ("wattage_w", "capacity_wh", "price_value"):
        if col in cand:
            cand[col] = pd.to_numeric(cand[col], errors="coerce")
    if w_range and "wattage_w" in cand:
        cand = cand[cand["wattage_w"].between(w_range[0], w_range[1])]
    if cap_range and "capacity_wh" in cand:
        cand = cand[cand["capacity_wh"].between(cap_range[0], cap_range[1])]
    if cand.empty:
        return None
    if name_pref:
        text = (
            cand["product_name"].fillna("") + " "
            + cand["short_description"].fillna("") + " "
            + cand["description"].fillna("")
        ).str.lower()
        preferred = cand[text.str.contains(name_pref, regex=True)]
        if not preferred.empty:
            cand = preferred
    priced = cand[cand["price_value"].notna() & (cand["price_value"] > 0)]
    pick = priced if not priced.empty else cand
    row = pick.sort_values(
        ["price_value", "product_name"], na_position="last"
    ).iloc[0]

    def _num(col):
        val = row.get(col)
        return round(float(val), 2) if val is not None and val == val else None

    def _str(col):
        val = row.get(col)
        return str(val) if val is not None and val == val and str(val) else None

    return {
        "product_name": _str("product_name"),
        "brand": _str("brand"),
        "model_number": _str("model_number"),
        "url": _str("url"),
        "image_url": _str("image_url"),
        "price_php": _num("price_value"),
        "price_type": _str("price_type"),
        "source_site": _str("source_site"),
        "wattage_w": _num("wattage_w"),
        "capacity_wh": _num("capacity_wh"),
    }


def calculate_cashflows(inputs: SizingInputs, sizing: "SizingResults") -> dict:
    """25-year life-cycle cash flows per spec §3.5: 0.5%/yr panel degradation,
    3%/yr tariff escalation, 1% O&M, Year-10 battery reinvestment at 60% of
    battery CapEx, discounted at 10%."""
    cf_out: list[float] = []
    cumulative = -sizing.total_installation_cost_php
    npv = cumulative
    discounted_payback = None
    for t in range(1, HORIZON_YEARS + 1):
        degradation = (1.0 - DEGRADATION_RATE) ** (t - 1)
        tariff = inputs.electricity_rate_php * (1.0 + TARIFF_ESCALATION) ** (t - 1)
        export_rate = sizing.export_rate_php * (1.0 + TARIFF_ESCALATION) ** (t - 1)
        revenue = (
            sizing.monthly_self_consumed_kwh * 12.0 * tariff
            + sizing.monthly_exportable_kwh * 12.0 * export_rate
        ) * degradation
        om = sizing.total_installation_cost_php * OM_FRACTION * (1.0 + TARIFF_ESCALATION) ** (t - 1)
        reinvest = (
            sizing.battery_cost_php * BATTERY_REPLACEMENT_FACTOR * (1.0 + TARIFF_ESCALATION) ** 9
            if t == BATTERY_LIFETIME_YEARS and sizing.battery_cost_php > 0
            else 0.0
        )
        flow = revenue - om - reinvest
        cf_out.append(round(flow, 2))
        npv += flow / (1.0 + DISCOUNT_RATE) ** t
        cumulative += flow
        if discounted_payback is None and cumulative >= 0:
            discounted_payback = t
    return {
        "cash_flows": cf_out,
        "npv_php": round(npv, 2),
        "discounted_payback_years": discounted_payback,
    }


def calculate_sizing(inputs: SizingInputs, products_df=None) -> SizingResults:
    days_in_month = 30.4167
    disclaimers: list[str] = []
    applicable_citations = [
        CITATION_REGISTRY["erc_net_metering_2021"],
        CITATION_REGISTRY["meralco_rates_2024"],
        CITATION_REGISTRY["mendoza_load_2022"],
        CITATION_REGISTRY["dela_cruz_solar_2023"],
        CITATION_REGISTRY["pssea_report_2024"],
        CITATION_REGISTRY["doe_ngef_2023"],
    ]
    if products_df is None:
        products_df = _products_df()

    # 1. Target Consumption
    daily_cons = inputs.monthly_consumption_kwh / days_in_month
    target_monthly = inputs.monthly_consumption_kwh * inputs.desired_savings
    daily_target = target_monthly / days_in_month

    # 2. Solar Sizing
    if inputs.pvout_annual and inputs.pvout_annual > 0:
        yield_per_kwp_day = inputs.pvout_annual / 365.0
    elif inputs.ghi_kwh_m2_day and inputs.ghi_kwh_m2_day > 0:
        yield_per_kwp_day = inputs.ghi_kwh_m2_day * SOLAR_PR_FALLBACK
    else:
        yield_per_kwp_day = 3.84

    raw_required_kwp = daily_target / yield_per_kwp_day
    panels_raw = math.ceil((raw_required_kwp * 1000.0) / PANEL_WATTAGE)

    roof_constrained = False
    if inputs.roof_area_m2 and inputs.roof_area_m2 > 0:
        max_fit = math.floor(inputs.roof_area_m2 / PANEL_AREA_M2)
        if panels_raw > max_fit:
            panels_raw = max_fit
            roof_constrained = True
            disclaimers.append(
                f"Array constrained by usable roof area ({inputs.roof_area_m2:.1f} m²). "
                f"Capped at {panels_raw} panels ({panels_raw * PANEL_WATTAGE / 1000.0:.2f} kWp)."
                if panels_raw > 0 else
                f"No {PANEL_WATTAGE}W panel fits within {inputs.roof_area_m2:.1f} m² of usable roof area."
            )

    panels_needed = max(1, panels_raw) if not (roof_constrained and panels_raw == 0) else 0
    actual_system_kwp = (panels_needed * PANEL_WATTAGE) / 1000.0
    daily_solar_gen = actual_system_kwp * yield_per_kwp_day
    monthly_solar_gen = daily_solar_gen * days_in_month
    roof_area_needed = panels_needed * PANEL_AREA_M2

    # 3. Energy Split (Daytime Self-Use vs Surplus)
    day_load = daily_cons * inputs.daytime_fraction
    night_load = daily_cons * (1.0 - inputs.daytime_fraction)

    direct_day_consumed = min(daily_solar_gen, day_load)
    daily_surplus = max(0.0, daily_solar_gen - day_load)

    # 4. Battery Storage
    usable_storage = 0.0
    nameplate_storage = 0.0
    battery_modules = 0
    installed_battery_kwh = 0.0
    storage_loss_day = 0.0
    nightly_delivered = 0.0

    if inputs.include_battery:
        applicable_citations.extend([
            CITATION_REGISTRY["preger_battery_2021"],
            CITATION_REGISTRY["adb_bess_handbook_2022"],
            CITATION_REGISTRY["bnef_battery_2023"],
        ])
        usable_storage = min(daily_surplus, night_load)
        nameplate_storage = usable_storage / DEPTH_OF_DISCHARGE
        raw_modules = math.ceil(nameplate_storage / UNIT_BATTERY_KWH) if nameplate_storage > 0 else 0

        # Continuous discharge power limit check (0.5C). Gated on
        # usable_storage: with no chargeable surplus there is nothing to
        # discharge, so no battery should be sized or costed.
        est_evening_peak_kw = night_load / 5.0
        modules_for_power = (
            math.ceil(est_evening_peak_kw / (UNIT_BATTERY_KWH * BATTERY_MAX_C_RATE))
            if est_evening_peak_kw > 0 and usable_storage > 0
            else 0
        )

        battery_modules = max(raw_modules, modules_for_power)
        installed_battery_kwh = battery_modules * UNIT_BATTERY_KWH
        storage_loss_day = usable_storage * (1.0 - ROUND_TRIP_EFFICIENCY)
        nightly_delivered = usable_storage * ROUND_TRIP_EFFICIENCY

    # 5. Export Modeling (Credited at BGC)
    daily_exportable = max(0.0, daily_surplus - usable_storage)
    monthly_exportable = daily_exportable * days_in_month
    export_rate = inputs.electricity_rate_php * DEFAULT_EXPORT_FRACTION
    monthly_export_credit = monthly_exportable * export_rate

    # Total Monthly Benefit
    daily_self_consumed = direct_day_consumed + nightly_delivered
    monthly_self_consumed = daily_self_consumed * days_in_month
    monthly_direct_savings = monthly_self_consumed * inputs.electricity_rate_php
    total_monthly_benefit = monthly_direct_savings + monthly_export_credit

    # 6. Turnkey Capital Costs & Dynamic BOM
    if inputs.include_battery:
        solar_base_cost = actual_system_kwp * PHP_PER_KWP_HYBRID_BASE
        battery_cost = installed_battery_kwh * PHP_PER_KWH_BATTERY
    else:
        solar_base_cost = actual_system_kwp * PHP_PER_KWP_GRID_TIE
        battery_cost = 0.0

    total_cost = solar_base_cost + battery_cost
    annual_benefit = total_monthly_benefit * 12.0
    simple_payback = round(total_cost / annual_benefit, 2) if annual_benefit > 0 else None
    annual_co2 = monthly_self_consumed * 12.0 * GRID_EMISSION_FACTOR

    inverter_pref = r"hybrid|off.?grid|sun-?\d|sg0|sph" if inputs.include_battery else r"grid.?tie|on.?grid|\bgt\b"
    bom_items: list[dict[str, Any]] = [
        {
            "id": "solar_panels",
            "name": f"Tier-1 Mono TOPCon/PERC {PANEL_WATTAGE}W Panels",
            "qty": panels_needed,
            "cost_share": BOM_SHARES_SOLAR["panels"],
            "total_php": solar_base_cost * BOM_SHARES_SOLAR["panels"],
            "citation_key": "pssea_report_2024",
            "matched_product": _match_product(products_df, "panel", w_range=(450, 650)),
        },
        {
            "id": "solar_inverter",
            "name": "Single-Phase Hybrid Inverter" if inputs.include_battery else "Single-Phase Grid-Tie Inverter",
            "qty": 1,
            "cost_share": BOM_SHARES_SOLAR["inverter"],
            "total_php": solar_base_cost * BOM_SHARES_SOLAR["inverter"],
            "citation_key": "pssea_report_2024",
            "matched_product": _match_product(
                products_df, "inverter",
                w_range=(actual_system_kwp * 800, 1e7),
                name_pref=inverter_pref,
            ),
        },
        {
            "id": "mounting_racking",
            "name": "Anodized Aluminum Roof Rails & Clamping Kits",
            "qty": panels_needed,
            "cost_share": BOM_SHARES_SOLAR["mounting"],
            "total_php": solar_base_cost * BOM_SHARES_SOLAR["mounting"],
            "citation_key": "dela_cruz_solar_2023",
            "matched_product": _match_product(products_df, "mounting"),
        },
        {
            "id": "electrical_bos",
            "name": "DC/AC Breakers, Type 2 SPD, Combiner & PV Cables",
            "qty": 1,
            "cost_share": BOM_SHARES_SOLAR["electrical_bos"],
            "total_php": solar_base_cost * BOM_SHARES_SOLAR["electrical_bos"],
            "citation_key": "dela_cruz_solar_2023",
            "matched_product": _match_product(products_df, ["breaker", "combiner_box", "cable"]),
        },
        {
            "id": "labor_installation",
            "name": "Certified Professional Mechanical & Electrical Installation",
            "qty": 1,
            "cost_share": BOM_SHARES_SOLAR["labor"],
            "total_php": solar_base_cost * BOM_SHARES_SOLAR["labor"],
            "citation_key": "dela_cruz_solar_2023",
            "matched_product": None,
        },
        {
            "id": "permits_compliance",
            "name": "LGU CFEI Permits, ERC COC & Net-Metering DIMC Liaison",
            "qty": 1,
            "cost_share": BOM_SHARES_SOLAR["permits"],
            "total_php": solar_base_cost * BOM_SHARES_SOLAR["permits"],
            "citation_key": "erc_net_metering_2021",
            "matched_product": None,
        },
    ]

    if inputs.include_battery and battery_modules > 0:
        bom_items.append({
            "id": "battery_storage",
            "name": f"LiFePO4 {UNIT_BATTERY_KWH} kWh 51.2V 100Ah Modular Battery (90% DoD)",
            "qty": battery_modules,
            "cost_share": 1.0,
            "total_php": battery_cost,
            "citation_key": "adb_bess_handbook_2022",
            "matched_product": _match_product(products_df, "battery", cap_range=(4000, 6000)),
        })

    if monthly_exportable > 1.0:
        disclaimers.append(
            f"Net-Metering Notice: Monthly export ({monthly_exportable:.1f} kWh) is credited at the "
            f"blended generation charge (₱{export_rate:.2f}/kWh under ERC Res. 05-2020). "
            f"Fixed distribution customer charges still apply."
        )
        disclaimers.append(NET_METERING_NOTICE)

    sizing = SizingResults(
        target_monthly_kwh=round(target_monthly, 1),
        daily_consumption_kwh=round(daily_cons, 2),
        daily_target_kwh=round(daily_target, 2),
        required_kwp=round(raw_required_kwp, 2),
        actual_system_kwp=round(actual_system_kwp, 2),
        panels_needed=panels_needed,
        daily_solar_generation_kwh=round(daily_solar_gen, 2),
        monthly_solar_generation_kwh=round(monthly_solar_gen, 1),
        roof_area_required_m2=round(roof_area_needed, 1),
        roof_area_constrained=roof_constrained,
        usable_storage_kwh=round(usable_storage, 2),
        nameplate_storage_kwh=round(nameplate_storage, 2),
        battery_modules_needed=battery_modules,
        installed_battery_kwh=round(installed_battery_kwh, 2),
        daily_storage_loss_kwh=round(storage_loss_day, 2),
        daily_self_consumed_kwh=round(daily_self_consumed, 2),
        monthly_self_consumed_kwh=round(monthly_self_consumed, 1),
        daily_exportable_kwh=round(daily_exportable, 2),
        monthly_exportable_kwh=round(monthly_exportable, 1),
        export_rate_php=round(export_rate, 2),
        monthly_export_credit_php=round(monthly_export_credit, 2),
        monthly_direct_savings_php=round(monthly_direct_savings, 2),
        total_monthly_benefit_php=round(total_monthly_benefit, 2),
        solar_base_cost_php=round(solar_base_cost, 2),
        battery_cost_php=round(battery_cost, 2),
        total_installation_cost_php=round(total_cost, 2),
        simple_payback_years=simple_payback,
        npv_php=None,
        discounted_payback_years=None,
        cash_flows=[],
        annual_co2_avoided_kg=round(annual_co2, 1),
        bom_items=bom_items,
        disclaimers=disclaimers,
        citations=applicable_citations,
    )

    cashflows = calculate_cashflows(inputs, sizing)
    sizing = dataclass_replace(sizing, cashflows)

    return sizing


def dataclass_replace(sizing: SizingResults, extra: dict) -> SizingResults:
    """Rebuild SizingResults with overridden fields (frozen dataclass)."""
    from dataclasses import fields, replace
    allowed = {f.name for f in fields(sizing)}
    return replace(sizing, **{k: v for k, v in extra.items() if k in allowed})
