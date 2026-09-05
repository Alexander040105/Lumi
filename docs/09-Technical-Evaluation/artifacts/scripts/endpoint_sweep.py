"""LUMI endpoint sweep — functional evidence collection.

Hits every mounted endpoint on the local backend with a valid request and a
negative case where applicable. Records status, latency, and a verdict against
the expected result. Writes CSV + JSONL artifacts for the functional test
results document.

Usage (backend must be running on :8000):
    python docs/09-Technical-Evaluation/artifacts/scripts/endpoint_sweep.py

Auth endpoints are exercised WITHOUT a token (expected 401) and with a
malformed token (expected 401). Authenticated happy-paths are marked
[OPEN] — requires a test user session.
"""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8000"
API = f"{BASE}/api/v1"
OUT_DIR = Path(__file__).resolve().parents[1] / "functional"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BAD_TOKEN = "Bearer not.a.real.jwt"


def probe_ids() -> dict:
    """Discover real IDs for parameterized endpoints."""
    ids: dict = {}
    try:
        r = httpx.get(f"{API}/ecosim/municipalities", timeout=30)
        items = r.json().get("items") or r.json().get("municipalities") or r.json()
        if isinstance(items, list) and items:
            m = items[0]
            ids["municipality_id"] = m.get("municipality_id") or m.get("id")
            ids["municipality_name"] = m.get("name") or m.get("municipality")
            ids["province_id_from_muni"] = m.get("province_id")
    except Exception as exc:
        print("WARN municipalities probe failed:", exc)
    try:
        r = httpx.get(f"{API}/ecosim/provinces", timeout=30)
        items = r.json().get("items") or r.json().get("provinces") or r.json()
        if isinstance(items, list) and items:
            p = items[0]
            ids["province_id"] = p.get("province_id") or p.get("id")
            ids["province_name"] = p.get("name") or p.get("province")
    except Exception as exc:
        print("WARN provinces probe failed:", exc)
    if "province_id" not in ids and ids.get("province_id_from_muni"):
        ids["province_id"] = ids["province_id_from_muni"]
    return ids


