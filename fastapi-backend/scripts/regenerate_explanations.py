"""One-time backfill for municipality_renewable_explanations.

Recomputes EcoSim for each requested municipality with `use_cache=False` so the
`_get_or_build_explanations` guard regenerates and overwrites any stale cached
explanation text.

Usage:
  cd fastapi-backend
  set PYTHONPATH=.
  # Regenerate every municipality
  python scripts/regenerate_explanations.py --all
  # Regenerate only municipalities with known mismatches
  python scripts/regenerate_explanations.py --mismatches-only
  # Regenerate specific IDs
  python scripts/regenerate_explanations.py --municipality-ids 5441,5442
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from pathlib import Path

# Allow imports from fastapi-backend/app
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.services.ecosim import renewable_energy_calculator
from app.services.supabase_service import get_supabase_client

MISMATCH_CSV = BASE_DIR.parent / "docs" / "04-ML-Data-Science" / "explanation_mismatches.csv"
REPORT_PATH = BASE_DIR.parent / "docs" / "04-ML-Data-Science" / "regenerate_explanations_report.md"

BILL = 5000.0
RATE = 14.29
SAVINGS = 0.5


def get_all_municipalities() -> list[dict]:
    client = get_supabase_client()
    all_items: list[dict] = []
    batch_size = 1000
    offset = 0
    while True:
        resp = (
            client.table("municipalities")
            .select("municipality_id,name,province_id")
            .order("municipality_id")
            .range(offset, offset + batch_size - 1)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            break
        all_items.extend(rows)
        offset += batch_size
        if len(rows) < batch_size:
            break
    return all_items


def get_mismatched_ids() -> list[dict]:
    if not MISMATCH_CSV.exists():
        print(f"Mismatches file not found: {MISMATCH_CSV}")
        return []
    ids: set[int] = set()
    with MISMATCH_CSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ids.add(int(row["municipality_id"]))
            except (KeyError, ValueError):
                continue
    client = get_supabase_client()
    items: list[dict] = []
    for muni_id in sorted(ids):
        resp = (
            client.table("municipalities")
            .select("municipality_id,name")
            .eq("municipality_id", muni_id)
            .single()
            .execute()
        )
        if resp.data:
            items.append(resp.data)
    return items


def get_specific_ids(ids_str: str) -> list[dict]:
    requested = {int(x.strip()) for x in ids_str.split(",") if x.strip().isdigit()}
    client = get_supabase_client()
    items: list[dict] = []
    for muni_id in sorted(requested):
        resp = (
            client.table("municipalities")
            .select("municipality_id,name")
            .eq("municipality_id", muni_id)
            .single()
            .execute()
        )
        if resp.data:
            items.append(resp.data)
    return items


def regenerate(item: dict) -> tuple[bool, str]:
    muni_id = item["municipality_id"]
    name = item.get("name", "?")
    try:
        renewable_energy_calculator(
            house="regenerate",
            municipality=name,
            municipality_id=muni_id,
            current_electricity_bill=BILL,
            electricity_rate=RATE,
            desired_savings=SAVINGS,
            mode="municipality",
            include_ai=False,
            use_cache=False,
        )
        return True, ""
    except Exception as exc:
        return False, str(exc)


def write_report(total: int, ok: int, errors: int, error_log: list[tuple[int, str, str]], elapsed: float) -> None:
    parent = REPORT_PATH.parent
    parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", encoding="utf-8") as f:
        f.write("# Regenerate Municipality Explanations Report\n\n")
        f.write(f"- Total processed: {total}\n")
        f.write(f"- Successful: {ok}\n")
        f.write(f"- Errors: {errors}\n")
        f.write(f"- Elapsed: {elapsed:.1f}s\n\n")
        if error_log:
            f.write("## Errors\n\n")
            f.write("| municipality_id | name | error |\n")
            f.write("|-----------------|------|-------|\n")
            for muni_id, name, err in error_log:
                f.write(f"| {muni_id} | {name} | {err} |\n")
        else:
            f.write("No errors.\n")
    print(f"\nReport written to {REPORT_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate cached EcoSim explanations.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Regenerate every municipality.")
    group.add_argument("--mismatches-only", action="store_true", help="Regenerate only municipalities with mismatches.")
    group.add_argument("--municipality-ids", type=str, help="Comma-separated municipality IDs to regenerate.")
    args = parser.parse_args()

    if args.all:
        items = get_all_municipalities()
    elif args.mismatches_only:
        items = get_mismatched_ids()
    else:
        items = get_specific_ids(args.municipality_ids)

    if not items:
        print("No municipalities to regenerate.")
        return 0

    print(f"Regenerating explanations for {len(items)} municipalities...")
    ok = 0
    errors = 0
    error_log: list[tuple[int, str, str]] = []
    start = time.time()

    for i, item in enumerate(items):
        success, err = regenerate(item)
        if success:
            ok += 1
        else:
            errors += 1
            error_log.append((item["municipality_id"], item.get("name", "?"), err))
        if (i + 1) % 50 == 0 or i + 1 == len(items):
            print(f"  Progress: {i + 1}/{len(items)} ({100 * (i + 1) / len(items):.0f}%) — ok={ok}, errors={errors}")

    elapsed = time.time() - start
    write_report(len(items), ok, errors, error_log, elapsed)
    print(f"Done: {ok}/{len(items)} ok, {errors} errors in {elapsed:.1f}s")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
