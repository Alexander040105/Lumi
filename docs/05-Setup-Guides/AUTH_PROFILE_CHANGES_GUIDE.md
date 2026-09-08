# LUMI Auth, EcoSim & Recent Changes — Implementation & Deployment Guide

This guide covers the auth/profile hardening, EcoSim error hardening, and renewable-energy scaling changes that were implemented on the current branch, plus the Supabase/Vercel steps you need to run to make them live.

> **Important:** I did not push or commit the latest files after the initial commits. You should review the working tree and commit/push when you are ready.

## 1. What was changed (code)

Implemented tasks from the approved plan:

1. **Enforce `is_active` on every verified request**
   - `fastapi-backend/app/dependencies/auth.py`
2. **Prevent self-lockout / last-admin demotion**
   - `fastapi-backend/app/routes/admin.py`
3. **Stricter rate limiting for auth/admin/protected writes**
   - `fastapi-backend/app/middleware/rate_limit.py`
4. **Fix `is_admin()` RLS to include `dev` role**
   - `supabase/migrations/0013_fix_is_admin_dev.sql`
5. **Cap `store_session` TTL and payload size**
   - `fastapi-backend/app/routes/protected.py`
6. **Pydantic validation on protected/admin writes**
   - `fastapi-backend/app/routes/protected.py` (`ProfileUpdatePayload`)
7. **Paginate `/admin/users` with backend search and filters**
   - `supabase/migrations/0014_admin_users_list.sql`
   - `fastapi-backend/app/routes/admin.py`
   - `react-frontend/src/pages/admin/AdminUsers.jsx`
8. **Admin edit of any user profile**
   - `fastapi-backend/app/routes/admin.py`
   - `react-frontend/src/components/admin/UserDetailDrawer.jsx`
9. **Security settings page (change email / password)**
   - `react-frontend/src/pages/SecuritySettings.jsx`
   - `react-frontend/src/routes/AppRoutes.jsx`
   - `react-frontend/src/components/layout/Navbar.jsx`
10. **MFA re-authentication before unenrollment**
    - `react-frontend/src/pages/MFASetup.jsx`
11. **Admin force password reset**
    - `fastapi-backend/app/routes/admin.py` (`POST /admin/users/{id}/force-password-reset`)
    - `react-frontend/src/components/admin/UserDetailDrawer.jsx`
12. **Unify profile editing path (Dashboard → backend)**
    - `react-frontend/src/pages/Dashboard.jsx`
13. **Enforce `user_usage_limits` for simulations and chat**
    - `fastapi-backend/app/config/settings.py`
    - `fastapi-backend/app/dependencies/quota.py`
    - `fastapi-backend/app/routes/ecosim.py`
    - `fastapi-backend/app/routes/chat.py`
14. **Self-service account deletion**
    - `fastapi-backend/app/routes/protected.py` (`DELETE /protected/me`)
    - `react-frontend/src/pages/SecuritySettings.jsx`
15. **Local JWT validation for read-only dependencies**
    - `fastapi-backend/app/dependencies/auth.py`

### Not yet implemented

These remain on the plan and are described in the **Next steps** section:

- **Task 12** — Wire Supabase email templates and production redirects (dashboard/configuration step).
- **Task 17** — View active sessions (requires a `user_sessions` table and Supabase session introspection).

## 2. Files you need to commit

