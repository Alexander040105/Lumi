-- Province-level atlas resources computed from Global Solar Atlas / Global Wind Atlas rasters.
-- Run this after creating municipality_atlas_averages and ingesting municipal atlas data.

create table if not exists public.province_atlas_averages (
  province_id integer primary key references public.provinces(province_id) on update cascade on delete restrict,
  province_name text,
  centroid_lat double precision,
  centroid_lon double precision,

  -- Area-weighted municipality aggregation
  muni_avg_solar_pvout_annual_kwh_kwp double precision,
  muni_avg_solar_pvout_daily_kwh_kwp double precision,
  muni_avg_solar_ghi_kwh_m2_day double precision,
  muni_avg_solar_dni_kwh_m2_day double precision,
  muni_avg_solar_dif_kwh_m2_day double precision,
  muni_avg_solar_gti_kwh_m2_day double precision,
  muni_avg_solar_temp_c double precision,
  muni_avg_solar_optimal_tilt_deg double precision,
  muni_avg_wind_speed_10m_ms double precision,
  muni_avg_wind_speed_50m_ms double precision,
  muni_avg_wind_speed_100m_ms double precision,
  muni_count smallint,

  -- Direct province centroid sample from rasters
  centroid_solar_pvout_annual_kwh_kwp double precision,
  centroid_solar_pvout_daily_kwh_kwp double precision,
  centroid_solar_ghi_kwh_m2_day double precision,
  centroid_solar_dni_kwh_m2_day double precision,
  centroid_solar_dif_kwh_m2_day double precision,
  centroid_solar_gti_kwh_m2_day double precision,
  centroid_solar_temp_c double precision,
  centroid_solar_optimal_tilt_deg double precision,
  centroid_wind_speed_10m_ms double precision,
  centroid_wind_speed_50m_ms double precision,
  centroid_wind_speed_100m_ms double precision,

  -- Reconciled / final values (default to area-weighted municipal average)
  solar_pvout_annual_kwh_kwp double precision,
  solar_pvout_daily_kwh_kwp double precision,
  solar_ghi_kwh_m2_day double precision,
  solar_dni_kwh_m2_day double precision,
  solar_dif_kwh_m2_day double precision,
  solar_gti_kwh_m2_day double precision,
  solar_temp_c double precision,
  solar_optimal_tilt_deg double precision,
  wind_speed_10m_ms double precision,
  wind_speed_50m_ms double precision,
  wind_speed_100m_ms double precision,

  -- Diagnostics
  reconciliation_note text,

  data_source text not null default 'Global Solar Atlas / Global Wind Atlas',
  updated_at timestamptz not null default now()
);

comment on table public.province_atlas_averages is
  'Solar and wind atlas values for each province, computed both as an area-weighted average of municipalities and as a direct centroid sample.';

comment on column public.province_atlas_averages.solar_pvout_annual_kwh_kwp is
  'Reconciled annual PV specific yield; by default the area-weighted municipal average.';
