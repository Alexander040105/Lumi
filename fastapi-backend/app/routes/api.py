from fastapi import APIRouter

from app.routes.health import router as health_router
# from app.routes.example import router as example_router
from app.routes.protected import router as protected_router
from app.routes.ecosim import router as ecosim_router
from app.routes.energyhub import router as energyhub_router
from app.routes.geothermal import router as geothermal_router
from app.routes.chat import router as chat_router
from app.routes.admin import router as admin_router
from app.routes.simulations import router as simulations_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
# api_router.include_router(example_router, prefix="/items", tags=["items"])
api_router.include_router(protected_router, prefix="/protected", tags=["protected"])
api_router.include_router(ecosim_router, prefix="/ecosim", tags=["ecosim"])
api_router.include_router(energyhub_router, prefix="/energyhub", tags=["energyhub"])
api_router.include_router(geothermal_router, prefix="/geothermal", tags=["geothermal"])
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(simulations_router, prefix="/simulations", tags=["simulations"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
