# 01 — Presentation Guide & Script (all slides)

> **How to use:** left column thinking — what's on the slide, what to say, when to move on.
> Scripts are ~conversational; deliver them in your own voice. Slide numbers follow deck order
> (title = S1).
>
> **Slide-count note:** `pdftotext` on `FINAL-DEFENSE-PPT.pdf` yields **29 text segments** —
> S1–S24 main presentation + 5 appendix pages (photo/tabulation pages). The convention "27
> slides" likely merges some appendix pages. All segments are covered below; adjust S# if your
> deck copy paginates differently.
>
> **Image-only content** (appendix photos, chart graphics) is marked `[USER INPUT NEEDED]` —
> fill in what the image actually shows; nothing is invented here.

**Total suggested timing: ~11–13 min core (S1–S22) + live demo (S23, 2–4 min).**

---

## S1 — Title

- **On slide:** Full title "LUMI: Data-Driven Environmental Intelligence System for Renewable
  Energy Decision Support"; team: Alexander Jon Solis (Developer), Lerrica Jeremy Torreno
  (Principal Researcher & Data Analyst), Sean Maverick Virata (Technical Writer).
- **Script:** "Good morning/afternoon. We present LUMI — a Data-Driven Environmental Intelligence
  System for Renewable Energy Decision Support. I'm [name], and this is our team."
- **Timing:** ~15 s. **Transition:** "Let me start with why this problem matters."
- **If asked:** who did what — developer ↔ system build; principal researcher ↔ data/study;
  technical writer ↔ manuscript. Know your own contribution cold.

## S2 — Background of the Study (Research Poster)

- **On slide:** Problems (rising electricity demand; households lack technical knowledge; data is
  scattered); related studies (Palanca-Tan 2024 — Metro Manila solar preference; Tarife 2023 —
  GIS + MCDM site suitability; Beriro 2022 — web-based weighted-criteria DSS); research gap —
  accessible, **location-specific, household-level** decision support.
- **Script:** "Three problems motivate LUMI: rising demand, households who can't interpret
  technical energy data, and data scattered across many sources. Prior work proved GIS-MCDM
  suitability assessment works — but it wasn't built for households. That gap is LUMI."
- **Timing:** ~45 s. **Transition:** "So we set a clear objective and a testable hypothesis."
- **If asked:** gap = *household* granularity + accessibility; prior work assessed sites for
  planners, not decisions for residents.

## S3 — General Objective & Hypotheses

- **On slide (verbatim):** GO — "develop a web-based decision support system that uses a weighted
  multi-criteria recommendation engine to identify suitable renewable energy options for
  households in Region IV-A (CALABARZON), with nationwide applicability at the province and
  municipality level." Null/Alternative hypotheses about *perceived support* vs prior methods.
- **Script:** "Our general objective: a web-based DSS using a weighted multi-criteria engine,
  evaluated with CALABARZON households but built for nationwide province-and-municipality
  coverage. The hypothesis is deliberately testable: does LUMI significantly improve *perceived*
  decision support versus people's prior methods?"
- **Timing:** ~40 s. **Transition:** "We decomposed that into eight specific objectives."
- **If asked:** note "perceived" — the hypothesis measures *perceived* support against a neutral
  3.00 benchmark, not engineering accuracy. Keep that distinction; the panel may probe it.
- **Watch:** say "households in CALABARZON, nationwide *applicability*" — never "nationally
  validated."

## S4 — Specific Objectives SO1–SO4 + Solutions

- **On slide:** SO1 interactive map interface → EnergyHub module (evidence: 4.50/5 IT rating);
  SO2 weighted MCDM engine (evidence: 82.22% agreement, 9 locations); SO3 predictive analytics →
  EnergyHub ARIMA(1,1,1) (MAE 6,829.09 GWh consumption / 1,019.66 MW peak); SO4 EcoSim what-if
  sim for solar/wind/hydro with geothermal as *reference only* (evidence: 4.40/5).
- **Script:** "SO1 is delivered by EnergyHub's interactive maps — rated 4.50/5 by IT experts.
  SO2 is our weighted MCDM engine, which agreed with engineering experts in 37 of 45 assessments
  across 9 locations. SO3 is ARIMA(1,1,1) forecasting — MAE of about 6.8 thousand GWh on national
  consumption and about 1,020 MW on peak demand. SO4 is EcoSim — household what-if simulation of
  solar, wind, and hydro, with geothermal shown as reference information."
