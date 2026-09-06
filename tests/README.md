# LUMI Testing & Evaluation Suite

**Project:** LUMI — Data-Driven Environmental Intelligence System for Renewable Energy Decision Support  
**Purpose:** Complete testing and evaluation framework for thesis Chapter 4 (Results & Discussion) and Chapter 5 (System Evaluation / Testing)

---

## Folder Structure

```
tests/
├── README.md                          # This file
├── tests/
│   ├── unit/
│   │   ├── conftest.py               # Shared pytest fixtures
│   │   ├── test_renewable_calculations.py   # Solar, Wind, Hydro unit tests
│   │   ├── test_ml_preprocessing.py         # ML preprocessing & metric tests
│   │   └── test_ai_service.py               # AI prompt, JSON, RAG mock tests
│   └── integration/
│       ├── test_api.py               # FastAPI endpoint integration tests
│       ├── test_database.py          # PostgreSQL schema & CRUD tests
│       ├── test_pipeline.py          # End-to-end DOE → ML → API pipeline tests
│       └── performance_test.py       # Response time & memory benchmarks
├── pilot_run/
│   ├── evaluate_models.py            # Model validation script (ARIMA, Linear, Holt, RF)
│   └── pilot_results/                # Output directory for CSVs and plots
├── docs/
│   ├── testing_strategy.md           # Phase 1: Strategy, scope, methodology
│   ├── usability_testing.md        # Phase 7: SUS questionnaire & task scenarios
│   ├── iso25010_evaluation.md      # Phase 9: ISO/IEC 25010 quality rubric
│   └── test_results_template.md    # Phase 10: 75 test cases with status tracking
└── reports/                          # Generated test reports (populate after runs)
```

---

## Quick Start

### Prerequisites

```bash
# From the LUMI project root
pip install pytest pytest-mock httpx pandas numpy scikit-learn statsmodels matplotlib psycopg2-binary
```

### Run Unit Tests

```bash
cd tests
pytest tests/unit/ -v
```

### Run Integration Tests (mock mode)

```bash
pytest tests/integration/test_api.py -v -m mock
pytest tests/integration/test_database.py -v
pytest tests/integration/test_pipeline.py -v
```

### Run Performance Tests

```bash
pytest tests/integration/performance_test.py -v -m local
```

### Run Pilot Model Validation

```bash
cd pilot_run
python evaluate_models.py
```

Outputs:
- `pilot_results/forecast_comparison.csv`
- `pilot_results/model_metrics.csv`
- `pilot_results/forecast_plot.png`

---

## Test Coverage by Module

| Module | Unit Tests | Integration Tests | Performance Tests | Usability | ISO 25010 |
|---|---|---|---|---|---|
| Authentication | — | ✅ | — | — | — |
| EnergyHub | — | ✅ | ✅ | — | — |
| EcoSim | ✅ (calculations) | ✅ | ✅ | — | — |
| AI / RAG | ✅ (prompts, JSON) | ✅ | ✅ | — | — |
| Database | — | ✅ | — | — | — |
| ML / Forecasting | ✅ (preprocessing) | ✅ (pipeline) | — | — | — |
| Visualization | — | — | — | ✅ | — |
| System Quality | — | — | — | — | ✅ |

---

## Phase Mapping

| Phase | Deliverable | File |
|---|---|---|
| Phase 1 | Testing Strategy | `docs/testing_strategy.md` |
| Phase 2 | Unit Tests | `tests/unit/test_*.py` |
| Phase 3 | API Tests | `tests/integration/test_api.py` |
| Phase 4 | Database Tests | `tests/integration/test_database.py` |
| Phase 5 | Pipeline Tests | `tests/integration/test_pipeline.py` |
| Phase 6 | Performance Tests | `tests/integration/performance_test.py` |
| Phase 7 | Usability Testing | `docs/usability_testing.md` |
| Phase 8 | Pilot Run | `pilot_run/evaluate_models.py` |
| Phase 9 | ISO 25010 Evaluation | `docs/iso25010_evaluation.md` |
| Phase 10 | Test Results Template | `docs/test_results_template.md` |

---

## Notes for Thesis Defense

- All test cases trace to actual LUMI modules (no generic tests).
- Features not implemented are marked "Not applicable / Not implemented" in the strategy document.
- The ISO 25010 evaluation produced a **weighted score of 3.60 / 5.0 (Good)**.
- Usability testing includes the **System Usability Scale (SUS)** with a target score ≥ 68.
- The pilot run evaluates **ARIMA, Linear Trend, Holt Smoothing, and Random Forest** on a held-out 2024 test set.

---

*Generated for LUMI Thesis Documentation*
