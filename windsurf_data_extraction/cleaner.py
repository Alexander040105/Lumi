"""
cleaner.py
==========
Data cleaning and normalization pipeline for extracted DOE tables.

Responsibilities:
  - load raw CSVs from raw_tables/
  - normalize column names, dates, numbers, units
  - remove noise (page numbers, footers, duplicate headers)
  - split multi-category tables into focused CSVs
  - export clean CSVs to csv/
"""

from __future__ import annotations

import json
import logging
import re
import shutil
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = REPO_ROOT / "windsurf_data_extraction" / "raw_tables"
OUTPUT_DIR = REPO_ROOT / "windsurf_data_extraction" / "csv"
REPORTS_DIR = REPO_ROOT / "windsurf_data_extraction" / "reports"

for d in (OUTPUT_DIR, REPORTS_DIR):
    d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------


def _clean_header(header) -> str:
    """Normalize column header to snake_case."""
    h = str(header).strip().lower() if header is not None else ""
    h = re.sub(r"[^\w\s]", " ", h)
    h = re.sub(r"\s+", "_", h)
    h = re.sub(r"_+", "_", h)
    h = h.strip("_")
    # Common abbreviations
    h = h.replace("mw", "megawatts")
    h = h.replace("kw", "kilowatts")
    h = h.replace("mwh", "megawatt_hours")
    h = h.replace("kwh", "kilowatt_hours")
    h = h.replace("php", "php")
    h = h.replace("us", "")
    h = h.replace("no_", "number")
    h = h.replace("yr", "year")
    h = h.replace("gen", "generation")
    if not h:
        h = "unnamed"
    return h[:80]


def _parse_number(val: Any) -> float | None:
    """Extract a numeric value from a string, handling commas, parens, units."""
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s:
        return None
    # Remove common wrappers
    s = re.sub(r"[\$,\u20b1\u00a5\u20ac\£]", "", s)  # currency symbols
    s = s.replace(",", "")
    s = s.replace("%", "")
    s = s.replace("(", "-").replace(")", "")
    s = re.sub(r"[A-Za-z/\s]+", "", s)  # strip trailing units like " MW"
    s = s.strip()
    try:
        return float(s)
    except ValueError:
        return None


def _extract_unit(val: Any) -> str | None:
    """Guess the unit from a string value."""
    if pd.isna(val):
        return None
    s = str(val).strip().lower()
    units = [
        ("megawatts", r"\b(mw|megawatt|megawatts)\b"),
        ("kilowatts", r"\b(kw|kilowatt|kilowatts)\b"),
        ("megawatt_hours", r"\b(mwh|megawatt[-_]?hour|megawatt[-_]?hours)\b"),
        ("kilowatt_hours", r"\b(kwh|kilowatt[-_]?hour|kilowatt[-_]?hours)\b"),
        ("gwh", r"\b(gwh)\b"),
        ("php", r"\b(php|\u20b1)\b"),
        ("usd", r"\b(usd|\$)\b"),
        ("percent", r"%"),
        ("tonnes", r"\b(ton|tons|tonne|tonnes|mt)\b"),
        ("hectares", r"\b(ha|hectare|hectares)\b"),
        ("percent", r"\b(percent|pct)\b"),
    ]
    for unit_name, pattern in units:
        if re.search(pattern, s):
            return unit_name
    return None


