# LUMI Auth Guide: Normal Users & Admin Accounts

This guide covers the complete authentication flow in LUMI — how normal users register and log in, and how developers manually create and manage admin accounts. All users (normal and admin) use the **same login page**. Roles are assigned after authentication via the `user_roles` table.

---

## 1. How Normal Users Sign Up & Log In

### 1.1 Sign Up (Email / Password)

1. Open the app and click **"Sign Up"** on the login page.
2. Enter email and password.
3. Supabase sends a confirmation email.
4. Click the confirmation link in the email.
5. The `on_auth_user_created` trigger automatically:
   - Creates a profile in `public.profiles` (with `plan = 'free'`)
   - Assigns `role = 'user'` in `public.user_roles`

### 1.2 Sign Up (Google OAuth)

1. Click **"Continue with Google"**.
2. Complete Google consent.
3. Supabase creates the user and fires the same trigger as above.
4. User is redirected back to the app with an active session.

### 1.3 Log In

1. Go to `/login`.
2. Enter email + password, or click Google OAuth.
3. Supabase returns a JWT access token.
4. The frontend stores the session in `AuthContext`.
5. `AuthContext` automatically fetches the user's `role` from `user_roles`.
6. The user is redirected to `/dashboard`.

> **Normal users** will never see the Admin Portal link in the navigation.

---

## 2. How Devs Create an Admin Account

> **Critical:** Admin accounts are **never** created through the public UI. Only developers with access to the Supabase Dashboard can create them.

### Method A: Supabase Dashboard (Recommended — Easiest)

Use this for creating your own admin account for thesis demo and testing.

#### Step 1: Create the User in Supabase Auth

