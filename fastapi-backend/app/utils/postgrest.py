"""PostgREST / supabase-py helpers for LUMI routes.

These utilities map PostgREST-specific errors (especially PGRST116, "exactly one
row expected") into clean HTTP exceptions instead of letting them leak through
the global 500 handler.
"""
from __future__ import annotations

from fastapi import HTTPException, status

from postgrest.exceptions import APIError


_PGRST116 = "PGRST116"


def is_pgrst116_not_found(exc: Exception) -> bool:
    """Return True if exc is a PostgREST 'exactly one row expected' error."""
    if not isinstance(exc, APIError):
        return False
    if getattr(exc, "code", None) == _PGRST116:
        return True
    # Fallback for older/supabase client variants that put the error in args.
    error = getattr(exc, "args", [{}])[0]
    if isinstance(error, dict) and error.get("code") == _PGRST116:
        return True
    if isinstance(error, str) and _PGRST116 in error:
        return True
    return False


def raise_for_pgrst116_or_404(exc: Exception, detail: str) -> None:
    """Re-raise PGRST116 as a clean 404; re-raise anything else unchanged."""
    if is_pgrst116_not_found(exc):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        ) from exc
    raise


def data_or_none_for_pgrst116(exc: Exception) -> None:
    """Swallow a PGRST116 as a missing row (return None); re-raise others."""
    if is_pgrst116_not_found(exc):
        return None
    raise
