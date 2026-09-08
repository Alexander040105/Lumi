# LUMI Testing Strategy

**Document Type:** Software Testing Strategy & Evaluation Plan  
**Project:** LUMI — Data-Driven Environmental Intelligence System for Renewable Energy Decision Support  
**Version:** 1.0  
**Date:** June 2026  

---

## 1. Testing Objectives

The primary objectives of the LUMI testing framework are to:

1. **Validate Functional Correctness:** Ensure that all system modules (EnergyHub, EcoSim, AI Layer, Database, Authentication) produce accurate and expected outputs for valid inputs.
2. **Ensure Data Integrity:** Verify that the Supabase PostgreSQL database maintains referential integrity, constraint compliance, and data consistency across all tables.
3. **Verify Algorithm Accuracy:** Confirm that renewable energy calculations (solar, wind, hydro) and machine learning forecasts adhere to established physics-based formulas and statistical principles.
4. **Assess AI Service Reliability:** Validate that the Gemini/Groq AI integration returns structured, grounded, and non-hallucinated responses under normal and edge-case conditions.
5. **Measure System Performance:** Establish acceptable response-time thresholds for API endpoints, dataset loading, and prediction inference.
6. **Evaluate Usability:** Determine whether target users (students, researchers, community planners) can effectively navigate the interface and interpret results.
7. **Pilot Model Validation:** Compare multiple forecasting models on a held-out test set using standard regression metrics (MAE, RMSE, MAPE, R²).
8. **ISO/IEC 25010 Compliance:** Evaluate LUMI against international software quality standards to produce a defendable quality assessment.

---

## 2. Testing Scope

### In Scope

| Module | Features Under Test |
|---|---|
| **Authentication / User Management** | OAuth (Google, GitHub) registration, JWT token generation, protected endpoint access, token expiry |
| **EnergyHub** | Overview stats, historical trends, ARIMA forecast (2025–2030), choropleth map data, source/grid breakdown, AI insights |
| **EcoSim** | Municipality selection, solar output calculation, wind output calculation (Betz-limit), hydro output calculation, economic scoring, payback period, carbon reduction |
| **AI Intelligence Layer** | Gemini prompt construction, JSON output normalization, RAG context retrieval (FAISS + sentence-transformers), fallback to Groq, error handling |
| **Database Layer** | CRUD operations, foreign key integrity, null constraints, index performance, view correctness (`regional_lookup`) |
| **Machine Learning Module** | Data preprocessing (missing values, differencing), ARIMA training, Linear Trend, Holt Smoothing, SARIMAX, Random Forest, model comparison |
| **End-to-End Pipeline** | DOE dataset → preprocessing → ML model → prediction → FastAPI → React visualization data |

### Out of Scope

- Third-party API uptime (NASA POWER, Google Gemini, Groq) — monitored but not controlled.
- Browser compatibility testing beyond Chrome/Firefox/Edge latest stable.
- Load testing beyond 50 concurrent users (thesis-scale application).
- Security penetration testing (OWASP-level) — limited to input validation and JWT checks.

---

## 3. Testing Methodology

### 3.1 Unit Testing

**Approach:** Test individual functions and classes in isolation using `pytest` with `unittest.mock` for external dependencies.

**Why appropriate for LUMI:**
- Renewable energy calculations (solar, wind, hydro) contain deterministic physics formulas that can be verified with known inputs and expected outputs.
- ML preprocessing functions (scaling, missing-value imputation) must behave consistently regardless of the larger pipeline state.
- AI service functions (prompt builders, JSON parsers) should be testable without making live API calls.

**Tools:** `pytest`, `pytest-mock`, `unittest.mock`

### 3.2 Integration / API Testing

**Approach:** Test FastAPI endpoints using `httpx` and FastAPI's `TestClient`.

**Why appropriate for LUMI:**
- FastAPI's dependency injection system allows overriding database and service dependencies in tests.
- Endpoints accept structured Pydantic schemas; integration tests verify schema validation, HTTP status codes, and response shapes.
- The EnergyHub and EcoSim modules expose public REST contracts that must remain stable for the React frontend.

**Tools:** `pytest`, `httpx`, `fastapi.testclient.TestClient`

### 3.3 Database Testing

**Approach:** Execute SQL assertions against a test PostgreSQL instance or an in-memory SQLite mirror of `lumischema.sql`.

**Why appropriate for LUMI:**
- The schema contains composite keys, foreign key cascades, and CHECK constraints (e.g., month 1–12, year >= 2018).
- The `regional_lookup` view performs a 4-table join; its correctness is critical for frontend dropdowns.
- Hydropower suitability data is pre-computed and must not violate mathematical bounds (e.g., slope >= 0, score 0–1).

**Tools:** `pytest`, `psycopg2-binary`, `sqlalchemy` (optional)

### 3.4 End-to-End Pipeline Testing

**Approach:** Simulate the complete DOE dataset → preprocessing → ML → API → frontend data chain using fixture data.

**Why appropriate for LUMI:**
- The EnergyHub forecast is the culmination of data extraction, cleaning, model training, artifact storage, and API serving.
- A break in any link (e.g., CSV column renamed, predictor loading error) is only detectable at the pipeline level.

**Tools:** `pytest`, `pandas`, `pathlib`

### 3.5 Performance Testing

**Approach:** Measure execution times for dataset loading, API responses, and prediction inference using `time` and `pytest-benchmark`.

