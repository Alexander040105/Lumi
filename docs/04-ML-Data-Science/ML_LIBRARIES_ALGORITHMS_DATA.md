# LUMI — Machine Learning Libraries, Algorithms, and Data

> Document focused on the ML/AI stack, the algorithms used in the EnergyHub forecasting and EcoSim recommendation modules, the data sources that feed them, and the rationale behind each choice.

---

## 1. Machine Learning & Data Science Libraries

| Library | Version (if pinned) | Role in LUMI |
|---------|---------------------|--------------|
| **pandas** | >=2.0.0 | Data loading, cleaning, merging, and time-series preprocessing for DOE data |
| **numpy** | >=1.24.0 | Numerical operations, array handling, and metric computation |
| **statsmodels** | — | ARIMA / SARIMA / SARIMAX model fitting, ADF stationarity test, ACF/PACF plots |
| **scikit-learn** | — | Random Forest Regression, regression metrics (MAE, RMSE, MAPE), train-test utilities |
| **torch** | — | Deep learning runtime (available in environment; not used for the primary forecasting pipeline) |
| **matplotlib** | — | EDA plots, forecast visualizations, ACF/PACF charts |
| **sentence-transformers** | 3.0.1 | Text embedding model for the RAG (Retrieval-Augmented Generation) pipeline |
| **faiss-cpu** | 1.9.0.post1 | Vector similarity search index for RAG document retrieval |
| **transformers** | — | Hugging Face model utilities |
| **langchain** | — | LLM chaining and text-splitting utilities for RAG |
| **nltk** | — | Text preprocessing for the RAG pipeline |
| **deep-translator** | — | Translation utilities for multilingual RAG support |

### Why these libraries?

- **pandas + numpy + statsmodels** form the backbone of the forecasting pipeline. The DOE dataset is only 22 annual observations, so a lightweight classical stack is sufficient and far more stable than deep-learning frameworks on limited data.
- **scikit-learn** is used for the Random Forest controlled experiment and for standard regression metrics.
- **sentence-transformers + FAISS** power the RAG system that enriches EcoSim AI recommendations with scraped renewable-energy pricing and equipment context.
- **torch** is present for future extensibility but is intentionally avoided in the current forecasting module due to deployment constraints (Render free-tier RAM limit of 512 MB).

---

## 2. Algorithms Used

### 2.1 EnergyHub — National Energy Demand Forecasting

All models were trained **offline** in `DOE_arima_forecasting.ipynb`. The production backend (`fastapi-backend/app/ml/predictor.py`) loads pre-computed CSV artifacts and serves them without retraining on every request.

| Algorithm | Family | Role in LUMI | Why It Was Used |
|-----------|--------|------------|-----------------|
| **Naive with Drift** | Baseline | Accuracy floor | Any deployed model must outperform this. Serves as the minimum acceptable benchmark (Makridakis et al., 2022). |
| **Linear Trend Regression** | OLS | Interpretable baseline | `beta_1` directly equals the annual growth rate in GWh. Easy to explain to non-technical stakeholders and panelists. |
| **ARIMA(1,1,1)** | Box-Jenkins | **Core production model** | Handles autocorrelation, first-order differencing (trend removal), and moving-average shocks. Parsimonious: only 3 parameters for 18 training points (Gonzales et al., 2024). |
| **Holt Linear Smoothing** | State-space | Trend-aware baseline | Optimized for short non-seasonal series. Provides a second classical baseline to confirm ARIMA superiority. |
| **SARIMAX(1,1,1) + Exog** | Box-Jenkins + Exogenous | Augmented ARIMA | Tests whether adding renewable-share and capacity-margin regressors improves accuracy. Deliberately kept simple to avoid overfitting. |
| **Random Forest Regression** | Tree ensemble | **Controlled experiment** | Deliberately constrained (`max_depth=3`, `min_samples_leaf=2`) to empirically demonstrate ML overfitting on a tiny dataset (Wang et al., 2024). |

#### Algorithm Selection Rationale

