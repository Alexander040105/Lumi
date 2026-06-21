# LUMI Machine Learning Model Evaluation Summary

**Document Type:** Comprehensive ML / AI Evaluation Report — Technical & Plain-Language  
**Project:** LUMI (Lightweight Utility for Municipal Intelligence)  
**Version:** 1.0  
**Date:** June 2026  

---

## Part 1: Technical Summary

### 1. Executive Overview

LUMI is a web-based environmental intelligence platform for Philippine municipalities. It comprises three core modules:

- **EnergyHub** — Climate visualization, energy trends, and time-series forecasting.
- **EcoSim** — Renewable-energy suitability analysis (solar, wind, hydro, geothermal) using physics-based calculators.
- **AI Chat** — LLM-powered (Gemini / Groq) structured recommendations for renewable energy planning.

This document consolidates **every machine-learning and AI model evaluated across LUMI**, reporting:

- **Empirical results** from the EnergyHub forecasting pilot run.
- **Theoretical assessments** from the ML feasibility study (models evaluated for fit but not empirically trained).
- **LLM evaluation dimensions** for the generative AI layer.
- **EcoSim deterministic models** (physics-based, non-ML, but included for completeness).

#### 1.1 Forecasting Dataset & Protocol

- **Source:** Philippine Department of Energy (DOE) Statistical Bulletin, 2003–2024.
- **Target Variable:** Total national electricity consumption (`consumption_gwh`).
- **Training Set:** 2003–2020 (n = 18 observations).
- **Test Set:** 2021–2024 (n = 4 observations, held out).
- **Rationale:** 18 training points are sufficient for parsimonious statistical models (ARIMA, Holt) but insufficient for advanced ML (LSTM, XGBoost). The 4-year test set provides an out-of-sample accuracy estimate.

> **Why not Accuracy, Recall, or F1?** These metrics require a confusion matrix (True Positives, False Positives, etc.), which only exists for discrete classification. Forecasting outputs a continuous number (e.g., 118,004.5 GWh). There is no "positive" or "negative" class. Applying classification metrics to continuous outputs is a **category error**.
>
> *Source:* `lumi_tests/docs/ml_evaluation_framework.md:2.1`

#### 1.2 Metrics Used

| Metric | Formula (Conceptual) | Why It Matters |
|---|---|---|
| **MAE** | `mean(|y - ŷ|)` | Average error in original units (GWh). Most intuitive. |
| **RMSE** | `sqrt(mean((y - ŷ)²))` | Penalizes large errors more heavily. |
| **MAPE** | `mean(|(y - ŷ) / y|) × 100` | Percentage error; comparable across scales. |
| **R²** | `1 - SS_res / SS_tot` | Proportion of variance explained by the model. |
| **AIC / BIC** | Penalize complexity vs. fit | Prefer simpler models if fit improvement is marginal. |
| **Directional Accuracy (DA)** | `% of correct up/down predictions` | Policy-relevant: knowing demand will increase is often more actionable than the exact magnitude. |
| **PICP** | `% of actual values inside prediction interval` | Uncertainty quantification: is the model honest about its confidence? |

---

### 2. Empirically Evaluated Forecasting Models

These six models were trained on the 2003–2020 training set and evaluated on the 2021–2024 test set. The results are stored in `DOE_Data_Extracted/model_comparison_results.csv` and were registered in the Supabase `ml_model_registry` table.

#### 2.1 Performance Leaderboard

| Rank | Model | MAE (GWh) | RMSE (GWh) | MAPE (%) |
|:---:|---|---:|---:|---:|
| 1 | **Linear Trend Regression** | 5,993.83 | 7,342.10 | **4.97%** |
| 2 | Holt Linear Smoothing | 6,557.72 | 7,997.68 | 5.44% |
| 3 | Naive with Drift | 6,709.32 | 8,128.45 | 5.57% |
| 4 | ARIMA(1,1,1) | 6,829.09 | 8,257.12 | 5.67% |
| 5 | SARIMAX(1,1,1) + Exogenous | 9,913.65 | 11,459.11 | 8.28% |
| 6 | Random Forest Regression | 15,957.41 | 17,806.29 | 13.41% |

*Source:* `DOE_Data_Extracted/model_comparison_results.csv:1-8`

#### 2.2 Model-by-Model Analysis

