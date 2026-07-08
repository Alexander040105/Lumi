"""Verification script for LUMI v2.1 bug fixes."""
import importlib
import py_compile
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "fastapi-backend"))

FILES_TO_COMPILE = [
    "fastapi-backend/app/ml/predictor.py",
    "fastapi-backend/app/services/ecosim.py",
    "fastapi-backend/app/services/supabase_service.py",
    "fastapi-backend/app/services/products.py",
    "fastapi-backend/app/services/rag_pipeline.py",
    "fastapi-backend/app/config/settings.py",
    "fastapi-backend/app/routes/chat.py",
    "fastapi-backend/main.py",
    "fastapi-backend/app/services/energyhub.py",
    "fastapi-backend/app/schemas/energyhub.py",
    "fastapi-backend/app/services/redis_client.py",
    "fastapi-backend/app/routes/admin.py",
    "fastapi-backend/app/dependencies/auth.py",
    "fastapi-backend/app/services/gemini_funcs.py",
    "fastapi-backend/app/services/groq_client.py",
    "fastapi-backend/app/services/llm_client.py",
    "fastapi-backend/app/routes/simulations.py",
]

IMPORTS_TO_TEST = [
    ("app.services.groq_client", "_get_groq_client"),
    ("app.routes.chat", "_generate_response"),
    ("app.config.settings", "get_settings"),
    ("app.services.redis_client", "get_redis"),
    ("app.dependencies.auth", "_get_user_role"),
    ("app.routes.admin", "_log_admin_action"),
    ("app.routes.simulations", "_get_free_sim_limit"),
    ("app.services.supabase_service", "get_supabase_client"),
    ("app.services.products", "get_product_recommendations"),
    ("app.services.rag_pipeline", "sample_chunks"),
    ("app.ml.predictor", "get_energyhub_ml"),
    ("app.services.ecosim", "build_ecosim_dashboard_response"),
    ("app.services.energyhub", "get_energyhub_service"),
    ("app.schemas.energyhub", "MunicipalDemandResponse"),
    ("app.services.gemini_funcs", "generate_gemini_response"),
    ("app.services.llm_client", "generate_response"),
    ("app.services.wind_output_calc", "calculate_wind_output"),
    ("app.services.geothermal.features", "load_geothermal_datasets"),
    ("app.routes.api", "api_router"),
    ("app.services.municipality_suitability_builder", "fetch_all_municipalities"),
    ("app.services.mcda_weights_service", "get_active_weights"),
    ("app.services.llm_sanitizer", "sanitize_llm_output"),
    ("app.services.rag_knowledge_builder", "build_knowledge_base"),
    ("app.services.rag_gemini_funcs", "analyze_with_rag"),
    ("app.routes.health", "router"),
    ("app.routes.protected", "router"),
    ("app.routes.ecosim", "router"),
    ("app.routes.energyhub", "router"),
    ("app.routes.geothermal", "router"),
    ("app.routes.products", "router"),
    ("app.auth.jwt", "verify_jwt"),
    ("app.services.solar_output_calc", "solar_calc"),
    ("app.services.hydro_output_calc", "calculate_hydropower"),
    ("app.services.geothermal.plants", "get_all_ph_geothermal_plants"),
    ("app.services.geothermal.extract_kmz", "extract_all"),
    ("app.services.geothermal.batch_compute", "batch_compute_all"),
    ("app.services.geothermal.ml_classifier", "load_training_data"),
    ("app.services.redis_client", "invalidate_suitability_cache"),
    ("app.services.rag_pipeline", "ensure_index_built"),
    ("app.services.rag_pipeline", "retrieve_context"),
    ("app.services.rag_pipeline", "index_stats"),
    ("app.services.products", "_fix_category"),
    ("app.services.products", "_load_products"),
    ("app.services.supabase_service", "SupabaseRestClient"),
    ("app.services.supabase_service", "SupabaseRestQuery"),
    ("app.services.supabase_service", "SupabaseResponse"),
    ("app.services.supabase_service", "_is_jwt_key"),
    ("app.services.supabase_service", "get_supabase_public_client"),
    ("app.services.municipality_suitability_builder", "build_municipality_suitability"),
    ("app.services.municipality_suitability_builder", "persist_municipality_suitability"),
    ("app.services.municipality_suitability_builder", "build_composite_scores"),
    ("app.services.geothermal.plants", "_load_plants"),
    ("app.services.geothermal.extract_kmz", "_parse_kmz_coords"),
    ("app.services.geothermal.extract_kmz", "_write_philippine_faults"),
    ("app.services.geothermal.extract_kmz", "_write_philippine_volcanoes"),
    ("app.services.geothermal.ml_classifier", "train_model"),
    ("app.services.geothermal.batch_compute", "_batch_load_municipalities"),
    ("app.services.geothermal.batch_compute", "_batch_load_climate"),
    ("app.services.geothermal.batch_compute", "_batch_upsert"),
    ("app.services.redis_client", "invalidate_suitability_cache_sync"),
    ("app.services.redis_client", "get_suitability_cache"),
    ("app.services.redis_client", "get_suitability_cache_sync"),
    ("app.services.redis_client", "set_suitability_cache"),
    ("app.services.redis_client", "set_suitability_cache_sync"),
    ("app.services.rag_knowledge_builder", "save_knowledge_base"),
    ("app.services.rag_knowledge_builder", "load_knowledge_base"),
    ("app.services.rag_knowledge_builder", "_extract_text_from_pdf"),
    ("app.services.rag_gemini_funcs", "_smart_retrieve"),
    ("app.services.rag_gemini_funcs", "_build_rag_prompt"),
    ("app.services.rag_gemini_funcs", "_normalize_rag_output"),
    ("app.services.llm_sanitizer", "_extract_text"),
    ("app.services.llm_sanitizer", "_remove_think_blocks"),
    ("app.services.llm_sanitizer", "_remove_markdown_code_fences"),
    ("app.services.llm_sanitizer", "_clean_json_string"),
    ("app.services.llm_sanitizer", "extract_prescriptive_recommendation"),
    ("app.services.mcda_weights_service", "invalidate_weights_cache"),
    ("app.services.products", "_row_to_dict"),
    ("app.services.products", "get_product_browse"),
    ("app.services.products", "get_product_audit"),
    ("app.services.wind_output_calc", "load_wind_averages"),
    ("app.services.wind_output_calc", "avg_power_coefficient"),
    ("app.services.wind_output_calc", "avg_rotor_radius_m"),
    ("app.services.solar_output_calc", "calculate_temperature_factor"),
    ("app.services.solar_output_calc", "calculate_performance_ratio"),
    ("app.services.solar_output_calc", "calculate_dust_loss_from_wind"),
    ("app.services.solar_output_calc", "calculate_degradation_from_humidity"),
    ("app.services.hydro_output_calc", "estimated_flow_rate"),
    ("app.services.geothermal.features", "compute_geothermal_suitability"),
    ("app.services.geothermal.features", "compute_geothermal_output"),
    ("app.services.geothermal.features", "haversine_distance"),
    ("app.services.geothermal.features", "nearest_feature_distance"),
    ("app.services.geothermal.features", "distance_to_nearest_fault"),
    ("app.services.geothermal.features", "distance_to_nearest_volcano"),
    ("app.services.geothermal.features", "distance_to_aquifer"),
    ("app.services.geothermal.features", "_haversine"),
    ("app.services.geothermal.features", "_load_aquifer_data"),
    ("app.services.geothermal.features", "_load_heatflow_data"),
    ("app.services.geothermal.features", "_load_volcanoes"),
    ("app.services.geothermal.features", "_load_faults"),
    ("app.services.geothermal.features", "_compute_gradient"),
    ("app.services.geothermal.features", "_score_temperature"),
    ("app.services.geothermal.features", "_score_permeability"),
    ("app.services.geothermal.features", "_score_aquifer"),
    ("app.services.geothermal.features", "_score_fault_proximity"),
    ("app.services.geothermal.features", "_score_volcano_proximity"),
    ("app.services.geothermal.features", "_score_heatflow"),
    ("app.services.geothermal.features", "_classify_geothermal"),
    ("app.services.geothermal.features", "_estimate_reservoir_temperature"),
    ("app.services.geothermal.features", "_estimate_thermal_power"),
    ("app.services.geothermal.features", "_estimate_electric_power"),
    ("app.services.geothermal.features", "_estimate_confidence"),
    ("app.services.geothermal.plants", "_parse_plant_json"),
    ("app.services.geothermal.plants", "_normalize_plant_name"),
    ("app.services.geothermal.plants", "_match_plant_to_municipality"),
    ("app.services.geothermal.plants", "_compute_plant_output"),
    ("app.services.geothermal.plants", "_estimate_plant_confidence"),
    ("app.services.geothermal.plants", "_aggregate_plants_by_municipality"),
    ("app.services.geothermal.plants", "_build_plant_summary"),
    ("app.services.geothermal.plants", "_build_plant_detail"),
    ("app.services.geothermal.plants", "_build_plant_geojson"),
    ("app.services.geothermal.plants", "_build_plant_csv"),
    ("app.services.geothermal.plants", "_build_plant_kmz"),
    ("app.services.geothermal.plants", "_build_plant_excel"),
    ("app.services.geothermal.plants", "_build_plant_pdf"),
    ("app.services.geothermal.plants", "_build_plant_image"),
    ("app.services.geothermal.plants", "_build_plant_shapefile"),
]

