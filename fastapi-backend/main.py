import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware, setup_logging
from app.middleware.security import BodySizeLimitMiddleware, SecurityHeadersMiddleware
from app.routes.api import api_router

settings = get_settings()
setup_logging(level=settings.log_level.upper())

app = FastAPI(title=settings.app_name, version="0.1.0")

# Middleware order: outermost first (body size → security headers → rate limit → CORS → request ID)
app.add_middleware(BodySizeLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-Request-ID"],
)
app.add_middleware(RequestIDMiddleware)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
async def startup_event():
    """Ensure the RAG knowledge base and FAISS index are up-to-date on startup.

    The build/load runs in a thread pool so heavy model imports do not block the
    Uvicorn event loop, and failures are logged as warnings instead of crashing
    the application.
    """
    from app.services.rag_pipeline import ensure_index_built
    from app.services.supabase_service import get_supabase_client
    from app.services.redis_client import get_redis_sync
    logger = logging.getLogger(__name__)

    try:
        await asyncio.to_thread(get_supabase_client)
        await asyncio.to_thread(get_redis_sync)
        logger.info("Supabase and Redis sync clients pre-initialized on startup.")
    except Exception as exc:
        logger.warning("Cache client pre-init failed on startup: %s", exc)

    if not settings.enable_rag:
        logger.info("RAG is disabled via settings.")
        return

    if settings.rag_backend == "pgvector":
        logger.info("RAG_BACKEND=pgvector; FAISS index is not built at startup.")
        return

    try:
        await asyncio.to_thread(ensure_index_built)
        logger.info("RAG index ready on startup.")
    except Exception as exc:
        logger.warning("RAG index build failed on startup: %s", exc, exc_info=settings.debug)


@app.get("/", tags=["root"])
async def root():
    return {"status": "ok", "service": settings.app_name}
