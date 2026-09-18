# **Title :** Machine Learning Evaluation of the LUMI Energy Forecasting and AI Recommendation Components

Group Name : \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
Technical Evaluators ( IT Experts ) \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
Evaluation Date : \_\_\_\_\_\_\_\_\_\_\_\_   Form Version : 2.0 (worksheet-format, adapted to LUMI)

# **Machine Learning Evaluation: Results and Discussion — LUMI Answer Form**

> **How to use this form.** This form mirrors the source worksheet's numbering 1–20 so each section can be tracked against it directly. **Pre-filled cells contain verified repository facts** — leave them as-is unless the underlying code or data changed. **Blank cells (`____`)** are yours to complete — from your own analysis, panel input, or by re-running the instruments listed in Section 22.
>
> **Adaptation note (applies throughout).** The worksheet was written for classification models — models that sort items into categories. LUMI's model predicts an **amount** (gigawatt-hours of electricity), so classifier-specific fields (confusion matrix, per-class scores, ROC-AUC) carry the correct forecasting substitutes instead, with a note on each swap. Section numbers are unchanged.
>
> **Discussion formula (Section 19):** for every major result write **Result → Meaning → Comparison → Explanation → Implication.**

---

## **1. Dataset Description**

*Worksheet asks: source, number of records, classes/split, collection period, preprocessing.*

Dataset (pre-filled): `data/DOE_Data_Extracted/data_v2_preprocessed/master_preprocessed.csv` — Philippine DOE national energy statistics, one row per year.

| Property | Value (pre-filled — verify if file changed) |
|---|---|
| Rows | 23 (one per year) |
| Columns | 45 |
| Coverage | 2003–2025 |
| Duplicate rows | 0 |
| Missing cells | 15 — all inside derived lag/growth/rolling columns (structural: earliest years lack a prior-year source) |
| Primary target | `total_consumption_gwh` (52,941 → 126,941 GWh) |
| Secondary targets | `total_peak_demand_mw`, `renewable_generation_gwh` |
| Consumption CAGR 2003–2024 | 4.252% · mean |YoY| 4.49% (max +10.17%, min −4.04%) |

**Split used by the evaluation pipeline (pre-filled):**

| Subset | Years | Samples | Share |
|---|---|---|---|
| Training | 2003–2020 | 18 | 81.8% |
| Held-out test | 2021–2024 | 4 | 18.2% |
| Set aside (future row) | 2025 | 1 | excluded from historical test metrics |

**"Balanced or imbalanced?" adaptation:** class balance applies to category counts; for a continuous target the corresponding concern is **sample size** (18 train / 4 test — each test point = 25% of reported error).

**Discussion (your analysis — sample-size implications, missing-data structure, why the 2025 row is set aside):**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
>
> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **2. Data Preprocessing**

*Worksheet asks: cleaning, missing values, duplicates, encoding, scaling, augmentation — and WHY each was used.*

Pre-filled checklist — mark **Verified?** after inspecting code/file:

| Step | Applied | Verified? | Why it is used |
|---|---|---|---|
| Annual alignment, de-duplication | ✔ | ____ | One record per year keeps time order honest |
| Missing values left in lag/rolling columns | ✔ | ____ | "Last year's value" has no source for the earliest rows |
| Feature engineering (lag-1/2, YoY, 3- & 5-yr rolling, capacity margin, renewable share) | ✔ | ____ | Gives comparison models autoregressive memory |
| Differencing d=1 | inside ARIMA | ____ | Removes the strong upward trend so the model learns deviations |
| Categorical encoding | — | ____ | No categorical predictors exist in the table |
| Feature scaling | skipped | ____ | All evaluated models are scale-invariant or tree-based |
| Augmentation | skipped | ____ | Fabricated national statistics would corrupt the evaluation |

**Discussion (explain why each technique was or was not applied):**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **3. Model Architecture / Algorithm**

*Worksheet asks: identify the algorithm(s); if several were tested, compare them.*

