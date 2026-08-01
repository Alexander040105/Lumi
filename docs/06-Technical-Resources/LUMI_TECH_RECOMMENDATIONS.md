# LUMI: Data-Driven Environmental Intelligence System

This document provides an extremely practical, free-tier-first, 6-week-realistic technology and architecture recommendation for the thesis system.

---

## 0) Executive Summary (6-Week Reality)

- Best overall stack for your skills and timeline: **Flask + Supabase Postgres + Vanilla HTML/CSS/JS + Chart.js + Upstash Redis (optional)**.
- Core strategy: **Monolithic app** (Flask serves both pages and APIs). It is the fastest to build and easiest to deploy.
- AI scope: **Short text explanations only** (chart summaries, recommendation reasoning). Keep token usage low.
- ML scope: **Classic, explainable models** (ARIMA/SARIMA, Prophet, Linear Regression). Avoid deep learning.
- Data: Combine **NASA POWER** and **Open-Meteo** for climate, plus **DOE/PAGASA/PSA** reports for local context.
- Deployment: **Render** (backend) + **Supabase** (DB/Auth) + **Upstash** (Redis) + optional **Cloudflare Pages** for static assets.

---

## 1) Full Recommended Tech Stack (Free Tier First)

### Frontend
**Recommended: Vanilla HTML/CSS/JS + Jinja templates**
- Why it fits: Uses your current skills and avoids React setup overhead.
- Budget friendly: Free.
- Beginner difficulty: Very low.
- Free-tier limitations: None.
- Scalability: Enough for thesis; can migrate to React later.
- 6-week realistic: Yes.

**Optional: React + Vite**
- Why it fits: Reusable UI components, clean state management.
- Budget friendly: Free hosting on Vercel.
- Beginner difficulty: Medium (1-2 week ramp).
- Free-tier limitations: None for small app.
- Scalability: Better for future.
- 6-week realistic: Only if at least 1 member already knows React.

### Backend
**Recommended: Flask**
- Why it fits: Easiest Python web framework for your skill set.
- Budget friendly: Free.
- Beginner difficulty: Low.
- Free-tier limitations: None.
- Scalability: Good for monolith and small datasets.
- 6-week realistic: Yes.

**Alternative: FastAPI**
- Why it fits: Built-in docs, strong typing, async.
- Beginner difficulty: Low to medium.
- 6-week realistic: Yes, but Flask is slightly faster to learn.

### Database
**Recommended: Supabase Postgres (free tier)**
- Why it fits: Managed Postgres + built-in auth + simple dashboard.
- Budget friendly: Free tier is enough for thesis.
- Beginner difficulty: Medium.
- Free-tier limitations: Row/storage limits, limited compute.
- Scalability: Very good; easy paid upgrade.
- 6-week realistic: Yes.

**Fallback: SQLite**
- Why it fits: Zero setup, fastest prototype.
- Limitation: Not ideal for cloud multi-user.

### Authentication
**Recommended: Supabase Auth**
- Why it fits: Ready-made auth with email/password, minimal code.
- Budget friendly: Free tier included.
- Beginner difficulty: Low.
- Free-tier limitations: Rate limits, email provider limits.
- 6-week realistic: Yes.

### Caching
**Recommended: Upstash Redis (free tier)**
- Why it fits: Cache API responses and AI outputs to reduce cost.
- Budget friendly: Free tier.
- Beginner difficulty: Low.
- Free-tier limitations: Limited memory/ops, but enough for thesis.
- 6-week realistic: Yes.

### AI Integration
**Cheapest: Gemini API free tier**
- Why it fits: Generous free tier for short summaries.
- Beginner difficulty: Low.
- Free-tier limitations: Rate limits and token caps.

**Alternative: HuggingFace Inference API**
- Good for short summarization, sometimes slow.

**Paid fallback: OpenAI API**
- Simple to integrate but cost can grow quickly.

### ML and Forecasting Libraries
- **statsmodels** for ARIMA/SARIMA.
- **prophet** (or **statsforecast**) for seasonal forecasting.
- **scikit-learn** for regression baselines.
- **pandas** and **numpy** for preprocessing.

### Visualization
- **Chart.js** (fastest and beginner friendly).
- **Leaflet** (maps if needed).
- **Plotly.js** (optional for richer charts).

### API Architecture
- REST endpoints under `/api/...`.
- Server-rendered pages for main views.
- Small number of endpoints (8-12) to reduce complexity.

