# LUMI ISO/IEC 25010 System Quality Evaluation

**Document Type:** Software Quality Evaluation Report  
**Standard:** ISO/IEC 25010:2011 — Systems and Software Quality Requirements and Evaluation (SQuaRE)  
**Project:** LUMI — Data-Driven Environmental Intelligence System for Renewable Energy Decision Support  
**Version:** 1.0  
**Date:** June 2026  

---

## 1. Introduction

This document evaluates the LUMI system against the eight primary quality characteristics defined in **ISO/IEC 25010**. Each characteristic is assessed using a 1–5 Likert scale based on evidence from the project codebase, architecture documentation, and functional testing.

### Scoring Scale

| Score | Description |
|---|---|
| **5** | Excellent — exceeds typical undergraduate project standards |
| **4** | Good — meets expectations with minor areas for improvement |
| **3** | Acceptable — functional but has notable limitations |
| **2** | Needs Improvement — significant gaps exist |
| **1** | Poor — does not meet basic requirements |

### Weighting

| Characteristic | Weight | Rationale |
|---|---|---|
| Functional Suitability | 0.20 | Core requirement for thesis defense |
| Performance Efficiency | 0.15 | User experience depends on responsive UI |
| Usability | 0.15 | Thesis explicitly evaluates usability |
| Reliability | 0.15 | Decision-support systems must be trustworthy |
| Security | 0.10 | User data protection essential |
| Maintainability | 0.10 | Code longevity and team collaboration |
| Compatibility | 0.10 | Cross-platform deployment |
| Portability | 0.05 | Deployment flexibility |

**Total Weighted Score Formula:**

```
Final Score = Σ(Score_i × Weight_i)
```

**Grade Interpretation:**

| Final Score | Grade | Description |
|---|---|---|
| 4.5 – 5.0 | Excellent | World-class quality for an academic project |
| 3.5 – 4.4 | Good | Strong quality, minor improvements needed |
| 2.5 – 3.4 | Acceptable | Meets minimum standards, gaps exist |
| 1.5 – 2.4 | Needs Improvement | Significant rework required |
| 1.0 – 1.4 | Poor | Does not meet basic quality expectations |

---

## 2. Quality Characteristic Evaluations

---

### 2.1 Functional Suitability (Weight: 0.20)

**Definition:** The degree to which the system provides functions that meet stated and implied user needs.

**Evaluation Criteria:**
- Completeness of functional requirements
- Correctness of calculations and forecasts
- Appropriateness of features for target users

**Evidence:**
- EnergyHub provides historical data, forecasts, choropleth maps, source breakdowns, and AI insights (`ENERGYHUB_ARCHITECTURE.md`).
- EcoSim provides solar, wind, and hydro output calculations with physics-based formulas (`ECOSIM_ARCHITECTURE.md`).
- RAG-enhanced AI analysis returns structured JSON with recommendations (`rag_gemini_funcs.py`).
- Forecasting uses ARIMA(1,1,1) evaluated on a held-out test set (`DOE_arima_forecasting.ipynb`).

**Limitations:**
- No real-time data feeds (relies on pre-computed CSVs).
- The DOE dataset lacks sub-national consumption data; the map aggregates only at the province level for some metrics.
- No geothermal energy simulation (scope limited to solar, wind, hydro).

**Score:** **4** — Good. All core features are implemented and verified. Minor gaps in real-time data and scope exclusions.

---

### 2.2 Performance Efficiency (Weight: 0.15)

**Definition:** The performance relative to the amount of resources used under stated conditions.

**Evaluation Criteria:**
- API response time
- Dataset loading time
- Prediction inference time
- Resource utilization

**Evidence:**
- Health endpoint responds in < 100ms (tested locally).
- EnergyHub overview endpoint loads pre-computed CSVs in < 1s.
- EcoSim calculation is deterministic (no ML inference at request time).
- FAISS retrieval operates on a small local index (< 1,000 chunks) with sub-second response.
- ML forecasts are pre-computed; no runtime training occurs.

