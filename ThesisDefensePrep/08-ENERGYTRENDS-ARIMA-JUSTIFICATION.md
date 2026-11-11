# 08 — EnergyTrends Charts & ARIMA Justification

> Deep-dive for defending the **Energy Trends** section of EnergyHub: the three line charts
> (Total Electricity Use, Peak Electricity Demand, Clean Energy Generation) and the ARIMA(1,1,1)
> forecasts drawn on them. Contains the chart anatomy, the data pipeline, the model rationale,
> the honest evaluation story, a per-chart talk-track, a hostile-question bank, and a
> paste-ready methodology appendix.
>
> Cross-links: slides → `01`, code → `02`/`06a`/`06c`, architecture → `03`, tests → `04`,
> catch-all Q&A → `05`, script → `07`.

**Reading order for the defense:** §3 (pipeline) → §5 (why ARIMA) → §6 (honest numbers) →
§7 (why ARIMA anyway) → §8 (talk-track) → §9 (Q&A bank). §10 is for the paper.

---

## 1. What changed pre-defense (read this first)

The forecast artifacts were **regenerated before the final defense**:

- The earlier `forecast_*_2025_2030.csv` files were produced by a model fitted **only on
  2003–2020 data** (the evaluation configuration). They were, in effect, the model's 2021–2026
  out-of-sample predictions relabeled 2025–2030, which is why the dashed line visibly dipped
  below the last historical point once 2021–2025 actuals were added to the chart.
- The shipped forecast is now produced by an ARIMA(1,1,1) **refit on the full 2003–2025
  series**, forecasting **2026–2030** — the standard "validate on holdout, deploy refit on
  all data" workflow. The evaluation protocol (and every reported metric) is unchanged.
- The `/model-comparison` endpoint now serves the **canonical** evaluation table from
  `docs/09-Technical-Evaluation/artifacts/rerun-2026-09-15/ml/` instead of the notebook's
  illustrative numbers.

If a panelist has seen an older build or screenshot where the forecast dips — own it:
*"That artifact was generated under our evaluation configuration rather than a deployment
refit; we regenerated it before the final defense so the forecast uses every available
observation. The evaluation numbers in the paper are unchanged."*
(Full mechanics + rehearsed answer → **§15, Anatomy of the dipped forecast**.)

> **Ops note:** `EnergyHubML` loads the forecast CSVs **once at backend startup**. A running
> server keeps serving the old artifact until restart — if the chart on screen still dips,
> the backend was started before the regenerated CSVs landed. Restart it (or redeploy) before
> demoing.

---

## 2. What the panel sees — chart anatomy

`react-frontend/src/components/energyhub/EnergyTrends.jsx` (435 ln) renders one card
("Energy Trends") containing three charts plus a Historical/Forecast legend:

| Chart | Series | Unit | Source column in `master_preprocessed.csv` |
|---|---|---|---|
| Total Electricity Use Over Time | `total_consumption_gwh` | GWh | DOE national electricity consumption |
| Peak Electricity Demand | `total_peak_demand_mw` | MW | DOE summed grid peak demand |
| Clean Energy Generation | `renewable_generation_gwh` | GWh | DOE geothermal+hydro+biomass+solar+wind |

Per-chart elements the panel may ask about:

- **Solid line = historical** (2003–2025, 23 points, DOE actuals). **Dashed red line = forecast**
  (2026–2030, 5 points, ARIMA(1,1,1) mean). The dashed series is drawn starting from the last
  historical point ("junction point", `EnergyTrends.jsx` ~L128) so the lines connect — a
  deliberate continuity convention, not a data point.
- **"What / Why it matters / What to do" explainer card** above each chart
  (`ChartExplanation.jsx`, strings in `i18n/en.json` L798–824) — household-readable framing;
  the "What" text says "forecast through 2030".
- **AI Analyze / Refresh button** (`ChartAiPanel`) — posts chart JSON to
  `/api/v1/energyhub/ai-insight`, LLM output sanitized client-side (`sanitizeLLMOutput`).
- **Enlarge icon** — opens the same traces in a Dialog modal.
- **Units:** GWh = energy over a year (volume); MW = instantaneous capacity (peak power).
  Be ready to explain the difference — it's a classic panel question.
