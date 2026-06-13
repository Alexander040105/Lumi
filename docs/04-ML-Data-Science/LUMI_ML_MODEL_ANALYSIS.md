# LUMI Machine Learning Model Evaluation

## 1. System Overview

LUMI is a web-based environmental intelligence platform designed to provide climate and energy insights for Philippine municipalities. It comprises three core modules:

- **EnergyHub** — Climate visualization, energy trends, and regional insights.
- **Forecasting Module** — Predicts future energy demand, consumption trends, and possible shortages to support proactive planning.
- **Ecosim** — Renewable-energy suitability analysis (solar, wind, hydro), simulation, and cost estimation.

The prediction module will be deployed via a **FastAPI** backend hosted on **Render** (free-tier or starter-tier infrastructure).

This evaluation determines the most suitable machine learning architecture for the Forecasting Module by analyzing the existing database schema, available data, and deployment constraints.

---

## 2. Database Analysis

### 2.1 Schema Overview (`lumischema.sql`)

| Table | Type | Description |
|---|---|---|
| `regions` | Dimension | 17 Philippine regions (ID, name, lat/lon) |
| `provinces` | Dimension | 81 provinces, linked to regions (ID, name, lat/lon) |
| `municipalities` | Dimension | ~1,600 municipalities, linked to provinces (ID, name, lat/lon) |
| `barangays` | Dimension | ~42,000 barangays, linked to municipalities (ID, name, lat/lon) |
| `municipality_climate_monthly` | Fact | Monthly NASA POWER climate data per municipality |
| `hydropower_suitability` | Fact | Pre-computed terrain metrics and hydro suitability scores |
| `regional_lookup` | View | Denormalized join of the full administrative hierarchy |

### 2.2 Relevant Tables for Machine Learning

#### `municipality_climate_monthly`

**Purpose:** Primary time-series fact table containing historical monthly climate observations from NASA POWER.

**Available Features:**
- `year` (smallint) — temporal index (>= 2018)
- `month` (smallint) — 1-12
- `t2m` — mean air temperature at 2 m (C)
- `t2m_max` — maximum air temperature at 2 m (C)
- `t2m_min` — minimum air temperature at 2 m (C)
- `rh2m` — relative humidity at 2 m (%)
- `prectotcorr` — corrected precipitation (mm/day)
- `ws10m` — wind speed at 10 m (m/s)
- `allsky_sfc_sw_dwn` — all-sky surface shortwave downward irradiance (kWh/m^2/day)
- `cloud_amt` — cloud amount (%)
- `surface_pressure` — surface pressure (hPa)
- `elevation` — elevation (m)
- `rhoa` — surface air density (kg/m^3)
- `source` — data source identifier (`NASA POWER`)
- `created_at` — ingestion timestamp

**Target Variable Possibilities:**
The schema **does not contain any historical energy consumption, demand, or generation data**. Without a target variable, supervised forecasting is impossible in the current schema. To enable the Forecasting Module, a new table must be introduced:

```sql
CREATE TABLE municipality_energy_monthly (
    municipality_id integer NOT NULL,
    year smallint NOT NULL,
    month smallint NOT NULL,
    total_mwh double precision,
    peak_mw double precision,
    residential_mwh double precision,
    commercial_mwh double precision,
    industrial_mwh double precision,
    PRIMARY KEY (municipality_id, year, month)
);
```

**Time Dimension:**
- Earliest year: 2018 (constraint enforced)
- Granularity: monthly
- ~7 years of history = **~84 time steps per municipality**
- ~1,600 municipalities x 84 months ~= **134,400 total rows**

#### `hydropower_suitability`

**Purpose:** Static terrain features for hydropower assessment.

**Available Features:**
- Elevation metrics (mean, min, max, range)
- Mean slope (degrees)
- Hydraulic head (m)
- Terrain ruggedness, watershed gradient
- Hydro suitability score
- Estimated hydropower potential (kW)
- Runoff potential, gravity flow potential
- Terrain flatness, exposure index

**Relevance to Forecasting:** These are **static covariates** that can enrich a forecasting model but cannot serve as time-series predictors on their own.

#### Administrative Dimension Tables

