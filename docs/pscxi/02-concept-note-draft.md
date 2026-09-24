# PHILIPPINE STARTUP CHALLENGE XI — CONCEPT NOTE (DRAFT)

**Team name:** `[TEAM INPUT: registered team name]`
**Startup name:** LUMI — Environmental Intelligence for the Philippines

> **How to use this draft.** Every claim below traces to repository evidence (code, data, docs) or public sources. `[TEAM INPUT: …]` marks facts only the team can supply — do not submit with markers unresolved. This draft follows the official PSC XI concept-note template sections verbatim.

---

## 1. SUMMARY

LUMI is a web platform that turns Philippine climate and energy data into household-level renewable-energy decisions. Filipinos pay among Southeast Asia's highest electricity rates `[TEAM INPUT: cite current ₱/kWh figure + source]`, yet homeowners who consider solar, wind, or micro-hydro have no tool that answers "will this work *in my municipality*, and what would it save me?" without hiring an engineer. LUMI's EcoSim simulator answers that question in plain language (English and Filipino) for all 1,600+ Philippine municipalities, fusing NASA POWER climate data, DOE national statistics, Global Solar/Wind Atlas rasters, and SRTM terrain — with equipment costs grounded in real scraped Philippine e-commerce pricing. EnergyHub complements it with national statistics and ARIMA demand forecasts for planners. The product is live, deployed, and already supports accounts, saved simulations, PDF reports, and premium tiers.

## 2. BACKGROUND OF THE PROBLEM

- Philippine residential electricity prices are among the region's highest `[TEAM INPUT: cite ERC/DOE figure]`; distributed rooftop solar is the most accessible hedge, but adoption is limited by uncertainty, not hardware availability.
- Deciding requires municipality-specific data (solar irradiance, wind at hub height, rainfall + terrain head for micro-hydro, local installer availability) that exists only in technical datasets — NASA POWER, Global Solar/Wind Atlas, DOE statistics — unreadable to non-technical users.
- Generic calculators use national averages or foreign pricing, producing estimates that are wrong for a specific town; homeowners either over-trust them or give up.
- On the planning side, DOE statistics are published as PDFs and spreadsheets; extracting trend lines and forecasts for a province is manual analyst work.
- Relevance: aligns with household energy-cost relief, renewable-energy adoption, and data-driven local planning — all SDG 7 priorities (see §3).

## 3. PROPOSED STARTUP SOLUTION

LUMI is an environmental-intelligence web application with two user-facing modules and an AI layer:

- **EcoSim (households):** pick a municipality (search across 1,600+, or geolocate with a distance sanity-check), enter bill/consumption figures from any Philippine electric bill (built-in bill-reading guide), and receive per-source estimates — solar output (irradiance, temperature, humidity, dust-loss adjusted), wind (power-coefficient + capacity-factor physics), micro-hydro (rainfall + DEM-derived head + slope) — plus economic analysis, a bill of materials, DOE-registry installer recommendations with SEC-verification tiers, and next-step guidance (net metering, LGU incentives). Results are hedged estimates with stated assumptions — "estimates, not promises" is a product commitment.
- **EnergyHub (planners/researchers):** Philippine DOE statistics 2003–2024, ARIMA(1,1,1) 2025–2030 demand forecasts with confidence intervals, generation-mix breakdowns, Luzon/Visayas/Mindanao grid analysis, and province-level choropleth maps.
- **LUMI AI:** Gemini/Groq-powered plain-language analysis, optionally RAG-backed by a vector store of scraped Philippine equipment pricing.

**SDG priority:** **SDG 7 — Affordable and Clean Energy** (primary: household access to actionable renewable-energy information). Secondary: SDG 11 (Sustainable Communities — municipal-level planning data), SDG 13 (Climate Action — CO₂-reduction quantification).

**Stage:** working deployed prototype beyond MVP — production deployment on Vercel, Supabase auth with MFA, bilingual UI, 121 backend + 71 frontend automated tests, completed security audit with fixes applied.

## 4. OBJECTIVES

1. Deliver municipality-specific renewable estimates for 100% of Philippine municipalities served by the dataset (1,600 verified live at evaluation time).
2. Achieve real-user testing cohort of `[TEAM INPUT: target n]` households and measure decision-confidence improvement vs. baseline survey. `[TEAM INPUT: define metric + instrument]`
3. Reach `[TEAM INPUT: target]` registered users / `[TEAM INPUT: target]` simulations run within 6 months of public launch.
4. Validate willingness-to-pay for the premium tier `[TEAM INPUT: price point]` with at least `[TEAM INPUT: n]` paying users or letters of intent from `[TEAM INPUT: LGU/installer partners]`.
5. Maintain the published model-accuracy targets: ARIMA national forecast ≈5.7% MAPE (measured, test set 2021–2024 — see repo README benchmark table).

## 5. TARGET MARKET / BENEFICIARIES

- **Primary:** Filipino homeowners (non-technical) considering rooftop solar or small renewables — especially in high-rate or outage-prone areas; mobile-first, bilingual EN/FIL.
- **Secondary:** energy planners, LGU staff, policymakers, researchers needing provincial statistics and forecasts (EnergyHub); renewable installers as a referral destination.
- **Beneficiary framing:** households gain decision confidence and cost visibility; LGUs gain planning analytics; the grid gains distributed-generation readiness.

## 6. VALUE PROPOSITION

**Municipality-level truth that generic tools cannot copy.** LUMI is the only Philippine tool that fuses NASA POWER municipal climate + DOE national statistics + Global Solar/Wind Atlas rasters + ERA5 + SRTM/HydroSHEDS terrain into per-municipality household assessments, and grounds AI cost estimates in real scraped Philippine e-commerce pricing — not generic figures.

