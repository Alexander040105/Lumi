# Table 19. ISO/IEC 25010:2023 System Quality Evaluation Criteria (Flat Format)

LUMI is evaluated against the ISO/IEC 25010:2023 software product quality model using two parallel questionnaire instruments. Instrument A is administered to end-users, including both household decision-makers and electrical engineers who may use the system for professional assessment. Instrument B is administered to expert evaluators (software engineers and renewable energy practitioners). Both instruments use a 5-point Likert scale.

**Legend:** 1.00-1.80 = Very Low | 1.81-2.60 = Low | 2.61-3.40 = Moderate | 3.41-4.20 = High | 4.21-5.00 = Very High

---

## Instrument A — End-User Questionnaire (Households and Electrical Engineers)

**Instructions:** Please rate your level of agreement with each statement using the scale below.

**5 = Strongly Agree | 4 = Agree | 3 = Neutral | 2 = Disagree | 1 = Strongly Disagree**

**Demographic Profile**

| Item | Response |
|------|----------|
| I am a: | [ ] Homeowner / Resident  [ ] Electrical Engineer  [ ] Other: _______ |
| Age range: | [ ] 18-24  [ ] 25-34  [ ] 35-44  [ ] 45-54  [ ] 55+ |
| Years of experience in electrical engineering (if applicable): | [ ] N/A  [ ] 1-5  [ ] 6-10  [ ] 11-20  [ ] 20+ |

---

### Table 19-A. End-User Evaluation Criteria

| Category | Indicator | Description | Rating Scale |
|----------|-----------|-------------|--------------|
| Functional Suitability | Functional Completeness | The LUMI system provides all the tools I need to evaluate renewable energy options for a household. | 1-5 |
| Functional Suitability | Functional Correctness | The energy calculations (solar, wind, hydro) produce reasonable and realistic results. | 1-5 |
| Functional Suitability | Functional Appropriateness | The information and recommendations are relevant to Philippine conditions and my location. | 1-5 |
| Performance Efficiency | Time Behaviour | The platform loads quickly and responds without noticeable lag. | 1-5 |
| Performance Efficiency | Capacity | The system works smoothly even with multiple users or tasks. | 1-5 |
| Performance Efficiency | Time Behaviour | The platform remains stable during extended use. | 1-5 |
| Compatibility | Co-existence | I can use LUMI in my browser alongside other websites without problems. | 1-5 |
| Compatibility | Interoperability | The system works correctly on my preferred browser and device. | 1-5 |
| Interaction Capability | Learnability / Operability | The interface is user-friendly and easy to navigate. | 1-5 |
| Interaction Capability | Appropriateness Recognizability | Instructions and labels are clear and understandable. | 1-5 |
| Interaction Capability | Learnability | I can operate the system without needing a tutorial or manual. | 1-5 |
| Interaction Capability | User Interface Aesthetics | The interface is visually pleasing and professionally designed. | 1-5 |
| Reliability | Faultlessness | The system functions consistently without crashing. | 1-5 |
| Reliability | Maturity | Errors or bugs are minimal during normal use. | 1-5 |
| Reliability | Recoverability | The system can recover from interruptions (e.g., page reloads, disconnections). | 1-5 |
| Security | Confidentiality / Authenticity | The platform ensures secure login or access control. | 1-5 |
| Security | Integrity | There are no exposed vulnerabilities during normal use. | 1-5 |
| Maintainability | Modularity / Analysability | The platform feels well-structured and consistent across modules. | 1-5 |
| Maintainability | Modifiability | Features appear logically organized and easy to improve or expand. | 1-5 |
| Flexibility | Adaptability | The platform works well on different browsers or devices. | 1-5 |
| Flexibility | Installability | No installation is required for access (web-based compatibility is effective). | 1-5 |
| Safety | Operational Constraint | LUMI clearly states that its recommendations are estimates and I should consult professionals. | 1-5 |
| Safety | Risk Identification | The system warns me about risks such as high upfront costs and weather-dependent output. | 1-5 |
| Safety | Hazard Warning | Safety hazards (electrical, structural) are mentioned when appropriate. | 1-5 |

---

## Instrument B — Expert Evaluator Questionnaire (Software Engineers and Renewable Energy Practitioners)

**Instructions:** Please rate your professional assessment of each statement using the scale below.

**5 = Strongly Agree | 4 = Agree | 3 = Neutral | 2 = Disagree | 1 = Strongly Disagree**

---

### Table 19-B. Expert Evaluator Evaluation Criteria

