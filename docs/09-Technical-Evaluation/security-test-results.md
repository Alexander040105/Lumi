# Security Test Results — LUMI

**Date:** September 5, 2026
**Scope:** AuthN/AuthZ, injection, CORS, headers, secrets handling, dependency CVEs, rate-limit/quota enforcement
**Tools:** Bandit 1.9.4, pip-audit 2.10.1, npm audit, `artifacts/scripts/security_probes.py`, targeted live probes
**Constraint honored:** No destructive DB writes; no credential brute-forcing; probes read-only or self-cancelling.

---

## 1. Methodology

1. **Static analysis:** `bandit -r fastapi-backend/app` + `pip-audit` (env) + `npm audit` (frontend).
2. **Live probes** (`security_probes.py`): JWT matrix, security headers, CORS preflight, docs exposure, error-body leakage.
3. **Targeted live tests:** XFF rate-limit bypass (LAN socket), rate-limit split-counter behavior, SQL-injection-style inputs via the endpoint sweep.
4. **Code audit:** auth deps, rate-limit/quota middleware, env handling, admin endpoints, ETL string interpolation.
5. **Secrets review:** `git ls-files` for tracked env/key files; `.env` names scanned for `VITE_`-prefixed secrets.

Raw artifacts: `artifacts/security/` (`bandit-app.txt`, `pip-audit-env.txt`, `npm-audit-frontend.json`, `probes.json`, `prod_smoke.txt`).

## 2. Confirmed Vulnerabilities

### SEC-01 — `X-Forwarded-For` trusted unconditionally → rate-limit & quota bypass  **HIGH**

`app/middleware/rate_limit.py:43-52` and `app/dependencies/quota.py` take the *leftmost* `X-Forwarded-For` as the client IP with no trusted-proxy validation. `_is_localhost()` then exempts loopback values.

**Live proof** (LAN socket 192.168.254.160 → `0.0.0.0:8001`, non-loopback client):

| Burst | Result |
|---|---|
| No XFF, 75 req | `60 × 200` then `15 × 429` — limiter enforced |
| `X-Forwarded-For: 127.0.0.1`, 75 req | `75 × 200`, **0 × 429** — bypassed |

Same code path exempts the **anonymous EcoSim AI quota** (1/day) and the stricter auth-endpoint limit (10/min). On Vercel, `x-vercel-forwarded-for`/platform headers should be preferred; trusting raw XFF is only safe behind a proxy that overwrites it.

### SEC-02 — Rate limiter fails open under intermittent Redis failure (split counters)  **MEDIUM**

`_is_allowed_redis` counts in the Redis ZSET; on exception it falls back to a **separate** in-memory dict (`_is_allowed_memory`). Under a flapping Redis, each request lands in exactly one counter — the two are never merged. Observed live: 70-request burst during "Event loop is closed" churn → **0 × 429** because counts split ~35/35, neither reaching 60. Worst case ≈ 2× effective limit; in multi-worker/serverless deployments the in-memory counter is per-process anyway (limits multiply per instance — architectural caveat, not a bug).

### SEC-03 — `_get_user_status` fails open on DB outage  **MEDIUM**

`app/dependencies/auth.py:223-228`: if the `profiles.is_active` lookup throws, the dependency returns `True` (allow). A suspended user retains access during a Supabase outage. `_get_user_role` (line 200) correctly fails *closed* to `"user"` — posture is inconsistent; status check should match.

### SEC-04 — Dependency CVEs in the backend env  **MEDIUM**

`pip-audit`: **87 known vulnerabilities across 15 packages** (`artifacts/security/pip-audit-env.txt`). Runtime-relevant:

| Package | Version | Advisory | Fix | Reachability |
|---|---|---|---|---|
| `python-jose` | 3.3.0 | PYSEC-2024-232/233 (alg-confusion / DoS in JWT verify), PYSEC-2025-185 | 3.4.0 | **Direct** — JWT verify path |
| `starlette` | 0.38.6 | 8 advisories (incl. PYSEC-2026-1941/1943, multipart DoS family) | ≥0.40.0 / 1.x | **Direct** — every request |
| `cryptography` | 49.0.0 | PYSEC-2026-3552 | 50.0.0 | Transitive (TLS/JWT) |
| `ecdsa` | 0.19.2 | PYSEC-2026-1325 (Minerva timing) | none yet | JWT alg support |
| `python-dotenv` | 1.0.1 | PYSEC-2026-2270 | 1.2.2 | Startup only |
| `pillow`, `transformers`, `torch`, `tornado`, `mistune`, `pip`, `setuptools`, `h2`, `pyasn1`, `ujson` | various | 60+ advisories | — | Mostly non-runtime or dev/ML |

### SEC-05 — `VITE_`-prefixed secret names in root `.env`  **MEDIUM (latent)**

Root `.env` contains `VITE_SUPABASE_SERVICE_ROLE_KEY` and `VITE_SUPABASE_JWT_SECRET`. No frontend source references them today, but **any `VITE_*` var is inlined into the client bundle** if ever imported — service-role key exposure would defeat RLS entirely. Rename to unprefixed names (backend-only) or move to `fastapi-backend/.env`.

### SEC-06 — `admin create-user` returns `temp_password` in the response body  **LOW**

`app/routes/admin.py:202-209` includes the generated password in JSON. Admin-only + HTTPS mitigates, but credentials should be delivered via a one-time link or server-side email, not an API response that intermediaries/logs may capture.