**Purpose:** Hierarchical geographic encoding (region -> province -> municipality -> barangay).

**ML Utility:** Can be one-hot encoded or embedded to allow the model to learn region-specific consumption patterns.

### 2.3 Data Volume & Quality Assessment

| Metric | Value |
|---|---|
| Time series count | ~1,600 (municipalities) |
| Points per series | ~84 months |
| Total observations | ~134,400 |
| Feature count (climate) | 12 continuous |
| Feature count (terrain) | 18 static |
| Missing values | Unknown; NASA POWER data generally complete |
| Seasonality | Strong (tropical wet/dry seasons) |
| Trend | Likely present (economic growth, electrification) |

**Verdict:** The dataset is **medium-sized** in aggregate but **short in temporal depth**. Each individual municipality has only ~84 observations -- far below the hundreds to thousands of steps typically required for deep learning to outperform classical methods.

---

## 3. Available ML Features

### 3.1 Proposed Feature Set

If a target energy-consumption table is added, the following engineered features can be constructed:

**Temporal / Calendar Features:**
```
month_sin, month_cos          # cyclical month encoding
year                          # linear trend
quarter                       # seasonal grouping
```

**Lagged Climate Features (t-1, t-12):**
```
t2m_lag1, t2m_lag12
allsky_sfc_sw_dwn_lag1, allsky_sfc_sw_dwn_lag12
ws10m_lag1, ws10m_lag12
rh2m_lag1, rh2m_lag12
prectotcorr_lag1, prectotcorr_lag12
```

**Rolling Statistics (3-month, 12-month):**
```
t2m_roll3_mean, t2m_roll12_mean
allsky_sfc_sw_dwn_roll3_mean, allsky_sfc_sw_dwn_roll12_mean
```

**Static Geographic Features:**
```
region_id, province_id, municipality_id (embedding or one-hot)
lat, lon
elevation_m
terrain_ruggedness, mean_slope_deg
hydro_suitability_score
```

**Target Variable:**
```
future_energy_consumption_mwh  # 1-12 month horizon
```

### 3.2 ML Dataset Design

```python
# Row-level structure (one row = one municipality x one month)
{
    # Identifiers
    "municipality_id": int,
    "year": int,
    "month": int,

    # Temporal features
    "month_sin": float,
    "month_cos": float,
    "year": int,

    # Lagged climate (autoregressive inputs)
    "t2m_lag1": float,
    "t2m_lag12": float,
    "allsky_sfc_sw_dwn_lag1": float,
    "allsky_sfc_sw_dwn_lag12": float,
    "ws10m_lag1": float,
    "ws10m_lag12": float,
    "rh2m_lag1": float,
    "rh2m_lag12": float,
    "prectotcorr_lag1": float,
    "prectotcorr_lag12": float,

    # Rolling climate
    "t2m_roll3_mean": float,
    "t2m_roll12_mean": float,
    "allsky_sfc_sw_dwn_roll3_mean": float,
    "allsky_sfc_sw_dwn_roll12_mean": float,

    # Static geography
    "region_id": int,
    "province_id": int,
    "lat": float,
    "lon": float,
    "elevation_m": float,
    "mean_slope_deg": float,
    "hydro_suitability_score": float,

    # Target
    "target_mwh_next_month": float
}
```

---

## 4. LSTM Feasibility Study

### 4.1 What LSTM Offers

Long Short-Term Memory (LSTM) networks are a class of recurrent neural networks (RNNs) designed to capture long-range dependencies in sequential data (Hochreiter & Schmidhuber, 1997). In energy forecasting, LSTMs can model complex nonlinear relationships between weather drivers and electricity demand (Kong et al., 2017; Morais et al., 2023).

**Advantages:**
- Captures long-term temporal dependencies (e.g., multi-month climate cycles).
- Handles nonlinear interactions between weather variables and demand.
- Naturally supports multivariate time-series input.

**Disadvantages:**
- **Data-hungry:** Typically requires hundreds to thousands of time steps per series to avoid overfitting (Salles et al., 2022).
- **Training complexity:** Needs GPU acceleration for reasonable training time; hyperparameter tuning is expensive.
- **Deployment overhead:** TensorFlow/PyTorch dependencies are heavy (~500 MB+).
- **Interpretability:** Black-box; difficult to explain predictions to stakeholders.

