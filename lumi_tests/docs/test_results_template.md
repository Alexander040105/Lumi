# LUMI System Test Results

**Document Type:** Software Test Result Report  
**Project:** LUMI — Data-Driven Environmental Intelligence System for Renewable Energy Decision Support  
**Version:** 1.0  
**Date:** June 2026  

---

## 1. Introduction

This document records the results of all system tests conducted on the LUMI platform. Each test case is uniquely identified, mapped to a system module, and evaluated against an expected result. The status of each test is recorded as **Passed**, **Failed**, or **Pending**.

Tests are organized by module: Authentication, EnergyHub, EcoSim, AI Features, Database, API Endpoints, and Visualization.

---

## 2. Test Result Legend

| Status | Symbol | Description |
|---|---|---|
| **Passed** | ✅ | Test executed successfully; actual result matched expected result. |
| **Failed** | ❌ | Test did not produce the expected result; defect logged. |
| **Pending** | ⏳ | Test not yet executed or awaiting environment setup. |
| **N/A** | — | Not applicable for current configuration. |

---

## 3. Authentication Module

| Test Case ID | Description | Expected Result | Actual Result | Status | Remarks |
|---|---|---|---|---|---|
| TC-AUTH-001 | Register via Google OAuth | JWT token returned; user record created in Supabase | | ⏳ | Requires live Supabase project |
| TC-AUTH-002 | Register via GitHub OAuth | JWT token returned; user record created in Supabase | | ⏳ | Requires live Supabase project |
| TC-AUTH-003 | Access protected endpoint without token | HTTP 401 Unauthorized | | ⏳ | Test with `test_api.py` |
| TC-AUTH-004 | Access protected endpoint with valid token | HTTP 200 OK; user data returned | | ⏳ | Test with `test_api.py` |
| TC-AUTH-005 | Access protected endpoint with expired token | HTTP 401 Unauthorized with "token expired" message | | ⏳ | Requires token expiry simulation |
| TC-AUTH-006 | Logout / token revocation | Session invalidated; subsequent requests return 401 | | ⏳ | Supabase handles token expiry |

---

## 4. EnergyHub Module

| Test Case ID | Description | Expected Result | Actual Result | Status | Remarks |
|---|---|---|---|---|---|
| TC-EH-001 | Load EnergyHub overview | Latest consumption, peak demand, and generation stats displayed | | ⏳ | Pre-computed CSVs |
| TC-EH-002 | View historical trends | Line chart renders with years 2003–2024 | | ⏳ | SVG inline chart |
| TC-EH-003 | View forecast (2025–2030) | Forecast line overlays historical data; CI bands visible | | ⏳ | ARIMA pre-computed forecasts |
| TC-EH-004 | Forecast metric = consumption | Returns consumption forecast values | | ⏳ | `GET /api/v1/energyhub/forecast?metric=consumption` |
| TC-EH-005 | Forecast metric = peak_demand | Returns peak demand forecast values | | ⏳ | `GET /api/v1/energyhub/forecast?metric=peak_demand` |
| TC-EH-006 | View choropleth map (renewable potential) | Map renders with province-level color gradients | | ⏳ | `GET /api/v1/energyhub/map-data` |
| TC-EH-007 | View source breakdown | Pie/bar chart shows coal, natural gas, renewable, oil percentages | | ⏳ | `GET /api/v1/energyhub/source-breakdown` |
| TC-EH-008 | View grid breakdown | Chart shows Luzon, Visayas, Mindanao generation split | | ⏳ | `GET /api/v1/energyhub/grid-breakdown` |
| TC-EH-009 | View AI-generated insight | Narrative text explains latest trends | | ⏳ | `GET /api/v1/energyhub/ai-insight` |
| TC-EH-010 | Invalid forecast metric | HTTP 422 validation error | | ⏳ | e.g., `metric=invalid` |

---

## 5. EcoSim Module

