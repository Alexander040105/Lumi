-- ========================================================================
-- LUMI v2 Database Migration
-- ========================================================================
-- Description: Migration script for existing LUMI databases.
--              Adds user-centric tables, views, indexes, RLS, and triggers
--              required for the v2 EcoSim Homes and new features.
-- Assumes:     Existing schema (regions, provinces, municipalities, barangays,
--              climate, hydropower, national_energy, ml_model_registry,
--              forecast_cache) is already in place.
-- Run in:      Supabase SQL Editor (existing project)
-- ========================================================================

create extension if not exists "pgcrypto"   with schema extensions;
create extension if not exists "uuid-ossp"  with schema extensions;

-- ========================================================================
-- 1. NEW: User-Centric Tables
-- ========================================================================

create table if not exists public.user_homes (
    home_id         uuid primary key default gen_random_uuid(),
    user_id         uuid not null references auth.users(id) on delete cascade,
    name            text not null default 'My Home',
    municipality_id integer not null references public.municipalities(municipality_id),
    created_at      timestamptz default now(),
    updated_at      timestamptz default now()
);

comment on table public.user_homes is
    'Persistent home profiles linked to Supabase Auth users.';

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
    'Energy consumption snapshot per home for historical tracking.';

create table if not exists public.home_simulations (
    simulation_id           uuid primary key default gen_random_uuid(),
    home_id                 uuid not null references public.user_homes(home_id) on delete cascade,
    simulation_name         text default 'Simulation',
    panel_wattage           int default 400,
    number_of_panels        int default 2,
    include_battery         boolean default false,
    battery_kwh             float default 0,
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
    'Saved EcoSim simulation results with denormalized metrics for fast reads.';

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
    'User feedback on recommendations, UI, or bugs.';

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
    'Scraped renewable energy equipment pricing history for cost trend analysis.';

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
-- 2. NEW: Indexes
-- ========================================================================

create index if not exists idx_user_homes_user_id         on public.user_homes(user_id);
create index if not exists idx_user_homes_municipality_id on public.user_homes(municipality_id);
create index if not exists idx_profiles_home_id            on public.home_energy_profiles(home_id);
create index if not exists idx_simulations_home_id       on public.home_simulations(home_id);
create index if not exists idx_simulations_home_created  on public.home_simulations(home_id, created_at desc);
create index if not exists idx_simulations_recommended_source on public.home_simulations(recommended_source);
create index if not exists idx_comparisons_home_id       on public.simulation_comparisons(home_id);
create index if not exists idx_feedback_user_id          on public.user_feedback(user_id);
create index if not exists idx_feedback_simulation_id    on public.user_feedback(simulation_id);
create index if not exists idx_equipment_category        on public.equipment_prices(category);
create index if not exists idx_equipment_scraped_at      on public.equipment_prices(scraped_at desc);
create index if not exists idx_scores_composite          on public.municipality_renewable_scores(composite_score desc);

-- ========================================================================
-- 3. NEW: Views
-- ========================================================================

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
    '12-month climate averages per municipality using the latest year of NASA POWER data.';

-- ========================================================================
-- 4. Triggers
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

-- ========================================================================
-- 5. Row-Level Security (RLS)
-- ========================================================================

alter table public.user_homes enable row level security;
alter table public.home_energy_profiles enable row level security;
alter table public.home_simulations enable row level security;
alter table public.simulation_comparisons enable row level security;
alter table public.user_feedback enable row level security;
alter table public.equipment_prices enable row level security;

create policy if not exists "Users own their homes"
    on public.user_homes for all using (user_id = auth.uid());

create policy if not exists "Users own their profiles"
    on public.home_energy_profiles for all
    using (home_id in (select home_id from public.user_homes where user_id = auth.uid()));

create policy if not exists "Users own their simulations"
    on public.home_simulations for all
    using (home_id in (select home_id from public.user_homes where user_id = auth.uid()));

create policy if not exists "Users own their comparisons"
    on public.simulation_comparisons for all
    using (home_id in (select home_id from public.user_homes where user_id = auth.uid()));

create policy if not exists "Users see their own feedback"
    on public.user_feedback for all using (user_id = auth.uid());

create policy if not exists "Allow public read on equipment_prices"
    on public.equipment_prices for select using (true);
create policy if not exists "Allow authenticated write on equipment_prices"
    on public.equipment_prices for all using (auth.role() = 'authenticated');
