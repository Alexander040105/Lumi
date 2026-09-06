# Failure & Recovery Results — LUMI

**Date:** September 5, 2026
**Method:** `artifacts/scripts/failure_matrix.py` — controlled failure injection via TestClient + singleton/mocking (no `.env` tampering; `settings.py:15` uses `load_dotenv(override=True)` so env-based injection is unreliable — in-process patching was used instead).
**Raw artifact:** `artifacts/failure/failure_matrix.json` (17 scenarios)

**Verdict legend:** GRACEFUL (degraded but correct response) · DEGRADED (works but wrong semantics) · FAIL · N/A · BYPASS-CONFIRMED (security-relevant behavior)

---

## 1. Results Matrix

| ID | Failure injected | Observed behavior | Verdict |
|---|---|---|---|
| TC-FR-01 | Gemini outage (all models raise) | Automatic fallback to **live Groq** — response produced in 1,683ms; log: `"All Gemini models failed; falling back to Groq emergency path"` | GRACEFUL |
| TC-FR-02 | EcoSim AI worker exceeds hard timeout (`_AI_CALL_TIMEOUT` → 50ms) | Returns structured fallback dict `error:"AI analysis timed out"` in **61ms** — no hang | GRACEFUL |
| TC-FR-03 | All LLM providers down (worker raises) | `analyze_renewable_results` returns fallback dict — endpoint remains functional | GRACEFUL |
| TC-FR-04a | Supabase client broken → `/health/detailed` | `status=degraded`, `supabase=error`, still HTTP 200 | GRACEFUL |
| TC-FR-04b | Supabase down → `/ecosim/municipalities` | **200** — served from bundled CSV fallback (1,813 items still returned) | GRACEFUL |
| TC-FR-04c | Supabase down → `/ecosim/` simulation | **404** `"The selected municipality was not found"` — clean, no crash | GRACEFUL |
| TC-FR-04d | Supabase down → `/protected/me` (no token) | **401** `"Missing token"` — auth fails before DB dependency | GRACEFUL |
| TC-FR-05 | Redis client → NullRedis | `/health/detailed`: `redis=not_configured`; `/map/solar` → **200** (cache-miss path) | GRACEFUL |
| TC-FR-06 | NASA POWER outage at runtime | **N/A** — runtime climate is served from Supabase + bundled CSVs; NASA POWER exists only in disabled ETL scripts (`api.py:16`) | N/A |
| TC-FR-07a | `municipality_id=999999` → `/ecosim/` | **404** clean message | GRACEFUL |
| TC-FR-07b | `municipality_id=999999` → `/geothermal/{id}` | **500** — global handler returns sanitized body `{detail, request_id}` but PGRST116 should map to 404 | DEGRADED |
| TC-FR-08 | ML worker URL dead (`127.0.0.1:59999`) → `POST /api/v1/chat` | **503** `{"detail":"ML worker unavailable: All connection attempts failed"}`; non-proxied paths unaffected (health 200) | GRACEFUL (⚠ leaks raw exception text — SEC-07) |
| TC-FR-09a | 70-req burst, public XFF, Redis loop-broken | 0×429 — **split counters**: ~35 reqs went to Redis path, ~35 to in-memory fallback; neither reached the 60 cap | FAIL-OPEN (see SEC-02) |
| TC-FR-09b | 70-req burst, `X-Forwarded-For: 127.0.0.1` | 0×429 — limiter bypassed (proven from LAN socket: 75×200 vs 60+15×429 without XFF) | BYPASS-CONFIRMED (SEC-01) |
| TC-FR-09c | NullRedis + public XFF, 75-req burst | Exactly `60×200, 15×429` — in-memory fallback **correct** when Redis returns NullRedis cleanly | GRACEFUL |
| TC-FR-09d | Throwing Redis (`pipeline()` raises) | Exactly `60×200, 15×429` — exception→memory path **correct** for a hard failure | GRACEFUL |
| TC-FR-10a | POST body >1MB | **413** `"Request body too large. Maximum size is 1 MB."` | GRACEFUL |
| TC-FR-10b | Malformed JSON body | **422** `json_invalid` | GRACEFUL |
| TC-FR-10c | Non-integer path param | **422** `int_parsing` | GRACEFUL |