- **What is NOT rendered:** the 95% confidence intervals. The API serves `ci_lower`/`ci_upper`
  for every forecast point (`predictor.py:get_forecast`); the UI chooses not to draw them.
  If asked "where is the uncertainty?": *"The intervals are computed and served — we chose a
  cleaner visualization for households; the widening-interval analysis is in the paper."*

## 3. Data provenance — the full chain, citable

```
DOE Philippine energy statistics (annual, 2003–2025)
  └─ python_scripts/prepare_national_energy_csv.py (+ data_v2_preprocessing.py)
      └─ data/DOE_Data_Extracted/data_v2_preprocessed/master_preprocessed.csv   (23 rows)
          └─ data/DOE_Data_Extracted/notebooks/EnergyTrends_ARIMA_Forecast.ipynb
              ├─ evaluation: train 2003–2020 / test 2021–2024  → evaluation_*_2021_2024.csv
              └─ deployment: refit on 2003–2025 → forecast_*_2026_2030.csv (mean + 95% CI)
                  └─ fastapi-backend/app/ml/predictor.py  (EnergyHubML._load_all, ~L115–136)
                      │    · bundled CSV preferred (use_local_data_fallback=True, settings.py L208)
                      │    · fallback: public.doe_datasets in Supabase
                      └─ app/services/energyhub.py::build_trends (L241–253)
                          └─ GET /api/v1/energyhub/trends   (routes/energyhub.py L55–60)
                              └─ react-frontend/src/pages/EnergyHub.jsx → EnergyTrends.jsx
```

Adjacent forecast surfaces (know they exist):

- `GET /api/v1/energyhub/forecast?metric=` — the same precomputed forecast + metadata
  (`model: "ARIMA(1,1,1)"`, `training_period: "2003-2025"`, `test_period: "2021-2024"`).
- `GET /api/v1/energyhub/model-comparison?metric=` — canonical held-out metrics per series.
- `GET /api/v1/forecast/run`, `/forecast/backtest`, `/forecast/models` — **premium-gated**
  live SARIMA path via `services/forecasting.py` (walk-forward backtest + model registry
  `forecast_model_runs`). Distinct from the precomputed pipeline; exists for extensibility.
- `EnergyOverview` card: "2030 demand outlook" shows `forecast_growth_pct` =
  (2030 forecast ÷ latest actual − 1). With the refit: **+13.05%** (142,877 vs 126,378).

**No runtime third-party calls** — every number on the chart is served from bundled,
versioned CSV artifacts. That's why the endpoint is fast and reproducible.

## 4. Why a line chart (if asked)

- The data is a continuous annual time series — lines encode continuity and trend better
  than bars; 23 points is too few for any fancier encoding to earn its complexity.
- Solid vs. dashed distinguishes **measured** from **modeled** without a second chart;
  the junction convention keeps the eye moving across the boundary.
- Same encoding across all three charts = consistent mental model, matching the
  household-usability design goals (clarity of charts scored **4.70/5**).

## 5. The model, in plain English

**ARIMA(p,d,q) = Autoregressive Integrated Moving Average.**

- **d=1 — "Integrated":** we model the *year-over-year change*, not the level. The series
  trends upward (non-stationary); differencing once makes it workable.
- **p=1 — "Autoregressive":** this year's *change* depends partly on last year's change —
  momentum exists in the system (electrification, industrial growth persist).
- **q=1 — "Moving Average":** this year's *change* also corrects for last year's surprise —
  shocks (e.g. the 2020 COVID demand drop) decay rather than persist forever.

So ARIMA(1,1,1) reads: *"next year's consumption grows by a momentum-plus-correction of
last year's growth."* That is a defensible model of a national demand series.

**Why (1,1,1) specifically:** an AIC grid search over 9 candidate orders picked (1,1,1)
with the lowest AIC (**325.63**; runner-up (2,1,1) at 327.47) —
`docs/09-Technical-Evaluation/artifacts/rerun-2026-09-15/ml/aic_grid.csv`.
Crucially, the order was selected **before** test-set evaluation — selection hygiene:
we did not shop for the order that flattered the holdout.

