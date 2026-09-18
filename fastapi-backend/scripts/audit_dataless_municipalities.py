"""Audit municipalities that have no climate data, and optionally delete them.

Municipalities with no row in ``municipality_climate_averages`` can't run the
simulator and surface as stale "City of X" duplicates in the picker. The API
already hides them (``list_municipalities`` filter); this script reports them
and can delete the ones nothing else references.

Tables are audited against a code-derived list because the committed schema
dumps are incomplete — any table here that lacks a ``municipality_id`` column
is skipped rather than treated as an error.

Dry-run by default — prints the report and makes NO writes:

  cd fastapi-backend
  python scripts/audit_dataless_municipalities.py

Delete only rows with zero references:

  python scripts/audit_dataless_municipalities.py --apply
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_repo / "fastapi-backend"))

from dotenv import load_dotenv

load_dotenv(dotenv_path=_repo / ".env")

BATCH = 1000

# Tables that hold municipality_id references in this codebase. Audited
# tolerantly: a table missing the column is skipped, not fatal.
REFERENCE_TABLES = [
    "barangays",
    "ecosim_ai_cache",
    "geospatial_metadata",
    "geothermal_output",
    "geothermal_suitability",
    "hydropower_suitability",
    "municipal_population",
    "municipality_atlas_averages",
    "municipality_catchment_enrichment",
    "municipality_climate_monthly",
    "municipality_era5_averages",
    "municipality_renewable_explanations",
    "saved_simulations",
    "user_ecosim_logs",
]


def _paged_column(client, table: str, column: str) -> list:
    rows = []
    offset = 0
    while True:
        resp = client.table(table).select(column).range(offset, offset + BATCH - 1).execute()
        batch = resp.data or []
        rows.extend(batch)
        if len(batch) < BATCH:
            return rows
        offset += BATCH


def _climate_ids(client) -> set[int]:
    ids = {
        row["municipality_id"]
        for row in _paged_column(client, "municipality_climate_averages", "municipality_id")
        if row.get("municipality_id") is not None
    }
    # Union the bundled CSV fallback — the simulator reads it when the table
    # has no rows, so those municipalities are not "data-less".
    csv_path = _repo / "fastapi-backend" / "app" / "services" / "local_data" / "municipality_climate_averages.csv"
    if csv_path.exists():
        import csv

        with csv_path.open(newline="") as f:
            for row in csv.DictReader(f):
                if row.get("municipality_id"):
                    ids.add(int(row["municipality_id"]))
    return ids


def _reference_counts(client, table: str, ids: list[int]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for i in range(0, len(ids), 500):
        chunk = ids[i : i + 500]
        resp = (
            client.table(table)
            .select("municipality_id")
            .in_("municipality_id", chunk)
            .execute()
        )
        for row in resp.data or []:
            mid = row.get("municipality_id")
            if mid is not None:
                counts[mid] = counts.get(mid, 0) + 1
    return counts


def main() -> None:
    apply = "--apply" in sys.argv
    from app.services.supabase_service import get_supabase_client

    client = get_supabase_client()

    municipalities = _paged_column(client, "municipalities", "municipality_id,name")
    climate_ids = _climate_ids(client)
    candidates = [m for m in municipalities if m.get("municipality_id") not in climate_ids]
    candidate_ids = [m["municipality_id"] for m in candidates]

    print(f"Municipalities total        : {len(municipalities)}")
    print(f"With climate data           : {len(climate_ids)}")
    print(f"Candidates (no climate data): {len(candidates)}")

    referenced: dict[int, dict[str, int]] = {}
    skipped_tables: list[str] = []
    for table in REFERENCE_TABLES:
        try:
            counts = _reference_counts(client, table, candidate_ids)
        except Exception:
            skipped_tables.append(table)
            continue
        for mid, n in counts.items():
            referenced.setdefault(mid, {})[table] = n

    safe = [m for m in candidates if m["municipality_id"] not in referenced]
    blocked = [m for m in candidates if m["municipality_id"] in referenced]

    print(f"Referenced by other tables  : {len(blocked)}")
    print(f"Zero references (deletable) : {len(safe)}")
    if skipped_tables:
        print(f"Tables skipped (no column)  : {', '.join(skipped_tables)}")

    print("\n-- Blocked candidates (referenced, will NOT be deleted) --")
    for m in blocked:
        refs = ", ".join(f"{t}={n}" for t, n in referenced[m["municipality_id"]].items())
        print(f"  {m['municipality_id']:>10}  {m.get('name','')!r:<40} {refs}")

    print("\n-- Deletable candidates --")
    for m in safe:
        print(f"  {m['municipality_id']:>10}  {m.get('name','')!r}")

    if not apply:
        print("\nDry run — no rows were deleted. Re-run with --apply to delete the deletable set.")
        return

    if not safe:
        print("\nNothing to delete.")
        return

    safe_ids = [m["municipality_id"] for m in safe]
    deleted = 0
    for i in range(0, len(safe_ids), 500):
        chunk = safe_ids[i : i + 500]
        resp = client.table("municipalities").delete().in_("municipality_id", chunk).execute()
        deleted += len(resp.data or chunk)
    print(f"\nDeleted {deleted} municipalities with zero references.")
    print("Skipped %d referenced rows — resolve their references first." % len(blocked))


if __name__ == "__main__":
    main()
