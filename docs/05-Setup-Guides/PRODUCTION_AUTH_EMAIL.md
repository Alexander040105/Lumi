# Production Auth & Email Checklist

Settings and expected behaviors for LUMI's Supabase-backed authentication in
production. Audit basis: `main/PRODUCTION` project (`husnkzlccdjpwlqcfbv`),
October 2026. Keep this in sync when auth settings change — most "email didn't
send" incidents are config drift, not code bugs.

## Expected behaviors (so nobody re-reports them as bugs)

| Behavior | Why it happens |
|---|---|
| Signup with an **already-registered** email shows "account already exists" and sends **no email** | Supabase anti-enumeration: `signUp` returns a fake user with empty `identities`, no session, and no confirmation email so attackers can't probe which emails are registered. Detected in `AuthContext.signUp` (`accountExists`) and shown in `Login.jsx`. |
| Email+password signup, then Google sign-in with the **same** email logs in "as Google" | Supabase identity linking: a provider-verified email matching an existing `auth.users` row becomes a second identity **on the same `user.id`** — same account, same profile, two sign-in methods. The `handle_new_user` trigger (`supabase/table_scripts/auth_admin_schema.sql`) creates profile/role once with `on conflict do nothing`. |
| Google sign-up gets **no** confirmation email | By design: Google-verified emails set `email_confirmed_at` automatically. The backend accepts them because `get_verified_user` (`fastapi-backend/app/dependencies/auth.py`) only checks that flag. |
| Email+password user can't call protected APIs before confirming | Intended: `get_verified_user` returns 403 "Email address not verified" until `email_confirmed_at` is set. |

## Supabase Dashboard checklist (production project)

- [x] **Authentication → Emails → Enable custom SMTP = ON** — Maileroo
  (`smtp.maileroo.com:587`), sender `lumi@<subdomain>.maileroo.org`, name
  "LUMI". *The built-in mailer is dev-only and silently drops mail past
  ~2–4/hour — this was the root cause of the missing confirmation emails.*
- [ ] **Authentication → Sign In/Providers → Email → "Confirm email" = ON**
  — if off, signups auto-confirm and no email is ever sent.
- [ ] **Authentication → URL Configuration:**
  - Site URL = production frontend domain
  - Redirect URLs allowlist includes:
    `https://<prod-domain>/auth/callback` (confirm + OAuth + reset all land
    here — code sends `emailRedirectTo`/`redirectTo` to this path from
    `AuthContext.jsx`), plus `http://localhost:*/**` for dev.
    *An unlisted `emailRedirectTo` makes Supabase reject or misroute the link.*
- [ ] **Google provider = ON** and
  `https://husnkzlccdjpwlqcfbv.supabase.co/auth/v1/callback` is registered in
  Google Cloud Console (matches `SUPABASE_OAUTH_CALLBACK_URL` in `.env`).
- [ ] **Deliverability:** the `*.maileroo.org` shared sender domain can land in
  spam — check spam on first tests; verify a custom sending domain with
  DKIM/SPF inside Maileroo for production grade.
- [ ] **After each test:** Logs → Auth — `user_signedup`, email-sent events,
  and any SMTP handshake errors surface here first.

## Verification matrix

| # | Scenario | Expected |
|---|---|---|
| T1 | New email + password signup | Check-email box; email arrives; link → `/auth/callback` → dashboard; `/protected/me` 200 |
| T2 | Same email + password signup again | "Account already exists" notice; **no email sent** |
| T3 | Google sign-in with T1's email | Same `user.id`; Dashboard → Users shows one user, two identities |
| T4 | Google sign-up, fresh account | Instant login, no email needed |
| T5 | Resend on the check-email box | `auth.resend type=signup` succeeds; second email arrives |
| T6 | Forgot password | Reset email arrives; `/auth/callback` → `/reset-password` completes |
| T7 | Unconfirmed user calls a protected API | 403 "Email address not verified" |

## If emails still don't arrive

1. Logs → Auth on the project — SMTP handshake/credential errors appear here.
2. Maileroo dashboard — sending logs show whether Supabase handed the mail off
   and whether the recipient's server accepted it.
3. Only then suspect code — the frontend path (`AuthContext.signUp` →
   `confirmationRequired` → check-email UI + resend) is verified correct.
