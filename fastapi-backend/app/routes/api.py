from fastapi import APIRouter

from app.routes.health import router as health_router
from app.routes.example import router as example_router
from app.routes.protected import router as protected_router
from app.routes.ecosim import router as ecosim_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(example_router, prefix="/items", tags=["items"])
api_router.include_router(protected_router, prefix="/protected", tags=["protected"])
api_router.include_router(ecosim_router, prefix="/ecosim", tags=["ecosim"])
