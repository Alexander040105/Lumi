# LUMI Azure Deployment Guide

This guide covers deploying the LUMI FastAPI backend to **Microsoft Azure** using **Azure Container Apps** and an **Azure Container Registry**. The frontend remains on Vercel (see [`VERCEL_DEPLOYMENT_GUIDE.md`](./VERCEL_DEPLOYMENT_GUIDE.md) for that part).

After the Supabase data-offload refactor, the backend container no longer bundles large CSV/GeoJSON files. Instead, it loads reference data from Supabase and caches it in Upstash Redis, so the image stays small and the bundle is well under Azure Container Apps limits.

---

## Prerequisites

- An active **Azure subscription**
- **Azure CLI** installed and authenticated (`az login`)
- **Docker** installed (or use `az acr build` which does not require a local Docker daemon)
- A **Supabase** project with `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`
- An **Upstash Redis** URL for caching
- (Optional) A **Vercel** account for the React frontend

---

## 1. Prepare the environment

1. Copy the env template and fill in your real credentials:

   ```powershell
   Copy-Item deploy\env-template.txt .env
   ```

2. Required values for the Azure backend container:

   | Variable | Purpose |
   |----------|---------|
   | `SUPABASE_URL` | Supabase project URL |
   | `SUPABASE_ANON_KEY` | For frontend/auth validation |
   | `SUPABASE_SERVICE_ROLE_KEY` | For backend DB writes and migration scripts |
   | `SUPABASE_JWT_SECRET` | JWT validation if the backend issues/validates tokens |
   | `UPSTASH_REDIS_URL` | `rediss://default:pwd@host.upstash.io:6379` |
   | `GROQ_API_KEY` | LLM provider for RAG/natural-language queries |
   | `GEMINI_API_KEY` | Alternate LLM provider |
   | `CORS_ORIGINS` | JSON array, e.g. `["https://lumi.vercel.app"]` |
   | `APP_NAME` | `Lumi API` |
   | `API_V1_PREFIX` | `/api/v1` |
   | `USE_LOCAL_DATA_FALLBACK` | `false` on Azure (data comes from Supabase) |
   | `RAG_BACKEND` | `pgvector` when using Supabase pgvector |

   > **Important:** Set `USE_LOCAL_DATA_FALLBACK=false` so the backend does not try to read local CSV/GeoJSON files that are not included in the container image.

---

## 2. Run the data migrations

Before deploying the backend, the Supabase project must contain all the offloaded data. Run the SQL migration first, then the two Python upload/precompute scripts.

### 2.1 Run the SQL migration

Open `supabase/migrations/0008_data_offload.sql` in the Supabase SQL Editor and execute it. This creates:

- `public.doe_datasets`
- `public.municipality_climate_averages`
- `public.products`
- `public.wind_products` / `public.wind_products_summary`
- `public.geothermal_heatflow` / `geothermal_faults` / `geothermal_volcanoes`
- Extra aquifer columns on `public.geothermal_suitability`
- Row Level Security (RLS) policies and storage bucket `geojsons`

### 2.2 Upload CSV data to Supabase

From the repo root, with your `.env` configured:

```powershell
python scripts/migrate_csv_to_supabase.py
```

This uploads DOE CSVs, municipality climate averages, products, wind products, and geothermal points into the new Supabase tables. It is safe to run multiple times because it uses `ON CONFLICT`/`upsert`.

### 2.3 Precompute aquifer scores

This script requires `geopandas` and `shapely`:

```powershell
pip install geopandas shapely
python scripts/precompute_aquifer_scores.py
```

It reads the aquifer GeoJSON, matches each municipality by point-in-polygon, and writes the aquifer score and properties to `public.geothermal_suitability`.

---

## 3. Build the backend Docker image

The backend is containerized by `deploy/backend/Dockerfile`.

### Option A: Build with Azure Container Registry (recommended)

No local Docker daemon is required.

