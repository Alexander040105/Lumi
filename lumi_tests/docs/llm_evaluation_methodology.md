# Large Language Model Evaluation Methodology for the LUMI AI Intelligence Layer

**Document Type:** Thesis Chapter — AI/NLP Module Evaluation  
**Project:** LUMI (Lightweight Utility for Municipal Intelligence)  
**Version:** 1.0  
**Date:** June 2026  

---

## 1. Introduction

The LUMI Environmental Intelligence System integrates **Google Gemini** and **Groq-hosted LLMs** (e.g., Llama 3) to provide structured renewable energy recommendations for Philippine municipalities. Unlike traditional machine learning classifiers — which predict discrete labels — these models are **generative systems** that produce free-form natural language and structured JSON outputs.

This fundamental difference means that **Accuracy, Recall, and F1-score are mathematically inapplicable** as primary evaluation metrics for Gemini and Groq. Instead, LLM evaluation requires a multi-dimensional framework that measures:

1. **Response quality** — Is the output factually correct, relevant, and actionable?
2. **Grounding fidelity** — Does the model rely on retrieved knowledge (RAG context) rather than hallucinating?
3. **System efficiency** — Is the response fast, cost-effective, and reliable?
4. **Human preference** — Do domain experts and target users find the recommendations useful?

This document presents a research-based evaluation methodology suitable for an undergraduate thesis, drawing on practices from the NLP and AI evaluation literature (2021–2026).

---

## 2. Why Accuracy, Recall, and F1-Score Cannot Evaluate Generative LLMs

### 2.1 The Category Error

Classification metrics require a **fixed set of discrete labels** and a **ground-truth label** for each input. For example:

- Input: "Is this email spam?"
- Possible outputs: {Spam, Not Spam}
- Ground truth: Spam
- Accuracy = 1 if prediction = Spam, else 0

For a generative LLM in LUMI:

- Input: "What renewable energy is best for Tinambac, Camarines Sur?"
- Possible outputs: **Infinite valid responses** — "Solar panels are recommended due to high irradiance," "A 5kW rooftop solar system with battery backup," "Given the municipality's 4.5 kWh/m²/day solar irradiance..."
- Ground truth: **Does not exist as a single label.** The "correct" answer depends on budget, terrain, grid access, and policy priorities.

### 2.2 No Confusion Matrix Exists

There is no TP/FP/TN/FN for generative text. The LLM does not choose from a fixed set of classes; it **generates** a unique string every time. Even for constrained JSON output, the values within fields (e.g., `"cost_range": "PHP 150,000–250,000"`) are continuous estimates, not discrete labels.

### 2.3 What Practitioners Sometimes Do (And Why It Is Wrong)

Some researchers attempt to:
- **Token-level accuracy:** Compare generated tokens to a reference answer token-by-token. This is overly strict — "solar" and "photovoltaic" are semantically equivalent but would register as a mismatch.
- **Forced classification:** Reduce the recommendation to a single label (solar/wind/hydro) and apply accuracy. This destroys nuance — a recommendation might say "solar is best, but hydro is viable if budget allows." Forcing a single label loses critical information.

**Recommendation:** Use NLP-native metrics and human evaluation, not classification metrics.

---

## 3. LLM Evaluation Dimensions

### 3.1 Intrinsic (Automated) Metrics

These metrics can be computed automatically during or after inference.

#### 3.1.1 Response Latency

**Definition:** Wall-clock time from API request to fully parsed response.

$$
\text{Latency} = t_{\text{response}} - t_{\text{request}}
$$

| Threshold | Interpretation |
|---|---|
| < 1,000 ms | Excellent — seamless user experience |
| 1,000–3,000 ms | Acceptable — slight delay, tolerable for research |
| 3,000–5,000 ms | Marginal — user may perceive sluggishness |
| > 5,000 ms | Poor — requires optimization or fallback |

**LUMI Measurement:** Wrap the `generate_response()` call in `time.perf_counter()`:

```python
import time
start = time.perf_counter()
response = generate_response(prompt, model="gemini-2.5-flash")
latency_ms = (time.perf_counter() - start) * 1000
```

**LUMI Target:** < 2,000 ms for RAG + Gemini pipeline; < 500 ms for Groq fallback.

#### 3.1.2 Token Usage

**Definition:** Total tokens consumed (input prompt + output response).

