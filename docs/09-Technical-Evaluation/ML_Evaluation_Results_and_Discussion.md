# Machine Learning Evaluation: Results and Discussion

**Title:** Machine Learning Evaluation of the LUMI Energy Forecasting and AI Recommendation Components
**Project:** LUMI — Data-Driven Environmental Intelligence System
**Evaluation date:** 2026-09-15 (fresh re-execution); historical baseline September 5–8, 2026
**Evaluator:** Automated evaluation executed in-repository by Devin (scripts, commands, and raw artifacts listed in Appendix A)

> **Scope note.** Per stakeholder instruction this report covers (a) the **ARIMA(1,1,1) statistical forecasting pipeline** and its five comparison models, and (b) the **Groq LLM recommendation layer** evaluated as a generative-AI component (not a predictive ML model). A geothermal-suitability `RandomForestClassifier` exists in `geothermal/ml_classifier.py` but was excluded from scope by the stakeholder. Classification-oriented worksheet items (confusion matrix, per-class precision/recall/F1, ROC-AUC) are **not applicable to a continuous regression/forecasting target**; where the worksheet asks for them, this report states that explicitly and supplies the correct time-series substitutes (directional-accuracy 2×2 matrix, per-model regression metrics, expanding-window cross-validation, prediction-interval coverage).

---

## 4. Results and Discussion

### 4.1 Dataset Characteristics

**Source.** Philippine Department of Energy (DOE) national energy statistics, preprocessed into `data/DOE_Data_Extracted/data_v2_preprocessed/master_preprocessed.csv`. The file is the single modeling table used by the forecasting pipeline.

**Measured profile** (`artifacts/rerun-2026-09-15/ml/dataset_profile.json`, recomputed 2026-09-15):

| Property | Value |
|---|---|
| Rows | **23** (one record per year) |
| Columns | **45** |
| Coverage | **2003–2025** (annual) |
| Duplicate rows | **0** |
| Missing cells | **15**, all confined to derived lag/difference/rolling columns (`total_consumption_diff1`, `total_peak_demand_diff1`, `renewable_generation_diff1`, `consumption_yoy_growth`, `peak_yoy_growth`, `consumption_lag1/2`, `peak_lag1`, `consumption_roll3`, `consumption_roll5`) — structurally expected, since the earliest years have no prior-year window |
| Primary target | `total_consumption_gwh` — range **52,941 → 126,941 GWh** |
| Secondary targets | `total_peak_demand_mw`, `renewable_generation_gwh` |
| Derived features | YoY growth, lag-1/lag-2, 3- and 5-yr rolling means, capacity margin, renewable share %, years-since-2003 index |
| Consumption CAGR 2003–2024 | **4.252%** |
| Mean absolute YoY change | **4.492%** (max +10.17%, min −4.04%) |

**Split (as implemented in the evaluation pipeline):**

| Subset | Years | Samples | Share of 2003–2024 |
|---|---|---|---|
| Training | 2003–2020 | **18** | 81.8% |
| Held-out test | 2021–2024 | **4** | 18.2% |
| Out-of-sample (2025) | 2025 | 1 | excluded from historical test metrics |
| **Total modeling rows** | 2003–2025 | **23** | — |

**Discussion (Result → Meaning → Comparison → Explanation → Implication).** The dataset contains 23 annual observations covering 2003–2025, of which 22 rows (2003–2024) were usable for the historical train/test protocol. This is an extremely small sample by machine-learning standards, which is the dominant methodological constraint of this evaluation: it rules out data-hungry learners, makes every test-set observation carry 25% of the reported error, and forces reliance on time-series-appropriate validation rather than large held-out sets. The missing values are concentrated in derived lag/rolling columns for the earliest years and are an inherent consequence of lagging a short series, not a data-quality defect. The 2025 row is retained in the file but excluded from the 2021–2024 test computation so the reported metrics remain comparable to the pipeline's documented protocol.

### 4.2 Data Preprocessing Results

Observed preprocessing, verified against `master_preprocessed.csv` and the pipeline code:

