# Prompt for SWE-2 High: EcoSim + EnergyHub Layman Explainer

Copy everything below the horizontal rule and paste it into a new SWE-2 High session inside this repository (`Lumi`). It will produce a plain-English document explaining every formula, decision matrix, data-processing step, and AI component behind EcoSim and EnergyHub.

---

## Role and audience

You are SWE-2 High working in the Lumi repository. You are writing a reference document for the LUMI development team. They will use it to explain the system to thesis panelists and to people they consult about the system. The readers are smart but are not programmers. Every explanation must make sense to someone who has never read the code.

## Your task

Create one new file:

`docs/04-ML-Data-Science/ECOSIM_ENERGYHUB_LAYMAN_GUIDE.md`

(If the user asks for a different path or filename, use theirs instead.)

The document must list and explain every formula, decision matrix, data-processing step, piece of math, and AI/ML component that EcoSim and EnergyHub use — including the shared backend services that power both modules. It must be complete enough that a team member can answer "how does the system decide/compute X?" for any X, in plain language, without opening the code.

## Non-negotiable style rules

1. **Plain English only.** Write the way a person would explain it out loud to another person. Short sentences. Everyday words.
2. **Define every technical term the first time it appears.** Example: "performance ratio (a single number that rolls up all real-world energy losses)".
3. **No litotes.** Never use double negatives or understatement. Do not write "not insignificant", "not uncommon", "no small", "hardly surprising", "not without merit". State things directly: say "significant", "common", "large", or name the actual size.
4. **No hedging filler.** Cut "it could be argued", "in a sense", "to some extent". Say what is true.
5. **Natural sentence formation.** Read each paragraph as if speaking it. If a sentence sounds like a textbook, rewrite it.
6. **Show the math simply.** Write formulas in plain ASCII, e.g. `Score = 0.6 x energy ratio + 0.4 x location score`. Explain each symbol in a bullet or table right below it.
7. **Every item gets a code reference** in the form `path/to/file.py:line` so a developer can verify it. Verify the line numbers yourself against the current code — do not trust stale docs.
8. **No litotes check before finishing:** search your output for "not ", "no small", "hardly", "scarcely", "cannot be overstated" and rewrite any hits.

## Format for each item

Use this exact pattern for every formula, rule, or AI component (it matches `docs/04-ML-Data-Science/PANEL_FORMULA_SUMMARY_SIMPLE.md`):

```
### <Name of the thing>

**What it is:** 2-4 plain sentences. What goes in, what comes out, in everyday words.

**The math (simplified):**
```
formula in plain ASCII
```
Bullet list explaining each symbol/constant and where its value comes from.

**Why it matters:** 1-3 plain sentences on what breaks or goes wrong without it.

**Where it lives in the code:** `path:line` (function name)
```

For decision rules and matrices that are not single formulas, replace "The math" with "How it decides" and show the rule, the weights, or the threshold table.

## Scope — cover ALL of the following

Verify each item in the actual code. Treat existing docs as leads only — they may be stale. If the code disagrees with an old doc, the code wins.

### A. EcoSim — how a user's answers become a recommendation

- `fastapi-backend/app/services/ecosim.py`
  - `consumption_calculator` (~line 908): electricity bill -> monthly kWh -> desired savings -> required system size
  - `renewable_energy_calculator` (~line 933): the main pipeline that runs all four energy sources
  - `_calculate_option_summary` (~line 1657): `suitability_score = source_score x (0.4 + 0.6 x energy_ratio) x 100`, `generation_score`, ranking logic
  - `_build_static_renewable_explanations`, `_get_or_build_explanations`: how the per-source explanations are produced and cached
  - `build_ecosim_dashboard_response`, `_recommendation_key`: how options are ranked and presented
  - Baseline constants (e.g. `solar_score_baseline_pvout`, `wind_score_baseline_kwh`, `hydro_score_baseline_kwh` ~line 1357)
- `fastapi-backend/app/services/solar_output_calc.py`
  - `calculate_temperature_factor`: -0.004 per degree C above 25 C
  - `calculate_noct_cell_temp`, `calculate_temperature_factor_noct`: cell temperature from air temperature + irradiance (NOCT model)
  - `calculate_soiling_loss`, `calculate_dust_loss_from_wind`: dust losses tied to wind speed
  - `calculate_degradation_from_humidity`: humidity-driven degradation
  - `calculate_air_density_correction`: altitude/air-density effect
  - `calculate_performance_ratio`: the multiplier that rolls up all losses
  - `solar_calc`, `solar_calc_advanced`, `solar_calc_pvout`: the three solar output paths