---

**Model 1: Linear Trend Regression**

| Attribute | Detail |
|---|---|
| **Family** | Statistical baseline |
| **How it works** | Ordinary least squares using `year` as the sole predictor. |
| **Code** | `lumi_tests/pilot_run/evaluate_models.py:132-138` |
| **MAE / RMSE / MAPE** | 5,993.83 GWh / 7,342.10 GWh / **4.97%** |

**Why it performed best:**
Philippine national electricity consumption from 2003–2020 is remarkably linear (trend ≈ +3,190 GWh/year). With only 18 observations, the simplest model avoids overfitting and captures the dominant signal without adding unnecessary parameters.

**Key finding:** Lowest MAE and MAPE across all models. This proves that when the underlying data is nearly linear, complex models add noise, not insight.

---

**Model 2: Holt Linear Exponential Smoothing**

| Attribute | Detail |
|---|---|
| **Family** | Statistical baseline |
| **How it works** | Maintains smoothed estimates of *level* and *trend*, giving more weight to recent observations. |
| **Code** | `lumi_tests/pilot_run/evaluate_models.py:153-162` |
| **MAE / RMSE / MAPE** | 6,557.72 GWh / 7,997.68 GWh / 5.44% |

**Why it performed well:**
Holt adapts to recent changes better than pure linear regression, but on this dataset the growth trend is stable enough that the extra adaptivity does not provide a meaningful improvement. The slight accuracy penalty comes from the model "chasing" minor noise that is actually just random fluctuation around a straight line.

**Key finding:** Second-best MAPE (5.44%), very close to Linear Trend. A solid trend-aware baseline.

---

**Model 3: Naive with Drift**

| Attribute | Detail |
|---|---|
| **Family** | Statistical baseline (accuracy floor) |
| **How it works** | Projects the last observed value forward using the average historical change per step. |
| **Code** | Evaluated in `DOE_Data_Extracted/DOE_arima_forecasting.ipynb` |
| **MAE / RMSE / MAPE** | 6,709.32 GWh / 8,128.45 GWh / 5.57% |

**Why it performed well:**
Surprisingly competitive because the series is dominated by a stable upward drift. Any model that captures "keep going up at roughly the same rate" will score well. This is the **dumbest smart model** — and that is on purpose. Any real model must beat the Naive model to justify its complexity.

**Key finding:** MAPE 5.57%. This is the accuracy floor. If a fancy model cannot beat "just keep going in the same direction," it is useless.

---

**Model 4: ARIMA(1,1,1)**

| Attribute | Detail |
|---|---|
| **Family** | Core thesis model (Box-Jenkins) |
| **How it works** | **Auto**Regressive (remembers last year) + **I**ntegrated (differences to remove trend) + **M**oving **A**verage (adjusts for recent shocks). The parameters (1,1,1) mean: remember 1 past value, difference once, adjust for 1 recent shock. |
| **Code** | `lumi_tests/pilot_run/evaluate_models.py:141-150` |
| **MAE / RMSE / MAPE** | 6,829.09 GWh / 8,257.12 GWh / 5.67% |

**Why it performed slightly worse than Linear Trend:**
The data is so close to a straight line that ARIMA's extra parameters (autoregressive and moving-average terms) do not improve fit enough to justify the added complexity on n = 18. On a longer or more volatile series, ARIMA's memory and shock-adjustment would pay off.

**Key finding:** MAPE 5.67% — still excellent. Chosen as the **thesis production model** (see Section 6) because it provides 95% prediction intervals, is statistically defensible, and is robust to potential future trend changes.

---

**Model 5: SARIMAX(1,1,1) + Exogenous Variables**

| Attribute | Detail |
|---|---|
| **Family** | Extended ARIMA with external regressors |
| **How it works** | ARIMA plus exogenous variables (renewable energy share %, capacity margin %). |
| **Code** | Evaluated in `DOE_Data_Extracted/DOE_arima_forecasting.ipynb` |
| **MAE / RMSE / MAPE** | 9,913.65 GWh / 11,459.11 GWh / 8.28% |

**Why it performed worst among statistical models:**
With only 18 training observations, adding 2 exogenous variables forces the model to learn more parameters with the same limited data. This is a classic **curse of dimensionality** on small samples. The model overfits the exogenous features and generalizes poorly to the test set.

