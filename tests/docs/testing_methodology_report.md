# Testing and Evaluation Methodology for the LUMI Environmental Intelligence System

**Document Type:** Thesis Chapter Supplement — System Testing & Evaluation Methodology  
**Project:** LUMI (Lightweight Utility for Municipal Intelligence) — Data-Driven Environmental Intelligence System for Renewable Energy Decision Support  
**Version:** 1.0  
**Date:** June 2026  

---

## Abstract

This document presents the comprehensive testing and evaluation methodology employed to validate the LUMI Environmental Intelligence System. The methodology encompasses unit testing, integration testing, performance benchmarking, end-to-end pipeline validation, usability evaluation, and a pilot study for machine learning model comparison. All testing activities are grounded in ISO/IEC 25010 software quality standards and aligned with the research objectives outlined in the thesis proposal. The results of these evaluations provide empirical evidence of system correctness, reliability, and suitability for deployment as a renewable energy decision-support platform.

---

## 1. Introduction

Software testing is a critical phase in the system development life cycle that ensures the correctness, reliability, and performance of a software application (Myers et al., 2011). For decision-support systems such as LUMI — which integrates renewable energy simulation, machine learning forecasting, and artificial intelligence-based recommendation — rigorous testing is essential to validate the accuracy of computations, the integrity of data flows, and the usability of the interface.

The testing methodology described in this document is designed to address the following research objectives:

1. **RO1:** Evaluate the functional correctness of the EcoSim renewable energy simulation module.
2. **RO2:** Validate the accuracy of the EnergyHub machine learning forecasting module.
3. **RO3:** Assess the reliability and robustness of the AI intelligence layer (Gemini/Groq integration).
4. **RO4:** Measure system performance under expected operational conditions.
5. **RO5:** Evaluate system usability among target users (students, researchers, community planners).

The methodology is structured into ten phases, each addressing a distinct aspect of system quality. These phases are implemented through automated test suites, manual evaluation protocols, and comparative model validation experiments.

---

## 2. Testing Strategy and Scope

### 2.1 Testing Objectives

The primary objectives of the LUMI testing framework are:

- **Functional Correctness:** Verify that all system modules produce accurate and expected outputs for valid inputs.
- **Data Integrity:** Ensure that the Supabase PostgreSQL database maintains referential integrity, constraint compliance, and data consistency.
- **Algorithm Accuracy:** Confirm that renewable energy calculations (solar, wind, hydro) and machine learning forecasts adhere to established physics-based formulas and statistical principles.
- **AI Service Reliability:** Validate that the Gemini/Groq AI integration returns structured, grounded, and non-hallucinated responses.
- **System Performance:** Establish acceptable response-time thresholds for API endpoints, dataset loading, and prediction inference.
- **Usability Evaluation:** Determine whether target users can effectively navigate the interface and interpret results.

### 2.2 Testing Scope

#### In Scope

| Module | Features Under Test |
|---|---|
| **Authentication / User Management** | OAuth (Google, GitHub) registration, JWT token generation, protected endpoint access, token expiry |
| **EnergyHub** | Overview statistics, historical trends, ARIMA forecast (2025–2030), choropleth map data, source/grid breakdown, AI insights |
| **EcoSim** | Municipality selection, solar output calculation, wind output calculation (Betz-limit validation), hydro output calculation, economic scoring, payback period, carbon reduction |
| **AI Intelligence Layer** | Gemini prompt construction, JSON output normalization, RAG context retrieval (FAISS + sentence-transformers), fallback to Groq, error handling |
| **Database Layer** | CRUD operations, foreign key integrity, null constraints, index performance, view correctness (`regional_lookup`) |
| **Machine Learning Module** | Data preprocessing (missing values, differencing), ARIMA training, Linear Trend, Holt Smoothing, SARIMAX, Random Forest, model comparison |
| **End-to-End Pipeline** | DOE dataset → preprocessing → ML model → prediction → FastAPI → React visualization data |

#### Out of Scope

