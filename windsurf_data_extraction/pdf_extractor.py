"""
pdf_extractor.py
================
Multi-strategy PDF table and text extraction pipeline for DOE energy data.

Strategies (in order of preference):
  1. pdfplumber  — best for text-based PDF tables
  2. camelot     — lattice / stream mode for complex tables
  3. PyMuPDF     — fallback text extraction + metadata

Outputs:
  - raw_tables/      : extracted tables as CSV
  - raw_text/        : extracted text per page
  - metadata.json    : PDF metadata and extraction logs
"""

from __future__ import annotations

import csv
import json
import logging
import re
import shutil
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
import pandas as pd
import pdfplumber

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
DOE_DIR = REPO_ROOT / "regionalData" / "DOE_Data"
OUTPUT_DIR = REPO_ROOT / "windsurf_data_extraction"
RAW_TABLES_DIR = OUTPUT_DIR / "raw_tables"
RAW_TEXT_DIR = OUTPUT_DIR / "raw_text"

RAW_TABLES_DIR.mkdir(parents=True, exist_ok=True)
RAW_TEXT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _slugify(name: str) -> str:
    """Create a filesystem-safe slug from a filename."""
    base = Path(name).stem
    base = re.sub(r"[^\w\s-]", "", base)
    base = re.sub(r"[-\s]+", "_", base)
    return base.lower().strip("_")[:80]


def _df_to_csv(df: pd.DataFrame, path: Path) -> None:
    """Write DataFrame to CSV with consistent settings."""
    df.to_csv(path, index=False, encoding="utf-8-sig")


# ---------------------------------------------------------------------------
# pdfplumber extraction
# ---------------------------------------------------------------------------


def extract_with_pdfplumber(pdf_path: Path) -> list[dict[str, Any]]:
    """
    Extract tables from a PDF using pdfplumber.

    Returns a list of dicts:
      {
        "page": int,
        "table_index": int,
        "strategy": "pdfplumber",
        "columns": list,
        "rows": list[dict],
        "row_count": int,
      }
    """
    results: list[dict[str, Any]] = []
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.find_tables()
                for t_idx, table in enumerate(tables):
                    df = pd.DataFrame(table.extract())
                    if df.empty:
                        continue
                    # Use first row as header if it looks like headers
                    if len(df) > 1:
                        headers = [str(c).strip() if c is not None else "" for c in df.iloc[0]]
                        df = df.iloc[1:].reset_index(drop=True)
                        df.columns = headers
                    results.append({
                        "page": page_num,
                        "table_index": t_idx,
                        "strategy": "pdfplumber",
                        "columns": list(df.columns),
                        "rows": df.to_dict(orient="records"),
                        "row_count": len(df),
                    })
    except Exception as exc:
        logger.warning("pdfplumber failed for %s: %s", pdf_path.name, exc)
    return results


# ---------------------------------------------------------------------------
# Camelot extraction
# ---------------------------------------------------------------------------


def extract_with_camelot(pdf_path: Path) -> list[dict[str, Any]]:
    """
    Extract tables using camelot (lattice + stream modes).
    """
    results: list[dict[str, Any]] = []
    try:
        import camelot
    except ImportError:
        logger.warning("camelot not installed; skipping")
        return results

    for flavor in ("lattice", "stream"):
        try:
            tables = camelot.read_pdf(str(pdf_path), flavor=flavor, pages="all")
            for t_idx, table in enumerate(tables):
                df = table.df
                if df.empty:
                    continue
                # Try to promote first row to header
                if len(df) > 1:
                    headers = [str(c).strip() if c is not None else "" for c in df.iloc[0]]
                    df = df.iloc[1:].reset_index(drop=True)
                    df.columns = headers
                results.append({
                    "page": table.page,
                    "table_index": t_idx,
                    "strategy": f"camelot-{flavor}",
                    "columns": list(df.columns),
                    "rows": df.to_dict(orient="records"),
                    "row_count": len(df),
                })
        except Exception as exc:
            logger.warning("camelot-%s failed for %s: %s", flavor, pdf_path.name, exc)
    return results


# ---------------------------------------------------------------------------
# PyMuPDF text extraction
# ---------------------------------------------------------------------------