1. Go to your [Supabase Dashboard](https://supabase.com/dashboard).
2. Select your LUMI project.
3. Navigate to **Auth → Users**.
4. Click **"Add user"** (top-right).
5. Choose **"Send invitation"** or **"Create new user"**:
   - **Option A (Invitation):** Enter the admin email. Supabase sends an invite link. The admin clicks it and sets their own password.
   - **Option B (Direct):** Enter email + password manually. The user is immediately active (skip email confirmation).
6. Note the **User ID (UUID)** of the newly created user.

#### Step 2: Assign the Admin Role

1. In the Supabase Dashboard, go to **SQL Editor**.
2. Run the following query (replace `USER_UUID_HERE` with the actual UUID):

```sql
-- Set this user as an admin
update public.user_roles
set role = 'admin'
where user_id = 'USER_UUID_HERE';
```

3. Verify the role was set:

```sql
select * from public.user_roles
where user_id = 'USER_UUID_HERE';
```

You should see:

| user_id | role | created_at |
|---------|------|------------|
| `USER_UUID_HERE` | `admin` | *(timestamp)* |

> **Important:** If you see **"Success. No rows returned"** (0 rows affected), this means the `user_roles` row for this user does not exist yet. This happens for accounts created **before** the `handle_new_user` trigger was set up (e.g., an old Google OAuth account). In that case, use **INSERT** instead of **UPDATE**:
>
> ```sql
> -- For existing users created BEFORE the trigger existed
> insert into public.user_roles (user_id, role, created_at)
> values ('USER_UUID_HERE', 'admin', now())
> on conflict (user_id) do update set role = 'admin';
>
> -- Also ensure they have a profile row (admins are always premium)
> insert into public.profiles (id, full_name, plan, is_active, created_at)
> values ('USER_UUID_HERE', 'Admin User', 'premium', true, now())
> on conflict (id) do update set plan = 'premium';
> ```
>
> **Note:** Admin and dev accounts are **always treated as premium** by the system, regardless of the `plan` value stored in `profiles`. The backend automatically overrides the plan to `premium` for any user with `role = 'admin'` or `role = 'dev'`. This ensures admins never hit free-tier limits.

#### Step 3: Log In as Admin

1. Go to the LUMI app: `http://localhost:5173/login`.
2. Enter the admin email and password.
3. After login, look at the navigation bar.
4. If you see **"Admin Portal"**, the role is working correctly.
5. Click it to access `/admin`.

---

### Method B: Local Seed Script (For Fresh Environments)

Use this when setting up LUMI on a new machine or after resetting the database.

1. Make sure you have the **Service Role Key** from Supabase Dashboard → Project Settings → API.
2. Set environment variables:

```bash
export SUPABASE_URL=https://<your-project>.supabase.co
export SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
```

3. Run the seed script (from the repo root):

```bash
cd d:\63947\Documents\GitHub\Lumi
.venv\Scripts\activate
python scripts\seed_admin.py
```

4. The script will:
   - Create a user with email `admin@lumi.local`.
   - Assign `role = 'admin'` in `user_roles`.
   - Print the admin user ID and role.

> **Note:** The seed script only works if the `user_roles` and `profiles` tables + trigger already exist. Run the schema SQL first (see [Section 4](#4-database-schema)).

---

### Method C: Dev-Only API Endpoint (Advanced)

If you need to promote an existing user to admin without the dashboard:

```bash
# Requires a hardcoded dev secret in the backend
curl -X POST http://localhost:8000/api/v1/dev/promote-to-admin \
  -H "Authorization: Bearer <ADMIN_JWT>" \
  -H "X-Dev-Secret: <your-dev-secret>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER_UUID_HERE", "role": "admin"}'
```

> This endpoint is **not exposed in the frontend** and should only be used in emergencies.

---

## 3. What Happens When an Admin Logs In

The flow is identical to a normal user, but the `role` fetched from `user_roles` is `"admin"`:

```
User opens /login
     │
     ▼
Enters credentials → Supabase validates → Returns JWT
     │
     ▼
Frontend stores session in AuthContext
     │
     ▼
AuthContext calls: supabase.from("user_roles").select("role")
     │
     ▼
Role = "admin" → isAdmin = true
     │
     ▼
Navigation bar now shows "Admin Portal" link
     │
     ▼
User clicks /admin → AdminRoute guard checks isAdmin
     │
     ▼
Admin dashboard renders
```

### Admin-Only Backend Endpoints

When an admin hits a protected endpoint (e.g., `GET /api/v1/admin/users`), the backend:

1. Extracts the JWT from the `Authorization` header.
2. Verifies the JWT with `verify_jwt()`.
3. Calls `_get_user_role(user_id)` to fetch the role from `user_roles`.
4. If role is not `"admin"` or `"dev"`, returns **403 Forbidden**.

---

## 4. Database Schema

Ensure these tables exist before creating admin accounts:

```sql
-- Role enum
create type public.app_role as enum ('user', 'admin', 'dev');

-- User roles table (one per user)
create table public.user_roles (
  user_id uuid primary key references auth.users on delete cascade,
  role public.app_role not null default 'user',
  created_at timestamptz default now()
);

-- User profiles (extends auth.users with app-specific data)
create table public.profiles (
  id uuid primary key references auth.users on delete cascade,
  full_name text,
  avatar_url text,
  plan text default 'free',
  is_active boolean default true,
  created_at timestamptz default now()
);

-- Trigger: auto-create profile + role on every signup
create function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, full_name)
  values (new.id, new.raw_user_meta_data->>'full_name');

  insert into public.user_roles (user_id, role)
  values (new.id, 'user');

  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- Admin audit log (tracks admin actions)
create table public.admin_audit_log (
  id uuid primary key default gen_random_uuid(),
  admin_id uuid references auth.users,
  action text not null,
  target_user_id uuid references auth.users,
  details jsonb default '{}',
  created_at timestamptz default now()
);
```

### Row-Level Security (RLS) Policies

```sql
-- Users can only read their own role
alter table public.user_roles enable row level security;

create policy "Users read own role"
  on public.user_roles for select
  using (auth.uid() = user_id);

-- Admins can read all roles (needed for /admin/users)
create policy "Admins read all roles"
  on public.user_roles for select
  using (exists (
    select 1 from public.user_roles ur
    where ur.user_id = auth.uid() and ur.role = 'admin'
  ));

-- Users can read their own profile
alter table public.profiles enable row level security;

create policy "Users read own profile"
  on public.profiles for select
  using (auth.uid() = id);
```

---

## 5. Quick Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| **"Admin Portal" link not showing** | Role is still `"user"` | Re-run the SQL `update user_roles set role = 'admin'` with the correct UUID |
| **"Success. No rows returned" when running UPDATE** | User was created BEFORE the `handle_new_user` trigger existed | Use `INSERT INTO public.user_roles ... ON CONFLICT DO UPDATE` instead (see Method A Step 2) |
| **403 on `/admin` routes** | `require_admin` middleware rejecting | Verify role in Supabase SQL Editor; ensure JWT is valid |
| **New user has no `user_roles` row** | Trigger not created | Run the `handle_new_user()` trigger SQL above |
| **Admin link shows for everyone** | Frontend `isAdmin` check broken | Verify `AuthContext.jsx` is fetching role from `user_roles` table |
| **Cannot log in as admin** | Wrong password / unconfirmed email | Use Supabase Dashboard → Auth → Users → reset password |

---

---

## 6. Normal User vs Admin: What Each Sees

### Normal User Experience

When a user with `role = 'user'` logs in, they see:

| Screen / Feature | What a Normal User Sees |
|------------------|-------------------------|
| **Navigation bar** | Home, EcoSim, EnergyHub, Dashboard, Settings, Logout |
| **Dashboard** | Their own saved simulations, saved locations, AI insights, recommendations |
| **EcoSim** | Run simulations, save up to 3 scenarios (free tier), compare scenarios, export PDF |
| **EnergyHub** | National analytics, choropleth map, forecasts — read only |
| **Chatbot** | 5 questions per month, generic knowledge base |
| **Settings** | Profile info, preferences, subscription status (free/premium) |
| **Admin Portal link** | **Not visible** |

### Admin User Experience

When a user with `role = 'admin'` logs in, they see **everything a normal user sees** PLUS the Admin Portal:

| Screen / Feature | What an Admin Sees |
|------------------|--------------------|
| **Navigation bar** | Normal links + **"Admin Portal"** link |
| **Dashboard** | Same personal dashboard, but with a banner: "You are logged in as Admin" |
| **EcoSim / EnergyHub** | Same as normal user |
| **Admin Portal** | Four sub-modules (see below) |

---

## 7. How the Admin Operates — Module by Module

### 7.1 User Management (`/admin/users`)

This is the admin's primary tool for overseeing the user base.

**What it shows:**
- A paginated table of **all registered users**.
- Columns: Email, Full Name, Role, Plan, Sign-up Date, Simulation Count, Status.
- **Search bar** to find users by email or name.
- **Filters**: Active / Banned / Free / Premium / Admin.

**What the admin can do:**

| Action | How to Do It | What Happens |
|--------|--------------|--------------|
| **View a user's saved simulations** | Click the user's row → "View Simulations" button | Opens a drawer showing all saved EcoSim scenarios for that user |
| **Ban / suspend a user** | Toggle the "Active" switch in the user's row | Sets `profiles.is_active = false`; the user can no longer log in |
| **Unban a user** | Toggle the "Active" switch back on | Sets `profiles.is_active = true` |
| **Change a user's plan** | Dropdown in the user's row: Free / Researcher / Planner | Updates `profiles.plan`; useful for giving premium access to thesis panelists |
| **Promote a user to admin** | Dropdown in the user's row: "Make Admin" (dev-only accounts see this) | Updates `user_roles.role = 'admin'`; an entry is written to `admin_audit_log` |
| **Export user list** | Click "Export CSV" button | Downloads a CSV with all user data for offline reporting |

**Example workflow — Banning a spam user:**
1. Go to `/admin/users`.
2. Search for the spammer's email.
3. Toggle the "Active" switch to OFF.
4. The user is immediately locked out on their next request.
5. The action is logged in `admin_audit_log`.

---

### 7.2 Analytics Dashboard (`/admin/analytics`)

This gives the admin a bird's-eye view of how the platform is being used.

**Metrics displayed:**

| Metric | Data Source | Why It Matters |
|--------|-------------|----------------|
| **Total Registered Users** | `auth.users` count | Platform growth |
| **Simulations Run (Today)** | `saved_simulations` filtered by `created_at` | Daily activity |
| **Simulations Run (All Time)** | `saved_simulations` total count | Overall engagement |
| **Most-Searched Municipalities** | Aggregate `municipality_id` from `saved_simulations` | Shows which areas users care about |
| **Chatbot Conversations (Today)** | `chat_messages` filtered by `created_at` | AI feature usage |
| **Free vs Premium Distribution** | `profiles.plan` grouped by value | Monetization funnel health |
| **Peak Usage Hours** | `created_at` timestamps aggregated by hour | Helps plan infrastructure |

**Example workflow — Checking if the chatbot is popular:**
1. Go to `/admin/analytics`.
2. Look at the "Chatbot Conversations (Today)" card.
3. If the number is low, consider increasing the free tier limit in `/admin/config`.

---

### 7.3 Content Moderation (`/admin/moderate`)

This module lets admins review chatbot conversations for inappropriate content.

**What it shows:**
- A paginated table of **all chat sessions**.
- Columns: Session ID, User Email, Message Count, Created At, Flagged Status.
- Drill-down: Click a row to see the full conversation transcript.

**What the admin can do:**

| Action | How to Do It | What Happens |
|--------|--------------|--------------|
| **Flag a conversation** | Click the flag icon next to a session | Marks the session as flagged in the database |
| **Delete a session** | Click the trash icon | Removes all messages in that session from `chat_messages` |
| **Filter by user** | Enter an email in the search bar | Shows only that user's chat history |
| **Filter by flagged** | Toggle "Show Flagged Only" | Shows only flagged sessions |

> **Note:** For thesis defense, this module can be **read-only** (view conversations without delete/flag). This is acceptable to demonstrate the feature.

**Example workflow — Investigating a complaint:**
1. A user emails: "The chatbot gave me bad advice."
2. Admin goes to `/admin/moderate`.
3. Searches for the user's email.
4. Reads the conversation transcript to understand the issue.
5. Decides whether to flag the session or adjust the chatbot's system prompt.

---

### 7.4 System Config (`/admin/config`)

This is the admin's control panel for tuning the platform's behavior.

**Toggles and settings:**

| Setting | Default | What It Controls |
|---------|---------|-------------------|
| **Free Chat Limit** | 5 | How many chatbot questions a free user gets per month |
| **Free Simulation Limit** | 3 | How many simulations a free user can save |
| **Chatbot Enabled** | ON | Global on/off switch for the chatbot feature |
| **Maintenance Banner** | (empty text) | If filled, shows a yellow banner on all pages |
| **ARIMA Forecast Refresh** | (button) | Triggers the backend to reload forecast CSV artifacts |

**Example workflow — Increasing free limits for a demo:**
1. Thesis panelists will use the system during the defense.
2. Go to `/admin/config`.
3. Change "Free Chat Limit" from 5 to 50.
4. Change "Free Simulation Limit" from 3 to 10.
5. Click "Save Changes".
6. All free users now have higher limits for the demo period.

**Example workflow — Enabling maintenance mode:**
1. Before deploying a major update, go to `/admin/config`.
2. Fill the "Maintenance Banner" field: "Scheduled maintenance at 2 PM. Save your work."
3. The banner appears on every page for all users.
4. After maintenance, clear the field and click "Save Changes."

---

## 8. Key Differences Summarized

| Aspect | Normal User | Admin |
|--------|-------------|-------|
| **Login URL** | `/login` (same) | `/login` (same) |
| **Sign-up** | Public form | Only via Supabase Dashboard (devs) |
| **Navbar** | No Admin link | Has "Admin Portal" link |
| **Dashboard** | Personal data only | Personal data + admin banner |
| **EcoSim** | Save their own simulations (limit based on plan) | Same (unlimited — admin is always premium) |
| **EnergyHub** | Read-only analytics | Same |
| **Chatbot** | Limited questions (based on plan) | Unlimited — admin is always premium |
| **Admin Portal** | Invisible / 403 if guessed | Full access to Users, Analytics, Moderation, Config |
| **Can view other users' data?** | No | Yes — via User Management |
| **Can change system settings?** | No | Yes — via System Config |
| **Can ban users?** | No | Yes — via User Management |
| **Can export data?** | Their own PDF reports | User CSVs, system analytics |

---

## 9. Security Checklist for Devs

- [ ] Never expose `SUPABASE_SERVICE_ROLE_KEY` in frontend code or `.env` files that are committed.
- [ ] Admin accounts are created **only** via Supabase Dashboard or local seed scripts.
- [ ] There is **no public UI** for registering as an admin.
- [ ] The `/admin` route is not linked in the navbar unless `isAdmin === true`.
- [ ] Backend `require_admin` rejects all non-admin requests with **403**, even if the URL is guessed.
- [ ] The `user_roles` table has RLS enabled so users cannot read each other's roles.
- [ ] Audit logging is enabled for admin actions (banning users, promoting roles, config changes).
- [ ] Admin actions that modify data (ban, promote, delete) write to `admin_audit_log` for accountability.