1. **Parsimony:** With only 22 observations, every extra parameter increases overfitting risk. ARIMA(1,1,1) uses just 3 parameters on 18 training rows (15 degrees of freedom).
2. **Interpretability:** ARIMA coefficients and confidence intervals are explainable in thesis defense. LSTM or XGBoost would be black-boxes.
3. **Temporal awareness:** Unlike random-forest or gradient-boosting, ARIMA explicitly models the sequential nature of time series.
4. **Deployment fit:** A trained ARIMA model is < 1 MB. It loads instantly and uses negligible RAM, making it ideal for Render free-tier hosting.
5. **Why not LSTM / XGBoost / LightGBM?** The `LUMI_ML_MODEL_ANALYSIS.md` evaluation concluded that:
   - LSTM requires hundreds to thousands of time steps per series; 84 monthly steps (or 22 annual steps) is insufficient and leads to severe overfitting.
   - Deep-learning frameworks (TensorFlow / PyTorch) are 300–400 MB base, risking OOM kills on 512 MB Render instances.
   - Gradient boosting, while excellent on tabular data, still needs larger sample sizes (>100K rows) to reliably outperform ARIMA on this scale.

#### Evaluation Metrics

| Metric | Purpose |
|--------|---------|
| **MAE** | Average absolute error in GWh; robust to outliers; intuitive for policy communication |
| **RMSE** | Penalizes large errors; useful for detecting peak-demand miss-events |
| **MAPE** | Scale-independent percentage; directly comparable across variables |

#### Model Comparison Results (Test Set: 2021–2024)

| Model | MAE | RMSE | MAPE |
|-------|-----|------|------|
| Linear Trend Regression | 5,994 | 7,342 | 4.97 % |
| Holt Linear Smoothing | 6,558 | 7,998 | 5.44 % |
| Naive with Drift | 6,709 | 8,128 | 5.57 % |
| **ARIMA(1,1,1)** | 6,829 | 8,257 | 5.67 % |
| SARIMAX(1,1,1) + Exog | 9,914 | 11,459 | 8.28 % |
| Random Forest Regression | 15,957 | 17,806 | 13.41 % |

> The **ARIMA(1,1,1)** model was selected as the final forecaster because it is the best balance of accuracy, parsimony, and interpretability. Linear Trend Regression scored slightly lower MAE but cannot capture autocorrelation or shocks. Random Forest massively overfit, confirming the decision to avoid complex ML on this dataset.

---

### 2.2 EcoSim — Renewable Energy Simulation & Recommendation

**Important:** EcoSim does **not** use machine learning for its core simulation. It uses deterministic, physics-based formulas derived from peer-reviewed literature. ML is used only for the **optional AI analysis layer** (Gemini / RAG).

| Component | Method | Why |
|-----------|--------|-----|
| **Solar output** | Physics-based irradiance-to-energy conversion with temperature factor, dust loss, humidity degradation, performance ratio | Municipal-level solar potential is a deterministic function of climate variables. No training data needed (Huda et al., 2024; Taduran & Piao, 2025). |
| **Wind output** | Betz-capped power equation + capacity factor using product-database averages | Wind power follows aerodynamic laws. Product averages provide realistic rotor-radius and power-coefficient inputs. |
| **Hydro output** | Rational-method runoff estimation + micro-hydropower formula (`rho * g * Q * H * eta`) | Runoff is a direct function of rainfall, slope, and watershed gradient. DEM-derived hydraulic head removes the need for empirical training. |
| **Economic scoring** | Rule-based weighted linear combination (WLC) + simple payback period | Defensible, transparent, and thesis-appropriate. Avoids ML-based costing where no large labeled dataset exists (Asadi et al., 2023; Ngwakwe, 2025). |
| **AI analysis** | Google Gemini (standard) or RAG-backed Gemini | Provides natural-language summaries. RAG enriches responses with scraped renewable-energy pricing context from FAISS retrieval. |

#### EcoSim AI / RAG Stack

| Technology | Role |
|-----------|------|
| **Sentence Transformers** | Embeds scraped renewable-energy documents (pricing, equipment) into dense vectors |
| **FAISS-CPU** | Stores vectors and performs fast top-k similarity search at query time |
| **Google Gemini API** | Generates natural-language analysis, recommendations, and cost estimates |
| **Groq API** | Fast LLM fallback when Gemini is unavailable or rate-limited |
| **LangChain + NLTK** | Document chunking, text splitting, and preprocessing for the knowledge base |

