-- ========================================================================
-- LUMI v2 Complete Database Schema
-- ========================================================================
-- Description: Standalone schema for a fresh LUMI v2 Supabase database.
--              Includes all geographic, climate, energy, ML, and new
--              user-centric tables with RLS, indexes, and triggers.
-- Run in:     Supabase SQL Editor (new project)
-- ========================================================================

-- ========================================================================
-- 0. Extensions
-- ========================================================================
create extension if not exists "pgcrypto"   with schema extensions;
create extension if not exists "uuid-ossp"  with schema extensions;

-- ========================================================================
-- 1. Geographic Tables
-- ========================================================================

create table if not exists public.regions (
    region_id   integer primary key,
    name        text not null,
    lat         double precision,
    lon         double precision
);

create table if not exists public.provinces (
    province_id integer primary key,
    region_id   integer not null references public.regions(region_id) on update cascade on delete restrict,
    name        text not null,
    lat         double precision,
    lon         double precision
);

create table if not exists public.municipalities (
    municipality_id integer primary key,
    province_id     integer not null references public.provinces(province_id) on update cascade on delete restrict,
    name            text not null,
    lat             double precision,
    lon             double precision
);

create table if not exists public.barangays (
    barangay_id     integer primary key,
    municipality_id integer not null references public.municipalities(municipality_id) on update cascade on delete restrict,
    name            text not null,
    lat             double precision,
    lon             double precision
);

-- ========================================================================
-- 2. Climate Data
-- ========================================================================

create table if not exists public.municipality_climate_monthly (
    municipality_id     integer not null,
    year                smallint not null,
    month               smallint not null,
    t2m                 double precision,
    t2m_max             double precision,
    t2m_min             double precision,
    rh2m                double precision,
    prectotcorr         double precision,
    ws10m               double precision,
    allsky_sfc_sw_dwn   double precision,
    source              text not null default 'NASA POWER',
    created_at          timestamptz not null default now(),
    cloud_amt           double precision,
    surface_pressure    double precision,
    elevation           double precision,
    rhoa                double precision,
    constraint municipality_climate_monthly_pkey primary key (municipality_id, year, month),
    constraint municipality_climate_monthly_municipality_id_fkey foreign key (municipality_id)
        references public.municipalities(municipality_id) on update cascade on delete restrict,
    constraint municipality_climate_monthly_year_check check (year >= 2018),
    constraint municipality_climate_monthly_month_check check (month between 1 and 12)
);

comment on table public.municipality_climate_monthly is
    'Monthly historical climate data by municipality from NASA POWER.';

-- ========================================================================
-- 3. Hydropower Suitability
-- ========================================================================

create table if not exists public.hydropower_suitability (
    municipality_id                 integer not null primary key references public.municipalities(municipality_id) on update cascade on delete restrict,
    province_id                     integer not null references public.provinces(province_id) on update cascade on delete restrict,
    municipality_name               text not null,
    province                        text not null,
    latitude                        double precision,
    longitude                       double precision,
    elevation_m                     double precision,
    mean_elevation_m                double precision,
    min_elevation_m                 double precision,
    max_elevation_m                 double precision,
    elevation_range_m               double precision,
    mean_slope_deg                  double precision,
    hydraulic_head_m                double precision,
    terrain_ruggedness              double precision,
    watershed_gradient              double precision,
    hydro_suitability_score         double precision,
    estimated_hydropower_potential_kw double precision,
    runoff_potential                double precision,
    gravity_flow_potential          double precision,
    terrain_flatness                double precision,
    slope_classification            text,
    elevation_classification        text,
    ridge_elevation                 double precision,
    terrain_exposure_index          double precision
);

-- ========================================================================
-- 4. National Energy & ML Forecasting
-- ========================================================================

