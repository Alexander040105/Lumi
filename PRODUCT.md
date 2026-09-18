# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

**Primary: Filipino homeowners** — non-technical household users who want to know whether solar, wind, or micro-hydro makes sense for their home and municipality. Their job: compare renewable options, understand estimated cost, payback period, monthly savings, and CO₂ reduction in plain language before committing money.

**Secondary (confirmed):** energy planners, policymakers, and researchers using EnergyHub's national statistics, ARIMA forecasts, and province-level choropleth maps for analysis and planning contexts.

**Account tiers (implemented):** free users (basic simulations, up to 3 saved scenarios), premium users (unlimited simulations, advanced AI insights, priority RAG), admins (user management, audit logging, system configuration). Roles `admin` and `dev` gate admin surfaces.

## Product Purpose

LUMI is an environmental intelligence system for the Philippines that turns technical climate and energy data into decisions ordinary people can act on. It combines:

- **EcoSim** — household-level renewable energy simulator: municipality lookup across 1,600+ Philippine municipalities, solar/wind/micro-hydro output estimation, economic analysis (installation cost, payback, monthly savings, CO₂ reduction), bill of materials, and AI-powered recommendations.
- **EnergyHub** — national energy analytics: Philippine DOE statistics (2003–2024), ARIMA-based 2025–2030 demand forecasts with confidence intervals, generation-mix breakdowns, grid-level (Luzon/Visayas/Mindanao) analysis, and interactive province-level choropleth maps.
- **LUMI AI Assistant** — Gemini-powered analysis and natural-language recommendations, optionally RAG-backed by a vector store of scraped e-commerce equipment pricing.

Success means a homeowner can land on the site, pick their municipality, and leave understanding which renewable option fits their area and budget — without needing engineering literacy.

## Positioning

Municipality-level specificity for the Philippines that generic energy tools cannot truthfully copy: LUMI fuses NASA POWER municipal climate data, DOE national statistics, Global Solar/Wind Atlas rasters, ERA5 reanalysis, and SRTM/HydroSHEDS terrain into per-municipality assessments, then grounds its AI cost estimates in real scraped Philippine e-commerce equipment pricing rather than generic figures.

## Operating Context

- Deployed on Vercel (frontend + FastAPI serverless function via `api/index.py`); expert-tested by IT and Engineering reviewers and entering real-user testing after revisions. Treat it as production-facing: claims and polish expectations apply.
- Supabase Auth (email/password + Google OAuth, MFA supported); JWT-protected FastAPI routes; Postgres RLS; Upstash Redis session caching.
- Simulations can be saved to an account and exported as PDF reports (pdfmake).
- The UI is bilingual: English (`en.json`) and Filipino (`fil.json`) via the i18n layer.
- Voice is deliberately plain and hedged ("estimated costs", "options may work in your area") — estimates, not promises. This honesty is a product commitment.

## Capabilities and Constraints

- **Stack:** React 18 + Vite + Tailwind CSS v4 + shadcn/ui (Radix primitives) frontend; FastAPI + Supabase + Redis backend; Leaflet maps; Plotly and Recharts visualizations; pdfmake exports.
- **Data sources:** NASA POWER (municipal climate), DOE Philippines (national statistics), Global Solar Atlas 2.0 and Global Wind Atlas (CC BY 4.0 — attribution required), ERA5 (Copernicus/ECMWF), USGS SRTM/HydroSHEDS (terrain), scraped e-commerce pricing (RAG knowledge base).
- **Forecasting:** pre-trained ARIMA(1,1,1) served from CSV artifacts — no runtime model training; interpretability was chosen over marginal accuracy gains.
- **Honesty constraint:** simulation outputs are estimates with stated assumptions; the product must not present them as guarantees.
- `expo-mobile/` is an abandoned scaffold (node_modules only) — not a shipping surface; platform remains web.

## Brand Commitments

- **Name:** LUMI — "Environmental Intelligence for the Philippines."
- **Logo:** `react-frontend/public/lumi-logo.png` (favicon/brand mark).
- **Binding visual identity:** the green environmental palette and gold solar accent are user-confirmed as fixed; future design work must preserve them.
- **Voice:** plain-language bridge between technical climate data and public understanding; hedged, honest, never salesy.

## Evidence on Hand

- Real datasets and pipelines under `data/` (DOE extracts, geothermal shapefiles, PH GeoJSON, SRTM raster, scraped pricing).
- Extensive internal documentation under `docs/` (architecture, module specs, ML methodology, evaluation/audit reports).
- Expert review completed (IT and Engineering testers); real-user testing upcoming.
- **Absence to respect:** no public testimonials, case studies, press, or production user metrics exist — future surfaces must not fabricate them.

## Product Principles

1. **Non-technical first.** Every surface must be legible to a homeowner, not just an engineer; technical depth is available but never required.
2. **Estimates, not promises.** Costs, outputs, and forecasts are always presented with their assumptions and uncertainty; precision theater is a violation.
3. **Locality is the value.** Design and copy emphasize the user's specific municipality and grid context over national averages.
4. **Accessibility is a gate, not a polish.** WCAG AA contrast/focus/keyboard support and en/fil parity ship with features, not after.
5. **Green identity is load-bearing.** The environmental palette signals trust and domain; it is preserved, not restyled.

## Accessibility & Inclusion

- **Required standard:** WCAG AA — contrast ratios, visible focus, keyboard operability are hard requirements for UI work.
- **Localization:** full English + Filipino strings ship together; new copy must land in both `en.json` and `fil.json`.
- **Audience consideration:** primary users may be on modest hardware and Philippine mobile connections — keep surfaces light and forgiving.
