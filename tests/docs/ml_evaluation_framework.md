# Machine Learning Evaluation Framework for the LUMI Environmental Intelligence System

**Document Type:** Thesis Chapter — Predictive Analytics Module Evaluation  
**Project:** LUMI (Lightweight Utility for Municipal Intelligence)  
**Version:** 2.0  
**Date:** June 2026  

---

## 1. Introduction and Motivation

The LUMI Environmental Intelligence System employs multiple machine learning and statistical models to support renewable energy decision-making. These models span three distinct analytical tasks:

1. **Time-Series Forecasting** — Predicting national electricity consumption and peak demand (2025–2030) using historical DOE data.
2. **Regression Estimation** — Calculating solar, wind, and hydropower output potentials from environmental parameters.
3. **Generative Recommendation** — Producing structured renewable energy recommendations via Large Language Models (Gemini/Groq).

A common misconception in undergraduate research is to apply classification metrics — such as **Accuracy**, **Precision**, **Recall**, and **F1-score** — uniformly across all machine learning tasks. This document provides a rigorous, research-based justification for selecting task-appropriate evaluation metrics, distinguishes forecasting evaluation from classification evaluation, and presents a complete experimental protocol suitable for thesis-level research.

> **Key Principle:** *Accuracy, Recall, and F1-score are defined only for discrete classification problems. They are mathematically undefined for continuous regression and time-series forecasting tasks.*

---

## 2. Why Accuracy, Recall, and F1-Score Are Inappropriate for Regression and Forecasting

### 2.1 Mathematical Definition

Classification metrics operate on **discrete label predictions** (e.g., class 0 or class 1). They require:

- A **confusion matrix**: True Positives (TP), False Positives (FP), True Negatives (TN), False Negatives (FN).
- **Accuracy** = (TP + TN) / (TP + TN + FP + FN)
- **Recall** = TP / (TP + FN)
- **Precision** = TP / (TP + FP)
- **F1-score** = 2 × (Precision × Recall) / (Precision + Recall)

For a regression or forecasting model, the output is a **continuous real-valued number** (e.g., 118,004.5 GWh). There is no "positive" or "negative" class, no confusion matrix, and consequently no TP, FP, TN, or FN. Applying classification metrics to continuous outputs is a **category error** (James et al., 2021).

### 2.2 What Happens If You Try?

Some practitioners attempt to "bin" continuous outputs into categories (e.g., "high demand" vs. "low demand") to force classification metrics. This approach:

- **Destroys information** — A forecast of 118,000 GWh vs. 120,000 GWh is treated identically if both fall in the same bin.
- **Introduces arbitrary thresholds** — The bin boundaries are subjective and dramatically affect the metric.
- **Obscures magnitude of error** — A forecast that is 10,000 GWh off receives the same penalty as one that is 100 GWh off if both are in the wrong bin.

**Recommendation:** Never use Accuracy, Recall, or F1-score for regression or forecasting tasks.

---

## 3. Task-Appropriate Evaluation Metrics

### 3.1 Decision Matrix: Which Metric for Which Task?

| ML Task | Appropriate Metrics | Inappropriate Metrics | Rationale |
|---|---|---|---|
| **Time-Series Forecasting** | MAE, RMSE, MAPE, MPE, R², AIC, BIC, Directional Accuracy, PICP | Accuracy, Recall, F1, Precision | Output is continuous; temporal ordering matters |
| **Regression (Solar/Wind/Hydro)** | MAE, RMSE, MAPE, R², Relative Error | Accuracy, Recall, F1 | Output is continuous energy output (kWh, kW) |
| **Binary Classification** | Accuracy, Precision, Recall, F1, AUC-ROC, AUC-PR | MAE, RMSE | Output is discrete (0/1); confusion matrix applies |
| **Multi-Class Classification** | Accuracy, Macro-F1, Weighted-F1, Cohen's Kappa | MAE, RMSE | Output is one of K discrete classes |
| **Generative LLM (Gemini/Groq)** | BLEU, ROUGE, Faithfulness, Relevance, Hallucination Rate, Latency, Token Usage | Accuracy, Recall, F1 (as primary) | Output is unstructured text; requires NLP-specific metrics |