create table if not exists public.national_energy_annual (
    year                            smallint primary key,
    total_consumption_gwh           decimal(12, 2),
    residential_consumption_gwh     decimal(12, 2),
    commercial_consumption_gwh      decimal(12, 2),
    industrial_consumption_gwh      decimal(12, 2),
    others_consumption_gwh          decimal(12, 2),
    electricity_sales_gwh           decimal(12, 2),
    utilities_own_use_gwh         decimal(12, 2),
    system_losses_gwh               decimal(12, 2),
    luzon_peak_demand_mw            decimal(12, 2),
    visayas_peak_demand_mw          decimal(12, 2),
    mindanao_peak_demand_mw         decimal(12, 2),
    total_peak_demand_mw            decimal(12, 2),
    luzon_generation_gwh            decimal(12, 2),
    visayas_generation_gwh          decimal(12, 2),
    mindanao_generation_gwh         decimal(12, 2),
    coal_generation_gwh             decimal(12, 2),
    oil_based_generation_gwh        decimal(12, 2),
    natural_gas_generation_gwh      decimal(12, 2),
    renewable_generation_gwh        decimal(12, 2),
    geothermal_generation_gwh       decimal(12, 2),
    hydro_generation_gwh            decimal(12, 2),
    biomass_generation_gwh          decimal(12, 2),
    solar_generation_gwh            decimal(12, 2),
    wind_generation_gwh             decimal(12, 2),
    total_installed_capacity_mw     decimal(12, 2),
    total_dependable_capacity_mw    decimal(12, 2),
    created_at                      timestamptz default now(),
    updated_at                      timestamptz default now(),
    constraint valid_year check (year between 2000 and 2100),
    constraint non_negative_consumption check (total_consumption_gwh >= 0),
    constraint non_negative_peak_demand check (total_peak_demand_mw >= 0)
);

comment on table public.national_energy_annual is
    'Philippine national energy statistics (annual) extracted from DOE Power Statistics. Used as target variables for ML forecasting.';

create table if not exists public.ml_model_registry (
    model_id        uuid primary key default gen_random_uuid(),
    model_name      text not null,
    model_version   text not null,
    model_type      text not null check (model_type in ('SARIMA', 'LightGBM', 'XGBoost', 'Prophet')),
    target_variable text not null,
    train_date      date not null,
    metrics         jsonb,
    model_path      text,
    is_active       boolean default false,
    created_at      timestamptz default now(),
    updated_at      timestamptz default now()
);

comment on table public.ml_model_registry is
    'Registry of trained forecasting models. Only one model per target_variable should be is_active=true at a time.';

create table if not exists public.forecast_cache (
    forecast_id     uuid primary key default gen_random_uuid(),
    model_id        uuid not null references public.ml_model_registry(model_id) on delete cascade,
    target_variable text not null,
    horizon_years   smallint not null check (horizon_years > 0 and horizon_years <= 10),
    forecast_year   smallint not null,
    forecast_month  smallint check (forecast_month is null or (forecast_month between 1 and 12)),
    predicted_value decimal(14, 4) not null,
    lower_bound     decimal(14, 4),
    upper_bound     decimal(14, 4),
    created_at      timestamptz default now()
);

comment on table public.forecast_cache is
    'Cached forecast results per model, target, and horizon. TTL managed by application logic (e.g., 24h).';

-- ========================================================================
-- 5. Views
-- ========================================================================

create or replace view public.regional_lookup as
select
    r.region_id,
    r.name as region_name,
    r.lat as region_lat,
    r.lon as region_lon,
    p.province_id,
    p.name as province_name,
    p.lat as province_lat,
    p.lon as province_lon,
    m.municipality_id,
    m.name as municipality_name,
    m.lat as municipality_lat,
    m.lon as municipality_lon,
    b.barangay_id,
    b.name as barangay_name,
    b.lat as barangay_lat,
    b.lon as barangay_lon
from public.regions r
join public.provinces p on p.region_id = r.region_id
join public.municipalities m on m.province_id = p.province_id
join public.barangays b on b.municipality_id = m.municipality_id;

-- ========================================================================
-- 6. Indexes (Existing)
-- ========================================================================

create index if not exists idx_provinces_region_id
    on public.provinces(region_id);
create index if not exists idx_municipalities_province_id
    on public.municipalities(province_id);
create index if not exists idx_barangays_municipality_id
    on public.barangays(municipality_id);
create index if not exists idx_climate_monthly_municipality_id
    on public.municipality_climate_monthly(municipality_id);
create index if not exists idx_climate_monthly_year_month
    on public.municipality_climate_monthly(year, month);
create index if not exists idx_climate_monthly_municipality_year_month
    on public.municipality_climate_monthly(municipality_id, year, month);
create index if not exists idx_hydropower_suitability_municipality_name
    on public.hydropower_suitability(municipality_name);
create index if not exists idx_hydropower_suitability_province_id
    on public.hydropower_suitability(province_id);