- `fastapi-backend/app/services/wind_output_calc.py`
  - `extrapolate_wind_speed`: power-law height correction for wind speed
  - `calculate_wind_output`: wind speed -> turbine output; `load_wind_averages`/`_compute_wind_averages`: the wind CSV averages
- `fastapi-backend/app/services/hydro_output_calc.py`
  - `normalize`, `estimate_runoff_coefficient`, `estimated_flow_rate`, `estimate_discharge`, `calculate_hydropower` (P = rho x g x Q x H x efficiency): the full hydro chain
- `fastapi-backend/app/services/geothermal/` (`features.py`, `ml_classifier.py`, `plants.py`, `batch_compute.py`)
  - How volcano/heat-flow/geology features are extracted, how the classifier scores geothermal suitability, how confidence is produced
- `fastapi-backend/app/services/mcda.py`
  - `aggregate_score`: Weighted Linear Combination — the core decision matrix
  - `ahp_consistency_ratio`: the AHP consistency check on judgment matrices
  - `promethee_ii`: the PROMETHEE II outranking method
- `fastapi-backend/app/services/mcda_weights_service.py`: where the per-source criterion weights come from (Supabase table + cache)
- `fastapi-backend/app/services/financials.py`: `calculate_npv`, `calculate_irr`, `calculate_lcoe`, `calculate_payback` — the money math
- `fastapi-backend/app/services/confidence.py`: how the confidence score is assembled from data coverage, data recency, model maturity, spatial resolution
- `fastapi-backend/app/services/gemini_funcs.py`: the AI-generated renewable analysis — cache key, prompt construction, JSON parsing, normalization, geothermal stripping for province-level answers
- Inputs: `climate_service.py`, `geospatial_service.py`, `catchment_data.py`, `atlas_data.py` — where the climate/terrain data comes from and how it is looked up per municipality

### B. EnergyHub — forecasting, maps, and AI insights

- `fastapi-backend/app/services/energyhub.py`
  - `_classify_score`: the thresholds that turn a number into a label
  - Map builders: `_build_geothermal_potential_map`, `_build_renewable_potential_map`, `_build_province_metric_map`, `_build_municipality_potential_map`, `_build_barangay_potential_map`
  - `_aggregate_factors`, `_apply_geothermal_boost`: how factor scores combine and how geothermal boosts nearby provinces
  - `estimate_municipal_demand`: how municipal electricity demand is estimated from provincial data
  - `get_provincial_consumption`, `get_irena_*`, `get_meralco_rate`, `get_solar_atlas`: external/statistical data getters
  - `get_ai_insight`, `analyze_chart`, `get_map_explanation`, `_build_chart_prompt`, `_build_map_explanation_prompt`, `_hash_chart_data`, `_get_cached_insight`, `_cache_insight`, `_generate_llm_insight`, `_clean_llm_text`, `_static_map_explanation`: the AI insight pipeline — prompt, LLM call, static fallback, cache
  - `_nearest_geo_feature`, `_lookup_item_lat_lon`, `_summarize_map_data`, `_map_data_sources`
- `fastapi-backend/app/ml/predictor.py` (`EnergyHubML`)
  - `get_forecast`: reads offline forecast artifacts (ARIMA-family model outputs)
  - `get_model_comparison`: how candidate models are compared
  - `get_latest_statistics`, `get_historical_trends`, `get_source_breakdown`, `get_grid_breakdown`, `get_ai_insight`, `get_provincial_consumption`, `get_regional_sales`
- `fastapi-backend/app/services/forecasting.py`
  - `fit_sarima`, `fit_arimax`: SARIMA(p,d,q)(P,D,Q,s) and ARIMAX — explain what a time-series model with seasonal terms is, in layman terms
  - `backtest_walk_forward`: walk-forward validation — training on the past, testing on the next step, rolling forward
  - `calculate_metrics`: MAE / RMSE / MAPE and friends — what each error number means
  - `select_best_sarima_config`, `run_forecast_pipeline`, `run_forecast_pipeline_cached`, `reconcile_forecast_cache`, `log_model_run`, `_classify_model_type`
- `fastapi-backend/app/services/llm_client.py`, `groq_client.py`, `llm_sanitizer.py`: how LLM calls are made, retried, parsed, and cleaned (thinking-block stripping)
- `fastapi-backend/app/services/rag_pipeline.py`, `rag_hybrid.py`, `rag_faiss.py`, `rag_embeddings_client.py`, `rag_gemini_funcs.py`, `rag_pgvector_store.py`, `rag_knowledge_builder.py`
  - The RAG (retrieval-augmented generation) pipeline: how documents are chunked, embedded, indexed (FAISS and/or pgvector), and retrieved
  - `rag_hybrid.py`: BM25 keyword scoring + vector search combined with reciprocal rank fusion, `rerank_results`, `verify_citations`, `validate_input`, `sanitize_output`
