# EcoSim Sizing/Battery — Deployment Notes

Implements `docs/ECOSIM-SIZING-BATTERY-IMPLEMENTATION-SPEC.md` on the Vercel free tier.

## What ships

- `sizing` block on `GET /api/v1/ecosim/` and `POST /api/v1/ecosim/` (also `/ecosim/ai` accepts the new params). Optional inputs: `include_battery`, `roof_area_m2`, `daytime_fraction` (all backward-compatible when omitted).
- 550W panel sizing, optional roof clamp, LiFePO4 dispatch (90% DoD, 88% RTE, 0.5C), ERC net-metering export credit at 55% of retail rate, 25-yr cash flows (0.5%/yr degradation, 3%/yr tariff escalation, 1% O&M, year-10 battery replacement at 60% CapEx, 10% discount).
- BOM lines matched to the live `products` catalog; quote-only rows stay quote-only. Solar option card now carries cost/payback/NPV; wind/hydro/geothermal financials remain hidden.
- Wind viability floor: hub-height mean <5.0 m/s → suitability 0 + excluded from recommendation. Hydro: `source_type=academic`, excluded from purchase recommendation, NWRB/PD 1067 disclaimer.

## Serverless fit

- **Zero new dependencies** — pure `math` + `pandas` (already in `api/requirements.txt`).
- Sizing compute is sub-millisecond; product matching reuses the cached `_load_products()` dataframe (one Supabase read per cold start, shared with the products service).
- New params are part of the Redis `params_hash`, so old cache entries can't be served for new requests. Cached results that predate the feature yield `sizing: null` and the frontend hides the sections gracefully.

## Limits / known simplifications

- Diurnal split is a single `daytime_fraction` (0.35/0.50), not an hourly load profile.
- Cash-flow horizon models one battery replacement (year 10) per spec §3.5.
- Financial outputs are planning estimates anchored to cited PH turnkey rates — not installer quotes.
- With `include_battery=true`, the Solar option card shows the grid-tie baseline while the sizing card shows the selected hybrid system — intentional split.
- `matched_product` is a deterministic cheapest-priced pick per BOM line, not a vendor recommendation.

## Verification

`pytest fastapi-backend/tests/test_sizing.py` — 21 tests: spec acceptance vector, roof clamp (incl. zero-fit), daytime fraction, C-rate binding, export credit, cash flows, product matching incl. quote-only, wind/hydro policy gates, backward-compat API, param validation. Frontend: `npm run build` clean; browser-checked end-to-end (wizard → sizing card → BOM → references).
