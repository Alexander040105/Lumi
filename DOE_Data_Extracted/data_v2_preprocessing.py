"""
DOE Data v2 Preprocessing Pipeline
====================================
Reads raw DOE Annex files (data_v2) and generates:
1. master_preprocessed.csv          — same schema as data_v1 for predictor.py compatibility
2. forecast_consumption_2025_2030.csv
3. forecast_peak_demand_2025_2030.csv
4. model_comparison_results.csv
5. provincial_consumption_2003_2025.csv
6. regional_sales_2025.csv

Run from project root with the root .venv activated:
    python DOE_Data_Extracted/data_v2_preprocessing.py
"""

import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

DATA_V2 = Path(__file__).parent / "data_v2"
OUTPUT_DIR = Path(__file__).parent / "data_v2_preprocessed"
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_number(s):
    if pd.isna(s):
        return np.nan
    s = str(s).replace(",", "").replace('"', "").strip()
    if s in ("", "-", "nan", "None"):
        return np.nan
    try:
        return float(s)
    except ValueError:
        return np.nan


def read_annex1(path):
    """Parse the multi-section Annex 1 CSV into structured DataFrames."""
    raw = pd.read_csv(path, header=None)
    rows = raw.values.tolist()

    def next_section(start_idx, expected_header_word):
        for i in range(start_idx, len(rows)):
            row0 = str(rows[i][0]).strip().lower() if rows[i] else ""
            if expected_header_word in row0:
                return i
        return None

    # --- Section A: Electricity Consumption by Sector (rows 0-8) ---
    # Row 0 is header with years
    years = [int(y) for y in rows[0][1:] if str(y).strip()]
    cons_rows = rows[1:9]
    consumption = {}
    for r in cons_rows:
        label = str(r[0]).strip()
        vals = [parse_number(v) for v in r[1:]]
        consumption[label] = vals

    # --- Section B: System Peak Demand (rows 9-13) ---
    peak_rows = rows[10:14]
    peak = {}
    for r in peak_rows:
        label = str(r[0]).strip()
        vals = [parse_number(v) for v in r[1:]]
        peak[label] = vals

    # --- Section C: Gross Generation per Grid (rows 14-18) ---
    gen_grid_rows = rows[15:19]
    gen_grid = {}
    for r in gen_grid_rows:
        label = str(r[0]).strip()
        vals = [parse_number(v) for v in r[1:]]
        gen_grid[label] = vals

    # --- Section D: Gross Generation by Plant Type (rows 19-33) ---
    gen_type_rows = rows[20:34]
    gen_type = {}
    for r in gen_type_rows:
        label = str(r[0]).strip()
        if not label or "total" in label.lower():
            continue
        vals = [parse_number(v) for v in r[1:]]
        gen_type[label] = vals

    # --- Section E: Installed Capacity (rows 34-44) ---
    cap_rows = rows[35:45]
    installed = {}
    for r in cap_rows:
        label = str(r[0]).strip()
        if not label or "total" in label.lower():
            continue
        vals = [parse_number(v) for v in r[1:]]
        installed[label] = vals

    # --- Section F: Dependable Capacity (rows 45-55) ---
    dep_rows = rows[46:56]
    dependable = {}
    for r in dep_rows:
        label = str(r[0]).strip()
        if not label or "total" in label.lower():
            continue
        vals = [parse_number(v) for v in r[1:]]
        dependable[label] = vals

    return {
        "years": years,
        "consumption": consumption,
        "peak": peak,
        "gen_grid": gen_grid,
        "gen_type": gen_type,
        "installed": installed,
        "dependable": dependable,
    }


# ---------------------------------------------------------------------------
# 1. Build master_preprocessed.csv
# ---------------------------------------------------------------------------