def build_cases(ids: dict) -> list[dict]:
    mid = ids.get("municipality_id", 1)
    pid = ids.get("province_id", 1)
    sim = {
        "municipality_id": mid,
        "monthly_consumption": 350,
        "monthly_bill": 5000,
    }
    cases = []

    def add(cid, method, path, expected, note="", params=None, json_body=None,
            headers=None, auth="none"):
        cases.append({
            "id": cid, "method": method, "path": path, "params": params,
            "json": json_body, "headers": headers or {},
            "expected": expected, "note": note, "auth": auth,
        })

    # --- Health ---
    add("TC-API-001", "GET", "/health", "200 {'status':'ok'}")
    add("TC-API-001b", "GET", "/health/detailed", "200 dependency checks")

    # --- EcoSim ---
    add("TC-ES-001", "GET", "/ecosim/municipalities", "200, items > 0")
    add("TC-ES-001b", "GET", "/ecosim/provinces", "200, items > 0")
    add("TC-ES-001c", "GET", "/ecosim/barangays", "200 list",
        params={"municipality_id": mid})
    add("TC-ES-002", "GET", "/ecosim/", "200 dashboard",
        params=sim)
    add("TC-ES-003", "GET", "/ecosim/", "422 missing params")
    add("TC-ES-004", "GET", "/ecosim/", "404 invalid municipality",
        params={"municipality_id": 999999, "monthly_consumption": 350,
                "monthly_bill": 5000})
    add("TC-ES-004b", "GET", "/ecosim/", "422 negative id",
        params={"municipality_id": -1, "monthly_consumption": 350,
                "monthly_bill": 5000})
    add("TC-ES-010", "GET", "/ecosim/ai", "200 AI analysis or graceful fallback",
        params=sim)
    add("TC-ES-011", "GET", "/ecosim/", "200 with RAG flag",
        params={**sim, "include_ai": "true", "use_rag": "true"})
    add("TC-ES-012", "POST", "/ecosim/", "200/201 simulation",
        json_body={
            "house_name": "Eval Test House",
            "municipality": ids.get("municipality_name", "ABORLAN"),
            "electricity_rate": 12.0,
            "current_electricity_bill": 5000.0,
            "desired_savings": 0.5,
            "mode": "municipality",
        })
    add("TC-ES-012b", "POST", "/ecosim/", "422 out-of-range desired_savings",
        json_body={
            "house_name": "x", "municipality": "ABORLAN",
            "electricity_rate": 12.0, "current_electricity_bill": 5000.0,
            "desired_savings": 1.5,
        })
    add("TC-ES-013", "POST", "/ecosim/", "422 invalid body",
        json_body={"municipality_id": "not-an-int"})

    # --- EnergyHub ---
    add("TC-EH-001", "GET", "/energyhub/overview", "200 overview")
    add("TC-EH-002", "GET", "/energyhub/trends", "200 trends")
    add("TC-EH-004", "GET", "/energyhub/forecast", "200 consumption forecast",
        params={"metric": "consumption"})
    add("TC-EH-005", "GET", "/energyhub/forecast", "200 peak_demand forecast",
        params={"metric": "peak_demand"})
    add("TC-EH-006", "GET", "/energyhub/map-data", "200 map data")
    add("TC-EH-007", "GET", "/energyhub/source-breakdown", "200 source mix")
    add("TC-EH-008", "GET", "/energyhub/grid-breakdown", "200 grid split")
    add("TC-EH-009", "GET", "/energyhub/ai-insight", "200 static insight",
        params={"use_llm": "false"})
    add("TC-EH-010", "GET", "/energyhub/forecast", "4xx invalid metric",
        params={"metric": "invalid_metric"})
    add("TC-EH-011", "GET", "/energyhub/model-comparison", "200 model metrics")
    add("TC-EH-012", "GET", "/energyhub/provincial-demand", "200 provincial demand")
    add("TC-EH-013", "GET", f"/energyhub/municipal-demand/{pid}",
        "200 municipal demand")
    add("TC-EH-014", "GET", "/energyhub/irena/overview", "200 IRENA overview")
    add("TC-EH-015", "GET", "/energyhub/irena/capacity", "200 IRENA capacity")
    add("TC-EH-016", "GET", "/energyhub/irena/generation", "200 IRENA generation")
    add("TC-EH-017", "GET", "/energyhub/irena/renewable-share", "200 RE share")
    add("TC-EH-018", "GET", "/energyhub/meralco-rate", "200 Meralco rate")
    add("TC-EH-019", "GET", "/energyhub/solar-atlas", "200/4xx solar atlas",
        params={"location": "Quezon"})
    add("TC-EH-020", "GET", "/energyhub/map-explanation", "200 map explanation",
        params={"metric": "renewable_potential"})
    add("TC-EH-021", "POST", "/energyhub/analyze-chart", "200/503 chart analysis",
        json_body={"chart_type": "trends", "chart_data": {"years": [2020]}})

    # --- Geothermal ---
    add("TC-GEO-001", "GET", "/geothermal/plants", "200 plant list")
    add("TC-GEO-002", "GET", f"/geothermal/{mid}", "200 suitability")
    add("TC-GEO-003", "GET", "/geothermal/ecosim/geothermal", "200 params",
        params={"municipality_id": mid})
    add("TC-GEO-004", "GET", "/geothermal/ecohub/geothermal-summary", "200 summary")
    add("TC-GEO-005", "GET", "/geothermal/999999", "404 invalid municipality")

    # --- Geospatial ---
    add("TC-GS-001", "GET", "/geospatial/centroids", "200 centroids",
        params={"level": "province"})
    add("TC-GS-002", "GET", f"/geospatial/centroids/municipality/{mid}",
        "200 centroid")
    add("TC-GS-003", "GET", "/geospatial/climate", "200 climate",
        params={"geo_id": mid, "level": "municipality"})
    add("TC-GS-004", "GET", "/geospatial/climate/hierarchy", "200 hierarchy",
        params={"municipality_id": mid})
    add("TC-GS-005", "GET", "/geospatial/climate/province-aggregate",
        "200 province aggregate", params={"province_id": pid, "year": 2023})
    add("TC-GS-006", "GET", "/geospatial/climate", "422 missing geo_id")

    # --- Map ---
    add("TC-MAP-001", "GET", "/map/psgc/hierarchy", "200 PSGC hierarchy",
        params={"municipality_id": mid})
    add("TC-MAP-002", "GET", "/map/coverage", "200 coverage")
    for rt in ("solar", "wind", "hydro", "geothermal"):
        add(f"TC-MAP-003-{rt}", "GET", f"/map/{rt}", f"200 {rt} map data")
    add("TC-MAP-004", "GET", "/map/nuclear", "4xx invalid renewable_type")

    # --- Products ---
    add("TC-PROD-001", "GET", "/products/recommend", "200 recommendations",
        params={"energy_type": "solar"})
    add("TC-PROD-002", "GET", "/products/browse", "200 product list")
    add("TC-PROD-003", "GET", "/products/audit", "200 audit")
    add("TC-PROD-004", "GET", "/products/recommend", "422 missing energy_type")

    # --- Forecast ---
    add("TC-FC-001", "GET", "/forecast/run", "200 forecast run")
    add("TC-FC-002", "GET", "/forecast/backtest", "200 backtest")
    add("TC-FC-003", "GET", "/forecast/models", "200 model registry")

    # --- Protected (expect 401 without token) ---
    add("TC-AUTH-003", "GET", "/protected/me", "401 no token")
    add("TC-AUTH-003b", "GET", "/protected/me", "401 malformed token",
        headers={"Authorization": BAD_TOKEN})
    add("TC-AUTH-004", "GET", "/protected/profile", "401 no token")
    add("TC-AUTH-007", "GET", "/simulations", "401 no token")
    add("TC-AUTH-007b", "POST", "/simulations", "401 no token",
        json_body={"label": "x", "results": {}})
    add("TC-AUTH-008", "GET", "/simulations/00000000-0000-0000-0000-000000000000",
        "401 no token")

    # --- Admin (expect 401/403 without admin token) ---
    add("TC-ADM-001", "GET", "/admin/users", "401/403 no token")
    add("TC-ADM-001b", "GET", "/admin/users", "401/403 bad token",
        headers={"Authorization": BAD_TOKEN})
    add("TC-ADM-002", "GET", "/admin/analytics", "401/403 no token")
    add("TC-ADM-003", "GET", "/admin/config", "401/403 no token")
    add("TC-ADM-004", "GET", "/admin/usage", "401/403 no token")
    add("TC-ADM-005", "GET", "/admin/logs", "401/403 no token")

    # --- Injection probes ---
    add("TC-SEC-INJ-01", "GET", "/ecosim/", "4xx injection rejected",
        params={"municipality_id": "1 OR 1=1", "monthly_consumption": 350,
                "monthly_bill": 5000})
    add("TC-SEC-INJ-02", "GET", "/energyhub/forecast", "4xx injection rejected",
        params={"metric": "consumption;DROP TABLE municipalities--"})
    add("TC-SEC-INJ-03", "GET", "/geospatial/centroids/../../etc/passwd/1",
        "4xx path traversal rejected")
    add("TC-SEC-INJ-04", "GET", "/products/recommend", "4xx injection rejected",
        params={"energy_type": "solar' OR '1'='1"})

    return cases