def _normalize_date(val: Any) -> str | None:
    """Try to normalize a date string to YYYY-MM."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    # Patterns
    # "January 2024" or "Jan 2024"
    m = re.search(r"([A-Za-z]+)\s+(\d{4})", s)
    if m:
        month_str, year = m.group(1), m.group(2)
        month_map = {
            "jan": "01", "january": "01",
            "feb": "02", "february": "02",
            "mar": "03", "march": "03",
            "apr": "04", "april": "04",
            "may": "05",
            "jun": "06", "june": "06",
            "jul": "07", "july": "07",
            "aug": "08", "august": "08",
            "sep": "09", "sept": "09", "september": "09",
            "oct": "10", "october": "10",
            "nov": "11", "november": "11",
            "dec": "12", "december": "12",
        }
        key = month_str.lower()[:3]
        if key in month_map:
            return f"{year}-{month_map[key]}"
    # "2024" alone
    if re.fullmatch(r"\d{4}", s):
        return f"{s}-01"
    # "2024-01" or "2024/01"
    m = re.search(r"(\d{4})[-/](\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return None


def _is_noise_row(row: pd.Series) -> bool:
    """Detect footer / header-repeat / page-number rows."""
    text = " ".join(str(v).strip().lower() for v in row if pd.notna(v))
    noise_patterns = [
        r"^page\s+\d+",
        r"^source:\s",
        r"^note:\s",
        r"^notes:\s",
        r"^\d+\s+of\s+\d+",
        r"^department\s+of\s+energy",
        r"^doe\s",
        r"^republic\s+of\s+the\s+philippines",
        r"^data\s+as\s+of",
        r"^prepared\s+by",
        r"^\d+$",  # lone page number
    ]
    for pat in noise_patterns:
        if re.search(pat, text):
            return True
    return False


def _is_mostly_empty(row: pd.Series, threshold: float = 0.8) -> bool:
    """Return True if > threshold fraction of cells are empty."""
    empty = sum(1 for v in row if pd.isna(v) or str(v).strip() == "")
    return empty / len(row) >= threshold


# ---------------------------------------------------------------------------
# Category detection
# ---------------------------------------------------------------------------


def _detect_category(df: pd.DataFrame, filename: str) -> str:
    """Guess the renewable / energy category from data content + filename."""
    try:
        cols_str = " ".join(str(c) for c in df.columns).lower()
        sample = df.head(10).fillna("").astype(str)
        vals_str = " ".join(sample.values.flatten()).lower()
        text_blob = cols_str + " " + vals_str
    except Exception:
        text_blob = ""
    fname = filename.lower()

    scores: dict[str, int] = {
        "solar": 0, "wind": 0, "hydro": 0,
        "geothermal": 0, "biomass": 0,
        "coal": 0, "oil": 0, "natural_gas": 0,
        "general": 0,
    }

    keywords = {
        "solar": ["solar", "photovoltaic", "pv", "sun", "irradiance", "insolation"],
        "wind": ["wind", "turbine", "windspeed", "wind_speed", "onshore", "offshore"],
        "hydro": ["hydro", "hydropower", "dam", "reservoir", "run-of-river", "pumped storage"],
        "geothermal": ["geothermal", "steam", "binary", "flash"],
        "biomass": ["biomass", "bagasse", "rice husk", "municipal solid waste", "msw"],
        "coal": ["coal", "subcritical", "supercritical", "ultra supercritical"],
        "oil": ["diesel", "oil", "bunker", "fuel oil", "petroleum"],
        "natural_gas": ["natural gas", "lng", "liquefied natural gas", "gas turbine"],
    }

    for cat, words in keywords.items():
        for w in words:
            scores[cat] += text_blob.count(w)
            scores[cat] += fname.count(w) * 3

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"


# ---------------------------------------------------------------------------
# Smart CSV reader
# ---------------------------------------------------------------------------


def _has_title_row(df: pd.DataFrame) -> bool:
    """Heuristic: first row is a title if most cells are empty or it's very long."""
    if df.empty or len(df) < 2:
        return False
    first = df.iloc[0]
    non_empty = sum(1 for v in first if pd.notna(v) and str(v).strip() != "")
    # If only 1 cell is non-empty in first row, it's likely a title
    if non_empty == 1 and len(df.columns) > 1:
        return True
    # If first row text is much longer than second row header text
    first_text_len = sum(len(str(v)) for v in first if pd.notna(v))
    second = df.iloc[1]
    second_text_len = sum(len(str(v)) for v in second if pd.notna(v))
    if first_text_len > second_text_len * 3 and non_empty <= 2:
        return True
    return False


def read_csv_smart(path: Path) -> pd.DataFrame | None:
    """Read a CSV, attempting to skip title rows."""
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=True)
    except Exception:
        return None
    if df.empty:
        return df

    # Try to detect and skip title row(s)
    attempts = 0
    while _has_title_row(df) and attempts < 3 and len(df) > 1:
        # Use second row as header
        new_headers = df.iloc[1]
        df = df.iloc[2:].reset_index(drop=True)
        df.columns = new_headers
        attempts += 1

    # If still looks like title (first row has 1 non-empty cell), skip it
    if _has_title_row(df) and len(df) > 1:
        new_headers = df.iloc[1]
        df = df.iloc[2:].reset_index(drop=True)
        df.columns = new_headers

    return df


# ---------------------------------------------------------------------------
# Core cleaning function
# ---------------------------------------------------------------------------


def clean_table(df: pd.DataFrame, filename: str) -> pd.DataFrame | None:
    """
    Apply full cleaning pipeline to a raw DataFrame.

    Returns cleaned DataFrame or None if table is unusable.
    """
    if df.empty:
        return None

    # --- headers ---
    df.columns = [_clean_header(c) for c in df.columns]

    # --- deduplicate columns ---
    seen: dict[str, int] = {}
    new_cols: list[str] = []
    for c in df.columns:
        if c in seen:
            seen[c] += 1
            new_cols.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            new_cols.append(c)
    df.columns = new_cols

    # --- drop noise rows ---
    mask = df.apply(lambda row: not (_is_noise_row(row) or _is_mostly_empty(row)), axis=1)
    df = df[mask].reset_index(drop=True)

    if df.empty:
        return None

    # --- normalize numeric-looking columns ---
    for col in df.columns:
        # Try to extract numbers
        numeric_vals = df[col].apply(_parse_number)
        non_null = numeric_vals.notna().sum()
        # If >50% of non-empty cells are numeric, create _numeric + _unit columns
        total_non_empty = df[col].apply(lambda x: pd.notna(x) and str(x).strip() != "").sum()
        if total_non_empty > 0 and non_null / total_non_empty >= 0.5:
            df[f"{col}_numeric"] = numeric_vals
            # Try to infer unit from first few non-null values
            units = df[col].apply(_extract_unit)
            most_common = units.mode()
            if len(most_common) > 0 and most_common.iloc[0] is not None:
                df[f"{col}_unit"] = most_common.iloc[0]

    # --- normalize date-like columns ---
    for col in df.columns:
        if "date" in col or "year" in col or "month" in col or "period" in col:
            norm_dates = df[col].apply(_normalize_date)
            if norm_dates.notna().sum() > 0:
                df[f"{col}_normalized"] = norm_dates

    # --- add provenance ---
    df["source_pdf"] = filename
    df["detected_category"] = _detect_category(df, filename)

    return df


