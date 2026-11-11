# Megaplan: Thesis Table 3.47 Corrections (reviewer-flagged)

You are producing **targeted revisions to `1-4-CCS_LUMI_Thesis.docx`** — the LUMI thesis manuscript
("LUMI: Data-Driven Environmental Intelligence System for Renewable Energy Decision Support",
University of Perpetual Help System DALTA – Molino, November 2026).

A reviewer flagged **three "High" priority claims** in **§3.9.22 — Table 3.47: LUMI Forecasting
Error and Response Time Metrics (p. 202–203)** that contradict the thesis's own verified results
in §3.3.13. This document specifies, for each flag, **where** the claim lives, **why** it is
wrong, **what** to change, and the **done-when** check. It is a location + fix-description spec —
wording decisions belong to the editor.

---

## 1. Ground rules

1. **Edit the `.docx`, not the conversion.** `D:\63947\Downloads\1-4-CCS_LUMI_Thesis.docx.md` is a
   reference export used for line anchoring below; the Word file is the source of truth.
2. **Numbers are verbatim.** Every figure in §3 below was verified against the thesis's own
   tables and text (conversion line numbers cited as `docx.md:L#`). Never round or "improve" a
   number.
3. **Truth already exists in the thesis.** §3.3.13 (ML evaluation, Tables 3.16–3.24) and
   §3.3.13.17 already state the corrected findings — Table 3.47's summary framing is the stale
   copy. The fix propagates §3.3.13's honesty into §3.9.22; it does not invent new claims.
4. **Scope is the three flags only.** Do not restyle the table, renumber figures, or touch
   unrelated sections. See §7 for observed-but-out-of-scope notes.
5. **Preserve table style.** Match the manuscript's existing tone for Result and Interpretation
   cells (APA-ish reporting register).

---

## 2. The three flags (verbatim from the review table)

| # | Priority | Location | Reviewer comment |
|---|---|---|---|
| F1 | High | Table 3.47, p. 202 | "The paper still claims ARIMA performed comparably to or better than all five models. However, Linear Trend achieved 4.965% MAPE, compared with ARIMA's 5.667%. ARIMA was competitive, but not the best in that comparison." |
| F2 | High | Table 3.47, p. 202 | "The RMSE explanation still says all values were 20–30% higher than MAE. The actual differences are 20.91%, 27.40%, and 9.52%, respectively." |
| F3 | High | Table 3.47, p. 202 | "The performance interpretation says all response times were below their limits, but live AI calls averaged 7.1 seconds, exceeding the stated 5-second AI target. The local API and live AI measurements should be distinguished." |

---

## 3. Verified truth-table (source for all fixes)

All values verified against the thesis conversion; use exactly these.

| Fact | Value | Thesis source |
|---|---|---|
| Linear Trend held-out MAPE (consumption) | **4.965%** — rank 1 of 6 | Table 3.18 Model Testing Results (p.147, `docx.md:L1994`); rank table §3.3.13.8 (p.150, `L2050`) |
| ARIMA(1,1,1) held-out MAPE (consumption) | **5.667%** — rank 4 of 6 | Table 3.18 (`L1997`); §3.3.13.8 (`L2053`); §3.3.13.17 (`L2155`) |
| Peak-demand winner | **SARIMAX 3.868%** vs ARIMA 5.611% | §3.3.13.8 narrative (`L2014`) |
| RE-generation winner | **Linear Trend & Holt 9.405%** vs ARIMA 13.665% | §3.3.13.8 narrative (`L2014`) |
| ARIMA direction-of-change | 8/11 years (72.7%) — best of all models | §3.3.13.8 (`L2014`) |
| RMSE−MAE gap, computed | consumption **20.91%** (8,257.12/6,829.09); peak **27.40%** (1,299.08/1,019.66); RE gen **9.52%** (3,939.69/3,597.39) | computed from Table 3.47's own figures (`L2671–2672`) — matches reviewer |
| Live LLM-call latency | mean **~7.1 s** (typical 5–7 s, max 18.5 s) | §3.3.13 intro (`L1898`), §3.3.13.17 (`L2157`) |
| AI fallback-path latency | **~1.9 s** | same as above |
| Local API benchmark | ~104 ms avg / ~49 ms standard endpoints / ~612 ms heaviest flow — **21 endpoints, no live LLM call** | Table 3.47 ART row (`L2673`) |
| Thesis's own verdict on the model | "a reasonable choice… **not the most accurate model**" | §3.3.13.17 (`L2155`) |

