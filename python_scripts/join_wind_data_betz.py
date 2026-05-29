import csv
import json
import math
import os
import re
import statistics
from typing import Dict, Iterable, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRAPED_DIR = os.path.join(BASE_DIR, "scraped_data")
OUTPUT_DIR = os.path.join(SCRAPED_DIR, "output")

OUT_JOINED = os.path.join(OUTPUT_DIR, "wind_products_joined_betz.csv")
OUT_STATS = os.path.join(OUTPUT_DIR, "wind_products_stats_betz.csv")

DEFAULT_WIND_SPEED_MPS = 12.0
DEFAULT_AIR_DENSITY = 1.225

WIND_FILE_PATTERN = re.compile(r"wind", re.IGNORECASE)

POWER_RE = re.compile(
    r"(?<![A-Za-z])(?P<num>\d{1,3}(?:[\d,]{0,3})?(?:\.\d+)?)\s*(?P<unit>mw|kw|w)\b",
    re.IGNORECASE,
)

METER_RE = re.compile(r"(?P<num>\d+(?:\.\d+)?)\s*(?P<unit>m|meter|metre)\b", re.IGNORECASE)
CM_RE = re.compile(r"(?P<num>\d+(?:\.\d+)?)\s*cm\b", re.IGNORECASE)
MM_RE = re.compile(r"(?P<num>\d+(?:\.\d+)?)\s*mm\b", re.IGNORECASE)
IN_RE = re.compile(r"(?P<num>\d+(?:\.\d+)?)\s*(inches|inch|in)\b", re.IGNORECASE)
FT_RE = re.compile(r"(?P<num>\d+(?:\.\d+)?)\s*(ft|feet)\b", re.IGNORECASE)

WIND_SPEED_RE = re.compile(r"(?P<num>\d+(?:\.\d+)?)\s*(m/s|mps)\b", re.IGNORECASE)

BETZ_LIMIT = 16 / 27


def detect_source(filename: str) -> str:
    lower = filename.lower()
    for source in ["amazon", "alibaba", "lazada", "shopee"]:
        if source in lower:
            return source
    return "unknown"


def normalize_text(value: Optional[str]) -> str:
    return (value or "").strip()


def parse_power_w(text: str) -> Optional[float]:
    matches = []
    for match in POWER_RE.finditer(text):
        raw = match.group("num").replace(",", "")
        try:
            num = float(raw)
        except ValueError:
            continue
        unit = match.group("unit").lower()
        if unit == "mw":
            power = num * 1_000_000.0
        elif unit == "kw":
            power = num * 1_000.0
        else:
            power = num
        matches.append(power)
    if not matches:
        return None
    return max(matches)


def parse_diameter_m(text: str) -> Optional[float]:
    candidates: List[float] = []

    for match in METER_RE.finditer(text):
        if "m/s" in text[match.start():match.start() + 6].lower():
            continue
        num = float(match.group("num"))
        candidates.append(num)

    for match in CM_RE.finditer(text):
        num = float(match.group("num"))
        candidates.append(num / 100.0)

    for match in MM_RE.finditer(text):
        num = float(match.group("num"))
        candidates.append(num / 1000.0)

    for match in IN_RE.finditer(text):
        num = float(match.group("num"))
        candidates.append(num * 0.0254)

    for match in FT_RE.finditer(text):
        num = float(match.group("num"))
        candidates.append(num * 0.3048)

    if not candidates:
        return None

    return max(candidates)


def parse_wind_speed_mps(text: str) -> Optional[float]:
    matches = []
    for match in WIND_SPEED_RE.finditer(text):
        try:
            matches.append(float(match.group("num")))
        except ValueError:
            continue

    if not matches:
        return None

    lowered = text.lower()
    for match in WIND_SPEED_RE.finditer(text):
        window = lowered[max(0, match.start() - 12):match.end() + 12]
        if "rated" in window:
            try:
                return float(match.group("num"))
            except ValueError:
                continue

    return max(matches)


def compute_power_coefficient(
    power_w: float,
    diameter_m: float,
    wind_speed_mps: float,
    air_density: float = 1.225,
    clamp_to_betz: bool = False,
) -> Optional[float]:
    if power_w <= 0 or diameter_m <= 0 or wind_speed_mps <= 0:
        return None
    if not 0.9 <= air_density <= 1.3:
        return None

    radius_m = diameter_m / 2.0
    area = math.pi * radius_m ** 2
    available_wind_power = 0.5 * air_density * area * (wind_speed_mps ** 3)
    if available_wind_power <= 0:
        return None

    cp = power_w / available_wind_power

    if clamp_to_betz:
        return min(cp, BETZ_LIMIT)

    return None if cp > BETZ_LIMIT else cp


def read_csv_rows(path: str) -> Iterable[Dict[str, str]]:
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row:
                yield row


