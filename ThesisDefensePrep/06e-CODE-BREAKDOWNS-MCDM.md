# 06e — MCDM Breakdown: Every Weight, Factor & Formula

> The complete reference for the weighted multi-criteria recommendation engine — every weight
> verbatim, every factor's provenance, every formula with code, two hand-computed worked
> examples, sensitivity analysis, and the honest runtime-vs-dormant map. Use this when the panel
> asks *"how does the scoring actually work?"* or *"where did the weights come from?"*
>
> **TOC:** [§0 Runtime truth map](#0-runtime-truth-map-read-this-first) ·
> [§1 All weight tables](#1-complete-weight-tables) · [§2 Factor provenance](#2-factor-provenance-per-source) ·
> [§3 Formulas](#3-the-formulas) · [§4 Worked examples](#4-worked-examples) ·
> [§5 Sensitivity](#5-sensitivity-analysis) · [§6 Thesis linkage](#6-thesis-validation-linkage) ·
> [§7 Honest caveats](#7-honest-caveats--discrepancies) · [§8 Q&A hooks](#8-panel-qa-hooks)

---

## 0. Runtime truth map (read this first)

LUMI's "weighted MCDM engine" is actually **four scoring paths**, and only some use AHP weights.
This table is the single most defensible summary — learn it before any weight question.

| Path | Where | Method | Uses `mcda_weights`? | Status |
|---|---|---|---|---|
| **EcoSim household scoring** | `ecosim.py` → `solar/wind/hydro_output_calc.py`, `geothermal/` | Physics output → baseline-normalized score → proximity boost → `source_score × (0.4 + 0.6×ratio) × 100` | **No** (except geo sub-score) | **LIVE** — the defended engine |
| **Geothermal AHP sub-score** | `geothermal/features.py` L557–597 | 5 criteria × AHP weights, availability-masked weighted sum | **Yes** — the only live consumer | **LIVE** |
| **Map-level municipality scores** | `municipality_suitability_builder.py` | Single-factor normalizations + **unweighted mean** composite | No | **LIVE** (feeds EnergyHub map) |
| **Confidence scoring** | `confidence.py` | 4-factor weighted mean (data quality, not resource) | Own weights | **LIVE** |
| `mcda.py` trio (`ahp_consistency_ratio`, `aggregate_score`, `promethee_ii`) | `services/mcda.py` | AHP CR + weighted sum + PROMETHEE II outranking | Reads weights when invoked | **DORMANT** — zero callers in routes/services/tests/scripts; infrastructure for validation/cross-checks |
| Solar/wind/hydro weight rows | `mcda_weights` table / `_DEFAULT_WEIGHTS` | — | Present but nothing fetches them at runtime | **DORMANT** — documented defaults, tunable via SQL |
| Geothermal RF classifier | `geothermal/ml_classifier.py` | RandomForest on AHP sub-scores | Trains on AHP outputs | **EXCLUDED** — thesis explicitly says "exists in the codebase but was excluded from this evaluation" |

**One-liner for the stand:** *"The household recommendation is a deterministic weighted linear
combination over physics-based sub-scores; AHP-style weights drive the geothermal sub-score, and
the full MCDA utility functions exist for weight validation and outranking cross-checks."*

---

## 1. Complete weight tables

Every numeric weight that shapes a score, verbatim with its source.

### 1.0 What is WLC — the method LUMI actually ships

**Weighted Linear Combination (WLC)** — also called the **weighted sum model (WSM)** — is the
simplest MCDM aggregation: each criterion is normalized to a common scale, multiplied by its
importance weight, and summed.

```
score = Σᵢ ( wᵢ × xᵢ ),   where Σᵢ wᵢ = 1 and every xᵢ is on the same scale (0–1 or 0–100)
```

- **Compensatory**: a strong criterion can offset a weak one — which is why factor masks and
  renormalization (§3.1) matter when data is missing.
- **No pairwise comparisons needed**: unlike AHP's derivation step or PROMETHEE's outranking
  matrix, WLC runs in O(n) per alternative — fast enough for a real-time web query, and every
  score decomposes into `wᵢ × xᵢ` contributions a user can read. That is exactly the reason
  **Beriro et al. (2022)** chose WSM for their UK onshore-wind feasibility web DSS — *"the lack
  of need for pairwise comparison allowed the model to … assess the feasibility of renewable
  energy infrastructure faster"* — and LUMI's own stated rationale.
- **Canonical GIS-MCDM reference**: Malczewski (2006); Philippine precedent for the method
  family: Tarife et al. (2023), Asadi et al. (2023). Shorabeh et al. (2021) combine ANP +
  Fuzzy + WLC for Iran sites.

**AHP vs WLC — how they relate** (the panel's favorite confusion): they answer *different*
questions. AHP derives **what the weights should be** (expert pairwise judgments → priority
vector → consistency check); WLC computes **how the scores combine** given weights. LUMI uses
both in sequence on the geothermal path — AHP-derived weights, WLC aggregation — and WLC alone
everywhere else.

**Where WLC appears in LUMI** (all four are WLC variants, each documented below):

| Path | Form | Status |
|---|---|---|
| Geothermal sub-score | availability-masked WLC: `Σ(wᵢ·xᵢ)/Σwᵢ(available)` | **LIVE** — `features.py` L583–597 |
| EcoSim household composite | 2-factor WLC: `source_score × (0.4 + 0.6·ratio) × 100` — the paper cites **Vanegas-Cantarero et al. (2022)** for the 60/40 split | **LIVE** — `ecosim.py` L1767 |
| Confidence score | 4-factor WLC: coverage .35 + recency .15 + maturity .30 + resolution .20 | **LIVE** — `confidence.py` L105–110 |
| Map composite | degenerate WLC — equal weights, i.e. `mean(available)` | **LIVE** — `municipality_suitability_builder.py` L113–119 |
| `mcda.py aggregate_score` | generic WLC over arbitrary criteria | **DORMANT** — zero callers |

**Thesis's own wording** (for quoting under pressure): Ch.1 synthesis calls the approach
*"a weighted multi-criteria scoring … to combine important environmental and energy-related
factors"*; the EcoSim methodology text says the composite *"combines 60 percent energy coverage
with 40 percent source quality, following the weighted linear combination approach used in
GIS-MCDA renewable energy site-selection studies (Vanegas-Cantarero et al., 2022)"*; and the
EnergyHub choropleth section describes a *"weighted linear combination"* citing Candan et al.
(2022) — with the discrepancy flagged in §7.5.

### 1.1 AHP criterion weights — `mcda_weights_service.py` L16–44 + `mcda_weights` table

| Energy type | Criterion | Weight | Live? |
|---|---|---|---|
| geothermal | `heat_flow` | **0.30** | ✅ |
| geothermal | `fault` | **0.15** | ✅ |
| geothermal | `volcano` | **0.10** | ✅ |
| geothermal | `aquifer` | **0.15** | ✅ |
| geothermal | `temperature` | **0.10** | ✅ |
| *(geothermal sums to 0.80 — remaining ~0.20 headroom is the separate plant-proximity boost)* | | | |
| solar | `irradiance` | 0.40 | ⚠️ dormant |
| solar | `temperature` | 0.20 | ⚠️ dormant |
| solar | `cloud_cover` | 0.20 | ⚠️ dormant |
| solar | `terrain_slope` | 0.10 | ⚠️ dormant |
| solar | `land_use` | 0.10 | ⚠️ dormant |
| wind | `wind_speed` | 0.40 | ⚠️ dormant |
| wind | `terrain_roughness` | 0.20 | ⚠️ dormant |
| wind | `elevation` | 0.20 | ⚠️ dormant |
| wind | `land_use` | 0.10 | ⚠️ dormant |
| wind | `air_density` | 0.10 | ⚠️ dormant |
| hydro | `rainfall` | 0.30 | ⚠️ dormant |
| hydro | `watershed_slope` | 0.25 | ⚠️ dormant |
| hydro | `catchment_area` | 0.25 | ⚠️ dormant |
| hydro | `hydraulic_head` | 0.20 | ⚠️ dormant |

- Loader: `load_mcda_weights()` fetches active rows from `mcda_weights` (energy_type × criterion,
  `is_active` partial-unique index, integer `version` for revision history) → in-memory cache →
  falls back to `_DEFAULT_WEIGHTS` if table missing/empty/unreachable. `invalidate_weights_cache()`
  exists for post-update refresh. **Weights are normalized to sum 1 inside the scorer**, so
  stored sums needn't equal 1.0.
- **Provenance: `UNVERIFIED:`** — code/docstrings call these "AHP-derived"/"expert judgment"
  defaults (solar: irradiance dominates "primary energy input"; wind: V³ scaling; hydro:
  rainfall+slope needed for flow; geo: heat flow primary). **No pairwise matrices or derivation
  artifacts exist in the repo.** Defend as: *literature-informed defaults (Asadi 2023 GIS-AHP;
  Tarife 2023 PH GIS-Fuzzy-AHP; Shatnawi 2021 criterion importance) that are tunable via the
  `mcda_weights` table — the design point is tunability + fallback resilience.*

### 1.2 Confidence weights — `confidence.py` L105–110

| Factor | Weight | What it measures |
|---|---|---|
| `coverage` | **0.35** | Data availability: climate (0.3 + 0.3×vars/10) + terrain .15 + population .1 + tariff .1 + user inputs .05 |
| `recency` | **0.15** | Climate-data age: ≤2y→1.0, ≤5y→0.8, ≤10y→0.6, older/unknown→0.4/0.3 |
| `model_maturity` | **0.30** | Per-source: solar .85, wind .70, hydro .65, geothermal .40 |
| `spatial_resolution` | **0.20** | Fixed .55 (NASA POWER ~0.5° ≈ 50 km — coarse for municipal work) |

Output: `overall×100` → High ≥75 / Moderate ≥55 / Low ≥35 / Very Low. Plus generated
recommendations for improving confidence (data gaps → fetch hints). **This is a meta-score
about data quality — it is NOT the suitability score.** Keep them separate on the stand.

### 1.3 EcoSim composite weights — `ecosim.py` L1763–1767

```python
energy_ratio = min(generation_kwh / consumption_kwh, 1.0)
suitability_score = source_score * (0.4 + 0.6 * energy_ratio) * 100
```

- `source_score` (0–1) = resource quality; `energy_ratio` = household coverage, capped at 1.0.
- Reading: **40% of the score is "pure resource," up to 60% scales with how much of your bill the
  source can actually cover.** A perfect resource covering nothing scores 40 — a resource
  covering your whole bill keeps its full quality score.

### 1.4 Score baselines — `ecosim.py` L1356–1359 (returned in payload for transparency)

| Source | Baseline | Score formula | Rationale |
|---|---|---|---|
| solar | `solar_score_baseline_pvout = 1800` kWh/kWp/yr | `min(pvout/1800 × 100, 100)` | "1800 is excellent for PH" (`solar_output_calc.py` L336–337) |
| solar (alt paths) | 6.0 kWh/m²/day | `min(irr/6.0 × 100, 100)` | `solar_calc` L186, `solar_calc_advanced` L289 — used when PVOUT unavailable |
| wind | `wind_score_baseline_kwh = 300` kWh/mo | `min(kwh/300, 1.0)` | output-normalized so comparable to solar/hydro |
| hydro | `hydro_score_baseline_kwh = 100` kWh/mo | `min(final_kwh/100, 1.0)` | output floor (calibration version "v5") |
| geothermal | — | `geothermal_score × 100` | AHP score passthrough |

### 1.5 Proximity boost parameters — `geothermal/plants.py` L116–143, `wind_plants.py` L129–168, `hydro_plants.py` L129–167

| Param | Value | Behavior |
|---|---|---|
| `max_bonus` | 30 (geo) / `DEFAULT_MAX_BONUS` (wind, hydro) | bonus = `max_bonus × (1 − dist/radius)` — linear taper |
| `DEFAULT_BOOST_RADIUS_KM` | module constant | only *operating* plants count |
| province fallback | `max_bonus × 0.5` | wind (and hydro): no coords → same-province plant = half bonus |
| cap | `min(base + bonus, 100)` | cannot exceed 100 |

### 1.6 Classification bands

| Band | EcoSim (`explanation` ratings) | `get_classification`/`aggregate_score` | Geothermal (0–1) |
|---|---|---|---|
| top | ≥80 Excellent | ≥81 Very High | ≥0.80 High |
| high | ≥60 Good | ≥61 High | ≥0.60 Good |
| mid | ≥40 Moderate | ≥41 Moderate | ≥0.40 Moderate |
| low | ≥25/21 | ≥21 Low | <0.40 Low |
| bottom | <25 Fair | <21 Very Low | |

### 1.7 Hydro upstream constants — `build_catchment_enrichment.py` + `hydro_output_calc.py`

| Constant | Values |
|---|---|
| Runoff coefficient C (by slope) | <3°: 0.30 · 3–10°: 0.45 · 10–20°: 0.60 · >20°: 0.75 |
| Drainage-density multiplier | 0.8–1.2 (norm over 0.65–1.23 km/km²) |
| Hypsometric-integral multiplier | 0.9–1.1 (higher HI → flashier catchment) |
| C clip | 0.20–0.85 |
| Stream-feasibility penalty | 0.1–1.0 (too-far streams → 0.1) |
| Rational method | `Q_design = (C·P·A)/t × 0.40` design-flow factor; `c_eff = C×(0.5+0.5·runoff_potential)×(0.7+0.3·watershed_gradient)` |
| Flow clamp | 0.001–0.5 m³/s (floor applied **only when no enrichment data** — genuinely dry areas show 0) |
| Turbine/generator/head | 0.75 / 0.90 / `head_factor` 0.20 |

---

## 2. Factor provenance per source

Where each score's inputs actually come from — the chain a "what feeds this number?" answer needs.

### 2.1 Solar (household)

| Factor | Raw variable | Source | Transform → sub-score |
|---|---|---|---|
| irradiance / PVOUT | `solar_pvout_annual_kwh_kwp` or `allsky_sfc_sw_dwn` | Global Solar Atlas CSV / NASA POWER `municipality_climate_monthly` | `/1800` (PVOUT path) or `/6.0` (irradiance path) → 0–100 |
| temperature derating | `t2m` | NASA POWER | ~−0.4%/°C above 25°C (PR factor) |
| dust/humidity/inverter/mismatch/wiring | fixed PR constants + `ws10m`, `rh2m` | hardcoded physics factors | multiplicative PR ≈ system eff .80 × temp × dust × inv .96 × mismatch .98 × wiring .98 × degr. |

### 2.2 Wind (household)

| Factor | Raw variable | Source | Transform → sub-score |
|---|---|---|---|
| wind speed | `ws10m` | NASA POWER / Wind Atlas | power curve → monthly kWh (Betz-limit Cp enforced — tested) |
| output → score | `monthly_energy_kwh` | computed | `/300` cap 1.0 |
| proximity | operating wind plants | `wind_plants.py` registry | +tapered boost (province fallback ×0.5) |

### 2.3 Hydro (household)

| Factor | Raw variable | Source | Transform → sub-score |
|---|---|---|---|
| rainfall | `prectotcorr` | NASA POWER | monthly precip → rational-method flow |
| runoff coefficient | slope → C base; refined by drainage density + hypsometric | catchment enrichment (Boothroyd 2023) | C = base × dd_mult × hi_mult, clip .2–.85 |
| catchment area | `effective_catchment_area_km2` | catchment enrichment | area → Q_design |
| head | `stream_head_m` / `hydraulic_head_m` | enrichment / `hydropower_suitability` | × `head_factor` 0.20 |
| feasibility | `stream_feasibility_penalty` | enrichment | distance-based 0.1–1.0 |
| output → score | `final_hydro_kwh` | computed | `/100` cap 1.0; floor only w/o enrichment |
| proximity | operating hydro plants | `hydro_plants.py` | +tapered boost |

### 2.4 Geothermal (the true AHP path)

| Criterion | Raw variable | Source | Transform → sub-score |
|---|---|---|---|
| `heat_flow` | heat flow mW/m² | geothermal datasets (IDW) | dataset score (0–1) |
| `fault` | `fault_distance_km` | fault lines | `exp(−d/20)` — distance-decay |
| `volcano` | `volcano_distance_km` | volcano registry | `exp(−d/30)` — distance-decay |
| `aquifer` | permeability, porosity, thickness | PH aquifer rows | `calculate_aquifer_score` composite |
| `temperature` | `surface_temp_c` | surface temp proxy | `_normalize(20–35°C)` |
| *(post-score)* | operating geo plants | `plants.py` | +30-pt tapered boost, cap 100 |
| output context | `reservoir_temperature_c`, `geothermal_score_mcda` | `geothermal_output`/`geothermal_suitability` | feeds map + suitability columns |

**Availability masking** (`features.py` L578–590): each criterion contributes `weight × score`
**only if data exists** (`avail` flag — fault/volcano count when distance was measured; others
when score > 0). The weighted sum is **divided by the available weight only**, so missing data
renormalizes the remaining weights instead of silently zeroing them out.

### 2.5 Map-level scores (EnergyHub choropleth, `municipality_suitability_builder.py`)

| Score | Formula | Note |
|---|---|---|
| solar | `min(irr/5.0 × 100, 100)` | **single-factor** — irradiance only (not the AHP row) |
| wind | `min(ws10m/7.0 × 100, 100)` | single-factor |
| hydro | `hydro_suitability_score × 100` | passthrough of upstream score |
| geothermal | `geothermal_score × 100` | passthrough (+ `geothermal_score_mcda` column kept) |
| composite | `mean(available scores)` | **unweighted average** — a degenerate WLC with equal weights (see §7.5: the paper describes 40/30/30 weights here — the code ships an equal-weight mean over ≤4 sources) |

Fallbacks: `_estimate_solar_from_lat` (PH ~5–20°N), wind → flat 3.2 m/s when no data.

---

## 3. The formulas

### 3.1 Geothermal AHP weighted sum (live) — `features.py` L583–597

```python
total_weight = sum(ahp_weights[k] * avail[k] for k in ahp_weights)
geothermal_score = sum(sub_scores[k]*ahp_weights[k]*avail[k] for k in ahp_weights) / total_weight
geothermal_score = clamp(0, 1)
```

Per criterion: `sub_scores = {heat_flow, fault=e^{−d/20}, volcano=e^{−d/30}, aquifer, temp}`.
**Plain:** each available criterion contributes `weight × score`; dividing by *available* weight
means a municipality missing aquifer data is scored on the 4 criteria it has — not penalized to
zero. Classification ≥0.80 High / ≥0.60 Good / ≥0.40 Moderate / else Low.

### 3.2 Household composite (live) — `ecosim.py` L1763–1767

`suitability = source_score × (0.4 + 0.6 × energy_ratio) × 100`. See §1.3 — **the resource
quality scales the whole score; coverage scales within it.** NOT the `0.6×ratio + 0.4×score`
form shown in `docs/MCDA_BREAKDOWN.md` §2.2 — see §7 discrepancy.

### 3.3 Recommendation selection (live) — `ecosim.py` L2118–2138

- Household options only: `source_type != "utility"` (**geothermal excluded from household
  recommendation — shown as reference**).
- Key: `(min(monthly_output, consumption), suitability_score)` — **usable output first**, capped
  at consumption; suitability score is only the tie-breaker.
- Hidden `suitability_recommended` = max suitability (stored, not shown — "for future reactivation").
- AI override only when a `reason` is provided.

### 3.4 Confidence (live) — `confidence.py` L99–141

`overall = .35·coverage + .15·recency + .30·maturity + .20·resolution` → ×100 → bands + actionable
recommendations. Data-quality meta-score, never the suitability itself.

### 3.5 Proximity boost (live) — all three `*_plants.py`

`bonus = max_bonus × (1 − distance_km / radius_km)` on the **closest operating plant** →
`min(base + bonus, 100)`. Wind/hydro add a province-level half-bonus when no coordinates.

### 3.6 DORMANT trio — `mcda.py` (callable infrastructure, zero live callers)

- `ahp_consistency_ratio` (L16–60): eigenvector-approx priority vector → λ_max →
  `CI=(λ−n)/(n−1)` → Saaty RI (n=1–10) → `CR=CI/RI`; `is_consistent = CR<0.10`. For validating
  expert pairwise matrices *if* an AHP exercise is ever run.
- `aggregate_score` (L63–123): normalized weighted sum over arbitrary criteria + 5-band
  classification; equal-weights fallback when none provided.
- `promethee_ii` (L126–213): Type-5 linear preference w/ indifference threshold q (default 10%
  of range) → pairwise π matrix → positive/negative/net flows → complete ranking. Cross-check
  alternative to weighted-sum rankings.

**If asked "does PROMETHEE II run in production?" → honest answer:** *"The module is implemented
and unit-testable but not wired into the live request path; the shipped engine is WLC, matching
the paper's 'weighted multi-criteria' description."*

### 3.7 Geothermal RF classifier (excluded) — `ml_classifier.py`

Trains `RandomForest` on AHP features + score labels; **thesis states it was excluded from the
evaluation** — mention only if asked "is there ML beyond ARIMA?"

---

## 4. Worked examples

### 4.1 Geothermal AHP — illustrative municipality, partial data

*Illustrative inputs* (same transforms as `features.py`; test fixtures confirm `exp`/`_normalize`
math — `test_geothermal_calculations.py`):

| Criterion | Raw | Sub-score | Weight | avail | w·s |
|---|---|---|---|---|---|
| heat_flow | 82 mW/m² → score .72 | .720 | .30 | 1 | .2160 |
| fault | 8 km → e^(−8/20) | .670 | .15 | 1 | .1005 |
| volcano | 45 km → e^(−45/30) | .223 | .10 | 1 | .0223 |
| aquifer | **no data** | .000 | .15 | **0** | 0 |
| temperature | 28°C → (28−20)/15 | .533 | .10 | 1 | .0533 |

- `total_weight` = .30+.15+.10+.10 = **0.65** (aquifer excluded)
- `geothermal_score` = .3921 / .65 = **0.603 → "Good"**
- **Without masking** (÷0.80): .49 → "Moderate". *Masking is what makes partial-data scores fair.*

### 4.2 Household composite — solar vs wind at 400 kWh/month consumption

Solar: PVOUT 1,500 → `source_score` = 1500/1800 = **0.833**; output 320 kWh → `energy_ratio` = 0.8
→ suitability = .833 × (.4 + .6×.8) × 100 = .833 × .88 × 100 = **73.3**

Wind: output 310 kWh → `wind_score` = min(310/300,1) = **1.0**; `energy_ratio` = .775
→ suitability = 1.0 × (.4 + .465) × 100 = **86.5**

**Recommendation key:** solar (320 usable, 73.3) vs wind (310 usable, 86.5) →
**solar wins** — usable output outranks suitability. *This is the subtle piece: the headline
"recommended source" is output-first, score-second; the suitability score is the tie-breaker.*

---

## 5. Sensitivity analysis

- **Weight perturbation (geothermal):** heat_flow .30→.40 on §4.1 inputs → numerator .4641, total
  weight .75 → score .619 vs .603 — a +33% weight move shifts the score ~2.6% because
  renormalization dilutes it. *Weights steer; data dominates.*
- **Availability masking:** each missing criterion removes its weight from the denominator —
  score stays comparable but converges on fewer criteria. All-missing → `total_weight=0` → 0.0.
- **Baseline sensitivity:** wind 250 kWh → .833 (pre-boost); if the 300 baseline were 200, the
  same output caps at 1.0. **The baseline constants are the scoring scale's anchor — they were
  calibration-tuned** (`test_calibration.py` pins wind-output-based scoring, hydro 100 kWh
  anchor, cross-source comparability).
- **energy_ratio cap:** gen 600 vs consumption 400 → ratio caps at 1.0 → score = full
  `source_score × 100`. Over-generation can't inflate the score — and `min(output, consumption)`
  in the recommendation key can't either.
- **Boost cap:** any source can gain ≤30 pts from plant proximity, capped at 100 — a province-
  level wind match gives half that. Boost *nudges*, never manufactures.
- **Confidence floor:** maturity is fixed per source (geo .40 drags its confidence even with
  good data) — expect "Low/Moderate confidence" labels on geothermal; that's designed honesty.

---

## 6. Thesis validation linkage

| Thesis/deck claim | Code ground truth |
|---|---|
| "weighted multi-criteria recommendation engine" | WLC composite `source_score × (0.4+0.6·ratio) × 100` + AHP-weighted geothermal sub-score (`ecosim.py`, `features.py`) |
| "deterministic scoring algorithm (physics-based estimators + weighted MCDA)" | solar/wind/hydro physics → baseline norms; geo AHP weighted sum; no learned weights at runtime |
| 82.22% expert agreement | 37/45 valid matches; 5 EE/ECE experts × 9 locations; "Insufficient Information" excluded from denominator; 80% threshold = 4/5 (Hohmann 2025 consensus bands); per-location: 100%×3, 80%×4, 60%×2 (Bulacan/Cavite → refinement rec) |
| "criteria and rule logic validated through interviews" | Criteria shipped = solar (irr/temp/cloud/slope/land-use rows dormant + PVOUT live), wind (speed etc.), hydro (rainfall/slope/area/head), geo (5 AHP criteria); expert instrument recommended Fuzzy-AHP+TOPSIS — WLC+AHP shipped (see §7) |
| AHP/PROMETHEE in RRL | `mcda.py` implements both — available, not runtime |

**Agreement ≠ accuracy** — the paper says it; say it on the stand.

---

## 7. Honest caveats & discrepancies

1. **`UNVERIFIED:` weight provenance** — "AHP-derived" is a label; no pairwise matrices, survey,
   or derivation notebook exists in-repo. Defensible line: *literature-informed defaults
   (Asadi 2023; Tarife 2023; Shatnawi 2021's technical-criterion dominance), tunable via
   `mcda_weights`, with code fallback so scoring never breaks.*
2. **Interviews recommended Fuzzy-AHP + TOPSIS** (thesis §2.13) — the shipped engine is WLC +
   AHP-weighted geo. If asked: *chosen for transparency, real-time speed, and explainability —
   consistent with Beriro 2022's WSM choice for the same reason.*
3. **`docs/MCDA_BREAKDOWN.md` discrepancies** — §2.2 writes `0.6×energy_ratio + 0.4×source_score`
   (the code is `source_score × (0.4 + 0.6·ratio) × 100`: at source_score .5, ratio 1 the doc
   form gives 80, code gives 50) and §3.1 shows the `irr/6.0` path while EcoSim actually calls
   `solar_calc_pvout` (/1800). Quote the code, not the older doc.
4. **Solar/wind/hydro AHP rows are dormant** — present in `_DEFAULT_WEIGHTS`/schema, unfetched
   at runtime. The live solar/wind/hydro scores are output-normalized physics, not weight-table
   sums. Don't claim "all four sources use AHP weights."
5. **Map composite: paper says WLC 40/30/30, code ships an equal-weight mean** — the thesis
   methodology (Ch.3, citing Candan et al. 2022) describes the provincial choropleth as a
   weighted linear combination — *"solar receives the largest weight at 40 percent, while wind
   and hydropower each receive 30 percent"* over **3** sources. The shipped
   `_compute_composite` (L113–119) computes `sum(available)/len(available)` — an **unweighted
   mean over ≤4** available sources, geothermal included. Defensible line: *"the 40/30/30
   weighting was the design intent from the literature; the deployed builder uses an
   equal-weight composite so a source isn't double-counted through the province rollup — the
   equal-mean is itself a degenerate WLC."* If pressed, own it as a divergence to fix, not a
   feature to hide. Only household EcoSim uses the 0.4/0.6 composite.
6. **`mcda.py` is dormant** — implementable, tested shapes, but no caller. It's honest
   infrastructure, not a production path.
7. **No admin endpoint for weights** — the schema comment says "admin panel or SQL"; only SQL
   works today (`invalidate_weights_cache()` exists for when it changes).

---

## 8. Panel Q&A hooks

- **"Where did the weights come from?"** → literature-informed defaults shaped like Philippine
  GIS-AHP practice (heat-flow dominant for geo, irradiance/speed dominant for solar/wind,
  rainfall+slope+catchment+head for hydro), stored in `mcda_weights` so they're tunable; code
  falls back to defaults so scoring can't break. Provenance of the specific numbers:
  `UNVERIFIED:` — no derivation artifact in-repo.
- **"Why weighted-sum and not TOPSIS/Fuzzy-AHP?"** → transparency + real-time + explainability;
  same reason Beriro 2022 chose WSM. PROMETHEE II + AHP CR are implemented for cross-checks.
- **"Is 82.22% your accuracy?"** → agreement rate with expert assessments (37/45, 9 locations),
  not predictive accuracy — paper itself says so.
- **"What if a weight is wrong?"** → §5: weights steer within renormalization; per-source data
  dominates; tunable table + version column exist for revision.
- **"Why is geothermal excluded from household recs?"** → `source_type=="utility"` — utility-
  scale only; shown as reference because a household can't install a plant.
- **"Does the AI decide the recommendation?"** → no — deterministic engine picks; AI only
  explains (override requires a reason field).
- **"Why can a lower-suitability source win?"** → recommendation key = usable output first
  (capped at consumption), suitability is tie-breaker — a source that covers more of your bill
  is more useful than a marginally better resource that covers less.
- **"What's the confidence score vs the suitability score?"** → confidence = data-quality
  meta-score (coverage/recency/maturity/resolution); suitability = resource+fit. Separate scales.
- **"Is your method WLC or AHP?"** → both, in sequence — they solve different problems. AHP
  derives *what the weights should be* (pairwise judgments → priority vector → CR < 0.10
  consistency gate); WLC is *how the scores combine* (`Σwᵢxᵢ`). Geothermal uses AHP weights +
  masked-WLC aggregation; EcoSim, confidence, and the map composite are plain WLC variants —
  see §1.0. The name to cite for the method is Malczewski (2006); the precedent for choosing
  WSM over pairwise methods in a real-time web DSS is Beriro et al. (2022).
- **"The paper says the map uses 40/30/30 weights — does it?"** → honest answer: the code
  ships an equal-weight mean over available sources (§7.5). The 40/30/30 in the methodology
  chapter is the documented design intent (Candan et al., 2022); flag it as a divergence
  between the paper and the deployed builder — don't improvise a defense of numbers that
  aren't in the code.

---
*Constants verified against `main @ 438789c`. `UNVERIFIED:` marks claims with no in-repo evidence.*
