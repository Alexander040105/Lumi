# LUMI Forecasting Module — Data Sources & Acquisition Guide

## What the Forecasting Module Is Trying to Predict

Based on `LUMI_TECH_RECOMMENDATIONS.md` and the system thesis objectives, the **Forecasting Module** (`/forecasting` page, `forecast_service.py`) is responsible for:

| Prediction Task | Description |
|---|---|
| **Future energy consumption** | Monthly or seasonal electricity consumption (kWh / MWh) per region or municipality |
| **Energy demand trends** | Direction and magnitude of demand growth/decline over 1–12 month horizons |
| **Possible energy shortages** | Alerts when forecasted demand approaches or exceeds estimated supply capacity |
| **Peak demand timing** | When peak load is expected (critical for grid planning and renewable sizing) |

**How it works in the UI:** The user selects a **region** and a **forecast model** (e.g., ARIMA, Prophet). The backend returns a **forecast time series + confidence bands**, visualized as a line chart, plus an AI-generated trend explanation.

**The core target variable:** `monthly_energy_consumption_mwh` (or `kwh`) at the **region or municipality level**.

---

## Your Current Data Gap

You already have excellent **climate covariates** (NASA POWER monthly data for ~1,600 municipalities) and **terrain data** for Ecosim. However:

**You have ZERO historical energy consumption or demand data in your schema.**

- `municipality_climate_monthly` = climate drivers (temperature, irradiance, wind, rainfall)
- `hydropower_suitability` = static terrain features
- `deptOfEnergyDataset.csv` = **electricity rates** (peso/kWh), **not consumption volume**

To train any forecasting model, you need a **target variable**: historical energy consumption or demand per region/municipality over time.

---

## Recommended Data Sources (with Direct Links)

### 1. DOE Philippine Power Statistics — Primary Source

The Department of Energy publishes annual power statistics with historical time-series data going back to **2003**.

**What you can get:**
- Electricity Sales and Consumption per Grid and per Sector (2003–2024)
- System Peak Demand per Grid (2001–2024)
- Gross Generation per Grid and per Technology (2003–2024)
- Monthly Electricity Sales and Power Consumption Data (2024)

**Direct links:**
- **Main portal:** https://doe.gov.ph/site/epimb/articles/group/statistics?category=Philippine+Power+Statistics&display_type=Card
- **2024 Power Statistics bundle:** https://doe.gov.ph/articles/2764665--2024-power-statistics
- **Electricity Sales & Consumption (2003–2024 PDF):** https://prod-cms.doe.gov.ph/documents/d/guest/06_electricity-consumption-pdf
- **2024 Monthly Sales & Consumption Data:** https://prod-cms.doe.gov.ph/documents/d/guest/10_2024-monthly-e-sales-and-power-consumption-data-pdf
- **System Peak Demand (2001–2024 PDF):** https://prod-cms.doe.gov.ph/documents/d/guest/07_system-peak-demand-pdf
- **Consumption by Region (2024 PDF):** https://prod-cms.doe.gov.ph/documents/d/guest/09_e-sales-and-consumption-per-region-pdf
- **Gross Generation by Technology (2003–2024 PDF):** https://prod-cms.doe.gov.ph/documents/d/guest/04_gross-generation-pdf

> **Note:** These are PDF reports. You will need to manually extract tables (copy-paste or use a PDF table extractor like **Tabula** or **Camelot**) into CSV. This is realistic for a thesis project.

---

### 2. PSA OpenStat — Energy Database

The Philippine Statistics Authority maintains an online energy database with regional-level electricity data.

**What you can get:**
- Regional electricity consumption statistics
- Sectoral breakdowns (residential, commercial, industrial)
- Historical trends aligned with census years

**Direct link:**
- **PSA OpenStat Energy:** https://openstat.psa.gov.ph/Database/Energy

---

### 3. FOI Philippines — DOE Monthly Regional Consumption

A Freedom of Information request result contains the **2025 monthly regional electricity consumption dataset**, which may include downloadable CSV or Excel formats.

**Direct link:**
- **2025 Monthly Regional Electricity Consumption:** https://www.foi.gov.ph/agencies/doe/2025-monthly-regional-electricity-consumption-dataset-for-the-philippines/

---

### 4. NGCP Operations Data

The National Grid Corporation of the Philippines publishes operations data including peak demand and grid generation.

**What you can get:**
- Peak demand forecasts and actuals
- LUZON-VISAYAS-MINDANAO (LVM) grid operations
- Weekly operating margin reports

**Direct link:**
- **NGCP Operations:** https://www.ngcp.ph/operations

---

### 5. World Bank Open Data — Philippines Energy Indicators

Useful for macro-level trend validation and cross-checking your regional forecasts.

**What you can get:**
- National electricity consumption per capita
- Energy intensity, access rates, CO2 intensity
- Annual data (good for long-term trend context)

**Direct link:**
- **World Bank Energy Indicators:** https://data.worldbank.org/indicator/EG.ELC.ACCS.ZS?locations=PH

---

### 6. PAGASA Historical Weather Data (Optional Enhancement)

NASA POWER is already in your schema, but PAGASA provides ground-truth station data for key cities, which can improve forecast accuracy for temperature-driven demand (e.g., cooling degree days).

**Direct link:**
- **PAGASA Climate Data:** https://www.pagasa.dost.gov.ph/climate/climate-data

---

## Suggested Data Acquisition Strategy

| Step | Action | Output |
|---|---|---|
| **1** | Download DOE "Electricity Sales and Consumption per Grid and per Sector" PDFs (2021–2024) | Raw consumption tables |
| **2** | Extract tables from PDFs using **Tabula** (free, open-source) | `doe_consumption_by_region.csv` |
| **3** | Download DOE "System Peak Demand" PDFs | `doe_peak_demand.csv` |
| **4** | Cross-reference with `regions` table in your schema to map DOE grid regions to your 17 Philippine regions | Linked dataset |
| **5** | Ingest into a new table: `region_energy_monthly` (year, month, region_id, total_mwh, residential_mwh, commercial_mwh, industrial_mwh, peak_mw) | ML-ready target variable |
| **6** | (Optional) Request PSA OpenStat bulk download or email DOE EPIMB at `epimb.ppdd@doe.gov.ph` for Excel/CSV versions | Cleaner data |

---

## Bottom Line

Your Forecasting Module is trying to predict **regional/municipal electricity consumption and peak demand trends** 1–12 months ahead. Right now, you have all the **feature data** (climate, terrain, geography) but none of the **target data** (historical consumption). The **DOE Power Statistics PDFs** are your best and most authoritative source. Extract them into CSV, load them into a new `region_energy_monthly` table, and your schema will finally support supervised forecasting.

---

*Document generated: June 2026*
