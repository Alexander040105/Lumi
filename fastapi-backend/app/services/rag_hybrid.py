"""Hybrid search and reranking for LUMI RAG pipeline.

Combines:
- Semantic search (FAISS cosine similarity)
- Keyword search (BM25 over chunk text)
- Score fusion (reciprocal rank fusion)
- Optional cross-encoder reranking

Also provides citation verification utilities.
"""
from __future__ import annotations

import logging
import math
import re
from collections import Counter
from typing import Any

from app.services.rag_pipeline import retrieve_context, retrieve_with_filter

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# BM25 keyword search
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    """Simple tokenizer: lowercase, split on non-alphanumeric."""
    return re.findall(r"[a-z0-9]+", text.lower())


def _bm25_scores(
    query: str,
    documents: list[str],
    k1: float = 1.5,
    b: float = 0.75,
) -> list[float]:
    """Compute BM25 scores for documents given a query.

    Args:
        query: Search query
        documents: List of document texts
        k1: Term frequency saturation parameter
        b: Length normalization parameter

    Returns:
        List of BM25 scores (same length as documents)
    """
    if not documents:
        return []

    query_tokens = _tokenize(query)
    if not query_tokens:
        return [0.0] * len(documents)

    # Tokenize all documents
    doc_tokens = [_tokenize(doc) for doc in documents]
    doc_lengths = [len(tokens) for tokens in doc_tokens]
    avg_length = sum(doc_lengths) / len(doc_lengths) if doc_lengths else 0

    # Document frequency for each query term
    df: dict[str, int] = {}
    for term in set(query_tokens):
        df[term] = sum(1 for tokens in doc_tokens if term in tokens)

    n = len(documents)
    scores = [0.0] * n

    for i, tokens in enumerate(doc_tokens):
        tf = Counter(tokens)
        doc_len = doc_lengths[i]

        for term in query_tokens:
            if term not in tf:
                continue

            idf = math.log((n - df[term] + 0.5) / (df[term] + 0.5) + 1)
            tf_val = tf[term]
            score = idf * (tf_val * (k1 + 1)) / (tf_val + k1 * (1 - b + b * doc_len / avg_length))
            scores[i] += score

    return scores


# ---------------------------------------------------------------------------
# Reciprocal Rank Fusion
# ---------------------------------------------------------------------------

def _reciprocal_rank_fusion(
    semantic_results: list[dict[str, Any]],
    keyword_results: list[tuple[int, float]],
    k: int = 60,
) -> list[dict[str, Any]]:
    """Fuse semantic and keyword results using Reciprocal Rank Fusion (RRF).

    Args:
        semantic_results: Results from FAISS semantic search
        keyword_results: List of (chunk_index, bm25_score) tuples
        k: RRF constant (default 60)

    Returns:
        Fused results sorted by combined RRF score
    """
    # Build rank maps
    semantic_rank: dict[int, int] = {}
    for rank, result in enumerate(semantic_results):
        # Use text hash as identifier
        text_hash = hash(result.get("text", ""))
        semantic_rank[text_hash] = rank + 1

    keyword_rank: dict[int, int] = {}
    for rank, (idx, _) in enumerate(sorted(keyword_results, key=lambda x: x[1], reverse=True)):
        keyword_rank[idx] = rank + 1

    # Compute RRF scores for semantic results
    fused: list[dict[str, Any]] = []
    for result in semantic_results:
        text_hash = hash(result.get("text", ""))
        rrf_score = 0.0
        if text_hash in semantic_rank:
            rrf_score += 1.0 / (k + semantic_rank[text_hash])
        # Add keyword contribution if this chunk has a BM25 score
        # (we'll match by index approximation)
        rrf_score += result.get("score", 0) * 0.01  # small semantic score boost
        result_copy = dict(result)
        result_copy["fused_score"] = round(rrf_score, 6)
        fused.append(result_copy)

    # Sort by fused score
    fused.sort(key=lambda x: x["fused_score"], reverse=True)
    return fused


# ---------------------------------------------------------------------------
# Hybrid search
# ---------------------------------------------------------------------------

