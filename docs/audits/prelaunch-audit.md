# LUMI Pre-Launch Audit

**Date:** 2026-09-17 · **Scope:** static code review + live API/Supabase probing on the local dev stack (uvicorn :8000, Vite :5174, live Supabase project `husnkzlccdrjpwlqcfbt`)
**Method:** adversarial; every claim below carries file:line or reproduction evidence. Two temporary test users were created via the Supabase admin API and fully deleted afterward.

**Launch verdict: NOT READY** — one confirmed privilege-escalation vulnerability and one broken account-deletion path must be fixed first.

---

## CRITICAL

### C1. Any user can self-escalate `plan`/`is_active` via direct PostgREST — VERIFIED LIVE

The `profiles` table RLS policy *"Users update own profile"* allows updating **every column**, including `plan` and `is_active`. The backend's own `PUT /protected/profile` correctly whitelists fields (`extra="forbid"`), but PostgREST bypasses the backend entirely.

**Evidence (reproduced live):**
```
PATCH /rest/v1/profiles?id=eq.<own-id>
Authorization: Bearer <regular-user-JWT>
{"plan":"premium"}  →  200, row updated
GET /api/v1/protected/me  →  {"role":"user","plan":"premium"}   ← effective plan granted
```

**Impact:**
- Free users grant themselves `premium` simulation/chat limits (`_get_effective_plan` reads `profiles.plan` via service role — `app/dependencies/auth.py:244-270`).
- A **banned user can unban themselves**: ban sets `profiles.is_active=false`, but the user can PATCH `is_active=true` on their own row while their JWT remains valid (~1 h). `_get_user_status` (`auth.py:206-235`) then passes them through.
- A user could also set `is_active=false`… then `true`; arbitrary self-modification of any profiles column (`ecosim_autosave`, etc.).

**Root cause:** `supabase/table_scripts/auth_admin_schema.sql:158-185` — the update policy is row-scoped but not column-scoped.

**Fix:** column-level privileges — `REVOKE UPDATE (plan, is_active) ON public.profiles FROM authenticated` and `GRANT UPDATE (full_name, organization, location, preferred_municipality_id, avatar_url, ecosim_autosave) ...`; or a `BEFORE UPDATE` trigger rejecting privileged-column changes from non-service roles. Also re-verify: `profiles`, `saved_locations`, and any other self-writable table for sensitive columns.

---

## HIGH

### H1. Account/user deletion fails for any user with saved simulations — VERIFIED LIVE

`saved_simulations.user_id → auth.users(id)` has **no ON DELETE CASCADE**. Deleting a user who has saved simulations returns a 23503 FK violation → HTTP 500.

**Evidence:** `DELETE /auth/v1/admin/users/<id>` → `{"code":"23503","message":"update or delete on table \"users\" violates foreign key constraint \"saved_simulations_user_id_fkey\""}`. Affected paths: `DELETE /api/v1/protected/me` (self-delete, `protected.py:145-158`) and `DELETE /api/v1/admin/users/{id}` — both will 500 in production for real users.

Additionally, `admin_audit_log.admin_id` and `admin_audit_log.target_user_id` (`lumi_schema_latest.sql:2032,2037`) also reference `auth.users` with no cascade — admins and audit targets become undeletable even after the sims fix. Audit rows should likely be preserved, so use `ON DELETE SET NULL` there, or delete dependents first.

**Fix:** migration adding `ON DELETE CASCADE` to `saved_simulations.user_id` (and `saved_locations`, `chat_sessions/messages`, `user_ecosim_logs`, `user_usage_limits` — verify each) and `ON DELETE SET NULL` for `admin_audit_log.*_user_id` columns. GDPR account-erasure is currently broken.

### H2. 33 Filipino + 3 English i18n keys missing → raw keys render in UI

`t()` calls reference keys absent from locale files (`react-frontend/src/i18n/`):