**Why classical statistics, not ML:** 23 annual observations is far too few for LSTM/RF/
XGBoost to learn anything but noise — the pilot bake-off confirms it (RF: 10.94% MAPE on
consumption, worst-but-one). Literature anchor: Krishnan et al. (2024) uses ARIMA for
energy-demand forecasting; classical models remain standard for short annual series.

**Why annual, not seasonal/SARIMA:** the data is annual — there is no within-year
seasonal period to model (s=1 is degenerate). Seasonality would require monthly/quarterly
DOE data we deliberately scoped out.

## 6. Honest evaluation numbers — memorize this table

Protocol (unchanged, as reported): **train 2003–2020, test 2021–2024**, six models,
canonical artifacts `rerun-2026-09-15/ml/model_metrics_*.csv`.

| Model | Consumption MAPE | Peak MAPE | Renewable MAPE |
|---|---|---|---|
| Linear Trend Regression | **4.965** | 6.562 | **9.405** |
| Naive with Drift | 5.566 | 5.482 | 13.106 |
| Holt Linear Smoothing | 5.435 | 5.482 | **9.405** |
| **ARIMA(1,1,1)** | **5.667** | **5.611** | **13.665** |
| SARIMAX(1,1,1) + Exog | 14.031 | **3.868** | 21.285 |
| Random Forest | 10.937 | 11.776 | 13.646 |

ARIMA absolute errors: MAE **6,829.09 GWh** / RMSE **8,257.12 GWh** (consumption),
**1,019.66 MW** / **1,299.08 MW** (peak), **3,597.39 GWh** / **3,939.69 GWh** (renewable).
RMSE exceeds MAE by 20.9%/27.4%/9.5% — errors on consumption and peak were dominated by
one hard year (the 2024 demand surge, which **every** model under-predicted:
ARIMA −10.94%, Linear −9.85% on 2024 consumption).

Supporting evidence:

- **Direction-of-change accuracy: 8/11 test years = 72.7% — best of all six models.**
  For decision support, "will it go up or down next year" matters more than the decimal.
- **Expanding-window CV (7 folds, consumption):** ARIMA mean |error| 3.61% — within
  0.1 pp of Naive (3.58) and Holt (3.53) — with the **lowest fold-to-fold std (2.51)**;
  the most stable model across training windows.
- **Diebold–Mariano test vs Linear Trend:** stat 3.532, p≈0.0004, **but n=4** — the
  artifact itself says "essentially no power; reported for completeness." Use it only to
  show we ran the formal test and disclosed its weakness.
- **New — 2025 one-step check** (added pre-defense): a ≤2024-trained ARIMA predicts
  2025 within **3.20%** (consumption), **3.00%** (peak), **11.25%** (renewable) of the
  actuals — a fresh pseudo-out-of-sample point on the newest year, consistent with the
  holdout MAPEs.

## 7. Why ARIMA was retained despite not winning every MAPE

This is the question the panel *will* ask. The answer, in order:

1. **Selection was done a-priori.** (1,1,1) came out of an AIC grid search *before* test
   evaluation — we did not cherry-pick on test error.
2. **The gap is statistically indistinguishable.** On consumption ARIMA trails the best
   model by 0.7 pp **on a 4-point holdout** — with n=4, no test has the power to call that
   a real difference; our own DM test says so explicitly.
3. **ARIMA wins on the metrics that matter for this product:** best direction-of-change
   (72.7%) and the most stable cross-validated error (lowest CV std).
4. **It produces native prediction intervals** — the `ci_lower`/`ci_upper` we serve —
   which a deterministic linear extrapolation does not give you out of the box.
5. **It was *not* the best on every series, and we say so.** SARIMAX won peak demand
   (3.868%) but requires exogenous regressors — you cannot produce an unconditional
   5-year forecast from a model whose forecasts depend on inputs you'd have to forecast
   too — and it was worst on the other two series (14.0%, 21.3%). One consistent,
   interpretable model family across all three series is a defensible engineering choice.
6. **The paper now says exactly this** — "competitive… though not achieving the lowest
   error on every target," retained for diagnostic adequacy, native intervals, and
   direction accuracy (see `docs/table-3.47-revisions.md`).

## 8. Per-chart talk-track (verbatim, ~60–90 s each)