| Category | Indicator | Description | Rating Scale |
|----------|-----------|-------------|--------------|
| Functional Suitability | Functional Completeness | The system's feature set (forecasting, Ecosim, mapping, AI assistant) is complete for a household-level renewable energy decision-support system. | 1-5 |
| Functional Suitability | Functional Correctness | The physics-based calculations (solar temperature factor, wind Betz limit, hydro runoff coefficients, economic payback) are implemented correctly per engineering principles. | 1-5 |
| Functional Suitability | Functional Appropriateness | Philippine-specific defaults (electricity rates, climate zones, DOE data) are appropriate for the target population. | 1-5 |
| Performance Efficiency | Time Behaviour | API endpoints meet the stated performance thresholds under normal load (overview <2s, Ecosim <3s, AI <5s, map <2s). | 1-5 |
| Performance Efficiency | Resource Utilization | The system demonstrates efficient memory usage (FAISS <5MB, DataFrame <10MB) with no memory leaks under sustained API load. | 1-5 |
| Performance Efficiency | Capacity | The system maintains acceptable response times and error rates under concurrent load (50 simultaneous requests). | 1-5 |
| Compatibility | Interoperability | External API integrations (NASA POWER, Gemini, Groq, Supabase) operate correctly with proper error handling. | 1-5 |
| Compatibility | Interoperability | The REST API conforms to OpenAPI standards with valid JSON schemas. | 1-5 |
| Interaction Capability | User Error Protection | Input validation, error handling, and user guidance effectively prevent or recover from common user errors. | 1-5 |
| Interaction Capability | Inclusivity | The interface accommodates users with varying technical backgrounds through plain-language explanations. | 1-5 |
| Reliability | Faultlessness | The system operates without unhandled exceptions, memory leaks, or unexpected terminations under normal and edge-case usage. | 1-5 |
| Reliability | Availability | Health-check endpoints confirm all services (API, database, ML artifacts) are operational. | 1-5 |
| Reliability | Fault Tolerance | Fallback mechanisms (Gemini to Groq, default climate values, descriptive error responses) ensure graceful degradation. | 1-5 |
| Security | Confidentiality | Authentication (OAuth 2.0, JWT HMAC-SHA256), authorization (RLS), and secret management adequately protect user data. | 1-5 |
| Security | Integrity | Data integrity is maintained through RLS write restrictions, Pydantic validation, and input sanitization. | 1-5 |
| Security | Authenticity / Non-repudiation | Identity verification through OAuth and JWT validation effectively prevents impersonation and enforces session expiration. | 1-5 |
| Maintainability | Modularity | The codebase exhibits clear modularity through domain-based FastAPI routers, service layers, and component-based React architecture. | 1-5 |
| Maintainability | Reusability | Core components (renewable calculators, chart primitives, geographic utilities) are reusable across contexts. | 1-5 |
| Maintainability | Modifiability / Testability | The system can accommodate changes (new LLM providers, data sources, chart types) with minimal structural modification. | 1-5 |
| Flexibility | Adaptability | The system can be adapted to different deployment targets (static hosting, ASGI servers, PostgreSQL-compatible databases). | 1-5 |
| Flexibility | Scalability | The stateless API design and pre-computed ML artifacts support horizontal scaling and growth in user base. | 1-5 |
| Flexibility | Replaceability | Individual components (LLM provider, database host, climate data source) can be replaced without architectural redesign. | 1-5 |
| Safety | Operational Constraint | Operational constraints (conservative engineering assumptions, confidence disclosures) prevent dangerous reliance on automated recommendations. | 1-5 |
| Safety | Risk Identification | The system proactively identifies and communicates risks (financial, environmental, geographic, data quality). | 1-5 |
| Safety | Fail Safe | Failure modes default to safe states: structured error responses, input validation rejection, and fallback defaults for missing data. | 1-5 |

---

## Appendix A. ISO 25010:2023 Sub-Characteristic Mapping

