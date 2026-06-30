# LUMI Thesis — Panelist Revisions & New Dataset Integration Master Document

## Executive Summary

This document consolidates **all 8 panelist revisions** (Phases 1–8) and the **new free dataset integration** (IRENA, Meralco rates, Global Solar Atlas, Global Wind Atlas) implemented for the LUMI thesis. Each revision addresses specific panelist feedback with concrete code changes, data pipelines, and frontend updates.

---

## Phase 1: DOE Data v2 Migration

**Panelist Feedback:** "Use the most recent DOE data and ensure backward compatibility."

**What was done:**
- Created `DOE_Data_Extracted/data_v2_preprocessing.py` to parse DOE Annex 1 (national statistics) and Annex 8 (provincial/regional data).
- Generated `master_preprocessed.csv` matching the v1 schema (including the duplicate `year` column for backward compatibility).
- Trained ARIMA(1,1,1) models for consumption and peak demand forecasting.
- Output forecast CSVs: `forecast_consumption_2025_2030.csv`, `forecast_peak_demand_2025_2030.csv`.
- Output model comparison: `model_comparison_results.csv`.
- Updated `predictor.py` to preferentially load from `data_v2_preprocessed/` with fallback to `data_v1/`.

**Files created/modified:**
- `@DOE_Data_Extracted/data_v2_preprocessing.py`
- `@fastapi-backend/app/ml/predictor.py`

---

## Phase 2: EcoSim Province/Municipality Mode

**Panelist Feedback:** "Allow analysis at the province level, not just municipality."

**What was done:**
- Added `mode` parameter (`"municipality"` | `"province"`) to EcoSim GET/POST endpoints.
- Created `list_provinces()` and `get_province_data()` in `ecosim.py`.
- Province mode aggregates climate and terrain data from all municipalities in the province.
- Frontend added radio toggle between municipality and province with conditional dropdowns.
- Added `get_province_name_by_id()` for proper name resolution in province mode.

**New API endpoints:**
- `GET /ecosim/provinces`
- `GET /ecosim/?mode=province`
- `POST /ecosim/ { mode: "province" }`

**Files created/modified:**
- `@fastapi-backend/app/services/ecosim.py`
- `@fastapi-backend/app/routes/ecosim.py`
- `@fastapi-backend/app/schemas/ecosim.py`
- `@react-frontend/src/pages/Ecosim.jsx`
- `@react-frontend/src/services/apiClient.js`

---

## Phase 3: Provincial & Municipal Energy Demand

**Panelist Feedback:** "Show provincial energy demand and estimate municipal-level demand."

**What was done:**
- Added `GET /energyhub/provincial-demand` endpoint returning DOE Annex 8 regional consumption breakdown.
- Added `GET /energyhub/municipal-demand/{province_id}` endpoint for population-weighted disaggregation.
- Formula: `D_muni = D_prov * (P_muni / P_prov)` using PSA population ratios.
- Created `municipal_population.sql` Supabase table schema for PSA 2020 Census data.
- Added `ProvincialDemand.jsx` bar chart component to EnergyHub frontend.
- Graceful fallback when PSA population data is not yet loaded.

**Files created/modified:**
- `@fastapi-backend/app/services/energyhub.py`
- `@fastapi-backend/app/routes/energyhub.py`
- `@fastapi-backend/app/schemas/energyhub.py`
- `@react-frontend/src/components/energyhub/ProvincialDemand.jsx`
- `@supabase_tables_scripts/municipal_population.sql`

---

## Phase 4: EnergyHub UX Redesign

**Panelist Feedback:** "Charts need explanation — users don't understand what they mean."

**What was done:**
- Created reusable `ChartExplanation` component with **What / Why / Action** format.
- Added explanations to every EnergyHub visualization:
  - **Consumption trend:** "What: Historical vs forecast... Why: Growth signals investment opportunities... Action: Consider solar/wind ahead of peak strain..."
  - **Peak demand:** "What: Highest recorded demand... Why: Rising peaks need reliable capacity... Action: Prioritize distributed solar or battery storage..."
  - **Renewable generation:** "What: Total RE generation by year... Why: Rising share = successful policy... Action: Advocate for local RE if your province lags..."
  - **Source breakdown:** "What: Share by plant type... Why: High fossil = carbon + price risk... Action: Push for local solar/wind adoption..."