### 8.1 Total Electricity Use Over Time

> "The solid line is 23 years of official DOE electricity-consumption data — from about
> 52,900 gigawatt-hours in 2003 to 126,378 in 2025, a 139 percent increase. The dashed
> line is the ARIMA forecast: the model was validated on a held-out 2021-to-2024 window,
> then refit on all the data and projects roughly 143,000 gigawatt-hours by 2030 —
> about 13 percent above today. Notice the forecast continues the recent acceleration —
> it saw the post-2021 industrial-demand surge. For households, this is the 'why' behind
> the app: rising demand means rising prices and more strain, and that's the demand
> clean energy has to meet."

Point at: the 2020 dip (COVID), the 2024 acceleration, the dashed continuation.

### 8.2 Peak Electricity Demand

> "Same data, different question: not how much energy per year, but the single highest
> moment of demand — what the grid must be sized for. Peaks went from about 8,300
> megawatts in 2003 to 19,212 in 2025, and the model projects roughly 21,600 by 2030.
> This is the chart that says why distributed solar and storage matter at the municipal
> level — every megawatt of local generation is a megawatt of peak relief."

If pressed on SARIMAX winning this series: see §7.5 — rehearsed answer ready.

### 8.3 Clean Energy Generation

> "This one requires honesty. Clean generation nearly doubled — about 17,700 gigawatt-hours
> in 2003 to 31,647 in 2025 — but because *total* demand grew even faster, the renewable
> *share* actually fell from 33 percent to 25 percent. The recent slope is encouraging —
> solar alone went from 1,400 to 4,800 gigawatt-hours in two years — and the forecast is
> deliberately cautious: roughly flat at 32,000 with a wide interval. The model is telling
> you this series is volatile and policy-driven; a mechanical model won't promise a surge.
> For the household that's actually the right message: the gap to the 35-percent-by-2030
> target is the opportunity."

### Transition out of the section

> "All three forecasts come from the same model family — ARIMA(1,1,1) — selected by an AIC
> grid search, validated on held-out years, and refit on the full series. Happy to walk
> through the model comparison table."

## 9. Hostile-question bank

**Q: "Why ARIMA and not LSTM/Prophet/XGBoost?"**
A: 23 annual observations — deep or highly-parameterized models overfit; our own Random
Forest proof: 10.9% MAPE, among the worst. Classical statistical models are the standard
choice for short annual series (Krishnan et al. 2024 uses ARIMA for energy demand).
Prophet adds trend+seasonality machinery for series that have neither the length nor the
seasonal period to benefit.

**Q: "Linear Trend beat ARIMA on consumption. Why didn't you ship it?"**
A: Full answer in §7. Short version: AIC-first selection, a 0.7-pp gap on a 4-point
holdout isn't statistically meaningful, ARIMA won direction-of-change and CV stability,
and it natively produces the prediction intervals we serve.

**Q: "SARIMAX won on peak demand — 3.868%. Why not use it?"**
A: SARIMAX+Exog forecasts conditional on exogenous regressors — you'd need a forecast of
the regressors themselves to get a 5-year path, which circularizes the problem. It was
also the worst model on the other two series (14.0% and 21.3%). One consistent family,
one honest story.

**Q: "13.7% MAPE on renewables is bad."**
A: It is the weakest series — we report it rather than hide it. The series carries a
structural break (solar output roughly tripled in two years); no univariate annual model
captures that. The wide confidence interval is the model *saying* it's uncertain — which
is more honest than a confident wrong line.

**Q: "Your forecast used to dip below the last actual — explain that."**
A: (§15 has the full three-layer anatomy + the verbatim.) Earlier artifacts were generated
under the evaluation configuration — a model trained only through 2020 whose output rows were
mislabeled 2025–2030, so the chart plotted its *2021–2026* predictions against 2021–2025
actuals (~17% low on consumption). Superseded by a full-data refit pre-defense.

**Q: "The confidence interval is enormous by 2030 — useless?"**
A: ±10% around the 2030 mean is honest uncertainty for a 23-observation annual series
five steps out. Intervals that stayed tight would be the suspicious output. The interval
is part of the product — we present a range, not a false-precision point.

