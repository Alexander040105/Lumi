"""
Build structured renewable-energy knowledge documents from scraped product data
AND all other LUMI data sources (national energy statistics, municipality climate,
terrain metrics).

The input is scraped e-commerce listings (Alibaba, Amazon, Lazada).  Instead of
indexing raw product rows, we aggregate them into *knowledge chunks* that a
RAG system can use to answer budget, component, and comparison questions.

Knowledge categories
--------------------
- equipment_cost   : price ranges for individual components
- installation_cost: system-level installation estimates (derived from equipment + labour ratios)
- maintenance_cost : expected maintenance / replacement schedules
- components       : required parts for each renewable type
- capacity_info    : typical system sizes and outputs
- pricing_assumptions: how prices were derived, currency notes, source caveats
- national_energy_statistics: DOE national energy annual data
- municipality_climate: NASA POWER climate averages per municipality
- terrain_metrics: terrain and hydropower suitability per municipality
"""

from __future__ import annotations

import json
import logging
import re
import statistics
from pathlib import Path
from typing import Any

import pandas as pd

from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CSV = REPO_ROOT / "scraped_data" / "output" / "cleaned" / "cleaned_products_master.csv"
LOCAL_DATA_DIR = Path(__file__).resolve().parent / "local_data"
LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_JSON_PATH = LOCAL_DATA_DIR / "rag_knowledge_base.json"

# LUMI data sources for RAG
NATIONAL_ENERGY_CSV = REPO_ROOT / "DOE_Data_Extracted" / "national_energy_annual_ready.csv"
MUNICIPALITIES_CSV = REPO_ROOT / "regionalData" / "municipalities.csv"
CLIMATE_CSV = REPO_ROOT / "fastapi-backend" / "app" / "services" / "local_data" / "municipality_climate_averages.csv"
TERRAIN_CSV = REPO_ROOT / "regionalData" / "output" / "terrain_metrics" / "municipality_terrain_metrics.csv"

# ---------------------------------------------------------------------------
# Re-classification rules (fixes the wind/hydro mis-labelling in the CSV)
# ---------------------------------------------------------------------------
RENEWABLE_RULES: list[tuple[str, list[str]]] = [
    ("solar", ["solar", "pv", "photovoltaic", "panel", "inverter", "mppt", "pwm", "charge controller", "solar battery"]),
    ("hydro", ["hydro", "hydroelectric", "pelton", "francis", "kaplan", "water turbine", "micro hydro", "hydropower", "hydro generator", "water power", "run-of-river"]),
    ("wind",  ["wind", "windmill", "wind turbine", "wind controller", "dump load", "wind generator", "aeolian"]),
]

PRODUCT_TYPE_RULES: list[tuple[str, list[str]]] = [
    ("panel",            ["solar panel", "pv panel", "photovoltaic panel"]),
    ("inverter",         ["inverter", "microinverter", "solar inverter", "grid tie inverter"]),
    ("battery",          ["battery", "lifepo4", "lithium battery", "solar battery", "deep cycle"]),
    ("charge_controller", ["charge controller", "mppt", "pwm controller", "solar controller"]),
    ("mounting_system",  ["mounting bracket", "mounting system", "solar bracket", "panel bracket", "solar rack"]),
    ("turbine",          ["turbine", "pelton", "francis", "kaplan", "water turbine", "wind turbine", "windmill"]),
    ("generator",        ["generator", "permanent magnet generator", "pmg"]),
    ("controller",       ["controller", "wind controller", "hydro controller"]),
    ("meter",            ["energy meter", "smart meter", "power meter"]),
]

