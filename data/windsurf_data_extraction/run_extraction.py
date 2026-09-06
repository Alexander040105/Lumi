"""
run_extraction.py
=================
Orchestrator for the full DOE PDF extraction pipeline.

Steps:
  1. pdf_extractor.extract_all()   -> raw_tables/ + raw_text/
  2. cleaner.run_cleaning()        -> csv/
  3. rag_converter.run_conversion() -> rag_documents/
  4. generate data_quality_report.md

Usage:
  python -m data.windsurf_data_extraction.run_extraction
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Ensure imports work when run as module
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from windsurf_data_extraction import pdf_extractor, cleaner, rag_converter

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

REPORTS_DIR = REPO_ROOT / "windsurf_data_extraction" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_quality_report(
    extraction_meta: dict[str, Any],
    cleaning_summary: dict[str, Any],
    rag_summary: dict[str, Any],
) -> Path:
    """Write a human-readable data-quality markdown report."""
    now = datetime.now().isoformat()
    lines: list[str] = [
        "# DOE Data Extraction — Quality Report",
        "",
        f"**Generated:** {now}",
        "",
        "---",
        "",
        "## 1. Overview",
        "",
        f"- **PDFs processed:** {extraction_meta.get('pdfs_processed', 'N/A')}",
        f"- **Total pages:** {extraction_meta.get('total_pages', 'N/A')}",
        f"- **Total raw tables extracted:** {extraction_meta.get('total_tables', 'N/A')}",
        f"- **Tables cleaned & kept:** {cleaning_summary.get('tables_cleaned', 'N/A')}",
        f"- **Tables discarded:** {cleaning_summary.get('tables_discarded', 'N/A')}",
        f"- **RAG chunks generated:** {rag_summary.get('total_chunks', 'N/A')}",
        "",
        "---",
        "",
        "## 2. PDFs Processed",
        "",
    ]

    for pdf_report in extraction_meta.get("per_pdf", []):
        lines.extend([
            f"### {pdf_report['pdf_name']}",
            "",
            f"- **Slug:** `{pdf_report['slug']}`",
            f"- **Pages:** {pdf_report['pages']}",
            f"- **Tables extracted:** {pdf_report['tables_extracted']}",
            f"- **Table files:**",
        ])
        for tf in pdf_report.get("table_files", []):
            lines.append(f"  - `{tf}`")
        lines.append(f"- **Text dir:** `{pdf_report.get('text_dir', 'N/A')}`")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## 3. Cleaning Report",
        "",
    ])

    for row in cleaning_summary.get("files", []):
        lines.append(
            f"| `{row['file']}` | {row['original_rows']} | {row['cleaned_rows']} | "
            f"{row['columns']} | {row['category']} |"
        )
    lines.insert(-len(cleaning_summary.get("files", [])), "| File | Original Rows | Cleaned Rows | Columns | Category |")
    lines.insert(-len(cleaning_summary.get("files", [])), "|------|--------------|--------------|---------|----------|")

    lines.extend([
        "",
        "---",
        "",
        "## 4. RAG Documents",
        "",
    ])
    for cat, info in rag_summary.get("categories", {}).items():
        lines.append(f"- **{cat}:** {info['chunks']} chunks (`{info['file']}`)")
    lines.append("")

    lines.extend([
        "---",
        "",
        "## 5. Assumptions & Notes",
        "",
        "- Numeric values with commas, currency symbols, and percentage signs were stripped and stored in separate `_numeric` and `_unit` columns.",
        "- Dates were normalized to `YYYY-MM` format where possible.",
        "- Rows containing only page numbers, footers, or repeated headers were removed.",
        "- Category detection is heuristic-based on column names and content keywords.",
        "- Tables with >80% empty cells were discarded.",
        "- RAG chunks are generated per-row; each chunk contains a natural-language sentence plus metadata.",
        "",
        "---",
        "",
        "## 6. Extraction Issues",
        "",
    ])

    issues = [r for r in cleaning_summary.get("files", []) if r.get("category") in ("discarded", "error")]
    if issues:
        for row in issues:
            lines.append(f"- `{row['file']}` → {row.get('error', 'discarded (empty/noisy)')}")
    else:
        lines.append("- No major issues detected.")

    lines.append("")

    report_path = REPORTS_DIR / "data_quality_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Quality report: %s", report_path)
    return report_path


def main() -> None:
    logger.info("=" * 60)
    logger.info("STEP 1: PDF EXTRACTION")
    logger.info("=" * 60)
    extraction_meta = pdf_extractor.run_all()

    logger.info("")
    logger.info("=" * 60)
    logger.info("STEP 2: CLEANING & NORMALIZATION")
    logger.info("=" * 60)
    cleaning_summary = cleaner.run_cleaning()

    logger.info("")
    logger.info("=" * 60)
    logger.info("STEP 3: RAG CONVERSION")
    logger.info("=" * 60)
    rag_summary = rag_converter.run_conversion()

    logger.info("")
    logger.info("=" * 60)
    logger.info("STEP 4: QUALITY REPORT")
    logger.info("=" * 60)
    report_path = generate_quality_report(extraction_meta, cleaning_summary, rag_summary)

    logger.info("")
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 60)
    logger.info("Report: %s", report_path)
    logger.info("CSV output: %s", cleaner.OUTPUT_DIR)
    logger.info("RAG output: %s", rag_converter.RAG_DIR)


if __name__ == "__main__":
    main()