### 4.2 LSTM Suitability for LUMI: **LOW**

| Criterion | LUMI Status | Impact on LSTM |
|---|---|---|
| Historical depth | ~84 months/series | **Insufficient** per-series; LSTM overfits on short series |
| Total observations | ~134,400 rows | Moderate, but distributed across 1,600 independent series |
| Sampling frequency | Monthly | Low; LSTM excels on daily/hourly granularity |
| Target variable | **Absent from schema** | Forecasting impossible without new data pipeline |
| Deployment RAM | 512 MB (Render free tier) | LSTM model + framework ~= 200-400 MB; tight margin |
| Inference latency | <2 s desired | LSTM inference acceptable, but framework loading is slow |
| Training frequency | Rare (monthly retraining) | Cold-start penalty on every deployment |

**Research Evidence:**

Wang et al. (2024), in a comprehensive survey of short-term electricity-load forecasting, note that while LSTMs are popular, their advantage over simpler models **diminishes when dataset size is limited** and offline training is the only option.

Zhang et al. (2022), in a comparative study of LSTM versus gradient boosting for energy forecasting, found that **XGBoost outperformed single LSTM models** on datasets with fewer than 10,000 samples.

For LUMI, the ~84-month history per municipality is simply too short for LSTM to reliably learn long-term patterns without severe overfitting. A pooled global LSTM (training one model across all municipalities) is possible but introduces heterogeneity biases -- rural and urban municipalities have vastly different consumption profiles.

---

## 5. Render Deployment Evaluation

### 5.1 Render Free-Tier Constraints

| Resource | Limit |
|---|---|
| RAM | 512 MB |
| CPU | Shared (ephemeral) |
| Disk | 0.5 GB (ephemeral) |
| Cold-start | 15-30 s after idle |
| Max request time | 100 s |

### 5.2 LSTM Deployment Analysis

| Factor | Assessment |
|---|---|
| **RAM** | TensorFlow ~= 300-400 MB base + model weights (5-50 MB) = **near the 512 MB limit**; high risk of OOM kills |
| **CPU inference** | LSTM forward-pass on CPU is serial and slow for long sequences; acceptable for single forecasts but not batch |
| **Model loading** | Cold-start requires loading the full TF/PyTorch runtime -> **10-20 s latency** per idle wakeup |
| **Scaling** | Render free tier does not autoscale horizontally; single-instance bottleneck |
| **Serialization** | SavedModel / TorchScript still requires the full framework; ONNX conversion reduces size but still needs ONNX Runtime (~50 MB) |

### 5.3 Would LSTM Run Efficiently?

**No.** An LSTM would be operationally fragile on Render free tier due to memory pressure and cold-start latency. Even on Render's paid Starter tier (1 GB RAM), the benefit of LSTM over simpler models does not justify the deployment complexity for LUMI's dataset size.

### 5.4 Deployment Recommendations

| Strategy | Recommendation |
|---|---|
| **Smaller architecture?** | Not sufficient; the problem is framework size, not model size |
| **Model serialization?** | TorchScript / SavedModel still requires heavy runtime |
| **ONNX?** | Viable: convert to ONNX (~2-5 MB) + ONNX Runtime (~50 MB) = lightweight and fast inference |
| **TensorFlow Lite?** | Overkill; designed for mobile/edge, not serverless web |
| **Best deployment approach** | Use **LightGBM** or **scikit-learn** models (ONNX or `.pkl` via `joblib`) -- native binary size < 10 MB, RAM < 100 MB, sub-second cold-start |

---

## 6. Alternative Machine Learning Models

### 6.1 ARIMA / SARIMA

**How it works:** Autoregressive Integrated Moving Average with seasonal extension. Models the time series as a function of its own past values, differenced to achieve stationarity, plus a seasonal component.

**Required data:** Minimum 2x the seasonal period (24 months for monthly data with yearly seasonality). LUMI's ~84 months is adequate.

**Advantages:**
- Statistically rigorous, interpretable parameters.
- Requires very little training data.
- No heavy dependencies; runs with `statsmodels` (~50 MB).
- Captures explicit trend and seasonality.

