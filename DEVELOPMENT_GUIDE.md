# Development Guide

## Recommended Workflow
- Run backend and frontend in separate terminals
- Keep .env files local and never commit them
- Build UI features by composing shadcn primitives and Tailwind utilities

## Naming Conventions
- Components: PascalCase
- Hooks: useSomething
- Services: noun or verb-based names (authService, apiClient)
- Pages: PascalCase matching route intent (Dashboard, Login)

## Scaling Tips
- One page per route in src/pages
- One service per integration in src/services
- Keep global UI primitives in src/components/ui
- Use layout components for shared shells

## Common Mistakes
- Putting business logic inside UI components
- Duplicating Tailwind class strings instead of composing components
- Mixing frontend and backend environment variables

## Production Recommendations
- Build with npm run build
- Serve with a CDN or static host (Vercel)
- Use environment-specific Supabase projects
- Lock down service role keys to backend only

## Vercel Notes
- Add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in Vercel env
- Add VITE_API_BASE_URL to point to your FastAPI deployment
- Rebuild on env change
