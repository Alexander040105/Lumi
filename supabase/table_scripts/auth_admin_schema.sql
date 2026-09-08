-- =============================================================================
-- LUMI Auth, Admin & User Management Schema
-- =============================================================================
-- Run this in the Supabase SQL Editor to set up (or fix) all tables,
-- triggers, RLS policies, and indexes needed for authentication,
-- user roles, profiles, saved simulations, chat history, audit logging,
-- and admin system configuration.
--
-- All statements are idempotent — safe to re-run.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. Role enum
-- ---------------------------------------------------------------------------
do $$
begin
  if not exists (select 1 from pg_type where typname = 'app_role') then
    create type public.app_role as enum ('user', 'admin', 'dev');
  end if;
end $$;

-- ---------------------------------------------------------------------------
-- 2. Profiles (extends auth.users with app-specific data)
-- ---------------------------------------------------------------------------
create table if not exists public.profiles (
  id uuid primary key references auth.users on delete cascade,
  full_name text,
  avatar_url text,
  organization text,
  location text,
  preferred_municipality_id integer,
  plan text default 'free',
  is_active boolean default true,
  created_at timestamptz default now()
);

comment on table public.profiles is 'Extended user profile linked to Supabase Auth.';

-- ---------------------------------------------------------------------------
-- 3. User roles (one row per user)
-- ---------------------------------------------------------------------------
create table if not exists public.user_roles (
  user_id uuid primary key references auth.users on delete cascade,
  role public.app_role not null default 'user',
  created_at timestamptz default now()
);

comment on table public.user_roles is 'Role-based access control (user/admin/dev).';

-- ---------------------------------------------------------------------------
-- 4. Admin audit log (tracks every admin action)
-- ---------------------------------------------------------------------------
create table if not exists public.admin_audit_log (
  id uuid primary key default gen_random_uuid(),
  admin_id uuid references auth.users,
  action text not null,
  target_user_id uuid references auth.users,
  details jsonb default '{}',
  created_at timestamptz default now()
);

comment on table public.admin_audit_log is 'Immutable log of admin actions for accountability.';

-- ---------------------------------------------------------------------------
-- 5. Saved simulations (EcoSim runs per user)
-- ---------------------------------------------------------------------------
create table if not exists public.saved_simulations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users on delete cascade,
  municipality_id integer references public.municipalities(municipality_id),
  name text,
  source text default 'ecosim',
  inputs jsonb default '{}',
  results jsonb default '{}',
  created_at timestamptz default now()
);

create index if not exists idx_saved_simulations_user_id on public.saved_simulations(user_id);
create index if not exists idx_saved_simulations_municipality_id on public.saved_simulations(municipality_id);

-- ---------------------------------------------------------------------------
-- 6. Chat sessions (conversation threads)
-- ---------------------------------------------------------------------------
create table if not exists public.chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users on delete cascade,
  title text default 'New Chat',
  is_flagged boolean default false,
  created_at timestamptz default now()
);

create index if not exists idx_chat_sessions_user_id on public.chat_sessions(user_id);

-- ---------------------------------------------------------------------------
-- 7. Chat messages (individual messages inside a session)
-- ---------------------------------------------------------------------------
create table if not exists public.chat_messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.chat_sessions on delete cascade,
  role text not null check (role in ('user', 'assistant', 'system')),
  content text not null,
  created_at timestamptz default now()
);

create index if not exists idx_chat_messages_session_id on public.chat_messages(session_id);

-- ---------------------------------------------------------------------------
-- 8. System config (global key-value settings for admin toggles)
-- ---------------------------------------------------------------------------
create table if not exists public.system_config (
  key text primary key,
  value jsonb not null default '{}',
  updated_at timestamptz default now()
);

-- Seed default config
insert into public.system_config (key, value)
values ('global', jsonb_build_object(
  'chatbot_enabled', true,
  'maintenance_mode', false,
  'free_chat_limit', 5,
  'free_sim_limit', 3
))
on conflict (key) do nothing;

-- ---------------------------------------------------------------------------
-- 9. Trigger: auto-create profile + role on new auth user
-- ---------------------------------------------------------------------------
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, full_name, plan, is_active, created_at)
  values (new.id, new.raw_user_meta_data->>'full_name', 'free', true, now())
  on conflict (id) do nothing;

  insert into public.user_roles (user_id, role, created_at)
  values (new.id, 'user', now())
  on conflict (user_id) do nothing;

  return new;
end;
$$ language plpgsql security definer;

-- Drop then recreate trigger to avoid duplicate-trigger errors
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- ---------------------------------------------------------------------------
-- 10. RLS Policies
-- ---------------------------------------------------------------------------

-- Profiles: users read/update own, admins read all
alter table public.profiles enable row level security;

drop policy if exists "Users read own profile" on public.profiles;
create policy "Users read own profile"
  on public.profiles for select
  using (auth.uid() = id);

drop policy if exists "Users update own profile" on public.profiles;
create policy "Users update own profile"
  on public.profiles for update
  using (auth.uid() = id)
  with check (auth.uid() = id);