---

## 3. Data Sources & Datasets

### 3.1 DOE Philippine Power Statistics (2003–2024)

| File | Rows x Cols | Description |
|------|-------------|-------------|
| `Tabula_DOE_Data.csv` | Raw PDF extraction | Original lattice-extracted tables from DOE 2024 Power Statistics PDF |
| `electricity_consumption_by_sector_GWh.csv` | 8 x 23 | Residential, commercial, industrial, others, sales, own use, losses |
| `system_peak_demand_MW.csv` | 4 x 23 | Luzon, Visayas, Mindanao, and total non-coincidental peak demand |
| `gross_power_generation_by_grid_GWh.csv` | 4 x 23 | Generation per island grid |
| `gross_power_generation_by_plant_type_GWh.csv` | 14 x 23 | Coal, natural gas, oil, geothermal, hydro, solar, wind, biomass, etc. |
| `installed_capacity_by_plant_type_MW.csv` | 10 x 23 | Maximum possible capacity per fuel type |
| `dependable_capacity_by_plant_type_MW.csv` | 10 x 23 | Reliable capacity accounting for maintenance/fuel issues |
| `national_energy_annual_ready.csv` | 22 x 27 | Pre-cleaned consolidated file used as validation ground truth |
| `master_preprocessed.csv` | 22 x ~37 | Final merged dataset with engineered features (lags, rolling means, YoY growth, capacity margins) |

#### Data Extraction Method
- **Tool:** Tabula (open-source Java-based PDF table extractor)
- **Process:** Manual download of DOE PDFs → lattice/stream parsing → CSV export → validation against original PDFs
- **Validation:** Maximum cell-level discrepancy = **0.0000** after cleaning

#### Engineered Features

| Feature | Formula | Rationale |
|---------|---------|-----------|
| `years_since_2003` | `year - 2003` | Captures linear time trend |
| `consumption_yoy_growth` | `(current - previous) / previous * 100` | Growth rate, not just absolute level |
| `renewable_share_pct` | `renewable_generation / total_consumption * 100` | Policy-relevant RE penetration metric |
| `capacity_margin_pct` | `(dependable - peak) / peak * 100` | Grid stress / reliability signal |
| `consumption_lag1 / lag2` | `.shift(1)`, `.shift(2)` | Autoregressive inputs for RF baseline |
| `consumption_roll3 / roll5` | 3-year and 5-year moving averages | Smooths one-off shocks (e.g., COVID-2020) |

---

### 3.2 NASA POWER Climate Data

| Dataset | Source | Coverage | Use |
|---------|--------|----------|-----|
| `municipality_climate_monthly` | NASA POWER API | 2018–present, ~1,600 Philippine municipalities, monthly granularity | EcoSim climate lookup, renewable scoring |
| `municipality_climate_averages.csv` | Pre-aggregated from monthly table | Long-term averages per municipality | Fast O(1) CSV lookup for EcoSim simulation |

**Key climate variables:**
- `allsky_sfc_sw_dwn` — All-sky surface shortwave downward irradiance (kWh/m²/day) → **Solar calculations**
- `ws10m` — Wind speed at 10 m (m/s) → **Wind calculations**
- `prectotcorr` — Corrected precipitation (mm/day) → **Hydropower runoff**
- `t2m` — Air temperature (°C) → **Solar temperature derating**
- `rh2m` — Relative humidity (%) → **Panel degradation**
- `cloud_amt` — Cloud amount (%) → **Solar penalty**
- `surface_pressure` — Surface pressure (hPa) → **Air density for wind**
- `elevation` — Elevation (m) → **Terrain context**

---

### 3.3 Terrain & DEM Data

| Dataset | Source | Use |
|---------|--------|-----|
| `hydropower_suitability` (Supabase) | Derived via `rasterio`, `richdem`, `whitebox` | Micro-hydropower feasibility: hydraulic head, slope, runoff potential, gravity flow |
| DEM Rasters | USGS SRTM / HydroSHEDS | Elevation, watershed gradient, terrain ruggedness |