create index if not exists idx_national_energy_year
    on public.national_energy_annual(year);
create unique index if not exists idx_ml_model_active_unique
    on public.ml_model_registry(target_variable, is_active) where is_active = true;
create index if not exists idx_ml_model_type_target
    on public.ml_model_registry(model_type, target_variable, train_date desc);
create index if not exists idx_forecast_cache_lookup
    on public.forecast_cache(target_variable, forecast_year, forecast_month);
create index if not exists idx_forecast_cache_model
    on public.forecast_cache(model_id, created_at desc);
create index if not exists idx_forecast_cache_created
    on public.forecast_cache(created_at desc);

-- ========================================================================
-- 7. NEW: User-Centric Tables (LUMI v2)
-- ========================================================================

-- --------------------------------------------------------
-- 7.1 user_homes — Persistent "Home" profiles
-- --------------------------------------------------------
create table if not exists public.user_homes (
    home_id         uuid primary key default gen_random_uuid(),
    user_id         uuid not null references auth.users(id) on delete cascade,
    name            text not null default 'My Home',
    municipality_id integer not null references public.municipalities(municipality_id),
    created_at      timestamptz default now(),
    updated_at      timestamptz default now()
);

comment on table public.user_homes is
    'Persistent home profiles linked to Supabase Auth users. Each user may have multiple homes.';

-- --------------------------------------------------------
-- 7.2 home_energy_profiles — Energy consumption snapshots
-- --------------------------------------------------------
create table if not exists public.home_energy_profiles (
    profile_id                  uuid primary key default gen_random_uuid(),
    home_id                     uuid not null references public.user_homes(home_id) on delete cascade,
    monthly_consumption_kwh     float not null,
    monthly_bill_php            float not null,
    electricity_rate_php_per_kwh float generated always as (
        case when monthly_consumption_kwh > 0 then monthly_bill_php / monthly_consumption_kwh else 0 end
    ) stored,
    desired_savings_pct         float default 0.50,
    created_at                  timestamptz default now()
);

comment on table public.home_energy_profiles is
    'Energy consumption snapshot per home. Historical tracking is achieved by inserting new rows.';

-- --------------------------------------------------------
-- 7.3 home_simulations — Saved EcoSim results
-- --------------------------------------------------------
create table if not exists public.home_simulations (
    simulation_id           uuid primary key default gen_random_uuid(),
    home_id                 uuid not null references public.user_homes(home_id) on delete cascade,
    simulation_name         text default 'Simulation',
    -- inputs
    panel_wattage           int default 400,
    number_of_panels        int default 2,
    include_battery         boolean default false,
    battery_kwh             float default 0,
    -- outputs (denormalized for fast reads)
    recommended_source      text,
    suitability_score       float,
    estimated_generation_kwh float,
    monthly_savings_php     float,
    installation_cost_php   float,
    payback_years           float,
    carbon_reduction_kg     float,
    independence_score      float,
    results_json            jsonb,
    ai_analysis_json        jsonb,
    created_at              timestamptz default now()
);

comment on table public.home_simulations is
    'Saved EcoSim simulation results per home. Key metrics are denormalized for fast dashboard queries.';

-- --------------------------------------------------------
-- 7.4 simulation_comparisons — Side-by-side comparison sets
-- --------------------------------------------------------
create table if not exists public.simulation_comparisons (
    comparison_id   uuid primary key default gen_random_uuid(),
    home_id         uuid not null references public.user_homes(home_id) on delete cascade,
    comparison_name text default 'Comparison',
    simulation_ids  uuid[] not null,
    created_at      timestamptz default now(),
    constraint simulation_ids_length check (array_length(simulation_ids, 1) between 2 and 3)
);

comment on table public.simulation_comparisons is
    'Saved side-by-side comparison sets of 2-3 simulations per home.';

-- --------------------------------------------------------
-- 7.5 user_feedback — Recommendation quality & feedback
-- --------------------------------------------------------
create table if not exists public.user_feedback (
    feedback_id     uuid primary key default gen_random_uuid(),
    user_id         uuid not null references auth.users(id) on delete cascade,
    simulation_id   uuid references public.home_simulations(simulation_id) on delete set null,
    rating          integer check (rating between 1 and 5),
    comment         text,
    feedback_type   text check (feedback_type in ('recommendation', 'ui', 'bug', 'general')),
    created_at      timestamptz default now()
);