```
fastapi-backend/app/config/settings.py
fastapi-backend/app/dependencies/auth.py
fastapi-backend/app/dependencies/quota.py
fastapi-backend/app/middleware/rate_limit.py
fastapi-backend/app/routes/admin.py
fastapi-backend/app/routes/chat.py
fastapi-backend/app/routes/ecosim.py
fastapi-backend/app/routes/protected.py
react-frontend/src/components/admin/UserDetailDrawer.jsx
react-frontend/src/components/layout/Navbar.jsx
react-frontend/src/pages/SecuritySettings.jsx
react-frontend/src/pages/MFASetup.jsx
react-frontend/src/pages/Dashboard.jsx
react-frontend/src/routes/AppRoutes.jsx
supabase/migrations/0013_fix_is_admin_dev.sql
supabase/migrations/0014_admin_users_list.sql
supabase/migrations/0019_ecosim_explanations.sql
supabase/migrations/0020_clear_ai_insights_cache.sql
supabase/migrations/0021_add_saved_simulation_mode.sql
fastapi-backend/app/services/ecosim.py
fastapi-backend/app/services/gemini_funcs.py
fastapi-backend/app/services/solar_output_calc.py
fastapi-backend/app/services/wind_output_calc.py
fastapi-backend/app/services/atlas_data.py
fastapi-backend/app/services/apiClient.js
react-frontend/src/pages/Ecosim.jsx
react-frontend/src/services/apiClient.js
react-frontend/src/components/ecosim/EcosimResults.jsx
docs/05-Setup-Guides/AUTH_PROFILE_CHANGES_GUIDE.md
docs/05-Setup-Guides/ECOSIM_RENEWABLE_DATA_AUDIT.md
```

## 3. Supabase / DB steps

### 3.1 Apply the new migrations

Run the whole migration set in order:

```bash
supabase db push
```

If you are not using the CLI, run these files in the SQL Editor in order:

1. `supabase/migrations/0013_fix_is_admin_dev.sql`
2. `supabase/migrations/0014_admin_users_list.sql`

### 3.2 Verify `is_admin()` includes `dev`

```sql
SELECT pg_get_functiondef('public.is_admin'::regprocedure);
```

You should see:

```sql
WHERE user_id = auth.uid() AND role IN ('admin', 'dev')
```

### 3.3 Verify RPC grants

```sql
GRANT EXECUTE ON FUNCTION public.get_admin_users_list(integer, integer, text, text, text, boolean) TO service_role;
GRANT EXECUTE ON FUNCTION public.get_admin_usage_summary(integer, integer, text) TO service_role;
GRANT EXECUTE ON FUNCTION public.is_admin() TO authenticated;
```

### 3.4 Service-role key

The FastAPI admin endpoints now rely on `get_admin_users_list`, `get_admin_usage_summary`, and `admin_audit_log` insertion. Make sure the backend environment has a real Supabase **service-role** key, not the anon key:

```
SUPABASE_SERVICE_ROLE_KEY=eyJ...
# or
SUPABASE_JWT_SERVICE_ROLE_KEY=eyJ...
```

## 4. EcoSim scaling & error hardening

### 4.1 What changed

1. **Dev-time quota/rate-limit bypass**
   - `fastapi-backend/app/dependencies/quota.py`
   - `fastapi-backend/app/middleware/rate_limit.py`
   - Local requests from `127.0.0.1`, `::1`, `localhost`, or `0.0.0.0` no longer consume the anonymous quota and are not rate-limited.
2. **Better EcoSim 404/422 error messages**
   - `fastapi-backend/app/services/ecosim.py`
3. **Prevent duplicate `onRun` submissions**
   - `react-frontend/src/pages/Ecosim.jsx`
4. **Improved API error handling**
   - `react-frontend/src/services/apiClient.js` (`ApiError` with `status`)
5. **Province-mode save simulations**
   - `fastapi-backend/app/routes/simulations.py`
   - `react-frontend/src/pages/Ecosim.jsx`
6. **AI province-mode guard**
   - `fastapi-backend/app/services/gemini_funcs.py`
   - `fastapi-backend/app/services/ecosim.py`
7. **Wind uses 10 m hub height**
   - `fastapi-backend/app/services/ecosim.py`
   - `fastapi-backend/app/config/settings.py` (`household_solar_size_kwp`)
   - `fastapi-backend/app/services/ecosim.py` now picks `wind_speed_10m_ms` first.
   - The `assumptions` block reports `wind_speed_height_m: 10` and `wind_speed_mps`.
8. **Solar advanced model & realistic home size**
   - `fastapi-backend/app/services/ecosim.py` now uses `solar_calc_advanced` when DNI/DHI are in `municipality_atlas_averages`.
   - Default home array is now `household_solar_size_kwp` (3.0 kWp) instead of a hard-coded 0.8 kWp.

