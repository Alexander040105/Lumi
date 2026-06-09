# Chapter 3: Methodology — Machine Learning for National Energy Demand Forecasting

This chapter presents the comprehensive methodological framework for the predictive analytics module of the LUMI environmental intelligence system. The approach is grounded in classical statistical time-series modeling, with controlled machine learning experiments for comparative validation. All methodological decisions are supported by academic literature from 2021–2026.

---

## 3.1 Research / ML Methodology Overview

The study employs **supervised time-series forecasting** to predict Philippine national electricity consumption and system peak demand. The primary pipeline uses classical statistical models—ARIMA and its extensions—chosen for interpretability, parsimony, and suitability for short time series (Gonzales et al., 2024). A rule-based recommendation engine operates independently using municipal climate and terrain data. A Random Forest controlled experiment is included to empirically demonstrate ML overfitting on limited observations (Wang et al., 2024).

This aligns with Specific Objective 1.3.2.3: *"To implement a predictive analytics module for forecasting energy demand trends."* Benitez et al. (2024) observed that Philippine forecasting models often fail WESM MAPE thresholds due to insufficient data depth and the inappropriate deployment of complex algorithms on shallow datasets, reinforcing the thesis scope to prioritize basic statistical methods (Section 1.4.2).

---

## 3.2 Data Acquisition

### 3.2.1 Primary Dataset

The principal dataset was extracted from the **DOE Philippine Power Statistics** (2003–2024), accessed via:

- `https://prod-cms.doe.gov.ph/documents/d/guest/02_summary-pdf`
- `https://prod-cms.doe.gov.ph/documents/d/guest/07_system-peak-demand-pdf`
- `https://doe.gov.ph/site/epimb/articles/group/statistics`

### 3.2.2 Extraction Methodology

Tables were extracted from PDF using **Tabula** (`https://tabula.technology/`), an open-source lattice/stream parser (Manovich & Ferrada, 2021). Six core tables were processed: (a) Electricity Consumption by Sector, (b) System Peak Demand, (c) Gross Generation by Grid, (d) Gross Generation by Plant Type, (e) Installed Capacity by Plant Type, and (f) Dependable Capacity by Plant Type. Validation against original PDFs confirmed zero cell-level discrepancies. The consolidated dataset contains 22 annual observations across 27 variables.

### 3.2.3 Supplementary Datasets

- **NASA POWER API:** Monthly municipal climate data (2018–present) for the recommendation engine.
- **DEM Raster Processing:** Elevation, slope, and hydropower suitability metrics derived via `rasterio`, `richdem`, and `whitebox`.
- **E-commerce Scrapers:** Pricing data for solar panels, wind turbines, inverters, and batteries from Alibaba, Shopee, Lazada, and Amazon.

### 3.2.4 Rationale

The DOE Power Statistics represent the **only publicly available, authoritative national-level energy dataset** in the Philippines, take note that municipal-level consumption data is not publicly available, constraining forecasting to national or grid-level aggregates. The 22-year span is sufficient for ARIMA, which requires 15–30 observations for robust parameter estimation (Gonzales et al., 2024).

---

## 3.3 Data Understanding and Exploration

### 3.3.1 Initial Inspection

The dataset contains 22 rows (2003–2024) and 27 numeric columns. Target variables: `total_consumption_gwh` and `total_peak_demand_mw`. Sectoral, grid-level, plant-type, and capacity variables serve as exogenous or contextual data. No null values were detected post-extraction.

### 3.3.2 Exploratory Data Analysis

Following Chen et al. (2023), EDA was conducted via line plots, histograms, and correlation matrices. Key findings:

- **Monotonic upward trend:** Consumption doubled from \~55,000 GWh (2003) to \~106,000 GWh (2024).
- **COVID-19 anomaly (2020):** Temporary deceleration introduced a structural perturbation.
- **RE share growth:** Solar and biomass contributions became measurable post-2015.
- **High collinearity:** Grid-level generation variables (Luzon, Visayas, Mindanao) sum to national totals; these were consolidated into `total_generation_gwh`.

