import argparse
import json
import logging
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd


DEFAULT_INPUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scraped_data"
    / "output"
    / "cleaned"
    / "cleaned_products_master.csv"
)
DEFAULT_OUTPUT_DIR = (
    Path(__file__).resolve().parents[1]
    / "scraped_data"
    / "output"
    / "rag_ready"
)

CANONICAL_COLUMNS = [
    "product_name",
    "description",
    "category",
    "subcategory",
    "price_value",
    "price_raw",
    "currency",
    "source",
    "seller",
    "location",
    "url",
    "ratings",
    "reviews",
    "source_file",
]

COLUMN_MAP = {
    "energy_category": "category",
    "energy_subcategory": "subcategory",
    "source_site": "source",
}

RENEWABLE_KEYWORDS = {
    "solar": ["solar", "pv", "photovoltaic", "panel", "inverter", "charge controller", "mppt", "pwm"],
    "wind": ["wind", "turbine", "windmill", "generator", "wind controller", "dump load"],
    "hydro": ["hydro", "hydroelectric", "micro hydro", "pelton", "water turbine", "hydro turbine"],
}

PRODUCT_TYPE_KEYWORDS = {
    "panel": ["panel"],
    "inverter": ["inverter", "microinverter"],
    "battery": ["battery"],
    "controller": ["controller", "mppt", "pwm", "dump load"],
    "turbine": ["turbine", "windmill", "pelton"],
    "generator": ["generator"],
    "mounting_system": ["mounting", "bracket", "rack"],
    "meter": ["energy meter", "smart meter"],
}

DROP_REASONS = [
    "missing_name",
    "short_name",
    "invalid_price",
    "missing_category",
]


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(levelname)s | %(message)s",
    )