## 2. Verified Resilience Mechanisms (code-level)

| Mechanism | Location | Behavior |
|---|---|---|
| Global exception handler | `main.py` + `app/middleware/` | Sanitized `{detail, request_id}` — no stack/path leak (verified TC-FR-07b body) |
| Request IDs | `RequestIDMiddleware` | UUID per request, echoed in logs + error bodies |
| LLM provider fallback | `llm_client.py` | Gemini → Groq when `GROQ_API_KEY` set |
| LLM hard timeout + persistent cache | `gemini_funcs.py:601-647` | Worker-thread timeout → fallback dict; results cached by content key |
| Supabase→CSV fallback | `ecosim.py:79-115` | Climate/municipality data falls back to bundled CSVs; 404 only if both empty |
| Redis NullRedis | `redis_client.py` | All cache helpers try/except → no-op |
| Rate-limit memory fallback | `rate_limit.py:54-63` | Works for clean NullRedis & hard exceptions; **not** merged with Redis counter (SEC-02) |
| Quota in-memory fallback | `dependencies/quota.py` | Anonymous quota works without Redis (per-process) |
| Frontend retry/timeout | `apiClient.js:5-7,58-95` | 30s timeout, 3 retries, 500ms exp backoff, no retry on 429 |
| ML-worker proxy isolation | `ml_worker_proxy.py:68-83` | 55s timeout → 503; other routes unaffected |
| Health degradation | `health.py` | `degraded` status + per-check detail |

## 3. Crash / Fail-Open Findings

| Finding | Severity | Detail |
|---|---|---|
| Rate-limit split-counter fail-open | Medium | Intermittent Redis → ~2× effective limit (FR-09a). Multi-instance deployments multiply the in-memory limit per process |
| `_get_user_status` fails open | Medium | Suspended users pass during a `profiles` outage (auth.py:223-228); `_get_user_role` fails closed — inconsistent |
| `/geothermal/{bad_id}` → 500 | Low | Sanitized body, wrong status semantics (DEF-01) |

## 4. Proposed / Not-Executed Scenarios

| Scenario | Status | Reason |
|---|---|---|
| Production Vercel function timeout (504) under cold-start | [OPEN] | Not load-tested against prod per scope constraint |
| Supabase **Auth** outage with a valid cached JWT | [OPEN] | Requires a real user token; `get_verified_user` would 401 (no local fallback on required paths — arguably correct) |
| pgvector outage during RAG queries | [OPEN] | Would need targeted mock of the vector client; expected behavior mirrors Supabase outage |
| Groq **and** Gemini real-API outage (network-level) | Partially covered | FR-03 simulated both raising; live network partition untested |
| Redis **permanent** outage under sustained load | Covered in part | NullRedis path verified; split-counter edge case found instead |

## 5. Recommendations

1. **Merge rate-limit counters** (or prefer Redis and count failures toward the window) — closes the SEC-02 fail-open gap.
2. **Fail closed in `_get_user_status`** to match `_get_user_role`.
3. **Map PGRST116 → 404** in `geothermal` (and audit for other `.single()` callers).
4. **Generic 503 body** in `ml_worker_proxy` — move exception text to logs keyed by `request_id`.
5. **Structured "degraded" responses**: endpoints that lose Supabase currently return 404 — a 503 with `Retry-After` would distinguish "not found" from "dependency down".
6. **Surface fallback state to the client**: EcoSim AI fallback returns 200 with `error` inside the payload — a `X-Degraded: true` header would let the UI show honest state.

*End of Failure & Recovery Results*
