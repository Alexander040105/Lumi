-- Municipal Population Table
-- --------------------------
-- Stores PSA population census data for population-weighted municipal
-- energy demand estimation (Revision 8).
--
-- Data source: Philippine Statistics Authority (PSA) 2020 Census of Population
-- and Housing, or 2025 population projections.
--
-- Load instruction: Insert rows with province_id referencing provinces table,
-- municipality_id referencing municipalities table, and population count.

create table if not exists public.municipal_population (
  id bigint generated always as identity primary key,
  province_id integer not null references public.provinces(province_id) on delete cascade,
  municipality_id integer not null references public.municipalities(municipality_id) on delete cascade,
  population integer not null check (population >= 0),
  year integer not null default 2020,
  source text default 'PSA 2020 Census',
  created_at timestamp with time zone default now()
);

create index if not exists idx_municipal_population_province_id on public.municipal_population(province_id);
create index if not exists idx_municipal_population_municipality_id on public.municipal_population(municipality_id);

-- Example insert (replace with actual PSA data):
-- insert into public.municipal_population (province_id, municipality_id, population, year, source)
-- values (1, 1, 45000, 2020, 'PSA 2020 Census');
