# LUMI DigitalOcean Deployment Guide

Deploy LUMI's FastAPI backend and Vite React frontend to a single DigitalOcean Droplet using Docker Compose and Nginx.

---

## Prerequisites

- A DigitalOcean account
- Your local machine with Git and a terminal
- `.env` file populated with real secrets (copy from `deploy/env-template.txt`)

---

## Step 1: Create the Droplet

1. Go to [DigitalOcean Droplets](https://cloud.digitalocean.com/droplets).
2. Choose **Ubuntu 24.04 (LTS)**.
3. Select the **Basic** plan, then the **$24/mo** tier (4 GiB / 2 vCPUs).
4. Choose a datacenter region close to your users (e.g., Singapore for Asia).
5. Add your SSH key for passwordless login.
6. Give it a hostname like `lumi-prod`.
7. Click **Create Droplet**.

Wait ~1 minute, then note the **public IPv4 address**.

---

## Step 2: Prepare Your Repo Locally

On your local machine:

```bash
cd ~/Documents/GitHub/Lumi   # or wherever your repo lives

# Ensure .env is filled out
cp deploy/env-template.txt .env
# Edit .env with your real Supabase, Upstash, Groq keys, etc.

# Build the frontend (must exist before deployment)
cd react-frontend
npm install
npm run build
cd ..

# Commit and push everything
git add -A
git commit -m "chore: add DigitalOcean deployment infrastructure"
git push origin main
```

---

## Step 3: Run the Deploy Script on the Droplet

SSH into your Droplet and run the one-liner:

```bash
ssh root@<DROPLET_IP>

# Download and run the deploy script
curl -fsSL https://raw.githubusercontent.com/Alexander040105/Lumi/main/deploy/deploy-droplet.sh | bash
```

The script will:
- Install Docker & Docker Compose
- Clone/pull the repo
- Build the React frontend
- Build the backend Docker image
- Start both containers

After it finishes, visit:
- `http://<DROPLET_IP>` — your React app
- `http://<DROPLET_IP>/health/` — health check
- `http://<DROPLET_IP>/api/v1/docs` — FastAPI auto-docs

---

## Step 4: Re-deploying After Code Changes

Whenever you push code changes:

```bash
ssh root@<DROPLET_IP>
cd ~/Lumi
git pull origin main

# Rebuild frontend if UI changed
cd react-frontend && npm install && npm run build && cd ..

# Rebuild and restart containers
docker compose build --no-cache
docker compose up -d
```

---

## Step 5: Get a Domain (Required for SSL)

Until you have a domain, the app runs on **HTTP only** (port 80).

### Buy a domain
- **Namecheap**, **Cloudflare Registrar**, **Porkbun**, etc.
- A `.com` is ~$10–15/year. A `.xyz` or `.online` can be ~$1–3/year.

### Point it to your Droplet
1. In your domain registrar's DNS panel, create an **A record**:
   - Host: `@` (or `www`, or `lumi` for a subdomain)
   - Value: your Droplet's public IPv4 address
   - TTL: 3600 (or Auto)
2. Wait 5–60 minutes for DNS propagation.

### Update CORS
Edit your `.env` on the Droplet:

```bash
ssh root@<DROPLET_IP>
cd ~/Lumi
nano .env
```

Change:
```
CORS_ORIGINS=["https://yourdomain.com"]
```

Then restart:
```bash
docker compose up -d
```

---

## Step 6: Enable HTTPS with Let's Encrypt (Certbot)

Once your domain resolves to the Droplet:

```bash
ssh root@<DROPLET_IP>

# Install Certbot
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate (nginx must NOT be listening on 443 yet)
# First, stop the docker nginx container temporarily:
docker compose stop nginx

# Run Certbot standalone on port 80
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# The certs will be at:
#   /etc/letsencrypt/live/yourdomain.com/fullchain.pem
#   /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### Mount certs into the Nginx container

Edit `docker-compose.yml` to uncomment the SSL port and add cert volumes:

```yaml
  nginx:
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deploy/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./react-frontend/dist:/usr/share/nginx/html:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro   # <-- add this
      - /var/lib/certbot:/var/lib/certbot:ro   # <-- add this
```

Edit `deploy/nginx/nginx.conf` — duplicate the server block for port 443 with SSL certificates and add an HTTP -> HTTPS redirect. Example:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # ... rest of locations from the existing server block
}
```

Restart:
```bash
docker compose up -d
```

### Auto-renewal

Certbot certificates expire every 90 days. Set up a cron job:

```bash
sudo crontab -e
# Add this line:
0 3 * * * certbot renew --quiet && docker compose -f /root/Lumi/docker-compose.yml restart nginx
```

---

## Step 7: Verify & Monitor

Check containers are healthy:
```bash
docker ps
docker compose logs -f backend
docker compose logs -f nginx
```

Test endpoints:
```bash
curl http://<DROPLET_IP>/health/
curl http://<DROPLET_IP>/api/v1/health/
```

Check backend RAM usage:
```bash
docker stats lumi-backend --no-stream
```

---

## Troubleshooting

### Backend fails to start / OOM
- Check `docker stats` — if RAM is near 4 GB, the model is too large or you have a memory leak.
- Verify swap is enabled: `free -h`. If not:
  ```bash
  sudo fallocate -l 2G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  ```

### `CORS_ORIGINS` misconfigured
- If the frontend shows CORS errors in the browser console, check that your production domain is in the `.env` `CORS_ORIGINS` array.

### Nginx returns 502 Bad Gateway
- Backend container crashed. Check `docker compose logs backend`.
- Ensure the backend healthcheck passes before nginx starts (`depends_on` with `condition: service_healthy`).

### Frontend shows blank page / 404 on refresh
- Make sure `react-frontend/dist/` exists and contains `index.html`.
- Verify `deploy/nginx/nginx.conf` has `try_files $uri $uri/ /index.html`.

---

## Architecture Recap

```
Internet
    |
    v
[Nginx :80/:443]  ← serves React SPA (dist/) + proxies /api/* →
    |                                    |
    +-- SPA routes (try_files fallback)  |
    |                                    v
    +-- /api/v1/* ----------------> [FastAPI :8080]
                                        |
                                        +--> Supabase (DB + Auth)
                                        +--> Upstash Redis (cache)
                                        +--> Groq API (LLM)
```

All heavy ML/GIS packages (`torch`, `faiss-cpu`, `rasterio`, `sentence-transformers`) run inside the backend container. No local database services consume Droplet RAM.

---

## File Reference

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Defines `backend` and `nginx` services |
| `deploy/backend/Dockerfile` | Multi-stage Python image |
| `deploy/nginx/nginx.conf` | Nginx reverse proxy + SPA config |
| `deploy/env-template.txt` | All required env vars |
| `deploy/deploy-droplet.sh` | Automated first-time Droplet setup |
| `DEPLOYMENT_GUIDE.md` | This document |
