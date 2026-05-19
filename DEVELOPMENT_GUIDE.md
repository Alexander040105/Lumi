# Development Guide

## Recommended Workflow
- Run backend and frontend in separate terminals
- Keep .env files local and never commit them
- Add new features by creating a router + service + schema trio

## Scaling Tips
- Split routers by domain boundaries
- Keep auth logic centralized in app/auth
- Keep external services in app/services
- Add versioned routes under /api/v1 and later /api/v2

## Common Mistakes
- Putting database logic directly in routes
- Duplicating auth checks across files
- Mixing environment variables between backend and frontend

## Production Considerations
- Use a production ASGI server (uvicorn + gunicorn)
- Enable HTTPS in production
- Configure CORS for the real frontend domain
- Use environment-specific Supabase projects or keys

## Folder Organization Checklist
- routes: HTTP endpoints only
- services: business logic and data access
- schemas: request and response models
- dependencies: reusable dependencies
- auth: JWT and security helpers