**Files created/modified:**
- `@react-frontend/src/components/energyhub/ChartExplanation.jsx`
- `@react-frontend/src/components/energyhub/EnergyTrends.jsx`
- `@react-frontend/src/components/energyhub/EnergySources.jsx`

---

## Phase 5: Product Recommendations

**Panelist Feedback:** "EcoSim should recommend actual products, not just generic sources."

**What was done:**
- Created `products.py` service reading `cleaned_products_master.csv`.
- Fixed hydro products misclassified as "wind" using source_file hints.
- Added `/products/recommend?energy_type=solar&budget_php=50000` endpoint.
- Added `/products/browse` with filters and pagination.
- Added `/products/audit` for data quality reporting.
- Integrated product cards into EcoSim results inline (shows 4 products for the recommended source).
- Transparent note: "Prices converted from USD using PHP 56 = 1 USD. Links may be outdated."

**Files created/modified:**
- `@fastapi-backend/app/services/products.py`
- `@fastapi-backend/app/routes/products.py`
- `@fastapi-backend/app/schemas/products.py`
- `@fastapi-backend/app/routes/api.py`
- `@react-frontend/src/services/apiClient.js`
- `@react-frontend/src/pages/Ecosim.jsx`

---

## Phase 6: Data Improvement Audit & Free Sources

**Panelist Feedback:** "Document where your data comes from and what free alternatives exist."

**What was done:**
- Created `FREE_ALTERNATIVE_DATA.md` cataloging 10 free data sources:
  1. DOE (Philippines) — primary source
  2. PSA (population, economic indicators)
  3. NASA POWER (climate data)
  4. Global Wind Atlas (wind resource maps)
  5. Global Solar Atlas (solar resource maps)
  6. OpenStreetMap (building footprints)
  7. Philippine Power Statistics (DOE annual reports)
  8. MERALCO/ERC (tariff schedules)
  9. Climate Change Commission (GHG inventories)
  10. IRENA (global RE statistics)
- Data gap matrix with integration actions.

**Files created:**
- `@docs/FREE_ALTERNATIVE_DATA.md`

---

## Phase 7: Municipal Demand Granularity Study

**Panelist Feedback:** "Explain how you estimate municipal demand — what's the methodology?"

**What was done:**
- Created `municipal_demand_granularity_study.md` documenting:
  - Problem statement (no public municipal consumption data)
  - Population-weighted disaggregation formula
  - Assumptions and limitations (uniform per-capita consumption, industrial concentration, temporal stability)
  - Data sources (DOE Annex 8 + PSA Census)
  - Implementation details (`estimate_municipal_demand()` in `energyhub.py`)
  - 5 suggested improvements: economic weighting, nighttime lights, DU data-sharing, building footprints, ML downscaling

**Files created:**
- `@docs/municipal_demand_granularity_study.md`

---

## Phase 8: Final Documentation & Integration Testing

**What was done:**
- Backend syntax verification for all new modules.
- Frontend build verification (`npm run build` passed).
- Integration summary with deployment checklist.

---

## New Dataset Integration (Post-Panelist, From FREE_ALTERNATIVE_DATA.md)

### IRENA Data → EnergyHub Benchmarking Layer

**Integration mode:** Display alongside DOE (supplement, not replace)

**Datasets processed:**
- `C-ELECCAP_*.csv` → `irena_ph_capacity_by_tech.csv` (272 rows, 7 technologies)
- `C-ELECGEN_*.csv` → `irena_ph_generation_by_tech.csv` (182 rows, 5 technologies)
- `R-ELECGEN_*.csv` → `irena_asia_generation.csv` (120 rows, Asia region)
- `RESHARE_*.xlsx` → `irena_renewable_share.csv` (50 rows, 2000–2025)