- **Timing:** ~60 s. **Transition:** "…and the remaining four objectives."
- **If asked:** why two modules? EnergyHub = understand the data; EcoSim = simulate *your*
  household. National-vs-personal scale separation.

## S5 — Specific Objectives SO5–SO8 + Solutions

- **On slide:** SO5 user-friendly interface → dashboards + AI explanations (4.70/5 household
  clarity); SO6 system evaluation → 100 CALABARZON households (4.73 usability, 4.79 advantage);
  SO7 expert validation → barangay consultation + engineers + ISO 25010 by IT experts (4.47/5);
  SO8 performance testing → agreement rate, response time, MAE/RMSE (82.22%, ~104 ms,
  6,829.09/8,257.12 GWh).
- **Script:** "SO5–SO8 cover usability, evaluation, expert validation, and performance testing —
  the numbers you see here are the ones we'll unpack in results."
- **Timing:** ~35 s. **Transition:** "Before methodology — what the system does and does not
  claim."
- **If asked:** the SO-column is the defense checklist; every later claim maps back to an SO.
  Cross-reference: `02-PAPER-TO-CODE-AUDIT.md` Part A.0.

## S6 — Scope & Limitations

- **On slide:** Scope — nationwide province/municipality coverage; solar, wind, hydro +
  geothermal reference; integrated features; 100 households + 10 IT + 5 engineers. Limitations —
  CALABARZON sample (not nationally representative); **preliminary** assessments, not a
  substitute for engineering feasibility studies; data dependency; geothermal agreement not
  evaluated.
- **Script:** "Scope: nationwide data coverage, three recommended sources plus geothermal as
  reference. Limitations we state upfront: the household sample is CALABARZON only; outputs are
  preliminary decision support, not engineering feasibility studies; accuracy depends on source
  datasets; and geothermal agreement was not evaluated."
- **Timing:** ~40 s. **This slide is your shield** — deliver it confidently; pre-empting
  limitations reads as rigor.
- **If asked:** "Why not nationally representative?" → sampling was scoped to CALABARZON for the
  evaluation phase; nationwide applies to *data coverage*, not the respondent sample.

## S7 — Methodology

- **On slide:** Mixed-method developmental research; pipeline Needs Assessment → System
  Development → System Evaluation → Final Evaluation; evaluators 100 households + 10 IT + 5
  engineering experts; three instruments (household questionnaire; ISO/IEC 25010:2023 IT
  instrument; engineering instrument covering suitability, interaction, reliability, safety,
  agreement).
- **Script:** "Mixed-method developmental research: we built iteratively, then evaluated with
  three respondent groups and three matched instruments — households for usability and
  comparison, IT experts for ISO/IEC 25010 software quality, and licensed engineers for technical
  validation."
- **Timing:** ~40 s. **Transition:** "Here's what the analysis produced."
- **If asked:** needs-assessment phase earlier surveyed ~196 household decision-makers (paper) —
  don't confuse that N with the final 100.

## S8 — Data Analysis: Evaluation Results

- **On slide:** Household usability **4.73** (Strongly Agree), comparison **4.79**; IT experts
  **4.47 Excellent**; engineering **3.27 Satisfactory**; Cronbach's α **0.923** usability /
  **0.868** comparison; **t(99)=55.47, p<.001** → reject null; ratings vs neutral benchmark 3.00.
- **Script:** "Usability averaged 4.73 and comparison with prior methods 4.79 — both Strongly
  Agree. Reliability is strong: α of 0.923 and 0.868. A one-sample t-test against the neutral
  benchmark of 3.00 gives t(99) = 55.47, p < .001 — we reject the null. IT experts rated the
  software 4.47, Excellent. Engineering's technical assessment was 3.27 — Satisfactory, and we
  report that honestly."
- **Timing:** ~55 s.
- **If asked:** (a) benchmark = neutral 3.00 midpoint, *not* a competing system — say exactly
  that. (b) Why is engineering only 3.27? → their rubric is stricter (suitability, safety,
  reliability); it drove the improvements in Recommendations (S21/22). (c) The appendix reports
  4.46 vs the deck's 4.47 — rounding-level discrepancy, already flagged in our prep notes;
  if pressed: "4.47 in the summary, 4.46 in the tabulated appendix — presentation-level rounding,
  same Excellent band."
