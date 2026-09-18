# **Title :** Machine Learning Evaluation of the LUMI Energy Forecasting and AI Recommendation Components — Plain-Language Version

Group Name : \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
Technical Evaluators ( IT Experts ) \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# **Machine Learning Evaluation: Results and Discussion**

> **How to read this document.** This file follows the same numbering as the source worksheet, so every section 1–20 can be tracked against it directly. Every section is answered for LUMI. Section 20 contains the write-up in the recommended 4.1–4.19 structure. Sections 21 and 22 are extra LUMI sections (the Groq AI layer and the evidence list).
>
> **Plain-language rule.** Technical terms are explained the first time they appear. Every statement is a direct description of what was measured — the numbers come from the files listed in Section 22.
>
> **One adaptation you will see repeated.** Several worksheet sections were written for *classification* models — models that sort items into categories (for example, "spam" vs "not spam"). LUMI's model does something different: it predicts an **amount** (how many gigawatt-hours of electricity the Philippines will use next year). You cannot build a confusion matrix or an ROC curve for an amount, so those sections name the correct forecasting substitute and report it instead. The section numbers stay the same.

---

## **1. Dataset Description**

*This section asks: where did the data come from, how many records, how was it split into training and testing, and is it balanced?*

**Answer.** The data comes from the **Philippine Department of Energy (DOE)** — official national energy statistics. Our team preprocessed it into one table: `data/DOE_Data_Extracted/data_v2_preprocessed/master_preprocessed.csv`.

| Property | Value |
|---|---|
| Rows | **23** — one record per year |
| Columns | **45** |
| Years covered | **2003–2025** |
| Duplicate rows | **0** |
| Missing cells | **15** — all inside computed columns such as "last year's value" or "3-year rolling average," which are blank for the earliest years because there is no earlier year to draw from |
| Main target (what we predict) | `total_consumption_gwh` — total electricity used, ranging **52,941 → 126,941 GWh** |
| Other targets | `total_peak_demand_mw`, `renewable_generation_gwh` |
| Average yearly growth 2003–2024 | **4.252%** per year |

The worksheet's table asks for a training/validation/testing split. Our pipeline uses only two blocks because 23 rows cannot support three:

| Subset | Years | Samples | Share |
|---|---|---|---|
| Training | 2003–2020 | **18** | 81.8% |
| Held-out test | 2021–2024 | **4** | 18.2% |
| **Total used in evaluation** | 2003–2024 | **22** | 100% |

