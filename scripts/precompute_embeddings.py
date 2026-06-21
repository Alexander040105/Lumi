#!/usr/bin/env python3
"""
Pre-compute RAG chunk embeddings offline.

This script loads the embedding model once, encodes all knowledge chunks,
and saves the vectors alongside the chunks.  On memory-constrained hosts
(e.g. Render free tier) the backend can then be configured to load the
pre-computed vectors instead of loading the model at runtime.

Usage:
    cd fastapi-backend
    python -m scripts.precompute_embeddings

Output:
    app/services/local_data/rag_precomputed.json
    (contains chunk text + pre-computed vector for each chunk)
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Paths — same as rag_pipeline.py
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_DATA_DIR = REPO_ROOT / "fastapi-backend" / "app" / "services" / "local_data"
CHUNKS_PATH = LOCAL_DATA_DIR / "rag_chunks.json"
OUTPUT_PATH = LOCAL_DATA_DIR / "rag_precomputed.json"

DEFAULT_MODEL = "all-MiniLM-L6-v2"


def _load_chunks() -> list[dict]:
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(f"Chunks file not found: {CHUNKS_PATH}")
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    logger.info("Loading chunks from %s ...", CHUNKS_PATH)
    chunks = _load_chunks()
    if not chunks:
        logger.error("No chunks found.")
        return 1

    logger.info("Loaded %s chunks.", len(chunks))

    # Import here so we fail fast if sentence-transformers is missing
    try:
        import torch
        torch.set_num_threads(1)
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        logger.error("sentence-transformers not installed: %s", exc)
        return 1

    logger.info("Loading embedding model %s ...", DEFAULT_MODEL)
    model = SentenceTransformer(DEFAULT_MODEL, device="cpu")

    texts = [c["text"] for c in chunks]
    logger.info("Encoding %s chunks ...", len(texts))
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    records = []
    for chunk, vec in zip(chunks, embeddings):
        records.append({
            "text": chunk["text"],
            "renewable_type": chunk.get("renewable_type", ""),
            "category": chunk.get("category", ""),
            "product_type": chunk.get("product_type", ""),
            "sources": chunk.get("sources", []),
            "embedding": vec.tolist(),
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    logger.info("Saved %s pre-computed records to %s", len(records), OUTPUT_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