- **Watch:** say "significantly above neutral benchmark," not "better than every alternative."

## S9 — Recommendation Validation

- **On slide:** **82.22%** — 37 of 45 assessments matched; Solar & Wind 85%; Hydropower 60%;
  Geothermal N/A.
- **Script:** "The MCDM engine's outputs were compared with engineering experts' own assessments:
  37 of 45 matched — 82.22% — across 9 locations. By source: solar and wind 85%, hydropower 60%,
  geothermal not evaluated."
- **Timing:** ~35 s. **Transition:** "Let me show how the system is actually built."
- **If asked:** **82.22% is agreement rate, not accuracy** — say "agreement with expert
  assessment," never "82% accurate." Hydro's 60% motivated the refinement recommendation.
  "Of 45" = 5 engineers × 9 locations.

## S10 — System Architecture

- **On slide (diagram):** Input: DOE data, climate data, terrain/GIS data, location data, user
  input → Process: ARIMA model, RAG, renewable-energy formulas, suitability scoring → Output:
  suitability recommendations, LLM summary → UI: EcoSim, EnergyHub. Database + External APIs feed
  the process.
- **Script:** "One data spine feeds everything: DOE statistics, climate, terrain/GIS, and
  location data — ingested offline into our database — plus user input at runtime. Processing
  combines four engines: ARIMA forecasting, RAG-grounded LLM explanations, the renewable-energy
  output formulas, and weighted suitability scoring. Outputs surface through two modules —
  EnergyHub and EcoSim."
- **Timing:** ~45 s.
- **If asked (likely technical):** stack = FastAPI + React/Vite + Supabase Postgres with RLS +
  Redis caching; deployed serverless on Vercel. External APIs/data are fetched **offline in ETL**,
  not at request time — that's how the API averages ~104 ms. Full detail: `03-SYSTEM-DESIGN-AUDIT.md` §1–4.

## S11 — Functional Requirements: EnergyHub I

- **On slide:** National Overview & Provincial Demand — national electricity statistics,
  provincial demand, renewable-energy benchmarks. `[USER INPUT NEEDED: describe the
  screenshot/chart on this slide]`
- **Script:** "EnergyHub answers 'what does the national picture look like?' — consumption,
  generation mix, provincial demand, and benchmarks."
- **Timing:** ~20 s.

## S12 — Functional Requirements: EnergyHub II

- **On slide:** Renewable Potential & Forecasting — interactive potential maps; historical +
  forecasted national trends. `[USER INPUT NEEDED: which map/forecast is shown]`
- **Script:** "Second half: interactive renewable-potential maps down to municipality level, plus
  historical and ARIMA-forecasted national trends."
- **Timing:** ~20 s.

## S13 — Functional Requirements: EcoSim I

- **On slide:** Location-based recommendations, suitability comparisons, estimated generation.
- **Script:** "EcoSim is the personal layer: pick a location, enter your consumption, get ranked
  renewable options with suitability scores and estimated generation."
- **Timing:** ~20 s.

## S14 — Functional Requirements: EcoSim II

- **On slide:** AI-generated explanations + directory of renewable-energy providers/retailers.
- **Script:** "Every result can be explained by the AI assistant in plain language, and the
  provider directory — built from the 2026 DOE registry — connects users to real installers."
- **Timing:** ~20 s.
- **If asked:** providers = 32 verified entries (`data/providers.json`); matching is
  provider-agnostic by design (git `896843d`).

## S15 — Functional Requirements: EcoSim III

- **On slide:** Recommended Next Steps — suggested actions incl. expert consultation and local
  requirements.
- **Script:** "We deliberately end with next steps — including 'consult a licensed engineer' —
  because the system is decision *support*, not a feasibility study."
- **Timing:** ~20 s. This closing point reinforces the limitation story — land it.

## S16 — Functional Requirements: User Authentication

- **On slide:** secure registration, sign-in, **Google** authentication, 2FA.
- **Script:** "Accounts support email-password, Google sign-in, and TOTP two-factor
  authentication — Supabase-auth backed, with row-level security on user data."
- **Timing:** ~20 s.
- **If asked:** say Google + email + TOTP 2FA only — GitHub OAuth appears in an old test doc but
  is **UNVERIFIED** in code; don't claim it.

## S17 — Functional Requirements: Saved Simulations

