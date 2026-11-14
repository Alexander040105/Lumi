# EcoSim Sizing, Battery, and Export — Audit + Research Plan

This document does three things: (1) audits every formula EcoSim uses today, exactly as implemented; (2) defines the math needed to answer "how many panels / turbines / batteries do I need to cover X% of my bill, and what can I sell back to the utility?"; (3) lists every data point and research item that must be gathered before implementing. It is written to be self-contained so it can be uploaded to NotebookLM alongside external sources.

---

## PART A — What EcoSim does today (audit)

### A.1 Inputs

`GET /ecosim/` (`fastapi-backend/app/schemas/ecosim.py:112-118`) accepts:

- `municipality_id` — location resolved from Supabase climate rows (NASA POWER, Global Solar/Wind Atlas, catchment enrichment, terrain). No lat/lon input.
- `monthly_consumption` (kWh), `monthly_bill` (PHP), optional `electricity_rate` (₱/kWh)
- `desired_savings` — default 0.5 (50%); label "off-grid" shown above 75% in the wizard
- `mode` (municipality | province | barangay), `data_source`, `include_ai`, `use_rag`

Derived in `consumption_calculator` (`ecosim.py:908-918`):

- `monthly_consumption_kwh = monthly_bill / electricity_rate` (when bill+rate given instead of consumption)
- `daily_consumption_kwh = monthly / days_in_month`
- `target_monthly_consumption_kwh = monthly × (1 − desired_savings)` — **computed but never used downstream.** This is the natural insertion point for sizing.

If user-entered consumption and bill-derived consumption differ by >20%, the code flags `input_warning` and overrides with the bill-derived value (`ecosim.py:1827-1843`).

### A.2 Solar generation — fixed system, not sized to load

Household solar is a **hardcoded 1.25 kWp system = 3 × 400 W panels** (`settings.py:75`, `ecosim.py:1069-1083`). It does not scale with the user's consumption.

Three output paths (`ecosim.py:1101-1133`), in priority order:

1. **PVOUT path** (`solar_output_calc.py:312-344`) — used when the location has Global Solar Atlas `solar_pvout_annual_kwh_kwp`:
   `daily_kwh = system_kwp × PVOUT / 365`, `monthly = daily × days`, `annual = kWp × PVOUT`.
   PVOUT is a per-kWp annual yield (kWh/kWp/year) that already embeds losses — no separate performance ratio applied. **Because it is linear in kWp, sizing is a single division.**
2. **Advanced path** (`solar_output_calc.py:195-297`) — used when DNI+DHI present: GHI → POA transposition → NOCT cell-temperature factor (γ = −0.004/°C) → soiling → air density → combined PR → `daily = kWp × POA × PR`.
3. **Legacy path** (`solar_output_calc.py:175-191`) — `daily = kWp × GHI × PR` with default losses: system efficiency 0.80, inverter 0.96, mismatch 0.98, wiring 0.98, degradation 0.99, dust 0.97.

### A.3 Wind generation — one turbine

`calculate_wind_output` (`wind_output_calc.py:127-245`) models **a single small household turbine**:

- Extrapolate wind speed to 30 m hub: `V = V_ref × (30/h_ref)^0.143` (power-law shear).
- Swept area `A = π × 6.2²` m² (rotor radius 6.2 m — note: settings comment says "5.5 m diameter" but the value is a radius; the power-curve cap hides this).
- Raw power `P = 0.5 × ρ × A × V³ × Cp × 0.90`, with `Cp ≤ 0.593` (Betz limit enforced); Cp comes from the average of scraped wind products or 0.35 fallback.
- Power curve (`wind_output_calc.py:229-237`): 0 below 3 m/s cut-in; `min(P_raw, 1.2 kW)` between cut-in and 11 m/s rated; flat 1.2 kW from 11–25 m/s; 0 above 25 m/s cut-out.
- `daily = kW × 24 × capacity_factor(0.22)`, monthly = × days.

Post-scaling (outside the calc): monthly kWh is multiplied by `wind_generation_scale = min(1 + 0.3 × ln1p(MW/100), 1.5)` when operating wind farms are nearby (`ecosim.py:1942-1953`). The scale is exposed in `assumptions` — **must be divided out before computing a per-turbine count.**

### A.4 Hydro generation — one run-of-river unit

`estimated_flow_rate` + `calculate_hydropower` (`hydro_output_calc.py:35-241`):

