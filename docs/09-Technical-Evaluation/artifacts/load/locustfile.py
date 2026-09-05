"""LUMI load test — Locust user profiles.

Profiles
--------
Profile A (default): raw capacity from localhost. The app's RateLimitMiddleware
and anonymous quota skip loopback clients, so this measures the raw FastAPI
ceiling (single uvicorn worker) without throttling noise.

Profile B (LUMI_LOAD_PROFILE=throttled): every request carries
`X-Forwarded-For: 203.0.113.7` so the 60 req/min per-IP limiter engages —
verifies throttle behavior (429 + Retry-After).

Profile C (LUMI_LOAD_PROFILE=spoof): every request carries
`X-Forwarded-For: 127.0.0.1` — documents the known bypass where a spoofed
loopback IP skips the limiter entirely.

Run (from repo root):
    python -m locust -f docs/09-Technical-Evaluation/artifacts/load/locustfile.py \
        --headless -u 50 -r 5 -t 90s \
        --csv docs/09-Technical-Evaluation/artifacts/load/runs/u50 \
        --html docs/09-Technical-Evaluation/artifacts/load/runs/u50.html \
        --host http://127.0.0.1:8000

LLM-backed endpoints (ecosim?include_ai, ai-insight use_llm, analyze-chart) are
excluded from sustained load: they are quota-gated and would burn LLM provider
quota without adding signal about app capacity.
"""

from __future__ import annotations

import os
import random

from locust import HttpUser, between, task

PROFILE = os.getenv("LUMI_LOAD_PROFILE", "raw").lower()

HEADERS = {}
if PROFILE == "throttled":
    HEADERS["X-Forwarded-For"] = "203.0.113.7"  # TEST-NET-3 public IP
elif PROFILE == "spoof":
    HEADERS["X-Forwarded-For"] = "127.0.0.1"  # spoofed loopback

# Real municipality IDs seen in /ecosim/municipalities responses.
MUNICIPALITY_IDS = [5441, 5415, 5145, 5050, 5892, 4919, 5354, 5131]


class LumiUser(HttpUser):
    wait_time = between(0.2, 1.0)

    @task(5)
    def energyhub_read(self):
        self.client.get("/api/v1/energyhub/overview",
                        headers=HEADERS, name="GET /energyhub/overview")
        self.client.get("/api/v1/energyhub/trends",
                        headers=HEADERS, name="GET /energyhub/trends")
        self.client.get("/api/v1/energyhub/map-data",
                        headers=HEADERS, name="GET /energyhub/map-data")

    @task(3)
    def map_and_geo(self):
        self.client.get("/api/v1/map/coverage",
                        headers=HEADERS, name="GET /map/coverage")
        self.client.get("/api/v1/map/solar",
                        headers=HEADERS, name="GET /map/solar")
        self.client.get(
            f"/api/v1/geospatial/centroids",
            params={"level": "province"},
            headers=HEADERS, name="GET /geospatial/centroids",
        )

    @task(4)
    def ecosim_simulation(self):
        mid = random.choice(MUNICIPALITY_IDS)
        self.client.get(
            "/api/v1/ecosim/",
            params={
                "municipality_id": mid,
                "monthly_consumption": 350,
                "monthly_bill": 5000,
            },
            headers=HEADERS, name="GET /ecosim/ (simulation)",
        )

    @task(2)
    def lists_and_products(self):
        self.client.get("/api/v1/ecosim/municipalities",
                        headers=HEADERS, name="GET /ecosim/municipalities")
        self.client.get("/api/v1/ecosim/provinces",
                        headers=HEADERS, name="GET /ecosim/provinces")
        self.client.get("/api/v1/products/browse",
                        headers=HEADERS, name="GET /products/browse")
        self.client.get("/api/v1/geothermal/plants",
                        headers=HEADERS, name="GET /geothermal/plants")
