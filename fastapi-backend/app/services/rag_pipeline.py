"""
RAG Pipeline: semantic chunking, embedding, and FAISS retrieval for LUMI.

This module replaces the ad-hoc text slicing in the old RAG implementation with:
- sentence-aware chunking
- rich metadata (renewable_type, category, product_type)
- cosine-similarity FAISS search
- persisted index so the backend does not rebuild on every startup
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]
LOCAL_DATA_DIR = Path(__file__).resolve().parent / "local_data"
LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

INDEX_PATH = LOCAL_DATA_DIR / "rag_faiss.index"
CHUNKS_PATH = LOCAL_DATA_DIR / "rag_chunks.json"
KNOWLEDGE_JSON_PATH = LOCAL_DATA_DIR / "rag_knowledge_base.json"

DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def _index_is_stale() -> bool:
    """Return True if the knowledge base JSON is newer than the FAISS index."""
    if not KNOWLEDGE_JSON_PATH.exists():
        return False  # no knowledge base to compare
    if not INDEX_PATH.exists():
        return True
    return KNOWLEDGE_JSON_PATH.stat().st_mtime > INDEX_PATH.stat().st_mtime

# ---------------------------------------------------------------------------
# Globals (lazy-loaded)
# ---------------------------------------------------------------------------
_index: "faiss.Index | None" = None
_chunks: list[dict[str, Any]] = []
_embedder: "SentenceTransformer | None" = None


# ---------------------------------------------------------------------------
# Embedder
# ---------------------------------------------------------------------------

def _get_embedder(model_name: str = DEFAULT_EMBEDDING_MODEL):
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is required for RAG. "
                "Add it to fastapi-backend/requirements.txt"
            ) from exc
        logger.info("Loading embedding model %s ...", model_name)
        _embedder = SentenceTransformer(model_name)
    return _embedder


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def _sentences(text: str) -> list[str]:
    """Split text into sentences without breaking on decimals or abbreviations."""
    # Simple regex that preserves decimal numbers and common abbreviations
    pattern = r"(?<=[.!?])\s+(?=[A-Z])"
    parts = re.split(pattern, text)
    return [p.strip() for p in parts if p.strip()]


def _semantic_chunks(
    text: str,
    max_words: int = 150,
    overlap_sentences: int = 1,
) -> list[str]:
    """
    Build chunks that respect sentence boundaries.

    Strategy:
    - Walk through sentences.
    - Add sentences to current chunk while word count <= max_words.
    - When the next sentence would overflow, emit chunk and start next chunk
      with the last *overlap_sentences* sentence(s) for continuity.
    """
    sents = _sentences(text)
    if not sents:
        return [text] if text.strip() else []

    # If the whole text is small enough, keep it as one chunk
    total_words = len(text.split())
    if total_words <= max_words:
        return [text]

    chunks: list[str] = []
    current_sents: list[str] = []
    current_words = 0

    for sent in sents:
        sent_words = len(sent.split())
        if current_words + sent_words > max_words and current_sents:
            chunks.append(" ".join(current_sents))
            # overlap
            if overlap_sentences > 0:
                current_sents = current_sents[-overlap_sentences:] + [sent]
                current_words = sum(len(s.split()) for s in current_sents)
            else:
                current_sents = [sent]
                current_words = sent_words
        else:
            current_sents.append(sent)
            current_words += sent_words

    if current_sents:
        chunks.append(" ".join(current_sents))

    return chunks


def _clean_text(text: str) -> str:
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Document ingestion
# ---------------------------------------------------------------------------

def _chunk_documents(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Turn knowledge documents into chunked records with preserved metadata.
    """
    chunks: list[dict[str, Any]] = []
    for doc in docs:
        content = _clean_text(doc.get("content", ""))
        if not content:
            continue

        for chunk_text in _semantic_chunks(content):
            chunks.append({
                "text": chunk_text,
                "renewable_type": doc.get("renewable_type", ""),
                "category": doc.get("category", ""),
                "product_type": doc.get("product_type", ""),
                "sources": doc.get("sources", []),
            })
    return chunks


# ---------------------------------------------------------------------------
# Index build / load
# ---------------------------------------------------------------------------

def build_faiss_index(
    docs: list[dict[str, Any]],
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    save: bool = True,
) -> dict[str, Any]:
    """
    Build a FAISS index from knowledge documents.

    Returns metadata about the index.  The index itself is kept in memory
    and optionally written to disk.
    """
    global _index, _chunks

    try:
        import faiss
    except ImportError as exc:
        raise ImportError(
            "faiss-cpu is required for RAG. Add it to fastapi-backend/requirements.txt"
        ) from exc

    chunks = _chunk_documents(docs)
    if not chunks:
        raise ValueError("No chunks generated from documents")

    texts = [c["text"] for c in chunks]
    embedder = _get_embedder(model_name)
    logger.info("Encoding %s chunks ...", len(texts))
    embeddings = embedder.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    embeddings = embeddings.astype("float32")

    # Inner-product index on *normalized* vectors = cosine similarity
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    _index = index
    _chunks = chunks

    if save:
        faiss.write_index(index, str(INDEX_PATH))
        with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        logger.info("Saved FAISS index to %s", INDEX_PATH)

    return {
        "documents": len(docs),
        "chunks": len(chunks),
        "dimension": dimension,
        "index_path": str(INDEX_PATH),
        "chunks_path": str(CHUNKS_PATH),
    }


