# Frontend Guide

## Structure
- src/pages/ - page-level routes
- src/components/ - reusable UI components
- src/layouts/ - layout shells with Outlet
- src/context/ - auth provider
- src/services/ - API clients and external integrations
- src/routes/ - route definitions
- src/utils/ - shared helpers

## Auth Flow
- Login uses Supabase OAuth
- Session persists with supabase-js
- Auth context exposes session and access token

## Protected Routes
ProtectedRoute checks for a session before showing a page. If no session exists, it redirects to /login.

## API Communication
apiClient.js wraps fetch and adds Authorization headers when a token is available.

## Adding a New Page
1. Create a new file in src/pages/
2. Add a route in src/routes/AppRoutes.jsx
3. Use ProtectedRoute if the page requires auth

## Adding a New API Call
1. Create a function in src/services/apiClient.js
2. Use the access token from the auth context