**Q: "Four test years proves nothing."**
A: Correct — which is why model order was chosen by AIC *before* the holdout, why we ran
7-fold expanding-window CV, why we tracked direction-of-change, and why we added a 2025
one-step check (3.2% consumption error). The holdout is one evidence line among several.

**Q: "What is differencing / why d=1?"**
A: §5. The level trends; we model the change. If asked about d=2: the AIC grid tried
nearby orders including heavier differencing-adjacent structures; (1,1,1) minimized AIC.

**Q: "6,829 GWh error sounds enormous."**
A: National demand is ~126,000 GWh — that's 5.67% (MAPE). That's exactly why we report
both absolute and relative error.

**Q: "Did you check residuals / diagnostics?"**
A: Order selection on AIC, residual diagnostics and fit checks in the evaluation run
(`rerun-2026-09-15/ml/`), and honest limitations: on peak demand the AR estimate sits on
the stationarity boundary (statsmodels emits a convergence notice and returns the
constrained optimum — the forecast is a conservative trend extrapolation).

**Q: "Why does the renewable forecast go flat?"**
A: The model sees a volatile, mean-reverting differenced series — the honest mechanical
answer is 'high uncertainty around the current level,' not a promised surge. The recent
solar-driven growth is real; whether it compounds is a policy question, not a time-series
question, and the wide interval says exactly that.

**Q: "No seasonality? Demand is seasonal."**
A: Within-year seasonality exists in monthly data; our series is annual totals/peaks —
there is no seasonal period to model at this resolution.

**Q: "How do households use a possibly-wrong forecast?"**
A: It's context, not a billing calculation — the charts answer "is demand going up, and
roughly how fast," which is why direction-of-change accuracy (72.7%) and intervals matter
more than the point estimate. All decision-support claims stay in 'preliminary' language.

**Q: "What if 2030 is way off?"**
A: Then the interval was the honest statement of that possibility — that's what
probabilistic forecasting is for. The model is refit as new DOE data lands; the pipeline
(notebook → CSV → API) is reproducible end-to-end.

**Q: "Why is the forecast only 5 years?"**
A: Two reasons: beyond ~5 steps the interval is wider than the signal for this series
length, and 2030 is the policy-relevant horizon (the NREP renewable-share targets the app
references). A 10-year ARIMA forecast would be decoration, not information.

**Q: "Show me where the numbers come from, live."**
A: `GET /api/v1/energyhub/trends` → historical `series` + `forecast*` objects; then
`/model-comparison?metric=consumption` for the evaluation table; then open
`data/DOE_Data_Extracted/data_v2_preprocessed/forecast_consumption_2026_2030.csv`.

## 10. Methodology appendix — paste-ready prose for the thesis

> **Forecasting pipeline.** National energy statistics published by the Department of
> Energy (2003–2025, 23 annual observations) were preprocessed into a master table
> containing three target series: total electricity consumption (GWh), total peak demand
> (MW), and renewable generation (GWh). Model candidates were evaluated under a fixed
> holdout protocol — training on 2003–2020 and testing on 2021–2024 — using MAE, RMSE,
> and MAPE. The ARIMA order was selected by an AIC grid search over nine candidate
> specifications prior to test evaluation; ARIMA(1,1,1) attained the lowest AIC (325.63).
>
> **Model evaluation.** In the six-model comparison, ARIMA(1,1,1) produced competitive
> held-out errors — 5.667% MAPE on consumption, 5.611% on peak demand, and 13.665% on
> renewable generation — within about one percentage point of the best-performing model
> on the headline consumption series, though not the lowest error on every target. ARIMA
> achieved the best direction-of-change accuracy (72.7% of test years) and the most
> stable error across expanding-window cross-validation folds (lowest standard
> deviation, 2.51 pp). It was retained for the deployment forecast on the basis of its
> diagnostic adequacy, native prediction intervals, direction accuracy, and consistency
> across the three series; a Diebold–Mariano comparison against the best baseline was
> computed but carries essentially no statistical power at n=4 and is reported for
> completeness only.
>
> **Deployment.** Following standard practice, the validated model specification was
> refit on the complete 2003–2025 series to produce the deployed forecast for
> 2026–2030 with 95% prediction intervals. A supplementary one-step check — a model
> trained through 2024 predicting 2025 — yielded errors of 3.20% (consumption), 3.00%
> (peak demand), and 11.25% (renewable generation) against the actual 2025 observations,
> consistent with the holdout results. All forecasts are precomputed artifacts served
> from versioned data files; no model retraining occurs at request time.
>
> **Limitations.** The forecast is a univariate statistical extrapolation: it does not
> model policy changes, price effects, or structural breaks (the 2024 demand surge was
> under-predicted by every evaluated model). Renewable generation is the least
> predictable series (13.7% holdout MAPE) because it is driven by capacity additions and
> policy rather than inertia alone; the model expresses this through wider intervals.
> Forecasts are preliminary decision-support context, not planning-grade projections.