| Step | Applied? | Evidence / why |
|---|---|---|
| Temporal alignment to annual records | Yes | 23 rows, one per year, no gaps or duplicates |
| Missing-value handling | Structural | The 15 NaNs exist only where lags/rolling windows reach before 2003; lag/rolling features are used only by the ML baselines, and models that need them either drop the affected rows or accept NaN-free windows |
| Feature engineering | Yes | Lag-1/2, diff-1, YoY growth, 3/5-yr rolling means, `years_since_2003`, capacity margin, renewable share — created to give the baselines autoregressive structure that the statistical models derive internally |
| Differencing for stationarity | Yes — inside ARIMA | The `d=1` term performs first-order differencing on the strongly trended series (CAGR 4.25%) rather than pre-differencing the file |
| Categorical encoding | N/A | No categorical predictors; all features are continuous annual aggregates |
| Feature scaling | Not applied | Justified: Linear Trend, ARIMA, Holt, Naive-drift are scale-invariant or univariate; Random Forest is tree-based and does not require scaling |
| Augmentation | Not used | Not applicable to annual national statistics; no synthetic years were fabricated |

**Discussion.** Preprocessing is deliberately minimal because the data are already clean national aggregates; the meaningful work is the construction of autoregressive features for the comparison models and the internal differencing performed by ARIMA's `d=1`. Not applying scaling is correct here — imposing it would add a step without changing any evaluated model's behavior.

### 4.3 Model Development and Training

**Models evaluated** (all re-executed on 2026-09-15 by `artifacts/scripts/evaluate_forecasting_models.py`):

| Model | Type | Configuration |
|---|---|---|
| **ARIMA(1,1,1)** — production model | Statistical time-series | order (1,1,1), selected by AIC grid (see §4.10); statsmodels `ARIMA` |
| Linear Trend Regression | Baseline | OLS of consumption on `years_since_2003` |
| Naive with Drift | Baseline | Random-walk-with-drift extrapolation |
| Holt Linear Smoothing | Statistical | `ExponentialSmoothing(trend='add')` |
| SARIMAX(1,1,1) + Exog | Statistical + exogenous | ARIMA errors with exogenous regressors |
| Random Forest Regression | ML baseline | `RandomForestRegressor` on engineered lag/rolling features |

**Production serving note.** `fastapi-backend/app/ml/predictor.py` does **not** retrain per request; it loads precomputed forecast CSVs (`forecast_consumption_2025_2030.csv`, model comparison artifacts) and serves stored ARIMA point forecasts with confidence intervals. Training cost is therefore an offline concern, not a latency concern.

### 4.4 Training and Validation Performance

**Fit times (measured, `latency_and_size.json`):**

| Model | Fit time (s) |
|---|---|
| Linear Trend Regression | 0.0374 |
| Naive with Drift | 0.00005 |
| Holt Linear Smoothing | 0.0160 |
| **ARIMA(1,1,1)** | **0.0859** |
| SARIMAX(1,1,1) + Exog | 0.0704 |
| Random Forest Regression | 0.1026 |

There are no iterative epochs or train/validation loss curves — none of these are gradient-trained models. The closest analogue to a "training curve" for ARIMA is the in-sample fit quality and residual diagnostics:

- ARIMA(1,1,1) parameters: `ar.L1 ≈ 0.9999`, `ma.L1 ≈ −0.9972`, `σ² ≈ 1.032×10⁷`; AIC **325.63**, BIC **328.13**.
- Ljung–Box test on residuals at lag 5: statistic **0.258**, p = **0.9984** → no evidence of residual autocorrelation; the model captured the serial structure it was designed for.
- The near-unity AR coefficient paired with a near-cancelling MA coefficient is the classic signature of a model sitting close to a random-walk-with-drift — consistent with ARIMA performing on par with (slightly worse than) the naive-drift baseline on the test set.

**Discussion.** Fit times are all under ~0.11 s; training cost is a non-issue at this data size. The residual diagnostics indicate a statistically adequate in-sample fit (white-noise residuals), yet the parameter values warn that the fitted process is barely distinguishable from a drifted random walk — which foreshadows the test-set result that simpler trend/drift methods match or beat it.

### 4.5 Model Performance on the Test Dataset

