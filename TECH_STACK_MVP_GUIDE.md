# Tech Stack MVP Guide (4 Weeks)

This guide highlights the minimum React + FastAPI + Supabase stack knowledge you need to build the Lumi MVP in 4 weeks. Each section is the essentials only.

## 0) Core goals for 4 weeks

- Keep scope tight: one or two core flows, not all features.
- Ship weekly: a working demo at the end of each week.
- Avoid architecture rabbit holes: follow existing patterns in this repo.

## 1) React (Vite)

What to know
- Components and props: build UI as reusable components.
- State and effects: `useState` for local state, `useEffect` for data fetching and side effects.
- Routing: routes live in [react-frontend/src/routes/AppRoutes.jsx](react-frontend/src/routes/AppRoutes.jsx).
- Auth context: use [react-frontend/src/context/AuthContext.jsx](react-frontend/src/context/AuthContext.jsx).
- API calls: use [react-frontend/src/services/apiClient.js](react-frontend/src/services/apiClient.js).

Code pattern: fetch data with auth
```jsx
import { useEffect, useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { getProtectedMe } from "../services/apiClient";

export default function ProfileCard() {
	const { accessToken } = useAuth();
	const [profile, setProfile] = useState(null);

	useEffect(() => {
		if (!accessToken) return;
		getProtectedMe(accessToken).then((data) => setProfile(data.user));
	}, [accessToken]);

	if (!profile) return <div>Loading...</div>;
	return <pre>{JSON.stringify(profile, null, 2)}</pre>;
}
```
Reference: [react-frontend/src/pages/Dashboard.jsx](react-frontend/src/pages/Dashboard.jsx)

Key habits
- Keep page logic in [react-frontend/src/pages](react-frontend/src/pages).
- Keep API integration inside [react-frontend/src/services](react-frontend/src/services).
- Use [react-frontend/src/components/ui](react-frontend/src/components/ui) for consistent UI.

Common pitfalls
- Mixing fetch logic inside UI components.
- Skipping loading and error states.
- Not using the auth context when calling protected APIs.

Deeper example: protected route guard
```jsx
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function ProtectedRoute({ children }) {
	const { session, loading } = useAuth();
	const location = useLocation();

	if (loading) return <div>Loading...</div>;
	if (!session) return <Navigate to="/login" state={{ from: location }} replace />;
	return children;
}
```
Reference: [react-frontend/src/components/shared/ProtectedRoute.jsx](react-frontend/src/components/shared/ProtectedRoute.jsx)

Deeper example: simple form + validation pattern
```jsx
import { useState } from "react";

export default function SimpleForm({ onSave }) {
	const [label, setLabel] = useState("");
	const [error, setError] = useState("");

	const handleSubmit = (event) => {
		event.preventDefault();
		if (label.trim().length < 2) {
			setError("Label must be at least 2 characters");
			return;
		}
		setError("");
		onSave({ label });
		setLabel("");
	};

	return (
		<form onSubmit={handleSubmit} className="space-y-2">
			<input value={label} onChange={(e) => setLabel(e.target.value)} />
			{error && <p className="text-sm text-red-500">{error}</p>}
			<button type="submit">Save</button>
		</form>
	);
}
```

## 2) Tailwind CSS

What to know
- Utility-first CSS: combine small classes in JSX.
- Responsive classes: `sm:`, `md:`, `lg:`.
- Shared layout classes: `page-container`, `stack` in globals.

Files to know
- [react-frontend/src/styles/globals.css](react-frontend/src/styles/globals.css)
- [react-frontend/tailwind.config.cjs](react-frontend/tailwind.config.cjs)

Key habits
- Keep custom CSS in globals and reuse classes.
- Favor Tailwind utilities over inline styles.

Code pattern: layout utilities
```jsx
export default function Page() {
	return (
		<section className="page-container stack">
			<h1 className="text-2xl font-semibold">Title</h1>
			<div className="grid gap-4 md:grid-cols-2">
				<div className="rounded-lg border p-4">Card A</div>
				<div className="rounded-lg border p-4">Card B</div>
			</div>
		</section>
	);
}
```
Reference: [react-frontend/src/pages/Dashboard.jsx](react-frontend/src/pages/Dashboard.jsx)