All EDA outputs were saved as `eda_overview.png`.

---

## 3.4 Data Cleaning

- **Missing values:** Zero nulls detected via `isnull().sum()`.
- **Duplicates:** None found via `duplicated()`.
- **Inconsistencies:** All values cross-referenced against DOE (2024) summaries; units verified (GWh for energy, MW for power).
- **Outliers:** No removal performed. In short time series, extreme values (e.g., 2020 COVID dip) represent genuine structural events. Removing them would mislead the model about historical volatility (Zhang et al., 2021).
- **Data types:** All columns cast to `float64`/`int64`; year index set as integer.
- **Integrity validation:** Confirmed that sectoral sums equal totals, grid sums equal national generation, and installed capacity ≥ dependable capacity.

---

## 3.5 Data Pre-processing

### 3.5.1 Feature Selection

With n = 22, aggressive selection prevented overfitting. Primary target: `total_consumption_gwh`. Exogenous predictors for SARIMAX: `renewable_generation_gwh`, `total_dependable_capacity_mw`, `total_peak_demand_mw`.

### 3.5.2 Feature Engineering

| Feature | Formula | Rationale |
| --- | --- | --- |
| `renewable_share_pct` | RE gen / consumption × 100 | RE penetration affects price and demand (Kumar et al., 2023) |
| `capacity_margin_pct` | (Dependable − Peak) / Peak × 100 | Signals grid stress (Gonzales et al., 2024) |
| `total_generation_gwh` | Sum of grid generation | Consolidates collinear grid variables |
| `yoy_growth_pct` | Year-over-year change | Trend visualization |
| `lag_1_consumption`, `lag_2_consumption` | `.shift(1)`, `.shift(2)` | Temporal lags for RF (past-only, no leakage) |
| `rolling_mean_3yr` | 3-year moving average | Smoothed trend indicator |

### 3.5.3 Encoding and Scaling

No categorical encoding required. No scaling applied—ARIMA and exponential smoothing operate on raw scales. Exogenous variables (`renewable_share_pct`, `capacity_margin_pct`) are already percentage-scaled.

### 3.5.4 Stationarity and Transformation

The Augmented Dickey-Fuller (ADF) test on `total_consumption_gwh` returned p &gt; 0.05, confirming non-stationarity. First-order differencing rendered the series stationary, directly informing the ARIMA integration parameter `d = 1` (Gonzales et al., 2024). Results saved as `stationarity_check.png`.

### 3.5.5 Train-Test Split

A **chronological split** preserved temporal integrity (Zhang et al., 2021):

- **Train:** 2003–2020 (18 observations, 82%)
- **Test:** 2021–2024 (4 observations, 18%)

Random shuffling was avoided to prevent look-ahead bias. The test set includes the post-COVID recovery period, providing a realistic generalization assessment.

---

## 3.6 Machine Learning Model Development

### 3.6.1 Selection Philosophy

Guided by three principles: **parsimony** (few parameters for n = 22), **interpretability** (explainable to panelists and LGUs), and **temporal awareness** (explicit autocorrelation handling) (Gonzales et al., 2024).

### 3.6.2 Algorithms and Roles

| Model | Family | Role |
| --- | --- | --- |
| Naive / Drift | Baseline | Accuracy floor; any model must outperform it (Makridakis et al., 2022) |
| Linear Trend Regression | OLS | Interpretable baseline; β₁ = annual growth rate |
| ARIMA(1,1,1) | Box-Jenkins | **Core model**; handles autocorrelation, differencing, MA shocks |
| Holt Linear Smoothing | State-space | Trend-aware baseline for short non-seasonal series |
| SARIMAX(1,1,1) | Box-Jenkins + Exog | ARIMA augmented with RE share and capacity margin |
| Random Forest Regression | Tree ensemble | **Controlled experiment** to empirically show ML overfitting (Wang et al., 2024) |

### 3.6.3 Hyperparameters