| Model | How it predicts | Configuration (fill in) |
|---|---|---|
| **ARIMA(1,1,1)** — production | Uses last year's change + last year's shock; emits confidence ranges | ____ |
| Linear Trend Regression | Straight line through history, extended forward | ____ |
| Naive with Drift | Last value + mean yearly increase | ____ |
| Holt Linear Smoothing | Smooths level and slope, weighs recent years more | ____ |
| SARIMAX(1,1,1) + Exog | ARIMA + exogenous input columns | ____ |
| Random Forest Regression | Tree committee over lag/rolling features | ____ |

**Production serving check (pre-filled):** `fastapi-backend/app/ml/predictor.py` loads precomputed forecast CSVs — confirm the current behavior: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **4. Training Performance**

*Worksheet asks: training/validation accuracy, loss, epochs, training time, overfit/underfit signs.*

**Adaptation note:** epochs and loss curves belong to gradient-trained models; all six models fit in a single mathematical step. The statistical substitutes are **fit time** and **residual diagnostics**.

*(Instrument: `evaluate_forecasting_models.py` → `latency_and_size.json`, `summary.json → arima_diagnostics`)*

| Model | Fit time (s) |
|---|---:|
| Linear Trend Regression | ____ |
| Naive with Drift | ____ |
| Holt Linear Smoothing | ____ |
| ARIMA(1,1,1) | ____ |
| SARIMAX(1,1,1) + Exog | ____ |
| Random Forest Regression | ____ |

**ARIMA diagnostics:**

| Item | Value |
|---|---|
| ar.L1 | ____ |
| ma.L1 | ____ |
| sigma² | ____ |
| AIC / BIC | ____ / ____ |
| Ljung–Box lag-5 statistic / p-value | ____ / ____ |

**Discussion (overfit/underfit read; what the near-unit AR coefficient tells you; are residuals white noise?):**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **5. Test-Set Performance**

*Worksheet asks: accuracy, precision, recall, F1 on held-out data.*

**Adaptation note:** classification metrics apply to models that pick categories — this model predicts amounts, so the correct metrics are **MAE, RMSE, MAPE, R²**, plus **direction-of-change accuracy** as the classification-style substitute.

*(Instrument: `model_metrics_consumption.csv`, `model_metrics_peak_demand.csv`, `model_metrics_renewable.csv`, `forecast_vs_actual.csv`)*

**Held-out test, total consumption 2021–2024:**

| Model | MAE (GWh) | RMSE (GWh) | MAPE (%) | R² |
|---|---:|---:|---:|---:|
| Linear Trend Regression | ____ | ____ | ____ | ____ |
| Naive with Drift | ____ | ____ | ____ | ____ |
| Holt Linear Smoothing | ____ | ____ | ____ | ____ |
| **ARIMA(1,1,1)** | ____ | ____ | ____ | ____ |
| SARIMAX(1,1,1) + Exog | ____ | ____ | ____ | ____ |
| Random Forest Regression | ____ | ____ | ____ | ____ |

**Per-year held-out errors (fill for the production model at minimum):**

| Year | Actual | Predicted | Residual | % error |
|---|---:|---:|---:|---:|
| 2021 | ____ | ____ | ____ | ____ |
| 2022 | ____ | ____ | ____ | ____ |
| 2023 | ____ | ____ | ____ | ____ |
| 2024 | ____ | ____ | ____ | ____ |

**Directional accuracy (classification-style substitute):**

| Model | Correct calls | Rate |
|---|---|---|
| ____ | ____ / ____ | ____% |

**Discussion — Result → Meaning → Comparison → Explanation → Implication:**

> Result: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
>
> Meaning: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
>
> Comparison: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
>
> Explanation: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
>
> Implication: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **6. Confusion Matrix**

*Worksheet asks: which categories get confused with which.*

**Adaptation note:** a classification confusion matrix needs categories — this substitute asks "did the model call the **direction of change** right?"

*(Instrument: `directional_confusion.csv`)*

| Actual ↓ / Predicted → | Up | Down |
|---|---|---|
| **Up** | ____ | ____ |
| **Down** | ____ | ____ |

**Discussion (which years were missed and why — watch acceleration years and the lone contraction year):**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **7. Class-by-Class Evaluation**

*Worksheet asks: best/weakest class, per-class precision/recall/F1.*

**Adaptation note:** the regression equivalent of per-class scoring is **per-target performance** — one model specification across the three forecast targets.