### 3.2 Time-Series Forecasting Metrics (EnergyHub)

The LUMI EnergyHub module predicts Philippine national electricity consumption using models including ARIMA, Linear Trend Regression, Holt's Exponential Smoothing, and SARIMAX. The following metrics are used for evaluation:

#### 3.2.1 Scale-Dependent Metrics

**Mean Absolute Error (MAE)**

$$
\text{MAE} = \frac{1}{n} \sum_{t=1}^{n} |y_t - \hat{y}_t|
$$

- **Interpretation:** Average magnitude of forecast error in original units (GWh).
- **Advantage:** Intuitive, same units as target variable.
- **Disadvantage:** Not comparable across datasets with different scales.
- **LUMI Usage:** Primary metric for model selection. Best model: Linear Trend Regression (MAE = 5,993.83 GWh).

**Root Mean Squared Error (RMSE)**

$$
\text{RMSE} = \sqrt{\frac{1}{n} \sum_{t=1}^{n} (y_t - \hat{y}_t)^2}
$$

- **Interpretation:** Square root of average squared error; penalizes large errors more heavily than MAE.
- **Advantage:** Differentiable; useful for optimization.
- **Disadvantage:** Sensitive to outliers.
- **LUMI Usage:** Secondary metric. Best model: Linear Trend Regression (RMSE = 7,342.10 GWh).

#### 3.2.2 Scale-Independent (Percentage) Metrics

**Mean Absolute Percentage Error (MAPE)**

$$
\text{MAPE} = \frac{100}{n} \sum_{t=1}^{n} \left| \frac{y_t - \hat{y}_t}{y_t} \right|
$$

- **Interpretation:** Average percentage error; comparable across different time series.
- **Advantage:** Scale-independent; easily explained to non-technical stakeholders (LGU planners, community users).
- **Disadvantage:** Unstable when actual values are near zero (division by zero risk).
- **LUMI Usage:** Percentage-based reporting for dashboards. Philippine consumption values (tens of thousands of GWh) are safely distant from zero.
- **Best Model:** Linear Trend Regression (MAPE = 4.97%).

**Mean Percentage Error (MPE)**

$$
\text{MPE} = \frac{100}{n} \sum_{t=1}^{n} \frac{y_t - \hat{y}_t}{y_t}
$$

- **Interpretation:** Signed average percentage error; reveals systematic bias.
- **Advantage:** Identifies whether a model consistently over-forecasts (MPE > 0) or under-forecasts (MPE < 0).
- **LUMI Usage:** Bias detection. If MPE ≈ 0, the model is unbiased on average.

#### 3.2.3 Variance-Explained Metrics

**Coefficient of Determination (R²)**

$$
R^2 = 1 - \frac{\sum_{t=1}^{n} (y_t - \hat{y}_t)^2}{\sum_{t=1}^{n} (y_t - \bar{y})^2}
$$

- **Interpretation:** Proportion of variance in the target variable explained by the model.
- **Range:** (−∞, 1]. R² = 1 indicates perfect fit; R² = 0 means the model is no better than predicting the mean; R² < 0 means worse than the mean.
- **LUMI Usage:** Variance explanation for thesis defense. A high R² (e.g., > 0.90) supports the claim that the model captures the underlying trend.

#### 3.2.4 Information Criteria

**Akaike Information Criterion (AIC)**

$$
\text{AIC} = 2k - 2\ln(\hat{L})
$$

- **Interpretation:** Penalizes model complexity (number of parameters k) against goodness of fit (log-likelihood L̂).
- **Usage:** Compare models fit to the **same data**. Lower AIC is better.
- **LUMI Usage:** Compare ARIMA variants (ARIMA vs. SARIMAX). If adding exogenous variables increases AIC, the extra complexity is not justified.

**Bayesian Information Criterion (BIC)**

$$
\text{BIC} = k\ln(n) - 2\ln(\hat{L})
$$

