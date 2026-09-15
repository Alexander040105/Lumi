"""LUMI performance benchmark — evidence collection.

Measures per-endpoint latency (min/mean/p50/p95/max) against the local
backend, plus service-level timings for representative Supabase REST queries.
Writes artifacts/perf/latency.csv and summary.json.

Usage (backend running on :8000):
    python docs/09-Technical-Evaluation/artifacts/scripts/benchmark.py [--n 30]

AI-backed endpoints are sampled lightly (default 5) to conserve LLM quota.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
import time
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8000/api/v1"
OUT_DIR = Path(__file__).resolve().parents[1] / "perf"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# (name, path, params, threshold_ms from rubric Table 19-B / performance_test.py)
ENDPOINTS = [
    ("health", "/health", {}, 500),
    ("health_detailed", "/health/detailed", {}, 5000),
    ("energyhub_overview", "/energyhub/overview", {}, 2000),
    ("energyhub_forecast", "/energyhub/forecast", {"metric": "consumption"}, 2000),
    ("energyhub_trends", "/energyhub/trends", {}, 2000),
    ("energyhub_map_data", "/energyhub/map-data", {}, 2000),
    ("energyhub_source_breakdown", "/energyhub/source-breakdown", {}, 2000),
    ("energyhub_grid_breakdown", "/energyhub/grid-breakdown", {}, 2000),
    ("energyhub_model_comparison", "/energyhub/model-comparison", {}, 2000),
    ("energyhub_provincial_demand", "/energyhub/provincial-demand", {}, 2000),
    ("ecosim_municipalities", "/ecosim/municipalities", {}, 2000),
    ("ecosim_provinces", "/ecosim/provinces", {}, 2000),
    ("geothermal_plants", "/geothermal/plants", {}, 2000),
    ("geothermal_municipality", "/geothermal/5441", {}, 2000),
    ("geospatial_climate", "/geospatial/climate",
     {"geo_id": 5441, "level": "municipality"}, 2000),
    ("map_coverage", "/map/coverage", {}, 2000),
    ("map_solar", "/map/solar", {}, 2000),
    ("products_recommend", "/products/recommend", {"energy_type": "solar"}, 2000),
    ("forecast_models", "/forecast/models", {}, 2000),
]

# Sampled lightly — each call may invoke an LLM (Groq default provider).
AI_ENDPOINTS = [
    ("ecosim_simulation", "/ecosim/",
     {"municipality_id": 5441, "monthly_consumption": 350,
      "monthly_bill": 5000}, 3000),
    ("ecosim_ai", "/ecosim/ai",
     {"municipality_id": 5441, "monthly_consumption": 350,
      "monthly_bill": 5000}, 5000),
    ("energyhub_ai_insight", "/energyhub/ai-insight", {"use_llm": "true"}, 5000),
    ("energyhub_map_explanation", "/energyhub/map-explanation",
     {"metric": "renewable_potential"}, 5000),
]


def pct(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    s = sorted(values)
    k = max(0, min(len(s) - 1, round((q / 100) * (len(s) - 1))))
    return s[k]


def sample(client: httpx.Client, name: str, path: str, params: dict,
           n: int, threshold: int) -> dict:
    lats, statuses, errors = [], [], []
    for _ in range(n):
        t0 = time.perf_counter()
        try:
            r = client.get(path, params=params)
            statuses.append(r.status_code)
        except Exception as exc:
            statuses.append(-1)
            errors.append(str(exc)[:120])
        lats.append((time.perf_counter() - t0) * 1000)
    ok = all(s == 200 for s in statuses)
    return {
        "endpoint": name, "method": "GET", "path": path, "params": params,
        "n": n, "min_ms": round(min(lats), 1), "mean_ms": round(statistics.mean(lats), 1),
        "p50_ms": round(pct(lats, 50), 1), "p95_ms": round(pct(lats, 95), 1),
        "max_ms": round(max(lats), 1),
        "statuses": ",".join(str(s) for s in sorted(set(statuses))),
        "all_2xx": ok, "threshold_ms": threshold,
        "within_threshold": pct(lats, 95) <= threshold if ok else False,
        "errors": "; ".join(errors[:3]),
    }


def supabase_timings() -> list[dict]:
    """Time representative Supabase REST round-trips via the service client."""
    rows = []
    repo_root = Path(__file__).resolve().parents[4]
    sys.path.insert(0, str(repo_root / "fastapi-backend"))
    try:
        from app.services.supabase_service import get_supabase_client  # noqa
        client = get_supabase_client()
        queries = [
            ("regions_select_1", lambda: client.table("regions").select("region_id").limit(1).execute()),
            ("municipalities_select_10", lambda: client.table("municipalities").select("municipality_id,name").limit(10).execute()),
            ("climate_monthly_filtered", lambda: client.table("municipality_climate_monthly").select("*").eq("municipality_id", 5441).limit(12).execute()),
        ]
        for name, fn in queries:
            lats = []
            err = ""
            for _ in range(10):
                t0 = time.perf_counter()
                try:
                    fn()
                except Exception as exc:
                    err = str(exc)[:120]
                lats.append((time.perf_counter() - t0) * 1000)
            rows.append({
                "endpoint": f"db:{name}", "method": "RPC", "path": "supabase",
                "params": {}, "n": 10, "min_ms": round(min(lats), 1),
                "mean_ms": round(statistics.mean(lats), 1),
                "p50_ms": round(pct(lats, 50), 1), "p95_ms": round(pct(lats, 95), 1),
                "max_ms": round(max(lats), 1), "statuses": "ok" if not err else "err",
                "all_2xx": not err, "threshold_ms": 2000,
                "within_threshold": pct(lats, 95) <= 2000, "errors": err,
            })
    except Exception as exc:
        rows.append({"endpoint": "db:setup", "method": "-", "path": "-",
                     "params": {}, "n": 0, "min_ms": 0, "mean_ms": 0,
                     "p50_ms": 0, "p95_ms": 0, "max_ms": 0, "statuses": "setup-fail",
                     "all_2xx": False, "threshold_ms": 0, "within_threshold": False,
                     "errors": str(exc)[:200]})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--ai-n", type=int, default=5)
    ap.add_argument("--db-only", action="store_true",
                    help="Only run Supabase query timings, write db_timings.csv")
    args = ap.parse_args()

    if args.db_only:
        rows = supabase_timings()
        csv_path = OUT_DIR / "db_timings.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        for r in rows:
            print(f"{r['endpoint']:<34} n={r['n']:>2} mean={r['mean_ms']:>8}ms "
                  f"p95={r['p95_ms']:>8}ms {r['statuses']} {r['errors'][:60]}")
        print(f"\nArtifacts: {csv_path}")
        return

    rows = []
    with httpx.Client(base_url=BASE, timeout=90.0) as client:
        for name, path, params, thr in ENDPOINTS:
            r = sample(client, name, path, params, args.n, thr)
            rows.append(r)
            print(f"{name:<32} n={r['n']:>2} mean={r['mean_ms']:>8}ms "
                  f"p95={r['p95_ms']:>8}ms thr={thr} "
                  f"{'OK' if r['within_threshold'] else 'OVER'}"
                  f"{'' if r['all_2xx'] else '  statuses=' + r['statuses']}")
        for name, path, params, thr in AI_ENDPOINTS:
            r = sample(client, name, path, params, args.ai_n, thr)
            rows.append(r)
            print(f"{name:<32} n={r['n']:>2} mean={r['mean_ms']:>8}ms "
                  f"p95={r['p95_ms']:>8}ms thr={thr} "
                  f"{'OK' if r['within_threshold'] else 'OVER'}"
                  f"{'' if r['all_2xx'] else '  statuses=' + r['statuses']}")

    rows.extend(supabase_timings())

    csv_path = OUT_DIR / "latency.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (OUT_DIR / "summary.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nArtifacts: {csv_path}")


if __name__ == "__main__":
    main()
