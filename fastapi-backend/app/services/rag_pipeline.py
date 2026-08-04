'''
RAG pipeline dispatcher.

Supports two backends selected by the RAG_BACKEND environment variable:
- pgvector: external embeddings + Supabase pgvector (Vercel-compatible).
- faiss: local sentence-transformers + FAISS (local development).
'''
from __future__ import annotations

import logging
from typing import Any

from app.config.settings import get_settings
from app.services import rag_pgvector_store


def _rag_faiss():
    '''Lazy import the FAISS backend so Vercel does not load it by default.'''
    from app.services import rag_faiss

    return rag_faiss

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

# Backward-compatible module-level globals. For the pgvector backend these stay
# None; for the faiss backend they mirror the values in app.services.rag_faiss.
_index: Any = None
_chunks: list[dict[str, Any]] = []
_embedder: Any = None


def _rag_backend() -> str:
    return (get_settings().rag_backend or 'faiss').lower()


def build_faiss_index(
    docs: list[dict[str, Any]],
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    save: bool = True,
) -> dict[str, Any]:
    return _rag_faiss().build_faiss_index(docs, model_name=model_name, save=save)


def load_faiss_index(
    index_path=None,
    chunks_path=None,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> bool:
    if _rag_backend() == 'pgvector':
        logger.warning('load_faiss_index is not used with RAG_BACKEND=pgvector')
        return False
    return _rag_faiss().load_faiss_index(
        index_path=index_path, chunks_path=chunks_path, model_name=model_name
    )


def ensure_index_built(
    docs: list[dict[str, Any]] | None = None,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> bool:
    if _rag_backend() == 'pgvector':
        return rag_pgvector_store.ensure_index_built()
    return _rag_faiss().ensure_index_built(docs=docs, model_name=model_name)


def retrieve_context(
    query: str,
    top_k: int = 5,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    score_threshold: float = 0.25,
    use_cache: bool = True,
) -> list[dict[str, Any]]:
    if _rag_backend() == 'pgvector':
        return rag_pgvector_store.retrieve_context(
            query,
            top_k=top_k,
            model_name=model_name,
            score_threshold=score_threshold,
            use_cache=use_cache,
        )
    return _rag_faiss().retrieve_context(
        query,
        top_k=top_k,
        model_name=model_name,
        score_threshold=score_threshold,
        use_cache=use_cache,
    )


def retrieve_with_filter(
    query: str,
    top_k: int = 5,
    renewable_type: str | None = None,
    category: str | None = None,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    score_threshold: float = 0.25,
    use_cache: bool = True,
) -> list[dict[str, Any]]:
    if _rag_backend() == 'pgvector':
        return rag_pgvector_store.retrieve_with_filter(
            query,
            top_k=top_k,
            renewable_type=renewable_type,
            category=category,
            model_name=model_name,
            score_threshold=score_threshold,
            use_cache=use_cache,
        )
    return _rag_faiss().retrieve_with_filter(
        query,
        top_k=top_k,
        renewable_type=renewable_type,
        category=category,
        model_name=model_name,
        score_threshold=score_threshold,
        use_cache=use_cache,
    )


def index_stats() -> dict[str, Any]:
    if _rag_backend() == 'pgvector':
        return rag_pgvector_store.index_stats()
    return _rag_faiss().index_stats()


def sample_chunks(n: int = 3) -> list[dict[str, Any]]:
    if _rag_backend() == 'pgvector':
        return rag_pgvector_store.sample_chunks(n=n)
    return _rag_faiss().sample_chunks(n=n)
