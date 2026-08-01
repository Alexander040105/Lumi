"""
prepare_national_energy_csv.py
==============================
Combines all 6 DOE extracted CSVs into a single clean CSV
matching the `national_energy_annual` Supabase schema.
Uses only the Python standard library (no pandas dependency).

Output: DOE_Data_Extracted/national_energy_annual_ready.csv
"""

import csv
import math
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "DOE_Data_Extracted"
OUTPUT_FILE = INPUT_DIR / "national_energy_annual_ready.csv"


def read_wide_csv(filename: str) -> dict:
    """Read a DOE CSV where rows=categories and columns=years.
    Returns {category: {year: value}}"""
    filepath = INPUT_DIR / filename
    result = {}
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        years = [int(h) for h in header[1:]]
        for row in reader:
            if not row or all(cell.strip() == "" for cell in row):
                continue
            category = row[0].strip()
            result[category] = {}
            for year_str, val_str in zip(years, row[1:]):
                val_str = val_str.strip()
                if val_str == "":
                    result[category][year_str] = None
                else:
                    result[category][year_str] = float(val_str)
    return result


def safe_get(data: dict, category: str, year: int) -> float | None:
    """Safely retrieve a value from the nested dict."""
    cat_data = data.get(category, {})
    return cat_data.get(year)


def build_energy_table() -> list[dict]:
    years = list(range(2003, 2025))

    # Read all 6 source files
    cons = read_wide_csv("electricity_consumption_by_sector_GWh.csv")
    peak = read_wide_csv("system_peak_demand_MW.csv")
    gen_grid = read_wide_csv("gross_power_generation_by_grid_GWh.csv")
    gen_plant = read_wide_csv("gross_power_generation_by_plant_type_GWh.csv")
    cap = read_wide_csv("installed_capacity_by_plant_type_MW.csv")
    dep = read_wide_csv("dependable_capacity_by_plant_type_MW.csv")

    records = []
    for year in years:
        row: dict[str, float | int | None] = {"year": year}

        # ---- Consumption ----
        row["total_consumption_gwh"] = safe_get(cons, "Total Electricity Consumption", year)
        row["residential_consumption_gwh"] = safe_get(cons, "Residential", year)
        row["commercial_consumption_gwh"] = safe_get(cons, "Commercial", year)
        row["industrial_consumption_gwh"] = safe_get(cons, "Industrial", year)
        row["others_consumption_gwh"] = safe_get(cons, "Others", year)
        row["electricity_sales_gwh"] = safe_get(cons, "Electricity Sales", year)
        row["utilities_own_use_gwh"] = safe_get(cons, "Utilities Own Use", year)
        row["system_losses_gwh"] = safe_get(cons, "System Losses", year)

        # ---- Peak Demand ----
        row["luzon_peak_demand_mw"] = safe_get(peak, "Luzon", year)
        row["visayas_peak_demand_mw"] = safe_get(peak, "Visayas", year)
        row["mindanao_peak_demand_mw"] = safe_get(peak, "Mindanao", year)
        row["total_peak_demand_mw"] = safe_get(peak, "Total Non-Coincident Peak Demand", year)

        # ---- Generation by Grid ----
        row["luzon_generation_gwh"] = safe_get(gen_grid, "Luzon", year)
        row["visayas_generation_gwh"] = safe_get(gen_grid, "Visayas", year)
        row["mindanao_generation_gwh"] = safe_get(gen_grid, "Mindanao", year)

        # ---- Generation by Plant Type ----
        row["coal_generation_gwh"] = safe_get(gen_plant, "Coal", year)
        row["natural_gas_generation_gwh"] = safe_get(gen_plant, "Natural Gas", year)
        row["renewable_generation_gwh"] = safe_get(gen_plant, "Renewable Energy (RE)", year)
        row["geothermal_generation_gwh"] = safe_get(gen_plant, "Geothermal", year)
        row["hydro_generation_gwh"] = safe_get(gen_plant, "Hydro", year)
        row["biomass_generation_gwh"] = safe_get(gen_plant, "Biomass", year)
        row["solar_generation_gwh"] = safe_get(gen_plant, "Solar", year)
        row["wind_generation_gwh"] = safe_get(gen_plant, "Wind", year)

        # Oil-based = Oil-Based + Combined Cycle + Diesel + Gas Turbine + Oil Thermal
        oil_subs = ["Oil-Based", "Combined Cycle", "Diesel", "Gas Turbine", "Oil Thermal"]
        oil_sum = 0.0
        has_oil = False
        for sub in oil_subs:
            v = safe_get(gen_plant, sub, year)
            if v is not None:
                oil_sum += v
                has_oil = True
        row["oil_based_generation_gwh"] = round(oil_sum, 2) if has_oil else None

        # ---- Capacity ----
        row["total_installed_capacity_mw"] = safe_get(cap, "Total Installed Capacity", year)
        row["total_dependable_capacity_mw"] = safe_get(dep, "Total Dependable Capacity", year)

        records.append(row)

    return records