- Third-party API uptime (NASA POWER, Google Gemini, Groq) — monitored but not controlled.
- Browser compatibility testing beyond Chrome/Firefox/Edge latest stable.
- Load testing beyond 50 concurrent users (thesis-scale application).
- Security penetration testing (OWASP-level) — limited to input validation and JWT checks.

---

## 3. Testing Environment

| Component | Specification |
|---|---|
| **Operating System** | Windows 11 / Ubuntu 22.04 |
| **Python** | 3.13.2 |
| **Node.js** | 18+ |
| **Backend Framework** | FastAPI 0.115.0 (Uvicorn, port 8000) |
| **Frontend Framework** | React 18.3.1 + Vite (port 5173) |
| **Database** | Supabase PostgreSQL (cloud-managed) |
| **Test Runner** | pytest 9.1.0 |
| **HTTP Client** | httpx 0.27.2 |
| **Browser** | Google Chrome 120+ / Mozilla Firefox 121+ / Microsoft Edge |

### Environment Variables

The following environment variables are required for full test execution:

```bash
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_ANON_KEY=<anon_key>
SUPABASE_JWT_SECRET=<jwt_secret>
GEMINI_API_KEY=<gemini_key>
GROQ_API_KEY=<groq_key>
UPSTASH_REDIS_URL=<redis_url>
TEST_DATABASE_URL=<postgresql_connection_string>
```

---

## 4. Testing Phases

### Phase 1: Unit Testing

**Objective:** Validate individual functions and classes in isolation.

**Approach:** Test modules are organized by domain: renewable energy calculations, machine learning preprocessing, and AI service logic. Each test uses `pytest` with `unittest.mock` for external dependencies. Fixtures are defined in `conftest.py` and reused across test classes.

**Rationale:** Renewable energy calculations (solar, wind, hydro) contain deterministic physics formulas that can be verified with known inputs and expected outputs. ML preprocessing functions (scaling, missing-value imputation) must behave consistently regardless of the larger pipeline state. AI service functions (prompt builders, JSON parsers) should be testable without making live API calls.

**Test Files:**
- `tests/unit/test_renewable_calculations.py` — 48 tests for solar (temperature factor, dust loss, humidity degradation, performance ratio, solar_calc), wind (Betz limit validation, power estimation, input validation), and hydro (normalization, runoff coefficient, flow estimation, hydropower calculation).
- `tests/unit/test_ml_preprocessing.py` — 20 tests for data preprocessing, feature engineering, model training, and metric computation (MAE, RMSE, MAPE, R²).
- `tests/unit/test_ai_service.py` — 18 tests for prompt construction, JSON parsing, RAG retrieval mocking, and error handling.

**Key Assertions:**
- Solar temperature factor equals 1.0 at 25°C reference temperature.
- Wind power coefficient (Cp) exceeding the Betz limit (0.593) raises `ValueError`.
- Hydropower flow rate is clamped to realistic bounds [0.001, 0.5] m³/s.
- ML preprocessing handles missing values via forward-fill and backward-fill.
- AI JSON parser validates required fields (`recommended_energy_source`, `cost_range`, `explanation`, `caveats`, `environmental_impact`).

---

### Phase 2: Integration Testing — API Endpoints

**Objective:** Validate FastAPI endpoints using `httpx` and FastAPI's `TestClient`.

**Approach:** Integration tests verify schema validation, HTTP status codes, and response shapes. Tests are marked with `@pytest.mark.mock` (isolated, no live server) and `@pytest.mark.live` (requires running backend).

**Rationale:** FastAPI's dependency injection system allows overriding database and service dependencies in tests. Endpoints accept structured Pydantic schemas; integration tests verify schema validation, HTTP status codes, and response shapes. The EnergyHub and EcoSim modules expose public REST contracts that must remain stable for the React frontend.

**Test File:** `tests/integration/test_api.py`