Differentiators vs. alternatives:
- vs. **generic solar calculators**: per-municipality climate truth + PH equipment pricing + Filipino-language plain voice
- vs. **installers' sales quotes**: independent, hedged, non-sales estimates with stated assumptions
- vs. **raw DOE/NASA data**: a bilingual interface a homeowner can actually use; planners get forecasts + maps without PDF extraction work
- **Trust as a feature:** honesty scaffolding (disclaimers, input-consistency warnings, "utility-scale, not a home option" geothermal fallback), data citations on outputs, WCAG AA accessibility commitment

## 7. BUSINESS MODEL

Options supported by the current codebase — `[TEAM INPUT: choose and commit]`:

1. **Freemium SaaS (implemented):** free tier (3 saved scenarios, basic simulations) → premium (unlimited simulations, advanced AI insights, priority RAG, on-demand SARIMA forecasting — `forecast.py` premium gate already enforces this). Revenue: monthly/annual subscription `[TEAM INPUT: pricing research]`.
2. **B2G/B2B licensing:** EnergyHub analytics + municipal suitability data licensed to LGUs, NGOs, and researchers; installer/brand dashboards.
3. **Referral/marketplace revenue:** DOE-registry installer recommendations → qualified-lead fees (provider-matching pipeline `matchProviders.js` already ranks by tech fit and SEC verification).

Recommended primary: freemium (already coded end-to-end) with B2G pilots as the credibility channel.

## 8. MARKET ANALYSIS

`[TEAM INPUT: this section needs cited research — do not submit unverified numbers. Suggested sources below.]`

- **TAM sketch:** ~`[TEAM INPUT]` million Philippine households (PSA census); addressable subset = grid-connected homeowners with rooftop potential in municipalities with solar/wind/hydro viability (the repo's own suitability tables can produce a defensible count — run `municipality_suitability` aggregates).
- **Demand signals:** record-high retail electricity rates; net-metering program growth `[TEAM INPUT: ERC figures]`; government renewable targets under the Philippine Energy Plan.
- **Competition:** generic international calculators (no PH municipal data), installer-provided estimates (sales-incentivized), manual engineering consultancies (expensive, slow). No direct Philippine per-municipality consumer competitor identified in this review — verify before claiming.
- **Trend tailwinds:** declining PV module costs, e-commerce availability of solar kits (the repo's scraped pricing corpus is itself evidence of market maturity), government RE push.

## 9. OPERATIONS PLAN

- **Product:** already built and deployed (Vercel frontend + FastAPI serverless backend, Supabase Postgres/Auth, Upstash Redis). Ops cost is near-zero at demo scale on free tiers.
- **Data pipeline:** NASA POWER / DOE / Atlas / ERA5 / SRTM ingested offline into Supabase + bundled fallbacks; ARIMA forecasts pre-computed (no runtime training); scraped pricing feeds the RAG knowledge base.
- **Delivery:** web app — no distribution friction; bilingual UI; PDF reports for offline sharing.
- **Team ops:** `[TEAM INPUT: roles — e.g., lead dev, data lead, pitch lead, mentor]`
- **Roadmap:** real-user testing → fix-forward on feedback → premium launch → LGU/installer partnerships → optional mobile wrapper (the abandoned `expo-mobile` scaffold shows intent, not a commitment).
- **Risk ops:** Supabase SMTP must be configured before user-testing volume (audit L9/L13); production env flags (`ENVIRONMENT`, `CORS_ORIGINS`) to be set per `01-evaluation-report.md` M1.

## 10. FINANCIAL REQUIREMENT

`[TEAM INPUT: fill with real figures — the ranges below are placeholders to localize, not estimates to submit.]`

| Item | Est. cost (₱) | Purpose |
|---|---|---|
| Cloud hosting (Vercel/Supabase/Upstash paid tiers) | [TEAM INPUT] | Production reliability beyond free tier |
| LLM API usage (Gemini/Groq) | [TEAM INPUT] | AI analysis + RAG features |
| Domain + email (custom SMTP) | [TEAM INPUT] | Trust + transactional email |
| User-testing incentives | [TEAM INPUT] | Household cohort recruitment |
| Marketing/community outreach | [TEAM INPUT] | LGU demos, installer outreach |
| Contingency (10–15%) | [TEAM INPUT] | — |
| **Total ask** | **[TEAM INPUT]** | — |

Use-of-funds narrative (for the video pitch): funds extend an already-built product into validated adoption — they buy *users and evidence*, not engineering.

---

## Evidence appendix (repo-traceable claims)

| Claim | Evidence |
|---|---|
| 1,600+ municipalities | `GET /api/v1/ecosim/municipalities` → 1,600 items (live 2026-09-24) |
| ARIMA MAPE ≈5.67% | README benchmark table; `docs/04-ML-Data-Science/` |
| Deployed production app | `https://lumi-frontend-xi.vercel.app` + `lumi-backend-ten.vercel.app` (live-verified) |
| Security posture | `docs/audits/prelaunch-audit.md` + migrations 0024/0025 fixes; `docs/pscxi/01-evaluation-report.md` |
| Bilingual EN/FIL | `react-frontend/src/i18n/en.json` + `fil.json` (795-key parity) |
| Data sources | README data table; `data/` corpus |
| DOE installer registry | `matchProviders.js`, `providers.json`, `ProviderRecommendations.jsx` |
| Premium gating exists | `forecast.py:31-44`, plan-tier logic in `auth.py` |
| Test coverage | 71 frontend + 121 backend tests green (2026-09-24 run) |