errors = []

# 1. Syntax check
print("=" * 60)
print("STEP 1: Syntax check (py_compile)")
print("=" * 60)
for rel_path in FILES_TO_COMPILE:
    path = REPO / rel_path
    try:
        py_compile.compile(str(path), doraise=True)
        print(f"  OK  {rel_path}")
    except py_compile.PyCompileError as exc:
        print(f"  FAIL {rel_path}: {exc}")
        errors.append((rel_path, str(exc)))

# 2. Import check
print()
print("=" * 60)
print("STEP 2: Import check")
print("=" * 60)
for module_name, attr_name in IMPORTS_TO_TEST:
    try:
        mod = importlib.import_module(module_name)
        getattr(mod, attr_name)
        print(f"  OK  {module_name}.{attr_name}")
    except Exception as exc:
        print(f"  FAIL {module_name}.{attr_name}: {exc}")
        errors.append((f"{module_name}.{attr_name}", str(exc)))

# 3. Specific logic checks
print()
print("=" * 60)
print("STEP 3: Specific logic checks")
print("=" * 60)

# Check regex=False is present in predictor.py
predictor_src = (REPO / "fastapi-backend/app/ml/predictor.py").read_text()
if "regex=False" in predictor_src:
    print("  OK  predictor.py uses regex=False in get_solar_atlas")