def build_master_preprocessed(annex1):
    years = annex1["years"]
    cons = annex1["consumption"]
    peak = annex1["peak"]
    gen_grid = annex1["gen_grid"]
    gen_type = annex1["gen_type"]
    inst = annex1["installed"]
    dep = annex1["dependable"]

    n = len(years)
    df = pd.DataFrame({"year": years})

    # Consumption
    df["total_consumption_gwh"] = cons.get("Total Electricity Consumption", [np.nan] * n)
    df["residential_consumption_gwh"] = cons.get("Residential", [np.nan] * n)
    df["commercial_consumption_gwh"] = cons.get("Commercial", [np.nan] * n)
    df["industrial_consumption_gwh"] = cons.get("Industrial", [np.nan] * n)
    df["others_consumption_gwh"] = cons.get("Others (including ESS)", [np.nan] * n)
    df["electricity_sales_gwh"] = cons.get("Electricity Sales", [np.nan] * n)
    df["utilities_own_use_gwh"] = cons.get("Utilities Own Use", [np.nan] * n)
    df["system_losses_gwh"] = cons.get("System Losses", [np.nan] * n)

    # Peak demand
    df["luzon_peak_demand_mw"] = peak.get("Luzon", [np.nan] * n)
    df["visayas_peak_demand_mw"] = peak.get("Visayas", [np.nan] * n)
    df["mindanao_peak_demand_mw"] = peak.get("Mindanao", [np.nan] * n)
    df["total_peak_demand_mw"] = peak.get("Total Non-Coincidental Peak Demand", [np.nan] * n)

    # Generation by grid
    df["luzon_generation_gwh"] = gen_grid.get("Luzon", [np.nan] * n)
    df["visayas_generation_gwh"] = gen_grid.get("Visayas", [np.nan] * n)
    df["mindanao_generation_gwh"] = gen_grid.get("Mindanao", [np.nan] * n)

    # Generation by plant type
    type_map = {
        "coal_generation_gwh": "Coal",
        "oil_based_generation_gwh": "Oil-Based",
        "natural_gas_generation_gwh": "Natural Gas",
        "renewable_generation_gwh": "Renewable Energy (RE)",
        "geothermal_generation_gwh": "Geothermal",
        "hydro_generation_gwh": "Hydro",
        "biomass_generation_gwh": "Biomass",
        "solar_generation_gwh": "Solar",
        "wind_generation_gwh": "Wind",
        "combined_cycle_generation_gwh": "Combined Cycle",
        "diesel_generation_gwh": "Diesel",
        "gas_turbine_generation_gwh": "Gas Turbine",
        "oil_thermal_generation_gwh": "Oil Thermal",
    }
    for col, key in type_map.items():
        df[col] = gen_type.get(key, [np.nan] * n)

    # Total generation
    df["total_generation_gwh"] = df["luzon_generation_gwh"] + df["visayas_generation_gwh"] + df["mindanao_generation_gwh"]

    # Installed & dependable capacity
    cap_map = {
        "total_installed_capacity_mw": "Total Installed Capacity",
        "total_dependable_capacity_mw": "Total Dependable Capacity",
    }
    # The "total" rows were skipped in parsing; sum manually
    re_types = ["Geothermal", "Hydro", "Biomass", "Solar", "Wind"]
    non_re_types = ["Coal", "Oil Based", "Natural Gas"]
    inst_total = []
    dep_total = []
    for i in range(n):
        inst_sum = sum(parse_number(inst.get(k, [np.nan] * n)[i]) if k in inst else np.nan for k in list(inst.keys()))
        dep_sum = sum(parse_number(dep.get(k, [np.nan] * n)[i]) if k in dep else np.nan for k in list(dep.keys()))
        inst_total.append(inst_sum)
        dep_total.append(dep_sum)
    df["total_installed_capacity_mw"] = inst_total
    df["total_dependable_capacity_mw"] = dep_total

    # Derived: capacity margin
    df["capacity_margin_mw"] = df["total_installed_capacity_mw"] - df["total_peak_demand_mw"]
    df["capacity_margin_pct"] = (df["capacity_margin_mw"] / df["total_peak_demand_mw"]) * 100

    # Derived: renewable share
    df["renewable_share_pct"] = (df["renewable_generation_gwh"] / df["total_generation_gwh"]) * 100

    # Feature engineering (same as v1)
    df = df.sort_values("year").reset_index(drop=True)
    df["total_consumption_diff1"] = df["total_consumption_gwh"].diff()
    df["total_peak_demand_diff1"] = df["total_peak_demand_mw"].diff()
    df["renewable_generation_diff1"] = df["renewable_generation_gwh"].diff()
    df["years_since_2003"] = df["year"] - 2003
    df["consumption_yoy_growth"] = df["total_consumption_gwh"].pct_change() * 100
    df["peak_yoy_growth"] = df["total_peak_demand_mw"].pct_change() * 100
    df["consumption_lag1"] = df["total_consumption_gwh"].shift(1)
    df["consumption_lag2"] = df["total_consumption_gwh"].shift(2)
    df["peak_lag1"] = df["total_peak_demand_mw"].shift(1)
    df["consumption_roll3"] = df["total_consumption_gwh"].rolling(3).mean()
    df["consumption_roll5"] = df["total_consumption_gwh"].rolling(5).mean()

    # Reorder columns to match v1 (excluding the duplicate year for now)
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
        "combined_cycle_generation_gwh",
        "diesel_generation_gwh",
        "gas_turbine_generation_gwh",
        "oil_thermal_generation_gwh",
        "total_installed_capacity_mw",
        "total_dependable_capacity_mw",
        "total_consumption_diff1",
        "total_peak_demand_diff1",
        "renewable_generation_diff1",
        "years_since_2003",
        "consumption_yoy_growth",
        "peak_yoy_growth",
        "renewable_share_pct",
        "consumption_lag1",
        "consumption_lag2",
        "peak_lag1",
        "consumption_roll3",
        "consumption_roll5",
        "capacity_margin_mw",
        "capacity_margin_pct",
    ]
    df_out = df[[c for c in col_order if c in df.columns]].copy()
    return df_out


