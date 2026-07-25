"""Structured logging and request ID middleware for LUMI.

Adds:
- X-Request-ID header to every response
- Structured JSON log lines with request_id, method, path, status, duration_ms
- Correlation of client-supplied X-Request-ID if present
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("lumi.request")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to every request and response."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        start = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 2)

        response.headers["X-Request-ID"] = request_id

        # Structured log line
        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": request.client.host if request.client else None,
            },
        )

        return response


class DefaultRequestFilter(logging.Filter):
    """Inject default request metadata into every LogRecord.

    Some handlers or formatters (e.g. Uvicorn's defaults) expect fields such
    as ``request_id``.  This filter ensures those attributes exist before
    formatting, so records from library loggers do not trigger a KeyError.
    """

    _DEFAULTS = {
        "request_id": None,
        "method": None,
        "path": None,
        "status_code": None,
        "duration_ms": None,
        "client_ip": None,
    }

    def filter(self, record: logging.LogRecord) -> bool:
        for key, default in self._DEFAULTS.items():
            if not hasattr(record, key):
                setattr(record, key, default)
        return True


class SafeJSONFormatter(logging.Formatter):
    """JSON formatter that tolerates records without request metadata.

    Library loggers (e.g. faiss, uvicorn) do not carry the extra fields
    injected by RequestIDMiddleware.  This formatter defaults those fields
    to None instead of raising ``KeyError``.
    """

    def format(self, record: logging.LogRecord) -> str:
        try:
            message = record.getMessage()
        except (TypeError, ValueError, KeyError):
            message = str(record.msg)

        payload = {
            "time": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "request_id": getattr(record, "request_id", None),
            "method": getattr(record, "method", None),
            "path": getattr(record, "path", None),
            "status_code": getattr(record, "status_code", None),
            "duration_ms": getattr(record, "duration_ms", None),
            "client_ip": getattr(record, "client_ip", None),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(payload, default=str, ensure_ascii=False)


def setup_logging(level: int | str = logging.INFO) -> None:
    """Configure structured logging for the application."""
    formatter = SafeJSONFormatter()
    default_filter = DefaultRequestFilter()

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.addFilter(default_filter)

    # Reconfigure the root logger
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    # Reconfigure common library loggers that may carry their own handlers
    # (Uvicorn, FastAPI/Starlette, FAISS, HTTP clients).  Replace any handler
    # that has a non-safe formatter so it cannot raise on missing ``request_id``.
    for name in (
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "uvicorn.asgi",
        "fastapi",
        "starlette",
        "faiss",
        "httpx",
        "httpcore",
        "urllib3",
    ):
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.propagate = False

    # Quiet noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("faiss").setLevel(logging.WARNING)