CURRENCY_TO_PHP = {
    "PHP": 1.0,
    "USD": 60.0,   # approximate; documents will note this is an estimate
    "CNY": 8.96,
    "EUR": 70.0,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def classify_renewable(name: str, source_file: str = "") -> str:
    text = _normalize(name + " " + source_file)
    for rtype, keywords in RENEWABLE_RULES:
        if any(kw in text for kw in keywords):
            return rtype
    return ""


def classify_product_type(name: str) -> str:
    text = _normalize(name)
    for ptype, keywords in PRODUCT_TYPE_RULES:
        if any(kw in text for kw in keywords):
            return ptype
    return ""


def to_php(price: float, currency: str) -> float:
    return price * CURRENCY_TO_PHP.get(currency.upper(), 1.0)


def _currency_note(currency: str) -> str:
    if currency.upper() == "USD":
        return "converted from USD to PHP at approximate rate 1 USD = 60 PHP"
    if currency.upper() == "CNY":
        return "converted from CNY to PHP at approximate rate 1 CNY = 8.96 PHP"
    return ""


# ---------------------------------------------------------------------------
# Load & clean CSV
# ---------------------------------------------------------------------------

def load_and_fix_csv(csv_path: Path = DEFAULT_CSV) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Cleaned CSV not found: {csv_path}")

    df = pd.read_csv(csv_path, dtype=str)
    df = df.rename(columns={c: c.strip().lower() for c in df.columns})

    # Keep only rows that have a parseable price
    df["price_value_num"] = pd.to_numeric(df.get("price_value", pd.Series()), errors="coerce")
    df = df.dropna(subset=["price_value_num"])
    df["price_value_num"] = df["price_value_num"].astype(float)

    # Re-classify renewable type using name + source file
    df["renewable_type"] = df.apply(
        lambda r: classify_renewable(
            str(r.get("product_name", "")),
            str(r.get("source_file", "")),
        ),
        axis=1,
    )

    # Re-classify product type using product name
    df["product_type"] = df["product_name"].astype(str).apply(classify_product_type)

    # Drop rows we cannot classify at all
    df = df[df["renewable_type"] != ""].copy()

    # Convert prices to PHP
    df["currency"] = df.get("currency", "PHP").fillna("PHP")
    df["price_php"] = df.apply(lambda r: to_php(r["price_value_num"], r["currency"]), axis=1)

    return df


# ---------------------------------------------------------------------------
# Aggregate knowledge generators
# ---------------------------------------------------------------------------

def _price_range_text(values: list[float]) -> str:
    if not values:
        return "No price data available."
    mn = min(values)
    mx = max(values)
    med = statistics.median(values)
    mean = statistics.mean(values)
    return (
        f"Prices range from PHP {mn:,.0f} to PHP {mx:,.0f}. "
        f"Median PHP {med:,.0f}, average PHP {mean:,.0f}. "
        f"Based on {len(values)} product listings."
    )


def build_equipment_cost_knowledge(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Aggregate price knowledge per renewable_type + product_type."""
    docs: list[dict[str, Any]] = []

    for rtype, group in df.groupby("renewable_type"):
        for ptype, subgroup in group.groupby("product_type"):
            if ptype == "":
                continue
            prices = subgroup["price_php"].dropna().tolist()
            if len(prices) < 3:
                continue

            sources = subgroup["source_site"].dropna().unique().tolist()
            note = _currency_note(subgroup["currency"].iloc[0])

            content = (
                f"{rtype.title()} {ptype.replace('_', ' ')} equipment cost: {_price_range_text(prices)} "
                f"Sources: {', '.join(sources)}. {note}"
            ).strip()

            docs.append({
                "renewable_type": rtype,
                "category": "equipment_cost",
                "product_type": ptype,
                "content": content,
                "sources": sources,
            })

    return docs


def build_installation_cost_knowledge(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Derive rough installation-cost knowledge from equipment totals.
    Industry rule-of-thumb:
        solar  -> installation ~30-50 % of equipment cost
        wind   -> installation ~20-40 % of equipment cost (tower + labour)
        hydro  -> installation ~40-70 % of equipment cost (civil works)
    """
    docs: list[dict[str, Any]] = []

    for rtype, group in df.groupby("renewable_type"):
        prices = group["price_php"].dropna().tolist()
        if len(prices) < 5:
            continue

        total_equip = sum(prices)
        avg_equip = statistics.mean(prices)
        med_equip = statistics.median(prices)

        if rtype == "solar":
            ratio_low, ratio_high = 0.30, 0.50
            details = (
                "Residential solar installation typically includes mounting structures, wiring, "
                "inverter installation, labour, permits, and net-metering setup. "
                "Small residential systems (1-2 kWp) may have higher per-watt installation costs."
            )
        elif rtype == "wind":
            ratio_low, ratio_high = 0.20, 0.40
            details = (
                "Wind system installation includes tower erection, foundation, wiring, controller setup, "
                "and safety equipment. Off-grid or hybrid setups may require additional battery integration labour."
            )
        else:  # hydro
            ratio_low, ratio_high = 0.40, 0.70
            details = (
                "Micro-hydro installation involves intake design, penstock laying, civil works for the powerhouse, "
                "electrical connection, and regulatory permits. Head and flow measurements are required beforehand."
            )

        content = (
            f"{rtype.title()} installation cost estimate: "
            f"Based on scraped equipment data, average equipment cost per major component is around PHP {avg_equip:,.0f} "
            f"(median PHP {med_equip:,.0f}). "
            f"Installation is estimated at {int(ratio_low*100)}-{int(ratio_high*100)}% of equipment cost. "
            f"Therefore a typical system installation may add PHP {avg_equip*ratio_low:,.0f} - PHP {avg_equip*ratio_high:,.0f} "
            f"on top of equipment prices. {details}"
        )

        docs.append({
            "renewable_type": rtype,
            "category": "installation_cost",
            "product_type": "system",
            "content": content,
            "sources": ["aggregated_scraped_data"],
        })

    return docs


def build_maintenance_cost_knowledge() -> list[dict[str, Any]]:
    """Explicit knowledge documents for maintenance schedules and costs."""
    return [
        {
            "renewable_type": "solar",
            "category": "maintenance_cost",
            "product_type": "system",
            "content": (
                "Solar maintenance cost: Annual maintenance for residential solar is typically 0.5-1% of "
                "total system cost per year. Key tasks include panel cleaning (2-4 times/year), inverter health checks, "
                "and visual inspection of mounting hardware. Panel lifespan is 20-25 years; inverters usually last 10-15 years "
                "and may need replacement once during system life. Batteries (if off-grid) last 5-10 years depending on cycle depth."
            ),
            "sources": ["industry_standard"],
        },
        {
            "renewable_type": "wind",
            "category": "maintenance_cost",
            "product_type": "system",
            "content": (
                "Wind maintenance cost: Small wind turbines require annual inspection of blades, tower bolts, "
                "and controller electronics. Maintenance is roughly 1-3% of initial system cost per year. "
                "Turbine lifespan is 15-20 years; blades may need replacement or repair after 10 years. "
                "Grease bearings every 6-12 months. Off-grid systems also need battery bank monitoring."
            ),
            "sources": ["industry_standard"],
        },
        {
            "renewable_type": "hydro",
            "category": "maintenance_cost",
            "product_type": "system",
            "content": (
                "Hydro maintenance cost: Micro-hydro systems have low ongoing maintenance if the intake screen is kept clear. "
                "Annual maintenance is roughly 1-2% of system cost. Key tasks: trash-rack cleaning, penstock inspection, "
                "turbine runner checks for cavitation or debris damage, and generator brush replacement. "
                "Turbine lifespan can exceed 25 years; electronic controllers may need replacement after 10-15 years."
            ),
            "sources": ["industry_standard"],
        },
    ]


def build_components_knowledge() -> list[dict[str, Any]]:
    return [
        {
            "renewable_type": "solar",
            "category": "components",
            "product_type": "system",
            "content": (
                "Solar system required components: photovoltaic (PV) panels, DC/AC inverter (string or micro), "
                "mounting structure (roof or ground), DC combiner box, AC disconnect, electrical wiring, "
                "net-metering equipment (if grid-tied), optional battery bank with charge controller (if off-grid). "
                "Residential systems in the Philippines are typically 1-5 kWp."
            ),
            "sources": ["industry_standard"],
        },
        {
            "renewable_type": "wind",
            "category": "components",
            "product_type": "system",
            "content": (
                "Wind system required components: rotor blades, permanent-magnet generator or alternator, "
                "tower (guyed or freestanding), charge controller or grid-tie inverter, dump load (off-grid), "
                "battery bank (off-grid), deep-cycle batteries, wind-direction tail or yaw mechanism, "
                "guy wires and foundation anchors, electrical wiring and disconnects. "
                "Small residential turbines are typically 0.5-10 kW rated."
            ),
            "sources": ["industry_standard"],
        },
        {
            "renewable_type": "hydro",
            "category": "components",
            "product_type": "system",
            "content": (
                "Hydro system required components: intake/weir structure, trash rack, penstock (PVC or steel pipe), "
                "forebay tank with overflow, turbine (Pelton, Francis, or Kaplan depending on head/flow), "
                "generator/alternator, governor or load controller, electrical wiring, powerhouse structure, "
                "tailrace channel, grid-tie inverter or battery charge controller (off-grid). "
                "Micro-hydro systems are typically 0.5-100 kW."
            ),
            "sources": ["industry_standard"],
        },
    ]


def build_capacity_knowledge() -> list[dict[str, Any]]:
    return [
        {
            "renewable_type": "solar",
            "category": "capacity_info",
            "product_type": "system",
            "content": (
                "Solar capacity assumptions: A typical 550 W mono PERC panel produces ~2.0-2.5 kWh/day in the Philippines "
                "depending on location and season. A 2-panel (1.1 kWp) system can generate ~60-80 kWh/month. "
                "Residential installs range from 1-5 kWp. Grid-tied systems can be larger; off-grid sizing depends on battery storage."
            ),
            "sources": ["industry_standard"],
        },
        {
            "renewable_type": "wind",
            "category": "capacity_info",
            "product_type": "system",
            "content": (
                "Wind capacity assumptions: Small wind turbines (0.5-5 kW) need average wind speeds above 4-5 m/s to be viable. "
                "A 1 kW turbine at 5 m/s average generates roughly 100-150 kWh/month depending on capacity factor (15-25%). "
                "Tower height is critical; every doubling of height can increase wind speed by ~10-15%. "
                "Philippine wind resources are strongest in northern Luzon and some coastal areas."
            ),
            "sources": ["industry_standard"],
        },
        {
            "renewable_type": "hydro",
            "category": "capacity_info",
            "product_type": "system",
            "content": (
                "Hydro capacity assumptions: Micro-hydro output depends on head (vertical drop) and flow rate. "
                "Power (kW) ≈ 9.81 × flow (m³/s) × head (m) × system efficiency (0.50-0.70). "
                "A typical micro-hydro site with 10 m head and 0.05 m³/s flow yields ~3-5 kW. "
                "Run-of-river designs are preferred for minimal environmental impact. "
                "Philippine highland municipalities with steep terrain and perennial streams are best suited."
            ),
            "sources": ["industry_standard"],
        },
    ]


def build_comparison_knowledge() -> list[dict[str, Any]]:
    return [
        {
            "renewable_type": "all",
            "category": "comparison",
            "product_type": "system",
            "content": (
                "Solar vs Wind vs Hydro cost comparison (Philippines context): "
                "Solar has the lowest upfront cost per kW installed (PHP ~60,000-80,000/kW) and the widest availability, "
                "but output is reduced during cloudy months (June-October). "
                "Wind requires higher tower costs and good wind resource; upfront cost is PHP ~80,000-120,000/kW; "
                "maintenance is moderate but wind is intermittent. "
                "Hydro has the highest civil-works cost (PHP ~100,000-150,000/kW) but the longest lifespan and most stable output, "
                "provided a suitable stream exists. Solar is usually the safest default for Philippine households; "
                "hydro is best for remote off-grid sites with perennial water; wind is niche and site-specific."
            ),
            "sources": ["industry_standard"],
        },
    ]


def build_pricing_assumptions_knowledge(df: pd.DataFrame) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for rtype, group in df.groupby("renewable_type"):
        sources = group["source_site"].dropna().unique().tolist()
        currencies = group["currency"].dropna().unique().tolist()
        content = (
            f"{rtype.title()} pricing assumptions: Prices were scraped from {', '.join(sources)}. "
            f"Original currencies: {', '.join(currencies)}. "
            f"Non-PHP prices were converted using approximate rates and may differ from current market rates. "
            f"Prices reflect individual component listings, not complete turn-key systems. "
            f"Shipping, import duties, and local taxes are not included."
        )
        docs.append({
            "renewable_type": rtype,
            "category": "pricing_assumptions",
            "product_type": "system",
            "content": content,
            "sources": sources,
        })
    return docs


# ---------------------------------------------------------------------------
# Raw product chunks (for specific equipment queries)
# ---------------------------------------------------------------------------

def build_raw_product_chunks(df: pd.DataFrame, max_per_group: int = 30) -> list[dict[str, Any]]:
    """
    Keep a subset of individual product listings so the RAG can answer
    'What is the cheapest solar panel?' style questions.
    """
    docs: list[dict[str, Any]] = []
    for (rtype, ptype), group in df.groupby(["renewable_type", "product_type"]):
        if ptype == "":
            continue
        subset = group.nsmallest(max_per_group, "price_php")
        for _, row in subset.iterrows():
            content = (
                f"Product: {row['product_name']}. "
                f"Type: {rtype} {ptype}. "
                f"Price: PHP {row['price_php']:,.0f} (original {row['currency']} {row['price_value_num']}). "
                f"Source: {row.get('source_site', '')}. "
                f"URL: {row.get('url', '')}."
            )
            docs.append({
                "renewable_type": rtype,
                "category": "equipment_cost",
                "product_type": ptype,
                "content": content,
                "sources": [str(row.get("source_site", ""))],
            })
    return docs


# ---------------------------------------------------------------------------
# National energy statistics knowledge
# ---------------------------------------------------------------------------

def build_national_energy_knowledge() -> list[dict[str, Any]]:
    """Build knowledge documents from DOE national energy annual data."""
    docs: list[dict[str, Any]] = []
    if not NATIONAL_ENERGY_CSV.exists():
        logger.warning("National energy CSV not found: %s", NATIONAL_ENERGY_CSV)
        return docs

    df = pd.read_csv(NATIONAL_ENERGY_CSV)
    df = df.sort_values("year")

    # Per-year detailed documents
    for _, row in df.iterrows():
        year = int(row["year"])
        content = (
            f"In {year}, the Philippines total electricity consumption was {row['total_consumption_gwh']:,.2f} GWh. "
            f"Residential sector consumed {row['residential_consumption_gwh']:,.2f} GWh, "
            f"commercial {row['commercial_consumption_gwh']:,.2f} GWh, "
            f"industrial {row['industrial_consumption_gwh']:,.2f} GWh, "
            f"others {row['others_consumption_gwh']:,.2f} GWh. "
            f"Total electricity sales were {row['electricity_sales_gwh']:,.2f} GWh with system losses of {row['system_losses_gwh']:,.2f} GWh "
            f"and utilities own use of {row['utilities_own_use_gwh']:,.2f} GWh. "
            f"Peak demand reached {row['total_peak_demand_mw']:,.2f} MW nationally: "
            f"{row['luzon_peak_demand_mw']:,.2f} MW in Luzon, "
            f"{row['visayas_peak_demand_mw']:,.2f} MW in Visayas, "
            f"{row['mindanao_peak_demand_mw']:,.2f} MW in Mindanao. "
            f"Gross generation totaled {row['luzon_generation_gwh'] + row['visayas_generation_gwh'] + row['mindanao_generation_gwh']:,.2f} GWh: "
            f"{row['luzon_generation_gwh']:,.2f} GWh in Luzon, "
            f"{row['visayas_generation_gwh']:,.2f} GWh in Visayas, "
            f"{row['mindanao_generation_gwh']:,.2f} GWh in Mindanao. "
            f"By fuel type: coal {row['coal_generation_gwh']:,.2f} GWh, "
            f"oil-based {row['oil_based_generation_gwh']:,.2f} GWh, "
            f"natural gas {row['natural_gas_generation_gwh']:,.2f} GWh, "
            f"renewable {row['renewable_generation_gwh']:,.2f} GWh. "
            f"Renewable breakdown: geothermal {row['geothermal_generation_gwh']:,.2f} GWh, "
            f"hydro {row['hydro_generation_gwh']:,.2f} GWh, "
            f"biomass {row['biomass_generation_gwh']:,.2f} GWh, "
            f"solar {row['solar_generation_gwh']:,.2f} GWh, "
            f"wind {row['wind_generation_gwh']:,.2f} GWh. "
            f"Installed capacity was {row['total_installed_capacity_mw']:,.2f} MW and dependable capacity {row['total_dependable_capacity_mw']:,.2f} MW."
        )
        docs.append({
            "renewable_type": "general",
            "category": "national_energy_statistics",
            "product_type": "annual_report",
            "content": content,
            "sources": ["DOE national_energy_annual_ready.csv"],
        })

    # Trend documents: year-over-year changes
    for i in range(1, len(df)):
        prev = df.iloc[i - 1]
        curr = df.iloc[i]
        year = int(curr["year"])
        prev_year = int(prev["year"])
        total_change = ((curr["total_consumption_gwh"] - prev["total_consumption_gwh"]) / prev["total_consumption_gwh"] * 100) if prev["total_consumption_gwh"] else 0
        solar_change = ((curr["solar_generation_gwh"] - prev["solar_generation_gwh"]) / prev["solar_generation_gwh"] * 100) if prev["solar_generation_gwh"] else 0
        wind_change = ((curr["wind_generation_gwh"] - prev["wind_generation_gwh"]) / prev["wind_generation_gwh"] * 100) if prev["wind_generation_gwh"] else 0
        peak_change = ((curr["total_peak_demand_mw"] - prev["total_peak_demand_mw"]) / prev["total_peak_demand_mw"] * 100) if prev["total_peak_demand_mw"] else 0
        content = (
            f"From {prev_year} to {year}, total electricity consumption changed by {total_change:+.1f}% "
            f"from {prev['total_consumption_gwh']:,.2f} to {curr['total_consumption_gwh']:,.2f} GWh. "
            f"Peak demand changed by {peak_change:+.1f}% from {prev['total_peak_demand_mw']:,.2f} to {curr['total_peak_demand_mw']:,.2f} MW. "
            f"Solar generation changed by {solar_change:+.1f}% from {prev['solar_generation_gwh']:,.2f} to {curr['solar_generation_gwh']:,.2f} GWh. "
            f"Wind generation changed by {wind_change:+.1f}% from {prev['wind_generation_gwh']:,.2f} to {curr['wind_generation_gwh']:,.2f} GWh. "
            f"Coal generation was {curr['coal_generation_gwh']:,.2f} GWh vs {prev['coal_generation_gwh']:,.2f} GWh previously. "
            f"Renewable generation was {curr['renewable_generation_gwh']:,.2f} GWh vs {prev['renewable_generation_gwh']:,.2f} GWh previously."
        )
        docs.append({
            "renewable_type": "general",
            "category": "national_energy_statistics",
            "product_type": "trend",
            "content": content,
            "sources": ["DOE national_energy_annual_ready.csv"],
        })

    # Long-term summary
    first = df.iloc[0]
    last = df.iloc[-1]
    first_year = int(first["year"])
    last_year = int(last["year"])
    total_growth = ((last["total_consumption_gwh"] - first["total_consumption_gwh"]) / first["total_consumption_gwh"] * 100)
    solar_growth = ((last["solar_generation_gwh"] - first["solar_generation_gwh"]) / first["solar_generation_gwh"] * 100) if first["solar_generation_gwh"] else 0
    wind_growth = ((last["wind_generation_gwh"] - first["wind_generation_gwh"]) / first["wind_generation_gwh"] * 100) if first["wind_generation_gwh"] else 0
    peak_growth = ((last["total_peak_demand_mw"] - first["total_peak_demand_mw"]) / first["total_peak_demand_mw"] * 100)
    content = (
        f"Long-term Philippine energy trends from {first_year} to {last_year}: "
        f"Total electricity consumption grew by {total_growth:.1f}% from {first['total_consumption_gwh']:,.2f} to {last['total_consumption_gwh']:,.2f} GWh. "
        f"Peak demand grew by {peak_growth:.1f}% from {first['total_peak_demand_mw']:,.2f} to {last['total_peak_demand_mw']:,.2f} MW. "
        f"Coal generation grew from {first['coal_generation_gwh']:,.2f} to {last['coal_generation_gwh']:,.2f} GWh. "
        f"Natural gas generation changed from {first['natural_gas_generation_gwh']:,.2f} to {last['natural_gas_generation_gwh']:,.2f} GWh. "
        f"Oil-based generation declined from {first['oil_based_generation_gwh']:,.2f} to {last['oil_based_generation_gwh']:,.2f} GWh. "
        f"Renewable generation grew from {first['renewable_generation_gwh']:,.2f} to {last['renewable_generation_gwh']:,.2f} GWh. "
        f"Solar generation grew by {solar_growth:.1f}% from {first['solar_generation_gwh']:,.2f} to {last['solar_generation_gwh']:,.2f} GWh. "
        f"Wind generation grew by {wind_growth:.1f}% from {first['wind_generation_gwh']:,.2f} to {last['wind_generation_gwh']:,.2f} GWh. "
        f"Installed capacity expanded from {first['total_installed_capacity_mw']:,.2f} to {last['total_installed_capacity_mw']:,.2f} MW."
    )
    docs.append({
        "renewable_type": "general",
        "category": "national_energy_statistics",
        "product_type": "summary",
        "content": content,
        "sources": ["DOE national_energy_annual_ready.csv"],
    })

    logger.info("Built %s national energy knowledge documents", len(docs))
    return docs


# ---------------------------------------------------------------------------
# Municipality climate knowledge
# ---------------------------------------------------------------------------

def _load_municipality_names() -> dict[int, str]:
    """Load municipality_id -> name mapping."""
    name_map: dict[int, str] = {}
    if not MUNICIPALITIES_CSV.exists():
        return name_map
    df = pd.read_csv(MUNICIPALITIES_CSV)
    for _, row in df.iterrows():
        mid = int(row["municipality_id"])
        name_map[mid] = str(row["name"]).strip()
    return name_map


def build_municipality_climate_knowledge(max_docs: int = 2000) -> list[dict[str, Any]]:
    """Build knowledge documents from NASA POWER climate averages per municipality."""
    docs: list[dict[str, Any]] = []
    if not CLIMATE_CSV.exists():
        logger.warning("Climate CSV not found: %s", CLIMATE_CSV)
        return docs

    name_map = _load_municipality_names()
    df = pd.read_csv(CLIMATE_CSV)

    # Sort by municipality_id and limit to avoid overwhelming the index
    df = df.sort_values("municipality_id")
    if len(df) > max_docs:
        # Prioritize diverse climates: sample across wind speed and solar irradiance quartiles
        df["ws_q"] = pd.qcut(df["avg_ws10m"], q=4, labels=False, duplicates="drop")
        df["sol_q"] = pd.qcut(df["avg_allsky_sfc_sw_dwn"], q=4, labels=False, duplicates="drop")
        sampled = df.groupby(["ws_q", "sol_q"]).head(max_docs // 16)
        remaining = max_docs - len(sampled)
        if remaining > 0:
            remaining_ids = df[~df["municipality_id"].isin(sampled["municipality_id"])]["municipality_id"].head(remaining)
            df = pd.concat([sampled, df[df["municipality_id"].isin(remaining_ids)]])
        else:
            df = sampled

    for _, row in df.iterrows():
        mid = int(row["municipality_id"])
        name = name_map.get(mid, f"Municipality {mid}")
        content = (
            f"{name} has an average temperature of {row['avg_t2m']:.1f}°C "
            f"(max {row['avg_t2m_max']:.1f}°C, min {row['avg_t2m_min']:.1f}°C), "
            f"relative humidity of {row['avg_rh2m']:.1f}%, "
            f"average wind speed of {row['avg_ws10m']:.2f} m/s, "
            f"solar irradiance of {row['avg_allsky_sfc_sw_dwn']:.2f} kWh/m²/day, "
            f"and elevation of {row['elevation']:.0f} meters. "
            f"Annual precipitation averages {row['avg_prectotcorr']:.2f} mm/day. "
            f"Surface pressure is {row['avg_surface_pressure']:.2f} kPa and air density {row['avg_rhoa']:.3f} kg/m³. "
            f"Cloud amount averages {row['avg_cloud_amt']:.1f}%."
        )
        docs.append({
            "renewable_type": "general",
            "category": "municipality_climate",
            "product_type": "climate_profile",
            "content": content,
            "sources": ["NASA POWER municipality_climate_averages.csv"],
        })

    # Add a few high-wind and high-solar highlights for better retrieval
    df_all = pd.read_csv(CLIMATE_CSV)
    for label, col, threshold in [("high wind", "avg_ws10m", 5.0), ("high solar", "avg_allsky_sfc_sw_dwn", 5.5)]:
        top = df_all.nlargest(20, col)
        for _, row in top.iterrows():
            mid = int(row["municipality_id"])
            name = name_map.get(mid, f"Municipality {mid}")
            content = (
                f"{name} is a {label} municipality with {col.replace('avg_', '').replace('_', ' ')} "
                f"of {row[col]:.2f}. "
                f"Temperature {row['avg_t2m']:.1f}°C, wind {row['avg_ws10m']:.2f} m/s, "
                f"solar {row['avg_allsky_sfc_sw_dwn']:.2f} kWh/m²/day, elevation {row['elevation']:.0f}m."
            )
            docs.append({
                "renewable_type": "general",
                "category": "municipality_climate",
                "product_type": f"{label}_highlight",
                "content": content,
                "sources": ["NASA POWER municipality_climate_averages.csv"],
            })

    logger.info("Built %s municipality climate knowledge documents", len(docs))
    return docs


# ---------------------------------------------------------------------------
# Terrain / hydropower knowledge
# ---------------------------------------------------------------------------

def build_terrain_knowledge(max_docs: int = 2000) -> list[dict[str, Any]]:
    """Build knowledge documents from municipality terrain metrics."""
    docs: list[dict[str, Any]] = []
    if not TERRAIN_CSV.exists():
        logger.warning("Terrain CSV not found: %s", TERRAIN_CSV)
        return docs

    df = pd.read_csv(TERRAIN_CSV)
    df = df.sort_values("municipality_id")
    if len(df) > max_docs:
        # Prioritize high-hydropower-potential and high-terrain-diversity municipalities
        df["hydro_q"] = pd.qcut(df["hydro_suitability_score"], q=4, labels=False, duplicates="drop")
        sampled = df.groupby("hydro_q").head(max_docs // 4)
        remaining = max_docs - len(sampled)
        if remaining > 0:
            remaining_ids = df[~df["municipality_id"].isin(sampled["municipality_id"])]["municipality_id"].head(remaining)
            df = pd.concat([sampled, df[df["municipality_id"].isin(remaining_ids)]])
        else:
            df = sampled

    for _, row in df.iterrows():
        name = str(row["municipality_name"]).strip()
        province = str(row["province"]).strip()
        content = (
            f"{name} in {province} has terrain characteristics: "
            f"elevation {row['elevation_m']:.0f} m (mean {row['mean_elevation_m']:.1f} m, range {row['elevation_range_m']:.0f} m), "
            f"mean slope {row['mean_slope_deg']:.1f}°, hydraulic head {row['hydraulic_head_m']:.0f} m, "
            f"terrain ruggedness {row['terrain_ruggedness']:.1f}, watershed gradient {row['watershed_gradient']:.4f}, "
            f"runoff potential {row['runoff_potential']:.4f}, gravity flow potential {row['gravity_flow_potential']:.4f}. "
            f"Hydropower suitability score is {row['hydro_suitability_score']:.3f}. "
            f"Estimated hydropower potential is {row['estimated_hydropower_potential_kw']:.2f} kW. "
            f"Slope classification: {row['slope_classification']}. Elevation classification: {row['elevation_classification']}."
        )
        docs.append({
            "renewable_type": "hydro",
            "category": "terrain_metrics",
            "product_type": "terrain_profile",
            "content": content,
            "sources": ["municipality_terrain_metrics.csv"],
        })

    # Add high-hydropower highlights
    df_all = pd.read_csv(TERRAIN_CSV)
    top_hydro = df_all.nlargest(20, "estimated_hydropower_potential_kw")
    for _, row in top_hydro.iterrows():
        name = str(row["municipality_name"]).strip()
        province = str(row["province"]).strip()
        content = (
            f"{name} in {province} is a high-hydropower-potential site with "
            f"estimated capacity of {row['estimated_hydropower_potential_kw']:.2f} kW, "
            f"hydraulic head {row['hydraulic_head_m']:.0f} m, "
            f"mean slope {row['mean_slope_deg']:.1f}°, "
            f"and hydro suitability score {row['hydro_suitability_score']:.3f}."
        )
        docs.append({
            "renewable_type": "hydro",
            "category": "terrain_metrics",
            "product_type": "hydro_highlight",
            "content": content,
            "sources": ["municipality_terrain_metrics.csv"],
        })

    logger.info("Built %s terrain knowledge documents", len(docs))
    return docs


# ---------------------------------------------------------------------------
# Geothermal suitability knowledge (Supabase)
# ---------------------------------------------------------------------------

def build_geothermal_knowledge(max_docs: int = 2000) -> list[dict[str, Any]]:
    """Build knowledge documents from geothermal_suitability table in Supabase."""
    docs: list[dict[str, Any]] = []
    try:
        client = get_supabase_client()
        resp = client.table("geothermal_suitability").select("*").execute()
        rows = resp.data or []
        if not rows:
            logger.warning("No geothermal suitability data found in Supabase")
            return docs

        # Load name maps
        name_map = _load_municipality_names()
        muni_resp = client.table("municipalities").select("municipality_id,province_id,name").execute()
        muni_rows = muni_resp.data or []
        muni_map = {m["municipality_id"]: m for m in muni_rows}

        prov_resp = client.table("provinces").select("province_id,name").execute()
        prov_rows = prov_resp.data or []
        prov_map = {p["province_id"]: p["name"] for p in prov_rows}

        # Sort and limit
        rows = sorted(rows, key=lambda r: r.get("municipality_id", 0))
        if len(rows) > max_docs:
            # Prioritize high-suitability and diverse classifications
            high = [r for r in rows if (r.get("geothermal_score") or 0) > 0.15]
            moderate = [r for r in rows if 0.08 < (r.get("geothermal_score") or 0) <= 0.15]
            low = [r for r in rows if (r.get("geothermal_score") or 0) <= 0.08]
            per_bucket = max_docs // 3
            rows = (high[:per_bucket] + moderate[:per_bucket] + low[:per_bucket])

        for row in rows:
            mid = row.get("municipality_id")
            muni = muni_map.get(mid, {})
            muni_name = muni.get("name") or name_map.get(mid, f"Municipality {mid}")
            prov_name = prov_map.get(muni.get("province_id"), "")

            score = row.get("geothermal_score") or 0
            classification = row.get("classification") or "unknown"
            fault_dist = row.get("fault_distance_km")
            fault_density = row.get("fault_density")
            volcano_dist = row.get("volcano_distance_km")
            heat_flow = row.get("heat_flow_score")
            temp_score = row.get("temperature_score")
            aquifer = row.get("aquifer_score")

            content = (
                f"{muni_name}{' in ' + prov_name if prov_name else ''} has a geothermal suitability score of {score:.3f} "
                f"(classification: {classification}). "
            )
            details = []
            if fault_dist is not None:
                details.append(f"fault distance {fault_dist:.1f} km")
            if fault_density is not None:
                details.append(f"fault density {fault_density:.2f}")
            if volcano_dist is not None:
                details.append(f"volcano distance {volcano_dist:.1f} km")
            if heat_flow is not None:
                details.append(f"heat flow score {heat_flow:.3f}")
            if temp_score is not None:
                details.append(f"temperature score {temp_score:.3f}")
            if aquifer is not None:
                details.append(f"aquifer score {aquifer:.3f}")
            if details:
                content += "Key factors: " + ", ".join(details) + ". "
            content += (
                f"This indicates {'strong' if score > 0.15 else 'moderate' if score > 0.08 else 'limited'} "
                f"potential for geothermal energy development."
            )

            docs.append({
                "renewable_type": "geothermal",
                "category": "geothermal_suitability",
                "product_type": "municipality_profile",
                "content": content,
                "sources": ["Supabase geothermal_suitability"],
            })

        # Add province-level aggregate summaries
        prov_scores: dict[str, list[float]] = {}
        for row in resp.data or []:
            mid = row.get("municipality_id")
            muni = muni_map.get(mid, {})
            prov = prov_map.get(muni.get("province_id"), "")
            if prov:
                prov_scores.setdefault(prov, []).append(row.get("geothermal_score") or 0)

        for prov, scores in prov_scores.items():
            avg = sum(scores) / len(scores)
            content = (
                f"{prov} has an average geothermal suitability score of {avg:.3f} across {len(scores)} municipalities. "
                f"This suggests {'strong' if avg > 0.15 else 'moderate' if avg > 0.08 else 'limited'} "
                f"province-wide geothermal energy potential."
            )
            docs.append({
                "renewable_type": "geothermal",
                "category": "geothermal_suitability",
                "product_type": "province_summary",
                "content": content,
                "sources": ["Supabase geothermal_suitability"],
            })

        logger.info("Built %s geothermal knowledge documents", len(docs))
    except Exception as exc:
        logger.warning("Failed to build geothermal knowledge: %s", exc)

    return docs


# ---------------------------------------------------------------------------
# Hydropower suitability knowledge (Supabase)
# ---------------------------------------------------------------------------

def build_hydropower_suitability_knowledge(max_docs: int = 2000) -> list[dict[str, Any]]:
    """Build knowledge documents from hydropower_suitability table in Supabase."""
    docs: list[dict[str, Any]] = []
    try:
        client = get_supabase_client()
        resp = client.table("hydropower_suitability").select("*").execute()
        rows = resp.data or []
        if not rows:
            logger.warning("No hydropower suitability data found in Supabase")
            return docs

        # Load name maps
        name_map = _load_municipality_names()

        # Sort and limit
        rows = sorted(rows, key=lambda r: r.get("municipality_id", 0))
        if len(rows) > max_docs:
            # Prioritize high-hydro-potential municipalities
            rows.sort(key=lambda r: r.get("hydro_suitability_score") or 0, reverse=True)
            rows = rows[:max_docs]

        for row in rows:
            mid = row.get("municipality_id")
            muni_name = row.get("municipality_name") or name_map.get(mid, f"Municipality {mid}")
            prov_name = row.get("province", "")
            score = row.get("hydro_suitability_score") or 0
            head = row.get("hydraulic_head_m")
            slope = row.get("mean_slope_deg")
            runoff = row.get("runoff_potential")
            gravity = row.get("gravity_flow_potential")
            est_kw = row.get("estimated_hydropower_potential_kw")

            content = (
                f"{muni_name}{' in ' + prov_name if prov_name else ''} has a hydropower suitability score of {score:.3f}. "
            )
            details = []
            if head is not None:
                details.append(f"hydraulic head {head:.0f} m")
            if slope is not None:
                details.append(f"mean slope {slope:.1f}°")
            if runoff is not None:
                details.append(f"runoff potential {runoff:.3f}")
            if gravity is not None:
                details.append(f"gravity flow potential {gravity:.3f}")
            if est_kw is not None:
                details.append(f"estimated capacity {est_kw:.2f} kW")
            if details:
                content += "Terrain characteristics: " + ", ".join(details) + ". "
            content += (
                f"This indicates {'excellent' if score > 0.6 else 'good' if score > 0.4 else 'moderate' if score > 0.2 else 'limited'} "
                f"potential for small-scale hydropower development."
            )

            docs.append({
                "renewable_type": "hydro",
                "category": "hydropower_suitability",
                "product_type": "municipality_profile",
                "content": content,
                "sources": ["Supabase hydropower_suitability"],
            })

        # Add province-level aggregate summaries
        prov_rows: dict[str, list[dict]] = {}
        for row in resp.data or []:
            prov = row.get("province", "").strip()
            if prov:
                prov_rows.setdefault(prov, []).append(row)

        for prov, prov_data in prov_rows.items():
            scores = [r.get("hydro_suitability_score") or 0 for r in prov_data]
            avg = sum(scores) / len(scores)
            capacities = [r.get("estimated_hydropower_potential_kw") or 0 for r in prov_data if r.get("estimated_hydropower_potential_kw")]
            total_cap = sum(capacities)
            content = (
                f"{prov} has an average hydropower suitability score of {avg:.3f} across {len(prov_data)} municipalities. "
            )
            if capacities:
                content += f"Aggregate estimated hydropower capacity is {total_cap:.2f} kW. "
            content += (
                f"This suggests {'excellent' if avg > 0.6 else 'good' if avg > 0.4 else 'moderate' if avg > 0.2 else 'limited'} "
                f"province-wide small-scale hydropower potential."
            )
            docs.append({
                "renewable_type": "hydro",
                "category": "hydropower_suitability",
                "product_type": "province_summary",
                "content": content,
                "sources": ["Supabase hydropower_suitability"],
            })

        logger.info("Built %s hydropower suitability knowledge documents", len(docs))
    except Exception as exc:
        logger.warning("Failed to build hydropower suitability knowledge: %s", exc)

    return docs


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def build_knowledge_base(csv_path: Path = DEFAULT_CSV) -> list[dict[str, Any]]:
    df = load_and_fix_csv(csv_path)
    logger.info("Loaded %s rows after cleaning/fixes", len(df))

    docs: list[dict[str, Any]] = []
    # Product / scraped data
    docs.extend(build_equipment_cost_knowledge(df))
    docs.extend(build_installation_cost_knowledge(df))
    docs.extend(build_maintenance_cost_knowledge())
    docs.extend(build_components_knowledge())
    docs.extend(build_capacity_knowledge())
    docs.extend(build_comparison_knowledge())
    docs.extend(build_pricing_assumptions_knowledge(df))
    docs.extend(build_raw_product_chunks(df))

    # LUMI data sources
    docs.extend(build_national_energy_knowledge())
    docs.extend(build_municipality_climate_knowledge())
    docs.extend(build_terrain_knowledge())
    docs.extend(build_geothermal_knowledge())
    docs.extend(build_hydropower_suitability_knowledge())

    # Deduplicate by content hash
    seen: set[str] = set()
    unique_docs: list[dict[str, Any]] = []
    for d in docs:
        h = hash(d["content"])
        if h not in seen:
            seen.add(h)
            unique_docs.append(d)

    logger.info("Built %s knowledge documents", len(unique_docs))
    return unique_docs


def save_knowledge_base(docs: list[dict[str, Any]], path: Path = KNOWLEDGE_JSON_PATH) -> Path:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    logger.info("Saved knowledge base to %s", path)
    return path


def load_knowledge_base(path: Path = KNOWLEDGE_JSON_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(
            f"Knowledge base not found at {path}. Run build_knowledge_base() first."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    docs = build_knowledge_base()
    save_knowledge_base(docs)
