from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Any

import httpx

from app.config.settings import get_settings
from app.services.redis_client import get_redis_sync

logger = logging.getLogger(__name__)

_EMBEDDING_CACHE_PREFIX = 'lumi:rag:embedding'
_EMBEDDING_CACHE_TTL_SECONDS = 3600
_HUGGINGFACE_INFERENCE_URL = 'https://api-inference.huggingface.co/models/{model}'


def _cache_key(text: str) -> str:
    normalized = text.strip().lower()
    digest = hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:32]
    return f'{_EMBEDDING_CACHE_PREFIX}:{digest}'


def _get_cached_embedding(key: str) -> list[float] | None:
    try:
        redis = get_redis_sync()
        if redis is None:
            return None
        cached = redis.get(key)
        if cached:
            return json.loads(cached)
    except Exception as exc:
        logger.debug('Embedding cache read failed: %s', exc)
    return None


def _save_cached_embedding(key: str, embedding: list[float]) -> None:
    try:
        redis = get_redis_sync()
        if redis is None:
            return
        redis.setex(key, _EMBEDDING_CACHE_TTL_SECONDS, json.dumps(embedding))
    except Exception as exc:
        logger.debug('Embedding cache write failed: %s', exc)


def _format_embeddings(raw: Any, count: int) -> list[list[float]]:
    '''Normalize HuggingFace / OpenAI responses into a list of float lists.'''
    if not isinstance(raw, list):
        raise ValueError(f'Unexpected embedding response type: {type(raw)}')
    if count == 1:
        if not raw:
            raise ValueError('Empty embedding response for single input')
        if isinstance(raw[0], (int, float)):
            return [raw]
        if isinstance(raw[0], list) and len(raw) == 1:
            return raw
        raise ValueError('Unexpected single embedding response shape')
    if not all(isinstance(item, list) for item in raw):
        raise ValueError('Batch embedding response must be a list of lists')
    if len(raw) != count:
        raise ValueError(f'Expected {count} embeddings, got {len(raw)}')
    return raw


def _embed_with_huggingface(
    texts: list[str],
    model: str,
    token: str | None,
    batch_size: int,
) -> list[list[float]]:
    url = _HUGGINGFACE_INFERENCE_URL.format(model=model)
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'

    results: list[list[float]] = []
    with httpx.Client(timeout=60.0) as client:
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            payload = {'inputs': batch}
            for attempt in range(3):
                try:
                    resp = client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        results.extend(_format_embeddings(data, len(batch)))
                        break
                    if resp.status_code == 503 and attempt < 2:
                        logger.warning('HuggingFace inference is loading, retrying...')
                        time.sleep(2 ** attempt)
                        continue
                    raise RuntimeError(
                        f'HuggingFace inference error {resp.status_code}: {resp.text}'
                    )
                except (RuntimeError, ValueError):
                    raise
                except Exception as exc:
                    if attempt == 2:
                        raise RuntimeError(
                            f'HuggingFace inference call failed: {exc}'
                        ) from exc
                    logger.warning('HuggingFace inference call failed, retrying: %s', exc)
                    time.sleep(2 ** attempt)
    return results


def _embed_with_openai(
    texts: list[str],
    model: str,
    token: str | None,
    batch_size: int,
) -> list[list[float]]:
    if not token:
        raise ValueError('OPENAI_API_KEY is required when EMBEDDING_PROVIDER=openai')
    url = 'https://api.openai.com/v1/embeddings'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

    results: list[list[float]] = []
    with httpx.Client(timeout=60.0) as client:
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            payload = {'input': batch, 'model': model}
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json().get('data', [])
            results.extend([item['embedding'] for item in data])
    return results


def _embed_batch(texts: list[str]) -> list[list[float]]:
    settings = get_settings()
    provider = settings.embedding_provider.lower() if settings.embedding_provider else 'huggingface-inference'
    model = settings.embedding_model or 'sentence-transformers/all-MiniLM-L6-v2'
    batch_size = max(1, settings.embedding_batch_size or 32)

    if provider in ('huggingface', 'huggingface-inference', 'hf'):
        token = settings.hf_token or settings.embedding_api_key or None
        return _embed_with_huggingface(texts, model, token, batch_size)
    if provider == 'openai':
        token = settings.openai_api_key or settings.embedding_api_key or None
        return _embed_with_openai(texts, model, token, batch_size)
    raise ValueError(f'Unsupported embedding provider: {settings.embedding_provider}')


def encode(texts: str | list[str]) -> list[list[float]]:
    '''Encode one or more texts, using Redis cache to avoid repeated API calls.'''
    if isinstance(texts, str):
        texts = [texts]
    if not texts:
        return []

    results: list[list[float] | None] = [None] * len(texts)
    unique_texts: list[str] = []
    unique_norms: list[str] = []
    norm_to_indices: dict[str, list[int]] = {}

    for idx, text in enumerate(texts):
        normalized = text.strip().lower()
        if normalized not in norm_to_indices:
            norm_to_indices[normalized] = []
            unique_texts.append(text)
            unique_norms.append(normalized)
        norm_to_indices[normalized].append(idx)

    missing_texts: list[str] = []
    missing_norms: list[str] = []
    for text, norm in zip(unique_texts, unique_norms):
        cache_key = _cache_key(norm)
        cached = _get_cached_embedding(cache_key)
        if cached:
            for idx in norm_to_indices[norm]:
                results[idx] = cached
        else:
            missing_texts.append(text)
            missing_norms.append(norm)

    if missing_texts:
        embeddings = _embed_batch(missing_texts)
        for norm, emb in zip(missing_norms, embeddings):
            _save_cached_embedding(_cache_key(norm), emb)
            for idx in norm_to_indices[norm]:
                results[idx] = emb

    return [r for r in results if r is not None]


def encode_query(query: str) -> list[float]:
    '''Convenience helper for a single query.'''
    embeddings = encode(query)
    if not embeddings:
        raise RuntimeError('Failed to encode query')
    return embeddings[0]