## 11. Say / never-say — forecasting-specific additions

| Never say | Say instead |
|---|---|
| "Our model is the most accurate" | "Competitive — within ~1 pp of the best on the headline target, best on direction-of-change, most stable in CV" |
| "The model predicts 143 TWh in 2030" | "The model estimates ~142.9 TWh in 2030, within a 95% interval of ~129–157 TWh" |
| "The model was validated" | "Evaluated on a 2021–2024 holdout, 7-fold CV, plus a one-step check on 2025" |
| "SARIMAX/Linear results were close enough" | "We report per-series winners honestly; we chose one consistent, interpretable family" |
| "The forecast is the future demand" | "A statistically grounded extrapolation with uncertainty — preliminary context" |
| "ARIMA converged cleanly everywhere" | "Peak-demand fit hits the AR boundary; documented, output verified sane" |

## 12. Discrepancy watchlist — forecasting items

| # | Item | Facts | Rehearsed answer |
|---|---|---|---|
| F1 | Superseded forecast files | `forecast_*_2025_2030.csv` still exist in `data_v1/` + `data_v2_preprocessed/` (mislabeled ≤2020-model output) | "Superseded by the 2026–2030 refit; retained for provenance. The API loads only the `2026_2030` files." |
| F2 | Two comparison tables exist | Notebook `evaluation_*.csv` (4 models, Holt 5.136) vs canonical `model_metrics_*` (6 models, Holt 5.435) | "The served `/model-comparison` table is canonical; the notebook's is illustrative and says so." |
| F3 | Peak convergence notice | `ARIMA(1,1,1)` on peak hits AR≈1.0 boundary; ConvergenceWarning | "Constrained optimum; output verified sane; documented in the notebook markdown." |
| F4 | Renewable was missing from migrate list | `forecast_renewable_generation_*.csv` wasn't in `migrate_csv_to_supabase.py` DOE_CSVS | Fixed — now included for v1+v2. |
| F5 | `/forecast/run` start year | Was hardcoded 2025 even after 2025 actuals landed | Fixed — now derived from `max(year)+1`. |
| F6 | Old screenshots / recordings | Any captured demo showing the dipping forecast | Retake; if shown, use the §1 ownership answer. |
| F7 | `forecast_2030_gwh` key name | API field name says 2030 — still correct (horizon ends 2030) | Non-issue; noted for completeness. |

## 13. Re-derivation checklist (reproduce everything in ~15 min)

1. `py -3` env with `statsmodels`, `pandas`, `numpy` installed.
2. Open `data/DOE_Data_Extracted/notebooks/EnergyTrends_ARIMA_Forecast.ipynb`; run all —
   reproduces `evaluation_*_2021_2024.csv`, `forecast_*_2026_2030.csv` (v2+v1), and the
   one-step-check numbers.
3. `Get-Content data/DOE_Data_Extracted/data_v2_preprocessed/forecast_*_2026_2030.csv` —
   expect years 2026–2030, `ci_lower ≤ mean ≤ ci_upper`.
4. Start backend (`uvicorn main:app --port 8000 --app-dir fastapi-backend`), then:
   - `GET /api/v1/energyhub/trends` → `forecast_years` = [2026…2030],
     `training_period` = "2003-2025", `test_period` = "2021-2024"
   - `GET /api/v1/energyhub/model-comparison?metric=consumption` → matches
     `model_metrics_consumption.csv` to the digit
   - `GET /api/v1/energyhub/forecast?metric=peak_demand` → same numbers as the CSV
