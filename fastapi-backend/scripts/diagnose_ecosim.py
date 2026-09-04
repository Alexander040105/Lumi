"""Diagnose EcoSim for every province that has municipality atlas data.

Calls ``build_ecosim_dashboard_response`` directly in province mode for each
province ID found in the local municipality atlas CSV, so no server or
Supabase dashboard is required.  Prints the first failing province and the
traceback, or a summary of how many provinces succeeded.

Usage:
  cd fastapi-backend
  python scripts/diagnose_ecosim.py
"""
from __future__ import annotations

import csv
import os
import sys
import traceback
from pathlib import Path


def _province_ids() -> list[int]:
    csv_path = Path(__file__).resolve().parents[1] / "app" / "services" / "local_data" / "municipality_atlas_averages.csv"
    province_ids: set[int] = set()
    with csv_path.open(newline="") as f:
        for row in csv.DictReader(f):
            province_ids.add(int(row["province_id"]))
    return sorted(province_ids)


def _call(province_id: int) -> dict | None:
    os.environ.setdefault("USE_REDIS_CACHE", "false")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from app.services.ecosim import build_ecosim_dashboard_response

    try:
        return build_ecosim_dashboard_response(
            municipality_id=province_id,
            monthly_consumption=350,
            monthly_bill=5000,
            electricity_rate=14.29,
            desired_savings=0.5,
            include_ai=False,
            mode="province",
            data_source="auto",
        )
    except Exception:
        print(f"\nFailure for province_id={province_id}")
        traceback.print_exc()
        raise


def main() -> None:
    province_ids = _province_ids()
    print(f"Diagnosing {len(province_ids)} provinces...")

    ok = 0
    first_failure: tuple[int, str] | None = None
    for pid in province_ids:
        try:
            result = _call(pid)
            rec = result.get("recommended_source", "?")
            print(f"  {pid:>4} -> {rec}")
            ok += 1
        except Exception as exc:
            if first_failure is None:
                first_failure = (pid, str(exc))
            # Keep going to surface how many are affected.

    print(f"\n{ok}/{len(province_ids)} provinces succeeded.")
    if first_failure:
        print(f"First failure: province_id={first_failure[0]}, {first_failure[1]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
