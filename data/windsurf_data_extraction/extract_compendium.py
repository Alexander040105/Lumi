"""
extract_compendium.py
=====================
Optimized extraction for the large DOE Compendium (76MB).
Uses only pdfplumber (skips camelot for speed) and writes in batches.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

import fitz
import pandas as pd
import pdfplumber

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = REPO_ROOT / "regionalData" / "DOE_Data" / "doe_compendium_energy_statistics.pdf"
OUTPUT_DIR = REPO_ROOT / "windsurf_data_extraction"
RAW_TABLES_DIR = OUTPUT_DIR / "raw_tables"
RAW_TEXT_DIR = OUTPUT_DIR / "raw_text"

BATCH_SIZE = 50  # pages per batch


def _slugify(name: str) -> str:
    import re
    base = Path(name).stem
    base = re.sub(r"[^\w\s-]", "", base)
    base = re.sub(r"[-\s]+", "_", base)
    return base.lower().strip("_")[:80]


def extract_compendium() -> dict[str, Any]:
    slug = _slugify(PDF_PATH.name)
    logger.info("Extracting compendium: %s", PDF_PATH.name)

    # Get page count with PyMuPDF
    doc = fitz.open(str(PDF_PATH))
    total_pages = len(doc)
    doc.close()
    logger.info("  Total pages: %s", total_pages)

    all_tables: list[dict[str, Any]] = []
    text_pages: list[dict[str, Any]] = []

    with pdfplumber.open(str(PDF_PATH)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            if page_num % BATCH_SIZE == 0:
                logger.info("  Processing page %s/%s", page_num, total_pages)

            # Extract text
            text = page.extract_text() or ""
            if text.strip():
                text_pages.append({
                    "page_number": page_num,
                    "text": text,
                    "word_count": len(text.split()),
                })

            # Extract tables
            tables = page.find_tables()
            for t_idx, table in enumerate(tables):
                try:
                    df = pd.DataFrame(table.extract())
                    if df.empty:
                        continue
                    if len(df) > 1:
                        headers = [str(c).strip() if c is not None else "" for c in df.iloc[0]]
                        df = df.iloc[1:].reset_index(drop=True)
                        df.columns = headers
                    all_tables.append({
                        "page": page_num,
                        "table_index": t_idx,
                        "columns": list(df.columns),
                        "rows": df.to_dict(orient="records"),
                        "row_count": len(df),
                    })
                except Exception as exc:
                    logger.debug("Table skip on page %s: %s", page_num, exc)

    logger.info("  Extracted %s tables, %s text pages", len(all_tables), len(text_pages))

    # Write tables
    table_paths: list[str] = []
    for idx, table in enumerate(all_tables, start=1):
        df = pd.DataFrame(table["rows"])
        out_name = f"{slug}_table_{idx:04d}_p{table['page']}.csv"
        out_path = RAW_TABLES_DIR / out_name
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        table_paths.append(str(out_path.relative_to(OUTPUT_DIR)))

    # Write text
    text_out_dir = RAW_TEXT_DIR / slug
    text_out_dir.mkdir(parents=True, exist_ok=True)
    for page in text_pages:
        ppath = text_out_dir / f"page_{page['page_number']:04d}.txt"
        ppath.write_text(page["text"], encoding="utf-8")
    full_text = "\n\n---PAGE BREAK---\n\n".join(p["text"] for p in text_pages)
    (text_out_dir / "full_text.txt").write_text(full_text, encoding="utf-8")

    report = {
        "pdf_name": PDF_PATH.name,
        "slug": slug,
        "tables_extracted": len(all_tables),
        "table_files": table_paths,
        "pages": total_pages,
        "text_dir": str(text_out_dir.relative_to(OUTPUT_DIR)),
    }
    logger.info("  Done: %s tables written", len(all_tables))
    return report


if __name__ == "__main__":
    if not PDF_PATH.exists():
        logger.error("PDF not found: %s", PDF_PATH)
        sys.exit(1)
    result = extract_compendium()
    meta_path = OUTPUT_DIR / "compendium_metadata.json"
    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False, default=str)
    logger.info("Metadata: %s", meta_path)