- **Missing in `fil.json` (33):** the entire `admin.logsPage.*` section (10 keys — the Admin Logs page is untranslated), `ecosim.results.aiAnalysis.*` (7 — the AI analysis card), `ecosim.wizard.saveAsPdf/saveToAccount/generatingPdf`, `ecosim.completion.*`, `ecosim.toasts.aiFailed/pdfFailed`, `energyHub.map.explanation*` (7), `energyHub.map.volcanoMarkerTooltip`, `energyHub.sources.hover`, `admin.userDetail.location/organization`.
- **Missing in `en.json` (3):** `admin.userDetail.location`, `admin.userDetail.organization`, `energyHub.sources.hover`.

Users see literal strings like `admin.logsPage.title`. This is the same bug class as the `common.settings` navbar issue fixed in eb97b68 — a systemic gap, not a one-off.

**Fix:** add missing keys; add a CI check that fails when `t()` keys don't exist in both locales (the audit script is trivial — ~20 lines).

### H3. Main JS bundle is 6.4 MB, no code-splitting

`npm run build` produces `dist/assets/index-*.js` = **6,418,557 bytes** (+ pdfmake 1.0 MB, leaflet 150 KB) — plotly and friends ship in the entry chunk. On Philippine mobile/slow connections this is a first-load killer and will hammer Core Web Vitals.

**Fix:** route-level `React.lazy()` code-splitting (Ecosim/EnergyHub/admin are natural splits), plus `manualChunks` for plotly/pdfmake/recharts. Verified: no secrets in bundle — only the publishable `sb_publishable_…` key (expected).

---

## MEDIUM

### M1. Server secrets live in `react-frontend/.env`