```powershell
$RESOURCE_GROUP   = "lumi-rg"
$ACR_NAME         = "lumiacr" + (Get-Random -Maximum 9999)  # must be globally unique
$AZURE_REGION     = "southeastasia"

# Create resource group and ACR
az group create --name $RESOURCE_GROUP --location $AZURE_REGION
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Build and push directly from the repo root
az acr build `
  --registry $ACR_NAME `
  --image lumi-backend:v1 `
  --file deploy/backend/Dockerfile `
  .`
```

### Option B: Build locally and push

```powershell
$ACR_LOGIN_SERVER = "$ACR_NAME.azurecr.io"

# Build
az acr login --name $ACR_NAME

docker build -t lumi-backend:v1 -f deploy/backend/Dockerfile .
docker tag lumi-backend:v1 "$ACR_LOGIN_SERVER/lumi-backend:v1"
docker push "$ACR_LOGIN_SERVER/lumi-backend:v1"
```

### Dockerfile summary

- Uses `python:3.11-slim`
- Installs GIS runtime libs (`libgeos`, `libproj`, `libgdal`)
- Copies `fastapi-backend/` into `/app`
- Runs `uvicorn main:app --host 0.0.0.0 --port 8080 --workers 2`
- Health check: `GET /api/v1/health/`

---

## 4. Deploy to Azure Container Apps

### 4.1 Create the Container Apps environment

```powershell
$ENVIRONMENT_NAME = "lumi-env"
$APP_NAME         = "lumi-backend"
$ACR_LOGIN_SERVER = "$ACR_NAME.azurecr.io"

az containerapp env create `
  --name $ENVIRONMENT_NAME `
  --resource-group $RESOURCE_GROUP `
  --location $AZURE_REGION

# Get ACR credentials
$ACR_CREDENTIALS = az acr credential show --name $ACR_NAME --resource-group $RESOURCE_GROUP --output json | ConvertFrom-Json
$ACR_USERNAME = $ACR_CREDENTIALS.username
$ACR_PASSWORD = $ACR_CREDENTIALS.passwords[0].value

az containerapp create `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --environment $ENVIRONMENT_NAME `
  --image "$ACR_LOGIN_SERVER/lumi-backend:v1" `
  --cpu 1 `
  --memory 2Gi `
  --min-replicas 1 `
  --max-replicas 3 `
  --target-port 8080 `
  --ingress external `
  --registry-server $ACR_LOGIN_SERVER `
  --registry-username $ACR_USERNAME `
  --registry-password $ACR_PASSWORD `
  --env-vars `
    "SUPABASE_URL=$env:SUPABASE_URL" `
    "SUPABASE_ANON_KEY=$env:SUPABASE_ANON_KEY" `
    "SUPABASE_SERVICE_ROLE_KEY=$env:SUPABASE_SERVICE_ROLE_KEY" `
    "SUPABASE_JWT_SECRET=$env:SUPABASE_JWT_SECRET" `
    "UPSTASH_REDIS_URL=$env:UPSTASH_REDIS_URL" `
    "GROQ_API_KEY=$env:GROQ_API_KEY" `
    "GEMINI_API_KEY=$env:GEMINI_API_KEY" `
    "CORS_ORIGINS=$env:CORS_ORIGINS" `
    "APP_NAME=$env:APP_NAME" `
    "API_V1_PREFIX=$env:API_V1_PREFIX" `
    "USE_LOCAL_DATA_FALLBACK=false" `
    "RAG_BACKEND=pgvector" `
    "LOG_LEVEL=INFO"
```

> **Security:** In a production environment, pass sensitive values as Container App secrets (via the Azure Portal or `az containerapp secret set`) instead of plain `--env-vars` so they are encrypted at rest.

### 4.2 Verify the deployment

Wait 1–2 minutes, then get the app URL:

```powershell
$FQDN = az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn --output tsv

# Health check
curl "https://$FQDN/api/v1/health/"