def extract_text_with_pymupdf(pdf_path: Path) -> dict[str, Any]:
    """
    Extract full text and metadata with PyMuPDF.
    """
    doc = fitz.open(str(pdf_path))
    metadata = doc.metadata
    pages_text: list[dict[str, Any]] = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        pages_text.append({
            "page_number": page_num + 1,
            "text": text,
            "word_count": len(text.split()),
        })
    doc.close()
    return {
        "metadata": metadata,
        "pages": pages_text,
        "total_pages": len(pages_text),
    }


# ---------------------------------------------------------------------------
# Master extractor
# ---------------------------------------------------------------------------


def extract_pdf(pdf_path: Path) -> dict[str, Any]:
    """
    Run the full extraction pipeline on a single PDF.

    Returns extraction report dict.
    """
    slug = _slugify(pdf_path.name)
    logger.info("Extracting: %s", pdf_path.name)

    # --- 1. pdfplumber ---
    plumber_tables = extract_with_pdfplumber(pdf_path)
    logger.info("  pdfplumber: %s tables", len(plumber_tables))

    # --- 2. camelot ---
    camelot_tables = extract_with_camelot(pdf_path)
    logger.info("  camelot: %s tables", len(camelot_tables))

    # Merge tables (deduplicate by row count + first 3 column names)
    all_tables = plumber_tables.copy()
    seen_signatures = set()
    for t in plumber_tables:
        sig = (t["row_count"], tuple(t["columns"][:3]))
        seen_signatures.add(sig)

    for t in camelot_tables:
        sig = (t["row_count"], tuple(t["columns"][:3]))
        if sig not in seen_signatures:
            all_tables.append(t)
            seen_signatures.add(sig)

    # --- 3. PyMuPDF text ---
    text_data = extract_text_with_pymupdf(pdf_path)
    logger.info("  PyMuPDF: %s pages", text_data["total_pages"])

    # --- Write outputs ---
    # Tables as individual CSVs
    table_paths: list[str] = []
    for idx, table in enumerate(all_tables, start=1):
        df = pd.DataFrame(table["rows"])
        out_name = f"{slug}_table_{idx:03d}_p{table['page']}.csv"
        out_path = RAW_TABLES_DIR / out_name
        _df_to_csv(df, out_path)
        table_paths.append(str(out_path.relative_to(OUTPUT_DIR)))

    # Text per page
    text_out_dir = RAW_TEXT_DIR / slug
    text_out_dir.mkdir(parents=True, exist_ok=True)
    for page in text_data["pages"]:
        ppath = text_out_dir / f"page_{page['page_number']:04d}.txt"
        ppath.write_text(page["text"], encoding="utf-8")

    # Full text concatenated
    full_text_path = text_out_dir / "full_text.txt"
    full_text = "\n\n---PAGE BREAK---\n\n".join(p["text"] for p in text_data["pages"])
    full_text_path.write_text(full_text, encoding="utf-8")

    report = {
        "pdf_name": pdf_path.name,
        "slug": slug,
        "tables_extracted": len(all_tables),
        "table_files": table_paths,
        "pages": text_data["total_pages"],
        "text_dir": str(text_out_dir.relative_to(OUTPUT_DIR)),
        "pdf_metadata": text_data["metadata"],
    }
    logger.info("  Done: %s tables -> %s", len(all_tables), RAW_TABLES_DIR.name)
    return report


# ---------------------------------------------------------------------------
# CLI / script entry
# ---------------------------------------------------------------------------


def run_all() -> dict[str, Any]:
    """Extract every PDF in DOE_Data/."""
    pdfs = sorted(DOE_DIR.glob("*.pdf"))
    if not pdfs:
        logger.error("No PDFs found in %s", DOE_DIR)
        return {}

    reports: list[dict[str, Any]] = []
    for pdf in pdfs:
        report = extract_pdf(pdf)
        reports.append(report)

    summary = {
        "pdfs_processed": len(reports),
        "total_tables": sum(r["tables_extracted"] for r in reports),
        "total_pages": sum(r["pages"] for r in reports),
        "per_pdf": reports,
    }

    meta_path = OUTPUT_DIR / "metadata.json"
    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False, default=str)
    logger.info("Summary written to %s", meta_path)
    return summary


if __name__ == "__main__":
    run_all()