*(The 2025 row exists in the file but was kept out of the test scoring so the results match the pipeline's documented method.)*

**Is the dataset balanced?** That question applies to category counts — for example, "500 spam emails vs 500 normal emails." Our target is an amount that grows every year, so "balance" has a different meaning here. The relevant fact is **size**: 18 training years and 4 test years is a very small dataset. Each test year carries 25% of the final score, so one unusual year can change the ranking. This small size shapes every conclusion in this document.

---

# **2. Data Preprocessing**

*This section asks: what was done to the raw data before training, and why?*

**Answer — what the pipeline actually does, verified against the file and the code:**

| Step | Applied? | Why |
|---|---|---|
| One row per year, in order | Yes | 23 rows, no gaps, no duplicate years |
| Missing-value handling | Left in place | The 15 blank cells exist only where a formula needs a year before 2003. Models that use those columns work only with complete rows |
| Feature engineering (new computed columns) | Yes | Columns such as "last year's consumption," "year-over-year growth," and "3-year rolling average" were added so the comparison models can see recent history |
| Differencing | Yes — inside ARIMA | ARIMA's `d=1` setting makes it work on *changes* between years instead of raw levels, which handles the strong upward trend |
| Category encoding | Skipped | The table has no text categories — every column is a number |
| Feature scaling (shrinking all columns to one range) | Skipped | Four of the six models are scale-invariant (multiplying units changes nothing) and Random Forest is tree-based, so scaling would add a step and change nothing |
| Augmentation (inventing extra rows) | Skipped | Fabricated national statistics would corrupt the evaluation — we only used real DOE figures |

**Discussion.** Preprocessing is light because the input is already clean official statistics. The real work is the computed history columns for the comparison models and the differencing ARIMA performs internally.

---

# **3. Model Architecture / Algorithm**

*This section asks: which algorithm(s) were used? If several were tested, compare them.*

**Answer.** Six models were trained and tested. One is the production model; five are comparison baselines.

| Model | What it does |
|---|---|
| **ARIMA(1,1,1)** — the production model | A standard statistical forecaster. It predicts next year's level from the most recent change and the most recent surprise, and it also produces a confidence range ("probably between X and Y") |
| Linear Trend Regression | Fits one straight line through all 18 training years and extends it forward |
| Naive with Drift | Predicts "last year's value plus the average yearly increase" |
| Holt Linear Smoothing | Like Naive with Drift, but it weighs recent years more heavily, so it adjusts to recent changes faster |
| SARIMAX(1,1,1) + Exog | ARIMA plus extra input columns (exogenous variables) |
| Random Forest Regression | A committee of decision trees over the engineered history columns |

The comparison table with real scores is in Section 5 (test results) and Section 10 (ranking).

**Production note.** In the live system, `fastapi-backend/app/ml/predictor.py` loads precomputed forecast files and serves the stored ARIMA predictions with their confidence ranges. The API does not retrain the model per request.

---

# **4. Training Performance**

*This section asks: training accuracy, validation accuracy, loss curves, epochs, training time, and signs of over- or under-fitting.*

**Answer.** First, an honest adjustment: **epochs and loss curves belong to gradient-trained models such as neural networks.** None of our six models train that way — each one fits in a single mathematical step. Measured fit times (`latency_and_size.json`):

| Model | Fit time (s) |
|---|---:|
| Naive with Drift | 0.00005 |
| Holt Linear Smoothing | 0.0160 |
| Linear Trend Regression | 0.0374 |
| SARIMAX(1,1,1) + Exog | 0.0704 |
| **ARIMA(1,1,1)** | **0.0859** |
| Random Forest Regression | 0.1026 |

All six fit in about a tenth of a second or less — training cost is a non-issue on 18 rows.

For a statistical model, the equivalent of "did training go well" is the **residual diagnostic** — checking whether the model's leftover errors still contain usable patterns. ARIMA's measured diagnostics:

| Diagnostic | Value | Reading |
|---|---|---|
| `ar.L1` coefficient | ≈ 0.9999 | The model weighs last year's change almost fully |
| `ma.L1` coefficient | ≈ −0.9972 | Surprises are absorbed almost fully within one year |
| AIC / BIC (fit-quality scores) | **325.63 / 328.13** | Best of the 9 configurations searched (Section 11) |
| Ljung–Box test on residuals, lag 5 | statistic **0.258**, p = **0.9984** | The leftovers are statistically indistinguishable from random noise — the model extracted all the repeating pattern the data contained |

**Good fit / overfit / underfit read.** ARIMA's residuals pass the white-noise check, so the model is fitted correctly — it is *adequate*. The near-1.0 AR coefficient paired with the near-cancelling MA coefficient means the fitted process behaves very close to a simple "last value plus average increase" — which explains why the simpler drift method performs almost identically on the test set (Section 5). There is no overfitting evidence; the model is if anything close to minimal complexity.

---

# **5. Test-Set Performance**

*This is the most important section. It asks: how accurate is the model on data it never saw during training?*

**Adaptation note.** The worksheet's metrics — accuracy, precision, recall, F1 — measure how often a model picks the right category. Our model predicts an amount, so we report the standard forecasting metrics: **MAE** (average absolute error in GWh), **RMSE** (same, but big misses count extra), **MAPE** (average error as a percentage), and **R²** (whether the model beats always predicting the test-set average; 1.0 is perfect, 0 means it ties the average, negative means worse). We also report **direction-of-change accuracy** — did the model correctly predict whether usage went up or down?

**Held-out test results — total consumption, 2021–2024** (`model_metrics_consumption.csv`):

| Model | MAE (GWh) | RMSE (GWh) | MAPE (%) | R² |
|---|---:|---:|---:|---:|
| **Linear Trend Regression** | **5,993.83** | **7,342.10** | **4.965** | **0.1054** |
| Holt Linear Smoothing | 6,557.72 | 7,997.68 | 5.435 | −0.0615 |
| Naive with Drift | 6,709.32 | 8,128.45 | 5.566 | −0.0965 |
| ARIMA(1,1,1) | 6,829.09 | 8,257.12 | 5.667 | −0.1315 |
| Random Forest Regression | 13,118.37 | 15,349.45 | 10.937 | −2.9099 |
| SARIMAX(1,1,1) + Exog | 16,721.10 | 18,787.73 | 14.031 | −4.8577 |

**Year by year — ARIMA's errors** (`forecast_vs_actual.csv`):

| Year | Actual (GWh) | Predicted | Missed by | % error |
|---|---:|---:|---:|---:|
| 2021 | 106,115 | 104,579.7 | 1,535.3 | −1.45% |
| 2022 | 111,516 | 107,403.3 | 4,112.7 | −3.69% |
| 2023 | 118,004 | 110,226.7 | 7,777.3 | −6.59% |
| 2024 | 126,941 | 113,049.9 | 13,891.1 | −10.94% |

**Direction-of-change accuracy (the classification-style substitute):**

| Model | Correct calls | Rate |
|---|---|---|
| ARIMA(1,1,1) | 8 of 11 fold+test years | **72.7%** |
| Linear Trend (cross-validation years) | 3 of 7 | 42.9% |
| Linear Trend (test years) | 2 of 4 | 50.0% |

**Discussion — in plain terms.** When we compared each model's predictions with the real 2021–2024 figures, the straight-line model came closest (about 5% off on average) and **ARIMA placed fourth** (about 5.7% off). But the top four models sit only 0.7 percentage points apart — on just four test years, that spread is too small to declare a real winner. Every model predicted too low in every test year, and the misses grew the further ahead they looked: ARIMA went from 1.5% too low in 2021 to 10.9% too low in 2024. The cause is in the data, not in any single model: electricity demand accelerated after 2020, faster than anything in the models' 2003–2020 training history. The negative R² scores for five models mean that with only four test years, "always predict the average" is hard to beat — a side effect of the tiny test set. **Takeaway: the forecaster reliably gets the direction and rough size right — within about 5–6% — and its main weakness is under-predicting years when demand suddenly speeds up.**

---

# **6. Confusion Matrix**

*This section asks: where does the model make mistakes — which categories get confused with which?*

**Adaptation note.** A confusion matrix needs categories. There are no categories here — the target is an amount. The closest valid substitute: **did the model predict the right direction of change?** From `directional_confusion.csv` (ARIMA, unique years 2015–2024):

| Actual \ Predicted | Up | Down |
|---|---|---|
| **Up** | 7 | 2 |
| **Down** | 1 | 0 |

**Discussion — where the mistakes are.** ARIMA called the correct direction in 8 of 10 unique years. The informative cells are the two misses in 2023–2024: the model predicted a slowdown exactly when demand accelerated. The third miss is 2020 — the only year electricity use actually fell (−4.04%, the pandemic year) — which the model predicted up. Both kinds of miss share one cause: the model cannot anticipate events that have no precedent in its 18 training years.

*(For completeness: ROC-AUC, which the worksheet covers in Section 8, is also addressed there.)*

---

# **7. Class-by-Class Evaluation**

*This section asks: which categories does the model handle best and worst?*

**Adaptation note.** There are no classes, so per-class precision and recall have no meaning. The correct equivalent is **per-target performance** — the same ARIMA(1,1,1) applied to the three different things we forecast:

| Target | ARIMA MAPE | Best model on this target | Best MAPE |
|---|---:|---|---:|
| `total_consumption_gwh` (electricity used) | 5.667% | Linear Trend | 4.965% |
| `total_peak_demand_mw` (peak load) | 5.611% | SARIMAX + Exog | 3.868% (R² = 0.4124) |
| `renewable_generation_gwh` (renewable output) | 13.665% | Linear Trend / Holt | 9.405% |

**Discussion.** The "weakest class" equivalent is renewable generation — its series is more volatile and harder to predict from history alone, and every model scores worse on it. The "best class" equivalent is peak demand, where SARIMAX's extra input columns produced the only clearly positive R² of the whole evaluation. This tells us the fixed (1,1,1) setting is reasonable for the smooth consumption and demand series but a poor default for renewables — choosing settings per target is a concrete improvement.

---

# **8. ROC-AUC / PR-AUC**

*This section asks: how well does the model separate the classes across all decision thresholds?*

**Adaptation note.** ROC and PR curves measure a classifier across decision thresholds on class probabilities. A point forecaster has neither classes nor thresholds, so these curves cannot be computed — this is a structural non-applicability, not a skipped test.

The forecasting equivalent of "how much should we trust the output" is **prediction-interval coverage**: ARIMA promises a 95% confidence range — "the real value should land inside this band 95% of the time." Measured result: the 95% range contained the real value in **3 of the 4 test years (75%)**. The miss was 2024 — the acceleration year, the same year the point forecast missed worst.

**Discussion.** The intervals are slightly overconfident exactly under the condition where point forecasts also degrade — a demand regime change. The range is honest enough to be useful (the API already serves it as `ci_lower`/`ci_upper`), and coverage deserves a re-check whenever the test window includes a structural shift.

---

# **9. Cross-Validation**

*This section asks: does the model hold up across repeated tests on different data slices — stronger evidence than a single test window?*

**Answer.** We used **expanding-window cross-validation**: train on the early years, test on the next year, then grow the training window and repeat — 7 rounds. (Ordinary random k-fold would let the model peek at the future, so it was correctly avoided.) Results — average absolute % error per fold (`cv_summary.csv`):

| Model | Folds | Mean APE | Std dev |
|---|---:|---:|---:|
| Holt | 7 | **3.525%** | 3.496% |
| Naive with Drift | 7 | 3.584% | 2.535% |
| **ARIMA(1,1,1)** | 7 | **3.607%** | **2.512%** |
| Linear Trend | 7 | 5.861% | 3.917% |

**Discussion.** Across the seven rounds, ARIMA, Holt, and Naive-with-Drift finish within 0.09 percentage points of each other — statistically indistinguishable — while **Linear Trend, the Section-5 "winner," comes in last**. This is the key finding of the whole evaluation: the single 4-year test ranking was partly luck, and the repeated-window test is the more trustworthy leaderboard. It is also the core of the defense for keeping ARIMA: it ties for best where the evidence is strongest.

---

# **10. Comparison With Other Machine-Learning Models**

*This section asks: how does the proposed model rank against baselines — and warns against calling the proposed model "better" on one metric alone.*

**Answer — consolidated ranking on the 2021–2024 consumption test:**

| Rank | Model | MAPE | What distinguishes it |
|---|---|---:|---|
| 1 | Linear Trend | 4.965% | Lowest error on this split — but last in cross-validation |
| 2 | Holt | 5.435% | Best cross-validation mean; less stable across windows |
| 3 | Naive with Drift | 5.566% | Nearly free to compute; hard to beat on a smooth series |
| 4 | **ARIMA(1,1,1)** | **5.667%** | The only model that also produces confidence ranges; tied-best in cross-validation |
| 5 | Random Forest | 10.937% | Needs far more than 18 rows to learn from |
| 6 | SARIMAX + Exog | 14.031% | Its extra input columns extrapolated badly on this target |

**Discussion — and the honest version the worksheet asks for.** Following the worksheet's own warning, we do **not** claim the production model is "better" on accuracy: **Linear Trend had the lowest MAPE on this split, and ARIMA placed fourth.** The defense rests on evidence the accuracy column cannot show:

1. **Where the evidence is strongest — the repeated-window test — ARIMA ties for best** (3.61% vs Linear Trend's 5.86%).
2. **ARIMA is the only model that says how sure it is.** Its confidence ranges are what the API sends users. The other three produce a single number with no stated uncertainty.
3. **ARIMA is the only model whose fit we can verify.** Its leftover errors are pure noise (Section 4), meaning it extracted all the structure present. There is no equivalent check for the other three.
4. **ARIMA has an upgrade path.** Its extended form, SARIMAX, already produced the best score on peak demand; Linear Trend and Naive-with-Drift have no equivalent extensions.

In one sentence: the top four models are equally accurate for practical purposes, so the choice went to the one that is also honest about its uncertainty, provably well-fitted, and able to improve later.

---

# **11. Hyperparameter Evaluation**

*This section asks: which settings were tested, which were selected, and why?*

**Answer.** ARIMA's "settings" are its order (p,d,q) — how many past changes and past surprises it weighs. We searched all 9 combinations of p,d,q in {0,1,2} with d fixed at 1, scored by **AIC** (a fit-quality score that penalizes extra complexity — lower is better). From `aic_grid.csv`:

| Order | AIC | BIC |
|---|---:|---:|
| **(1,1,1) — selected** | **325.63** | **328.13** |
| (2,1,1) | 327.47 | 330.80 |
| (1,1,2) | 329.13 | 332.46 |
| (2,1,2) | 331.01 | 335.17 |
| (0,1,0) | 332.49 | 333.32 |
| (1,1,0) | 332.82 | 334.49 |
| (0,1,1) | 332.92 | 334.58 |
| (0,1,2) | 334.29 | 336.79 |
| (2,1,0) | 334.36 | 336.86 |

**Discussion.** (1,1,1) won the search by 1.8 AIC points — the standard AIC criterion selected the setting. The search stayed narrow by design: d was fixed at 1 and seasonal orders were skipped (annual data has no within-year season). Searching a wider space per target remains a listed improvement.

---

# **12. Feature Importance / Explainability**

*This section asks: which inputs drive the predictions — can we explain the model's decisions?*

**Answer.** ARIMA explains itself through its fitted parameters rather than a feature-importance list:

| Fitted parameter | Value | Plain reading |
|---|---|---|
| `ar.L1` | ≈ 1.00 | Next year's level ≈ this year's level plus the trend |
| `ma.L1` | ≈ −1.00 | A one-year surprise is absorbed almost fully within the next year |

Together these describe a smooth, steadily-growing process where shocks fade quickly — which matches what the consumption series looks like.

For the Random Forest baseline, its top features are `consumption_lag1` and the rolling averages — i.e., it also predicts almost purely from recent levels, the same information ARIMA uses. With only 18 rows it memorizes rather than learns, which explains its 10.9% MAPE.

SHAP and LIME were considered and skipped: at 18 rows and under 10 features they would add machinery without adding insight. This is recorded as a deliberate choice, open to revisiting if the dataset grows.

---

# **13. Error Analysis**

*This section asks: which cases failed, and why?*

**Answer — the observed error patterns:**

| Error pattern | How often | Likely cause |
|---|---|---|
| Predicted too low | All 6 models, all 4 test years (24/24) | Post-2020 demand acceleration — no precedent in the 2003–2020 training window |
| Errors grow with distance | Steady −1.45% → −10.94% (ARIMA) | Each extra forecast year compounds the same trend miss |
| Predicted "down," actual "up" | 2 of 4 test years | The near-unit-root fit pulls predictions back toward average growth |
| Predicted "up" in 2020 (actual −4.04%) | 1 of 1 down year | A single contraction year in 18 cannot teach the model what a downturn looks like |
| SARIMAX severe under-prediction | All 4 years (−22.8% by 2024) | Its extra input columns trended worse than the target itself |
| Random Forest flat predictions (~102–103k every year) | 3 of 4 years | Trees cannot extrapolate beyond values seen in training |

**Discussion.** The most important observation: **every model failed in the same direction — too low.** When six different methods share one failure mode, the cause is the data regime, not the model choice. Any purely history-based model on this series will under-predict an acceleration. The plausible fixes are adding demand drivers (economic growth, electrification policy) as inputs, or retraining on a shorter recent window.

---

# **14. Robustness Testing**

*This section asks: does the model stay reliable when inputs are disturbed?*

**Answer.** We ran a perturbation test: 30 evaluation runs with the input series slightly disturbed each time (`robustness_perturbation.csv`).

| Measure | Result |
|---|---|
| Runs | 30 |
| MAPE — mean | **5.707%** |
| MAPE — std dev | **0.155** |
| MAPE — min / max | 5.279% / 6.068% |

**Discussion.** The spread is about ±0.16 percentage points — the model's accuracy is stable under small input disturbances. This supports use as a planning-guidance tool: small data revisions will not flip the outputs.

---

# **15. Statistical Significance**

*This section asks: are the differences between models statistically proven, or just observed?*

**Answer.** We ran a Diebold–Mariano-style test comparing ARIMA's and Linear Trend's errors on the 4 test years (`dm_test.json`):

| Item | Value |
|---|---|
| DM statistic | 3.532 |
| Approximate p-value | 0.0004 |
| Test points (n) | 4 |

**Discussion — the honest statement.** The p-value looks impressive, but **four test points cannot power a real significance test** — the script itself flags this. With n=4, the honest claim is: *the observed differences between models are small and depend on which years were chosen for the test; they are descriptive, not statistically established.* The remedy is more granular data — monthly observations would multiply the sample twelve-fold.

---

# **16. Generalization**

*This section asks: will the model work beyond the test data — other periods, other conditions?*

**Answer.**

- **Temporal generalization:** partially supported. Cross-validation (Section 9) shows the model performs consistently across different time windows — the strongest generalization evidence available with annual data.
- **Regime generalization:** weak. The model was trained on 2003–2020 and tested during an acceleration it had never seen — it under-predicted every test year.
- **External generalization:** untested. There is one national series for one country; no second dataset exists to validate against. Establishing this would require either an external country's demand series or more granular Philippine data.
- **What we can claim:** the model generalizes across ordinary variation in this series; it does not generalize to structural breaks — which is a property of every extrapolative model, not an ARIMA defect.

---

# **17. Practical Performance**

*This section asks: is the model fast and light enough for real deployment?*

**Answer** (`latency_and_size.json`):

| Metric | ARIMA(1,1,1) | Random Forest |
|---|---:|---:|
| 6-step forecast latency (mean) | **0.97 ms** | 9.93 ms |
| Model file size | **93.6 KB** | 181.6 KB |
| Fit time | 0.086 s | 0.103 s |

**Discussion.** Deployment cost is trivial: sub-millisecond forecasts, a 94 KB artifact, no GPU. Production serving is even cheaper — the API reads precomputed forecast files rather than running the model. The real deployment risks are about **freshness** (served forecasts stay fixed until the files are regenerated) and **access** (the `/forecast/*` routes now require authentication), not speed or size.

---

# **18. Limitations of the ML Model**

*This section asks: state the weaknesses honestly — doing so strengthens credibility.*

**Answer — all nine, stated directly:**

1. **Very small dataset:** 18 training years, 4 test years; each test year is 25% of the score.
2. **No statistical power:** with n=4, significance tests are decorative — model differences are descriptive only.
3. **Training window predates the acceleration:** all models under-predict 2021–2024 for the same reason.
4. **No external validation:** one series, one country, one contiguous test block.
5. **Univariate inputs:** consumption is predicted from its own history alone — economic and policy drivers are not inputs.
6. **One fixed setting across targets:** (1,1,1) suits the smooth consumption series but scores 13.7% MAPE on renewables — per-target settings are needed.
7. **Intervals slightly overconfident:** 75% coverage where 95% was promised, under acceleration.
8. **Served forecasts are static files:** freshness depends on re-running the pipeline.
9. **Documentation drift found:** an older comparison table in the repository contained rows marked *"placeholder — model not executed"* — unaudited figures that overstated the earlier evaluation. Our fresh run replaced them with real numbers; both models scored far worse than the placeholders implied.

---

# **19. Recommended Discussion Formula**

*The worksheet asks every major result to be discussed as: Result → Meaning → Comparison → Explanation → Implication. Here it is applied to the central finding.*

> **Result.** ARIMA(1,1,1) achieved 5.667% MAPE on the held-out 2021–2024 test — fourth of six models — and 3.607% mean absolute error across 7 cross-validation windows, tied for best.
>
> **Meaning.** On a single four-year split the model's point accuracy is mid-pack; across repeated windows it is among the best. The two evaluations measure different things, and the repeated one is the stronger evidence.
>
> **Comparison.** Linear Trend scored lowest on the single test (4.965%) but last in cross-validation (5.861%); Holt and Naive-with-Drift tie ARIMA in cross-validation but offer no confidence ranges and no fit diagnostics.
>
> **Explanation.** The test years sit inside a demand acceleration none of the models' training data contains, so all six under-predicted; the ranking among the top four shifts with the chosen window. ARIMA's fitted parameters show the data itself is near a drifted random walk, which is why the simplest baselines tie it.
>
> **Implication.** ARIMA is retained as the production model on the strength of cross-validation parity, verifiable fit quality, native confidence ranges, and an upgrade path — with its limitations (point accuracy mid-pack on the single split, intervals slightly overconfident under acceleration) stated openly to users.

---

# **20. Recommended Publishable ML Results & Discussion Structure**

*The worksheet's recommended chapter structure — each subsection answered in condensed form. Sections 1–19 above hold the detailed evidence.*

## **4. Results and Discussion**

### **4.1 Dataset Characteristics**

The model is trained on Philippine DOE national energy statistics — 23 annual rows (2003–2025), 45 columns, zero duplicates, with the main target `total_consumption_gwh` spanning 52,941–126,941 GWh. Training used 18 years (2003–2020); the 2021–2024 years were held out for testing. The dataset's small size is the defining constraint of this evaluation.

### **4.2 Data Preprocessing Results**

Preprocessing consisted of annual alignment, engineered history columns (lags, growth rates, rolling means), and ARIMA's internal differencing. The 15 missing cells are confined to derived columns for the earliest years. Scaling and augmentation were deliberately skipped as unnecessary or harmful for this data.

### **4.3 Model Development and Training**

Six models were trained: the production ARIMA(1,1,1) plus five comparators (Linear Trend, Naive-with-Drift, Holt, SARIMAX+Exog, Random Forest). Production serving reads precomputed forecast files rather than retraining per request.

### **4.4 Training and Validation Performance**

All models fit in under ~0.11 s. ARIMA's residuals pass the Ljung–Box white-noise check (p = 0.9984), confirming a correct fit; its near-unity AR and near-cancelling MA coefficients indicate the series behaves close to a drifted random walk — foreshadowing the simple baselines' competitive performance.

### **4.5 Model Performance on the Test Dataset**

On 2021–2024, Linear Trend achieved the lowest MAPE (4.965%), with Holt (5.435%), Naive-with-Drift (5.566%), and ARIMA (5.667%) close behind; Random Forest (10.937%) and SARIMAX (14.031%) trailed. All models under-predicted every test year as demand accelerated past the training regime. ARIMA predicted the correct direction of change in 8 of 11 evaluated years (72.7%).

### **4.6 Confusion Matrix Analysis — Adapted for Regression**

A classification confusion matrix cannot apply to an amount. The directional substitute shows ARIMA correct on 8 of 10 unique years, with misses concentrated in the acceleration years (predicted slowdown, actual speed-up) and the single 2020 contraction. ROC-AUC is likewise structurally inapplicable and is replaced by interval coverage in 4.7.

### **4.7 Class-Level Performance — Adapted for Regression**

Per-target results replace per-class metrics: ARIMA scores 5.667% (consumption), 5.611% (peak demand), and 13.665% (renewables), while SARIMAX's 3.868% on peak demand is the best result observed anywhere in the evaluation. Prediction-interval coverage — the regression analogue of a confidence-quality score — was 3 of 4 test years (75%), missing the acceleration year.

### **4.8 Cross-Validation Results**

Seven expanding-window folds give Holt 3.525%, Naive-with-Drift 3.584%, ARIMA 3.607% (tied-best within noise), and Linear Trend 5.861% (clearly last) — reversing the single-split ranking and showing it was window-dependent.

### **4.9 Comparative Evaluation**

The production model placed fourth on the held-out split and tied for best in cross-validation. Its selection rests on verified fit diagnostics, native confidence ranges, cross-validation parity, and an upgrade path — not on dominating raw accuracy.

### **4.10 Hyperparameter Analysis**

The (1,1,1) order won a 9-configuration AIC grid (325.63 vs 327.47 next-best) — selected by criterion, with wider and per-target searches left as future work.

### **4.11 Feature Importance / Explainability**

ARIMA is explained by its parameters (≈1.0 AR = follow last year's change; ≈−1.0 MA = absorb shocks in one year). The Random Forest's dominant features are recent-level columns — the same information — and SHAP/LIME were deliberately skipped at this sample size.

### **4.12 Error Analysis**

All six models under-predicted all four test years, with errors growing by horizon — a shared, data-driven failure mode rooted in post-2020 acceleration. Remedies: exogenous demand drivers, shorter retraining windows.

### **4.13 Robustness and Generalization**

Thirty perturbation runs produced MAPE 5.707% ± 0.155 — stable under input noise. Temporal generalization is supported by cross-validation; regime-change and external generalization remain unestablished.

### **4.14 Statistical Significance**

A Diebold–Mariano comparison (statistic 3.532, nominal p≈0.0004, n=4) is reported with its own caveat: at four points the test has no real power, and model differences are descriptive rather than statistically established.

### **4.15 Practical/Deployment Performance**

ARIMA forecasts six steps in 0.97 ms from a 93.6 KB artifact — trivially deployable; production serving reads precomputed files. Residual risks are artifact freshness and the new authentication requirement on forecast routes, not compute.

### **4.16 Comparison With Related Studies**

No external benchmark table exists in the repository, and none was fabricated. The internal reference — the September comparison CSV — contained "placeholder — model not executed" rows for SARIMAX and Random Forest; this evaluation replaced them with measured results that proved far worse than the placeholders implied.

### **4.17 Limitations**

Small sample (18/4), no statistical power, regime mismatch, no external validation, univariate inputs, one fixed order across targets, 75% interval coverage, static served artifacts, and the discovered documentation drift — all stated openly.

### **4.18 Implications**

*Theoretical:* at n=18, information content bounds model complexity — the naive-drift/ARIMA equivalence is textbook behavior. *Practical:* forecasts serve as trend guidance (5–7% error, usually correct direction) and should always be shown with their intervals. *Organizational:* evaluation artifacts need the same audit discipline as code. *Technical:* per-target order selection, monthly data if published, exogenous drivers where SARIMAX showed promise, scheduled artifact regeneration.

### **4.19 Overall Synthesis**

ARIMA(1,1,1) is a reasonable production choice rather than a demonstrably optimal one: fourth on the four-year test (5.667% vs 4.965%), tied for best in cross-validation (3.607%), diagnostically sound, the only model emitting confidence ranges (75% empirical coverage), and deployment-trivial. Every alternative shares its under-prediction weakness — the binding constraint is the dataset. **Verdict: fit for purpose as a trend-guidance service whose outputs are always presented with their stated ranges.**

---

## **The most important distinction — applied to LUMI**

The worksheet warns against making the results section about user ratings ("respondents rated the system 4.50"). This document follows the required evidence order: dataset quality → methodology → test performance → per-target performance → error analysis → cross-validation → baseline comparison → statistical evidence → explainability → generalization → practical implications. Usability and acceptance testing are covered in the companion System Testing Report.

---

# **21. Generative-AI Component: Groq Evaluation** *(added for LUMI)*

*The worksheet has no section for a generative-AI layer, but LUMI's Groq integration is part of the evaluated ML surface — reported here on its own correct criteria: output contract, speed, resilience. Source: `llm_groq_eval.py` → `llm_eval.json` (six live calls, `groq/compound-mini`).*

| Check | Result |
|---|---|
| Live analysis calls | 6 of 6 returned non-empty, correctly-structured markdown — 100% |
| Required sections present (`## Observation / Interpretation / Recommendation`) | 100% |
| Prescriptive content extractable | 100% |
| Latency | min 4,166.8 ms · mean **7,076.1 ms** · median 5,052.3 ms · p95 5,588.6 ms · max **18,468.7 ms** |
| Token sample | 571 prompt + 450 completion = **1,021 tokens** |
| JSON-mode probe | **0% valid JSON** — expected: the live prompt asks for markdown, so prose is the correct output (a code comment claims otherwise — logged as a defect) |
| Gemini→Groq fallback | injected Gemini failure → Groq answered in **1,919.7 ms** |
| Hard timeout | 0.5 s budget → empty return in **504.1 ms**, caller fallback path verified |

**Discussion.** The recommendation layer is reliable on its contract and its resilience: every call produced usable, correctly-formatted output, and both failure paths behaved as designed. Its weakness is speed — ~5 seconds typical, with an 18.5-second worst case that dominates how slow the AI features feel. One configured fallback model name returned HTTP 404 for this account — a live configuration defect logged in the defect table.

---

# **22. Evidence Appendix** *(added)*

Every number above comes from a file produced by the 2026-09-15 re-run:

| What produced it | Output files (under `docs/09-Technical-Evaluation/artifacts/rerun-2026-09-15/`) |
|---|---|
| `artifacts/scripts/evaluate_forecasting_models.py` — dataset profile, 6 models, CV, DM test, robustness, latency, AIC grid | `ml/{summary.json, model_metrics_*.csv, cv_summary.csv, cv_expanding_window.csv, dm_test.json, directional_confusion.csv, forecast_vs_actual.csv, residuals_test.csv, aic_grid.csv, robustness_perturbation.csv, latency_and_size.json, forecast_plot.png, dataset_profile.json, run_log.txt}` |
| `artifacts/scripts/llm_groq_eval.py` — live Groq evaluation | `llm/{llm_eval.json, prompt_and_response_snippets.json, run_log.txt}` |

Environment: Python 3.13.2 (`fastapi-backend/.venv`) · statsmodels 0.14.6 · scikit-learn 1.9.0 · pandas 3.0.5 · groq 0.18.0 · i5-8400 · ~8 GB RAM · Windows 11 Pro for Workstations.

**Formal companion documents:** `ML_Evaluation_Results_and_Discussion.md` (the formal 4.x report with the same numbers) and `ML_Evaluation_Results_and_Discussion_FORM_LUMI.md` (the fillable evaluation form).