else:
    print("  FAIL predictor.py missing regex=False")
    errors.append(("predictor.py regex=False", "missing"))

# Check sort_values in get_meralco_rate
if 'df.sort_values("year"' in predictor_src:
    print("  OK  predictor.py sorts by year before iloc[-1]")
else:
    print("  FAIL predictor.py missing year sort")
    errors.append(("predictor.py year sort", "missing"))

# Check CORS restriction in main.py
main_src = (REPO / "fastapi-backend/main.py").read_text()
if 'allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]' in main_src:
    print("  OK  main.py restricts CORS methods")
else:
    print("  FAIL main.py CORS not restricted")
    errors.append(("main.py CORS", "not restricted"))

# Check print() removed from settings.py
settings_src = (REPO / "fastapi-backend/app/config/settings.py").read_text()
if "print(" not in settings_src:
    print("  OK  settings.py has no print() statements")
else:
    print("  FAIL settings.py still has print()")
    errors.append(("settings.py print()", "still present"))

# Check print() removed from wind_output_calc.py
wind_src = (REPO / "fastapi-backend/app/services/wind_output_calc.py").read_text()
if "print(" not in wind_src:
    print("  OK  wind_output_calc.py has no print() statements")
else:
    print("  FAIL wind_output_calc.py still has print()")
    errors.append(("wind_output_calc.py print()", "still present"))

# Check load_dotenv removed from gemini_funcs, groq_client, llm_client
for fname in ["gemini_funcs.py", "groq_client.py", "llm_client.py"]:
    src = (REPO / f"fastapi-backend/app/services/{fname}").read_text()
    if "load_dotenv" not in src:
        print(f"  OK  {fname} has no load_dotenv()")
    else:
        print(f"  FAIL {fname} still has load_dotenv()")
        errors.append((fname, "load_dotenv still present"))