**Key finding:** MAPE 8.28%. Lesson: more features hurt when data is scarce.

---

**Model 6: Random Forest Regression (Controlled Experiment)**

| Attribute | Detail |
|---|---|
| **Family** | Machine Learning (ensemble decision trees) |
| **How it works** | 100 decision trees trained on random subsets of data; final prediction = average of all trees. In LUMI, it used `trend` and `lag_1` features. |
| **Code** | `lumi_tests/pilot_run/evaluate_models.py:165-178` |
| **MAE / RMSE / MAPE** | 15,957.41 GWh / 17,806.29 GWh / **13.41%** |

**Why it failed catastrophically:**
With only 18 training observations, Random Forest memorizes the training set perfectly (training MAPE ≈ 1.45%) but generalizes poorly (test MAPE = 13.41%). The **11.95 percentage-point train-test gap** is a textbook overfitting signature. Random Forest needs thousands of observations to generalize; with 18, it builds hundreds of mini-trees that memorize instead of learning.

**Key finding:** Worst overall. Included as a **controlled experiment** to empirically justify the thesis decision to use parsimonious statistical models instead of advanced ML.

> | Observation | Result |
> |---|---|
> | Training MAPE | 1.45% (near-perfect fit) |
> | Test MAPE | 13.41% (significantly worse than statistical models) |
> | Train-Test Gap | −11.95 percentage points (classic overfitting) |
>
> *Source:* `lumi_tests/docs/ml_evaluation_framework.md:7`

---

### 3. Theoretically Evaluated Models (Feasibility Study)

The following models were assessed in the `docs/04-ML-Data-Science/LUMI_ML_MODEL_ANALYSIS.md` feasibility study. They were evaluated for architectural fit, data requirements, and deployment constraints, but **were not empirically trained** because the current dataset and infrastructure do not support them.

| Model | Suitability Verdict | Expected MAPE | Rationale |
|---|---|---|---|
| **LSTM** | **LOW** | — | Needs hundreds to thousands of time steps per series; LUMI has only 84 monthly steps per municipality. Heavy deployment (~300–400 MB framework). |
| **Prophet** | **MEDIUM** | 7–12% | Good for seasonality and missing data, but the Stan/CmdStanPy backend adds ~100 MB. One model per municipality = maintenance overhead. |
| **XGBoost / LightGBM** | **HIGH** (Recommended for Phase 2) | 5–10% | State-of-the-art on tabular data. Single global model can learn across all municipalities. Serialized size < 20 MB; inference < 100 MB RAM; sub-millisecond latency. |
| **Temporal Fusion Transformer (TFT)** | **OVERKILL** | — | Needs 100K+ samples and rich static/dynamic covariates. Requires PyTorch. Deployment on Render free tier is impractical. |
| **Naive / ETS** | **BASELINE** | — | Essential floor reference. Any deployed model must significantly beat this before it is justified. |

*Source:* `docs/04-ML-Data-Science/LUMI_ML_MODEL_ANALYSIS.md:4-6`

#### 3.1 Why LightGBM Is the Theoretical Future Choice

LightGBM (or XGBoost) represents the **practical sweet spot** for LUMI if the dataset grows:

1. **Data fit:** Treats forecasting as supervised regression on engineered temporal features (lags, rolling stats, cyclic encoding), sidestepping the need for sequential deep learning.
2. **Scale:** A single global model with geographic embeddings learns region-specific patterns without maintaining 1,600 separate models.
3. **Deployment fit:** Serialized model < 20 MB; inference uses < 100 MB RAM; cold-start < 1 s on Render.
4. **Accuracy:** Gradient boosting is empirically superior to LSTM on small-to-medium tabular forecasting tasks.
5. **Interpretability:** SHAP values explain why a municipality's forecast is high or low.

*Source:* `docs/04-ML-Data-Science/LUMI_ML_MODEL_ANALYSIS.md:7.1`

---

### 4. LLM / Generative AI Evaluation

The AI Chat layer integrates **Google Gemini 2.5 Flash** (primary) and **Groq-hosted Llama 3** (fallback). Because these are **generative models** producing free-form natural language and structured JSON, traditional classification metrics are mathematically inapplicable.

#### 4.1 Why Accuracy, Recall, and F1 Fail for LLMs

