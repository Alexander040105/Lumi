# 9.8. Testing and Evaluation

This section presents the testing and evaluation activities conducted for LUMI, aligned with the actual test suite, evaluation framework, and quality assessment instruments implemented in the project repository.

## 9.8.1. Unit Testing

Unit testing was performed during development to verify individual functions and modules in isolation before integration. The test suite is organized under `lumi_tests/tests/unit/` and implemented using **pytest** with `unittest.mock` for external dependencies.

**Renewable Energy Calculations** (`test_renewable_calculations.py`) covers solar (temperature factor, dust loss, humidity degradation, performance ratio, and `solar_calc` with score capping), wind (Betz-limit validation, cubic power scaling, swept area and rated power computation), and hydro (runoff coefficient by slope, flow rate bounding, hydropower with zero-flow handling, and head clamping). Edge cases include None inputs, boundary values, and invalid physical parameters. Economic summary tests (`TestCalculateOptionSummary`, RE-017) validate `_calculate_option_summary` for solar, wind, and geothermal scenarios, asserting suitability score bounds, positive payback periods, and correct scale classification (residential vs. utility).

**Geothermal Calculations** (`test_geothermal_calculations.py`) covers haversine distance, fault and volcano proximity, heat flow normalization (40–120 mW/m² range), geothermal gradient (`G = q/k`), reservoir temperature (`T_res = T_surf + G × depth`), aquifer composite scoring (permeability, porosity, thickness), flow rate estimation, overall suitability scoring with classification (High/Good/Moderate/Low), and energy output computation (thermal power, electric power, annual energy GWh) for binary and flash plant types. Edge cases include missing surface temperature fallback (Philippine average 27°C), zero/negative thermal conductivity rejection, and insufficient data handling.

**Machine Learning Preprocessing** (`test_ml_preprocessing.py`) validates missing-value imputation via `ffill()` and `bfill()`, integer year conversion, time-feature creation (monotonic trend and lag variables), train-test splitting with temporal ordering, linear trend forecast accuracy on perfectly linear series, and MAPE calculation with zero-value exclusion.

**AI Service Layer** (`test_ai_service.py`) tests prompt construction (simulation data inclusion, JSON grounding rules, RAG context injection), JSON parsing and schema validation, cosine similarity bounds, chunk filtering by `renewable_type`, score threshold filtering, and graceful handling of missing API keys and malformed responses. All Gemini and Groq calls are mocked.

**Frontend Component Tests** (`react-frontend/src/components/__tests__/DashboardChart.test.jsx`) use **Vitest** with `@testing-library/react` and `jsdom` to validate dashboard chart rendering with mock data points (FE-001) and AI chat input validation error display (FE-004). Additional frontend coverage is implemented via manual UI walkthroughs during usability testing.

A module is considered compliant when its test suite achieves at least **70% statement coverage** for core services and all critical-path functions have dedicated test cases.

## 9.8.2. Usability Testing

Usability testing evaluates how effectively target users learn to operate LUMI, complete common tasks, and interpret presented information. It covers dashboard navigation, forecast exploration, Ecosim configuration, map interaction, chart interpretation, and AI assistant query formulation.

A combination of task-based observation and post-task questionnaires is employed. Participants think aloud while completing predefined tasks of increasing complexity. Observers record task completion times, error counts, help requests, and subjective comments. The **System Usability Scale (SUS)** and a custom Likert-scale questionnaire are administered after testing.

Each participant attends a single 45-60 minute session beginning with a brief demographic questionnaire, followed by tasks such as identifying recent electricity consumption values on the EnergyHub dashboard, generating a renewable energy recommendation via Ecosim, interpreting choropleth map colors, and asking the AI assistant about solar energy suitability. Observers record success status, time taken, errors, and verbal feedback.

Evaluation criteria include **task completion rate >= 85%**, average task time <= 90 seconds for simple tasks and <= 5 minutes for complex tasks, **SUS score >= 68**, and average Likert ratings >= 4.0 for clarity and satisfaction. Participants are recruited from three groups: household decision-makers (non-technical primary users), renewable energy professionals (domain experts), and technical users (students/researchers in computer science, engineering, or environmental science). The questionnaire covers demographics, task experience (difficulty rating 1-5), interface assessment (label clarity, chart readability, map usefulness, AI quality), and overall satisfaction (likelihood to recommend, perceived usefulness, trust in recommendations), plus open feedback.

## 9.8.3. System Testing