-- Helper: check admin status without RLS recursion (runs as table owner)
create or replace function public.is_admin()
returns boolean
language sql
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.user_roles
    where user_id = auth.uid() and role in ('admin', 'dev')
  );
$$;

drop policy if exists "Admins read all profiles" on public.profiles;
create policy "Admins read all profiles"
  on public.profiles for select
  using (public.is_admin());

-- User roles: users read own, admins read all
alter table public.user_roles enable row level security;

drop policy if exists "Users read own role" on public.user_roles;
create policy "Users read own role"
  on public.user_roles for select
  using (auth.uid() = user_id);

drop policy if exists "Admins read all roles" on public.user_roles;
create policy "Admins read all roles"
  on public.user_roles for select
  using (public.is_admin());

-- Admin audit log: only admins can read
alter table public.admin_audit_log enable row level security;

drop policy if exists "Admins read audit log" on public.admin_audit_log;
create policy "Admins read audit log"
  on public.admin_audit_log for select
  using (public.is_admin());

-- Saved simulations: users manage own
alter table public.saved_simulations enable row level security;

drop policy if exists "Users manage own simulations" on public.saved_simulations;
create policy "Users manage own simulations"
  on public.saved_simulations for all
  using (auth.uid() = user_id);

-- Chat sessions: users manage own
alter table public.chat_sessions enable row level security;

drop policy if exists "Users manage own chat sessions" on public.chat_sessions;
create policy "Users manage own chat sessions"
  on public.chat_sessions for all
  using (auth.uid() = user_id);

-- Chat messages: users manage via session ownership
alter table public.chat_messages enable row level security;

drop policy if exists "Users manage own chat messages" on public.chat_messages;
create policy "Users manage own chat messages"
  on public.chat_messages for all
  using (exists (
    select 1 from public.chat_sessions cs
    where cs.id = session_id and cs.user_id = auth.uid()
  ));

-- System config: everyone can read, only admins can write
alter table public.system_config enable row level security;

drop policy if exists "Anyone read system config" on public.system_config;
create policy "Anyone read system config"
  on public.system_config for select
  to authenticated, anon
  using (true);

drop policy if exists "Admins update system config" on public.system_config;
create policy "Admins update system config"
  on public.system_config for all
  using (public.is_admin());

-- ---------------------------------------------------------------------------
-- 11. Fix: ensure existing pre-trigger users get profiles + roles
-- ---------------------------------------------------------------------------
insert into public.profiles (id, full_name, plan, is_active, created_at)
select id, raw_user_meta_data->>'full_name', 'free', true, now()
from auth.users
where not exists (select 1 from public.profiles p where p.id = auth.users.id)
on conflict (id) do nothing;

insert into public.user_roles (user_id, role, created_at)
select id, 'user', now()
from auth.users
where not exists (select 1 from public.user_roles ur where ur.user_id = auth.users.id)
on conflict (user_id) do nothing;

-- Ensure all existing admin/dev accounts are on premium
update public.profiles
set plan = 'premium'
from public.user_roles
where public.profiles.id = public.user_roles.user_id
  and public.user_roles.role in ('admin', 'dev')
  and public.profiles.plan != 'premium';

-- ---------------------------------------------------------------------------
-- 10. Storage: avatars bucket
-- ---------------------------------------------------------------------------
-- Create the bucket if it doesn't exist (run via Supabase dashboard SQL editor)
-- Note: bucket creation via SQL requires appropriate privileges.
-- If this fails, create the bucket manually in Storage → New bucket.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('avatars', 'avatars', true, 2097152, array['image/jpeg','image/png','image/webp','image/gif'])
on conflict (id) do nothing;

-- Policy: anyone can read avatars
drop policy if exists "Public read avatars" on storage.objects;
create policy "Public read avatars"
  on storage.objects for select
  using (bucket_id = 'avatars');

-- Policy: authenticated users can upload to their own folder
drop policy if exists "Users upload own avatar" on storage.objects;
create policy "Users upload own avatar"
  on storage.objects for insert
  with check (
    bucket_id = 'avatars'
    and auth.uid() is not null
    and (storage.foldername(name))[1] = auth.uid()::text
  );

-- Policy: authenticated users can update/delete their own avatars
drop policy if exists "Users manage own avatar" on storage.objects;
create policy "Users manage own avatar"
  on storage.objects for all
  using (
    bucket_id = 'avatars'
    and auth.uid() is not null
    and (storage.foldername(name))[1] = auth.uid()::text
  );

-- ---------------------------------------------------------------------------
-- 12. Promote a user to admin (run manually with target email)
-- ---------------------------------------------------------------------------
-- Uncomment and replace 'user@example.com' with the actual email, then run:
--
-- update public.user_roles
-- set role = 'admin'
-- where user_id = (select id from auth.users where email = 'user@example.com');
--
-- update public.profiles
-- set plan = 'premium'
-- where id = (select id from auth.users where email = 'user@example.com');