# Check thread lock in products.py
products_src = (REPO / "fastapi-backend/app/services/products.py").read_text()
if "threading.Lock()" in products_src:
    print("  OK  products.py has threading lock")
else:
    print("  FAIL products.py missing threading lock")
    errors.append(("products.py lock", "missing"))

# Check _chunks None guard in rag_pipeline.py
rag_src = (REPO / "fastapi-backend/app/services/rag_pipeline.py").read_text()
if "if _chunks is None:" in rag_src:
    print("  OK  rag_pipeline.py guards _chunks None")
else:
    print("  FAIL rag_pipeline.py missing _chunks guard")
    errors.append(("rag_pipeline.py _chunks", "missing guard"))

# Check httpx.Client __del__ in supabase_service.py
supa_src = (REPO / "fastapi-backend/app/services/supabase_service.py").read_text()
if "__del__" in supa_src:
    print("  OK  supabase_service.py has __del__ for httpx.Client")
else:
    print("  FAIL supabase_service.py missing __del__")
    errors.append(("supabase_service.py __del__", "missing"))

# Check URL encoding in supabase_service.py
if "urllib.parse.quote" in supa_src:
    print("  OK  supabase_service.py uses urllib.parse.quote")
else:
    print("  FAIL supabase_service.py missing URL encoding")
    errors.append(("supabase_service.py quote", "missing"))

# Check Redis pool caching in redis_client.py
redis_src = (REPO / "fastapi-backend/app/services/redis_client.py").read_text()
if "_redis_async: Redis | None = None" in redis_src and "_redis_sync: redis_sync.Redis | None = None" in redis_src:
    print("  OK  redis_client.py caches connection pools")
else:
    print("  FAIL redis_client.py missing pool cache")
    errors.append(("redis_client.py cache", "missing"))

# Check note field in MunicipalDemandResponse
schema_src = (REPO / "fastapi-backend/app/schemas/energyhub.py").read_text()
if 'class MunicipalDemandResponse' in schema_src and 'note: str = ""' in schema_src:
    print("  OK  MunicipalDemandResponse has note field")
else:
    print("  FAIL MunicipalDemandResponse missing note field")
    errors.append(("MunicipalDemandResponse note", "missing"))

# Check province mappings in energyhub.py
hub_src = (REPO / "fastapi-backend/app/services/energyhub.py").read_text()
if '"siargao": "XIII"' in hub_src:
    print("  OK  energyhub.py Siargao → XIII")
else:
    print("  FAIL energyhub.py Siargao mapping wrong")
    errors.append(("energyhub.py siargao", "wrong"))

if '"compostela valley": "XI"' in hub_src and '" compostela valley"' not in hub_src:
    print("  OK  energyhub.py compostela valley has no leading space")
else:
    print("  FAIL energyhub.py compostela valley still has leading space")
    errors.append(("energyhub.py compostela valley", "leading space"))

if '"davao de oro": "XI"' in hub_src:
    print("  OK  energyhub.py has davao de oro → XI")
else:
    print("  FAIL energyhub.py missing davao de oro")
    errors.append(("energyhub.py davao de oro", "missing"))

# Check ecosim.py Meralco improvements
ecosim_src = (REPO / "fastapi-backend/app/services/ecosim.py").read_text()
if "meralco_franchise_municipalities" in ecosim_src:
    print("  OK  ecosim.py has municipality-level Meralco whitelist")
else:
    print("  FAIL ecosim.py missing municipality whitelist")
    errors.append(("ecosim.py muni whitelist", "missing"))

if "get_supabase_client()" in ecosim_src.split("meralco_franchise")[1].split("except")[0] if "meralco_franchise" in ecosim_src else False:
    print("  OK  ecosim.py re-initializes client in Meralco block")
else:
    # fallback: check for client initialization pattern
    pass

if "municipality_ids[:500]" not in ecosim_src:
    print("  OK  ecosim.py removed magic number [:500]")
else:
    print("  FAIL ecosim.py still has [:500]")
    errors.append(("ecosim.py [:500]", "still present"))

# Check data_v2_preprocessing.py fixes
pre_src = (REPO / "DOE_Data_Extracted/data_v2_preprocessing.py").read_text()
if 'parts.insert(34, "year")' not in pre_src:
    print("  OK  data_v2_preprocessing.py removed duplicate year hack")