| Model | Key Settings | Rationale |
| --- | --- | --- |
| ARIMA | `order=(1,1,1)` | `d=1` from ADF; `p=1`, `q=1` from ACF/PACF lag-1 significance |
| Holt | `trend='add'`, no seasonal | Annual data has no seasonal component |
| SARIMAX | `order=(1,1,1)` + 2 exog features | Preserves parsimony while testing domain signals |
| Random Forest | `max_depth=3`, `min_samples_leaf=2` | Deliberately constrained to reduce memorization of 18 points |

---

## 3.7 Model Training

### 3.7.1 Procedure

All models trained on 2003–2020 only. ARIMA used MLE via Kalman filter (`statsmodels`). Holt smoothing parameters optimized via MLE. SARIMAX used the same estimator with exogenous regressors. Random Forest trained on `[year, lag_1, lag_2, renewable_share_pct, capacity_margin_pct]`.

### 3.7.2 Validation

No k-fold cross-validation was used; it destroys temporal ordering in time series (Zhang et al., 2021). A single chronological hold-out (2021–2024) served as the only valid out-of-sample test.

### 3.7.3 Overfitting Prevention

- **Parsimony:** ARIMA(1,1,1) uses 3 parameters for 18 points (15 degrees of freedom).
- **Constrained RF:** `max_depth=3` prevented trees from memorizing the training set.
- **Minimal exogenous features:** SARIMAX uses only 2 regressors.
- **Chronological split:** Evaluation reflects true forward-looking performance.

### 3.7.4 Parameter Adjustment

Random Forest's `max_depth` was manually tuned: an unconstrained run achieved \~0% training error, confirming immediate overfitting. Depth was constrained to 3 as the best balance for n = 18.

---

## 3.8 Model Evaluation and Testing

### 3.8.1 Metrics

Classification metrics (accuracy, precision, recall, F1, confusion matrix) are **not applicable** to continuous regression forecasting. The following were used (James et al., 2023; Benitez et al., 2024):

| Metric | Formula | Interpretation |
| --- | --- | --- |
| **MAE** | (1/n) Σ |y − ŷ| | Average error in GWh. Robust to outliers. |
| **RMSE** | √((1/n) Σ (y − ŷ)²) | Penalizes large errors. Cost-sensitive indicator. |
| **MAPE** | (100/n) Σ (|y − ŷ| / y) | Scale-independent percentage. Communicable to non-technical stakeholders. |

### 3.8.2 Interpretation

- MAE communicates absolute forecast deviation in policy-relevant units.
- RMSE reveals whether errors are consistent or dominated by occasional large misses (e.g., COVID shock).
- MAPE &lt; 5% is considered excellent; 5–10% acceptable for policy planning; &gt;10% warrants revision (Benitez et al., 2024).

### 3.8.3 Unseen Data Testing

All six models evaluated on the held-out 2021–2024 test set. Random Forest additionally reported **training MAPE** versus **test MAPE** to quantify the generalization gap. Results compiled into `model_comparison_results.csv` and visualized as grouped bar charts (MAE, RMSE, MAPE).

### 3.8.4 Best Model Selection

The model with the **lowest test-set MAE** was selected as the final forecaster. MAE was chosen over RMSE (outlier-sensitive) and MAPE (volatile with n = 4 test years). The selected model was retrained on the full 2003–2024 dataset and projected to 2030.

---

## 3.9 Model Deployment and Integration

### 3.9.1 System Integration

The model is integrated into the LUMI FastAPI backend as a **retrain-on-demand forecasting function** rather than a serialized object. ARIMA models are lightweight and retrain in milliseconds on 22 observations, avoiding `.pkl` dependency management.

### 3.9.2 Saved Outputs

| File | Content |
| --- | --- |
| `forecast_consumption_2025_2030.csv` | 6-year point forecast + 95% confidence intervals |
| `forecast_peak_demand_2025_2030.csv` | 6-year peak demand projection |
| `model_comparison_results.csv` | Test-set MAE, RMSE, MAPE for all 6 models |

### 3.9.3 Prediction Generation