The worksheet's classification metrics — accuracy, precision, recall, F1, ROC-AUC — are **not applicable**: the target is a continuous quantity (GWh), not a class. The correct metrics for this problem are MAE, RMSE, MAPE, and R², plus direction-of-change accuracy as a classification-style substitute.

**Held-out test results, total consumption 2021–2024** (`model_metrics_consumption.csv`):

| Model | MAE (GWh) | RMSE (GWh) | MAPE (%) | R² |
|---|---:|---:|---:|---:|
| **Linear Trend Regression** | **5,993.83** | **7,342.10** | **4.965** | **0.1054** |
| Holt Linear Smoothing | 6,557.72 | 7,997.68 | 5.435 | −0.0615 |
| Naive with Drift | 6,709.32 | 8,128.45 | 5.566 | −0.0965 |
| ARIMA(1,1,1) | 6,829.09 | 8,257.12 | 5.667 | −0.1315 |
| Random Forest Regression | 13,118.37 | 15,349.45 | 10.937 | −2.9099 |
| SARIMAX(1,1,1) + Exog | 16,721.10 | 18,787.73 | 14.031 | −4.8577 |

**Secondary targets** (same protocol):

| Target | Best model | Best MAPE | ARIMA MAPE |
|---|---|---:|---:|
| `total_peak_demand_mw` | SARIMAX + Exog | 3.868% (R²=0.4124) | 5.611% |
| `renewable_generation_gwh` | Linear Trend / Holt | 9.405% | 13.665% |

**Per-year held-out errors — ARIMA(1,1,1)** (`forecast_vs_actual.csv`):

| Year | Actual (GWh) | Predicted | Residual | % err |
|---|---:|---:|---:|---:|
| 2021 | 106,115 | 104,579.7 | 1,535.3 | −1.45% |
| 2022 | 111,516 | 107,403.3 | 4,112.7 | −3.69% |
| 2023 | 118,004 | 110,226.7 | 7,777.3 | −6.59% |
| 2024 | 126,941 | 113,049.9 | 13,891.1 | −10.94% |

**Directional accuracy (substitute for classification accuracy):**

| Model | Correct direction calls | Rate |
|---|---|---|
| ARIMA(1,1,1) | **8 / 11** fold+test years | **72.7%** |
| Linear Trend (CV) | 3 / 7 | 42.9% |
| Linear Trend Regression (test) | 2 / 4 | 50.0% |

**Discussion.** *Result:* ARIMA(1,1,1) achieved MAPE 5.667% / MAE 6,829 GWh on the held-out years — the **fourth-best** of six models, behind Linear Trend (4.965%), Holt (5.435%), and Naive-drift (5.566%). *Meaning:* in absolute terms all top-four models err by roughly 5–6% of annual national consumption (~5,000–8,000 GWh) — respectable for a 4-year-ahead horizon. *Comparison:* every model under-forecast every test year, and errors grow monotonically with horizon (ARIMA: −1.45% → −10.94%); actual consumption grew faster than any model's extrapolated trend. *Explanation:* the test years coincided with accelerating post-2020 demand growth (the 2024 actual of 126,941 GWh is the series maximum), which purely extrapolative methods trained on 2003–2020 systematically underestimate; R² is near zero or negative for five of six models because with only four test points the variance of the test mean is tiny and cumulative under-forecasting dominates. *Implication:* ARIMA's raw point accuracy does not currently justify its position as the sole production model on accuracy grounds alone — its retained advantages are statistical structure and native prediction intervals (§4.8, §4.15); the honest conclusion is that **forecast accuracy on 2021–2024 is modest and direction-of-growth is captured, but magnitude of acceleration is not**.

### 4.6 Confusion Matrix Analysis

A conventional classification confusion matrix is **not applicable** — there are no classes. As the closest valid substitute, a **directional 2×2** was computed from `directional_confusion.csv` (ARIMA, unique years 2015–2024, CV folds + test):

| Actual \ Predicted | Up | Down |
|---|---|---|
| **Up** | 7 | 2 |
| **Down** | 1 | 0 |