**New API endpoints:**
- `GET /energyhub/irena/overview`
- `GET /energyhub/irena/capacity?year={year}`
- `GET /energyhub/irena/generation?year={year}`
- `GET /energyhub/irena/renewable-share`

**Frontend:** IRENA benchmark card added to EnergyHub showing latest RE capacity, generation, and share.

### Meralco Rates → EcoSim Tariff Accuracy

**Integration mode:** Meralco franchise areas only (NCR, Bulacan, Cavite, Laguna, Rizal)

**Dataset processed:**
- `FOI_-_Meralco_Actual_Implemented_Rates_2011-2020_*.xlsx` → `meralco_rates_2011_2020.csv` (10 rows)

**Extracted:** Generation Energy Charge per year (2011–2020)

**New API endpoint:**
- `GET /energyhub/meralco-rate?year={year}`

**EcoSim integration:**
- When a user selects a municipality/province in the Meralco franchise, the EcoSim response includes `meralco_rate`.
- Frontend displays a "Meralco Generation Charge Reference" card comparing the Meralco generation charge with the user's effective rate.
- Transparent note: "Generation charge component only. Total bill includes transmission, distribution, and other charges."

### Global Solar Atlas → EcoSim Solar Supplement

**Integration mode:** Supplement NASA POWER (display alongside, not replace)

**Dataset processed:**
- `Philippines_GISdata_LTAym_*_GlobalSolarAtlas-v2_GEOTIFF/` → `solar_atlas_ph.csv` (15 locations)

**Extracted metrics:**
- GHI (Global Horizontal Irradiance): mean = 4.874 kWh/m²/day
- DNI (Direct Normal Irradiance): mean = 3.750 kWh/m²/day
- DIF (Diffuse Horizontal): mean = 2.181 kWh/m²/day
- PVOUT (PV Power Output): mean = 3.918 kWh/kW/day
- TEMP (Air Temperature): mean = 26.214 °C

**New API endpoint:**
- `GET /energyhub/solar-atlas?location={name}`

**Note:** Actual integration into EcoSim solar calculations (blending with NASA POWER) requires province-level lookup mapping. The data is loaded and available via API; frontend integration can be added in a future iteration.

### Global Wind Atlas → Documented Limitation

**Finding:** The provided GeoJSON files (`globalWindAtlastPH*.geojson`) contain only the Philippines country boundary polygon. They do **not** contain wind speed, power density, or air density raster/grid values.

**Action:** Documented in `FREE_ALTERNATIVE_DATA.md` as a known gap. Wind Atlas web interface or separate raster download would be needed for actual wind data integration.

---

## Complete File Inventory

### New Files
| File | Purpose |
|------|---------|
| `DOE_Data_Extracted/data_v2_preprocessing.py` | Parse DOE v2 Annex data, train ARIMA |
| `DOE_Data_Extracted/data_v2/irena_preprocessing.py` | Parse IRENA CSVs/XLSX |
| `DOE_Data_Extracted/data_v2/meralco_preprocessing.py` | Parse Meralco Excel rates |
| `DOE_Data_Extracted/data_v2/solar_atlas_preprocessing.py` | Sample Solar Atlas GEOTIFFs |
| `fastapi-backend/app/services/products.py` | Product recommendation service |
| `fastapi-backend/app/routes/products.py` | Product API routes |
| `fastapi-backend/app/schemas/products.py` | Product Pydantic schemas |
| `react-frontend/src/components/energyhub/ChartExplanation.jsx` | Reusable chart explanation block |
| `react-frontend/src/components/energyhub/ProvincialDemand.jsx` | Provincial demand bar chart |
| `supabase_tables_scripts/municipal_population.sql` | PSA population table schema |
| `docs/FREE_ALTERNATIVE_DATA.md` | Free data sources catalog |
| `docs/municipal_demand_granularity_study.md` | Methodology document |
| `docs/REVISIONS_INTEGRATION_SUMMARY.md` | Integration checklist |