- Flow: `Q = C × rainfall × catchment_area / month_seconds × design_flow(0.80) × gravity_factor`, clamped to [0.001, 0.5] m³/s. Catchment = enriched area × 0.002 fraction, capped at 2.0 km².
- Head: DEM head × 0.50 factor, clamped [2, 30] m (or enriched `stream_head_m` clamped [0, 30]).
- Electric power: `P = ρ·g·Q·H / 1000 × (0.85 × 0.95)` = ~0.81 combined efficiency.
- `daily = P × 24`, monthly = × days, optional stream-distance feasibility penalty.
- Post-scaling: `hydro_generation_scale` up to 2.5×, plant floor, and an absolute cap of **250 kWh/month**.

Hydro is a **physics unit, not a countable product** — a home either has a viable stream or it doesn't. Sizing here means "how many kW can this site sustain," not "how many turbines."

### A.5 Geothermal — reference only

Utility-scale thermodynamic estimate (`geothermal/features.py:623`), `source_type: "utility"`, excluded from household recommendation. Not a sizing target.

### A.6 Economics — computed, then hidden

`_calculate_option_summary` (`ecosim.py:1657-1812`):

- `usable_kwh = min(generation, consumption)` — **surplus energy is discarded here.** No storage, no export credit.
- `monthly_savings = usable_kwh × electricity_rate`
- System-kW proxies: solar `gen/(30×4.5)` (4.5 peak-sun-hours), wind `gen/(30×24×0.25)` (25% CF), hydro `gen/(30×24×0.50)` (50% CF)
- `installation_cost = system_kW × cost_per_kw` with `COST_PER_KW_SOLAR=₱60,000`, `WIND=₱80,000`, `HYDRO=₱100,000`, `GEOTHERMAL=₱100,000` (`ecosim.py:149-162`)
- `payback = cost / (savings × 12)`; `energy_ratio = min(gen/cons, 1)`; `suitability = source_score × (0.4 + 0.6×energy_ratio) × 100`
- `carbon_reduction = usable_kwh × 0.6835 kg` (DOE 2019-2021 OMEF)
- `financials.py` computes NPV, IRR, LCOE, discounted payback, BCR (10% discount, 25/30-yr life, 0.5%/yr degradation, 1% O&M, 3% inflation) — but on **uncapped** annual generation, which is inconsistent with the capped simple payback.

**Then all of it is nulled before the response** (`ecosim.py:2193-2202`, `2248-2254`): `monthly_savings, installation_cost, payback_years, discounted_payback_years, npv_php, irr, lcoe_php_kwh, benefit_cost_ratio, system_kw, comparison → None`. Comment: "Hide financial/LCOE fields until cost data is reliable." The engine exists; the decision to show it was deferred.

### A.7 What exists but is dead/incomplete

- `react-frontend/src/components/ecosim/EcosimBOM.jsx` (148 lines) — a bill-of-materials component with per-source item schemas and cost shares (Solar: panels `ceil(kw×1000/400)`, inverter, mounting, labor, permits at 40/20/15/20/5%). **Never imported anywhere** — dead code, but it is a working precedent for the BOM feature.
- Meralco rate data — `data_v2/data_v2_preprocessed/meralco_rates_2011_2020.csv` has Residential generation-energy-charge rates (₱3.70–5.79/kWh, 2011-2020) and a `GET /energyhub/meralco-rate` endpoint exists. The EcoSim Meralco card in `EcosimResults.jsx` is dead (field removed from response schema).
- `products.csv` — ~871 rows subcategory "battery" but **no capacity/voltage/chemistry fields**; only names, prices, URLs. Wind products have parsed `power_w, rotor_radius_m, power_coefficient` but are only used to compute fleet averages, not picked per-user.
- Cache mechanics — simulation results are cached by `params_hash` with `scoring_version: "v5"` (`ecosim.py:967-1011`). **Any new sizing/battery input must be added to `cache_payload` or stale cached results will be served.**

### A.8 Confirmed gaps

1. No load-driven sizing — solar is a fixed 3-panel array regardless of consumption.
2. No battery model — zero capacity/DoD/efficiency/cost constants anywhere.
3. No export/surplus economics — surplus silently zeroed by `min(gen, cons)`.
4. No temporal granularity — one average month; no day/night split, so "self-consumed vs stored vs exported" has no natural home yet.
5. No product linkage — 400 W panel hardcoded; products lack structured specs.
6. Economics computed-but-hidden, and internally inconsistent (capped vs uncapped savings; docstring says 4.0 PSH, code uses 4.5).