def normalize_text(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", " ", text)
    cleaned = re.sub(r"&[a-zA-Z]+;", " ", cleaned)
    cleaned = re.sub(r"[\r\n\t]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def normalize_for_match(text: str) -> str:
    if not text:
        return ""
    cleaned = normalize_text(text).lower()
    cleaned = re.sub(r"[^a-z0-9\s\-\.\+/]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def normalize_name(name: str) -> str:
    if not name:
        return ""
    cleaned = normalize_for_match(name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def coerce_price(value: str) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).strip()
    if cleaned == "":
        return None
    cleaned = re.sub(r"[^0-9\.]+", "", cleaned)
    if cleaned == "":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def enrich_category(name_normalized: str, category: str) -> str:
    if category:
        return category
    for renewable, keywords in RENEWABLE_KEYWORDS.items():
        if any(keyword in name_normalized for keyword in keywords):
            return renewable
    return ""


def infer_product_type(name_normalized: str) -> str:
    for product_type, keywords in PRODUCT_TYPE_KEYWORDS.items():
        if any(keyword in name_normalized for keyword in keywords):
            return product_type
    return ""


def tokenize(text: str) -> List[str]:
    return [token for token in re.split(r"\W+", text) if token]


def token_set_similarity(a: str, b: str) -> float:
    tokens_a = set(tokenize(a))
    tokens_b = set(tokenize(b))
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a.intersection(tokens_b)
    union = tokens_a.union(tokens_b)
    return len(intersection) / max(len(union), 1)


def build_document(row: Dict[str, str]) -> str:
    return (
        f"{row['product_name']}. "
        f"Category: {row.get('category', '')}/{row.get('subcategory', '')}. "
        f"Renewable: {row.get('renewable_type', '')}. "
        f"Type: {row.get('product_type', '')}. "
        f"Price: {row.get('currency', '')} {row.get('price_value', '')}. "
        f"Source: {row.get('source', '')}. "
        f"Ratings: {row.get('ratings', '')} ({row.get('reviews', '')} reviews). "
        f"URL: {row.get('url', '')}."
    ).strip()


def sentence_split(text: str) -> List[str]:
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [part.strip() for part in parts if part.strip()]


def chunk_document(text: str, max_words: int, overlap_ratio: float) -> List[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]

    sentences = sentence_split(text)
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0
    target_overlap = int(max_words * overlap_ratio)

    for sentence in sentences:
        sentence_words = sentence.split()
        if current_len + len(sentence_words) > max_words and current:
            chunks.append(" ".join(current))
            overlap = current[-target_overlap:] if target_overlap > 0 else []
            current = overlap + sentence_words
            current_len = len(current)
        else:
            current.extend(sentence_words)
            current_len += len(sentence_words)

    if current:
        chunks.append(" ".join(current))
    return chunks


def completeness_score(row: Dict[str, str]) -> int:
    return sum(1 for value in row.values() if value not in ("", None))


def exact_dedupe(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    best_by_key: Dict[str, Dict[str, str]] = {}
    for row in rows:
        key = "|".join([
            row.get("product_name_normalized", ""),
            str(row.get("price_value", "")),
            row.get("source", ""),
            row.get("url", ""),
        ])
        existing = best_by_key.get(key)
        if not existing or completeness_score(row) > completeness_score(existing):
            best_by_key[key] = row
    return list(best_by_key.values())


def near_dedupe(rows: List[Dict[str, str]], threshold: float) -> List[Dict[str, str]]:
    kept: List[Dict[str, str]] = []
    for row in rows:
        name_norm = row.get("product_name_normalized", "")
        price = row.get("price_value", "")
        source = row.get("source", "")
        is_duplicate = False
        for existing in kept:
            if existing.get("source") != source:
                continue
            if existing.get("price_value") != price:
                continue
            similarity = token_set_similarity(name_norm, existing.get("product_name_normalized", ""))
            if similarity >= threshold:
                if completeness_score(row) > completeness_score(existing):
                    kept.remove(existing)
                    kept.append(row)
                is_duplicate = True
                break
        if not is_duplicate:
            kept.append(row)
    return kept


def flatten_metadata(row: Dict[str, str]) -> Dict[str, object]:
    metadata = {
        "category": row.get("category", ""),
        "subcategory": row.get("subcategory", ""),
        "renewable_type": row.get("renewable_type", ""),
        "product_type": row.get("product_type", ""),
        "price_value": row.get("price_value"),
        "currency": row.get("currency", ""),
        "source": row.get("source", ""),
        "seller": row.get("seller", ""),
        "location": row.get("location", ""),
        "ratings": row.get("ratings", ""),
        "reviews": row.get("reviews", ""),
        "url": row.get("url", ""),
        "source_file": row.get("source_file", ""),
    }
    return metadata


def load_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    df = df.rename(columns={column: column.strip().lower() for column in df.columns})
    df = df.rename(columns={key: value for key, value in COLUMN_MAP.items() if key in df.columns})
    for column in CANONICAL_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df


def process_rows(
    df: pd.DataFrame,
    max_words: int,
    overlap_ratio: float,
    near_dedupe_threshold: float,
) -> Tuple[List[Dict[str, str]], Dict[str, int], int]:
    drop_counts = {reason: 0 for reason in DROP_REASONS}
    rows: List[Dict[str, str]] = []
    chunked_count = 0

    for _, record in df.iterrows():
        row = {key: ("" if pd.isna(value) else str(value).strip()) for key, value in record.items()}
        row["product_name"] = normalize_text(row.get("product_name", ""))
        row["product_name_normalized"] = normalize_name(row.get("product_name", ""))
        row["description"] = normalize_text(row.get("description", ""))

        if not row["product_name"]:
            drop_counts["missing_name"] += 1
            continue
        if len(row["product_name_normalized"]) < 4:
            drop_counts["short_name"] += 1
            continue

        row["price_value"] = coerce_price(row.get("price_value", ""))
        if row["price_value"] is None:
            drop_counts["invalid_price"] += 1
            continue

        row["currency"] = row.get("currency", "") or "PHP"
        row["category"] = enrich_category(row["product_name_normalized"], row.get("category", ""))
        row["subcategory"] = row.get("subcategory", "")
        row["renewable_type"] = row["category"]
        row["product_type"] = infer_product_type(row["product_name_normalized"])

        if not row["category"]:
            drop_counts["missing_category"] += 1
            continue

        row["document_text"] = build_document(row)
        row["summary"] = row["document_text"].split(".")[0].strip() + "."

        chunks = chunk_document(row["document_text"], max_words, overlap_ratio)
        if len(chunks) > 1:
            chunked_count += 1

        row["chunks"] = chunks
        rows.append(row)

    exact = exact_dedupe(rows)
    near = near_dedupe(exact, near_dedupe_threshold)
    deduped_count = len(rows) - len(near)

    return near, drop_counts, chunked_count


def export_files(
    rows: List[Dict[str, str]],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    rag_rows = []
    documents = []
    jsonl_path = output_dir / "chromadb_ready.jsonl"

    with jsonl_path.open("w", encoding="utf-8") as jsonl_handle:
        for index, row in enumerate(rows, start=1):
            metadata = flatten_metadata(row)
            doc_id = f"prod_{index:06d}"

            rag_row = {key: row.get(key, "") for key in CANONICAL_COLUMNS}
            rag_row.update({
                "renewable_type": row.get("renewable_type", ""),
                "product_type": row.get("product_type", ""),
                "document_text": row.get("document_text", ""),
                "summary": row.get("summary", ""),
                "doc_id": doc_id,
            })
            rag_rows.append(rag_row)

            documents.append({
                "id": doc_id,
                "text": row.get("document_text", ""),
                "metadata": metadata,
            })

            jsonl_handle.write(json.dumps({
                "id": doc_id,
                "text": row.get("document_text", ""),
                "metadata": metadata,
            }, ensure_ascii=True) + "\n")

    pd.DataFrame(rag_rows).to_csv(output_dir / "rag_ready.csv", index=False)

    with (output_dir / "rag_documents.json").open("w", encoding="utf-8") as handle:
        json.dump(documents, handle, ensure_ascii=True, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare RAG-ready product dataset.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-words", type=int, default=160)
    parser.add_argument("--overlap", type=float, default=0.15)
    parser.add_argument("--near-dedupe-threshold", type=float, default=0.85)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    setup_logging(args.log_level)

    if not args.input.exists():
        logging.error("Input file not found: %s", args.input)
        return

    df = load_dataset(args.input)
    rows, drop_counts, chunked_count = process_rows(
        df,
        max_words=args.max_words,
        overlap_ratio=args.overlap,
        near_dedupe_threshold=args.near_dedupe_threshold,
    )

    export_files(rows, args.output_dir)

    logging.info("Rows loaded: %s", len(df))
    logging.info("Rows kept: %s", len(rows))
    logging.info("Chunked documents: %s", chunked_count)
    for reason, count in drop_counts.items():
        logging.info("Dropped (%s): %s", reason, count)


if __name__ == "__main__":
    main()