| Target | Model | MAPE (%) | Reading |
|---|---|---:|---|
| `total_consumption_gwh` | ARIMA(1,1,1) | ____ | ____ |
| `total_peak_demand_mw` | ARIMA(1,1,1) | ____ | ____ |
| `renewable_generation_gwh` | ARIMA(1,1,1) | ____ | ____ |
| `total_peak_demand_mw` | best comparator: ____ | ____ | ____ |

**Discussion (which target suits a fixed order, which needs its own settings — the "hardest class" equivalent):**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **8. ROC-AUC / PR-AUC**

*Worksheet asks: ROC curve, AUC, PR curve — threshold-based class separation.*

**Adaptation note:** ROC/PR curves require class probabilities and a decision threshold — a point forecaster has neither, so these are structurally inapplicable (not skipped). The forecasting equivalent is **prediction-interval coverage**: does the promised 95% range contain reality?

*(Instrument: `summary.json → picp_95pct_test`)*

| Item | Value |
|---|---|
| 95% interval coverage on the test set | ____ / ____ |
| Which year(s) fell outside the band | ____ |
| Nominal vs. empirical coverage gap | ____ |

**Discussion (are the intervals honest under regime change?):**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **9. Cross-Validation**

*Worksheet asks: k-fold cross-validation results — stronger evidence than one split.*

**Adaptation note:** time-series data requires **expanding-window CV** — random k-fold would leak the future.

*(Instrument: `cv_summary.csv`, `cv_expanding_window.csv`)*

| Model | Folds | Mean APE (%) | Std dev |
|---|---|---:|---:|
| ARIMA(1,1,1) | ____ | ____ | ____ |
| Holt | ____ | ____ | ____ |
| Naive w/ Drift | ____ | ____ | ____ |
| Linear Trend | ____ | ____ | ____ |

**Discussion (does the single-split leaderboard survive resampling?):**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **10. Comparison With Other Machine-Learning Models**

*Worksheet asks: proposed model vs baselines — and warns not to claim "better" on accuracy alone.*

| Rank | Model | MAPE (%) | Key differentiator |
|---|---|---:|---|
| 1 | ____ | ____ | ____ |
| 2 | ____ | ____ | ____ |
| 3 | ____ | ____ | ____ |
| 4 | ____ | ____ | ____ |
| 5 | ____ | ____ | ____ |
| 6 | ____ | ____ | ____ |

**Discussion — justify the production pick on grounds beyond raw accuracy (intervals, diagnostics, CV parity, upgrade path):**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **11. Hyperparameter Evaluation**

*Worksheet asks: parameters tested, configuration selected, why it performed better.*

*(Instrument: `aic_grid.csv` — order search over p,d,q ∈ {0,1,2}, d fixed at 1)*

| Order | AIC | BIC |
|---|---:|---:|
| (0,1,0) | ____ | ____ |
| (0,1,1) | ____ | ____ |
| (0,1,2) | ____ | ____ |
| (1,1,0) | ____ | ____ |
| (1,1,1) | ____ | ____ |
| (1,1,2) | ____ | ____ |
| (2,1,0) | ____ | ____ |
| (2,1,1) | ____ | ____ |
| (2,1,2) | ____ | ____ |

**Selected configuration:** \_\_\_\_\_\_ **Because:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**Discussion (search width, fixed d, per-target orders as future work):**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **12. Feature Importance / Explainability**

*Worksheet asks: which inputs drive predictions — feature importance, SHAP, LIME.*

**Adaptation note:** ARIMA explains itself through fitted parameters; the Random Forest baseline exposes `feature_importances_`.

| Item | Value | Plain-language reading |
|---|---|---|
| ar.L1 | ____ | ____ |
| ma.L1 | ____ | ____ |
| RF top feature 1 | ____ | ____ |
| RF top feature 2 | ____ | ____ |
| SHAP/LIME used? | ____ | ____ |

**Discussion:**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **13. Error Analysis**

*Worksheet asks: which cases failed, which were confused, why — with an error table.*

| Error pattern | Frequency | Likely cause |
|---|---|---|
| ____ | ____ | ____ |
| ____ | ____ | ____ |
| ____ | ____ | ____ |
| ____ | ____ | ____ |