- **Interpretation:** Similar to AIC but with a stronger penalty for model complexity (k × ln(n)).
- **Usage:** Favors simpler models more aggressively than AIC.
- **LUMI Usage:** Model parsimony selection. With n = 18 training observations, BIC strongly penalizes over-parameterized models.

#### 3.2.5 Directional Accuracy

**Directional Accuracy (DA)**

$$
\text{DA} = \frac{100}{n-1} \sum_{t=2}^{n} \mathbb{1}\left[ \text{sign}(\hat{y}_t - \hat{y}_{t-1}) = \text{sign}(y_t - y_{t-1}) \right]
$$

- **Interpretation:** Percentage of times the forecast correctly predicts the **direction** (up or down) of change.
- **Importance:** For energy policy planning, knowing whether demand will increase or decrease is often more actionable than the exact magnitude.
- **LUMI Usage:** Policy-relevance metric. A model with high DA but moderate MAE may be preferred for strategic planning.

#### 3.2.6 Prediction Interval Coverage Probability (PICP)

$$
\text{PICP} = \frac{100}{n} \sum_{t=1}^{n} \mathbb{1}\left[ y_t \in [\hat{y}_t^{\text{lower}}, \hat{y}_t^{\text{upper}}] \right]
$$

- **Interpretation:** Percentage of actual values that fall within the model's 95% prediction interval.
- **Target:** PICP ≈ 95% for a well-calibrated model.
- **LUMI Usage:** Uncertainty quantification. If PICP < 95%, the model is overconfident; if PICP > 95%, the intervals are too wide.

### 3.3 Regression Metrics (EcoSim — Solar, Wind, Hydro)

The EcoSim module uses physics-based formulas to calculate renewable energy output. While these are primarily deterministic (not ML-based), validation against external benchmarks or sensor data would use:

| Metric | Application |
|---|---|
| **MAE** | Average error in kWh between calculated and measured solar output |
| **RMSE** | Penalizes large estimation errors in hydropower potential |
| **MAPE** | Percentage error for comparing across different municipality sizes |
| **R²** | How much variance in observed output is explained by the model |
| **Relative Error** | Error normalized by the capacity of the installation |

> **Note:** The current EcoSim calculators are physics-based (not data-driven ML). These metrics would apply if validation data (e.g., actual solar generation from installed systems) were available for comparison.

### 3.4 Classification Metrics (If Applicable)

Should LUMI implement classification tasks in the future (e.g., classifying municipalities into "high/medium/low" renewable potential):

| Metric | When to Use |
|---|---|
| **Accuracy** | Balanced datasets; all classes equally important |
| **Precision** | When false positives are costly (e.g., overestimating potential) |
| **Recall** | When false negatives are costly (e.g., missing viable sites) |
| **F1-Score** | Harmonic mean of precision and recall; good for imbalanced data |
| **AUC-ROC** | Threshold-independent comparison across models |
| **Cohen's Kappa** | Agreement metric accounting for chance |

---

## 4. Statistical Comparison of Models

### 4.1 Diebold-Mariano Test

The Diebold-Mariano (DM) test (Diebold & Mariano, 2002) is the standard statistical test for comparing the forecast accuracy of two models. It tests whether the difference in forecast errors is statistically significant.

**Null Hypothesis (H₀):** The two models have equal forecast accuracy.
**Alternative Hypothesis (H₁):** The two models have different forecast accuracy.

**Procedure:**
1. Compute the loss differential: $d_t = L(e_{1t}) - L(e_{2t})$
2. For MAE-based loss: $L(e) = |e|$
3. Compute the DM statistic: $DM = \frac{\bar{d}}{\sqrt{\widehat{\text{Var}}(\bar{d})}}$
4. Compare against the standard normal distribution.

**LUMI Application:** Compare Linear Trend Regression vs. ARIMA(1,1,1) vs. Holt Smoothing on the 2021–2024 test set. If DM > 1.96 (p < 0.05), the difference is significant at the 5% level.

### 4.2 Wilcoxon Signed-Rank Test

For non-normally distributed errors (common with small samples), the Wilcoxon signed-rank test provides a non-parametric alternative to the paired t-test.

