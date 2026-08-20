"""Request timing middleware.

Logs method, path, status code, and wall-clock duration for every request.
This is the first pass of the observability work; later slices can add
Supabase/Redis call counts and per-route breakdowns.
"""

from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("lumi.timing")


class TimingMiddleware(BaseHTTPMiddleware):
    """Log request duration and outcome for every request."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.warning(
                "%s %s - exception after %.2f ms: %s",
                request.method,
                request.url.path,
                duration_ms,
                exc,
            )
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s %s - %.2f ms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