def load_faiss_index(
    index_path: Path = INDEX_PATH,
    chunks_path: Path = CHUNKS_PATH,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> bool:
    """
    Load a previously built FAISS index from disk.

    Returns True if loaded successfully, False if files are missing.
    """
    global _index, _chunks

    if not index_path.exists() or not chunks_path.exists():
        logger.warning("FAISS index or chunks file missing; needs rebuild.")
        return False

    try:
        import faiss
    except ImportError:
        logger.error("faiss-cpu not installed")
        return False

    _index = faiss.read_index(str(index_path))
    with open(chunks_path, "r", encoding="utf-8") as f:
        _chunks = json.load(f)

    # sanity-check embedder is loadable (we don't need it yet, but we want early failure)
    _get_embedder(model_name)

    logger.info("Loaded FAISS index with %s chunks", len(_chunks))
    return True


def ensure_index_built(
    docs: list[dict[str, Any]] | None = None,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> None:
    """
    Idempotent helper: load existing index, or build from *docs* if missing.
    If the knowledge-base JSON is also missing or newer than the index, rebuild.
    """
    global _index, _chunks
    if _index is not None and not _index_is_stale():
        return
    if _index_is_stale():
        logger.info("Knowledge base is newer than FAISS index; rebuilding index...")
        _index = None
        _chunks = []
    elif load_faiss_index(model_name=model_name):
        return
    if docs is None:
        from app.services.rag_knowledge_builder import (
            build_knowledge_base,
            load_knowledge_base,
            save_knowledge_base,
        )
        try:
            docs = load_knowledge_base()
        except FileNotFoundError:
            logger.info("Knowledge base JSON missing; rebuilding from CSV...")
            docs = build_knowledge_base()
            save_knowledge_base(docs)
    build_faiss_index(docs, model_name=model_name)


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def retrieve_context(
    query: str,
    top_k: int = 5,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    score_threshold: float = 0.25,
) -> list[dict[str, Any]]:
    """
    Retrieve the most semantically similar chunks for a query.

    Because we use IndexFlatIP + normalized vectors, the raw score is
    cosine similarity (range 0..1).  *score_threshold* filters out
    irrelevant matches.
    """
    if _index is None:
        ensure_index_built(model_name=model_name)

    if _index is None or not _chunks:
        raise RuntimeError("FAISS index is not available")

    embedder = _get_embedder(model_name)
    query_emb = embedder.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    query_emb = query_emb.astype("float32")

    scores, indices = _index.search(query_emb, top_k)
    results: list[dict[str, Any]] = []

    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(_chunks):
            continue
        if score < score_threshold:
            continue
        chunk = _chunks[idx]
        results.append({
            "text": chunk["text"],
            "score": round(float(score), 4),
            "renewable_type": chunk.get("renewable_type", ""),
            "category": chunk.get("category", ""),
            "product_type": chunk.get("product_type", ""),
            "sources": chunk.get("sources", []),
        })

    return results


def retrieve_with_filter(
    query: str,
    top_k: int = 5,
    renewable_type: str | None = None,
    category: str | None = None,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    score_threshold: float = 0.25,
) -> list[dict[str, Any]]:
    """
    Same as retrieve_context but allows post-filtering by metadata fields.
    Retrieves more candidates than top_k so filtering still yields results.
    """
    candidates = retrieve_context(
        query,
        top_k=top_k * 4,
        model_name=model_name,
        score_threshold=score_threshold,
    )
    if renewable_type:
        candidates = [c for c in candidates if c.get("renewable_type") == renewable_type]
    if category:
        candidates = [c for c in candidates if c.get("category") == category]
    return candidates[:top_k]


# ---------------------------------------------------------------------------
# Diagnostic helpers
# ---------------------------------------------------------------------------

def index_stats() -> dict[str, Any]:
    return {
        "chunks_loaded": len(_chunks),
        "index_present": _index is not None,
        "index_path_exists": INDEX_PATH.exists(),
        "chunks_path_exists": CHUNKS_PATH.exists(),
    }


def sample_chunks(n: int = 3) -> list[dict[str, Any]]:
    """Return a sample of stored chunks for debugging."""
    return _chunks[:n]