---

## PART B — The sizing model (math to implement)

Granularity decision matters. The honest recommendation: **stay monthly-average with an assumed daytime-load fraction** — it matches the existing model's precision; an hourly simulation would imply accuracy the input data (monthly climate averages) cannot support. Document it as a simplification ceiling.

### B.1 Target energy

```
target_kwh_month = monthly_consumption_kwh × savings_fraction
surplus_kwh_month = extra_export_kwh user wants beyond 100% (optional input, default 0)
required_generation_kwh_month = target + surplus
daily_required = required_generation / days_in_month
```

### B.2 Solar panels

PVOUT path is linear per-kWp, so:

```
yield_per_kwp_day = PVOUT / 365
required_kwp      = daily_required / yield_per_kwp_day
panels_needed     = ceil(required_kwp × 1000 / panel_wattage)
```

With today's 400 W panel constant. Research needed: representative PH-market panel wattages (400–550 W), price per panel or per Wp, whether to keep PVOUT or add a PR-derated fallback for PVOUT-missing locations (then `required_kwp = daily_required / (GHI × PR)`).

### B.3 Wind turbines

Per-unit output already exists — un-scale it first:

```
per_turbine_monthly = monthly_energy_kwh / wind_generation_scale   (from assumptions)
turbines_needed     = ceil(daily_required × days / per_turbine_monthly)
```

Caveats: a "household wind turbine" count > ~2 is impractical for most homes (rotor 12.4 m diameter); show it but flag feasibility. The 1.2 kW/6.2 m-radius product is a modeling stand-in — research real PH-available small-wind specs (rated kW, rotor diameter, cut-in, price).

### B.4 Hydro

Not a count — report the site's `available_power_kw` and whether it can carry the load:

```
site_kw = available_power_kw (already computed, un-scaled)
covers_load = site_kw ≥ daily_required / 24   (with capacity-factor derating)
```

If insufficient, the honest output is "run-of-river at this site yields ≈X kW — enough for Y% of your target," not "buy N turbines."

### B.5 Battery storage

Purpose: shift daytime surplus into non-solar hours (and store exportable surplus if user wants >100%).

```
daytime_fraction        = share of daily load during solar hours (research: ~0.30–0.45 PH)
daily_surplus           = max(daily_gen − daily_load × daytime_fraction, 0)
nightly_need            = daily_load × (1 − daytime_fraction)
usable_battery_kwh      = min(daily_surplus, nightly_need)          (cover-the-night case)
nameplate_kwh           = usable_battery_kwh / depth_of_discharge    (LiFePO4 DoD ≈ 0.90)
charge_loss             = nameplate × (1 − round_trip_efficiency)    (η_rt ≈ 0.90–0.95)
batteries_needed        = ceil(nameplate_kwh / unit_battery_kwh)     (e.g., 5 kWh modules)
```

If the user wants to store surplus for export rather than self-consume, `usable_battery_kwh = min(daily_surplus, desired_export)` — same formula, different right-hand side. Both are special cases of `min(available_surplus, demand_to_shift)`.

### B.6 Export / sell-back (net metering)

```
exportable_kwh_month = max(surplus − stored_kwh, 0) × inverter_efficiency(0.96)
export_credit_php    = exportable × export_rate_php_kwh
monthly_benefit      = self_consumed_kwh × retail_rate + exportable × export_rate
```

**Critical:** Philippine net metering (RA 9513 / ERC rules) credits exported energy at roughly the **generation charge** — about half of retail — not the retail rate. Using retail overstates benefit ~2×. The in-repo Meralco CSV (₱3.70–5.79/kWh generation charge, 2011-2020) is a starting point but needs current values.

### B.7 Cost and payback (re-enabled)

```
system_cost_php = panels × panel_cost  OR  required_kwp × php_per_kwp_installed
                + turbines × turbine_installed_cost
                + battery_kwh × php_per_kwh_installed
                + inverter + BOS + labor + permits (see BOM)
annual_benefit  = 12 × (self_consumed × retail + exported × export_rate)
payback_years   = system_cost / annual_benefit
```

