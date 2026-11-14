import argparse
import csv
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd


DEFAULT_INPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "scraped_data" / "output"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "scraped_data" / "output" / "cleaned"

HEADER_SYNONYMS = {
    "product_name": {"name", "title", "item_name", "product", "listing_name"},
    "price_raw": {"price", "amount", "cost", "price_php", "price_usd"},
    "ratings": {"rating", "stars", "review_score"},
    "reviews": {"review_count", "num_reviews"},
    "url": {"link", "product_url"},
}

POSITIVE_KEYWORDS = {
    "solar": [
        "solar", "pv", "photovoltaic", "panel", "inverter", "charge controller", "mppt",
        "pwm", "battery", "solar battery", "mounting", "microinverter",
        "energy meter", "smart meter",
        # balance-of-system terms seen in PH retailer pricelists
        "cable", "wire", "thhn", "mc4", "connector", "breaker", "fuse",
        "combiner", "enclosure", "distribution", "surge", "spd", "gland",
        "rail", "bracket", "pump", "adaptor", "adapter", "terminal", "lug",
    ],
    "wind": [
        "wind", "turbine", "windmill", "generator", "dump load", "wind controller",
        "wind mppt",
    ],
    "hydro": [
        "hydro", "hydroelectric", "micro hydro", "pelton", "turbine", "water turbine",
        "hydro turbine", "hydro generator",
    ],
}

SUBCATEGORY_KEYWORDS = {
    "solar": {
        "panel": ["panel"],
        "inverter": ["inverter", "microinverter"],
        "charge_controller": ["charge controller", "mppt", "pwm"],
        "battery": ["battery"],
        "combiner_box": ["combiner"],
        "breaker": ["breaker", "fuse", "spd", "surge", "distribution"],
        "pump": ["pump"],
        "enclosure": ["enclosure", "tray", "gland", "box"],
        "cable": ["cable", "wire", "thhn"],
        "accessory": ["mc4", "connector", "adaptor", "adapter", "terminal", "lug", "clip", "clamp"],
        "mounting": ["mounting", "bracket", "rail"],
        "package": ["package", "bundle", "promo", "kit"],
        "meter": ["energy meter", "smart meter"],
    },
    "wind": {
        "turbine": ["turbine", "windmill"],
        "controller": ["controller", "wind mppt", "dump load"],
        "generator": ["generator"],
        "breaker": ["breaker"],
    },
    "hydro": {
        "turbine": ["turbine", "pelton"],
        "controller": ["controller"],
        "generator": ["generator"],
    },
}

EXCLUSION_KEYWORDS = [
    "t-shirt", "shirt", "hoodie", "cap", "hat", "cosmetic", "makeup", "perfume",
    "phone case", "screen protector", "toy", "lego", "game", "book", "poster",
    "ring", "necklace", "bracelet", "watch", "shoe", "sandal", "underwear",
    "bag", "backpack", "dress", "skirt", "jacket", "pant", "shorts",
]

SPAM_PHRASES = [
    "sponsored", "ad", "best seller", "hot sale", "limited offer", "free shipping",
]

# Vendor-reported category labels -> (energy_category, energy_subcategory).
# Checked as substrings against the normalized source_category, in order.
VENDOR_CATEGORY_MAP = [
    ("grid tie inverter", ("solar", "inverter")),
    ("inverter", ("solar", "inverter")),
    ("cable", ("solar", "cable")),
    ("wire", ("solar", "cable")),
    ("breaker", ("solar", "breaker")),
    ("protection", ("solar", "breaker")),
    ("combiner", ("solar", "combiner_box")),
    ("controller", ("solar", "charge_controller")),
    ("meter", ("solar", "meter")),
    ("pump", ("solar", "pump")),
    ("mount", ("solar", "mounting")),
    ("rail", ("solar", "mounting")),
    ("distribution", ("solar", "enclosure")),
    ("enclosure", ("solar", "enclosure")),
    ("promo", ("solar", "package")),
    ("package", ("solar", "package")),
    ("batter", ("solar", "battery")),
    ("storage", ("solar", "battery")),
    ("panel", ("solar", "panel")),
    ("accessor", ("solar", "accessory")),
    ("turbine", ("wind", "turbine")),
    ("wind", ("wind", "turbine")),
]

