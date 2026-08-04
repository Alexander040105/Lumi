from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

# Add the fastapi-backend package to the import path.
_BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_BACKEND))

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)

LOCAL_DATA_DIR = _BACKEND / 'app' / 'services' / 'local_data'
KNOWLEDGE_JSON = LOCAL_DATA_DIR / 'rag_knowledge_base.json'


def _chunk_documents(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    '''Reuse the existing chunking logic from the FAISS backend.'''
    from app.services.rag_faiss import _chunk_documents as chunker

    return chunker(docs)


def _vector_literal(embedding: list[float]) -> str:
    '''Format an embedding as a pgvector literal string.'''
    return '[' + ','.join(f'{x:.8f}' for x in embedding) + ']'


def _truncate(client) -> None:
    '''Remove existing chunks so the seeder is idempotent.'''
    try:
        client.table('rag_chunks').delete().neq('id', 0).execute()
        logger.info('Cleared existing rag_chunks.')
    except Exception as exc:
        logger.warning('Could not clear rag_chunks before seeding: %s', exc)


def _build_records(chunks: list[dict[str, Any]], embeddings: list[list[float]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for chunk, emb in zip(chunks, embeddings):
        records.append({
            'chunk_text': chunk.get('text', ''),
            'renewable_type': chunk.get('renewable_type', '') or '',
            'category': chunk.get('category', '') or '',
            'product_type': chunk.get('product_type', '') or '',
            'sources': chunk.get('sources', []),
            'embedding': _vector_literal(emb),
        })
    return records


def _seed(client, records: list[dict[str, Any]]) -> int:
    batch_size = 500
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        client.table('rag_chunks').insert(batch).execute()
        logger.info('Inserted chunk batch %s-%s', i, min(i + batch_size, len(records)))
    return len(records)


def _encode_local(texts: list[str]) -> list[list[float]]:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer('all-MiniLM-L6-v2')
    arrays = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return arrays.astype('float32').tolist()


def _encode_external(texts: list[str]) -> list[list[float]]:
    from app.services.rag_embeddings_client import encode

    return encode(texts)


def main() -> None:
    from app.services.supabase_service import get_supabase_client

    client = get_supabase_client()
    _truncate(client)

    logger.info('Loading knowledge base from %s', KNOWLEDGE_JSON)
    with open(KNOWLEDGE_JSON, 'r', encoding='utf-8') as f:
        docs = json.load(f)

    chunks = _chunk_documents(docs)
    logger.info('Generated %s chunks from %s documents', len(chunks), len(docs))

    texts = [c.get('text', '') for c in chunks]
    try:
        embeddings = _encode_local(texts)
        logger.info('Computed %s embeddings locally', len(embeddings))
    except ImportError:
        logger.warning(
            'sentence-transformers not installed; falling back to the external embedding API. '
            'This is slower and may hit rate limits.'
        )
        embeddings = _encode_external(texts)

    records = _build_records(chunks, embeddings)
    count = _seed(client, records)
    logger.info('Seeded %s chunks into Supabase.', count)

    # Quick sanity check.
    from app.services import rag_pgvector_store

    stats = rag_pgvector_store.index_stats()
    logger.info('pgvector stats: %s', stats)


if __name__ == '__main__':
    main()