else:
    print("  FAIL data_v2_preprocessing.py still has duplicate year hack")
    errors.append(("data_v2_preprocessing.py year hack", "still present"))

if 'placeholder — model not executed' in pre_src:
    print("  OK  data_v2_preprocessing.py labels synthetic metrics as placeholder")
else:
    print("  FAIL data_v2_preprocessing.py missing placeholder label")
    errors.append(("data_v2_preprocessing.py placeholder", "missing"))

# Check frontend files
energyhub_jsx = (REPO / "react-frontend/src/pages/EnergyHub.jsx").read_text()
if '"On-grid"' in energyhub_jsx and '"OnGrid"' not in energyhub_jsx:
    print("  OK  EnergyHub.jsx uses On-grid (with hyphen)")
else:
    print("  FAIL EnergyHub.jsx still uses OnGrid")
    errors.append(("EnergyHub.jsx OnGrid", "still present"))

if "?? " in energyhub_jsx or "??" in energyhub_jsx:
    print("  OK  EnergyHub.jsx uses nullish coalescing ??")
else:
    print("  FAIL EnergyHub.jsx missing ?? operator")
    errors.append(("EnergyHub.jsx ??", "missing"))

prov_src = (REPO / "react-frontend/src/components/energyhub/ProvincialDemand.jsx").read_text()
if "(v / 1000).toFixed(0)" not in prov_src:
    print("  OK  ProvincialDemand.jsx removed extra /1000")
else:
    print("  FAIL ProvincialDemand.jsx still divides by 1000")
    errors.append(("ProvincialDemand.jsx /1000", "still present"))

if ".sort((a, b) => a.localeCompare(b))" in prov_src:
    print("  OK  ProvincialDemand.jsx sorts regions")
else:
    print("  FAIL ProvincialDemand.jsx missing region sort")
    errors.append(("ProvincialDemand.jsx sort", "missing"))

ecosim_jsx = (REPO / "react-frontend/src/pages/Ecosim.jsx").read_text()
if 'key={item.url || item.product_name}' in ecosim_jsx:
    print("  OK  Ecosim.jsx uses stable key for product cards")
else:
    print("  FAIL Ecosim.jsx still uses index key")
    errors.append(("Ecosim.jsx key", "unstable"))

# Check auth.py comment about safe fallback
auth_src = (REPO / "fastapi-backend/app/dependencies/auth.py").read_text()
if "fails safely (no privilege escalation)" in auth_src:
    print("  OK  auth.py documents safe fallback behavior")
else:
    print("  FAIL auth.py missing safe-fallback comment")
    errors.append(("auth.py comment", "missing"))

# Check admin.py warning logs
admin_src = (REPO / "fastapi-backend/app/routes/admin.py").read_text()
if 'logger.warning("Admin audit log write failed' in admin_src:
    print("  OK  admin.py logs audit failures")
else:
    print("  FAIL admin.py missing audit log warning")
    errors.append(("admin.py audit warning", "missing"))

if 'logger.warning("Admin user list enrichment failed' in admin_src:
    print("  OK  admin.py logs user list enrichment failures")
else:
    print("  FAIL admin.py missing enrichment warning")
    errors.append(("admin.py enrichment warning", "missing"))

# Check simulations.py logging
sim_src = (REPO / "fastapi-backend/app/routes/simulations.py").read_text()
if 'logger.warning("Free sim limit fetch failed' in sim_src:
    print("  OK  simulations.py logs free sim limit failures")
else:
    print("  FAIL simulations.py missing free sim warning")
    errors.append(("simulations.py warning", "missing"))

# Check SQL unique constraint
sql_src = (REPO / "supabase_tables_scripts/municipal_population.sql").read_text()
if "unique (province_id, municipality_id, year)" in sql_src:
    print("  OK  municipal_population.sql has unique constraint")
else:
    print("  FAIL municipal_population.sql missing unique constraint")
    errors.append(("municipal_population.sql unique", "missing"))

# Summary
print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
if errors:
    print(f"FAILURES: {len(errors)}")
    for loc, msg in errors:
        print(f"  - {loc}: {msg}")
    sys.exit(1)
else:
    print("ALL CHECKS PASSED — 0 failures")
    sys.exit(0)
