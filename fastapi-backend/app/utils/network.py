"""Network / reverse-proxy helpers for LUMI.

Rate limiting and quota enforcement need a stable client identifier, but they
must not trust arbitrary ``X-Forwarded-For`` values sent by untrusted clients.
The helpers below:

* Use the direct peer IP for localhost checks (so spoofed XFF can never bypass
  limits locally).
* Trust platform headers (Vercel) when present; otherwise fall back to the
  direct peer IP.
"""
from __future__ import annotations

from starlette.requests import Request


def _direct_peer_ip(request: Request) -> str:
    return request.client.host if request.client and request.client.host else "unknown"


def _is_localhost(client_ip: str) -> bool:
    # nosec B104: these are sentinel strings used for localhost identification,
    # not a bind address.
    return client_ip in ("127.0.0.1", "::1", "localhost")


def _is_trusted_proxy_platform(request: Request) -> bool:
    """Detect Vercel or another trusted platform that sanitizes client headers.

    Vercel sets ``x-vercel-forwarded-for`` and overwrites ``X-Forwarded-For``
    with the real client chain. We use this as a trust signal.
    """
    return any(
        h in request.headers
        for h in ("x-vercel-forwarded-for", "x-vercel-id", "x-vercel-ip-country")
    )


def get_client_id(request: Request) -> str:
    """Return the best-effort client identifier for rate/quotas.

    On Vercel, this is the client IP reported by the platform. Otherwise it is
    the direct peer IP, which prevents clients from fabricating unlimited
    identities with ``X-Forwarded-For``.
    """
    if _is_trusted_proxy_platform(request):
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        forwarded = request.headers.get("x-vercel-forwarded-for")
        if forwarded:
            return forwarded.split(",")[-1].strip()
    return _direct_peer_ip(request)