**Discussion.** ARIMA called the correct direction in 8 of 10 unique years (80% on de-duplicated years; 72.7% counting the duplicated 2021 fold row reported by the script). The telling cells are the two 2023–2024 "predicted-down / actual-up" misses — the model anticipated a slowdown exactly when demand accelerated — and the single 2020 false-up (actual −4.04% pandemic-year contraction, the only down year in the dataset, predicted up). Both error classes are consistent: the model cannot anticipate regime changes that have no precedent in 18 training years.

### 4.7 Class-Level Performance

Per-class precision/recall/F1 are **not applicable** to regression. The structurally equivalent breakdown is **per-target performance** (§4.5 tables): the same ARIMA(1,1,1) specification performs very differently across targets — 5.667% MAPE on consumption, 5.611% on peak demand, and 13.665% on renewable generation — because the renewable-generation series is more volatile and structural-break-prone. *Implication:* a single fixed order is a reasonable default for the smooth consumption/demand aggregates but a poor choice for the renewable share series; per-target order selection is a concrete improvement path.

### 4.8 ROC-AUC / PR-AUC

**Not applicable** — ROC and PR curves require a classification decision threshold over class probabilities; the task is point forecasting of a continuous target. The deployment-relevant analogue is **prediction-interval coverage**: the ARIMA 95% intervals covered **3 of 4** held-out test points (75% empirical coverage, `summary.json` → `picp_95pct_test`), with 2024 — the acceleration year — falling outside the band. *Implication:* intervals are slightly overconfident under regime acceleration, exactly the condition in which point forecasts also degrade; coverage should be rechecked whenever the test window includes a structural break.

### 4.9 Cross-Validation Results

Expanding-window time-series cross-validation (7 folds; random k-fold would leak future information and was correctly not used) — absolute % error (`cv_summary.csv`):

| Model | Folds | Mean APE | Std dev |
|---|---|---:|---:|
| Holt | 7 | **3.525%** | 3.496% |
| Naive w/ Drift | 7 | 3.584% | 2.535% |
| **ARIMA(1,1,1)** | 7 | **3.607%** | **2.512%** |
| Linear Trend | 7 | 5.861% | 3.917% |

**Discussion.** *Result:* across folds the top three methods are statistically indistinguishable (means within 0.09 pp of each other), while Linear Trend is clearly worse in CV despite winning the single 4-year test split. *Meaning:* the single-split leaderboard in §4.5 is not stable evidence — the model ranking flips under resampling. *Implication:* model selection should not rest on the 4-point test alone; ARIMA's CV showing (competitive mean, lowest-magnitude deviation alongside Naive-drift) is the fairer justification for keeping it, provided intervals remain calibrated.

### 4.10 Comparative Evaluation

Consolidated consumption leaderboard (fresh 2026-09-15 run):

| Rank | Model | MAPE | Key differentiator |
|---|---|---:|---|
| 1 | Linear Trend | 4.965% | Best on this split; worst in CV (5.861%) — split-lucky |
| 2 | Holt | 5.435% | Best CV mean; consistent performer |
| 3 | Naive + Drift | 5.566% | Near-free, hard to beat |
| 4 | **ARIMA(1,1,1)** | **5.667%** | Only model emitting calibrated intervals; top-tier CV |
| 5 | Random Forest | 10.937% | 18 training rows ≪ RF's data appetite |
| 6 | SARIMAX + Exog | 14.031% | Exog regressors extrapolated poorly |

**Discussion.** The proposed production model does **not** dominate the baselines on point accuracy; no honest reading of these tables can claim that. Its case rests on three pillars the baselines lack: (a) a likelihood-based fit with diagnostic testing (§4.4), (b) native prediction intervals used by the API's `ci_lower`/`ci_upper` fields, and (c) CV performance equal to the best baselines. SARIMAX's failure on consumption (14.0%) alongside its win on peak demand (3.87%) shows exogenous-regressor value is target-dependent — worth revisiting per-target, not globally. Random Forest's −2.91 R² confirms tree ensembles are inappropriate at n=18.

### 4.11 Hyperparameter Analysis

ARIMA order selection — AIC grid over p,d,q ∈ {0,1,2} with d=1 (`aic_grid.csv`):

