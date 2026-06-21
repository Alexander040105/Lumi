from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.routes.api import api_router

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.on_event("startup")
async def startup_event():
    """Ensure the RAG knowledge base and FAISS index are up-to-date on startup."""
    import logging
    from app.services.rag_pipeline import ensure_index_built
    logger = logging.getLogger(__name__)

    if not settings.rag_warmup_on_startup:
        logger.info("RAG warmup on startup is disabled (RAG_WARMUP_ON_STARTUP=false).")
        return

    try:
        ensure_index_built()
        logger.info("RAG index ready on startup.")
    except Exception as exc:
        logger.warning("RAG index build failed on startup: %s", exc)


@app.get("/", tags=["root"])
async def root():
    return {"status": "ok", "service": settings.app_name}


@app.get("/warmup", tags=["system"])
async def warmup():
    """
    Trigger lazy-loading of the RAG embedding model and FAISS index.
    Call this once after deploy to pre-warm before the demo.
    """
    import logging
    from app.services.rag_pipeline import ensure_index_built, index_stats
    logger = logging.getLogger(__name__)

    try:
        ensure_index_built()
        stats = index_stats()
        return {"status": "warmed_up", "rag_stats": stats}
    except Exception as exc:
        logger.warning("RAG warmup failed: %s", exc)
        return {"status": "warmup_failed", "error": str(exc), "rag_stats": index_stats()}


@app.get("/rag/status", tags=["system"])
async def rag_status():
    """Return the current status of the RAG pipeline."""
    from app.services.rag_pipeline import index_stats, RAG_ENABLED
    return {
        "rag_enabled": RAG_ENABLED,
        "rag_warmup_on_startup": settings.rag_warmup_on_startup,
        **index_stats(),
    }