PLACEHOLDER_PRICES = {"n/a", "na", "none", "contact seller", "negotiable", "0", ""}

CURRENCY_SYMBOLS = {
    "php": ["php", "\u20b1"],
    "usd": ["usd", "us$", "$"]
}


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(levelname)s | %(message)s",
    )


def normalize_header(header: str) -> str:
    return re.sub(r"\s+", "_", header.strip().lower())


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = {col: normalize_header(col) for col in df.columns}
    df = df.rename(columns=normalized)

    reverse_lookup: Dict[str, str] = {}
    for canonical, aliases in HEADER_SYNONYMS.items():
        for alias in aliases:
            reverse_lookup[alias] = canonical

    rename_map = {}
    for col in df.columns:
        if col in reverse_lookup:
            rename_map[col] = reverse_lookup[col]
    df = df.rename(columns=rename_map)

    for canonical in HEADER_SYNONYMS:
        if canonical not in df.columns:
            df[canonical] = ""

    df = df.dropna(axis=1, how="all")
    return df


def sniff_delimiter(sample: str) -> Optional[str]:
    try:
        return csv.Sniffer().sniff(sample).delimiter
    except csv.Error:
        return None


def read_csv_with_fallback(path: Path) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    encodings = ["utf-8", "utf-8-sig", "latin-1"]
    delimiters = [",", "\t", ";"]

    sample = ""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            sample = handle.read(4096)
    except Exception as exc:
        return None, f"read failed: {exc}"

    sniffed = sniff_delimiter(sample)
    if sniffed and sniffed not in delimiters:
        delimiters.insert(0, sniffed)

    for encoding in encodings:
        for delimiter in delimiters:
            try:
                df = pd.read_csv(
                    path,
                    dtype=str,
                    encoding=encoding,
                    encoding_errors="replace",
                    on_bad_lines="skip",
                    sep=delimiter,
                )
                if df.empty:
                    continue
                return df, None
            except Exception:
                continue

    return None, "parse failed with fallback encodings/delimiters"


def validate_file(path: Path) -> Optional[str]:
    if not path.exists():
        return "missing"
    if path.stat().st_size == 0:
        return "empty file"
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            header = handle.readline().strip()
            if not header:
                return "missing header"
    except Exception as exc:
        return f"unreadable: {exc}"
    return None