def verdict(expected: str, status: int, elapsed: float, body: str) -> str:
    """Map expected spec + actual response to a verdict."""
    exp = expected.split()[0].rstrip(",")
    if exp == "200" and status == 200:
        return "PASS"
    if exp == "200/201" and status in (200, 201):
        return "PASS"
    if exp == "200/503" and status in (200, 503):
        return "PASS"
    if exp == "200/4xx" and (status == 200 or 400 <= status < 500):
        return "PASS"
    if exp == "401" and status == 401:
        return "PASS"
    if exp == "401/403" and status in (401, 403):
        return "PASS"
    if exp == "404" and status == 404:
        return "PASS"
    if exp == "422" and status == 422:
        return "PASS"
    if exp == "4xx" and 400 <= status < 500:
        return "PASS"
    if exp == "4xx/404" and status in range(400, 500):
        return "PASS"
    return "FAIL"


def main() -> None:
    ids = probe_ids()
    print("Discovered ids:", ids)
    cases = build_cases(ids)
    results = []
    client = httpx.Client(base_url=API, timeout=60.0, follow_redirects=True)
    for c in cases:
        t0 = time.perf_counter()
        snippet = ""
        try:
            r = client.request(
                c["method"], c["path"], params=c.get("params"),
                json=c.get("json"), headers=c.get("headers") or {},
            )
            elapsed = (time.perf_counter() - t0) * 1000
            status = r.status_code
            try:
                snippet = json.dumps(r.json())[:220]
            except Exception:
                snippet = r.text[:220]
        except Exception as exc:
            elapsed = (time.perf_counter() - t0) * 1000
            status = -1
            snippet = f"EXC: {exc}"
        v = verdict(c["expected"], status, elapsed, snippet)
        results.append({
            "id": c["id"], "method": c["method"], "path": c["path"],
            "expected": c["expected"], "status": status,
            "latency_ms": round(elapsed, 1), "verdict": v,
            "note": c["note"], "response_snippet": snippet,
        })
        print(f"{c['id']:>16} {c['method']:>6} {c['path']:<52} -> {status} "
              f"{v} ({elapsed:.0f}ms)")

    csv_path = OUT_DIR / "endpoint_sweep.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)
    jsonl = OUT_DIR / "endpoint_sweep.jsonl"
    with jsonl.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    n_pass = sum(1 for r in results if r["verdict"] == "PASS")
    print(f"\n{n_pass}/{len(results)} passed. Artifacts: {csv_path}, {jsonl}")


if __name__ == "__main__":
    main()
