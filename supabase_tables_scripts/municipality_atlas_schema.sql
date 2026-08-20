-- Municipality-level atlas resources extracted from Global Solar Atlas and Global Wind Atlas rasters.
-- Run this after importing municipalities and geospatial_metadata.

create table if not exists public.municipality_atlas_averages (
  municipality_id integer not null references public.municipalities(municipality_id) on update cascade on delete restrict,
  province_id     integer not null references public.provinces(province_id) on update cascade on delete restrict,
  centroid_lat    double precision not null,
  centroid_lon    double precision not null,

  -- Global Solar Atlas (AvgDailyTotals)
  solar_ghi_kwh_m2_day      double precision,  -- Long-term yearly average daily GHI (kWh/m2/day)
  solar_dni_kwh_m2_day      double precision,  -- Direct normal irradiance (kWh/m2/day)
  solar_dif_kwh_m2_day      double precision,  -- Diffuse horizontal irradiance (kWh/m2/day)
  solar_gti_kwh_m2_day      double precision,  -- Global tilted irradiance at optimum tilt (kWh/m2/day)
  solar_pvout_annual_kwh_kwp double precision, -- PV specific yield (kWh/kWp/year)
  solar_pvout_daily_kwh_kwp  double precision, -- solar_pvout_annual_kwh_kwp / 365
  solar_temp_c              double precision,  -- Long-term yearly average temperature (C)
  solar_optimal_tilt_deg    double precision,  -- Optimum tilt angle (degrees)

  -- Global Wind Atlas
  wind_speed_10m_ms  double precision,
  wind_speed_50m_ms  double precision,
  wind_speed_100m_ms double precision,
  wind_speed_150m_ms double precision,

  -- Metadata
  data_source text not null default 'Global Solar Atlas / Global Wind Atlas',
  updated_at  timestamptz not null default now(),

  primary key (municipality_id)
);

create index if not exists idx_muni_atlas_province
  on public.municipality_atlas_averages (province_id);

comment on table public.municipality_atlas_averages is
  'Solar and wind atlas values sampled at municipal centroids from Global Solar Atlas and Global Wind Atlas GeoTIFFs.';

comment on column public.municipality_atlas_averages.solar_pvout_annual_kwh_kwp is
  'Annual PV specific yield in kWh/kWp/year, including temperature, soiling and system losses, from Global Solar Atlas.';

comment on column public.municipality_atlas_averages.wind_speed_100m_ms is
  'Long-term average wind speed at 100 m hub height from Global Wind Atlas (m/s).';