**Endpoints Validated:**
- `GET /api/v1/health` — Health check
- `GET /api/v1/energyhub/overview` — Overview statistics
- `GET /api/v1/energyhub/forecast` — Forecast with metric parameter
- `GET /api/v1/energyhub/trends` — Historical trends
- `GET /api/v1/energyhub/map-data` — Choropleth map data
- `GET /api/v1/energyhub/source-breakdown` — Generation by source
- `GET /api/v1/energyhub/grid-breakdown` — Grid-level breakdown
- `GET /api/v1/ecosim/` — EcoSim dashboard (query params)
- `GET /api/v1/ecosim/municipalities` — Municipality list
- `POST /api/v1/ecosim/` — EcoSim simulation submission

---

### Phase 3: Integration Testing — Database Layer

**Objective:** Validate Supabase PostgreSQL schema integrity, CRUD operations, and constraint enforcement.

**Approach:** SQL assertions are executed against a test PostgreSQL instance. The `lumischema.sql` file serves as the authoritative schema reference.

**Rationale:** The schema contains composite keys, foreign key cascades, and CHECK constraints (e.g., month 1–12, year >= 2018). The `regional_lookup` view performs a 4-table join; its correctness is critical for frontend dropdowns. Hydropower suitability data is pre-computed and must not violate mathematical bounds.

**Test File:** `tests/integration/test_database.py`

**Validation Areas:**
- **Schema Existence:** All 6 expected tables, 8 indexes, and the `regional_lookup` view exist.
- **CRUD Operations:** Insert, select, update, delete for `regions`, `provinces`, `municipalities`, `municipality_climate_monthly`, `hydropower_suitability`.
- **Foreign Key Integrity:** Cross-table references (barangays → municipalities → provinces → regions) are validated via LEFT JOIN checks.
- **Constraint Validation:** Month (1–12), year (>= 2018), and NOT NULL constraints are enforced.
- **Data Type Validation:** `t2m` is DOUBLE PRECISION, `year` is SMALLINT.

---

### Phase 4: End-to-End Pipeline Testing

**Objective:** Simulate the complete data flow from DOE dataset ingestion to React visualization output.

**Approach:** The pipeline is decomposed into discrete stages: data loading → preprocessing → feature engineering → model training → forecast generation → API response formatting. Each stage is tested independently and in sequence.

**Rationale:** The EnergyHub forecast is the culmination of data extraction, cleaning, model training, artifact storage, and API serving. A break in any link (e.g., CSV column renamed, predictor loading error) is only detectable at the pipeline level.

**Test File:** `tests/integration/test_pipeline.py`

**Pipeline Stages Validated:**
1. **Data Loading:** DOE CSV loads as DataFrame with expected columns.
2. **Preprocessing:** Missing values removed; years sorted; no duplicates; consumption positive.
3. **Feature Engineering:** Trend, lag, rolling mean, and year-over-year growth features created; no NaN values remain.
4. **Model Training:** Linear regression model converges with positive coefficient; predictions have correct shape.
5. **Forecast Generation:** 6-year forecast (2025–2030) produced; confidence intervals ordered (lower < point < upper).
6. **API Formatting:** Response is a dict with `forecast` array containing `year`, `value`, `ci_lower`, `ci_upper`.

**Failure Handling Tests:**
- Empty DataFrame returns empty result.
- Missing `consumption_gwh` column raises exception.
- Single-row DataFrame loses all rows after lag creation (dropna).
- Corrupted CSV with string values raises `ValueError` on type conversion.

---

### Phase 5: Performance Testing

**Objective:** Measure execution times for key operations and validate against defined thresholds.

**Approach:** `time.perf_counter()` is used for micro-benchmarking. Target thresholds are defined in a centralized `THRESHOLDS` dictionary.

**Test File:** `tests/integration/performance_test.py`

**Metrics and Thresholds:**