| Test Case ID | Description | Expected Result | Actual Result | Status | Remarks |
|---|---|---|---|---|---|
| TC-ES-001 | Load municipality list | Dropdown populated with 1,600+ municipalities | | ⏳ | `GET /api/v1/ecosim/municipalities` |
| TC-ES-002 | Select municipality and run simulation | Dashboard response with solar, wind, hydro scores | | ⏳ | `GET /api/v1/ecosim/?municipality_id=123` |
| TC-ES-003 | Missing municipality_id parameter | HTTP 422 validation error | | ⏳ | Required parameter |
| TC-ES-004 | Invalid municipality_id | HTTP 404 or empty results | | ⏳ | e.g., `municipality_id=999999` |
| TC-ES-005 | Solar output calculation | Positive daily and monthly kWh values; score 0–100 | | ⏳ | `solar_output_calc.py` |
| TC-ES-006 | Wind output calculation | Positive energy values; Betz limit not exceeded | | ⏳ | `wind_output_calc.py` |
| TC-ES-007 | Hydro output calculation | Positive energy values; flow rate within bounds | | ⏳ | `hydro_output_calc.py` |
| TC-ES-008 | Economic scoring (payback period) | Positive payback years; estimated cost in PHP | | ⏳ | Derived from output calc |
| TC-ES-009 | Carbon reduction estimate | Positive CO₂ reduction in tonnes/year | | ⏳ | Derived from output calc |
| TC-ES-010 | Include AI analysis = true | Response includes AI analysis panel | | ⏳ | `include_ai=true` |
| TC-ES-011 | Include RAG = true | AI response incorporates retrieved knowledge chunks | | ⏳ | `use_rag=true` |
| TC-ES-012 | POST simulation with full body | HTTP 201 Created with complete response | | ⏳ | `POST /api/v1/ecosim/` |
| TC-ES-013 | POST with invalid body | HTTP 422 validation error | | ⏳ | Missing required fields |

---

## 6. AI Intelligence Layer

| Test Case ID | Description | Expected Result | Actual Result | Status | Remarks |
|---|---|---|---|---|---|
| TC-AI-001 | Gemini prompt construction | Prompt contains simulation data and grounding rules | | ⏳ | `rag_gemini_funcs.py` |
| TC-AI-002 | Gemini JSON output parsing | Valid JSON with all required fields | | ⏳ | `gemini_funcs.py` |
| TC-AI-003 | Gemini fallback to Groq | When Gemini 503s, Groq responds successfully | | ⏳ | `llm_client.py` |
| TC-AI-004 | RAG retrieval (valid query) | Returns chunks with score >= 0.25 | | ⏳ | `rag_pipeline.py` |
| TC-AI-005 | RAG retrieval (no relevant chunks) | Returns empty list or low-score warning | | ⏳ | Edge case |
| TC-AI-006 | Invalid JSON from LLM | System returns fallback message or error gracefully | | ⏳ | Error handling |
| TC-AI-007 | Empty API response | System detects empty response and retries or falls back | | ⏳ | Resilience test |

---

## 7. Database Layer

| Test Case ID | Description | Expected Result | Actual Result | Status | Remarks |
|---|---|---|---|---|---|
| TC-DB-001 | Insert valid climate record | Record persisted in `municipality_climate_monthly` | | ⏳ | CRUD test |
| TC-DB-002 | Insert climate record with month=13 | Violates CHECK constraint; insert rejected | | ⏳ | Constraint test |
| TC-DB-003 | Insert climate record with year=1999 | Violates CHECK constraint (year >= 2018); insert rejected | | ⏳ | Constraint test |
| TC-DB-004 | Foreign key integrity (barangays → municipalities) | All barangays reference existing municipalities | | ⏳ | `test_database.py` |
| TC-DB-005 | Foreign key integrity (municipalities → provinces) | All municipalities reference existing provinces | | ⏳ | `test_database.py` |
| TC-DB-006 | Foreign key integrity (provinces → regions) | All provinces reference existing regions | | ⏳ | `test_database.py` |
| TC-DB-007 | Regional lookup view correctness | View returns consistent municipality count | | ⏳ | `test_database.py` |
| TC-DB-008 | Hydropower suitability bounds | `hydro_suitability_score` between 0 and 1 | | ⏳ | Data validation |
| TC-DB-009 | Delete municipality with child climate data | Rejected due to ON DELETE RESTRICT | | ⏳ | FK behavior |
| TC-DB-010 | Index performance on climate query | Query by municipality_id uses btree index | | ⏳ | EXPLAIN ANALYZE |

---

## 8. API Endpoints

| Test Case ID | Description | Expected Result | Actual Result | Status | Remarks |
|---|---|---|---|---|---|
| TC-API-001 | Health check | HTTP 200, body: `{"status": "ok"}` | | ⏳ | `GET /api/v1/health` |
| TC-API-002 | EnergyHub overview | HTTP 200, valid JSON schema | | ⏳ | `GET /api/v1/energyhub/overview` |
| TC-API-003 | EnergyHub forecast | HTTP 200, forecast array present | | ⏳ | `GET /api/v1/energyhub/forecast` |
| TC-API-004 | EnergyHub trends | HTTP 200, trend data array present | | ⏳ | `GET /api/v1/energyhub/trends` |
| TC-API-005 | EnergyHub map data | HTTP 200, geographic data points present | | ⏳ | `GET /api/v1/energyhub/map-data` |
| TC-API-006 | EcoSim GET with valid params | HTTP 200, dashboard response | | ⏳ | `GET /api/v1/ecosim/` |
| TC-API-007 | EcoSim GET missing params | HTTP 422 validation error | | ⏳ | Missing required query params |
| TC-API-008 | EcoSim municipalities | HTTP 200, items array > 0 | | ⏳ | `GET /api/v1/ecosim/municipalities` |
| TC-API-009 | EcoSim POST valid body | HTTP 201, complete response | | ⏳ | `POST /api/v1/ecosim/` |
| TC-API-010 | EcoSim POST invalid body | HTTP 422 validation error | | ⏳ | Missing required fields |
| TC-API-011 | Response times within threshold | All endpoints < 2s | | ⏳ | `performance_test.py` |
| TC-API-012 | CORS headers present | Access-Control-Allow-Origin header present | | ⏳ | Preflight request |

