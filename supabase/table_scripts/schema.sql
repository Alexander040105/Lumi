-- Supabase schema for regions, provinces, municipalities, barangays.

create table if not exists public.regions (
  region_id integer primary key,
  name text not null,
  lat double precision,
  lon double precision
);

create table if not exists public.provinces (
  province_id integer primary key,
  region_id integer not null references public.regions(region_id) on update cascade on delete restrict,
  name text not null,
  lat double precision,
  lon double precision
);

create table if not exists public.municipalities (
  municipality_id integer primary key,
  province_id integer not null references public.provinces(province_id) on update cascade on delete restrict,
  name text not null,
  lat double precision,
  lon double precision
);

create table if not exists public.barangays (
  barangay_id integer primary key,
  municipality_id integer not null references public.municipalities(municipality_id) on update cascade on delete restrict,
  name text not null,
  lat double precision,
  lon double precision
);

create index if not exists idx_provinces_region_id on public.provinces(region_id);
create index if not exists idx_municipalities_province_id on public.municipalities(province_id);
create index if not exists idx_barangays_municipality_id on public.barangays(municipality_id);

-- Joined view (no data duplication)
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

-- Materialized joined table (snapshot). Run after importing CSVs.
create table if not exists public.regional_lookup_flat (
  region_id integer not null,
  region_name text not null,
  region_lat double precision,
  region_lon double precision,
  province_id integer not null,
  province_name text not null,
  province_lat double precision,
  province_lon double precision,
  municipality_id integer not null,
  municipality_name text not null,
  municipality_lat double precision,
  municipality_lon double precision,
  barangay_id integer not null,
  barangay_name text not null,
  barangay_lat double precision,
  barangay_lon double precision,
  primary key (barangay_id)
);

-- Refresh data in the flat table when needed.
-- truncate public.regional_lookup_flat;
-- insert into public.regional_lookup_flat (
--   region_id, region_name, region_lat, region_lon,
--   province_id, province_name, province_lat, province_lon,
--   municipality_id, municipality_name, municipality_lat, municipality_lon,
--   barangay_id, barangay_name, barangay_lat, barangay_lon
-- )
-- select
--   region_id, region_name, region_lat, region_lon,
--   province_id, province_name, province_lat, province_lon,
--   municipality_id, municipality_name, municipality_lat, municipality_lon,
--   barangay_id, barangay_name, barangay_lat, barangay_lon
-- from public.regional_lookup;

-- If tables already exist, run these once:
-- alter table public.regions add column if not exists lat double precision;
-- alter table public.regions add column if not exists lon double precision;
-- alter table public.provinces add column if not exists lat double precision;
-- alter table public.provinces add column if not exists lon double precision;
-- alter table public.municipalities add column if not exists lat double precision;
-- alter table public.municipalities add column if not exists lon double precision;
-- alter table public.barangays add column if not exists lat double precision;
-- alter table public.barangays add column if not exists lon double precision;