| Metric | Threshold | Rationale |
|---|---|---|
| API Response Time | < 2,000 ms | User experience threshold for dashboard loading |
| Prediction Inference | < 5,000 ms | Linear regression on 22 data points should be near-instant |
| Dataset Loading | < 3,000 ms | DOE CSV (~22 rows) loads quickly; larger climate CSVs may exceed |
| RAG Retrieval | < 1,000 ms | FAISS index search on ~1,000 vectors |
| Map Aggregation | < 2,000 ms | Group 1,600 municipalities by province |
| Memory Footprint | < 10 MB (DataFrame), < 5 MB (FAISS) | Reasonable for thesis-scale deployment |

---

### Phase 6: Usability Testing

**Objective:** Evaluate the system's ease of use among target users.

**Approach:** Task-based evaluation with the System Usability Scale (SUS) questionnaire (Brooke, 1996). Participants complete 5 core tasks and rate their experience on a 10-item Likert scale.

**Test File:** `docs/usability_testing.md`

**Target User Profiles:**
- Energy Researchers (academics studying renewable energy trends)
- Community Planners (LGU staff evaluating renewable options)
- Students (undergraduate/graduate learners)
- Renewable Energy Users (homeowners considering installations)

**Task Scenarios:**
1. View regional energy consumption on the EnergyHub dashboard.
2. Run a renewable energy simulation for a specific municipality.
3. Check the ML-generated energy demand forecast for 2030.
4. Interpret the choropleth map to identify provinces with highest solar potential.
5. Read and understand the AI-generated explanation for a simulation result.

**Measurement Metrics:**
- Task Success Rate (Complete = 1.0, Partial = 0.5, Fail = 0.0)
- Completion Time (seconds)
- Errors (deviations from optimal path)
- System Usability Scale Score (0–100; target ≥ 68)

**SUS Scoring Method:**
- For odd items (1, 3, 5, 7, 9): subtract 1 from response.
- For even items (2, 4, 6, 8, 10): subtract response from 5.
- Sum converted scores and multiply by 2.5.

**Interpretation:**

| SUS Score | Adjective Rating |
|---|---|
| 85–100 | Excellent |
| 70–84 | Good |
| 50–69 | Okay |
| 0–49 | Poor |

---

### Phase 7: Pilot Run / Model Validation

**Objective:** Compare multiple forecasting models on a held-out test set using standard regression metrics.

**Approach:** Models are trained on DOE Philippine national energy demand data (2003–2023) and evaluated on the 2024 held-out year. Metrics computed: MAE, RMSE, MAPE, and R² Score.

**Script:** `pilot_run/evaluate_models.py`

**Models Evaluated:**
- **ARIMA(1,1,1):** Autoregressive integrated moving average, fitted via `statsmodels`.
- **Linear Trend Regression:** Simple linear regression on temporal trend.
- **Holt Smoothing:** Exponential smoothing with additive trend.
- **Random Forest Regressor:** Controlled experiment to demonstrate overfitting on limited time-series data.

**Outputs:**
- `pilot_results/forecast_comparison.csv` — Forecast values per model.
- `pilot_results/model_metrics.csv` — MAE, RMSE, MAPE, R² per model.
- `pilot_results/forecast_plot.png` — Visual comparison of forecasts.

**Rationale:** The thesis scope states the predictive analytics module uses "basic statistical methods" but does not evaluate them against a held-out test set in production. A controlled pilot provides quantitative evidence for model selection.

---

### Phase 8: ISO/IEC 25010 System Quality Evaluation

**Objective:** Evaluate LUMI against the eight primary quality characteristics of ISO/IEC 25010.

**Approach:** Each characteristic is rated on a 1–5 Likert scale using a weighted formula.

**Document:** `docs/iso25010_evaluation.md`

**Quality Characteristics and Weights:**

| Characteristic | Weight | Score | Evidence |
|---|---|---|---|
| Functional Suitability | 0.20 | 4 | All core features implemented; minor gaps in real-time data |
| Performance Efficiency | 0.15 | 4 | Adequate for thesis scale; no formal load testing |
| Compatibility | 0.10 | 3 | Standard REST; no data export feature |
| Usability | 0.15 | 3 | Clean UI; no formal accessibility audit |
| Reliability | 0.15 | 4 | Fallback mechanisms (Gemini → Groq) in place |
| Security | 0.10 | 4 | OAuth 2.0 + JWT + RLS; no rate limiting |
| Maintainability | 0.10 | 3 | Modular design; partial test coverage |
| Portability | 0.05 | 3 | Standard deployment; no Docker containerization |

