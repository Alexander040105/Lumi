# Production Auth & Email Checklist

Settings and expected behaviors for LUMI's Supabase-backed authentication in
production. Audit basis: `main/PRODUCTION` project (`husnkzlccdrjpwlqcfbt`),
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

- [x] **Authentication → Emails → Enable custom SMTP = ON** — **Gmail**
  (`smtp.gmail.com:587`), username = sender = `lumi.dev404@gmail.com`,
  password = the 16-character Google app password (requires 2-Step
  Verification on that Google account; generate at
  myaccount.google.com/apppasswords), sender name "LUMI". *The built-in
  mailer is dev-only and silently drops mail past ~2–4/hour — a `429` on
  `POST /auth/v1/resend` (`over_email_send_rate_limit`) in the 29 Oct Auth
  logs proved it was still active and caused the missing confirmation
  emails. Gmail is the chosen production path for the demo (free, no DNS
  needed, sends to any recipient); verified delivering on 29 Oct.*
- [ ] **Authentication → Rate Limits → emails per hour** — raise to ~60.
  *GoTrue's own cap is independent of the SMTP provider and caused the
  observed `429` — it still throttles bursts even with Gmail configured.
  Gmail itself allows ~500/day, far above demo volume.*
- [x] **Authentication → Sign In/Providers → Email → "Confirm email" = ON**
  — if off, signups auto-confirm and no email is ever sent. *Verified on via
  a completed `type=signup` verify event (`303`) in the 29 Oct Auth logs.*
- [ ] **Authentication → URL Configuration:**
  - Site URL = production frontend domain
  - Redirect URLs allowlist includes:
    `https://<prod-domain>/auth/callback` (confirm + OAuth + reset all land
    here — code sends `emailRedirectTo`/`redirectTo` to this path from
    `AuthContext.jsx`), plus `http://localhost:*/**` for dev.
    *An unlisted `emailRedirectTo` makes Supabase reject or misroute the link.*
- [ ] **Google provider = ON** and
  `https://husnkzlccdrjpwlqcfbt.supabase.co/auth/v1/callback` is registered in
  Google Cloud Console (matches `SUPABASE_OAUTH_CALLBACK_URL` in `.env`).
- [x] **Deliverability:** a `gmail.com` sender auto-passes DKIM/SPF, but a
  new account has no sending reputation — some recipients' filters score the
  first emails as spam (expected; instruct demo users to check spam, and the
  confirmation copy already says so). Testing trick: `+alias` addresses
  (`lumi.dev404+testN@gmail.com`) all deliver to the same inbox. *A branded
  `noreply@domain` sender needs a verified sending domain (Resend/Maileroo +
  DKIM/SPF) — requires buying a domain; documented as the future upgrade,
  out of scope for the demo.*
- [ ] **After each test:** Logs → Auth — `user_signedup`, email-sent events,
  and any SMTP handshake errors surface here first.

## Verification matrix

| # | Scenario | Expected |
|---|---|---|
| T1 | New email + password signup | Check-email box; email arrives (**check spam on first send**); link → `/auth/callback` → dashboard; `/protected/me` 200 |
| T2 | Same email + password signup again | "Account already exists" notice; **no email sent** |
| T3 | Google sign-in with T1's email | Same `user.id`; Dashboard → Users shows one user, two identities |
| T4 | Google sign-up, fresh account | Instant login, no email needed |
| T5 | Resend on the check-email box | `auth.resend type=signup` succeeds; second email arrives (spam check applies) |
| T6 | Forgot password | Reset email arrives; `/auth/callback` → `/reset-password` completes |
| T7 | Unconfirmed user calls a protected API | 403 "Email address not verified" |

## If emails still don't arrive

1. Logs → Auth on the project — SMTP handshake/credential errors and `429`
   rate-limit rejections appear here.
2. If the log shows an SMTP auth failure — the app password is wrong,
   expired, or Google blocked the sign-in; check
   myaccount.google.com/security for blocked attempts and regenerate the
   app password.
3. Check the recipient's spam folder — a `gmail.com` sender lands there on
   first contact for stricter filters.
4. Only then suspect code — the frontend path (`AuthContext.signUp` →
   `confirmationRequired` → check-email UI + resend) is verified correct.