comment on table public.user_feedback is
    'User feedback on recommendations, UI, or bugs. Optional link to a specific simulation.';

-- --------------------------------------------------------
-- 7.6 equipment_prices — Scraped renewable energy pricing
-- --------------------------------------------------------
create table if not exists public.equipment_prices (
    price_id            uuid primary key default gen_random_uuid(),
    product_name        text not null,
    category            text not null check (category in ('solar_panel', 'inverter', 'wind_turbine', 'battery', 'controller', 'other')),
    price_php           decimal(12, 2) not null,
    source_url          text,
    scraped_at          timestamptz default now(),
    vendor              text,
    specifications_json jsonb,
    constraint positive_price check (price_php > 0)
);

comment on table public.equipment_prices is
    'Scraped renewable energy equipment pricing history for cost trend analysis and simulation cost estimates.';

-- --------------------------------------------------------
-- 7.7 municipality_renewable_scores — Pre-computed cache
-- --------------------------------------------------------
create table if not exists public.municipality_renewable_scores (
    municipality_id     integer primary key references public.municipalities(municipality_id) on delete cascade,
    solar_score         float,
    wind_score          float,
    hydro_score         float,
    composite_score     float,
    computed_at         timestamptz default now()
);

comment on table public.municipality_renewable_scores is
    'Pre-computed composite renewable energy scores per municipality for fast ranking queries.';

-- ========================================================================
-- 8. NEW: Indexes (LUMI v2)
-- ========================================================================

create index if not exists idx_user_homes_user_id
    on public.user_homes(user_id);
create index if not exists idx_user_homes_municipality_id
    on public.user_homes(municipality_id);
create index if not exists idx_profiles_home_id
    on public.home_energy_profiles(home_id);
create index if not exists idx_simulations_home_id
    on public.home_simulations(home_id);
create index if not exists idx_simulations_home_created
    on public.home_simulations(home_id, created_at desc);
create index if not exists idx_simulations_recommended_source
    on public.home_simulations(recommended_source);
create index if not exists idx_comparisons_home_id
    on public.simulation_comparisons(home_id);
create index if not exists idx_feedback_user_id
    on public.user_feedback(user_id);
create index if not exists idx_feedback_simulation_id
    on public.user_feedback(simulation_id);
create index if not exists idx_equipment_category
    on public.equipment_prices(category);
create index if not exists idx_equipment_scraped_at
    on public.equipment_prices(scraped_at desc);
create index if not exists idx_scores_composite
    on public.municipality_renewable_scores(composite_score desc);

-- ========================================================================
-- 9. NEW: Views (LUMI v2)
-- ========================================================================

-- --------------------------------------------------------
-- 9.1 user_dashboard_stats — Aggregated dashboard per user
-- --------------------------------------------------------
create or replace view public.user_dashboard_stats as
select
    uh.user_id,
    count(distinct uh.home_id) as total_homes,
    count(distinct hs.simulation_id) as total_simulations,
    coalesce(sum(hs.carbon_reduction_kg), 0)::float as total_carbon_reduction_kg,
    coalesce(avg(hs.independence_score), 0)::float as avg_independence_score,
    mode() within group (order by hs.recommended_source) as best_recommended_source,
    max(hs.created_at) as latest_simulation_date
from public.user_homes uh
left join public.home_simulations hs on hs.home_id = uh.home_id
group by uh.user_id;

comment on view public.user_dashboard_stats is
    'Aggregated statistics per user for the redesigned Dashboard page.';

-- --------------------------------------------------------
-- 9.2 seasonal_municipality_averages — 12-month climate summary
-- --------------------------------------------------------
create or replace view public.seasonal_municipality_averages as
select
    municipality_id,
    avg(allsky_sfc_sw_dwn) as avg_irradiance,
    avg(ws10m) as avg_wind_speed,
    avg(prectotcorr) as avg_rainfall,
    avg(t2m) as avg_temperature,
    avg(rh2m) as avg_humidity,
    avg(cloud_amt) as avg_cloud_cover,
    avg(rhoa) as avg_air_density,
    max(allsky_sfc_sw_dwn) as max_irradiance,
    min(allsky_sfc_sw_dwn) as min_irradiance,
    max(ws10m) as max_wind_speed,
    min(ws10m) as min_wind_speed,
    max(prectotcorr) as max_rainfall,
    min(prectotcorr) as min_rainfall,
    stddev(allsky_sfc_sw_dwn) as stddev_irradiance,
    stddev(ws10m) as stddev_wind_speed
