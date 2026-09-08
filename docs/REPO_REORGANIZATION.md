# Repository Reorganization — Audit & Changelog

**Branch:** `chore/repo-reorganization`
**Purpose:** Structural/hygiene pass for thesis-defense evaluation — clean
top-level layout, no functional changes, no deletions without review.

---

## 1. Commits

| # | Commit | Scope |
|---|--------|-------|
| 1 | `241d963` | Untrack committed build artifacts, caches, runtime profiles |
| 2 | `2d9c014` | Relocate stray root files into `docs/`, `data/`, `scripts/`, `supabase/` |
| 3 | `bd2c2b6` | Group data directories under `data/`; rename `lumi_tests/` → `tests/` |
| 4 | `edc270c` | Relocate script-style verification files out of `app/services/` |
| 5 | (docs)   | Documentation consolidation + this file |

---

## 2. Untracked (index-only removals — files remain on disk)

Removed from the Git index because they are generated/local artifacts
(~3,561 files):

- `node_modules/` (root) and `react-frontend/node_modules/`
- `data/scraped_data/runtime/` — Selenium browser profile/cache (~1,500 files)
- `data/scraped_data/output/` — regenerated scrape outputs
- `scripts/gap_output/` — generated CSV reports
- `supabase/.temp/` — Supabase CLI local state (project-ref, pooler URL)
- `react-frontend/vite.config.js.timestamp-*.mjs` — Vite artifact
- `**/Thumbs.db` — Windows OS noise (8 files, incl. `data/regionalData/PHFaultLines/*`)

`.gitignore` now covers: `supabase/.temp/`, `*.timestamp-*.mjs`, `Thumbs.db`,
`data/scraped_data/runtime/`, `data/scraped_data/output/`, plus the
`data/`-anchored dataset rules.

## 3. Moved / Renamed

### Root clutter → organized homes

| From | To |
|------|----|
| `explain_*.json`, `geo.json`, `hydro.json`, `wind.json`, `md.json`, `ren.json`, `response.json`, `invalid.json`, `test_output.txt`, `retrieval_test_output.txt`, `gemini_mock_test.txt`, `fastapi-backend/chart_counts.txt` | `data/debug_outputs/` |
| `thesis_papers_extract.json`, `municipality_climate_averages.csv` | `data/` |
| `verify_fixes.py`, `generate_erd.py` | `scripts/` |
| `lumischema.sql`, `lumi_schema_v3.sql`, `lumi_schema_v4.sql` | `supabase/schema_structure/` |
| `supabase_tables_scripts/` | `supabase/table_scripts/` |
| `Chapter_3_*.md` (5 files), `lumi-details/`, `revisionFiles/` | `docs/thesis/` |
| `DEPLOYMENT_GUIDE.md` | `docs/05-Setup-Guides/` |
| `DOCS_INDEX.md`, `DocumentationFormat.md`, `LUMI_Project_Checklist_Compliance.md`, `CHANGELOG_v2.1_FIXES.md`, `CHANGELOG_v3.2.md` | `docs/` |
| `ECOSIM_BREAKDOWN.md` | `docs/03-Modules/` |
| `lumi_erd.png` | `docs/02-Architecture/` |

### Data directories → `data/`

`DOE_Data_Extracted/`, `GeothermalDatasets/`, `regionalData/`,
`philippine_geojson/`, `phl_msk_alt/`, `scraped_data/`,
`windsurf_data_extraction/`, `newDataPointsToExtract/`,
`ThesisResearchStudies/` all moved under `data/`.

~50 inbound path references updated across `fastapi-backend/` services and
scripts, `scripts/`, `python_scripts/`, `tests/`, `vercel.json`
(`includeFiles`), `.vercelignore`, `.dockerignore`, `.gitignore`, and docs.

Notable fixes while moving:

- `scripts/verify_fixes.py`: `REPO` root math corrected (`parent` → `parents[1]`)
  after moving off the root.
- `scripts/generate_erd.py`: hardcoded `d:/...` output path replaced with a
  repo-relative `docs/02-Architecture/lumi_erd.png`.
- `scripts/migrate_csv_to_supabase.py`: `DOE_CSVS` literals are **Supabase
  `dataset_name` identifiers** — kept unchanged; only the filesystem read path
  gained the `data/` prefix.
- `data/windsurf_data_extraction/*.py`: `parents[1]` now resolves to `data/`,
  so all internal joins self-heal; module usage updated to
  `python -m data.windsurf_data_extraction.*`.

### Tests

- `lumi_tests/` → `tests/` (CI `working-directory` updated in
  `.github/workflows/ci.yml`).
- Six files in `fastapi-backend/app/services/` (`test_*.py`) turned out to be
  **script-style verification harnesses** — no `def test_` functions; five run
  live RAG/LLM queries at import time and lack `__main__` guards. Moving them
  into `fastapi-backend/tests/` broke pytest collection for the real suite, so
  they were moved to `fastapi-backend/scripts/check_*.py` instead (deviation
  from the original plan, done to avoid a regression). Path math updated
  (`parents[3]` → `parents[2]`).

### Docs consolidation

Loose `docs/*.md` files distributed into the numbered categories:

- `05-Setup-Guides/`: AZURE_DEPLOYMENT_GUIDE, VERCEL_DEPLOYMENT_GUIDE,
  VERCEL_BACKEND_404_FIX, DEVELOPMENT_WORKFLOW
- `03-Modules/`: ECOSIM_DATA_IMPROVEMENTS, SYSTEM_FUNCTION_INVENTORY(+SIMPLIFIED),
  RecommendedRenewableEnergyProviders
- `02-Architecture/`: geospatial_architecture, geospatial_data_pipeline,
  geographic_granularity