### SEC-07 — ML-worker 503 leaks raw exception text  **LOW**

`app/services/ml_worker_proxy.py:79-80`: `{"detail": "ML worker unavailable: {exc}"}` — exception strings can embed internal hostnames/URLs. Verified live: `POST /api/v1/chat` → 503 `"All connection attempts failed"`. Return a generic message + request_id.

### SEC-08 — `etl.py` table-name interpolation  **LOW**

Table identifiers interpolated into SQL strings (code-verified; ETL router disabled — `api.py:16`). Not reachable at runtime; fix before re-enabling ETL.

### SEC-09 — Bandit: MD5 for cache keys, `0.0.0.0` bind strings, `try/except/pass`  **LOW/INFO**

`bandit-app.txt`: 4 High / 3 Medium / 13 Low. Triaged: the two MD5 hits (`ecosim.py` ~958/963) hash non-secret cache keys — **not password storage**, acceptable but migrate to `sha256` for hygiene. `0.0.0.0` strings are in `_is_localhost` helpers (not socket binds). `try/except/pass` in `settings.py` masks config errors. Most `assert` hits are test helpers.

### SEC-10 — `server: uvicorn` banner + docs exposure  **INFO**

`server` header discloses the ASGI server; `/docs`, `/openapi.json`, `/redoc` return 200 in **production** (verified). Acceptable for a public API but worth an intentional decision.

## 3. Verified Controls (executed, passing)

| Control | Evidence |
|---|---|
| No token → 401 on all protected/admin routes | probes SEC-AUTH-01, ADM×3 |
| Malformed / `alg:none` / wrong-signature JWT → 401 | SEC-AUTH-02/03/04 |
| Expired JWT (real secret) → 401 | SEC-AUTH-05 |
| Validly-signed JWT for nonexistent user → 401 (server-side `auth.get_user` check) | SEC-AUTH-06 |
| Security headers 5/5 (XCTO, XFO, HSTS, CSP, Referrer-Policy) local + prod | SEC-HDR-01, `prod_smoke.txt` |
| CORS allowlist + `lumi-frontend-*.vercel.app` regex; disallowed origin → 400 | SEC-CORS-* local + prod |
| SQL-injection-style inputs → 200/404/422, no SQL execution | sweep `inj` rows |
| 500 body sanitized (`{"detail":"Server error…","request_id"}` — no stack/path leak) | SEC-ERR-01 |
| Body >1MB → 413; malformed JSON → 422 | failure_matrix TC-FR-10 |
| Rate limit works when Redis healthy (60/min → 429) & on NullRedis in-memory fallback (exactly 60→429) | §2 live tests |
| `.env` not tracked in git; only `*.env.example` committed | `git ls-files` |
| Auth hardening notes: local-JWT optional path (`get_verified_user_optional`) trusts signature without re-checking user existence — only usable if `SUPABASE_JWT_SECRET` already leaked | code read, auth.py:132-167 |

## 4. Frontend dependency audit

`npm audit`: **7 vulnerabilities** — 1 critical (`vitest` via `@vitest/mocker`, dev-only), 1 high (`vite` path-traversal, dev-only), 5 moderate incl. **`react-router`/`react-router-dom` open-redirect & XSS advisories (CVE-2025-68470 family — runtime-shipped)** and `esbuild` dev-server request forgery. Recommendation: bump `react-router-dom` (fix available, non-major); vitest/vite require major upgrades.

## 5. Supabase / RLS posture

- Backend uses **service-role key** (bypasses RLS) for all server-side reads — correct pattern for a trusted backend; means RLS is *not* the access-control layer for API consumers (the FastAPI auth deps are).
- Anon/publishable key is hardcoded in `react-frontend/src/utils/env.js` — acceptable *by design* for the publishable key, provided RLS is enabled on user-facing tables (frontend never talks to tables directly in current code — all data flows through the backend).
- RLS policies themselves were not probed (requires authenticated Supabase session) — **[OPEN]**.

## 6. Findings Register

| ID | Severity | Status |
|---|---|---|
| SEC-01 XFF bypass | **High** | Confirmed live — fix: trust `x-vercel-forwarded-for` / real socket IP behind platform |
| SEC-02 split-counter fail-open | Medium | Confirmed — merge counters or prefer-Redis-then-stampede |
| SEC-03 status check fail-open | Medium | Confirmed — fail closed like `_get_user_role` |
| SEC-04 dependency CVEs | Medium | pip/npm audit artifacts; priority: `python-jose`, `starlette`, `react-router-dom` |
| SEC-05 `VITE_` secret names | Medium (latent) | Rename/move |
| SEC-06 temp_password in response | Low | Design change |
| SEC-07 503 leaks exception text | Low | Generic message |
| SEC-08 etl.py SQL identifiers | Low (unreachable) | Parameterize before re-enable |
| SEC-09 bandit triage | Low/Info | MD5→sha256 hygiene |
| SEC-10 banner + docs exposure | Info | Decision needed |

## 7. Limitations

- No authenticated-session testing (no test credentials) — admin/user role paths probed only unauthenticated.
- RLS policies not exercised directly.
- No TLS/cert testing (localhost) — prod HSTS verified.
- Pen-test depth is bounded: no fuzzing, no session-fixation or CSRF cross-site tests beyond CORS preflight.

*End of Security Test Results*