from public.municipality_climate_monthly
where year = (select max(year) from public.municipality_climate_monthly)
group by municipality_id;

comment on view public.seasonal_municipality_averages is
    '12-month climate averages per municipality using the latest year of NASA POWER data. For EcoSim seasonal analysis.';

-- ========================================================================
-- 10. Triggers
-- ========================================================================

create or replace function public.set_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger if not exists trg_user_homes_updated
    before update on public.user_homes
    for each row execute function public.set_updated_at();

create trigger if not exists trg_national_energy_annual_updated
    before update on public.national_energy_annual
    for each row execute function public.set_updated_at();

create trigger if not exists trg_ml_model_registry_updated
    before update on public.ml_model_registry
    for each row execute function public.set_updated_at();

-- ========================================================================
-- 11. Row-Level Security (RLS)
-- ========================================================================

-- --------------------------------------------------------
-- 11.1 Existing tables
-- --------------------------------------------------------
alter table public.national_energy_annual enable row level security;
alter table public.ml_model_registry enable row level security;
alter table public.forecast_cache enable row level security;

-- national_energy_annual: public read, authenticated write
create policy if not exists "Allow public read on national_energy_annual"
    on public.national_energy_annual for select using (true);
create policy if not exists "Allow authenticated write on national_energy_annual"
    on public.national_energy_annual for all using (auth.role() = 'authenticated');

-- ml_model_registry: public read, authenticated write
create policy if not exists "Allow public read on ml_model_registry"
    on public.ml_model_registry for select using (true);
create policy if not exists "Allow authenticated write on ml_model_registry"
    on public.ml_model_registry for all using (auth.role() = 'authenticated');

-- forecast_cache: authenticated read/write
create policy if not exists "Allow authenticated read on forecast_cache"
    on public.forecast_cache for select using (auth.role() = 'authenticated');
create policy if not exists "Allow authenticated write on forecast_cache"
    on public.forecast_cache for all using (auth.role() = 'authenticated');

-- --------------------------------------------------------
-- 11.2 New tables (LUMI v2)
-- --------------------------------------------------------
alter table public.user_homes enable row level security;
alter table public.home_energy_profiles enable row level security;
alter table public.home_simulations enable row level security;
alter table public.simulation_comparisons enable row level security;
alter table public.user_feedback enable row level security;
alter table public.equipment_prices enable row level security;

-- user_homes: users see only their own homes
create policy if not exists "Users own their homes"
    on public.user_homes for all using (user_id = auth.uid());

-- home_energy_profiles: cascade through user_homes
create policy if not exists "Users own their profiles"
    on public.home_energy_profiles for all
    using (home_id in (select home_id from public.user_homes where user_id = auth.uid()));

-- home_simulations: cascade through user_homes
create policy if not exists "Users own their simulations"
    on public.home_simulations for all
    using (home_id in (select home_id from public.user_homes where user_id = auth.uid()));

-- simulation_comparisons: cascade through user_homes
create policy if not exists "Users own their comparisons"
    on public.simulation_comparisons for all
    using (home_id in (select home_id from public.user_homes where user_id = auth.uid()));

-- user_feedback: users see own feedback; admins can see all (handled in app logic if needed)
create policy if not exists "Users see their own feedback"
    on public.user_feedback for all using (user_id = auth.uid());

-- equipment_prices: public read (anyone can browse prices), authenticated/system write
create policy if not exists "Allow public read on equipment_prices"
    on public.equipment_prices for select using (true);
create policy if not exists "Allow authenticated write on equipment_prices"
    on public.equipment_prices for all using (auth.role() = 'authenticated');

-- ========================================================================
-- 12. Grants
-- ========================================================================
grant usage on schema public to anon, authenticated, service_role;

grant select on all tables in schema public to anon, authenticated;
grant all on all tables in schema public to service_role;
grant all on all sequences in schema public to anon, authenticated, service_role;
grant all on all functions in schema public to anon, authenticated, service_role;

alter default privileges in schema public
    grant all on tables to anon, authenticated, service_role;
alter default privileges in schema public
    grant all on sequences to anon, authenticated, service_role;
alter default privileges in schema public
    grant all on functions to anon, authenticated, service_role;