5. Load EnergyHub → Energy Trends: dashed line continues **upward** from the last green
   point on all three charts (no dip); "2030 demand outlook" on the overview shows
   ≈ **+13.05%**.
6. Canonical artifacts (unchanged): `docs/09-Technical-Evaluation/artifacts/
   rerun-2026-09-15/ml/{aic_grid,model_metrics_*,cv_*,dm_test,forecast_vs_actual}.*`

## 14. Numbers crib (memorize)

- Series: **52,941 → 126,378 GWh** (+138.7%) · **8,275 → 19,212 MW** · **17,692 →
  31,647 GWh** renewable; renewable share 33.4% → **25.0%**
- AIC: **(1,1,1) = 325.63**, lowest of 9
- Holdout MAPE: **5.667 / 5.611 / 13.665**; best-on-series: Linear 4.965, SARIMAX 3.868,
  Linear+Holt 9.405
- MAE: **6,829.09 GWh / 1,019.66 MW / 3,597.39 GWh**; RMSE **8,257.12 / 1,299.08 / 3,939.69**
- Direction-of-change: **72.7%** (8/11) — best · CV: mean **3.61%**, lowest std **2.51**
- 2025 one-step: **3.20% / 3.00% / 11.25%**
- Deployed 2030: **142,877 GWh** (+13.05% vs 2025) · **21,648 MW** · **32,226 GWh**
  (CI 2030: 128,724–157,030 / 19,357–23,939 / 25,363–39,088)
- The dip, quantified (old artifact — first dashed point vs last actual):
  consumption **−17.3%** (104,580 vs 126,378) · peak **−18.4%** (15,685 vs 19,212) ·
  renewable **−31.2%** (21,781 vs 31,647)

---

## 15. Anatomy of the dipped forecast — why the old line dropped

*This section exists because the panel may have seen the older build (or a screenshot) where
the dashed forecast starts visibly **below** the last green point. Know this cold — it is the
single most "gotcha"-shaped question available on these charts, and it has a complete,
honest, mechanical answer.*

### 15.1 What the screenshot actually shows

| Chart | Last actual (2025) | First dashed point ("2025" label) | Gap |
|---|---|---|---|
| Total Electricity Use | 126,378 GWh | 104,580 GWh | **−17.3%** |
| Peak Electricity Demand | 19,212 MW | 15,685 MW | **−18.4%** |
| Clean Energy Generation | 31,647 GWh | 21,781 GWh | **−31.2%** |

The dashed line then climbs gently toward ~118,696 GWh / ~17,700 MW / ~22,638 GWh by "2030" —
below today's actuals the whole way. The chart was not showing a pessimistic future; it was
showing a stale prediction wearing the wrong year labels.

### 15.2 Layer 1 — the generator bug (mislabeled years)

`train_and_forecast_series` in `data/DOE_Data_Extracted/data_v2_preprocessing.py` (mirrored
in the notebook) did this:

```python
train = df[df["year"] <= 2020][target_col]          # evaluation window only
model = ARIMA(train, order=(1, 1, 1)).fit()
fcast = model.get_forecast(steps=6)                 # predictions for 2021–2026
forecast_years = list(range(2025, 2031))            # ...but labeled 2025–2030
```

The year labels were **hand-assigned**, not derived from the series' actual end. So the row
marked `2025` contained the model's **step-1 prediction for 2021**, the row marked `2026`
held its 2022 prediction, and so on. Verified forensically: the old CSV's "2025–2028"
values (104,579.74 / 107,403.30 / 110,226.69 / 113,049.90) are bit-for-bit identical to the
held-out 2021–2024 predictions recorded in
`docs/09-Technical-Evaluation/artifacts/rerun-2026-09-15/ml/forecast_vs_actual.csv`.

### 15.3 Layer 2 — the statistical reason the values were low

Even ignoring the labels, the ≤2020 model could only produce low numbers:

- Its forecast is **anchored to the end of its training window — 2020**, when consumption
  was **101,756 GWh, a COVID-depressed year (−4.0% vs 2019)**. Every forward step starts
  from that floor.