# ---------------------------------------------------------------------------
# CSV export by category
# ---------------------------------------------------------------------------


def export_by_category(all_cleaned: list[pd.DataFrame]) -> dict[str, list[Path]]:
    """
    Group cleaned tables by detected category and write consolidated CSVs.
    """
    category_dfs: dict[str, list[pd.DataFrame]] = {}
    for df in all_cleaned:
        cat = str(df["detected_category"].iloc[0]) if "detected_category" in df.columns else "general"
        category_dfs.setdefault(cat, []).append(df)

    exported: dict[str, list[Path]] = {}
    for cat, dfs in category_dfs.items():
        cat_dir = OUTPUT_DIR / cat
        cat_dir.mkdir(parents=True, exist_ok=True)

        # Write individual files
        for idx, df in enumerate(dfs, start=1):
            out_path = cat_dir / f"{cat}_consolidated_{idx:03d}.csv"
            df.to_csv(out_path, index=False, encoding="utf-8-sig")
            exported.setdefault(cat, []).append(out_path)

        # Also write a mega-consolidated file if >1 table
        if len(dfs) > 1:
            try:
                # Only keep columns common to all tables
                common_cols = set(dfs[0].columns)
                for d in dfs[1:]:
                    common_cols &= set(d.columns)
                if common_cols:
                    mega = pd.concat([d[list(common_cols)] for d in dfs], ignore_index=True)
                    mega_path = cat_dir / f"{cat}_all.csv"
                    mega.to_csv(mega_path, index=False, encoding="utf-8-sig")
                    exported.setdefault(cat, []).append(mega_path)
            except Exception as exc:
                logger.warning("Could not build mega-consolidated for %s: %s", cat, exc)

    return exported


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------


def run_cleaning() -> dict[str, Any]:
    csv_files = sorted(INPUT_DIR.glob("*.csv"))
    if not csv_files:
        logger.error("No raw CSVs found in %s", INPUT_DIR)
        return {}

    cleaned: list[pd.DataFrame] = []
    report_rows: list[dict[str, Any]] = []

    for path in csv_files:
        try:
            df = read_csv_smart(path)
            if df is None:
                report_rows.append({
                    "file": path.name,
                    "original_rows": 0,
                    "cleaned_rows": 0,
                    "columns": 0,
                    "category": "error",
                    "error": "Could not read CSV",
                })
                continue
            cleaned_df = clean_table(df, path.name)
            if cleaned_df is not None and not cleaned_df.empty:
                cleaned.append(cleaned_df)
                report_rows.append({
                    "file": path.name,
                    "original_rows": len(df),
                    "cleaned_rows": len(cleaned_df),
                    "columns": len(cleaned_df.columns),
                    "category": cleaned_df["detected_category"].iloc[0],
                })
            else:
                report_rows.append({
                    "file": path.name,
                    "original_rows": len(df),
                    "cleaned_rows": 0,
                    "columns": 0,
                    "category": "discarded",
                })
        except Exception as exc:
            logger.error("Failed to clean %s: %s", path.name, exc)
            report_rows.append({
                "file": path.name,
                "original_rows": 0,
                "cleaned_rows": 0,
                "columns": 0,
                "category": "error",
                "error": str(exc),
            })

    exported = export_by_category(cleaned)

    summary = {
        "raw_files_processed": len(csv_files),
        "tables_cleaned": len(cleaned),
        "tables_discarded": len([r for r in report_rows if r["cleaned_rows"] == 0]),
        "category_counts": {cat: len(dfs) for cat, dfs in {str(df["detected_category"].iloc[0]): [df] for df in cleaned}.items()},
        "files": report_rows,
        "exported_paths": {k: [str(p.relative_to(OUTPUT_DIR)) for p in v] for k, v in exported.items()},
    }

    report_path = REPORTS_DIR / "cleaning_report.json"
    with report_path.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False, default=str)
    logger.info("Cleaning report: %s", report_path)
    return summary


if __name__ == "__main__":
    run_cleaning()
