# EcoSim "Sell Electricity" Module — Implementation Plan

Feature: let a household *sell* excess generation back to the grid as a first-class EcoSim capability (net-metering export), not just an incidental surplus line.

> **Status:** Research complete. Regulatory answers landed in `docs/ECOSIM_SELL_ELECTRICITY_RESEARCH.md` (authoritative). This document is the reconciled implementation plan: audit → research decisions → phased tasks.
> **Companion research:** `docs/ECOSIM_SELL_ELECTRICITY_RESEARCH.md` — statutory basis (RA 9513, ERC Res. 06-2019, Res. 15-2025, DOE DC2024-08-0025), DU rate tables, arbitrage math, schema proposals.

---

## 1. System Audit — What Already Exists

### Backend

| Area | Location | Status |
|---|---|---|
| Export model | `fastapi-backend/app/services/sizing.py` | Daytime self-use vs. surplus split → battery captures `SURPLUS_CAPTURE_FRACTION = 0.85` of surplus (charge-rate/intermittency cap) → residual exported at `DEFAULT_EXPORT_FRACTION = 0.55` of retail (BGC proxy). Export credit is now non-zero even with a battery — physically correct spillover. |
| Cash flows | `sizing.py::calculate_cashflows` | 25-yr horizon splits revenue into self-consumed @ retail + export @ export rate, 3%/yr escalation. Matches research §1.c perpetual-banking model (no annual forfeiture — correct per ERC Res. 15-2025). |
| Disclaimer + citation | `sizing.py` `NET_METERING_NOTICE`, `app/config/citations.py` | ERC net-metering + Meralco citations; notice appended when `monthly_exportable > 1.0`. |
| API schema | `app/schemas/ecosim.py::SizingBlock` | `monthly_exportable_kwh`, `export_rate_php`, `monthly_export_credit_php`, `total_monthly_benefit_php` returned. |
| Solar option financials | `app/services/ecosim.py` | Solar option's savings/cost/payback/NPV overridden by sizing-block values (export-aware). |
| RAG knowledge | `app/services/local_data/rag_*.json` | Net-metering/export chunks indexed for AI explanations. |

### Frontend

| Area | Location | Status |
|---|---|---|
| Export credit stat | `EcosimResults.jsx` | "Export Credit ₱/mo" sizing stat rendered — now non-zero with battery enabled. |
| Tooltips | `EcosimResults.jsx`, `EcosimBOM.jsx`, `glossary.js` | `HelpTooltip` glossary definitions on every sizing stat, the sizing title, BOM title/headers/rows/total. en+fil parity. |

## 2. Research Answers → Decisions

Each brief research question is resolved by `ECOSIM_SELL_ELECTRICITY_RESEARCH.md`; decisions below cite its section.

| Question | Finding | Decision |
|---|---|---|
| Credit formula | Net *billing*: export kWh × DU blended generation cost, deducted from subtotal import bill; credits roll over **perpetually** (Res. 15-2025), no cash payout (§1.a, §1.c) | Keep current monetary credit model — already matches. No forfeiture modeling needed. |
| Oversizing legal? | Yes if within 100 kW cap **and** service-entrance connected load (~13.8 kVA @ 60A/230V); DU can't reject incidental surplus (§1.b, §1.e) | Add `sizing_intent` (offset_bill / maximize_export) clamped to `min(100 kW, roof capacity, service entrance)`. |
| Non-bypassable floor | ~₱120/mo fixed customer charge always payable (§1.d) | Add `MIN_MONTHLY_BILL_FLOOR_PHP = 120` + UI copy noting grid connection fee remains. |
| 0.55 fraction defensible? | Yes — 52–62% band across Meralco/VECO/BENECO/ECs; scales with local retail (§2.a, §4.a) | Keep `DEFAULT_EXPORT_FRACTION = 0.55`; add optional `export_rate_override_php` input later. |
| Daytime fraction | 0.35 / 0.50 verified by peer-reviewed PH load studies (§4.b) | Keep. Relabel wizard occupancy options per research §4.b wording. |
| Battery vs export | Export wins financially (+₱6.60/kWh vs +₱6.30 net of wear); battery wins for resilience/high tariffs (§4.c) | Add `surplus_strategy` (export_to_grid / battery_storage) selector + UI note. |
| Oversize NPV? | Strongly positive — LCOE ₱4.32/kWh vs credit ₱6.60; break-even at 36% of retail; ~5.2-yr payback per incremental kWp (§4.d) | Surface "Annual export earnings" KPI + `oversizing_npv_positive`/`is_net_exporter` flags in schema. |
| Permits share | 8% BOM share already covers DIMC + ERC COC + LGU CFEI (§3.b) | Retain `permits_compliance = 0.08`; no double-charging. Optionally split 5%/3% in unbundled view. |
| FIT status | Closed to new entrants; NM is the only household export path (§2.b) | One-line UI note where export is explained (already in glossary `export_credit`/`net_metering`). |
| POP/TOU | Meralco POP can stack with NM — peak export ~₱8.50/kWh credit (§2.c) | Defer: `pricing_scheme: flat\|peak_off_peak` is a stretch item, not phase 1–3. |
| DER path >100 kW | 30% export cap + derated BGC; residential scope is <100 kW (§1.b) | Validation clamp + warning only; no DER commercial modeling. |