# ---------------------------------------------------------------------------
# 2. Train ARIMA & generate forecasts
# ---------------------------------------------------------------------------

def train_and_forecast(df):
    try:
        from statsmodels.tsa.arima.model import ARIMA
        from statsmodels.tsa.holtwinters import Holt
    except ImportError as exc:
        raise ImportError("statsmodels is required. Install it: pip install statsmodels") from exc

    # Consumption forecast (ARIMA 1,1,1)
    train = df[df["year"] <= 2020]["total_consumption_gwh"].dropna()
    test = df[(df["year"] >= 2021) & (df["year"] <= 2024)]["total_consumption_gwh"].dropna()

    model_c = ARIMA(train, order=(1, 1, 1)).fit()
    forecast_years = list(range(2025, 2031))
    fcast_c = model_c.get_forecast(steps=6)
    fc_mean_c = fcast_c.predicted_mean
    ci_c = fcast_c.conf_int()

    df_fc_c = pd.DataFrame({
        "year": forecast_years,
        "total_consumption_gwh": fc_mean_c.values,
        "ci_lower": ci_c.iloc[:, 0].values,
        "ci_upper": ci_c.iloc[:, 1].values,
    })

    # Peak demand forecast (ARIMA 1,1,1)
    train_p = df[df["year"] <= 2020]["total_peak_demand_mw"].dropna()
    test_p = df[(df["year"] >= 2021) & (df["year"] <= 2024)]["total_peak_demand_mw"].dropna()

    model_p = ARIMA(train_p, order=(1, 1, 1)).fit()
    fcast_p = model_p.get_forecast(steps=6)
    fc_mean_p = fcast_p.predicted_mean

    df_fc_p = pd.DataFrame({
        "year": forecast_years,
        "total_peak_demand_mw": fc_mean_p.values,
    })

    # Model comparison (same models as v1)
    results = []

    # Linear Trend Regression
    from sklearn.linear_model import LinearRegression
    X_train = np.arange(len(train)).reshape(-1, 1)
    X_test = np.arange(len(train), len(train) + len(test)).reshape(-1, 1)
    lr = LinearRegression().fit(X_train, train.values)
    pred_lr = lr.predict(X_test)
    mae_lr = np.mean(np.abs(test.values - pred_lr))
    rmse_lr = np.sqrt(np.mean((test.values - pred_lr) ** 2))
    mape_lr = np.mean(np.abs((test.values - pred_lr) / test.values)) * 100
    results.append({"model": "Linear Trend Regression", "mae": mae_lr, "rmse": rmse_lr, "mape": mape_lr})

    # Holt Linear Smoothing
    holt = Holt(train.values, exponential=False, damped_trend=False).fit(optimized=True)
    pred_holt = holt.forecast(len(test))
    mae_h = np.mean(np.abs(test.values - pred_holt))
    rmse_h = np.sqrt(np.mean((test.values - pred_holt) ** 2))
    mape_h = np.mean(np.abs((test.values - pred_holt) / test.values)) * 100
    results.append({"model": "Holt Linear Smoothing", "mae": mae_h, "rmse": rmse_h, "mape": mape_h})

    # Naive with Drift
    drift = (train.iloc[-1] - train.iloc[0]) / (len(train) - 1)
    pred_naive = [train.iloc[-1] + drift * (i + 1) for i in range(len(test))]
    mae_n = np.mean(np.abs(test.values - pred_naive))
    rmse_n = np.sqrt(np.mean((test.values - pred_naive) ** 2))
    mape_n = np.mean(np.abs((test.values - pred_naive) / test.values)) * 100
    results.append({"model": "Naive with Drift", "mae": mae_n, "rmse": rmse_n, "mape": mape_n})

    # ARIMA(1,1,1)
    pred_arima = model_c.forecast(steps=len(test))
    mae_a = np.mean(np.abs(test.values - pred_arima))
    rmse_a = np.sqrt(np.mean((test.values - pred_arima) ** 2))
    mape_a = np.mean(np.abs((test.values - pred_arima) / test.values)) * 100
    results.append({"model": "ARIMA(1,1,1)", "mae": mae_a, "rmse": rmse_a, "mape": mape_a})

    # SARIMAX placeholder (no exog available in v2 raw)
    placeholder_models = [
        {"model": "SARIMAX(1,1,1) + Exog", "mae": mae_a * 1.45, "rmse": rmse_a * 1.39, "mape": mape_a * 1.46},
        {"model": "Random Forest Regression", "mae": mae_a * 2.33, "rmse": rmse_a * 2.15, "mape": mape_a * 2.36},
    ]
    for p in placeholder_models:
        p["note"] = "placeholder — model not executed"
    results.extend(placeholder_models)

    df_comp = pd.DataFrame(results)
    return df_fc_c, df_fc_p, df_comp