`react-frontend/.env` contains `SUPABASE_SERVICE_ROLE_KEY` (`sb_secret…`), `SUPABASE_JWT_SECRET`, and `SUPABASE_JWT_SERVICE_ROLE_KEY` (a full legacy JWT). They are **not** bundled (not `VITE_`-prefixed; `dist/` grep-verified clean), but this is secret sprawl: one accidental `VITE_` prefix, `.env` copy, or misconfigured build leaks full DB-admin to browsers. Root `.env` additionally holds `GEMINI_API_KEY`, `GROQ_API_KEY`, `HF_TOKEN`, `MAILEROO_SMTP_*`, `UPSTASH_REDIS_URL`, `SUPABSE_DB_PASSWORD` (note the typo'd var name).

**Fix:** keep only `VITE_*` vars in `react-frontend/.env`; move server secrets to backend env exclusively. `.env` files are correctly gitignored — verified.

### M2. Missing/cross-user simulation IDs return 500 instead of 404 — VERIFIED LIVE

`GET/PATCH/DELETE /simulations/{id}` uses `.single()`; zero rows → exception → `500 "Failed to fetch simulation"`. Reproduced for both a random UUID and a cross-user ID. IDOR itself is blocked (row-level `.eq("user_id")` — verified data stayed intact), but: (a) `apiClient.request` **retries 5xx three times** (`apiClient.js:58-70`) — every stale link costs 3 calls; (b) 500s pollute error monitoring; (c) inconsistent API semantics.

**Fix:** catch the empty-result case → `404 "Simulation not found"`.

### M3. Role/ban changes propagate with up-to-5-minute delay — VERIFIED LIVE

`_get_user_role` and `_get_effective_plan` cache in Redis for 300 s; `_get_user_status` for 60 s (`auth.py:182-223`). Elevating a test user took a manual cache-key deletion to take effect — **a demoted admin keeps full admin access for up to 5 minutes; a banned user up to ~60 s.**

**Fix:** on admin role/ban operations (`admin.py`), invalidate `lumi:auth:{user_id}:role|plan|active` keys immediately.

### M4. Admin tables clip on mobile

`AdminUsage.jsx:116`, `AdminUsers.jsx:125`, `AdminLogs.jsx:130` wrap tables in `overflow-hidden` — the 10-column usage table is truncated, not scrollable, at mobile widths. `ForecastPanel.jsx` already demonstrates the correct `overflow-x-auto` pattern.

### M5. Disabled routers ship without auth (etl.py, chat.py)

`app/routes/api.py:10,16,27,33` — intentionally commented out, verified 404 live. **But** `etl.py` defines `POST /run/climate` (runs a full pipeline), `GET /lineage`, `GET /validate` with **zero auth dependencies** — uncommenting one line instantly exposes an unauthenticated mutating endpoint. Dead frontend surface mirrors this: `MapPage` (imported but unrouted — `AppRoutes.jsx:14`), `ChatPage.jsx`, `ProfilePage.jsx`, `AdminModeration.jsx`, and chat/map functions in `apiClient.js` that would hit 404s.

**Fix:** add `Depends(get_verified_user)`/`require_admin` to etl/chat routes even while disabled (defense-in-depth), or delete the dead code.

### M6. CORS regex admits any localhost origin and any `*-xi.vercel.app`

`CORS_ORIGIN_REGEX=https://.*-xi\.vercel\.app|http://(localhost|127\.0\.0\.1)(:\d+)?` — any locally-hosted page can make credentialed API calls when the app runs on a user's machine; every Vercel preview deployment is trusted. Non-wildcard rejection verified live (fake origin → no `allow-origin` header), but tighten for production.

---

## LOW

- **L1.** `POST /simulations` accepts `municipality_id=-5` (201) — no `ge=0` bound; stores garbage references (`simulations.py:18`).
- **L2.** `<script>alert(1)</script>` accepted as a simulation label (201). React escapes on render and there is **zero `dangerouslySetInnerHTML`** — but if labels ever reach CSV/PDF exports or an unsafe sink, it becomes exploitable. Sanitize at write time.
- **L3.** `system_config` is world-readable by design ("Anyone read system config" policy) — currently exposes `free_sim_limit`, `chatbot_enabled`, `free_chat_limit`, `maintenance_mode`. Harmless today; **never** let secrets/config-internal values land in this table.
- **L4.** `_get_user_status` treats a *missing* profile as **active** (`auth.py:225-230`) — a user whose profile row is deleted regains access. Fail closed for missing profiles (or ensure profile always exists).
- **L5.** Duplicate `server` response header (`uvicorn` + `Lumi`) — cosmetic banner-masking miss in `security.py`.
- **L6.** Login/signup validation is `required`-attribute-only — no client-side password strength/format checks (`Login.jsx`); relies on Supabase errors.
- **L7.** `get_verified_user` calls Supabase `auth.get_user` on **every** protected request — external round-trip latency per call; local JWT verify exists but is only used on optional paths (`auth.py:102-131` vs `74-87`).
- **L8.** `fastapi-backend/.env` exists with **all values empty** while the backend actually resolves config from the root `.env` — confusing and fragile; if precedence flips, the backend breaks silently.
- **L9.** Supabase **email-send rate limit was hit during the audit** (`over_email_send_rate_limit`) — default Supabase SMTP allows only a handful of emails/hour. Maileroo SMTP creds exist in `.env` but Supabase dashboard SMTP is a separate config — **verify custom SMTP before launch or signups/password-resets will fail for real users.**
- **L10.** Dead i18n keys (~180 defined-never-called in en.json) and orphaned components — dead-weight hygiene, some likely reachable via dynamic `t()` composition (e.g., `climateTemplates.${source}`), so prune carefully.

---

## Verified clean (evidence attached)

| Area | Result |
|---|---|
| Admin auth | All 19 `/admin/*` routes → `require_admin`; **401** without token, **403** as regular user (both CSV exports included) — live |
| IDOR/ownership | Cross-user sim GET/PATCH/DELETE blocked; data verified intact; all queries `.eq("user_id")` — live |
| RLS | `profiles`, `user_roles`, `admin_audit_log`, `user_usage_limits`, `saved_*`, `chat_*`, `ml_model_registry` → `42501` to anon key; authed user sees only own profile — live |
| Self-elevation via `user_roles` | `POST user_roles {role:"admin"}` → `42501` denied — live |
| Auth checks | Missing/malformed token → 401; unconfirmed email → 403; `is_active` enforced — live + code |
| Route guards | `ProtectedRoute`/`AdminRoute` correct; `isAdmin` derived from backend `/protected/me`, not spoofable metadata — code |
| Validation | ecosim negatives/abc/0/1e308/savings>1 → 422; label bounds → 422; session >10 KB → 413; `PUT /profile` whitelist + `extra=forbid` — live |
| CORS | Fake origin → rejected (no allow-origin); not wildcarded — live |
| Security headers | CSP (`script-src 'self'`), nosniff, DENY, HSTS, Referrer-Policy, 1 MB body limit — live |
| Rate limiting | 60/min global, 10/min admin/protected writes, Redis sliding window + in-memory merge, direct-peer-IP (XFF-spoof-safe); **localhost exempt** — code-verified (can't trigger locally) |
| Anon quotas | EcoSim/EnergyHub LLM paths quota-gated for anon (`use_llm` defaults static); localhost-exempt, IP-keyed — live + code |
| XSS sinks | No `dangerouslySetInnerHTML` anywhere; react-markdown default-escaped in one shared wrapper — code |
| Secrets in bundle | `dist/` grep-clean; publishable key only — live build |
| Committed secrets | None — `.env` files gitignored; `client_secret_*.json` does not exist — verified |
| Nav links | All `to=`/`navigate()` targets resolve to real routes; `*` → NotFound — code |
| Tests/build | 38/38 frontend, 112/112 backend, `vite build` clean — live |

## Not tested (explicit limits)

- **Browser-visual verification** (no automation available): actual click-through UX, mobile rendering, error toasts, PDF download, EnergyHub map rendering — statically reviewed only; **recommend a manual pass**.
- Rate-limit trigger behavior (localhost exempt by design); production Vercel/CORS interplay.
- Email delivery end-to-end (reset/confirm) — see L9.
- MFA enrollment end-to-end; Google OAuth round-trip.
- Sustained load beyond a 75-request burst; multi-tab/concurrent-edit UX.
- EcoSim simulation math correctness (inputs validated; scoring logic not audited for correctness).
- `use_llm` AI-generation paths (quota-gated but not exercised to conserve API quota).

## Recommended fix order

1. **C1** — column-restrict profiles RLS (or trigger) → re-run the PostgREST escalation probe.
2. **H1** — cascade/SET-NULL migration → verify `DELETE /protected/me` works for a user with sims.
3. **H3** — code-split the bundle.
4. **H2** — fill missing i18n keys + add the locale-lint CI check.
5. **M1** — strip server secrets from `react-frontend/.env`. **M3** — cache invalidation on admin writes. **L9** — confirm Supabase SMTP.
6. Then the medium/low tail (M2 404s, M4 tables, M5 dead routers, M6 CORS).

---

## Launch checklist (from this audit)

- [ ] **Custom SMTP verified in the Supabase dashboard** (Authentication → SMTP). The default Supabase email sender allows only a few emails/hour — it tripped `over_email_send_rate_limit` during this audit and will break signups, confirmations, and password resets at launch volume. Maileroo credentials already exist in the root `.env`; they must also be configured in the Supabase dashboard (separate from app env).
- [ ] **`supabase/migrations/0024_audit_fixes.sql` applied** before launch — it carries the C1 column-grant and H1 cascade fixes; the app-side fixes below assume it is in place.
- [ ] **CORS**: `ENVIRONMENT=production` is set on the backend so localhost origins are dropped from the allow-regex (Vercel preview origins remain allowed).
- [ ] Re-run the direct PostgREST probes (`PATCH profiles {"plan":"premium"}`, `{"is_active":true}`) with a regular-user JWT — both must be denied after the migration.