# Root check
curl "https://$FQDN/"
```

You should see:

```json
{"status":"ok","service":"Lumi API"}
```

---

## 5. Configure secrets as encrypted values (production)

Using the Azure Portal:

1. Go to **Container Apps** → `lumi-backend` → **Secrets**.
2. Add secrets for:
   - `supabase-url`
   - `supabase-anon-key`
   - `supabase-service-role-key`
   - `supabase-jwt-secret`
   - `upstash-redis-url`
   - `groq-api-key`
   - `gemini-api-key`
3. Go to **Environment variables** and reference each secret by name (`secretRef`).
4. Restart the container app.

---

## 6. Deploy the frontend to Vercel

The React frontend continues to be hosted on Vercel.

1. In Vercel, set the environment variable:

   ```
   VITE_API_BASE_URL=https://<your-container-app-fqdn>/api/v1
   ```

2. Ensure `CORS_ORIGINS` in the backend includes your Vercel domain.
3. Deploy from `react-frontend/`.

See [`VERCEL_DEPLOYMENT_GUIDE.md`](./VERCEL_DEPLOYMENT_GUIDE.md) for the full Vercel steps.

---

## 7. Monitoring and scaling

- **Logs:** In the Azure Portal, go to `lumi-backend` → **Monitoring** → **Log stream**.
- **Metrics:** Use **Container Apps** → **Metrics** to watch CPU, memory, and HTTP requests.
- **Application Insights:** (Optional) Create an Application Insights resource and add the connection string to the container environment variables.
- **Scaling:** `min-replicas 1` keeps a warm instance. Increase `max-replicas` and add HTTP or CPU scaling rules based on load.

---

## 8. Updating the deployment

After code changes:

```powershell
# Rebuild and push a new image tag
az acr build `
  --registry $ACR_NAME `
  --image lumi-backend:v2 `
  --file deploy/backend/Dockerfile `
  .

# Update the Container App
az containerapp update `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --image "$ACR_LOGIN_SERVER/lumi-backend:v2"
```

The app performs a rolling update with zero downtime.

---

## 9. CI/CD with GitHub Actions (optional)

A minimal workflow snippet:

```yaml
name: Build and Deploy to Azure

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Azure login
        uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Build and push to ACR
        run: |
          az acr build \
            --registry ${{ secrets.AZURE_ACR_NAME }} \
            --image lumi-backend:${{ github.sha }} \
            --file deploy/backend/Dockerfile \
            .

      - name: Deploy to Container Apps
        run: |
          az containerapp update \
            --name lumi-backend \
            --resource-group lumi-rg \
            --image "${{ secrets.AZURE_ACR_NAME }}.azurecr.io/lumi-backend:${{ github.sha }}"
```

Store `AZURE_CREDENTIALS` and `AZURE_ACR_NAME` as GitHub repository secrets.

---

## 10. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Container fails with `ModuleNotFoundError` | Missing Python package in `fastapi-backend/requirements.txt` | Add the package and rebuild the image. |
| `Connection refused` to Supabase | `SUPABASE_URL` or `SUPABASE_SERVICE_ROLE_KEY` wrong | Check `.env` and Container App secrets. |
| Requests timeout on first call | RAG/FAISS index building at startup | Set `RAG_BACKEND=pgvector` so no local FAISS build is needed, or increase `initial_delay_seconds` for the health check. |
| `/api/v1/health/` returns 404 | `API_V1_PREFIX` not set or health route missing | Ensure `API_V1_PREFIX=/api/v1`. |
| Large startup times or memory issues | Data loaded from local files | Set `USE_LOCAL_DATA_FALLBACK=false` and verify `fastapi-backend/app/services/local_data/` is excluded from the image. |
| `precompute_aquifer_scores.py` fails | `geopandas` or `shapely` not installed | `pip install geopandas shapely` and re-run the script. |

---

## Quick reference commands

```powershell
# Log stream
az containerapp logs show --name lumi-backend --resource-group lumi-rg --follow

# Restart
az containerapp revision restart --name lumi-backend --resource-group lumi-rg

# List revisions
az containerapp revision list --name lumi-backend --resource-group lumi-rg

# Delete everything when done testing
az group delete --name lumi-rg --yes --no-wait
```