| Component | LUMI Typical Range |
|---|---|
| Input (RAG context + prompt) | 2,000–5,000 tokens |
| Output (JSON response) | 300–800 tokens |
| Total per query | 2,300–5,800 tokens |

**Measurement:** Gemini API returns `usage_metadata`:

```python
tokens_in = response.usage_metadata.prompt_token_count
tokens_out = response.usage_metadata.candidates_token_count
total_tokens = tokens_in + tokens_out
```

**LUMI Usage:** Track token consumption to estimate API costs and identify prompts that are unnecessarily verbose.

#### 3.1.3 Cost Efficiency

**Definition:** Cost per query, derived from token usage and provider pricing.

| Provider | Input Cost (per 1M tokens) | Output Cost (per 1M tokens) |
|---|---|---|
| Gemini 2.5 Flash | ~$0.15 | ~$0.60 |
| Groq (Llama 3 70B) | ~$0.59 | ~$0.79 |

$$
\text{Cost} = \frac{\text{tokens}_{\text{in}} \times \text{input\_rate} + \text{tokens}_{\text{out}} \times \text{output\_rate}}{1,000,000}
$$

**LUMI Target:** < $0.005 per query (Gemini Flash at typical token count).

#### 3.1.4 JSON Validity Rate

**Definition:** Percentage of responses that parse as valid JSON.

$$
\text{JSON Validity Rate} = \frac{\text{Valid JSON Responses}}{\text{Total Responses}} \times 100
$$

**Measurement:**

```python
import json
valid = 0
for response in responses:
    try:
        json.loads(response)
        valid += 1
    except json.JSONDecodeError:
        pass
rate = (valid / len(responses)) * 100
```

**LUMI Target:** ≥ 95%. The prompt explicitly instructs JSON output, but LLMs occasionally wrap JSON in markdown code blocks or omit closing braces.

#### 3.1.5 Schema Compliance Rate

**Definition:** Percentage of valid JSON responses that contain all required fields.

**Required Fields (LUMI RAG Response):**
- `recommended_energy_source`
- `estimated_budget` (with `equipment`, `installation`, `maintenance`)
- `cost_range`
- `explanation`
- `limitations`

**Measurement:**

```python
required = ["recommended_energy_source", "estimated_budget", "cost_range", "explanation", "limitations"]
compliant = all(field in parsed_json for field in required)
```

**LUMI Target:** ≥ 90%.

### 3.2 Extrinsic (Quality) Metrics

These metrics assess the semantic and factual quality of responses.

#### 3.2.1 Hallucination Rate

**Definition:** Percentage of factual claims in the response that cannot be verified against the retrieved RAG context.

**Procedure:**
1. Extract all factual claims from the LLM response (e.g., "solar irradiance is 4.5 kWh/m²/day").
2. Check each claim against the RAG retrieved chunks.
3. A claim is a **hallucination** if it contradicts the context or cannot be found in it.

$$
\text{Hallucination Rate} = \frac{\text{Hallucinated Claims}}{\text{Total Factual Claims}} \times 100
$$

**LUMI Target:** < 10%. The prompt includes strong grounding rules ("ALL facts MUST come from retrieved knowledge"), but LLMs may still generate plausible-sounding but unverified figures.

**Measurement Method:** Manual annotation by the researcher on a sample of 50 responses.

#### 3.2.2 Faithfulness (Grounding Score)

**Definition:** The degree to which the response is entailed by and consistent with the retrieved context.

**Scoring Rubric (1–5 Likert Scale):**

| Score | Description |
|---|---|
| 5 | All claims are directly supported by retrieved context; no external knowledge used |
| 4 | Most claims are supported; minor details from parametric knowledge |
| 3 | Mix of retrieved and parametric knowledge; no contradictions |
| 2 | Significant parametric knowledge used; some claims not verifiable |
| 1 | Response relies primarily on internal knowledge; contradicts retrieved context |

**LUMI Target:** Mean score ≥ 4.0.

#### 3.2.3 Relevance Score

**Definition:** The degree to which the response directly addresses the user's query and municipality context.

**Scoring Rubric (1–5 Likert Scale):**

| Score | Description |
|---|---|
| 5 | Directly answers the question with municipality-specific details |
| 4 | Answers the question with general Philippine context |
| 3 | Partially answers; some information is tangential |
| 2 | Off-topic or generic; could apply to any municipality |
| 1 | Completely irrelevant or unresponsive |