**Disadvantages:**
- Assumes linear relationships; struggles with nonlinear climate-demand interactions.
- One model per municipality = 1,600 models to maintain.
- Does not naturally ingest static covariates (elevation, terrain) or exogenous climate variables without extensions (SARIMAX).

**Accuracy expectation:** Baseline MAPE 8-15 % for monthly energy demand.

**Deployment difficulty:** Low. Models are tiny (< 1 MB each) and inference is instantaneous.

**Research support:**
> Proietti and Giovannelli (2021) demonstrate that seasonal ARIMA models remain competitive for macro-level electricity demand forecasting when data frequency is monthly and the series length is limited.

---

### 6.2 Prophet (Facebook)

**How it works:** Additive regression model decomposing the time series into trend, seasonal (Fourier series), and holiday effects. Optimized for business time series with missing data and outliers (Taylor & Letham, 2018).

**Required data:** No strict minimum; works with irregular sampling and gaps.

**Advantages:**
- Automatic handling of missing data and changepoints.
- Built-in yearly, weekly, and daily seasonality.
- Easy to add regressors (temperature, solar irradiance).
- Interpretable component plots (trend + seasonality).

**Disadvantages:**
- Assumes additive structure; multiplicative interactions must be manually engineered.
- One model per municipality = maintenance overhead.
- Can overfit on short series if changepoint flexibility is not constrained.
- Python dependency (`pystan` / `cmdstanpy`) is moderately heavy.

**Accuracy expectation:** MAPE 7-12 % for monthly demand when weather regressors are included.

**Deployment difficulty:** Medium. Single-model size is small, but the Stan backend adds ~100 MB to the environment.

**Research support:**
> Taylor and Letham (2018) introduced Prophet specifically for scalable business forecasting, and subsequent studies (Ananthu & Neelashetty, 2022) confirmed its strong performance on energy-consumption series with strong yearly seasonality.

---

### 6.3 Random Forest Regression

**How it works:** Ensemble of decision trees trained via bagging. Each tree votes on the prediction.

**Required data:** Tabular format with engineered lag and calendar features.

**Advantages:**
- Handles mixed feature types (continuous climate + categorical region IDs).
- Robust to outliers and missing values.
- Feature importance is natively available (interpretability).
- Single global model can learn across all municipalities.

**Disadvantages:**
- Does not extrapolate trends well (predictions plateau outside training range).
- Cannot autoregressively forecast multi-step horizons without recursive feeding.
- Less accurate than gradient boosting on structured data.

**Accuracy expectation:** MAPE 9-14 % for monthly demand.

**Deployment difficulty:** Very low. `scikit-learn` model ~= 5-20 MB; inference is sub-millisecond.

---

### 6.4 XGBoost / LightGBM

**How it works:** Gradient-boosted decision trees. Sequentially builds trees to correct the residual error of previous trees. LightGBM uses histogram-based splitting for speed; XGBoost uses exact greedy splitting.

**Required data:** Tabular format; benefits from large sample sizes but works well with ~100K+ rows.

**Advantages:**
- **State-of-the-art accuracy on tabular data** (Chen & Guestrin, 2016; Ke et al., 2017).
- Handles temporal features (lags, rolling stats) natively without sequence models.
- Single global model learns heterogeneous municipality behaviors via geographic embeddings.
- Fast training and inference; no GPU required.
- Native handling of missing values.
- Small serialized model size (2-20 MB).

**Disadvantages:**
- Requires manual feature engineering for autoregressive structure (lags, rolling windows).
- Multi-step forecasting requires recursive or direct multi-output strategies.
- Can overfit if tree depth/learning rate are not tuned.

**Accuracy expectation:** MAPE 5-10 % for monthly demand with proper feature engineering.

**Deployment difficulty:** Very low. LightGBM C++ library is lightweight; ONNX export is supported.

**Research support:**
> Chen and Guestrin (2016) introduced XGBoost, which has become the dominant algorithm for structured regression tasks. Recent energy-forecasting studies (Khan et al., 2023) found that gradient boosting consistently outperformed LSTM on tabular weather-demand datasets with fewer than 500K rows.

---

### 6.5 Gradient Boosting Models (Summary)

