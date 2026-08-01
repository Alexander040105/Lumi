# Supabase Guide

## Create a Supabase Project
1. Sign in to https://supabase.com
2. Create a new project
3. Wait for provisioning to complete

## Get API Keys
Project Settings -> API:
- Project URL -> SUPABASE_URL
- anon public key -> SUPABASE_ANON_KEY
- JWT secret -> SUPABASE_JWT_SECRET

## OAuth Providers
Authentication -> Providers:
- Enable Google, GitHub, or other providers
- Add redirect URL:
  - http://localhost:5173

## Frontend Connection
The React app uses the anon key to open OAuth sessions and manage the user session.

## Backend Connection
The FastAPI server uses the JWT secret to validate access tokens from Supabase.

## JWT Validation Flow
1. User logs in via Supabase OAuth
2. Supabase returns a session with access_token
3. React sends access_token in Authorization: Bearer header
4. FastAPI validates the token using SUPABASE_JWT_SECRET
5. Protected endpoints return data when the token is valid

## Security Notes
- Never expose SUPABASE_SERVICE_ROLE_KEY in the frontend
- Use SUPABASE_SERVICE_ROLE_KEY only in backend or trusted services
- Rotate keys if they leak
- Keep the JWT secret private

## Database Integration Concepts
- Use Supabase client in backend services to access tables
- Keep data access in service modules
- Use row level security policies in Supabase