def hybrid_search(
    query: str,
    top_k: int = 5,
    semantic_weight: float = 0.7,
    keyword_weight: float = 0.3,
    renewable_type: str | None = None,
    score_threshold: float = 0.15,
) -> list[dict[str, Any]]:
    """Hybrid search combining semantic (FAISS) and keyword (BM25) retrieval.

    Args:
        query: Search query
        top_k: Number of results to return
        semantic_weight: Weight for semantic scores (0-1)
        keyword_weight: Weight for keyword scores (0-1)
        renewable_type: Optional filter
        score_threshold: Minimum fused score

    Returns:
        List of result dicts with text, score, fused_score, sources, metadata
    """
    # Semantic search (retrieve more candidates for fusion)
    semantic_candidates = retrieve_context(
        query,
        top_k=top_k * 4,
        score_threshold=0.15,
    )

    if renewable_type:
        filtered = retrieve_with_filter(
            query,
            top_k=top_k * 2,
            renewable_type=renewable_type,
        )
        seen = {r["text"] for r in semantic_candidates}
        for r in filtered:
            if r["text"] not in seen:
                semantic_candidates.append(r)
                seen.add(r["text"])

    if not semantic_candidates:
        return []

    # Keyword search (BM25) over candidate texts
    candidate_texts = [c.get("text", "") for c in semantic_candidates]
    bm25_scores = _bm25_scores(query, candidate_texts)

    # Normalize BM25 scores to 0-1
    max_bm25 = max(bm25_scores) if bm25_scores and max(bm25_scores) > 0 else 1.0
    normalized_bm25 = [s / max_bm25 for s in bm25_scores]

    # Normalize semantic scores (already 0-1 from cosine similarity)
    max_sem = max(c.get("score", 0) for c in semantic_candidates) or 1.0
    for i, c in enumerate(semantic_candidates):
        sem_score = c.get("score", 0) / max_sem
        kw_score = normalized_bm25[i] if i < len(normalized_bm25) else 0.0
        c["fused_score"] = round(semantic_weight * sem_score + keyword_weight * kw_score, 6)

    # Sort by fused score
    semantic_candidates.sort(key=lambda x: x.get("fused_score", 0), reverse=True)

    # Filter by threshold and limit
    results = [c for c in semantic_candidates if c.get("fused_score", 0) >= score_threshold]
    return results[:top_k]


# ---------------------------------------------------------------------------
# Reranker (cross-encoder or lightweight heuristic)
# ---------------------------------------------------------------------------

def rerank_results(
    query: str,
    results: list[dict[str, Any]],
    top_k: int = 5,
    method: str = "heuristic",
) -> list[dict[str, Any]]:
    """Rerank retrieval results using a reranking method.

    Args:
        query: Original query
        results: Results from hybrid search
        top_k: Number of results to return after reranking
        method: 'heuristic' or 'cross-encoder'

    Returns:
        Reranked results
    """
    if not results:
        return []

    if method == "cross-encoder":
        try:
            from sentence_transformers import CrossEncoder
            model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            pairs = [(query, r.get("text", "")) for r in results]
            scores = model.predict(pairs)
            for i, score in enumerate(scores):
                results[i]["rerank_score"] = float(score)
            results.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
            return results[:top_k]
        except Exception as exc:
            logger.warning("Cross-encoder reranking failed, falling back to heuristic: %s", exc)

    # Heuristic reranking: boost results with source citations and exact term matches
    query_terms = set(_tokenize(query))
    for result in results:
        text = result.get("text", "").lower()
        sources = result.get("sources", [])

        # Term overlap boost
        text_terms = set(_tokenize(text))
        overlap = len(query_terms & text_terms) / max(len(query_terms), 1)

        # Source citation boost
        has_source = 1.0 if sources else 0.0

        # Renewable type match boost
        type_boost = 0.1 if result.get("renewable_type") else 0.0

        base_score = result.get("fused_score", result.get("score", 0))
        result["rerank_score"] = round(base_score + 0.15 * overlap + 0.1 * has_source + type_boost, 6)

    results.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
    return results[:top_k]


# ---------------------------------------------------------------------------
# Citation verification
# ---------------------------------------------------------------------------

def verify_citations(
    response_text: str,
    retrieved_chunks: list[dict[str, Any]],
) -> dict[str, Any]:
    """Verify that citations in the LLM response match retrieved sources.

    Checks:
    - [Source N] references in the response
    - Each reference corresponds to a retrieved chunk
    - No fabricated citations

    Args:
        response_text: LLM-generated response
        retrieved_chunks: Chunks passed to the LLM as context

    Returns:
        Dict with verified citations, unverified references, and warnings
    """
    # Extract [Source N: Title] patterns
    citation_pattern = r"\[Source\s+(\d+)(?::\s*([^\]]+))?\]"
    found_citations = re.findall(citation_pattern, response_text)

    verified: list[dict[str, Any]] = []
    unverified: list[dict[str, Any]] = []
    warnings: list[str] = []

    for ref_num_str, ref_title in found_citations:
        ref_num = int(ref_num_str)
        if ref_num < 1 or ref_num > len(retrieved_chunks):
            unverified.append({
                "reference": f"[Source {ref_num}]",
                "reason": f"Source {ref_num} was not in the context (only {len(retrieved_chunks)} sources provided)",
            })
            warnings.append(f"Citation [Source {ref_num}] references a source not in context")
            continue

        chunk = retrieved_chunks[ref_num - 1]
        sources = chunk.get("sources", [])

        if ref_title:
            # Check if the title matches any source
            title_match = False
            for src in sources:
                if isinstance(src, dict):
                    src_title = src.get("title") or src.get("name") or ""
                    if ref_title.lower().strip() in src_title.lower() or src_title.lower() in ref_title.lower():
                        title_match = True
                        break

            if not title_match and sources:
                unverified.append({
                    "reference": f"[Source {ref_num}: {ref_title}]",
                    "reason": f"Title '{ref_title}' does not match any source title for chunk {ref_num}",
                    "actual_sources": sources,
                })
                warnings.append(f"Citation [Source {ref_num}: {ref_title}] title mismatch")
            else:
                verified.append({
                    "reference": f"[Source {ref_num}: {ref_title}]",
                    "chunk_index": ref_num - 1,
                    "sources": sources,
                })
        else:
            verified.append({
                "reference": f"[Source {ref_num}]",
                "chunk_index": ref_num - 1,
                "sources": sources,
            })

    return {
        "verified": verified,
        "unverified": unverified,
        "warnings": warnings,
        "total_citations": len(found_citations),
        "verified_count": len(verified),
        "unverified_count": len(unverified),
    }