- Data processing: `etl_orchestrator.py`, `data_cache.py`, `build_catchment_enrichment.py`, `municipality_suitability_builder.py`, `load_catchment_to_supabase.py`, plus `docs/04-ML-Data-Science/DOE_datacleaning_EXPLAINED.md` (verify against scripts in `python_scripts/` and `scripts/`)

### C. What the user sees (brief section only)

- `react-frontend/src/pages/Ecosim.jsx`, `react-frontend/src/pages/EnergyHub.jsx`
- `react-frontend/src/components/ecosim/` (`EcosimWizard`, `EcosimResults`, `EcosimBOM`, `ProviderRecommendations`, `ExplanationModal`)
- `react-frontend/src/components/energyhub/` (`AiInsightPanel`, `ChartExplanation`, `MapExplanationCard`, `EnergyMap`, `EnergyOverview`, `EnergySources`, `EnergyTrends`, `ProvincialDemand`, `PlotlyChart`)
- `react-frontend/src/utils/ecosimAnalysis.js`
- One or two sentences per component: what the user sees and which backend number produces it.

## Required structure of the output document

1. **Title + purpose + audience** (short).
2. **The 30-second version** — one plain paragraph each for "What EcoSim does" and "What EnergyHub does", suitable for reading aloud to a panelist.
3. **EcoSim: from answers to recommendation** — the pipeline in plain steps, then every formula grouped by energy source (solar, wind, hydro, geothermal).
4. **The decision matrix** — WLC/aggregate_score, the weights and where they come from, AHP consistency check, PROMETHEE II, suitability vs generation score, confidence score.
5. **The money math** — NPV, IRR, LCOE, payback.
6. **EnergyHub: forecasting** — SARIMA/ARIMAX in plain terms, walk-forward backtesting, the error metrics, model comparison, where the offline artifacts come from.
7. **EnergyHub: maps and demand** — score classification, factor aggregation, geothermal boost, municipal demand estimation, provincial/regional statistics.
8. **The AI explanations** — Gemini/Groq insights for EcoSim results, EnergyHub chart/map insights, caching, static fallbacks, sanitization.
9. **The chat/RAG pipeline** — retrieval, hybrid search, reranking, citations, guardrails.
10. **Data sources and processing** — climate CSVs, geospatial/GeoJSON, catchment enrichment, DOE cleaning, ETL, Supabase tables, external APIs (IRENA, Meralco rate, Solar Atlas).
11. **What the user sees** — the frontend mapping.
12. **Cheat sheet** — a table: "If a panelist asks X -> point them to section Y / formula Z".

## Existing docs to consolidate (verify against code before reusing)

- `docs/04-ML-Data-Science/PANEL_FORMULA_SUMMARY.md`, `PANEL_FORMULA_SUMMARY_SIMPLE.md`
- `docs/04-ML-Data-Science/MCDA_BREAKDOWN.md`, `MCDA_BREAKDOWN_SIMPLE.md`
- `docs/04-ML-Data-Science/GEOTHERMAL_FORMULAS.md`, `GEOTHERMAL_FORMULAS_SIMPLE.md`
- `docs/04-ML-Data-Science/PRICING_FORMULA_SUMMARY.md`
- `docs/04-ML-Data-Science/COMPLETE_FORMULA_SUMMARY_WITH_RRL.md` — keep the APA references where they apply
- `docs/04-ML-Data-Science/LUMI_METHODOLOGY_ML.md`, `ML_MODEL_EVALUATION_SUMMARY.md`, `ML_LIBRARIES_ALGORITHMS_DATA.md`, `DOE_datacleaning_EXPLAINED.md`
- `docs/03-Modules/ECOSIM_ARCHITECTURE.md`, `ECOSIM_BREAKDOWN.md`, `ECOSIM_DATA_IMPROVEMENTS.md`, `ENERGYHUB_ARCHITECTURE.md`
- `docs/07-Data-Extraction-Reports/ecosim_economic_formula_references.md`

## Verification checklist (run all of these before you finish)

- [ ] Every file and function in the scope list above was opened and read — no item skipped or guessed.
- [ ] Every formula/rule has a `file:line` reference verified against current code.
- [ ] Every technical term is defined in plain words at first use.
- [ ] Search the output for litotes/understatement ("not ", "no small", "hardly", "scarcely") and rewrite hits directly.
- [ ] Read the "30-second version" aloud in your head — it must sound like natural speech.
- [ ] All 12 required sections are present.
- [ ] `git status` shows only the new output file.