**Final Weighted Score:** 3.60 / 5.0 (**Good**)

---

## 5. Test Case Design

### 5.1 Test Case Identification

Each test case follows a structured naming convention:

```
TC-{MODULE}-{NUMBER}
```

Where `MODULE` is a 2-letter code:
- `AU` — Authentication
- `EH` — EnergyHub
- `ES` — EcoSim
- `AI` — AI Intelligence Layer
- `DB` — Database
- `AP` — API Endpoints
- `VZ` — Visualization
- `ML` — Machine Learning

**Example:** `TC-EH-001` = EnergyHub Test Case 001 (Load regional forecast)

### 5.2 Test Case Template

| Field | Description |
|---|---|
| **Test Case ID** | Unique identifier |
| **Module** | System module under test |
| **Description** | Brief description of the test scenario |
| **Preconditions** | Required state before test execution |
| **Test Steps** | Sequential actions to perform |
| **Expected Result** | Anticipated outcome |
| **Actual Result** | Observed outcome (populated during execution) |
| **Status** | Passed / Failed / Pending |
| **Remarks** | Additional notes, references to defects |

### 5.3 Test Coverage Summary

| Module | Unit Tests | Integration Tests | Performance Tests | Total |
|---|---|---|---|---|
| Authentication | — | 2 | — | 2 |
| EnergyHub | — | 10 | 3 | 13 |
| EcoSim | 48 | 6 | 2 | 56 |
| AI / RAG | 18 | — | 2 | 20 |
| Database | — | 30 | — | 30 |
| ML / Forecasting | 20 | 15 | 2 | 37 |
| Visualization | — | — | 2 | 2 |
| **Total** | **86** | **63** | **11** | **160** |

---

## 6. Data Collection and Analysis

### 6.1 Automated Test Execution

Automated tests are executed via pytest from the `tests/` directory:

```bash
pytest tests/unit/ -v --tb=short
pytest tests/integration/test_api.py -v -m mock
pytest tests/integration/test_database.py -v
pytest tests/integration/test_pipeline.py -v
pytest tests/integration/performance_test.py -v -m local
```

Results are captured in `test_results/lumi_test_results.txt` and `test_results/unit_test_results.txt`.

### 6.2 Manual Evaluation Protocols

Usability testing follows a structured observation protocol:

1. **Pre-test Briefing:** Explain the system purpose and obtain informed consent.
2. **Task Execution:** Participant completes 5 tasks while the observer records time, errors, and notes.
3. **SUS Questionnaire:** Participant completes the 10-item SUS questionnaire.
4. **Post-test Interview:** Open-ended questions about usefulness, confusion, and recommendations.

### 6.3 Statistical Analysis

For the pilot run, model performance is compared using:

- **Mean Absolute Error (MAE):** Average magnitude of prediction errors.
- **Root Mean Squared Error (RMSE):** Square root of average squared errors; sensitive to outliers.
- **Mean Absolute Percentage Error (MAPE):** Percentage-based error; interpretable across scales.
- **Coefficient of Determination (R²):** Proportion of variance explained by the model.

The best-performing model is selected based on the lowest MAPE on the held-out 2024 test set.

---

## 7. Ethical Considerations

- All usability test participants provide **informed consent** before testing.
- Participant data is **anonymized** and stored securely.
- Participants may withdraw from the test at any time without penalty.
- No personal data collected during testing is shared outside the research team.
- API keys (Gemini, Groq, Supabase) are stored in `.env` and excluded from version control.

---

## 8. Expected Outcomes