### Hosting
- **Render** for Flask app.
- **Supabase** for Postgres + Auth.
- **Upstash** for Redis.
- **Cloudflare Pages** for static assets if needed.

### Security
- Use HTTPS from hosting provider.
- Store secrets in env vars.
- Validate inputs.
- Add basic rate limiting for AI endpoints.

---

## 2) Development Approach Analysis (Fastest and Most Realistic)

### Flask vs FastAPI vs Django

| Framework | Pros | Cons | Beginner Level | 6-Week Realistic |
| --- | --- | --- | --- | --- |
| Flask | Minimal setup, simple routing | Fewer built-ins | Low | Yes (best) |
| FastAPI | Auto docs, typing, async | Slightly more setup | Low-Med | Yes |
| Django | Full stack, ORM, admin | Heavy, steep learning | Med-High | Risky |

**Recommendation:** Flask for fastest learning curve and lowest risk.

### Vanilla JS vs React

| Option | Pros | Cons | Learning Curve | 6-Week Realistic |
| --- | --- | --- | --- | --- |
| Vanilla JS | Fastest to ship, minimal tooling | Less reuse | Low | Yes (best) |
| React | Clean UI architecture | Extra tooling/time | Medium | Only if already skilled |

**Recommendation:** Vanilla JS for speed and certainty.

### Monolith vs Split Frontend/Backend

| Option | Pros | Cons | 6-Week Realistic |
| --- | --- | --- | --- |
| Monolith | One deploy, fewer moving parts | Less separation | Yes (best) |
| Split | Cleaner separation | More deploy complexity | Risky |

**Recommendation:** Monolith.

### REST APIs vs Server-Rendered Templates

| Option | Pros | Cons | 6-Week Realistic |
| --- | --- | --- | --- |
| Server-rendered | Fast, simple, fewer bugs | Less SPA interactivity | Yes (best) |
| Full REST SPA | Modern UX | More build complexity | Risky |

**Recommendation:** Hybrid: server-rendered pages plus small REST endpoints for charts and forecasts.

---

## 3) Flask + Supabase + Redis + Vanilla JS Implementation Guide (Complete)

### 3.1 System Architecture (Text Diagram)

[Browser]
    |
    v
[Flask App]
    |  \
    |   \-> [Supabase Auth]
    |    \
    |     \-> [Supabase Postgres]
    |      \
    |       \-> [Upstash Redis]
    |        \
    |         \-> [LLM API]
    |
    \-> [Static JS + Chart.js]

### 3.2 Recommended Folder Structure

project/
    app/
        __init__.py
        config.py
        extensions.py
        routes/
            pages.py
            api_climate.py
            api_forecast.py
            api_recommend.py
            api_auth.py
        services/
            supabase_client.py
            redis_cache.py
            climate_service.py
            forecast_service.py
            recommend_service.py
            llm_service.py
        models/
            schemas.py
        templates/
            base.html
            index.html
            dashboard.html
            forecasting.html
            ecosim.html
        static/
            css/
            js/
                charts.js
                dashboard.js
    data/
        raw/
        processed/
    scripts/
        ingest_climate.py
        ingest_energy.py
    tests/
    .env.example
    requirements.txt
    run.py
    README.md

### 3.3 Flask Setup

1) Create venv and install:
- flask
- python-dotenv
- psycopg2-binary or asyncpg
- supabase-py
- redis
- pandas, numpy
- statsmodels, prophet (optional)
- scikit-learn
- requests

2) Create `app/__init__.py` to initialize Flask and blueprints.
3) Use `app/config.py` to load env vars.
4) Add `run.py` as entrypoint.

### 3.4 Supabase Postgres Setup

1) Create Supabase project (free tier).
2) Copy connection string and API keys.
3) Create tables for climate, energy, forecasts, recommendations.
4) Use `supabase-py` for reads and writes.

### 3.5 Redis Setup (Upstash)

1) Create Upstash Redis (free tier).
2) Store `REDIS_URL` in env vars.
3) Cache responses for:
- Climate API responses
- Forecast results
- LLM summaries

### 3.6 Authentication Setup (Supabase Auth)

Simplest approach:
- Use Supabase email/password.
- Frontend uses Supabase JS client for sign in.
- Flask uses JWT in headers for protected endpoints.

If time is short:
- Skip auth in MVP (public read-only).

### 3.7 API Routing Structure (Example)

- GET / -> Landing page
- GET /dashboard -> EnergyHub
- GET /forecasting -> Forecast module
- GET /ecosim -> Recommendation module