1. **No ground-truth label:** For a query like *"What renewable energy is best for Tinambac, Camarines Sur?"* there is no single "correct" class. The answer depends on budget, terrain, grid access, and policy priorities.
2. **No fixed output space:** The LLM can generate thousands of valid phrasings of the same recommendation.
3. **No confusion matrix:** There is no TP/FP/TN/FN for generative text.

*Source:* `lumi_tests/docs/llm_evaluation_methodology.md:2`

#### 4.2 Evaluation Dimensions & Targets

| Dimension | Type | Target | Measurement Method |
|---|---|---|---|
| Response Latency | Intrinsic | < 2,000 ms (Gemini); < 500 ms (Groq) | `time.perf_counter()` |
| Token Usage | Intrinsic | < 6,000 tokens/query | API `usage_metadata` |
| Cost Efficiency | Intrinsic | < $0.005/query (Gemini) | Token count × provider rate |
| JSON Validity Rate | Intrinsic | ≥ 95% | `json.loads()` success rate |
| Schema Compliance | Intrinsic | ≥ 90% | Required field presence check |
| Hallucination Rate | Extrinsic | < 10% | Manual annotation (n = 50 responses) |
| Faithfulness | Extrinsic | ≥ 4.0 / 5 | 1–5 Likert rubric (grounding to RAG context) |
| Relevance | Extrinsic | ≥ 4.0 / 5 | 1–5 Likert rubric (query specificity) |
| Grounding Citation Rate | Extrinsic | ≥ 70% | Regex match for source citations |
| BLEU / ROUGE | Reference | 0.3–0.5 | N-gram overlap vs. reference answers |
| Human Correctness | Human | ≥ 4.0 / 5 | Expert panel (n = 4 raters) |
| Inter-Rater Kappa | Human | κ ≥ 0.60 | Cohen's Kappa |

*Source:* `lumi_tests/docs/llm_evaluation_methodology.md:3-6`

#### 4.3 Gemini vs. Groq: Comparative Summary

| Dimension | Gemini 2.5 Flash | Groq (Llama 3) |
|---|---|---|
| **Latency** | Moderate (occasional 503 overload) | Fast (Groq inference engine) |
| **Cost** | Lower ($0.15/M input tokens) | Higher ($0.59/M input tokens) |
| **RAG Grounding** | Strong (prompt engineering effective) | Moderate |
| **JSON Compliance** | High | Moderate |
| **Fallback Reliability** | Primary; sometimes overloaded | Fallback; highly available |
| **Context Window** | 1M tokens | 128K tokens |
| **Philippine Knowledge** | Moderate (general training data) | Lower (less Philippine-specific) |

**Fallback Strategy:** When Gemini returns a 503 overload error, LUMI automatically switches to Groq. The fallback is evaluated on:
1. **Availability:** Does Groq respond when Gemini fails?
2. **Quality Degradation:** Is the Groq response significantly worse for the same query?
3. **Latency Improvement:** Does fallback reduce user-perceived wait time?

*Source:* `lumi_tests/docs/llm_evaluation_methodology.md:4`

---

### 5. EcoSim Deterministic Models (Non-ML)

EcoSim's solar, wind, hydro, and geothermal calculators are **physics-based**, not data-driven machine-learning models. They use deterministic formulas derived from engineering principles and NASA POWER climate data.

#### 5.1 Why ML Was Not Used for EcoSim

1. **No ground-truth sensor data:** Actual generation readings from installed renewable systems were unavailable for supervised training.
2. **Interpretability:** Physics-based formulas are transparent, auditable, and explainable to LGU planners.
3. **Zero training cost:** No data collection, labeling, or model maintenance is required.
4. **Immediate deployability:** Formulas work the moment climate data is available.

#### 5.2 Model Types

| Energy Source | Model Type | Key Inputs |
|---|---|---|
| **Solar** | Physics-based regression | Irradiance (kWh/m²/day), temperature, panel efficiency, degradation, dust loss |
| **Wind** | Physics-based regression | Wind speed, rotor radius, power coefficient, air density, capacity factor |
| **Hydro** | Physics-based regression | Elevation, slope, hydraulic head, runoff coefficient, flow rate |
| **Geothermal** | Suitability scoring + thermal power formula | Heat flow, fault distance, volcano distance, aquifer properties, thermal conductivity |

