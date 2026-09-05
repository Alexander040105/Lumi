# Technical Evaluation Materials — LUMI

**Package date:** September 5, 2026
**Purpose:** Retrospective audit + thesis-panel evaluation evidence for the LUMI renewable-energy intelligence system (EcoSim · Energy Hub · AI features · FastAPI · React/Vite · Supabase · Groq/Gemini · Vercel).

---

## Documents

| # | Document | Contents |
|---|---|---|
| 1 | [functional-test-results.md](functional-test-results.md) | All automated suites + 75-endpoint live sweep; expected vs actual per test case; defect log |
| 2 | [performance-measurements.md](performance-measurements.md) | Endpoint latency (min/mean/p50/p95/max), LLM & Supabase timings, frontend bundle, prod smoke |
| 3 | [load-scalability-results.md](load-scalability-results.md) | Locust stepped runs 1→100 users, throughput plateau, breaking point, rate-limit profiles |
| 4 | [security-test-results.md](security-test-results.md) | 10 findings register (1 High confirmed live), auth matrix, scans, verified controls |
| 5 | [system-architecture.md](system-architecture.md) | Mermaid deployment topology, request pipeline, data flow, auth sequence, failure boundaries |
| 6 | [failure-recovery-results.md](failure-recovery-results.md) | 17-scenario failure-injection matrix, verified resilience, crash/fail-open findings |

## Evidence artifacts (`artifacts/`)

```
artifacts/
├── scripts/           endpoint_sweep.py · benchmark.py · failure_matrix.py · security_probes.py
├── functional/        unit/integration/frontend test logs + endpoint_sweep.jsonl/csv
├── perf/              latency.csv · db_timings.csv · vite-build.txt
├── load/              locustfile.py · runs/*.csv+html (6 levels + clean re-runs + profiles)
├── security/          bandit-app.txt · pip-audit-env.txt · npm-audit-frontend.json
│                      · probes.json · prod_smoke.txt
└── failure/           failure_matrix.json
```

## Headline results

- **Functional:** 333 automated assertions pass (176 + 77 + 9 + 67 + 4); sweep 70/75 with 5 low-severity validation findings; 30 DB tests blocked on `TEST_DATABASE_URL` (deliberately not run against production).
- **Performance:** all core endpoints p95 < 500ms single-user; simulation ~450ms; LLM path ~460ms–3.2s; Supabase ~70–160ms/query.
- **Load:** zero failures at all levels; graceful degradation; interactive ceiling ~10–25 users on a single worker; ~11–14 RPS plateau.
- **Security:** XFF-spoof rate-limit/quota bypass **confirmed from a real LAN socket**; split-counter fail-open under Redis flapping; 87 backend + 7 frontend dependency advisories; all auth/JWT probes rejected correctly.
- **Failure:** 15/17 scenarios graceful — CSV fallback, NullRedis, LLM fallback+timeout, 503 proxy isolation, 413/422 input gates all verified live.

## Known gaps (honest accounting)

- Dedicated chatbot (`/api/v1/chat` + `ChatPage.jsx`) is **code-present but not mounted** — live AI coverage is via EcoSim AI + EnergyHub endpoints.
- `TEST_DATABASE_URL` not configured → 30 DB-layer tests pending (kept off production by design).
- OAuth/valid-token flows not exercised (no test credentials).
- Production load testing deliberately excluded — smoke-level only.
- NASA POWER is not part of runtime behavior — marked N/A, not measured.

## Environment used

Windows 11 · Python 3.13.2 (global env) · uvicorn single worker · Node 24.15.0 · pytest 9.1.0 · Locust 2.46.4 · pip-audit 2.10.1 · Bandit 1.9.4 · Vitest 2.1.9 · live Supabase (eu-west) + Upstash Redis · prod smoke: `lumi-backend-ten.vercel.app`.
