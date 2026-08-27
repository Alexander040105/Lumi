# LUMI Auth & Profile Changes — Implementation & Deployment Guide

This guide covers the auth/profile hardening and admin improvements that were implemented on the current branch, plus the Supabase/Vercel steps you need to run to make them live.

## What was changed (code)

These commits are on `development3` and have not been pushed:

- `b97b35c` — Enforce `is_active` on every verified request
- `e3932f8` — Protect against self-lockout and last-admin demotion
- `fa36ce4` — Apply a stricter rate limit to auth/admin/protected writes
- `ea828fe` — Add `is_admin()` migration to include `dev` role in RLS
- `f386c31` — Cap `store_session` TTL and payload size
- `59be4e4` — Add Pydantic validation and caps to protected write endpoints
- `f33fcab` — Paginate `/admin/users` with backend search and filters
- `22135e7` — Allow admins to edit any user's profile fields

The relevant files are:

- `fastapi-backend/app/dependencies/auth.py`
- `fastapi-backend/app/middleware/rate_limit.py`
- `fastapi-backend/app/routes/admin.py`
- `fastapi-backend/app/routes/protected.py`
- `react-frontend/src/pages/admin/AdminUsers.jsx`
- `react-frontend/src/components/admin/UserDetailDrawer.jsx`
- `supabase/migrations/0013_fix_is_admin_dev.sql`
- `supabase/migrations/0014_admin_users_list.sql`

## Supabase / DB steps (do these first)

### 1. Apply the two new migrations

Run the whole migration set so `0009`, `0011`, `0012`, `0013`, and `0014` are applied in order:

```bash
supabase db push
```

If you do not use the CLI, open **Supabase Dashboard → SQL Editor** and run the SQL in these files, in order:

1. `supabase/migrations/0013_fix_is_admin_dev.sql`
2. `supabase/migrations/0014_admin_users_list.sql`

### 2. Verify `is_admin()` includes `dev`

Run this in the SQL Editor:

```sql
SELECT pg_get_functiondef('public.is_admin'::regprocedure);
```

You should see:

```sql
WHERE user_id = auth.uid() AND role IN ('admin', 'dev')
```

If it still says `AND role = 'admin'`, the `0013` migration did not apply correctly.

### 3. Verify the new RPC is callable

```sql
GRANT EXECUTE ON FUNCTION public.get_admin_users_list(integer, integer, text, text, text, boolean) TO service_role;
GRANT EXECUTE ON FUNCTION public.get_admin_usage_summary(integer, integer, text) TO service_role;
GRANT EXECUTE ON FUNCTION public.is_admin() TO authenticated;
```

The migration already contains these, but run the commands if you get `permission denied for function` when hitting `/admin/users` or `/admin/usage`.

### 4. Make sure the backend uses the service-role key

The FastAPI admin endpoints rely on a Supabase service-role key. In `.env` or Vercel environment variables, set **one** of:

```
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SERVICE_ROLE_KEY=eyJ...
```

Do **not** use the anon key. Without the service-role key, `get_admin_users_list`, `get_admin_usage_summary`, and `admin_audit_log` inserts will fail.

## Vercel / deployment steps

### 1. Fix `vercel.json` max duration for Hobby

Your `vercel.json` currently has:

```json
"maxDuration": 60
```

Vercel Hobby only allows 10 seconds. Change it to:

```json
"maxDuration": 10
```

### 2. Set the production API and Supabase URLs

In the Vercel dashboard for the frontend, set:

```
VITE_API_BASE_URL=https://<your-fastapi-vercel-app>/api/v1
VITE_SUPABASE_URL=https://<your-project>.supabase.co
VITE_SUPABASE_ANON_KEY=<your-anon-key>
```

### 3. Build and deploy

Frontend:

```bash
cd react-frontend
npm ci
npm run build
```

Backend (Vercel handles this on `git push`, or locally):

```bash
vercel --prod
```

## Supabase Auth email templates

The HTML templates in `templates/email/` are not applied automatically. Copy the relevant ones into **Supabase Dashboard → Auth → Templates**:

- `confirm-signup.html`
- `reset-password.html`
- `change-email.html`
- `reauthentication.html`

### Redirect URLs

In **Supabase Dashboard → Authentication → URL Configuration**, set:

- Site URL: `https://<your-frontend-vercel-app>/`
- Redirect URLs: add `https://<your-frontend-vercel-app>/reset-password`

The reset password flow sends the user to `https://<your-frontend-vercel-app>/reset-password`.

## Smoke-test checklist

After deployment, run through this in order:

1. Sign up a new user with email/password.
2. Confirm the email and log in.
3. Edit your profile from `/dashboard` or `/profile`.
4. Upload an avatar and confirm it saves.
5. Enable MFA from `/mfa`.
6. Log out, then log in with the MFA code.
7. As an admin, open `/admin/users`.
   - Confirm pagination, search, role/plan/status filters work.
   - Confirm the list does not time out.
8. Click a user, then click **Edit** in the drawer and change `full_name`/`organization`/`location`.
9. Ban a test user, then try to call a protected endpoint with that user's token. It should return `403 Account suspended`.
10. Try to demote the only admin to `user`. It should fail with `Cannot remove the last admin/dev account`.
11. Confirm `/protected/session` rejects a TTL greater than 86,400 seconds or a payload larger than 10 KB.

## Vercel free-tier reminders

- All admin user operations now hit a single Supabase RPC per page, so they stay under the 10 s limit.
- The tighter rate limit (10 non-GET requests per minute on `/api/v1/admin/*` and `/api/v1/protected/*`) is intentional for Hobby.
- Avatar uploads are still limited to 2 MB on the client/schema side.
- Redis/Upstash is required; the existing `NullRedis` fallback is only for brief outages.

## What is NOT yet implemented

These items from the original plan are still pending. You can tackle them next in any order:

- **Task 5** — `/settings/security` page for logged-in users to change password and email.
- **Task 6** — MFA backup codes and a re-authentication gate before disabling MFA.
- **Task 7** — Admin force logout and force password reset.
- **Task 9** — Unify profile editing path between `/dashboard` and `/profile`.
- **Task 12** — Wire the custom email templates and production redirects in Supabase.
- **Task 13** — Enforce `user_usage_limits` against `simulations_this_month` and `chat_messages_this_month`.
- **Task 15** — Use local JWT verification for read-only dependencies.
- **Task 16** — Self-service account deactivation/deletion page.
- **Task 17** — View active sessions and revoke other devices.

## Rollback plan

If anything breaks in production:

1. Revert the latest commits:
   ```bash
   git revert HEAD~0
   ```
   or `git reset --hard <last-good-commit>` if you have not pushed.
2. Re-run `supabase db push` if you rolled back any `.sql` migration.
3. Redeploy the FastAPI function and the Vite frontend.

## Support / next steps

If the admin user list fails with a function error, the most likely causes are:

- `0014_admin_users_list.sql` not applied.
- `GRANT EXECUTE` missing on `get_admin_users_list`.
- The backend is not using the service-role key.

For `403 Account suspended` not working, the issue is almost always that `is_active` is `false` but `profiles` was not created, or the `is_active` cache was not invalidated after a ban (this should happen automatically after the `ea828fe` commit).