**Prompts to answer:** Which years failed worst? Did errors grow with horizon? Were all models wrong in the same direction? What role did the post-2020 acceleration play?

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **14. Robustness Testing**

*Worksheet asks: does the model stay reliable when conditions change — noise, missing features, different distributions?*

*(Instrument: `robustness_perturbation.csv`)*

| Robustness check | Result |
|---|---|
| Perturbation runs (n) | ____ |
| MAPE mean / std / min / max | ____ / ____ / ____ / ____ |
| Alternative test window | ____ |

**Discussion:**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **15. Statistical Significance**

*Worksheet asks: are model differences statistically proven (McNemar, Wilcoxon, Friedman)?*

**Adaptation note:** those tests need classification predictions or many folds; with n=4 test points the applicable tool is a **Diebold–Mariano loss comparison** — reported with its power caveat.

*(Instrument: `dm_test.json`)*

| Item | Value |
|---|---|
| Comparison | ____ |
| DM statistic | ____ |
| p-value (normal approx) | ____ |
| n (test points) | ____ |
| Power caveat acknowledged | ____ |

**Honest-statement prompt — at this sample size, differences are descriptive; say so:**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **16. Generalization**

*Worksheet asks: does the model work beyond the test data — other users, places, sources, times?*

| Generalization axis | Evidence | Result |
|---|---|---|
| Temporal (other time windows) | expanding-window CV | ____ |
| Regime (acceleration) | test window 2021–2024 | ____ |
| External dataset | ____ | ____ (single national series in repo — record what a real external test would need) |
| Other locations/users | ____ | ____ |

**Discussion:**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **17. Practical Performance**

*Worksheet asks: prediction time, latency, memory, model size, deployment requirements.*

*(Instrument: `latency_and_size.json`)*

| Metric | ARIMA(1,1,1) | Random Forest |
|---|---:|---:|
| 6-step forecast latency (mean) | ____ ms | ____ ms |
| Serialized size (joblib) | ____ bytes | ____ bytes |
| Fit time | ____ s | ____ s |
| Production serving path | ____ | — |

**Discussion (deployment feasibility, freshness of served artifacts):**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **18. Limitations of the ML Model**

*Worksheet asks: state weaknesses transparently — doing so strengthens credibility.*

Check all that apply and elaborate:

- ☐ Tiny sample (18 train / 4 test)
- ☐ Thin statistical power (n=4)
- ☐ Regime mismatch (training predates post-2020 acceleration)
- ☐ Single series / single country
- ☐ Univariate inputs only
- ☐ One fixed order across targets
- ☐ Interval coverage below nominal under acceleration
- ☐ Served forecasts are static artifacts
- ☐ Documentation drift (placeholder metrics found earlier)
- ☐ Other: \_\_\_\_\_\_

**Discussion:**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **19. Recommended Discussion Formula**

*Worksheet asks: for every major result use Result → Meaning → Comparison → Explanation → Implication.*

**Applied example (pre-filled — the ARIMA selection finding):**

> **Result:** ARIMA achieved 5.667% MAPE on the held-out test — fourth of six — and 3.607% mean error across 7 CV windows, tied for best.
>
> **Meaning:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
>
> **Comparison:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
>
> **Explanation:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
>
> **Implication:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**Apply the same formula to one more major result of your choosing:**

> Result: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
>
> Meaning: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
>
> Comparison: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
>
> Explanation: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
>
> Implication: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **20. Recommended Publishable ML Results & Discussion Structure**

*The worksheet's recommended chapter skeleton — each subsection is a prompt for the write-up. Fill in or cross-reference the completed report (`ML_Evaluation_Results_and_Discussion.md`).*

## **4. Results and Discussion**

### **4.1 Dataset Characteristics**

> Source, sample size, target range, split: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.2 Data Preprocessing Results**

> Cleaning, engineering, scaling decisions: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.3 Model Development and Training**

> Algorithm, hyperparameters, training configuration: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.4 Training and Validation Performance**

> Fit quality, diagnostics, overfit/underfit read: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.5 Model Performance on the Test Dataset**

> MAE/RMSE/MAPE/R², directional accuracy: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.6 Confusion Matrix Analysis**