**Measurement Method:**
- `performance_test.py` benchmarks API response times.
- Memory footprint of the FAISS index is < 5MB.

**Limitations:**
- Choropleth map aggregation over 1,600+ municipalities may exceed 2s on slower connections.
- No formal load testing has been conducted.

**Score:** **4** — Good. Performance is adequate for a thesis-scale application with a small user base.

---

### 2.3 Compatibility (Weight: 0.10)

**Definition:** The degree to which the system can exchange information with other systems and coexist in the same environment.

**Evaluation Criteria:**
- API standard compliance (REST/JSON)
- Database compatibility (PostgreSQL via Supabase)
- Frontend browser compatibility

**Evidence:**
- FastAPI exposes standard REST endpoints with JSON responses and OpenAPI auto-docs (`/docs`).
- Supabase PostgreSQL is a widely supported managed database with REST and GraphQL clients.
- Frontend uses standard React + Vite; builds to static files compatible with any static host.
- CORS configured for `localhost:5173` and production domain.

**Limitations:**
- No formal SOAP or GraphQL API.
- No data export feature (e.g., CSV download from frontend).

**Score:** **3** — Acceptable. Standard REST compatibility is present; export features would improve this score.

---

### 2.4 Usability (Weight: 0.15)

**Definition:** The degree to which the system can be used by specified users to achieve specified goals with effectiveness, efficiency, and satisfaction.

**Evaluation Criteria:**
- Interface clarity and consistency
- Task completion ease
- Helpfulness of visualizations
- Accessibility

**Evidence:**
- React frontend uses shadcn/ui primitives with consistent styling (`SHADCN_SETUP_GUIDE.md`).
- TailwindCSS provides responsive layouts for different screen sizes.
- Charts use inline SVG with tooltips and legends.
- AI explanations are displayed in plain language with structured formatting.

**Measurement Method:**
- System Usability Scale (SUS) questionnaire (see `usability_testing.md`).
- Task-based evaluation with target users.

**Limitations:**
- No formal accessibility audit (WCAG compliance untested).
- No dark mode or theme customization.
- No in-app tutorial or onboarding flow.

**Score:** **3** — Acceptable. The interface is clean and functional but lacks advanced usability features.

---

### 2.5 Reliability (Weight: 0.15)

**Definition:** The degree to which the system performs specified functions under specified conditions for a specified period of time.

**Evaluation Criteria:**
- Availability of the system
- Fault tolerance (fallback mechanisms)
- Data consistency
- Recoverability

**Evidence:**
- AI layer implements a fallback chain: Gemini → Groq → structured error response (`llm_client.py`).
- FAISS index and CSV assets are loaded at startup; missing files raise descriptive errors.
- Supabase Row Level Security (RLS) ensures data consistency.
- The system does not perform destructive operations on user data.

**Limitations:**
- No formal uptime monitoring or health checks in production.
- No automated backup strategy beyond Supabase's managed backups.
- Redis caching is used but not critically required for core functionality.

**Score:** **4** — Good. Fallback mechanisms and data integrity measures are in place.

---

### 2.6 Security (Weight: 0.10)

**Definition:** The degree to which the system protects information and data so that unauthorized persons or systems cannot read or modify them.

**Evaluation Criteria:**
- Authentication strength
- Authorization controls
- Data protection
- Input validation

**Evidence:**
- OAuth 2.0 via Supabase (Google, GitHub) with JWT tokens (`SUPABASE_GUIDE.md`).
- JWT validation using `python-jose` with HMAC-SHA256 (`app/auth/`).
- Protected endpoints use `Depends(get_current_user)`.
- Row Level Security (RLS) policies restrict data access per user.
- Pydantic schemas enforce type-safe API contracts.
- Secrets stored in `.env`; excluded from version control via `.gitignore`.