def read_json_rows(path: str) -> Iterable[Dict[str, str]]:
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        payload = json.load(handle)

    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                yield item
        return

    if isinstance(payload, dict):
        if "data" in payload and isinstance(payload["data"], list):
            for item in payload["data"]:
                if isinstance(item, dict):
                    yield item
            return


def extract_row_fields(row: Dict[str, str]) -> Tuple[str, str, str, str, str]:
    name = normalize_text(row.get("name") or row.get("title") or row.get("product") or row.get("product_name"))
    price = normalize_text(row.get("price") or row.get("price_value") or row.get("sale_price"))
    ratings = normalize_text(row.get("ratings") or row.get("rating"))
    reviews = normalize_text(row.get("reviews") or row.get("review_count"))
    url = normalize_text(row.get("url") or row.get("link") or row.get("product_url"))
    return name, price, ratings, reviews, url


def find_wind_files(root_dir: str) -> List[str]:
    paths: List[str] = []
    for root, _dirs, files in os.walk(root_dir):
        for filename in files:
            if not WIND_FILE_PATTERN.search(filename):
                continue
            ext = os.path.splitext(filename)[1].lower()
            if ext not in {".csv", ".json"}:
                continue
            paths.append(os.path.join(root, filename))
    return sorted(paths)


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    rows: List[Dict[str, str]] = []
    wind_files = find_wind_files(SCRAPED_DIR)

    for path in wind_files:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".csv":
            source_rows = read_csv_rows(path)
        else:
            source_rows = read_json_rows(path)

        for row in source_rows:
            name, price, ratings, reviews, url = extract_row_fields(row)
            raw_text = " ".join([name, price, ratings, reviews, url])
            power_w = parse_power_w(raw_text)
            diameter_m = parse_diameter_m(raw_text)
            wind_speed = parse_wind_speed_mps(raw_text) or DEFAULT_WIND_SPEED_MPS

            rotor_radius = diameter_m / 2.0 if diameter_m else ""
            power_coeff = ""
            if power_w and diameter_m:
                cp = compute_power_coefficient(
                    power_w,
                    diameter_m,
                    wind_speed,
                    air_density=DEFAULT_AIR_DENSITY,
                    clamp_to_betz=False,
                )
                if cp is not None:
                    power_coeff = cp

            rows.append({
                "source_file": os.path.relpath(path, SCRAPED_DIR).replace("\\", "/"),
                "source_site": detect_source(path),
                "name": name,
                "price": price,
                "ratings": ratings,
                "reviews": reviews,
                "url": url,
                "power_w": f"{power_w:.2f}" if power_w is not None else "",
                "diameter_m": f"{diameter_m:.3f}" if diameter_m is not None else "",
                "rotor_radius_m": f"{rotor_radius:.3f}" if diameter_m is not None else "",
                "wind_speed_mps": f"{wind_speed:.2f}" if wind_speed else "",
                "power_coefficient": f"{power_coeff:.3f}" if isinstance(power_coeff, float) else "",
            })

    fieldnames = [
        "source_file",
        "source_site",
        "name",
        "price",
        "ratings",
        "reviews",
        "url",
        "power_w",
        "diameter_m",
        "rotor_radius_m",
        "wind_speed_mps",
        "power_coefficient",
    ]

    with open(OUT_JOINED, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    rotor_values = [float(r["rotor_radius_m"]) for r in rows if r["rotor_radius_m"]]
    cp_values = [float(r["power_coefficient"]) for r in rows if r["power_coefficient"]]

    avg_rotor = statistics.mean(rotor_values) if rotor_values else 0.0
    avg_cp = statistics.mean(cp_values) if cp_values else 0.0

    with open(OUT_STATS, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "records_total",
            "records_with_rotor_radius",
            "records_with_power_coefficient",
            "avg_rotor_radius_m",
            "avg_power_coefficient",
        ])
        writer.writeheader()
        writer.writerow({
            "records_total": len(rows),
            "records_with_rotor_radius": len(rotor_values),
            "records_with_power_coefficient": len(cp_values),
            "avg_rotor_radius_m": f"{avg_rotor:.3f}",
            "avg_power_coefficient": f"{avg_cp:.3f}",
        })

    print(f"Joined {len(rows)} rows from {len(wind_files)} wind files")
    print(
        "Average rotor radius (m): "
        f"{avg_rotor:.3f} from {len(rotor_values)} rows where a blade diameter was parsed "
        "from text (m/cm/mm/in/ft), then divided by 2."
    )
    print(
        "Average power coefficient: "
        f"{avg_cp:.3f} from {len(cp_values)} rows with both parsed power (W/kW/MW) and diameter; "
        f"uses Cp = P / (0.5 * {DEFAULT_AIR_DENSITY} * A * V^3) with V={DEFAULT_WIND_SPEED_MPS} m/s unless a m/s value is present."
    )


if __name__ == "__main__":
    main()