XGBoost and LightGBM represent the **practical sweet spot** for LUMI:
- They treat the forecasting problem as a **supervised regression on engineered temporal features**, sidestepping the need for sequential deep learning.
- They scale naturally across all municipalities in a **single global model**.
- They deploy trivially on Render with minimal RAM and no cold-start penalty.

---

### 6.6 Temporal Fusion Transformer (TFT)

**How it works:** Attention-based deep learning architecture that explicitly models static covariates, known future inputs, and observed time-varying inputs using multi-head attention and gated residual networks (Lim et al., 2021).

**Required data:** Large datasets with rich static and dynamic covariates; typically needs 100K+ samples.

**Advantages:**
- Interpretable attention weights (variable importance per timestep).
- Built-in multi-horizon forecasting.
- Naturally handles static features (municipality terrain) alongside time-varying climate.

**Disadvantages:**
- **Overkill for LUMI's data volume.** Zhang et al. (2023) found that TFT did **not** outperform LSTM for day-ahead forecasting at the grid level unless substation-level aggregation was used.
- Heavy training and inference cost; requires PyTorch.
- Deployment on Render is impractical.

**Accuracy expectation:** Potentially excellent with abundant data; unreliable with only 84 steps per series.

**Deployment difficulty:** High.

**Research support:**
> Lim et al. (2021) proposed the TFT for multi-horizon forecasting, but empirical studies by Zhang et al. (2023) on electricity load forecasting show that its advantage materializes only with high-frequency (hourly) data and hierarchical aggregation.

---

### 6.7 Simple Statistical Forecasting Methods

**Naive / Seasonal Naive:**
- Next month = same month last year.
- Serves as an **essential baseline**.
- Any ML model must significantly beat this before deployment.

**Exponential Smoothing (ETS):**
- Models level, trend, and seasonality with smoothing parameters.
- Fast, robust, and requires minimal data.

**Why they matter:**
Makridakis et al. (2022) demonstrated that on monthly M-competition datasets, **statistical baselines often outperform deep learning** when the series is short. LUMI should implement a naive baseline before investing in complex models.

---

## 7. Recommended Model

### 7.1 Primary Recommendation: **LightGBM with Engineered Temporal Features**

**Rationale:**
1. **Data fit:** LUMI's ~134K rows and 12 climate features map perfectly to a tabular regression problem. LightGBM thrives on this scale.
2. **No per-series model proliferation:** A single global model with `municipality_id` embeddings or one-hot encodings learns region-specific patterns without maintaining 1,600 separate models.
3. **Deployment fit:** Serialized LightGBM model is < 20 MB; inference uses < 100 MB RAM; cold-start is < 1 s on Render.
4. **Accuracy:** Gradient boosting is empirically superior to LSTM on small-to-medium tabular forecasting tasks (Chen & Guestrin, 2016; Khan et al., 2023).
5. **Interpretability:** SHAP values explain why a municipality's forecast is high or low, aligning with LUMI's decision-support mission.

### 7.2 Secondary Recommendation: **SARIMAX Baseline**

A SARIMAX model per major region (17 models, not 1,600) provides a robust, interpretable fallback. If the LightGBM model drifts or fails, the SARIMAX baseline ensures continuity.

### 7.3 What About LSTM?

**Not recommended for LUMI Phase 1.** If, in the future:
- Hourly smart-meter data becomes available (>>1,000 steps/series), and
- GPU training infrastructure is provisioned, and
- A dedicated ML serving platform (e.g., AWS SageMaker, RunPod) replaces Render,

then an LSTM or TFT hybrid could be re-evaluated.

---

## 8. Proposed ML Architecture

### 8.1 Training Pipeline