---

## 9. Visualization Module

| Test Case ID | Description | Expected Result | Actual Result | Status | Remarks |
|---|---|---|---|---|---|
| TC-VIZ-001 | EnergyHub line chart renders | SVG chart visible with axes, labels, data points | | ⏳ | `EnergyTrends.jsx` |
| TC-VIZ-002 | EnergyHub choropleth map renders | Leaflet map loads with colored province polygons | | ⏳ | `EnergyMap.jsx` |
| TC-VIZ-003 | Map legend visible | Color scale legend explains metric values | | ⏳ | Inline SVG legend |
| TC-VIZ-004 | Map tooltip on hover | Tooltip shows province name and metric value | | ⏳ | Leaflet popup |
| TC-VIZ-005 | EcoSim KPI cards display | System kWp, score, and output values visible | | ⏳ | `Ecosim.jsx` |
| TC-VIZ-006 | EcoSim comparison table | Solar / Wind / Hydro columns with values | | ⏳ | `Ecosim.jsx` |
| TC-VIZ-007 | EcoSim AI panel | AI explanation text rendered in card/panel | | ⏳ | `Ecosim.jsx` |
| TC-VIZ-008 | Responsive layout (mobile) | UI adapts to 375px width without horizontal scroll | | ⏳ | Tailwind responsive |
| TC-VIZ-009 | Responsive layout (tablet) | UI adapts to 768px width with rearranged cards | | ⏳ | Tailwind responsive |

---

## 10. Machine Learning Module

| Test Case ID | Description | Expected Result | Actual Result | Status | Remarks |
|---|---|---|---|---|---|
| TC-ML-001 | DOE data preprocessing | Missing values handled; data types correct | | ⏳ | `DOE_arima_forecasting.ipynb` |
| TC-ML-002 | Stationarity check | ADF test p-value < 0.05 or differencing applied | | ⏳ | Time series assumption |
| TC-ML-003 | ARIMA model training | Model converges without errors | | ⏳ | `statsmodels ARIMA` |
| TC-ML-004 | ARIMA forecast shape | 6 forecast values for 2025–2030 | | ⏳ | `predictor.py` |
| TC-ML-005 | Forecast confidence intervals | Lower < point estimate < Upper for all years | | ⏳ | ARIMA `get_forecast` |
| TC-ML-006 | Model comparison CSV | MAE, RMSE, MAPE computed for all models | | ⏳ | `evaluate_models.py` |
| TC-ML-007 | Held-out test evaluation | At least one model achieves MAPE < 20% | | ⏳ | 2024 test set |
| TC-ML-008 | Random Forest overfitting demo | Train R² ≈ 1.0, Test R² << 1.0 | | ⏳ | Controlled experiment |

---

## 11. Summary Statistics

| Module | Total Tests | Passed | Failed | Pending | Pass Rate |
|---|---|---|---|---|---|
| Authentication | 6 | 0 | 0 | 6 | 0% |
| EnergyHub | 10 | 0 | 0 | 10 | 0% |
| EcoSim | 13 | 0 | 0 | 13 | 0% |
| AI Intelligence | 7 | 0 | 0 | 7 | 0% |
| Database | 10 | 0 | 0 | 10 | 0% |
| API Endpoints | 12 | 0 | 0 | 12 | 0% |
| Visualization | 9 | 0 | 0 | 9 | 0% |
| Machine Learning | 8 | 0 | 0 | 8 | 0% |
| **Grand Total** | **75** | **0** | **0** | **75** | **0%** |

**Note:** All test cases are currently marked **Pending** (⏳). Execute the test suite and update the Actual Result and Status columns accordingly.

---

## 12. Defect Log

| Defect ID | Test Case ID | Severity | Description | Status |
|---|---|---|---|---|
| | | | | |

*Log defects discovered during test execution here.*

---

## 13. Sign-Off

| Role | Name | Signature | Date |
|---|---|---|---|
| Test Engineer | | | |
| QA Lead | | | |
| Research Adviser | | | |

---

*End of System Test Results Report*