### Modified Files
| File | Changes |
|------|---------|
| `fastapi-backend/app/ml/predictor.py` | Load v2 data, IRENA, Meralco, Solar Atlas; new getter methods |
| `fastapi-backend/app/services/ecosim.py` | Province mode, Meralco franchise check |
| `fastapi-backend/app/routes/ecosim.py` | `/provinces`, mode parameter |
| `fastapi-backend/app/schemas/ecosim.py` | Province schemas, mode field |
| `fastapi-backend/app/services/energyhub.py` | IRENA, Meralco, Solar Atlas, municipal demand |
| `fastapi-backend/app/routes/energyhub.py` | New benchmarking endpoints |
| `fastapi-backend/app/schemas/energyhub.py` | New response schemas |
| `fastapi-backend/app/routes/api.py` | Register products router |
| `react-frontend/src/pages/Ecosim.jsx` | Mode toggle, product cards, Meralco display |
| `react-frontend/src/pages/EnergyHub.jsx` | IRENA benchmark, ProvincialDemand |
| `react-frontend/src/services/apiClient.js` | Province, product APIs |
| `react-frontend/src/services/energyhub.js` | IRENA, Meralco, Solar Atlas APIs |
| `react-frontend/src/components/energyhub/EnergyTrends.jsx` | ChartExplanation blocks |
| `react-frontend/src/components/energyhub/EnergySources.jsx` | ChartExplanation block |

---

## API Endpoint Reference

### EcoSim
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ecosim/provinces` | GET | List all provinces |
| `/ecosim/` | GET | Run simulation (supports `mode=municipality/province`) |
| `/ecosim/` | POST | Run simulation with body params |

### EnergyHub
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/energyhub/overview` | GET | National statistics + forecast summary |
| `/energyhub/irena/overview` | GET | IRENA capacity + generation + share |
| `/energyhub/irena/capacity` | GET | Filter by `year` |
| `/energyhub/irena/generation` | GET | Filter by `year` |
| `/energyhub/irena/renewable-share` | GET | Year-by-year RE share |
| `/energyhub/meralco-rate` | GET | Filter by `year` |
| `/energyhub/solar-atlas` | GET | Filter by `location` |
| `/energyhub/provincial-demand` | GET | DOE Annex 8 breakdown |
| `/energyhub/municipal-demand/{province_id}` | GET | Population-weighted estimates |

### Products
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/products/recommend` | GET | `energy_type`, `budget_php`, `limit` |
| `/products/browse` | GET | Filters + pagination |
| `/products/audit` | GET | Data quality report |

---

## Deployment Checklist

- [ ] Run `DOE_Data_Extracted/data_v2_preprocessing.py` (if Annex files change)
- [ ] Run `DOE_Data_Extracted/data_v2/irena_preprocessing.py`
- [ ] Run `DOE_Data_Extracted/data_v2/meralco_preprocessing.py`
- [ ] Run `DOE_Data_Extracted/data_v2/solar_atlas_preprocessing.py`
- [ ] Populate `municipal_population` Supabase table with PSA 2020 Census data
- [ ] Verify all CSVs exist in `DOE_Data_Extracted/data_v2_preprocessed/`
- [ ] Run backend: `uvicorn main:app --reload`
- [ ] Run frontend: `npm run dev` (or build: `npm run build`)
- [ ] Test `/energyhub/irena/overview`
- [ ] Test `/energyhub/meralco-rate`
- [ ] Test `/energyhub/solar-atlas`
- [ ] Test EcoSim with Meralco-area municipality (e.g., Manila)
- [ ] Test EcoSim province mode

---

## Known Data Gaps & Future Work

| Gap | Status | Action |
|-----|--------|--------|
| PSA municipal population | Required for Phase 3 | Load PSA 2020 Census into `municipal_population` table |
| Wind Atlas actual wind data | GeoJSONs are boundary-only only | Download raster from globalwindatlas.info web interface |
| Solar Atlas province-level aggregation | Sampled at 15 cities only | Add zonal statistics by province polygon |
| Meralco total rate | Only generation charge extracted | Add transmission + distribution components if available |
| Product URL staleness | Ongoing | Review `/products/audit` quarterly |

---

*Document compiled: June 30, 2026*
*Revisions implemented by: LUMI Development Team*