def normalize_text(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", " ", text)
    for phrase in SPAM_PHRASES:
        cleaned = cleaned.replace(phrase, " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def normalize_name(name: str) -> str:
    if not name:
        return ""
    normalized = normalize_text(name).lower()
    normalized = re.sub(r"[^a-z0-9\s\-]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def detect_currency(price_raw: str, source_site: str) -> str:
    lowered = price_raw.lower()
    for currency, tokens in CURRENCY_SYMBOLS.items():
        if any(token in lowered for token in tokens):
            return currency.upper()
    return "PHP"


def parse_price_value(price_raw: str, source_site: str) -> Tuple[Optional[float], str]:
    if not price_raw:
        return None, ""

    raw_lower = price_raw.strip().lower()
    if raw_lower in PLACEHOLDER_PRICES:
        return None, "placeholder"

    cleaned = re.sub(r"[,$]", "", price_raw)
    cleaned = cleaned.replace("\u20b1", "")
    cleaned = cleaned.replace("PHP", "").replace("php", "")
    cleaned = cleaned.replace("USD", "").replace("usd", "")
    cleaned = cleaned.replace("US$", "").replace("us$", "")

    numbers = re.findall(r"\d+(?:\.\d+)?", cleaned)
    if not numbers:
        return None, "no numeric price"

    values = [float(value) for value in numbers]
    if len(values) >= 2 and ("-" in cleaned or " to " in cleaned.lower()):
        median_value = (min(values) + max(values)) / 2
        return median_value, "range median"

    return values[0], ""


def assign_category(name_normalized: str, source_category: str = "") -> Tuple[Optional[str], Optional[str]]:
    # Trust the vendor's own category label when present (PH retailer sources
    # carry real categories; name-keyword matching is only a fallback).
    if source_category:
        lowered = source_category.lower()
        for needle, (category, vendor_sub) in VENDOR_CATEGORY_MAP:
            if needle in lowered:
                # vendor category decides the energy_category; let the product
                # name refine the subcategory (mixed sections like "Breakers,
                # Wires & Electrical Supplies" hold several kinds of items)
                for sub, keywords in SUBCATEGORY_KEYWORDS.get(category, {}).items():
                    if any(keyword in name_normalized for keyword in keywords):
                        return category, sub
                return category, vendor_sub

    if not name_normalized:
        return None, None

    for keyword in EXCLUSION_KEYWORDS:
        if keyword in name_normalized:
            return None, None

    matched_categories = []
    for category, keywords in POSITIVE_KEYWORDS.items():
        if any(keyword in name_normalized for keyword in keywords):
            matched_categories.append(category)

    if not matched_categories:
        return None, None

    category = matched_categories[0]
    subcategory = None
    for sub, keywords in SUBCATEGORY_KEYWORDS.get(category, {}).items():
        if any(keyword in name_normalized for keyword in keywords):
            subcategory = sub
            break

    return category, subcategory


def is_corrupted_name(name: str) -> bool:
    if not name:
        return True
    if "\ufffd" in name:
        return True
    alnum = sum(ch.isalnum() for ch in name)
    if alnum == 0:
        return True
    if alnum / max(len(name), 1) < 0.3:
        return True
    return False


_SPAM_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(phrase) for phrase in SPAM_PHRASES) + r")\b"
)

# Retailer sources whose pricelists legitimately use terse names ("DEYE",
# "THHN", "Mc4") — only phrase-level spam applies to them.
TRUSTED_NAME_SOURCES = {
    "solarwarehouse", "solarportal", "solarmallph", "prosolar", "rs_components",
}


def is_spam_name(name: str, source: str = "") -> bool:
    lowered = name.lower()
    if _SPAM_RE.search(lowered):
        return True
    if source in TRUSTED_NAME_SOURCES:
        return not lowered.strip()
    if len(lowered) < 4:
        return True
    if len(set(lowered)) <= 3:
        return True
    return False


def dedupe_rows(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    best_by_key: Dict[str, Dict[str, str]] = {}
    for row in rows:
        key_parts = [
            row.get("product_name_normalized", ""),
            str(row.get("price_value", "")),
            row.get("currency", ""),
            row.get("url", ""),
        ]
        key = "|".join(key_parts)
        if key not in best_by_key:
            best_by_key[key] = row
            continue

        current = best_by_key[key]
        current_score = sum(1 for value in current.values() if value not in ("", None))
        candidate_score = sum(1 for value in row.values() if value not in ("", None))
        if candidate_score > current_score:
            best_by_key[key] = row

    return list(best_by_key.values())


def process_file(path: Path, stats: Dict[str, int], rejected_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    error = validate_file(path)
    if error:
        logging.warning("Skipping %s: %s", path.name, error)
        stats["files_skipped"] += 1
        return []

    df, error = read_csv_with_fallback(path)
    if error or df is None:
        logging.warning("Skipping %s: %s", path.name, error or "read failed")
        stats["files_skipped"] += 1
        return []

    df = standardize_columns(df)
    df["source_file"] = path.name
    df["source_site"] = infer_source_site(path.name)

    rows: List[Dict[str, str]] = []
    for _, record in df.iterrows():
        stats["rows_read"] += 1
        row = {key: ("" if pd.isna(value) else str(value).strip()) for key, value in record.items()}
        row["product_name_raw"] = row.get("product_name", "")
        row["product_name"] = normalize_text(row.get("product_name", ""))
        row["product_name_normalized"] = normalize_name(row.get("product_name", ""))

        rejection_reasons = []

        if not row["product_name"]:
            rejection_reasons.append("missing name")
        if is_corrupted_name(row["product_name"]):
            rejection_reasons.append("corrupted name")
        if is_spam_name(row["product_name"], row["source_site"]):
            # trusted retailer rows may carry a bare brand/model name while
            # the spec lives in `description` (e.g. "DEYE" + "8KW")
            details = str(row.get("description") or "").strip()
            if details and len(details) <= 60:
                row["product_name_raw"] = f"{row['product_name'].strip()} {details}".strip()
                row["product_name"] = row["product_name_raw"]
                row["product_name_normalized"] = normalize_name(row["product_name"])
            if is_spam_name(row["product_name"], row["source_site"]):
                rejection_reasons.append("spam name")

        price_raw = row.get("price_raw", "")
        if not price_raw:
            price_raw = row.get("price", "")
        row["price_raw"] = price_raw
        price_value, price_note = parse_price_value(price_raw, row["source_site"])
        if price_note:
            row["price_note"] = price_note
        # Quote-priced rows ("Message for price") are real catalogue items:
        # keep them with price_type=quote instead of rejecting.
        price_type = str(row.get("price_type", "") or "").strip().lower()
        if price_type not in ("fixed", "quote"):
            price_type = "fixed" if price_value is not None else "quote"
        row["price_type"] = price_type
        if price_value is None and price_type != "quote":
            rejection_reasons.append("invalid price")
        row["price_value"] = price_value
        row["currency"] = detect_currency(price_raw, row["source_site"])

        category, subcategory = assign_category(
            row["product_name_normalized"], row.get("source_category", "")
        )
        row["energy_category"] = category
        row["energy_subcategory"] = subcategory
        if not category:
            rejection_reasons.append("non-renewable")

        if rejection_reasons:
            stats["rows_rejected"] += 1
            rejected_rows.append({
                **row,
                "rejection_reason": "; ".join(sorted(set(rejection_reasons))),
            })
            continue

        rows.append(row)

    stats["rows_kept"] += len(rows)
    return rows


SOURCE_SITE_TOKENS = {
    "solarwarehouse": "solarwarehouse",
    "solarportal": "solarportal",
    "solarmallph": "solarmallph",
    "prosolar": "prosolar",
    "rs_wind": "rs_components",
    "amazon": "amazon",
    "lazada": "lazada",
    "alibaba": "alibaba",
    "shopee": "shopee",
}


def infer_source_site(filename: str) -> str:
    lowered = filename.lower()
    for token, site in SOURCE_SITE_TOKENS.items():
        if token in lowered:
            return site
    return "unknown"


def stable_column_order() -> List[str]:
    return [
        "product_name",
        "product_name_raw",
        "product_name_normalized",
        "price_raw",
        "price_value",
        "currency",
        "energy_category",
        "energy_subcategory",
        "source_site",
        "source_file",
        "url",
        "ratings",
        "reviews",
        "source_category",
        "brand",
        "model_number",
        "short_description",
        "description",
        "specs_json",
        "image_url",
        "price_type",
        "price_note",
        "rejection_reason",
    ]


def finalize_dataframe(rows: List[Dict[str, str]], columns: List[str]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    for column in columns:
        if column not in df.columns:
            df[column] = ""
    return df[columns]


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean scraped product CSVs.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    setup_logging(args.log_level)

    input_dir: Path = args.input_dir
    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(input_dir.glob("*.csv"))
    if not csv_files:
        logging.warning("No CSV files found in %s", input_dir)
        return

    stats = {
        "files_processed": 0,
        "files_skipped": 0,
        "rows_read": 0,
        "rows_kept": 0,
        "rows_rejected": 0,
    }

    all_rows: List[Dict[str, str]] = []
    rejected_rows: List[Dict[str, str]] = []

    for path in csv_files:
        stats["files_processed"] += 1
        all_rows.extend(process_file(path, stats, rejected_rows))

    deduped_rows = dedupe_rows(all_rows)

    column_order = stable_column_order()
    cleaned_df = finalize_dataframe(deduped_rows, column_order)
    rejected_df = finalize_dataframe(rejected_rows, column_order)

    cleaned_path = output_dir / "cleaned_products_master.csv"
    rejected_path = output_dir / "cleaned_products_rejected.csv"

    cleaned_df.to_csv(cleaned_path, index=False)
    rejected_df.to_csv(rejected_path, index=False)

    logging.info("Files processed: %s", stats["files_processed"])
    logging.info("Files skipped: %s", stats["files_skipped"])
    logging.info("Rows read: %s", stats["rows_read"])
    logging.info("Rows kept: %s", len(cleaned_df))
    logging.info("Rows rejected: %s", len(rejected_df))
    logging.info("Master dataset: %s", cleaned_path)
    logging.info("Rejected rows: %s", rejected_path)


if __name__ == "__main__":
    main()