**LUMI Target:** Mean score ≥ 4.0.

#### 3.2.4 Grounding Citation Rate

**Definition:** Percentage of responses that explicitly cite specific knowledge sources (e.g., "solar panel equipment cost" or "national_energy_statistics").

**Measurement:** Regex match for source category names in the response text.

**LUMI Target:** ≥ 70%. The prompt instructs citation, but LLMs do not always comply.

#### 3.2.5 BLEU and ROUGE Scores (Reference-Based)

**BLEU (Bilingual Evaluation Understudy):**
- Measures n-gram overlap between generated text and a reference answer.
- Range: 0–1. Higher is better.
- **Limitation:** BLEU penalizes valid paraphrases. A score of 0.3–0.5 is typical for open-domain generation.

**ROUGE (Recall-Oriented Understudy for Gisting Evaluation):**
- Measures recall of n-grams against reference summaries.
- ROUGE-L measures longest common subsequence.
- **Limitation:** Requires a reference answer, which may not exist for novel queries.

**LUMI Application:** Compute BLEU/ROUGE against 20 reference responses prepared by the researcher for common queries (e.g., "What is the best renewable energy for General Santos City?").

### 3.3 Human Evaluation Protocol

Automated metrics capture surface-level quality but cannot assess **actionability**, **correctness of reasoning**, or **policy relevance**. Human evaluation is essential.

#### 3.3.1 Expert Panel Composition

| Role | Number | Expertise |
|---|---|---|
| Renewable Energy Engineer | 1 | Validates technical correctness of recommendations |
| Environmental Scientist | 1 | Validates climate and terrain assertions |
| Community Planner / LGU Staff | 1 | Assesses actionability and policy relevance |
| Computer Science Researcher | 1 | Assesses AI output quality and hallucination |

#### 3.3.2 Evaluation Sample

- **50 responses** covering 10 representative municipalities (5 queries each).
- Municipalities selected for diversity: high-solar (Ilocos), high-wind (Batanes), high-hydro (Ifugao), mixed (Cebu), urban (Manila).

#### 3.3.3 Rating Dimensions

Each response is rated on a 5-point Likert scale for:

1. **Correctness** — Are all facts, figures, and technical claims accurate?
2. **Completeness** — Does the response address budget, installation, maintenance, and caveats?
3. **Clarity** — Is the response understandable to a non-technical LGU staff member?
4. **Actionability** — Can the user take concrete next steps based on this recommendation?
5. **Municipality Specificity** — Is the recommendation tailored to the specific municipality's climate and terrain?

#### 3.3.4 Inter-Rater Reliability

Compute **Cohen's Kappa (κ)** between each pair of raters:

| κ | Interpretation |
|---|---|
| 0.81–1.00 | Almost perfect agreement |
| 0.61–0.80 | Substantial agreement |
| 0.41–0.60 | Moderate agreement |
| 0.21–0.40 | Fair agreement |
| 0.00–0.20 | Slight agreement |

**LUMI Target:** κ ≥ 0.60 (substantial agreement) for all dimension pairs.

---

## 4. Gemini vs. Groq: Comparative Evaluation

### 4.1 Evaluation Dimensions

| Dimension | Gemini 2.5 Flash | Groq (Llama 3) |
|---|---|---|
| **Latency** | Moderate (often 503 overload) | Fast (Groq inference engine) |
| **Cost** | Lower ($0.15/M input tokens) | Higher ($0.59/M input tokens) |
| **RAG Grounding** | Strong (prompt engineering effective) | Moderate |
| **JSON Compliance** | High | Moderate |
| **Fallback Reliability** | Primary; sometimes overloaded | Fallback; highly available |
| **Context Window** | 1M tokens | 128K tokens |
| **Philippine Knowledge** | Moderate (general training data) | Lower (less Philippine-specific) |

### 4.2 Fallback Strategy Evaluation

LUMI uses Groq as a fallback when Gemini is overloaded. The fallback is evaluated on:

1. **Availability:** Does Groq respond when Gemini returns 503?
2. **Quality Degradation:** Is the Groq response significantly worse than Gemini for the same query?
3. **Latency Improvement:** Does fallback reduce user-perceived wait time?

**Measurement:** Log all fallback events and compare response quality scores (faithfulness, relevance) between Gemini and Groq for the same queries.

---

## 5. LLM Query Logging Schema

To enable continuous evaluation, all LLM queries are logged to a database table:

```sql
CREATE TABLE IF NOT EXISTS public.llm_query_log (
    log_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_timestamp     TIMESTAMPTZ DEFAULT NOW(),
    user_id             UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    model_name          TEXT NOT NULL,          -- e.g., 'gemini-2.5-flash', 'groq-llama3-70b'
    is_fallback         BOOLEAN DEFAULT FALSE,
    prompt_text         TEXT NOT NULL,
    prompt_tokens       INTEGER,
    response_text       TEXT,
    response_tokens     INTEGER,
    latency_ms          DOUBLE PRECISION,
    estimated_cost_usd  DOUBLE PRECISION,
    is_valid_json       BOOLEAN,
    has_all_fields      BOOLEAN,
    municipality_id     INTEGER,
    renewable_type      TEXT,                   -- 'solar', 'wind', 'hydro', or NULL
    error_message       TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_llm_query_model ON public.llm_query_log (model_name, query_timestamp DESC);
CREATE INDEX idx_llm_query_user ON public.llm_query_log (user_id, query_timestamp DESC);
CREATE INDEX idx_llm_query_municipality ON public.llm_query_log (municipality_id);
```

**Rationale:** This table enables:
- Cost tracking and API usage monitoring
- A/B testing between Gemini and Groq
- Post-hoc hallucination analysis
- Response time trend analysis
- Debugging of JSON parsing failures

---

## 6. Summary: LLM Evaluation Checklist

| Metric | Type | Target | How to Measure |
|---|---|---|---|
| Response Latency | Intrinsic | < 2,000 ms | `time.perf_counter()` |
| Token Usage | Intrinsic | < 6,000 tokens/query | API `usage_metadata` |
| Cost Efficiency | Intrinsic | < $0.005/query | Token count × rate |
| JSON Validity Rate | Intrinsic | ≥ 95% | `json.loads()` success rate |
| Schema Compliance | Intrinsic | ≥ 90% | Required field presence check |
| Hallucination Rate | Extrinsic | < 10% | Manual annotation (n=50) |
| Faithfulness | Extrinsic | ≥ 4.0 / 5 | Expert rubric |
| Relevance | Extrinsic | ≥ 4.0 / 5 | Expert rubric |
| Grounding Citation | Extrinsic | ≥ 70% | Regex source citation match |
| BLEU / ROUGE | Reference | 0.3–0.5 | Compare to reference answers |
| Human Correctness | Human | ≥ 4.0 / 5 | Expert panel (n=4) |
| Human Actionability | Human | ≥ 4.0 / 5 | Expert panel (n=4) |
| Inter-Rater Kappa | Human | κ ≥ 0.60 | Cohen's Kappa |

---

## 7. Key Distinction: Forecasting Model vs. LLM Evaluation

| Aspect | Forecasting Model (ARIMA, Holt) | LLM (Gemini, Groq) |
|---|---|---|
| **Output Type** | Continuous number (GWh, MW) | Free-form text / structured JSON |
| **Ground Truth** | Historical measured data | No single correct answer |
| **Primary Metrics** | MAE, RMSE, MAPE, R² | Hallucination rate, Faithfulness, Relevance |
| **Statistical Tests** | Diebold-Mariano, Wilcoxon | N/A (no ground truth for significance testing) |
| **Evaluation Method** | Automated against held-out data | Human evaluation + automated NLP metrics |
| **Error Type** | Quantitative deviation | Factual incorrectness, hallucination, irrelevance |
| **Optimization Target** | Minimize prediction error | Maximize factual grounding + user usefulness |

---

## 8. References

- Chiang, C.-H., et al. (2024). Evaluating large language models: A survey. *ACM Computing Surveys*, 57(1), 1–38.
- Liu, Y., et al. (2023). G-Eval: NLG evaluation using GPT-4 with better human alignment. *EMNLP 2023*.
- Papineni, K., et al. (2002). BLEU: A method for automatic evaluation of machine translation. *ACL 2002*.
- Rajpurkar, P., et al. (2016). SQuAD: 100,000+ questions for machine comprehension of text. *EMNLP 2016*.
- Wang, B., et al. (2023). Faithfulness evaluation of text generation: A survey. *Findings of ACL 2023*.
- Zheng, L., et al. (2024). Judging LLM-as-a-judge with MT-bench and chatbot arena. *NeurIPS 2024*.

---

*End of LLM Evaluation Methodology*