def validate_data(records: list[dict]) -> None:
    """Run sanity checks on the combined dataset."""
    print("\n=== DATA VALIDATION ===")

    # Check all years present
    expected_years = set(range(2003, 2025))
    found_years = {r["year"] for r in records}
    missing = expected_years - found_years
    if missing:
        print(f"  [WARN] Missing years: {sorted(missing)}")
    else:
        print("  [OK] All 22 years (2003-2024) present")

    # Check total consumption = sales + own_use + losses
    mismatches = 0
    for r in records:
        total = r["total_consumption_gwh"] or 0
        sales = r["electricity_sales_gwh"] or 0
        own_use = r["utilities_own_use_gwh"] or 0
        losses = r["system_losses_gwh"] or 0
        diff = abs(total - (sales + own_use + losses))
        if diff > 1:
            mismatches += 1
            if mismatches <= 3:
                print(f"  [WARN] {r['year']}: total={total:.2f} vs computed={sales+own_use+losses:.2f} (diff={diff:.2f})")
    if mismatches == 0:
        print("  [OK] total_consumption_gwh == sales + own_use + losses")
    else:
        print(f"  [WARN] {mismatches} years with consumption mismatch")

    # Check peak demand = Luzon + Visayas + Mindanao
    mismatches = 0
    for r in records:
        total = r["total_peak_demand_mw"] or 0
        luzon = r["luzon_peak_demand_mw"] or 0
        vis = r["visayas_peak_demand_mw"] or 0
        mind = r["mindanao_peak_demand_mw"] or 0
        diff = abs(total - (luzon + vis + mind))
        if diff > 1:
            mismatches += 1
            if mismatches <= 3:
                print(f"  [WARN] {r['year']}: total_peak={total:.2f} vs computed={luzon+vis+mind:.2f}")
    if mismatches == 0:
        print("  [OK] total_peak_demand_mw == Luzon + Visayas + Mindanao")
    else:
        print(f"  [WARN] {mismatches} years with peak demand mismatch")

    # Check generation: coal + oil + gas + RE  vs grid total
    mismatches = 0
    for r in records:
        coal = r["coal_generation_gwh"] or 0
        oil = r["oil_based_generation_gwh"] or 0
        gas = r["natural_gas_generation_gwh"] or 0
        re = r["renewable_generation_gwh"] or 0
        plant_total = coal + oil + gas + re

        luzon = r["luzon_generation_gwh"] or 0
        vis = r["visayas_generation_gwh"] or 0
        mind = r["mindanao_generation_gwh"] or 0
        grid_total = luzon + vis + mind

        diff = abs(grid_total - plant_total)
        if diff > 1:
            mismatches += 1
            if mismatches <= 3:
                print(f"  [WARN] {r['year']}: grid_sum={grid_total:.2f} vs plant_sum={plant_total:.2f}")
    if mismatches == 0:
        print("  [OK] Grid generation totals match plant type sums")
    else:
        print(f"  [WARN] {mismatches} years with generation mismatch")

    # Null counts
    print("\n  [INFO] Null value counts per column:")
    all_cols = list(records[0].keys())
    for col in all_cols:
        nulls = sum(1 for r in records if r[col] is None)
        if nulls > 0:
            print(f"      {col}: {nulls} nulls")

    print("\n=== END VALIDATION ===\n")


def write_csv(records: list[dict]) -> None:
    """Write records to CSV matching the Supabase schema column order."""
    col_order = [
        "year",
        "total_consumption_gwh",
        "residential_consumption_gwh",
        "commercial_consumption_gwh",
        "industrial_consumption_gwh",
        "others_consumption_gwh",
        "electricity_sales_gwh",
        "utilities_own_use_gwh",
        "system_losses_gwh",
        "luzon_peak_demand_mw",
        "visayas_peak_demand_mw",
        "mindanao_peak_demand_mw",
        "total_peak_demand_mw",
        "luzon_generation_gwh",
        "visayas_generation_gwh",
        "mindanao_generation_gwh",
        "coal_generation_gwh",
        "oil_based_generation_gwh",
        "natural_gas_generation_gwh",
        "renewable_generation_gwh",
        "geothermal_generation_gwh",
        "hydro_generation_gwh",
        "biomass_generation_gwh",
        "solar_generation_gwh",
        "wind_generation_gwh",
        "total_installed_capacity_mw",
        "total_dependable_capacity_mw",
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=col_order)
        writer.writeheader()
        for row in records:
            # Round floats to 2 decimals, leave None as empty string
            clean_row = {}
            for col in col_order:
                val = row.get(col)
                if val is None:
                    clean_row[col] = ""
                elif isinstance(val, float):
                    clean_row[col] = f"{val:.2f}"
                else:
                    clean_row[col] = val
            writer.writerow(clean_row)


def print_preview(records: list[dict], n: int = 5) -> None:
    """Print first and last n rows in a readable format."""
    col_order = list(records[0].keys())

    def fmt_row(r):
        return " | ".join(f"{c}={r[c] if r[c] is not None else 'NULL':>12}" for c in col_order)

    print(f"\nPreview (first {n} rows):")
    for r in records[:n]:
        print("  " + fmt_row(r))
    print(f"\nPreview (last {n} rows):")
    for r in records[-n:]:
        print("  " + fmt_row(r))


def main():
    print("Building national_energy_annual dataset from DOE CSVs...")

    records = build_energy_table()
    validate_data(records)
    write_csv(records)

    print(f"Saved to: {OUTPUT_FILE}")
    print(f"Shape: {len(records)} rows x {len(records[0])} columns")
    print_preview(records)


if __name__ == "__main__":
    main()
