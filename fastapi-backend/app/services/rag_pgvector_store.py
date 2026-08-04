from __future__ import annotations

import logging
from typing import Any

from app.config.settings import get_settings
from app.services.rag_embeddings_client import encode
from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)

_RAG_TABLE = 'rag_chunks'
_RAG_RPC = 'match_rag_chunks'


def _vector_literal(embedding: list[float]) -> str:
    '''Format an embedding as a pgvector literal string.'''
    return '[' + ','.join(f'{x:.8f}' for x in embedding) + ']'


def _row_to_result(row: dict[str, Any]) -> dict[str, Any]:
    return {
        'text': row.get('chunk_text', ''),
        'score': round(float(row.get('similarity', 0.0)), 4),
        'renewable_type': row.get('renewable_type', '') or '',
        'category': row.get('category', '') or '',
        'product_type': row.get('product_type', '') or '',
        'sources': row.get('sources') or [],
    }


def _count_rows(client) -> int:
    try:
        resp = client.table(_RAG_TABLE).select('id', count='exact').limit(1).execute()
        if hasattr(resp, 'count') and resp.count is not None:
            return int(resp.count)
        # Fallback: exact count may not be available in all clients.
        count_resp = client.table(_RAG_TABLE).select('id').execute()
        return len(count_resp.data) if count_resp.data else 0
    except Exception:
        return 0


def ensure_index_built() -> bool:
    '''Check whether the pgvector table has been seeded.'''
    try:
        client = get_supabase_client()
        resp = client.table(_RAG_TABLE).select('id').limit(1).execute()
        has_rows = bool(resp.data)
        if not has_rows:
            logger.warning('RAG chunks table is empty; seeding is required.')
        return has_rows
    except Exception as exc:
        logger.warning('Could not verify pgvector RAG store: %s', exc)
        return False


def index_stats() -> dict[str, Any]:
    try:
        client = get_supabase_client()
        count = _count_rows(client)
        return {
            'chunks_loaded': count,
            'pgvector_enabled': True,
            'index_present': count > 0,
        }
    except Exception as exc:
        logger.warning('Could not get pgvector RAG stats: %s', exc)
        return {'chunks_loaded': 0, 'pgvector_enabled': False, 'index_present': False}


def _retrieve(
    query: str,
    top_k: int,
    renewable_type: str | None,
    category: str | None,
    score_threshold: float,
) -> list[dict[str, Any]]:
    settings = get_settings()
    embedding_model = settings.embedding_model or 'sentence-transformers/all-MiniLM-L6-v2'
    expected_model = 'sentence-transformers/all-MiniLM-L6-v2'
    if embedding_model != expected_model:
        logger.warning(
            'RAG_BACKEND=pgvector expects 384-d %s embeddings; using %s may fail.',
            expected_model,
            embedding_model,
        )

    embeddings = encode(query)
    if not embeddings or not embeddings[0]:
        raise RuntimeError('Failed to encode query for RAG retrieval')

    vector = _vector_literal(embeddings[0])
    client = get_supabase_client()
    params = {
        'query_embedding': vector,
        'match_count': top_k,
        'similarity_threshold': score_threshold,
        'filter_renewable_type': renewable_type,
        'filter_category': category,
    }

    try:
        resp = client.rpc(_RAG_RPC, params).execute()
    except Exception as exc:
        logger.exception('match_rag_chunks RPC failed')
        raise RuntimeError(f'pgvector RAG retrieval failed: {exc}') from exc

    rows = resp.data or []
    return [_row_to_result(row) for row in rows]


def retrieve_context(
    query: str,
    top_k: int = 5,
    model_name: str = 'all-MiniLM-L6-v2',
    score_threshold: float = 0.25,
    use_cache: bool = True,
) -> list[dict[str, Any]]:
    return _retrieve(query, top_k, None, None, score_threshold)


def retrieve_with_filter(
    query: str,
    top_k: int = 5,
    renewable_type: str | None = None,
    category: str | None = None,
    model_name: str = 'all-MiniLM-L6-v2',
    score_threshold: float = 0.25,
    use_cache: bool = True,
) -> list[dict[str, Any]]:
    return _retrieve(query, top_k, renewable_type, category, score_threshold)


def sample_chunks(n: int = 3) -> list[dict[str, Any]]:
    '''Return a sample of stored chunks for debugging.'''
    try:
        client = get_supabase_client()
        resp = client.table(_RAG_TABLE).select('*').limit(n).execute()
        rows = resp.data or []
        return [_row_to_result(row) for row in rows]
    except Exception as exc:
        logger.warning('Could not sample chunks: %s', exc)
        return []
