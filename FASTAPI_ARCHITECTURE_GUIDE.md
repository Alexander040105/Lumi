# FastAPI Architecture Guide

## Blueprint-Style Modularity
FastAPI routers map cleanly to Flask Blueprints. Each feature lives in its own route module and can have its own dependencies and services.

- Flask Blueprint -> FastAPI APIRouter
- Blueprint registration -> app.include_router
- Blueprint url_prefix -> include_router prefix

## Current Structure
- app/routes/ - route modules (one file per domain)
- app/services/ - business logic and external integrations
- app/schemas/ - Pydantic request/response models
- app/dependencies/ - shared dependencies (auth, db, etc.)
- app/auth/ - JWT validation and security helpers
- app/config/ - settings and environment configuration

## How Routers Work
Each module exports a router:

```python
router = APIRouter()

@router.get("/")
async def list_items():
    ...
```

The top-level API router aggregates them:

```python
api_router.include_router(items_router, prefix="/items", tags=["items"])
```

## Adding a New Module
1. Create a new route file in app/routes/ (example: users.py)
2. Create schemas in app/schemas/
3. Create a service in app/services/
4. Register the router in app/routes/api.py

## Dependency Injection
Use dependencies to keep route functions thin:

- app/dependencies/auth.py holds JWT validation
- Routes request user data by adding Depends(get_current_user)

## Service Layer Pattern
Keep business rules in services, not in routes.

- Route: input validation and response models
- Service: data access, external API calls, domain rules

## Scaling Tips
- One router file per domain or bounded context
- One service file per integration or domain
- Split schemas by feature when they grow
- Keep authentication in its own module for reuse across routes
