# 07 — Master Script (the delivery document)

> **What this is:** the script you actually perform. Doc `01` explains the slides; this file is
> the *run of show* — every spoken line, who says it, how the three presenters hand off, the demo
> choreography, the Q&A protocol, and what to say when things go wrong.
>
> **The three layers:**
> - **Verbatim** — the polished monologue. Memorize it or deliver it near-verbatim. Written fresh;
>   every number is the verified figure.
> - **Talk-track** — 3–6 bullets carrying the same content. Your rescue version if you can't hold
>   the full lines — glance, get the beats, say it your way.
> - **Owner / Setup / Transition / If pressed** — who speaks, what's on screen, the exact line into
>   the next slide, and the answer you need if the panel interrupts.
>
> **Hand-offs:** `[→ NAME]` marks where ownership changes. Each has a spoken hand-off line —
> presenter changes are your natural transition beats; land them cleanly and the run feels
> choreographed instead of segmented.

## Presenters

| Who | Role | Owns | ~Core time |
|---|---|---|---|
| **Sean Maverick Virata** | Technical Writer | S1–2 · S6 · S21–22 · S24 — framing, scope honesty, business, close | ~3.5 min |
| **Lerrica Jeremy Torreno** | Principal Researcher & Data Analyst | S3–5 · S7–9 · S20 — the research spine | ~5.7 min |
| **Alexander Jon Solis** | Developer | S10–19 · S23 — the system, results, demo | ~6 min + demo |