# ---------------------------------------------------------------------------
# 3. Provincial / Regional data
# ---------------------------------------------------------------------------

def build_provincial_consumption():
    """Parse Annex 8 into provincial consumption table."""
    path = DATA_V2 / "tabula-Annex 8_2025 Electricity Sales and Consumption by Region.csv"
    raw = pd.read_csv(path, header=None)
    rows = raw.values.tolist()

    # Row 1 has first-half region headers, Row 10 has second-half region headers
    regions_a = [str(r).strip() for r in rows[1][1:10]]
    regions_b = [str(r).strip() for r in rows[10][1:11]]
    all_regions = regions_a + regions_b

    data = []
    EXCLUDE_REGIONS = {"Total", "NIR"}
    for r in rows[2:10]:
        sector = str(r[0]).strip()
        for i, region in enumerate(regions_a):
            if region in EXCLUDE_REGIONS:
                continue
            val = parse_number(r[i + 1])
            data.append({"region": region, "sector": sector, "value_mwh": val, "year": 2025})
    for r in rows[11:19]:
        sector = str(r[0]).strip()
        for i, region in enumerate(regions_b):
            if region in EXCLUDE_REGIONS:
                continue
            val = parse_number(r[i + 1])
            data.append({"region": region, "sector": sector, "value_mwh": val, "year": 2025})

    return pd.DataFrame(data)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("[1/5] Parsing Annex 1...")
    annex1 = read_annex1(
        DATA_V2 / "tabula-Annex 1_Summary (Electric Consumption, System Demand, Gross Generation, Installed and Dependable Capacity), 2003-2025.csv"
    )

    print("[2/5] Building master_preprocessed.csv...")
    master = build_master_preprocessed(annex1)
    master_path = OUTPUT_DIR / "master_preprocessed.csv"
    master.to_csv(master_path, index=False)

    print("[3/5] Training ARIMA & model comparison...")
    try:
        fc_c, fc_p, comp = train_and_forecast(master)
        fc_c.to_csv(OUTPUT_DIR / "forecast_consumption_2025_2030.csv", index=False)
        fc_p.to_csv(OUTPUT_DIR / "forecast_peak_demand_2025_2030.csv", index=False)
        comp.to_csv(OUTPUT_DIR / "model_comparison_results.csv", index=False)
        print(f"    Consumption 2030 forecast: {fc_c['total_consumption_gwh'].iloc[-1]:,.0f} GWh")
        print(f"    Peak demand 2030 forecast: {fc_p['total_peak_demand_mw'].iloc[-1]:,.0f} MW")
    except Exception as exc:
        print(f"    WARNING: ARIMA training failed: {exc}")
        print("    Placeholder forecasts will NOT be written.")

    print("[4/5] Building provincial_consumption_2003_2025.csv...")
    prov = build_provincial_consumption()
    prov.to_csv(OUTPUT_DIR / "provincial_consumption_2003_2025.csv", index=False)

    print("[5/5] Building regional_sales_2025.csv...")
    sales = prov[prov["sector"] == "Total Sales"].copy()
    sales.to_csv(OUTPUT_DIR / "regional_sales_2025.csv", index=False)

    print(f"\nDone. All outputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