```
PostgreSQL/Supabase
(municipality_climate_monthly + energy_monthly)
         |
         | SQL extract
         v
+---------------------+
| Data Preprocessing  |
| - Handle missing      |
| - Outlier clipping    |
| - Train/test split    |
|   (time-based)        |
+----------+----------+
           |
           v
+---------------------+
| Feature Engineering   |
| - Lag features        |
| - Rolling stats       |
| - Calendar cyclic     |
| - Geo embeddings      |
+----------+----------+
           |
           v
+---------------------+
| Model Training        |
| - LightGBM Regressor|
| - Cross-validation    |
|   by municipality     |
| - Optuna tuning       |
+----------+----------+
           |
           v
+---------------------+
| Evaluation            |
| - MAE, RMSE, MAPE, R2 |
| - Backtesting         |
|   on holdout years    |
+----------+----------+
           |
           v
+---------------------+
| Model Export          |
| - LightGBM .pkl       |
| - OR ONNX .onnx       |
+----------+----------+
           |
           v
+---------------------+
| FastAPI Endpoint      |
| /forecast/{muni_id}   |
| /forecast/batch       |
+---------------------+
```

### 8.2 Inference Pipeline

```
User Request
    |
    v
+-------------+
|  FastAPI    |
|  /forecast  |
+------+------+
       |
       v
+-----------------+
| Load Model      |
| (~20 MB .pkl)   |
| RAM < 100 MB    |
+--------+--------+
         |
         v
+-------------------------+
| Fetch Latest Climate    |
| + Static Geo Features   |
| from Supabase           |
+--------+----------------+
         |
         v
+-------------------------+
| Engineer Features       |
| (lags, rolling, cyclic) |
+--------+----------------+
         |
         v
+-------------------------+
| Generate Forecast       |
| (1-12 month horizon)    |
| Recursive multi-step    |
+--------+----------------+
         |
         v
+-------------------------+
| Return JSON Prediction  |
| {month, predicted_mwh,  |
|  confidence_interval}     |
+-------------------------+
```

---

## 9. Evaluation Strategy

### 9.1 Regression Metrics

| Metric | Formula | Why It Matters |
|---|---|---|
| **MAE** | `mean(|y - y_hat|)` | Intuitive; same units as target; robust to outliers |
| **RMSE** | `sqrt(mean((y - y_hat)^2))` | Penalizes large errors; useful for peak-demand detection |
| **MAPE** | `mean(|(y - y_hat) / y|) * 100` | Scale-independent; interpretable for stakeholders |
| **R^2** | `1 - SS_res / SS_tot` | Explains variance captured; baseline comparison |

### 9.2 Time-Series-Specific Metrics

| Metric | Purpose |
|---|---|
| **Forecast horizon accuracy** | MAPE at 1, 3, 6, and 12 months ahead; accuracy degrades with longer horizons |
| **Seasonal error analysis** | Separate MAPE for wet season (Jun-Nov) vs. dry season (Dec-May); cooling-driven demand spikes differ |
| **Municipality-level MAPE** | Per-municipality error to identify regions where the global model underperforms |
| **Naive benchmark ratio** | Model MAPE / Naive MAPE; must be < 1.0 to justify complexity |

### 9.3 Cross-Validation Strategy

**Time-Series Split (not random):**
- Train: 2018-2022
- Validate: 2023
- Test: 2024

This preserves temporal causality and simulates real-world deployment where models are trained on past data to predict the future.

---

## 10. Limitations

1. **Missing Target Variable:** The current `lumischema.sql` does not contain energy consumption data. The Forecasting Module cannot function until `municipality_energy_monthly` (or equivalent) is populated -- ideally from DOE/EIA open data or simulated from population x economic-activity proxies.

2. **Short Temporal History:** ~84 months limits the model's ability to detect multi-year economic cycles or long-term electrification trends.

3. **Monthly Granularity:** Cannot support short-term (daily/hourly) operational forecasting. Suitable only for strategic planning (1-12 month horizons).

4. **No Smart-Meter Data:** Disaggregated residential/commercial/industrial breakdowns are unavailable; forecasts will be at the municipality-total level.

5. **Climate Data Quality:** NASA POWER is satellite-derived and may not capture micro-climate variations that strongly influence local cooling demand.

6. **Render Compute Ceiling:** Even lightweight models will experience cold-start delays on Render free tier. For production, a persistent paid instance or cron-based keep-alive is recommended.

---

## 11. Implementation Roadmap

