# Supabase Auth + Redis Guide (Lumi)

This guide covers email/password auth, Google OAuth, MFA (TOTP), reset password flow, and Redis-backed session storage for FastAPI.

## 1) Supabase dashboard (development)

1. Create or open your Supabase project.
2. Auth -> Providers:
   - Enable Email.
   - Enable Google.
3. Google OAuth settings:
   - Add Client ID + Client Secret.
   - Redirect URI:
     https://`<your-project-ref>`.supabase.co/auth/v1/callback
4. Auth -> URL Configuration:
   - Site URL: http://localhost:5173
   - Redirect URLs:
     - http://localhost:5173
     - http://localhost:5173/login
     - http://localhost:5173/reset-password
5. Auth -> Email Templates:
   - Ensure Confirm Signup and Reset Password are enabled.
   - Use redirect URL for Reset Password: http://localhost:5173/reset-password
6. Auth -> MFA:
   - Enable TOTP.
   - Keep MFA optional while testing.

## 2) Frontend environment variables

Set these in react-frontend/.env.local (do not commit):

VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_API_BASE_URL=http://localhost:8000/api/v1

React uses these helpers:

- [react-frontend/src/utils/env.js](react-frontend/src/utils/env.js)

## 3) Frontend auth flow

### Email and password

The auth context now supports:

- signInWithPassword
- signUp
- resetPassword
- updatePassword

Implementation:

- [react-frontend/src/context/AuthContext.jsx](react-frontend/src/context/AuthContext.jsx)
- [react-frontend/src/pages/Login.jsx](react-frontend/src/pages/Login.jsx)

How to test:

1. Open http://localhost:5173/login
2. Sign up with email/password.
3. Confirm the email (Supabase sends it).
4. Sign in with email/password.

### Reset password

1. On the login page, click "Forgot password".
2. Enter email -> Supabase sends reset link.
3. Open the link, which lands on /reset-password.
4. Set a new password.

Reset page:

- [react-frontend/src/pages/ResetPassword.jsx](react-frontend/src/pages/ResetPassword.jsx)

### Google OAuth

1. Click "Continue with Google" on the login page.
2. Complete Google consent.
3. You should be redirected back with a session.

## 4) MFA (TOTP)

This UI lives on the dashboard:

- [react-frontend/src/pages/Dashboard.jsx](react-frontend/src/pages/Dashboard.jsx)

How to use:

1. Sign in.
2. Go to /dashboard.
3. Click "Enroll TOTP".
4. Scan the QR code with an authenticator app.
5. Enter the 6-digit code and click "Verify code".

If you need to require MFA for all users later, set it in Supabase Auth -> MFA.

## 5) FastAPI auth verification

FastAPI validates Supabase access tokens via the JWT secret:

- [fastapi-backend/app/auth/jwt.py](fastapi-backend/app/auth/jwt.py)
- [fastapi-backend/app/dependencies/auth.py](fastapi-backend/app/dependencies/auth.py)

Make sure .env in fastapi-backend includes:

SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_JWT_SECRET=

## 6) Redis setup

### Option A: Local Redis (recommended for dev)

If you have Docker:

- docker run -p 6379:6379 redis:7

### Option B: Upstash Redis (managed)

Use the provided Redis URL.

### Backend dependency

Install:

- redis==5.0.8

### Backend env variable

Set in fastapi-backend/.env:

REDIS_URL=redis://localhost:6379/0

### Redis client helper

- [fastapi-backend/app/services/redis_client.py](fastapi-backend/app/services/redis_client.py)

## 7) Session storage endpoint

An authenticated example endpoint stores a JSON payload in Redis:

- [fastapi-backend/app/routes/protected.py](fastapi-backend/app/routes/protected.py)

Example request:

POST http://localhost:8000/api/v1/protected/session
Authorization: Bearer <SUPABASE_ACCESS_TOKEN>

Body:
{
  "lastPage": "/dashboard",
  "prefs": { "theme": "dark" }
}

## 8) Production checklist

- Update Supabase Site URL + Redirect URLs for your production domain.
- Set VITE_* variables in your hosting provider.
- Use a managed Redis provider in production.
- Lock down service role keys to backend only.