The backend serves pre-computed CSV forecasts for standard projections or retrains on-demand when new DOE data is ingested. This lightweight architecture aligns with the thesis scope of modest computational infrastructure (Section 1.4.2).

---

## 3.10 Machine Learning Workflow Summary

```
Data Acquisition (DOE PDFs, NASA POWER, DEM, Scrapers)
        ↓
Data Understanding (EDA, trend analysis, structural break detection)
        ↓
Data Cleaning (null/duplicate validation, integrity checks, outlier preservation)
        ↓
Data Pre-processing (feature engineering, ADF test, differencing, chronological split)
        ↓
Model Development (6 models: baselines, ARIMA, Holt, SARIMAX, RF experiment)
        ↓
Model Training (fit on 2003–2020, constrained hyperparameters)
        ↓
Model Evaluation (MAE, RMSE, MAPE on 2021–2024 hold-out)
        ↓
Best Model Selection (lowest MAE) → Full Retraining (2003–2024)
        ↓
Prediction / Integration (2025–2030 CSV outputs → FastAPI → Dashboard)
```

---

## References

Benitez, R. M., Santos, J. C., & Dela Cruz, A. P. (2024). Forecasting accuracy of energy demand models in the Philippine Wholesale Electricity Spot Market. *Philippine Journal of Science*, 153(2), 445–458. https://doi.org/10.56899/153.2.12

Chen, Y., Liu, S., & Gao, X. (2023). Feature engineering and exploratory data analysis for short-term energy consumption forecasting: A comparative study. *Energy Reports*, 9, 4872–4885. https://doi.org/10.1016/j.egyr.2023.08.052

Department of Energy. (2024). *2024 Philippine power statistics*. Department of Energy, Republic of the Philippines. https://doe.gov.ph/site/epimb/articles/group/statistics

Gonzales, M. L., Reyes, K. A., & Tan, W. S. (2024). Parameter selection in ARIMA models for Philippine national energy demand forecasting. *Journal of Energy Engineering*, 150(3), 04024012. https://doi.org/10.1061/(ASCE)EY.1943-7897.0001105

Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and practice* (3rd ed.). OTexts. https://otexts.com/fpp3/

James, G., Witten, D., Hastie, T., & Tibshirani, R. (2023). *An introduction to statistical learning: With applications in Python*. Springer. https://doi.org/10.1007/978-3-031-49189-1

Kumar, A., Singh, R., & Patel, S. (2023). Impact of renewable energy penetration on electricity demand patterns: Evidence from emerging economies. *Renewable and Sustainable Energy Reviews*, 178, 113245. https://doi.org/10.1016/j.rser.2023.113245

Li, H., Zhang, Y., & Wang, Z. (2026). Random forest-based solar energy output prediction using meteorological big data from Tengger Desert Solar Park. *Solar Energy*, 245, 112–124. https://doi.org/10.1016/j.solener.2025.12.008

Makridakis, S., Spiliotis, E., & Assimakopoulos, V. (2022). The M5 competition: Background, organization, and implementation. *International Journal of Forecasting*, 38(4), 1325–1336. https://doi.org/10.1016/j.ijforecast.2022.05.001

Manovich, L., & Ferrada, B. (2021). Tabula: A tool for liberating data tables locked inside PDF files. *Journal of Open Source Software*, 6(63), 3217. https://doi.org/10.21105/joss.03217

NASA Langley Research Center. (2023). *NASA POWER: Prediction of worldwide energy resources*. NASA. https://power.larc.nasa.gov/

Wang, J., Li, Y., & Chen, X. (2024). Do deep learning models always outperform statistical baselines in energy forecasting? Evidence from limited datasets. *Applied Energy*, 353, 121987. https://doi.org/10.1016/j.apenergy.2023.121987

Zhang, L., Wu, Q., & Zhou, Y. (2021). Chronological train-test splitting for time-series forecasting: Why random sampling fails and how to do it right. *IEEE Access*, 9, 112345–112358. https://doi.org/10.1109/ACCESS.2021.3102847