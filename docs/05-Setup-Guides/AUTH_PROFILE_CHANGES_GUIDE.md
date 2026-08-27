# LUMI Auth & Profile Changes — Implementation & Deployment Guide

This guide covers the auth/profile hardening and admin improvements that were implemented on the current branch, plus the Supabase/Vercel steps you need to run to make them live.

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
docs/05-Setup-Guides/AUTH_PROFILE_CHANGES_GUIDE.md
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

## 4. Vercel / deployment steps

### 4.1 `vercel.json` max duration

Vercel Hobby only allows 10 seconds. Change:

```json
"maxDuration": 10
```

### 4.2 Frontend environment

```
VITE_API_BASE_URL=https://<your-fastapi-vercel-app>/api/v1
VITE_SUPABASE_URL=https://<your-project>.supabase.co
VITE_SUPABASE_ANON_KEY=<your-anon-key>
```

### 4.3 Build commands

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

## 5. Supabase Auth email templates and redirects

### 5.1 Upload the templates

The templates are in `templates/email/`. Copy the relevant HTML into **Supabase Dashboard → Auth → Templates**:

- `confirm-signup.html`
- `reset-password.html`
- `change-email.html`
- `reauthentication.html`

### 5.2 Set the redirect URL

In **Supabase Dashboard → Authentication → URL Configuration**:

- Site URL: `https://<your-frontend-vercel-app>/`
- Redirect URLs: add `https://<your-frontend-vercel-app>/reset-password`

This is required for the reset-password and change-email flows to return to the correct Vercel frontend.

## 6. Smoke-test checklist

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

## 7. Configuration / tuning

The usage limits are in `fastapi-backend/app/config/settings.py`:

```python
free_simulation_limit: int = 5
premium_simulation_limit: int = 1000
free_chat_message_limit: int = 20
premium_chat_message_limit: int = 5000
```

Admins and devs are unlimited. Adjust these values before going live.

## 8. Known limitations and next steps

- **Force logout:** Supabase GoTrue does not expose an admin "sign out by user ID" API in the Python client. The existing **Ban** action is the correct way to revoke access. Force password reset is implemented.
- **Email templates (Task 12):** still needs to be copied into the Supabase dashboard and the redirect URL set.
- **Local JWT validation (Task 15):** implemented in `get_verified_user_optional` for read-only paths. Set `SUPABASE_JWT_SECRET` to enable it; the dependency falls back to `supabase.auth.get_user` if the secret is not configured.
- **Active sessions (Task 17):** not implemented. Supabase does not expose an admin "list sessions" API by user ID in `supabase-py`. You would need to track sessions in a new `public.user_sessions` table or use the GoTrue REST API directly.

## 9. Rollback

If anything breaks:

1. Revert the affected commits locally or reset to the previous known-good state.
2. Re-run `supabase db push` if you rolled back any `.sql` migration.
3. Redeploy the FastAPI function and Vite frontend.

## 10. If something fails

- `/admin/users` empty or permission error → migration `0014` not applied, or `GRANT EXECUTE` missing, or the backend is using the anon key.
- `403 Account suspended` not working → `is_active` is `false` but `0013` not applied, or the Redis `lumi:auth:{id}:active` cache was stale (it now invalidates on ban/delete/role/plan changes).
- Password reset not sending → check `SUPABASE_SERVICE_ROLE_KEY` and the redirect URL in Supabase.
- EcoSim 429 for free users → `user_usage_limits` table must be populated (it is created by the sign-up trigger for new users; existing users may need a row inserted).