**Limitations:**
- No rate limiting on API endpoints.
- No formal penetration testing.
- API keys (Gemini, Groq) are environment-dependent; no key rotation mechanism.

**Score:** **4** — Good. Standard security practices are followed; advanced hardening is out of scope.

---

### 2.7 Maintainability (Weight: 0.10)

**Definition:** The degree to which the system can be effectively and efficiently modified without introducing defects or degrading existing quality.

**Evaluation Criteria:**
- Code modularity
- Documentation completeness
- Test coverage
- Naming conventions

**Evidence:**
- FastAPI backend uses domain-based routers and a service layer (`FASTAPI_ARCHITECTURE_GUIDE.md`).
- Frontend follows component-first organization (`FRONTEND_STRUCTURE_GUIDE.md`).
- Multiple architecture guides document design decisions.
- Type hints used throughout Python codebase.
- Test scripts exist for RAG, LLM, and pipeline (`test_rag_pipeline.py`, `test_full_pipeline.py`).

**Limitations:**
- No formal code linting (flake8, black) enforced.
- Test coverage is partial; no comprehensive pytest suite exists.
- Some frontend components are tightly coupled to specific page layouts.

**Score:** **3** — Acceptable. Modular design is present but test coverage and tooling could be improved.

---

### 2.8 Portability (Weight: 0.05)

**Definition:** The degree to which the system can be transferred from one environment to another.

**Evaluation Criteria:**
- Deployment flexibility
- Environment configuration ease
- Dependency management

**Evidence:**
- Frontend deploys as static files (Vite `dist/` → Vercel).
- Backend runs on any ASGI server (Uvicorn) with standard Python requirements.
- Database is cloud-managed (Supabase) but PostgreSQL-compatible; migration possible.
- Dependencies listed in `requirements.txt`, `fastapi-backend/requirements.txt`, and `package.json`.
- Virtual environment located at project root (`.venv`).

**Limitations:**
- FAISS index file (~MB) and local CSVs must be copied to deployment target.
- No Docker containerization.
- Windows-centric development (path separators, `concurrently` scripts).

**Score:** **3** — Acceptable. Standard deployment practices are documented but containerization is absent.

---

## 3. Weighted Score Calculation

| Characteristic | Score | Weight | Weighted Score |
|---|---|---|---|
| Functional Suitability | 4 | 0.20 | 0.80 |
| Performance Efficiency | 4 | 0.15 | 0.60 |
| Compatibility | 3 | 0.10 | 0.30 |
| Usability | 3 | 0.15 | 0.45 |
| Reliability | 4 | 0.15 | 0.60 |
| Security | 4 | 0.10 | 0.40 |
| Maintainability | 3 | 0.10 | 0.30 |
| Portability | 3 | 0.05 | 0.15 |
| **Total** | | **1.00** | **3.60** |

### Final Grade

**Final Score: 3.60 / 5.0**

**Grade: Good**

LUMI demonstrates **Good** overall system quality. The strongest areas are **Functional Suitability**, **Performance Efficiency**, **Reliability**, and **Security** — all critical for a decision-support system. The primary areas for improvement are **Compatibility** (data export), **Usability** (accessibility, onboarding), **Maintainability** (test coverage, linting), and **Portability** (Docker, cross-platform scripts).

---

## 4. Recommendations

| Priority | Recommendation | Target Characteristic |
|---|---|---|
| High | Implement comprehensive pytest suite with >70% coverage | Maintainability |
| High | Add data export (CSV, PDF) from frontend | Compatibility |
| Medium | Conduct formal accessibility audit (WCAG 2.1) | Usability |
| Medium | Add in-app onboarding / tooltips for first-time users | Usability |
| Medium | Add API rate limiting and request logging | Security |
| Low | Dockerize the application for cross-platform deployment | Portability |
| Low | Add dark mode and theme customization | Usability |

---

*End of ISO/IEC 25010 Evaluation*