| Order | AIC | BIC |
|---|---:|---:|
| **(1,1,1)** | **325.63** | **328.13** |
| (2,1,1) | 327.47 | 330.80 |
| (1,1,2) | 329.13 | 332.46 |
| (2,1,2) | 331.01 | 335.17 |
| (0,1,0) | 332.49 | 333.32 |
| (1,1,0) | 332.82 | 334.49 |
| (0,1,1) | 332.92 | 334.58 |
| (0,1,2) | 334.29 | 336.79 |
| (2,1,0) | 334.36 | 336.86 |

**Discussion.** The (1,1,1) order is not an arbitrary choice — it is the AIC/BIC-optimal order within the searched 3×3 grid, 1.8 AIC points ahead of the next candidate. However, d was fixed at 1 and seasonal orders were not searched (annual data ⇒ no within-year seasonality), so the grid is appropriate but narrow; a wider order/search space and per-target selection remain open improvements.

### 4.12 Feature Importance / Explainability

ARIMA is interpretable through its fitted parameters rather than feature importances: `ar.L1 ≈ 1.00` means next year's level ≈ this year's level plus drift; `ma.L1 ≈ −1.00` means shocks are absorbed almost fully within one step — together describing a smooth-trend process with fast shock decay. For the Random Forest baseline, scikit-learn `feature_importances_` is available in the evaluation script's model object; its dominant features are `consumption_lag1` and the rolling means, i.e., it predicts almost purely from recent level — the same information ARIMA uses — but with 18 rows it cannot learn more than memorization, explaining its 10.9% MAPE. SHAP/LIME were not applied: at n=18 with <10 features they would add machinery without adding insight.

### 4.13 Error Analysis

| Error pattern | Frequency | Likely cause |
|---|---|---|
| Under-forecast magnitude (all 6 models, all 4 test years) | 24/24 model-year pairs | Post-2020 demand acceleration absent from 2003–2020 training window |
| Error growth with horizon | Monotone −1.45% → −10.94% (ARIMA) | Multi-step extrapolation compounds trend miss |
| Direction miss on growth years | 2/4 test years predicted "down" vs actual "up" | Near-unit-root fit reverts toward mean growth |
| 2020 downturn predicted "up" | 1/1 down-year | Single negative year in 18 cannot teach contraction behavior |
| SARIMAX severe under-shoot (−22.8% by 2024) | 4/4 years | Exogenous regressors extrapolated worse than the target trend |
| RF flat-lining (~102–103k every year) | 3/4 years | Trees cannot extrapolate beyond the training range — they predict the mean of seen leaves |

**Discussion.** Every model failed in the *same direction* — under-prediction — which indicates the dominant error source is the **data regime**, not model specification. The practical consequence: any purely-extrapolative model on this series will under-predict accelerating demand; adding exogenous drivers (electrification policy, economic growth) or retraining on shorter recent windows are the plausible fixes.

### 4.14 Robustness and Generalization