| Table Ref. | Category | Indicator | ISO 25010:2023 Sub-Characteristic |
|------------|----------|-----------|--------------------------------------|
| 19-A.1 | Functional Suitability | Functional Completeness | Functional Completeness |
| 19-A.2 | Functional Suitability | Functional Correctness | Functional Correctness |
| 19-A.3 | Functional Suitability | Functional Appropriateness | Functional Appropriateness |
| 19-A.4 | Performance Efficiency | Time Behaviour | Time Behaviour |
| 19-A.5 | Performance Efficiency | Capacity | Capacity |
| 19-A.6 | Performance Efficiency | Time Behaviour | Time Behaviour |
| 19-A.7 | Compatibility | Co-existence | Co-existence |
| 19-A.8 | Compatibility | Interoperability | Interoperability |
| 19-A.9 | Interaction Capability | Learnability / Operability | Learnability / Operability |
| 19-A.10 | Interaction Capability | Appropriateness Recognizability | Appropriateness Recognizability |
| 19-A.11 | Interaction Capability | Learnability | Learnability |
| 19-A.12 | Interaction Capability | User Interface Aesthetics | User Interface Aesthetics |
| 19-A.13 | Reliability | Faultlessness | Faultlessness |
| 19-A.14 | Reliability | Maturity | Maturity |
| 19-A.15 | Reliability | Recoverability | Recoverability |
| 19-A.16 | Security | Confidentiality / Authenticity | Confidentiality / Authenticity |
| 19-A.17 | Security | Integrity | Integrity |
| 19-A.18 | Maintainability | Modularity / Analysability | Modularity / Analysability |
| 19-A.19 | Maintainability | Modifiability | Modifiability |
| 19-A.20 | Flexibility | Adaptability | Adaptability |
| 19-A.21 | Flexibility | Installability | Installability |
| 19-A.22 | Safety | Operational Constraint | Operational Constraint |
| 19-A.23 | Safety | Risk Identification | Risk Identification |
| 19-A.24 | Safety | Hazard Warning | Hazard Warning |
| 19-B.1 | Functional Suitability | Functional Completeness | Functional Completeness |
| 19-B.2 | Functional Suitability | Functional Correctness | Functional Correctness |
| 19-B.3 | Functional Suitability | Functional Appropriateness | Functional Appropriateness |
| 19-B.4 | Performance Efficiency | Time Behaviour | Time Behaviour |
| 19-B.5 | Performance Efficiency | Resource Utilization | Resource Utilization |
| 19-B.6 | Performance Efficiency | Capacity | Capacity |
| 19-B.7 | Compatibility | Interoperability | Interoperability |
| 19-B.8 | Compatibility | Interoperability | Interoperability |
| 19-B.9 | Interaction Capability | User Error Protection | User Error Protection |
| 19-B.10 | Interaction Capability | Inclusivity | Inclusivity |
| 19-B.11 | Reliability | Faultlessness | Faultlessness |
| 19-B.12 | Reliability | Availability | Availability |
| 19-B.13 | Reliability | Fault Tolerance | Fault Tolerance |
| 19-B.14 | Security | Confidentiality | Confidentiality |
| 19-B.15 | Security | Integrity | Integrity |
| 19-B.16 | Security | Authenticity / Non-repudiation | Authenticity / Non-repudiation |
| 19-B.17 | Maintainability | Modularity | Modularity |
| 19-B.18 | Maintainability | Reusability | Reusability |
| 19-B.19 | Maintainability | Modifiability / Testability | Modifiability / Testability |
| 19-B.20 | Flexibility | Adaptability | Adaptability |
| 19-B.21 | Flexibility | Scalability | Scalability |
| 19-B.22 | Flexibility | Replaceability | Replaceability |
| 19-B.23 | Safety | Operational Constraint | Operational Constraint |
| 19-B.24 | Safety | Risk Identification | Risk Identification |
| 19-B.25 | Safety | Fail Safe | Fail Safe |

---

## Appendix B. Scoring and Analysis Procedure

**Step 1: Data Entry**
- For each respondent, record Likert scores (1-5) for every statement.
- Categorize end-user respondents by type: Household/Resident or Electrical Engineer.

**Step 2: Characteristic-Level Aggregation**
- For each characteristic (e.g., Functional Suitability), compute the mean of all statement scores within that characteristic.
- Compute standard deviation to assess inter-respondent agreement.
- Apply verbal interpretation per the legend.

**Step 3: Weighted Overall Score**

| Quality Characteristic | Weight |
|------------------------|--------|
| Functional Suitability | 0.18 |
| Performance Efficiency | 0.12 |
| Compatibility | 0.08 |
| Interaction Capability | 0.15 |
| Reliability | 0.12 |
| Security | 0.10 |
| Maintainability | 0.10 |
| Flexibility | 0.08 |
| Safety | 0.07 |
| **Total** | **1.00** |

Weighted Overall Score = sum of (Characteristic Mean x Weight) across all nine characteristics.

**Step 4: Grade Interpretation**

| Overall Score | Grade | Interpretation |
|---------------|-------|----------------|
| 4.50 - 5.00 | Excellent | World-class quality for an academic project |
| 3.50 - 4.49 | Good | Strong quality; minor improvements recommended |
| 2.50 - 3.49 | Acceptable | Meets minimum standards; notable gaps exist |
| 1.50 - 2.49 | Needs Improvement | Significant rework required |
| 1.00 - 1.49 | Poor | Does not meet basic quality expectations |

**Step 5: Segmented Reporting**
- Report overall scores for all end-users combined.
- Report separate scores for Household/Resident respondents and Electrical Engineer respondents to identify perception gaps between technical and non-technical end-users.
- Report expert evaluator scores separately.
- Compare end-user and expert scores to highlight alignment or divergence in quality perceptions.

---

*Table 19. ISO/IEC 25010:2023 Evaluation Criteria for LUMI (Flat Format) — End of Table*
