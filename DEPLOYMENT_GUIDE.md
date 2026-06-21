# LUMI Deployment Guide

This guide covers deploying the LUMI web application to **DigitalOcean** using two approaches:

1. **[DigitalOcean Droplet + Docker Compose](#approach-1-droplet--docker-compose)** — Full control, lower cost, best for sustained workloads.
2. **[DigitalOcean App Platform](#approach-2-app-platform)** — Fully managed, zero server maintenance, fastest setup.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Approach 1: Droplet + Docker Compose](#approach-1-droplet--docker-compose)
- [Approach 2: App Platform](#approach-2-app-platform)
- [Post-Deployment Checklist](#post-deployment-checklist)
- [Troubleshooting](#troubleshooting)
- [Architecture Overview](#architecture-overview)

---

## Prerequisites

| Item | Version | Notes |
|------|---------|-------|
| Git | Any | To push code |
| Node.js | 20+ | Frontend build |
| npm | 10+ | Frontend build |
| Python | 3.11+ | Backend runtime |
| Docker | 24+ | Droplet approach |
| Docker Compose | 2.20+ | Droplet approach |
| DigitalOcean Account | — | [Sign up here](https://www.digitalocean.com) |
| Supabase Project | — | [Create here](https://supabase.com) |
| Google AI Studio Key | — | For Gemini API |
| Groq API Key | — | For Groq LLM API |

---

## Environment Variables

LUMI requires several API keys and configuration values. **Create a `.env` file at the repo root** using the template below.

> **Never commit `.env` to Git.** It is already in `.gitignore`.

```bash
# Supabase (Database + Auth)
SUPABASE_URL=https://xxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SECRET=your-jwt-secret

# LLM APIs
GEMINI_API_KEY=AI...
GROQ_API_KEY=gsk_...

# Redis (optional — used for caching)
# The backend code expects UPSTASH_REDIS_URL as the variable name.
UPSTASH_REDIS_URL=redis://localhost:6379

# CORS (update with your production domain)
CORS_ORIGINS=["https://your-domain.com"]
```

### Where to get each value

| Variable | Source | How to obtain |
|----------|--------|---------------|
| `SUPABASE_URL` | Supabase Dashboard | Settings → API → Project URL |
| `SUPABASE_ANON_KEY` | Supabase Dashboard | Settings → API → `anon` public key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Dashboard | Settings → API → `service_role` key (keep secret) |
| `SUPABASE_JWT_SECRET` | Supabase Dashboard | Settings → JWT Settings → JWT Secret |
| `GEMINI_API_KEY` | Google AI Studio | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| `GROQ_API_KEY` | Groq Console | [console.groq.com/keys](https://console.groq.com/keys) |

### Frontend Build-time Variables

The frontend also needs env vars, but they are baked in at build time (Vite).

```bash
cd react-frontend
```

Create `react-frontend/.env`:

```
VITE_SUPABASE_URL=https://xxxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
VITE_API_BASE_URL=https://your-domain.com/api/v1
```

---

## Approach 1: Droplet + Docker Compose

This approach deploys LUMI on a single DigitalOcean Droplet using Docker Compose. Nginx serves the React frontend and reverse-proxies API calls to the FastAPI backend.

### Step 1: Provision a Droplet

1. Log in to [DigitalOcean](https://cloud.digitalocean.com).
2. Click **Create → Droplets**.
3. Choose an image: **Ubuntu 24.04 (LTS)**.
4. Choose a plan:
   - **Basic → Premium Intel/AMD**
   - For a thesis demo: **4 GB RAM / 2 CPUs** (`s-2vcpu-4gb`) — minimum recommended.
   - For production: **8 GB RAM / 4 CPUs**.
5. Choose a datacenter region: **Singapore (`SGP1`)** is closest to the Philippines.
6. Authentication: **SSH Key** (recommended) or password.
7. Hostname: `lumi-server`.
8. Click **Create Droplet**.

### Step 2: Point Your Domain (Recommended)

1. Buy or use an existing domain (e.g., `lumi.example.com`).
2. In your DNS provider, create an **A record**:
   - Name: `@` (or subdomain like `lumi`)
   - Value: `<Your Droplet IP>`
   - TTL: 3600

### Step 3: Install Docker on the Droplet

SSH into your Droplet and run:

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to docker group (logout and back in to take effect)
sudo usermod -aG docker $USER
```

### Step 4: Clone the Repo on the Droplet

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git lumi
cd lumi
```

### Step 5: Configure Environment Variables

```bash
# Create the backend .env file at repo root
nano .env
```

Paste your filled-in values from the [Environment Variables](#environment-variables) section above.

Also update `CORS_ORIGINS` to match your domain:

```
CORS_ORIGINS=["https://lumi.example.com"]
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

### Step 6: Build the Frontend

On your **local machine** (or on the Droplet if it has Node.js):

```bash
cd react-frontend

# Create frontend env file
printf "VITE_API_BASE_URL=https://your-domain.com/api/v1\nVITE_SUPABASE_URL=https://xxxxxx.supabase.co\nVITE_SUPABASE_ANON_KEY=eyJ...\n" > .env

npm install
npm run build
```

This creates `react-frontend/dist/` with static files.

### Step 7: Deploy with Docker Compose

Back on the **Droplet**, from the repo root:

```bash
cd ~/lumi

# Build and start all services
docker compose up -d --build

# Verify services are running
docker compose ps

# View logs
docker compose logs -f backend
```

Services will be available:
- **Website**: `http://<DROPLET_IP>` (or your domain once DNS propagates)
- **API**: `http://<DROPLET_IP>/api/v1`
- **Health**: `http://<DROPLET_IP>/`

### Step 8: Enable HTTPS with Let's Encrypt (Recommended)

Install Certbot on the Droplet:

```bash
sudo apt install -y certbot python3-certbot-nginx
```

If you are using the built-in nginx container (from `docker-compose.yml`), run Certbot in standalone mode or use a separate nginx on the host. The easiest method:

**Option A: Host-level nginx (recommended for HTTPS)**

Install nginx on the Droplet host:

```bash
sudo apt install -y nginx
sudo systemctl enable nginx
```

Create `/etc/nginx/sites-available/lumi`:

```nginx
server {
    listen 80;
    server_name lumi.example.com;

    location / {
        proxy_pass http://localhost:80;  # docker-compose nginx
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable it:

```bash
sudo ln -s /etc/nginx/sites-available/lumi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Now obtain SSL:

```bash
sudo certbot --nginx -d lumi.example.com
```

Follow the prompts. Certbot will automatically configure HTTPS redirect.

**Option B: Use Cloudflare (Easiest)**

If you use Cloudflare as your DNS provider, simply enable the **Orange Cloud** (Proxied) mode. Cloudflare will provide automatic HTTPS without needing Certbot.

### Step 9: Updating After Code Changes

```bash
cd ~/lumi
git pull origin main

# Rebuild frontend if changed
cd react-frontend && npm install && npm run build && cd ..

# Restart services
docker compose down
docker compose up -d --build
```

---

## Approach 2: App Platform

DigitalOcean App Platform is a Platform-as-a-Service (PaaS) that builds and deploys directly from Git. It handles SSL, load balancing, and CI/CD automatically.

### Step 1: Push Code to GitHub

Ensure your repo is on GitHub (or GitLab) with all code committed.

```bash
git add .
git commit -m "Prepare for App Platform deployment"
git push origin main
```

### Step 2: Create the App

1. In DigitalOcean, go to **Apps** → **Create App**.
2. Choose **GitHub** as the source.
3. Authorize DigitalOcean to access your repos.
4. Select the **LUMI repo** and the **main** branch.
5. Click **Next**.

### Step 3: Configure Components

App Platform should auto-detect components. Verify the following:

#### Static Site (Frontend)

- **Source Directory**: `react-frontend`
- **Build Command**: `npm install && npm run build`
- **Output Directory**: `dist`
- **Routes**: `/`
- **Catchall Document**: `index.html`

#### Service (Backend)

- **Source Directory**: `fastapi-backend`
- **Dockerfile**: `../deploy/backend/Dockerfile`
- **HTTP Port**: `8080`
- **Health Check Path**: `/`
- **Routes**: `/api`

### Step 4: Set Environment Variables

In the App Platform UI, add the following **App-level** or **Component-level** environment variables.

#### Frontend (Static Site) — Build-time vars

| Key | Value |
|-----|-------|
| `VITE_SUPABASE_URL` | Your Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Your Supabase anon key |
| `VITE_API_BASE_URL` | `https://lumi-xxxxxxxx.ondigitalocean.app/api/v1` (use your App URL) |

#### Backend (Service) — Runtime vars

| Key | Value |
|-----|-------|
| `APP_NAME` | `Lumi API` |
| `API_V1_PREFIX` | `/api/v1` |
| `CORS_ORIGINS` | `["https://lumi-xxxxxxxx.ondigitalocean.app"]` |
| `SUPABASE_URL` | Your Supabase URL |
| `SUPABASE_ANON_KEY` | Your Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Your Supabase service role key |
| `SUPABASE_JWT_SECRET` | Your Supabase JWT secret |
| `UPSTASH_REDIS_URL` | Your Redis URL (or leave blank). Code expects `UPSTASH_REDIS_URL`. |
| `GEMINI_API_KEY` | Your Gemini API key |
| `GROQ_API_KEY` | Your Groq API key |

### Step 5: Deploy

1. Click **Next** → review resources.
2. Choose a plan:
   - **Starter** ($0/month for static sites + $12/month for basic service) — good for demo.
   - **Pro** — for higher traffic.
3. Click **Create Resources**.

App Platform will build, deploy, and provide an HTTPS URL (e.g., `https://lumi-abc123.ondigitalocean.app`).

### Step 6: Custom Domain (Optional)

1. In the App dashboard, go to **Settings → Domains**.
2. Click **Add Domain**.
3. Enter your domain (e.g., `lumi.example.com`).
4. Follow the DNS instructions to add a CNAME record.
5. DigitalOcean will automatically provision an SSL certificate.

### Step 7: Enable Managed Redis (Optional)

If you want caching:
1. In DigitalOcean, go to **Databases → Create Database Cluster**.
2. Choose **Redis** → **7**.
3. Create the cluster in the same region.
4. Copy the connection string.
5. Add it as `UPSTASH_REDIS_URL` in App Platform environment variables.

---

## Post-Deployment Checklist

Verify everything works after deployment:

- [ ] Homepage loads at `https://your-domain.com`
- [ ] API health check returns `{"status":"ok"}` at `https://your-domain.com/`
- [ ] EnergyHub dashboard loads without console errors
- [ ] Ecosim simulation runs for a municipality (e.g., "MALAY")
- [ ] AI assistant responds to a test query
- [ ] Map choropleth renders province colors
- [ ] User can register and log in
- [ ] Forecast chart displays historical + projected data
- [ ] API endpoints respond under 2 seconds

### First-Request Delay Note

If the RAG FAISS index has not been pre-built inside the container, the **first AI assistant query may take 30–60 seconds** while the backend downloads the embedding model and builds the index. Subsequent requests will be fast.

The provided `Dockerfile` and `docker-compose.yml` persist the `local_data/` folder, so after the first build, the index survives restarts.

---

## Troubleshooting

### Backend container exits immediately

```bash
docker compose logs backend
```

Common causes:
- `.env` file missing or malformed.
- `SUPABASE_URL` is unreachable (check internet connectivity).
- Missing `DOE_Data_Extracted/` or `philippine_geojson/` directories.

### CORS errors in browser

The `CORS_ORIGINS` env var must exactly match your frontend URL, including `https://` and no trailing slash.

Example:
```
CORS_ORIGINS=["https://lumi.example.com"]
```

### Frontend shows blank page

1. Check browser DevTools Console for errors.
2. Verify `VITE_API_BASE_URL` was set before running `npm run build`.
3. Check that `dist/index.html` exists after build.

### AI assistant hangs or times out

1. Check that `GEMINI_API_KEY` and `GROQ_API_KEY` are valid.
2. Check backend logs for RAG index build errors.
3. The first request builds the FAISS index — wait 60 seconds.

### "Module not found" errors

The backend `Dockerfile` uses the repo root as build context and copies the entire repo. Ensure data folders (`DOE_Data_Extracted`, `philippine_geojson`, `GeothermalDatasets`) are present and not excluded by `.dockerignore`.

### Droplet runs out of RAM during build

For the `s-2vcpu-4gb` Droplet, building the backend image with `sentence-transformers` and `faiss-cpu` can use ~2 GB RAM. If the build fails:

```bash
# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Architecture Overview

```
┌─────────────────┐
│     User        │
│   (Browser)     │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────────────┐
│   Nginx (port 80/443)  │
│  - Serves React SPA      │
│  - Proxies /api/*        │
└────────┬────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐  ┌──────────────┐
│React  │  │ FastAPI      │
│(dist) │  │ (port 8080)  │
└───────┘  └──────┬───────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
    ┌─────────┐      ┌──────────┐
    │Supabase │      │ Redis    │
    │(PG+Auth)│      │(Cache)   │
    └─────────┘      └──────────┘
         │
         ▼
    ┌──────────┐
    │ NASA     │
    │ POWER    │
    │ (Public) │
    └──────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│Gemini  │ │ Groq   │
│(Google)│ │(LLM)   │
└────────┘ └────────┘
```

### Data Flow

1. **Frontend** (React + Vite) builds to static files served by Nginx.
2. **Nginx** routes `/api/*` to the FastAPI backend; all other paths serve the React SPA.
3. **Backend** (FastAPI) handles:
   - Auth via Supabase JWT
   - Energy calculations (solar, wind, hydro, geothermal)
   - ARIMA forecast serving
   - RAG-based AI assistant (Gemini + FAISS)
   - Database queries via Supabase
4. **Redis** caches suitability scores and API responses (optional).
5. **External APIs**: NASA POWER (climate data), Google Gemini, Groq.

---

## Maintenance Commands

### View logs

```bash
docker compose logs -f backend
docker compose logs -f nginx
```

### Restart a service

```bash
docker compose restart backend
```

### Update and redeploy

```bash
git pull origin main
docker compose down
docker compose up -d --build
```

### Backup RAG index

```bash
docker cp lumi-backend:/app/fastapi-backend/app/services/local_data ./rag-backup
```

### Free disk space

```bash
docker system prune -a -f
docker volume prune -f
```

---

## Cost Estimates (DigitalOcean)

| Component | Droplet Approach | App Platform |
|-----------|-----------------|--------------|
| Droplet (4GB/2CPU) | ~$24/month | — |
| App Platform Service | — | ~$12/month (Basic) |
| Static Site | — | Free |
| Managed Redis | ~$15/month (optional) | ~$15/month (optional) |
| Domain | ~$12/year | ~$12/year |
| **Total** | **~$24–39/month** | **~$12–27/month** |

*DigitalOcean offers $200 free credit for new accounts. Student accounts via GitHub Education get additional perks.*

---

*Last updated: June 2026*