- **Perturbation robustness** (`robustness_perturbation.csv`): 30 runs with small input perturbations → MAPE mean **5.707%**, std **0.155%**, range **5.279–6.068%**. The model is stable under input noise — no chaotic sensitivity.
- **Generalization caveats:** the single held-out window (2021–2024) is one contiguous block during an acceleration regime — a favorable test would show different numbers. There is **no external validation dataset** (no second country's series, no held-out region). Temporal generalization is partially supported by CV stability, but genuine external validity is unestablished.

### 4.15 Statistical Significance

A Diebold–Mariano-style comparison of ARIMA vs Linear Trend absolute-error losses on the test set (`dm_test.json`): statistic **3.532**, normal-approximation p ≈ **0.0004**, n = **4**. The evaluation script itself flags the caveat: **with n=4 the test has essentially no power and the nominal p-value must not be read as a real significance result.** No other significance testing was performed, because no defensible test exists at this sample size; the honest statement is that model differences on this test set are **not statistically established** — they are descriptive only. This is a limitation of the data, remediable only by more granular (monthly/quarterly) observations.

### 4.16 Practical/Deployment Performance

| Metric | ARIMA(1,1,1) | Random Forest |
|---|---:|---:|
| 6-step forecast latency (mean) | **0.97 ms** | 9.93 ms |
| Serialized size (joblib) | **93.6 KB** | 181.6 KB |
| Fit time | 0.086 s | 0.103 s |

Serving reality is even cheaper: `predictor.py` reads precomputed CSVs, so production inference is a file read, not model execution. Deployment-wise ARIMA is unambiguously suitable — sub-millisecond, ~94 KB, no GPU. The real deployment risks are not compute but **staleness** (forecasts don't update until the CSV artifacts are regenerated) and the new authentication gate on `/forecast/*` routes changing previously-public behavior (see System Testing Report §8).

### 4.17 Comparison With Related Studies

Direct numeric comparison to published Philippine-demand forecasting studies was **not executable**: no benchmark table from an external study exists in the repository, and fabricating one would violate this report's ground rules. The internal reference point is the repository's own prior evaluation (`docs/04-ML-Data-Science/ML_MODEL_EVALUATION_SUMMARY.md`), whose stored `model_comparison_results.csv` marked the SARIMAX and Random Forest rows *"placeholder — model not executed."* This fresh run replaced those placeholders with real numbers — and found both models substantially worse than the placeholders implied — which is itself a reportable finding: **earlier documentation contained unaudited placeholder metrics that overstated pipeline completeness.** (See System Testing Report, defect table.)

### 4.18 Limitations

1. **Tiny sample:** 18 training / 4 test annual points; each test point = 25% of reported error.
2. **No statistical power:** n=4 renders the DM test decorative; differences are descriptive.
3. **Regime mismatch:** training window predates post-2020 demand acceleration → systematic under-forecasting in every model.
4. **No external validation:** single national series, single country, single contiguous test block.
5. **Documentation drift found:** stored comparison CSV contained "placeholder — model not executed" rows later contradicted by real runs.
6. **Univariate modeling:** consumption is forecast from its own history; policy/economic drivers are not inputs.
7. **Fixed (1,1,1) order across targets** despite demonstrably different series behavior (renewables MAPE 13.7% vs consumption 5.7%).
8. **Interval coverage below nominal** (75% vs 95%) under the acceleration regime.
9. **Served forecasts are static artifacts** — freshness depends on pipeline re-runs, not the model itself.

### 4.19 Implications

- *Theoretical:* with 18 observations, model complexity is bounded by information content — the naive-drift/ARIMA equivalence observed is exactly what time-series theory predicts for a smooth trended series.
- *Practical:* the system's forecasts are usable as directional/trend guidance (5–7% error, correct growth direction in most years) but should not be presented to users as precise planning numbers without interval context — which the API already emits and should display prominently.
- *Organizational:* the placeholder-metric discovery shows evaluation artifacts need the same audit discipline as code; a metrics file is a claim, not evidence.
- *Technical roadmap:* (a) per-target order selection, (b) move to monthly data if DOE publishes it (the single highest-leverage improvement — it multiplies n by 12), (c) add exogenous demand drivers where SARIMAX showed target-specific promise, (d) schedule artifact regeneration so served forecasts can't silently go stale.

### 4.19b Overall Synthesis

The ARIMA(1,1,1) production forecaster is a **reasonable but not demonstrably optimal** choice: it loses the 4-point test to a straight line (5.67% vs 4.97% MAPE), ties the best baselines in cross-validation (3.61%), is diagnostically sound (white-noise residuals), uniquely provides prediction intervals (75% empirical coverage — slightly underconfident), and is deployment-trivial (0.97 ms, 94 KB). Its errors are honest, stable under perturbation (±0.16 pp), and shared by every comparator — the binding constraint is the dataset, not the model. The truthful verdict: **fit for purpose as a trend-extrapolation service, provided its intervals and limitations are surfaced to users; not a precision planning instrument.**

---

## 4.20 Generative AI Component: Groq LLM Evaluation

The Groq integration (`app/services/llm_client.py`, `groq_client.py`; default model `groq/compound-mini`, `LLM_PROVIDER=groq`) is a **generative recommendation layer**, evaluated on its own correct criteria — latency, output contract compliance, resilience — not regression metrics. Live evaluation: `artifacts/scripts/llm_groq_eval.py` → `artifacts/rerun-2026-09-15/llm/llm_eval.json`.

| Metric | Result | Evidence |
|---|---|---|
| Renewable-analysis calls | n = 6, **100%** non-empty, sanitizer-survival 100%, required headers (`## Observation/Interpretation/Recommendation`) 100%, prescriptive-content extraction 100% | `llm_eval.json → runs[]` |
| Latency | min 4,166.8 ms · mean **7,076.1 ms** · median 5,052.3 ms · p95 5,588.6 ms · max **18,468.7 ms** | `latency{}` |
| Token usage sample | `groq/compound-mini`: 571 prompt + 450 completion = **1,021 tokens**, 2,028.6 ms | `token_usage_sample` |
| JSON-mode probe | n = 4, **0% valid JSON, 0% schema compliance**, mean 2,217.8 ms | `json_mode` |
| Gemini→Groq fallback | Injected Gemini failure → Groq responded in **1,919.7 ms** | `fallback` |
| Hard timeout | 0.5 s budget → elapsed **504.1 ms**, returned empty string (caller-side fallback path verified) | `timeout_path` |

**Discussion.** *Result:* the recommendation path is functionally reliable — every live call produced sanitized, correctly-structured markdown with extractable prescriptive content — but **slow**: ~5 s typical, ~7 s mean, with an 18.5 s outlier that dominates user-perceived latency on AI features. *Meaning:* for an interactive product, median ~5 s AI responses are acceptable only with streaming/progressive UX; the frontend's retry/status-polling work (git log `53649f4`) is justified by exactly this tail. *Comparison:* the 0% JSON-validity figure is **expected behavior, not a defect**: the live renewable-analysis prompt asks for markdown sections, so plain-prose output is the correct contract — but it exposes a **documentation/code mismatch**, since `groq_client.py` comments claim Groq forces JSON output; downstream consumers must not assume JSON (see defect table). *Explanation:* the fallback (Gemini fail → Groq answer in <2 s) and timeout (504 ms → empty string → caller fallback) paths both behaved as designed, matching the historical failure-matrix verdict of GRACEFUL. *Implication:* the LLM layer is production-sound in contract and resilience; its risks are (a) latency tail, (b) one configured fallback model (`qwen/qwen3.6-27b`) returning HTTP 404 model-not-found for this account — a live configuration defect — and (c) token/latency cost of ~1,000-token responses on every AI feature call.

---

## Appendix A — What was actually executed (evidence index)

All paths relative to `docs/09-Technical-Evaluation/artifacts/`:

| Command / script | Output artifacts |
|---|---|
| `python artifacts/scripts/evaluate_forecasting_models.py` (created for this evaluation; runs all 6 models, CV, DM test, robustness, latency, size, AIC grid) | `rerun-2026-09-15/ml/{summary.json, model_metrics_*.csv, cv_*.csv, dm_test.json, directional_confusion.csv, forecast_vs_actual.csv, residuals_test.csv, aic_grid.csv, robustness_perturbation.csv, latency_and_size.json, forecast_plot.png, dataset_profile.json, run_log.txt}` |
| `python artifacts/scripts/llm_groq_eval.py` (created; live Groq calls with `.env` loaded) | `rerun-2026-09-15/llm/{llm_eval.json, prompt_and_response_snippets.json, run_log.txt}` |
| pandas dataset profiling (one-liner) | `ml/dataset_profile.json` + values quoted in §4.1 |

Environment: Python 3.13.2 venv (`fastapi-backend/.venv`), statsmodels 0.14.6, scikit-learn 1.9.0, pandas 3.0.5, groq 0.18.0; i5-8400, 8 GB RAM, Windows 11 Pro for Workstations.

**Historical evidence referenced (not re-generated):** `TECHNICAL_EVALUATION_ALL_RESULTS.md` (Sept 5–8 session), `data/DOE_Data_Extracted/data_v2_preprocessed/model_comparison_results.csv` (contained the placeholder rows this run superseded).