REST endpoints:
- GET /api/climate?region=...&start=...&end=...
- GET /api/energy?region=...&start=...&end=...
- POST /api/forecast (region, model)
- POST /api/recommend (inputs)
- POST /api/ai/summary (chart_data)

### 3.8 Frontend/Backend Communication

- Fetch data from `/api/...` endpoints with `fetch()`.
- Render charts with Chart.js.
- Cache heavy endpoints with Redis.

### 3.9 Dashboard and Charts

- Use Chart.js for line charts and bar charts.
- Use cards for KPIs (avg temp, avg rainfall, total kWh).
- Add region selector (dropdown) with JS fetch on change.

### 3.10 ML Integration

- Create `forecast_service.py` that:
    - Loads time series from Postgres
    - Runs ARIMA/SARIMA or Prophet
    - Stores forecasts in Postgres
    - Returns JSON for Chart.js

### 3.11 LLM Integration Workflow

- Send a small JSON summary to LLM:
    - region, time range, top trends, forecast direction
- Store AI output in Redis for 24 hours.

### 3.12 Forecasting Module Integration

- User selects region and model.
- Backend returns forecast series plus confidence band.
- Frontend shows line chart and AI explanation.

### 3.13 Deployment Workflow (Beginner Friendly)

1) Push to GitHub.
2) Create Render service and connect repo.
3) Add env vars (DB, Redis, LLM API key).
4) Render builds and deploys.
5) Set Supabase allowed domains.

### 3.14 Git and GitHub Workflow

