# LUMI System Function Inventory

**Document Version:** 1.0  
**Date:** 2025-06-26  
**Purpose:** Thesis-ready system documentation for logical diagram creation (Chapter 2.7 onwards).  
**Scope:** Documents the CURRENT implemented LUMI system. No redesign. Partially implemented features are explicitly labeled.

---

## Table of Contents

1. [Part 1: LUMI Module Inventory](#part-1-lumi-module-inventory)
2. [Part 2: User Role and Actor Analysis](#part-2-user-role-and-actor-analysis)
3. [Part 3: Complete System Function List](#part-3-complete-system-function-list)
4. [Part 4: System Process Flow Analysis](#part-4-system-process-flow-analysis)
5. [Part 5: Data Flow Diagram Information](#part-5-data-flow-diagram-information)
6. [Part 6: Module Interaction Map](#part-6-module-interaction-map)
7. [Part 7: Database and Data Process Mapping](#part-7-database-and-data-process-mapping)
8. [Part 8: AI / LLM Process Flow](#part-8-ai--llm-process-flow)
9. [Part 9: Machine Learning Process Flow](#part-9-machine-learning-process-flow)
10. [Part 10: Diagram Recommendation](#part-10-diagram-recommendation)

---

## Part 1: LUMI Module Inventory

### Module 1: Authentication & Identity Management

- **Purpose:** Secure user identity, session management, and role-based access control.
- **Description:** Manages user registration, login (email/password and OAuth), JWT token verification, password reset, and role assignment. Integrates with Supabase Auth for identity storage and JWT handling. Auto-creates profile and role records on new user signup via database triggers.
- **Main Users:** All users (Guest, Registered User, Admin).
- **Functions:**
  - Register new user (email/password)
  - OAuth sign-in (Google, etc. via Supabase)
  - Login with credentials
  - Password reset via email link
  - JWT token validation and user extraction
  - Role fetching (`user`, `admin`, `dev`)
  - Avatar URL sync from OAuth metadata
- **Input Data:** Email, password, OAuth provider token, JWT bearer token.
- **Processing:** Supabase Auth API calls, JWT decode with `supabase_jwt_secret`, profile/role lookup, trigger-based auto-provisioning.
- **Output:** Authenticated session, user metadata, role, access token.
- **Dependencies:** Supabase Auth, `profiles` table, `user_roles` table.

### Module 2: User Dashboard

- **Purpose:** Centralized user hub for profile management, saved content, and quick navigation.
- **Description:** Displays the authenticated user's profile (editable), saved locations (preferred municipality), saved EcoSim simulations, and composite renewable suitability scores for selected municipalities. Provides quick-action links to EcoSim, LUMI AI, and EnergyHub.
- **Main Users:** Registered Users.
- **Functions:**
  - Fetch and display user profile
  - Edit profile (name, organization, location, avatar)
  - Display saved locations/municipalities
  - Display saved simulations
  - Fetch and display composite renewable score for a selected municipality (solar, wind, hydro, geothermal)
  - Quick navigation to other modules
- **Input Data:** User ID, municipality ID, profile updates.
- **Processing:** Supabase queries to `profiles`, `saved_simulations`, `solar_suitability`, `wind_suitability`, `hydropower_suitability`, `geothermal_suitability`, `municipalities`.
- **Output:** Profile card, saved items list, composite score visualization, navigation links.
- **Dependencies:** Authentication module, EcoSim module, Suitability Engine, Supabase.

### Module 3: EcoSim (Renewable Energy Simulation)

- **Purpose:** Simulate renewable energy potential and cost savings for a household in a selected Philippine municipality.
- **Description:** Allows users to input household details (monthly bill, electricity rate, desired savings percentage) and select a municipality. The system computes potential energy output and cost breakdowns for solar, wind, hydro, and geothermal sources using climate and terrain data. Optional AI and RAG integration for enhanced recommendations.
- **Main Users:** Registered Users, Guests (MVP public mode).
- **Functions:**
  - List all municipalities (alphabetical)
  - Retrieve municipality climate averages (NASA POWER aggregation)
  - Calculate solar energy output (panel wattage, irradiance, performance ratio)
  - Calculate wind energy output (Betz-limit physics-based turbine model)
  - Calculate hydropower output (runoff coefficient, flow rate, head)
  - Retrieve geothermal output (pre-computed Supabase table, fallback to on-the-fly estimation)
  - Consumption calculator (monthly/daily kWh from bill amount)
  - Cost and CO2 savings estimation
  - Save simulation results (registered users)
- **Input Data:** Municipality name/ID, monthly electricity bill (PHP), electricity rate (PHP/kWh), desired savings (%), house type.
- **Processing:** Fetch NASA POWER climate averages → apply physics-based formulas per energy type → compute costs and savings → aggregate results.
- **Output:** Simulation results JSON (energy outputs, costs, payback periods, CO2 savings, suitability scores).
- **Dependencies:** NASA POWER climate data, `municipalities`, `municipality_climate_monthly`, `hydropower_suitability`, `geothermal_output`, `geothermal_suitability`, `geothermal/features.py`, solar/wind/hydro calculator services.

### Module 4: EnergyHub (National Energy Intelligence)

- **Purpose:** Visualize and analyze national Philippine energy statistics with ML forecasting and AI insights.
- **Description:** Provides an interactive dashboard for national energy overview, historical trends, choropleth maps, source/grid breakdowns, and ML-powered forecasts. Integrates AI for chart analysis and natural language insights.
- **Main Users:** All users (public access).
- **Functions:**
  - National energy overview (latest consumption, generation, peak demand)
  - ML forecast for consumption and peak demand (ARIMA-based)
  - Historical trends (multi-year time series)
  - Choropleth map data (solar, wind, hydro, geothermal, composite suitability at municipality/province level)
  - Energy source breakdown (percentage by technology)
  - Grid breakdown (ownership: private, government, coop)
  - AI-powered chart analysis and insights
  - Model comparison (forecast accuracy metrics)
- **Input Data:** Geographic level (municipality/province), metric type, year range.
- **Processing:** Aggregate from `national_energy_annual`, `municipalities`, suitability tables; serve pre-computed ARIMA forecasts; optionally call LLM for insight generation.
- **Output:** JSON datasets for charts, map GeoJSON with color-coded scores, AI-generated insight text.
- **Dependencies:** `national_energy_annual`, `municipalities`, `forecast_cache`, `ml_model_registry`, Redis cache, LLM services, ML predictor.

### Module 5: Geothermal Analysis

- **Purpose:** Specialized geothermal energy assessment including plant data and municipality-level suitability/output.
- **Description:** Provides endpoints for listing existing geothermal plants in the Philippines, detailed geothermal analysis for a municipality (using IHFC heat flow, fault/volcano proximity, NASA POWER temperature), and EcoSim parameter retrieval. Includes fallback on-the-fly computation when pre-computed data is unavailable.
- **Main Users:** All users.
- **Functions:**
  - List geothermal plants (name, location, status, capacity)
  - Municipality geothermal suitability analysis
  - Municipality geothermal energy output estimation
  - Retrieve EcoSim geothermal parameters
  - Province-level geothermal summary
- **Input Data:** Municipality name/ID, latitude, longitude.
- **Processing:** Load IHFC heat flow + fault/volcano datasets → calculate distances → normalize factors → compute suitability score → estimate reservoir temperature and MW output.
- **Output:** Geothermal suitability score, classification, reservoir temperature, thermal/electric power, annual energy GWh, confidence score.
- **Dependencies:** IHFC Global Heat Flow Database, PHIVOLCS fault/volcano data, `geothermal_suitability`, `geothermal_output`, `municipalities`.

### Module 6: AI Chat Assistant (RAG-Powered)

- **Purpose:** Provide AI-assisted renewable energy decision support through a conversational interface.
- **Description:** Users ask natural language questions about renewable energy, costs, components, or LUMI data. The system uses Retrieval-Augmented Generation (RAG) to retrieve relevant knowledge chunks from scraped product data, DOE statistics, NASA POWER climate data, and terrain metrics, then generates a contextual response using Groq LLM. Includes citation formatting and persona instructions.
- **Main Users:** All users (MVP public mode; chat session persistence partially implemented).
- **Functions:**
  - Send message to AI (with RAG context retrieval)
  - Retrieve relevant knowledge chunks (semantic search via FAISS)
  - Generate AI response (Groq/Gemini LLM)
  - Sanitize LLM output (strip markdown fences, JSON wrappers, normalize whitespace)
  - Extract prescriptive recommendation structure (observation, interpretation, recommendation, reason)
  - Display formatted citations with sources
  - List chat sessions (partially implemented — skipped in MVP public mode)
  - Get chat session detail (partially implemented)
- **Input Data:** User natural language query, chat history (in-memory only for MVP).
- **Processing:** Embed query → FAISS similarity search → rank top-k chunks → assemble prompt with context + source metadata → call Groq API → sanitize response → format with citations.
- **Output:** AI response text, source citations (title, URL, organization).
- **Dependencies:** `rag_pipeline.py` (SentenceTransformer + FAISS), `rag_knowledge_builder.py`, `groq_client.py`, `gemini_funcs.py`, `llm_sanitizer.py`, knowledge JSON files.

### Module 7: Admin & System Management

- **Purpose:** Administrative control over users, system configuration, analytics, and content moderation.
- **Description:** Protected admin-only interface and API for managing the LUMI platform. Requires `admin` or `dev` role.
- **Main Users:** Administrators, Developers.
- **Functions:**
  - List all users (with profile, role, plan)
  - Create user (admin action)
  - Get user detail
  - Ban/unban user (soft delete via `is_active`)
  - Change user role
  - Change user plan
  - View user simulations
  - Generate usage report
  - System analytics (dashboard metrics)
  - System configuration (toggle chatbot, maintenance mode, limits)
  - Chat session moderation (view flagged sessions)
  - Admin audit logging (immutable action log)
- **Input Data:** Admin JWT token, target user ID, action parameters, config updates.
- **Processing:** Verify admin role → perform Supabase Auth Admin API or direct table operations → log action to `admin_audit_log`.
- **Output:** User lists, analytics metrics, confirmation messages, audit trail.
- **Dependencies:** `auth.py` (role enforcement), Supabase Auth Admin API, `profiles`, `user_roles`, `admin_audit_log`, `system_config`, `saved_simulations`, `chat_sessions`.

### Module 8: Suitability Engine (Backend Computation)

- **Purpose:** Compute and persist municipality-level renewable energy suitability scores.
- **Description:** Batch or on-demand computation service that calculates solar, wind, hydro, and geothermal suitability scores for every municipality using climate and terrain data. Updates the `municipalities` table with composite scores and classifications. Classifications: Excellent, Good, Moderate, Poor, Unsuitable.
- **Main Users:** System (backend service), Admin (trigger re-computation).
- **Functions:**
  - Compute solar suitability (from NASA POWER irradiance, temperature)
  - Compute wind suitability (from NASA POWER wind speed, air density)
  - Compute hydro suitability (from terrain metrics + rainfall)
  - Compute geothermal suitability (from heat flow, faults, volcanoes)
  - Compute composite suitability score
  - Classify score into tiered category
  - Persist scores to Supabase
  - Cache results in Redis
- **Input Data:** Municipality coordinates, NASA POWER monthly climate averages, terrain metrics (elevation, slope, ruggedness), heat flow data.
- **Processing:** Fetch data per municipality → normalize each factor → apply weighted formula → classify → upsert to `municipalities` + type-specific tables → cache in Redis.
- **Output:** Suitability scores, classifications, cached map data.
- **Dependencies:** NASA POWER, `municipality_climate_monthly`, terrain pipeline, `municipalities`, `hydropower_suitability`, `geothermal_suitability`, Redis.

### Module 9: Machine Learning Forecasting

- **Purpose:** Predict future national energy consumption and peak demand using time-series forecasting.
- **Description:** Offline-trained ARIMA(1,1,1) models on historical DOE data. Forecasts are pre-computed and stored in CSV artifacts. The backend predictor loads these artifacts and serves predictions via API. Includes a model registry for tracking active models.
- **Main Users:** All users (via EnergyHub).
- **Functions:**
  - Load pre-computed ARIMA forecasts (consumption, peak demand)
  - Load historical DOE data
  - Get latest national statistics
  - Get historical trends (multi-year)
  - Serve forecasted values for specific years
  - Cache forecasts in `forecast_cache` table
  - Model registry (track model versions, active status)
- **Input Data:** Target variable (`total_consumption_gwh`, `peak_demand_mw`), forecast year.
- **Processing:** Load CSV artifact → extract forecast series → return JSON with forecast values, confidence intervals, and historical context.
- **Output:** Forecast JSON (year, predicted value, lower/upper bounds), historical trend dataset.
- **Dependencies:** DOE historical CSVs, `ml_model_registry`, `forecast_cache`, `national_energy_annual`.

### Module 10: Data ETL & Ingestion Pipeline

- **Purpose:** Extract, clean, and load external data into LUMI's database and knowledge base.
- **Description:** Collection of scripts and services that process data from NASA POWER (climate), DOE (energy statistics), Global Energy Monitor (geothermal plants), e-commerce scrapers (product pricing), and terrain analysis (elevation, slope). Outputs are stored in Supabase or local CSV/JSON files for RAG.
- **Main Users:** System (automated/scheduled), Admin (manual trigger).
- **Functions:**
  - Extract NASA POWER climate data per municipality
  - Clean and normalize DOE energy statistics
  - Extract geothermal plant data (KMZ/Excel to CSV/JSON)
  - Scrape e-commerce product listings (Alibaba, Amazon, Lazada)
  - Clean scraped product data
  - Build RAG knowledge chunks from all sources
  - Compute terrain metrics (elevation, slope, ruggedness, watershed)
  - Ingest all data into Supabase
- **Input Data:** Raw external files (PDF, Excel, KMZ, CSV), API responses (NASA POWER), scraped HTML.
- **Processing:** Parsing → cleaning → normalization → aggregation → chunking → embedding/indexing.
- **Output:** Clean database tables, FAISS index, knowledge JSON files.
- **Dependencies:** NASA POWER API, DOE datasets, GeothermalDatasets, scraped_data pipeline, terrain pipeline, Supabase, FAISS.

---

## Part 2: User Role and Actor Analysis

### Actor 1: Guest User (Unauthenticated Visitor)

- **Responsibilities:** Browse public information, explore energy data, use limited simulation features.
- **Accessible Features:**
  - Home page / landing page
  - About page (system documentation)
  - EnergyHub (national overview, trends, choropleth map, source breakdown)
  - EcoSim (basic simulation, limited to MVP public mode)
  - AI Chat (MVP public mode, no session persistence)
  - Login / Registration / Password Reset
- **Restrictions:**
  - Cannot save simulations
  - Cannot access Dashboard
  - Cannot access Admin pages
  - No profile management
  - Chat sessions not persisted
  - No personalized recommendations

### Actor 2: Registered User (Authenticated)

- **Responsibilities:** Access personalized features, save preferences and simulations, interact with AI assistant.
- **Accessible Features:**
  - All Guest features
  - User Dashboard (profile, saved locations, saved simulations, composite scores)
  - EcoSim (full simulation with save capability)
  - AI Chat (with session persistence — partially implemented)
  - Profile editing (name, organization, location, avatar)
  - View municipality renewable scores
- **Restrictions:**
  - Cannot access Admin pages
  - Cannot modify system configuration
  - Cannot view other users' data
  - Chat usage may be limited by free plan limits

### Actor 3: Administrator / Developer

- **Responsibilities:** Manage users, monitor system health, configure platform settings, moderate content.
- **Accessible Features:**
  - All Registered User features
  - Admin Dashboard (`/admin`)
  - User Management (list, create, ban, change role/plan)
  - System Analytics (usage metrics)
  - System Configuration (toggle features, set limits)
  - Chat Moderation (view flagged sessions)
  - View Admin Audit Log
  - Access all profiles via RLS override
- **Restrictions:**
  - Cannot delete users permanently (soft delete only)
  - Audit log is immutable

### Actor 4: External Data Sources (System Actors)

- **Responsibilities:** Provide raw environmental, energy, and market data.
- **Entities:**
  - **NASA POWER API:** Climate data (temperature, irradiance, wind, precipitation, humidity, air density)
  - **DOE (Department of Energy Philippines):** National energy statistics, generation data, consumption by sector
  - **Global Energy Monitor / IHFC:** Geothermal plant locations, heat flow measurements
  - **PHIVOLCS / GIS:** Fault lines, volcano locations
  - **E-commerce Platforms (Alibaba, Amazon, Lazada, iSTA Breeze):** Product pricing for renewable energy components
- **Accessible Features:** Read-only external APIs; LUMI pulls data on schedule or on-demand.
- **Restrictions:** No write access to LUMI systems.

### Actor 5: AI / LLM Services (System Actors)

- **Responsibilities:** Generate natural language insights, recommendations, and chat responses.
- **Entities:**
  - **Groq API:** Primary LLM for chat responses and chart analysis
  - **Google Gemini API:** Fallback/chart analysis LLM
  - **SentenceTransformer (all-MiniLM-L6-v2):** Embedding model for RAG
  - **FAISS:** Vector search index for knowledge retrieval
- **Accessible Features:** Receive prompts and context from LUMI backend; return generated text.
- **Restrictions:** No direct database access; all context is assembled by LUMI's RAG pipeline.

### User Interaction Matrix

| Actor | Module | Action | Output |
|---|---|---|---|
| Guest | Home | View landing page | Feature overview, navigation |
| Guest | About | Read documentation | System architecture info |
| Guest | EnergyHub | View national overview | Consumption, generation, peak demand stats |
| Guest | EnergyHub | View choropleth map | Color-coded suitability map |
| Guest | EnergyHub | View trends | Historical chart data |
| Guest | EcoSim | Run basic simulation | Energy output estimate (no save) |
| Guest | AI Chat | Ask question | AI response with citations |
| Guest | Auth | Register / Login | Authenticated session |
| Registered | Dashboard | View profile | User info, saved items |
| Registered | Dashboard | Edit profile | Updated profile |
| Registered | Dashboard | View saved simulations | Simulation history list |
| Registered | Dashboard | View composite score | Solar + Wind + Hydro + Geo score |
| Registered | EcoSim | Run simulation + save | Saved simulation record |
| Registered | AI Chat | Ask question (persisted) | AI response, session stored |
| Registered | Auth | Reset password | Password updated |
| Admin | Admin Dashboard | View analytics | System usage metrics |
| Admin | Admin Users | List users | User table with roles/plans |
| Admin | Admin Users | Ban user | User `is_active` = false |
| Admin | Admin Users | Change role | Role updated in `user_roles` |
| Admin | Admin Config | Update settings | `system_config` updated |
| Admin | Admin Moderation | View flagged chats | Flagged session list |
| System | Suitability Engine | Compute scores | Updated `municipalities` table |
| System | ML Forecasting | Generate forecast | `forecast_cache` entries |
| System | Data ETL | Ingest NASA POWER | `municipality_climate_monthly` updated |
| System | RAG Pipeline | Build knowledge index | FAISS index + chunk files |

---

## Part 3: Complete System Function List

### 3.1 Authentication & Identity Management Functions

**Function:** `POST /auth/register` (Supabase client-side)  
**Purpose:** Create a new user account.  
**User Action:** Guest fills registration form with email and password.  
**System Process:**
1. Frontend calls `supabase.auth.signUp()`
2. Supabase Auth creates user in `auth.users`
3. Database trigger `on_auth_user_created` auto-creates `profiles` and `user_roles` rows
**Input:** Email, password, optional full name.  
**Output:** Confirmation email sent (if enabled), user UUID created.  
**Status:** Implemented.

**Function:** `POST /auth/login` (Supabase client-side)  
**Purpose:** Authenticate existing user.  
**User Action:** Guest enters credentials on login page.  
**System Process:**
1. Frontend calls `supabase.auth.signInWithPassword()`
2. Supabase returns JWT session
3. Frontend stores session
4. Frontend fetches role from `user_roles`
**Input:** Email, password.  
**Output:** JWT access token, refresh token, user metadata, role.  
**Status:** Implemented.

**Function:** `POST /auth/oauth/{provider}`  
**Purpose:** Authenticate via OAuth provider.  
**User Action:** Guest clicks "Sign in with Google".  
**System Process:**
1. Frontend calls `supabase.auth.signInWithOAuth({ provider })`
2. User redirected to provider, then back to LUMI
3. Supabase creates/updates `auth.users`
4. Trigger ensures `profiles` and `user_roles` exist
5. Frontend syncs avatar via `/api/v1/protected/sync-avatar`
**Input:** OAuth provider name.  
**Output:** Authenticated session, profile with avatar.  
**Status:** Implemented.

**Function:** `POST /auth/reset-password`  
**Purpose:** Initiate password reset.  
**User Action:** Guest enters email on reset form.  
**System Process:** Frontend calls `supabase.auth.resetPasswordForEmail()` with redirect URL.  
**Input:** Email address.  
**Output:** Password reset email dispatched.  
**Status:** Implemented.

**Function:** `POST /auth/update-password`  
**Purpose:** Set new password after reset.  
**User Action:** User enters new password from reset link.  
**System Process:** Frontend calls `supabase.auth.updateUser({ password })`.  
**Input:** New password.  
**Output:** Updated user credentials.  
**Status:** Implemented.

**Function:** `GET /api/v1/protected/me`  
**Purpose:** Retrieve current authenticated user's basic info.  
**User Action:** Page load or auth check.  
**System Process:** Backend extracts JWT, verifies with `supabase_jwt_secret`, returns user payload.  
**Input:** Bearer token.  
**Output:** User ID, email, metadata.  
**Status:** Implemented.

**Function:** `GET /api/v1/protected/profile`  
**Purpose:** Fetch extended user profile.  
**User Action:** Dashboard page loads.  
**System Process:** Backend queries `profiles` table by user ID.  
**Input:** Bearer token → user ID.  
**Output:** Full name, avatar URL, organization, location, preferred municipality, plan, is_active.  
**Status:** Implemented.

**Function:** `PUT /api/v1/protected/profile`  
**Purpose:** Update user profile fields.  
**User Action:** User edits profile form.  
**System Process:** Validate input → update `profiles` row.  
**Input:** Full name, organization, location, preferred_municipality_id.  
**Output:** Updated profile record.  
**Status:** Implemented.

**Function:** `POST /api/v1/protected/sync-avatar`  
**Purpose:** Sync OAuth avatar from auth metadata to `profiles`.  
**User Action:** Automatic on login.  
**System Process:** Read `auth.users.raw_user_meta_data` → extract avatar → update `profiles.avatar_url`.  
**Input:** Bearer token.  
**Output:** Updated avatar URL.  
**Status:** Implemented.

---

### 3.2 Dashboard Functions

**Function:** `Dashboard Page Load`  
**Purpose:** Display personalized user dashboard.  
**User Action:** Registered user navigates to `/dashboard`.  
**System Process:**
1. Fetch profile from `/api/v1/protected/profile`
2. Fetch saved simulations from `saved_simulations` (Supabase RLS-filtered)
3. Fetch saved locations/preferred municipality
4. If municipality selected, fetch solar, wind, hydro, geothermal scores in parallel
5. Calculate composite score average
**Input:** User ID, optional municipality ID.  
**Output:** Profile card, simulation list, composite score gauge, navigation buttons.  
**Status:** Implemented.

**Function:** `Save Simulation` (frontend + backend)  
**Purpose:** Persist an EcoSim run for later review.  
**User Action:** User clicks "Save Simulation" after EcoSim run.  
**System Process:** Frontend calls `supabase.from('saved_simulations').insert()` with user_id, municipality_id, inputs, results.  
**Input:** Municipality ID, simulation inputs JSON, results JSON.  
**Output:** New row in `saved_simulations`.  
**Status:** Implemented.

---

### 3.3 EcoSim Functions

**Function:** `GET /api/v1/ecosim/municipalities`  
**Purpose:** List all Philippine municipalities for dropdown selection.  
**User Action:** User opens municipality selector in EcoSim.  
**System Process:** Query `municipalities` table (name, municipality_id), sort alphabetically, limit 20,000.  
**Input:** None.  
**Output:** Array of `{ municipality_id, name }`.  
**Status:** Implemented.

**Function:** `POST /api/v1/ecosim/simulate`  
**Purpose:** Run renewable energy simulation for a household.  
**User Action:** User selects municipality, inputs bill amount, rate, savings target.  
**System Process:**
1. Retrieve municipality climate averages from `municipality_climate_monthly`
2. Calculate solar output (`solar_output_calc.py`)
3. Calculate wind output (`wind_output_calc.py`)
4. Calculate hydro output (`hydro_output_calc.py`)
5. Retrieve geothermal output (`geothermal_output` table or on-the-fly)
6. Calculate consumption from bill amount
7. Compute costs, savings, payback, CO2 reduction
8. Optionally include AI recommendation and RAG pricing context
**Input:** Municipality name, house type, monthly bill, electricity rate, desired savings %, optional AI/RAG flags.  
**Output:** Detailed simulation JSON with all four energy types, financial projections, suitability scores.  
**Status:** Implemented.

**Function:** `GET /api/v1/ecosim/results/{municipality_id}` (implied by frontend service `getEcosim`)  
**Purpose:** Retrieve previous simulation results for a municipality.  
**User Action:** Dashboard loads saved simulations.  
**System Process:** Fetch from `saved_simulations` or re-run calculation.  
**Input:** Municipality ID.  
**Output:** Simulation results.  
**Status:** Partially implemented — persistence exists; dedicated results endpoint is implicit.

---

### 3.4 EnergyHub Functions

**Function:** `GET /api/v1/energyhub/overview`  
**Purpose:** Get latest national energy statistics.  
**User Action:** User opens EnergyHub page.  
**System Process:** Fetch latest year from `national_energy_annual` + ML predictor latest stats.  
**Input:** None.  
**Output:** Total consumption, residential consumption, peak demand, generation mix.  
**Status:** Implemented.

**Function:** `GET /api/v1/energyhub/forecast`  
**Purpose:** Get ML forecast for a target variable.  
**User Action:** User selects "Forecast" view or chart.  
**System Process:** Load pre-computed ARIMA CSV → extract forecast series → return with confidence intervals.  
**Input:** Target variable (`total_consumption_gwh` or `peak_demand_mw`), optional horizon.  
**Output:** Forecast array (year, predicted value, lower, upper).  
**Status:** Implemented.

**Function:** `GET /api/v1/energyhub/trends`  
**Purpose:** Get multi-year historical trends.  
**User Action:** User views "Trends" chart.  
**System Process:** Query `national_energy_annual` for year range → return time series.  
**Input:** Year range, metric selection.  
**Output:** Historical data array for charting.  
**Status:** Implemented.

**Function:** `GET /api/v1/energyhub/map`  
**Purpose:** Get choropleth map data for a renewable metric.  
**User Action:** User selects metric and geographic level on map.  
**System Process:**
1. Check Redis cache for `lumi:suitability:{type}:{level}`
2. If cache miss, query `municipalities` + suitability tables
3. Aggregate to province level if requested
4. Cache result in Redis (TTL 1 hour)
**Input:** Renewable type (solar, wind, hydro, geothermal, composite), geographic level (municipality, province).  
**Output:** Array of geo-located scores with classification.  
**Status:** Implemented.

**Function:** `GET /api/v1/energyhub/sources`  
**Purpose:** Get energy source breakdown by technology.  
**User Action:** User views "Sources" pie/bar chart.  
**System Process:** Aggregate `national_energy_annual` or DOE data by source type.  
**Input:** Year.  
**Output:** Percentages per source (coal, natural gas, renewable, hydro, geothermal, wind, solar, biomass).  
**Status:** Implemented.

**Function:** `GET /api/v1/energyhub/grid`  
**Purpose:** Get grid ownership breakdown.  
**User Action:** User views grid breakdown chart.  
**System Process:** Aggregate by ownership category.  
**Input:** Year.  
**Output:** Private vs. government vs. cooperative percentages.  
**Status:** Implemented.

**Function:** `POST /api/v1/energyhub/ai-insight`  
**Purpose:** Generate AI insight for a chart or dataset.  
**User Action:** User clicks "Analyze with AI" on a chart.  
**System Process:**
1. Serialize chart data
2. Check `chart_ai_insights` cache (by chart type + data hash)
3. If cache miss, assemble prompt with chart context
4. Call LLM (Gemini/Groq)
5. Sanitize and structure response
6. Cache result in `chart_ai_insights`
**Input:** Chart type, chart data JSON.  
**Output:** AI-generated insight text (observation, interpretation, recommendation, reason).  
**Status:** Implemented.

**Function:** `POST /api/v1/energyhub/chart-analysis`  
**Purpose:** Analyze a specific chart with natural language query.  
**User Action:** User asks a question about a visible chart.  
**System Process:** Combine chart data + user question → LLM prompt → return analysis.  
**Input:** Chart data, user question text.  
**Output:** Natural language analysis.  
**Status:** Implemented.

**Function:** `GET /api/v1/energyhub/model-comparison`  
**Purpose:** Compare forecast model performance.  
**User Action:** User views model accuracy metrics.  
**System Process:** Read `ml_model_registry` entries → compute MAE/RMSE.  
**Input:** Target variable.  
**Output:** Model comparison table (model name, version, MAE, RMSE, train date).  
**Status:** Partially implemented — registry exists, endpoint returns model metadata.

---

### 3.5 Geothermal Analysis Functions

**Function:** `GET /api/v1/geothermal/plants`  
**Purpose:** List all geothermal power plants in the Philippines.  
**User Action:** User views geothermal plant directory.  
**System Process:** Read from Supabase table or local dataset (`Geothermal-Power-Tracker-March-2026-Final.xlsx`).  
**Input:** None.  
**Output:** Plant list (name, location, capacity MW, status, coordinates).  
**Status:** Implemented.

**Function:** `GET /api/v1/geothermal/analysis/{municipality_name}`  
**Purpose:** Detailed geothermal suitability and output for a municipality.  
**User Action:** User searches municipality in geothermal explorer.  
**System Process:**
1. Find municipality coordinates
2. Check `geothermal_suitability` + `geothermal_output` tables
3. If missing, run on-the-fly computation (`geothermal/features.py`)
4. Return score, classification, reservoir temp, power estimates
**Input:** Municipality name.  
**Output:** Geothermal analysis JSON (suitability_score, classification, reservoir_temperature_c, thermal_power_mw, electric_power_mw, annual_energy_gwh, confidence, source).  
**Status:** Implemented.

**Function:** `GET /api/v1/geothermal/ecosim-params/{municipality_name}`  
**Purpose:** Retrieve EcoSim-specific geothermal parameters for a municipality.  
**User Action:** EcoSim page requests geothermal data for simulation.  
**System Process:** Fetch from `geothermal_output` or compute fallback values.  
**Input:** Municipality name.  
**Output:** Simplified geothermal parameters for EcoSim integration.  
**Status:** Implemented.

**Function:** `GET /api/v1/geothermal/province-summary`  
**Purpose:** Get province-level aggregated geothermal summary.  
**User Action:** EnergyHub dashboard displays geothermal regional summary.  
**System Process:** Aggregate `geothermal_output` by province via `municipalities` join.  
**Input:** Optional province filter.  
**Output:** Province summary with plant counts, total capacity, average suitability.  
**Status:** Implemented.

---

### 3.6 AI Chat Assistant Functions

**Function:** `POST /api/v1/chat/send`  
**Purpose:** Send a message to the AI assistant and receive a RAG-enhanced response.  
**User Action:** User types a question in the chat interface and clicks send.  
**System Process:**
1. Receive user message + optional session ID
2. Embed query using `SentenceTransformer` (`all-MiniLM-L6-v2`)
3. Search FAISS index for top-k relevant knowledge chunks
4. Rank and filter chunks by similarity score
5. Assemble prompt with system persona + retrieved context + source metadata
6. Call Groq API (Llama 3 or equivalent) with assembled prompt
7. Receive raw LLM response
8. Sanitize response (`llm_sanitizer.py`: strip fences, JSON, normalize whitespace)
9. Extract prescriptive structure (observation, interpretation, recommendation, reason)
10. Format citations from chunk source metadata
11. Return structured response to frontend
**Input:** User message text, optional chat history, optional session ID.  
**Output:** AI response text, source citations array, structured insight object.  
**Status:** Implemented.

**Function:** `GET /api/v1/chat/sessions`  
**Purpose:** List user's chat sessions.  
**User Action:** User opens chat history sidebar.  
**System Process:** Query `chat_sessions` by user_id (RLS-protected).  
**Input:** Bearer token.  
**Output:** Array of session objects (id, title, created_at, is_flagged).  
**Status:** Partially implemented — database schema exists, endpoint structure present but skipped in MVP public mode.

**Function:** `GET /api/v1/chat/sessions/{session_id}`  
**Purpose:** Get messages for a specific chat session.  
**User Action:** User selects a chat session from history.  
**System Process:** Query `chat_messages` joined with `chat_sessions` (ownership verified via RLS).  
**Input:** Session UUID.  
**Output:** Array of messages (role, content, created_at).  
**Status:** Partially implemented — schema exists, MVP uses in-memory state.

---

### 3.7 Admin & System Management Functions

**Function:** `GET /api/v1/admin/users`  
**Purpose:** List all registered users with profile and role info.  
**User Action:** Admin opens User Management page.  
**System Process:** Verify admin role → query `profiles` + `user_roles` + Supabase Auth metadata.  
**Input:** Admin bearer token, optional filters (role, plan, active status).  
**Output:** Paginated user list with id, email, full_name, role, plan, is_active, created_at.  
**Status:** Implemented.

**Function:** `POST /api/v1/admin/users`  
**Purpose:** Create a new user via admin action.  
**User Action:** Admin clicks "Create User" and fills form.  
**System Process:** Verify admin role → call Supabase Auth Admin API → create user → trigger auto-creates profile/role.  
**Input:** Email, password, role, plan, full_name.  
**Output:** New user record confirmation.  
**Status:** Implemented.

**Function:** `GET /api/v1/admin/users/{user_id}`  
**Purpose:** Get detailed info for a single user.  
**User Action:** Admin clicks on a user row.  
**System Process:** Verify admin role → fetch profile, role, simulations, chat sessions.  
**Input:** Target user UUID.  
**Output:** User detail object with related records.  
**Status:** Implemented.

**Function:** `PUT /api/v1/admin/users/{user_id}/ban`  
**Purpose:** Soft-delete (ban) a user by setting `is_active = false`.  
**User Action:** Admin clicks "Ban User".  
**System Process:** Verify admin role → update `profiles.is_active = false` → log to `admin_audit_log`.  
**Input:** Target user UUID, reason.  
**Output:** Confirmation, audit log entry.  
**Status:** Implemented.

**Function:** `PUT /api/v1/admin/users/{user_id}/unban`  
**Purpose:** Re-enable a banned user.  
**User Action:** Admin clicks "Unban User".  
**System Process:** Verify admin role → update `profiles.is_active = true` → log to `admin_audit_log`.  
**Input:** Target user UUID.  
**Output:** Confirmation, audit log entry.  
**Status:** Implemented.

**Function:** `PUT /api/v1/admin/users/{user_id}/role`  
**Purpose:** Change a user's role.  
**User Action:** Admin selects new role from dropdown.  
**System Process:** Verify admin role → update `user_roles.role` → update `profiles.plan` to premium if admin/dev → log action.  
**Input:** Target user UUID, new role (`user`, `admin`, `dev`).  
**Output:** Confirmation, updated role record.  
**Status:** Implemented.

**Function:** `PUT /api/v1/admin/users/{user_id}/plan`  
**Purpose:** Change a user's subscription plan.  
**User Action:** Admin selects new plan from dropdown.  
**System Process:** Verify admin role → update `profiles.plan` → log action.  
**Input:** Target user UUID, new plan (`free`, `premium`).  
**Output:** Confirmation, updated plan.  
**Status:** Implemented.

**Function:** `GET /api/v1/admin/users/{user_id}/simulations`  
**Purpose:** View all simulations created by a user.  
**User Action:** Admin clicks "View Simulations" on user detail.  
**System Process:** Query `saved_simulations` by user_id.  
**Input:** Target user UUID.  
**Output:** Array of simulation records.  
**Status:** Implemented.

**Function:** `GET /api/v1/admin/analytics`  
**Purpose:** Get system-wide usage analytics.  
**User Action:** Admin opens Analytics dashboard.  
**System Process:** Aggregate counts from `profiles`, `saved_simulations`, `chat_sessions`, `auth.users`.  
**Input:** Admin bearer token, date range.  
**Output:** Metrics JSON (total users, active users, simulation count, chat count, growth trends).  
**Status:** Implemented.

**Function:** `GET /api/v1/admin/config`  
**Purpose:** Read current system configuration.  
**User Action:** Admin opens System Config page.  
**System Process:** Read `system_config` key-value store.  
**Input:** None.  
**Output:** Global config JSON (chatbot_enabled, maintenance_mode, free_chat_limit, free_sim_limit).  
**Status:** Implemented.

**Function:** `PUT /api/v1/admin/config`  
**Purpose:** Update system configuration.  
**User Action:** Admin toggles a system setting.  
**System Process:** Verify admin role → upsert `system_config` row → log to audit log.  
**Input:** Config key, new JSON value.  
**Output:** Updated config.  
**Status:** Implemented.

**Function:** `GET /api/v1/admin/moderation`  
**Purpose:** List flagged chat sessions for moderation review.  
**User Action:** Admin opens Chat Moderation page.  
**System Process:** Query `chat_sessions` where `is_flagged = true`.  
**Input:** Admin bearer token.  
**Output:** Flagged session list with user info and message previews.  
**Status:** Partially implemented — schema exists, moderation UI present, flagging logic basic.

---

### 3.8 Suitability Engine Functions

**Function:** `municipality_suitability_builder.compute_all()`  
**Purpose:** Batch compute suitability scores for all municipalities.  
**User Action:** System script or admin trigger.  
**System Process:**
1. Iterate all municipalities
2. Fetch NASA POWER climate averages per municipality
3. Calculate solar score (irradiance-based normalization)
4. Calculate wind score (wind speed + air density normalization)
5. Calculate hydro score (terrain slope + rainfall + runoff potential)
6. Calculate geothermal score (heat flow + fault/volcano proximity)
7. Compute composite score (weighted average)
8. Classify each score (`get_suitability_classification` SQL function)
9. Upsert results to `municipalities`, `hydropower_suitability`, `geothermal_suitability`
10. Invalidate and repopulate Redis cache
**Input:** Full municipality list, climate data, terrain data, heat flow data.  
**Output:** Updated database tables, Redis cache entries.  
**Status:** Implemented.

**Function:** `municipality_suitability_builder.compute_single(municipality_id)`  
**Purpose:** Compute suitability for a single municipality on demand.  
**User Action:** System fallback when cached data is missing.  
**System Process:** Same as batch but for one municipality.  
**Input:** Municipality ID.  
**Output:** Single municipality score set.  
**Status:** Implemented.

---

### 3.9 Machine Learning Forecasting Functions

**Function:** `EnergyHubML.load_forecasts()`  
**Purpose:** Load pre-computed ARIMA forecast artifacts from CSV.  
**User Action:** System startup or first API request.  
**System Process:** Read `DOE_Data_Extracted/` CSV files containing ARIMA(1,1,1) forecast series.  
**Input:** File path to forecast CSV.  
**Output:** Pandas DataFrame with year, predicted value, lower bound, upper bound.  
**Status:** Implemented.

**Function:** `EnergyHubML.get_forecast(target_variable, year)`  
**Purpose:** Serve a specific forecast value.  
**User Action:** EnergyHub frontend requests forecast data.  
**System Process:** Lookup in loaded DataFrame → return matching row.  
**Input:** Target variable string, forecast year.  
**Output:** Forecast point with confidence interval.  
**Status:** Implemented.

**Function:** `EnergyHubML.get_latest_stats()`  
**Purpose:** Get the most recent actual national energy statistics.  
**User Action:** EnergyHub overview loads.  
**System Process:** Read latest row from historical data CSV.  
**Input:** None.  
**Output:** Latest year consumption, peak demand, generation.  
**Status:** Implemented.

**Function:** `EnergyHubML.get_trends(start_year, end_year)`  
**Purpose:** Get historical trend data for charting.  
**User Action:** User selects year range in EnergyHub trends view.  
**System Process:** Filter historical DataFrame by year range.  
**Input:** Start year, end year, metric.  
**Output:** Time series array for chart rendering.  
**Status:** Implemented.

---

### 3.10 Data ETL & Ingestion Functions

**Function:** `extract_nasa_power.py` (script)  
**Purpose:** Extract climate data from NASA POWER API for all municipalities.  
**User Action:** System scheduled task or manual admin run.  
**System Process:**
1. Load municipality coordinates from `municipalities`
2. Batch-call NASA POWER API ( monthly averages )
3. Parse JSON response
4. Upsert into `municipality_climate_monthly`
**Input:** Municipality coordinates, API key, year range.  
**Output:** Populated `municipality_climate_monthly` table.  
**Status:** Implemented.

**Function:** `clean_scraped_products.py`  
**Purpose:** Clean and normalize raw scraped e-commerce data.  
**User Action:** System pipeline step.  
**System Process:** Parse raw JSON/CSV → normalize prices → deduplicate → standardize units → write `cleaned_products_master.csv`.  
**Input:** Raw scraped data files.  
**Output:** Cleaned product CSV.  
**Status:** Implemented.

**Function:** `rag_knowledge_builder.build_chunks()`  
**Purpose:** Convert all data sources into RAG-ready knowledge chunks.  
**User Action:** System startup (triggered by `main.py` `startup_event`).  
**System Process:**
1. Load cleaned product data
2. Load DOE national energy statistics
3. Load NASA POWER municipality climate averages
4. Load terrain metrics
5. Load hydropower and geothermal suitability data
6. Aggregate into semantic chunks by category (equipment_cost, installation_cost, maintenance_cost, components, capacity_info, national_energy_statistics, municipality_climate, terrain_metrics)
7. Enrich each chunk with source metadata (title, URL, organization)
8. Write to `all_chunks.json`
**Input:** All cleaned data files and database tables.  
**Output:** `all_chunks.json` with structured knowledge chunks.  
**Status:** Implemented.

**Function:** `rag_pipeline.ensure_index_built()`  
**Purpose:** Build or refresh the FAISS vector index from knowledge chunks.  
**User Action:** FastAPI startup event (`main.py`).  
**System Process:**
1. Check if `all_chunks.json` and FAISS index files exist and are up-to-date
2. If stale or missing, load chunks
3. Embed each chunk using `SentenceTransformer`
4. Build FAISS flat index (L2 distance)
5. Persist index and chunk mapping to disk
**Input:** `all_chunks.json`, embedding model.  
**Output:** `faiss_index.bin`, `chunk_map.json`.  
**Status:** Implemented.

**Function:** `terrain_pipeline`  
**Purpose:** Compute terrain metrics for all municipalities from DEM data.  
**User Action:** Admin script execution.  
**System Process:**
1. Load PHL DEM (Digital Elevation Model) raster data
2. Extract elevation, slope, ruggedness per municipality polygon
3. Compute watershed gradient, hydraulic head, runoff potential
4. Write `municipality_terrain_metrics.csv`
**Input:** DEM raster (`PHL_msk_alt.grd`), municipality boundary GeoJSON.  
**Output:** Terrain metrics CSV/Supabase table.  
**Status:** Implemented.

---

## Part 4: System Process Flow Analysis

### 4.1 User Registration / Login Flow

**Start:** Guest visits LUMI landing page.

**Process Steps:**
1. Guest clicks "Sign Up" or "Login"
2. Frontend renders auth form (email/password) or OAuth button
3. For email registration:
   - Frontend calls `supabase.auth.signUp({ email, password })`
   - Supabase Auth inserts user into `auth.users`
   - Database trigger `on_auth_user_created` fires
   - Trigger auto-inserts `profiles` row (with `full_name` from metadata, plan=`free`, is_active=`true`)
   - Trigger auto-inserts `user_roles` row (role=`user`)
4. For login:
   - Frontend calls `supabase.auth.signInWithPassword({ email, password })`
   - Supabase returns JWT session object
5. Frontend stores session in React context (`AuthContext`)
6. Frontend fetches role from `user_roles` table
7. If OAuth login, frontend calls `/api/v1/protected/sync-avatar`
8. Frontend redirects to Dashboard (if registered) or previous page

**Decision Points:**
- Is email already registered? → Show error
- Is password strong enough? → Frontend validation
- Is email confirmed? (if email confirmation enabled) → Show pending message

**End Result:** Authenticated session established; user can access protected features.

---

### 4.2 Dashboard Usage Flow

**Start:** Registered user navigates to `/dashboard`.

**Process Steps:**
1. `ProtectedRoute` checks for valid session; redirects to login if missing
2. Dashboard component mounts
3. Parallel data fetches:
   - `GET /api/v1/protected/profile` → profile data
   - `supabase.from('saved_simulations').select()` → simulation history (RLS-filtered)
   - `supabase.from('profiles').select('preferred_municipality_id')` → saved location
4. If preferred municipality exists:
   - Parallel fetches to `solar_suitability`, `wind_suitability`, `hydropower_suitability`, `geothermal_suitability`
   - Calculate composite score = average of available scores
5. Render profile card, simulation list, composite score gauge
6. Display quick-action buttons (EcoSim, AI Chat, EnergyHub)

**Decision Points:**
- Is user authenticated? → Route guard
- Does user have saved simulations? → Show list or empty state
- Does user have preferred municipality? → Show composite score or prompt selection

**End Result:** Personalized dashboard displayed with user data and navigation.

---

### 4.3 Renewable Assessment Flow (EcoSim)

**Start:** User navigates to `/ecosim`.

**Process Steps:**
1. EcoSim page mounts; fetch municipality list from `GET /api/v1/ecosim/municipalities`
2. User selects municipality from dropdown
3. User inputs monthly bill, electricity rate, desired savings %
4. User clicks "Simulate"
5. Frontend calls `POST /api/v1/ecosim/simulate` with parameters
6. Backend processes:
   - Fetch municipality climate averages from `municipality_climate_monthly`
   - `solar_output_calc.py`: Calculate temperature factor, dust loss, degradation, performance ratio, then solar output (kWh/month)
   - `wind_output_calc.py`: Load average rotor radius and power coefficient from scraped wind products → calculate wind power using Betz-limit physics
   - `hydro_output_calc.py`: Estimate runoff coefficient from slope → calculate design flow rate → estimate hydropower output
   - `geothermal/features.py` or `geothermal_output` table: Retrieve or compute geothermal suitability and output
   - `consumption_calculator()`: Convert bill to monthly/daily kWh and target consumption
   - Aggregate financials (cost per kWh for each source, payback period, CO2 savings)
   - If `include_ai=true`, call LLM for prescriptive recommendation
   - If `use_rag=true`, retrieve product pricing context from RAG pipeline
7. Backend returns simulation results JSON
8. Frontend renders results cards (Solar, Wind, Hydro, Geothermal) with scores, outputs, costs, savings
9. If authenticated, user can click "Save Simulation" → insert into `saved_simulations`

**Decision Points:**
- Is municipality valid? → 404 if not found
- Is climate data available? → Fallback to estimation or error
- Is user authenticated? → Enable/disable save button
- Did user request AI/RAG? → Include enhanced recommendation text

**End Result:** Comprehensive renewable energy simulation displayed with actionable recommendations.

---

### 4.4 Choropleth Map Flow

**Start:** User navigates to EnergyHub and clicks "Map" tab.

**Process Steps:**
1. EnergyHub page mounts; map component initializes with Philippine GeoJSON
2. User selects renewable metric (solar/wind/hydro/geothermal/composite)
3. User selects geographic level (municipality or province)
4. Frontend calls `GET /api/v1/energyhub/map?type={type}&level={level}`
5. Backend checks Redis cache key `lumi:suitability:{type}:{level}`
6. If cache hit:
   - Return cached data immediately
7. If cache miss:
   - Query `municipalities` table for coordinates and scores
   - If province level, aggregate municipality scores by province
   - Join with GeoJSON-compatible location data
   - Store result in Redis with 1-hour TTL
8. Frontend receives array of `{ id, name, lat, lon, score, classification }`
9. Frontend colors GeoJSON regions based on score (e.g., green = excellent, red = unsuitable)
10. Hover tooltip shows municipality name, score, and classification

**Decision Points:**
- Is data cached in Redis? → Fast path vs. database query
- Is score NULL? → Render as gray (no data)
- Municipality or province level? → Aggregation logic differs

**End Result:** Interactive choropleth map visualizing renewable energy suitability across the Philippines.

---

### 4.5 Forecasting Flow

**Start:** User navigates to EnergyHub and selects "Forecast" view.

**Process Steps:**
1. Frontend calls `GET /api/v1/energyhub/forecast?target=total_consumption_gwh`
2. Backend loads pre-computed ARIMA CSV artifact via `EnergyHubML.load_forecasts()`
3. Backend extracts forecast series (year, predicted, lower, upper)
4. Backend optionally queries `forecast_cache` for additional cached predictions
5. Backend returns forecast JSON array
6. Frontend renders line chart with historical actuals + forecast line + confidence band
7. User can toggle between consumption and peak demand forecasts
8. User can view model comparison via `GET /api/v1/energyhub/model-comparison`

**Decision Points:**
- Is forecast CSV available? → Load from file or return error
- Is target variable valid? → Validate against supported list
- Should we cache this response? → Store in `forecast_cache` table

**End Result:** Time-series forecast chart with confidence intervals displayed.

---

### 4.6 EcoSim Simulation Flow (Detailed)

**Start:** User submits EcoSim form.

**Process Steps:**
1. Validate input (bill > 0, rate > 0, savings 0-100%)
2. Backend retrieves municipality data:
   - `municipalities` table for coordinates
   - `municipality_climate_monthly` for climate averages
3. Calculate household consumption:
   - monthly_kwh = bill / rate
   - daily_kwh = monthly_kwh / days_in_month
   - target_kwh = monthly_kwh * (1 - savings)
4. For each energy type:
   - **Solar:** irradiance → performance ratio (temp, dust, humidity, degradation) → panel output → monthly output → cost vs. target
   - **Wind:** ws10m → air density → swept area → Betz-limited power → capacity factor → monthly energy → turbine count estimation
   - **Hydro:** rainfall → runoff coefficient (from slope) → design flow → hydraulic head → power → monthly energy
   - **Geothermal:** reservoir temp → thermal power → electric power (binary/flash efficiency) → annual GWh → scale to household
5. Financial analysis:
   - Cost per kWh for each source (using scraped product pricing or industry standard)
   - Installation cost estimate
   - Payback period calculation
   - CO2 offset (kg CO2/kWh avoided grid emissions)
6. AI enhancement (optional):
   - Assemble prompt with simulation results
   - Call LLM for prescriptive recommendation
   - Structure into observation, interpretation, recommendation, reason
7. Format and return JSON response

**Decision Points:**
- Is municipality in database? → 404 if not
- Is climate data complete? → Use defaults or partial calculation
- Which energy types are viable? → Filter by score threshold
- Include AI? → Conditional LLM call

**End Result:** Detailed simulation report with energy outputs, financial projections, and AI recommendations.

---

### 4.7 AI Recommendation Flow (Chat)

**Start:** User types a question in LUMI AI Chat and presses Enter.

**Process Steps:**
1. Frontend adds user message to chat state
2. Frontend calls `POST /api/v1/chat/send` with message text
3. Backend receives message
4. RAG Retrieval:
   - Embed query: `SentenceTransformer.encode(message)`
   - Search FAISS index: `index.search(query_embedding, k=5)`
   - Retrieve top-5 chunk texts and source metadata
5. Prompt Assembly:
   - System persona: "You are LUMI, a renewable energy assistant..."
   - Retrieved context: chunk texts with source labels
   - User question
   - Instructions: "Answer based on context. Cite sources. Format as observation, interpretation, recommendation, reason."
6. LLM Generation:
   - Call Groq API with assembled prompt (model: Llama 3, temperature ~0.7)
   - Receive raw text response
7. Sanitization:
   - `strip_markdown_fences()` → remove ```json wrappers
   - `strip_json_wrappers()` → extract text from JSON objects
   - `strip_key_value_formatting()` → remove key-value line noise
   - `normalize_whitespace()` → collapse blank lines, unescape chars
8. Structure Extraction:
   - `extract_prescriptive_recommendation()` → regex for Observation, Interpretation, Recommendation, Reason sections
   - If no sections found, put full text in recommendation field
9. Citation Formatting:
   - Map retrieved chunk sources to `{ title, url, org }` objects
   - Append "Sources" section to response
10. Backend returns structured response JSON
11. Frontend renders AI message with formatted sections and clickable citations

**Decision Points:**
- Is FAISS index ready? → Fallback to general knowledge if not
- Are any chunks relevant? → Filter by similarity threshold
- Did LLM return malformed JSON? → Sanitize pipeline handles it
- Is user authenticated? → Skip session persistence in MVP

**End Result:** Contextual AI response with structured insights and cited sources.

---

### 4.8 Report / Export Flow

**Start:** User wants to export simulation or analysis results.

**Process Steps:**
1. User clicks "Export" or "Download" button on Dashboard, EcoSim, or EnergyHub
2. Frontend generates report content:
   - For EcoSim: compile simulation results JSON into formatted text
   - For EnergyHub: compile chart data and AI insights
3. Frontend triggers browser download as `.txt` or `.json` file
4. *(Partially implemented)* No backend PDF generation or email delivery is currently implemented.

**Decision Points:**
- What format? → JSON or plain text (frontend-only)
- Is data available? → Disable export if no results

**End Result:** Client-side file download with raw data.
**Status:** Partially implemented — basic client-side JSON/txt export only; no PDF or server-side rendering.

---

## Part 5: Data Flow Diagram Information

### 5.1 External Entities

| Entity | Description | Data Provided | Data Received |
|---|---|---|---|
| **Guest User** | Unauthenticated visitor | Browse requests, simulation inputs, chat messages | Web pages, public data, AI responses |
| **Registered User** | Authenticated user | Profile updates, simulation save requests, chat messages | Dashboard, saved items, personalized scores |
| **Administrator** | System manager | User management commands, config changes, moderation actions | User lists, analytics, audit logs |
| **NASA POWER API** | Climate data provider | Temperature, irradiance, wind, precipitation, humidity, air density | API request coordinates |
| **DOE Philippines** | Energy statistics provider | National energy annual data, generation mix | — |
| **Global Energy Monitor / IHFC** | Geothermal data provider | Plant locations, heat flow measurements | — |
| **E-commerce Platforms** | Product pricing data | Renewable component listings, prices | Scraper requests |
| **Groq / Gemini API** | LLM service provider | Generated text responses | Prompts with RAG context |

### 5.2 Processes

#### Level 0 DFD: System Overview

**Process:** LUMI System  
**Input Data:** User queries, simulation parameters, admin commands, external climate/energy/pricing data.  
**Output Data:** Web pages, simulation results, AI responses, forecasts, map data, admin reports.  
**Connected External Entities:** Guest User, Registered User, Administrator, NASA POWER, DOE, GEM/IHFC, E-commerce APIs, Groq/Gemini.

#### Level 1 DFD: Major Process Breakdown

**Process 1.0 — Authentication & Session Management**  
**Input:** Registration/login credentials, OAuth tokens, password reset requests.  
**Output:** JWT sessions, user profiles, role assignments.  
**Connected Data Stores:** `auth.users`, `profiles`, `user_roles`.

**Process 2.0 — Dashboard & Profile Services**  
**Input:** User ID, profile updates, municipality selections.  
**Output:** Profile data, saved simulations, composite suitability scores.  
**Connected Data Stores:** `profiles`, `saved_simulations`, `solar_suitability`, `wind_suitability`, `hydropower_suitability`, `geothermal_suitability`, `municipalities`.

**Process 3.0 — EcoSim Simulation Engine**  
**Input:** Municipality name, bill amount, electricity rate, savings target.  
**Output:** Simulation results (energy outputs, costs, payback, CO2).  
**Connected Data Stores:** `municipalities`, `municipality_climate_monthly`, `hydropower_suitability`, `geothermal_output`, `geothermal_suitability`.

**Process 4.0 — EnergyHub Analytics**  
**Input:** Metric type, year range, geographic level, chart data.  
**Output:** Overview stats, forecast series, trend data, choropleth data, source breakdown, AI insights.  
**Connected Data Stores:** `national_energy_annual`, `municipalities`, `forecast_cache`, `ml_model_registry`, `chart_ai_insights`, Redis cache.

**Process 5.0 — Geothermal Analysis**  
**Input:** Municipality name/coordinates.  
**Output:** Plant list, suitability score, output estimates.  
**Connected Data Stores:** `geothermal_suitability`, `geothermal_output`, `municipalities`.

**Process 6.0 — AI Chat & RAG**  
**Input:** Natural language query.  
**Output:** AI response with citations.  
**Connected Data Stores:** FAISS index, `all_chunks.json`, `chat_sessions` (partial), `chat_messages` (partial).

**Process 7.0 — Admin & System Management**  
**Input:** Admin commands (ban, role change, config update).  
**Output:** User lists, analytics reports, system config.  
**Connected Data Stores:** `profiles`, `user_roles`, `admin_audit_log`, `system_config`, `saved_simulations`, `chat_sessions`.

**Process 8.0 — Suitability Computation**  
**Input:** Municipality coordinates, climate data, terrain data.  
**Output:** Suitability scores and classifications.  
**Connected Data Stores:** `municipalities`, `hydropower_suitability`, `geothermal_suitability`, Redis cache.

**Process 9.0 — ML Forecasting**  
**Input:** Target variable, forecast year.  
**Output:** Forecast values with confidence intervals.  
**Connected Data Stores:** `forecast_cache`, `ml_model_registry`, `national_energy_annual`.

**Process 10.0 — Data ETL & Ingestion**  
**Input:** Raw external files, API responses, scraped HTML.  
**Output:** Cleaned tables, FAISS index, knowledge chunks.  
**Connected Data Stores:** All database tables, FAISS index files.

#### Level 2 DFD: Detailed Subprocesses (Selected Examples)

**Process 6.1 — Query Embedding**  
**Input:** User query text.  
**Output:** Query embedding vector (384-d float array).  
**Connected Components:** `SentenceTransformer` model.

**Process 6.2 — FAISS Retrieval**  
**Input:** Query embedding vector.  
**Output:** Top-k chunk indices and distances.  
**Connected Data Stores:** `faiss_index.bin`.

**Process 6.3 — Prompt Assembly**  
**Input:** User query, retrieved chunks, source metadata.  
**Output:** Formatted prompt string for LLM.  
**Connected Components:** `rag_knowledge_builder.py` source map.

**Process 6.4 — LLM Generation**  
**Input:** Assembled prompt.  
**Output:** Raw LLM text.  
**Connected External Entities:** Groq API, Gemini API.

**Process 6.5 — Response Sanitization**  
**Input:** Raw LLM text.  
**Output:** Clean plain text with structured sections.  
**Connected Components:** `llm_sanitizer.py`.

**Process 3.1 — Solar Calculation**  
**Input:** Panel wattage, count, irradiance, temperature, humidity, wind speed.  
**Output:** Daily/monthly solar output, solar score.  
**Connected Components:** `solar_output_calc.py`.

**Process 3.2 — Wind Calculation**  
**Input:** Wind speed, air density, rotor radius, power coefficient, capacity factor.  
**Output:** Wind power, monthly energy.  
**Connected Components:** `wind_output_calc.py`, scraped product averages.

**Process 3.3 — Hydro Calculation**  
**Input:** Rainfall, slope, runoff potential, watershed gradient, gravity flow.  
**Output:** Design flow rate, hydropower output.  
**Connected Components:** `hydro_output_calc.py`.

**Process 3.4 — Geothermal Calculation**  
**Input:** Surface temperature, latitude, longitude.  
**Output:** Suitability score, reservoir temperature, thermal/electric power.  
**Connected Components:** `geothermal/features.py`, IHFC heat flow data, fault/volcano datasets.

### 5.3 Data Stores

| Data Store | Type | Description |
|---|---|---|
| **Supabase PostgreSQL Database** | Relational DB | Primary data store for all application tables |
| **Redis (Upstash)** | Key-Value Cache | Suitability map cache, session store |
| **FAISS Index** | Vector Index | Semantic search index for RAG knowledge chunks |
| **Local CSV/JSON Files** | File Storage | ML forecast artifacts, knowledge chunks, scraped data |
| **Supabase Auth** | Identity Store | JWT-based user authentication and identity |
| **Supabase Storage** | Object Storage | Avatar images in `avatars` bucket |

### 5.4 Data Flows

| Flow | From | To | Data |
|---|---|---|---|
| F1 | Guest/Registered User | Auth Process | Credentials, OAuth token |
| F2 | Auth Process | Supabase Auth | User creation/login request |
| F3 | Supabase Auth | Auth Process | JWT session, user metadata |
| F4 | Auth Process | `profiles` / `user_roles` | Profile/role records |
| F5 | Registered User | Dashboard Process | Profile update, municipality selection |
| F6 | Dashboard Process | `profiles` | Read/update profile data |
| F7 | Dashboard Process | `saved_simulations` | Read simulation history |
| F8 | User | EcoSim Process | Simulation parameters |
| F9 | EcoSim Process | `municipality_climate_monthly` | Climate data query |
| F10 | EcoSim Process | Calculation Services | Raw climate/terrain data |
| F11 | Calculation Services | EcoSim Process | Energy output results |
| F12 | EcoSim Process | `saved_simulations` | Save results (if authenticated) |
| F13 | User | EnergyHub Process | Metric/year/level selection |
| F14 | EnergyHub Process | `national_energy_annual` | Historical stats query |
| F15 | EnergyHub Process | `forecast_cache` | Forecast read/write |
| F16 | EnergyHub Process | Redis | Suitability cache read/write |
| F17 | EnergyHub Process | LLM APIs | Chart analysis prompts |
| F18 | User | AI Chat Process | Natural language query |
| F19 | AI Chat Process | FAISS Index | Embedding search |
| F20 | AI Chat Process | Groq/Gemini | Assembled prompt |
| F21 | Groq/Gemini | AI Chat Process | Raw generated text |
| F22 | Admin | Admin Process | Management commands |
| F23 | Admin Process | `admin_audit_log` | Immutable action records |
| F24 | Data ETL Scripts | NASA POWER | Coordinate-based API requests |
| F25 | Data ETL Scripts | Supabase Tables | Bulk insert/update operations |
| F26 | RAG Builder | FAISS Index | Index rebuild/update |

---

## Part 6: Module Interaction Map

### 6.1 High-Level Communication Pattern

```
User Interface (React Frontend)
    ↕ HTTP/JSON (REST API)
API Layer (FastAPI Routers)
    ↕ Internal function calls
Processing Services (Python)
    ↕ SQL / REST / Cache commands
Data Stores (Supabase, Redis, FAISS, Files)
    ↕ Data aggregation / embedding
External Services (NASA POWER, Groq, Gemini)
    ↕ Processed results
Visualization Layer (React + Recharts/Leaflet)
    ↕ Rendered to User
```

### 6.2 Per-Module Communication Details

**Module: Authentication & Identity**
- **Sends to:** Supabase Auth (user creation, login, token verify)
- **Receives from:** Supabase Auth (JWT session, user metadata)
- **Connected To:** `profiles`, `user_roles` (via DB trigger), Frontend AuthContext

**Module: User Dashboard**
- **Sends to:** Protected API (`/protected/profile`), Supabase direct queries
- **Receives from:** Auth module (user ID), EcoSim module (simulation list), Suitability Engine (scores)
- **Connected To:** `profiles`, `saved_simulations`, `solar_suitability`, `wind_suitability`, `hydropower_suitability`, `geothermal_suitability`

**Module: EcoSim**
- **Sends to:** `municipality_climate_monthly`, `geothermal_output`, `geothermal_suitability`, `hydropower_suitability`
- **Receives from:** NASA POWER (via climate table), Calculation Services (solar, wind, hydro, geothermal results), RAG Pipeline (pricing context, optional), LLM Services (AI recommendation, optional)
- **Connected To:** Dashboard (save simulation), EnergyHub (shared municipality data)

**Module: EnergyHub**
- **Sends to:** `national_energy_annual`, `municipalities`, `forecast_cache`, `ml_model_registry`, `chart_ai_insights`, Redis
- **Receives from:** ML Forecasting Service (ARIMA predictions), Suitability Engine (cached map data), LLM Services (AI chart insights)
- **Connected To:** Frontend charting components, Map component

**Module: Geothermal Analysis**
- **Sends to:** `geothermal_suitability`, `geothermal_output`, `municipalities`
- **Receives from:** IHFC heat flow dataset, PHIVOLCS fault/volcano data, NASA POWER temperature (via climate table)
- **Connected To:** EcoSim (parameter retrieval), EnergyHub (province summary)

**Module: AI Chat Assistant**
- **Sends to:** FAISS index (semantic search), Groq API (prompt), Gemini API (fallback)
- **Receives from:** RAG Pipeline (relevant chunks), LLM Sanitizer (cleaned output)
- **Connected To:** Frontend ChatPage, Knowledge Builder (chunk source)

**Module: Admin & System Management**
- **Sends to:** `profiles`, `user_roles`, `admin_audit_log`, `system_config`, Supabase Auth Admin API
- **Receives from:** Auth module (role verification), all user tables
- **Connected To:** Admin frontend pages only

**Module: Suitability Engine**
- **Sends to:** `municipalities`, `hydropower_suitability`, `geothermal_suitability`, Redis
- **Receives from:** NASA POWER (climate data), Terrain Pipeline (elevation, slope), Geothermal datasets (heat flow, faults)
- **Connected To:** EnergyHub (map data source), EcoSim (fallback computation)

**Module: ML Forecasting**
- **Sends to:** `forecast_cache`, `ml_model_registry`
- **Receives from:** DOE historical CSVs, offline ARIMA training notebooks
- **Connected To:** EnergyHub (forecast endpoint)

**Module: Data ETL & Ingestion**
- **Sends to:** All Supabase tables, FAISS index files, local CSV/JSON files
- **Receives from:** NASA POWER API, DOE PDFs/Excel, E-commerce scrapers, DEM raster data
- **Connected To:** Suitability Engine (climate/terrain input), RAG Pipeline (knowledge chunks)

### 6.3 Interaction Matrix

| Sender Module | Receiver Module | Data Sent | Communication Method |
|---|---|---|---|
| Frontend | Auth API | Credentials, token | HTTP POST/GET |
| Auth API | Supabase Auth | User ops | Supabase client SDK |
| Supabase Auth | DB Trigger | New user event | Internal trigger |
| DB Trigger | `profiles` / `user_roles` | Profile/role rows | SQL INSERT |
| Frontend | EcoSim API | Simulation params | HTTP POST |
| EcoSim API | Solar Calc Service | Climate data | Python function call |
| EcoSim API | Wind Calc Service | Climate data | Python function call |
| EcoSim API | Hydro Calc Service | Terrain + rainfall | Python function call |
| EcoSim API | Geothermal Service | Coordinates, temp | Python function call |
| EcoSim API | `saved_simulations` | Results (conditional) | SQL INSERT |
| Frontend | EnergyHub API | Metric selections | HTTP GET |
| EnergyHub API | ML Predictor | Target variable | Python function call |
| EnergyHub API | Redis | Cache key | Redis GET/SETEX |
| EnergyHub API | `national_energy_annual` | Year filter | SQL SELECT |
| EnergyHub API | LLM Service | Chart prompt | HTTP POST to Groq/Gemini |
| Frontend | Chat API | User message | HTTP POST |
| Chat API | RAG Pipeline | Query text | Python function call |
| RAG Pipeline | FAISS Index | Embedding vector | FAISS search |
| Chat API | LLM Service | Assembled prompt | HTTP POST to Groq |
| Chat API | LLM Sanitizer | Raw response | Python function call |
| Admin Frontend | Admin API | Management commands | HTTP GET/PUT/POST |
| Admin API | Supabase Auth Admin | User ops | Admin SDK |
| Admin API | `admin_audit_log` | Action records | SQL INSERT |
| Suitability Engine | Redis | Suitability data | Redis SETEX |
| Data ETL | NASA POWER | Coordinates | HTTP API |
| Data ETL | Supabase Tables | Cleaned data | SQL INSERT/UPDATE |
| RAG Builder | FAISS Index | Embeddings | FAISS build |

---

## Part 7: Database and Data Process Mapping

### 7.1 Core Geographic Tables

**Table:** `regions`  
**Purpose:** Top-level Philippine administrative divisions.  
**Used By Modules:** EnergyHub (regional aggregation), Suitability Engine, Data ETL.  
**Data Stored:** region_id (PK), name, lat, lon.  
**Operations:** Read-only (seeded at setup).

**Table:** `provinces`  
**Purpose:** Provincial administrative divisions within regions.  
**Used By Modules:** EnergyHub (province-level maps), EcoSim, Geothermal Analysis, Suitability Engine.  
**Data Stored:** province_id (PK), region_id (FK), name, lat, lon.  
**Operations:** Read (primary), referenced by `municipalities`.

**Table:** `municipalities`  
**Purpose:** Central geographic entity for all municipal-level analysis. Stores aggregated renewable suitability scores.  
**Used By Modules:** EcoSim, EnergyHub (choropleth), Dashboard, Suitability Engine, Geothermal Analysis, Data ETL.  
**Data Stored:** municipality_id (PK), province_id (FK), name, lat, lon, solar_suitability_score, wind_suitability_score, hydro_suitability_score, geothermal_suitability_score, composite_suitability_score, solar_classification, wind_classification, hydro_classification, geothermal_classification, composite_classification.  
**Operations:** Read (primary), UPDATE (by Suitability Engine batch jobs).

**Table:** `barangays`  
**Purpose:** Barangay (village) level subdivisions within municipalities.  
**Used By Modules:** Geographic reference, potential future micro-level analysis.  
**Data Stored:** barangay_id (PK), municipality_id (FK), name, lat, lon.  
**Operations:** Read-only (seeded at setup).

### 7.2 Climate & Environmental Data Tables

**Table:** `municipality_climate_monthly`  
**Purpose:** Monthly climate averages per municipality from NASA POWER.  
**Used By Modules:** EcoSim (solar, wind, hydro calculations), Suitability Engine, EnergyHub.  
**Data Stored:** municipality_id (FK), year, month, t2m, t2m_max, t2m_min, rh2m, prectotcorr, ws10m, allsky_sfc_sw_dwn, cloud_amt, surface_pressure, elevation, rhoa, source, created_at.  
**Operations:** Read (primary), INSERT (by Data ETL scripts).

### 7.3 Renewable Energy Suitability Tables

**Table:** `solar_suitability`  
**Purpose:** Pre-computed solar suitability scores per municipality.  
**Used By Modules:** Dashboard, EcoSim, EnergyHub (map).  
**Data Stored:** municipality_id (FK), solar_score, classification, irradiance_avg, temp_factor, panel_output_kwh_month.  
**Operations:** Read (primary), INSERT/UPDATE (by Suitability Engine).
**Status:** Referenced in `Dashboard.jsx` queries; schema confirmed in database.

**Table:** `wind_suitability`  
**Purpose:** Pre-computed wind suitability scores per municipality.  
**Used By Modules:** Dashboard, EcoSim, EnergyHub (map).  
**Data Stored:** municipality_id (FK), wind_score, classification, avg_ws10m, air_density, estimated_output_kwh_month.  
**Operations:** Read (primary), INSERT/UPDATE (by Suitability Engine).
**Status:** Referenced in `Dashboard.jsx` queries; schema confirmed in database.

**Table:** `hydropower_suitability`  
**Purpose:** Pre-computed hydropower suitability with terrain metrics.  
**Used By Modules:** EcoSim, EnergyHub (map), Dashboard, Suitability Engine.  
**Data Stored:** municipality_id (PK), province_id (FK), municipality_name, province, latitude, longitude, elevation_m, mean_elevation_m, min_elevation_m, max_elevation_m, elevation_range_m, mean_slope_deg, hydraulic_head_m, terrain_ruggedness, watershed_gradient, hydro_suitability_score, estimated_hydropower_potential_kw, runoff_potential, gravity_flow_potential, terrain_flatness, slope_classification, elevation_classification, ridge_elevation, terrain_exposure_index.  
**Operations:** Read, INSERT/UPDATE.

**Table:** `geothermal_suitability`  
**Purpose:** Pre-computed geothermal suitability scores.  
**Used By Modules:** Geothermal Analysis, EcoSim, Dashboard, EnergyHub.  
**Data Stored:** municipality_id (PK), heat_flow_score, fault_density, volcano_proximity, surface_temperature_score, aquifer_score, geothermal_score, classification, confidence.  
**Operations:** Read, INSERT/UPDATE.

**Table:** `geothermal_output`  
**Purpose:** Pre-computed geothermal energy output estimates per municipality.  
**Used By Modules:** Geothermal Analysis, EcoSim.  
**Data Stored:** municipality_id (FK), reservoir_temperature_c, estimated_flow_rate_kg_s, thermal_power_mw, electric_power_mw, annual_energy_gwh, confidence_score, source, assumption.  
**Operations:** Read, INSERT/UPDATE.

### 7.4 National Energy Statistics Tables

**Table:** `national_energy_annual`  
**Purpose:** Historical national energy statistics from DOE.  
**Used By Modules:** EnergyHub (overview, trends, source breakdown, grid breakdown), ML Forecasting.  
**Data Stored:** year (PK), total_consumption_gwh, residential_consumption_gwh, commercial_consumption_gwh, industrial_consumption_gwh, total_generation_gwh, peak_demand_mw, coal_gwh, natural_gas_gwh, oil_based_gwh, hydro_gwh, geothermal_gwh, wind_gwh, solar_gwh, biomass_gwh, total_renewable_gwh, grid_private_pct, grid_government_pct, grid_cooperative_pct.  
**Operations:** Read (primary), INSERT/UPDATE (by Data ETL).

**Table:** `forecast_cache`  
**Purpose:** Cache for ML forecast API responses.  
**Used By Modules:** EnergyHub, ML Forecasting.  
**Data Stored:** forecast_id (PK), model_id (FK), target_variable, forecast_year, forecast_month, predicted_value, lower_bound, upper_bound, created_at.  
**Operations:** Read, INSERT.

**Table:** `ml_model_registry`  
**Purpose:** Track ML model versions and active status.  
**Used By Modules:** ML Forecasting, EnergyHub (model comparison).  
**Data Stored:** model_id (PK), model_name, model_version, model_type, target_variable, train_date, features_used, hyperparameters, metrics_json, is_active, artifact_path, created_at, updated_at.  
**Operations:** Read, INSERT, UPDATE (activate/deactivate models).

### 7.5 User & Auth Tables

**Table:** `profiles` (extends `auth.users`)  
**Purpose:** Extended user profile data.  
**Used By Modules:** Authentication, Dashboard, Admin.  
**Data Stored:** id (PK, FK to auth.users), full_name, avatar_url, organization, location, preferred_municipality_id, plan, is_active, created_at.  
**Operations:** Read, UPDATE.

**Table:** `user_roles`  
**Purpose:** Role-based access control.  
**Used By Modules:** Authentication, Admin.  
**Data Stored:** user_id (PK, FK to auth.users), role (`user`/`admin`/`dev`), created_at.  
**Operations:** Read, UPDATE (by Admin).

**Table:** `saved_simulations`  
**Purpose:** Store user-saved EcoSim runs.  
**Used By Modules:** EcoSim, Dashboard, Admin.  
**Data Stored:** id (PK), user_id (FK), municipality_id (FK), name, source, inputs (JSONB), results (JSONB), created_at.  
**Operations:** Read (RLS-filtered by user_id), INSERT, DELETE.

**Table:** `chat_sessions`  
**Purpose:** Chat conversation threads.  
**Used By Modules:** AI Chat, Admin (moderation).  
**Data Stored:** id (PK), user_id (FK), title, is_flagged, created_at.  
**Operations:** Read (RLS-filtered), INSERT, UPDATE (flag), DELETE.
**Status:** Partially implemented — schema exists, MVP uses in-memory state.

**Table:** `chat_messages`  
**Purpose:** Individual messages within chat sessions.  
**Used By Modules:** AI Chat.  
**Data Stored:** id (PK), session_id (FK), role (`user`/`assistant`/`system`), content, created_at.  
**Operations:** Read (via session ownership RLS), INSERT.
**Status:** Partially implemented — schema exists, MVP uses in-memory state.

### 7.6 Admin & System Tables

**Table:** `admin_audit_log`  
**Purpose:** Immutable log of admin actions for accountability.  
**Used By Modules:** Admin.  
**Data Stored:** id (PK), admin_id (FK), action, target_user_id (FK), details (JSONB), created_at.  
**Operations:** INSERT (append-only), Read (admin-only).

**Table:** `system_config`  
**Purpose:** Global key-value settings for admin toggles.  
**Used By Modules:** Admin, AI Chat (limits), EcoSim (limits).  
**Data Stored:** key (PK), value (JSONB), updated_at.  
**Operations:** Read (all users), UPDATE (admin-only).

### 7.7 AI & Cache Tables

**Table:** `chart_ai_insights`  
**Purpose:** Cache AI-generated insights for charts to reduce LLM API calls.  
**Used By Modules:** EnergyHub.  
**Data Stored:** id (PK), chart_type, chart_data_hash, insight_text, created_at.  
**Operations:** Read (by chart_type + hash), INSERT.

### 7.8 Views

**View:** `regional_lookup`  
**Purpose:** Flattened hierarchical geographic lookup (region → province → municipality → barangay).  
**Used By Modules:** EnergyHub, Data ETL, general queries.  
**Data Stored:** All IDs and names from `regions`, `provinces`, `municipalities`, `barangays` joined.  
**Operations:** Read-only.

### 7.9 Database Functions

**Function:** `get_suitability_classification(score numeric)`  
**Purpose:** Classify a numeric suitability score into a tier.  
**Used By:** Suitability Engine, triggers.  
**Logic:** Returns `Excellent`, `Good`, `Moderate`, `Poor`, or `Unsuitable` based on score thresholds.

**Function:** `set_updated_at()`  
**Purpose:** Auto-update `updated_at` timestamp on row modification.  
**Used By:** `ml_model_registry`, `national_energy_annual` (via triggers).  
**Logic:** Sets `updated_at = now()` on UPDATE.

**Trigger:** `trg_ml_model_registry_updated`  
**Purpose:** Auto-update timestamp on `ml_model_registry` changes.  
**Target Table:** `ml_model_registry`.

**Trigger:** `trg_national_energy_annual_updated`  
**Purpose:** Auto-update timestamp on `national_energy_annual` changes.  
**Target Table:** `national_energy_annual`.

**Trigger:** `on_auth_user_created`  
**Purpose:** Auto-create profile and role on new Supabase Auth user.  
**Target Table:** `auth.users` (after insert).  
**Logic:** Insert into `profiles` and `user_roles` with defaults.

---

## Part 8: AI / LLM Process Flow

### 8.1 High-Level AI Flow

```
User Question
    ↓
[Frontend] ChatPage.jsx captures input
    ↓
[Backend] POST /api/v1/chat/send
    ↓
[RAG Pipeline] Embed query + retrieve chunks
    ↓
[Prompt Assembly] System persona + context + question
    ↓
[Groq / Gemini API] LLM generation
    ↓
[LLM Sanitizer] Clean and structure response
    ↓
[Citation Formatter] Attach source metadata
    ↓
[Frontend] Render formatted response with citations
    ↓
User
```

### 8.2 Detailed AI Process Steps

**Step 1: Query Reception**
- **Process:** `POST /api/v1/chat/send`
- **Input:** `{ message: string, session_id?: string }`
- **Action:** Validate input, check rate limits (if configured in `system_config`)

**Step 2: Knowledge Retrieval (RAG)**
- **Process:** `rag_pipeline.retrieve_context(query, top_k=5)`
- **Sub-steps:**
  1. Load `SentenceTransformer('all-MiniLM-L6-v2')` model (cached in memory)
  2. Encode user query into 384-dimensional embedding vector
  3. Load FAISS flat index (`faiss_index.bin`) from disk
  4. Perform `index.search(query_embedding, k=5)` — L2 distance similarity search
  5. Map returned indices to original chunks via `chunk_map.json`
  6. Filter chunks by minimum similarity threshold (if configured)
  7. Return top-k chunk texts + source metadata
- **Output:** Array of `{ text: string, source: string, title: string, url: string, org: string }`

**Step 3: Prompt Assembly**
- **Process:** `chat.py` inline prompt builder
- **System Persona:** "You are LUMI, an expert renewable energy decision-support assistant for the Philippines. You provide evidence-based recommendations using the provided context."
- **Context Block:** Concatenate retrieved chunk texts with `[Source: title]` labels
- **User Question:** Original message
- **Formatting Instructions:** "Answer in plain text. Cite sources. Structure your response with: Observation, Interpretation, Recommendation, Reason."
- **Output:** Complete prompt string (~500-2000 tokens)

**Step 4: LLM Generation**
- **Process:** `groq_client.generate()` or `gemini_funcs.generate()`
- **Primary Provider:** Groq API (model: `llama3-8b-8192` or equivalent fast model)
- **Fallback Provider:** Google Gemini API (if Groq fails or for specific chart analysis)
- **Parameters:** temperature ~0.7, max_tokens ~1024
- **Input:** Assembled prompt
- **Output:** Raw generated text string

**Step 5: Response Sanitization**
- **Process:** `llm_sanitizer.sanitize_llm_output(raw_text)`
- **Pipeline:**
  1. `strip_markdown_fences()` — remove ```json ... ``` wrappers
  2. `strip_json_wrappers()` — if entire response is JSON, extract narrative text value
  3. `strip_key_value_formatting()` — remove lines like `"summary": "..."`
  4. `normalize_whitespace()` — collapse multiple blank lines, unescape `\n` and `\t`, remove outer quotes
- **Output:** Clean plain text

**Step 6: Structure Extraction**
- **Process:** `llm_sanitizer.extract_prescriptive_recommendation(clean_text)`
- **Regex Patterns:**
  - Observation: `(?i)(?:##?\s*)?(?:Observation|What the data shows)[\s:]*\n?(.*?)(?=\n\n?(?:##?\s*)?(?:Interpretation|What this means)|$)`
  - Interpretation: `(?i)(?:##?\s*)?(?:Interpretation|What this means)[\s:]*\n?(.*?)(?=\n\n?(?:##?\s*)?(?:Recommendation|What to consider)|$)`
  - Recommendation: `(?i)(?:##?\s*)?(?:Recommendation|What to consider|Suggested action)[\s:]*\n?(.*?)(?=\n\n?(?:##?\s*)?(?:Reason|Why|Rationale)|$)`
  - Reason: `(?i)(?:##?\s*)?(?:Reason|Why|Rationale)[\s:]*\n?(.*?)$`
- **Fallback:** If no sections match, place entire text in `recommendation`
- **Output:** `{ observation, interpretation, recommendation, reason }`

**Step 7: Citation Formatting**
- **Process:** Map chunk source labels to structured citations using `rag_knowledge_builder.SOURCE_MAP`
- **Source Categories:**
  - E-commerce: Alibaba, Amazon, Lazada, iSTA Breeze
  - Government: DOE Philippine Power Statistics
  - Scientific: NASA POWER
  - Internal: LUMI Suitability Models, Terrain Analysis
- **Output Format:** `[{ title: string, url: string, org: string }]`

**Step 8: Frontend Rendering**
- **Process:** `ChatPage.jsx` message rendering
- **Display:**
  - AI avatar + name "LUMI AI"
  - Structured sections (if extracted): bold headings for Observation, Interpretation, Recommendation, Reason
  - Clickable citation chips with title and URL
  - Timestamp
- **Status:** Implemented.

### 8.3 AI Process Variants

**Chart Analysis (EnergyHub):**
- **Trigger:** User clicks "Analyze with AI" on a chart
- **Input:** Chart data JSON (series labels, values, chart type)
- **Process:**
  1. Compute chart data hash
  2. Check `chart_ai_insights` cache (chart_type + hash)
  3. If cache miss, assemble prompt with chart context
  4. Call Gemini API (preferred for structured analysis)
  5. Sanitize and cache result
- **Output:** Insight text with prescriptive structure

**EcoSim AI Recommendation:**
- **Trigger:** EcoSim simulation with `include_ai=true`
- **Input:** Simulation results JSON (all energy outputs, costs, scores)
- **Process:** Assemble prompt with simulation context → call LLM → sanitize → return structured recommendation
- **Output:** Observation, interpretation, recommendation, reason tailored to the user's specific simulation

---

## Part 9: Machine Learning Process Flow

### 9.1 High-Level ML Flow

```
DOE Raw Data (PDFs, Excel)
    ↓
[Data Extraction] windsurf_data_extraction scripts
    ↓
[Data Cleaning] DOE_datacleaning.ipynb
    ↓
[Feature Engineering] Aggregate by year, sector, source
    ↓
[Model Training] DOE_arima_forecasting.ipynb (offline)
    ↓
[Forecast Generation] ARIMA(1,1,1) predictions
    ↓
[Artifact Storage] CSV files in DOE_Data_Extracted/
    ↓
[Model Registry] ml_model_registry table
    ↓
[Prediction Serving] EnergyHubML.load_forecasts()
    ↓
[Visualization] Recharts line charts in EnergyHub
    ↓
User
```

### 9.2 Detailed ML Process Steps

**Step 1: Data Collection**
- **Source:** Department of Energy Philippines publications
  - `2024 Philippine Energy Situationer and Key Energy Statistics`
  - `06_2024 LVM Grid Gross Generation Per Region, per Technology, and per Ownership`
  - `(FINAL) 11-20-25_DOE KEY ENERGY STAT (POCKET SIZE) 2024`
- **Process:** `windsurf_data_extraction/pdf_extractor.py`, `extract_compendium.py`
- **Output:** Raw CSV tables in `windsurf_data_extraction/raw_tables/`

**Step 2: Data Cleaning**
- **Process:** `DOE_datacleaning.ipynb`
- **Actions:**
  - Parse PDF tables using Camelot/Tabula
  - Handle merged cells and multi-row headers
  - Standardize column names (year, consumption_gwh, peak_demand_mw, etc.)
  - Resolve inconsistencies between different DOE publications
  - Convert all units to consistent scale (GWh, MW)
- **Output:** Clean CSVs: `national_energy_annual_ready.csv`, `consumption_by_sector.csv`, etc.

**Step 3: Feature Engineering**
- **Process:** `DOE_arima_forecasting.ipynb`
- **Actions:**
  - Aggregate monthly/quarterly data to annual totals
  - Create time-series indices (year as datetime)
  - Engineer lag features (1-year, 2-year lag)
  - Compute rolling averages
  - Separate target variables:
    - `total_consumption_gwh`
    - `peak_demand_mw`
- **Output:** Structured time-series DataFrames for modeling

**Step 4: Model Training (Offline)**
- **Process:** `DOE_arima_forecasting.ipynb` — Jupyter notebook execution
- **Model:** ARIMA(1,1,1) — AutoRegressive Integrated Moving Average
  - `p=1` (autoregressive term)
  - `d=1` (differencing order for stationarity)
  - `q=1` (moving average term)
- **Rationale:** ARIMA is chosen for its interpretability and effectiveness on annual macroeconomic/energy time series with limited data points.
- **Training Data:** Historical `national_energy_annual` (earliest available year to present)
- **Validation:** Walk-forward validation or train-test split on last 2-3 years
- **Metrics Computed:** MAE (Mean Absolute Error), RMSE (Root Mean Square Error), MAPE
- **Output:**
  - Trained model object (pickled, not served live)
  - Forecast CSV artifact: `forecast_consumption_2025_2040.csv`, `forecast_peak_demand_2025_2040.csv`
  - Model metadata JSON

**Step 5: Model Registry**
- **Process:** `DOE_model_registry.ipynb` or manual insert
- **Table:** `ml_model_registry`
- **Actions:**
  - Insert new model record with version, train_date, metrics
  - Set `is_active = true` for the new model
  - Ensure uniqueness constraint: only one active model per target_variable (`idx_ml_model_active_unique`)
- **Stored Data:** model_name, model_version, model_type (`ARIMA`), target_variable, train_date, features_used, hyperparameters (`{"p":1,"d":1,"q":1}`), metrics_json (`{"mae":X,"rmse":Y}`), is_active, artifact_path

**Step 6: Forecast Caching**
- **Process:** `EnergyHubML` or admin script
- **Table:** `forecast_cache`
- **Actions:**
  - Read forecast CSV artifact
  - Insert rows into `forecast_cache` linking to model_id
  - Enables fast API serving without file I/O on every request
- **Index:** `idx_forecast_cache_lookup` on (target_variable, forecast_year, forecast_month)

**Step 7: Prediction Serving**
- **Process:** `app/ml/predictor.py` — `EnergyHubML` class
- **Actions:**
  - On class instantiation (or first request), load forecast CSV into pandas DataFrame
  - `get_forecast(target_variable, year)` → lookup row in DataFrame
  - `get_latest_stats()` → return most recent historical actual
  - `get_trends(start_year, end_year)` → filter historical DataFrame
- **Performance:** Sub-millisecond lookup after initial load; no real-time model inference

**Step 8: Visualization**
- **Process:** EnergyHub frontend (`react-frontend/src/pages/EnergyHub.jsx`)
- **Chart Library:** Recharts (assumed from React ecosystem)
- **Display:**
  - Historical actuals: solid line
  - Forecast: dashed line
  - Confidence interval: shaded band (lower, upper)
  - Interactive tooltip with year and value
- **User Interaction:** Toggle between consumption and peak demand; zoom year range

### 9.3 ML Model Specification

| Attribute | Value |
|---|---|
| **Model Type** | ARIMA (AutoRegressive Integrated Moving Average) |
| **Order** | (1, 1, 1) |
| **Training Framework** | `statsmodels` (Python) |
| **Training Environment** | Offline Jupyter Notebook (`DOE_arima_forecasting.ipynb`) |
| **Target Variables** | `total_consumption_gwh`, `peak_demand_mw` |
| **Forecast Horizon** | ~15 years (2025–2040) |
| **Input Features** | Year (time index), lagged values |
| **Output** | Predicted value, 95% confidence lower bound, 95% confidence upper bound |
| **Serving Method** | Pre-computed CSV artifacts loaded at runtime |
| **Cache Layer** | `forecast_cache` table + `EnergyHubML` in-memory DataFrame |
| **Model Registry** | `ml_model_registry` table with active flag |

---

## Part 10: Diagram Recommendation

### 10.1 Recommended Diagrams for Thesis

| Diagram Name | Purpose | Components Needed | Recommended Chapter Placement |
|---|---|---|---|
| **System Architecture Diagram** | Show overall LUMI system structure (frontend, backend, database, external APIs) | React Frontend, FastAPI Backend, Supabase DB, Redis, FAISS, NASA POWER, Groq/Gemini, DOE datasets | Chapter 2.7 — System Design / Architecture |
| **Use Case Diagram** | Show actor-system interactions for all user types | Actors: Guest, Registered User, Admin, System; Use Cases: Register, Login, Simulate, View Dashboard, Chat with AI, Administer Users, Configure System | Chapter 2.7 — System Functions / Requirements |
| **Module Interaction Diagram** | Show how 10 major modules communicate with each other | 10 modules with labeled arrows (HTTP, SQL, Function Call, Cache) | Chapter 2.7 — Module Design |
| **Data Flow Diagram (DFD) Level 0** | System overview showing boundaries with external entities | Single process "LUMI System", 8 external entities, aggregated data flows | Chapter 2.7 — Data Flow / Chapter 3 |
| **Data Flow Diagram (DFD) Level 1** | Break LUMI into 10 major processes | 10 processes, 6 data stores, external entities, labeled data flows | Chapter 2.7 or Chapter 3 — Process Decomposition |
| **Data Flow Diagram (DFD) Level 2** | Detail RAG pipeline and EcoSim calculation subprocesses | Process 6 (AI Chat) broken into embedding, retrieval, prompt assembly, LLM generation, sanitization; Process 3 (EcoSim) broken into solar, wind, hydro, geothermal calculations | Chapter 3 — Detailed Design |
| **Activity Diagram — Registration/Login** | Show user auth workflow with decision points | Swimlanes: User, Frontend, Supabase Auth, Database; Actions: enter credentials, validate, create profile, redirect | Chapter 2.7 — Process Flow |
| **Activity Diagram — EcoSim Simulation** | Show end-to-end simulation workflow | Swimlanes: User, Frontend, Backend, Services, Database; Actions: select municipality, input parameters, calculate outputs, display results, save | Chapter 2.7 — Process Flow |
| **Activity Diagram — AI Chat (RAG)** | Show RAG-enhanced chat workflow | Swimlanes: User, Frontend, Backend, RAG Pipeline, LLM API; Actions: type message, embed query, search FAISS, assemble prompt, generate response, sanitize, display | Chapter 2.7 — AI Process Flow |
| **Activity Diagram — Choropleth Map** | Show map data retrieval and rendering | Swimlanes: User, Frontend, Backend, Redis, Database; Actions: select metric, check cache, query DB, aggregate, color map, show tooltip | Chapter 2.7 — Process Flow |
| **Sequence Diagram — Authentication** | Show temporal order of auth operations | Objects: User, Browser, AuthContext, Supabase Auth, `profiles`, `user_roles`; Messages: signUp, create user, trigger, insert profile/role | Chapter 2.7 — System Interaction |
| **Sequence Diagram — AI Chat** | Show temporal order of RAG + LLM operations | Objects: User, ChatPage, Chat API, RAG Pipeline, FAISS, Groq API, LLM Sanitizer; Messages: send message, embed, search, retrieve chunks, generate, sanitize, respond | Chapter 2.7 — AI Interaction |
| **Entity-Relationship Diagram (ERD)** | Show database schema relationships | All tables from Part 7 with PK/FK lines, cardinality notation | Chapter 2.7 — Database Design / Chapter 3 |
| **Class Diagram — Backend Services** | Show Python service class relationships | Classes: EnergyHubService, EnergyHubML, SupabaseRestClient, RedisClient, RAGPipeline, LLMSanitizer with methods and dependencies | Chapter 3 — Object Design |
| **Deployment Diagram** | Show physical/runtime deployment | Vercel/Netlify (Frontend), Render/Railway (Backend), Supabase Cloud (DB + Auth), Upstash (Redis), Groq/Gemini APIs (External) | Chapter 3 — Deployment / Implementation |
| **State Machine — User Session** | Show session states | States: Guest, Authenticating, Authenticated, Admin; Transitions: login, logout, role promotion | Chapter 2.7 — State Behavior |
| **Component Diagram — Frontend** | Show React component hierarchy | Components: App → AppRoutes → ProtectedRoute → Dashboard/EcoSim/EnergyHub/ChatPage; Shared: AuthContext, useAuth, Toaster | Chapter 3 — Frontend Architecture |

### 10.2 Diagram Priority for Thesis Team

**Tier 1 (Must-Have):**
1. System Architecture Diagram
2. Use Case Diagram
3. DFD Level 0 and Level 1
4. ERD
5. Activity Diagram — EcoSim Simulation

**Tier 2 (High Value):**
6. Module Interaction Diagram
7. DFD Level 2 (RAG and EcoSim detail)
8. Activity Diagram — AI Chat (RAG)
9. Sequence Diagram — AI Chat
10. Deployment Diagram

**Tier 3 (If Space Permits):**
11. Activity Diagram — Registration/Login
12. Activity Diagram — Choropleth Map
13. Class Diagram — Backend Services
14. Component Diagram — Frontend
15. State Machine — User Session

### 10.3 Partially Implemented Features Summary

| Feature / Component | Status | Notes |
|---|---|---|
| Chat session persistence (`chat_sessions`, `chat_messages`) | Partially implemented | Schema exists, RLS policies configured, but MVP uses in-memory React state. Frontend queries skip session storage. |
| Chat session moderation (`is_flagged`) | Partially implemented | Schema field exists, Admin Moderation UI present, but automated flagging logic is basic/not fully wired. |
| Report/Export (PDF generation) | Partially implemented | Only client-side JSON/txt download exists. No server-side PDF rendering or email delivery. |
| Model comparison metrics | Partially implemented | `ml_model_registry` tracks models, but automated MAE/RMSE computation and display may be limited to metadata. |
| Premium plan gating | MVP public mode | Plan field exists in `profiles`, but most features are publicly accessible; premium restrictions not strictly enforced in frontend. |
| OAuth providers beyond Google | Partially implemented | `signInWithProvider` is generic, but UI may only expose Google. |
| Real-time notifications | Not implemented | Toast system exists for local feedback, but no WebSocket/push notifications. |
| Mobile responsiveness | Partially implemented | Expo mobile project directory exists but may not be fully integrated or deployed. |

---

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2025-06-26 | LUMI System Analyst | Initial complete inventory based on current codebase implementation. |

---

**END OF DOCUMENT**
