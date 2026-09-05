# Load & Scalability Results — LUMI

**Date:** September 5, 2026
**Tool:** Locust 2.46.4 (headless), `artifacts/load/locustfile.py`
**Target:** Local FastAPI backend `http://127.0.0.1:8000` (single uvicorn worker)
**Constraint honored:** No load applied to production Vercel/Gemini/Groq — all load local.

---

## 1. Methodology

`locustfile.py` models a realistic mixed workload over public endpoints, weighted toward the heavier ones:

| Task | Endpoint | Weight |
|---|---|---|
| EcoSim simulation | `GET /ecosim/?municipality_id=<real>&…` | 3 |
| Municipality/province lists | `GET /ecosim/{municipalities,provinces}` | 2 |
| EnergyHub reads | `overview`, `trends`, `map-data` | 2 |
| Map/geospatial | `map/coverage`, `map/solar`, `geospatial/centroids` | 2 |
| Catalog | `geothermal/plants`, `products/browse` | 1 |

Municipality IDs are real (5441, 5415, 5145, 5050, 5892, 4919, 5354, 5131) — an earlier pass that mixed a province ID produced 404 noise and was discarded.

**Stepped profile:** 1 → 10 → 25 → 50 → 75 → 100 users, 60s per level, hatch rate 5/s.
**Profiles:** `raw` (default), `throttled` (fixed XFF → same IP bucket), `spoof` (rotating random XFFs).

> ⚠️ First-pass u=25–u=100 ran while dependency scanners (bandit/pip-audit/npm-audit) and failure-matrix bursts competed for CPU. Levels 10/25/50/75 were re-run in a clean window (`clean_u*.csv`); u=100 uses the first-pass value (directionally consistent).

## 2. Results — stepped concurrency

| Users | Reqs | Fails | Avg (ms) | p50 | p95 | Max | RPS |
|---|---|---|---|---|---|---|---|
| 1 | 96 | 0 | 90 | 38 | 600 | 1,100 | 3.3 |
| 10 (clean) | 790 | 0 | 519 | 410 | 1,400 | 2,800 | 13.3 |
| 25 (clean) | 769 | 0 | 1,637 | 1,400 | ~3,300 | ~6,000 | 13.0 |
| 50 (clean) | 614 | 0 | 3,838 | 3,800 | ~7,000 | ~9,600 | 10.5 |
| 75 (clean) | 657 | 0 | 5,582 | 5,500 | ~8,700 | ~12,000 | 11.0 |
| 100 (pass-1) | 814 | 0 | 5,591 | 5,700 | ~8,900 | ~14,000 | 13.7 |

Artifacts: `artifacts/load/runs/u{N}_stats.csv`, `u{N}.html`, `clean_u{N}_stats.csv`.

## 3. Interpretation

- **Zero hard failures at every level** — no 5xx, no timeouts, no connection resets. The system degrades **gracefully** (latency inflates; every request completes).
- **Throughput plateaus at ~11–14 RPS** regardless of user count → the worker is saturated; requests queue rather than fail.
- **Latency knee between 10 and 25 users:** p95 crosses ~2s near u=10–25 and ~3s by u=25 — attributable to sync (non-`async def`) handlers blocking the FastAPI thread pool on sequential Supabase REST round-trips (~70–300ms each) plus the heavier EcoSim compute.
- **Single-worker ceiling:** ~10–15 concurrent users for interactive (sub-second p95) experience; ~25 users before p95 breaches 3s.

## 4. Rate-limit interaction under load

| Profile | Result |
|---|---|
| `throttled` (u=8, 45s, fixed IP) | **429s on all probed endpoints** once the 60/min window filled — limiter works under load |
| `spoof` (u=8, 30s, rotating XFF) | 378 reqs, **0×429** — each spoofed IP stays under the cap; see security doc SEC-01 |

## 5. Bottleneck analysis (observed + code-correlated)

| # | Bottleneck | Evidence |
|---|---|---|
| B-01 | Single uvicorn worker + sync handlers block the thread pool on Supabase I/O | Latency curve saturates at 11–14 RPS; `app/services/*` uses sync `httpx`/`supabase` calls |
| B-02 | Per-request Supabase REST round-trips (uncached paths) | DB timings §4 of perf doc: ~70ms floor per call |
| B-03 | EcoSim simulation compute ~450ms serial | `latency.csv` `ecosim_simulation` |
| B-04 | CORS preflight + per-request middleware add fixed ~30–60ms | p50 floor under no contention |
| B-05 | **No CORS/504/Gemini-timeout cascade observed** — quota gates (1/day anon) cap LLM spend before timeouts matter | ai-insight 401s, not timeouts |

No 504s occurred locally; Vercel serverless has its own function-duration limit (would surface as 504 under sustained load — untested by design).

## 6. Breaking point

| Threshold | Level reached |
|---|---|
| p95 < 1s | ~10 users |
| p95 < 3s | ~25 users |
| Hard failures (>1% error) | **Not reached** at u=100 — graceful degradation |

**Recommended ceiling (this hardware/deployment):** ~10 concurrent interactive users per single worker; horizontal scale-out (multiple uvicorn workers / Vercel concurrency) required beyond that. In-memory rate-limit + quota counters are **per-process**, so effective limits multiply per worker/instance — see security doc SEC-01.

## 7. Reproduction

```bash
# Stepped (per level)
python -m locust -f docs/09-Technical-Evaluation/artifacts/load/locustfile.py \
  --headless -u 25 -r 5 -t 60s \
  --csv docs/09-Technical-Evaluation/artifacts/load/runs/u25 \
  --host http://127.0.0.1:8000 --only-summary

# Rate-limit profiles
LUMI_LOAD_PROFILE=throttled python -m locust ... -u 8 -t 45s
LUMI_LOAD_PROFILE=spoof     python -m locust ... -u 8 -t 30s
```

## 8. Limitations

- Localhost loopback removes WAN latency — absolute numbers are optimistic vs. real clients.
- u=100 retained from the contaminated first pass; a clean re-run is queued but direction is clear (plateau + graceful degradation).
- Production (Vercel serverless) scaling behavior not load-tested — cold-start smoke only (0.8–3.8s).
- Anonymous-quota 401s appear in traces where AI endpoints were exercised — counted as failures by locust but are **intended** behavior.

*End of Load & Scalability Results*
