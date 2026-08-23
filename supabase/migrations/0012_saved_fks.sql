-- Add missing municipality_id foreign keys so the frontend can join municipalities(name)
-- on saved_locations and saved_simulations without a PostgREST 400 error.

-- saved_locations.municipality_id is NOT NULL; restrict deletion of a municipality that is bookmarked.
alter table public.saved_locations
  drop constraint if exists saved_locations_municipality_id_fkey;
alter table public.saved_locations
  add constraint saved_locations_municipality_id_fkey
  foreign key (municipality_id) references public.municipalities(municipality_id)
  on update cascade on delete restrict;

-- saved_simulations.municipality_id is nullable; set null if a referenced municipality is deleted.
alter table public.saved_simulations
  drop constraint if exists saved_simulations_municipality_id_fkey;
alter table public.saved_simulations
  add constraint saved_simulations_municipality_id_fkey
  foreign key (municipality_id) references public.municipalities(municipality_id)
  on update cascade on delete set null;