### 4.2 Migrations to apply

In addition to `0013` and `0014` from the auth work, run:

- `supabase/migrations/0019_ecosim_explanations.sql`
- `supabase/migrations/0020_clear_ai_insights_cache.sql`
- `supabase/migrations/0021_add_saved_simulation_mode.sql`
- `0022_add_wind_speed_10m_ms_to_municipality_atlas.sql` (if you add the column — not yet created)

### 4.3 Data to load

- `municipality_atlas_averages.wind_speed_10m_ms` should be populated from `fastapi-backend/app/services/local_data/municipality_atlas_averages.csv` or from sampling `data/newDataPointsToExtract/GlobalWindAtlas_PHL_wind-speed_10m.tif`.
- For a full renewable data audit and the free datasets that can improve solar, hydro, and geothermal, see:
  - `docs/05-Setup-Guides/ECOSIM_RENEWABLE_DATA_AUDIT.md`

## 5. Vercel / deployment steps

### 5.1 `vercel.json` max duration

Vercel Hobby only allows 10 seconds. Change:

```json
"maxDuration": 10
```

### 5.2 Frontend environment

```
VITE_API_BASE_URL=https://<your-fastapi-vercel-app>/api/v1
VITE_SUPABASE_URL=https://<your-project>.supabase.co
VITE_SUPABASE_ANON_KEY=<your-anon-key>
```

### 5.3 Build commands

Frontend:

```bash
cd react-frontend
npm ci
npm run build
```

Backend (handled by Vercel on `git push`, or deploy manually):

```bash
vercel --prod
```

## 6. Supabase Auth email templates and redirects

### 6.1 Upload the templates

The templates are in `templates/email/`. Copy the relevant HTML into **Supabase Dashboard → Auth → Templates**:

- `confirm-signup.html`
- `reset-password.html`
- `change-email.html`
- `reauthentication.html`

### 6.2 Set the redirect URL

In **Supabase Dashboard → Authentication → URL Configuration**:

- Site URL: `https://<your-frontend-vercel-app>/`
- Redirect URLs: add `https://<your-frontend-vercel-app>/reset-password`

This is required for the reset-password and change-email flows to return to the correct Vercel frontend.

## 7. Smoke-test checklist

1. Sign up and confirm email.
2. Log in and go to `/settings/security`.
3. Change email (check new inbox for confirmation) and password.
4. From `/dashboard`, edit `full_name`, `organization`, `location`, and upload an avatar — save via the backend.
5. Enable MFA from `/mfa`, then try to disable it (requires current TOTP code).
6. As an admin, open `/admin/users` and confirm pagination, search, role/plan/status filters work without timeout.
7. Click a user, edit their profile, and click **Force reset password** to send a reset email.
8. Try to ban a user, then call a protected endpoint with their token — should get `403 Account suspended`.
9. Try to demote the only admin to `user` — should fail with `Cannot remove the last admin/dev account`.
10. Trigger more than `free_simulation_limit` EcoSim calculations with a free user — should get `429 Monthly simulation limit reached`.
11. Send more than `free_chat_message_limit` chat messages — should get `429 Monthly chat_message limit reached`.
12. Test self-service account deletion from `/settings/security`.
13. EcoSim: run a **province** simulation and confirm the Geothermal card and AI text are hidden.
14. EcoSim: run a **municipality** simulation and confirm the recommendation is no longer always Wind or always Solar.
15. EcoSim: save a province-mode simulation and verify `mode` and `province_id` are stored.
16. EcoSim: check that repeated local dev requests do not produce `401` or `429`.

## 8. Configuration / tuning

The usage limits are in `fastapi-backend/app/config/settings.py`:

```python
free_simulation_limit: int = 5
premium_simulation_limit: int = 1000
free_chat_message_limit: int = 20
premium_chat_message_limit: int = 5000

# Residential solar array size for EcoSim
echo HOUSEHOLD_SOLAR_SIZE_KWP=1.25 >> fastapi-backend/.env
```

