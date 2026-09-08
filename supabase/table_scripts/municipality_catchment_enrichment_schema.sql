-- Municipality catchment enrichment schema
-- Run this after importing municipalities and provinces.
--
-- Data source (CC-BY 4.0):
--   Boothroyd, R.J., Williams, R.D., Hoey, T.B., et al. (2023).
--   National-scale geodatabase of catchment characteristics in the
--   Philippines for river management applications.
--   PLOS ONE, 18(3), e0281933.
--   https://pmc.ncbi.nlm.nih.gov/articles/PMC9994713/

create table if not exists public.municipality_catchment_enrichment (
  municipality_id integer not null references public.municipalities(municipality_id) on update cascade on delete restrict,
  province_id     integer not null references public.provinces(province_id) on update cascade on delete restrict,

  -- Catchment assignment
  catchment_name text,
  catchment_match_method text,
  catchment_distance_m double precision,

  -- Catchment morphology
  catchment_area_km2 double precision,
  catchment_mean_slope_deg double precision,
  catchment_relief_m double precision,
  catchment_drainage_density_km_km2 double precision,
  catchment_hypsometric_integral double precision,
  catchment_ruggedness_number double precision,
  catchment_melton_ruggedness double precision,
  catchment_mean_stream_slope_m_m double precision,

  -- Nearest household-relevant stream (order 1-2)
  nearest_stream_gradient_m_m double precision,
  nearest_stream_upstream_area_km2 double precision,
  nearest_stream_order integer,
  nearest_stream_elevation_m double precision,
  distance_to_nearest_stream_m double precision,

  -- Derived household-scale fields
  effective_catchment_area_km2 double precision,
  stream_head_m double precision,
  stream_feasibility_penalty double precision,
  enriched_runoff_coefficient double precision,

  -- Metadata
  data_source text not null default 'Boothroyd et al. 2023 (PMC9994713)',
  updated_at  timestamptz not null default now(),

  primary key (municipality_id)
);

create index if not exists idx_catchment_enrichment_province
  on public.municipality_catchment_enrichment (province_id);

create index if not exists idx_catchment_enrichment_catchment_name
  on public.municipality_catchment_enrichment (catchment_name);

comment on table public.municipality_catchment_enrichment is
  'Per-municipality catchment morphology and nearest-stream data from Boothroyd et al. 2023 national geodatabase (PMC9994713).';

comment on column public.municipality_catchment_enrichment.stream_head_m is
  'Estimated hydraulic head from nearest stream gradient × assumed penstock length (100 m).';

comment on column public.municipality_catchment_enrichment.stream_feasibility_penalty is
  '0.1-1.0 multiplier reflecting distance to nearest stream. 1.0 within 2 km, decays to 0.1 at 10+ km.';

comment on column public.municipality_catchment_enrichment.effective_catchment_area_km2 is
  'Household-scale catchment area = real basin area × 0.001 fraction, capped at 1.0 km².';

comment on column public.municipality_catchment_enrichment.enriched_runoff_coefficient is
  'Runoff coefficient refined by drainage density and hypsometric integral.';