---

## 4. FIX-1 — MAE row: superiority claim is false

- **Where:** Table 3.47, **MAE row, Result cell** — the closing em-dash clause
  *"…— comparable to or better than all five baseline models in the same evaluation run."*
  (`docx.md:L2671`)
- **Why it's wrong:** contradicted by the thesis's own benchmark. On national consumption, Linear
  Trend scored 4.965% MAPE vs ARIMA's 5.667% (ARIMA ranked **4th of 6**). On peak demand SARIMAX
  won (3.868% vs 5.611%); on renewable generation the linear-trend and Holt models won (9.405% vs
  13.665%). ARIMA led only on direction-of-change accuracy (72.7%). The clause as written is
  false on every target.
- **What to change:** remove the superiority clause and reframe honestly — e.g., describe ARIMA
  as *competitive*: within ~1 percentage point of the best model on the headline consumption
  target, outperformed by task-specific baselines on the other two targets, and the only model
  providing prediction intervals / best direction-of-change. Anchor the framing to §3.3.13.17's
  verdict ("a reasonable choice for the system, but it is not the most accurate model") so the
  summary table agrees with the deep-dive.
- **Leave as-is:** the MAE Interpretation cell's claim of "single-digit percentage error against
  both of the headline targets" is accurate (5.667% consumption, 5.611% peak — RE generation is
  separately disclosed at ≈13.7% in the Result cell).
- **Done when:** Table 3.47 contains no "better than"/"all five" superiority language, and its
  characterization of ARIMA matches §3.3.13.17.

## 5. FIX-2 — RMSE row: "20–30% higher than MAE" is wrong

- **Where:** Table 3.47, **RMSE row, Result cell** — *"…each roughly 20–30% higher than its
  corresponding MAE, indicating errors were concentrated in a single year rather than spread
  evenly."* (`docx.md:L2672`)
- **Why it's wrong:** the actual RMSE−MAE ratios, computed from the same row's own figures, are
  **20.91%** (consumption), **27.40%** (peak demand), and **9.52%** (renewable generation) — the
  third is far outside the claimed 20–30% band.
- **What to change:** state the true figures — either list all three ratios or give a truthful
  range ("roughly 10–27% higher"). Then qualify the inference: a large RMSE−MAE gap signals that
  a few large errors dominate — consistent with the 2024 demand-surge under-forecast already
  explained in the Interpretation cell — but the small 9.52% gap on renewable generation cannot
  support "errors concentrated in a single year" for that target. Scope the inference to the
  targets where it holds, or drop it.
- **Leave as-is:** the Interpretation cell's 2024-surge / shared-under-forecast explanation is
  accurate and corroborated by §3.3.13.11 — keep it.
- **Done when:** the stated RMSE−MAE relationship matches the three computed ratios, and the
  error-concentration inference is scoped accordingly.

## 6. FIX-3 — ART row: local-API and live-AI latencies are conflated

- **Where:** Table 3.47, **ART row, Interpretation cell** — *"The levels of response time remain
  well under the predetermined limits—API below 2,000 ms, AI below 5,000 ms, and web page loads
  below 3,000 ms—entitling the system to an Excellent rating… the slowest response recorded is
  about eight times below its limit…"* (`docx.md:L2673`)