- `04-ML-Data-Science/`: COMPLETE_FORMULA_SUMMARY_WITH_RRL,
  GEOTHERMAL_FORMULAS(+SIMPLE), MCDA_BREAKDOWN(+SIMPLE),
  PANEL_FORMULA_SUMMARY(+SIMPLE), PRICING_FORMULA_SUMMARY,
  ML_MODEL_EVALUATION_SUMMARY, municipal_demand_granularity_study,
  FREE_ALTERNATIVE_DATA
- `07-Data-Extraction-Reports/`: ATLAS_DATA_INTEGRATION, ERA5_INTEGRATION,
  ERA5_VALIDATION, PROVINCE_ATLAS_VALIDATION
- `09-Technical-Evaluation/`: LUMI_COMPREHENSIVE_AUDIT,
  LUMI_PRODUCTION_READINESS_REPORT, LUMI_Project_Checklist_Compliance,
  DocumentationFormat, DATA_ACCURACY_AND_THESIS_DEFENSE_GUIDE
- `thesis/`: THESIS_RESEARCH_INTEGRATION, LUMI_THESIS_REVISIONS_MASTER,
  REVISIONS_INTEGRATION_SUMMARY, shortened_section_9_8,
  CONSULTATION_RECORD_2_CHANGELOG, CONSULTATION_RECORD_2_IMPLEMENTATION
- `01-Project-Overview/`: LUMI_COMPLETE_SYSTEM_DOCUMENTATION,
  LUMI_IMPLEMENTATION_LOG, LESSONS_LEARNED
- Left at `docs/` root: `DOCS_INDEX.md`, `CHANGELOG_v2.1_FIXES.md`,
  `CHANGELOG_v3.2.md`

All inbound `docs/NAME.md` references updated; `DOCS_INDEX.md` regenerated.

### New documentation

- `fastapi-backend/README.md`, `react-frontend/README.md` — per-app guides
- Root `README.md` — project-structure tree and docs table refreshed
- `docs/DOCS_INDEX.md` — regenerated

---

## 4. Before / After (top level)

**Before**

```
Lumi/
├── api/  data dirs scattered at root:  ├── DOE_Data_Extracted/
├── GeothermalDatasets/  ├── newDataPointsToExtract/  ├── phl_msk_alt/
├── philippine_geojson/  ├── regionalData/  ├── scraped_data/
├── ThesisResearchStudies/  ├── windsurf_data_extraction/
├── lumi-details/  revisionFiles/  lumi_tests/  supabase_tables_scripts/
├── ~30 loose .md/.json/.sql/.png/.txt/.py files at root
├── node_modules/ + scraped_data/runtime/ committed (3.5k junk files)
```

**After**

```
Lumi/
├── api/                # Vercel entry point
├── data/               # all datasets & data pipelines (+ debug_outputs/)
├── deploy/  docs/  expo-mobile/  fastapi-backend/  python_scripts/
├── react-frontend/  scripts/  supabase/  templates/  tests/
└── root config only: README, .env.example, .gitignore, package.json,
    pyproject.toml, requirements*.txt, vercel.json, docker-compose*.yml,
    .dockerignore, .vercelignore, .gitattributes, .windsurfrules
```

---

## 5. Flagged for manual review — NOT changed

| Item | Why flagged |
|------|-------------|
| `expo-mobile/` | Contains only `.expo/` cache — no source code. Delete? |
| `example.py` route/schema/service trio | Scaffold-looking code; possibly intentional example |
| `app/routes/chat.py`, `app/routes/etl.py` | Present but not mounted in `main.py` (see known-gaps note in 09-Technical-Evaluation) |
| Old `lumi-fastapi-react-v1.x`–`vN.x` branches | Version-snapshot branches; confirm before pruning |
| Duplicate requirements manifests (`requirements.txt`, `requirements-no-torch.txt`, `fastapi-backend/requirements*.txt`, `api/requirements.txt`) | Vercel pins `api/requirements.txt`; local uses `fastapi-backend/requirements.txt`. Consolidation needs deploy verification |
| Competing schemas (`lumischema.sql`, `lumi_schema_v3/v4.sql`, `supabase/schema_structure/lumi_schema_latest.sql`) | Canonical schema should be confirmed (v4 is referenced as primary) |
| `data/` dataset tracking | `GeothermalDatasets`, `newDataPointsToExtract`, `ThesisResearchStudies` were gitignored-but-tracked; kept tracked. Consider untracking + external storage if size matters |
| `data/debug_outputs/` dumps | Preserved for thesis/audit value; safe to delete later |
| `docs/09-Technical-Evaluation/` references `artifacts/` | The `artifacts/` dir (test logs, sweep JSONL) is **not in the repo** — restore it or accept doc-only evidence |
| `newCatchmentsData/` | Untracked local dir used by `build_catchment_enrichment.py` — stays local, added to `.dockerignore` |
| `templates/`, `deploy/` | Present but unreferenced — confirm still needed |

---

## 6. Verification

- `cd fastapi-backend && python -m pytest tests -q` → **77 passed**
- `cd tests && python -m pytest tests/unit -q` → **176 passed**
- `vercel.json` `includeFiles` now bundles `data/DOE_Data_Extracted/data_v2_preprocessed/**`
- `.vercelignore` / `.dockerignore` / `.gitignore` updated for the new layout
- `api/index.py` unchanged (still `sys.path`-inserts `fastapi-backend`, imports `main:app`)
- Remaining risk: Vercel deploy should be smoke-tested once; `dataset_name`
  rows in Supabase keep their `DOE_Data_Extracted/...` keys (unchanged by design).