| Evaluation | Expected Outcome |
|---|---|
| Unit Tests | ≥ 85% pass rate for core services |
| API Tests | All endpoints return expected status codes |
| Database Tests | 100% CRUD success; zero FK violations |
| Pipeline Tests | Complete execution without exceptions |
| Performance Tests | API response < 2s; prediction < 5s |
| Usability Tests | SUS score ≥ 68 (above-average usability) |
| Pilot Run | At least one model achieves MAPE < 20% |
| ISO 25010 | Overall weighted score ≥ 3.5 (Acceptable) |

---

## 9. Limitations and Future Work

1. **Test Coverage:** Integration tests for the API require a running backend or mocked dependencies. Full coverage is achieved only in a live environment.
2. **Database Testing:** The database tests require a live PostgreSQL connection (Supabase or local). Without `TEST_DATABASE_URL`, these tests raise `RuntimeError`.
3. **Performance Benchmarking:** Performance tests are hardware-dependent. Results should be interpreted relative to the development machine specifications.
4. **Usability Sample Size:** The SUS is most reliable with ≥ 10 participants per user profile. The thesis schedule may limit recruitment.
5. **Model Generalization:** The pilot run uses national-level data. Sub-national (province or municipality) forecasting is not yet implemented due to data availability constraints.

---

## 10. Conclusion

The testing and evaluation methodology presented in this document provides a systematic, evidence-based framework for validating the LUMI Environmental Intelligence System. By combining automated unit and integration tests, performance benchmarks, usability evaluation, and a controlled pilot study, the methodology ensures that all critical aspects of system quality are assessed. The results of these evaluations are documented in the accompanying test results files and serve as empirical support for the thesis claims regarding system correctness, reliability, and usability.

---

## References

- Brooke, J. (1996). SUS: A quick and dirty usability scale. *Usability Evaluation in Industry*, 189–194.
- ISO/IEC 25010:2011. (2011). *Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models*. International Organization for Standardization.
- Myers, G. J., Sandler, C., & Badgett, T. (2011). *The Art of Software Testing* (3rd ed.). Wiley.
- Pressman, R. S., & Maxim, B. R. (2015). *Software Engineering: A Practitioner's Approach* (8th ed.). McGraw-Hill.

---

## Appendix A: Test Execution Commands

```bash
# Navigate to test directory
cd tests

# Run all unit tests
pytest tests/unit/ -v

# Run integration tests (API mock mode)
pytest tests/integration/test_api.py -v -m mock

# Run integration tests (database — requires TEST_DATABASE_URL)
pytest tests/integration/test_database.py -v

# Run end-to-end pipeline tests
pytest tests/integration/test_pipeline.py -v

# Run performance benchmarks
pytest tests/integration/performance_test.py -v -m local

# Run pilot model validation
cd pilot_run
python evaluate_models.py

# Generate full test report
python run_tests_and_save.py
```

## Appendix B: File Reference

| File | Purpose |
|---|---|
| `docs/testing_strategy.md` | Testing objectives, scope, methodology |
| `docs/usability_testing.md` | SUS questionnaire, task scenarios, report template |
| `docs/iso25010_evaluation.md` | ISO/IEC 25010 quality rubric with scoring |
| `docs/test_results_template.md` | 75 test cases with Pass/Fail/Pending tracking |
| `tests/unit/conftest.py` | Shared pytest fixtures |
| `tests/unit/test_renewable_calculations.py` | Solar, wind, hydro unit tests |
| `tests/unit/test_ml_preprocessing.py` | ML preprocessing and metric tests |
| `tests/unit/test_ai_service.py` | AI prompt, JSON, RAG tests |
| `tests/integration/test_api.py` | FastAPI endpoint tests |
| `tests/integration/test_database.py` | PostgreSQL schema and CRUD tests |
| `tests/integration/test_pipeline.py` | End-to-end pipeline tests |
| `tests/integration/performance_test.py` | Performance benchmarks |
| `pilot_run/evaluate_models.py` | Model validation script |
| `run_tests_and_save.py` | Automated test runner and report generator |
| `pytest.ini` | pytest configuration with custom markers |

---

*End of Testing and Evaluation Methodology Report*