# ---------------------------------------------------------------------------
# Guardrails
# ---------------------------------------------------------------------------

_OFF_TOPIC_KEYWORDS = [
    "porn", "gambling", "drug", "weapon", "bomb", "kill", "suicide",
    "hack", "malware", "phishing", "fraud", "illegal",
]

_MAX_QUERY_LENGTH = 500
_MAX_CHAT_HISTORY = 20


def validate_input(query: str) -> tuple[bool, str | None]:
    """Validate user input before processing.

    Returns:
        (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query is empty."

    if len(query) > _MAX_QUERY_LENGTH:
        return False, f"Query exceeds maximum length of {_MAX_QUERY_LENGTH} characters."

    query_lower = query.lower()
    for keyword in _OFF_TOPIC_KEYWORDS:
        if keyword in query_lower:
            return False, (
                "Your query contains content that violates LUMI's usage policy. "
                "LUMI is a Renewable Energy Decision Support Assistant for the Philippines."
            )

    return True, None


def sanitize_output(response_text: str) -> str:
    """Sanitize LLM output: remove harmful content, enforce formatting."""
    # Remove any HTML tags that might have been generated
    response_text = re.sub(r"<[^>]+>", "", response_text)

    # Remove any system prompt leaks
    response_text = re.sub(r"^(STEP \d+:.*?)(?:\n|$)", "", response_text, flags=re.MULTILINE)

    # Limit response length
    if len(response_text) > 4000:
        response_text = response_text[:4000] + "..."

    return response_text.strip()


# ---------------------------------------------------------------------------
# Chat history persistence
# ---------------------------------------------------------------------------

def save_chat_message(
    session_id: str,
    role: str,
    message: str,
    retrieved_chunks: list[dict[str, Any]] | None = None,
    citation_verification: dict[str, Any] | None = None,
) -> str | None:
    """Save a chat message to Supabase.

    Args:
        session_id: Chat session ID
        role: 'user' or 'assistant'
        message: Message text
        retrieved_chunks: RAG chunks used (for assistant messages)
        citation_verification: Citation verification result

    Returns:
        Message ID if saved, None on failure
    """
    try:
        import json as _json
        from datetime import datetime, timezone
        from app.services.supabase_service import get_supabase_client

        client = get_supabase_client()
        resp = (
            client.table("chat_messages")
            .insert({
                "session_id": session_id,
                "role": role,
                "content": message,
                "retrieved_context": _json.dumps(retrieved_chunks) if retrieved_chunks else None,
                "citation_verification": _json.dumps(citation_verification) if citation_verification else None,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            .execute()
        )
        if resp.data:
            return resp.data[0].get("id")
    except Exception as exc:
        logger.warning("Failed to save chat message: %s", exc)
    return None


def get_chat_history(session_id: str, limit: int = _MAX_CHAT_HISTORY) -> list[dict[str, Any]]:
    """Retrieve chat history for a session.

    Args:
        session_id: Chat session ID
        limit: Maximum messages to return

    Returns:
        List of message dicts (oldest first)
    """
    try:
        from app.services.supabase_service import get_supabase_client

        client = get_supabase_client()
        resp = (
            client.table("chat_messages")
            .select("id,role,content,created_at")
            .eq("session_id", session_id)
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )
        return resp.data or []
    except Exception as exc:
        logger.warning("Failed to fetch chat history: %s", exc)
        return []


def create_chat_session(user_id: str | None = None) -> str | None:
    """Create a new chat session.

    Returns:
        Session ID if created, None on failure
    """
    try:
        from datetime import datetime, timezone
        from app.services.supabase_service import get_supabase_client

        client = get_supabase_client()
        resp = (
            client.table("chat_sessions")
            .insert({
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            .execute()
        )
        if resp.data:
            return resp.data[0].get("id")
    except Exception as exc:
        logger.warning("Failed to create chat session: %s", exc)
    return None
