"""ETL and data engineering API routes for LUMI.

Provides:
- /etl/run/climate — run the climate data ETL pipeline
- /etl/lineage — view data lineage history
- /etl/validate — validate data in a target table
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Query

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/run/climate")
async def run_climate_etl() -> dict[str, Any]:
    """Run the climate data ETL pipeline."""
    from app.services.etl_orchestrator import build_climate_etl_pipeline

    orchestrator = build_climate_etl_pipeline()
    results = orchestrator.run()

    return {
        "pipeline": orchestrator.pipeline_name,
        "steps": [
            {
                "step": r.step_name,
                "status": r.status,
                "rows_affected": r.rows_affected,
                "duration_seconds": r.duration_seconds,
                "error": r.error,
            }
            for r in results
        ],
        "summary": {
            "success": sum(1 for r in results if r.status == "success"),
            "failed": sum(1 for r in results if r.status == "failed"),
            "skipped": sum(1 for r in results if r.status == "skipped"),
        },
    }


@router.get("/lineage")
async def get_lineage(
    source: str | None = Query(default=None, description="Filter by data source"),
    table: str | None = Query(default=None, description="Filter by target table"),
    limit: int = Query(default=50, le=200),
) -> dict[str, Any]:
    """View data lineage history."""
    from app.services.etl_orchestrator import get_lineage_history

    history = get_lineage_history(source=source, table=table, limit=limit)
    return {"items": history, "count": len(history)}


@router.get("/validate")
async def validate_table(
    table: str = Query(..., description="Table name to validate"),
) -> dict[str, Any]:
    """Run basic validation checks on a Supabase table.

    Checks row count, null rates, and basic column statistics.
    """
    from app.services.supabase_service import get_supabase_client

    client = get_supabase_client()
    try:
        resp = client.table(table).select("*").limit(1000).execute()
        rows = resp.data or []

        if not rows:
            return {"table": table, "valid": False, "error": "No rows returned"}

        # Basic stats
        columns = list(rows[0].keys()) if rows else []
        null_counts: dict[str, int] = {}
        for col in columns:
            null_counts[col] = sum(1 for r in rows if r.get(col) is None)

        return {
            "table": table,
            "valid": True,
            "row_count_sampled": len(rows),
            "columns": columns,
            "null_counts": null_counts,
            "null_rates": {
                col: round(null_counts[col] / len(rows), 4) if rows else 0
                for col in columns
            },
        }
    except Exception as exc:
        logger.warning("Table validation failed for %s: %s", table, exc)
        return {"table": table, "valid": False, "error": str(exc)}
