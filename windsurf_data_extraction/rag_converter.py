"""
rag_converter.py
================
Convert cleaned DOE CSV data into RAG-ready text chunks.

Outputs:
  rag_documents/
    ├── solar_chunks.json
    ├── wind_chunks.json
    ├── hydro_chunks.json
    ├── geothermal_chunks.json
    ├── biomass_chunks.json
    ├── coal_chunks.json
    ├── oil_chunks.json
    ├── natural_gas_chunks.json
    └── general_chunks.json

Each chunk:
  {
    "content": "Human-readable description of the data row...",
    "metadata": {
      "source": "doe_compendium_energy_statistics.pdf",
      "category": "solar",
      "table": "solar_all.csv",
      "row_id": 42,
      "columns": ["region", "capacity_mw", ...]
    }
  }
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = REPO_ROOT / "windsurf_data_extraction" / "csv"
RAG_DIR = REPO_ROOT / "windsurf_data_extraction" / "rag_documents"
RAG_DIR.mkdir(parents=True, exist_ok=True)

# Columns to skip in natural-language generation
_SKIP_COLS = {"source_pdf", "detected_category", "row_id"}


def _row_to_sentence(row: dict[str, Any], category: str) -> str:
    """Turn a data row into a concise natural-language statement."""
    parts: list[str] = []
    region = row.get("region") or row.get("location") or row.get("area") or row.get("province")
    year = row.get("year") or row.get("date") or row.get("period")

    # Build a descriptive sentence
    if region:
        parts.append(f"In {region}")
    if year:
        parts.append(f"for {year}")

    # Add key metrics
    metrics: list[str] = []
    for k, v in row.items():
        if k in _SKIP_COLS or v is None or pd.isna(v):
            continue
        # Try to find numeric + unit pairs
        if k.endswith("_numeric"):
            base = k.replace("_numeric", "")
            unit_key = f"{base}_unit"
            unit = row.get(unit_key)
            val_str = f"{v} {unit}" if unit else str(v)
            metrics.append(f"{base.replace('_', ' ')} was {val_str}")
        elif not k.endswith("_unit") and not k.endswith("_normalized"):
            # Skip raw columns that have a _numeric counterpart
            numeric_key = f"{k}_numeric"
            if numeric_key not in row:
                metrics.append(f"{k.replace('_', ' ')} was {v}")

    if metrics:
        parts.append(", ".join(metrics[:6]))  # limit to avoid overly long chunks

    sentence = ", ".join(p for p in parts if p)
    if not sentence:
        sentence = f"Data point in {category}: " + ", ".join(
            f"{k}={v}" for k, v in row.items() if k not in _SKIP_COLS and pd.notna(v)
        )[:200]
    return sentence.strip() + "."


def _chunk_from_row(
    row: dict[str, Any],
    idx: int,
    source_file: str,
    category: str,
    columns: list[str],
) -> dict[str, Any]:
    """Build a single RAG chunk from a CSV row."""
    return {
        "content": _row_to_sentence(row, category),
        "metadata": {
            "source": row.get("source_pdf", source_file),
            "category": category,
            "table": source_file,
            "row_id": idx,
            "columns": columns,
        },
    }


def convert_csv_to_chunks(csv_path: Path, category: str) -> list[dict[str, Any]]:
    """Read a CSV and turn every row into a RAG chunk."""
    try:
        df = pd.read_csv(csv_path, dtype=str)
    except Exception as exc:
        logger.warning("Could not read %s: %s", csv_path.name, exc)
        return []

    if df.empty:
        return []

    # Add row_id if missing
    if "row_id" not in df.columns:
        df["row_id"] = df.index + 1

    chunks: list[dict[str, Any]] = []
    columns = [c for c in df.columns if c not in _SKIP_COLS]
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        chunk = _chunk_from_row(row_dict, int(idx), csv_path.name, category, columns)
        chunks.append(chunk)

    logger.info("  %s -> %s chunks", csv_path.name, len(chunks))
    return chunks


def run_conversion() -> dict[str, Any]:
    """Convert every CSV in csv/ into RAG JSON files."""
    if not CSV_DIR.exists():
        logger.error("CSV dir not found: %s", CSV_DIR)
        return {}

    all_chunks_by_cat: dict[str, list[dict[str, Any]]] = {}
    total_files = 0

    for cat_dir in CSV_DIR.iterdir():
        if not cat_dir.is_dir():
            continue
        category = cat_dir.name
        for csv_file in cat_dir.glob("*.csv"):
            # Skip mega-consolidated files; they only contain common columns
            # (usually just metadata) and produce empty chunks. The individual
            # *_consolidated_*.csv files have the full schema.
            if csv_file.name.endswith("_all.csv"):
                logger.info("Skipping mega-consolidated file: %s", csv_file.name)
                continue
            chunks = convert_csv_to_chunks(csv_file, category)
            if chunks:
                all_chunks_by_cat.setdefault(category, []).extend(chunks)
                total_files += 1

    # Write per-category JSON
    summary: dict[str, Any] = {"categories": {}, "total_chunks": 0}
    for cat, chunks in all_chunks_by_cat.items():
        out_path = RAG_DIR / f"{cat}_chunks.json"
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(chunks, fh, indent=2, ensure_ascii=False)
        summary["categories"][cat] = {
            "file": str(out_path.relative_to(REPO_ROOT / "windsurf_data_extraction")),
            "chunks": len(chunks),
        }
        summary["total_chunks"] += len(chunks)
        logger.info("Wrote %s (%s chunks)", out_path.name, len(chunks))

    # Also write a master index
    master_path = RAG_DIR / "all_chunks.json"
    all_chunks: list[dict[str, Any]] = []
    for chunks in all_chunks_by_cat.values():
        all_chunks.extend(chunks)
    with master_path.open("w", encoding="utf-8") as fh:
        json.dump(all_chunks, fh, indent=2, ensure_ascii=False)
    summary["master_file"] = str(master_path.relative_to(REPO_ROOT / "windsurf_data_extraction"))
    summary["total_files"] = total_files

    logger.info("RAG conversion complete: %s total chunks", summary["total_chunks"])
    return summary


if __name__ == "__main__":
    run_conversion()