Deeper example: reusable layout class
```css
/* globals.css */
.page-container {
	max-width: 1100px;
	margin: 0 auto;
	padding: 2rem 1.5rem;
}

.stack > * + * {
	margin-top: 1.25rem;
}
```
Reference: [react-frontend/src/styles/globals.css](react-frontend/src/styles/globals.css)

## 3) shadcn/ui

What to know
- Components are copied into your repo, so you own them.
- Add new components with `npx shadcn-ui@latest add <component>`.

Files to know
- [react-frontend/components.json](react-frontend/components.json)
- [react-frontend/src/components/ui](react-frontend/src/components/ui)

Key habits
- Prefer composition: wrap UI primitives instead of rewriting them.
- Edit component source directly when needed.

Code pattern: compose UI primitives
```jsx
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function CTA() {
	return (
		<Card>
			<CardHeader>
				<CardTitle>Get started</CardTitle>
			</CardHeader>
			<CardContent>
				<Button>Continue</Button>
			</CardContent>
		</Card>
	);
}
```
Reference: [react-frontend/src/pages/Login.jsx](react-frontend/src/pages/Login.jsx)

Deeper example: pattern for loading states
```jsx
import { Button } from "@/components/ui/button";

export default function SubmitButton({ loading, children }) {
	return (
		<Button type="submit" disabled={loading}>
			{loading ? "Saving..." : children}
		</Button>
	);
}
```

## 4) FastAPI

What to know
- Routers live in [fastapi-backend/app/routes](fastapi-backend/app/routes).
- Business logic goes in [fastapi-backend/app/services](fastapi-backend/app/services).
- Schemas (Pydantic models) go in [fastapi-backend/app/schemas](fastapi-backend/app/schemas).
- Auth dependencies live in [fastapi-backend/app/dependencies/auth.py](fastapi-backend/app/dependencies/auth.py).

Key habits
- Keep route handlers thin: validate input and call services.
- Use dependency injection for auth and shared resources.

Code pattern: router + schema + service
```py
# app/schemas/example.py
from pydantic import BaseModel

class ExampleIn(BaseModel):
	label: str

class ExampleOut(BaseModel):
	label: str
	saved: bool

# app/services/example.py
def save_example(data: ExampleIn) -> ExampleOut:
	return ExampleOut(label=data.label, saved=True)

# app/routes/example.py
from fastapi import APIRouter
from app.schemas.example import ExampleIn, ExampleOut
from app.services.example import save_example

router = APIRouter()

@router.post("/", response_model=ExampleOut)
async def create_example(payload: ExampleIn):
	return save_example(payload)
```
Reference: [fastapi-backend/app/routes/example.py](fastapi-backend/app/routes/example.py)

Common pitfalls
- Putting logic in routes instead of services.
- Returning raw database objects without a schema.

Deeper example: CRUD router layout
```py
# app/routes/items.py
from fastapi import APIRouter, Depends
from app.dependencies.auth import get_verified_user
from app.schemas.item import ItemIn, ItemOut
from app.services.items import create_item, list_items

router = APIRouter()

@router.get("/", response_model=list[ItemOut])
async def read_items(user=Depends(get_verified_user)):
	return list_items(user_id=user.get("sub"))

@router.post("/", response_model=ItemOut)
async def create(payload: ItemIn, user=Depends(get_verified_user)):
	return create_item(payload, user_id=user.get("sub"))
```

Deeper example: service layer access
```py
# app/services/items.py
from app.schemas.item import ItemIn, ItemOut

def list_items(user_id: str) -> list[ItemOut]:
	return []

def create_item(payload: ItemIn, user_id: str) -> ItemOut:
	return ItemOut(id="temp", label=payload.label, owner_id=user_id)
```

## 5) Supabase (Auth + Postgres)

What to know
- Frontend uses anon key to sign users in.
- Backend validates JWTs using the JWT secret.
- Keep service role keys only on backend.

Files to know
- Frontend client: [react-frontend/src/services/supabaseClient.js](react-frontend/src/services/supabaseClient.js)
- Backend auth: [fastapi-backend/app/auth/jwt.py](fastapi-backend/app/auth/jwt.py)

