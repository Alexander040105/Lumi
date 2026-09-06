"""LUMI security probes — live checks against the local backend.

Covers: JWT auth matrix (none/malformed/alg:none/wrong-sig/expired),
security headers, CORS preflight, API-docs exposure, error-body leakage.

No secret values are printed. Writes artifacts/security/probes.json.

Usage (backend on :8000):
    python docs/09-Technical-Evaluation/artifacts/scripts/security_probes.py
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8000"
API = f"{BASE}/api/v1"
OUT = Path(__file__).resolve().parents[1] / "security" / "probes.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

RESULTS: list[dict] = []
XFF = {"X-Forwarded-For": "127.0.0.1"}


def rec(tid, check, observed, verdict, detail=""):
    RESULTS.append({"id": tid, "check": check, "observed": observed,
                    "verdict": verdict, "detail": detail[:400]})
    print(f"{tid:>14} | {verdict:<6} | {observed}")


def mint_jwt(payload: dict, key: str, alg: str = "HS256") -> str:
    from jose import jwt as jose_jwt
    return jose_jwt.encode(payload, key, algorithm=alg)


def alg_none_jwt() -> str:
    import base64
    h = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').rstrip(b"=")
    p = base64.urlsafe_b64encode(
        b'{"sub":"11111111-1111-1111-1111-111111111111","role":"authenticated","exp":9999999999}'
    ).rstrip(b"=")
    return (h + b"." + p + b".").decode()


def main() -> None:
    c = httpx.Client(base_url=API, timeout=30)

    # ---------- JWT auth matrix on /protected/me ----------
    r = c.get("/protected/me", headers=XFF)
    rec("SEC-AUTH-01", "No token -> /protected/me", f"HTTP {r.status_code}",
        "PASS" if r.status_code == 401 else "FAIL", r.text[:120])

    r = c.get("/protected/me", headers={**XFF, "Authorization": "Bearer garbage"})
    rec("SEC-AUTH-02", "Malformed token", f"HTTP {r.status_code}",
        "PASS" if r.status_code == 401 else "FAIL", r.text[:120])

    r = c.get("/protected/me",
              headers={**XFF, "Authorization": f"Bearer {alg_none_jwt()}"})
    rec("SEC-AUTH-03", "alg=none JWT", f"HTTP {r.status_code}",
        "PASS" if r.status_code == 401 else "FAIL", r.text[:120])

    wrong = mint_jwt({"sub": "11111111-1111-1111-1111-111111111111",
                      "role": "authenticated", "exp": int(time.time()) + 3600},
                     key="definitely-not-the-secret")
    r = c.get("/protected/me",
              headers={**XFF, "Authorization": f"Bearer {wrong}"})
    rec("SEC-AUTH-04", "Wrong-signature JWT", f"HTTP {r.status_code}",
        "PASS" if r.status_code == 401 else "FAIL", r.text[:120])

    # Load the JWT secret from the repo .env for local verification tests.
    # Values are used in-memory only and never printed or persisted.
    try:
        from dotenv import dotenv_values
        repo_root = Path(__file__).resolve().parents[4]
        env = dotenv_values(repo_root / ".env")
    except Exception:
        env = {}
    secret = env.get("SUPABASE_JWT_SECRET") or os.getenv("SUPABASE_JWT_SECRET")
    if secret:
        expired = mint_jwt({"sub": "11111111-1111-1111-1111-111111111111",
                            "role": "authenticated", "aud": "authenticated",
                            "exp": int(time.time()) - 3600,
                            "iat": int(time.time()) - 7200}, key=secret)
        r = c.get("/protected/me",
                  headers={**XFF, "Authorization": f"Bearer {expired}"})
        rec("SEC-AUTH-05", "Expired JWT (real secret, expired exp)",
            f"HTTP {r.status_code}",
            "PASS" if r.status_code == 401 else "FAIL", r.text[:160])

        fake = mint_jwt({"sub": "11111111-1111-1111-1111-111111111111",
                         "role": "authenticated", "aud": "authenticated",
                         "exp": int(time.time()) + 3600}, key=secret)
        r = c.get("/protected/me",
                  headers={**XFF, "Authorization": f"Bearer {fake}"})
        rec("SEC-AUTH-06", "Locally-minted JWT for nonexistent user",
            f"HTTP {r.status_code}",
            "PASS" if r.status_code == 401 else "FAIL",
            "if 200: local JWT fallback accepts unregistered users")

    # ---------- Admin without admin token ----------
    for ep in ("/admin/users", "/admin/analytics", "/admin/config"):
        r = c.get(ep, headers={**XFF, "Authorization": "Bearer garbage"})
        rec("SEC-AUTH-ADM", f"Bad token -> {ep}", f"HTTP {r.status_code}",
            "PASS" if r.status_code in (401, 403) else "FAIL", r.text[:100])

    # ---------- Security headers ----------
    r = c.get("/health", headers=XFF)
    want = ["x-content-type-options", "x-frame-options",
            "strict-transport-security", "content-security-policy",
            "referrer-policy"]
    present = [h for h in want if h in r.headers]
    missing = [h for h in want if h not in r.headers]
    rec("SEC-HDR-01", "Security headers present",
        f"present={len(present)}/{len(want)} missing={missing}",
        "PASS" if len(present) >= 4 else "WARN",
        "; ".join(f"{h}: {r.headers[h]}" for h in present)[:380])

    rec("SEC-HDR-02", "Server banner disclosure",
        f"server={r.headers.get('server')!r}",
        "PASS" if not r.headers.get("server") else "WARN")

    # ---------- CORS preflight ----------
    for origin, label in (("http://localhost:5173", "allowed"),
                          ("https://lumi-frontend-abc.vercel.app", "regex-allowed"),
                          ("https://evil.example.com", "disallowed")):
        r = c.options("/ecosim/municipalities", headers={
            "Origin": origin, "Access-Control-Request-Method": "GET"})
        acao = r.headers.get("access-control-allow-origin")
        ok = (acao == origin) if label != "disallowed" else (acao is None)
        rec(f"SEC-CORS-{label}", f"Preflight origin={origin}",
            f"HTTP {r.status_code} ACAO={acao!r}",
            "PASS" if ok else "FAIL")

    # ---------- API docs / schema exposure ----------
    for path in ("/docs", "/openapi.json", "/redoc"):
        r = httpx.get(BASE + path, timeout=15)
        rec("SEC-DOCS", f"{path} exposure", f"HTTP {r.status_code}",
            "INFO" if r.status_code == 200 else "PASS")

    # ---------- Error body internals ----------
    r = c.get("/geothermal/999999", headers=XFF)
    body = r.text
    leaks = any(s in body.lower() for s in
                ("traceback", "c:\\", "site-packages", "file \""))
    rec("SEC-ERR-01", "500 body leaks internals (/geothermal/999999)",
        f"HTTP {r.status_code} leaks={leaks} body={body[:120]}",
        "PASS" if r.status_code == 500 and not leaks else "FAIL")

    OUT.write_text(json.dumps(RESULTS, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    print(f"\n{len(RESULTS)} probes -> {OUT}")


if __name__ == "__main__":
    main()
