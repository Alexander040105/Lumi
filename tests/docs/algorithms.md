# LUMI Algorithms Documentation

This document describes the algorithms implemented in the LUMI backend and frontend for the Auth, Chatbot, Dashboard, Saved Data, and Admin Portal features.

---

## 1. Role-Based Access Control (RBAC)

**Location:** `fastapi-backend/app/dependencies/auth.py`

### `_get_user_role(user_id: str) -> str`
Fetches the user's role from the `user_roles` Supabase table. If the query fails or returns no data, defaults to `"user"`.

### `get_current_user_with_role(user)`
Wraps `get_verified_user` and enriches the returned user dict with a `"role"` key.

### `require_admin(user)`
Calls `_get_user_role` and raises `HTTPException(403)` if the role is not `"admin"` or `"dev"`.

**Algorithm:**
1. Extract `sub` (user UUID) from JWT claims
2. Query `user_roles` table: `SELECT role WHERE user_id = sub`
3. If `role IN ('admin', 'dev')`: return enriched user dict
4. Else: raise `HTTPException(status_code=403, detail="Admin access required")`

---

## 2. RAG-Powered Chatbot

**Location:** `fastapi-backend/app/routes/chat.py`

### `_retrieve_context(query, municipality_id, top_k)`
Calls the existing `rag_pipeline.retrieve_with_filter()` to get semantically relevant chunks from the FAISS index.

### `_build_chat_prompt(query, chunks, user_context)`
Assembles a structured prompt with:
- System identity: "You are LUMI, a Renewable Energy Decision Support Assistant"
- Grounding instruction: "Answer using ONLY the retrieved context below"
- Retrieved chunks formatted as `[Source N] chunk_text`
- Optional user context (saved simulations, saved locations)
- User question

### `_generate_response(prompt)`
Calls `gemini_funcs.generate_chat_response(prompt)` and returns the generated text.

### `chat_message(payload, user)`
**Algorithm:**
1. Validate that `message` is non-empty
2. Create or reuse `chat_session` row
3. Persist user message to `chat_messages`
4. Run RAG retrieval: `chunks = retrieve_with_filter(message, municipality_id)`
5. Build prompt with chunks and user context
6. Generate response via Gemini API
7. Persist assistant message with `retrieved_chunks` metadata
8. Return `{session_id, role, message, retrieved_chunks}`

---

## 3. Decision Dashboard Composite Scoring

**Location:** `react-frontend/src/pages/Dashboard.jsx` (frontend computation)

### Composite Renewable Score
For a selected municipality, fetches suitability scores from:
- `solar_suitability` table → `solar_score`
- `wind_suitability` table → `wind_score`
- `hydropower_suitability` table → `hydro_score`
- `geothermal_suitability` table → `geothermal_score`

**Algorithm:**
```
composite = (solar_score + wind_score + hydro_score + geothermal_score) / 4
normalized = min(100, max(0, composite))
```

### Recommendation Ranking
For each renewable source at the selected municipality:
1. Fetch estimated generation (kWh/month) from EcoSim calculator
2. Compute simple payback: `installation_cost / (monthly_savings * 12)`
3. Compute carbon reduction using DOE grid emission factor
4. Calculate weighted score: `0.4 * generation_normalized + 0.3 * payback_inverted + 0.3 * carbon_normalized`
5. Sort sources by score descending
6. Return top 3 with CTA links

---

## 4. Admin Analytics Aggregation

**Location:** `fastapi-backend/app/routes/admin.py`

### `get_analytics()`
**Algorithm:**
1. Query `profiles` table with `count=exact` → `total_users`
2. Query `saved_simulations` table with `count=exact` → `total_simulations`
3. Query `chat_sessions` table with `count=exact` → `total_chat_sessions`
4. Count `free_users` and `premium_users` by iterating `plan` field from profiles data
5. Log admin action to `admin_audit_log`
6. Return aggregated metrics dict

---

## 5. Auto-Create Profile on Signup

**Location:** `tests/docs/supabase_schema_additions.sql`

### `handle_new_user()` Trigger
Fires `AFTER INSERT ON auth.users`.

**Algorithm:**
1. Insert into `profiles(id, full_name)` using `NEW.raw_user_meta_data->>'full_name'`
2. Insert into `user_roles(user_id, role)` with role = `'user'`
3. Insert into `user_usage_limits(user_id, plan)` with plan = `'free'`
4. Return `NEW`

This ensures zero-downtime profile creation without application-level code.

---

## 6. Row-Level Security (RLS) Ownership Check

**Location:** `tests/docs/supabase_schema_additions.sql`

### `chat_messages` RLS Policy
```sql
CREATE POLICY "Users can CRUD own chat messages"
ON public.chat_messages FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM public.chat_sessions s
        WHERE s.id = session_id AND s.user_id = auth.uid()
    )
);
```

This is a **transitive ownership check**: the policy does not directly compare `chat_messages` to `auth.uid()`, but instead verifies that the message's parent session belongs to the current user.

---

## 7. Frontend Route Guard Algorithm

**Location:** `react-frontend/src/components/shared/ProtectedRoute.jsx` and `AdminRoute.jsx`

### `ProtectedRoute`
1. Read `session` and `loading` from `AuthContext`
2. If `loading`: render `<Loading />` skeleton
3. If `!session`: redirect to `/login` with `state.from = currentLocation`
4. Else: render `children`

### `AdminRoute`
1. Read `user`, `isAdmin`, and `loading` from `AuthContext`
2. If `loading`: render `<Loading />` skeleton
3. If `!user`: redirect to `/login`
4. If `!isAdmin`: redirect to `/dashboard`
5. Else: render `children`

---

## 8. Profile Update Endpoint

**Location:** `fastapi-backend/app/routes/protected.py`

### `update_profile(payload, user)`
**Algorithm:**
1. Define `allowed_fields = {"full_name", "organization", "location", "preferred_municipality_id", "avatar_url"}`
2. Filter payload: `updates = {k: v for k, v in payload.items() if k in allowed_fields}`
3. If `updates` is empty: raise `HTTPException(400, "No valid fields")`
4. Execute `UPDATE profiles SET ... WHERE id = user.sub`
5. Return updated profile row

This whitelisting approach prevents injection of unexpected fields (e.g., `is_active`, `plan`) through the public API.