> **Note:** While these are deterministic, they are still "models" in the scientific sense — simplified representations of physical reality. If sensor validation data becomes available in the future, MAE, MAPE, and Relative Error would be used to validate them.
>
> *Source:* `docs/THESIS_RESEARCH_INTEGRATION.md` (formula appendix)

---

### 6. Why ARIMA Was Selected

ARIMA(1,1,1) was chosen as the **production forecasting model** for the thesis despite Linear Trend Regression having a lower MAPE (4.97% vs. 5.67%). The rationale:

1. **Uncertainty Quantification:** ARIMA natively provides 95% prediction intervals (PICP), essential for honest policy planning. Linear Trend cannot do this without ad-hoc assumptions.
2. **Statistical Defensibility:** ARIMA is a classic, well-documented model with decades of economic forecasting literature. It is more defensible in an undergraduate thesis than a simple linear regression.
3. **Robustness to Trend Changes:** If the growth rate of Philippine electricity consumption changes post-2024, ARIMA's autoregressive structure can adapt; a pure linear trend cannot.
4. **Deployment Fit:** Models are < 1 MB each; inference is instantaneous; no GPU or heavy dependencies required. Runs with `statsmodels` (~50 MB).
5. **Parsimony:** The difference between Linear Trend (4.97%) and ARIMA (5.67%) is only **0.7 percentage points** — small enough that ARIMA's additional benefits outweigh the marginal accuracy cost.
6. **Thesis Scope Alignment:** The thesis explicitly specifies "basic statistical methods instead of advanced machine learning." ARIMA satisfies this while providing more capability than a naive baseline.

**Honest Acknowledgment:**
On raw test-set metrics alone, **Linear Trend Regression is the "best" model** (lowest MAE, RMSE, and MAPE). It won because Philippine national electricity consumption from 2003–2020 is almost a perfect straight line. ARIMA was selected because it is the **"best-balanced" model** — offering nearly as much accuracy while providing prediction intervals, statistical rigor, and future robustness.

---

### 7. Unified Summary Comparison Table

| Model | Task | Status | Key Metric / Result | Why It Performed That Way |
|---|---|---|---|---|
| **Linear Trend Regression** | Forecasting | Empirical Baseline | MAPE **4.97%** | Data is nearly perfectly linear; simplest model wins. |
| **Holt Smoothing** | Forecasting | Empirical Baseline | MAPE 5.44% | Recent-year weighting helped slightly, but trend is stable. |
| **Naive with Drift** | Forecasting | Empirical Baseline | MAPE 5.57% | Stable upward drift makes naive projection surprisingly accurate. |
| **ARIMA(1,1,1)** | Forecasting | **Deployed** | MAPE 5.67% | Balanced accuracy, prediction intervals, and statistical rigor. |
| **SARIMAX + Exog** | Forecasting | Empirical Test | MAPE 8.28% | Too many parameters for n = 18; overfit exogenous features. |
| **Random Forest** | Forecasting | Controlled Experiment | MAPE 13.41% | Memorized 18 training points; classic overfitting. |
| **LSTM** | Forecasting | Theoretical | — | Needs hundreds of time steps; 18 is insufficient. Heavy deployment. |
| **Prophet** | Forecasting | Theoretical | — | Good for seasonality, but Stan backend too heavy for Render free tier. |
| **LightGBM / XGBoost** | Forecasting | Theoretical / Future | — | Recommended for Phase 2 when tabular data scale increases. |
| **TFT** | Forecasting | Theoretical | — | Overkill for 84 monthly steps per municipality. |
| **Gemini 2.5 Flash** | Chat / RAG | Deployed | Latency < 2 s | Primary LLM; strong RAG grounding but occasional 503 overload. |
| **Groq Llama 3** | Chat / RAG | Deployed (Fallback) | Latency < 500 ms | Fast fallback; slightly lower quality but highly available. |
| **EcoSim Physics** | Suitability | Deployed | N/A (Deterministic) | Physics-based formulas; no training required; no overfitting risk. |

---

## Part 2: Plain-English Summary ("Explain Like I'm 10")

### The Lemonade Stand That Became a Power Plant

Imagine you run a lemonade stand. Every day you write down how many cups you sold. After a month, you have a list like this:

- Monday: 20 cups
- Tuesday: 25 cups
- Wednesday: 22 cups
- ...