**LUMI Application:** With only n = 4 test observations (2021–2024), normality assumptions are tenuous. The Wilcoxon test is more appropriate for assessing whether one model's absolute errors are systematically smaller than another's.

### 4.3 Model Selection Criteria Summary

| Criterion | Purpose | Best Value |
|---|---|---|
| Lowest MAE | Minimum average error | Smallest |
| Lowest RMSE | Minimum squared error (outlier-sensitive) | Smallest |
| Lowest MAPE | Minimum percentage error | Smallest |
| Highest R² | Maximum variance explained | Largest |
| Lowest AIC | Best trade-off fit vs. complexity | Smallest |
| Lowest BIC | Best parsimonious model | Smallest |
| Highest DA | Best directional guidance | Largest |
| PICP ≈ 95% | Best-calibrated uncertainty | Closest to 95% |

---

## 5. Computational Performance Metrics

Beyond predictive accuracy, the LUMI system must operate within acceptable computational bounds:

| Metric | Definition | LUMI Threshold | Measurement |
|---|---|---|---|
| **Training Time** | Wall-clock time to fit the model | < 30 s | `time.perf_counter()` |
| **Inference Time** | Wall-clock time to generate a single forecast | < 100 ms | `time.perf_counter()` |
| **Memory Footprint** | Peak RAM usage during training | < 500 MB | `psutil.Process().memory_info()` |
| **Model Size** | Disk space of serialized model | < 10 MB | `os.path.getsize()` |

**Rationale:** The thesis scope specifies "basic statistical methods instead of advanced machine learning, to improve computational costs." These metrics empirically validate that claim.

---

## 6. Experimental Procedure for Undergraduate Thesis

### 6.1 Dataset Preparation

1. **Source:** Philippine Department of Energy (DOE) Statistical Bulletin, 2003–2024.
2. **Variables:** Total electricity consumption (GWh), peak demand (MW), renewable generation (GWh), dependable capacity (MW), capacity margin (%).
3. **Preprocessing:**
   - Handle missing values via forward-fill and backward-fill.
   - Convert year to integer index.
   - Engineer features: renewable_share_pct, capacity_margin_pct.
   - Verify no duplicate years.

### 6.2 Train-Test Separation

- **Training Set:** 2003–2020 (n = 18 observations)
- **Test Set:** 2021–2024 (n = 4 observations, held out)
- **Rationale:** 18 training points are sufficient for parsimonious statistical models (ARIMA, Holt) but insufficient for advanced ML (LSTM, XGBoost). The 4-year test set provides an out-of-sample accuracy estimate while leaving the most recent data for evaluation.

### 6.3 Experimental Procedure

1. **Fit Baseline Models:**
   - Naive with Drift (accuracy floor)
   - Linear Trend Regression (interpretable baseline)
2. **Fit Core Models:**
   - ARIMA(1,1,1) — thesis core model
   - Holt Linear Smoothing — trend-aware baseline
   - SARIMAX(1,1,1) + Exogenous — extended model with external variables
3. **Fit Controlled Experiment:**
   - Random Forest Regression — demonstrates ML overfitting on limited data
4. **Evaluate All Models:**
   - Compute MAE, RMSE, MAPE, R², MPE on test set.
   - Compute AIC, BIC from fitted models.
   - Compute directional accuracy.
   - Compute PICP for models with prediction intervals.
   - Record training and inference times.
5. **Statistical Comparison:**
   - Diebold-Mariano test between top-3 models.
   - Wilcoxon signed-rank test as non-parametric validation.
6. **Select Best Model:**
   - Lowest MAPE on test set (primary criterion).
   - Lowest AIC/BIC (secondary criterion for parsimony).
   - Highest directional accuracy (policy relevance).
7. **Generate Final Forecast:**
   - Retrain best model on full data (2003–2024).
   - Project 2025–2030 with 95% confidence intervals.

### 6.4 Interpretation of Results

