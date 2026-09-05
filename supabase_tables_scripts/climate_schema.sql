-- Historical monthly climate data per municipality (NASA POWER).

create table if not exists public.municipality_climate_monthly (
  municipality_id integer not null,
  year smallint not null,
  month smallint not null,
  t2m double precision,
  t2m_max double precision,
  t2m_min double precision,
  rh2m double precision,
  prectotcorr double precision,
  ws10m double precision,
  allsky_sfc_sw_dwn double precision,
  source text not null default 'NASA POWER',
  created_at timestamptz not null default now(),
  constraint municipality_climate_monthly_pkey primary key (municipality_id, year, month),
  constraint municipality_climate_monthly_municipality_id_fkey foreign key (municipality_id)
    references public.municipalities (municipality_id)
    on update cascade
    on delete restrict,
  constraint municipality_climate_monthly_year_check check (year >= 2018),
  constraint municipality_climate_monthly_month_check check (month between 1 and 12)
);

comment on table public.municipality_climate_monthly is
  'Monthly historical climate data by municipality from NASA POWER.';

comment on column public.municipality_climate_monthly.t2m is
  'Mean air temperature at 2m (C).';
comment on column public.municipality_climate_monthly.t2m_max is
  'Maximum air temperature at 2m (C).';
comment on column public.municipality_climate_monthly.t2m_min is
  'Minimum air temperature at 2m (C).';
comment on column public.municipality_climate_monthly.rh2m is
  'Relative humidity at 2m (%).';
comment on column public.municipality_climate_monthly.prectotcorr is
  'Precipitation corrected (mm/day).';
comment on column public.municipality_climate_monthly.ws10m is
  'Wind speed at 10m (m/s).';
comment on column public.municipality_climate_monthly.allsky_sfc_sw_dwn is
  'All-sky surface shortwave downward irradiance (kWh/m^2/day).';
comment on column public.municipality_climate_monthly.source is
  'Data source identifier.';

create index if not exists idx_climate_monthly_municipality_id
  on public.municipality_climate_monthly (municipality_id);

create index if not exists idx_climate_monthly_year_month
  on public.municipality_climate_monthly (year, month);

create index if not exists idx_climate_monthly_municipality_year_month
  on public.municipality_climate_monthly (municipality_id, year, month);