Existing ₱60k–100k/kW constants are placeholders hidden for exactly this reason — research real installed ₱/kW before un-nulling.

---

## PART C — Research / data-gathering checklist (for NotebookLM + own research)

Group research by what each item feeds. Every constant needs a Philippine-market source, not US/EU defaults.

### C.1 Net metering and export economics (Meralco / ERC / DOE)

1. **RA 9513 net-metering mechanics** — how credits are computed, caps (≤100 kW residential?), rollover rules, whether credits are in kWh or ₱.
2. **Meralco net-metering process** — application steps, costs (bi-directional meter fee, inspection), approval time, actual credited rate per kWh (which billing component offsets: generation charge only? distribution too?).
3. **Current Meralco residential rate decomposition** — generation vs transmission vs distribution vs taxes vs FIT-All, so we can show "you sell at ~₱5 but buy at ~₱11-13" honestly. (Seed data already in repo: `meralco_rates_2011_2020.csv`, needs 2021-2025 update.)
4. **ERC feed-in tariff (FIT) rates** — whether a household can choose FIT vs net metering and current ₱/kWh FIT per source.
5. **DU coverage** — net metering applies to on-grid users in franchise areas; how to phrase when municipality's DU isn't Meralco.

### C.2 Solar sizing constants (Philippine market)

6. Representative panel wattage and ₱/panel (and ₱/Wp) — Lazada/Shopee/PH-solar-reseller ranges for 400–550 W mono panels.
7. Installed ₱/kWp for residential rooftop PH (per kW turnkey including labor) — validate or replace the ₱60,000 placeholder.
8. PH-grid-appropriate inverter specs and prices (single-phase 1–10 kW hybrid vs string), and whether hybrid inverters bundle MPPT charge controllers.
9. Roof-area constraint — m² per panel (~2 m²), so we can cap `panels_needed` by an optional roof-area input.
10. Whether PVOUT (Global Solar Atlas) coverage exists for all target municipalities, or the GHI×PR fallback needs calibration for PH monsoon/cloud.

### C.3 Wind sizing constants