> Directional 2×2 substitute + why the classification version is N/A: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.7 Class-Level Performance**

> Per-target breakdown + interval coverage: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.8 Cross-Validation Results**

> Fold means, std, which ranking survives resampling: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.9 Comparative Evaluation**

> Proposed vs baselines, honest ranking: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.10 Hyperparameter Analysis**

> Order search, selected configuration: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.11 Feature Importance / Explainability**

> Fitted parameters, RF importances, SHAP/LIME decision: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.12 Error Analysis**

> Worst failures, shared failure direction, causes: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.13 Robustness and Generalization**

> Perturbation results, external/temporal validity: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.14 Statistical Significance**

> DM test result + power caveat: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.15 Practical/Deployment Performance**

> Latency, size, serving path, freshness risks: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.16 Comparison With Related Studies**

> Internal baseline + what external comparison would require: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.17 Limitations**

> Dataset, model, methodology: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.18 Implications**

> Theoretical, practical, organizational, technical: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

### **4.19 Overall Synthesis**

> The honest one-paragraph verdict: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

## **The most important distinction — applied**

The worksheet's evidence hierarchy — dataset → methodology → test performance → class-level → error analysis → CV → baselines → statistics → explainability → generalization → practical implications — maps to this form's sections 1–18. Usability/ISO-25010/UAT results belong to the companion **System Testing** documents, not here.

---

# **21. Generative-AI Component: Groq Evaluation Form** *(added for LUMI)*

*Groq is the generative recommendation layer — evaluate on contract, speed, and resilience. Instrument: `llm_groq_eval.py` → `llm_eval.json`.*

| Check | Expected | Result |
|---|---|---|
| Live analysis calls (n) | ____ | ____ |
| Non-empty response rate | ____% | ____ |
| Sanitizer survival rate | ____% | ____ |
| Required-section compliance (`## Observation/Interpretation/Recommendation`) | ____% | ____ |
| Prescriptive-content extraction | ____% | ____ |
| Latency min / mean / median / p95 / max (ms) | ____ | ____ |
| JSON-mode probe: valid-JSON rate / schema rate | prompt asks for markdown → prose is correct | ____ |
| Gemini→Groq fallback (injected failure) | returns response | ____ ms |
| Hard timeout | graceful empty return within budget | ____ ms |
| Token-usage sample (model / prompt / completion / total) | ____ | ____ |
| Configured fallback models reachable | all available | ____ |

**Discussion (latency tail vs. UX, contract clarity, resilience, config defects):**

> \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

# **22. Evidence Appendix — Instruments** *(added)*

| Section | Instrument | Artifact output |
|---|---|---|
| 1–2 | `artifacts/scripts/evaluate_forecasting_models.py` (dataset profile portion) | `artifacts/rerun-*/ml/dataset_profile.json` |
| 4–17 | `artifacts/scripts/evaluate_forecasting_models.py` | `artifacts/rerun-*/ml/{summary.json, model_metrics_*.csv, cv_*.csv, dm_test.json, directional_confusion.csv, forecast_vs_actual.csv, residuals_test.csv, aic_grid.csv, robustness_perturbation.csv, latency_and_size.json, forecast_plot.png}` |
| 21 | `artifacts/scripts/llm_groq_eval.py` (needs `.env` loaded for keys) | `artifacts/rerun-*/llm/{llm_eval.json, prompt_and_response_snippets.json, run_log.txt}` |

**Environment (pre-filled):** Python 3.13.2 venv (`fastapi-backend/.venv`) · statsmodels 0.14.6 · scikit-learn 1.9.0 · pandas 3.0.5 · groq 0.18.0 · i5-8400 · ~8 GB RAM · Windows 11 Pro for Workstations.

**Scope note (pre-filled):** this form covers ARIMA + comparators + the Groq layer per stakeholder instruction. A geothermal `RandomForestClassifier` (`geothermal/ml_classifier.py`) exists and can be added as an extended scope: evaluator decision — \_\_\_\_\_\_.

**Reference answers:** the completed measurements for every blank above are in `ML_Evaluation_Results_and_Discussion.md` (formal) and `ML_Evaluation_Results_and_Discussion_v2.md` (plain language).