*Adjustable — reassign whole blocks, never single slides, so hand-offs stay clean. If a presenter
is absent, fold their block to the adjacent owner (Torreno↔Virata on S6/S20, Virata covers S21–24;
Solis's block needs the developer or the best-prepared substitute — it carries the demo).*

## Run sheet

| S# | Slide | Owner | ~s | Cumulative |
|---|---|---|---|---|---|
| S1 | Title | VIRATA | 15 | 0:15 |
| S2 | Background of the Study | VIRATA | 45 | 1:00 |
| S3 | Objective & Hypotheses | TORRENO | 40 | 1:40 |
| S4 | Specific Objectives I | TORRENO | 60 | 2:40 |
| S5 | Specific Objectives II | TORRENO | 45 | 3:25 |
| S6 | Scope & Limitations | VIRATA | 50 | 4:15 |
| S7 | Methodology | TORRENO | 45 | 5:00 |
| S8 | Data Analysis | TORRENO | 70 | 6:10 |
| S9 | Recommendation Validation | TORRENO | 50 | 7:00 |
| S10 | System Architecture | SOLIS | 45 | 7:45 |
| S11 | EnergyHub I | SOLIS | 25 | 8:10 |
| S12 | EnergyHub II | SOLIS | 25 | 8:35 |
| S13 | EcoSim I | SOLIS | 25 | 9:00 |
| S14 | EcoSim II | SOLIS | 25 | 9:25 |
| S15 | EcoSim III | SOLIS | 25 | 9:50 |
| S16 | Authentication | SOLIS | 25 | 10:15 |
| S17 | Saved Simulations | SOLIS | 20 | 10:35 |
| S18 | Results: ML/AI Models | SOLIS | 95 | 12:10 |
| S19 | Results: System Testing | SOLIS | 60 | 13:10 |
| S20 | ISO 25010 Results | TORRENO | 35 | 13:45 |
| S21 | Conclusion & Recommendations | VIRATA | 55 | 14:40 |
| S22 | Monetization | VIRATA | 35 | 15:15 |
| S23 | System Demonstration | SOLIS | 120–240 | — |
| S24 | Thank You / Q&A | VIRATA | 10 | — |

**Timing reality:** listed budgets are conservative read-pace — natural delivery lands the
S1–S22 spine at **~11–13 min**, plus **2–4 min** demo. Over-time protocol is in §F.

## Delivery rules — the numbers stay honest

| Never say | Say instead |
|---|---|
| "82% accurate" | "82.22% agreement with engineering experts — 37 of 45" |
| "Nationally validated" | "Nationwide data coverage; the sample was CALABARZON" |
| "Fully secure" | "16 of 18 live probes passed; residuals documented" |
| "Replaces feasibility studies" | "Preliminary decision support — it routes users to engineers" |
| "Geothermal was validated" | "Geothermal is reference information only" |
| "Engineers rated it excellent" | "Engineering's technical assessment was 3.27 — Satisfactory" |
| "Proven business model" | "Proposed monetization; not yet validated" |
| "Real-time data" | "Curated datasets, offline ETL — no runtime third-party calls" |
| GitHub sign-in | email/password + Google + TOTP only |

**Fingertip numbers:** 4.73 · 4.79 · 4.47(4.46) · 3.27 · 82.22% (37/45) · 85%/60%/N-A · 5.67% ·
6,829.09 · 8,257.12 · 1,019.66 MW · ~104 ms · ~7.1 s · ~1.9 s · 315+2 · 82/82 · 16/18+warn ·
α .923/.868 · t(99)=55.47 · 100/10/5 (196 earlier) · 32 providers · 4.65/4.20.

---

## S1 — Title  ·  VIRATA  ·  ~15 s

- **Setup:** title slide up; Sean center stage, others flanking.
- **Verbatim:** "Good morning, everyone. I'm Sean Virata — this is Alexander Solis, our developer,
  and Lerrica Torreno, our principal researcher and data analyst. Together we present LUMI — a
  data-driven environmental intelligence system for renewable energy decision support."
- **Talk-track:** greet · name + role each · title once, cleanly.
- **Transition:** "Before the system itself — the problem it answers." *(same owner)*
- **If pressed:** own your contribution cold — dev ↔ build, research ↔ data/study, writer ↔
  manuscript.

## S2 — Background of the Study  ·  VIRATA  ·  ~45 s

- **Setup:** research-poster slide; hold position on the problems column.
- **Verbatim:** "Electricity demand keeps climbing — but the information a household would need to
  act on it is locked inside technical data, scattered across dozens of sources, and most
  households can't read any of it. The surrounding research already existed — in pieces.
  Palanca-Tan showed Metro Manila households *want* solar. Tarife sited renewable plants with GIS
  and fuzzy-AHP — for planners, not residents. Beriro built a web decision tool for wind projects —
  for industry, not homes. Preference, method, delivery — all proven separately, for different
  users. Nobody had put all three together at household level in the Philippines. That gap is
  LUMI."
- **Talk-track:** demand up / knowledge gap / data scattered · Palanca-Tan=wants it ·
  Tarife=planners · Beriro=projects · gap = household-level + accessible.
- **Transition:** `[→ LERRICA]` "Lerrica will walk you through what we set out to test."
- **If pressed:** the gap is household *granularity* — prior work sited plants for planners, not
  decisions for residents.

## S3 — General Objective & Hypotheses  ·  TORRENO  ·  ~40 s

- **Setup:** Lerrica steps forward; GO text on screen.
- **Verbatim:** "Our general objective: a web-based decision-support system driven by a weighted
  multi-criteria recommendation engine — in plain terms, each renewable option is scored by
  combining several location factors, each carrying an assigned importance weight — evaluated with
  households in CALABARZON, but built to cover every province and municipality nationwide. The
  hypothesis had to be falsifiable: do households perceive meaningfully better decision support
  from LUMI than from how they evaluated options before? The null says ratings sit at the neutral
  midpoint, 3.00. The alternative says they rise above it."
- **Talk-track:** GO in one breath · weighted MCDM = factors × weights · CALABARZON eval,
  nationwide coverage · H0 = midpoint 3.00.
- **Transition:** "Eight specific objectives decompose that goal." *(same owner)*
- **If pressed:** "nationwide *applicability*" never "nationally validated" · "perceived" =
  measured vs neutral 3.00, not engineering accuracy — keep the distinction.

## S4 — Specific Objectives SO1–SO4  ·  TORRENO  ·  ~60 s

- **Setup:** SO table visible; point down the rows as you speak.
- **Verbatim:** "First through fourth. SO1 — an interactive map interface, delivered by EnergyHub
  and rated 4.50 out of 5 by the IT experts. SO2 — the weighted MCDM engine itself: its
  recommendations matched the engineers' own picks in 37 of 45 valid assessments — an 82.22%
  agreement rate. SO3 — predictive analytics through ARIMA forecasting: a mean absolute error of
  about 6.8 thousand gigawatt-hours on national consumption — which sounds large only until you
  remember national demand runs around a hundred *thousand* GWh a year; as a percentage that's a
  5.67% miss — and about 1,020 megawatts on peak demand. And SO4 — EcoSim, the household what-if
  simulator for solar, wind, and hydro, rated 4.40. Geothermal appears in EcoSim as reference
  information only — it's utility-scale; no household installs a geothermal plant."
- **Talk-track:** SO1 maps→4.50 · SO2 engine→82.22% (37/45) · SO3 ARIMA→6,829 GWh = 5.67%,
  1,019.66 MW peak · SO4 EcoSim→4.40, geothermal reference-only.
- **Transition:** "The remaining four objectives." *(same owner)*
- **If pressed:** two modules because two scales — EnergyHub understands the data, EcoSim
  simulates *your* household.

## S5 — Specific Objectives SO5–SO8  ·  TORRENO  ·  ~45 s

- **Setup:** same table, second half.
- **Verbatim:** "SO5 was usability — households rated interface clarity 4.70 out of 5. SO6 was the
  evaluation itself: one hundred CALABARZON households produced a usability mean of 4.73 and a
  4.79 mean on comparison against their prior methods. SO7 was expert validation — barangay
  consultations, licensed engineers, and ten IT experts scoring the software under ISO/IEC 25010:
  4.47, 'Excellent.' And SO8 — performance testing: agreement rate, response time, and forecast
  error — 82.22%, roughly 104 milliseconds average local API response, and the error figures you
  saw. Four different kinds of evidence, deliberately: subjective ratings, a formal standard,
  expert agreement, and machine-measured numbers."
- **Talk-track:** SO5 clarity 4.70 · SO6 100 hh → 4.73/4.79 · SO7 ISO 25010 → 4.47 · SO8 →
  82.22%/~104 ms/MAE · evidence triangulation.
- **Transition:** `[→ SEAN]` "Before the methodology — what the system does and does not claim.
  Sean."
- **If pressed:** the SO column is the defense checklist; every later claim maps back to an SO.

## S6 — Scope & Limitations  ·  VIRATA  ·  ~50 s

- **Setup:** Sean back center; limitations column visible. **Deliver this one standing tall — it's
  your shield.**
- **Verbatim:** "Our scope runs nationwide at province and municipality level — solar, wind, and
  hydro recommendations, plus geothermal as reference. Now four limitations, stated upfront. One:
  the household sample is CALABARZON only — quota sampling, descriptive evidence — while data
  coverage is national; those are separate claims, and we keep them separate. Two: outputs are
  *preliminary* decision support, not engineering feasibility studies — the system itself tells
  users to consult a licensed engineer. Three: accuracy is bounded by the source datasets — NASA
  POWER's resolution is about fifty kilometers, coarse at municipality level, and we surface that
  inside the app as confidence scores rather than hiding it. Four: geothermal's expert agreement
  was never evaluated — so we never claim it."
- **Talk-track:** scope = nationwide coverage, 3 sources + geo reference · limits = CALABARZON
  sample / preliminary not feasibility / data-dependency → confidence scores / geothermal not
  evaluated.
- **Transition:** `[→ LERRICA]` "Back to Lerrica for how the work was done."
- **If pressed:** a limitation you volunteer reads as rigor; a limitation you're caught on reads as
  an error.

## S7 — Methodology  ·  TORRENO  ·  ~45 s

- **Setup:** methodology pipeline on screen.
- **Verbatim:** "The research was mixed-method and developmental: we built iteratively under Agile,
  then evaluated — needs assessment, system development, system evaluation, final evaluation.
  Three respondent groups answer three different questions, so each got a matched instrument: one
  hundred households rated usability and comparison on a questionnaire built from Nielsen's
  usability principles; ten IT experts rated software product quality on the ISO/IEC 25010
  instrument; and five licensed electrical and electronics engineers assessed technical validity —
  suitability, reliability, safety — plus gave their own independent recommendations. The small
  expert count is deliberate: purposive expert sampling optimizes for information density — a few
  highly relevant experts outperform many unqualified respondents."
- **Talk-track:** Agile + eval pipeline · 3 groups ↔ 3 instruments · 100 Nielsen / 10 ISO /
  5 engineers · small N = Information Power, justified not lazy.
- **Transition:** "Here's what the analysis produced." *(same owner)*
- **If pressed:** 196 respondents earlier (needs assessment) vs 100 (final eval) — different
  phases, different N; don't conflate.

## S8 — Data Analysis: Evaluation Results  ·  TORRENO  ·  ~70 s

- **Setup:** results figures on screen; slow down — this is the statistical core.
- **Verbatim:** "Households averaged 4.73 on usability and 4.79 on the comparison against prior
  methods — on a five-point scale, both sit inside 'Strongly Agree.' The instrument itself is
  reliable: Cronbach's alpha measures whether items hang together — 0.923 on usability is
  excellent internal consistency, 0.868 on comparison is good; above 0.8 is the accepted bar. For
  significance, a one-sample t-test compares the mean against the neutral midpoint, 3.00 — and
  note what that tests: 'above neutral,' not 'better than some competitor.' t with 99 degrees of
  freedom — one less than our hundred respondents — comes to 55.47, p below .001: the odds of
  seeing this by accident are under a tenth of a percent. We reject the null. Separately: IT
  experts scored software quality 4.47 — 'Excellent' — while the engineers' technical assessment
  came to 3.27 — 'Satisfactory.' That gap is real, we report it plainly — their rubric is stricter
  and it produced the recommendations you'll see at the end."
- **Talk-track:** 4.73/4.79 Strongly Agree · α .923/.868 reliable · t(99)=55.47 p<.001 vs 3.00 →
  reject H0 · IT 4.47 Excellent / eng 3.27 Satisfactory — stricter rubric → recommendations.
- **Transition:** "The engine's own validation, next." *(same owner)*
- **If pressed:** (a) benchmark = neutral midpoint, not a competing system; (b) 4.46-vs-4.47 =
  appendix tabulation vs summary — rounding-level, same band; (c) why 3.27 is reported, not
  hidden.

## S9 — Recommendation Validation  ·  TORRENO  ·  ~50 s

- **Setup:** the 82.22% figure front and center.
- **Verbatim:** "How do you validate a recommendation engine when there's no labeled ground truth?
  You ask the experts. Five licensed engineers each gave their own independent pick for nine test
  locations — forty-five assessments; 'insufficient information' responses were excluded from the
  denominator, so forty-five is the *valid* count. In thirty-seven, the engineer's own
  recommendation matched LUMI's — 82.22%. That clears the eighty-percent bar the consensus
  literature sets for expert agreement. By source: solar and wind each agreed eighty-five percent
  of the time; hydropower, sixty — which is exactly why refining the hydro criteria sits in our
  recommendations. Geothermal shows N/A: it was never evaluated."
- **Talk-track:** 5 eng × 9 loc = 45 valid · 37 matched → 82.22% ≥ 80% consensus bar · solar/wind
  85%, hydro 60% → refinement · geo N/A.
- **Transition:** `[→ ALEX]` "And here's the machine that produces all of it — Alex."
- **If pressed:** *agreement with expert judgment* — never "accuracy"; the paper itself says so.

## S10 — System Architecture  ·  SOLIS  ·  ~45 s

- **Setup:** Alex steps forward; architecture diagram on screen.
- **Verbatim:** "One data spine feeds everything. On the input side: DOE statistics, NASA POWER
  climate data, terrain and GIS datasets, and location data — all ingested *offline* into our own
  database through ETL pipelines — plus the user's own inputs at runtime. Processing combines four
  engines: ARIMA forecasting, RAG-grounded LLM explanations, the physics-based renewable output
  formulas, and weighted suitability scoring. Outputs — recommendations, forecasts, plain-language
  summaries — surface through the two modules, EnergyHub and EcoSim. That offline-ingestion detail
  is why the system is fast: no external API gets called at request time — everything's already
  local — which is how the endpoint sweep averages about 104 milliseconds."
- **Talk-track:** inputs offline via ETL + runtime user input · 4 engines: ARIMA / RAG-LLM /
  physics formulas / weighted scoring · outputs → EnergyHub + EcoSim · offline → ~104 ms.
- **Transition:** "Let me walk the features." *(same owner)*
- **If pressed (technical):** FastAPI backend, React/Vite frontend, Supabase Postgres + RLS, Redis
  cache, Vercel serverless — full depth in `03-SYSTEM-DESIGN-AUDIT.md` §1–4.

## S11 — EnergyHub I  ·  SOLIS  ·  ~25 s

- **Setup:** national overview / provincial demand screen.
- **Verbatim:** "EnergyHub answers the national question first — what does the country's energy
  picture actually look like? National consumption, generation mix, provincial demand broken down
  by sector, renewable benchmarks. It's the context layer: before anyone simulates their own
  house, they can see where the country stands. And it doubles as transparency — the same dataset
  the forecasts are built on is what users see here, so nothing on this screen is a black box."
- **Talk-track:** national stats + provincial demand + benchmarks · context before personal ·
  same data as forecasts → transparent.
- **Transition:** "Same module, two more dimensions." *(same owner)*

## S12 — EnergyHub II  ·  SOLIS  ·  ~25 s

- **Setup:** potential map / forecast chart.
- **Verbatim:** "The second half is spatial and temporal. Interactive suitability maps resolve down
  to municipality granularity — solar, wind, hydro, geothermal, and a composite view — alongside
  the historical demand series with the ARIMA forecast layered on top, so users see both where the
  resource is and where demand is heading. Map scores stay deliberately simple — normalized
  factors, unweighted composite — a national map needs comparability; the heavier weighted logic
  lives in EcoSim."
- **Talk-track:** maps→municipality, 4 sources + composite · history + ARIMA overlay ·
  map scores simple by design; weighted logic in EcoSim.
- **Transition:** "Which brings me to the household layer." *(same owner)*

## S13 — EcoSim I  ·  SOLIS  ·  ~25 s

- **Setup:** EcoSim recommendation screen.
- **Verbatim:** "EcoSim is the personal layer. Pick a province or municipality, enter monthly
  consumption or your bill, and the engine ranks renewable options — each with a suitability score
  and an estimated monthly generation figure. The score is a weighted linear combination in the
  literature-standard style: roughly forty percent reflects raw resource quality at that spot, up
  to sixty percent scales with how much of *your* consumption the source can actually cover — so a
  world-class resource that covers nothing won't outrank a good one that covers your bill."
- **Talk-track:** location + consumption/bill in → ranked options out · score ≈ 40% resource +
  60% coverage-of-your-bill · proximity nudge capped.
- **Transition:** "Results don't stop at a number." *(same owner)*

## S14 — EcoSim II  ·  SOLIS  ·  ~25 s

- **Setup:** AI explanation modal / provider directory.
- **Verbatim:** "Every result can be explained in plain language by the AI assistant — and the
  division of labor matters: the numbers stay deterministic; the LLM only narrates them, grounded
  by retrieval over our own data. The provider directory — thirty-two verified entries built from
  the 2026 DOE registry — then connects users to real installers. Matching is provider-agnostic by
  design: we match on technology and region, never sponsorship."
- **Talk-track:** AI narrates, numbers stay deterministic (RAG-grounded) · 32 verified DOE-registry
  providers · matching = tech + region, never sponsorship.
- **Transition:** "And the flow deliberately ends here." *(same owner)*
- **If pressed:** provider list = `data/providers.json`; neutrality enforced in code.

## S15 — EcoSim III  ·  SOLIS  ·  ~25 s

- **Setup:** "Recommended Next Steps" screen.
- **Verbatim:** "We end the result flow with recommended next steps — including 'consult a licensed
  engineer' — because this is decision *support*, not a feasibility study. This screen is the scope
  limitation from earlier, made visible inside the product: permits, structural checks, an actual
  site survey — the system routes users to the right next action instead of pretending the
  assessment is finished."
- **Talk-track:** next steps incl. licensed engineer · limitation made visible in-product ·
  responsible routing, not a disclaimer of value.
- **Transition:** "Underneath the features — accounts." *(same owner)*
- **If pressed:** "is this responsible design?" — this slide *is* the answer.

## S16 — Authentication  ·  SOLIS  ·  ~25 s

- **Setup:** login/auth screens.
- **Verbatim:** "Accounts support email-and-password, Google sign-in, and TOTP two-factor
  authentication — time-based one-time passwords, the six-digit codes from an authenticator app.
  The backend verifies tokens against Supabase, and row-level security means a user can only ever
  touch their own data. Enrollment is guided — QR code plus manual secret — and unenrolling
  requires a current code, so nobody locks themselves out silently."
- **Talk-track:** email + Google + TOTP 2FA · Supabase verify + RLS · guided enroll, safe unenroll.
- **Transition:** "Those accounts power the last feature." *(same owner)*
- **If pressed:** Google + email + TOTP only — GitHub OAuth is **unverified** in code; do not
  claim it.

## S17 — Saved Simulations  ·  SOLIS  ·  ~20 s

- **Setup:** saved-simulations list.
- **Verbatim:** "Signed-in users can save simulations and revisit or delete them — every run
  auto-saves by default under a preference the user controls. Worth noting where that default came
  from: IT-expert feedback in the earlier evaluation rounds — the autosave toggle is literally an
  evaluator-driven change."
- **Talk-track:** save/revisit/delete · autosave default-on, user-controlled · origin = IT-expert
  feedback.
- **Transition:** "Now the numbers behind it all — results." *(same owner)*
- **If pressed:** autosave = migration 0023 + profiles toggle in SecuritySettings.

## S18 — Results: ML/AI Models  ·  SOLIS  ·  ~95 s

- **Setup:** model results on screen. **Deepest slide — don't rush it.**
- **Verbatim:** "Three engines, each earning a different kind of number. First, ARIMA(1,1,1) — and
  the name itself encodes the model: one autoregressive term — the forecast leans on the previous
  period's value; one differencing step — strips out trend; one moving-average term — smooths last
  period's error. It's the classic Box-Jenkins structure, chosen because national demand is
  steadily trending and predictable — and we verified the choice with an AIC configuration search plus a
  pilot bake-off against linear regression, Holt, and random forest. Now the three error metrics,
  because they answer different questions. MAPE — mean absolute *percentage* error — is 5.67% on
  held-out data the model never saw during fitting: on average the forecast misses actual national
  consumption by under six percent. The MAE is the same average miss in energy units — 6,829
  gigawatt-hours — which only sounds large because national consumption runs around a hundred
  thousand GWh a year; the percentage is the honest read. And RMSE at 8,257 squares the errors
  before averaging, so it punishes large misses — sitting above MAE, it tells you occasional bigger
  misses exist, and we disclose that rather than smooth it over. For context: Philippine
  forecasting studies have been volatile enough to miss the spot market's eighteen-percent MAPE
  threshold — 5.67% sits far under that reference. Now the generative AI — and these are two
  different latencies people conflate. About 7.1 seconds is a live model call — a full provider
  round-trip including retries. About 1.9 seconds is the cached or fallback path — the common case
  once content is warm. Neither contradicts the 104-millisecond API average — that's local
  endpoints with no LLM in the path. Three latencies, three different things being measured. And
  the MCDM engine — 82.22% expert agreement, which Lerrica covered at validation."
- **Talk-track:** ARIMA p,d,q decode → seasonal data · AIC + pilot bake-off · MAPE 5.67% held-out
  · MAE 6,829 GWh vs ~100k national scale · RMSE 8,257 > MAE = bigger misses exist, disclosed ·
  WESM 18% context · 7.1 s live / 1.9 s cached / 104 ms API — three different measurements ·
  MCDM 82.22%.
- **Transition:** "Testing, at the system level." *(same owner)*
- **If pressed:** (a) **never claim the champion model** — Linear, Holt, and Naive score *lower*
  MAPE on the held-out set; selection rests on the AIC search, the pilot bake-off, and
  interpretability — say exactly that. (b) Every number maps to a harness artifact + re-run
  command — mapped in `01` S18's *Evidence to justify it live* block; open those files before the
  panel.

## S19 — Results: System Testing  ·  SOLIS  ·  ~60 s

- **Setup:** testing summary on screen.
- **Verbatim:** "Four testing layers, and each number means something specific. First, 315
  automated tests pass across unit, backend, frontend, and integration suites — with two
  integration tests *skipped*, not failed: they need a pytest plugin the environment doesn't
  provide, and that's documented rather than hidden. Second, a scripted live sweep hit all 82
  mounted endpoints — valid requests plus negative cases — and all 82 returned their expected
  results: endpoint-level coverage, not just unit-level. Third, performance: about 104
  milliseconds average response locally *including real database queries* — fast because every
  dataset is pre-ingested — and a load test at a hundred concurrent users completed with no
  failures. Fourth, security: sixteen of eighteen live probes passed — a JWT matrix covering no
  token, malformed, alg:none, wrong signature, expired — plus security headers, CORS preflight,
  docs exposure, and error-body leakage. The two residuals were documented, fixed, and
  re-verified — not hidden."
- **Talk-track:** 315 pass + 2 env-skipped · 82/82 live sweep incl. negatives · ~104 ms w/ DB,
  100-user zero-fail · 16/18 probes, residuals documented+fixed.
- **Transition:** `[→ LERRICA]` "And how the independent evaluators scored it — Lerrica."
- **If pressed:** "are counts exact today?" → 315 is the documented defense-time aggregate;
  suite-by-suite reconciliation lives in `04-TESTING-AUDIT.md`; honest line: "we can re-run any of
  this live." Evidence block (sweep CSV, benchmark summary, locust stats, probes.json) in `01`
  S19.

## S20 — ISO/IEC 25010 Results  ·  TORRENO  ·  ~35 s

- **Setup:** Lerrica forward; characteristic chart on screen.
- **Verbatim:** "ISO/IEC 25010 rates software across eight quality characteristics — functional
  suitability, performance, compatibility, usability, reliability, security, maintainability, and
  flexibility. Compatibility scored highest at 4.65 — the system coexists cleanly with browsers,
  devices, and the surrounding stack. Flexibility scored lowest at 4.20 — still inside the
  Excellent band, but the relative weak spot: adaptability to varied scenarios and datasets. And
  that weakest score directly produced one of our recommendations — broadening datasets and
  scenario coverage."
- **Talk-track:** 8 characteristics · high = compatibility 4.65 · low = flexibility 4.20 (still
  Excellent) · weakest score → concrete recommendation.
- **Transition:** `[→ SEAN]` "Sean closes it out."
- **If pressed:** overall 4.47 vs 4.46 appendix — rounding-level, same band.

## S21 — Conclusion & Recommendations  ·  VIRATA  ·  ~55 s

- **Setup:** Sean forward; conclusion text visible.
- **Verbatim:** "The conclusion follows the evidence chain. We built a working platform that
  integrates recommendation, forecasting, and simulation. Households rated it favorably, IT
  experts rated it Excellent, and the engine agreed with engineering experts in thirty-seven of
  forty-five assessments. The honest reading — the one printed on our own slide — is that
  agreement supports *potential*, not production-readiness: the engineers' 3.27 and the weaker
  locations tell us further validation is needed. So our recommendations are ours first: refine
  the MCDM criteria — hydropower and the low-agreement locations; expand datasets, forecasting,
  hardware sizing, and simulation depth; and validate across more Philippine locations. That
  self-critical close is deliberate — criteria *should* evolve with expert input."
- **Talk-track:** built + evaluated chain · households favorable / IT Excellent / 37-45 agreement ·
  honest: supports potential, not production-ready · recs: criteria / datasets+sims / more
  locations · self-critique = rigor.
- **Transition:** "We also sketched a responsible path to sustainability." *(same owner)*
- **If pressed:** cite Tarife's expert-refined criteria as precedent — refinement is method
  continuation, not confession.

## S22 — Monetization  ·  VIRATA  ·  ~35 s

- **Setup:** monetization slide; its own caveat is on-screen — lean on it.
- **Verbatim:** "A freemium model is *proposed*: free basic assessments sustaining reach — with an
  advertising line — premium subscriptions for deeper simulations, and provider partnerships. The
  rollout is three phases: validate, launch prioritizing Metro Manila where the household
  preference data applies, then expand to MSMEs, institutions, and government. And the caveat is
  printed on the slide itself: these are proposals — willingness to pay and commercial feasibility
  are not yet validated. We present a path, not a proven business."
- **Talk-track:** freemium + ads + premium + provider partnerships · 3 phases (validate → Metro
  Manila → MSME/gov) · caveat printed: proposed, unvalidated.
- **Transition:** `[→ ALEX]` "Alex will show you the real thing."
- **If pressed:** never claim commercial viability — repeat the disclaimer verbatim.

## S23 — System Demonstration  ·  SOLIS  ·  2–4 min

*(Full choreography in §D below — driver, click path, wait-narrations, failure ladder.)*

- **Setup:** browser ready at `lumi-frontend-xi.vercel.app`, warmed endpoints.
- **Verbatim (segue):** "Let me show you the system itself."
- **If asked mid-demo:** latencies — local API ~104 ms; the AI explanation is the slow call by
  design (~7 s live, ~2 s cached). Say it before they notice.
- **Transition:** `[→ SEAN]` after last demo stop — "That's the system. Sean."

## S24 — Thank You / Q&A  ·  VIRATA  ·  ~10 s

- **Setup:** closing slide; all three forward-facing.
- **Verbatim:** "That's LUMI — cleaner energy, brighter tomorrow. Thank you. We're happy to take
  your questions."
- **Talk-track:** tagline · thanks · open floor.
- **Pause-filler (only if silence):** "The short version of everything you saw: a working platform,
  household-approved usability, ISO-Excellent software quality, and an engine that agrees with
  engineers most of the time — with the gaps named and the next steps scheduled."
- **Then:** Q&A protocol — §E.

---

## D. S23 — Demo choreography (SOLIS drives + narrates; others field interruptions)

**Pre-flight (before the panel enters):**
1. Hit `lumi-backend-ten.vercel.app/api/v1/health/detailed` — expect supabase/redis/rag_index ok.
2. Warm the caches: load Dashboard → pick a municipality → run one EcoSim end-to-end.
3. Tab order: app tab → `docs/09-Technical-Evaluation/artifacts/screenshots/` folder tab (backup
   B-01…B-17) → deck. Cold serverless first-hit is slow — warm it during setup, never mid-demo.

**Click path (~2–4 min):**
1. **Dashboard** — municipality picker → composite score card.
   Narrate: "every number here is a real dataset — nothing mocked."
2. **EnergyHub** — national overview → renewable-potential map → forecast chart → AI insight.
   Narrate: "municipality granularity, and the forecast is the held-out model you just saw."
3. **EcoSim** — 5-step wizard: location → consumption/bill → options → results cards →
   per-source explanation modal → provider matches → PDF export.
   Narrate at results: "watch the scores and the confidence labels — the system says when its own
   data is thin."
4. **AI explanation** — the slow call. Narrate *while it loads*: "this is a live model call — a
   full provider round-trip, about seven seconds; the cached path underneath answers in about
   two." Say it before the panel clocks the wait.
5. **(If time)** Login + Saved Simulations → autosave → security settings.

**Failure ladder:**
- Hiccup/slow → narrate the degradation ladder ("fallback path serves the cached analysis") —
  it's a feature, show it working.
- Demo dead → flip to B-01…B-17 evidence screenshots: "the run you're about to see is preserved
  evidence" — narrate endpoint sweep, load stats, probe results.
  `[USER INPUT NEEDED: caption each B-## so you can flip without hunting]`
- Total loss → "we'll take questions and the demo is available after" — straight to S24.

**Hard rules:** never improvise a feature that isn't in the build; never claim live numbers you
haven't verified that morning.

---

## E. Q&A protocol (starts after S24)

### Fielding map — who answers what

| Question territory | Lead |
|---|---|
| Methodology, instruments, stats, sampling, agreement rate | TORRENO |
| System, code, models, security, deployment, data pipelines | SOLIS |
| Scope, limitations, process, business, team/roles | VIRATA |

**The 3-beat answer:** direct answer → evidence → hand back. ~15 s per answer; if it needs more,
offer the appendix/park it for after. Never talk over each other — the lead answers, others add
only if invited or if they hold a critical correction.

### Trap questions — the one-liners that survive them

- **"Why t-test against 3.00, not another system?"** → The items measure *perceived* support vs
  prior methods; 3.00 is the neutral midpoint. It tests "above neutral" — exactly what the
  hypothesis claims. *(TORRENO)*
- **"Why is engineering 3.27 so much lower than IT 4.47?"** → Different instruments and stakes:
  ISO software quality vs professional technical dimensions — suitability, safety, reliability.
  We report both; it shaped the recommendations. *(TORRENO)*
- **"Is 82.22% good enough?"** → It clears the 80% consensus bar and supports potential — the
  deck's own conclusion says further validation remains necessary. Hydro's 60% drove the
  refinement recommendation. *(TORRENO)*
- **"Is 100 respondents enough?"** → It's the declared scope — CALABARZON, stated on the
  limitations slide; α .923/.868 confirms reliability within it. *(TORRENO)*
- **"Where did the MCDM weights come from?"** → AHP-derived/expert-judgment defaults shaped like
  Philippine GIS-AHP practice, stored tunable in `mcda_weights` with safe fallbacks. If pressed on
  pairwise matrices: none exist in the repo — say that plainly. `06e` §7. *(SOLIS)*
- **"Do all sources use the weight table?"** → No — only geothermal reads it at runtime;
  solar/wind/hydro score via output-normalized physics then the 0.4/0.6 composite. Documented
  defaults for the others exist but are dormant. `06e` §0. *(SOLIS)*
- **"Why ARIMA(1,1,1)?"** → AIC grid search + pilot bake-off vs linear/Holt/RF; held-out MAPE
  5.67%; deployed model refit on all data through 2025 → forecasts 2026–2030, plus a one-step
  2025 check within 3.2%. If pressed "not lowest-MAPE": correct — selection = AIC + pilot +
  interpretability + native prediction intervals. Full chart/model deep-dive → `08`. *(SOLIS)*
- **"104 ms API but 7 s AI — contradiction?"** → Three different measurements: local API vs live
  LLM call vs cached path. Honest latency by design. *(SOLIS)*
- **"GWh-scale MAE sounds terrible."** → National consumption is ~a hundred thousand GWh — MAPE
  5.67% is the normalized figure; we report both for exactly this reason. *(SOLIS)*
- **"Is it just a wrapper on APIs?"** → Third-party calls happen offline in ETL; runtime computes
  scoring, formulas, forecasting, retrieval itself. *(SOLIS)*
- **"What's NOT tested?"** → RLS direct probing, load beyond 100 users, barangay scoring, the
  dormant chat route — documented in `04` §7. *(SOLIS)*
- **"Security posture?"** → GoTrue + RLS, fail-closed auth, per-IP quotas, boundary validation;
  16/18 probes with residuals documented — never "fully secure." *(SOLIS)*
- **"Why FastAPI/React/Supabase?"** → Decision log `03` D1–D3 — boundary validation + Python
  ecosystem / mature SPA / managed Postgres+Auth+RLS. *(SOLIS)*
- **"How does the AI stay honest?"** → RAG over our own knowledge chunks → grounded prompts →
  sanitizer strips wrappers → cached outputs; the numbers stay deterministic. *(SOLIS)*
- **"Why should households trust the recommendation?"** → Three signals: expert agreement (82.22%),
  per-source confidence scores surfaced in-app, transparent criteria users can inspect.
  *(VIRATA/TORRENO)*
- **"GitHub login?"** → Not in the build — email/password + Google + TOTP only. *(SOLIS)*

### Appendix flips — when they ask for proof

Flip to the appendix slide *while answering*, narrate one line, flip back.

| If asked… | Flip to | Say |
|---|---|---|
| Evidence of field work / consultations | **S25** | "These are the barangay consultations and engineering sessions." `[USER INPUT NEEDED: who/which]` |
| How the household eval was administered | **S26** | "Respondents used the live system in supervised sessions." |
| The item-level ratings | **S27** | "The item-by-item ratings behind the 4.73/4.79 means." |
| The 4.47 ISO claim | **S28** | "The characteristic-level scores behind the 4.47." |
| The raw tabulation / the 4.46 | **S29** | "The raw item tabulation — the 4.46 vs 4.47 is presentation rounding, same band." |

### Recovery lines

- **Honest limitations, 30 s (memorize):** "LUMI is preliminary decision support. The household
  sample is CALABARZON, not national. The 82.22% figure is expert *agreement*, not accuracy — and
  hydropower at 60% needs work. Geothermal is reference-only. Security probes passed 16 of 18 with
  documented residuals. And our own recommendations list exactly what we'd strengthen next."
- **When you genuinely don't know:** "That's outside what we measured — here's what we did
  measure: …" — pivot to adjacent evidence; never bluff a number.
- **If Q&A drags/hostile:** "Happy to go deeper on this after the session — the full audit trail
  is in our documentation pack." — then back to the next question.

---

## F. Contingencies

**Running over time** (panel is checking watches — cut in this order):
1. S16+S17 collapse to one line: "Standard secure auth — Google, 2FA — with saveable simulations."
2. S4/S5 → name each SO + its figure, skip explanation: saves ~60 s.
3. S18 → headline metrics only: "5.67% held-out MAPE, three latencies by design, 82.22%
  agreement": saves ~40 s.
4. Drop every optional parenthetical. Total recovery ≈ 2.5 min.

**Running under time** (finish early — deploy in this order):
1. S3's perceived-vs-accuracy distinction.
2. S9's agreement-framing paragraph.
3. S18's WESM 18% context + "not the lowest-MAPE" honesty.
4. S20's weakest-score → recommendation link.

**Tech failure:** projector drops → keep talking from memory (talk-track); deck dies → flip to
backup laptop/PDF; demo dies → §D failure ladder. Never narrate the failure — narrate the
recovery.

**Memory lapse:** jump to that block's talk-track line — "the short version is…" beats silence;
the bullets carry the numbers.

**Absent presenter:** fold their block to the adjacent owner (see Presenters table); reassign
Q&A leads by territory, never ad-lib someone else's section cold.

**Hostile probing:** acknowledge → evidence → move on. "Fair challenge — here's what the data
actually shows…" Never argue, never inflate.

---

## G. Pre-stage checklist

- [ ] Endpoints warmed (`/api/v1/health/detailed` → all ok) + one EcoSim run completed pre-panel
- [ ] Tab order set: app → B-01…B-17 folder → deck PDF
- [ ] `01` S18/S19 evidence artifacts open on the laptop (CSV/JSON rows for "justify it live")
- [ ] Water; timing watch assigned (one presenter keeps clock)
- [ ] `[USER INPUT NEEDED]` items in §E appendix table filled from the deck beforehand
- [ ] Cheat numbers memorized (§Delivery rules strip above)

---

*Cross-references: slide guide `01` · claims/Q&A depth `05` · architecture `03` · testing
reconciliation `04` · MCDM weights `06e` · claim-to-code traceability `02`.*
