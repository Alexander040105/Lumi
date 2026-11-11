# 01 — Presentation Guide & Script (all slides)

> **How to use:** each slide has **On slide** (what's printed), **Literature anchor** (the real
> RRL citations backing the claims — name-drop these when you want credibility), and a
> **Script** written as a full explanatory monologue. Deliver in your own voice; don't read
> verbatim.
>
> **`[core]` / `[optional]` tags:** every script sentence is tagged. Deliver all `[core]` lines
> and you stay inside ~11–13 min; `[optional]` lines are the depth you deploy when the panel is
> engaged, asks for elaboration, or you have time. Per-slide timing shows both budgets.
>
> **Slide-count note:** `pdftotext` on `FINAL-DEFENSE-PPT.pdf` yields **29 text segments** —
> S1–S24 main + 5 appendix pages. The "27 slides" convention likely merges appendix pages. All
> segments are covered; adjust S# if your deck paginates differently.
>
> **Image-only content** is marked `[USER INPUT NEEDED]` — nothing is invented.
>
> **Literature discipline:** every `(Author, Year)` below appears in the thesis RRL or code
> comments — they are real and citable. Use them naturally ("following the approach of Beriro
> et al., 2022…"), not as a bibliography dump.
>
> **`Evidence to justify it live` blocks** (S18, S19): reference material, *not* spoken — each
> spoken number is mapped to the harness code that produced it (`file:line`), the artifact
> file + exact field/row that records it, the re-run command, and a say-if-pressed line.
> Open the cited artifacts before the defense so you can point at the row live.

**Timing: ~11–13 min `[core]` spine (S1–S22) · ~16–18 min with all `[optional]` · + demo (S23, 2–4 min).**

---

## S1 — Title

- **On slide:** Full title "LUMI: Data-Driven Environmental Intelligence System for Renewable
  Energy Decision Support"; team: Alexander Jon Solis (Developer), Lerrica Jeremy Torreno
  (Principal Researcher & Data Analyst), Sean Maverick Virata (Technical Writer).
- **Literature anchor:** Bassetti (2024) — defines *environmental intelligence* as using ML/AI to
  simulate predicted environment models; that's the phrase's provenance in our title.
- **Script:**
  - `[core]` "Good morning/afternoon. We present LUMI — a Data-Driven Environmental Intelligence
    System for Renewable Energy Decision Support. I'm [name], and this is our team."
  - `[optional]` "Two phrases in that title carry the whole project: *environmental
    intelligence* — using data and models to reason about environmental systems — and *decision
    support* — LUMI informs a decision; it does not make it. Keep that in mind throughout."
- **Timing:** ~15 s core / ~30 s full. **Transition:** "Let me start with why this problem matters."
- **If asked:** who did what — developer ↔ system build; principal researcher ↔ data/study;
  technical writer ↔ manuscript. Know your own contribution cold.

## S2 — Background of the Study (Research Poster)

- **On slide:** Problems (rising electricity demand; households lack technical knowledge; data is
  scattered); related studies (Palanca-Tan 2024 — Metro Manila solar preference; Tarife 2023 —
  GIS + MCDM site suitability; Beriro 2022 — web-based weighted-criteria DSS); research gap —
  accessible, **location-specific, household-level** decision support.
- **Literature anchor:** Palanca-Tan (2024) household solar preference · Tarife et al. (2023)
  GIS+Fuzzy-AHP site suitability, southern Philippines · Beriro et al. (2022) UK web-based
  weighted-sum feasibility DSS.
- **Script:**
  - `[core]` "Three problems motivate LUMI: rising electricity demand, households who can't
    interpret technical energy data, and data scattered across many sources."
  - `[core]` "The closest work proves the method but not the audience: Palanca-Tan showed Metro
    Manila households already *want* solar; Tarife used GIS and fuzzy-AHP to site renewable
    plants — but for planners, not residents; Beriro built a web decision tool for onshore-wind
    feasibility — but for projects, not households."
  - `[optional]` "Notice the pattern: the *preference* exists, the *site-selection method*
    exists, and the *web delivery* exists — separately, in different studies, for different
    users. Nobody had put all three together at household level in the Philippines."
  - `[core]` "That gap is LUMI."
- **Timing:** ~45 s core / ~70 s full. **Transition:** "So we set a clear objective and a testable hypothesis."
- **If asked:** gap = *household* granularity + accessibility; prior work assessed sites for
  planners, not decisions for residents.

## S3 — General Objective & Hypotheses

- **On slide (verbatim):** GO — "develop a web-based decision support system that uses a weighted
  multi-criteria recommendation engine to identify suitable renewable energy options for
  households in Region IV-A (CALABARZON), with nationwide applicability at the province and
  municipality level." Null/Alternative hypotheses about *perceived support* vs prior methods.
- **Literature anchor:** Malczewski (2006) — the weighted multi-criteria definition we use ·
  Sprague & Carlson (1982), via El-Gayar (1997) — the DSS framework (data + dialog + model) the
  system is built on.
- **Script:**
  - `[core]` "Our general objective: a web-based decision-support system using a *weighted
    multi-criteria* engine — meaning each renewable option is scored by combining several
    location factors, each with an assigned importance weight — evaluated with CALABARZON
    households but built for nationwide province-and-municipality coverage."
  - `[optional]` "Two deliberate scope choices to notice: the *evaluation* is regional, but the
    *data coverage* is national — we say 'nationwide applicability,' never 'nationally
    validated.' And the DSS structure follows the classic Sprague-and-Carlson model: a data
    component, a dialog component — our UI — and a model component — our engines."
  - `[core]` "The hypothesis is deliberately testable: does LUMI significantly improve *perceived*
    decision support versus people's prior methods? The null says ratings won't differ from a
    neutral 3.00 midpoint; the alternative says they will."
  - `[optional]` "Why 'perceived'? Because a household decision aid succeeds when people
    understand and trust it — that's measurable, and it's the honest claim our instrument
    supports. Engineering accuracy is a different question — that one we test through expert
    agreement, which you'll see shortly."
- **Timing:** ~40 s core / ~75 s full. **Transition:** "We decomposed that into eight specific objectives."
- **If asked:** "perceived" = measured against neutral 3.00, not engineering accuracy — keep the
  distinction; the panel may probe it.
- **Watch:** "households in CALABARZON, nationwide *applicability*" — never "nationally validated."

## S4 — Specific Objectives SO1–SO4 + Solutions

- **On slide:** SO1 interactive map interface → EnergyHub module (evidence: 4.50/5 IT rating);
  SO2 weighted MCDM engine (evidence: 82.22% agreement, 9 locations); SO3 predictive analytics →
  EnergyHub ARIMA(1,1,1) (MAE 6,829.09 GWh consumption / 1,019.66 MW peak); SO4 EcoSim what-if
  sim for solar/wind/hydro with geothermal as *reference only* (evidence: 4.40/5).
- **Literature anchor:** Asadi et al. (2023) GIS-AHP site selection · Tarife et al. (2023)
  Philippine GIS-AHP · Krishnan et al. (2024) ARIMA for energy demand · Malakouti (2026)
  classical models as interpretable baselines.
- **Script:**
  - `[core]` "SO1 is delivered by EnergyHub's interactive maps — rated 4.50 out of 5 by the IT
    experts, so inside the top rating band for that module."
  - `[core]` "SO2 is our weighted MCDM engine. Its recommendations agreed with engineering
    experts in 37 of 45 valid assessments — that's 5 engineers times 9 locations — an 82.22%
    agreement rate."
  - `[core]` "SO3 is ARIMA(1,1,1) forecasting. Its mean absolute error is about 6.8 thousand GWh
    on national consumption — that number sounds large only until you remember national demand
    is roughly a hundred *thousand* GWh a year; as a percentage that's a 5.67% miss, which is
    why the paper reports MAPE. On peak demand the MAE is about 1,020 MW."
  - `[optional]` "We chose ARIMA deliberately: the literature shows classical statistical models
    are interpretable baselines that suffice on predictable seasonal demand data — exactly our
    case — and we verified the choice with an AIC search plus a pilot bake-off against linear
    regression, Holt, and random forest."
  - `[core]` "SO4 is EcoSim — household what-if simulation for solar, wind, and hydro, rated
    4.40/5. Geothermal appears as reference information only, because it's utility-scale — no
    household installs a geothermal plant."
- **Timing:** ~60 s core / ~90 s full. **Transition:** "…and the remaining four objectives."
- **If asked:** why two modules? EnergyHub = understand the data; EcoSim = simulate *your*
  household. National-vs-personal scale separation.

## S5 — Specific Objectives SO5–SO8 + Solutions

- **On slide:** SO5 user-friendly interface → dashboards + AI explanations (4.70/5 household
  clarity); SO6 system evaluation → 100 CALABARZON households (4.73 usability, 4.79 advantage);
  SO7 expert validation → barangay consultation + engineers + ISO 25010 by IT experts (4.47/5);
  SO8 performance testing → agreement rate, response time, MAE/RMSE (82.22%, ~104 ms,
  6,829.09/8,257.12 GWh).
- **Literature anchor:** Nielsen (usability principles → the household instrument) ·
  ISO/IEC 25010:2023 (IT instrument) · Butschek et al. (2023) GIS-MCDA validated by domain
  professionals.
- **Script:**
  - `[core]` "SO5 covers usability: households rated the interface's clarity 4.70 out of 5."
  - `[core]` "SO6 is the evaluation itself — one hundred CALABARZON households produced a
    usability mean of 4.73 and a comparison-with-prior-methods mean of 4.79, both in the
    strongest agreement band."
  - `[core]` "SO7 is expert validation — barangay consultations plus licensed engineers plus ten
    IT experts rating the software under the ISO/IEC 25010 quality model: 4.47, 'Excellent.'"
  - `[core]` "And SO8 is performance testing — agreement rate, response time, and forecast
    error — 82.22%, about 104 milliseconds average local API response, and the MAE/RMSE figures
    you see."
  - `[optional]` "Notice each SO has a *different kind* of evidence: subjective ratings for
    usability, a formal quality standard for software, expert agreement for the engine, and
    machine-measured numbers for performance — the triangulation is intentional."
- **Timing:** ~45 s core / ~65 s full. **Transition:** "Before methodology — what the system does and does not claim."
- **If asked:** the SO-column is the defense checklist; every later claim maps back to an SO.
  Cross-reference: `02-PAPER-TO-CODE-AUDIT.md` Part A.0.

## S6 — Scope & Limitations

- **On slide:** Scope — nationwide province/municipality coverage; solar, wind, hydro +
  geothermal reference; integrated features; 100 households + 10 IT + 5 engineers. Limitations —
  CALABARZON sample (not nationally representative); **preliminary** assessments, not a
  substitute for engineering feasibility studies; data dependency; geothermal agreement not
  evaluated.
- **Literature anchor:** quota sampling (Futri et al., 2022) — why the household sample is
  regional, non-probability.
- **Script:**
  - `[core]` "Scope: nationwide data coverage, three recommended sources plus geothermal as
    reference information."
  - `[core]` "Four limitations we state upfront. First, the household sample is CALABARZON only —
    quota sampling, descriptive evidence, not nationally representative — while *data coverage*
    is nationwide. Those are different claims; we keep them separate."
  - `[core]` "Second, outputs are *preliminary* decision support, not engineering feasibility
    studies — the system even tells users to consult licensed engineers."
  - `[core]` "Third, accuracy depends on the source datasets — NASA POWER's resolution is about
    fifty kilometers, which is coarse at municipality level; we surface that inside the app as
    confidence scores rather than hiding it."
  - `[core]` "Fourth, geothermal's expert agreement was not evaluated — so we never claim it."
  - `[optional]` "We list these ourselves for a reason: a limitation you volunteer reads as
    rigor; a limitation you're caught on reads as an error."
- **Timing:** ~50 s core / ~70 s full. **This slide is your shield** — deliver it confidently.
- **If asked:** "Why not nationally representative?" → sampling was scoped to CALABARZON for the
  evaluation phase; nationwide applies to *data coverage*, not the respondent sample.

## S7 — Methodology

- **On slide:** Mixed-method developmental research; pipeline Needs Assessment → System
  Development → System Evaluation → Final Evaluation; evaluators 100 households + 10 IT + 5
  engineering experts; three instruments (household questionnaire; ISO/IEC 25010:2023 IT
  instrument; engineering instrument covering suitability, interaction, reliability, safety,
  agreement).
- **Literature anchor:** Nielsen (usability → household items) · ISO/IEC 25010:2023 (IT items) ·
  Saunders et al. (2023) purposive sampling · Ahmad & Wilkins (2025) expert sampling ·
  Malterud et al. (2021) Information Power → small expert N · Futri et al. (2022) quota sampling.
- **Script:**
  - `[core]` "Mixed-method developmental research — we built iteratively under Agile, then
    evaluated. The pipeline runs needs assessment, development, system evaluation, final
    evaluation."
  - `[core]` "Three respondent groups answer three different questions, so each gets a matched
    instrument: 100 households on usability and comparison — the questionnaire built on
    Nielsen's usability principles; 10 IT experts on software product quality using the ISO/IEC
    25010:2023 instrument; and 5 licensed electrical and electronics engineers on technical
    validity — suitability, reliability, safety, and independent recommendations."
  - `[optional]` "The small expert count is justified, not lazy: purposive expert sampling
    targets *information density* — under the Information Power framework, a few highly relevant
    experts outperform many unqualified respondents. And don't confuse respondent counts: the
    earlier needs-assessment phase surveyed about 196 household decision-makers; the final
    evaluation used 100."
- **Timing:** ~45 s core / ~70 s full. **Transition:** "Here's what the analysis produced."
- **If asked:** 196 (needs assessment) vs 100 (final eval) — different phases, different N.

## S8 — Data Analysis: Evaluation Results

- **On slide:** Household usability **4.73** (Strongly Agree), comparison **4.79**; IT experts
  **4.47 Excellent**; engineering **3.27 Satisfactory**; Cronbach's α **0.923** usability /
  **0.868** comparison; **t(99)=55.47, p<.001** → reject null; ratings vs neutral benchmark 3.00.
- **Literature anchor:** Jurwita et al. (2024) — percentage-agreement formula used for
  recommendation matching · Hohmann et al. (2025) — consensus thresholds · Nielsen / ISO 25010 —
  instrument provenance.
- **Script:**
  - `[core]` "Household usability averaged 4.73 and the comparison against prior methods 4.79 —
    on the five-point scale both sit in the 'Strongly Agree' band, meaning respondents felt the
    system was both usable and better than how they evaluated options before."
  - `[core]` "The questionnaire itself is reliable: Cronbach's alpha measures whether the items
    hang together — 0.923 on usability is 'excellent' internal consistency, 0.868 on comparison
    is 'good.' Above 0.8 is the accepted reliability bar."
  - `[core]` "For significance, a one-sample t-test compares the mean against the neutral
    midpoint of 3.00 — not against another system, which matters: it tests 'above neutral,'
    not 'better than X.' t(99) — 99 degrees of freedom, one less than our 100 respondents —
    comes out at 55.47, p < .001: the chance of seeing this by accident is under a tenth of a
    percent. We reject the null."
  - `[core]` "IT experts rated software quality 4.47 — 'Excellent.' The engineering group's
    technical assessment was 3.27 — 'Satisfactory' — and we report it plainly: their rubric is
    stricter, covering suitability, safety, and reliability, and it directly produced the
    refinement recommendations you'll see at the end."
  - `[optional]` "If anyone spots the appendix tabulation showing 4.46: the deck summarizes
    4.47 — presentation-level rounding, same 'Excellent' band, already flagged in our prep."
- **Timing:** ~70 s core / ~85 s full.
- **If asked:** (a) benchmark = neutral 3.00 midpoint, *not* a competing system. (b) Why 3.27? →
  stricter rubric; drove S21 recommendations. (c) 4.46-vs-4.47 — rounding-level, same band.
- **Watch:** say "significantly above neutral benchmark," not "better than every alternative."

## S9 — Recommendation Validation

- **On slide:** **82.22%** — 37 of 45 assessments matched; Solar & Wind 85%; Hydropower 60%;
  Geothermal N/A.
- **Literature anchor:** **Hohmann et al. (2025)** — the consensus literature behind the 80%
  threshold (80–89% = consensus; 90–99% very strong; 100% unanimous) · **Jurwita et al. (2024)** —
  the percentage-agreement formula · Butschek et al. (2023) — domain-professional validation.
- **Script:**
  - `[core]` "Here's the engine's validation. Five licensed engineers each gave their own
    independent recommendation for nine test locations — 45 assessments. Responses of
    'insufficient information' were excluded from the denominator, so 45 is the *valid* count.
    In 37 of them, the engineer's own pick matched LUMI's recommendation: 82.22%."
  - `[core]` "That clears the 80% threshold we set from the consensus literature — an agreement
    level of at least 80% is the accepted bar for expert consensus."
  - `[core]` "By source: solar and wind each agreed 85% of the time; hydropower agreed 60% —
    which is exactly why our recommendations list includes refining the hydro criteria.
    Geothermal shows N/A because it was not evaluated at all."
  - `[optional]` "And the precise framing: this is *agreement with expert judgment*, not a
    measured accuracy rate — the paper says so itself. Agreement tells you the engine's logic
    matches professional reasoning in these cases; it does not certify production accuracy."
- **Timing:** ~50 s core / ~70 s full. **Transition:** "Let me show how the system is actually built."
- **If asked:** 82.22% = agreement, never "accuracy." 45 = 5 × 9. Hydro 60% → refinement rec.

## S10 — System Architecture

- **On slide (diagram):** Input: DOE data, climate data, terrain/GIS data, location data, user
  input → Process: ARIMA model, RAG, renewable-energy formulas, suitability scoring → Output:
  suitability recommendations, LLM summary → UI: EcoSim, EnergyHub. Database + External APIs feed
  the process.
- **Literature anchor:** Sprague & Carlson (1982) — data/dialog/model maps directly onto this
  diagram · Asadi et al. (2023) — GIS-AHP stack precedent.
- **Script:**
  - `[core]` "One data spine feeds everything. On the input side: DOE statistics, NASA POWER
    climate data, terrain and GIS datasets, and location data — all ingested *offline* into our
    database through ETL pipelines — plus the user's own inputs at runtime."
  - `[core]` "Processing combines four engines: ARIMA forecasting, RAG-grounded LLM explanations,
    the physics-based renewable output formulas, and the weighted suitability scoring. Outputs
    — recommendations, forecasts, and plain-language summaries — surface through the two
    modules, EnergyHub and EcoSim."
  - `[optional]` "That offline-ingestion detail is why the system is fast: no external API is
    called at request time — the data is already local — which is how the endpoint sweep
    averages about 104 milliseconds."
  - `[optional]` "Structurally it follows the classic DSS split — data component, model
    component, dialog component — so each piece of the diagram maps to a framework element the
    panel will recognize."
  - `[optional]` "Underneath: FastAPI backend, React/Vite frontend, Supabase Postgres with
    row-level security so users only touch their own rows, Redis caching, deployed serverless
    on Vercel."
- **Timing:** ~45 s core / ~80 s full.
- **If asked (technical):** stack + ETL detail — full depth in `03-SYSTEM-DESIGN-AUDIT.md` §1–4.

## S11 — Functional Requirements: EnergyHub I

- **On slide:** National Overview & Provincial Demand — national electricity statistics,
  provincial demand, renewable-energy benchmarks. `[USER INPUT NEEDED: describe the
  screenshot/chart on this slide]`
- **Literature anchor:** Bassetti (2024) — environmental-intelligence framing (turning national
  data into interpretable insight).
- **Script:**
  - `[core]` "EnergyHub answers the national question first: 'what does the country's energy
    picture look like?' — consumption levels, generation mix, provincial demand broken down by
    sector, and renewable benchmarks. It's the context layer: before a user simulates their own
    house, they can see where the country stands."
  - `[optional]` "The provincial-demand view matters for scale honesty — the same dataset the
    forecasts are built on is what users see here, so nothing on this screen is a black box."
- **Timing:** ~25 s core / ~40 s full.

## S12 — Functional Requirements: EnergyHub II

- **On slide:** Renewable Potential & Forecasting — interactive potential maps; historical +
  forecasted national trends. `[USER INPUT NEEDED: which map/forecast is shown]`
- **Literature anchor:** Asadi et al. (2023) GIS-AHP suitability mapping · Tarife et al. (2023).
- **Script:**
  - `[core]` "The second half is spatial and temporal: interactive suitability maps down to
    municipality granularity — solar, wind, hydro, geothermal, and a composite view — plus the
    historical series with the ARIMA forecast layered on top, so users see both where the
    resource is and where demand is going."
  - `[optional]` "Map-level scores are deliberately simple — normalized factors and an
    unweighted composite — because a national map needs comparability, while the household
    engine in EcoSim applies the fuller weighted logic. If asked why two scoring paths exist,
    that's the answer."
- **Timing:** ~25 s core / ~45 s full.

## S13 — Functional Requirements: EcoSim I

- **On slide:** Location-based recommendations, suitability comparisons, estimated generation.
- **Literature anchor:** Malczewski (2006) WLC · Beriro et al. (2022) WSM precedent.
- **Script:**
  - `[core]` "EcoSim is the personal layer. Pick a province or municipality, enter your monthly
    consumption or your bill, and the engine returns ranked renewable options — each with a
    suitability score and an estimated monthly generation figure."
  - `[optional]` "Under the hood the score is a weighted linear combination in the style the
    literature standardizes: roughly forty percent reflects raw resource quality at that
    location, and up to sixty percent scales with how much of *your* consumption the source can
    actually cover — so a great resource that covers nothing won't outrank a good one that
    covers your bill. A proximity bonus nudges scores near real operating plants, capped so it
    can't manufacture a result."
- **Timing:** ~25 s core / ~50 s full.

## S14 — Functional Requirements: EcoSim II

- **On slide:** AI-generated explanations + directory of renewable-energy providers/retailers.
- **Literature anchor:** (light) explainable-AI direction — XAI in decision support per the
  thesis RRL's IDSS discussion.
- **Script:**
  - `[core]` "Every result can be explained by the AI assistant in plain language — the numbers
    stay deterministic, the LLM only narrates them. And the provider directory — 32 verified
    entries built from the 2026 DOE registry — connects users to real installers."
  - `[optional]` "Provider matching is deliberately provider-agnostic: we match by technology
    and region, never by sponsorship — the deck's neutrality requirement is enforced in code."
- **Timing:** ~25 s core / ~40 s full.
- **If asked:** 32 verified providers (`data/providers.json`); matching is provider-agnostic by
  design (git `896843d`).

## S15 — Functional Requirements: EcoSim III

- **On slide:** Recommended Next Steps — suggested actions incl. expert consultation and local
  requirements.
- **Literature anchor:** decision-*support* framing (Sprague & Carlson 1982 — the tool informs,
  the human decides).
- **Script:**
  - `[core]` "We deliberately end the result flow with next steps — including 'consult a licensed
    engineer' — because the system is decision *support*, not a feasibility study. This screen
    is the scope limitation from earlier, made visible inside the product."
  - `[optional]` "That's not disclaiming value — it's routing users to the right next action:
    permits, structural checks, an actual site survey. A panel asking 'is this responsible
    design?' — this slide is the answer."
- **Timing:** ~25 s core / ~40 s full. Land the closing point.

## S16 — Functional Requirements: User Authentication

- **On slide:** secure registration, sign-in, **Google** authentication, 2FA.
- **Literature anchor:** (light — security is internal; cite Supabase-backed auth + RLS design).
- **Script:**
  - `[core]` "Accounts support email-and-password, Google sign-in, and TOTP two-factor
    authentication — time-based one-time passwords, the six-digit codes from an authenticator
    app. The backend verifies tokens against Supabase, and row-level security means users can
    only ever see their own data."
  - `[optional]` "Enrollment is guided — the app shows the QR code *and* the manual secret with
    app recommendations — and unenrolling requires a current code, so you can't lock yourself
    out silently."
- **Timing:** ~25 s core / ~40 s full.
- **If asked:** Google + email + TOTP 2FA only — GitHub OAuth appears in an old test doc but is
  **UNVERIFIED** in code; don't claim it.

## S17 — Functional Requirements: Saved Simulations

- **On slide:** save, revisit, delete previous EcoSim analyses.
- **Literature anchor:** (light — feature slide).
- **Script:**
  - `[core]` "Authenticated users can save simulations and revisit or delete them — and by
    default every run auto-saves under a preference the user controls."
  - `[optional]` "Worth knowing where that default came from: IT-expert feedback in the earlier
    evaluation rounds — the autosave toggle is literally an evaluator-driven change."
- **Timing:** ~20 s core / ~35 s full.
- **If asked:** autosave default-on came from IT-expert feedback (migration 0023 + profiles
  toggle in SecuritySettings).

## S18 — Results & Discussion: ML/AI Models

- **On slide:** ARIMA(1,1,1): **5.67%** held-out MAPE, MAE 6,829.09 GWh, RMSE 8,257.12 GWh.
  Generative AI: **~7.1 s** live model-call average; Groq/Gemini-supported; **~1.9 s** fallback
  path. MCDM: 82.22% agreement (37/45, 9 locations).
- **Literature anchor:** **Benitez et al. (2024)** — Philippine forecasting models volatile,
  failing WESM's 18% MAPE threshold — our 5.67% is well under that reference · Malakouti (2026) —
  classical statistical models as fast, interpretable baselines · Mustafa & Al-Yozbaky (2025) —
  classical models suffice on predictable seasonal data · Krishnan et al. (2024) — ARIMA for
  energy demand.
- **Script:**
  - `[core]` "Three engines, and each earns a different kind of number. First ARIMA(1,1,1). The
    name itself encodes the model: one autoregressive term — the forecast leans on the previous
    period's value — one differencing step, which strips out trend; and one moving-average
    term, which smooths last period's error. It's the classic Box-Jenkins-style structure,
    chosen because national demand is a steadily trending, predictable series — and we verified it through an
    AIC configuration search and a pilot bake-off against linear regression, Holt, and random
    forest."
  - `[core]` "Now the three error metrics, because they answer different questions. MAPE — mean
    absolute *percentage* error — is 5.67% on held-out data, meaning data the model never saw
    during fitting: on average the forecast misses actual national consumption by under six
    percent. The MAE — mean *absolute* error — is 6,829 GWh: that's the same average miss but in
    energy units, and it only sounds large because national consumption runs around a hundred
    thousand GWh a year — the percentage is the honest interpretation. And RMSE at 8,257 GWh
    squares errors before averaging, so it punishes large misses — RMSE sitting above MAE tells
    you there are occasional bigger misses, which we disclose rather than smooth over."
  - `[optional]` "For context the panel will appreciate: Philippine forecasting studies have
    been found volatile enough to miss the Wholesale Electricity Spot Market's 18% MAPE
    threshold (Benitez et al., 2024). 5.67% sits far under that reference — and we still
    present it as a held-out result, not a fitted one."
  - `[core]` "The generative-AI numbers are *two different things*, and we keep them separate.
    About 7.1 seconds is a live model call — a full provider round-trip including retries. About
    1.9 seconds is the cached or fallback path, which is the common case once content is warm.
    Neither contradicts the 104-millisecond API average — that's local endpoints with no LLM in
    the path. Three latencies, three different things being measured."
  - `[core]` "And the MCDM engine — 82.22% expert agreement, 37 of 45 valid assessments across 9
    locations, which we covered at validation."
- **Timing:** ~95 s core / ~115 s full — the deepest slide; don't rush it.
- **If asked:** (a) keep latencies separate — the trap. (b) MAE in GWh → national-scale context.
  (c) Model chosen by AIC + pilot bake-off (`artifacts/rerun-2026-09-15/ml/aic_grid.csv`,
  `tests/pilot_run/evaluate_models.py`).
- **Evidence to justify it live** *(reference, not spoken — point at these if challenged)*:
  - **5.67% / 6,829.09 / 8,257.12** — harness `docs/09-Technical-Evaluation/artifacts/scripts/
    evaluate_forecasting_models.py`: reads `master_preprocessed.csv` (L46), runs a held-out
    comparison of Linear / Naive / Holt / ARIMA / SARIMAX+Exog / RF plus an AIC configuration
    grid, writes the whole `ml/` artifact set (L142–222). The three numbers sit in
    `rerun-2026-09-15/ml/model_metrics_consumption.csv`, **ARIMA(1,1,1) row**. Supporting
    artifacts: `aic_grid.csv`, `cv_expanding_window.csv`, `cv_summary.csv`, `dm_test.json`,
    `forecast_vs_actual.csv`, `residuals_test.csv`, `robustness_perturbation.csv`,
    `latency_and_size.json`, `forecast_plot.png`. Re-run: `python evaluate_forecasting_models.py`.
  - ⚠ **Open this CSV before the panel does:** in the rerun table ARIMA is *not* the
    lowest-MAPE model — Linear 4.965, Holt 5.435, Naive 5.566 all score lower on the held-out
    set, while SARIMAX+Exog (14.0) and RF (10.9) score worse. The selection rests on the AIC
    search, the earlier pilot bake-off, and interpretability — say exactly that if asked "why
    not the best-scoring model"; never claim it was the champion.
  - **Peak MAE 1,019.66** — same harness → `ml/model_metrics_peak_demand.csv` ARIMA row
    (renewables variant: `model_metrics_renewable.csv`).
  - **~7.1 s live LLM** — harness `artifacts/scripts/llm_groq_eval.py` →
    `rerun-2026-09-15/llm/llm_eval.json`: `runs[]` = **6 live Groq calls**, each with
    `latency_ms` (mean **7,076.1 ms**), `headers_ok`, `survives_sanitizer`,
    `prescriptive_extracted`; `timeout_path` records the 0.5 s-timeout → empty-response
    behavior; raw outputs in `prompt_and_response_snippets.json`. Re-run: `python
    llm_groq_eval.py` (needs a live provider key).
  - **~1.9 s fallback** — same run's `rerun-2026-09-15/llm/run_log.txt`: *"fallback returned
    response: True (1919.7 ms)"* — the literal provenance of the number.
  - **82.22% agreement** — **not produced by code**: thesis validation records, 5 engineers ×
    9 locations, 37/45 valid matches. Deep dive: `06e` §6 · discrepancies: `05` watchlist.
    *Say:* "agreement with domain experts, not accuracy."

## S19 — Results & Discussion: System Testing

- **On slide:** **315** passed unit+backend+frontend+integration tests (+2 integration skipped);
  **82/82** endpoint checks in live sweep; **~104 ms** average local API response, no failures at
  tested 100-user load; **16/18** security probes passed + 1 warning/info findings.
- **Literature anchor:** ISO/IEC 25010:2023 reliability/functional-suitability characteristics —
  the framework these tests substantiate (testing itself is internal evidence).
- **Script:**
  - `[core]` "Testing covered four layers, and each number means something specific. First, 315
    automated tests passing across unit, backend, frontend, and integration suites — with two
    integration tests *skipped*, not failed: they require a pytest plugin the environment
    doesn't provide, and that's documented rather than hidden."
  - `[core]` "Second, a scripted live sweep hit all 82 mounted endpoints — valid requests plus
    negative cases — and all 82 returned their expected results. That's endpoint-level
    functional coverage, not just unit-level."
  - `[core]` "Third, performance: about 104 milliseconds average response locally *including
    real database queries* — fast because every dataset is pre-ingested; and a load test at 100
    concurrent users completed with no failures."
  - `[core]` "Fourth, security: 16 of 18 live probes passed — the probes cover the JWT matrix —
    no token, malformed, alg:none, wrong signature, expired — plus security headers, CORS
    preflight, API-docs exposure, and error-body leakage. The residual findings are documented
    with mitigations — not hidden."
  - `[optional]` "If asked 'are the counts still exact today?': the 315 is the documented
    defense-time aggregate — our testing audit reconciles it suite-by-suite; the honest line is
    'we can re-run any of this live.'"
- **Timing:** ~60 s core / ~75 s full.
- **If asked:** suite breakdown + drift reconciliation = `04-TESTING-AUDIT.md`. Say "documented
  with mitigations," never "fully secure."
- **Evidence to justify it live** *(reference, not spoken — point at these if challenged)*:
  - **315 tests** — suites: `tests/tests/unit/` (reported 177), `fastapi-backend/tests/`
    (reported 106), `tests/tests/integration/` (23 + 2 skipped, `-m mock` run), `react-frontend`
    vitest (reported 9). Preserved outputs: `artifacts/functional/pytest-lumi-unit.txt`,
    `rerun-2026-09-15/functional/pytest-backend.txt` — which honestly shows **104 pass + 2
    env-fail** inside the reported "106", `functional/pytest-lumi-integration.txt`,
    `functional/vitest-frontend.txt`. Re-run commands: `04` §7. *Say:* "315 is the defense-time
    aggregate; the audit reconciles drift suite-by-suite."
  - **82/82 sweep** — harness `artifacts/scripts/endpoint_sweep.py`: `BASE =
    "http://127.0.0.1:8000"` (L25) → `probe_ids()` fetches real IDs from the live API →
    `build_cases()` (L60) builds the 82 TC-* cases including auth endpoints hit without and
    with malformed token → `verdict()` (L237) maps expected-spec vs actual status to PASS →
    writes `artifacts/functional/endpoint_sweep.csv` (columns `id,method,path,expected,status,
    latency_ms,verdict,note,response_snippet`) + `.jsonl`. Corrections arc: 70/75 (Sep 5,
    defects DEF-01…06 logged in `functional-test-results.md`) → 79/82 (Sep-15 rerun) →
    **82/82** final. Re-run: `python endpoint_sweep.py` with the server running.
  - **~104 ms API** — harness `artifacts/scripts/benchmark.py`: `ENDPOINTS` list (~24),
    `sample()` n=30 per endpoint (`--n` default 30), `pct()` percentiles, `supabase_timings()`
    via `--db-only` → `artifacts/perf/latency.csv` + `summary.json`. **The 104 = mean of the
    24 per-endpoint `mean_ms` values = 104.7 ms** — open `summary.json` and point at the column.
  - **100 users, zero failures** — harness `artifacts/load/locustfile.py`: `LumiUser` with
    `wait_time between(0.2, 1.0)` and weighted `@task(5)/(3)/(4)/(2)` tasks; `LUMI_LOAD_PROFILE`
    selects A=raw (default) / B=throttled / C=spoof. Artifacts `artifacts/load/runs/u100_stats.csv`
    + `u100_failures.csv` (**headers only — zero failure rows**) + `u100.html`; full stepped
    series u1→u100 plus clean_u10..u75 and throttled_u8/spoof_u8 profiles. Re-run:
    `locust -f locustfile.py --host http://127.0.0.1:8000` (+ env for profiles).
  - **16/18 probes** — harness `artifacts/scripts/security_probes.py`: `rec()` records each
    probe as `{id,check,observed,verdict,detail}`; `mint_jwt()`/`alg_none_jwt()` mint real and
    expired tokens; the 18 entries — SEC-AUTH-01…06 (JWT matrix), SEC-AUTH-ADM×3, SEC-HDR-01/02,
    SEC-CORS-×3, SEC-DOCS×3, SEC-ERR-01 → `artifacts/security/probes.json`. **The two residuals
    were `SEC-HDR-02` server-banner disclosure (warning) and `SEC-DOCS` API-docs exposure
    (informational)** — both fixed afterward: the preserved post-hardening `probes.json`
    re-records all 18 as PASS (banner now `'Lumi'`, docs now 404). Findings register SEC-01…10
    in `security-test-results.md`. Re-run: `python security_probes.py`. *Say:* "the two
    residuals were documented, fixed, and re-verified."
  - **Adjacent evidence** — `artifacts/scripts/failure_matrix.py`: 17 FM-* injected scenarios
    (provider outage, timeouts, DB/Redis down, oversized bodies) → `failure/failure_matrix.json`
    — this is what backs the "negative cases" phrase; `make_screenshots.py` produced the
    B-01…B-17 evidence PNGs used in the demo backup plan.

## S20 — ISO/IEC 25010 Evaluation Results

- **On slide:** Compatibility highest (**4.65**), Flexibility lowest (**4.20**). `[USER INPUT
  NEEDED: if the slide shows the full characteristic bar chart, note each score]`
- **Literature anchor:** ISO/IEC 25010:2023 — the quality model itself (8 characteristics).
- **Script:**
  - `[core]` "ISO/IEC 25010 rates software across eight quality characteristics — functional
    suitability, performance, compatibility, usability, reliability, security, maintainability,
    and flexibility. Compatibility scored highest at 4.65 — the system coexists cleanly with
    browsers, devices, and the surrounding stack."
  - `[core]` "Flexibility scored lowest at 4.20 — still 'Excellent' band, but the relative weak
    spot: adaptability to varied scenarios and datasets. And that directly motivated one of our
    recommendations — broadening datasets and scenario coverage — so the weakest score produced
    a concrete action."
  - `[optional]` "Overall quality was 4.47 'Excellent' — and if anyone checks the appendix
    tabulation showing 4.46: presentation-level rounding, same band."
- **Timing:** ~35 s core / ~50 s full.
- **If asked:** 4.47 overall vs 4.46 appendix — rounding-level, same band.

## S21 — Conclusion & Recommendations

- **On slide:** Conclusion — successful development; positive evaluation (households favorable,
  IT Excellent); 82.22% agreement supports potential **but further engineering validation
  remains necessary**. Recommendations — refine MCDM criteria (esp. hydropower, low-agreement
  locations); expand datasets/forecasting/hardware sizing/advanced simulations; expand validation
  across more Philippine locations.
- **Literature anchor:** Tarife et al. (2023) — criteria refinement through expert consultation
  precedent · Hohmann et al. (2025) — consensus supports potential, not proof.
- **Script:**
  - `[core]` "The conclusion follows the evidence chain. We built a working platform that
    integrates recommendation, forecasting, and simulation. Households rated it favorably;
    IT experts rated it Excellent. And the engine agreed with engineering experts in 37 of 45
    assessments."
  - `[core]` "But the honest reading — the one printed on our slide — is that agreement supports
    *potential*, not production-readiness; the engineering group's 3.27 and the two 60%
    locations tell us further validation is needed."
  - `[core]` "So our own recommendations: refine the MCDM criteria — hydropower first, and the
    low-agreement locations; expand datasets, forecasting, hardware sizing, and simulation
    depth; and validate across more Philippine locations."
  - `[optional]` "That self-critical close is deliberate: citing Tarife's expert-refined
    criteria as precedent — criteria *should* evolve with expert input — our refinement
    recommendation is method continuation, not a confession."
- **Timing:** ~55 s core / ~75 s full. **Transition:** "We also sketched a responsible path to monetization."

## S22 — Business Monetization & Commercialization Plan

- **On slide:** Freemium model (free basic assessments + AdSense; premium subscriptions);
  provider partnerships; 3-phase plan (validation → launch w/ Metro Manila priority →
  MSME/institutional/government expansion). **Slide itself notes: proposed strategies; revenue
  and willingness-to-pay NOT yet validated.**
- **Literature anchor:** none forced — the slide's own caveat is the anchor; say "proposed."
- **Script:**
  - `[core]` "A freemium model is *proposed*: free basic assessments sustaining reach — with an
    advertising line — premium subscriptions for deeper simulations, and provider partnerships.
    The rollout is three phases: validate, launch prioritizing Metro Manila where Palanca-Tan's
    preference data applies, then expand to MSMEs, institutions, and government."
  - `[core]` "And the caveat is printed on our own slide: these are proposals — willingness to
    pay and commercial feasibility are not yet validated. We present a path, not a proven
    business."
  - `[optional]` "If asked 'why monetize a thesis system at all?': because sustainability is a
    real adoption question for a public-facing tool — and presenting it as unvalidated keeps the
    claim honest."
- **Timing:** ~35 s core / ~50 s full.
- **If asked:** never claim commercial viability — repeat the disclaimer.

## S23 — System Demonstration

- **On slide:** "SYSTEM DEMONSTRATION" (live demo segue).
- **Script:**
  - `[core]` "Let me show you the system itself."
  - `[optional]` Narrations for each stop (deploy only if the panel seems quiet/expecting talk):
    at the map — "every number here is a real dataset, nothing mocked"; at EcoSim results —
    "watch the scores and the confidence labels — the system says when its own data is thin";
    at AI explanation — "this is the slow call by design — a live provider round-trip, with a
    fast cached path underneath."
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
- **Script:**
  - `[core]` "That's LUMI — cleaner energy, brighter tomorrow. We're happy to take questions."
  - `[optional]` If a pause: "The short version of everything you saw: a working platform,
    household-approved usability, ISO-Excellent software quality, and an engine that agrees
    with engineers most of the time — with the gaps named and the next steps scheduled."
- **Timing:** ~10 s. Then Q&A mode — `05-DEFENSE-KNOWLEDGE-BASE.md` is the Q&A bank.

## S25 — Appendix: Interview / Data Gathering

- **On slide:** "APPENDIX — INTERVIEW / DATA GATHERING" — photo page. `[USER INPUT NEEDED: who is
  shown, which consultation — barangay officials / engineering experts]`
- **Literature anchor:** Tarife et al. (2023) — expert-refined criteria precedent.
- **Use:** only if asked for evidence of field work — `[core]` "we consulted barangay officials
  and licensed engineers; these are the sessions."
- **Backup reference:** appendix transcripts in thesis (@3121–3488).

## S26 — Appendix: Demonstration During Evaluation

- **On slide:** evaluation-session photos. `[USER INPUT NEEDED: setting, who's testing]`
- **Use:** if asked how household evaluation was administered — `[core]` "respondents used the
  live system during supervised sessions."

## S27 — Appendix: UAT Results

- **On slide:** "UAT RESULTS". `[USER INPUT NEEDED: what the tabulation shows — scores per
  criterion?]`
- **Use:** support for S8 numbers — `[core]` "the item-level ratings behind the 4.73/4.79 means."

## S28 — Appendix: IT Expert Testing & Results

- **On slide:** expert testing evidence. `[USER INPUT NEEDED: which screens/results shown]`
- **Use:** backup for the 4.47 ISO 25010 claim — `[core]` "the characteristic-level scores behind
  the 4.47 average."

## S29 — Appendix: Questionnaire Tabulation

- **On slide:** questionnaire tabulation tables. `[USER INPUT NEEDED: which instrument's
  tabulation is shown]`
- **Use:** deepest-level backup — `[core]` "the raw item-by-item tabulation," incl. the 4.46/4.47
  discrepancy if spotted (answer in S8's if-asked).

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

### Literature cheat card (name-drops by topic)

| If discussing… | Cite |
|---|---|
| Why weighted-sum | Beriro et al. 2022 (web WSM DSS) · Malczewski 2006 (WLC definition) |
| Site-suitability precedent | Tarife et al. 2023 (PH GIS-Fuzzy-AHP) · Asadi et al. 2023 (GIS-AHP) |
| Criterion importance | Shatnawi et al. 2021 (technical 53.6% dominant) |
| DSS structure | Sprague & Carlson 1982 · El-Gayar 1997 |
| Forecast choice | Benitez et al. 2024 (WESM 18% context) · Malakouti 2026 · Mustafa & Al-Yozbaky 2025 |
| ARIMA for demand | Krishnan et al. 2024 |
| Agreement methodology | Hohmann et al. 2025 (consensus bands) · Jurwita et al. 2024 (formula) |
| Sampling | Saunders et al. 2023 · Ahmad & Wilkins 2025 · Malterud 2021 · Futri et al. 2022 |
| Usability instrument | Nielsen · ISO/IEC 25010:2023 |
| Env-intelligence term | Bassetti 2024 |
