-- ERA5 10-metre wind reanalysis at province centroids.

create table if not exists public.province_era5_averages (
  province_id     integer primary key references public.provinces(province_id) on update cascade on delete restrict,
  province_name   text,
  centroid_lat    double precision,
  centroid_lon    double precision,
  era5_u10_ms     double precision,
  era5_v10_ms     double precision,
  era5_wind_speed_10m_ms double precision,
  data_source     text not null default 'ERA5 (Copernicus)',
  updated_at      timestamptz not null default now()
);

comment on table public.province_era5_averages is
  'ERA5 10 m wind components and scalar speed sampled at each province centroid.';
