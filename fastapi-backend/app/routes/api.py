from fastapi import APIRouter

from app.routes.health import router as health_router
# from app.routes.example import router as example_router
from app.routes.protected import router as protected_router
from app.routes.ecosim import router as ecosim_router
from app.routes.energyhub import router as energyhub_router
from app.routes.geothermal import router as geothermal_router
from app.routes.geospatial import router as geospatial_router
# from app.routes.chat import router as chat_router          # disabled: heavy RAG chat not needed at launch
from app.routes.admin import router as admin_router
from app.routes.simulations import router as simulations_router
from app.routes.products import router as products_router
from app.routes.forecast import router as forecast_router
from app.routes.map import router as map_router
# from app.routes.etl import router as etl_router              # disabled: long-running, not used by webapp

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
# api_router.include_router(example_router, prefix="/items", tags=["items"])
api_router.include_router(protected_router, prefix="/protected", tags=["protected"])
api_router.include_router(ecosim_router, prefix="/ecosim", tags=["ecosim"])
api_router.include_router(energyhub_router, prefix="/energyhub", tags=["energyhub"])
api_router.include_router(geothermal_router, prefix="/geothermal", tags=["geothermal"])
api_router.include_router(geospatial_router, prefix="/geospatial", tags=["geospatial"])
# api_router.include_router(chat_router, prefix="/chat", tags=["chat"])
api_router.include_router(simulations_router, prefix="/simulations", tags=["simulations"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(products_router, prefix="/products", tags=["products"])
api_router.include_router(forecast_router, prefix="/forecast", tags=["forecasting"])
api_router.include_router(map_router, prefix="/map", tags=["mapping"])
# api_router.include_router(etl_router, prefix="/etl", tags=["etl"])