**Why appropriate for LUMI:**
- The FAISS index and RAG retrieval must respond quickly enough to not degrade user experience.
- The choropleth map endpoint aggregates 1,600+ municipalities; response time impacts perceived system quality.
- ML forecasts are pre-computed, but the predictor loader must initialize within an acceptable window.

**Tools:** `pytest-benchmark`, Python `time` module

### 3.6 Usability Testing

**Approach:** Task-based evaluation with target users, measuring success rate, completion time, errors, and subjective satisfaction via the System Usability Scale (SUS).

**Why appropriate for LUMI:**
- The thesis objective explicitly includes evaluating "usability, usefulness, and acceptability" among potential users.
- The system targets non-technical audiences (communities, students); intuitive navigation is a core requirement.

**Tools:** Observation protocol, SUS questionnaire, Likert-scale forms

### 3.7 Pilot Run / Model Validation

**Approach:** Train multiple forecasting models on DOE 2003–2023 data, hold out 2024 for testing, and compute MAE, RMSE, MAPE, and R².

**Why appropriate for LUMI:**
- The thesis scope states the predictive analytics module uses "basic statistical methods" but does not evaluate them against a held-out test set in production.
- A controlled pilot provides quantitative evidence for model selection (ARIMA vs. Linear Trend vs. Holt vs. SARIMAX vs. Random Forest).

**Tools:** `pandas`, `statsmodels`, `scikit-learn`, `matplotlib`

### 3.8 ISO/IEC 25010 System Quality Evaluation

**Approach:** Rate LUMI on the eight primary quality characteristics of ISO/IEC 25010 using a 1–5 Likert scale with weighted importance.

**Why appropriate for LUMI:**
- Academic thesis evaluation often requires alignment with international standards.
- Provides a structured, defensible argument for system quality during defense.

**Tools:** Rubric-based scoring, weighted formula

---

## 4. Testing Environment

| Component | Specification |
|---|---|
| **OS** | Windows 11 / Ubuntu 22.04 |
| **Python** | 3.13.2 |
| **Node.js** | 18+ |
| **Backend** | FastAPI (Uvicorn, port 8000) |
| **Frontend** | React + Vite (port 5173) |
| **Database** | Supabase PostgreSQL (free tier) / Local test instance |
| **Test Runner** | pytest 8.x |
| **HTTP Client** | httpx 0.27+ |
| **Browser** | Chrome 120+ / Firefox 121+ |

### Environment Variables (Test)

```bash
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_ANON_KEY=<anon_key>
SUPABASE_JWT_SECRET=<jwt_secret>
GEMINI_API_KEY=<gemini_key>
GROQ_API_KEY=<groq_key>
UPSTASH_REDIS_URL=<redis_url>
```

---

## 5. Testing Tools

| Tool | Version | Purpose |
|---|---|---|
| `pytest` | >=8.0 | Core test runner |
| `pytest-mock` | >=3.14 | Mocking external APIs |
| `pytest-benchmark` | >=4.0 | Performance benchmarking |
| `httpx` | >=0.27 | Async HTTP client for API tests |
| `pandas` | >=2.0 | Data fixtures and assertions |
| `numpy` | >=1.24 | Numerical validation |
| `statsmodels` | >=0.14 | ML model verification |
| `scikit-learn` | >=1.5 | Model metrics (MAE, RMSE, MAPE, R²) |
| `matplotlib` | >=3.8 | Plotting forecast comparisons |

---

## 6. Testing Criteria

### 6.1 Pass / Fail Criteria

| Test Type | Pass Criteria |
|---|---|
| **Unit Test** | All assertions pass; code coverage >= 70% for core services. |
| **API Test** | All endpoints return expected status codes and response schemas. |
| **Database Test** | All CRUD operations succeed; foreign keys enforce referential integrity. |
| **Pipeline Test** | Complete execution chain produces expected output without exceptions. |
| **Performance Test** | API response < 2 s; prediction inference < 5 s; dataset load < 3 s. |
| **Usability Test** | Task success rate >= 80%; average SUS score >= 68 (above-average usability). |
| **Pilot Run** | At least one model achieves MAPE < 20% on the 2024 test set. |
| **ISO 25010** | Overall weighted score >= 3.5 / 5.0 ("Acceptable" or better). |

### 6.2 Exit Criteria

Testing is considered complete when:
1. All high-priority test cases (P1) pass.
2. No critical bugs (severity 1) remain open.
3. Performance benchmarks meet the thresholds defined above.
4. The System Test Plan (Phase 10) is fully executed and documented.
5. ISO 25010 evaluation is completed with evidence for each characteristic.

---

## 7. Roles & Responsibilities

| Role | Responsibility |
|---|---|
| **Test Engineer** | Write and maintain unit, integration, and API tests. |
| **QA Engineer** | Execute system test plan, document defects, verify fixes. |
| **Research Evaluator** | Conduct pilot run, usability testing, and ISO 25010 evaluation. |
| **AI Validation Specialist** | Validate Gemini/Groq output quality, RAG retrieval accuracy. |

---

## 8. Risk & Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| Gemini API rate limits during testing | High | Use mock responses for unit tests; limit live calls to integration tests only. |
| Supabase connection failures in CI | Medium | Provide local SQLite fallback for schema tests. |
| FAISS index file missing in test env | High | Create a minimal fixture index in `conftest.py`. |
| Test data drift from production | Medium | Pin fixture CSVs and freeze expected outputs. |

---

*End of Testing Strategy Document*