Key habits
- Use RLS in Supabase tables.
- Always pass the access token to FastAPI for protected routes.

Code pattern: email/password + Google
```js
// Email/password sign in
await supabase.auth.signInWithPassword({ email, password });

// Google OAuth
await supabase.auth.signInWithOAuth({ provider: "google" });
```
Reference: [react-frontend/src/context/AuthContext.jsx](react-frontend/src/context/AuthContext.jsx)

Code pattern: backend token validation
```py
from jose import jwt

payload = jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"], options={"verify_aud": False})
```
Reference: [fastapi-backend/app/auth/jwt.py](fastapi-backend/app/auth/jwt.py)

Deeper example: basic Supabase query (backend)
```py
from app.services.supabase_service import get_supabase_client

client = get_supabase_client()
result = client.table("items").select("id,label").eq("owner_id", user_id).execute()
rows = result.data or []
```

Deeper example: enforce email verification
```py
from fastapi import Depends
from app.dependencies.auth import get_verified_user

@router.get("/secure")
async def secure_endpoint(user=Depends(get_verified_user)):
	return {"ok": True}
```
Reference: [fastapi-backend/app/dependencies/auth.py](fastapi-backend/app/dependencies/auth.py)

## 6) Redis (session cache)

What to know
- Use Redis for short-lived session or cache data.
- Keep TTLs reasonable (minutes or hours).

Files to know
- Client helper: [fastapi-backend/app/services/redis_client.py](fastapi-backend/app/services/redis_client.py)
- Example endpoint: [fastapi-backend/app/routes/protected.py](fastapi-backend/app/routes/protected.py)

Key habits
- Use a namespaced key like `user:{id}:session`.
- Always set an expiry with `ex=...`.

Code pattern: set a session in Redis
```py
from app.services.redis_client import get_redis

redis = get_redis()
await redis.set("user:123:session", "{\"lastPage\": \"/dashboard\"}", ex=3600)
```
Reference: [fastapi-backend/app/routes/protected.py](fastapi-backend/app/routes/protected.py)

Deeper example: read + delete session
```py
value = await redis.get("user:123:session")
await redis.delete("user:123:session")
```

## 7) Environment variables

What to know
- Frontend uses `VITE_` prefixed vars.
- Backend reads `.env` via Pydantic settings.

Files to know
- Backend settings: [fastapi-backend/app/config/settings.py](fastapi-backend/app/config/settings.py)
- Frontend env helpers: [react-frontend/src/utils/env.js](react-frontend/src/utils/env.js)

Key habits
- Never commit secrets.
- Use separate Supabase projects for dev and prod.

Code pattern: frontend env usage
```js
export function getApiBaseUrl() {
	return import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
}
```
Reference: [react-frontend/src/utils/env.js](react-frontend/src/utils/env.js)

Deeper example: backend settings usage
```py
from app.config.settings import get_settings

settings = get_settings()
print(settings.supabase_url)
```
Reference: [fastapi-backend/app/config/settings.py](fastapi-backend/app/config/settings.py)

## 8) MVP development plan (4 weeks)

Week 1: Core auth + navigation
- Email/password + Google sign in working.
- One protected page with API call.

Week 1 deliverable checklist
- Login, logout, reset password.
- Dashboard loads user profile from FastAPI.

Week 2: Main data flow
- Core feature endpoints in FastAPI.
- CRUD in Supabase with RLS.

Week 2 deliverable checklist
- One complete CRUD feature in UI and API.
- RLS policies tested in Supabase.

Week 3: UX polish
- Loading states, empty states, validation.
- Tailwind and shadcn components to improve UI.

Week 3 deliverable checklist
- Loading and error states on every screen.
- Form validation on client and server.

Week 4: Production readiness
- Fix auth edge cases, logs, error handling.
- Deploy front + back with correct envs.

Week 4 deliverable checklist
- Deployment with correct env vars.
- Smoke test script or checklist.

## 9) Local commands you will use often

Frontend
- `npm install`
- `npm run dev`

