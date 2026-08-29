"""Check for stale EcoSim per-source explanations across all municipalities.

Compares the text embedded in `municipality_renewable_explanations` against the
numeric outputs from the most recent `calibration_all_results.csv` (the ground
truth for what the live calculation produces). Writes a CSV of mismatches and a
short markdown report.

Usage:
  cd fastapi-backend
  set PYTHONPATH=.
  python scripts/check_explanation_mismatches.py
"""
from __future__ import annotations

import csv
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path

# Allow imports from fastapi-backend/app
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.services.supabase_service import get_supabase_client

CALIBRATION_CSV = BASE_DIR.parent / "docs" / "04-ML-Data-Science" / "calibration_all_results.csv"
OUTPUT_DIR = BASE_DIR.parent / "docs" / "04-ML-Data-Science"

SOURCE_PATTERNS = {
    "solar": re.compile(r"produces\s+([0-9]+(?:\.[0-9]+)?)\s+kWh/month"),
    "wind": re.compile(r"generates\s+([0-9]+(?:\.[0-9]+)?)\s+kWh/month"),
    "hydro": re.compile(r"produce\s+([0-9]+(?:\.[0-9]+)?)\s+kWh monthly"),
}


def load_calibration(csv_path: Path) -> dict[int, dict]:
    """Return a dict of municipality_id -> row from the latest calibration CSV."""
    by_id: dict[int, dict] = {}
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("mode") != "municipality":
                continue
            try:
                muni_id = int(row["geo_id"])
            except (KeyError, ValueError):
                continue
            by_id[muni_id] = row
    return by_id


def fetch_explanations() -> dict[int, dict]:
    """Fetch all rows from the municipality_renewable_explanations table."""
    client = get_supabase_client()
    all_rows: list[dict] = []
    batch_size = 1000
    offset = 0
    while True:
        resp = (
            client.table("municipality_renewable_explanations")
            .select("*")
            .range(offset, offset + batch_size - 1)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            break
        all_rows.extend(rows)
        offset += batch_size
        if len(rows) < batch_size:
            break
    return {int(row["municipality_id"]): row for row in all_rows}


def parse_text_number(text: str | None, pattern: re.Pattern) -> float | None:
    """Return the monthly kWh number embedded in the text, or None."""
    if not text:
        return None
    match = pattern.search(text)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def check_mismatches(
    calibration: dict[int, dict],
    explanations: dict[int, dict],
    tolerance: float = 0.15,
) -> list[dict]:
    """Compare cached explanations to calibration outputs and return mismatches."""
    mismatches: list[dict] = []
    output_keys = {
        "solar": "solar_kwh",
        "wind": "wind_kwh",
        "hydro": "hydro_kwh",
    }

    for muni_id, cal_row in sorted(calibration.items()):
        name = cal_row.get("name", "?")
        exp_row = explanations.get(muni_id)
        if not exp_row:
            mismatches.append(
                {
                    "municipality_id": muni_id,
                    "name": name,
                    "source": "any",
                    "output_kwh": None,
                    "explanation_kwh": None,
                    "diff": None,
                    "status": "missing_cache_row",
                }
            )
            continue

        for source, csv_key in output_keys.items():
            try:
                output = float(cal_row.get(csv_key) or 0.0)
            except (TypeError, ValueError):
                output = 0.0

            text = exp_row.get(source) or ""
            text_num = parse_text_number(text, SOURCE_PATTERNS[source])

            if output == 0.0:
                # When output is zero, the explanation should not contain a number.
                if text_num is not None and not math.isclose(text_num, 0.0, abs_tol=tolerance):
                    mismatches.append(
                        {
                            "municipality_id": muni_id,
                            "name": name,
                            "source": source,
                            "output_kwh": output,
                            "explanation_kwh": text_num,
                            "diff": text_num,
                            "status": "stale",
                        }
                    )
                continue

            expected = round(output, 1)
            if text_num is None:
                mismatches.append(
                    {
                        "municipality_id": muni_id,
                        "name": name,
                        "source": source,
                        "output_kwh": output,
                        "explanation_kwh": None,
                        "diff": None,
                        "status": "missing_number",
                    }
                )
                continue

            if not math.isclose(text_num, expected, abs_tol=tolerance):
                mismatches.append(
                    {
                        "municipality_id": muni_id,
                        "name": name,
                        "source": source,
                        "output_kwh": output,
                        "explanation_kwh": text_num,
                        "diff": text_num - expected,
                        "status": "stale",
                    }
                )

    return mismatches


def write_outputs(mismatches: list[dict]) -> tuple[Path, Path]:
    """Write CSV and markdown reports."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT_DIR / "explanation_mismatches.csv"
    report_path = OUTPUT_DIR / "explanation_mismatch_report.md"

    fieldnames = [
        "municipality_id",
        "name",
        "source",
        "output_kwh",
        "explanation_kwh",
        "diff",
        "status",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in mismatches:
            writer.writerow(row)

    total = len(mismatches)
    by_source = Counter(m["source"] for m in mismatches)
    by_status = Counter(m["status"] for m in mismatches)

    with report_path.open("w", encoding="utf-8") as f:
        f.write("# EcoSim Explanation/Output Mismatch Report\n\n")
        f.write(f"**Total issues found:** {total}\n\n")
        f.write("## By source\n\n")
        for source, count in by_source.most_common():
            f.write(f"- {source}: {count}\n")
        f.write("\n## By status\n\n")
        for status, count in by_status.most_common():
            f.write(f"- {status}: {count}\n")
        f.write("\n## Sample issues (first 20)\n\n")
        f.write("| municipality_id | name | source | output_kwh | explanation_kwh | status |\n")
        f.write("|-----------------|------|--------|-----------:|----------------:|--------|\n")
        for m in mismatches[:20]:
            out = f"{m['output_kwh']:.3f}" if m['output_kwh'] is not None else "-"
            exp = f"{m['explanation_kwh']:.3f}" if m['explanation_kwh'] is not None else "-"
            f.write(
                f"| {m['municipality_id']} | {m['name']} | {m['source']} | "
                f"{out} | {exp} | {m['status']} |\n"
            )
        f.write(f"\n**Full list:** `{csv_path.name}`\n")

    return csv_path, report_path


def main() -> int:
    print(f"Loading calibration from {CALIBRATION_CSV}...")
    calibration = load_calibration(CALIBRATION_CSV)
    print(f"  {len(calibration)} municipalities in calibration CSV")

    print("Fetching cached explanations from Supabase...")
    explanations = fetch_explanations()
    print(f"  {len(explanations)} cached explanation rows")

    print("Comparing cached text to calibration outputs...")
    mismatches = check_mismatches(calibration, explanations)

    csv_path, report_path = write_outputs(mismatches)
    print(f"\nWrote {len(mismatches)} mismatches to:")
    print(f"  {csv_path}")
    print(f"  {report_path}")

    if mismatches:
        print("\nIssues by source:")
        for source, count in Counter(m["source"] for m in mismatches).most_common():
            print(f"  {source}: {count}")
    return 0 if not mismatches else 1


if __name__ == "__main__":
    raise SystemExit(main())
