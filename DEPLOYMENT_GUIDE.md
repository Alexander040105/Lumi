# LUMI Deployment Guide

This guide covers deploying LUMI to DigitalOcean using two approaches:
1. **Droplet + Docker Compose** (recommended — full control, lower cost)
2. **App Platform** (simpler, auto-scaling, slightly higher cost)

---

## Architecture Overview

```
                    ┌─────────────┐
                    │   Nginx :80 │
                    │  (reverse   │
                    │   proxy)    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │                         │
      /api/* ──────────► Backend :8080
      /*      ──────────► React SPA (static files)

  Backend ──► Supabase (Postgres + Auth)  [external]
          ──► Upstash Redis              [external or local]
          ──► Groq / Gemini APIs         [external]
```

---

## Prerequisites

### 1. External Services (already provisioned)
- **Supabase** project URL + keys (anon, service_role, JWT secret)
- **Upstash Redis** URL (or use a local Redis container)
- **Groq API key** (for chat)
- **Gemini API key** (optional, for AI analysis)

### 2. DigitalOcean Resources
- A **Droplet** (recommended: 2 vCPU / 4 GB RAM / 80 GB SSD — $24/mo)
  - Or an **App Platform** instance
- A **domain name** (optional but recommended)
- **SSH key** for Droplet access

### 3. Local Tools
- Docker Desktop (for building images locally)
- `doctl` CLI (optional, for DO Container Registry)
- `scp` / `rsync` (for file transfer)

---

## Approach A: Droplet + Docker Compose (Recommended)

### Step 1: Create a Droplet

1. Go to **DigitalOcean → Create → Droplets**
2. Choose:
   - **Image**: Ubuntu 22.04 (LTS) x64
   - **Size**: Basic → Regular → 2 vCPU / 4 GB / 80 GB SSD
   - **Datacenter**: Singapore (closest to Philippines)
   - **SSH Key**: Add your public key
3. Click **Create Droplet**
4. Note the Droplet IP address

### Step 2: Install Docker on the Droplet

SSH into your Droplet and install Docker:

```bash
ssh root@YOUR_DROPLET_IP

# Install Docker
apt-get update
apt-get install -y ca-certificates curl gnupg lsb-release
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify
docker --version
docker compose version
```

### Step 3: Prepare the Project on the Droplet

```bash
mkdir -p /opt/lumi
cd /opt/lumi

# Option 1: Clone from GitHub
git clone https://github.com/Alexander040105/Lumi.git .

# Option 2: Upload from local (if not using GitHub)
# On your local machine:
#   scp -r . root@YOUR_DROPLET_IP:/opt/lumi/
```

### Step 4: Create the .env File

```bash
cd /opt/lumi
cp deploy/env-template.txt .env
nano .env
```

Fill in all values:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...
SUPABASE_JWT_SECRET=your-jwt-secret

# Redis (Upstash or local container)
UPSTASH_REDIS_URL=rediss://default:password@your-upstash-host.upstash.io:6379
# Or for local Redis: redis://redis:6379

# LLM API Keys
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIza...

# CORS — set to your domain or IP
CORS_ORIGINS=["http://YOUR_DROPLET_IP","https://your-domain.com"]

# Application
APP_NAME=Lumi API
API_V1_PREFIX=/api/v1
```

### Step 5: Run Database Migrations

Run the SQL migrations against your Supabase database:

1. Go to **Supabase Dashboard → SQL Editor**
2. Run the migrations in order:
   - `supabase/migrations/0002_psgc_data_columns.sql`
   - `supabase/migrations/0003_schema_hardening.sql`
3. Verify tables were created:
   ```sql
   SELECT table_name FROM information_schema.tables
   WHERE table_schema = 'public' ORDER BY table_name;
   ```

### Step 6: Build and Start the Stack

```bash
cd /opt/lumi

# Build and start (production mode with nginx proxy)
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod up -d --build

# Check status
docker compose ps

# View backend logs
docker compose logs -f backend

# View nginx logs
docker compose logs -f nginx
```

### Step 7: Verify the Deployment

```bash
# Health check
curl http://localhost/api/v1/health/
# Expected: {"status":"ok"}

# Detailed health check
curl http://localhost/api/v1/health/detailed
# Expected: {"status":"ok","uptime_seconds":...,"checks":{"supabase":"ok","redis":"ok",...}}

# Frontend
curl -I http://localhost/
# Expected: HTTP/1.1 200 OK
```

### Step 8: Set Up SSL with Let's Encrypt (Optional but Recommended)

```bash
# Install certbot
apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate (replace your-domain.com)
certbot --nginx -d your-domain.com -d www.your-domain.com

# Certbot will automatically configure nginx and set up auto-renewal
```

### Step 9: Configure Firewall

```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

---

## Approach B: DigitalOcean App Platform

### Step 1: Create App Spec

The file `deploy/app.yaml` contains the App Platform spec. Edit it with your values:

```yaml
# deploy/app.yaml
envs:
  - key: SUPABASE_URL
    scope: RUN_TIME
    value: https://your-project.supabase.co
  # ... (all env vars from .env)
```

### Step 2: Deploy via DO Console

