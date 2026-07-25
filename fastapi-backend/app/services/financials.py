"""Financial analysis module for LUMI EcoSim.

Computes NPV, IRR, LCOE, discounted payback period, and simple payback
for renewable energy system investments.

All monetary values are in PHP. All energy values are in kWh.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class FinancialInputs:
    """Inputs for financial analysis."""
    system_capacity_kw: float
    annual_energy_kwh: float
    capital_cost_php: float
    annual_om_cost_php: float
    electricity_tariff_php_kwh: float = 12.0
    discount_rate: float = 0.10
    system_lifetime_years: int = 25
    degradation_rate: float = 0.005
    residual_value_php: float = 0.0
    inflation_rate: float = 0.03


@dataclass
class FinancialResults:
    """Results from financial analysis."""
    npv_php: float
    irr: float | None
    lcoe_php_kwh: float
    simple_payback_years: float | None
    discounted_payback_years: float | None
    total_revenue_php: float
    total_cost_php: float
    net_cash_flow_year_1_php: float
    benefit_cost_ratio: float
    annual_savings_year_1_php: float


def calculate_npv(
    cash_flows: list[float],
    discount_rate: float,
) -> float:
    """Calculate Net Present Value of a series of cash flows.

    Args:
        cash_flows: List of annual cash flows (index 0 = initial investment, negative)
        discount_rate: Annual discount rate (e.g., 0.10 for 10%)

    Returns:
        NPV in PHP
    """
    npv = 0.0
    for t, cf in enumerate(cash_flows):
        npv += cf / ((1 + discount_rate) ** t)
    return npv


def calculate_irr(
    cash_flows: list[float],
    guess: float = 0.1,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> float | None:
    """Calculate Internal Rate of Return using Newton-Raphson.

    Args:
        cash_flows: List of annual cash flows (index 0 = initial investment)
        guess: Initial IRR guess
        max_iter: Maximum iterations
        tol: Convergence tolerance

    Returns:
        IRR as decimal (e.g., 0.12 for 12%) or None if no convergence
    """
    rate = guess
    for _ in range(max_iter):
        npv = 0.0
        dnpv = 0.0
        for t, cf in enumerate(cash_flows):
            factor = (1 + rate) ** t
            npv += cf / factor
            if t > 0:
                dnpv -= t * cf / (factor * (1 + rate))
        if abs(npv) < tol:
            return rate
        if abs(dnpv) < 1e-12:
            break
        rate -= npv / dnpv
        if rate <= -1.0:
            return None
    return None


def calculate_lcoe(
    capital_cost_php: float,
    annual_om_cost_php: float,
    annual_energy_kwh: float,
    discount_rate: float,
    lifetime_years: int,
    degradation_rate: float = 0.005,
) -> float:
    """Calculate Levelized Cost of Energy (LCOE).

    LCOE = (PV of costs) / (PV of energy production)

    Args:
        capital_cost_php: Total upfront capital cost
        annual_om_cost_php: Annual O&M cost (assumed constant in real terms)
        annual_energy_kwh: Year 1 energy production
        discount_rate: Annual discount rate
        lifetime_years: System lifetime
        degradation_rate: Annual energy degradation rate

    Returns:
        LCOE in PHP/kWh
    """
    pv_costs = capital_cost_php
    pv_energy = 0.0

    for t in range(1, lifetime_years + 1):
        discount_factor = 1 / ((1 + discount_rate) ** t)
        pv_costs += annual_om_cost_php * discount_factor
        annual_energy = annual_energy_kwh * ((1 - degradation_rate) ** (t - 1))
        pv_energy += annual_energy * discount_factor

    if pv_energy <= 0:
        return float("inf")
    return pv_costs / pv_energy


def calculate_payback(
    capital_cost_php: float,
    annual_savings_php: float,
    discount_rate: float,
    degradation_rate: float = 0.005,
    max_years: int = 50,
) -> tuple[float | None, float | None]:
    """Calculate simple and discounted payback periods.

    Args:
        capital_cost_php: Total upfront cost
        annual_savings_php: Year 1 net savings
        discount_rate: Annual discount rate
        degradation_rate: Annual degradation of savings
        max_years: Maximum years to consider

    Returns:
        Tuple of (simple_payback_years, discounted_payback_years)
    """
    if annual_savings_php <= 0:
        return None, None

    # Simple payback
    simple = capital_cost_php / annual_savings_php

    # Discounted payback
    cumulative = -capital_cost_php
    discounted = None
    for t in range(1, max_years + 1):
        savings = annual_savings_php * ((1 - degradation_rate) ** (t - 1))
        discounted_savings = savings / ((1 + discount_rate) ** t)
        prev_cumulative = cumulative
        cumulative += discounted_savings
        if cumulative >= 0 and prev_cumulative < 0:
            # Interpolate within the year
            fraction = abs(prev_cumulative) / discounted_savings
            discounted = t - 1 + fraction
            break

    return round(simple, 2), discounted


def analyze_financials(inputs: FinancialInputs) -> FinancialResults:
    """Full financial analysis of a renewable energy system.

    Args:
        inputs: FinancialInputs dataclass with system parameters

    Returns:
        FinancialResults dataclass with all metrics
    """
    # Build cash flow series: Year 0 = -capital_cost, Years 1..N = net savings
    cash_flows: list[float] = [-inputs.capital_cost_php]

    annual_savings_y1 = inputs.annual_energy_kwh * inputs.electricity_tariff_php_kwh
    net_cash_y1 = annual_savings_y1 - inputs.annual_om_cost_php

    total_revenue = 0.0
    total_om = 0.0

    for t in range(1, inputs.system_lifetime_years + 1):
        energy = inputs.annual_energy_kwh * ((1 - inputs.degradation_rate) ** (t - 1))
        revenue = energy * inputs.electricity_tariff_php
        om = inputs.annual_om_cost_php
        net = revenue - om
        cash_flows.append(net)
        total_revenue += revenue
        total_om += om

    # Add residual value in final year
    if inputs.residual_value_php > 0:
        cash_flows[-1] += inputs.residual_value_php

    # NPV
    npv = calculate_npv(cash_flows, inputs.discount_rate)

    # IRR
    irr = calculate_irr(cash_flows)

    # LCOE
    lcoe = calculate_lcoe(
        capital_cost_php=inputs.capital_cost_php,
        annual_om_cost_php=inputs.annual_om_cost_php,
        annual_energy_kwh=inputs.annual_energy_kwh,
        discount_rate=inputs.discount_rate,
        lifetime_years=inputs.system_lifetime_years,
        degradation_rate=inputs.degradation_rate,
    )

    # Payback
    simple_pb, discounted_pb = calculate_payback(
        capital_cost_php=inputs.capital_cost_php,
        annual_savings_php=net_cash_y1,
        discount_rate=inputs.discount_rate,
        degradation_rate=inputs.degradation_rate,
    )

    # Benefit-cost ratio
    pv_benefits = sum(
        inputs.annual_energy_kwh * ((1 - inputs.degradation_rate) ** (t - 1))
        * inputs.electricity_tariff_php / ((1 + inputs.discount_rate) ** t)
        for t in range(1, inputs.system_lifetime_years + 1)
    )
    pv_costs = inputs.capital_cost_php + sum(
        inputs.annual_om_cost_php / ((1 + inputs.discount_rate) ** t)
        for t in range(1, inputs.system_lifetime_years + 1)
    )
    bcr = pv_benefits / pv_costs if pv_costs > 0 else 0.0

    return FinancialResults(
        npv_php=round(npv, 2),
        irr=round(irr, 4) if irr is not None else None,
        lcoe_php_kwh=round(lcoe, 4),
        simple_payback_years=simple_pb,
        discounted_payback_years=discounted_pb,
        total_revenue_php=round(total_revenue, 2),
        total_cost_php=round(inputs.capital_cost_php + total_om, 2),
        net_cash_flow_year_1_php=round(net_cash_y1, 2),
        benefit_cost_ratio=round(bcr, 4),
        annual_savings_year_1_php=round(annual_savings_y1, 2),
    )


def to_dict(results: FinancialResults) -> dict[str, Any]:
    """Convert FinancialResults to a dict for API responses."""
    return {
        "npv_php": results.npv_php,
        "irr": results.irr,
        "lcoe_php_kwh": results.lcoe_php_kwh,
        "simple_payback_years": results.simple_payback_years,
        "discounted_payback_years": results.discounted_payback_years,
        "total_revenue_php": results.total_revenue_php,
        "total_cost_php": results.total_cost_php,
        "net_cash_flow_year_1_php": results.net_cash_flow_year_1_php,
        "benefit_cost_ratio": results.benefit_cost_ratio,
        "annual_savings_year_1_php": results.annual_savings_year_1_php,
    }