| Scenario | Interpretation |
|---|---|
| Best model MAPE < 10% | Highly accurate; suitable for policy planning |
| Best model MAPE 10–20% | Acceptable; acknowledge uncertainty in discussion |
| Best model MAPE > 20% | Poor; consider data limitations or model reformulation |
| R² > 0.90 | Model captures most variance; strong explanatory power |
| R² < 0.70 | Weak fit; consider missing variables or non-linearities |
| DM test p < 0.05 | Difference between models is statistically significant |
| DA > 80% | Model reliably predicts direction; valuable for strategic planning |
| PICP ≈ 95% | Well-calibrated uncertainty; trust intervals |

---

## 7. Random Forest as a Controlled Experiment

The thesis scope specifies "basic statistical methods instead of advanced machine learning." To empirically justify this decision, a Random Forest Regressor was included as a **controlled experiment**:

| Observation | Result |
|---|---|
| Training MAPE | 1.45% (near-perfect fit) |
| Test MAPE | 13.41% (significantly worse than statistical models) |
| Train-Test Gap | −11.95 percentage points (classic overfitting signature) |
| Comparison | Random Forest underperforms Linear Trend (4.97% MAPE) and ARIMA (5.67% MAPE) |

**Conclusion:** Even with constrained hyperparameters (max_depth=3, min_samples_leaf=2), Random Forest overfits severely on n = 18 training observations. This confirms the thesis decision to use parsimonious statistical models.

---

## 8. LLM Evaluation: Why Traditional Metrics Fail for Gemini and Groq

Google Gemini and Groq-hosted LLMs are **generative models**, not classifiers. Their output is free-form natural language (and structured JSON), not a discrete class label. Traditional Accuracy, Recall, and F1 are inapplicable because:

1. **No ground-truth label:** For a query like "What renewable energy is best for Tinambac, Camarines Sur?" there is no single "correct" class. The answer depends on climate, budget, terrain, and policy context.
2. **No fixed output space:** The LLM can generate thousands of valid phrasings of the same recommendation.
3. **No confusion matrix:** There is no TP/FP/TN/FN for generative text.

Instead, LLM evaluation requires **NLP-specific metrics** and **human evaluation** (see `llm_evaluation_methodology.md` for the complete framework).

---

## 9. Summary: Correct Metrics by LUMI Module

| LUMI Module | Task Type | Primary Metrics | Secondary Metrics |
|---|---|---|---|
| **EnergyHub — Forecasting** | Time-Series Regression | MAE, MAPE, R² | RMSE, MPE, AIC, BIC, DA, PICP |
| **EnergyHub — Model Selection** | Statistical Comparison | Diebold-Mariano, Wilcoxon | AIC, BIC, Train Time |
| **EcoSim — Solar Calc** | Physics-Based Regression | MAE, MAPE (if validated) | RMSE, Relative Error |
| **EcoSim — Wind Calc** | Physics-Based Regression | MAE, MAPE (if validated) | RMSE, Relative Error |
| **EcoSim — Hydro Calc** | Physics-Based Regression | MAE, MAPE (if validated) | RMSE, Relative Error |
| **AI Layer — Gemini/Groq** | Generative Text | BLEU, ROUGE, Faithfulness | Hallucination Rate, Latency, Cost |
| **System — Performance** | Engineering | Response Time, Memory | Throughput, Availability |

---

## 10. References

- Box, G. E. P., Jenkins, G. M., Reinsel, G. C., & Ljung, G. M. (2016). *Time Series Analysis: Forecasting and Control* (5th ed.). Wiley.
- Diebold, F. X., & Mariano, R. S. (2002). Comparing predictive accuracy. *Journal of Business & Economic Statistics*, 20(1), 134–144.
- Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and Practice* (3rd ed.). OTexts.
- James, G., Witten, D., Hastie, T., & Tibshirani, R. (2021). *An Introduction to Statistical Learning* (2nd ed.). Springer.
- Makridakis, S., Spiliotis, E., & Assimakopoulos, V. (2022). The M5 Competition: Results and findings. *International Journal of Forecasting*, 38(4), 1356–1363.
- Wang, Y., et al. (2024). Short-term load forecasting using LSTM networks: A comparative study. *Energy*, 288, 129656.

---

*End of Machine Learning Evaluation Framework*
