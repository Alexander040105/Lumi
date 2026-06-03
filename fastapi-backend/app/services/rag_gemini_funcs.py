import json
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from app.services.gemini_funcs import generate_gemini_response, parse_gemini_json_response

_repo_root = Path(__file__).resolve().parents[3]
load_dotenv(dotenv_path=_repo_root / ".env")

logger = logging.getLogger(__name__)

RAG_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2")

_RAG_INDEX = None
_RAG_CHUNKS: list[str] = []
_RAG_METADATA: list[dict[str, Any]] = []
_RAG_EMBEDDER = None


def _get_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _get_embedder():
    global _RAG_EMBEDDER
    if _RAG_EMBEDDER is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is required for RAG. Install it in fastapi-backend/requirements.txt"
            ) from exc
        _RAG_EMBEDDER = SentenceTransformer(RAG_EMBEDDING_MODEL)
    return _RAG_EMBEDDER


def _read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _load_documents(scraped_data_path: Path) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for file_path in scraped_data_path.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in {".txt", ".md", ".json", ".csv", ".html"}:
            continue

        raw_text = _read_text_file(file_path)
        if not raw_text.strip():
            continue

        if file_path.suffix.lower() == ".json":
            try:
                payload = json.loads(raw_text)
                raw_text = json.dumps(payload, ensure_ascii=True, indent=2)
            except json.JSONDecodeError:
                pass

        documents.append(
            {
                "text": raw_text,
                "source": str(file_path),
            }
        )

    return documents


def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        start = end - overlap
        if start < 0:
            start = 0
        if start >= len(text):
            break
    return chunks


def create_vector_database(scraped_data: str | None = None) -> dict[str, Any]:
    global _RAG_INDEX, _RAG_CHUNKS, _RAG_METADATA

    scraped_path = Path(scraped_data) if scraped_data else _get_repo_root() / "scraped_data"
    if not scraped_path.exists():
        raise FileNotFoundError(f"scraped_data path not found: {scraped_path}")

    documents = _load_documents(scraped_path)
    if not documents:
        raise ValueError("No documents found in scraped_data")

    chunks: list[str] = []
    metadata: list[dict[str, Any]] = []

    for doc in documents:
        for chunk in _chunk_text(doc["text"]):
            chunks.append(chunk)
            metadata.append({"source": doc["source"]})

    embedder = _get_embedder()
    embeddings = embedder.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
    embeddings = embeddings.astype("float32")

    try:
        import faiss
    except ImportError as exc:
        raise ImportError(
            "faiss-cpu is required for RAG. Install it in fastapi-backend/requirements.txt"
        ) from exc

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    _RAG_INDEX = index
    _RAG_CHUNKS = chunks
    _RAG_METADATA = metadata

    return {
        "documents": len(documents),
        "chunks": len(chunks),
        "dimension": embeddings.shape[1],
    }


def retrieve_context(user_query: str, top_k: int = 5) -> list[dict[str, Any]]:
    if _RAG_INDEX is None:
        create_vector_database()

    embedder = _get_embedder()
    query_embedding = embedder.encode([user_query], convert_to_numpy=True, normalize_embeddings=True)
    query_embedding = query_embedding.astype("float32")

    distances, indices = _RAG_INDEX.search(query_embedding, top_k)
    results: list[dict[str, Any]] = []

    for score, idx in zip(distances[0], indices[0]):
        if idx < 0 or idx >= len(_RAG_CHUNKS):
            continue
        results.append(
            {
                "text": _RAG_CHUNKS[idx],
                "score": float(score),
                "source": _RAG_METADATA[idx]["source"],
            }
        )

    return results


def _build_rag_prompt(
    analysis_payload: dict[str, Any],
    user_query: str,
    retrieved_context: list[dict[str, Any]],
) -> str:
    simulation_payload = json.dumps(analysis_payload, ensure_ascii=True, indent=2)
    context_payload = json.dumps(retrieved_context, ensure_ascii=True, indent=2)

    return (
        "You are LUMI, an environmental intelligence assistant focused on renewable energy "
        "decision support. Use the simulation data and retrieved knowledge to answer the "
        "user's question. Keep the response concise and practical.\n\n"
        "OUTPUT FORMAT: Return ONLY valid JSON with this exact structure:\n"
        "{\n"
        "  \"recommendation\": \"\",\n"
        "  \"cost_breakdown\": {\"equipment\": [], \"installation\": \"\", \"maintenance\": \"\"},\n"
        "  \"estimated_payback\": \"\",\n"
        "  \"limitations\": \"\"\n"
        "}\n\n"
        "SYSTEM CONTEXT: LUMI renewable energy decision support\n\n"
        "SIMULATION DATA:\n"
        f"{simulation_payload}\n\n"
        "RETRIEVED KNOWLEDGE:\n"
        f"{context_payload}\n\n"
        "USER QUESTION:\n"
        f"{user_query}\n"
    )


def _normalize_rag_output(data: dict[str, Any]) -> dict[str, Any]:
    output = {
        "recommendation": "",
        "cost_breakdown": {
            "equipment": [],
            "installation": "",
            "maintenance": "",
        },
        "estimated_payback": "",
        "limitations": "",
    }

    if not isinstance(data, dict):
        return output

    output.update({k: v for k, v in data.items() if k in output})

    if isinstance(data.get("cost_breakdown"), dict):
        output["cost_breakdown"].update(data["cost_breakdown"])

    return output


def analyze_with_rag(
    analysis_payload: dict[str, Any],
    user_query: str,
    top_k: int = 5,
) -> dict[str, Any]:
    try:
        retrieved_context = retrieve_context(user_query, top_k=top_k)
        prompt = _build_rag_prompt(analysis_payload, user_query, retrieved_context)
        response_text = generate_gemini_response(prompt)
        parsed = parse_gemini_json_response(response_text)
        return _normalize_rag_output(parsed)
    except Exception:
        logger.exception("Gemini RAG analysis failed")
        return {
            "recommendation": "Gemini RAG analysis failed.",
            "cost_breakdown": {"equipment": [], "installation": "", "maintenance": ""},
            "estimated_payback": "",
            "limitations": "",
        }