**Key terrain variables:**
- `hydraulic_head_m` — Vertical drop for hydropower
- `mean_slope_deg` — Average terrain steepness
- `runoff_potential` — Estimated water runoff coefficient
- `gravity_flow_potential` — Gravity-driven flow feasibility
- `hydro_suitability_score` — Composite terrain-based score

---

### 3.4 E-Commerce Pricing Data (RAG Knowledge Base)

| Source | Scraper File | Use |
|--------|--------------|-----|
| Alibaba | `alibaba_scraper.py` | Solar panel, inverter, battery pricing |
| Amazon | `amazon_scraper.py` | Equipment cost reference |
| Lazada | `lazada_scraper.py` | Local Philippines marketplace pricing |
| Shopee | `shopee_scraper.py` | Local Philippines marketplace pricing |

These are used to build the **RAG knowledge base** for cost-aware AI recommendations, not for rule-based simulation costing.

---

### 3.5 GeoJSON & Administrative Data

| File | Use |
|------|-----|
| `philippine_geojson_file_per_region.json` | Choropleth map rendering in EnergyHub |
| `regions`, `provinces`, `municipalities` (Supabase) | Administrative hierarchy, map labels, coordinate lookups |

---

## 4. Train / Test Split Strategy

| Set | Years | Observations | Purpose |
|-----|-------|--------------|---------|
| **Train** | 2003–2020 | 18 | Fit all models |
| **Test** | 2021–2024 | 4 | Evaluate forecast accuracy on unseen future |

**Why chronological?** Time series has direction. Random shuffling would leak future information into training, inflating accuracy metrics by 20–40% and producing models that fail in production (Makridakis et al., 2022).

---

## 5. Deployment Architecture for ML

```
data/DOE_Data_Extracted/
  ├── master_preprocessed.csv              (historical data)
  ├── forecast_consumption_2025_2030.csv   (ARIMA point forecast + 95% CI)
  ├── forecast_peak_demand_2025_2030.csv  (ARIMA peak demand forecast)
  └── model_comparison_results.csv         (test-set metrics for all 6 models)
          ↓
fastapi-backend/app/ml/predictor.py
          ↓
EnergyHubML singleton (loads once at startup)
          ↓
FastAPI endpoints (/overview, /forecast, /trends, /model-comparison)
          ↓
React frontend (EnergyHub dashboard)
```

**No runtime training.** The backend is stateless and O(1) for all ML endpoints. ARIMA was trained once in the Jupyter notebook and serialized as CSV artifacts.

---

## 6. Summary Table: Why We Chose What We Chose

| Decision | Chosen Option | Rejected Options | Reason |
|----------|---------------|----------------|--------|
| **Forecasting algorithm** | ARIMA(1,1,1) | LSTM, XGBoost, LightGBM, Prophet | Short series (n=22); interpretability; minimal deployment footprint |
| **Simulation engine** | Physics-based formulas | ML regression / neural networks | Renewable potential is deterministic; no training data needed; fully explainable |
| **Scoring method** | Rule-based weighted linear combination | ML classifier | No labeled feasibility dataset exists; rule-based is defensible for thesis |
| **AI explanations** | Gemini + RAG (FAISS + sentence-transformers) | Full conversational chatbot | Token/cost limits; short summaries only; cached in Redis |
| **Data ingestion** | Tabula PDF extraction + NASA POWER API | Real-time DOE API (none exists) | DOE has no public API; manual extraction is the only authoritative source |
| **Backend ML serving** | Pre-computed CSV artifacts | On-demand model retraining | ARIMA trains in milliseconds, but `statsmodels` is heavy; CSVs guarantee deterministic outputs |

---

*Compiled from: `data/DOE_Data_Extracted/` notebooks, `fastapi-backend/app/ml/predictor.py`, `ECOSIM_ARCHITECTURE.md`, `ENERGYHUB_ARCHITECTURE.md`, `LUMI_ML_MODEL_ANALYSIS.md`, `LUMI_METHODOLOGY_ML.md`, and `LUMI_TECH_RECOMMENDATIONS.md`.*
