# LUMI Deployment Guide — Vercel (Frontend) + Render (Backend)

Deploy the LUMI frontend to **Vercel** and the FastAPI backend to **Render's free tier**, with the full RAG AI assistant preserved for your thesis proposal defense.

---

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Step 1: Backend on Render](#step-1-backend-on-render)
- [Step 2: Frontend on Vercel](#step-2-frontend-on-vercel)
- [Step 3: Connect Frontend to Backend](#step-3-connect-frontend-to-backend)
- [Step 4: Warm Up RAG Before Demo](#step-4-warm-up-rag-before-demo)
- [Post-Deployment Checklist](#post-deployment-checklist)
- [Troubleshooting](#troubleshooting)
- [Optional: Pre-Compute Embeddings](#optional-pre-compute-embeddings)
- [Upgrading from Free Tier](#upgrading-from-free-tier)

---

## Architecture

```
┌─────────────────┐         HTTPS          ┌──────────────────┐
│  User Browser   │───────────────────────▶│  Vercel          │
│                 │                        │  React SPA       │
└─────────────────┘                        └────────┬─────────┘
                                                   │
                                                   │ HTTPS
                                                   ▼
                                          ┌──────────────────┐
                                          │  Render          │
                                          │  FastAPI         │
                                          │  (port $PORT)    │
                                          └────────┬─────────┘
                                                   │
                        ┌──────────────────────────┼──────────────────────────┐
                        │                          │                          │
                        ▼                          ▼                          ▼
                  ┌──────────┐            ┌──────────────┐            ┌──────────┐
                  │ Supabase │            │ Gemini / Groq│            │ NASA     │
                  │ (DB+Auth)│            │ (LLM APIs)   │            │ POWER    │
                  └──────────┘            └──────────────┘            └──────────┘
```

---

## Prerequisites

| Service | Purpose | Cost |
|---------|---------|------|
| [Vercel](https://vercel.com) | Frontend hosting | Free (generous) |
| [Render](https://render.com) | Backend hosting | Free tier (512MB RAM) |
| [Supabase](https://supabase.com) | PostgreSQL + Auth | Free tier sufficient |
| [Google AI Studio](https://aistudio.google.com/app/apikey) | Gemini API | Free tier sufficient |
| [Groq Console](https://console.groq.com/keys) | Groq LLM API | Free tier (rate limited) |
| [GitHub](https://github.com) | Git repo hosting | Free |

---

## Environment Variables

### Backend (`fastapi-backend/` — set in Render dashboard)

Create these in **Render → Dashboard → Service → Environment**.

| Variable | Required | Example / How to get |
|----------|----------|---------------------|
| `SUPABASE_URL` | Yes | Supabase Dashboard → Settings → API → Project URL |
| `SUPABASE_ANON_KEY` | Yes | Supabase Dashboard → Settings → API → `anon` key |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Supabase Dashboard → Settings → API → `service_role` key |
| `SUPABASE_JWT_SECRET` | Yes | Supabase Dashboard → Settings → JWT Settings → JWT Secret |
| `GEMINI_API_KEY` | Yes | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `GROQ_API_KEY` | Yes | [Groq Console](https://console.groq.com/keys) |
| `CORS_ORIGINS` | Yes | `["https://lumi-frontend.vercel.app"]` (your exact Vercel URL) |
| `RAG_ENABLED` | No | `true` (default) |
| `RAG_WARMUP_ON_STARTUP` | No | `false` (default; saves RAM at boot) |
| `UPSTASH_REDIS_URL` | No | Leave blank for free tier |

> **Important**: On Render, env vars are injected directly into the process — there is no `.env` file. The backend code already falls back to `os.environ` when `.env` is missing.

### Frontend (`react-frontend/` — set in Vercel dashboard)

| Variable | Required | Example |
|----------|----------|---------|
| `VITE_API_BASE_URL` | Yes | `https://lumi-backend.onrender.com/api/v1` |
| `VITE_SUPABASE_URL` | Yes | Same as backend `SUPABASE_URL` |
| `VITE_SUPABASE_ANON_KEY` | Yes | Same as backend `SUPABASE_ANON_KEY` |

---

## Step 1: Backend on Render

### 1.1 Push Code to GitHub

Make sure everything is committed, including the new files (`render.yaml`, `vercel.json`, etc.):

```bash
git add .
git commit -m "Add Vercel + Render deployment config"
git push origin main
```

### 1.2 Create a New Web Service on Render

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **New → Web Service**
3. Connect your **GitHub** account and select the LUMI repo
4. Fill in the form:

| Field | Value |
|-------|-------|
| Name | `lumi-backend` |
| Root Directory | `fastapi-backend` |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1` |
| Plan | **Free** |

5. Click **Advanced** and add the environment variables from the table above
6. Click **Create Web Service**

### 1.3 Wait for Build

- Render will install dependencies (~2–5 minutes)
- On free tier, installing `torch` + `sentence-transformers` + `faiss-cpu` takes the most time
- If the build fails with "Killed" or exceeds 15 minutes, see [Troubleshooting](#troubleshooting)

### 1.4 Verify Health Endpoint

Once the deploy finishes, open:

```
https://lumi-backend.onrender.com/
```

You should see:
```json
{"status": "ok", "service": "Lumi API"}
```

Also verify RAG status:
```
https://lumi-backend.onrender.com/rag/status
```

---

## Step 2: Frontend on Vercel

### 2.1 Import Project

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repo
3. In the project settings:

| Field | Value |
|-------|-------|
| Framework Preset | Vite |
| Root Directory | `react-frontend` |
| Build Command | `npm run build` |
| Output Directory | `dist` |

4. Add environment variables:
   - `VITE_API_BASE_URL=https://lumi-backend.onrender.com/api/v1`
   - `VITE_SUPABASE_URL=...`
   - `VITE_SUPABASE_ANON_KEY=...`

5. Click **Deploy**

### 2.2 SPA Routing

`vercel.json` (already in repo) handles React Router paths:
```json
{
  "rewrites": [{"source": "/(.*)", "destination": "/index.html"}]
}
```

---

## Step 3: Connect Frontend to Backend

### 3.1 Update Render CORS

After Vercel gives you a production URL, update the `CORS_ORIGINS` env var on Render:

```
CORS_ORIGINS=["https://lumi-frontend.vercel.app"]
```

> If you use a custom domain, include that too: `["https://lumi.example.com", "https://lumi-frontend.vercel.app"]`

### 3.2 Redeploy Render

Render will auto-restart with the new CORS value. No manual redeploy needed.

---

## Step 4: Warm Up RAG Before Demo

### The Cold Start Problem

On Render's free tier:
- The service **sleeps after 15 minutes of inactivity**
- When it wakes up, the first AI chat request triggers loading of the embedding model (~30–60 seconds)
- The model uses ~150–200MB RAM

### Pre-Warm Before Your Defense

**Option A: Hit the `/warmup` endpoint**

```bash
curl https://lumi-backend.onrender.com/warmup
```

Or just open it in a browser. It will:
1. Load the FAISS index
2. Load the embedding model into memory
3. Return stats: `{"status": "warmed_up", "rag_stats": {...}}`

**Option B: Send a test chat message**

Ask the AI assistant anything before the demo starts. The first response may take 30–60s; subsequent responses will be fast.

**Best Practice for Defense Day**:
- Open the site **5 minutes before** your presentation
- Send one chat question to trigger warmup
- Keep the tab open so the service doesn't sleep

---

## Post-Deployment Checklist

| Check | How to Test |
|-------|-------------|
| Homepage loads | Open Vercel URL |
| API health | `GET /` → `{"status": "ok"}` |
| RAG status | `GET /rag/status` → shows `rag_enabled: true`, chunk count |
| EnergyHub dashboard | Navigate, check charts load |
| Ecosim simulation | Select "MALAY", enter bill & consumption, generate |
| AI chat (warm) | Ask "What renewable source is best for my home?" |
| AI chat (cold) | Wait 15 min idle, then ask again — may be slow |
| Map choropleth | Check province colors render |
| User login | Register / log in via Supabase Auth |
| Forecast chart | Check historical + projected data |

---

## Troubleshooting

### Build fails with "Killed" on Render

**Cause**: `pip install` of `torch` + `sentence-transformers` + `faiss-cpu` uses too much RAM during build.

**Fix**: The pre-built wheels should install fine. If they don't:
1. Switch to the **Starter tier** ($7/month, 2GB RAM) — zero code changes needed
2. Or see [Optional: Pre-Compute Embeddings](#optional-pre-compute-embeddings) to eliminate model loading

### 502 Bad Gateway after deploy

**Cause**: Backend crashed on startup (likely OOM when loading model).

**Fix**:
1. Check Render logs for `MemoryError` or OOM kill
2. Set `RAG_ENABLED=false` in Render env vars → backend starts without RAG
3. AI chat will still work but without citation-backed context
4. Upgrade to Starter tier to re-enable full RAG

### CORS errors in browser

**Symptom**: Console shows `Access-Control-Allow-Origin` errors.

**Fix**: Update `CORS_ORIGINS` on Render to **exactly** match your Vercel URL, including `https://` and no trailing slash.

```
CORS_ORIGINS=["https://lumi-frontend.vercel.app"]
```

### AI assistant responds without citations

**Cause**: RAG is unavailable (model failed to load or `RAG_ENABLED=false`).

**Check**: `GET /rag/status` on the backend. If `rag_enabled: false` or `index_present: false`, the AI is running in "direct Gemini" mode.

### Service sleeps during demo

**Symptom**: First request after a pause takes 30–60s.

**Fix**: Keep the site active before presenting. Hit `/warmup` 5 minutes before your slot. For guaranteed uptime, upgrade to Starter tier.

---

## Optional: Pre-Compute Embeddings

If the embedding model still won't load on 512MB RAM, you can eliminate runtime model loading entirely by pre-computing all embeddings offline.

### Step A: Run locally

```bash
cd fastapi-backend
python -m scripts.precompute_embeddings
```

This creates `app/services/local_data/rag_precomputed.json` with every chunk's embedding vector already computed.

### Step B: Modify rag_pipeline.py

In `retrieve_context`, instead of calling `_get_embedder()` and encoding the query on the fly, load the pre-computed vectors and use cosine similarity manually (no FAISS or model needed). This reduces RAM usage by ~200MB.

> This is a fallback if the standard approach fails. Most free-tier deployments succeed with the pre-built wheels.

---

## Upgrading from Free Tier

If free tier is insufficient, the simplest upgrade path is **Render Starter** ($7/month):

| Feature | Free | Starter |
|---------|------|---------|
| RAM | 512MB | 2GB |
| Sleep | After 15 min idle | Never |
| Build timeout | 15 min | 30 min |
| Disk | Ephemeral | Ephemeral |

**To upgrade**: In Render dashboard → Service → Settings → Plan → **Starter**. Zero code changes. The service will redeploy automatically with more RAM.

---

## Maintenance Commands

### View backend logs
```bash
# On Render: Dashboard → Service → Logs
```

### Check RAG status
```bash
curl https://lumi-backend.onrender.com/rag/status
```

### Manual warmup
```bash
curl https://lumi-backend.onrender.com/warmup
```

### Update after code changes
```bash
git push origin main
# Both Vercel and Render auto-deploy on push
```

---

## Cost Summary

| Service | Tier | Monthly Cost |
|---------|------|-------------|
| Vercel | Hobby (free) | $0 |
| Render | Free | $0 |
| Render | Starter | $7 |
| Supabase | Free | $0 |
| Gemini API | Free | $0 |
| Groq API | Free | $0 |
| **Total (Free)** | | **$0** |
| **Total (Starter)** | | **$7** |

---

*Last updated: June 2026*