- main branch for stable releases.
- feature/* branches for changes.
- PR and review before merge (simple).

### 3.15 Environment Variables

.env example:
- SUPABASE_URL
- SUPABASE_ANON_KEY
- SUPABASE_SERVICE_KEY
- DATABASE_URL
- REDIS_URL
- LLM_API_KEY

### 3.16 Recommended Python Packages

- flask
- python-dotenv
- supabase
- psycopg2-binary
- redis
- pandas
- numpy
- statsmodels
- prophet (optional)
- scikit-learn
- requests

### 3.17 Recommended Frontend Libraries

- Chart.js
- Leaflet (optional)
- Tailwind (optional, if you want faster styling)

---

## 4) Machine Learning and LLM Recommendations (Practical)

### Time Series Forecasting

| Model | Why It Fits | Data Needed | Training Complexity | Deployment | 6-Week Realistic |
| --- | --- | --- | --- | --- | --- |
| ARIMA/SARIMA | Simple, explainable | Monthly or daily time series | Low | Easy | Yes (best) |
| Prophet | Handles seasonality easily | Time series with seasonality | Low-Med | Easy | Yes |
| LSTM | Powerful | Large dataset | High | Hard | No |

### Regression Models (Energy Demand)

| Model | Why It Fits | Data Needed | Complexity | 6-Week Realistic |
| --- | --- | --- | --- | --- |
| Linear Regression | Baseline, easy | Small dataset | Low | Yes (best baseline) |
| Random Forest | Handles non-linear | Medium dataset | Med | Maybe |
| XGBoost | Strong performance | Medium dataset | Med-High | Risky |

### Classification Models (Feasibility)

| Model | Why It Fits | Data Needed | 6-Week Realistic |
| --- | --- | --- | --- |
| Rule-based thresholds | No training | None | Yes (best) |
| Logistic Regression | Simple | Small labeled data | Maybe |
| Random Forest | Strong but needs data | Medium dataset | Risky |

### Prophet vs ARIMA vs LSTM (Quick Verdict)

- Prophet vs ARIMA: Prophet is easier with seasonality; ARIMA is simpler and more explainable.
- LSTM: Avoid. Too complex and data-hungry for 6 weeks.

### Best Overall ML Approach

- Use **ARIMA/SARIMA** for forecasting.
- Use **Linear Regression** for simple consumption prediction.
- Use **rule-based thresholds** for feasibility and recommendations.

### Simplest Realistic ML Pipeline

1) Clean data with pandas.
2) Train ARIMA on historical energy consumption.
3) Save forecast series.
4) Use rule-based logic for recommendations.
5) Use LLM for text explanations only.

### Which Tasks Should Stay Rule-Based

- Solar vs wind vs hydro feasibility.
- Cost estimation and ROI.
- Recommendation scoring with fixed thresholds.

### Which Tasks Are Best for LLM

- Summarize charts.
- Explain forecast trends.
- Generate a short recommendation summary.

---

## 5) AI and LLM Recommendations

### Provider Comparison

| Provider | Cost | Ease | Free Tier | Best Use |
| --- | --- | --- | --- | --- |
| Gemini | Lowest cost | Easy | Yes | Short summaries |
| HuggingFace | Free but slower | Easy | Yes | Short text |
| OpenAI | Paid | Easy | Limited credits | Higher quality |
| Ollama | Free local | Medium | Local only | Offline demos |

### Cheapest Integration Strategy

- Use Gemini free tier for short text.
- Cache outputs in Redis.
- Limit to one summary per chart per day.

### Prompt Strategy

- Use a fixed prompt template.
- Provide only necessary stats (mean, trend, max, min).
- Limit output to 3-5 sentences.

### Realistic AI Features in 6 Weeks

- Yes: short chart summaries, simple recommendation explanations.
- Maybe: automatic report generation (template + short AI).
- No: full conversational assistant.

---

## 6) Data Source Recommendations (Free and Practical)

### Climate and Weather

1) PAGASA: https://www.pagasa.dost.gov.ph/
- Free, no public API, manual downloads

2) NASA POWER: https://power.larc.nasa.gov/
- Free REST API, very beginner friendly

3) Open-Meteo: https://open-meteo.com/
- Free API, easy to use

4) OpenWeather: https://openweathermap.org/
- Free tier with API key

### Energy and Electricity

1) DOE Philippines: https://www.doe.gov.ph/
- Official reports, manual extraction

2) NGCP: https://www.ngcp.ph/
- Demand data often in reports, manual extraction

3) PSA: https://psa.gov.ph/
- National statistics

### Solar, Wind, Hydro Potential

1) Global Solar Atlas: https://globalsolaratlas.info/
2) Global Wind Atlas: https://globalwindatlas.info/
3) NASA POWER: https://power.larc.nasa.gov/
4) USGS SRTM: https://www2.jpl.nasa.gov/srtm/

### Terrain and Land Use

1) OpenStreetMap: https://www.openstreetmap.org/
2) HydroSHEDS: https://www.hydrosheds.org/
3) PH Geoportal: https://geoportal.gov.ph/

### Data Strategy (Best 6-week path)

- Use NASA POWER and Open-Meteo as primary APIs.
- Use DOE and PSA PDFs as citation sources.
- Store cleaned data in Postgres for charts.

---

## 7) Renewable Energy Costing Data Sources

### Practical Sources

- DOE Philippines reports: https://www.doe.gov.ph/
- IRENA cost reports: https://www.irena.org/Publications
- PSA: https://psa.gov.ph/
- Local installer quotes (manual citation)
- Market snapshots (Lazada/Shopee, manual reference only)

### Best Practical Approach for Costing

- Use **static cost ranges** stored in JSON or DB.
- Update once for thesis and cite sources.
- Avoid ML-based costing (no data and too complex).

### Static vs Dynamic Pricing

- Static is best for 6 weeks.
- Dynamic pricing requires APIs that are not available.

---

## 8) Renewable Energy Feasibility Logic (Realistic)

### Example Rules

IF:
- solar_irradiance >= 4.0 kWh/m2/day
- urban or suburban
- monthly_kwh >= 150
THEN:
- recommend rooftop solar

IF:
- average_wind_speed < 5.5 m/s
THEN:
- reject residential wind

IF:
- no nearby river OR elevation_drop < 5m
THEN:
- reject micro-hydro

### Why Solar is Most Realistic in PH

- High irradiance across most regions.
- Rooftop installations are feasible.
- Mature market and support.

### Why Wind and Hydro Need Strict Conditions

- Wind needs consistent speed and open exposure.
- Hydro requires water flow and terrain.

---

## 9) Database Design Recommendations

### Postgres vs MySQL vs SQLite

| DB | Pros | Cons | 6-Week Realistic |
| --- | --- | --- | --- |
| Postgres | Best analytics, strong SQL | Setup required | Yes (best) |
| MySQL | Common, stable | Slightly less analytics | Yes |
| SQLite | Fastest setup | Not ideal for cloud | Only for prototype |

### Recommended Schema (Minimal)

- regions(id, name, lat, lon, island_group)
- climate_daily(id, region_id, date, temp_c, rain_mm, humidity)
- energy_monthly(id, region_id, month, kwh)
- forecasts(id, region_id, date, model, yhat, yhat_lower, yhat_upper)
- recommendations(id, region_id, created_at, type, score, text)
- cost_ranges(id, component, low, mid, high, source)

### Redis Caching Strategy

- Cache climate queries by region and date range.
- Cache LLM outputs per region per day.
- Cache forecast results for 24 hours.

---

## 10) Deployment Plan (Cheapest + Simple)

### Recommended Architecture

- Flask app on Render
- Supabase Postgres + Auth
- Upstash Redis
- Optional static assets on Cloudflare Pages

### Steps

1) Create GitHub repo
2) Create Supabase project and tables
3) Create Upstash Redis
4) Deploy Flask on Render
5) Configure env vars
6) Test endpoints

### HTTPS

- Render provides HTTPS automatically

### CI/CD

- GitHub Actions: run tests and deploy

---

## 11) Cost Analysis (Free Tier)

### Estimated Monthly Cost

- Supabase free tier: 0 USD
- Render free tier: 0 USD
- Upstash Redis free tier: 0 USD
- Gemini free tier: 0 USD

Total: 0 USD

### Scaling Costs (Future)

- Render paid: 7 to 25 USD
- Supabase upgrade: 10 to 25 USD
- LLM usage: depends on calls

---

## 12) Security and Best Practices

- Use Supabase Auth for login.
- Never expose service keys in frontend.
- Validate input in Flask endpoints.
- Use rate limits for AI endpoints.
- Store secrets in env vars.
- Add DB backups weekly.

---

## 13) Final Recommendation (Most Realistic)

### Best Overall Stack (Recommended)

- Frontend: Vanilla HTML/CSS/JS + Jinja templates
- Backend: Flask
- DB/Auth: Supabase Postgres + Supabase Auth
- Cache: Upstash Redis
- AI: Gemini free tier (short summaries)
- ML: ARIMA/SARIMA + Linear Regression
- Hosting: Render

### Simpler Backup Stack

- Frontend: Vanilla HTML/CSS/JS
- Backend: Flask
- DB: SQLite
- AI: None
- Hosting: Render

### Best ML Approach

- ARIMA/SARIMA for forecasting
- Linear Regression baseline for demand
- Rule-based logic for feasibility

### Best LLM Approach

- Short summaries only (Gemini free tier), cached in Redis

### Tradeoffs

- Flask + Supabase: fastest and easiest, but less built-in tooling than Django.
- Redis optional: helps performance and cost, but adds a service.
- Vanilla JS: fastest, but less reusable UI compared to React.

---

## 14) Bonus: Realistic 6-Week Development Roadmap

### Week 1: Planning and Data
- Finalize scope and features
- Identify and test data sources
- Set up Supabase schema

### Week 2: Backend Foundation
- Flask app and base routes
- Data ingestion scripts
- Core API endpoints

### Week 3: Frontend Dashboard
- Build EnergyHub page
- Integrate Chart.js
- Add region filters

### Week 4: Forecasting Module
- Implement ARIMA/Prophet
- Forecast endpoints
- Chart visualizations

### Week 5: Recommendation Engine
- Rule-based feasibility logic
- Costing calculator
- LLM summaries (cached)

### Week 6: Testing and Deployment
- Fix bugs
- Deploy on Render
- Prepare thesis documentation and demo

### Priority Order

1) Data ingestion and dashboard
2) Forecasting
3) Recommendation engine
4) AI summaries

### Optional Stretch Goals

- User accounts
- Map-based visualization
- Automated PDF reporting


### Best Overall Stack (Recommended)
- Frontend: Server-rendered templates + vanilla JS
- Backend: FastAPI
- DB: Neon Postgres
- AI: HuggingFace Inference API (free tier) for short explanations
- Forecasting: statsmodels ARIMA/SARIMA
- Charts: Chart.js + Leaflet
- Hosting: Render + Neon

**Why best:** Fastest build, minimal complexity, free tier friendly.

### Simpler Backup Stack
- Frontend: Vanilla HTML/CSS/JS
- Backend: Flask
- DB: SQLite
- AI: No AI (use template explanations)
- Hosting: Render

**Tradeoff:** simpler but less scalable and less AI-ready.

**Most realistic within 6 weeks:** Best Overall Stack.

---

## 10) BONUS: 6-WEEK ROADMAP

### Week 1: Planning + Data
- Confirm scope, data sources, and features
- Build initial schema and data pipeline
- Create UI wireframes

### Week 2: Core Backend + DB
- Setup FastAPI + Postgres
- Implement data ingestion scripts
- Build REST endpoints

### Week 3: Dashboard + Charts
- Build UI pages
- Integrate charts and maps
- Display region-based climate data

### Week 4: Forecasting Module
- Implement ARIMA/Prophet forecasting
- Add forecast results to UI

### Week 5: Recommendation Engine + AI
- Implement rule-based recommendations
- Add AI insights (short text only)

### Week 6: Testing + Deployment + Docs
- Functional testing
- Deploy to Render
- Finish thesis documentation

**Priority Order:**
1) Data ingestion + dashboard
2) Forecasting
3) Recommendations
4) AI insights

**Stretch Goals:**
- What-if simulation
- Advanced AI explanations
- User accounts

---

## Simple Text Architecture Diagram

[User Browser]
    |
    v
[FastAPI App]
    |\
    | \--> [Chart.js/Leaflet]
    |
    +--> [Postgres DB]
    |
    +--> [AI API (HuggingFace/Gemini)]
    |
    +--> [Data Ingestion Scripts]

---

## Final Notes

Keep AI features minimal and focus on a clean, working pipeline. A stable, reliable prototype is more important than advanced complexity for a 6-week thesis timeline.

---

## 11) RENEWABLE ENERGY COSTING AND FEASIBILITY DATA SOURCES (PHILIPPINES)

This section focuses on realistic, low-cost, and defensible data sources for **residential** renewable energy recommendations in the Philippines. Solar is prioritized; wind and hydro are treated as conditional and often excluded for household users.

### A) Renewable Energy Installation Costs (Residential)

**1) DOE Philippines (Department of Energy)**
- Official link: https://www.doe.gov.ph/
- Free or paid: Free
- API limits: No public API; reports and statistics are downloaded manually
- API key: No
- Integration ease: Medium (manual data extraction into CSV)
- Data quality: High (official government)
- Beginner-friendly: Medium
- Thesis suitability: High (credible public source)
- Use case: National energy reports, policy docs, price references, and market context

**2) Philippine Statistics Authority (PSA)**
- Official link: https://psa.gov.ph/
- Free or paid: Free
- API limits: No public API; manual datasets
- API key: No
- Integration ease: Medium (manual)
- Data quality: High
- Beginner-friendly: Medium
- Thesis suitability: High
- Use case: Household energy consumption baselines for ROI assumptions

**3) World Bank Open Data (Energy Indicators)**
- Official link: https://data.worldbank.org/
- Free or paid: Free
- API limits: Generous; no strict limits for light use
- API key: No
- Integration ease: Easy (REST + CSV)
- Data quality: High
- Beginner-friendly: High
- Thesis suitability: High
- Use case: Macro energy pricing context and trends

**4) IRENA (International Renewable Energy Agency) Cost Data**
- Official link: https://www.irena.org/Publications
- Free or paid: Free
- API limits: No public API; reports PDF/Excel
- API key: No
- Integration ease: Medium (extract tables)
- Data quality: High
- Beginner-friendly: Medium
- Thesis suitability: High
- Use case: Global benchmark cost ranges for solar PV, batteries, and LCOE

**5) Lazada / Shopee (Philippines) Marketplace Pricing**
- Official links: https://www.lazada.com.ph/ , https://shopee.ph/
- Free or paid: Free to browse
- API limits: No official public API for pricing; scraping is against terms
- API key: No
- Integration ease: Low (manual reference only)
- Data quality: Medium (market variance)
- Beginner-friendly: High (manual)
- Thesis suitability: Medium (use as reference only, cite as market snapshot)
- Use case: Realistic consumer pricing for panels, inverters, batteries

**6) Manufacturer and Installer Price Lists (Local Companies)**
- Official link: Company websites (varies)
- Free or paid: Usually free catalogs and quotations
- API limits: Not applicable
- API key: No
- Integration ease: Low (manual)
- Data quality: Medium to High
- Beginner-friendly: Medium
- Thesis suitability: Medium (use as examples with citations)
- Use case: Cost ranges, installed system prices, O and M estimates

**7) OpenEI Utility Rate Database (Global Utility Rates)**
- Official link: https://openei.org/wiki/Utility_Rate_Database
- Free or paid: Free
- API limits: Limited rate for free API; suitable for light use
- API key: Not required for manual; API key for automated access
- Integration ease: Medium
- Data quality: Medium (PH coverage may be limited)
- Beginner-friendly: Medium
- Thesis suitability: Medium
- Use case: Electricity rates baseline if local sources are limited

**8) Kaggle Cost Datasets (Solar Pricing)**
- Official link: https://www.kaggle.com/datasets
- Free or paid: Free
- API limits: Kaggle API requires account
- API key: Yes (Kaggle token)
- Integration ease: Easy
- Data quality: Varies by dataset
- Beginner-friendly: Medium
- Thesis suitability: Medium (ensure dataset credibility)
- Use case: Baseline cost assumptions where local data is missing

**9) Research Papers and Thesis Repositories**
- Official links: Google Scholar, university repositories
- Free or paid: Mixed
- API limits: Not applicable
- API key: No
- Integration ease: Low (manual)
- Data quality: High if peer-reviewed
- Beginner-friendly: Medium
- Thesis suitability: High
- Use case: Localized cost assumptions for PH markets

**Practical cost data strategy (6-week reality):**
- Use **manual cost ranges** from DOE/IRENA/marketplace snapshots.
- Store costs in a **static JSON or DB table** (panels, inverter, battery, labor, O and M).
- Update manually once for thesis, then keep static to avoid API complexity.

### B) Renewable Energy Feasibility Data (Philippines)

**1) Global Solar Atlas**
- Official link: https://globalsolaratlas.info/
- Free or paid: Free
- API limits: Limited; API access may require request
- API key: Possible for API access
- Integration ease: Medium (manual or API if granted)
- Data quality: High
- Beginner-friendly: Medium
- Thesis suitability: High
- Use case: Solar PV potential, irradiance maps

**2) Global Wind Atlas**
- Official link: https://globalwindatlas.info/
- Free or paid: Free
- API limits: Limited; API access may require request
- API key: Possible for API access
- Integration ease: Medium
- Data quality: High
- Beginner-friendly: Medium
- Thesis suitability: High
- Use case: Average wind speed and wind power density

**3) NASA POWER API**
- Official link: https://power.larc.nasa.gov/
- Free or paid: Free
- API limits: Generous
- API key: No
- Integration ease: Easy (REST)
- Data quality: High
- Beginner-friendly: High
- Thesis suitability: High
- Use case: Solar irradiance, temperature, humidity, rainfall

**4) Open-Meteo**
- Official link: https://open-meteo.com/
- Free or paid: Free
- API limits: Generous free tier
- API key: No
- Integration ease: Easy
- Data quality: High
- Beginner-friendly: High
- Thesis suitability: High
- Use case: Wind speed, solar radiation, climate context

**5) PAGASA Climate Normals / Historical Data**
- Official link: https://www.pagasa.dost.gov.ph/
- Free or paid: Free (may require request)
- API limits: No public API
- API key: No
- Integration ease: Medium (manual)
- Data quality: High
- Beginner-friendly: Medium
- Thesis suitability: High
- Use case: Local climate validation and historical patterns

**6) USGS / SRTM Elevation Data**
- Official link: https://earthexplorer.usgs.gov/ and https://www2.jpl.nasa.gov/srtm/
- Free or paid: Free
- API limits: Download-based
- API key: No
- Integration ease: Medium
- Data quality: High
- Beginner-friendly: Medium
- Thesis suitability: High
- Use case: Terrain and elevation for hydro or wind feasibility

**7) OpenStreetMap (OSM)**
- Official link: https://www.openstreetmap.org/
- Free or paid: Free
- API limits: Limited for heavy use
- API key: No
- Integration ease: Medium
- Data quality: Medium to High (crowdsourced)
- Beginner-friendly: Medium
- Thesis suitability: Medium
- Use case: Identify rivers, elevation context, urban density, land use

**8) HydroSHEDS (Hydrography Data)**
- Official link: https://www.hydrosheds.org/
- Free or paid: Free (for research)
- API limits: Download-based
- API key: No
- Integration ease: Medium
- Data quality: High
- Beginner-friendly: Medium
- Thesis suitability: High
- Use case: River networks and flow data for micro-hydro feasibility

**9) Philippine Geoportal**
- Official link: https://geoportal.gov.ph/
- Free or paid: Free
- API limits: Mixed by dataset
- API key: Some datasets may require access
- Integration ease: Medium
- Data quality: High
- Beginner-friendly: Medium
- Thesis suitability: High
- Use case: Local geographic layers and environmental datasets

**Practical feasibility data strategy (6-week reality):**
- Use **NASA POWER** + **Open-Meteo** for climate and wind.
- Use **Global Solar Atlas** for solar potential reference.
- Use **Global Wind Atlas** for wind feasibility screening.
- Treat hydro as **manual and optional** unless river data is easy.

---

## Cost Estimation in the Web App (Best Practical Approach)

**Best method for 6 weeks:**
- Rule-based costing using **static cost ranges** from credible sources.
- Store ranges in JSON or database table with version and citation.

**Why rule-based (not ML) within 6 weeks:**
- ML requires large labeled datasets that you do not have.
- Rule-based costing is defensible and explainable in a thesis.

**Static vs periodically updated vs API-driven:**
- **Static** is most practical and safe for thesis.
- If time allows, update monthly or by manual upload.
- API-driven pricing is risky due to missing public APIs.

**Most practical costing simulation:**
- Use a small set of inputs: region, roof size estimate, energy usage tier.
- Compute a recommended system size (kW) from usage.
- Apply cost range: panel + inverter + battery + labor + O and M.
- Output a **range** (low/medium/high) instead of a single price.

### Short Costing Formula Example (Residential Solar)

| Component | Example Formula | Notes |
| --- | --- | --- |
| System size (kW) | monthly_kwh / 120 | Assumes ~4 kWh/day per kW, 30 days |
| Panel cost | system_kw * panel_cost_per_kw | Use low/med/high range |
| Inverter cost | system_kw * inverter_cost_per_kw | 1 inverter per system |
| Battery cost (optional) | system_kw * battery_cost_per_kw | Only if user wants backup |
| Labor + mounts | system_kw * labor_cost_per_kw | Includes rails and install |
| Total cost | sum(all components) | Show range + assumptions |

### Sample Static Pricing JSON Schema

```json
{
    "currency": "PHP",
    "version": "2026-05",
    "assumptions": {
        "kwh_per_kw_per_day": 4.0,
        "days_per_month": 30,
        "notes": "Conservative baseline for PH solar output"
    },
    "components": {
        "panel_cost_per_kw": {"low": 25000, "mid": 35000, "high": 45000},
        "inverter_cost_per_kw": {"low": 8000, "mid": 12000, "high": 18000},
        "battery_cost_per_kw": {"low": 20000, "mid": 30000, "high": 45000},
        "labor_cost_per_kw": {"low": 8000, "mid": 12000, "high": 16000}
    },
    "maintenance_annual": {
        "percent_of_capex": 1.5
    },
    "sources": [
        "DOE Philippines reports",
        "IRENA cost ranges",
        "Local installer quotations (snapshot)"
    ]
}
```

---

## Why Solar is Most Realistic for Philippine Households

- High solar irradiance in most regions.
- Rooftop installation is feasible for urban and suburban homes.
- Mature consumer market for solar PV in PH.
- Lower operational complexity compared to wind or hydro.

## Why Wind and Hydro Need Stricter Conditions

- Wind turbines require **consistent high wind speeds** and open exposure.
- Micro-hydro requires **nearby flowing water** and elevation drop.
- Urban households rarely have these conditions.

### Recommended feasibility conditions

**Solar:**
- Irradiance above threshold (e.g., 4.0 kWh/m2/day)
- Minimal shading and sufficient roof area

**Wind:**
- Average wind speed above threshold (e.g., 5.5 m/s)
- Open exposure, not dense urban area

**Hydro:**
- River or stream within close distance
- Elevation drop and reliable flow

---

## Simple, Defensible Recommendation Logic (Example)

**Rule 1: Solar**
- IF high solar irradiance AND urban/suburban household AND small/medium energy use
- THEN recommend rooftop solar PV (2-5 kW)

**Rule 2: Wind**
- IF low wind speed region
- THEN reject residential wind turbine recommendation

**Rule 3: Hydro**
- IF no nearby flowing water OR no elevation drop
- THEN reject micro-hydro recommendation

**Rule 4: Feasible Wind (rare for residential)**
- IF average wind speed >= 5.5 m/s AND rural open area
- THEN mark wind as conditional and show caution

**Rule 5: Feasible Hydro (rare for residential)**
- IF river within 1 km AND slope >= threshold
- THEN mark micro-hydro as conditional and show caution

---

## How to Avoid Unrealistic Recommendations

- Use conservative thresholds.
- Always show explanations and data source references.
- Default to solar when data is missing, and mark wind/hydro as not feasible.
- Treat wind and hydro as optional or advanced.
- Make recommendations **region-based**, not generic.