- **On slide:** save, revisit, delete previous EcoSim analyses.
- **Script:** "Authenticated users can save simulations — by default every run auto-saves under a
  preference they control — and revisit or delete them."
- **Timing:** ~20 s.
- **If asked:** autosave default-on came from IT-expert feedback (migration 0023 + profiles
  toggle in SecuritySettings).

## S18 — Results & Discussion: ML/AI Models

- **On slide:** ARIMA(1,1,1): **5.67%** held-out MAPE, MAE 6,829.09 GWh, RMSE 8,257.12 GWh.
  Generative AI: **~7.1 s** live model-call average; Groq/Gemini-supported; **~1.9 s** fallback
  path. MCDM: 82.22% agreement (37/45, 9 locations).
- **Script:** "Three engines, three numbers. ARIMA(1,1,1) held-out MAPE of 5.67% on national
  consumption — MAE 6,829 GWh, RMSE 8,257 GWh. Live generative-AI calls average about 7.1
  seconds; the cached/provider-fallback path is about 1.9 seconds. And the MCDM engine — 82.22%
  expert agreement."
- **Timing:** ~45 s.
- **If asked:** (a) **keep latencies separate** — 104 ms is local API, 7.1 s is live LLM, 1.9 s
  is fallback; panels love this trap. (b) MAE in GWh sounds huge → it's national-scale demand
  (~80,000+ GWh baseline); that's why MAPE 5.67% is the interpretable metric. (c) Model chosen by
  AIC grid search + pilot comparison vs Linear/Holt/RandomForest (`ml/aic_grid.csv`,
  `tests/pilot_run/evaluate_models.py`).

## S19 — Results & Discussion: System Testing

- **On slide:** **315** passed unit+backend+frontend+integration tests (+2 integration skipped);
  **82/82** endpoint checks in live sweep; **~104 ms** average local API response, no failures at
  tested 100-user load; **16/18** security probes passed + 1 warning/info findings.
- **Script:** "Testing covered four layers: 315 automated tests passing — with two
  environment-dependent integration tests skipped; a scripted live sweep validating all 82
  endpoints; performance averaging about 104 milliseconds locally with no failures at the tested
  100-user load; and 16 of 18 security probes passing, with the residual findings documented —
  not hidden."
- **Timing:** ~40 s.
- **If asked:** suite breakdown + drift reconciliation = `04-TESTING-AUDIT.md` (unit 177 /
  backend 121-collected / frontend vitest / integration subsets; the "315" is the documented
  defense-time aggregate). Security residuals: XFF edge case + dependency warnings — say
  "documented with mitigations," never "fully secure."

## S20 — ISO/IEC 25010 Evaluation Results

- **On slide:** Compatibility highest (**4.65**), Flexibility lowest (**4.20**). `[USER INPUT
  NEEDED: if the slide shows the full characteristic bar chart, note each score]`
- **Script:** "Across ISO 25010 characteristics, Compatibility scored highest at 4.65;
  Flexibility lowest at 4.20 — which directly motivated the recommendation to broaden datasets
  and scenario coverage."
- **Timing:** ~25 s.
- **If asked:** overall software quality = 4.47 Excellent (S8); the appendix tabulation reports
  4.46 — same Excellent band, rounding-level difference.

## S21 — Conclusion & Recommendations

- **On slide:** Conclusion — successful development; positive evaluation (households favorable,
  IT Excellent); 82.22% agreement supports potential **but further engineering validation
  remains necessary**. Recommendations — refine MCDM criteria (esp. hydropower, low-agreement
  locations); expand datasets/forecasting/hardware sizing/advanced simulations; expand validation
  across more Philippine locations.
- **Script:** "We conclude LUMI successfully integrates recommendation, forecasting, and
  simulation into one platform households actually rated highly — while being explicit that
  82.22% agreement supports potential, not production-readiness. Our own recommendations: refine
  the MCDM criteria — hydropower especially — expand datasets and simulations, and validate in
  more locations."
- **Timing:** ~45 s. **Transition:** "We also sketched a responsible path to monetization."

## S22 — Business Monetization & Commercialization Plan

- **On slide:** Freemium model (free basic assessments + AdSense; premium subscriptions);
  provider partnerships; 3-phase plan (validation → launch w/ Metro Manila priority →
  MSME/institutional/government expansion). **Slide itself notes: proposed strategies; revenue
  and willingness-to-pay NOT yet validated.**