Backend
- `pip install -r requirements.txt`
- `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

## 10) MVP checklist

- Login, logout, and session persistence.
- One core user flow end-to-end.
- Data validation on frontend and backend.
- Basic error handling and logs.
- Deployed demo with real data.

## 11) End-to-end CRUD example (UI + API + Supabase)

This example shows a full Items feature: table, RLS policy, FastAPI routes, and React UI.

### Step A: Supabase table

Create a table named `items` with these columns:

- id (uuid, primary key, default: gen_random_uuid())
- owner_id (uuid, not null)
- label (text, not null)
- created_at (timestamp, default: now())

### Step B: RLS policy

Enable RLS on `items` and add this policy (owner-only CRUD):

```sql
create policy "Owner can manage items"
on items
for all
using (auth.uid() = owner_id)
with check (auth.uid() = owner_id);
```

### Step C: FastAPI schema

Create schemas:

```py
# app/schemas/item.py
from pydantic import BaseModel

class ItemIn(BaseModel):
	label: str

class ItemOut(BaseModel):
	id: str
	label: str
	owner_id: str
```

### Step D: FastAPI service

```py
# app/services/items.py
from app.schemas.item import ItemIn, ItemOut
from app.services.supabase_service import get_supabase_client

def list_items(user_id: str) -> list[ItemOut]:
	client = get_supabase_client()
	result = client.table("items").select("id,label,owner_id").eq("owner_id", user_id).execute()
	rows = result.data or []
	return [ItemOut(**row) for row in rows]

def create_item(payload: ItemIn, user_id: str) -> ItemOut:
	client = get_supabase_client()
	result = (
		client.table("items")
		.insert({"label": payload.label, "owner_id": user_id})
		.select("id,label,owner_id")
		.single()
		.execute()
	)
	return ItemOut(**result.data)
```

### Step E: FastAPI routes

```py
# app/routes/items.py
from fastapi import APIRouter, Depends
from app.dependencies.auth import get_verified_user
from app.schemas.item import ItemIn, ItemOut
from app.services.items import list_items, create_item

router = APIRouter()

@router.get("/", response_model=list[ItemOut])
async def read_items(user=Depends(get_verified_user)):
	return list_items(user_id=user.get("sub"))

@router.post("/", response_model=ItemOut)
async def add_item(payload: ItemIn, user=Depends(get_verified_user)):
	return create_item(payload, user_id=user.get("sub"))
```

Register the router in the API index:

```py
# app/routes/api.py
from app.routes.items import router as items_router

api_router.include_router(items_router, prefix="/items", tags=["items"])
```

Reference: [fastapi-backend/app/routes/api.py](fastapi-backend/app/routes/api.py)

### Step F: React service

```js
// src/services/apiClient.js
export function listItems(token) {
	return request("/items/", { token });
}

export function createItem(token, payload) {
	return request("/items/", {
		token,
		method: "POST",
		body: JSON.stringify(payload)
	});
}
```

Reference: [react-frontend/src/services/apiClient.js](react-frontend/src/services/apiClient.js)

### Step G: React UI

```jsx
import { useEffect, useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { createItem, listItems } from "../services/apiClient";

export default function ItemsPanel() {
	const { accessToken } = useAuth();
	const [items, setItems] = useState([]);
	const [label, setLabel] = useState("");

	useEffect(() => {
		if (!accessToken) return;
		listItems(accessToken).then(setItems);
	}, [accessToken]);

	const handleCreate = async (event) => {
		event.preventDefault();
		const item = await createItem(accessToken, { label });
		setItems((prev) => [item, ...prev]);
		setLabel("");
	};

	return (
		<section className="space-y-3">
			<form onSubmit={handleCreate} className="flex gap-2">
				<input value={label} onChange={(e) => setLabel(e.target.value)} placeholder="Label" />
				<button type="submit">Add</button>
			</form>
			<ul className="space-y-2">
				{items.map((item) => (
					<li key={item.id}>{item.label}</li>
				))}
			</ul>
		</section>
	);
}
```

### Step H: Test flow

1. Sign in (email/password or Google).
2. Create an item in the UI.
3. Reload and confirm list returns only your items.
4. Try with another user to ensure RLS blocks cross-user access.