Now your friend asks: **"How many cups will you sell next Monday?"**

That's basically what LUMI does — except instead of lemonade, it predicts **how much electricity the Philippines will use** next year. And instead of guessing randomly, it uses "smart math recipes" (we call them **models**) to make the best guess possible.

To find the best recipe, LUMI tried six different ones. Some were super simple. Some were very fancy. Here's what happened.

---

### The Report Card

| Model | Grade | What It Did |
|---|---|---|
| **Linear Trend Regression** | **A+** | Drew a ruler-straight line through the dots. Simple and perfect. |
| **Holt Smoothing** | **A** | Remembered recent years better than old ones. Almost as good. |
| **Naive with Drift** | **A-** | Just kept going in the same direction. Surprisingly smart! |
| **ARIMA(1,1,1)** | **A-** | Remembered last year, checked the trend, and adjusted for bumps. |
| **SARIMAX + Exog** | **B** | Tried to use extra clues but didn't have enough homework time. |
| **Random Forest** | **D** | Memorized every answer from practice. Failed the real test. |

**Winner:** Linear Trend Regression. Why? Because Philippine electricity use from 2003–2024 is almost a perfect straight line going up. The simplest model saw that clearly.

But LUMI chose **ARIMA** for the real job. Why? Because ARIMA is like a wise teacher who not only guesses the number but also says: **"I'm pretty sure it will be between THIS and THAT."** That's much more helpful when you're planning power plants!

---

### One-Sentence Takeaways for Every Model

- **Linear Trend:** "I drew a straight line through the dots and extended it." It won because the dots were already almost in a straight line!
- **ARIMA:** "I remembered last year, looked at the trend, and adjusted for bumps." It wasn't the absolute best guesser, but it was the most honest — it told you how sure it was by giving a range.
- **Holt:** "I remembered yesterday more than last week." Good for short memories.
- **Naive:** "If you sold 2 more cups every day, you'll sell 2 more tomorrow." The simplest guess, and it was almost right!
- **SARIMAX:** "I tried to look at the weather AND the lemonade sales, but I got confused because I didn't have enough practice."
- **Random Forest:** "I memorized every old test answer. When the new test came, I failed because the questions were different." This is called **overfitting**.
- **LSTM:** "I'm a super-smart brain that needs thousands of practice problems. You only gave me 18, so I couldn't learn."
- **LightGBM:** "I'm the best student in the class, but I need more homework to show it. Next year, maybe!"
- **Gemini (AI Chat):** "I'm a super-fast writer who reads books before answering. Sometimes I make up facts if I can't find the right page."
- **EcoSim:** "I use science formulas instead of guessing. I don't need practice because I follow the rules of physics."

---

### The Golden Rule

> **"The best model is not the fanciest one. It's the one that understands the data honestly and tells you the truth about its own uncertainty."**

That's why LUMI chose **ARIMA** for forecasting. It wasn't the highest scorer on the test, but it was the most trustworthy. It gave answers with a "probably between X and Y" range, which is much more helpful for grown-ups planning power plants than a single number that might be wrong.

And that's why LUMI uses **physics formulas** for EcoSim. They don't need to "practice" on old data because they follow the laws of nature. And that's why LUMI uses **two different writers** (Gemini and Groq) for the chat — so if one is too busy, the other can help out quickly.

---

## References

- `DOE_Data_Extracted/model_comparison_results.csv` — Empirical metrics for the 6 forecasting models.
- `lumi_tests/pilot_run/evaluate_models.py` — Python script implementing model fitting and evaluation.
- `lumi_tests/docs/ml_evaluation_framework.md` — Academic framework for metric selection, statistical tests, and the Random Forest controlled experiment.
- `lumi_tests/docs/lumi_metrics_and_models_for_everyone.md` — Plain-language explanations of metrics and models.
- `docs/04-ML-Data-Science/LUMI_ML_MODEL_ANALYSIS.md` — Theoretical feasibility study for LSTM, Prophet, LightGBM, and TFT.
- `lumi_tests/docs/llm_evaluation_methodology.md` — Evaluation framework for Gemini and Groq generative models.
- `docs/THESIS_RESEARCH_INTEGRATION.md` — Formula appendix for EcoSim physics-based calculators.

---

*Document generated: June 2026*