1. Go to **DigitalOcean → Apps → Create App**
2. Choose **Deploy from Docker Compose**
3. Connect your GitHub repo: `Alexander040105/Lumi`
4. Select the `docker-compose.yml` file
5. Set environment variables (from `.env`)
6. Click **Deploy**

### Step 3: Configure Custom Domain

1. In the App settings → Domains
2. Add your domain
3. Update DNS records as instructed by DO

---

## Approach C: Simple Droplet (No Docker)

If you prefer running the backend directly without Docker:

### Step 1: Install Dependencies

```bash
apt-get update
apt-get install -y python3.11 python3.11-venv python3-pip nginx nodejs npm

# For GIS packages
apt-get install -y libgeos-dev libproj-dev libgdal-dev
```

### Step 2: Set Up Backend

```bash
cd /opt/lumi/fastapi-backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Set Up Frontend

```bash
cd /opt/lumi/react-frontend
npm ci
npm run build
cp -r dist/* /var/www/html/
```

### Step 4: Configure Nginx

```bash
cp deploy/nginx/nginx.conf /etc/nginx/conf.d/lumi.conf
nginx -t
systemctl reload nginx
```

### Step 5: Run Backend with Systemd

Create `/etc/systemd/system/lumi-backend.service`:

```ini
[Unit]
Description=LUMI FastAPI Backend
After=network.target

[Service]
User=root
WorkingDirectory=/opt/lumi/fastapi-backend
EnvironmentFile=/opt/lumi/.env
ExecStart=/opt/lumi/fastapi-backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable lumi-backend
systemctl start lumi-backend
```

---

## Post-Deployment

### 1. Run Data Sync Scripts (Optional)

If you need to refresh PSGC data or climate data:

```bash
cd /opt/lumi
source fastapi-backend/.venv/bin/activate  # if not using Docker

# PSGC data sync
python scripts/sync_psgc_data.py

# NASA POWER climate gap filling
python scripts/run_nasa_for_gaps.py

# Rebuild municipality suitability scores
cd fastapi-backend
python -m app.services.municipality_suitability_builder
```

### 2. Refresh Materialized Views

Run in Supabase SQL Editor:

```sql
SELECT public.refresh_map_views();
```

### 3. Set Up GitHub Actions CI/CD (Optional)

1. Go to your GitHub repo → Settings → Secrets and Variables → Actions
2. Add the following secrets:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `DO_DROPLET_IP` — your Droplet IP
   - `DO_SSH_USER` — `root`
   - `DO_SSH_PRIVATE_KEY` — your SSH private key
3. Push to `main` branch to trigger deployment

### 4. Monitoring

```bash
# View backend logs
docker compose logs -f backend

# View nginx access logs
docker compose exec nginx cat /var/log/nginx/access.log

# Check resource usage
docker stats

# Disk space
df -h
```

---

## Troubleshooting

### Backend won't start
```bash
docker compose logs backend
# Common issues:
# - Missing .env file
# - Wrong SUPABASE_URL
# - Redis connection refused (check UPSTASH_REDIS_URL)
```

### Frontend shows blank page
```bash
# Check if frontend built successfully
docker compose logs frontend
# Check nginx config
docker compose exec nginx nginx -t
```

### API returns 502 Bad Gateway
```bash
# Backend is not running or crashed
docker compose ps
docker compose restart backend
```

### Supabase connection errors
```bash
# Verify credentials
docker compose exec backend python -c "
from app.services.supabase_service import get_supabase_client
c = get_supabase_client()
r = c.table('regions').select('*').limit(1).execute()
print(r.data)
"
```

### Redis connection errors
```bash
# If using Upstash, verify URL format:
# rediss://default:PASSWORD@HOST.upstash.io:6379
# Note the double 's' in 'rediss' for TLS
```

---

## Cost Estimate (Monthly)

| Component | Cost |
|-----------|------|
| DO Droplet (2 vCPU / 4 GB) | $24 |
| Supabase (Free tier) | $0 |
| Upstash Redis (Free tier) | $0 |
| Groq (Free tier) | $0 |
| Domain (optional) | ~$10/yr |
| **Total** | **~$24/mo** |

For higher traffic:
- Upgrade Droplet to 4 vCPU / 8 GB ($48/mo)
- Supabase Pro ($25/mo)
- Upstash Pay-as-you-go

---

## File Reference

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Local dev + base services |
| `docker-compose.prod.yml` | Production overlay (replicas, resources) |
| `deploy/backend/Dockerfile` | Backend image (Python 3.11 + GIS libs) |
| `deploy/frontend/Dockerfile` | Frontend image (Node 20 → nginx) |
| `deploy/nginx/nginx.conf` | Reverse proxy config |
| `deploy/nginx/frontend.conf` | Frontend-only nginx config |
| `deploy/nginx/Dockerfile` | Nginx proxy container |
| `deploy/env-template.txt` | All required env vars |
| `.github/workflows/ci.yml` | CI: tests + Docker build check |
| `.github/workflows/deploy.yml` | CD: build, push, SSH deploy |
| `supabase/migrations/0003_schema_hardening.sql` | DB migration |