Admins and devs are unlimited. Adjust these values before going live. EcoSim recommendation logic now caps usable output at the user's monthly consumption and uses the source `suitability_score` as a tie-breaker, so the best natural resource wins.

## 9. Known limitations and next steps

- **Force logout:** Supabase GoTrue does not expose an admin "sign out by user ID" API in the Python client. The existing **Ban** action is the correct way to revoke access. Force password reset is implemented.
- **Email templates (Task 12):** still needs to be copied into the Supabase dashboard and the redirect URL set.
- **Local JWT validation (Task 15):** implemented in `get_verified_user_optional` for read-only paths. Set `SUPABASE_JWT_SECRET` to enable it; the dependency falls back to `supabase.auth.get_user` if the secret is not configured.
- **Active sessions (Task 17):** not implemented. Supabase does not expose an admin "list sessions" API by user ID in `supabase-py`. You would need to track sessions in a new `public.user_sessions` table or use the GoTrue REST API directly.

### 9.1 AI output sanitization

All LLM-generated text that reaches the UI passes through `fastapi-backend/app/services/llm_sanitizer.py`:

- **`strip_thinking_blocks`** removes `<think>...</think>` and `<reasoning>...</reasoning>` chain-of-thought blocks (both literal and HTML-escaped `&lt;think&gt;` forms). Unclosed opening tags cause everything from the tag to end-of-text to be discarded, since there is no safe way to know where an unclosed thinking block ends.
- **`decode_html_entities`** converts `&lt;`, `&gt;`, `&amp;` etc. to literal characters via `html.unescape`.
- **`strip_html_tags`** removes any remaining `<...>` tag (e.g. `<ol>`, `<ul>`, `<p>`, `<em>`, `<strong>`) while preserving the text content inside.
- Both `sanitize_llm_output()` and `clean_ai_output()` run the full pipeline: thinking blocks → markdown fences → JSON wrappers → key-value formatting → HTML entity decode → HTML tag strip → whitespace normalization.
- `llm_client.generate_response()` calls `clean_ai_output()` on every provider response when `clean=True` (the default).
- `gemini_funcs._build_renewable_analysis_result()` calls `sanitize_llm_output()` then `extract_prescriptive_recommendation()`.
- `rag_gemini_funcs.analyze_with_rag()` calls `clean_ai_output()` then `extract_prescriptive_recommendation()`.
- The frontend `Markdown.jsx` component uses `react-markdown` without `rehype-raw`, so any residual HTML tags are rendered as escaped text rather than interpreted.
- **Cache residue:** Old cached EcoSim AI results in Redis/Supabase may still contain `<think>` tags. A forced re-run or cache TTL expiry will clear them; using `include_ai=true` with a new `municipality_id` bypasses the cache.
- **`household_solar_size_kwp` env variable:** Controls the residential solar array size used by EcoSim (default 3.0 kWp). Set via `HOUSEHOLD_SOLAR_SIZE_KWP` in `fastapi-backend/.env`. The computed `number_of_panels` is derived from this value and the panel wattage (400 W).

## 10. Rollback

If anything breaks:

1. Revert the affected commits locally or reset to the previous known-good state.
2. Re-run `supabase db push` if you rolled back any `.sql` migration.
3. Redeploy the FastAPI function and Vite frontend.

## 11. If something fails

- `/admin/users` empty or permission error → migration `0014` not applied, or `GRANT EXECUTE` missing, or the backend is using the anon key.
- `403 Account suspended` not working → `is_active` is `false` but `0013` not applied, or the Redis `lumi:auth:{id}:active` cache was stale (it now invalidates on ban/delete/role/plan changes).
- Password reset not sending → check `SUPABASE_SERVICE_ROLE_KEY` and the redirect URL in Supabase.
- EcoSim 429 for free users → `user_usage_limits` table must be populated (it is created by the sign-up trigger for new users; existing users may need a row inserted).