System testing validates LUMI's integrated functionality as a complete application, ensuring correct module interaction, consistent data flows, and reliable behavior under realistic usage. The integration test suite is located under `lumi_tests/tests/integration/`.

**API Integration Tests** (`test_api.py`) use FastAPI's `TestClient` and `httpx` to verify endpoint status codes, response schema validation, and input validation for EnergyHub (overview, trends, forecast with consumption metric and invalid-metric error handling, map-data, source/grid breakdown), EcoSim (GET with parameters, POST with JSON body for valid and invalid municipalities, missing-param handling), and authentication (protected endpoint 401 behavior, OAuth callback existence, valid JWT access, expired/malformed JWT rejection).

**Database Integration Tests** (`test_database.py`) execute SQL assertions against PostgreSQL (Supabase) to verify table existence, CRUD operations, foreign key integrity (barangays-municipalities-provinces-regions, hydropower suitability), CHECK constraints (month 1-12, year >= 2018), index presence, and correctness of the `regional_lookup` four-table join view.

**Performance Tests** (`performance_test.py`) measure dataset loading (< 3s), linear regression inference (< 5s), API response times (< 2s for EnergyHub overview, < 3s for EcoSim), map aggregation over 1,600 municipalities (< 2s), FAISS RAG retrieval (< 1s), and memory footprint (< 5MB for FAISS index, < 10MB for municipality DataFrame).

**End-to-End Pipeline Tests** (`test_pipeline.py`) simulate the complete DOE dataset -> preprocessing -> ML model -> prediction -> FastAPI -> frontend data chain using fixture data. The system is considered ready for pilot deployment when all critical-path scenarios pass, no high-severity defects remain, API response times meet thresholds, and stability is maintained during continuous usage.

## 9.8.4. Pilot Run

The pilot run evaluates multiple forecasting models on a held-out test set using standard regression metrics. The script `lumi_tests/pilot_run/evaluate_models.py` trains models on DOE 2003-2023 data and evaluates on the 2024 holdout.

Models compared include Linear Trend Regression, ARIMA(1,1,1), Holt Linear Smoothing, SARIMAX with exogenous variables, and Random Forest (as a controlled experiment to demonstrate overfitting on limited data). Evaluation metrics are MAE, RMSE, MAPE, MPE, R2, AIC, BIC, directional accuracy, and prediction interval coverage probability (PICP). Statistical comparison uses the Diebold-Mariano test and Wilcoxon signed-rank test.

The Random Forest controlled experiment demonstrated severe overfitting (training MAPE 1.45% vs. test MAPE 13.41%), confirming the thesis decision to use parsimonious statistical models. The best-performing model, Linear Trend Regression, achieved MAPE = 4.97% on the test set.

Pilot success criteria: at least one model achieves MAPE < 20% on the 2024 test set, all critical-path integration scenarios pass, and API performance thresholds are met.

## 9.8.5. Evaluation Rubrics (ISO/IEC 25010)

LUMI was evaluated against the **ISO/IEC 25010:2011** software quality model using a 1-5 Likert scale with weighted importance. The evaluation is documented in `lumi_tests/docs/iso25010_evaluation.md`.

**Table 19. ISO/IEC 25010 Evaluation Results**

| Quality Characteristic | Score | Weight | Weighted Score |
| --- | --- | --- | --- |
| Functional Suitability | 4 | 0.20 | 0.80 |
| Performance Efficiency | 4 | 0.15 | 0.60 |
| Compatibility | 3 | 0.10 | 0.30 |
| Usability | 3 | 0.15 | 0.45 |
| Reliability | 4 | 0.15 | 0.60 |
| Security | 4 | 0.10 | 0.40 |
| Maintainability | 3 | 0.10 | 0.30 |
| Portability | 3 | 0.05 | 0.15 |
| **Total** | | **1.00** | **3.60** |

**Final Score: 3.60 / 5.0 (Good)**

The strongest areas are **Functional Suitability**, **Performance Efficiency**, **Reliability**, and **Security**, supported by evidence from the codebase and architecture documentation. Primary areas for improvement are **Compatibility** (data export features), **Usability** (accessibility audit, onboarding), **Maintainability** (test coverage >70%, linting enforcement), and **Portability** (Docker containerization).

Two parallel evaluation instruments were prepared: one for end users (focusing on functional suitability, usability, and satisfaction) and one for expert evaluators (focusing on performance efficiency, reliability, security, and maintainability). Results are aggregated by category, and mean scores are computed for each indicator and overall quality characteristic.