### Reconciliation note
Research §5.3 pseudocode still shows the pre-fix `usable_storage = min(daily_surplus, night_load)`. The shipped code now uses `min(daily_surplus * 0.85, night_load)` — when implementing `surplus_strategy`, the `battery_storage` branch must keep the `SURPLUS_CAPTURE_FRACTION` factor (uncaptured surplus still exports).

## 3. Phased Implementation Plan

Aligned with research §6; phases ordered by independence so each lands green.

### Phase 1 — Backend: caps, intents, schema ✅ done
- [x] `SURPLUS_CAPTURE_FRACTION` dispatch fix — export credit with battery (spec + tests updated).
- [x] Constants: `NET_METERING_MAX_KW = 100.0`, `MIN_MONTHLY_BILL_FLOOR_PHP = 120.0`, `SERVICE_ENTRANCE_KW_DEFAULT = 15.0`, `SERVICE_VOLTAGE_V = 230.0`, `SOLAR_ROOFTOP_LCOE_PHP_KWH = 4.32`.
- [x] Sizing inputs: `sizing_intent` (`offset_bill`|`maximize_export`), `service_entrance_amps`, `export_rate_override_php` — plumbed through `EcosimQueryParams`, `PostHouse`, GET + POST routes, `build_ecosim_dashboard_response`, `renewable_energy_calculator` (+ cache key), `_attach_sizing`.
- [x] `maximize_export`: sizes to `min(100 kW, roof_kwp, service_entrance_kwp)` with hosting-capacity disclaimer. Verified live: 27 panels / 14.85 kWp at the 15 kW default cap.
- [x] `surplus_strategy`: **folded into `include_battery`** — battery on = store strategy (85% capture, residual exports); battery off = export-all. No separate flag (avoids contradictory states).
- [x] Bill floor: `net_monthly_bill_remaining_php = max(120, bill − total_benefit)`.
- [x] Schema outputs: `annual_export_energy_kwh`, `annual_export_income_php`, `is_net_exporter`, `oversizing_npv_positive`, `regulatory_capacity_cap_kw`, `sizing_intent`.
- [x] Tests: `TestMaximizeExportIntent` (5 vectors) + override test — 27/27 green; live API verified (422 on bad `sizing_intent`).

### Phase 2 — Financials consistency
- [ ] `financials.py`/`ecosim.py`: split revenue streams (self-consumed @ retail + export @ BGC) so solar `irr`/`lcoe`/`bcr` stop assuming 100% retail.
- [ ] Wind/Hydro: credit surplus via same export path (research supports NM for all RE sources ≤100 kW) or explicitly scope solar-only with a code comment.
- [ ] Bump cache `scoring_version`.

### Phase 3 — Frontend wizard + results
- [ ] Wizard step: sizing intent ("Offset my bill" / "Maximize export earnings") + surplus strategy selector with the §4.c economics note ("exporting usually pays back faster; battery = backup power").
- [ ] `EcosimResults.jsx`: dedicated "Grid Sales (Net-Metering)" card — annual export earnings hero stat, net-exporter badge, strategy comparison pill (per research §5.4).
- [ ] Bill-floor line: "grid connection fee ~₱120/mo remains".
- [ ] `ecosimPdf.js`: export-credit + net-metering summary rows (PDF still omits export entirely).
- [ ] i18n en+fil keys for all new copy; glossary terms reused via `HelpTooltip`.

### Phase 4 — Reporting & AI (stretch)
- [ ] AI insight prompts mention export earnings explicitly.
- [ ] Optional: unbundled permit split (5% LGU + 3% NM interconnection) in BOM detail view.
- [ ] Optional: `pricing_scheme: peak_off_peak` POP modeling (Meralco-only).

## 4. Out of Scope (confirmed by research)

- FIT revenue — program closed to new entrants (§2.b).
- Cash-out/refund of credits — statutory no-cash-payout rule (§1.c).
- DER commercial modeling >100 kW — clamp + warn only (§1.b).
- Per-DU tariff registry — 0.55 heuristic verified; `export_rate_override` covers edge cases (§2.a, §4.a).

## 5. Original Agent Prompt (archived)

The Antigravity prompt that produced the research doc was the previous §4 of this file; its output is `docs/ECOSIM_SELL_ELECTRICITY_RESEARCH.md`.