- **Script:** "A freemium model is proposed — free assessments, premium simulations, provider
  partnerships — phased validation, launch, expansion. Important caveat, printed on the slide:
  these are proposals; willingness to pay and commercial feasibility are not yet validated."
- **Timing:** ~25 s.
- **If asked:** never claim commercial viability — the deck itself disclaims it. Repeat that.

## S23 — System Demonstration

- **On slide:** "SYSTEM DEMONSTRATION" (live demo segue).
- **Script:** "Let me show you the system itself."
- **Choreography (practice this):** open `lumi-frontend-xi.vercel.app` →
  1. Dashboard: searchable municipality picker → composite score card;
  2. EnergyHub: national overview → renewable potential map → forecast chart → AI insight;
  3. EcoSim: 5-step wizard (location → consumption → options) → results cards → per-source
     explanation modal → provider matches → PDF export;
  4. (If time) Login + saved simulations.
- **Backup plan (if live demo fails):** narrate the evidence screenshots in order —
  `docs/09-Technical-Evaluation/artifacts/screenshots/` **B-01 … B-17** (verify which artifact
  shows which screen beforehand and list here):
  - B-01__… `[USER INPUT NEEDED: caption each screenshot]`
- **If asked mid-demo:** latency expectations — local API ~104 ms; AI explanations are the slow
  call (~7 s live) by design, with cached/fallback path ~2 s. Say it before they notice.

## S24 — Thank You

- **On slide:** "CLEANER ENERGY, BRIGHTER TOMORROW — THANK YOU".
- **Script:** "That's LUMI — cleaner energy, brighter tomorrow. We're happy to take questions."
- **Timing:** ~10 s. Then move into Q&A mode — `05-DEFENSE-KNOWLEDGE-BASE.md` is the Q&A bank.

## S25 — Appendix: Interview / Data Gathering

- **On slide:** "APPENDIX — INTERVIEW / DATA GATHERING" — photo page. `[USER INPUT NEEDED: who is
  shown, which consultation — barangay officials / engineering experts]`
- **Use:** only if asked for evidence of field work — "we consulted barangay officials and
  licensed engineers; these are the sessions."
- **Backup reference:** appendix transcripts in thesis (@3121–3488).

## S26 — Appendix: Demonstration During Evaluation

- **On slide:** evaluation-session photos. `[USER INPUT NEEDED: setting, who's testing]`
- **Use:** if asked how household evaluation was administered — "respondents used the live
  system during supervised sessions."

## S27 — Appendix: UAT Results

- **On slide:** "UAT RESULTS". `[USER INPUT NEEDED: what the tabulation shows — scores per
  criterion?]`
- **Use:** support for S8 numbers — "item-level ratings behind the 4.73/4.79 means."

## S28 — Appendix: IT Expert Testing & Results

- **On slide:** expert testing evidence. `[USER INPUT NEEDED: which screens/results shown]`
- **Use:** backup for the 4.47 ISO 25010 claim — "the characteristic-level scores behind the
  4.47 average."

## S29 — Appendix: Questionnaire Tabulation

- **On slide:** questionnaire tabulation tables. `[USER INPUT NEEDED: which instrument's
  tabulation is shown]`
- **Use:** deepest-level backup — "the raw item-by-item tabulation," incl. the 4.46/4.47
  discrepancy if a panel member spotted it (answer in S8's if-asked).

---

### Quick-reference cheat card

| Figure | Say it as | Never as |
|---|---|---|
| 82.22% (37/45) | "agreement with engineering experts" | "accuracy" |
| 4.73 / 4.79 | "usability / perceived-advantage means" | "satisfaction %" |
| t(99)=55.47 | "vs neutral benchmark 3.00" | "vs competing systems" |
| ~104 ms / ~7.1 s / ~1.9 s | local API / live LLM / fallback | conflated |
| 3.27 | "Satisfactory — and we report it" | "excellent" |
| 60% hydro | "weaker agreement — motivates refinement" | hidden |
| Geothermal | "reference information only" | validated/recommended |
| Nationwide | "data coverage" | "nationally validated sample" |
| 315 tests | "documented defense-time aggregate" | exact current count (see 04) |
| 16/18 + warning | "probes passed, residuals documented" | "fully secure" |
| Monetization | "proposed, unvalidated" | "business model proven" |