11. Real small-wind products sold in PH — rated kW, rotor diameter, cut-in, price (the model's 1.2 kW / 6.2 m-radius stand-in needs replacing or justifying).
12. Whether horizontal small-wind at household scale is viable in PH at all (most literature says marginal outside coastal/ridge sites) — informs whether to show a count or "not recommended."
13. BOS for small wind: tower height/cost, foundation, guy wires, charge controller/dump load.

### C.4 Hydro sizing constants

14. Pico/micro-hydro products or typical DIY Philippine run-of-river specs — kW range, penstock, civil works cost per kW.
15. Environmental/legal requirement — water rights / NWRB permits for small installations; whether household-scale hydro is legally feasible (affects whether we show it as an option at all).

### C.5 Battery storage (biggest gap — nothing exists)

16. **LiFePO4 ₱/kWh installed** in PH — per-unit prices for common modules (e.g., 5 kWh wall-mount, 2.4/3.5 kWh rack), and whether DIY cells vs branded differ.
17. **Depth of discharge and cycle life** per chemistry (LiFePO4 ~90% DoD, ~4-6k cycles; lead-acid ~50%, ~1k) — justifies recommending lithium despite price.
18. **Round-trip efficiency** (~90-95% LiFePO4, ~80% lead-acid) for charge losses.
19. **Autonomy days convention** — whether to size for 1 night only vs N days of cloud cover (off-grid sizing standard is 1–3 days; decide which).
20. **C-rate / power rating** — battery must also deliver the evening peak kW, not just store kWh; whether to add a kW check.
21. Battery degradation/replacement horizon (warranties ~5-10 yr) — needed for honest payback when batteries are included (they wear out before panels do).

### C.6 Consumption profile assumptions

22. **PH household daytime vs nighttime load fraction** — what share of a typical Filipino household's daily kWh is used during solar-generating hours (~7am–5pm)? This single constant drives the self-consumption/storage/export split. Look for Meralco/DOE load-research-cell data, academic PH household-load-curve studies, or IES/UP datasets. If none exists, a defensible default (e.g., 0.35) with sensitivity shown.
23. Typical PH household monthly kWh/bill distribution for sanity-check bounds (ERC/DOE lifeline <100 kWh stats).

### C.7 BOM / balance of system per setup

24. Solar home BOM: panels, inverter (hybrid if battery), mounting rails, combiner/fuses, DC/AC breakers, grounding, wiring, net-meter, charge controller (if DC-coupled), batteries, labor %, permits/fees.
25. Wind BOM: turbine, tower, foundation, controller, inverter, dump load, batteries.
26. Hydro BOM: turbine, penstock, intake/weir civil works, controller, inverter, channel maintenance.
27. Cost shares per line — the dead `EcosimBOM.jsx` uses 40/20/15/20/5% for solar; validate against PH installer quotes or BOM literature.

### C.8 Where each number lands in code

- New constants → `app/config/settings.py` (env-overridable, like the existing household constants)
- Battery/export math → new small module `app/services/sizing.py` (mirrors `financials.py` pattern)
- Response → new `sizing` block in `EcosimDashboardResponse`; add inputs to `cache_payload` (scoring_version bump to v6)
- UI → revive `EcosimBOM.jsx` or slim sizing card in `EcosimResults.jsx`; PDF in `ecosimPdf.js`

---

## PART D — What the user answers look like (concrete worked example)

Given: monthly bill ₱5,000 at ₱12/kWh → ~417 kWh/month; desired_savings = 100% + battery storage.

1. Target: 417 kWh/month, ~13.9 kWh/day.
2. Solar at PVOUT 1,400 kWh/kWp/yr → 3.84 kWh/kWp/day → need 13.9/3.84 = **3.6 kWp → 9 × 400 W panels**.
3. Daytime fraction 0.35 → day use 4.9 kWh, night use 9.0 kWh/day.
4. Generation 13.9/day − day use 4.9 = 9.0 surplus → usable battery = min(9.0, 9.0) = 9.0 → nameplate 9.0/0.90 = **10 kWh → 2 × 5 kWh LiFePO4 modules**.
5. Export = max(9.0 − 9.0 stored, 0) = 0 kWh → nothing to sell (fully offset). For >100% case: extra gen − stored → credited at ~₱5/kWh generation charge, not ₱12 retail — e.g., 100 kWh/month exported ≈ **₱500 credit**, shown explicitly as "≈₱500/month Meralco net-metering credit."
6. Cost: 9 panels + hybrid inverter + 10 kWh battery + BOS + labor → payback = cost / annual bill savings (₱60,000/yr saved here).

That end-to-end example is the acceptance test for the whole feature.

---

## PART E — Decisions needed before implementation

**E.1 Temporal granularity** — (a) monthly-average + assumed daytime fraction (recommended — matches existing model precision), (b) explicit two-bucket day/night model, (c) hourly simulation (rejected: implies accuracy the monthly climate inputs don't have).

**E.2 Wind/hydro unit counts** — (a) show raw `ceil()` counts with feasibility caveats, (b) show counts but cap at a practical max with "consider hybrid solar+wind" guidance, (c) show feasibility + equivalent kW only. Recommend (b).

**E.3 Economics visibility** — (a) un-null the already-computed economics once ₱/kW and ₱/kWh are researched (recommended — the engine is done), (b) keep hidden and show only a sizing-derived cost range, (c) show both. Depends on cost-data confidence.

**E.4 Where sizing lives** — (a) new `sizing` block inside existing `/ecosim/` response (recommended — reuse climate fetch, cache, explanations), (b) separate `/ecosim/sizing` endpoint (extra round-trip, split cache), (c) frontend-only sizing using existing response fields (loses un-scaled per-unit values unless exposed).

**E.5 Battery role** — (a) sizing for self-consumption shift only (recommended starting scope), (b) + export-storage mode, (c) + backup-power/autonomy mode. (a) covers the stated use case; (b) is the same formula with a different demand term.

---

## PART F — Implementation order (post-research)

1. `sizing.py` service + settings constants (battery ₱/kWh, DoD, η_rt, daytime_fraction, export_rate, unit sizes) — pure functions, assert-tested.
2. Un-scale wind/hydro per-unit outputs; solar per-kWp yield derivation; `panels/turbines/batteries` counts.
3. `sizing` block in `/ecosim/` response + `cache_payload` v6 bump.
4. Export credit at generation-charge rate; "sell ≈₱X/month" line.
5. Revive or reimplement `EcosimBOM.jsx`; PDF section; i18n en/fil keys.
6. Decide economics visibility; fix capped-vs-uncapped savings inconsistency in `financials.py`.