- **Why it's wrong:** the ART row's Result cell measures only the **local API benchmark** — 21
  endpoints, ~104 ms average, ~612 ms heaviest flow — which includes **no live LLM call**. The
  thesis itself records live AI calls at **~7.1 s mean** (up to 18.5 s), which *exceeds* the
  stated 5,000 ms AI limit; only the **~1.9 s fallback path** complies (§3.3.13 intro `L1898`;
  §3.3.13.17 `L2157`). As written, the interpretation asserts an "all below limits" outcome the
  measurements do not support — exactly the conflation the reviewer flagged.
- **What to change:**
  1. Scope the "below limits" claim to what was measured — the local API benchmark (and note the
     two auth-gated endpoints, already disclosed).
  2. Identify the ~612 ms "full EcoSim simulation with AI recommendation" flow for what it is —
     the served/cached path — and state live-LLM latency separately (~7.1 s mean, fallback ~1.9 s)
     with its mitigation (progress indicators, graceful timeout/fallback per §3.3.13.17).
  3. Remove or qualify *"entitling the system to an Excellent rating"* and *"eight times below
     its limit"* — both rest on treating every latency class as passing the AI limit.
  4. Editorial note: the 2,000/5,000/3,000 ms limits are asserted only in this cell — either cite
     where the acceptance criteria are defined in the methodology chapter or soften
     "predetermined". *(Context for the rewrite, not a separate fix item.)*
- **Done when:** the interpretation distinguishes local-API vs live-AI measurements, no longer
  asserts that all response times met the AI limit, and the ~7.1 s / ~1.9 s split appears
  wherever AI latency is summarized in the table.

---

## 7. Ripple-checks (same table, same page — do these while editing)

- **Narrative paragraph under Table 3.47** (`docx.md:L2678`): *"…produced levels of prediction
  error, across national electricity consumption peak demand and renewable‑energy generation…"*
  — vague/incomplete phrasing. Update so its summary matches the corrected rows (competitive,
  not best-in-class; response times split by measurement class).
- **§4.1.4 System Performance** (`docx.md:L2704–2706`): reports raw MAE/RMSE numbers and ~104 ms
  only — makes **no** overclaim, so no edit is strictly required. Verify it stays consistent
  after the table fix; optionally add the live-AI distinction for coherence with FIX-3.
- **TOC entry** (`docx.md:L280` lists Table 3.47 at p.203; reviewer cites p.202): cosmetic —
  confirm after the .docx repaginates.

## 8. Acceptance criteria

- [ ] No "comparable to or better than all five" (or equivalent) language remains in Table 3.47;
      ARIMA is described as competitive and consistent with §3.3.13.17's "not the most accurate
      model" verdict. *(F1)*
- [ ] The RMSE row states the true RMSE−MAE relationship (20.91% / 27.40% / 9.52% or a truthful
      10–27% range) and the single-year inference is scoped to the targets it supports. *(F2)*
- [ ] The ART interpretation scopes "below limits" to the measured local-API benchmark, reports
      live-AI (~7.1 s) vs fallback (~1.9 s) separately, and removes the all-below-limits /
      "eight times" / "entitling…Excellent" assertions. *(F3)*
- [ ] The narrative paragraph under the table and §4.1.4 are consistent with the corrected rows.

## 9. Out of scope (observed, not actioned — per review scope)

- **§3.3.13.14 duplicated block** (`docx.md:L2123–2129`): the entire "Comparison with Previous
  Studies" passage (three paragraphs + closing) is pasted a second time, concatenated
  mid-sentence after "…comparison file." — a copy-paste defect worth fixing in a separate pass.
- **Undefined limits:** the 2,000/5,000/3,000 ms "predetermined limits" are never defined in the
  methodology chapter — flagged inside FIX-3 as context only.
- Anything outside Table 3.47 / its narrative paragraph.

---

*Source anchors: thesis conversion `D:\63947\Downloads\1-4-CCS_LUMI_Thesis.docx.md`; corrected
numbers verified against §3.3.13 Tables 3.16–3.24 and §3.3.13.17 of the same document.*