- ARIMA(1,1,1) extrapolates the **average drift** of its training period (≈+2,600 GWh/yr
  over 2003–2020). It has no mechanism to anticipate the **post-2021 demand acceleration**:
  +4.3% (2021), +5.1% (2022), +5.8% (2023), **+7.6% (2024)** — industrial recovery and
  electrification pushing consumption to 126,941 by 2024.
- Result: its 2021–2026 path (104.6k → 118.7k) was *reasonable as an extrapolation from
  2020* — and already obsolete the moment 2021 actuals (106,115) exceeded it. Every
  evaluated model under-predicted 2024 for the same reason (ARIMA −10.94%, Linear −9.85%):
  the surge was structural, not statistical noise.
- The renewable gap is the largest (−31.2%) because the **2024–2025 solar inflection**
  (solar alone ~3.4× in two years) was entirely outside the training window.

### 15.4 Layer 3 — the process reason it persisted

- Forecasts are **precomputed CSV artifacts** — deliberately, for speed and
  reproducibility ("no runtime retraining"). There was no regeneration step wired to the
  ingestion of new DOE years, so when `master_preprocessed.csv` was extended through 2025,
  the historical line grew while the forecast line stayed frozen in the ≤2020 world.
- `EnergyHubML` loads the CSVs **once at backend startup** — a running server keeps
  serving whatever artifact was on disk when it booted, which is why old numbers can
  persist on screen even after the files are fixed.

### 15.5 Why it went unnoticed

The artifact predated the newest data, and the junction gap grew as each actual year was
appended. When the series ended at 2021–2022 (106,115 / 111,516 GWh), the first dashed point
(104,580) sat only ~1.5–6% below the last actual — easy to read as a mild, conservative
step. Once 2023 (118,004), 2024 (126,941), and 2025 (126,378) landed, the same point became
an unmistakable ~11–17% cliff. The bug was always there; the widening data is what exposed it.

### 15.6 The fix, and why it cannot recur

- Deployment fit now uses the **full series** (2003–2025) → forecast **2026–2030**
  (consumption 129,678 → 142,877; peak 19,699 → 21,648; renewable 32,506 → 32,226).
- Forecast years are now **derived from the data** (`max(year) + 1..+5`) in both the
  notebook and `data_v2_preprocessing.py`, and `/forecast/run` derives its start year the
  same way — the label can no longer drift from the data.
- Filenames now encode the true horizon (`forecast_*_2026_2030.csv`) so a stale artifact
  can't masquerade as a current one.
- Old `forecast_*_2025_2030.csv` files are retained as superseded provenance (watchlist F1).

### 15.7 Rehearsed answers

**Verbatim (~45 s):**
> "Fair catch — that screenshot shows a pipeline artifact we found and corrected before the
> final defense. That forecast CSV was produced under our *evaluation* configuration — a
> model trained only through 2020 — and its output rows were labeled 2025 through 2030, so
> what appeared as 'the 2025 forecast' was actually the model's prediction for 2021. Since
> that model had never seen the post-2021 demand surge — which was 7.6 percent in 2024
> alone — its path naturally sat below the actuals, about seventeen percent low on
> consumption. We regenerated the artifact the textbook way: the validated ARIMA(1,1,1)
> refit on the complete 2003–2025 series, forecasting 2026 to 2030. The chart now continues
> smoothly from the last actual, and the evaluation numbers in the paper — the 5.67 percent
> held-out MAPE — are unaffected; this was a deployment-artifact issue, not a
> model-accuracy issue."

**Short version (~15 s):**
> "That was a labeling bug in a precomputed artifact — a 2020-trained model's 2021–2026
> predictions written as 2025–2030. Fixed by refitting on all data through 2025; the
> evaluation numbers are unchanged."

**If pressed "why didn't the model see the surge?":**
> "A univariate ARIMA extrapolates average drift from its training window — a structural
> acceleration after that window is invisible to any univariate model. That's also why all
> six evaluated models under-predicted 2024, by −9.9% to −22.8%. It's a stated limitation
> of the method, which is why the deployed model is refit as new DOE data lands."

**If pressed "why did it take so long to catch?":**
> "The artifact predated the newest data by construction; the gap only became visible as
> fresh actuals were appended to the historical series. Once it surfaced we fixed it at the
> generator, not just the file — forecast years are now derived from the data itself."