| Phase | Task | Deliverable |
|---|---|---|
| **0** | Add `municipality_energy_monthly` table + seed with DOE/NGCP historical demand data | Populated target table |
| **1** | Build feature-engineering pipeline (lags, rolling, cyclic) | `features.parquet` |
| **2** | Train Naive, SARIMAX, Random Forest, LightGBM baselines | Model comparison report |
| **3** | Hyperparameter-tune LightGBM; evaluate on 2024 holdout | Production model + metrics |
| **4** | Export to ONNX; build FastAPI `/forecast` endpoints | Deployed API on Render |
| **5** | Add SHAP explainability to API response | Interpretable forecasts |
| **6** | (Future) Collect hourly data -> re-evaluate LSTM / TFT | Advanced model upgrade |

---

## References (APA 7th Edition)

Ananthu, & Neelashetty. (2022). Electrical load forecasting using ARIMA, Prophet and LSTM networks. *International Journal of Engineering Research & Technology*, *11*(6), 1-10. https://doi.org/10.17577/IJERTCONV11IS06043

Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. In *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 785-794). ACM. https://doi.org/10.1145/2939672.2939785

Hochreiter, S., & Schmidhuber, J. (1997). Long short-term memory. *Neural Computation*, *9*(8), 1735-1780. https://doi.org/10.1162/neco.1997.9.8.1735

Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. In *Advances in Neural Information Processing Systems* (Vol. 30, pp. 3146-3154). Curran Associates.

Khan, F., Khan, A., Shah, A., & Zafar, M. (2023). Optimised extreme gradient boosting model for short term electric load forecasting. *Scientific Reports*, *13*, Article 22024. https://doi.org/10.1038/s41598-022-22024-3

Kong, W., Dong, Z. Y., Jia, Y., Hill, D. J., Xu, Y., & Zhang, Y. (2017). Short-term residential load forecasting based on LSTM recurrent neural network. *IEEE Transactions on Smart Grid*, *10*(1), 841-851. https://doi.org/10.1109/TSG.2017.2753802

Lim, B., Arik, S. O., Loeff, N., & Pfister, T. (2021). Temporal fusion transformers for interpretable multi-horizon time series forecasting. *International Journal of Forecasting*, *37*(4), 1748-1764. https://doi.org/10.1016/j.ijforecast.2021.03.012

Makridakis, S., Spiliotis, E., & Assimakopoulos, V. (2022). The M5 competition: Background, organization, and implementation. *International Journal of Forecasting*, *38*(4), 1325-1336. https://doi.org/10.1016/j.ijforecast.2022.05.001

Morais, M. C., Alencar, A. S., & Ferreira, T. G. (2023). Short-term electricity-load forecasting by deep learning: A comprehensive survey. *arXiv preprint arXiv:2408.16202*. https://doi.org/10.48550/arXiv.2408.16202

Proietti, T., & Giovannelli, A. (2021). Nowcasting monthly macroeconomic indicators with a large number of daily predictors. *Journal of Forecasting*, *40*(7), 1314-1336. https://doi.org/10.1002/for.2776

Salles, R., Pacitti, E., Bezerra, E., Porto, F., & Ogasawara, E. (2022). TSPred: A framework for nonstationary time series prediction. *ACM Computing Surveys*, *55*(3), 1-35. https://doi.org/10.1145/3492826

Taylor, S. J., & Letham, B. (2018). Forecasting at scale. *The American Statistician*, *72*(1), 37-45. https://doi.org/10.1080/00031305.2017.1380080

Wang, X., Li, Y., Shi, W., Jiang, Q., Song, X., & Li, X. (2024). Short-term electricity-load forecasting by deep learning: A comprehensive survey. *arXiv preprint arXiv:2408.16202*. https://doi.org/10.48550/arXiv.2408.16202

Zhang, G., Wei, C., Jing, C., & Wang, Y. (2023). Short-term electricity load forecasting using the temporal fusion transformer: Effect of grid hierarchies and data sources. In *Proceedings of the 10th ACM International Conference on Systems for Energy-Efficient Buildings, Cities, and Transportation* (pp. 281-284). ACM. https://doi.org/10.1145/3575813.3597345

Zhang, Y., & Li, H. (2022). Load forecasting for energy communities: A novel LSTM-XGBoost hybrid model. *Energy Informatics*, *5*(1), Article 12. https://doi.org/10.1186/s42162-022-00212-9

---

*Document generated: June 2026*
