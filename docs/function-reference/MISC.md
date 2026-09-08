# Miscellaneous (supporting code and files)
## `.dockerignore`

**File:** `.dockerignore`

**Summary:** Docker/deployment configuration that packages or orchestrates the LUMI services.


## `.env.example`

**File:** `.env.example`

**Summary:** Reference or configuration file.


## `.vercelignore`

**File:** `.vercelignore`

**Summary:** Reference or configuration file.


## `api/index.py`

**File:** `api/index.py`

**Summary:** Source file `api/index.py`.

### `_PathFix.__init__`

- **File:** `api/index.py`
- **Lines:** `36-37`
- **Signature:** `def __init__(self, app):`
- **Purpose:** Method of `_PathFix` that handles   init  .

**Code:**
```python
def __init__(self, app):
        self.app = app
```

**Explanation:** It accepts `app`. See the code below for the full implementation.

### `_PathFix.__call__`

- **File:** `api/index.py`
- **Lines:** `39-61`
- **Signature:** `async def __call__(self, scope, receive, send):`
- **Purpose:** Method of `_PathFix` that handles   call  .

**Code:**
```python
async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            path = scope.get("path", "/")
            raw_path = scope.get("raw_path", b"/")

            for prefix in ("/api/index.py", "/api/index"):
                if path.startswith(prefix):
                    rest = path[len(prefix):]
                    if not rest.startswith("/"):
                        rest = "/" + rest
                    scope["path"] = rest or "/"

                    raw_prefix = prefix.encode()
                    raw_rest = raw_path[len(raw_prefix):]
                    if not raw_rest.startswith(b"/"):
                        raw_rest = b"/" + raw_rest
                    scope["raw_path"] = raw_rest or b"/"
                    break

            # The app is served from the public root; do not use a subpath mount.
            scope["root_path"] = ""

        await self.app(scope, receive, send)
```

**Explanation:** It accepts `scope`, `receive`, `send`. See the code below for the full implementation. Key calls include `get()`, `startswith()`, `encode()`, `len()`, `app()`.


## `deploy/app.yaml`

**File:** `deploy/app.yaml`

**Summary:** YAML configuration for deployment or service orchestration.

**First lines:**
```yaml
# DigitalOcean App Platform spec for LUMI
# Usage: doctl apps create deploy/app.yaml
# Or via DO Console: Apps → Create App → Deploy from source

spec:
  name: lumi
  services:
    - name: backend
      dockerfile_path: deploy/backend/Dockerfile
      source_dir: /
      http_port: 8080
      instance_count: 2
      instance_size_slug: basic-2vcpu-4gb
      health_check:
        http_path: /api/v1/health/
        initial_delay_seconds: 60
        period_seconds: 30
        timeout_seconds: 10
        success_threshold: 1
        failure_threshold: 3
      envs:
        - key: SUPABASE_URL
          scope: RUN_TIME
          type: SECRET
        - key: SUPABASE_ANON_KEY
          scope: RUN_TIME
          type: SECRET
        - key: SUPABASE_SERVICE_ROLE_KEY
          scope: RUN_TIME
          type: SECRET
```


## `deploy/backend/Dockerfile`

**File:** `deploy/backend/Dockerfile`

**Summary:** Docker/deployment configuration that packages or orchestrates the LUMI services.


## `deploy/deploy-droplet.sh`

**File:** `deploy/deploy-droplet.sh`

**Summary:** Shell script used for deployment or automation.

**First lines:**
```sh
#!/usr/bin/env bash
set -euo pipefail

# LUMI Automated Deployment Script for DigitalOcean Droplet
# Usage: ./deploy/deploy-droplet.sh
# Prerequisites: .env file in project root, Docker installed on target

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================"
echo "  LUMI Deployment Script"
echo "============================================"

# Check .env exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "ERROR: .env file not found at $PROJECT_DIR/.env"
    echo "Copy deploy/env-template.txt to .env and fill in values."
    exit 1
fi

# Check Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Install Docker first."
    exit 1
fi

echo ""
echo "[1/5] Building images..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod build
```


## `deploy/env-template.txt`

**File:** `deploy/env-template.txt`

**Summary:** Text template or notes file.

**First lines:**
```txt
# =============================================================================
# LUMI Environment Variables
# =============================================================================
# Copy this file to .env and fill in the values.
# DO NOT commit .env to version control.

# ---------------------------------------------------------------------------
# Supabase
# ---------------------------------------------------------------------------
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# ---------------------------------------------------------------------------
# Redis (Upstash)
# ---------------------------------------------------------------------------
UPSTASH_REDIS_URL=redis://localhost:6379
# or: rediss://default:password@your-upstash-host.upstash.io:6379

# ---------------------------------------------------------------------------
# LLM API Keys
# ---------------------------------------------------------------------------
GROQ_API_KEY=your-groq-api-key
GEMINI_API_KEY=your-gemini-api-key

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```


## `deploy/nginx/nginx.conf`

**File:** `deploy/nginx/nginx.conf`

**Summary:** Configuration file for nginx or another service.

**First lines:**
```nginx
upstream backend {
    server backend:8080;
}

server {
    listen 80;
    server_name _;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml image/svg+xml;
    gzip_min_length 256;

    # API proxy
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }

    # Health check proxy
    location /health {
        proxy_pass http://backend/api/v1/health/;
        proxy_set_header Host $host;
    }

```


## `docker-compose.prod.yml`

**File:** `docker-compose.prod.yml`

**Summary:** Docker/deployment configuration that packages or orchestrates the LUMI services.

**First lines:**
```yml
# LUMI — Production docker-compose overlay
# Usage:
#   export LUMI_REGISTRY=registry.digitalocean.com/<your-registry>
#   export LUMI_IMAGE_TAG=latest
#   docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod pull
#   docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod up -d

services:
  backend:
    image: ${LUMI_REGISTRY:-lumi}/lumi-backend:${LUMI_IMAGE_TAG:-latest}
    build: !reset null
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 2G
    environment:
      - WORKERS=4
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]

  frontend:
    image: ${LUMI_REGISTRY:-lumi}/lumi-frontend:${LUMI_IMAGE_TAG:-latest}
    build: !reset null
    deploy:
      replicas: 1

  nginx:
    profiles:
      - prod
    deploy:
```


## `docker-compose.yml`

**File:** `docker-compose.yml`

**Summary:** Docker/deployment configuration that packages or orchestrates the LUMI services.

**First lines:**
```yml
# LUMI — docker-compose for local development parity
# Usage: docker compose up -d
# Backend runs on :8080, Frontend on :5173 (dev) or nginx :80 (prod)

services:
  backend:
    build:
      context: .
      dockerfile: deploy/backend/Dockerfile
    ports:
      - "8080:8080"
    env_file:
      - .env
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import httpx; r=httpx.get('http://localhost:8080/api/v1/health/'); r.raise_for_status()"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  frontend:
    build:
      context: .
      dockerfile: deploy/frontend/Dockerfile
    ports:
      - "3000:80"
    depends_on:
```


## `scripts/generate_erd.py`

**File:** `scripts/generate_erd.py`

**Summary:** Generate a PNG ERD diagram for the LUMI database schema using matplotlib.

### `draw_table`

- **File:** `scripts/generate_erd.py`
- **Lines:** `23-48`
- **Signature:** `def draw_table(ax, x, y, title, columns, color, width=2.4, col_height=0.18, title_height=0.35):`
- **Purpose:** Draw a table box with title and columns.

**Code:**
```python
def draw_table(ax, x, y, title, columns, color, width=2.4, col_height=0.18, title_height=0.35):
    """Draw a table box with title and columns."""
    n_cols = len(columns)
    height = title_height + n_cols * col_height + 0.08

    # Main box
    rect = FancyBboxPatch((x - width/2, y - height), width, height,
                          boxstyle="round,pad=0.02", 
                          facecolor='white', edgecolor=color, linewidth=2)
    ax.add_patch(rect)

    # Title bar
    title_rect = FancyBboxPatch((x - width/2, y - title_height), width, title_height,
                                boxstyle="round,pad=0.02", 
                                facecolor=color, edgecolor=color, linewidth=2)
    ax.add_patch(title_rect)
    ax.text(x, y - title_height/2, title, ha='center', va='center',
            fontsize=8.5, fontweight='bold', color='white')

    # Columns
    for i, col in enumerate(columns):
        cy = y - title_height - (i + 0.5) * col_height
        ax.text(x - width/2 + 0.08, cy, col, ha='left', va='center',
                fontsize=6.5, color='#333333', family='monospace')

    return (x, y, x, y - height, width, height)
```

**Explanation:** It accepts `ax`, `x`, `y`, `title`, `columns`, `color`, `width`, `col_height`, `title_height`. See the code below for the full implementation. Key calls include `len()`, `FancyBboxPatch()`, `add_patch()`, `text()`, `enumerate()`.

### `draw_relationship`

- **File:** `scripts/generate_erd.py`
- **Lines:** `50-53`
- **Signature:** `def draw_relationship(ax, x1, y1, x2, y2, style='--'):`
- **Purpose:** Draw a relationship line with crow's foot notation.

**Code:**
```python
def draw_relationship(ax, x1, y1, x2, y2, style='--'):
    """Draw a relationship line with crow's foot notation."""
    # Simple line
    ax.plot([x1, x2], [y1, y2], color='#666666', linewidth=1.0, linestyle=style, zorder=1)
```

**Explanation:** It accepts `ax`, `x1`, `y1`, `x2`, `y2`, `style`. See the code below for the full implementation. Key calls include `plot()`.

### `main`

- **File:** `scripts/generate_erd.py`
- **Lines:** `55-355`
- **Signature:** `def main():`
- **Purpose:** Handles main.

**Code:**
```python
def main():
    fig, ax = plt.subplots(1, 1, figsize=(32, 24), dpi=150)
    ax.set_xlim(0, 32)
    ax.set_ylim(0, 24)
    ax.axis('off')
    ax.set_facecolor('#F8F9FA')
    fig.patch.set_facecolor('#F8F9FA')

    # Title
    ax.text(16, 23.4, 'LUMI Database Entity-Relationship Diagram', 
            ha='center', va='center', fontsize=22, fontweight='bold', color='#2C3E50')
    ax.text(16, 22.9, 'PostgreSQL Schema v4  —  21 Tables + 1 Auth View', 
            ha='center', va='center', fontsize=12, color='#7F8C8D')

    # Legend
    legend_items = [
        ('Geographic Hierarchy', COLORS['geo']),
        ('Renewable Energy', COLORS['renewable']),
        ('Statistics & ML', COLORS['stats']),
        ('User Management', COLORS['user']),
        ('Auth / Cache', COLORS['auth']),
    ]
    for i, (label, color) in enumerate(legend_items):
        lx = 2 + i * 4.5
        ly = 22.3
        rect = mpatches.Rectangle((lx, ly - 0.12), 0.4, 0.24, facecolor=color, edgecolor='none')
        ax.add_patch(rect)
        ax.text(lx + 0.55, ly, label, ha='left', va='center', fontsize=9, color='#333')

    # ===== Geographic Hierarchy (left side) =====
    geo_x = 5.5

    t_regions = draw_table(ax, geo_x, 20.5, 'regions', [
        'region_id  PK',
        'name',
        'lat, lon',
    ], COLORS['geo'])

    t_provinces = draw_table(ax, geo_x, 16.8, 'provinces', [
        'province_id  PK',
        'region_id  FK',
        'name',
        'lat, lon',
    ], COLORS['geo'])

    t_municipalities = draw_table(ax, geo_x, 11.5, 'municipalities', [
        'municipality_id  PK',
        'province_id  FK',
        'name, lat, lon',
        'solar_suitability_score',
        'solar_classification',
        'wind_suitability_score',
        'wind_classification',
        'hydro_suitability_score',
        'hydro_classification',
        'geothermal_suitability_score',
        'geothermal_classification',
        'composite_suitability_score',
        'suitability_updated_at',
    ], COLORS['geo'], width=3.0)

    t_barangays = draw_table(ax, geo_x - 4.5, 7.0, 'barangays', [
        'barangay_id  PK',
        'municipality_id  FK',
        'name, lat, lon',
    ], COLORS['geo'])

    t_climate = draw_table(ax, geo_x + 4.5, 7.0, 'municipality_climate_monthly', [
        'municipality_id  FK',
        'year, month  PK',
        't2m, t2m_max, t2m_min',
        'rh2m, prectotcorr',
        'ws10m, allsky_sfc_sw_dwn',
        'cloud_amt, elevation',
        'source, created_at',
    ], COLORS['geo'], width=3.0)

    # ===== Renewable Energy (center-left) =====
    ren_x = 12.5

    t_hydro = draw_table(ax, ren_x, 20.0, 'hydropower_suitability', [
        'municipality_id  PK/FK',
        'province_id  FK',
        'mean_slope_deg',
        'hydraulic_head_m',
        'hydro_suitability_score',
        'estimated_potential_kw',
        'runoff_potential',
        'gravity_flow_potential',
        'slope_classification',
    ], COLORS['renewable'], width=2.8)

    t_geosuit = draw_table(ax, ren_x, 15.0, 'geothermal_suitability', [
        'municipality_id  PK/FK',
        'heat_flow_score',
        'fault_density',
        'fault_distance_km',
        'volcano_distance_km',
        'aquifer_score',
        'temperature_score',
        'geothermal_score',
        'classification',
    ], COLORS['renewable'], width=2.8)

    t_geoout = draw_table(ax, ren_x, 9.5, 'geothermal_output', [
        'municipality_id  PK/FK',
        'reservoir_temperature_c',
        'estimated_flow_rate_kg_s',
        'thermal_power_mw',
        'electric_power_mw',
        'annual_energy_gwh',
        'confidence_score',
    ], COLORS['renewable'], width=2.8)

    # ===== Stats & ML (center-right) =====
    stats_x = 19.0

    t_national = draw_table(ax, stats_x, 21.0, 'national_energy_annual', [
        'year  PK',
        'total_consumption_gwh',
        'total_peak_demand_mw',
        'luzon_generation_gwh',
        'renewable_generation_gwh',
        'total_installed_capacity_mw',
        'created_at, updated_at',
    ], COLORS['stats'], width=2.8)

    t_mlreg = draw_table(ax, stats_x, 16.5, 'ml_model_registry', [
        'model_id  PK',
        'model_name, version',
        'model_type',
        'target_variable',
        'train_date',
        'metrics (jsonb)',
        'is_active',
    ], COLORS['stats'], width=2.6)

    t_forecast = draw_table(ax, stats_x + 4.0, 16.5, 'forecast_cache', [
        'forecast_id  PK',
        'model_id  FK',
        'target_variable',
        'horizon_years',
        'forecast_year, month',
        'predicted_value',
        'lower_bound, upper_bound',
    ], COLORS['stats'], width=2.8)

    t_chart = draw_table(ax, stats_x + 4.0, 21.0, 'chart_ai_insights', [
        'id  PK',
        'chart_type',
        'chart_data_hash',
        'insight',
        'created_at',
    ], COLORS['cache'], width=2.4)

    # ===== User Management (bottom) =====
    user_y = 4.0
    user_x_start = 2.5
    user_spacing = 3.0

    t_auth = draw_table(ax, user_x_start, user_y + 1.0, 'auth.users', [
        'id  PK',
    ], COLORS['auth'], width=1.6)

    t_profiles = draw_table(ax, user_x_start + user_spacing, user_y, 'profiles', [
        'id  PK/FK',
        'full_name',
        'organization',
        'plan',
        'is_active',
        'created_at',
    ], COLORS['user'], width=2.0)

    t_roles = draw_table(ax, user_x_start + user_spacing*2, user_y, 'user_roles', [
        'user_id  PK/FK',
        'role (app_role)',
        'created_at',
    ], COLORS['user'], width=2.0)

    t_limits = draw_table(ax, user_x_start + user_spacing*3, user_y, 'user_usage_limits', [
        'user_id  PK/FK',
        'chat_messages_this_month',
        'simulations_this_month',
        'plan',
    ], COLORS['user'], width=2.2)

    t_chat_sess = draw_table(ax, user_x_start + user_spacing*4.2, user_y + 0.5, 'chat_sessions', [
        'id  PK',
        'user_id  FK',
        'title',
        'created_at',
    ], COLORS['user'], width=2.0)

    t_chat_msg = draw_table(ax, user_x_start + user_spacing*5.5, user_y + 0.5, 'chat_messages', [
        'id  PK',
        'session_id  FK',
        'role',
        'content',
        'retrieved_chunks',
    ], COLORS['user'], width=2.2)

    t_saved_loc = draw_table(ax, user_x_start + user_spacing*6.8, user_y, 'saved_locations', [
        'id  PK',
        'user_id  FK',
        'municipality_id  FK',
        'label',
        'created_at',
    ], COLORS['user'], width=2.2)

    t_saved_sim = draw_table(ax, user_x_start + user_spacing*8.1, user_y, 'saved_simulations', [
        'id  PK',
        'user_id  FK',
        'municipality_id  FK',
        'label',
        'inputs (jsonb)',
        'results (jsonb)',
    ], COLORS['user'], width=2.2)

    t_audit = draw_table(ax, user_x_start + user_spacing*9.4, user_y, 'admin_audit_log', [
        'id  PK',
        'admin_id  FK',
        'action',
        'target_user_id  FK',
        'details (jsonb)',
    ], COLORS['user'], width=2.3)

    # ===== Relationship lines =====
    # Geographic
    ax.annotate('', xy=(geo_x, t_provinces[1] + 0.2), xytext=(geo_x, t_regions[3]),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2))
    ax.annotate('', xy=(geo_x, t_municipalities[1] + 0.2), xytext=(geo_x, t_provinces[3]),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2))
    ax.annotate('', xy=(t_barangays[0] + t_barangays[4]/2, t_barangays[1] + 0.1), 
                xytext=(geo_x - t_municipalities[4]/2, t_municipalities[3] + 0.5),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2, connectionstyle="arc3,rad=0.2"))
    ax.annotate('', xy=(t_climate[0] - t_climate[4]/2, t_climate[1] + 0.1), 
                xytext=(geo_x + t_municipalities[4]/2, t_municipalities[3] + 0.5),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2, connectionstyle="arc3,rad=-0.2"))

    # Renewable -> municipalities
    ax.annotate('', xy=(ren_x - t_hydro[4]/2, t_hydro[3] + 0.2), 
                xytext=(geo_x + t_municipalities[4]/2, t_municipalities[3] + 0.2),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2, connectionstyle="arc3,rad=0.15"))
    ax.annotate('', xy=(ren_x - t_geosuit[4]/2, t_geosuit[3] + 0.2), 
                xytext=(geo_x + t_municipalities[4]/2, t_municipalities[3] + 0.2),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2, connectionstyle="arc3,rad=0.1"))
    ax.annotate('', xy=(ren_x - t_geoout[4]/2, t_geoout[3] + 0.2), 
                xytext=(geo_x + t_municipalities[4]/2, t_municipalities[3] + 0.2),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2, connectionstyle="arc3,rad=0.05"))

    # ML -> forecast
    ax.annotate('', xy=(t_forecast[0] - t_forecast[4]/2, t_forecast[1] - 0.2), 
                xytext=(t_mlreg[0] + t_mlreg[4]/2, t_mlreg[1] - 0.2),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.2))

    # Auth -> user tables
    auth_top = (t_auth[0], t_auth[1])
    for t in [t_profiles, t_roles, t_limits]:
        ax.annotate('', xy=(t[0] - t[4]/2, (t[1] + t[3])/2), 
                    xytext=(auth_top[0] + t_auth[4]/2, auth_top[1] - 0.1),
                    arrowprops=dict(arrowstyle='->', color='#555', lw=1.0, connectionstyle="arc3,rad=0.1"))

    ax.annotate('', xy=(t_chat_sess[0] - t_chat_sess[4]/2, (t_chat_sess[1] + t_chat_sess[3])/2), 
                xytext=(auth_top[0] + t_auth[4]/2, auth_top[1] - 0.1),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.0, connectionstyle="arc3,rad=0.15"))
    ax.annotate('', xy=(t_saved_loc[0] - t_saved_loc[4]/2, (t_saved_loc[1] + t_saved_loc[3])/2), 
                xytext=(auth_top[0] + t_auth[4]/2, auth_top[1] - 0.1),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.0, connectionstyle="arc3,rad=0.2"))
    ax.annotate('', xy=(t_saved_sim[0] - t_saved_sim[4]/2, (t_saved_sim[1] + t_saved_sim[3])/2), 
                xytext=(auth_top[0] + t_auth[4]/2, auth_top[1] - 0.1),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.0, connectionstyle="arc3,rad=0.25"))
    ax.annotate('', xy=(t_audit[0] - t_audit[4]/2, (t_audit[1] + t_audit[3])/2), 
                xytext=(auth_top[0] + t_auth[4]/2, auth_top[1] - 0.1),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.0, connectionstyle="arc3,rad=0.3"))

    # Chat sessions -> messages
    ax.annotate('', xy=(t_chat_msg[0] - t_chat_msg[4]/2, (t_chat_msg[1] + t_chat_msg[3])/2), 
                xytext=(t_chat_sess[0] + t_chat_sess[4]/2, (t_chat_sess[1] + t_chat_sess[3])/2),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.0))

    # Saved items -> municipalities
    ax.annotate('', xy=(geo_x, t_municipalities[3]), 
                xytext=(t_saved_loc[0], t_saved_loc[1] + 0.2),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.0, connectionstyle="arc3,rad=0.3"))
    ax.annotate('', xy=(geo_x, t_municipalities[3]), 
                xytext=(t_saved_sim[0], t_saved_sim[1] + 0.2),
                arrowprops=dict(arrowstyle='->', color='#555', lw=1.0, connectionstyle="arc3,rad=-0.2"))

    # Domain labels
    ax.text(1.5, 21.5, 'Geographic\nHierarchy', ha='center', va='center', fontsize=10, 
            fontweight='bold', color=COLORS['geo'], style='italic')
    ax.text(10.0, 21.5, 'Renewable\nEnergy', ha='center', va='center', fontsize=10, 
            fontweight='bold', color=COLORS['renewable'], style='italic')
    ax.text(17.0, 23.0, 'Statistics &\nMachine Learning', ha='center', va='center', fontsize=10, 
            fontweight='bold', color=COLORS['stats'], style='italic')
    ax.text(1.5, 5.5, 'User\nManagement', ha='center', va='center', fontsize=10, 
            fontweight='bold', color=COLORS['user'], style='italic')

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=200, bbox_inches='tight', facecolor='#F8F9FA', edgecolor='none')
    print(f"ERD saved to {OUTPUT_PATH}")
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `subplots()`, `set_xlim()`, `set_ylim()`, `axis()`, `set_facecolor()`.


## `supabase/schema_structure/lumi_schema_v3.sql`

**File:** `supabase/schema_structure/lumi_schema_v3.sql`

**Summary:** SQL schema or migration script that defines the LUMI database tables.

**First lines:**
```sql



SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


COMMENT ON SCHEMA "public" IS 'standard public schema';



CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";



```


## `supabase/schema_structure/lumi_schema_v4.sql`

**File:** `supabase/schema_structure/lumi_schema_v4.sql`

**Summary:** SQL schema or migration script that defines the LUMI database tables.

**First lines:**
```sql



SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


COMMENT ON SCHEMA "public" IS 'standard public schema';



CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";



```


## `supabase/schema_structure/lumischema.sql`

**File:** `supabase/schema_structure/lumischema.sql`

**Summary:** SQL schema or migration script that defines the LUMI database tables.

**First lines:**
```sql



SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


COMMENT ON SCHEMA "public" IS 'standard public schema';



CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";



```


## `package.json`

**File:** `package.json`

**Summary:** JSON configuration or data file.

**First lines:**
```json
{
  "name": "lumi-root",
  "private": true,
  "version": "0.1.0",
  "scripts": {
    "dev": "concurrently \"npm run dev --prefix react-frontend\" \"uvicorn main:app --reload --host 0.0.0.0 --port 8000 --app-dir fastapi-backend\""
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4.3.0",
    "@tailwindcss/vite": "^4.3.0",
    "concurrently": "^9.0.1",
    "tailwindcss": "^4.3.0"
  }
}
```


## `pyproject.toml`

**File:** `pyproject.toml`

**Summary:** Python project configuration file.

**First lines:**
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "lumi-backend"
version = "0.1.0"
dependencies = [
    "fastapi==0.115.0",
    "pydantic-settings==2.4.0",
    "python-dotenv==1.0.1",
    "supabase==2.10.0",
    "python-jose[cryptography]==3.3.0",
    "httpx==0.27.2",
    "redis==5.0.8",
    "google-genai==0.6.0",
    "groq==0.18.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
]

[tool.vercel]
entrypoint = "api.index:app"
```


## `python_scripts/append_istabreeze_products.py`

**File:** `python_scripts/append_istabreeze_products.py`

**Summary:** Source file `python_scripts/append_istabreeze_products.py`.

### `normalize_name`

- **File:** `python_scripts/append_istabreeze_products.py`
- **Lines:** `17-21`
- **Signature:** `def normalize_name(text: str) -> str:`
- **Purpose:** Normalizes name.

**Code:**
```python
def normalize_name(text: str) -> str:
    cleaned = text.lower().strip()
    cleaned = "".join(ch if ch.isalnum() or ch.isspace() or ch in "-" else " " for ch in cleaned)
    cleaned = " ".join(cleaned.split())
    return cleaned
```

**Explanation:** It accepts `text` and returns `str`. See the code below for the full implementation. Key calls include `strip()`, `lower()`, `join()`, `isalnum()`, `isspace()`.

### `build_rows`

- **File:** `python_scripts/append_istabreeze_products.py`
- **Lines:** `24-59`
- **Signature:** `def build_rows() -> List[Dict[str, object]]:`
- **Purpose:** Builds rows.

**Code:**
```python
def build_rows() -> List[Dict[str, object]]:
    return [
        {
            "product_name": "IstaBreeze 450plus 12V or 24V wind generator",
            "price_raw": "EUR 360.00",
            "price_value": 360.00,
            "currency": "EUR",
            "energy_category": "wind",
            "energy_subcategory": "turbine",
            "source_site": "istabreeze",
            "source_file": "istabreeze_collection_500w.csv",
            "url": "https://en.istabreeze.store/de-fr/products/windgenerator-istabreeze%C2%AE-air-speed-in-12v-oder-24v",
        },
        {
            "product_name": "IstaBreeze Air-Speed 500W 12V or 24V wind turbine with carbon blades",
            "price_raw": "EUR 290.00",
            "price_value": 290.00,
            "currency": "EUR",
            "energy_category": "wind",
            "energy_subcategory": "turbine",
            "source_site": "istabreeze",
            "source_file": "istabreeze_collection_500w.csv",
            "url": "https://en.istabreeze.store/de-fr/products/istabreeze-airspeed-500w-carbon-buy",
        },
        {
            "product_name": "IstaBreeze i-500 12V or 24V wind turbine",
            "price_raw": "EUR 210.00",
            "price_value": 210.00,
            "currency": "EUR",
            "energy_category": "wind",
            "energy_subcategory": "turbine",
            "source_site": "istabreeze",
            "source_file": "istabreeze_collection_500w.csv",
            "url": "https://en.istabreeze.store/de-fr/products/i500-12v-24v-windkraftanlage",
        },
    ]
```

**Explanation:** It accepts zero arguments and returns `List[Dict[str, object]]`. See the code below for the full implementation.

### `main`

- **File:** `python_scripts/append_istabreeze_products.py`
- **Lines:** `62-89`
- **Signature:** `def main() -> None:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> None:
    parser = argparse.ArgumentParser(description="Append ISTABREEZE products to cleaned dataset.")
    parser.add_argument("--cleaned", type=Path, default=DEFAULT_CLEANED_PATH)
    args = parser.parse_args()

    cleaned_path = args.cleaned
    df = pd.read_csv(cleaned_path, dtype=str)
    columns = list(df.columns)

    new_rows = []
    for row in build_rows():
        full_row = {col: "" for col in columns}
        full_row.update(row)
        full_row["product_name_raw"] = row["product_name"]
        full_row["product_name_normalized"] = normalize_name(row["product_name"])
        full_row.setdefault("ratings", "")
        full_row.setdefault("reviews", "")
        full_row.setdefault("price_note", "")
        full_row.setdefault("rejection_reason", "")
        new_rows.append(full_row)

    combined = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    combined = combined.drop_duplicates(
        subset=["product_name_normalized", "price_value", "currency", "source_site", "url"],
        keep="first",
    )

    combined.to_csv(cleaned_path, index=False)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `ArgumentParser()`, `add_argument()`, `parse_args()`, `read_csv()`, `list()`.


## `python_scripts/clean_scraped_products.py`

**File:** `python_scripts/clean_scraped_products.py`

**Summary:** Source file `python_scripts/clean_scraped_products.py`.

### `setup_logging`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `79-83`
- **Signature:** `def setup_logging(level: str) -> None:`
- **Purpose:** Sets up logging.

**Code:**
```python
def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(levelname)s | %(message)s",
    )
```

**Explanation:** It accepts `level` and returns `None`. See the code below for the full implementation. Key calls include `basicConfig()`, `getattr()`, `upper()`.

### `normalize_header`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `86-87`
- **Signature:** `def normalize_header(header: str) -> str:`
- **Purpose:** Normalizes header.

**Code:**
```python
def normalize_header(header: str) -> str:
    return re.sub(r"\s+", "_", header.strip().lower())
```

**Explanation:** It accepts `header` and returns `str`. See the code below for the full implementation. Key calls include `sub()`, `lower()`, `strip()`.

### `standardize_columns`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `90-110`
- **Signature:** `def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:`
- **Purpose:** Handles standardize columns.

**Code:**
```python
def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = {col: normalize_header(col) for col in df.columns}
    df = df.rename(columns=normalized)

    reverse_lookup: Dict[str, str] = {}
    for canonical, aliases in HEADER_SYNONYMS.items():
        for alias in aliases:
            reverse_lookup[alias] = canonical

    rename_map = {}
    for col in df.columns:
        if col in reverse_lookup:
            rename_map[col] = reverse_lookup[col]
    df = df.rename(columns=rename_map)

    for canonical in HEADER_SYNONYMS:
        if canonical not in df.columns:
            df[canonical] = ""

    df = df.dropna(axis=1, how="all")
    return df
```

**Explanation:** It accepts `df` and returns `pd.DataFrame`. See the code below for the full implementation. Key calls include `normalize_header()`, `rename()`, `items()`, `dropna()`.

### `sniff_delimiter`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `113-117`
- **Signature:** `def sniff_delimiter(sample: str) -> Optional[str]:`
- **Purpose:** Handles sniff delimiter.

**Code:**
```python
def sniff_delimiter(sample: str) -> Optional[str]:
    try:
        return csv.Sniffer().sniff(sample).delimiter
    except csv.Error:
        return None
```

**Explanation:** It accepts `sample` and returns `Optional[str]`. See the code below for the full implementation. Key calls include `sniff()`, `Sniffer()`.

### `read_csv_with_fallback`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `120-152`
- **Signature:** `def read_csv_with_fallback(path: Path) -> Tuple[Optional[pd.DataFrame], Optional[str]]:`
- **Purpose:** Reads csv with fallback.

**Code:**
```python
def read_csv_with_fallback(path: Path) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    encodings = ["utf-8", "utf-8-sig", "latin-1"]
    delimiters = [",", "\t", ";"]

    sample = ""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            sample = handle.read(4096)
    except Exception as exc:
        return None, f"read failed: {exc}"

    sniffed = sniff_delimiter(sample)
    if sniffed and sniffed not in delimiters:
        delimiters.insert(0, sniffed)

    for encoding in encodings:
        for delimiter in delimiters:
            try:
                df = pd.read_csv(
                    path,
                    dtype=str,
                    encoding=encoding,
                    encoding_errors="replace",
                    on_bad_lines="skip",
                    sep=delimiter,
                )
                if df.empty:
                    continue
                return df, None
            except Exception:
                continue

    return None, "parse failed with fallback encodings/delimiters"
```

**Explanation:** It accepts `path` and returns `Tuple[Optional[pd.DataFrame], Optional[str]]`. See the code below for the full implementation. Key calls include `open()`, `read()`, `sniff_delimiter()`, `insert()`, `read_csv()`.

### `validate_file`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `155-167`
- **Signature:** `def validate_file(path: Path) -> Optional[str]:`
- **Purpose:** Validates file.

**Code:**
```python
def validate_file(path: Path) -> Optional[str]:
    if not path.exists():
        return "missing"
    if path.stat().st_size == 0:
        return "empty file"
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            header = handle.readline().strip()
            if not header:
                return "missing header"
    except Exception as exc:
        return f"unreadable: {exc}"
    return None
```

**Explanation:** It accepts `path` and returns `Optional[str]`. See the code below for the full implementation. Key calls include `exists()`, `stat()`, `open()`, `strip()`, `readline()`.

### `normalize_text`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `170-177`
- **Signature:** `def normalize_text(text: str) -> str:`
- **Purpose:** Normalizes text.

**Code:**
```python
def normalize_text(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", " ", text)
    for phrase in SPAM_PHRASES:
        cleaned = cleaned.replace(phrase, " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
```

**Explanation:** It accepts `text` and returns `str`. See the code below for the full implementation. Key calls include `sub()`, `replace()`, `strip()`.

### `normalize_name`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `180-186`
- **Signature:** `def normalize_name(name: str) -> str:`
- **Purpose:** Normalizes name.

**Code:**
```python
def normalize_name(name: str) -> str:
    if not name:
        return ""
    normalized = normalize_text(name).lower()
    normalized = re.sub(r"[^a-z0-9\s\-]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized
```

**Explanation:** It accepts `name` and returns `str`. See the code below for the full implementation. Key calls include `lower()`, `normalize_text()`, `sub()`, `strip()`.

### `detect_currency`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `189-194`
- **Signature:** `def detect_currency(price_raw: str, source_site: str) -> str:`
- **Purpose:** Handles detect currency.

**Code:**
```python
def detect_currency(price_raw: str, source_site: str) -> str:
    lowered = price_raw.lower()
    for currency, tokens in CURRENCY_SYMBOLS.items():
        if any(token in lowered for token in tokens):
            return currency.upper()
    return "PHP"
```

**Explanation:** It accepts `price_raw`, `source_site` and returns `str`. See the code below for the full implementation. Key calls include `lower()`, `items()`, `any()`, `upper()`.

### `parse_price_value`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `197-220`
- **Signature:** `def parse_price_value(price_raw: str, source_site: str) -> Tuple[Optional[float], str]:`
- **Purpose:** Parses price value.

**Code:**
```python
def parse_price_value(price_raw: str, source_site: str) -> Tuple[Optional[float], str]:
    if not price_raw:
        return None, ""

    raw_lower = price_raw.strip().lower()
    if raw_lower in PLACEHOLDER_PRICES:
        return None, "placeholder"

    cleaned = re.sub(r"[,$]", "", price_raw)
    cleaned = cleaned.replace("\u20b1", "")
    cleaned = cleaned.replace("PHP", "").replace("php", "")
    cleaned = cleaned.replace("USD", "").replace("usd", "")
    cleaned = cleaned.replace("US$", "").replace("us$", "")

    numbers = re.findall(r"\d+(?:\.\d+)?", cleaned)
    if not numbers:
        return None, "no numeric price"

    values = [float(value) for value in numbers]
    if len(values) >= 2 and ("-" in cleaned or " to " in cleaned.lower()):
        median_value = (min(values) + max(values)) / 2
        return median_value, "range median"

    return values[0], ""
```

**Explanation:** It accepts `price_raw`, `source_site` and returns `Tuple[Optional[float], str]`. See the code below for the full implementation. Key calls include `lower()`, `strip()`, `sub()`, `replace()`, `findall()`.

### `assign_category`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `223-246`
- **Signature:** `def assign_category(name_normalized: str) -> Tuple[Optional[str], Optional[str]]:`
- **Purpose:** Handles assign category.

**Code:**
```python
def assign_category(name_normalized: str) -> Tuple[Optional[str], Optional[str]]:
    if not name_normalized:
        return None, None

    for keyword in EXCLUSION_KEYWORDS:
        if keyword in name_normalized:
            return None, None

    matched_categories = []
    for category, keywords in POSITIVE_KEYWORDS.items():
        if any(keyword in name_normalized for keyword in keywords):
            matched_categories.append(category)

    if not matched_categories:
        return None, None

    category = matched_categories[0]
    subcategory = None
    for sub, keywords in SUBCATEGORY_KEYWORDS.get(category, {}).items():
        if any(keyword in name_normalized for keyword in keywords):
            subcategory = sub
            break

    return category, subcategory
```

**Explanation:** It accepts `name_normalized` and returns `Tuple[Optional[str], Optional[str]]`. See the code below for the full implementation. Key calls include `items()`, `any()`, `append()`, `get()`.

### `is_corrupted_name`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `249-259`
- **Signature:** `def is_corrupted_name(name: str) -> bool:`
- **Purpose:** Handles is corrupted name.

**Code:**
```python
def is_corrupted_name(name: str) -> bool:
    if not name:
        return True
    if "\ufffd" in name:
        return True
    alnum = sum(ch.isalnum() for ch in name)
    if alnum == 0:
        return True
    if alnum / max(len(name), 1) < 0.3:
        return True
    return False
```

**Explanation:** It accepts `name` and returns `bool`. See the code below for the full implementation. Key calls include `sum()`, `isalnum()`, `max()`, `len()`.

### `is_spam_name`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `262-270`
- **Signature:** `def is_spam_name(name: str) -> bool:`
- **Purpose:** Handles is spam name.

**Code:**
```python
def is_spam_name(name: str) -> bool:
    lowered = name.lower()
    if any(phrase in lowered for phrase in SPAM_PHRASES):
        return True
    if len(lowered) < 4:
        return True
    if len(set(lowered)) <= 3:
        return True
    return False
```

**Explanation:** It accepts `name` and returns `bool`. See the code below for the full implementation. Key calls include `lower()`, `any()`, `len()`, `set()`.

### `dedupe_rows`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `273-293`
- **Signature:** `def dedupe_rows(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:`
- **Purpose:** Handles dedupe rows.

**Code:**
```python
def dedupe_rows(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    best_by_key: Dict[str, Dict[str, str]] = {}
    for row in rows:
        key_parts = [
            row.get("product_name_normalized", ""),
            str(row.get("price_value", "")),
            row.get("currency", ""),
            row.get("url", ""),
        ]
        key = "|".join(key_parts)
        if key not in best_by_key:
            best_by_key[key] = row
            continue

        current = best_by_key[key]
        current_score = sum(1 for value in current.values() if value not in ("", None))
        candidate_score = sum(1 for value in row.values() if value not in ("", None))
        if candidate_score > current_score:
            best_by_key[key] = row

    return list(best_by_key.values())
```

**Explanation:** It accepts `rows` and returns `List[Dict[str, str]]`. See the code below for the full implementation. Key calls include `join()`, `sum()`, `get()`, `str()`, `values()`.

### `process_file`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `296-359`
- **Signature:** `def process_file(path: Path, stats: Dict[str, int], rejected_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:`
- **Purpose:** Processes file.

**Code:**
```python
def process_file(path: Path, stats: Dict[str, int], rejected_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    error = validate_file(path)
    if error:
        logging.warning("Skipping %s: %s", path.name, error)
        stats["files_skipped"] += 1
        return []

    df, error = read_csv_with_fallback(path)
    if error or df is None:
        logging.warning("Skipping %s: %s", path.name, error or "read failed")
        stats["files_skipped"] += 1
        return []

    df = standardize_columns(df)
    df["source_file"] = path.name
    df["source_site"] = infer_source_site(path.name)

    rows: List[Dict[str, str]] = []
    for _, record in df.iterrows():
        stats["rows_read"] += 1
        row = {key: ("" if pd.isna(value) else str(value).strip()) for key, value in record.items()}
        row["product_name_raw"] = row.get("product_name", "")
        row["product_name"] = normalize_text(row.get("product_name", ""))
        row["product_name_normalized"] = normalize_name(row.get("product_name", ""))

        rejection_reasons = []

        if not row["product_name"]:
            rejection_reasons.append("missing name")
        if is_corrupted_name(row["product_name"]):
            rejection_reasons.append("corrupted name")
        if is_spam_name(row["product_name"]):
            rejection_reasons.append("spam name")

        price_raw = row.get("price_raw", "")
        if not price_raw:
            price_raw = row.get("price", "")
        row["price_raw"] = price_raw
        price_value, price_note = parse_price_value(price_raw, row["source_site"])
        if price_note:
            row["price_note"] = price_note
        if price_value is None:
            rejection_reasons.append("invalid price")
        row["price_value"] = price_value
        row["currency"] = detect_currency(price_raw, row["source_site"])

        category, subcategory = assign_category(row["product_name_normalized"])
        row["energy_category"] = category
        row["energy_subcategory"] = subcategory
        if not category:
            rejection_reasons.append("non-renewable")

        if rejection_reasons:
            stats["rows_rejected"] += 1
            rejected_rows.append({
                **row,
                "rejection_reason": "; ".join(sorted(set(rejection_reasons))),
            })
            continue

        rows.append(row)

    stats["rows_kept"] += len(rows)
    return rows
```

**Explanation:** It accepts `path`, `stats`, `rejected_rows` and returns `List[Dict[str, str]]`. See the code below for the full implementation. Key calls include `validate_file()`, `warning()`, `read_csv_with_fallback()`, `standardize_columns()`, `infer_source_site()`.

### `infer_source_site`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `362-367`
- **Signature:** `def infer_source_site(filename: str) -> str:`
- **Purpose:** Handles infer source site.

**Code:**
```python
def infer_source_site(filename: str) -> str:
    lowered = filename.lower()
    for site in ("amazon", "lazada", "alibaba", "shopee"):
        if site in lowered:
            return site
    return "unknown"
```

**Explanation:** It accepts `filename` and returns `str`. See the code below for the full implementation. Key calls include `lower()`.

### `stable_column_order`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `370-387`
- **Signature:** `def stable_column_order() -> List[str]:`
- **Purpose:** Handles stable column order.

**Code:**
```python
def stable_column_order() -> List[str]:
    return [
        "product_name",
        "product_name_raw",
        "product_name_normalized",
        "price_raw",
        "price_value",
        "currency",
        "energy_category",
        "energy_subcategory",
        "source_site",
        "source_file",
        "url",
        "ratings",
        "reviews",
        "price_note",
        "rejection_reason",
    ]
```

**Explanation:** It accepts zero arguments and returns `List[str]`. See the code below for the full implementation.

### `finalize_dataframe`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `390-395`
- **Signature:** `def finalize_dataframe(rows: List[Dict[str, str]], columns: List[str]) -> pd.DataFrame:`
- **Purpose:** Handles finalize dataframe.

**Code:**
```python
def finalize_dataframe(rows: List[Dict[str, str]], columns: List[str]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    for column in columns:
        if column not in df.columns:
            df[column] = ""
    return df[columns]
```

**Explanation:** It accepts `rows`, `columns` and returns `pd.DataFrame`. See the code below for the full implementation. Key calls include `DataFrame()`.

### `main`

- **File:** `python_scripts/clean_scraped_products.py`
- **Lines:** `398-449`
- **Signature:** `def main() -> None:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> None:
    parser = argparse.ArgumentParser(description="Clean scraped product CSVs.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    setup_logging(args.log_level)

    input_dir: Path = args.input_dir
    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(input_dir.glob("*.csv"))
    if not csv_files:
        logging.warning("No CSV files found in %s", input_dir)
        return

    stats = {
        "files_processed": 0,
        "files_skipped": 0,
        "rows_read": 0,
        "rows_kept": 0,
        "rows_rejected": 0,
    }

    all_rows: List[Dict[str, str]] = []
    rejected_rows: List[Dict[str, str]] = []

    for path in csv_files:
        stats["files_processed"] += 1
        all_rows.extend(process_file(path, stats, rejected_rows))

    deduped_rows = dedupe_rows(all_rows)

    column_order = stable_column_order()
    cleaned_df = finalize_dataframe(deduped_rows, column_order)
    rejected_df = finalize_dataframe(rejected_rows, column_order)

    cleaned_path = output_dir / "cleaned_products_master.csv"
    rejected_path = output_dir / "cleaned_products_rejected.csv"

    cleaned_df.to_csv(cleaned_path, index=False)
    rejected_df.to_csv(rejected_path, index=False)

    logging.info("Files processed: %s", stats["files_processed"])
    logging.info("Files skipped: %s", stats["files_skipped"])
    logging.info("Rows read: %s", stats["rows_read"])
    logging.info("Rows kept: %s", len(cleaned_df))
    logging.info("Rows rejected: %s", len(rejected_df))
    logging.info("Master dataset: %s", cleaned_path)
    logging.info("Rejected rows: %s", rejected_path)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `ArgumentParser()`, `add_argument()`, `parse_args()`, `setup_logging()`, `mkdir()`.


## `python_scripts/elevation_etl.py`

**File:** `python_scripts/elevation_etl.py`

**Summary:** ETL: Enrich municipality_climate_monthly with elevation data.

### `JsonFormatter.format`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `65-76`
- **Signature:** `def format(self, record: logging.LogRecord) -> str:`
- **Purpose:** Method of `JsonFormatter` that handles format.

**Code:**
```python
def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            payload.update(record.extra)
        return json.dumps(payload)
```

**Explanation:** It accepts `record` and returns `str`. See the code below for the full implementation. Key calls include `formatTime()`, `getMessage()`, `formatException()`, `hasattr()`, `isinstance()`.

### `setup_logging`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `79-86`
- **Signature:** `def setup_logging() -> logging.Logger:`
- **Purpose:** Sets up logging.

**Code:**
```python
def setup_logging() -> logging.Logger:
    logger = logging.getLogger("elevation_etl")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.handlers = [handler]
    logger.propagate = False
    return logger
```

**Explanation:** It accepts zero arguments and returns `logging.Logger`. See the code below for the full implementation. Key calls include `getLogger()`, `setLevel()`, `StreamHandler()`, `setFormatter()`, `JsonFormatter()`.

### `load_config`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `89-134`
- **Signature:** `def load_config() -> AppConfig:`
- **Purpose:** Loads config.

**Code:**
```python
def load_config() -> AppConfig:
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=repo_root / ".env", override=False)

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = None
    supabase_key_source = ""
    key_candidates = (
        "SUPABASE_JWT_SERVICE_ROLE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_JWT_ANON_KEY",
        "SUPABASE_ANON_KEY",
        "SUPABASE_KEY",
    )
    for key_name in key_candidates:
        value = os.getenv(key_name)
        if value:
            supabase_key = value
            supabase_key_source = key_name
            break

    if not supabase_url or not supabase_key:
        missing = []
        if not supabase_url:
            missing.append("SUPABASE_URL")
        if not supabase_key:
            missing.append("SUPABASE_SERVICE_ROLE_KEY/SUPABASE_ANON_KEY/SUPABASE_KEY")
        raise ValueError(f"Missing required env vars: {', '.join(missing)}")

    app_cfg = AppConfig(
        batch_size=int(os.getenv("BATCH_SIZE", "200")),
        max_retries=int(os.getenv("HTTP_MAX_RETRIES", "5")),
        backoff_factor=float(os.getenv("HTTP_BACKOFF_FACTOR", "0.5")),
        request_timeout=int(os.getenv("HTTP_TIMEOUT_SECONDS", "20")),
        rate_limit_per_second=float(os.getenv("RATE_LIMIT_PER_SECOND", "4")),
        concurrency=int(os.getenv("CONCURRENCY", "4")),
        dry_run=os.getenv("DRY_RUN", "false").lower() == "true",
        cache_ttl_days=int(os.getenv("CACHE_TTL_DAYS", "365")),
        resume_from_cache=os.getenv("RESUME_FROM_CACHE", "true").lower() == "true",
        use_async_requests=os.getenv("USE_ASYNC", "false").lower() == "true",
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        supabase_key_source=supabase_key_source,
    )

    return app_cfg
```

**Explanation:** It accepts zero arguments and returns `AppConfig`. See the code below for the full implementation. Key calls include `resolve()`, `Path()`, `load_dotenv()`, `getenv()`, `ValueError()`.

### `create_http_session`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `137-149`
- **Signature:** `def create_http_session(cfg: AppConfig) -> requests.Session:`
- **Purpose:** Creates http session.

**Code:**
```python
def create_http_session(cfg: AppConfig) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=cfg.max_retries,
        backoff_factor=cfg.backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
```

**Explanation:** It accepts `cfg` and returns `requests.Session`. See the code below for the full implementation. Key calls include `Session()`, `Retry()`, `HTTPAdapter()`, `mount()`.

### `SupabaseResponse.__init__`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `153-154`
- **Signature:** `def __init__(self, data: Any):`
- **Purpose:** Method of `SupabaseResponse` that handles   init  .

**Code:**
```python
def __init__(self, data: Any):
        self.data = data
```

**Explanation:** It accepts `data`. See the code below for the full implementation.

### `SupabaseRestQuery.__init__`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `158-163`
- **Signature:** `def __init__(self, client: "SupabaseRestClient", table: str):`
- **Purpose:** Method of `SupabaseRestQuery` that handles   init  .

**Code:**
```python
def __init__(self, client: "SupabaseRestClient", table: str):
        self._client = client
        self._table = table
        self._select = "*"
        self._filters: list[tuple[str, str]] = []
        self._single = False
```

**Explanation:** It accepts `client`, `table`. See the code below for the full implementation.

### `SupabaseRestQuery.select`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `165-167`
- **Signature:** `def select(self, columns: str = "*") -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles select.

**Code:**
```python
def select(self, columns: str = "*") -> "SupabaseRestQuery":
        self._select = columns
        return self
```

**Explanation:** It accepts `columns` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.eq`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `169-171`
- **Signature:** `def eq(self, column: str, value: str) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles eq.

**Code:**
```python
def eq(self, column: str, value: str) -> "SupabaseRestQuery":
        self._filters.append((column, value))
        return self
```

**Explanation:** It accepts `column`, `value` and returns `'SupabaseRestQuery'`. See the code below for the full implementation. Key calls include `append()`.

### `SupabaseRestQuery.single`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `173-175`
- **Signature:** `def single(self) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles single.

**Code:**
```python
def single(self) -> "SupabaseRestQuery":
        self._single = True
        return self
```

**Explanation:** It accepts zero arguments and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.update`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `177-179`
- **Signature:** `def update(self, payload: dict[str, Any]) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles update.

**Code:**
```python
def update(self, payload: dict[str, Any]) -> "SupabaseRestQuery":
        self._update_payload = payload
        return self
```

**Explanation:** It accepts `payload` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.execute`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `181-197`
- **Signature:** `def execute(self) -> SupabaseResponse:`
- **Purpose:** Method of `SupabaseRestQuery` that handles execute.

**Code:**
```python
def execute(self) -> SupabaseResponse:
        params: dict[str, str] = {"select": self._select}
        for column, value in self._filters:
            params[column] = f"eq.{value}"
        if self._single:
            params["limit"] = "1"

        url = f"{self._client.base_url}/rest/v1/{self._table}"
        if hasattr(self, "_update_payload"):
            response = self._client.http.patch(url, params=params, json=self._update_payload, headers=self._client.headers)
        else:
            response = self._client.http.get(url, params=params, headers=self._client.headers)
        response.raise_for_status()
        data = response.json()
        if self._single:
            data = data[0] if data else None
        return SupabaseResponse(data)
```

**Explanation:** It accepts zero arguments and returns `SupabaseResponse`. See the code below for the full implementation. Key calls include `hasattr()`, `patch()`, `get()`, `raise_for_status()`, `json()`.

### `SupabaseRestClient.__init__`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `201-208`
- **Signature:** `def __init__(self, base_url: str, api_key: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles   init  .

**Code:**
```python
def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Prefer": "return=representation",
        }
        self.http = httpx.Client(timeout=10.0)
```

**Explanation:** It accepts `base_url`, `api_key`. See the code below for the full implementation. Key calls include `rstrip()`, `Client()`.

### `SupabaseRestClient.table`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `210-211`
- **Signature:** `def table(self, table_name: str) -> SupabaseRestQuery:`
- **Purpose:** Method of `SupabaseRestClient` that handles table.

**Code:**
```python
def table(self, table_name: str) -> SupabaseRestQuery:
        return SupabaseRestQuery(self, table_name)
```

**Explanation:** It accepts `table_name` and returns `SupabaseRestQuery`. See the code below for the full implementation. Key calls include `SupabaseRestQuery()`.

### `_is_jwt_key`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `214-215`
- **Signature:** `def _is_jwt_key(key: str | None) -> bool:`
- **Purpose:** Handles  is jwt key.

**Code:**
```python
def _is_jwt_key(key: str | None) -> bool:
    return bool(key) and JWT_PATTERN.match(key) is not None
```

**Explanation:** It accepts `key` and returns `bool`. See the code below for the full implementation. Key calls include `bool()`, `match()`.

### `build_supabase_client`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `218-239`
- **Signature:** `def build_supabase_client(cfg: AppConfig) -> "Client | SupabaseRestClient":`
- **Purpose:** Builds supabase client.

**Code:**
```python
def build_supabase_client(cfg: AppConfig) -> "Client | SupabaseRestClient":
    if not cfg.supabase_url or not cfg.supabase_key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY/SUPABASE_KEY.")
    try:
        from supabase import create_client
    except Exception as exc:
        raise RuntimeError("supabase-py is required for Supabase API mode") from exc

    if _is_jwt_key(cfg.supabase_key):
        try:
            return create_client(cfg.supabase_url, cfg.supabase_key)
        except Exception as exc:
            logging.getLogger("elevation_etl").warning(
                "Supabase JWT client failed; falling back to REST client",
                extra={"extra": {"error": str(exc)}},
            )
            return SupabaseRestClient(cfg.supabase_url, cfg.supabase_key)

    logging.getLogger("elevation_etl").warning(
        "Supabase key is not JWT; using REST client fallback for table queries only.",
    )
    return SupabaseRestClient(cfg.supabase_url, cfg.supabase_key)
```

**Explanation:** It accepts `cfg` and returns `'Client | SupabaseRestClient'`. See the code below for the full implementation. Key calls include `RuntimeError()`, `_is_jwt_key()`, `create_client()`, `warning()`, `SupabaseRestClient()`.

### `fetch_municipalities_supabase`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `242-270`
- **Signature:** `def fetch_municipalities_supabase(client: "Client | SupabaseRestClient", page_size: int = 1000) -> List[Municipality]:`
- **Purpose:** Fetches municipalities supabase.

**Code:**
```python
def fetch_municipalities_supabase(client: "Client | SupabaseRestClient", page_size: int = 1000) -> List[Municipality]:
    all_rows: List[Municipality] = []
    offset = 0
    while True:
        response = (
            client.table("municipalities")
            .select("municipality_id,name,lat,lon")
            .not_.is_("lat", "null")
            .not_.is_("lon", "null")
            .order("municipality_id")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            break
        all_rows.extend(
            Municipality(
                municipality_id=row["municipality_id"],
                name=row["name"],
                lat=float(row["lat"]),
                lon=float(row["lon"]),
            )
            for row in rows
        )
        if len(rows) < page_size:
            break
        offset += page_size
    return all_rows
```

**Explanation:** It accepts `client`, `page_size` and returns `List[Municipality]`. See the code below for the full implementation. Key calls include `execute()`, `extend()`, `len()`, `range()`, `Municipality()`.

### `ensure_cache_dir`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `273-274`
- **Signature:** `def ensure_cache_dir(path: Path) -> None:`
- **Purpose:** Handles ensure cache dir.

**Code:**
```python
def ensure_cache_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
```

**Explanation:** It accepts `path` and returns `None`. See the code below for the full implementation. Key calls include `mkdir()`.

### `cache_path`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `277-278`
- **Signature:** `def cache_path(cache_dir: Path, municipality_id: int) -> Path:`
- **Purpose:** Handles cache path.

**Code:**
```python
def cache_path(cache_dir: Path, municipality_id: int) -> Path:
    return cache_dir / f"{municipality_id}.json"
```

**Explanation:** It accepts `cache_dir`, `municipality_id` and returns `Path`. See the code below for the full implementation.

### `cache_is_fresh`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `281-285`
- **Signature:** `def cache_is_fresh(path: Path, ttl_days: int) -> bool:`
- **Purpose:** Handles cache is fresh.

**Code:**
```python
def cache_is_fresh(path: Path, ttl_days: int) -> bool:
    if not path.exists():
        return False
    age_seconds = time.time() - path.stat().st_mtime
    return age_seconds <= ttl_days * 86400
```

**Explanation:** It accepts `path`, `ttl_days` and returns `bool`. See the code below for the full implementation. Key calls include `exists()`, `time()`, `stat()`.

### `read_cache`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `288-293`
- **Signature:** `def read_cache(path: Path) -> Optional[float]:`
- **Purpose:** Reads cache.

**Code:**
```python
def read_cache(path: Path) -> Optional[float]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return float(data["elevation"])
    except Exception:
        return None
```

**Explanation:** It accepts `path` and returns `Optional[float]`. See the code below for the full implementation. Key calls include `loads()`, `float()`, `read_text()`.

### `write_cache`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `296-297`
- **Signature:** `def write_cache(path: Path, elevation: float) -> None:`
- **Purpose:** Handles write cache.

**Code:**
```python
def write_cache(path: Path, elevation: float) -> None:
    path.write_text(json.dumps({"elevation": elevation}), encoding="utf-8")
```

**Explanation:** It accepts `path`, `elevation` and returns `None`. See the code below for the full implementation. Key calls include `write_text()`, `dumps()`.

### `rate_limit`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `300-308`
- **Signature:** `def rate_limit(last_call: float, rate_limit_per_second: float) -> float:`
- **Purpose:** Handles rate limit.

**Code:**
```python
def rate_limit(last_call: float, rate_limit_per_second: float) -> float:
    if rate_limit_per_second <= 0:
        return time.time()
    min_interval = 1.0 / rate_limit_per_second
    now = time.time()
    elapsed = now - last_call
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    return time.time()
```

**Explanation:** It accepts `last_call`, `rate_limit_per_second` and returns `float`. See the code below for the full implementation. Key calls include `time()`, `sleep()`.

### `fetch_elevation`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `311-341`
- **Signature:** `def fetch_elevation(`
- **Purpose:** Fetches elevation.

**Code:**
```python
def fetch_elevation(
    session: requests.Session,
    municipality: Municipality,
    cfg: AppConfig,
    logger: logging.Logger,
    cache_dir: Path,
) -> Tuple[Optional[float], Optional[str], bool]:
    cache_file = cache_path(cache_dir, municipality.municipality_id)
    if cfg.resume_from_cache and cache_is_fresh(cache_file, cfg.cache_ttl_days):
        cached = read_cache(cache_file)
        if cached is not None:
            return cached, None, True

    params = {"latitude": municipality.lat, "longitude": municipality.lon}
    try:
        resp = session.get(API_URL, params=params, timeout=cfg.request_timeout)
        if resp.status_code != 200:
            return None, f"http_{resp.status_code}", False
        payload = resp.json()
        elevation = payload.get("elevation", [None])[0]
        if elevation is None:
            return None, "missing_elevation", False
        elevation_value = float(elevation)
        write_cache(cache_file, elevation_value)
        return elevation_value, None, False
    except requests.RequestException as exc:
        logger.error(
            "Elevation API request failed",
            extra={"extra": {"municipality_id": municipality.municipality_id, "error": str(exc)}},
        )
        return None, "request_exception", False
```

**Explanation:** It accepts `session`, `municipality`, `cfg`, `logger`, `cache_dir` and returns `Tuple[Optional[float], Optional[str], bool]`. See the code below for the full implementation. Key calls include `cache_path()`, `cache_is_fresh()`, `read_cache()`, `get()`, `json()`.

### `AsyncRateLimiter.__init__`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `345-348`
- **Signature:** `def __init__(self, rate_limit_per_second: float) -> None:`
- **Purpose:** Method of `AsyncRateLimiter` that handles   init  .

**Code:**
```python
def __init__(self, rate_limit_per_second: float) -> None:
        self._rate = rate_limit_per_second
        self._lock = asyncio.Lock()
        self._last_call = 0.0
```

**Explanation:** It accepts `rate_limit_per_second` and returns `None`. See the code below for the full implementation. Key calls include `Lock()`.

### `AsyncRateLimiter.wait`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `350-359`
- **Signature:** `async def wait(self) -> None:`
- **Purpose:** Method of `AsyncRateLimiter` that handles wait.

**Code:**
```python
async def wait(self) -> None:
        if self._rate <= 0:
            return
        async with self._lock:
            min_interval = 1.0 / self._rate
            now = time.time()
            elapsed = now - self._last_call
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            self._last_call = time.time()
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `time()`, `sleep()`.

### `fetch_elevation_async`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `362-403`
- **Signature:** `async def fetch_elevation_async(`
- **Purpose:** Fetches elevation async.

**Code:**
```python
async def fetch_elevation_async(
    client: "httpx.AsyncClient",
    municipality: Municipality,
    cfg: AppConfig,
    logger: logging.Logger,
    cache_dir: Path,
    rate_limiter: AsyncRateLimiter,
) -> Tuple[Optional[float], Optional[str], bool]:
    cache_file = cache_path(cache_dir, municipality.municipality_id)
    if cfg.resume_from_cache and cache_is_fresh(cache_file, cfg.cache_ttl_days):
        cached = read_cache(cache_file)
        if cached is not None:
            return cached, None, True

    params = {"latitude": municipality.lat, "longitude": municipality.lon}
    for attempt in range(cfg.max_retries + 1):
        await rate_limiter.wait()
        try:
            resp = await client.get(API_URL, params=params, timeout=cfg.request_timeout)
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < cfg.max_retries:
                await asyncio.sleep(cfg.backoff_factor * (2 ** attempt))
                continue
            if resp.status_code != 200:
                return None, f"http_{resp.status_code}", False
            payload = resp.json()
            elevation = payload.get("elevation", [None])[0]
            if elevation is None:
                return None, "missing_elevation", False
            elevation_value = float(elevation)
            write_cache(cache_file, elevation_value)
            return elevation_value, None, False
        except Exception as exc:
            if attempt < cfg.max_retries:
                await asyncio.sleep(cfg.backoff_factor * (2 ** attempt))
                continue
            logger.error(
                "Elevation API request failed",
                extra={"extra": {"municipality_id": municipality.municipality_id, "error": str(exc)}},
            )
            return None, "request_exception", False

    return None, "request_exception", False
```

**Explanation:** It accepts `client`, `municipality`, `cfg`, `logger`, `cache_dir`, `rate_limiter` and returns `Tuple[Optional[float], Optional[str], bool]`. See the code below for the full implementation. Key calls include `cache_path()`, `cache_is_fresh()`, `read_cache()`, `range()`, `wait()`.

### `update_elevation_batch_supabase`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `406-432`
- **Signature:** `def update_elevation_batch_supabase(`
- **Purpose:** Updates elevation batch supabase.

**Code:**
```python
def update_elevation_batch_supabase(
    client: "Client | SupabaseRestClient",
    updates: List[Tuple[float, int]],
    dry_run: bool,
    logger: logging.Logger,
) -> int:
    if not updates:
        return 0
    if dry_run:
        return len(updates)

    updated = 0
    for elevation, municipality_id in updates:
        response = (
            client.table("municipality_climate_monthly")
            .update({"elevation": elevation})
            .eq("municipality_id", municipality_id)
            .execute()
        )
        if response.data is None:
            logger.error(
                "Supabase update returned no data",
                extra={"extra": {"municipality_id": municipality_id}},
            )
            continue
        updated += 1
    return updated
```

**Explanation:** It accepts `client`, `updates`, `dry_run`, `logger` and returns `int`. See the code below for the full implementation. Key calls include `len()`, `execute()`, `error()`, `eq()`, `update()`.

### `save_failed_csv`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `435-443`
- **Signature:** `def save_failed_csv(path: Path, failed: List[Tuple[Municipality, str]]) -> None:`
- **Purpose:** Saves failed csv.

**Code:**
```python
def save_failed_csv(path: Path, failed: List[Tuple[Municipality, str]]) -> None:
    if not failed:
        return
    header = "municipality_id,name,lat,lon,reason\n"
    rows = [
        f"{m.municipality_id},{m.name},{m.lat},{m.lon},{reason}\n"
        for m, reason in failed
    ]
    path.write_text(header + "".join(rows), encoding="utf-8")
```

**Explanation:** It accepts `path`, `failed` and returns `None`. See the code below for the full implementation. Key calls include `write_text()`, `join()`.

### `build_arg_parser`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `446-456`
- **Signature:** `def build_arg_parser() -> argparse.ArgumentParser:`
- **Purpose:** Builds arg parser.

**Code:**
```python
def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Enrich climate monthly data with elevation.")
    parser.add_argument("--batch-size", type=int, default=None, help="Update batch size.")
    parser.add_argument("--dry-run", action="store_true", help="Do not write updates.")
    parser.add_argument("--resume-from-cache", action="store_true", help="Use cached API data.")
    parser.add_argument("--no-cache", action="store_true", help="Disable cache usage.")
    parser.add_argument("--rate", type=float, default=None, help="Requests per second.")
    parser.add_argument("--limit", type=int, default=None, help="Limit municipalities for testing.")
    parser.add_argument("--cache-ttl-days", type=int, default=None, help="Cache TTL in days.")
    parser.add_argument("--async-requests", action="store_true", help="Use async HTTP requests.")
    return parser
```

**Explanation:** It accepts zero arguments and returns `argparse.ArgumentParser`. See the code below for the full implementation. Key calls include `ArgumentParser()`, `add_argument()`.

### `process_sync_supabase`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `459-501`
- **Signature:** `def process_sync_supabase(`
- **Purpose:** Processes sync supabase.

**Code:**
```python
def process_sync_supabase(
    client: "Client",
    municipalities: List[Municipality],
    cfg: AppConfig,
    logger: logging.Logger,
    cache_dir: Path,
) -> Tuple[int, int, int, List[Tuple[Municipality, str]]]:
    total_updated = 0
    total_failed = 0
    total_cached = 0
    failed_list: List[Tuple[Municipality, str]] = []

    iterator: Iterable[Municipality]
    if tqdm:
        iterator = tqdm(municipalities, desc="Municipalities")
    else:
        iterator = municipalities

    session = create_http_session(cfg)
    last_call = 0.0
    pending_updates: List[Tuple[float, int]] = []

    for municipality in iterator:
        last_call = rate_limit(last_call, cfg.rate_limit_per_second)
        elevation, error, cached_hit = fetch_elevation(session, municipality, cfg, logger, cache_dir)
        if cached_hit:
            total_cached += 1
        if elevation is None:
            total_failed += 1
            failed_list.append((municipality, error or "unknown"))
            continue

        pending_updates.append((elevation, municipality.municipality_id))
        if len(pending_updates) >= cfg.batch_size:
            updated = update_elevation_batch_supabase(client, pending_updates, cfg.dry_run, logger)
            total_updated += updated
            pending_updates.clear()

    if pending_updates:
        updated = update_elevation_batch_supabase(client, pending_updates, cfg.dry_run, logger)
        total_updated += updated

    return total_updated, total_failed, total_cached, failed_list
```

**Explanation:** It accepts `client`, `municipalities`, `cfg`, `logger`, `cache_dir` and returns `Tuple[int, int, int, List[Tuple[Municipality, str]]]`. See the code below for the full implementation. Key calls include `tqdm()`, `create_http_session()`, `rate_limit()`, `fetch_elevation()`, `append()`.

### `main`

- **File:** `python_scripts/elevation_etl.py`
- **Lines:** `504-564`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    logger = setup_logging()
    app_cfg = load_config()

    parser = build_arg_parser()
    args = parser.parse_args()

    app_cfg = AppConfig(
        batch_size=args.batch_size or app_cfg.batch_size,
        max_retries=app_cfg.max_retries,
        backoff_factor=app_cfg.backoff_factor,
        request_timeout=app_cfg.request_timeout,
        rate_limit_per_second=args.rate or app_cfg.rate_limit_per_second,
        concurrency=app_cfg.concurrency,
        dry_run=args.dry_run or app_cfg.dry_run,
        cache_ttl_days=args.cache_ttl_days or app_cfg.cache_ttl_days,
        resume_from_cache=(not args.no_cache) and (args.resume_from_cache or app_cfg.resume_from_cache),
        use_async_requests=args.async_requests or app_cfg.use_async_requests,
        supabase_url=app_cfg.supabase_url,
        supabase_key=app_cfg.supabase_key,
        supabase_key_source=app_cfg.supabase_key_source,
    )

    cache_dir = Path(CACHE_DIRNAME)
    ensure_cache_dir(cache_dir)
    failed_csv = cache_dir / FAILED_CSV_NAME

    total_updated = 0
    total_failed = 0
    total_cached = 0
    total_processed = 0
    failed_list: List[Tuple[Municipality, str]] = []

    logger.info(
        "Using Supabase API credentials",
        extra={"extra": {"key_source": app_cfg.supabase_key_source}},
    )
    client = build_supabase_client(app_cfg)
    municipalities = fetch_municipalities_supabase(client)
    if args.limit:
        municipalities = municipalities[: args.limit]
    total_processed = len(municipalities)
    total_updated, total_failed, total_cached, failed_list = process_sync_supabase(
        client, municipalities, app_cfg, logger, cache_dir
    )

    save_failed_csv(failed_csv, failed_list)

    logger.info(
        "ETL completed",
        extra={
            "extra": {
                "processed": total_processed,
                "updated": total_updated,
                "cached": total_cached,
                "failed": total_failed,
                "dry_run": app_cfg.dry_run,
            }
        },
    )
    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `setup_logging()`, `load_config()`, `build_arg_parser()`, `parse_args()`, `AppConfig()`.


## `python_scripts/extract_product_kw.py`

**File:** `python_scripts/extract_product_kw.py`

**Summary:** Extract kW values from product listing names and write a new CSV.

### `extract_kw_values`

- **File:** `python_scripts/extract_product_kw.py`
- **Lines:** `20-28`
- **Signature:** `def extract_kw_values(text: str) -> List[float]:`
- **Purpose:** Extract kW values from text. Converts W to kW. Ignores volts-only.

**Code:**
```python
def extract_kw_values(text: str) -> List[float]:
    """Extract kW values from text. Converts W to kW. Ignores volts-only."""
    values: List[float] = []
    for match in KW_REGEX.finditer(text):
        values.append(float(match.group(1)))
    for match in W_REGEX.finditer(text):
        watts = float(match.group(1))
        values.append(watts / 1000.0)
    return values
```

**Explanation:** It accepts `text` and returns `List[float]`. See the code below for the full implementation. Key calls include `finditer()`, `append()`, `float()`, `group()`.

### `mean_or_none`

- **File:** `python_scripts/extract_product_kw.py`
- **Lines:** `31-35`
- **Signature:** `def mean_or_none(values: Iterable[float]) -> Optional[float]:`
- **Purpose:** Handles mean or none.

**Code:**
```python
def mean_or_none(values: Iterable[float]) -> Optional[float]:
    items = list(values)
    if not items:
        return None
    return sum(items) / len(items)
```

**Explanation:** It accepts `values` and returns `Optional[float]`. See the code below for the full implementation. Key calls include `list()`, `sum()`, `len()`.

### `compute_kw`

- **File:** `python_scripts/extract_product_kw.py`
- **Lines:** `38-45`
- **Signature:** `def compute_kw(row: pd.Series) -> Optional[float]:`
- **Purpose:** Computes kw.

**Code:**
```python
def compute_kw(row: pd.Series) -> Optional[float]:
    for column in ("product_name", "product_name_raw"):
        value = row.get(column)
        if isinstance(value, str) and value.strip():
            kw_values = extract_kw_values(value.lower())
            if kw_values:
                return mean_or_none(kw_values)
    return None
```

**Explanation:** It accepts `row` and returns `Optional[float]`. See the code below for the full implementation. Key calls include `get()`, `isinstance()`, `strip()`, `extract_kw_values()`, `lower()`.

### `build_arg_parser`

- **File:** `python_scripts/extract_product_kw.py`
- **Lines:** `48-60`
- **Signature:** `def build_arg_parser() -> argparse.ArgumentParser:`
- **Purpose:** Builds arg parser.

**Code:**
```python
def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract kW values from product listings.")
    parser.add_argument(
        "--input",
        default=str(Path("scraped_data") / "output" / "cleaned" / "cleaned_products_master.csv"),
        help="Input CSV path.",
    )
    parser.add_argument(
        "--output",
        default=str(Path("scraped_data") / "output" / "cleaned" / "cleaned_products_master_kw.csv"),
        help="Output CSV path.",
    )
    return parser
```

**Explanation:** It accepts zero arguments and returns `argparse.ArgumentParser`. See the code below for the full implementation. Key calls include `ArgumentParser()`, `add_argument()`, `str()`, `Path()`.

### `main`

- **File:** `python_scripts/extract_product_kw.py`
- **Lines:** `63-74`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    args = build_arg_parser().parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    df = pd.read_csv(input_path)
    df["kw"] = df.apply(compute_kw, axis=1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Wrote {output_path}")
    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `parse_args()`, `build_arg_parser()`, `Path()`, `read_csv()`, `apply()`.


## `python_scripts/fill_missing_coords_from_geojson.py`

**File:** `python_scripts/fill_missing_coords_from_geojson.py`

**Summary:** Fill missing municipality lat/lon from Philippine GeoJSON centroids.

### `_rest_get`

- **File:** `python_scripts/fill_missing_coords_from_geojson.py`
- **Lines:** `59-63`
- **Signature:** `def _rest_get(table: str, params: dict) -> list[dict]:`
- **Purpose:** Handles  rest get.

**Code:**
```python
def _rest_get(table: str, params: dict) -> list[dict]:
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = httpx.get(url, params=params, headers=HEADERS, timeout=30.0)
    resp.raise_for_status()
    return resp.json() or []
```

**Explanation:** It accepts `table`, `params` and returns `list[dict]`. See the code below for the full implementation. Key calls include `get()`, `raise_for_status()`, `json()`.

### `_rest_patch`

- **File:** `python_scripts/fill_missing_coords_from_geojson.py`
- **Lines:** `66-70`
- **Signature:** `def _rest_patch(table: str, pk_col: str, pk_val: int, data: dict) -> None:`
- **Purpose:** Handles  rest patch.

**Code:**
```python
def _rest_patch(table: str, pk_col: str, pk_val: int, data: dict) -> None:
    url = f"{SUPABASE_URL}/rest/v1/{table}?{pk_col}=eq.{pk_val}"
    resp = httpx.patch(url, json=data, headers={**HEADERS, "Prefer": "return=minimal"}, timeout=30.0)
    if resp.status_code not in (200, 204):
        logger.warning("PATCH failed for %s.%s=%s: %s %s", table, pk_col, pk_val, resp.status_code, resp.text[:200])
```

**Explanation:** It accepts `table`, `pk_col`, `pk_val`, `data` and returns `None`. See the code below for the full implementation. Key calls include `patch()`, `warning()`.

### `normalize_name`

- **File:** `python_scripts/fill_missing_coords_from_geojson.py`
- **Lines:** `73-84`
- **Signature:** `def normalize_name(name: str) -> str:`
- **Purpose:** Normalize municipality name for matching.

**Code:**
```python
def normalize_name(name: str) -> str:
    """Normalize municipality name for matching."""
    return (
        name.upper()
        .replace(" CITY", "")
        .replace(" (POB.)", "")
        .replace(" (CAPITAL)", "")
        .replace(" (", " ")
        .replace(")", " ")
        .replace(".", "")
        .strip()
    )
```

**Explanation:** It accepts `name` and returns `str`. See the code below for the full implementation. Key calls include `strip()`, `replace()`, `upper()`.

### `compute_centroids`

- **File:** `python_scripts/fill_missing_coords_from_geojson.py`
- **Lines:** `87-109`
- **Signature:** `def compute_centroids(geojson_path: Path) -> dict[str, tuple[float, float]]:`
- **Purpose:** Compute centroid lat/lon for each municipality in GeoJSON.

**Code:**
```python
def compute_centroids(geojson_path: Path) -> dict[str, tuple[float, float]]:
    """Compute centroid lat/lon for each municipality in GeoJSON."""
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    centroids: dict[str, tuple[float, float]] = {}
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        name = props.get("adm3_en", "").strip()
        if not name:
            continue
        geom = feat.get("geometry")
        if not geom:
            continue
        try:
            poly = shape(geom)
            centroid = poly.centroid
            centroids[normalize_name(name)] = (round(centroid.y, 6), round(centroid.x, 6))
        except Exception:
            continue

    logger.info("Computed %d centroids from GeoJSON", len(centroids))
    return centroids
```

**Explanation:** It accepts `geojson_path` and returns `dict[str, tuple[float, float]]`. See the code below for the full implementation. Key calls include `open()`, `load()`, `get()`, `strip()`, `shape()`.

### `main`

- **File:** `python_scripts/fill_missing_coords_from_geojson.py`
- **Lines:** `112-184`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("Missing SUPABASE_URL or SUPABASE_KEY")
        return 1

    if not GEOJSON_PATH.exists():
        logger.error("GeoJSON not found: %s", GEOJSON_PATH)
        return 1

    # 1. Load GeoJSON centroids
    logger.info("Loading GeoJSON centroids...")
    centroids = compute_centroids(GEOJSON_PATH)

    # 2. Load municipalities CSV for name mapping
    logger.info("Loading municipalities CSV...")
    municipalities = pd.read_csv(CSV_MUNI_PATH)
    provinces = pd.read_csv(CSV_PROV_PATH).rename(columns={"Name": "name"})
    prov_map = dict(zip(provinces["province_id"], provinces["name"]))

    # 3. Fetch missing municipality IDs from Supabase
    logger.info("Fetching municipalities missing lat/lon...")
    missing_ids: list[int] = []
    offset = 0
    while True:
        params = {
            "select": "municipality_id,name",
            "or": "(lat.is.null,lon.is.null)",
            "offset": str(offset),
            "limit": "1000",
        }
        rows = _rest_get("municipalities", params)
        if not rows:
            break
        for row in rows:
            missing_ids.append(int(row["municipality_id"]))
        if len(rows) < 1000:
            break
        offset += 1000

    logger.info("Found %d municipalities missing coordinates", len(missing_ids))

    # 4. Build name -> (lat, lon) map from GeoJSON centroids
    updated = 0
    failed = 0
    for _, row in municipalities.iterrows():
        mid = int(row["municipality_id"])
        if mid not in missing_ids:
            continue

        name = str(row["name"])
        norm = normalize_name(name)

        # Try exact normalized match first
        coords = centroids.get(norm)

        # If no match, try without parenthetical suffix
        if not coords and "(" in norm:
            alt = norm.split("(")[0].strip()
            coords = centroids.get(alt)

        if not coords:
            logger.warning("No GeoJSON match for: %s (normalized: %s)", name, norm)
            failed += 1
            continue

        lat, lon = coords
        _rest_patch("municipalities", "municipality_id", mid, {"lat": lat, "lon": lon})
        updated += 1
        if updated % 100 == 0:
            logger.info("Updated %d/%d municipalities", updated, len(missing_ids))

    logger.info("Done. Updated: %d, Failed: %d, Total missing: %d", updated, failed, len(missing_ids))
    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `error()`, `exists()`, `info()`, `compute_centroids()`, `read_csv()`.


## `python_scripts/geocode_missing_coords.py`

**File:** `python_scripts/geocode_missing_coords.py`

**Summary:** Geocode missing lat/lon for municipalities using Nominatim + direct Supabase REST API.

### `load_env_file`

- **File:** `python_scripts/geocode_missing_coords.py`
- **Lines:** `27-36`
- **Signature:** `def load_env_file(path: Path) -> None:`
- **Purpose:** Loads env file.

**Code:**
```python
def load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))
```

**Explanation:** It accepts `path` and returns `None`. See the code below for the full implementation. Key calls include `is_file()`, `open()`, `strip()`, `split()`, `setdefault()`.

### `_rest_get`

- **File:** `python_scripts/geocode_missing_coords.py`
- **Lines:** `72-76`
- **Signature:** `def _rest_get(table: str, params: dict) -> list[dict]:`
- **Purpose:** Handles  rest get.

**Code:**
```python
def _rest_get(table: str, params: dict) -> list[dict]:
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = httpx.get(url, params=params, headers=HEADERS, timeout=30.0)
    resp.raise_for_status()
    return resp.json() or []
```

**Explanation:** It accepts `table`, `params` and returns `list[dict]`. See the code below for the full implementation. Key calls include `get()`, `raise_for_status()`, `json()`.

### `_rest_patch`

- **File:** `python_scripts/geocode_missing_coords.py`
- **Lines:** `79-83`
- **Signature:** `def _rest_patch(table: str, pk_col: str, pk_val: int, data: dict) -> None:`
- **Purpose:** Handles  rest patch.

**Code:**
```python
def _rest_patch(table: str, pk_col: str, pk_val: int, data: dict) -> None:
    url = f"{SUPABASE_URL}/rest/v1/{table}?{pk_col}=eq.{pk_val}"
    resp = httpx.patch(url, json=data, headers={**HEADERS, "Prefer": "return=minimal"}, timeout=30.0)
    if resp.status_code not in (200, 204):
        logger.warning("PATCH failed for %s.%s=%s: %s %s", table, pk_col, pk_val, resp.status_code, resp.text[:200])
```

**Explanation:** It accepts `table`, `pk_col`, `pk_val`, `data` and returns `None`. See the code below for the full implementation. Key calls include `patch()`, `warning()`.

### `fetch_missing_ids`

- **File:** `python_scripts/geocode_missing_coords.py`
- **Lines:** `86-104`
- **Signature:** `def fetch_missing_ids(table: str, id_field: str) -> list[int]:`
- **Purpose:** Fetches missing ids.

**Code:**
```python
def fetch_missing_ids(table: str, id_field: str) -> list[int]:
    missing: list[int] = []
    offset = 0
    while True:
        params = {
            "select": id_field,
            "or": "(lat.is.null,lon.is.null)",
            "offset": str(offset),
            "limit": str(PAGE_SIZE),
        }
        rows = _rest_get(table, params)
        if not rows:
            break
        for row in rows:
            missing.append(int(row[id_field]))
        if len(rows) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return missing
```

**Explanation:** It accepts `table`, `id_field` and returns `list[int]`. See the code below for the full implementation. Key calls include `_rest_get()`, `str()`, `append()`, `len()`, `int()`.

### `geocode`

- **File:** `python_scripts/geocode_missing_coords.py`
- **Lines:** `107-149`
- **Signature:** `def geocode(query: str, cache: dict) -> tuple[float | None, float | None]:`
- **Purpose:** Handles geocode.

**Code:**
```python
def geocode(query: str, cache: dict) -> tuple[float | None, float | None]:
    if query in cache:
        return cache[query]

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": USER_AGENT}
    if NOMINATIM_EMAIL:
        params["email"] = NOMINATIM_EMAIL
        headers["From"] = NOMINATIM_EMAIL

    for attempt in range(1, 4):
        try:
            resp = httpx.get(url, params=params, headers=headers, timeout=20.0)
        except Exception as exc:
            logger.warning("HTTP error for %r (attempt %d): %s", query, attempt, exc)
            time.sleep(5)
            continue

        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 60))
            logger.warning("Rate limited for %r. Waiting %ds...", query, wait)
            time.sleep(wait)
            continue

        if not resp.is_success:
            logger.warning("HTTP %s for %r: %s", resp.status_code, query, resp.text[:200])
            cache[query] = (None, None)
            return None, None

        data = resp.json()
        if not data:
            logger.warning("No results for: %r", query)
            cache[query] = (None, None)
            return None, None

        lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
        cache[query] = (lat, lon)
        return lat, lon

    logger.error("Exhausted retries for: %r", query)
    cache[query] = (None, None)
    return None, None
```

**Explanation:** It accepts `query`, `cache` and returns `tuple[float | None, float | None]`. See the code below for the full implementation. Key calls include `range()`, `json()`, `get()`, `int()`, `warning()`.

### `update_coords`

- **File:** `python_scripts/geocode_missing_coords.py`
- **Lines:** `152-155`
- **Signature:** `def update_coords(table: str, id_field: str, id_value: int, lat, lon) -> None:`
- **Purpose:** Updates coords.

**Code:**
```python
def update_coords(table: str, id_field: str, id_value: int, lat, lon) -> None:
    if lat is None or lon is None:
        return
    _rest_patch(table, id_field, id_value, {"lat": lat, "lon": lon})
```

**Explanation:** It accepts `table`, `id_field`, `id_value`, `lat`, `lon` and returns `None`. See the code below for the full implementation. Key calls include `_rest_patch()`.

### `main`

- **File:** `python_scripts/geocode_missing_coords.py`
- **Lines:** `158-214`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    # Load CSVs
    csv_dir = Path("regionalData")
    regions = pd.read_csv(csv_dir / "regions.csv")
    provinces = pd.read_csv(csv_dir / "provinces.csv").rename(columns={"Name": "name"})
    municipalities = pd.read_csv(csv_dir / "municipalities.csv")

    region_by_id = regions.set_index("region_id")
    prov_by_id = provinces.set_index("province_id")
    mun_by_id = municipalities.set_index("municipality_id")

    cache: dict[str, tuple] = {}

    # --- Regions ---
    missing_region_ids = fetch_missing_ids("regions", "region_id")
    logger.info("Regions missing coords: %d", len(missing_region_ids))
    for _, row in regions.iterrows():
        if int(row["region_id"]) not in missing_region_ids:
            continue
        query = f"{row['name']}, Philippines"
        lat, lon = geocode(query, cache)
        if lat and lon:
            update_coords("regions", "region_id", int(row["region_id"]), lat, lon)
        time.sleep(RATE_LIMIT_SECONDS)

    # --- Provinces ---
    missing_province_ids = fetch_missing_ids("provinces", "province_id")
    logger.info("Provinces missing coords: %d", len(missing_province_ids))
    for _, row in provinces.iterrows():
        if int(row["province_id"]) not in missing_province_ids:
            continue
        region = region_by_id.loc[row["region_id"]]
        query = f"{row['name']}, {region['name']}, Philippines"
        lat, lon = geocode(query, cache)
        if lat and lon:
            update_coords("provinces", "province_id", int(row["province_id"]), lat, lon)
        time.sleep(RATE_LIMIT_SECONDS)

    # --- Municipalities ---
    missing_muni_ids = fetch_missing_ids("municipalities", "municipality_id")
    logger.info("Municipalities missing coords: %d", len(missing_muni_ids))
    total = len(missing_muni_ids)
    for idx, row in municipalities.iterrows():
        mid = int(row["municipality_id"])
        if mid not in missing_muni_ids:
            continue
        prov = prov_by_id.loc[row["province_id"]]
        query = f"{row['name']}, {prov['name']}, Philippines"
        lat, lon = geocode(query, cache)
        if lat and lon:
            update_coords("municipalities", "municipality_id", mid, lat, lon)
        if (idx + 1) % 50 == 0 or idx == total - 1:
            logger.info("Geocoded %d/%d municipalities", idx + 1, total)
        time.sleep(RATE_LIMIT_SECONDS)

    logger.info("Done updating coordinates.")
    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `Path()`, `read_csv()`, `rename()`, `set_index()`, `fetch_missing_ids()`.


## `python_scripts/get_geocode.py`

**File:** `python_scripts/get_geocode.py`

**Summary:** Source file `python_scripts/get_geocode.py`.

### `load_env_file`

- **File:** `python_scripts/get_geocode.py`
- **Lines:** `12-21`
- **Signature:** `def load_env_file(path):`
- **Purpose:** Loads env file.

**Code:**
```python
def load_env_file(path):
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))
```

**Explanation:** It accepts `path`. See the code below for the full implementation. Key calls include `isfile()`, `open()`, `strip()`, `split()`, `setdefault()`.

### `geocode`

- **File:** `python_scripts/get_geocode.py`
- **Lines:** `52-90`
- **Signature:** `def geocode(query: str, cache: dict) -> tuple[float | None, float | None]:`
- **Purpose:** Handles geocode.

**Code:**
```python
def geocode(query: str, cache: dict) -> tuple[float | None, float | None]:
    if query in cache:
        return cache[query]

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": 1}
    headers = {"User-Agent": USER_AGENT}
    if NOMINATIM_EMAIL:
        params["email"] = NOMINATIM_EMAIL
        headers["From"] = NOMINATIM_EMAIL

    for attempt in range(1, 4):  # up to 3 manual retries for 429
        resp = session.get(url, params=params, headers=headers, timeout=20)

        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", 60))
            print(f"  [429] Rate limited. Waiting {wait}s before retry {attempt}/3...")
            time.sleep(wait)
            continue

        if not resp.ok:
            print(f"  [ERROR] HTTP {resp.status_code} for query: {query!r}")
            print(f"          Response: {resp.text[:200]}")
            cache[query] = (None, None)
            return None, None

        data = resp.json()
        if not data:
            print(f"  [WARN] No results for: {query!r}")
            cache[query] = (None, None)
            return None, None

        lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
        cache[query] = (lat, lon)
        return lat, lon

    print(f"  [FAIL] Exhausted retries for: {query!r}")
    cache[query] = (None, None)
    return None, None
```

**Explanation:** It accepts `query`, `cache` and returns `tuple[float | None, float | None]`. See the code below for the full implementation. Key calls include `range()`, `get()`, `json()`, `int()`, `sleep()`.

### `update_coords`

- **File:** `python_scripts/get_geocode.py`
- **Lines:** `93-96`
- **Signature:** `def update_coords(table: str, id_field: str, id_value: int, lat, lon):`
- **Purpose:** Updates coords.

**Code:**
```python
def update_coords(table: str, id_field: str, id_value: int, lat, lon):
    if lat is None or lon is None:
        return
    supabase.table(table).update({"lat": lat, "lon": lon}).eq(id_field, id_value).execute()
```

**Explanation:** It accepts `table`, `id_field`, `id_value`, `lat`, `lon`. See the code below for the full implementation. Key calls include `execute()`, `eq()`, `update()`, `table()`.

### `fetch_missing_ids`

- **File:** `python_scripts/get_geocode.py`
- **Lines:** `99-118`
- **Signature:** `def fetch_missing_ids(table: str, id_field: str, page_size: int = 1000) -> set[int]:`
- **Purpose:** Fetches missing ids.

**Code:**
```python
def fetch_missing_ids(table: str, id_field: str, page_size: int = 1000) -> set[int]:
    missing = set()
    offset = 0
    while True:
        response = (
            supabase.table(table)
            .select(id_field)
            .or_("lat.is.null,lon.is.null")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            break
        for row in rows:
            missing.add(int(row[id_field]))
        if len(rows) < page_size:
            break
        offset += page_size
    return missing
```

**Explanation:** It accepts `table`, `id_field`, `page_size` and returns `set[int]`. See the code below for the full implementation. Key calls include `set()`, `execute()`, `add()`, `len()`, `range()`.


## `python_scripts/ingest_nasa_power_monthly.py`

**File:** `python_scripts/ingest_nasa_power_monthly.py`

**Summary:** Source file `python_scripts/ingest_nasa_power_monthly.py`.

### `parse_bool`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `34-37`
- **Signature:** `def parse_bool(value: str | None, default: bool) -> bool:`
- **Purpose:** Parses bool.

**Code:**
```python
def parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y"}
```

**Explanation:** It accepts `value`, `default` and returns `bool`. See the code below for the full implementation. Key calls include `lower()`, `strip()`.

### `load_config`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `56-87`
- **Signature:** `def load_config() -> Config:`
- **Purpose:** Loads config.

**Code:**
```python
def load_config() -> Config:
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=repo_root / ".env", override=False)
    supabase_key = None
    for key_name in (
        "SUPABASE_JWT_SERVICE_ROLE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_JWT_ANON_KEY",
        "SUPABASE_ANON_KEY",
        "SUPABASE_KEY",
        "VITE_SUPABASE_SERVICE_ROLE_KEY",
        "VITE_SUPABASE_ANON_KEY",
    ):
        value = os.getenv(key_name)
        if value:
            supabase_key = value
            break
    date_formats = "YYYY"
    return Config(
        supabase_url=os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL"),
        supabase_key=supabase_key,
        start_year=MIN_INGEST_YEAR,
        end_year=MAX_INGEST_YEAR,
        rate_limit_seconds=float(os.getenv("NASA_RATE_LIMIT_SECONDS", "0.6")),
        request_timeout=int(os.getenv("NASA_REQUEST_TIMEOUT", "30")),
        only_missing=parse_bool(os.getenv("ONLY_MISSING"), True),
        update_existing=parse_bool(os.getenv("UPDATE_EXISTING"), True),
        batch_size=int(os.getenv("BATCH_SIZE", "500")),
        max_retries=int(os.getenv("NASA_MAX_RETRIES", "5")),
        backoff_factor=float(os.getenv("NASA_BACKOFF_FACTOR", "1.5")),
        nasa_date_formats=[fmt.strip().upper() for fmt in date_formats.split(",") if fmt.strip()],
    )
```

**Explanation:** It accepts zero arguments and returns `Config`. See the code below for the full implementation. Key calls include `resolve()`, `Path()`, `load_dotenv()`, `getenv()`, `Config()`.

### `build_supabase_client`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `90-93`
- **Signature:** `def build_supabase_client(config: Config) -> Client:`
- **Purpose:** Builds supabase client.

**Code:**
```python
def build_supabase_client(config: Config) -> Client:
    if not config.supabase_url or not config.supabase_key:
        raise SystemExit("Missing SUPABASE_URL or SUPABASE_*_KEY in .env.")
    return create_client(config.supabase_url, config.supabase_key)
```

**Explanation:** It accepts `config` and returns `Client`. See the code below for the full implementation. Key calls include `SystemExit()`, `create_client()`.

### `configure_logging`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `96-100`
- **Signature:** `def configure_logging() -> None:`
- **Purpose:** Configures logging.

**Code:**
```python
def configure_logging() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `basicConfig()`, `upper()`, `getenv()`.

### `build_session`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `103-113`
- **Signature:** `def build_session(config: Config) -> requests.Session:`
- **Purpose:** Builds session.

**Code:**
```python
def build_session(config: Config) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=config.max_retries,
        backoff_factor=config.backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session
```

**Explanation:** It accepts `config` and returns `requests.Session`. See the code below for the full implementation. Key calls include `Session()`, `Retry()`, `mount()`, `HTTPAdapter()`.

### `last_complete_year_month`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `116-123`
- **Signature:** `def last_complete_year_month() -> tuple[int, int]:`
- **Purpose:** Handles last complete year month.

**Code:**
```python
def last_complete_year_month() -> tuple[int, int]:
    today = date.today()
    last_month = today.month - 1
    last_year = today.year
    if last_month < 1:
        last_month = 12
        last_year -= 1
    return last_year, last_month
```

**Explanation:** It accepts zero arguments and returns `tuple[int, int]`. See the code below for the full implementation. Key calls include `today()`.

### `month_range`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `126-134`
- **Signature:** `def month_range(start_year: int, end_year: int) -> list[tuple[int, int]]:`
- **Purpose:** Handles month range.

**Code:**
```python
def month_range(start_year: int, end_year: int) -> list[tuple[int, int]]:
    last_year, last_month = last_complete_year_month()
    months = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if year > last_year or (year == last_year and month > last_month):
                break
            months.append((year, month))
    return months
```

**Explanation:** It accepts `start_year`, `end_year` and returns `list[tuple[int, int]]`. See the code below for the full implementation. Key calls include `last_complete_year_month()`, `range()`, `append()`.

### `fetch_municipalities`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `137-165`
- **Signature:** `def fetch_municipalities(supabase: Client, page_size: int = 1000) -> list[dict]:`
- **Purpose:** Fetches municipalities.

**Code:**
```python
def fetch_municipalities(supabase: Client, page_size: int = 1000) -> list[dict]:
    all_rows: list[dict] = []
    offset = 0
    while True:
        response = (
            supabase.table("municipalities")
            .select("municipality_id,name,lat,lon")
            .not_.is_("lat", "null")
            .not_.is_("lon", "null")
            .order("municipality_id")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            break
        all_rows.extend(
            {
                "municipality_id": row["municipality_id"],
                "name": row["name"],
                "lat": float(row["lat"]),
                "lon": float(row["lon"]),
            }
            for row in rows
        )
        if len(rows) < page_size:
            break
        offset += page_size
    return all_rows
```

**Explanation:** It accepts `supabase`, `page_size` and returns `list[dict]`. See the code below for the full implementation. Key calls include `execute()`, `extend()`, `len()`, `range()`, `float()`.

### `fetch_existing_months`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `168-190`
- **Signature:** `def fetch_existing_months(`
- **Purpose:** Fetches existing months.

**Code:**
```python
def fetch_existing_months(
    supabase: Client,
    municipality_id: int,
    page_size: int = 1000,
) -> set[tuple[int, int]]:
    existing: set[tuple[int, int]] = set()
    offset = 0
    while True:
        response = (
            supabase.table("municipality_climate_monthly")
            .select("year,month")
            .eq("municipality_id", municipality_id)
            .range(offset, offset + page_size - 1)
            .execute()
        )
        rows = response.data or []
        if not rows:
            break
        existing.update((row["year"], row["month"]) for row in rows)
        if len(rows) < page_size:
            break
        offset += page_size
    return existing
```

**Explanation:** It accepts `supabase`, `municipality_id`, `page_size` and returns `set[tuple[int, int]]`. See the code below for the full implementation. Key calls include `set()`, `execute()`, `update()`, `len()`, `range()`.

### `find_missing_months`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `193-199`
- **Signature:** `def find_missing_months(`
- **Purpose:** Finds missing months.

**Code:**
```python
def find_missing_months(
    existing: set[tuple[int, int]],
    start_year: int,
    end_year: int,
) -> list[tuple[int, int]]:
    expected = month_range(start_year, end_year)
    return [(year, month) for (year, month) in expected if (year, month) not in existing]
```

**Explanation:** It accepts `existing`, `start_year`, `end_year` and returns `list[tuple[int, int]]`. See the code below for the full implementation. Key calls include `month_range()`.

### `build_nasa_start_end`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `202-235`
- **Signature:** `def build_nasa_start_end(`
- **Purpose:** Builds nasa start end.

**Code:**
```python
def build_nasa_start_end(
    start_year: int,
    start_month: int,
    end_year: int,
    date_format: str,
) -> tuple[str, str]:
    if start_month < 1 or start_month > 12:
        raise ValueError(f"Invalid start_month: {start_month}")
    last_year, last_month = last_complete_year_month()
    if date_format == "YYYY":
        end_year = min(end_year, last_year)
        return (f"{start_year}", f"{end_year}")

    if end_year >= last_year:
        end_year = last_year
        end_month = last_month
    else:
        end_month = 12

    if date_format == "YYYYMM":
        return (
            f"{start_year}{start_month:02d}",
            f"{end_year}{end_month:02d}",
        )

    if date_format == "YYYYMMDD":
        start_day = 1
        end_day = calendar.monthrange(end_year, end_month)[1]
        return (
            f"{start_year}{start_month:02d}{start_day:02d}",
            f"{end_year}{end_month:02d}{end_day:02d}",
        )

    raise ValueError(f"Unsupported NASA_DATE_FORMATS entry: {date_format}")
```

**Explanation:** It accepts `start_year`, `start_month`, `end_year`, `date_format` and returns `tuple[str, str]`. See the code below for the full implementation. Key calls include `ValueError()`, `last_complete_year_month()`, `min()`, `monthrange()`.

### `nasa_request`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `238-285`
- **Signature:** `def nasa_request(`
- **Purpose:** Handles nasa request.

**Code:**
```python
def nasa_request(
    session: requests.Session,
    lat: float,
    lon: float,
    start_year: int,
    start_month: int,
    end_year: int,
    timeout: int,
    date_formats: list[str],
) -> dict:
    last_error: RuntimeError | None = None
    for date_format in date_formats:
        start_value, end_value = build_nasa_start_end(
            start_year,
            start_month,
            end_year,
            date_format,
        )
        params = {
            "parameters": ",".join(PARAMETERS),
            "community": "RE",
            "format": "JSON",
            "latitude": f"{lat:.6f}",
            "longitude": f"{lon:.6f}",
            "start": start_value,
            "end": end_value,
        }
        logging.debug(
            "NASA request format=%s start=%s end=%s lat=%s lon=%s",
            date_format,
            start_value,
            end_value,
            lat,
            lon,
        )
        resp = session.get(NASA_BASE_URL, params=params, timeout=timeout)
        if resp.ok:
            return resp.json()
        if resp.status_code == 422 and "date formatting" in resp.text:
            last_error = RuntimeError(
                f"NASA POWER error {resp.status_code}: {resp.text[:300]}"
            )
            continue
        raise RuntimeError(f"NASA POWER error {resp.status_code}: {resp.text[:300]}")

    if last_error:
        raise last_error
    raise RuntimeError("NASA POWER error: failed to build a valid date format")
```

**Explanation:** It accepts `session`, `lat`, `lon`, `start_year`, `start_month`, `end_year`, `timeout`, `date_formats` and returns `dict`. See the code below for the full implementation. Key calls include `build_nasa_start_end()`, `debug()`, `get()`, `RuntimeError()`, `join()`.

### `parse_nasa_payload`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `288-292`
- **Signature:** `def parse_nasa_payload(payload: dict) -> dict[str, dict[str, float | None]]:`
- **Purpose:** Parses nasa payload.

**Code:**
```python
def parse_nasa_payload(payload: dict) -> dict[str, dict[str, float | None]]:
    try:
        return payload["properties"]["parameter"]
    except KeyError as exc:
        raise RuntimeError("Unexpected NASA POWER response format") from exc
```

**Explanation:** It accepts `payload` and returns `dict[str, dict[str, float | None]]`. See the code below for the full implementation. Key calls include `RuntimeError()`.

### `coerce_value`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `295-301`
- **Signature:** `def coerce_value(value) -> float | None:`
- **Purpose:** Handles coerce value.

**Code:**
```python
def coerce_value(value) -> float | None:
    if value in MISSING_VALUES or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
```

**Explanation:** It accepts `value` and returns `float | None`. See the code below for the full implementation. Key calls include `float()`.

### `build_rows`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `304-329`
- **Signature:** `def build_rows(`
- **Purpose:** Builds rows.

**Code:**
```python
def build_rows(
    municipality_id: int,
    parameter_map: dict[str, dict[str, float | None]],
    start_year: int,
    end_year: int,
) -> list[dict]:
    rows = []
    for year, month in month_range(start_year, end_year):
        key = f"{year}{month:02d}"
        row = {
            "municipality_id": municipality_id,
            "year": year,
            "month": month,
            "t2m": coerce_value(parameter_map.get("T2M", {}).get(key)),
            "t2m_max": coerce_value(parameter_map.get("T2M_MAX", {}).get(key)),
            "t2m_min": coerce_value(parameter_map.get("T2M_MIN", {}).get(key)),
            "rh2m": coerce_value(parameter_map.get("RH2M", {}).get(key)),
            "rhoa": coerce_value(parameter_map.get("RHOA", {}).get(key)),
            "prectotcorr": coerce_value(parameter_map.get("PRECTOTCORR", {}).get(key)),
            "ws10m": coerce_value(parameter_map.get("WS10M", {}).get(key)),
            "allsky_sfc_sw_dwn": coerce_value(parameter_map.get("ALLSKY_SFC_SW_DWN", {}).get(key)),
            "cloud_amt": coerce_value(parameter_map.get("CLOUD_AMT", {}).get(key)),
            "surface_pressure": coerce_value(parameter_map.get("PS", {}).get(key)),
        }
        rows.append(row)
    return rows
```

**Explanation:** It accepts `municipality_id`, `parameter_map`, `start_year`, `end_year` and returns `list[dict]`. See the code below for the full implementation. Key calls include `month_range()`, `append()`, `coerce_value()`, `get()`.

### `build_rhoa_rows`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `332-341`
- **Signature:** `def build_rhoa_rows(rows: Iterable[dict]) -> list[dict]:`
- **Purpose:** Builds rhoa rows.

**Code:**
```python
def build_rhoa_rows(rows: Iterable[dict]) -> list[dict]:
    return [
        {
            "municipality_id": row["municipality_id"],
            "year": row["year"],
            "month": row["month"],
            "rhoa": row.get("rhoa"),
        }
        for row in rows
    ]
```

**Explanation:** It accepts `rows` and returns `list[dict]`. See the code below for the full implementation. Key calls include `get()`.

### `upsert_rows`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `344-354`
- **Signature:** `def upsert_rows(supabase: Client, rows: Iterable[dict]) -> int:`
- **Purpose:** Upserts rows.

**Code:**
```python
def upsert_rows(supabase: Client, rows: Iterable[dict]) -> int:
    if not rows:
        return 0
    response = (
        supabase.table("municipality_climate_monthly")
        .upsert(list(rows), on_conflict="municipality_id,year,month")
        .execute()
    )
    if response.data is None:
        raise RuntimeError("Supabase upsert returned no data.")
    return len(response.data)
```

**Explanation:** It accepts `supabase`, `rows` and returns `int`. See the code below for the full implementation. Key calls include `execute()`, `upsert()`, `list()`, `table()`, `RuntimeError()`.

### `sanitize_lat_lon`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `357-358`
- **Signature:** `def sanitize_lat_lon(lat: float, lon: float) -> bool:`
- **Purpose:** Handles sanitize lat lon.

**Code:**
```python
def sanitize_lat_lon(lat: float, lon: float) -> bool:
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0
```

**Explanation:** It accepts `lat`, `lon` and returns `bool`. See the code below for the full implementation.

### `main`

- **File:** `python_scripts/ingest_nasa_power_monthly.py`
- **Lines:** `361-475`
- **Signature:** `def main() -> None:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> None:
    configure_logging()
    config = load_config()
    supabase = build_supabase_client(config)

    session = build_session(config)
    total_rows = 0

    municipalities = fetch_municipalities(supabase)
    logging.info("Municipalities to process: %s", len(municipalities))

    for index, municipality in enumerate(municipalities, start=1):
        municipality_id = municipality["municipality_id"]
        name = municipality["name"]
        lat = municipality["lat"]
        lon = municipality["lon"]

        if not sanitize_lat_lon(lat, lon):
            logging.warning(
                "Skipping municipality %s due to invalid lat/lon: %s, %s",
                municipality_id,
                lat,
                lon,
            )
            continue

        existing = fetch_existing_months(supabase, municipality_id)

        if config.only_missing:
            missing_months = find_missing_months(
                existing,
                config.start_year,
                config.end_year,
            )
            if not missing_months and not config.update_existing:
                logging.info(
                    "[%s/%s] %s already complete. Skipping.",
                    index,
                    len(municipalities),
                    name,
                )
                continue
            if config.update_existing:
                start_year = config.start_year
                start_month = 1
            else:
                start_year, start_month = min(missing_months)
        else:
            start_year = config.start_year
            start_month = 1

        try:
            payload = nasa_request(
                session,
                lat,
                lon,
                start_year,
                start_month,
                config.end_year,
                config.request_timeout,
                config.nasa_date_formats,
            )
        except Exception as exc:
            logging.error(
                "NASA request failed for municipality %s (%s): %s",
                municipality_id,
                name,
                exc,
            )
            continue

        parameter_map = parse_nasa_payload(payload)
        rows = build_rows(municipality_id, parameter_map, start_year, config.end_year)

        existing_set = set(existing)
        missing_rows = [
            row
            for row in rows
            if (row["year"], row["month"]) not in existing_set
        ]
        existing_rows = [
            row
            for row in rows
            if (row["year"], row["month"]) in existing_set
        ]
        rhoa_rows = build_rhoa_rows(existing_rows) if config.update_existing else []

        inserted = 0
        try:
            for i in range(0, len(missing_rows), config.batch_size):
                batch = missing_rows[i : i + config.batch_size]
                inserted += upsert_rows(supabase, batch)
            for i in range(0, len(rhoa_rows), config.batch_size):
                batch = rhoa_rows[i : i + config.batch_size]
                inserted += upsert_rows(supabase, batch)
        except Exception as exc:
            logging.error(
                "Insert failed for municipality %s (%s): %s",
                municipality_id,
                name,
                exc,
            )
            continue

        total_rows += inserted
        logging.info(
            "[%s/%s] %s processed, rows upserted: %s",
            index,
            len(municipalities),
            name,
            inserted,
        )
        time.sleep(config.rate_limit_seconds)

    logging.info("Done. Total rows upserted: %s", total_rows)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `configure_logging()`, `load_config()`, `build_supabase_client()`, `build_session()`, `fetch_municipalities()`.


## `python_scripts/join_wind_data.py`

**File:** `python_scripts/join_wind_data.py`

**Summary:** Source file `python_scripts/join_wind_data.py`.

### `detect_source`

- **File:** `python_scripts/join_wind_data.py`
- **Lines:** `32-37`
- **Signature:** `def detect_source(filename: str) -> str:`
- **Purpose:** Handles detect source.

**Code:**
```python
def detect_source(filename: str) -> str:
    lower = filename.lower()
    for source in ["amazon", "alibaba", "lazada", "shopee"]:
        if source in lower:
            return source
    return "unknown"
```

**Explanation:** It accepts `filename` and returns `str`. See the code below for the full implementation. Key calls include `lower()`.

### `normalize_text`

- **File:** `python_scripts/join_wind_data.py`
- **Lines:** `40-41`
- **Signature:** `def normalize_text(value: Optional[str]) -> str:`
- **Purpose:** Normalizes text.

**Code:**
```python
def normalize_text(value: Optional[str]) -> str:
    return (value or "").strip()
```

**Explanation:** It accepts `value` and returns `str`. See the code below for the full implementation. Key calls include `strip()`.

### `parse_power_w`

- **File:** `python_scripts/join_wind_data.py`
- **Lines:** `44-62`
- **Signature:** `def parse_power_w(text: str) -> Optional[float]:`
- **Purpose:** Parses power w.

**Code:**
```python
def parse_power_w(text: str) -> Optional[float]:
    matches = []
    for match in POWER_RE.finditer(text):
        raw = match.group("num").replace(",", "")
        try:
            num = float(raw)
        except ValueError:
            continue
        unit = match.group("unit").lower()
        if unit == "mw":
            power = num * 1_000_000.0
        elif unit == "kw":
            power = num * 1_000.0
        else:
            power = num
        matches.append(power)
    if not matches:
        return None
    return max(matches)
```

**Explanation:** It accepts `text` and returns `Optional[float]`. See the code below for the full implementation. Key calls include `finditer()`, `replace()`, `lower()`, `append()`, `float()`.

### `parse_diameter_m`

- **File:** `python_scripts/join_wind_data.py`
- **Lines:** `65-93`
- **Signature:** `def parse_diameter_m(text: str) -> Optional[float]:`
- **Purpose:** Parses diameter m.

**Code:**
```python
def parse_diameter_m(text: str) -> Optional[float]:
    candidates: List[float] = []

    for match in METER_RE.finditer(text):
        if "m/s" in text[match.start():match.start() + 6].lower():
            continue
        num = float(match.group("num"))
        candidates.append(num)

    for match in CM_RE.finditer(text):
        num = float(match.group("num"))
        candidates.append(num / 100.0)

    for match in MM_RE.finditer(text):
        num = float(match.group("num"))
        candidates.append(num / 1000.0)

    for match in IN_RE.finditer(text):
        num = float(match.group("num"))
        candidates.append(num * 0.0254)

    for match in FT_RE.finditer(text):
        num = float(match.group("num"))
        candidates.append(num * 0.3048)

    if not candidates:
        return None

    return max(candidates)
```

**Explanation:** It accepts `text` and returns `Optional[float]`. See the code below for the full implementation. Key calls include `finditer()`, `float()`, `append()`, `lower()`, `group()`.

### `parse_wind_speed_mps`

- **File:** `python_scripts/join_wind_data.py`
- **Lines:** `96-116`
- **Signature:** `def parse_wind_speed_mps(text: str) -> Optional[float]:`
- **Purpose:** Parses wind speed mps.

**Code:**
```python
def parse_wind_speed_mps(text: str) -> Optional[float]:
    matches = []
    for match in WIND_SPEED_RE.finditer(text):
        try:
            matches.append(float(match.group("num")))
        except ValueError:
            continue

    if not matches:
        return None

    lowered = text.lower()
    for match in WIND_SPEED_RE.finditer(text):
        window = lowered[max(0, match.start() - 12):match.end() + 12]
        if "rated" in window:
            try:
                return float(match.group("num"))
            except ValueError:
                continue

    return max(matches)
```

**Explanation:** It accepts `text` and returns `Optional[float]`. See the code below for the full implementation. Key calls include `finditer()`, `append()`, `float()`, `group()`, `lower()`.

### `compute_power_coefficient`

- **File:** `python_scripts/join_wind_data.py`
- **Lines:** `119-126`
- **Signature:** `def compute_power_coefficient(power_w: float, diameter_m: float, wind_speed_mps: float, air_density: float) -> Optional[float]:`
- **Purpose:** Computes power coefficient.

**Code:**
```python
def compute_power_coefficient(power_w: float, diameter_m: float, wind_speed_mps: float, air_density: float) -> Optional[float]:
    if power_w <= 0 or diameter_m <= 0 or wind_speed_mps <= 0:
        return None
    area = math.pi * (diameter_m / 2.0) ** 2
    denom = 0.5 * air_density * area * (wind_speed_mps ** 3)
    if denom <= 0:
        return None
    return power_w / denom
```

**Explanation:** It accepts `power_w`, `diameter_m`, `wind_speed_mps`, `air_density` and returns `Optional[float]`. See the code below for the full implementation.

### `read_csv_rows`

- **File:** `python_scripts/join_wind_data.py`
- **Lines:** `129-134`
- **Signature:** `def read_csv_rows(path: str) -> Iterable[Dict[str, str]]:`
- **Purpose:** Reads csv rows.

**Code:**
```python
def read_csv_rows(path: str) -> Iterable[Dict[str, str]]:
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row:
                yield row
```

**Explanation:** It accepts `path` and returns `Iterable[Dict[str, str]]`. See the code below for the full implementation. Key calls include `open()`, `DictReader()`.

### `read_json_rows`

- **File:** `python_scripts/join_wind_data.py`
- **Lines:** `137-152`
- **Signature:** `def read_json_rows(path: str) -> Iterable[Dict[str, str]]:`
- **Purpose:** Reads json rows.

**Code:**
```python
def read_json_rows(path: str) -> Iterable[Dict[str, str]]:
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        payload = json.load(handle)

    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                yield item
        return

    if isinstance(payload, dict):
        if "data" in payload and isinstance(payload["data"], list):
            for item in payload["data"]:
                if isinstance(item, dict):
                    yield item
            return
```

**Explanation:** It accepts `path` and returns `Iterable[Dict[str, str]]`. See the code below for the full implementation. Key calls include `open()`, `load()`, `isinstance()`.

### `extract_row_fields`

- **File:** `python_scripts/join_wind_data.py`
- **Lines:** `155-161`
- **Signature:** `def extract_row_fields(row: Dict[str, str]) -> Tuple[str, str, str, str, str]:`
- **Purpose:** Extracts row fields.

**Code:**
```python
def extract_row_fields(row: Dict[str, str]) -> Tuple[str, str, str, str, str]:
    name = normalize_text(row.get("name") or row.get("title") or row.get("product") or row.get("product_name"))
    price = normalize_text(row.get("price") or row.get("price_value") or row.get("sale_price"))
    ratings = normalize_text(row.get("ratings") or row.get("rating"))
    reviews = normalize_text(row.get("reviews") or row.get("review_count"))
    url = normalize_text(row.get("url") or row.get("link") or row.get("product_url"))
    return name, price, ratings, reviews, url
```

**Explanation:** It accepts `row` and returns `Tuple[str, str, str, str, str]`. See the code below for the full implementation. Key calls include `normalize_text()`, `get()`.

### `find_wind_files`

- **File:** `python_scripts/join_wind_data.py`
- **Lines:** `164-174`
- **Signature:** `def find_wind_files(root_dir: str) -> List[str]:`
- **Purpose:** Finds wind files.

**Code:**
```python
def find_wind_files(root_dir: str) -> List[str]:
    paths: List[str] = []
    for root, _dirs, files in os.walk(root_dir):
        for filename in files:
            if not WIND_FILE_PATTERN.search(filename):
                continue
            ext = os.path.splitext(filename)[1].lower()
            if ext not in {".csv", ".json"}:
                continue
            paths.append(os.path.join(root, filename))
    return sorted(paths)
```

**Explanation:** It accepts `root_dir` and returns `List[str]`. See the code below for the full implementation. Key calls include `walk()`, `lower()`, `append()`, `search()`, `join()`.

### `main`

- **File:** `python_scripts/join_wind_data.py`
- **Lines:** `177-272`
- **Signature:** `def main() -> None:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    rows: List[Dict[str, str]] = []
    wind_files = find_wind_files(SCRAPED_DIR)

    for path in wind_files:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".csv":
            source_rows = read_csv_rows(path)
        else:
            source_rows = read_json_rows(path)

        for row in source_rows:
            name, price, ratings, reviews, url = extract_row_fields(row)
            raw_text = " ".join([name, price, ratings, reviews, url])
            power_w = parse_power_w(raw_text)
            diameter_m = parse_diameter_m(raw_text)
            wind_speed = parse_wind_speed_mps(raw_text) or DEFAULT_WIND_SPEED_MPS

            rotor_radius = diameter_m / 2.0 if diameter_m else ""
            power_coeff = ""
            if power_w and diameter_m:
                cp = compute_power_coefficient(power_w, diameter_m, wind_speed, DEFAULT_AIR_DENSITY)
                if cp is not None:
                    power_coeff = cp

            rows.append({
                "source_file": os.path.relpath(path, SCRAPED_DIR).replace("\\", "/"),
                "source_site": detect_source(path),
                "name": name,
                "price": price,
                "ratings": ratings,
                "reviews": reviews,
                "url": url,
                "power_w": f"{power_w:.2f}" if power_w is not None else "",
                "diameter_m": f"{diameter_m:.3f}" if diameter_m is not None else "",
                "rotor_radius_m": f"{rotor_radius:.3f}" if diameter_m is not None else "",
                "wind_speed_mps": f"{wind_speed:.2f}" if wind_speed else "",
                "power_coefficient": f"{power_coeff:.3f}" if isinstance(power_coeff, float) else "",
            })

    fieldnames = [
        "source_file",
        "source_site",
        "name",
        "price",
        "ratings",
        "reviews",
        "url",
        "power_w",
        "diameter_m",
        "rotor_radius_m",
        "wind_speed_mps",
        "power_coefficient",
    ]

    with open(OUT_JOINED, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    rotor_values = [float(r["rotor_radius_m"]) for r in rows if r["rotor_radius_m"]]
    cp_values = [float(r["power_coefficient"]) for r in rows if r["power_coefficient"]]

    avg_rotor = statistics.mean(rotor_values) if rotor_values else 0.0
    avg_cp = statistics.mean(cp_values) if cp_values else 0.0

    with open(OUT_STATS, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "records_total",
            "records_with_rotor_radius",
            "records_with_power_coefficient",
            "avg_rotor_radius_m",
            "avg_power_coefficient",
        ])
        writer.writeheader()
        writer.writerow({
            "records_total": len(rows),
            "records_with_rotor_radius": len(rotor_values),
            "records_with_power_coefficient": len(cp_values),
            "avg_rotor_radius_m": f"{avg_rotor:.3f}",
            "avg_power_coefficient": f"{avg_cp:.3f}",
        })

    print(f"Joined {len(rows)} rows from {len(wind_files)} wind files")
    print(
        "Average rotor radius (m): "
        f"{avg_rotor:.3f} from {len(rotor_values)} rows where a blade diameter was parsed "
        "from text (m/cm/mm/in/ft), then divided by 2."
    )
    print(
        "Average power coefficient: "
        f"{avg_cp:.3f} from {len(cp_values)} rows with both parsed power (W/kW/MW) and diameter; "
        f"uses Cp = P / (0.5 * {DEFAULT_AIR_DENSITY} * A * V^3) with V={DEFAULT_WIND_SPEED_MPS} m/s unless a m/s value is present."
    )
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `makedirs()`, `find_wind_files()`, `lower()`, `read_csv_rows()`, `read_json_rows()`.


## `python_scripts/join_wind_data_betz.py`

**File:** `python_scripts/join_wind_data_betz.py`

**Summary:** Source file `python_scripts/join_wind_data_betz.py`.

### `detect_source`

- **File:** `python_scripts/join_wind_data_betz.py`
- **Lines:** `37-42`
- **Signature:** `def detect_source(filename: str) -> str:`
- **Purpose:** Handles detect source.

**Code:**
```python
def detect_source(filename: str) -> str:
    lower = filename.lower()
    for source in ["amazon", "alibaba", "lazada", "shopee"]:
        if source in lower:
            return source
    return "unknown"
```

**Explanation:** It accepts `filename` and returns `str`. See the code below for the full implementation. Key calls include `lower()`.

### `normalize_text`

- **File:** `python_scripts/join_wind_data_betz.py`
- **Lines:** `45-46`
- **Signature:** `def normalize_text(value: Optional[str]) -> str:`
- **Purpose:** Normalizes text.

**Code:**
```python
def normalize_text(value: Optional[str]) -> str:
    return (value or "").strip()
```

**Explanation:** It accepts `value` and returns `str`. See the code below for the full implementation. Key calls include `strip()`.

### `parse_power_w`

- **File:** `python_scripts/join_wind_data_betz.py`
- **Lines:** `49-67`
- **Signature:** `def parse_power_w(text: str) -> Optional[float]:`
- **Purpose:** Parses power w.

**Code:**
```python
def parse_power_w(text: str) -> Optional[float]:
    matches = []
    for match in POWER_RE.finditer(text):
        raw = match.group("num").replace(",", "")
        try:
            num = float(raw)
        except ValueError:
            continue
        unit = match.group("unit").lower()
        if unit == "mw":
            power = num * 1_000_000.0
        elif unit == "kw":
            power = num * 1_000.0
        else:
            power = num
        matches.append(power)
    if not matches:
        return None
    return max(matches)
```

**Explanation:** It accepts `text` and returns `Optional[float]`. See the code below for the full implementation. Key calls include `finditer()`, `replace()`, `lower()`, `append()`, `float()`.

### `parse_diameter_m`

- **File:** `python_scripts/join_wind_data_betz.py`
- **Lines:** `70-98`
- **Signature:** `def parse_diameter_m(text: str) -> Optional[float]:`
- **Purpose:** Parses diameter m.

**Code:**
```python
def parse_diameter_m(text: str) -> Optional[float]:
    candidates: List[float] = []

    for match in METER_RE.finditer(text):
        if "m/s" in text[match.start():match.start() + 6].lower():
            continue
        num = float(match.group("num"))
        candidates.append(num)

    for match in CM_RE.finditer(text):
        num = float(match.group("num"))
        candidates.append(num / 100.0)

    for match in MM_RE.finditer(text):
        num = float(match.group("num"))
        candidates.append(num / 1000.0)

    for match in IN_RE.finditer(text):
        num = float(match.group("num"))
        candidates.append(num * 0.0254)

    for match in FT_RE.finditer(text):
        num = float(match.group("num"))
        candidates.append(num * 0.3048)

    if not candidates:
        return None

    return max(candidates)
```

**Explanation:** It accepts `text` and returns `Optional[float]`. See the code below for the full implementation. Key calls include `finditer()`, `float()`, `append()`, `lower()`, `group()`.

### `parse_wind_speed_mps`

- **File:** `python_scripts/join_wind_data_betz.py`
- **Lines:** `101-121`
- **Signature:** `def parse_wind_speed_mps(text: str) -> Optional[float]:`
- **Purpose:** Parses wind speed mps.

**Code:**
```python
def parse_wind_speed_mps(text: str) -> Optional[float]:
    matches = []
    for match in WIND_SPEED_RE.finditer(text):
        try:
            matches.append(float(match.group("num")))
        except ValueError:
            continue

    if not matches:
        return None

    lowered = text.lower()
    for match in WIND_SPEED_RE.finditer(text):
        window = lowered[max(0, match.start() - 12):match.end() + 12]
        if "rated" in window:
            try:
                return float(match.group("num"))
            except ValueError:
                continue

    return max(matches)
```

**Explanation:** It accepts `text` and returns `Optional[float]`. See the code below for the full implementation. Key calls include `finditer()`, `append()`, `float()`, `group()`, `lower()`.

### `compute_power_coefficient`

- **File:** `python_scripts/join_wind_data_betz.py`
- **Lines:** `124-147`
- **Signature:** `def compute_power_coefficient(`
- **Purpose:** Computes power coefficient.

**Code:**
```python
def compute_power_coefficient(
    power_w: float,
    diameter_m: float,
    wind_speed_mps: float,
    air_density: float = 1.225,
    clamp_to_betz: bool = False,
) -> Optional[float]:
    if power_w <= 0 or diameter_m <= 0 or wind_speed_mps <= 0:
        return None
    if not 0.9 <= air_density <= 1.3:
        return None

    radius_m = diameter_m / 2.0
    area = math.pi * radius_m ** 2
    available_wind_power = 0.5 * air_density * area * (wind_speed_mps ** 3)
    if available_wind_power <= 0:
        return None

    cp = power_w / available_wind_power

    if clamp_to_betz:
        return min(cp, BETZ_LIMIT)

    return None if cp > BETZ_LIMIT else cp
```

**Explanation:** It accepts `power_w`, `diameter_m`, `wind_speed_mps`, `air_density`, `clamp_to_betz` and returns `Optional[float]`. See the code below for the full implementation. Key calls include `min()`.

### `read_csv_rows`

- **File:** `python_scripts/join_wind_data_betz.py`
- **Lines:** `150-155`
- **Signature:** `def read_csv_rows(path: str) -> Iterable[Dict[str, str]]:`
- **Purpose:** Reads csv rows.

**Code:**
```python
def read_csv_rows(path: str) -> Iterable[Dict[str, str]]:
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row:
                yield row
```

**Explanation:** It accepts `path` and returns `Iterable[Dict[str, str]]`. See the code below for the full implementation. Key calls include `open()`, `DictReader()`.

### `read_json_rows`

- **File:** `python_scripts/join_wind_data_betz.py`
- **Lines:** `158-173`
- **Signature:** `def read_json_rows(path: str) -> Iterable[Dict[str, str]]:`
- **Purpose:** Reads json rows.

**Code:**
```python
def read_json_rows(path: str) -> Iterable[Dict[str, str]]:
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        payload = json.load(handle)

    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                yield item
        return

    if isinstance(payload, dict):
        if "data" in payload and isinstance(payload["data"], list):
            for item in payload["data"]:
                if isinstance(item, dict):
                    yield item
            return
```

**Explanation:** It accepts `path` and returns `Iterable[Dict[str, str]]`. See the code below for the full implementation. Key calls include `open()`, `load()`, `isinstance()`.

### `extract_row_fields`

- **File:** `python_scripts/join_wind_data_betz.py`
- **Lines:** `176-182`
- **Signature:** `def extract_row_fields(row: Dict[str, str]) -> Tuple[str, str, str, str, str]:`
- **Purpose:** Extracts row fields.

**Code:**
```python
def extract_row_fields(row: Dict[str, str]) -> Tuple[str, str, str, str, str]:
    name = normalize_text(row.get("name") or row.get("title") or row.get("product") or row.get("product_name"))
    price = normalize_text(row.get("price") or row.get("price_value") or row.get("sale_price"))
    ratings = normalize_text(row.get("ratings") or row.get("rating"))
    reviews = normalize_text(row.get("reviews") or row.get("review_count"))
    url = normalize_text(row.get("url") or row.get("link") or row.get("product_url"))
    return name, price, ratings, reviews, url
```

**Explanation:** It accepts `row` and returns `Tuple[str, str, str, str, str]`. See the code below for the full implementation. Key calls include `normalize_text()`, `get()`.

### `find_wind_files`

- **File:** `python_scripts/join_wind_data_betz.py`
- **Lines:** `185-195`
- **Signature:** `def find_wind_files(root_dir: str) -> List[str]:`
- **Purpose:** Finds wind files.

**Code:**
```python
def find_wind_files(root_dir: str) -> List[str]:
    paths: List[str] = []
    for root, _dirs, files in os.walk(root_dir):
        for filename in files:
            if not WIND_FILE_PATTERN.search(filename):
                continue
            ext = os.path.splitext(filename)[1].lower()
            if ext not in {".csv", ".json"}:
                continue
            paths.append(os.path.join(root, filename))
    return sorted(paths)
```

**Explanation:** It accepts `root_dir` and returns `List[str]`. See the code below for the full implementation. Key calls include `walk()`, `lower()`, `append()`, `search()`, `join()`.

### `main`

- **File:** `python_scripts/join_wind_data_betz.py`
- **Lines:** `198-299`
- **Signature:** `def main() -> None:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    rows: List[Dict[str, str]] = []
    wind_files = find_wind_files(SCRAPED_DIR)

    for path in wind_files:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".csv":
            source_rows = read_csv_rows(path)
        else:
            source_rows = read_json_rows(path)

        for row in source_rows:
            name, price, ratings, reviews, url = extract_row_fields(row)
            raw_text = " ".join([name, price, ratings, reviews, url])
            power_w = parse_power_w(raw_text)
            diameter_m = parse_diameter_m(raw_text)
            wind_speed = parse_wind_speed_mps(raw_text) or DEFAULT_WIND_SPEED_MPS

            rotor_radius = diameter_m / 2.0 if diameter_m else ""
            power_coeff = ""
            if power_w and diameter_m:
                cp = compute_power_coefficient(
                    power_w,
                    diameter_m,
                    wind_speed,
                    air_density=DEFAULT_AIR_DENSITY,
                    clamp_to_betz=False,
                )
                if cp is not None:
                    power_coeff = cp

            rows.append({
                "source_file": os.path.relpath(path, SCRAPED_DIR).replace("\\", "/"),
                "source_site": detect_source(path),
                "name": name,
                "price": price,
                "ratings": ratings,
                "reviews": reviews,
                "url": url,
                "power_w": f"{power_w:.2f}" if power_w is not None else "",
                "diameter_m": f"{diameter_m:.3f}" if diameter_m is not None else "",
                "rotor_radius_m": f"{rotor_radius:.3f}" if diameter_m is not None else "",
                "wind_speed_mps": f"{wind_speed:.2f}" if wind_speed else "",
                "power_coefficient": f"{power_coeff:.3f}" if isinstance(power_coeff, float) else "",
            })

    fieldnames = [
        "source_file",
        "source_site",
        "name",
        "price",
        "ratings",
        "reviews",
        "url",
        "power_w",
        "diameter_m",
        "rotor_radius_m",
        "wind_speed_mps",
        "power_coefficient",
    ]

    with open(OUT_JOINED, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    rotor_values = [float(r["rotor_radius_m"]) for r in rows if r["rotor_radius_m"]]
    cp_values = [float(r["power_coefficient"]) for r in rows if r["power_coefficient"]]

    avg_rotor = statistics.mean(rotor_values) if rotor_values else 0.0
    avg_cp = statistics.mean(cp_values) if cp_values else 0.0

    with open(OUT_STATS, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "records_total",
            "records_with_rotor_radius",
            "records_with_power_coefficient",
            "avg_rotor_radius_m",
            "avg_power_coefficient",
        ])
        writer.writeheader()
        writer.writerow({
            "records_total": len(rows),
            "records_with_rotor_radius": len(rotor_values),
            "records_with_power_coefficient": len(cp_values),
            "avg_rotor_radius_m": f"{avg_rotor:.3f}",
            "avg_power_coefficient": f"{avg_cp:.3f}",
        })

    print(f"Joined {len(rows)} rows from {len(wind_files)} wind files")
    print(
        "Average rotor radius (m): "
        f"{avg_rotor:.3f} from {len(rotor_values)} rows where a blade diameter was parsed "
        "from text (m/cm/mm/in/ft), then divided by 2."
    )
    print(
        "Average power coefficient: "
        f"{avg_cp:.3f} from {len(cp_values)} rows with both parsed power (W/kW/MW) and diameter; "
        f"uses Cp = P / (0.5 * {DEFAULT_AIR_DENSITY} * A * V^3) with V={DEFAULT_WIND_SPEED_MPS} m/s unless a m/s value is present."
    )
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `makedirs()`, `find_wind_files()`, `lower()`, `read_csv_rows()`, `read_json_rows()`.


## `python_scripts/municipality_climate_analysis.py`

**File:** `python_scripts/municipality_climate_analysis.py`

**Summary:** Source file `python_scripts/municipality_climate_analysis.py`.

### `load_env`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `49-73`
- **Signature:** `def load_env() -> Dict[str, str]:`
- **Purpose:** Load required environment variables.

**Code:**
```python
def load_env() -> Dict[str, str]:
    """Load required environment variables."""
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=repo_root / ".env", override=False)
    print(f"Loaded environment variables from: {repo_root / '.env'}")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = None
    for key_name in (
        "SUPABASE_JWT_SERVICE_ROLE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_JWT_ANON_KEY",
        "SUPABASE_ANON_KEY",
        "SUPABASE_KEY",
    ):
        value = os.getenv(key_name)
        if value:
            supabase_key = value
            break

    if not supabase_url or not supabase_key:
        raise EnvironmentError(
            "Missing SUPABASE_URL or SUPABASE_KEY. Add them to your .env file."
        )

    return {"SUPABASE_URL": supabase_url, "SUPABASE_KEY": supabase_key}
```

**Explanation:** It accepts zero arguments and returns `Dict[str, str]`. See the code below for the full implementation. Key calls include `resolve()`, `Path()`, `load_dotenv()`, `getenv()`, `EnvironmentError()`.

### `is_jwt_key`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `76-77`
- **Signature:** `def is_jwt_key(key: str | None) -> bool:`
- **Purpose:** Handles is jwt key.

**Code:**
```python
def is_jwt_key(key: str | None) -> bool:
    return bool(key) and JWT_PATTERN.match(key) is not None
```

**Explanation:** It accepts `key` and returns `bool`. See the code below for the full implementation. Key calls include `bool()`, `match()`.

### `SupabaseRestQuery.__init__`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `81-85`
- **Signature:** `def __init__(self, client: "SupabaseRestClient", table: str):`
- **Purpose:** Method of `SupabaseRestQuery` that handles   init  .

**Code:**
```python
def __init__(self, client: "SupabaseRestClient", table: str):
        self._client = client
        self._table = table
        self._select = "*"
        self._filters: list[tuple[str, str]] = []
```

**Explanation:** It accepts `client`, `table`. See the code below for the full implementation.

### `SupabaseRestQuery.select`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `87-89`
- **Signature:** `def select(self, columns: str = "*") -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles select.

**Code:**
```python
def select(self, columns: str = "*") -> "SupabaseRestQuery":
        self._select = columns
        return self
```

**Explanation:** It accepts `columns` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.range`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `91-93`
- **Signature:** `def range(self, start: int, end: int) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles range.

**Code:**
```python
def range(self, start: int, end: int) -> "SupabaseRestQuery":
        self._range = (start, end)
        return self
```

**Explanation:** It accepts `start`, `end` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.execute`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `95-104`
- **Signature:** `def execute(self):`
- **Purpose:** Method of `SupabaseRestQuery` that handles execute.

**Code:**
```python
def execute(self):
        params: dict[str, str] = {"select": self._select}
        headers = dict(self._client.headers)
        if hasattr(self, "_range"):
            start, end = self._range
            headers["Range"] = f"{start}-{end}"
        url = f"{self._client.base_url}/rest/v1/{self._table}"
        response = self._client.http.get(url, params=params, headers=headers)
        response.raise_for_status()
        return type("Resp", (), {"data": response.json()})
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `dict()`, `hasattr()`, `get()`, `raise_for_status()`, `type()`.

### `SupabaseRestClient.__init__`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `108-114`
- **Signature:** `def __init__(self, base_url: str, api_key: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles   init  .

**Code:**
```python
def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
        }
        self.http = httpx.Client(timeout=10.0)
```

**Explanation:** It accepts `base_url`, `api_key`. See the code below for the full implementation. Key calls include `rstrip()`, `Client()`.

### `SupabaseRestClient.table`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `116-117`
- **Signature:** `def table(self, table_name: str) -> SupabaseRestQuery:`
- **Purpose:** Method of `SupabaseRestClient` that handles table.

**Code:**
```python
def table(self, table_name: str) -> SupabaseRestQuery:
        return SupabaseRestQuery(self, table_name)
```

**Explanation:** It accepts `table_name` and returns `SupabaseRestQuery`. See the code below for the full implementation. Key calls include `SupabaseRestQuery()`.

### `get_supabase_client`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `123-131`
- **Signature:** `def get_supabase_client() -> Client:`
- **Purpose:** Initialize and return a Supabase client.

**Code:**
```python
def get_supabase_client() -> Client:
    """Initialize and return a Supabase client."""
    env = load_env()
    if is_jwt_key(env["SUPABASE_KEY"]):
        try:
            return create_client(env["SUPABASE_URL"], env["SUPABASE_KEY"])
        except Exception:
            return SupabaseRestClient(env["SUPABASE_URL"], env["SUPABASE_KEY"])
    return SupabaseRestClient(env["SUPABASE_URL"], env["SUPABASE_KEY"])
```

**Explanation:** It accepts zero arguments and returns `Client`. See the code below for the full implementation. Key calls include `load_env()`, `is_jwt_key()`, `create_client()`, `SupabaseRestClient()`.

### `fetch_all_rows`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `137-170`
- **Signature:** `def fetch_all_rows(supabase: Client, table_name: str) -> List[Dict[str, Any]]:`
- **Purpose:** Fetch all rows from a Supabase table using pagination.

**Code:**
```python
def fetch_all_rows(supabase: Client, table_name: str) -> List[Dict[str, Any]]:
    """Fetch all rows from a Supabase table using pagination."""
    all_rows: List[Dict[str, Any]] = []
    start = 0

    while True:
        end = start + PAGE_SIZE - 1
        try:
            response = (
                supabase
                .table(table_name)
                .select("*")
                .range(start, end)
                .execute()
            )
        except Exception as exc:
            raise RuntimeError(f"Supabase API request failed: {exc}") from exc

        data = response.data if response and response.data else []

        if not data:
            break

        all_rows.extend(data)
        start += PAGE_SIZE

        # Safety guard against unexpected pagination issues
        if start > 10_000_000:
            raise RuntimeError("Pagination exceeded safe limit. Check table size or API response.")

    if not all_rows:
        raise ValueError("No data returned from Supabase. Check table name and credentials.")

    return all_rows
```

**Explanation:** It accepts `supabase`, `table_name` and returns `List[Dict[str, Any]]`. See the code below for the full implementation. Key calls include `extend()`, `execute()`, `RuntimeError()`, `range()`, `select()`.

### `validate_dataframe`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `176-183`
- **Signature:** `def validate_dataframe(df: pd.DataFrame) -> None:`
- **Purpose:** Basic validation checks for expected columns and non-empty data.

**Code:**
```python
def validate_dataframe(df: pd.DataFrame) -> None:
    """Basic validation checks for expected columns and non-empty data."""
    if df.empty:
        raise ValueError("DataFrame is empty. No data to analyze.")

    missing_cols = [col for col in NASA_POWER_COLUMNS + ["municipality_id"] if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing expected columns: {missing_cols}")
```

**Explanation:** It accepts `df` and returns `None`. See the code below for the full implementation. Key calls include `ValueError()`.

### `summarize_missing_values`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `189-196`
- **Signature:** `def summarize_missing_values(df: pd.DataFrame) -> pd.DataFrame:`
- **Purpose:** Return a summary of missing values by column.

**Code:**
```python
def summarize_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Return a summary of missing values by column."""
    missing_counts = df.isna().sum().sort_values(ascending=False)
    missing_percent = (missing_counts / len(df) * 100).round(2)
    return pd.DataFrame({
        "missing_count": missing_counts,
        "missing_percent": missing_percent
    })
```

**Explanation:** It accepts `df` and returns `pd.DataFrame`. See the code below for the full implementation. Key calls include `sort_values()`, `sum()`, `isna()`, `round()`, `len()`.

### `descriptive_statistics`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `199-201`
- **Signature:** `def descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:`
- **Purpose:** Return descriptive statistics for numeric NASA POWER columns.

**Code:**
```python
def descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics for numeric NASA POWER columns."""
    return df[NASA_POWER_COLUMNS].describe().T
```

**Explanation:** It accepts `df` and returns `pd.DataFrame`. See the code below for the full implementation. Key calls include `describe()`.

### `plot_histogram`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `207-215`
- **Signature:** `def plot_histogram(df: pd.DataFrame, column: str) -> None:`
- **Purpose:** Plot a histogram for a single column.

**Code:**
```python
def plot_histogram(df: pd.DataFrame, column: str) -> None:
    """Plot a histogram for a single column."""
    plt.figure(figsize=(8, 4))
    plt.hist(df[column].dropna(), bins=30, color="#2E86AB", alpha=0.85)
    plt.title(f"Distribution of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()
```

**Explanation:** It accepts `df`, `column` and returns `None`. See the code below for the full implementation. Key calls include `figure()`, `hist()`, `dropna()`, `title()`, `xlabel()`.

### `plot_boxplot`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `218-225`
- **Signature:** `def plot_boxplot(df: pd.DataFrame, column: str) -> None:`
- **Purpose:** Plot a boxplot for a single column.

**Code:**
```python
def plot_boxplot(df: pd.DataFrame, column: str) -> None:
    """Plot a boxplot for a single column."""
    plt.figure(figsize=(6, 4))
    plt.boxplot(df[column].dropna(), vert=True)
    plt.title(f"Boxplot of {column}")
    plt.ylabel(column)
    plt.tight_layout()
    plt.show()
```

**Explanation:** It accepts `df`, `column` and returns `None`. See the code below for the full implementation. Key calls include `figure()`, `boxplot()`, `dropna()`, `title()`, `ylabel()`.

### `plot_correlation_heatmap`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `228-238`
- **Signature:** `def plot_correlation_heatmap(df: pd.DataFrame) -> None:`
- **Purpose:** Plot a correlation heatmap using matplotlib.

**Code:**
```python
def plot_correlation_heatmap(df: pd.DataFrame) -> None:
    """Plot a correlation heatmap using matplotlib."""
    corr = df[NASA_POWER_COLUMNS].corr()
    plt.figure(figsize=(10, 8))
    plt.imshow(corr, cmap="coolwarm", interpolation="nearest")
    plt.colorbar()
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=45, ha="right")
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.title("Correlation Heatmap: NASA POWER Parameters")
    plt.tight_layout()
    plt.show()
```

**Explanation:** It accepts `df` and returns `None`. See the code below for the full implementation. Key calls include `corr()`, `figure()`, `imshow()`, `colorbar()`, `xticks()`.

### `plot_municipality_distribution`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `241-253`
- **Signature:** `def plot_municipality_distribution(df: pd.DataFrame, column: str, sample_size: int = 10) -> None:`
- **Purpose:** Plot a distribution of values for a subset of municipalities.

**Code:**
```python
def plot_municipality_distribution(df: pd.DataFrame, column: str, sample_size: int = 10) -> None:
    """Plot a distribution of values for a subset of municipalities."""
    sample_ids = df["municipality_id"].dropna().unique()[:sample_size]
    plt.figure(figsize=(10, 5))
    for municipality_id in sample_ids:
        subset = df[df["municipality_id"] == municipality_id][column].dropna()
        plt.plot(subset.values, label=f"{municipality_id}")
    plt.title(f"{column} Distribution (Sample Municipalities)")
    plt.xlabel("Record Index")
    plt.ylabel(column)
    plt.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    plt.show()
```

**Explanation:** It accepts `df`, `column`, `sample_size` and returns `None`. See the code below for the full implementation. Key calls include `unique()`, `dropna()`, `figure()`, `plot()`, `title()`.

### `compute_all_time_averages`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `259-292`
- **Signature:** `def compute_all_time_averages(df: pd.DataFrame) -> pd.DataFrame:`
- **Purpose:** Compute all-time averages per municipality for NASA POWER parameters.

**Code:**
```python
def compute_all_time_averages(df: pd.DataFrame) -> pd.DataFrame:
    """Compute all-time averages per municipality for NASA POWER parameters."""
    if ELEVATION_COLUMN not in df.columns:
        df[ELEVATION_COLUMN] = pd.NA

    avg_df = (
        df.groupby("municipality_id")[NASA_POWER_COLUMNS]
        .mean(numeric_only=True)
        .reset_index()
    )

    elevation_df = (
        df[["municipality_id", ELEVATION_COLUMN]]
        .dropna(subset=[ELEVATION_COLUMN])
        .drop_duplicates(subset=["municipality_id"])
        .rename(columns={ELEVATION_COLUMN: "elevation"})
    )

    merged = avg_df.merge(elevation_df, on="municipality_id", how="left")
    if "elevation" not in merged.columns:
        merged["elevation"] = pd.NA

    return merged.rename(columns={
        "t2m": "avg_t2m",
        "t2m_max": "avg_t2m_max",
        "t2m_min": "avg_t2m_min",
        "rh2m": "avg_rh2m",
        "rhoa": "avg_rhoa",
        "prectotcorr": "avg_prectotcorr",
        "ws10m": "avg_ws10m",
        "allsky_sfc_sw_dwn": "avg_allsky_sfc_sw_dwn",
        "cloud_amt": "avg_cloud_amt",
        "surface_pressure": "avg_surface_pressure",
    })
```

**Explanation:** It accepts `df` and returns `pd.DataFrame`. See the code below for the full implementation. Key calls include `reset_index()`, `mean()`, `groupby()`, `rename()`, `drop_duplicates()`.

### `main`

- **File:** `python_scripts/municipality_climate_analysis.py`
- **Lines:** `323-359`
- **Signature:** `def main() -> None:`
- **Purpose:** Main execution flow.

**Code:**
```python
def main() -> None:
    """Main execution flow."""
    try:
        supabase = get_supabase_client()
        rows = fetch_all_rows(supabase, TABLE_NAME)
    except Exception as exc:
        print(f"Error loading data: {exc}")
        sys.exit(1)

    # Convert to DataFrame
    df = pd.DataFrame(rows)

    # Data validation
    try:
        validate_dataframe(df)
    except Exception as exc:
        print(f"Validation error: {exc}")
        sys.exit(1)

    # Basic EDA
    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print("\nMissing Values:\n", summarize_missing_values(df).head(15))
    print("\nDescriptive Statistics:\n", descriptive_statistics(df).head(15))

    # Visualization examples
    plot_histogram(df, "t2m")
    plot_boxplot(df, "t2m")
    plot_correlation_heatmap(df)
    plot_municipality_distribution(df, "t2m")

    # Compute all-time averages
    avg_df = compute_all_time_averages(df)

    # Save output
    avg_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved averages to {OUTPUT_CSV}")
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `get_supabase_client()`, `fetch_all_rows()`, `exit()`, `DataFrame()`, `validate_dataframe()`.


## `python_scripts/prepare_national_energy_csv.py`

**File:** `python_scripts/prepare_national_energy_csv.py`

**Summary:** prepare_national_energy_csv.py

### `read_wide_csv`

- **File:** `python_scripts/prepare_national_energy_csv.py`
- **Lines:** `20-40`
- **Signature:** `def read_wide_csv(filename: str) -> dict:`
- **Purpose:** Read a DOE CSV where rows=categories and columns=years.

**Code:**
```python
def read_wide_csv(filename: str) -> dict:
    """Read a DOE CSV where rows=categories and columns=years.
    Returns {category: {year: value}}"""
    filepath = INPUT_DIR / filename
    result = {}
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        years = [int(h) for h in header[1:]]
        for row in reader:
            if not row or all(cell.strip() == "" for cell in row):
                continue
            category = row[0].strip()
            result[category] = {}
            for year_str, val_str in zip(years, row[1:]):
                val_str = val_str.strip()
                if val_str == "":
                    result[category][year_str] = None
                else:
                    result[category][year_str] = float(val_str)
    return result
```

**Explanation:** It accepts `filename` and returns `dict`. See the code below for the full implementation. Key calls include `open()`, `reader()`, `next()`, `int()`, `strip()`.

### `safe_get`

- **File:** `python_scripts/prepare_national_energy_csv.py`
- **Lines:** `43-46`
- **Signature:** `def safe_get(data: dict, category: str, year: int) -> float | None:`
- **Purpose:** Safely retrieve a value from the nested dict.

**Code:**
```python
def safe_get(data: dict, category: str, year: int) -> float | None:
    """Safely retrieve a value from the nested dict."""
    cat_data = data.get(category, {})
    return cat_data.get(year)
```

**Explanation:** It accepts `data`, `category`, `year` and returns `float | None`. See the code below for the full implementation. Key calls include `get()`.

### `build_energy_table`

- **File:** `python_scripts/prepare_national_energy_csv.py`
- **Lines:** `49-112`
- **Signature:** `def build_energy_table() -> list[dict]:`
- **Purpose:** Builds energy table.

**Code:**
```python
def build_energy_table() -> list[dict]:
    years = list(range(2003, 2025))

    # Read all 6 source files
    cons = read_wide_csv("electricity_consumption_by_sector_GWh.csv")
    peak = read_wide_csv("system_peak_demand_MW.csv")
    gen_grid = read_wide_csv("gross_power_generation_by_grid_GWh.csv")
    gen_plant = read_wide_csv("gross_power_generation_by_plant_type_GWh.csv")
    cap = read_wide_csv("installed_capacity_by_plant_type_MW.csv")
    dep = read_wide_csv("dependable_capacity_by_plant_type_MW.csv")

    records = []
    for year in years:
        row: dict[str, float | int | None] = {"year": year}

        # ---- Consumption ----
        row["total_consumption_gwh"] = safe_get(cons, "Total Electricity Consumption", year)
        row["residential_consumption_gwh"] = safe_get(cons, "Residential", year)
        row["commercial_consumption_gwh"] = safe_get(cons, "Commercial", year)
        row["industrial_consumption_gwh"] = safe_get(cons, "Industrial", year)
        row["others_consumption_gwh"] = safe_get(cons, "Others", year)
        row["electricity_sales_gwh"] = safe_get(cons, "Electricity Sales", year)
        row["utilities_own_use_gwh"] = safe_get(cons, "Utilities Own Use", year)
        row["system_losses_gwh"] = safe_get(cons, "System Losses", year)

        # ---- Peak Demand ----
        row["luzon_peak_demand_mw"] = safe_get(peak, "Luzon", year)
        row["visayas_peak_demand_mw"] = safe_get(peak, "Visayas", year)
        row["mindanao_peak_demand_mw"] = safe_get(peak, "Mindanao", year)
        row["total_peak_demand_mw"] = safe_get(peak, "Total Non-Coincident Peak Demand", year)

        # ---- Generation by Grid ----
        row["luzon_generation_gwh"] = safe_get(gen_grid, "Luzon", year)
        row["visayas_generation_gwh"] = safe_get(gen_grid, "Visayas", year)
        row["mindanao_generation_gwh"] = safe_get(gen_grid, "Mindanao", year)

        # ---- Generation by Plant Type ----
        row["coal_generation_gwh"] = safe_get(gen_plant, "Coal", year)
        row["natural_gas_generation_gwh"] = safe_get(gen_plant, "Natural Gas", year)
        row["renewable_generation_gwh"] = safe_get(gen_plant, "Renewable Energy (RE)", year)
        row["geothermal_generation_gwh"] = safe_get(gen_plant, "Geothermal", year)
        row["hydro_generation_gwh"] = safe_get(gen_plant, "Hydro", year)
        row["biomass_generation_gwh"] = safe_get(gen_plant, "Biomass", year)
        row["solar_generation_gwh"] = safe_get(gen_plant, "Solar", year)
        row["wind_generation_gwh"] = safe_get(gen_plant, "Wind", year)

        # Oil-based = Oil-Based + Combined Cycle + Diesel + Gas Turbine + Oil Thermal
        oil_subs = ["Oil-Based", "Combined Cycle", "Diesel", "Gas Turbine", "Oil Thermal"]
        oil_sum = 0.0
        has_oil = False
        for sub in oil_subs:
            v = safe_get(gen_plant, sub, year)
            if v is not None:
                oil_sum += v
                has_oil = True
        row["oil_based_generation_gwh"] = round(oil_sum, 2) if has_oil else None

        # ---- Capacity ----
        row["total_installed_capacity_mw"] = safe_get(cap, "Total Installed Capacity", year)
        row["total_dependable_capacity_mw"] = safe_get(dep, "Total Dependable Capacity", year)

        records.append(row)

    return records
```

**Explanation:** It accepts zero arguments and returns `list[dict]`. See the code below for the full implementation. Key calls include `list()`, `range()`, `read_wide_csv()`, `safe_get()`, `append()`.

### `validate_data`

- **File:** `python_scripts/prepare_national_energy_csv.py`
- **Lines:** `115-194`
- **Signature:** `def validate_data(records: list[dict]) -> None:`
- **Purpose:** Run sanity checks on the combined dataset.

**Code:**
```python
def validate_data(records: list[dict]) -> None:
    """Run sanity checks on the combined dataset."""
    print("\n=== DATA VALIDATION ===")

    # Check all years present
    expected_years = set(range(2003, 2025))
    found_years = {r["year"] for r in records}
    missing = expected_years - found_years
    if missing:
        print(f"  [WARN] Missing years: {sorted(missing)}")
    else:
        print("  [OK] All 22 years (2003-2024) present")

    # Check total consumption = sales + own_use + losses
    mismatches = 0
    for r in records:
        total = r["total_consumption_gwh"] or 0
        sales = r["electricity_sales_gwh"] or 0
        own_use = r["utilities_own_use_gwh"] or 0
        losses = r["system_losses_gwh"] or 0
        diff = abs(total - (sales + own_use + losses))
        if diff > 1:
            mismatches += 1
            if mismatches <= 3:
                print(f"  [WARN] {r['year']}: total={total:.2f} vs computed={sales+own_use+losses:.2f} (diff={diff:.2f})")
    if mismatches == 0:
        print("  [OK] total_consumption_gwh == sales + own_use + losses")
    else:
        print(f"  [WARN] {mismatches} years with consumption mismatch")

    # Check peak demand = Luzon + Visayas + Mindanao
    mismatches = 0
    for r in records:
        total = r["total_peak_demand_mw"] or 0
        luzon = r["luzon_peak_demand_mw"] or 0
        vis = r["visayas_peak_demand_mw"] or 0
        mind = r["mindanao_peak_demand_mw"] or 0
        diff = abs(total - (luzon + vis + mind))
        if diff > 1:
            mismatches += 1
            if mismatches <= 3:
                print(f"  [WARN] {r['year']}: total_peak={total:.2f} vs computed={luzon+vis+mind:.2f}")
    if mismatches == 0:
        print("  [OK] total_peak_demand_mw == Luzon + Visayas + Mindanao")
    else:
        print(f"  [WARN] {mismatches} years with peak demand mismatch")

    # Check generation: coal + oil + gas + RE  vs grid total
    mismatches = 0
    for r in records:
        coal = r["coal_generation_gwh"] or 0
        oil = r["oil_based_generation_gwh"] or 0
        gas = r["natural_gas_generation_gwh"] or 0
        re = r["renewable_generation_gwh"] or 0
        plant_total = coal + oil + gas + re

        luzon = r["luzon_generation_gwh"] or 0
        vis = r["visayas_generation_gwh"] or 0
        mind = r["mindanao_generation_gwh"] or 0
        grid_total = luzon + vis + mind

        diff = abs(grid_total - plant_total)
        if diff > 1:
            mismatches += 1
            if mismatches <= 3:
                print(f"  [WARN] {r['year']}: grid_sum={grid_total:.2f} vs plant_sum={plant_total:.2f}")
    if mismatches == 0:
        print("  [OK] Grid generation totals match plant type sums")
    else:
        print(f"  [WARN] {mismatches} years with generation mismatch")

    # Null counts
    print("\n  [INFO] Null value counts per column:")
    all_cols = list(records[0].keys())
    for col in all_cols:
        nulls = sum(1 for r in records if r[col] is None)
        if nulls > 0:
            print(f"      {col}: {nulls} nulls")

    print("\n=== END VALIDATION ===\n")
```

**Explanation:** It accepts `records` and returns `None`. See the code below for the full implementation. Key calls include `set()`, `range()`, `sorted()`, `abs()`, `list()`.

### `write_csv`

- **File:** `python_scripts/prepare_national_energy_csv.py`
- **Lines:** `197-243`
- **Signature:** `def write_csv(records: list[dict]) -> None:`
- **Purpose:** Write records to CSV matching the Supabase schema column order.

**Code:**
```python
def write_csv(records: list[dict]) -> None:
    """Write records to CSV matching the Supabase schema column order."""
    col_order = [
        "year",
        "total_consumption_gwh",
        "residential_consumption_gwh",
        "commercial_consumption_gwh",
        "industrial_consumption_gwh",
        "others_consumption_gwh",
        "electricity_sales_gwh",
        "utilities_own_use_gwh",
        "system_losses_gwh",
        "luzon_peak_demand_mw",
        "visayas_peak_demand_mw",
        "mindanao_peak_demand_mw",
        "total_peak_demand_mw",
        "luzon_generation_gwh",
        "visayas_generation_gwh",
        "mindanao_generation_gwh",
        "coal_generation_gwh",
        "oil_based_generation_gwh",
        "natural_gas_generation_gwh",
        "renewable_generation_gwh",
        "geothermal_generation_gwh",
        "hydro_generation_gwh",
        "biomass_generation_gwh",
        "solar_generation_gwh",
        "wind_generation_gwh",
        "total_installed_capacity_mw",
        "total_dependable_capacity_mw",
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=col_order)
        writer.writeheader()
        for row in records:
            # Round floats to 2 decimals, leave None as empty string
            clean_row = {}
            for col in col_order:
                val = row.get(col)
                if val is None:
                    clean_row[col] = ""
                elif isinstance(val, float):
                    clean_row[col] = f"{val:.2f}"
                else:
                    clean_row[col] = val
            writer.writerow(clean_row)
```

**Explanation:** It accepts `records` and returns `None`. See the code below for the full implementation. Key calls include `open()`, `DictWriter()`, `writeheader()`, `writerow()`, `get()`.

### `print_preview`

- **File:** `python_scripts/prepare_national_energy_csv.py`
- **Lines:** `246-258`
- **Signature:** `def print_preview(records: list[dict], n: int = 5) -> None:`
- **Purpose:** Print first and last n rows in a readable format.

**Code:**
```python
def print_preview(records: list[dict], n: int = 5) -> None:
    """Print first and last n rows in a readable format."""
    col_order = list(records[0].keys())

    def fmt_row(r):
        return " | ".join(f"{c}={r[c] if r[c] is not None else 'NULL':>12}" for c in col_order)

    print(f"\nPreview (first {n} rows):")
    for r in records[:n]:
        print("  " + fmt_row(r))
    print(f"\nPreview (last {n} rows):")
    for r in records[-n:]:
        print("  " + fmt_row(r))
```

**Explanation:** It accepts `records`, `n` and returns `None`. See the code below for the full implementation. Key calls include `list()`, `keys()`, `join()`, `fmt_row()`.

### `main`

- **File:** `python_scripts/prepare_national_energy_csv.py`
- **Lines:** `261-270`
- **Signature:** `def main():`
- **Purpose:** Handles main.

**Code:**
```python
def main():
    print("Building national_energy_annual dataset from DOE CSVs...")

    records = build_energy_table()
    validate_data(records)
    write_csv(records)

    print(f"Saved to: {OUTPUT_FILE}")
    print(f"Shape: {len(records)} rows x {len(records[0])} columns")
    print_preview(records)
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `build_energy_table()`, `validate_data()`, `write_csv()`, `len()`, `print_preview()`.


## `python_scripts/prepare_rag_products.py`

**File:** `python_scripts/prepare_rag_products.py`

**Summary:** Source file `python_scripts/prepare_rag_products.py`.

### `setup_logging`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `73-77`
- **Signature:** `def setup_logging(level: str) -> None:`
- **Purpose:** Sets up logging.

**Code:**
```python
def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(levelname)s | %(message)s",
    )
```

**Explanation:** It accepts `level` and returns `None`. See the code below for the full implementation. Key calls include `basicConfig()`, `getattr()`, `upper()`.

### `normalize_text`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `80-87`
- **Signature:** `def normalize_text(text: str) -> str:`
- **Purpose:** Normalizes text.

**Code:**
```python
def normalize_text(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", " ", text)
    cleaned = re.sub(r"&[a-zA-Z]+;", " ", cleaned)
    cleaned = re.sub(r"[\r\n\t]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
```

**Explanation:** It accepts `text` and returns `str`. See the code below for the full implementation. Key calls include `sub()`, `strip()`.

### `normalize_for_match`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `90-96`
- **Signature:** `def normalize_for_match(text: str) -> str:`
- **Purpose:** Normalizes for match.

**Code:**
```python
def normalize_for_match(text: str) -> str:
    if not text:
        return ""
    cleaned = normalize_text(text).lower()
    cleaned = re.sub(r"[^a-z0-9\s\-\.\+/]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
```

**Explanation:** It accepts `text` and returns `str`. See the code below for the full implementation. Key calls include `lower()`, `normalize_text()`, `sub()`, `strip()`.

### `normalize_name`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `99-104`
- **Signature:** `def normalize_name(name: str) -> str:`
- **Purpose:** Normalizes name.

**Code:**
```python
def normalize_name(name: str) -> str:
    if not name:
        return ""
    cleaned = normalize_for_match(name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
```

**Explanation:** It accepts `name` and returns `str`. See the code below for the full implementation. Key calls include `normalize_for_match()`, `strip()`, `sub()`.

### `coerce_price`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `107-121`
- **Signature:** `def coerce_price(value: str) -> Optional[float]:`
- **Purpose:** Handles coerce price.

**Code:**
```python
def coerce_price(value: str) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).strip()
    if cleaned == "":
        return None
    cleaned = re.sub(r"[^0-9\.]+", "", cleaned)
    if cleaned == "":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None
```

**Explanation:** It accepts `value` and returns `Optional[float]`. See the code below for the full implementation. Key calls include `isinstance()`, `float()`, `strip()`, `str()`, `sub()`.

### `enrich_category`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `124-130`
- **Signature:** `def enrich_category(name_normalized: str, category: str) -> str:`
- **Purpose:** Handles enrich category.

**Code:**
```python
def enrich_category(name_normalized: str, category: str) -> str:
    if category:
        return category
    for renewable, keywords in RENEWABLE_KEYWORDS.items():
        if any(keyword in name_normalized for keyword in keywords):
            return renewable
    return ""
```

**Explanation:** It accepts `name_normalized`, `category` and returns `str`. See the code below for the full implementation. Key calls include `items()`, `any()`.

### `infer_product_type`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `133-137`
- **Signature:** `def infer_product_type(name_normalized: str) -> str:`
- **Purpose:** Handles infer product type.

**Code:**
```python
def infer_product_type(name_normalized: str) -> str:
    for product_type, keywords in PRODUCT_TYPE_KEYWORDS.items():
        if any(keyword in name_normalized for keyword in keywords):
            return product_type
    return ""
```

**Explanation:** It accepts `name_normalized` and returns `str`. See the code below for the full implementation. Key calls include `items()`, `any()`.

### `tokenize`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `140-141`
- **Signature:** `def tokenize(text: str) -> List[str]:`
- **Purpose:** Handles tokenize.

**Code:**
```python
def tokenize(text: str) -> List[str]:
    return [token for token in re.split(r"\W+", text) if token]
```

**Explanation:** It accepts `text` and returns `List[str]`. See the code below for the full implementation. Key calls include `split()`.

### `token_set_similarity`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `144-151`
- **Signature:** `def token_set_similarity(a: str, b: str) -> float:`
- **Purpose:** Handles token set similarity.

**Code:**
```python
def token_set_similarity(a: str, b: str) -> float:
    tokens_a = set(tokenize(a))
    tokens_b = set(tokenize(b))
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a.intersection(tokens_b)
    union = tokens_a.union(tokens_b)
    return len(intersection) / max(len(union), 1)
```

**Explanation:** It accepts `a`, `b` and returns `float`. See the code below for the full implementation. Key calls include `set()`, `tokenize()`, `intersection()`, `union()`, `len()`.

### `build_document`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `154-164`
- **Signature:** `def build_document(row: Dict[str, str]) -> str:`
- **Purpose:** Builds document.

**Code:**
```python
def build_document(row: Dict[str, str]) -> str:
    return (
        f"{row['product_name']}. "
        f"Category: {row.get('category', '')}/{row.get('subcategory', '')}. "
        f"Renewable: {row.get('renewable_type', '')}. "
        f"Type: {row.get('product_type', '')}. "
        f"Price: {row.get('currency', '')} {row.get('price_value', '')}. "
        f"Source: {row.get('source', '')}. "
        f"Ratings: {row.get('ratings', '')} ({row.get('reviews', '')} reviews). "
        f"URL: {row.get('url', '')}."
    ).strip()
```

**Explanation:** It accepts `row` and returns `str`. See the code below for the full implementation. Key calls include `strip()`, `get()`.

### `sentence_split`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `167-171`
- **Signature:** `def sentence_split(text: str) -> List[str]:`
- **Purpose:** Handles sentence split.

**Code:**
```python
def sentence_split(text: str) -> List[str]:
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [part.strip() for part in parts if part.strip()]
```

**Explanation:** It accepts `text` and returns `List[str]`. See the code below for the full implementation. Key calls include `split()`, `strip()`.

### `chunk_document`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `174-198`
- **Signature:** `def chunk_document(text: str, max_words: int, overlap_ratio: float) -> List[str]:`
- **Purpose:** Handles chunk document.

**Code:**
```python
def chunk_document(text: str, max_words: int, overlap_ratio: float) -> List[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]

    sentences = sentence_split(text)
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0
    target_overlap = int(max_words * overlap_ratio)

    for sentence in sentences:
        sentence_words = sentence.split()
        if current_len + len(sentence_words) > max_words and current:
            chunks.append(" ".join(current))
            overlap = current[-target_overlap:] if target_overlap > 0 else []
            current = overlap + sentence_words
            current_len = len(current)
        else:
            current.extend(sentence_words)
            current_len += len(sentence_words)

    if current:
        chunks.append(" ".join(current))
    return chunks
```

**Explanation:** It accepts `text`, `max_words`, `overlap_ratio` and returns `List[str]`. See the code below for the full implementation. Key calls include `split()`, `len()`, `sentence_split()`, `int()`, `append()`.

### `completeness_score`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `201-202`
- **Signature:** `def completeness_score(row: Dict[str, str]) -> int:`
- **Purpose:** Handles completeness score.

**Code:**
```python
def completeness_score(row: Dict[str, str]) -> int:
    return sum(1 for value in row.values() if value not in ("", None))
```

**Explanation:** It accepts `row` and returns `int`. See the code below for the full implementation. Key calls include `sum()`, `values()`.

### `exact_dedupe`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `205-217`
- **Signature:** `def exact_dedupe(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:`
- **Purpose:** Handles exact dedupe.

**Code:**
```python
def exact_dedupe(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    best_by_key: Dict[str, Dict[str, str]] = {}
    for row in rows:
        key = "|".join([
            row.get("product_name_normalized", ""),
            str(row.get("price_value", "")),
            row.get("source", ""),
            row.get("url", ""),
        ])
        existing = best_by_key.get(key)
        if not existing or completeness_score(row) > completeness_score(existing):
            best_by_key[key] = row
    return list(best_by_key.values())
```

**Explanation:** It accepts `rows` and returns `List[Dict[str, str]]`. See the code below for the full implementation. Key calls include `join()`, `get()`, `str()`, `completeness_score()`, `list()`.

### `near_dedupe`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `220-241`
- **Signature:** `def near_dedupe(rows: List[Dict[str, str]], threshold: float) -> List[Dict[str, str]]:`
- **Purpose:** Handles near dedupe.

**Code:**
```python
def near_dedupe(rows: List[Dict[str, str]], threshold: float) -> List[Dict[str, str]]:
    kept: List[Dict[str, str]] = []
    for row in rows:
        name_norm = row.get("product_name_normalized", "")
        price = row.get("price_value", "")
        source = row.get("source", "")
        is_duplicate = False
        for existing in kept:
            if existing.get("source") != source:
                continue
            if existing.get("price_value") != price:
                continue
            similarity = token_set_similarity(name_norm, existing.get("product_name_normalized", ""))
            if similarity >= threshold:
                if completeness_score(row) > completeness_score(existing):
                    kept.remove(existing)
                    kept.append(row)
                is_duplicate = True
                break
        if not is_duplicate:
            kept.append(row)
    return kept
```

**Explanation:** It accepts `rows`, `threshold` and returns `List[Dict[str, str]]`. See the code below for the full implementation. Key calls include `get()`, `token_set_similarity()`, `append()`, `completeness_score()`, `remove()`.

### `flatten_metadata`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `244-260`
- **Signature:** `def flatten_metadata(row: Dict[str, str]) -> Dict[str, object]:`
- **Purpose:** Handles flatten metadata.

**Code:**
```python
def flatten_metadata(row: Dict[str, str]) -> Dict[str, object]:
    metadata = {
        "category": row.get("category", ""),
        "subcategory": row.get("subcategory", ""),
        "renewable_type": row.get("renewable_type", ""),
        "product_type": row.get("product_type", ""),
        "price_value": row.get("price_value"),
        "currency": row.get("currency", ""),
        "source": row.get("source", ""),
        "seller": row.get("seller", ""),
        "location": row.get("location", ""),
        "ratings": row.get("ratings", ""),
        "reviews": row.get("reviews", ""),
        "url": row.get("url", ""),
        "source_file": row.get("source_file", ""),
    }
    return metadata
```

**Explanation:** It accepts `row` and returns `Dict[str, object]`. See the code below for the full implementation. Key calls include `get()`.

### `load_dataset`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `263-270`
- **Signature:** `def load_dataset(path: Path) -> pd.DataFrame:`
- **Purpose:** Loads dataset.

**Code:**
```python
def load_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    df = df.rename(columns={column: column.strip().lower() for column in df.columns})
    df = df.rename(columns={key: value for key, value in COLUMN_MAP.items() if key in df.columns})
    for column in CANONICAL_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df
```

**Explanation:** It accepts `path` and returns `pd.DataFrame`. See the code below for the full implementation. Key calls include `read_csv()`, `rename()`, `lower()`, `strip()`, `items()`.

### `process_rows`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `273-325`
- **Signature:** `def process_rows(`
- **Purpose:** Processes rows.

**Code:**
```python
def process_rows(
    df: pd.DataFrame,
    max_words: int,
    overlap_ratio: float,
    near_dedupe_threshold: float,
) -> Tuple[List[Dict[str, str]], Dict[str, int], int]:
    drop_counts = {reason: 0 for reason in DROP_REASONS}
    rows: List[Dict[str, str]] = []
    chunked_count = 0

    for _, record in df.iterrows():
        row = {key: ("" if pd.isna(value) else str(value).strip()) for key, value in record.items()}
        row["product_name"] = normalize_text(row.get("product_name", ""))
        row["product_name_normalized"] = normalize_name(row.get("product_name", ""))
        row["description"] = normalize_text(row.get("description", ""))

        if not row["product_name"]:
            drop_counts["missing_name"] += 1
            continue
        if len(row["product_name_normalized"]) < 4:
            drop_counts["short_name"] += 1
            continue

        row["price_value"] = coerce_price(row.get("price_value", ""))
        if row["price_value"] is None:
            drop_counts["invalid_price"] += 1
            continue

        row["currency"] = row.get("currency", "") or "PHP"
        row["category"] = enrich_category(row["product_name_normalized"], row.get("category", ""))
        row["subcategory"] = row.get("subcategory", "")
        row["renewable_type"] = row["category"]
        row["product_type"] = infer_product_type(row["product_name_normalized"])

        if not row["category"]:
            drop_counts["missing_category"] += 1
            continue

        row["document_text"] = build_document(row)
        row["summary"] = row["document_text"].split(".")[0].strip() + "."

        chunks = chunk_document(row["document_text"], max_words, overlap_ratio)
        if len(chunks) > 1:
            chunked_count += 1

        row["chunks"] = chunks
        rows.append(row)

    exact = exact_dedupe(rows)
    near = near_dedupe(exact, near_dedupe_threshold)
    deduped_count = len(rows) - len(near)

    return near, drop_counts, chunked_count
```

**Explanation:** It accepts `df`, `max_words`, `overlap_ratio`, `near_dedupe_threshold` and returns `Tuple[List[Dict[str, str]], Dict[str, int], int]`. See the code below for the full implementation. Key calls include `iterrows()`, `normalize_text()`, `normalize_name()`, `coerce_price()`, `enrich_category()`.

### `export_files`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `328-368`
- **Signature:** `def export_files(`
- **Purpose:** Handles export files.

**Code:**
```python
def export_files(
    rows: List[Dict[str, str]],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    rag_rows = []
    documents = []
    jsonl_path = output_dir / "chromadb_ready.jsonl"

    with jsonl_path.open("w", encoding="utf-8") as jsonl_handle:
        for index, row in enumerate(rows, start=1):
            metadata = flatten_metadata(row)
            doc_id = f"prod_{index:06d}"

            rag_row = {key: row.get(key, "") for key in CANONICAL_COLUMNS}
            rag_row.update({
                "renewable_type": row.get("renewable_type", ""),
                "product_type": row.get("product_type", ""),
                "document_text": row.get("document_text", ""),
                "summary": row.get("summary", ""),
                "doc_id": doc_id,
            })
            rag_rows.append(rag_row)

            documents.append({
                "id": doc_id,
                "text": row.get("document_text", ""),
                "metadata": metadata,
            })

            jsonl_handle.write(json.dumps({
                "id": doc_id,
                "text": row.get("document_text", ""),
                "metadata": metadata,
            }, ensure_ascii=True) + "\n")

    pd.DataFrame(rag_rows).to_csv(output_dir / "rag_ready.csv", index=False)

    with (output_dir / "rag_documents.json").open("w", encoding="utf-8") as handle:
        json.dump(documents, handle, ensure_ascii=True, indent=2)
```

**Explanation:** It accepts `rows`, `output_dir` and returns `None`. See the code below for the full implementation. Key calls include `mkdir()`, `open()`, `enumerate()`, `flatten_metadata()`, `update()`.

### `main`

- **File:** `python_scripts/prepare_rag_products.py`
- **Lines:** `371-401`
- **Signature:** `def main() -> None:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare RAG-ready product dataset.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-words", type=int, default=160)
    parser.add_argument("--overlap", type=float, default=0.15)
    parser.add_argument("--near-dedupe-threshold", type=float, default=0.85)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    setup_logging(args.log_level)

    if not args.input.exists():
        logging.error("Input file not found: %s", args.input)
        return

    df = load_dataset(args.input)
    rows, drop_counts, chunked_count = process_rows(
        df,
        max_words=args.max_words,
        overlap_ratio=args.overlap,
        near_dedupe_threshold=args.near_dedupe_threshold,
    )

    export_files(rows, args.output_dir)

    logging.info("Rows loaded: %s", len(df))
    logging.info("Rows kept: %s", len(rows))
    logging.info("Chunked documents: %s", chunked_count)
    for reason, count in drop_counts.items():
        logging.info("Dropped (%s): %s", reason, count)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `ArgumentParser()`, `add_argument()`, `parse_args()`, `setup_logging()`, `exists()`.


## `python_scripts/run_terrain_pipeline.py`

**File:** `python_scripts/run_terrain_pipeline.py`

**Summary:** Source file `python_scripts/run_terrain_pipeline.py`.

### `build_config`

- **File:** `python_scripts/run_terrain_pipeline.py`
- **Lines:** `10-24`
- **Signature:** `def build_config(args: argparse.Namespace, repo_root: Path) -> PipelineConfig:`
- **Purpose:** Builds config.

**Code:**
```python
def build_config(args: argparse.Namespace, repo_root: Path) -> PipelineConfig:
    base = default_config(repo_root)
    return PipelineConfig(
        raster_path=Path(args.raster_path) if args.raster_path else base.raster_path,
        municipalities_csv=Path(args.municipalities_csv) if args.municipalities_csv else base.municipalities_csv,
        provinces_csv=Path(args.provinces_csv) if args.provinces_csv else base.provinces_csv,
        output_dir=Path(args.output_dir) if args.output_dir else base.output_dir,
        polygon_path=Path(args.polygon_path) if args.polygon_path else None,
        buffer_m=args.buffer_m,
        batch_size=args.batch_size,
        use_supabase=not args.no_supabase,
        advanced_hydrology=args.advanced_hydrology,
        write_geojson=args.write_geojson,
        write_parquet=args.write_parquet,
    )
```

**Explanation:** It accepts `args`, `repo_root` and returns `PipelineConfig`. See the code below for the full implementation. Key calls include `default_config()`, `PipelineConfig()`, `Path()`.

### `main`

- **File:** `python_scripts/run_terrain_pipeline.py`
- **Lines:** `27-44`
- **Signature:** `def main() -> None:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> None:
    parser = argparse.ArgumentParser(description="Lumi terrain and hydrology pipeline")
    parser.add_argument("--raster-path", default=None, help="Path to PHL_msk_alt.vrt")
    parser.add_argument("--municipalities-csv", default=None, help="Municipalities CSV path")
    parser.add_argument("--provinces-csv", default=None, help="Provinces CSV path")
    parser.add_argument("--polygon-path", default=None, help="Optional municipality polygons (GeoJSON/Shapefile)")
    parser.add_argument("--output-dir", default=None, help="Output directory for CSVs")
    parser.add_argument("--buffer-m", type=float, default=2000.0, help="Sampling buffer in meters")
    parser.add_argument("--batch-size", type=int, default=500, help="Batch size for processing")
    parser.add_argument("--no-supabase", action="store_true", help="Disable Supabase coordinate enrichment")
    parser.add_argument("--advanced-hydrology", action="store_true", help="Enable hillshade/flow outputs")
    parser.add_argument("--write-geojson", action="store_true", help="Export GeoJSON output")
    parser.add_argument("--write-parquet", action="store_true", help="Export Parquet output")

    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    config = build_config(args, repo_root)
    run_pipeline(config)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `ArgumentParser()`, `add_argument()`, `parse_args()`, `resolve()`, `Path()`.


## `python_scripts/terrain_pipeline/__init__.py`

**File:** `python_scripts/terrain_pipeline/__init__.py`

**Summary:** Terrain and hydrology pipeline utilities for Lumi.

_No module-level or class-level functions in this file._

## `python_scripts/terrain_pipeline/config.py`

**File:** `python_scripts/terrain_pipeline/config.py`

**Summary:** Source file `python_scripts/terrain_pipeline/config.py`.

### `default_config`

- **File:** `python_scripts/terrain_pipeline/config.py`
- **Lines:** `40-46`
- **Signature:** `def default_config(repo_root: Path) -> PipelineConfig:`
- **Purpose:** Handles default config.

**Code:**
```python
def default_config(repo_root: Path) -> PipelineConfig:
    return PipelineConfig(
        raster_path=repo_root / "phl_msk_alt" / "PHL_msk_alt.vrt",
        municipalities_csv=repo_root / "regionalData" / "municipalities.csv",
        provinces_csv=repo_root / "regionalData" / "provinces.csv",
        output_dir=repo_root / "regionalData" / "output" / "terrain_metrics",
    )
```

**Explanation:** It accepts `repo_root` and returns `PipelineConfig`. See the code below for the full implementation. Key calls include `PipelineConfig()`.


## `python_scripts/terrain_pipeline/export.py`

**File:** `python_scripts/terrain_pipeline/export.py`

**Summary:** Source file `python_scripts/terrain_pipeline/export.py`.

### `write_csv`

- **File:** `python_scripts/terrain_pipeline/export.py`
- **Lines:** `10-13`
- **Signature:** `def write_csv(path: Path, rows: Iterable[dict]) -> None:`
- **Purpose:** Handles write csv.

**Code:**
```python
def write_csv(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
```

**Explanation:** It accepts `path`, `rows` and returns `None`. See the code below for the full implementation. Key calls include `mkdir()`, `DataFrame()`, `to_csv()`.

### `write_geojson`

- **File:** `python_scripts/terrain_pipeline/export.py`
- **Lines:** `16-18`
- **Signature:** `def write_geojson(path: Path, gdf: gpd.GeoDataFrame) -> None:`
- **Purpose:** Handles write geojson.

**Code:**
```python
def write_geojson(path: Path, gdf: gpd.GeoDataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(path, driver="GeoJSON")
```

**Explanation:** It accepts `path`, `gdf` and returns `None`. See the code below for the full implementation. Key calls include `mkdir()`, `to_file()`.

### `write_parquet`

- **File:** `python_scripts/terrain_pipeline/export.py`
- **Lines:** `21-23`
- **Signature:** `def write_parquet(path: Path, gdf: gpd.GeoDataFrame) -> None:`
- **Purpose:** Handles write parquet.

**Code:**
```python
def write_parquet(path: Path, gdf: gpd.GeoDataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(path, index=False)
```

**Explanation:** It accepts `path`, `gdf` and returns `None`. See the code below for the full implementation. Key calls include `mkdir()`, `to_parquet()`.


## `python_scripts/terrain_pipeline/hydrology.py`

**File:** `python_scripts/terrain_pipeline/hydrology.py`

**Summary:** Source file `python_scripts/terrain_pipeline/hydrology.py`.

### `generate_hillshade`

- **File:** `python_scripts/terrain_pipeline/hydrology.py`
- **Lines:** `16-18`
- **Signature:** `def generate_hillshade(dem_path: Path, output_path: Path, logger: logging.Logger) -> Optional[Path]:`
- **Purpose:** Handles generate hillshade.

**Code:**
```python
def generate_hillshade(dem_path: Path, output_path: Path, logger: logging.Logger) -> Optional[Path]:
    logger.warning("Hillshade generation disabled: richdem removed")
    return None
```

**Explanation:** It accepts `dem_path`, `output_path`, `logger` and returns `Optional[Path]`. See the code below for the full implementation. Key calls include `warning()`.

### `generate_flow_products`

- **File:** `python_scripts/terrain_pipeline/hydrology.py`
- **Lines:** `21-38`
- **Signature:** `def generate_flow_products(dem_path: Path, output_dir: Path, logger: logging.Logger) -> AdvancedHydrologyOutputs:`
- **Purpose:** Handles generate flow products.

**Code:**
```python
def generate_flow_products(dem_path: Path, output_dir: Path, logger: logging.Logger) -> AdvancedHydrologyOutputs:
    try:
        import whitebox
    except Exception:
        logger.warning("whitebox not available; skipping flow direction/accumulation")
        return AdvancedHydrologyOutputs()

    wbt = whitebox.WhiteboxTools()
    wbt.set_working_dir(str(output_dir))
    flow_dir = output_dir / "flow_direction.tif"
    flow_acc = output_dir / "flow_accumulation.tif"

    wbt.d8_pointer(str(dem_path), str(flow_dir))
    wbt.d8_flow_accumulation(str(dem_path), str(flow_acc))
    return AdvancedHydrologyOutputs(
        flow_direction_path=flow_dir,
        flow_accumulation_path=flow_acc,
    )
```

**Explanation:** It accepts `dem_path`, `output_dir`, `logger` and returns `AdvancedHydrologyOutputs`. See the code below for the full implementation. Key calls include `warning()`, `AdvancedHydrologyOutputs()`, `WhiteboxTools()`, `set_working_dir()`, `str()`.


## `python_scripts/terrain_pipeline/io.py`

**File:** `python_scripts/terrain_pipeline/io.py`

**Summary:** Source file `python_scripts/terrain_pipeline/io.py`.

### `SupabaseRestClient.__init__`

- **File:** `python_scripts/terrain_pipeline/io.py`
- **Lines:** `23-29`
- **Signature:** `def __init__(self, base_url: str, api_key: str) -> None:`
- **Purpose:** Method of `SupabaseRestClient` that handles   init  .

**Code:**
```python
def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
        }
        self.http = httpx.Client(timeout=20.0)
```

**Explanation:** It accepts `base_url`, `api_key` and returns `None`. See the code below for the full implementation. Key calls include `rstrip()`, `Client()`.

### `SupabaseRestClient.fetch_table`

- **File:** `python_scripts/terrain_pipeline/io.py`
- **Lines:** `31-47`
- **Signature:** `def fetch_table(self, table: str, columns: str, page_size: int = 1000) -> list[dict]:`
- **Purpose:** Method of `SupabaseRestClient` that fetches table.

**Code:**
```python
def fetch_table(self, table: str, columns: str, page_size: int = 1000) -> list[dict]:
        rows: list[dict] = []
        offset = 0
        while True:
            headers = dict(self.headers)
            headers["Range"] = f"{offset}-{offset + page_size - 1}"
            url = f"{self.base_url}/rest/v1/{table}"
            response = self.http.get(url, params={"select": columns}, headers=headers)
            response.raise_for_status()
            payload = response.json()
            if not payload:
                break
            rows.extend(payload)
            if len(payload) < page_size:
                break
            offset += page_size
        return rows
```

**Explanation:** It accepts `table`, `columns`, `page_size` and returns `list[dict]`. See the code below for the full implementation. Key calls include `dict()`, `get()`, `raise_for_status()`, `json()`, `extend()`.

### `load_env`

- **File:** `python_scripts/terrain_pipeline/io.py`
- **Lines:** `50-51`
- **Signature:** `def load_env(repo_root: Path) -> None:`
- **Purpose:** Loads env.

**Code:**
```python
def load_env(repo_root: Path) -> None:
    load_dotenv(dotenv_path=repo_root / ".env", override=False)
```

**Explanation:** It accepts `repo_root` and returns `None`. See the code below for the full implementation. Key calls include `load_dotenv()`.

### `resolve_supabase_config`

- **File:** `python_scripts/terrain_pipeline/io.py`
- **Lines:** `54-72`
- **Signature:** `def resolve_supabase_config(repo_root: Path) -> Optional[SupabaseConfig]:`
- **Purpose:** Handles resolve supabase config.

**Code:**
```python
def resolve_supabase_config(repo_root: Path) -> Optional[SupabaseConfig]:
    load_env(repo_root)
    url = os.getenv("SUPABASE_URL")
    key_candidates = (
        "SUPABASE_JWT_SERVICE_ROLE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_JWT_ANON_KEY",
        "SUPABASE_ANON_KEY",
        "SUPABASE_KEY",
    )
    key = None
    for key_name in key_candidates:
        value = os.getenv(key_name)
        if value:
            key = value
            break
    if url and key:
        return SupabaseConfig(url=url, key=key)
    return None
```

**Explanation:** It accepts `repo_root` and returns `Optional[SupabaseConfig]`. See the code below for the full implementation. Key calls include `load_env()`, `getenv()`, `SupabaseConfig()`.

### `load_municipalities`

- **File:** `python_scripts/terrain_pipeline/io.py`
- **Lines:** `75-118`
- **Signature:** `def load_municipalities(`
- **Purpose:** Loads municipalities.

**Code:**
```python
def load_municipalities(
    municipalities_csv: Path,
    provinces_csv: Path,
    supabase: Optional[SupabaseConfig],
    logger: logging.Logger,
) -> pd.DataFrame:
    municipalities = pd.read_csv(municipalities_csv)
    provinces = pd.read_csv(provinces_csv)
    provinces = provinces.rename(columns={"name": "province"})
    merged = municipalities.merge(provinces[["province_id", "province"]], on="province_id", how="left")

    if "lat" in merged.columns and "lon" in merged.columns:
        merged = merged.rename(columns={"lat": "latitude", "lon": "longitude"})
    else:
        merged["latitude"] = pd.NA
        merged["longitude"] = pd.NA

    if supabase:
        logger.info("Loading municipality coordinates from Supabase")
        client = SupabaseRestClient(supabase.url, supabase.key)
        payload = client.fetch_table("municipalities", "municipality_id,lat,lon")
        coords = pd.DataFrame(payload)
        coords = coords.rename(columns={"lat": "latitude", "lon": "longitude"})
        merged = merged.merge(coords, on="municipality_id", how="left", suffixes=("", "_sb"))
        merged["latitude"] = merged["latitude"].fillna(merged.pop("latitude_sb"))
        merged["longitude"] = merged["longitude"].fillna(merged.pop("longitude_sb"))

    missing = merged["latitude"].isna() | merged["longitude"].isna()
    if missing.any():
        count = int(missing.sum())
        logger.warning("Missing coordinates for %s municipalities", count)

    merged = merged.rename(columns={"name": "municipality_name"})
    merged = merged[
        [
            "municipality_id",
            "municipality_name",
            "province",
            "latitude",
            "longitude",
            "province_id",
        ]
    ]
    return merged
```

**Explanation:** It accepts `municipalities_csv`, `provinces_csv`, `supabase`, `logger` and returns `pd.DataFrame`. See the code below for the full implementation. Key calls include `read_csv()`, `rename()`, `merge()`, `info()`, `SupabaseRestClient()`.

### `load_polygons`

- **File:** `python_scripts/terrain_pipeline/io.py`
- **Lines:** `121-126`
- **Signature:** `def load_polygons(path: Path, logger: logging.Logger) -> gpd.GeoDataFrame:`
- **Purpose:** Loads polygons.

**Code:**
```python
def load_polygons(path: Path, logger: logging.Logger) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        logger.warning("Polygon CRS missing; assuming EPSG:4326")
        gdf = gdf.set_crs("EPSG:4326")
    return gdf
```

**Explanation:** It accepts `path`, `logger` and returns `gpd.GeoDataFrame`. See the code below for the full implementation. Key calls include `read_file()`, `warning()`, `set_crs()`.

### `save_json`

- **File:** `python_scripts/terrain_pipeline/io.py`
- **Lines:** `129-132`
- **Signature:** `def save_json(path: Path, payload: dict) -> None:`
- **Purpose:** Saves json.

**Code:**
```python
def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
```

**Explanation:** It accepts `path`, `payload` and returns `None`. See the code below for the full implementation. Key calls include `mkdir()`, `open()`, `dump()`.


## `python_scripts/terrain_pipeline/metrics.py`

**File:** `python_scripts/terrain_pipeline/metrics.py`

**Summary:** Source file `python_scripts/terrain_pipeline/metrics.py`.

### `normalize`

- **File:** `python_scripts/terrain_pipeline/metrics.py`
- **Lines:** `23-26`
- **Signature:** `def normalize(value: Optional[float], max_value: float) -> float:`
- **Purpose:** Handles normalize.

**Code:**
```python
def normalize(value: Optional[float], max_value: float) -> float:
    if value is None or np.isnan(value) or max_value <= 0:
        return 0.0
    return max(0.0, min(1.0, value / max_value))
```

**Explanation:** It accepts `value`, `max_value` and returns `float`. See the code below for the full implementation. Key calls include `isnan()`, `max()`, `min()`.

### `slope_classification`

- **File:** `python_scripts/terrain_pipeline/metrics.py`
- **Lines:** `29-46`
- **Signature:** `def slope_classification(`
- **Purpose:** Handles slope classification.

**Code:**
```python
def slope_classification(
    slope_deg: float,
    flat: float,
    gentle: float,
    moderate: float,
    steep: float,
) -> str:
    if np.isnan(slope_deg):
        return "unknown"
    if slope_deg < flat:
        return "flat"
    if slope_deg < gentle:
        return "gentle"
    if slope_deg < moderate:
        return "moderate"
    if slope_deg < steep:
        return "steep"
    return "very_steep"
```

**Explanation:** It accepts `slope_deg`, `flat`, `gentle`, `moderate`, `steep` and returns `str`. See the code below for the full implementation. Key calls include `isnan()`.

### `elevation_classification`

- **File:** `python_scripts/terrain_pipeline/metrics.py`
- **Lines:** `49-58`
- **Signature:** `def elevation_classification(elevation_m: float, low: float, mid: float, high: float) -> str:`
- **Purpose:** Handles elevation classification.

**Code:**
```python
def elevation_classification(elevation_m: float, low: float, mid: float, high: float) -> str:
    if np.isnan(elevation_m):
        return "unknown"
    if elevation_m < low:
        return "low"
    if elevation_m < mid:
        return "mid"
    if elevation_m < high:
        return "high"
    return "very_high"
```

**Explanation:** It accepts `elevation_m`, `low`, `mid`, `high` and returns `str`. See the code below for the full implementation. Key calls include `isnan()`.

### `terrain_flatness`

- **File:** `python_scripts/terrain_pipeline/metrics.py`
- **Lines:** `61-62`
- **Signature:** `def terrain_flatness(slope_deg: float, max_slope_deg: float) -> float:`
- **Purpose:** Handles terrain flatness.

**Code:**
```python
def terrain_flatness(slope_deg: float, max_slope_deg: float) -> float:
    return 1.0 - normalize(slope_deg, max_slope_deg)
```

**Explanation:** It accepts `slope_deg`, `max_slope_deg` and returns `float`. See the code below for the full implementation. Key calls include `normalize()`.

### `runoff_potential`

- **File:** `python_scripts/terrain_pipeline/metrics.py`
- **Lines:** `65-66`
- **Signature:** `def runoff_potential(slope_deg: float, elevation_m: float, caps: NormalizationCaps) -> float:`
- **Purpose:** Handles runoff potential.

**Code:**
```python
def runoff_potential(slope_deg: float, elevation_m: float, caps: NormalizationCaps) -> float:
    return normalize(slope_deg, caps.slope_deg) * normalize(elevation_m, caps.head_m)
```

**Explanation:** It accepts `slope_deg`, `elevation_m`, `caps` and returns `float`. See the code below for the full implementation. Key calls include `normalize()`.

### `gravity_flow_potential`

- **File:** `python_scripts/terrain_pipeline/metrics.py`
- **Lines:** `69-70`
- **Signature:** `def gravity_flow_potential(head_m: float, slope_deg: float, caps: NormalizationCaps) -> float:`
- **Purpose:** Handles gravity flow potential.

**Code:**
```python
def gravity_flow_potential(head_m: float, slope_deg: float, caps: NormalizationCaps) -> float:
    return normalize(head_m, caps.head_m) * normalize(slope_deg, caps.slope_deg)
```

**Explanation:** It accepts `head_m`, `slope_deg`, `caps` and returns `float`. See the code below for the full implementation. Key calls include `normalize()`.

### `hydro_suitability_score`

- **File:** `python_scripts/terrain_pipeline/metrics.py`
- **Lines:** `73-84`
- **Signature:** `def hydro_suitability_score(`
- **Purpose:** Handles hydro suitability score.

**Code:**
```python
def hydro_suitability_score(
    head_m: float,
    slope_deg: float,
    ruggedness_m: float,
    weights: SuitabilityWeights,
    caps: NormalizationCaps,
) -> float:
    head_score = normalize(head_m, caps.head_m)
    slope_score = normalize(slope_deg, caps.slope_deg)
    rugged_score = normalize(ruggedness_m, caps.ruggedness_m)
    total = weights.head * head_score + weights.slope * slope_score + weights.ruggedness * rugged_score
    return max(0.0, min(1.0, total))
```

**Explanation:** It accepts `head_m`, `slope_deg`, `ruggedness_m`, `weights`, `caps` and returns `float`. See the code below for the full implementation. Key calls include `normalize()`, `max()`, `min()`.

### `terrain_exposure_index`

- **File:** `python_scripts/terrain_pipeline/metrics.py`
- **Lines:** `87-90`
- **Signature:** `def terrain_exposure_index(max_elev: float, mean_elev: float, ruggedness_m: float) -> float:`
- **Purpose:** Handles terrain exposure index.

**Code:**
```python
def terrain_exposure_index(max_elev: float, mean_elev: float, ruggedness_m: float) -> float:
    if np.isnan(max_elev) or np.isnan(mean_elev) or np.isnan(ruggedness_m):
        return float("nan")
    return float((max_elev - mean_elev) / (ruggedness_m + 1e-6))
```

**Explanation:** It accepts `max_elev`, `mean_elev`, `ruggedness_m` and returns `float`. See the code below for the full implementation. Key calls include `isnan()`, `float()`.


## `python_scripts/terrain_pipeline/pipeline.py`

**File:** `python_scripts/terrain_pipeline/pipeline.py`

**Summary:** Source file `python_scripts/terrain_pipeline/pipeline.py`.

### `setup_logger`

- **File:** `python_scripts/terrain_pipeline/pipeline.py`
- **Lines:** `41-49`
- **Signature:** `def setup_logger() -> logging.Logger:`
- **Purpose:** Sets up logger.

**Code:**
```python
def setup_logger() -> logging.Logger:
    logger = logging.getLogger("terrain_pipeline")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    logger.propagate = False
    return logger
```

**Explanation:** It accepts zero arguments and returns `logging.Logger`. See the code below for the full implementation. Key calls include `getLogger()`, `setLevel()`, `StreamHandler()`, `Formatter()`, `setFormatter()`.

### `chunked`

- **File:** `python_scripts/terrain_pipeline/pipeline.py`
- **Lines:** `52-60`
- **Signature:** `def chunked(iterable: Iterable, size: int) -> Iterable[list]:`
- **Purpose:** Handles chunked.

**Code:**
```python
def chunked(iterable: Iterable, size: int) -> Iterable[list]:
    batch: list = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch
```

**Explanation:** It accepts `iterable`, `size` and returns `Iterable[list]`. See the code below for the full implementation. Key calls include `append()`, `len()`.

### `compute_metrics_for_row`

- **File:** `python_scripts/terrain_pipeline/pipeline.py`
- **Lines:** `63-176`
- **Signature:** `def compute_metrics_for_row(row: dict, cfg: PipelineConfig, ctx) -> dict:`
- **Purpose:** Computes metrics for row.

**Code:**
```python
def compute_metrics_for_row(row: dict, cfg: PipelineConfig, ctx) -> dict:
    lon = row.get("longitude")
    lat = row.get("latitude")
    if lon is None or lat is None or np.isnan(lon) or np.isnan(lat):
        row.update(
            {
                "elevation_m": np.nan,
                "mean_elevation_m": np.nan,
                "min_elevation_m": np.nan,
                "max_elevation_m": np.nan,
                "elevation_range_m": np.nan,
                "mean_slope_deg": np.nan,
                "hydraulic_head_m": np.nan,
                "terrain_ruggedness": np.nan,
                "watershed_gradient": np.nan,
                "hydro_suitability_score": np.nan,
                "estimated_hydropower_potential_kw": np.nan,
                "runoff_potential": np.nan,
                "gravity_flow_potential": np.nan,
                "terrain_flatness": np.nan,
                "slope_classification": "unknown",
                "elevation_classification": "unknown",
                "ridge_elevation": np.nan,
                "terrain_exposure_index": np.nan,
            }
        )
        return row

    elevation = sample_point(ctx, lon, lat)
    if elevation is None:
        elevation = np.nan
    raster_xy = point_to_raster_coords(lon, lat, ctx.crs)
    bounds = buffer_bounds(lon, lat, cfg.buffer_m, ctx.crs, raster_xy)
    window = read_window(ctx, bounds)

    zonal_mean = row.get("zonal_mean_elev")
    zonal_min = row.get("zonal_min_elev")
    zonal_max = row.get("zonal_max_elev")
    zonal_std = row.get("zonal_std_elev")

    if zonal_mean is not None and not np.isnan(zonal_mean):
        mean_elev = float(zonal_mean)
        min_elev = float(zonal_min) if zonal_min is not None else np.nan
        max_elev = float(zonal_max) if zonal_max is not None else np.nan
        std_elev = float(zonal_std) if zonal_std is not None else np.nan
    elif window.count() == 0:
        mean_elev = min_elev = max_elev = std_elev = np.nan
    else:
        mean_elev = float(window.mean())
        min_elev = float(window.min())
        max_elev = float(window.max())
        std_elev = float(window.std())

    elevation_range = max_elev - min_elev if not np.isnan(max_elev) else np.nan
    hydraulic_head = elevation_range

    pixel_sizes = pixel_size_meters(ctx, lat, lon)
    mean_slope = mean_slope_degrees(window, pixel_sizes)
    ruggedness = std_elev if not np.isnan(std_elev) else terrain_ruggedness_index(window)
    watershed_gradient = hydraulic_head / (cfg.buffer_m * 2.0) if cfg.buffer_m else np.nan

    caps = NormalizationCaps(
        head_m=cfg.normalize_max_head_m,
        slope_deg=cfg.normalize_max_slope_deg,
        ruggedness_m=cfg.normalize_max_ruggedness_m,
    )
    weights = SuitabilityWeights(
        head=cfg.suitability_weight_head,
        slope=cfg.suitability_weight_slope,
        ruggedness=cfg.suitability_weight_ruggedness,
    )

    runoff = runoff_potential(mean_slope, mean_elev, caps)
    gravity = gravity_flow_potential(hydraulic_head, mean_slope, caps)
    suitability = hydro_suitability_score(hydraulic_head, mean_slope, ruggedness, weights, caps)
    hydropower_kw = hydraulic_head * runoff * cfg.hydropower_scale_kw if not np.isnan(hydraulic_head) else np.nan

    slope_class = slope_classification(
        mean_slope,
        cfg.slope_flat_threshold_deg,
        cfg.slope_gentle_threshold_deg,
        cfg.slope_moderate_threshold_deg,
        cfg.slope_steep_threshold_deg,
    )
    elev_class = elevation_classification(
        mean_elev,
        cfg.elevation_low_m,
        cfg.elevation_mid_m,
        cfg.elevation_high_m,
    )

    row.update(
        {
            "elevation_m": elevation,
            "mean_elevation_m": mean_elev,
            "min_elevation_m": min_elev,
            "max_elevation_m": max_elev,
            "elevation_range_m": elevation_range,
            "mean_slope_deg": mean_slope,
            "hydraulic_head_m": hydraulic_head,
            "terrain_ruggedness": ruggedness,
            "watershed_gradient": watershed_gradient,
            "hydro_suitability_score": suitability,
            "estimated_hydropower_potential_kw": hydropower_kw,
            "runoff_potential": runoff,
            "gravity_flow_potential": gravity,
            "terrain_flatness": terrain_flatness(mean_slope, cfg.normalize_max_slope_deg),
            "slope_classification": slope_class,
            "elevation_classification": elev_class,
            "ridge_elevation": max_elev,
            "terrain_exposure_index": terrain_exposure_index(max_elev, mean_elev, ruggedness),
        }
    )
    return row
```

**Explanation:** It accepts `row`, `cfg`, `ctx` and returns `dict`. See the code below for the full implementation. Key calls include `get()`, `isnan()`, `update()`, `sample_point()`, `point_to_raster_coords()`.

### `run_pipeline`

- **File:** `python_scripts/terrain_pipeline/pipeline.py`
- **Lines:** `179-255`
- **Signature:** `def run_pipeline(cfg: PipelineConfig) -> dict:`
- **Purpose:** Runs pipeline.

**Code:**
```python
def run_pipeline(cfg: PipelineConfig) -> dict:
    logger = setup_logger()
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    raster_ctx = open_raster(str(cfg.raster_path))
    inspect_raster(raster_ctx, logger)

    supabase_cfg = None
    if cfg.use_supabase:
        supabase_cfg = resolve_supabase_config(cfg.raster_path.parents[1])
        if not supabase_cfg:
            logger.warning("Supabase credentials not found; using CSV coordinates only")

    muni_df = load_municipalities(cfg.municipalities_csv, cfg.provinces_csv, supabase_cfg, logger)
    muni_df = muni_df.dropna(subset=["latitude", "longitude"], how="any")

    geo = gpd.GeoDataFrame(
        muni_df,
        geometry=[Point(xy) for xy in zip(muni_df["longitude"], muni_df["latitude"])],
        crs="EPSG:4326",
    )

    if cfg.polygon_path:
        polygons = load_polygons(cfg.polygon_path, logger)
        if "municipality_id" not in polygons.columns:
            raise ValueError("Polygon data must include municipality_id")
        stats = zonal_stats(
            polygons,
            str(cfg.raster_path),
            stats=["mean", "min", "max", "std"],
            nodata=raster_ctx.nodata,
        )
        stats_df = polygons[["municipality_id"]].copy()
        stats_df["zonal_mean_elev"] = [item.get("mean") for item in stats]
        stats_df["zonal_min_elev"] = [item.get("min") for item in stats]
        stats_df["zonal_max_elev"] = [item.get("max") for item in stats]
        stats_df["zonal_std_elev"] = [item.get("std") for item in stats]
        geo = geo.merge(stats_df, on="municipality_id", how="left")

    results: list[dict] = []
    for batch in chunked(geo.to_dict(orient="records"), cfg.batch_size):
        for row in batch:
            results.append(compute_metrics_for_row(row, cfg, raster_ctx))

    metadata = {
        "raster_path": str(cfg.raster_path),
        "buffer_m": cfg.buffer_m,
        "count": len(results),
    }
    save_json(cfg.output_dir / "run_metadata.json", metadata)

    csv_rows = [
        {
            k: v
            for k, v in row.items()
            if k != "geometry" and not k.startswith("zonal_")
        }
        for row in results
    ]
    write_csv(cfg.output_dir / "municipality_terrain_metrics.csv", csv_rows)
    write_csv(cfg.output_dir / "hydropower_suitability.csv", csv_rows)
    write_csv(cfg.output_dir / "renewable_energy_geodata.csv", csv_rows)

    if cfg.write_geojson or cfg.write_parquet:
        output_gdf = gpd.GeoDataFrame(results, geometry="geometry", crs="EPSG:4326")
        if cfg.write_geojson:
            write_geojson(cfg.output_dir / "renewable_energy_geodata.geojson", output_gdf)
        if cfg.write_parquet:
            write_parquet(cfg.output_dir / "renewable_energy_geodata.parquet", output_gdf)

    if cfg.advanced_hydrology:
        hillshade_path = cfg.output_dir / "hillshade.tif"
        generate_hillshade(cfg.raster_path, hillshade_path, logger)
        generate_flow_products(cfg.raster_path, cfg.output_dir, logger)

    raster_ctx.dataset.close()
    logger.info("Pipeline complete. Outputs in %s", cfg.output_dir)
    return metadata
```

**Explanation:** It accepts `cfg` and returns `dict`. See the code below for the full implementation. Key calls include `setup_logger()`, `mkdir()`, `open_raster()`, `str()`, `inspect_raster()`.


## `python_scripts/terrain_pipeline/raster_utils.py`

**File:** `python_scripts/terrain_pipeline/raster_utils.py`

**Summary:** Source file `python_scripts/terrain_pipeline/raster_utils.py`.

### `open_raster`

- **File:** `python_scripts/terrain_pipeline/raster_utils.py`
- **Lines:** `24-38`
- **Signature:** `def open_raster(path: str) -> RasterContext:`
- **Purpose:** Handles open raster.

**Code:**
```python
def open_raster(path: str) -> RasterContext:
    dataset = rasterio.open(path)
    crs = CRS.from_wkt(dataset.crs.to_wkt())
    transform = dataset.transform
    pixel_size_x = abs(transform.a)
    pixel_size_y = abs(transform.e)
    return RasterContext(
        dataset=dataset,
        crs=crs,
        nodata=dataset.nodata,
        transform=transform,
        bounds=dataset.bounds,
        pixel_size_x=pixel_size_x,
        pixel_size_y=pixel_size_y,
    )
```

**Explanation:** It accepts `path` and returns `RasterContext`. See the code below for the full implementation. Key calls include `open()`, `from_wkt()`, `to_wkt()`, `abs()`, `RasterContext()`.

### `inspect_raster`

- **File:** `python_scripts/terrain_pipeline/raster_utils.py`
- **Lines:** `41-45`
- **Signature:** `def inspect_raster(ctx: RasterContext, logger: logging.Logger) -> None:`
- **Purpose:** Handles inspect raster.

**Code:**
```python
def inspect_raster(ctx: RasterContext, logger: logging.Logger) -> None:
    logger.info("Raster CRS: %s", ctx.crs.to_string())
    logger.info("Raster bounds: %s", ctx.bounds)
    logger.info("Raster resolution: %.6f x %.6f", ctx.pixel_size_x, ctx.pixel_size_y)
    logger.info("Raster nodata: %s", ctx.nodata)
```

**Explanation:** It accepts `ctx`, `logger` and returns `None`. See the code below for the full implementation. Key calls include `info()`, `to_string()`.

### `_meters_per_degree`

- **File:** `python_scripts/terrain_pipeline/raster_utils.py`
- **Lines:** `48-52`
- **Signature:** `def _meters_per_degree(lat: float, lon: float) -> Tuple[float, float]:`
- **Purpose:** Handles  meters per degree.

**Code:**
```python
def _meters_per_degree(lat: float, lon: float) -> Tuple[float, float]:
    geod = Geod(ellps="WGS84")
    _, _, dist_x = geod.inv(lon, lat, lon + 1.0, lat)
    _, _, dist_y = geod.inv(lon, lat, lon, lat + 1.0)
    return abs(dist_x), abs(dist_y)
```

**Explanation:** It accepts `lat`, `lon` and returns `Tuple[float, float]`. See the code below for the full implementation. Key calls include `Geod()`, `inv()`, `abs()`.

### `point_to_raster_coords`

- **File:** `python_scripts/terrain_pipeline/raster_utils.py`
- **Lines:** `55-63`
- **Signature:** `def point_to_raster_coords(`
- **Purpose:** Handles point to raster coords.

**Code:**
```python
def point_to_raster_coords(
    lon: float,
    lat: float,
    raster_crs: CRS,
) -> Tuple[float, float]:
    if raster_crs.is_geographic:
        return lon, lat
    transformer = Transformer.from_crs("EPSG:4326", raster_crs, always_xy=True)
    return transformer.transform(lon, lat)
```

**Explanation:** It accepts `lon`, `lat`, `raster_crs` and returns `Tuple[float, float]`. See the code below for the full implementation. Key calls include `from_crs()`, `transform()`.

### `buffer_bounds`

- **File:** `python_scripts/terrain_pipeline/raster_utils.py`
- **Lines:** `66-79`
- **Signature:** `def buffer_bounds(`
- **Purpose:** Handles buffer bounds.

**Code:**
```python
def buffer_bounds(
    lon: float,
    lat: float,
    buffer_m: float,
    raster_crs: CRS,
    raster_xy: Tuple[float, float],
) -> Tuple[float, float, float, float]:
    x, y = raster_xy
    if raster_crs.is_projected:
        return (x - buffer_m, y - buffer_m, x + buffer_m, y + buffer_m)
    meters_x, meters_y = _meters_per_degree(lat, lon)
    buffer_deg_x = buffer_m / meters_x if meters_x else 0.0
    buffer_deg_y = buffer_m / meters_y if meters_y else 0.0
    return (x - buffer_deg_x, y - buffer_deg_y, x + buffer_deg_x, y + buffer_deg_y)
```

**Explanation:** It accepts `lon`, `lat`, `buffer_m`, `raster_crs`, `raster_xy` and returns `Tuple[float, float, float, float]`. See the code below for the full implementation. Key calls include `_meters_per_degree()`.

### `read_window`

- **File:** `python_scripts/terrain_pipeline/raster_utils.py`
- **Lines:** `82-88`
- **Signature:** `def read_window(`
- **Purpose:** Reads window.

**Code:**
```python
def read_window(
    ctx: RasterContext,
    bounds: Tuple[float, float, float, float],
) -> np.ma.MaskedArray:
    window = from_bounds(*bounds, transform=ctx.transform)
    data = ctx.dataset.read(1, window=window, masked=True)
    return data
```

**Explanation:** It accepts `ctx`, `bounds` and returns `np.ma.MaskedArray`. See the code below for the full implementation. Key calls include `from_bounds()`, `read()`.

### `sample_point`

- **File:** `python_scripts/terrain_pipeline/raster_utils.py`
- **Lines:** `91-103`
- **Signature:** `def sample_point(ctx: RasterContext, lon: float, lat: float) -> Optional[float]:`
- **Purpose:** Handles sample point.

**Code:**
```python
def sample_point(ctx: RasterContext, lon: float, lat: float) -> Optional[float]:
    if ctx.crs.is_geographic:
        coords = [(lon, lat)]
    else:
        transformer = Transformer.from_crs("EPSG:4326", ctx.crs, always_xy=True)
        coords = [transformer.transform(lon, lat)]
    values = list(ctx.dataset.sample(coords))
    if not values:
        return None
    value = values[0][0]
    if ctx.nodata is not None and value == ctx.nodata:
        return None
    return float(value)
```

**Explanation:** It accepts `ctx`, `lon`, `lat` and returns `Optional[float]`. See the code below for the full implementation. Key calls include `from_crs()`, `transform()`, `list()`, `sample()`, `float()`.

### `pixel_size_meters`

- **File:** `python_scripts/terrain_pipeline/raster_utils.py`
- **Lines:** `106-110`
- **Signature:** `def pixel_size_meters(ctx: RasterContext, lat: float, lon: float) -> Tuple[float, float]:`
- **Purpose:** Handles pixel size meters.

**Code:**
```python
def pixel_size_meters(ctx: RasterContext, lat: float, lon: float) -> Tuple[float, float]:
    if ctx.crs.is_projected:
        return ctx.pixel_size_x, ctx.pixel_size_y
    meters_x, meters_y = _meters_per_degree(lat, lon)
    return ctx.pixel_size_x * meters_x, ctx.pixel_size_y * meters_y
```

**Explanation:** It accepts `ctx`, `lat`, `lon` and returns `Tuple[float, float]`. See the code below for the full implementation. Key calls include `_meters_per_degree()`.

### `mean_slope_degrees`

- **File:** `python_scripts/terrain_pipeline/raster_utils.py`
- **Lines:** `113-122`
- **Signature:** `def mean_slope_degrees(data: np.ma.MaskedArray, pixel_size: Tuple[float, float]) -> float:`
- **Purpose:** Handles mean slope degrees.

**Code:**
```python
def mean_slope_degrees(data: np.ma.MaskedArray, pixel_size: Tuple[float, float]) -> float:
    if data.count() == 0:
        return float("nan")
    filled = data.filled(data.mean())
    dy, dx = np.gradient(filled, pixel_size[1], pixel_size[0])
    slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
    slope_deg = np.degrees(slope_rad)
    if isinstance(data, np.ma.MaskedArray):
        slope_deg = np.ma.array(slope_deg, mask=data.mask)
    return float(np.ma.mean(slope_deg))
```

**Explanation:** It accepts `data`, `pixel_size` and returns `float`. See the code below for the full implementation. Key calls include `count()`, `float()`, `filled()`, `mean()`, `gradient()`.

### `terrain_ruggedness_index`

- **File:** `python_scripts/terrain_pipeline/raster_utils.py`
- **Lines:** `125-131`
- **Signature:** `def terrain_ruggedness_index(data: np.ma.MaskedArray) -> float:`
- **Purpose:** Handles terrain ruggedness index.

**Code:**
```python
def terrain_ruggedness_index(data: np.ma.MaskedArray) -> float:
    if data.count() == 0:
        return float("nan")
    filled = data.filled(data.mean())
    center = filled[filled.shape[0] // 2, filled.shape[1] // 2]
    tri = np.mean(np.abs(filled - center))
    return float(tri)
```

**Explanation:** It accepts `data` and returns `float`. See the code below for the full implementation. Key calls include `count()`, `float()`, `filled()`, `mean()`, `abs()`.


## `python_scripts/wind_power_coefficient.py`

**File:** `python_scripts/wind_power_coefficient.py`

**Summary:** Source file `python_scripts/wind_power_coefficient.py`.

### `compute_power_coefficient`

- **File:** `python_scripts/wind_power_coefficient.py`
- **Lines:** `7-30`
- **Signature:** `def compute_power_coefficient(`
- **Purpose:** Computes power coefficient.

**Code:**
```python
def compute_power_coefficient(
    power_w: float,
    diameter_m: float,
    wind_speed_mps: float,
    air_density: float = 1.225,
    clamp_to_betz: bool = False,
) -> Optional[float]:
    if power_w <= 0 or diameter_m <= 0 or wind_speed_mps <= 0:
        return None
    if not 0.9 <= air_density <= 1.3:
        return None

    radius_m = diameter_m / 2.0
    area = math.pi * radius_m ** 2
    available_wind_power = 0.5 * air_density * area * (wind_speed_mps ** 3)
    if available_wind_power <= 0:
        return None

    cp = power_w / available_wind_power

    if clamp_to_betz:
        return min(cp, BETZ_LIMIT)

    return None if cp > BETZ_LIMIT else cp
```

**Explanation:** It accepts `power_w`, `diameter_m`, `wind_speed_mps`, `air_density`, `clamp_to_betz` and returns `Optional[float]`. See the code below for the full implementation. Key calls include `min()`.

### `validate_power_coefficient`

- **File:** `python_scripts/wind_power_coefficient.py`
- **Lines:** `33-62`
- **Signature:** `def validate_power_coefficient(cp: Optional[float]) -> dict:`
- **Purpose:** Validates power coefficient.

**Code:**
```python
def validate_power_coefficient(cp: Optional[float]) -> dict:
    if cp is None:
        return {"valid": False, "category": "invalid", "message": "Calculation failed"}
    if cp <= 0:
        return {"valid": False, "category": "impossible", "message": "Cp must be positive"}
    if cp > BETZ_LIMIT:
        return {
            "valid": False,
            "category": "exceeds_betz",
            "message": f"Cp ({cp:.3f}) exceeds Betz limit ({BETZ_LIMIT:.3f})",
        }

    if cp < 0.25:
        category = "low_efficiency"
    elif cp < 0.35:
        category = "moderate_efficiency"
    elif cp < 0.45:
        category = "good_efficiency"
    elif cp < 0.50:
        category = "excellent_efficiency"
    else:
        category = "near_betz_limit"

    return {
        "valid": True,
        "category": category,
        "cp_decimal": cp,
        "cp_percent": cp * 100,
        "betz_ratio": cp / BETZ_LIMIT,
    }
```

**Explanation:** It accepts `cp` and returns `dict`. See the code below for the full implementation.


## `requirements-no-torch.txt`

**File:** `requirements-no-torch.txt`

**Summary:** Text template or notes file.

**First lines:**
```txt
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic-settings==2.4.0
supabase==2.10.0
python-jose[cryptography]==3.3.0
redis==5.0.8
httpx==0.27.2
flask
redis 
beautifulsoup4
google-generativeai
folium
supabase
nltk
transformers
langdetect
deep-translator
werkzeug
google-genai
logging
uvicorn
pandas
matplotlib
numpy
requests
scikit-learn
Flask
Flask-SQLAlchemy
Flask-Migrate
Flask-Login
```


## `requirements.txt`

**File:** `requirements.txt`

**Summary:** Text template or notes file.

**First lines:**
```txt
# =============================================================================
# LUMI - Comprehensive Python Dependencies
# =============================================================================
# This file aggregates every third-party package used across the LUMI repo:
#   - fastapi-backend/          (API, RAG, LLM clients)
#   - python_scripts/            (terrain pipeline, climate analysis, ETL)
#   - scraped_data/              (e-commerce web scrapers)
#   - windsurf_data_extraction/  (PDF extraction, cleaning, RAG conversion)
#   - DOE_Data_Extracted/      (Jupyter notebooks for ARIMA preprocessing)
#
# Install everything:
#   pip install -r requirements.txt
#
# For heavy ML / GIS packages, install inside a virtual environment.
# =============================================================================

# ---------------------------------------------------------------------------
# Web Framework & Server
# ---------------------------------------------------------------------------
fastapi==0.115.0
uvicorn[standard]==0.30.6
flask
flask-cors
flask-restful
Flask-SQLAlchemy
Flask-Migrate
Flask-Login
Flask-WTF
Flask-Mail
Flask-Session
```


## `scripts/check_cache.py`

**File:** `scripts/check_cache.py`

**Summary:** Source file `scripts/check_cache.py`.

_No module-level or class-level functions in this file._

## `scripts/debug_regions.py`

**File:** `scripts/debug_regions.py`

**Summary:** Source file `scripts/debug_regions.py`.

### `normalize_name`

- **File:** `scripts/debug_regions.py`
- **Lines:** `24-30`
- **Signature:** `def normalize_name(name):`
- **Purpose:** Normalizes name.

**Code:**
```python
def normalize_name(name):
    name = name.upper().strip()
    name = re.sub(r'^(CITY OF|MUNICIPALITY OF|BARANGAY OF)\s+', '', name)
    name = re.sub(r'\(.*?\)', '', name)
    name = re.sub(r'[^A-Z0-9 ]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name
```

**Explanation:** It accepts `name`. See the code below for the full implementation. Key calls include `strip()`, `upper()`, `sub()`.


## `scripts/extract_centroids.py`

**File:** `scripts/extract_centroids.py`

**Summary:** Extract centroid coordinates and area from GeoJSON boundary files.

### `norm`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `51-59`
- **Signature:** `def norm(name: str) -> str:`
- **Purpose:** Normalize a geographic name for matching.

**Code:**
```python
def norm(name: str) -> str:
    """Normalize a geographic name for matching."""
    s = name.strip().lower()
    s = _PARENTHETICAL.sub(" ", s)
    s = _CITY_SUFFIXES.sub("", s)
    s = _MUNI_SUFFIXES.sub("", s)
    s = s.replace("city of ", "").strip()
    s = _MULTI_SPACE.sub(" ", s)
    return s
```

**Explanation:** It accepts `name` and returns `str`. See the code below for the full implementation. Key calls include `lower()`, `strip()`, `sub()`, `replace()`.

### `compute_centroid_and_area`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `67-94`
- **Signature:** `def compute_centroid_and_area(feature: dict) -> tuple[float, float, float]:`
- **Purpose:** Compute centroid (lat, lon) and area_km2 from a GeoJSON feature.

**Code:**
```python
def compute_centroid_and_area(feature: dict) -> tuple[float, float, float]:
    """Compute centroid (lat, lon) and area_km2 from a GeoJSON feature.

    Uses shapely to compute the geometric centroid. Area is computed
    using a simple equirectangular approximation centered on the polygon.
    """
    geom = shape(feature["geometry"])

    # Centroid — shapely gives (lon, lat) in EPSG:4326
    centroid = geom.centroid
    lon = centroid.x
    lat = centroid.y

    # Area approximation: equirectangular projection
    # R_earth = 6371 km
    # area = (lon_range * cos(lat_avg) * lat_range) * (pi/180)^2 * R^2
    # But shapely doesn't do geodesic. Use the property from GeoJSON if available.
    props = feature.get("properties", {})
    area_km2 = props.get("area_km2")
    if area_km2 is None:
        # Fallback: rough equirectangular approximation
        minx, miny, maxx, maxy = geom.bounds
        lat_rad = lat * 3.141592653589793 / 180.0
        lon_range_km = (maxx - minx) * 111.32 * cos(lat_rad)
        lat_range_km = (maxy - miny) * 110.574
        area_km2 = lon_range_km * lat_range_km

    return round(lat, 6), round(lon, 6), round(float(area_km2), 2)
```

**Explanation:** It accepts `feature` and returns `tuple[float, float, float]`. See the code below for the full implementation. Key calls include `shape()`, `get()`, `cos()`, `round()`, `float()`.

### `cos`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `97-100`
- **Signature:** `def cos(x: float) -> float:`
- **Purpose:** Handles cos.

**Code:**
```python
def cos(x: float) -> float:
    import math

    return math.cos(x)
```

**Explanation:** It accepts `x` and returns `float`. See the code below for the full implementation. Key calls include `cos()`.

### `process_geojson`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `103-138`
- **Signature:** `def process_geojson(`
- **Purpose:** Process a GeoJSON file and return list of centroid records.

**Code:**
```python
def process_geojson(
    filepath: Path, name_property: str
) -> list[dict]:
    """Process a GeoJSON file and return list of centroid records.

    Each record: {name, centroid_lat, centroid_lon, area_km2, psgc}
    """
    print(f"Loading {filepath.name}...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])
    print(f"  {len(features)} features found")

    records = []
    for feat in features:
        props = feat.get("properties", {})
        name = props.get(name_property, "")
        if not name:
            continue

        lat, lon, area = compute_centroid_and_area(feat)
        psgc = props.get(f"{name_property.split('_')[0]}_psgc")

        records.append(
            {
                "name": name,
                "normalized_name": norm(name),
                "centroid_lat": lat,
                "centroid_lon": lon,
                "area_km2": area,
                "psgc": psgc,
            }
        )

    return records
```

**Explanation:** It accepts `filepath`, `name_property` and returns `list[dict]`. See the code below for the full implementation. Key calls include `open()`, `load()`, `get()`, `len()`, `compute_centroid_and_area()`.

### `SupabaseRestClient.__init__`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `147-153`
- **Signature:** `def __init__(self, base_url: str, api_key: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles   init  .

**Code:**
```python
def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
        }
        self.http = httpx.Client(timeout=60.0)
```

**Explanation:** It accepts `base_url`, `api_key`. See the code below for the full implementation. Key calls include `rstrip()`, `Client()`.

### `SupabaseRestClient.fetch_all`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `155-171`
- **Signature:** `def fetch_all(self, table: str, select: str, batch: int = 1000) -> list[dict]:`
- **Purpose:** Fetch all rows from a table with pagination.

**Code:**
```python
def fetch_all(self, table: str, select: str, batch: int = 1000) -> list[dict]:
        """Fetch all rows from a table with pagination."""
        rows = []
        offset = 0
        while True:
            url = f"{self.base_url}/rest/v1/{table}"
            params = {"select": select, "limit": str(batch), "offset": str(offset)}
            resp = self.http.get(url, params=params, headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                break
            rows.extend(data)
            if len(data) < batch:
                break
            offset += batch
        return rows
```

**Explanation:** It accepts `table`, `select`, `batch` and returns `list[dict]`. See the code below for the full implementation. Key calls include `get()`, `raise_for_status()`, `json()`, `extend()`, `str()`.

### `build_province_lookup`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `174-185`
- **Signature:** `def build_province_lookup(client: SupabaseRestClient) -> dict[str, dict]:`
- **Purpose:** Build normalized name → province record mapping.

**Code:**
```python
def build_province_lookup(client: SupabaseRestClient) -> dict[str, dict]:
    """Build normalized name → province record mapping."""
    print("Fetching provinces from Supabase...")
    rows = client.fetch_all("provinces", "province_id,name,region_id,lat,lon")
    print(f"  {len(rows)} provinces found")
    lookup = {}
    for r in rows:
        key = norm(r["name"])
        lookup[key] = r
        # Also add the raw name lowercased as an alias
        lookup[r["name"].lower().strip()] = r
    return lookup
```

**Explanation:** It accepts `client` and returns `dict[str, dict]`. See the code below for the full implementation. Key calls include `fetch_all()`, `len()`, `norm()`, `strip()`, `lower()`.

### `build_municipality_lookup`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `188-205`
- **Signature:** `def build_municipality_lookup(client: SupabaseRestClient) -> dict[str, dict]:`
- **Purpose:** Build normalized name → municipality record mapping.

**Code:**
```python
def build_municipality_lookup(client: SupabaseRestClient) -> dict[str, dict]:
    """Build normalized name → municipality record mapping."""
    print("Fetching municipalities from Supabase...")
    rows = client.fetch_all(
        "municipalities", "municipality_id,name,province_id,lat,lon"
    )
    print(f"  {len(rows)} municipalities found")
    lookup = {}
    for r in rows:
        key = norm(r["name"])
        # If duplicate normalized names exist, keep the first
        if key not in lookup:
            lookup[key] = r
        # Also add raw name
        raw_key = r["name"].lower().strip()
        if raw_key not in lookup:
            lookup[raw_key] = r
    return lookup
```

**Explanation:** It accepts `client` and returns `dict[str, dict]`. See the code below for the full implementation. Key calls include `fetch_all()`, `len()`, `norm()`, `strip()`, `lower()`.

### `write_csv`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `213-219`
- **Signature:** `def write_csv(filepath: Path, rows: list[dict], fieldnames: list[str]) -> None:`
- **Purpose:** Handles write csv.

**Code:**
```python
def write_csv(filepath: Path, rows: list[dict], fieldnames: list[str]) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Written {len(rows)} rows to {filepath.name}")
```

**Explanation:** It accepts `filepath`, `rows`, `fieldnames` and returns `None`. See the code below for the full implementation. Key calls include `mkdir()`, `open()`, `DictWriter()`, `writeheader()`, `writerows()`.

### `main`

- **File:** `scripts/extract_centroids.py`
- **Lines:** `227-335`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    load_dotenv(dotenv_path=REPO_ROOT / ".env", override=False)

    url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_KEY")
        or os.getenv("VITE_SUPABASE_ANON_KEY")
    )
    if not url or not key:
        print("ERROR: Missing Supabase credentials", file=sys.stderr)
        return 1

    client = SupabaseRestClient(url, key)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Province centroids ---
    print("\n=== Processing province GeoJSON ===")
    province_records = process_geojson(PROVINCE_GEOJSON, "adm2_en")
    province_lookup = build_province_lookup(client)

    province_matches = []
    province_unmatched = []
    for rec in province_records:
        match = province_lookup.get(rec["normalized_name"]) or province_lookup.get(
            rec["name"].lower().strip()
        )
        if match:
            province_matches.append(
                {
                    "province_id": match["province_id"],
                    "name": match["name"],
                    "centroid_lat": rec["centroid_lat"],
                    "centroid_lon": rec["centroid_lon"],
                    "area_km2": rec["area_km2"],
                    "source": "GeoJSON centroid",
                }
            )
        else:
            province_unmatched.append(rec)

    print(f"  Matched: {len(province_matches)}, Unmatched: {len(province_unmatched)}")
    if province_unmatched:
        print("  Unmatched provinces:")
        for u in province_unmatched[:10]:
            print(f"    {u['name']} (norm: {u['normalized_name']})")

    write_csv(
        OUTPUT_DIR / "geospatial_province_centroids.csv",
        province_matches,
        ["province_id", "name", "centroid_lat", "centroid_lon", "area_km2", "source"],
    )

    # --- Municipality centroids ---
    print("\n=== Processing municipality GeoJSON ===")
    muni_records = process_geojson(MUNICIPALITY_GEOJSON, "adm3_en")
    muni_lookup = build_municipality_lookup(client)

    muni_matches = []
    muni_unmatched = []
    for rec in muni_records:
        match = muni_lookup.get(rec["normalized_name"]) or muni_lookup.get(
            rec["name"].lower().strip()
        )
        if match:
            muni_matches.append(
                {
                    "municipality_id": match["municipality_id"],
                    "name": match["name"],
                    "province_id": match.get("province_id", ""),
                    "centroid_lat": rec["centroid_lat"],
                    "centroid_lon": rec["centroid_lon"],
                    "area_km2": rec["area_km2"],
                    "source": "GeoJSON centroid",
                }
            )
        else:
            muni_unmatched.append(rec)

    print(f"  Matched: {len(muni_matches)}, Unmatched: {len(muni_unmatched)}")
    if muni_unmatched:
        print(f"  (showing first 10 of {len(muni_unmatched)} unmatched)")
        for u in muni_unmatched[:10]:
            print(f"    {u['name']} (norm: {u['normalized_name']})")

    write_csv(
        OUTPUT_DIR / "geospatial_municipality_centroids.csv",
        muni_matches,
        [
            "municipality_id",
            "name",
            "province_id",
            "centroid_lat",
            "centroid_lon",
            "area_km2",
            "source",
        ],
    )

    # --- Summary ---
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"  Province centroids:  {len(province_matches)} matched")
    print(f"  Municipality centroids: {len(muni_matches)} matched")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"{'='*60}")
    print("\nNext step: Run insert_geospatial_metadata.py to insert into Supabase.")
    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `load_dotenv()`, `getenv()`, `SupabaseRestClient()`, `mkdir()`, `process_geojson()`.


## `scripts/identify_gaps.py`

**File:** `scripts/identify_gaps.py`

**Summary:** Identify municipalities from the GeoJSON map that are missing from Supabase

### `SupabaseRestClient.__init__`

- **File:** `scripts/identify_gaps.py`
- **Lines:** `21-27`
- **Signature:** `def __init__(self, base_url: str, api_key: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles   init  .

**Code:**
```python
def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
        }
        self.http = httpx.Client(timeout=30.0)
```

**Explanation:** It accepts `base_url`, `api_key`. See the code below for the full implementation. Key calls include `rstrip()`, `Client()`.

### `SupabaseRestClient.table`

- **File:** `scripts/identify_gaps.py`
- **Lines:** `29-30`
- **Signature:** `def table(self, table_name: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles table.

**Code:**
```python
def table(self, table_name: str):
        return SupabaseRestQuery(self, table_name)
```

**Explanation:** It accepts `table_name`. See the code below for the full implementation. Key calls include `SupabaseRestQuery()`.

### `SupabaseRestQuery.__init__`

- **File:** `scripts/identify_gaps.py`
- **Lines:** `34-41`
- **Signature:** `def __init__(self, client: SupabaseRestClient, table: str):`
- **Purpose:** Method of `SupabaseRestQuery` that handles   init  .

**Code:**
```python
def __init__(self, client: SupabaseRestClient, table: str):
        self._client = client
        self._table = table
        self._select_cols = "*"
        self._filters: list[tuple[str, str, str]] = []
        self._order: str | None = None
        self._range: tuple[int, int] | None = None
        self._not_null: list[str] = []
```

**Explanation:** It accepts `client`, `table`. See the code below for the full implementation.

### `SupabaseRestQuery.select`

- **File:** `scripts/identify_gaps.py`
- **Lines:** `43-45`
- **Signature:** `def select(self, columns: str = "*") -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles select.

**Code:**
```python
def select(self, columns: str = "*") -> "SupabaseRestQuery":
        self._select_cols = columns
        return self
```

**Explanation:** It accepts `columns` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.not_`

- **File:** `scripts/identify_gaps.py`
- **Lines:** `47-49`
- **Signature:** `def not_(self) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles not .

**Code:**
```python
def not_(self) -> "SupabaseRestQuery":
        self._not = True
        return self
```

**Explanation:** It accepts zero arguments and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.is_`

- **File:** `scripts/identify_gaps.py`
- **Lines:** `51-53`
- **Signature:** `def is_(self, column: str, value: str) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles is .

**Code:**
```python
def is_(self, column: str, value: str) -> "SupabaseRestQuery":
        self._filters.append((column, "is", str(value)))
        return self
```

**Explanation:** It accepts `column`, `value` and returns `'SupabaseRestQuery'`. See the code below for the full implementation. Key calls include `append()`, `str()`.

### `SupabaseRestQuery.eq`

- **File:** `scripts/identify_gaps.py`
- **Lines:** `55-57`
- **Signature:** `def eq(self, column: str, value: str | int) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles eq.

**Code:**
```python
def eq(self, column: str, value: str | int) -> "SupabaseRestQuery":
        self._filters.append((column, "eq", str(value)))
        return self
```

**Explanation:** It accepts `column`, `value` and returns `'SupabaseRestQuery'`. See the code below for the full implementation. Key calls include `append()`, `str()`.

### `SupabaseRestQuery.order`

- **File:** `scripts/identify_gaps.py`
- **Lines:** `59-61`
- **Signature:** `def order(self, column: str, desc: bool = False) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles order.

**Code:**
```python
def order(self, column: str, desc: bool = False) -> "SupabaseRestQuery":
        self._order = f"{column}.{'desc' if desc else 'asc'}"
        return self
```

**Explanation:** It accepts `column`, `desc` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.range`

- **File:** `scripts/identify_gaps.py`
- **Lines:** `63-65`
- **Signature:** `def range(self, start: int, end: int) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles range.

**Code:**
```python
def range(self, start: int, end: int) -> "SupabaseRestQuery":
        self._range = (start, end)
        return self
```

**Explanation:** It accepts `start`, `end` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.execute`

- **File:** `scripts/identify_gaps.py`
- **Lines:** `67-82`
- **Signature:** `def execute(self):`
- **Purpose:** Method of `SupabaseRestQuery` that handles execute.

**Code:**
```python
def execute(self):
        params: dict[str, str] = {"select": self._select_cols}
        for column, op, value in self._filters:
            if op == "is":
                params[column] = f"is.{value}"
            else:
                params[column] = f"{op}.{value}"
        if self._order:
            params["order"] = self._order
        url = f"{self._client.base_url}/rest/v1/{self._table}"
        headers = dict(self._client.headers)
        if self._range:
            headers["Range"] = f"{self._range[0]}-{self._range[1]}"
        response = self._client.http.get(url, params=params, headers=headers)
        response.raise_for_status()
        return type("Response", (), {"data": response.json()})()
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `dict()`, `get()`, `raise_for_status()`, `type()`, `json()`.

### `compute_centroid`

- **File:** `scripts/identify_gaps.py`
- **Lines:** `89-104`
- **Signature:** `def compute_centroid(geometry: dict) -> tuple[float, float]:`
- **Purpose:** Computes centroid.

**Code:**
```python
def compute_centroid(geometry: dict) -> tuple[float, float]:
    coords = geometry.get("coordinates", [])
    lats, lons = [], []

    def visit(c):
        if isinstance(c[0], list):
            for sub in c:
                visit(sub)
        else:
            lons.append(c[0])
            lats.append(c[1])

    visit(coords)
    if not lats:
        return 0.0, 0.0
    return sum(lats) / len(lats), sum(lons) / len(lons)
```

**Explanation:** It accepts `geometry` and returns `tuple[float, float]`. See the code below for the full implementation. Key calls include `get()`, `isinstance()`, `append()`, `visit()`, `sum()`.

### `load_geojson_municipalities`

- **File:** `scripts/identify_gaps.py`
- **Lines:** `107-123`
- **Signature:** `def load_geojson_municipalities() -> list[dict]:`
- **Purpose:** Loads geojson municipalities.

**Code:**
```python
def load_geojson_municipalities() -> list[dict]:
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        geom = feat.get("geometry")
        lat, lon = compute_centroid(geom) if geom else (0.0, 0.0)
        results.append({
            "geo_name": props.get("adm3_en", ""),
            "geo_province_psgc": props.get("adm2_psgc"),
            "geo_municipality_psgc": props.get("adm3_psgc"),
            "lat": round(lat, 6),
            "lon": round(lon, 6),
        })
    return results
```

**Explanation:** It accepts zero arguments and returns `list[dict]`. See the code below for the full implementation. Key calls include `open()`, `load()`, `get()`, `append()`, `compute_centroid()`.

### `fetch_all_municipalities_from_db`

- **File:** `scripts/identify_gaps.py`
- **Lines:** `126-149`
- **Signature:** `def fetch_all_municipalities_from_db(client) -> list[dict]:`
- **Purpose:** Fetches all municipalities from db.

**Code:**
```python
def fetch_all_municipalities_from_db(client) -> list[dict]:
    all_rows = []
    offset = 0
    batch = 1000
    while True:
        resp = (
            client.table("municipalities")
            .select(
                "municipality_id, province_id, name, lat, lon, "
                "solar_suitability_score, wind_suitability_score, "
                "hydro_suitability_score, geothermal_suitability_score, "
                "composite_suitability_score"
            )
            .range(offset, offset + batch - 1)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < batch:
            break
        offset += batch
    return all_rows
```

**Explanation:** It accepts `client` and returns `list[dict]`. See the code below for the full implementation. Key calls include `execute()`, `extend()`, `len()`, `range()`, `select()`.

### `main`

- **File:** `scripts/identify_gaps.py`
- **Lines:** `152-272`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    load_dotenv(dotenv_path=REPO_ROOT / ".env", override=False)
    url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_KEY")
        or os.getenv("VITE_SUPABASE_ANON_KEY")
    )
    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required", file=sys.stderr)
        return 1

    client = SupabaseRestClient(url, key)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    geo_munis = load_geojson_municipalities()
    print(f"GeoJSON municipalities: {len(geo_munis)}")

    db_munis = fetch_all_municipalities_from_db(client)
    print(f"DB municipalities:      {len(db_munis)}")

    # Build lookup by municipality_id (PSGC)
    db_by_id = {row["municipality_id"]: row for row in db_munis}

    # Also build by normalized name for fuzzy matching
    def norm(name: str) -> str:
        import re as _re
        n = name.lower().strip()
        # Strip parenthetical aliases: "paranas (wright)" -> "paranas"
        n = _re.sub(r'\s*\([^)]*\)\s*', ' ', n).strip()
        for prefix in ("city of ", "municipality of ", "province of "):
            if n.startswith(prefix):
                n = n[len(prefix):]
        for suffix in (" city", " municipality"):
            if n.endswith(suffix):
                n = n[: -len(suffix)]
        # Common aliases
        aliases = {
            "gen. s.k. pendatun": "general salipada k. pendatun",
            "pi v. corpuz": "pio v. corpuz",
            "muñoz": "munoz",
            "science city of muñoz": "munoz",
        }
        return aliases.get(n, n)

    db_by_name = {norm(row["name"]): row for row in db_munis if row.get("name")}

    missing_from_db = []
    null_scores = []
    has_data = []

    for gm in geo_munis:
        psgc = gm["geo_municipality_psgc"]
        db_row = db_by_id.get(psgc)

        if not db_row:
            # Try fuzzy name match
            db_row = db_by_name.get(norm(gm["geo_name"]))

        if not db_row:
            missing_from_db.append({
                "geo_name": gm["geo_name"],
                "geo_psgc": psgc,
                "geo_province_psgc": gm["geo_province_psgc"],
                "lat": gm["lat"],
                "lon": gm["lon"],
            })
            continue

        scores = [
            db_row.get("solar_suitability_score"),
            db_row.get("wind_suitability_score"),
            db_row.get("hydro_suitability_score"),
            db_row.get("geothermal_suitability_score"),
            db_row.get("composite_suitability_score"),
        ]
        has_any_score = any(s is not None for s in scores)

        if has_any_score:
            has_data.append({
                "municipality_id": db_row["municipality_id"],
                "name": db_row.get("name"),
                "lat": db_row.get("lat"),
                "lon": db_row.get("lon"),
                "solar_score": db_row.get("solar_suitability_score"),
                "wind_score": db_row.get("wind_suitability_score"),
                "hydro_score": db_row.get("hydro_suitability_score"),
                "geo_score": db_row.get("geothermal_suitability_score"),
                "composite_score": db_row.get("composite_suitability_score"),
            })
        else:
            null_scores.append({
                "municipality_id": db_row["municipality_id"],
                "name": db_row.get("name"),
                "lat": db_row.get("lat"),
                "lon": db_row.get("lon"),
            })

    # Write CSVs
    def write_csv(path, rows, fieldnames):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    write_csv(OUTPUT_DIR / "missing_from_db.csv", missing_from_db,
              ["geo_name", "geo_psgc", "geo_province_psgc", "lat", "lon"])
    write_csv(OUTPUT_DIR / "null_scores.csv", null_scores,
              ["municipality_id", "name", "lat", "lon"])
    write_csv(OUTPUT_DIR / "has_data.csv", has_data,
              ["municipality_id", "name", "lat", "lon",
               "solar_score", "wind_score", "hydro_score", "geo_score", "composite_score"])

    print(f"\n{'='*60}")
    print(f"Missing from DB:        {len(missing_from_db)}")
    print(f"In DB but NULL scores:  {len(null_scores)}")
    print(f"In DB with data:        {len(has_data)}")
    print(f"{'='*60}")
    print(f"Output written to: {OUTPUT_DIR}")
    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `load_dotenv()`, `getenv()`, `SupabaseRestClient()`, `mkdir()`, `load_geojson_municipalities()`.


## `scripts/insert_from_csvs.py`

**File:** `scripts/insert_from_csvs.py`

**Summary:** Insert missing geographic entries from CSVs into Supabase.

### `SupabaseRestClient.__init__`

- **File:** `scripts/insert_from_csvs.py`
- **Lines:** `27-35`
- **Signature:** `def __init__(self, base_url: str, api_key: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles   init  .

**Code:**
```python
def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        }
        self.http = httpx.Client(timeout=60.0)
```

**Explanation:** It accepts `base_url`, `api_key`. See the code below for the full implementation. Key calls include `rstrip()`, `Client()`.

### `SupabaseRestClient.insert_batch`

- **File:** `scripts/insert_from_csvs.py`
- **Lines:** `37-49`
- **Signature:** `def insert_batch(self, table: str, rows: list[dict]) -> tuple[int, str]:`
- **Purpose:** Method of `SupabaseRestClient` that inserts batch.

**Code:**
```python
def insert_batch(self, table: str, rows: list[dict]) -> tuple[int, str]:
        if not rows:
            return 0, ""
        url = f"{self.base_url}/rest/v1/{table}"
        try:
            resp = self.http.post(url, json=rows, headers=self.headers)
            resp.raise_for_status()
            return len(rows), ""
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500] if exc.response else ""
            return 0, f"HTTP {exc.response.status_code}: {body}"
        except Exception as exc:
            return 0, str(exc)
```

**Explanation:** It accepts `table`, `rows` and returns `tuple[int, str]`. See the code below for the full implementation. Key calls include `post()`, `raise_for_status()`, `len()`, `str()`.

### `read_csv`

- **File:** `scripts/insert_from_csvs.py`
- **Lines:** `52-57`
- **Signature:** `def read_csv(path: Path) -> list[dict]:`
- **Purpose:** Reads csv.

**Code:**
```python
def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)
```

**Explanation:** It accepts `path` and returns `list[dict]`. See the code below for the full implementation. Key calls include `exists()`, `open()`, `DictReader()`, `list()`.

### `main`

- **File:** `scripts/insert_from_csvs.py`
- **Lines:** `60-169`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    load_dotenv(dotenv_path=REPO_ROOT / ".env", override=False)

    url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_KEY")
        or os.getenv("VITE_SUPABASE_ANON_KEY")
    )
    if not url or not key:
        print("ERROR: Missing Supabase credentials", file=sys.stderr)
        return 1

    client = SupabaseRestClient(url, key)
    batch_size = 500
    total_inserted = 0

    # --- 1. Regions ---
    print("Reading missing_regions.csv...")
    regions = read_csv(GAP_DIR / "missing_regions.csv")
    print(f"  {len(regions)} regions to insert")
    inserted = 0
    for i in range(0, len(regions), batch_size):
        batch = regions[i : i + batch_size]
        # Convert types
        rows = [{"region_id": int(r["region_id"]), "name": r["name"]} for r in batch]
        count, err = client.insert_batch("regions", rows)
        inserted += count
        if err:
            print(f"  Batch {i // batch_size + 1} error: {err}")
        else:
            print(f"  Batch {i // batch_size + 1}: {count} inserted")
    total_inserted += inserted
    print(f"  Regions inserted: {inserted}")

    # --- 2. Provinces ---
    print("\nReading missing_provinces.csv...")
    provinces = read_csv(GAP_DIR / "missing_provinces.csv")
    print(f"  {len(provinces)} provinces to insert")
    inserted = 0
    for i in range(0, len(provinces), batch_size):
        batch = provinces[i : i + batch_size]
        rows = [
            {"province_id": int(p["province_id"]), "region_id": int(p["region_id"]), "name": p["name"]}
            for p in batch
        ]
        count, err = client.insert_batch("provinces", rows)
        inserted += count
        if err:
            print(f"  Batch {i // batch_size + 1} error: {err}")
        else:
            print(f"  Batch {i // batch_size + 1}: {count} inserted")
    total_inserted += inserted
    print(f"  Provinces inserted: {inserted}")

    # --- 3. Municipalities ---
    print("\nReading missing_municipalities.csv...")
    munis = read_csv(GAP_DIR / "missing_municipalities.csv")
    print(f"  {len(munis)} municipalities to insert")
    inserted = 0
    for i in range(0, len(munis), batch_size):
        batch = munis[i : i + batch_size]
        rows = [
            {
                "municipality_id": int(m["municipality_id"]),
                "province_id": int(m["province_id"]),
                "name": m["name"],
            }
            for m in batch
        ]
        count, err = client.insert_batch("municipalities", rows)
        inserted += count
        if err:
            print(f"  Batch {i // batch_size + 1} error: {err}")
        else:
            print(f"  Batch {i // batch_size + 1}: {count} inserted")
    total_inserted += inserted
    print(f"  Municipalities inserted: {inserted}")

    # --- 4. Barangays ---
    print("\nReading missing_barangays.csv...")
    barangays = read_csv(GAP_DIR / "missing_barangays.csv")
    print(f"  {len(barangays)} barangays to insert")
    inserted = 0
    # Smaller batches for barangays due to volume
    brgy_batch = 200
    for i in range(0, len(barangays), brgy_batch):
        batch = barangays[i : i + brgy_batch]
        rows = [
            {
                "barangay_id": int(b["barangay_id"]),
                "municipality_id": int(b["municipality_id"]),
                "name": b["name"],
            }
            for b in batch
        ]
        count, err = client.insert_batch("barangays", rows)
        inserted += count
        if err:
            print(f"  Batch {i // brgy_batch + 1} error: {err}")
        else:
            print(f"  Batch {i // brgy_batch + 1}: {count} inserted")
    total_inserted += inserted
    print(f"  Barangays inserted: {inserted}")

    print(f"\n{'='*60}")
    print(f"TOTAL INSERTED: {total_inserted}")
    print(f"{'='*60}")
    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `load_dotenv()`, `getenv()`, `SupabaseRestClient()`, `read_csv()`, `len()`.


## `scripts/insert_geospatial_metadata.py`

**File:** `scripts/insert_geospatial_metadata.py`

**Summary:** Insert geospatial metadata from CSVs into Supabase.

### `SupabaseRestClient.__init__`

- **File:** `scripts/insert_geospatial_metadata.py`
- **Lines:** `24-32`
- **Signature:** `def __init__(self, base_url: str, api_key: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles   init  .

**Code:**
```python
def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        }
        self.http = httpx.Client(timeout=60.0)
```

**Explanation:** It accepts `base_url`, `api_key`. See the code below for the full implementation. Key calls include `rstrip()`, `Client()`.

### `SupabaseRestClient.upsert_batch`

- **File:** `scripts/insert_geospatial_metadata.py`
- **Lines:** `34-46`
- **Signature:** `def upsert_batch(self, table: str, rows: list[dict]) -> tuple[int, str]:`
- **Purpose:** Method of `SupabaseRestClient` that upserts batch.

**Code:**
```python
def upsert_batch(self, table: str, rows: list[dict]) -> tuple[int, str]:
        if not rows:
            return 0, ""
        url = f"{self.base_url}/rest/v1/{table}"
        try:
            resp = self.http.post(url, json=rows, headers=self.headers)
            resp.raise_for_status()
            return len(rows), ""
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500] if exc.response else ""
            return 0, f"HTTP {exc.response.status_code}: {body}"
        except Exception as exc:
            return 0, str(exc)
```

**Explanation:** It accepts `table`, `rows` and returns `tuple[int, str]`. See the code below for the full implementation. Key calls include `post()`, `raise_for_status()`, `len()`, `str()`.

### `SupabaseRestClient.fetch_existing_keys`

- **File:** `scripts/insert_geospatial_metadata.py`
- **Lines:** `48-71`
- **Signature:** `def fetch_existing_keys(self, table: str, select: str) -> set[str]:`
- **Purpose:** Fetch existing geo keys to skip duplicates.

**Code:**
```python
def fetch_existing_keys(self, table: str, select: str) -> set[str]:
        """Fetch existing geo keys to skip duplicates."""
        rows = []
        offset = 0
        batch = 1000
        while True:
            url = f"{self.base_url}/rest/v1/{table}"
            params = {"select": select, "limit": str(batch), "offset": str(offset)}
            resp = self.http.get(url, params=params, headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                break
            rows.extend(data)
            if len(data) < batch:
                break
            offset += batch
        keys = set()
        for r in rows:
            for col in ["region_id", "province_id", "municipality_id", "barangay_id"]:
                val = r.get(col)
                if val is not None:
                    keys.add(f"{col}:{val}")
        return keys
```

**Explanation:** It accepts `table`, `select` and returns `set[str]`. See the code below for the full implementation. Key calls include `get()`, `raise_for_status()`, `json()`, `extend()`, `str()`.

### `read_csv`

- **File:** `scripts/insert_geospatial_metadata.py`
- **Lines:** `74-79`
- **Signature:** `def read_csv(path: Path) -> list[dict]:`
- **Purpose:** Reads csv.

**Code:**
```python
def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)
```

**Explanation:** It accepts `path` and returns `list[dict]`. See the code below for the full implementation. Key calls include `exists()`, `open()`, `DictReader()`, `list()`.

### `main`

- **File:** `scripts/insert_geospatial_metadata.py`
- **Lines:** `82-191`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    load_dotenv(dotenv_path=REPO_ROOT / ".env", override=False)

    url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_KEY")
        or os.getenv("VITE_SUPABASE_ANON_KEY")
    )
    if not url or not key:
        print("ERROR: Missing Supabase credentials", file=sys.stderr)
        return 1

    client = SupabaseRestClient(url, key)
    batch_size = 500
    total_inserted = 0

    # Check existing entries to avoid duplicates
    print("Fetching existing geospatial_metadata keys...")
    try:
        existing_keys = client.fetch_existing_keys(
            "geospatial_metadata",
            "region_id,province_id,municipality_id,barangay_id",
        )
        print(f"  {len(existing_keys)} existing entries")
    except Exception as exc:
        print(f"  Warning: could not fetch existing keys ({exc}), will attempt all")
        existing_keys = set()

    # --- Province centroids ---
    print("\n--- Province centroids ---")
    provinces = read_csv(GAP_DIR / "geospatial_province_centroids.csv")
    print(f"  {len(provinces)} rows in CSV")

    rows = []
    skipped = 0
    for p in provinces:
        pid = int(p["province_id"])
        geo_key = f"province_id:{pid}"
        if geo_key in existing_keys:
            skipped += 1
            continue
        rows.append(
            {
                "province_id": pid,
                "centroid_lat": float(p["centroid_lat"]),
                "centroid_lon": float(p["centroid_lon"]),
                "area_km2": float(p["area_km2"]) if p.get("area_km2") else None,
                "source": p.get("source", "GeoJSON centroid"),
            }
        )

    print(f"  Skipped (already exist): {skipped}")
    print(f"  To insert: {len(rows)}")

    inserted = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        count, err = client.upsert_batch("geospatial_metadata", batch)
        inserted += count
        if err:
            print(f"  Batch {i // batch_size + 1} error: {err}")
        else:
            print(f"  Batch {i // batch_size + 1}: {count} inserted")
    total_inserted += inserted
    print(f"  Province centroids inserted: {inserted}")

    # --- Municipality centroids ---
    print("\n--- Municipality centroids ---")
    munis = read_csv(GAP_DIR / "geospatial_municipality_centroids.csv")
    print(f"  {len(munis)} rows in CSV")

    rows = []
    skipped = 0
    for m in munis:
        mid = int(m["municipality_id"])
        geo_key = f"municipality_id:{mid}"
        if geo_key in existing_keys:
            skipped += 1
            continue
        rows.append(
            {
                "municipality_id": mid,
                "centroid_lat": float(m["centroid_lat"]),
                "centroid_lon": float(m["centroid_lon"]),
                "area_km2": float(m["area_km2"]) if m.get("area_km2") else None,
                "source": m.get("source", "GeoJSON centroid"),
            }
        )

    print(f"  Skipped (already exist): {skipped}")
    print(f"  To insert: {len(rows)}")

    inserted = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        count, err = client.upsert_batch("geospatial_metadata", batch)
        inserted += count
        if err:
            print(f"  Batch {i // batch_size + 1} error: {err}")
        else:
            print(f"  Batch {i // batch_size + 1}: {count} inserted")
    total_inserted += inserted
    print(f"  Municipality centroids inserted: {inserted}")

    print(f"\n{'='*60}")
    print(f"TOTAL INSERTED: {total_inserted}")
    print(f"{'='*60}")
    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `load_dotenv()`, `getenv()`, `SupabaseRestClient()`, `fetch_existing_keys()`, `set()`.


## `scripts/insert_missing_municipalities.py`

**File:** `scripts/insert_missing_municipalities.py`

**Summary:** Insert missing municipalities from GeoJSON into Supabase municipalities table.

### `load_province_name_by_psgc`

- **File:** `scripts/insert_missing_municipalities.py`
- **Lines:** `17-28`
- **Signature:** `def load_province_name_by_psgc() -> dict[int, str]:`
- **Purpose:** Loads province name by psgc.

**Code:**
```python
def load_province_name_by_psgc() -> dict[int, str]:
    import json
    with open(PROVINCE_GEOJSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    mapping = {}
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        psgc = props.get("adm2_psgc")
        name = props.get("adm2_en")
        if psgc and name:
            mapping[int(psgc)] = name
    return mapping
```

**Explanation:** It accepts zero arguments and returns `dict[int, str]`. See the code below for the full implementation. Key calls include `open()`, `load()`, `get()`, `int()`.

### `SupabaseRestClient.__init__`

- **File:** `scripts/insert_missing_municipalities.py`
- **Lines:** `32-40`
- **Signature:** `def __init__(self, base_url: str, api_key: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles   init  .

**Code:**
```python
def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        }
        self.http = httpx.Client(timeout=30.0)
```

**Explanation:** It accepts `base_url`, `api_key`. See the code below for the full implementation. Key calls include `rstrip()`, `Client()`.

### `SupabaseRestClient.table`

- **File:** `scripts/insert_missing_municipalities.py`
- **Lines:** `42-43`
- **Signature:** `def table(self, table_name: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles table.

**Code:**
```python
def table(self, table_name: str):
        return SupabaseRestQuery(self, table_name)
```

**Explanation:** It accepts `table_name`. See the code below for the full implementation. Key calls include `SupabaseRestQuery()`.

### `SupabaseRestQuery.__init__`

- **File:** `scripts/insert_missing_municipalities.py`
- **Lines:** `47-53`
- **Signature:** `def __init__(self, client: SupabaseRestClient, table: str):`
- **Purpose:** Method of `SupabaseRestQuery` that handles   init  .

**Code:**
```python
def __init__(self, client: SupabaseRestClient, table: str):
        self._client = client
        self._table = table
        self._select_cols = "*"
        self._filters: list[tuple[str, str, str]] = []
        self._order: str | None = None
        self._range: tuple[int, int] | None = None
```

**Explanation:** It accepts `client`, `table`. See the code below for the full implementation.

### `SupabaseRestQuery.select`

- **File:** `scripts/insert_missing_municipalities.py`
- **Lines:** `55-57`
- **Signature:** `def select(self, columns: str = "*") -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles select.

**Code:**
```python
def select(self, columns: str = "*") -> "SupabaseRestQuery":
        self._select_cols = columns
        return self
```

**Explanation:** It accepts `columns` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.eq`

- **File:** `scripts/insert_missing_municipalities.py`
- **Lines:** `59-61`
- **Signature:** `def eq(self, column: str, value: str | int) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles eq.

**Code:**
```python
def eq(self, column: str, value: str | int) -> "SupabaseRestQuery":
        self._filters.append((column, "eq", str(value)))
        return self
```

**Explanation:** It accepts `column`, `value` and returns `'SupabaseRestQuery'`. See the code below for the full implementation. Key calls include `append()`, `str()`.

### `SupabaseRestQuery.order`

- **File:** `scripts/insert_missing_municipalities.py`
- **Lines:** `63-65`
- **Signature:** `def order(self, column: str, desc: bool = False) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles order.

**Code:**
```python
def order(self, column: str, desc: bool = False) -> "SupabaseRestQuery":
        self._order = f"{column}.{'desc' if desc else 'asc'}"
        return self
```

**Explanation:** It accepts `column`, `desc` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.range`

- **File:** `scripts/insert_missing_municipalities.py`
- **Lines:** `67-69`
- **Signature:** `def range(self, start: int, end: int) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles range.

**Code:**
```python
def range(self, start: int, end: int) -> "SupabaseRestQuery":
        self._range = (start, end)
        return self
```

**Explanation:** It accepts `start`, `end` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.insert`

- **File:** `scripts/insert_missing_municipalities.py`
- **Lines:** `71-73`
- **Signature:** `def insert(self, rows: list[dict]) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles insert.

**Code:**
```python
def insert(self, rows: list[dict]) -> "SupabaseRestQuery":
        self._rows = rows
        return self
```

**Explanation:** It accepts `rows` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.execute`

- **File:** `scripts/insert_missing_municipalities.py`
- **Lines:** `75-95`
- **Signature:** `def execute(self):`
- **Purpose:** Method of `SupabaseRestQuery` that handles execute.

**Code:**
```python
def execute(self):
        if hasattr(self, "_rows"):
            # INSERT path
            url = f"{self._client.base_url}/rest/v1/{self._table}"
            response = self._client.http.post(url, json=self._rows, headers=self._client.headers)
            response.raise_for_status()
            return type("Response", (), {"data": response.json() if response.text else []})()

        # SELECT path
        params: dict[str, str] = {"select": self._select_cols}
        for column, op, value in self._filters:
            params[column] = f"{op}.{value}"
        if self._order:
            params["order"] = self._order
        url = f"{self._client.base_url}/rest/v1/{self._table}"
        headers = dict(self._client.headers)
        if self._range:
            headers["Range"] = f"{self._range[0]}-{self._range[1]}"
        response = self._client.http.get(url, params=params, headers=headers)
        response.raise_for_status()
        return type("Response", (), {"data": response.json()})()
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `hasattr()`, `post()`, `raise_for_status()`, `type()`, `json()`.

### `main`

- **File:** `scripts/insert_missing_municipalities.py`
- **Lines:** `98-177`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    load_dotenv(dotenv_path=REPO_ROOT / ".env", override=False)
    url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_KEY")
        or os.getenv("VITE_SUPABASE_ANON_KEY")
    )
    if not url or not key:
        print("ERROR: Missing Supabase credentials", file=sys.stderr)
        return 1

    if not CSV_PATH.exists():
        print(f"ERROR: {CSV_PATH} not found. Run identify_gaps.py first.", file=sys.stderr)
        return 1

    client = SupabaseRestClient(url, key)

    # Load province mapping
    province_psgc_to_name = load_province_name_by_psgc()
    print(f"Loaded {len(province_psgc_to_name)} provinces from GeoJSON")

    # Fetch DB provinces to map name -> province_id
    resp = client.table("provinces").select("province_id,name").execute()
    db_provinces = resp.data or []
    province_name_to_id = {}
    for p in db_provinces:
        name = p.get("name", "").strip().upper()
        province_name_to_id[name] = p["province_id"]
    print(f"Loaded {len(db_provinces)} provinces from DB")

    rows = []
    skipped = 0
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = row.get("geo_psgc")
            psgc = row.get("geo_province_psgc")
            if not mid:
                continue

            # Look up province name from PSGC, then map to DB province_id
            province_name = province_psgc_to_name.get(int(psgc)) if psgc else None
            province_id = province_name_to_id.get(province_name.upper()) if province_name else None

            if not province_id:
                print(f"  Warning: Cannot map province PSGC {psgc} for {row['geo_name']} — skipping")
                skipped += 1
                continue

            rows.append({
                "municipality_id": int(mid),
                "province_id": province_id,
                "name": row["geo_name"],
                "lat": float(row["lat"]) if row["lat"] else None,
                "lon": float(row["lon"]) if row["lon"] else None,
            })

    if not rows:
        print("No missing municipalities to insert.")
        return 0

    print(f"Inserting {len(rows)} missing municipalities...")
    batch_size = 100
    inserted = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        try:
            resp = client.table("municipalities").insert(batch).execute()
            inserted += len(batch)
            print(f"  Inserted batch {i//batch_size + 1}: {len(batch)} rows")
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500] if exc.response else ""
            print(f"  Batch {i//batch_size + 1} failed (status={exc.response.status_code}): {body}")
        except Exception as exc:
            print(f"  Batch {i//batch_size + 1} failed: {exc}")

    print(f"Done. Total inserted: {inserted}, Skipped: {skipped}")
    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `load_dotenv()`, `getenv()`, `exists()`, `SupabaseRestClient()`, `load_province_name_by_psgc()`.


## `scripts/migrate_csv_to_supabase.py`

**File:** `scripts/migrate_csv_to_supabase.py`

**Summary:** Migrate local CSV/GeoJSON datasets into Supabase.

### `_is_jwt_key`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `52-53`
- **Signature:** `def _is_jwt_key(key: str) -> bool:`
- **Purpose:** Handles  is jwt key.

**Code:**
```python
def _is_jwt_key(key: str) -> bool:
    return bool(key) and _JWT_PATTERN.match(key) is not None
```

**Explanation:** It accepts `key` and returns `bool`. See the code below for the full implementation. Key calls include `bool()`, `match()`.

### `_resolve_service_role_key`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `56-75`
- **Signature:** `def _resolve_service_role_key() -> str:`
- **Purpose:** Return a JWT-formatted key the supabase-py client can use.

**Code:**
```python
def _resolve_service_role_key() -> str:
    """Return a JWT-formatted key the supabase-py client can use.

    The environment may store either a real JWT (eyJ...) or a custom
    non-JWT identifier (sb_secret_...).  The official Supabase client
    requires a JWT, so fall back to the explicit JWT service role key.
    """
    for env_name in (
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_JWT_SERVICE_ROLE_KEY",
        "SUPABASE_ANON_KEY",
    ):
        value = os.environ.get(env_name)
        if value and _is_jwt_key(value):
            return value
    raise RuntimeError(
        "No JWT-formatted Supabase key found. "
        "Set SUPABASE_SERVICE_ROLE_KEY to a valid eyJ... JWT, or set "
        "SUPABASE_JWT_SERVICE_ROLE_KEY to the service_role JWT."
    )
```

**Explanation:** It accepts zero arguments and returns `str`. See the code below for the full implementation. Key calls include `get()`, `_is_jwt_key()`, `RuntimeError()`.

### `_get_client`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `78-79`
- **Signature:** `def _get_client() -> Client:`
- **Purpose:** Handles  get client.

**Code:**
```python
def _get_client() -> Client:
    return create_client(SUPABASE_URL, _resolve_service_role_key())
```

**Explanation:** It accepts zero arguments and returns `Client`. See the code below for the full implementation. Key calls include `create_client()`, `_resolve_service_role_key()`.

### `_normalize_text`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `110-111`
- **Signature:** `def _normalize_text(value: Any) -> str:`
- **Purpose:** Handles  normalize text.

**Code:**
```python
def _normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower())
```

**Explanation:** It accepts `value` and returns `str`. See the code below for the full implementation. Key calls include `sub()`, `lower()`, `strip()`, `str()`.

### `_sanitize_value`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `114-134`
- **Signature:** `def _sanitize_value(value: Any) -> Any:`
- **Purpose:** Replace NaN / inf floats with None and convert numpy scalars to Python types.

**Code:**
```python
def _sanitize_value(value: Any) -> Any:
    """Replace NaN / inf floats with None and convert numpy scalars to Python types."""
    if value is None:
        return None
    if isinstance(value, (np.integer, np.floating, np.bool_)):
        if pd.isna(value) or (isinstance(value, np.floating) and (np.isnan(value) or np.isinf(value))):
            return None
        return value.item()
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, (int, str, bool, list, dict)):
        return value
    # pandas / other scalar fallback
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value
```

**Explanation:** It accepts `value` and returns `Any`. See the code below for the full implementation. Key calls include `isinstance()`, `item()`, `isna()`, `isnan()`, `isinf()`.

### `_records_from_df`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `137-148`
- **Signature:** `def _records_from_df(df: pd.DataFrame) -> list[dict[str, Any]]:`
- **Purpose:** Return a list of dicts with native Python types and None instead of NaN/inf.

**Code:**
```python
def _records_from_df(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Return a list of dicts with native Python types and None instead of NaN/inf."""
    df = df.copy()
    df = df.replace([math.inf, -math.inf], math.nan)
    # Ensure ID-ish columns stay ints when possible
    for col in df.columns:
        if col in ("municipality_id", "id") or col.endswith("_id"):
            if df[col].dtype.kind == "f":
                df[col] = df[col].apply(lambda x: int(x) if pd.notnull(x) else None)

    records = df.to_dict(orient="records")
    return [{col: _sanitize_value(value) for col, value in row.items()} for row in records]
```

**Explanation:** It accepts `df` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `copy()`, `replace()`, `endswith()`, `apply()`, `notnull()`.

### `_fix_category`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `151-164`
- **Signature:** `def _fix_category(row: dict[str, Any]) -> str:`
- **Purpose:** Replicate products.py category correction logic.

**Code:**
```python
def _fix_category(row: dict[str, Any]) -> str:
    """Replicate products.py category correction logic."""
    cat = str(row.get("energy_category", "")).lower().strip()
    src = str(row.get("source_file", "")).lower()
    base = src.split("/")[-1].split("\\")[-1]
    if base.endswith("_hydro.csv") and cat == "wind":
        return "hydro"
    if base.endswith("_solar.csv") and cat != "solar":
        return "solar"
    if base.endswith("_wind.csv") and cat != "wind":
        return "wind"
    if base.endswith("_geothermal.csv") and cat != "geothermal":
        return "geothermal"
    return cat
```

**Explanation:** It accepts `row` and returns `str`. See the code below for the full implementation. Key calls include `strip()`, `lower()`, `str()`, `get()`, `split()`.

### `migrate_doe_datasets`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `199-216`
- **Signature:** `def migrate_doe_datasets(client: Client) -> None:`
- **Purpose:** Handles migrate doe datasets.

**Code:**
```python
def migrate_doe_datasets(client: Client) -> None:
    logger.info("Migrating DOE datasets into doe_datasets")
    for rel_path in DOE_CSVS:
        csv_path = ROOT / rel_path
        if not csv_path.exists():
            logger.warning("Skipping missing CSV: %s", rel_path)
            continue
        dataset_name = rel_path
        df = pd.read_csv(csv_path)
        records = _records_from_df(df)
        payload = {
            "dataset_name": dataset_name,
            "row_count": len(records),
            "data": records,
            "updated_at": "now()",
        }
        client.table("doe_datasets").upsert(payload, on_conflict="dataset_name").execute()
        logger.info("  -> %s: %s rows", dataset_name, len(records))
```

**Explanation:** It accepts `client` and returns `None`. See the code below for the full implementation. Key calls include `info()`, `read_csv()`, `_records_from_df()`, `execute()`, `exists()`.

### `_valid_municipality_ids`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `224-226`
- **Signature:** `def _valid_municipality_ids(client: Client) -> set[int]:`
- **Purpose:** Handles  valid municipality ids.

**Code:**
```python
def _valid_municipality_ids(client: Client) -> set[int]:
    resp = client.table("municipalities").select("municipality_id").execute()
    return {int(r["municipality_id"]) for r in (resp.data or []) if r.get("municipality_id") is not None}
```

**Explanation:** It accepts `client` and returns `set[int]`. See the code below for the full implementation. Key calls include `execute()`, `select()`, `table()`, `int()`, `get()`.

### `migrate_climate`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `229-244`
- **Signature:** `def migrate_climate(client: Client) -> None:`
- **Purpose:** Handles migrate climate.

**Code:**
```python
def migrate_climate(client: Client) -> None:
    csv_path = ROOT / "fastapi-backend/app/services/local_data/municipality_climate_averages.csv"
    df = pd.read_csv(csv_path)
    records = _records_from_df(df)
    valid_ids = _valid_municipality_ids(client)
    filtered = [r for r in records if r.get("municipality_id") in valid_ids]
    skipped = len(records) - len(filtered)
    if skipped:
        logger.warning("  -> skipped %s climate rows without matching municipalities", skipped)

    for i in range(0, len(filtered), 500):
        batch = filtered[i : i + 500]
        client.table("municipality_climate_averages").upsert(
            batch, on_conflict="municipality_id"
        ).execute()
    logger.info("Migrated municipality_climate_averages: %s rows", len(filtered))
```

**Explanation:** It accepts `client` and returns `None`. See the code below for the full implementation. Key calls include `read_csv()`, `_records_from_df()`, `_valid_municipality_ids()`, `get()`, `len()`.

### `migrate_products`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `252-267`
- **Signature:** `def migrate_products(client: Client) -> None:`
- **Purpose:** Handles migrate products.

**Code:**
```python
def migrate_products(client: Client) -> None:
    csv_path = ROOT / "fastapi-backend/app/services/local_data/products.csv"
    df = pd.read_csv(csv_path)
    df["energy_category"] = df.apply(
        lambda row: _fix_category(row.to_dict()), axis=1
    )
    records = _records_from_df(df)
    # Source-of-truth refresh: delete existing rows then re-insert
    try:
        client.table("products").delete().neq("id", 0).execute()
    except Exception as exc:
        logger.warning("Could not clear products table (may be empty): %s", exc)

    for i in range(0, len(records), 500):
        client.table("products").insert(records[i : i + 500]).execute()
    logger.info("Migrated products: %s rows", len(records))
```

**Explanation:** It accepts `client` and returns `None`. See the code below for the full implementation. Key calls include `read_csv()`, `apply()`, `_fix_category()`, `to_dict()`, `_records_from_df()`.

### `_compute_wind_summary`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `280-304`
- **Signature:** `def _compute_wind_summary(df: pd.DataFrame) -> dict[str, Any]:`
- **Purpose:** Handles  compute wind summary.

**Code:**
```python
def _compute_wind_summary(df: pd.DataFrame) -> dict[str, Any]:
    df = df.copy()
    df["rotor_radius_m"] = pd.to_numeric(df["rotor_radius_m"], errors="coerce")
    df["power_coefficient"] = pd.to_numeric(df["power_coefficient"], errors="coerce")

    rotor_series = df["rotor_radius_m"].dropna()
    cp_series = df["power_coefficient"].dropna()

    avg_rotor = float(rotor_series.mean()) if not rotor_series.empty else 0.0
    avg_cp = float(cp_series.mean()) if not cp_series.empty else 0.0

    return {
        "avg_rotor_radius_m": avg_rotor,
        "avg_power_coefficient": avg_cp * 100,  # matches wind_output_calc.py output
        "rotor_count": int(len(rotor_series)),
        "cp_count": int(len(cp_series)),
        "summary_rotor": (
            f"Average rotor radius (m): {avg_rotor:.3f} from {len(rotor_series)} rows "
            f"where a blade diameter was parsed from text (m/cm/mm/in/ft), then divided by 2."
        ),
        "summary_cp": (
            f"Average power coefficient: {avg_cp:.3f} from {len(cp_series)} rows with both parsed power "
            f"(W/kW/MW) and diameter; uses Cp = P / (0.5 * 1.225 * A * V^3) with V=12.0 m/s unless a m/s value is present."
        ),
    }
```

**Explanation:** It accepts `df` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `copy()`, `to_numeric()`, `dropna()`, `float()`, `mean()`.

### `migrate_wind`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `307-335`
- **Signature:** `def migrate_wind(client: Client) -> None:`
- **Purpose:** Handles migrate wind.

**Code:**
```python
def migrate_wind(client: Client) -> None:
    for rel_path, variant in WIND_CSVS:
        csv_path = ROOT / rel_path
        if not csv_path.exists():
            logger.warning("Wind CSV not found: %s", rel_path)
            continue
        df = pd.read_csv(csv_path)
        records = _records_from_df(df)

        # Source-of-truth refresh per variant
        try:
            client.table("wind_products").delete().eq("source_file", f"{variant}").execute()
        except Exception as exc:
            logger.warning("Could not clear wind_products for %s: %s", variant, exc)

        # source_file is a loose tag; keep the original column but also tag variant for deletion
        for rec in records:
            rec["source_file"] = variant

        for i in range(0, len(records), 500):
            client.table("wind_products").insert(records[i : i + 500]).execute()

        summary = _compute_wind_summary(df)
        summary["variant"] = variant
        summary["updated_at"] = "now()"
        client.table("wind_products_summary").upsert(
            summary, on_conflict="variant"
        ).execute()
        logger.info("Migrated wind products variant '%s': %s rows", variant, len(records))
```

**Explanation:** It accepts `client` and returns `None`. See the code below for the full implementation. Key calls include `read_csv()`, `_records_from_df()`, `range()`, `_compute_wind_summary()`, `execute()`.

### `migrate_geothermal`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `343-396`
- **Signature:** `def migrate_geothermal(client: Client) -> None:`
- **Purpose:** Handles migrate geothermal.

**Code:**
```python
def migrate_geothermal(client: Client) -> None:
    # Heat flow
    heat_path = ROOT / "fastapi-backend/app/services/local_data/geothermal_heatflow.csv"
    if heat_path.exists():
        df = pd.read_csv(heat_path)
        records = _records_from_df(df)
        try:
            client.table("geothermal_heatflow").delete().neq("id", 0).execute()
        except Exception as exc:
            logger.warning("Could not clear geothermal_heatflow: %s", exc)
        for i in range(0, len(records), 500):
            client.table("geothermal_heatflow").insert(records[i : i + 500]).execute()
        logger.info("Migrated geothermal_heatflow: %s rows", len(records))

    # Faults
    faults_path = ROOT / "fastapi-backend/app/services/local_data/geothermal_faults.json"
    if faults_path.exists():
        with open(faults_path, "r", encoding="utf-8") as f:
            faults = json.load(f)
        try:
            client.table("geothermal_faults").delete().neq("id", 0).execute()
        except Exception as exc:
            logger.warning("Could not clear geothermal_faults: %s", exc)
        records = [
            {
                "name": f.get("name"),
                "lat": _sanitize_value(f.get("lat")),
                "lon": _sanitize_value(f.get("lon")),
                "length_km": _sanitize_value(f.get("length_km")),
            }
            for f in faults
        ]
        client.table("geothermal_faults").insert(records).execute()
        logger.info("Migrated geothermal_faults: %s rows", len(records))

    # Volcanoes
    volcano_path = ROOT / "fastapi-backend/app/services/local_data/geothermal_volcanoes.json"
    if volcano_path.exists():
        with open(volcano_path, "r", encoding="utf-8") as f:
            volcanoes = json.load(f)
        try:
            client.table("geothermal_volcanoes").delete().neq("id", 0).execute()
        except Exception as exc:
            logger.warning("Could not clear geothermal_volcanoes: %s", exc)
        records = [
            {
                "name": v.get("name"),
                "lat": _sanitize_value(v.get("lat")),
                "lon": _sanitize_value(v.get("lon")),
            }
            for v in volcanoes
        ]
        client.table("geothermal_volcanoes").insert(records).execute()
        logger.info("Migrated geothermal_volcanoes: %s rows", len(records))
```

**Explanation:** It accepts `client` and returns `None`. See the code below for the full implementation. Key calls include `exists()`, `read_csv()`, `_records_from_df()`, `range()`, `info()`.

### `_extract_geojson_names`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `410-421`
- **Signature:** `def _extract_geojson_names(geojson_path: Path) -> dict[str, str]:`
- **Purpose:** Return {lower(adm2_en): adm2_en} from a GeoJSON feature collection.

**Code:**
```python
def _extract_geojson_names(geojson_path: Path) -> dict[str, str]:
    """Return {lower(adm2_en): adm2_en} from a GeoJSON feature collection."""
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    names: dict[str, str] = {}
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        name = props.get("adm2_en") or props.get("ADM2_EN")
        if name:
            key = name.strip().lower()
            names[key] = name.strip()
    return names
```

**Explanation:** It accepts `geojson_path` and returns `dict[str, str]`. See the code below for the full implementation. Key calls include `open()`, `load()`, `get()`, `lower()`, `strip()`.

### `_upload_storage_object`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `424-436`
- **Signature:** `def _upload_storage_object(client: Client, bucket: str, storage_path: str, local_path: Path) -> None:`
- **Purpose:** Handles  upload storage object.

**Code:**
```python
def _upload_storage_object(client: Client, bucket: str, storage_path: str, local_path: Path) -> None:
    content = local_path.read_bytes()
    file_options = {"content-type": "application/json"} if local_path.suffix == ".json" else {"content-type": "application/geo+json"}
    try:
        # Remove existing object first so the upload is idempotent
        try:
            client.storage.from_(bucket).remove([storage_path])
        except Exception:
            pass
        client.storage.from_(bucket).upload(storage_path, content, file_options=file_options)
        logger.info("  -> uploaded %s to %s/%s", local_path, bucket, storage_path)
    except Exception as exc:
        logger.error("Failed to upload %s to storage: %s", local_path, exc)
```

**Explanation:** It accepts `client`, `bucket`, `storage_path`, `local_path` and returns `None`. See the code below for the full implementation. Key calls include `read_bytes()`, `upload()`, `info()`, `remove()`, `error()`.

### `migrate_geojson`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `439-490`
- **Signature:** `def migrate_geojson(client: Client) -> None:`
- **Purpose:** Handles migrate geojson.

**Code:**
```python
def migrate_geojson(client: Client) -> None:
    bucket = "geojsons"
    try:
        client.storage.create_bucket(bucket, {"public": True})
    except Exception:
        logger.info("Storage bucket '%s' already exists or creation disabled", bucket)

    all_names: dict[str, str] = {}
    for rel_path, storage_name in GEOJSON_FILES:
        local_path = ROOT / rel_path
        if not local_path.exists():
            logger.warning("GeoJSON not found: %s", rel_path)
            continue
        _upload_storage_object(client, bucket, storage_name, local_path)
        if "province" in storage_name or "region" in storage_name:
            all_names.update(_extract_geojson_names(local_path))

    # Update provinces.geojson_name
    resp = client.table("provinces").select("province_id,name").execute()
    provinces = resp.data or []

    name_to_id: dict[str, int] = {}
    for p in provinces:
        name = str(p.get("name", "")).strip().lower()
        if name:
            name_to_id[name] = int(p["province_id"])

    updates = []
    for db_name_lower, province_id in name_to_id.items():
        matched = None
        if db_name_lower in all_names:
            matched = all_names[db_name_lower]
        else:
            mapped = _PROVINCE_NAME_MAP.get(db_name_lower)
            if mapped and mapped.strip():
                mapped_lower = mapped.strip().lower()
                if mapped_lower in all_names:
                    matched = all_names[mapped_lower]
        if matched:
            updates.append({"province_id": province_id, "geojson_name": matched})

    if updates:
        # Update geojson_name on the existing provinces table row by row.
        # Using .update avoids trying to insert rows and triggering NOT NULL
        # constraints on columns like region_id that we do not have here.
        for upd in updates:
            client.table("provinces").update(
                {"geojson_name": upd["geojson_name"]}
            ).eq("province_id", upd["province_id"]).execute()
        logger.info("Updated geojson_name for %s provinces", len(updates))
    else:
        logger.warning("No province names matched GeoJSON adm2_en values")
```

**Explanation:** It accepts `client` and returns `None`. See the code below for the full implementation. Key calls include `create_bucket()`, `info()`, `_upload_storage_object()`, `exists()`, `warning()`.

### `main`

- **File:** `scripts/migrate_csv_to_supabase.py`
- **Lines:** `498-507`
- **Signature:** `def main() -> None:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> None:
    client = _get_client()
    logger.info("Starting CSV/GeoJSON migration to Supabase")
    migrate_doe_datasets(client)
    migrate_climate(client)
    migrate_products(client)
    migrate_wind(client)
    migrate_geothermal(client)
    migrate_geojson(client)
    logger.info("Migration complete")
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `_get_client()`, `info()`, `migrate_doe_datasets()`, `migrate_climate()`, `migrate_products()`.


## `scripts/precompute_aquifer_scores.py`

**File:** `scripts/precompute_aquifer_scores.py`

**Summary:** Precompute aquifer scores for every municipality and write them into

### `_is_jwt_key`

- **File:** `scripts/precompute_aquifer_scores.py`
- **Lines:** `61-62`
- **Signature:** `def _is_jwt_key(key: str) -> bool:`
- **Purpose:** Handles  is jwt key.

**Code:**
```python
def _is_jwt_key(key: str) -> bool:
    return bool(key) and _JWT_PATTERN.match(key) is not None
```

**Explanation:** It accepts `key` and returns `bool`. See the code below for the full implementation. Key calls include `bool()`, `match()`.

### `_resolve_service_role_key`

- **File:** `scripts/precompute_aquifer_scores.py`
- **Lines:** `65-83`
- **Signature:** `def _resolve_service_role_key() -> str:`
- **Purpose:** Return a JWT-formatted key the supabase-py client can use.

**Code:**
```python
def _resolve_service_role_key() -> str:
    """Return a JWT-formatted key the supabase-py client can use.

    Falls back from SUPABASE_SERVICE_ROLE_KEY to the explicit
    SUPABASE_JWT_SERVICE_ROLE_KEY if the primary value is not a JWT.
    """
    for env_name in (
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_JWT_SERVICE_ROLE_KEY",
        "SUPABASE_ANON_KEY",
    ):
        value = os.environ.get(env_name)
        if value and _is_jwt_key(value):
            return value
    raise RuntimeError(
        "No JWT-formatted Supabase key found. "
        "Set SUPABASE_SERVICE_ROLE_KEY to a valid eyJ... JWT, or set "
        "SUPABASE_JWT_SERVICE_ROLE_KEY to the service_role JWT."
    )
```

**Explanation:** It accepts zero arguments and returns `str`. See the code below for the full implementation. Key calls include `get()`, `_is_jwt_key()`, `RuntimeError()`.

### `_get_client`

- **File:** `scripts/precompute_aquifer_scores.py`
- **Lines:** `86-87`
- **Signature:** `def _get_client() -> Client:`
- **Purpose:** Handles  get client.

**Code:**
```python
def _get_client() -> Client:
    return create_client(SUPABASE_URL, _resolve_service_role_key())
```

**Explanation:** It accepts zero arguments and returns `Client`. See the code below for the full implementation. Key calls include `create_client()`, `_resolve_service_role_key()`.

### `_load_aquifer_gdf`

- **File:** `scripts/precompute_aquifer_scores.py`
- **Lines:** `90-106`
- **Signature:** `def _load_aquifer_gdf() -> tuple[Any, Any]:`
- **Purpose:** Load the aquifer GeoJSON as a GeoDataFrame in EPSG:4326 and a metric CRS.

**Code:**
```python
def _load_aquifer_gdf() -> tuple[Any, Any]:
    """Load the aquifer GeoJSON as a GeoDataFrame in EPSG:4326 and a metric CRS."""
    try:
        import geopandas as gpd
    except ImportError as exc:
        raise RuntimeError(
            "geopandas is required for aquifer precomputation. "
            "Install it with: pip install geopandas"
        ) from exc

    gdf = gpd.read_file(AQUIFER_PATH)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    else:
        gdf = gdf.to_crs("EPSG:4326")
    gdf_projected = gdf.to_crs(AQUIFER_PROJECTED_CRS)
    return gdf, gdf_projected
```

**Explanation:** It accepts zero arguments and returns `tuple[Any, Any]`. See the code below for the full implementation. Key calls include `RuntimeError()`, `read_file()`, `set_crs()`, `to_crs()`.

### `_sanitize`

- **File:** `scripts/precompute_aquifer_scores.py`
- **Lines:** `109-116`
- **Signature:** `def _sanitize(value: Any) -> Any:`
- **Purpose:** Handles  sanitize.

**Code:**
```python
def _sanitize(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    return value
```

**Explanation:** It accepts `value` and returns `Any`. See the code below for the full implementation. Key calls include `isinstance()`, `isnan()`, `isinf()`.

### `_penalised_score`

- **File:** `scripts/precompute_aquifer_scores.py`
- **Lines:** `119-129`
- **Signature:** `def _penalised_score(raw_score: float | None, distance_km: float) -> float | None:`
- **Purpose:** Apply a linear distance decay so the score is conservative for fallback matches.

**Code:**
```python
def _penalised_score(raw_score: float | None, distance_km: float) -> float | None:
    """Apply a linear distance decay so the score is conservative for fallback matches.

    At 0 km from the polygon the raw score is kept; at the buffer edge it drops to 0.
    """
    if raw_score is None or raw_score <= 0.0:
        return None
    if AQUIFER_FALLBACK_BUFFER_KM <= 0:
        return raw_score
    factor = max(0.0, 1.0 - distance_km / AQUIFER_FALLBACK_BUFFER_KM)
    return round(max(0.0, min(1.0, raw_score * factor)), 6)
```

**Explanation:** It accepts `raw_score`, `distance_km` and returns `float | None`. See the code below for the full implementation. Key calls include `max()`, `round()`, `min()`.

### `_compute_aquifer_score`

- **File:** `scripts/precompute_aquifer_scores.py`
- **Lines:** `132-160`
- **Signature:** `def _compute_aquifer_score(props: dict[str, Any], stats: dict[str, Any]) -> float:`
- **Purpose:** Composite 0-1 aquifer score from porosity, permeability and thickness.

**Code:**
```python
def _compute_aquifer_score(props: dict[str, Any], stats: dict[str, Any]) -> float:
    """
    Composite 0-1 aquifer score from porosity, permeability and thickness.
    Higher values mean a more suitable aquifer for geothermal reinjection/storage.
    """
    porosity = _sanitize(props.get("porosity")) or 0.0
    perm_log10 = _sanitize(props.get("permeability_log10"))
    thickness = _sanitize(props.get("thickness_m")) or 0.0

    porosity_score = max(0.0, min(1.0, porosity))

    if perm_log10 is not None and stats.get("perm_range") is not None:
        pmin, pmax = stats["perm_range"]
        if pmax != pmin:
            perm_score = max(0.0, min(1.0, (perm_log10 - pmin) / (pmax - pmin)))
        else:
            perm_score = 0.0
    else:
        perm_score = 0.0

    thickness_min = stats.get("thickness_min", 0.0)
    thickness_max = stats.get("thickness_max", 1.0)
    denom = thickness_max - thickness_min if thickness_max != thickness_min else 1.0
    thickness_score = max(0.0, min(1.0, (thickness - thickness_min) / denom))

    # Weights: porosity most important for storage, permeability for flow,
    # thickness for reservoir volume.
    score = 0.4 * porosity_score + 0.3 * perm_score + 0.3 * thickness_score
    return round(max(0.0, min(1.0, score)), 6)
```

**Explanation:** It accepts `props`, `stats` and returns `float`. See the code below for the full implementation. Key calls include `_sanitize()`, `get()`, `max()`, `min()`, `round()`.

### `_aquifer_stats`

- **File:** `scripts/precompute_aquifer_scores.py`
- **Lines:** `163-179`
- **Signature:** `def _aquifer_stats(gdf: Any) -> dict[str, Any]:`
- **Purpose:** Pre-compute normalisation bounds from the aquifer dataset.

**Code:**
```python
def _aquifer_stats(gdf: Any) -> dict[str, Any]:
    """Pre-compute normalisation bounds from the aquifer dataset."""
    perms = [
        float(row["permeability_log10"])
        for _, row in gdf.iterrows()
        if pd.notnull(row.get("permeability_log10"))
    ]
    thicknesses = [
        float(row["thickness_m"])
        for _, row in gdf.iterrows()
        if pd.notnull(row.get("thickness_m"))
    ]
    return {
        "perm_range": (min(perms), max(perms)) if perms else (0.0, 1.0),
        "thickness_min": min(thicknesses) if thicknesses else 0.0,
        "thickness_max": max(thicknesses) if thicknesses else 1.0,
    }
```

**Explanation:** It accepts `gdf` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `float()`, `iterrows()`, `notnull()`, `get()`, `min()`.

### `_reset_geothermal_suitability`

- **File:** `scripts/precompute_aquifer_scores.py`
- **Lines:** `182-224`
- **Signature:** `def _reset_geothermal_suitability(client: Client) -> None:`
- **Purpose:** Delete every row in geothermal_suitability before re-seeding.

**Code:**
```python
def _reset_geothermal_suitability(client: Client) -> None:
    """Delete every row in geothermal_suitability before re-seeding.

    Previous runs left orphan, duplicate and mismatched rows.  Because we are
    about to re-insert freshly computed records, the safest step is a full table
    wipe.  Deleting in pages of 1000 with offset=0 works because the table
    shrinks as rows are removed.
    """
    resp = client.table("geothermal_suitability").select("*", count="exact").limit(1).execute()
    start_count = getattr(resp, "count", 0) or 0
    if start_count == 0:
        return

    logger.info("Resetting geothermal_suitability (current rows=%s)", start_count)

    # Try a single bulk delete of every row.  gte(0) works for both numeric and
    # text municipality_id values, and skips any nulls on the off chance they
    # exist (the column is a primary key, so there should not be any).
    try:
        client.table("geothermal_suitability").delete().gte("municipality_id", "0").execute()
    except Exception as exc:
        logger.warning("Bulk delete failed, will delete per row: %s", exc)

    # Confirm the table is empty; if not, delete the remaining rows one by one.
    # Always read from offset 0 because rows are being deleted; the next page
    # becomes the new page 0.
    page_size = 1000
    while True:
        resp = client.table("geothermal_suitability").select("municipality_id", count="exact").limit(1).execute()
        remaining = getattr(resp, "count", 0) or 0
        if remaining == 0:
            break

        batch = client.table("geothermal_suitability").select("municipality_id").limit(page_size).offset(0).execute().data or []
        if not batch:
            break
        for row in batch:
            try:
                client.table("geothermal_suitability").delete().eq("municipality_id", row["municipality_id"]).execute()
            except Exception as exc:
                logger.warning("Failed to delete row %s: %s", row.get("municipality_id"), exc)

    logger.info("geothermal_suitability reset complete")
```

**Explanation:** It accepts `client` and returns `None`. See the code below for the full implementation. Key calls include `execute()`, `limit()`, `select()`, `table()`, `getattr()`.

### `main`

- **File:** `scripts/precompute_aquifer_scores.py`
- **Lines:** `227-414`
- **Signature:** `def main() -> None:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> None:
    client = _get_client()
    logger.info("Loading aquifer GeoJSON from %s", AQUIFER_PATH)
    gdf, gdf_projected = _load_aquifer_gdf()
    stats = _aquifer_stats(gdf)

    logger.info("Fetching municipalities from Supabase")
    municipalities: list[dict[str, Any]] = []
    offset = 0
    page_size = 1000
    while True:
        resp = client.table("municipalities").select("municipality_id,lat,lon").limit(page_size).offset(offset).execute()
        batch = resp.data or []
        if not batch:
            break
        municipalities.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size
    logger.info("Found %s municipalities", len(municipalities))

    _reset_geothermal_suitability(client)

    updates: list[dict[str, Any]] = []
    unmatched_records: list[dict[str, Any]] = []
    primary_matched = 0
    fallback_matched = 0
    unmatched = 0
    fallback_distances: list[float] = []

    # Pre-project municipality points to the metric CRS for fast distance checks.
    valid_munis = [
        m for m in municipalities
        if m.get("lat") is not None and m.get("lon") is not None and m.get("municipality_id") is not None
    ]
    if valid_munis:
        import geopandas as gpd

        points_gdf = gpd.GeoDataFrame(
            {"municipality_id": [m["municipality_id"] for m in valid_munis]},
            geometry=[Point(m["lon"], m["lat"]) for m in valid_munis],
            crs="EPSG:4326",
        ).to_crs(AQUIFER_PROJECTED_CRS)
        points_indexed = points_gdf.set_index("municipality_id")["geometry"]
    else:
        points_indexed = None

    for muni in municipalities:
        muni_id = muni.get("municipality_id")
        lat = muni.get("lat")
        lon = muni.get("lon")
        if muni_id is None:
            continue
        if lat is None or lon is None:
            unmatched += 1
            unmatched_records.append(
                {
                    "municipality_id": muni_id,
                    "aquifer_score": None,
                    "aquifer_porosity": None,
                    "aquifer_permeability_log10": None,
                    "aquifer_thickness_m": None,
                    "aquifer_depth_m": None,
                    "aquifer_basin_name": None,
                    "aquifer_fallback": None,
                    "aquifer_distance_km": None,
                    "updated_at": "now()",
                }
            )
            continue

        point = Point(lon, lat)
        matches = gdf[gdf.geometry.contains(point)]

        fallback = False
        distance_km: float | None = None

        if matches.empty:
            # Strict nearest-aquifer fallback: only accept if within the buffer.
            if points_indexed is not None and muni_id in points_indexed.index:
                point_proj = points_indexed.at[muni_id]
                distances = gdf_projected.geometry.distance(point_proj)
                min_distance_m = float(distances.min())
                distance_km = min_distance_m / 1000.0

                if distance_km <= AQUIFER_FALLBACK_BUFFER_KM:
                    nearest_idx = distances.idxmin()
                    row = gdf.loc[nearest_idx]
                    fallback = True
                    fallback_matched += 1
                    fallback_distances.append(distance_km)
                else:
                    unmatched += 1
                    unmatched_records.append(
                        {
                            "municipality_id": muni_id,
                            "aquifer_score": None,
                            "aquifer_porosity": None,
                            "aquifer_permeability_log10": None,
                            "aquifer_thickness_m": None,
                            "aquifer_depth_m": None,
                            "aquifer_basin_name": None,
                            "aquifer_fallback": None,
                            "aquifer_distance_km": None,
                            "updated_at": "now()",
                        }
                    )
                    continue
            else:
                unmatched += 1
                unmatched_records.append(
                    {
                        "municipality_id": muni_id,
                        "aquifer_score": None,
                        "aquifer_porosity": None,
                        "aquifer_permeability_log10": None,
                        "aquifer_thickness_m": None,
                        "aquifer_depth_m": None,
                        "aquifer_basin_name": None,
                        "aquifer_fallback": None,
                        "aquifer_distance_km": None,
                        "updated_at": "now()",
                    }
                )
                continue
        else:
            # If several polygons overlap, pick the one with the highest thickness.
            row = matches.loc[matches["thickness_m"].idxmax()]
            primary_matched += 1

        props = row.to_dict()
        raw_score = _compute_aquifer_score(props, stats)
        aquifer_score = _penalised_score(raw_score, distance_km) if fallback else raw_score

        updates.append(
            {
                "municipality_id": muni_id,
                "aquifer_score": aquifer_score,
                "aquifer_porosity": _sanitize(props.get("porosity")),
                "aquifer_permeability_log10": _sanitize(props.get("permeability_log10")),
                "aquifer_thickness_m": _sanitize(props.get("thickness_m")),
                "aquifer_depth_m": _sanitize(props.get("depth_m")),
                "aquifer_basin_name": str(props.get("basin_name")) if props.get("basin_name") else None,
                "aquifer_fallback": fallback,
                "aquifer_distance_km": _sanitize(distance_km),
                "updated_at": "now()",
            }
        )

    # The table was just reset, so batch insert is safe and much faster than
    # 1000 sequential PATCH/POST calls.  Split into 500-row inserts because that
    # is below the 1000-row API cap and keeps responses manageable.
    all_updates = updates + unmatched_records
    # Defensive deduplication: the municipalities table should be unique, but
    # mixed types (int vs string) can make two rows look different to Python
    # while clashing on the database primary key.
    deduped: dict[str, dict[str, Any]] = {}
    for record in all_updates:
        key = str(record["municipality_id"])
        deduped[key] = record
    all_updates = list(deduped.values())

    for i in range(0, len(all_updates), BATCH_SIZE):
        batch = all_updates[i : i + BATCH_SIZE]
        try:
            resp = client.table("geothermal_suitability").insert(batch).execute()
            logger.info(
                "Inserted batch %s-%s: %s rows",
                i,
                min(i + BATCH_SIZE, len(all_updates)),
                len(resp.data) if resp.data else 0,
            )
        except Exception as exc:
            logger.error("Failed to insert batch %s-%s: %s", i, i + BATCH_SIZE, exc)

    logger.info(
        "Precomputed aquifer scores: primary=%s, fallback=%s, unmatched=%s (total=%s)",
        primary_matched,
        fallback_matched,
        unmatched,
        len(municipalities),
    )
    if fallback_distances:
        logger.info(
            "Fallback distances: max=%.2f km, avg=%.2f km",
            max(fallback_distances),
            sum(fallback_distances) / len(fallback_distances),
        )
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `_get_client()`, `info()`, `_load_aquifer_gdf()`, `_aquifer_stats()`, `execute()`.


## `scripts/run_nasa_for_gaps.py`

**File:** `scripts/run_nasa_for_gaps.py`

**Summary:** Fetch NASA POWER climate data for municipalities that lack it.

### `SupabaseRestClient.__init__`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `30-37`
- **Signature:** `def __init__(self, base_url: str, api_key: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles   init  .

**Code:**
```python
def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.http = httpx.Client(timeout=30.0)
```

**Explanation:** It accepts `base_url`, `api_key`. See the code below for the full implementation. Key calls include `rstrip()`, `Client()`.

### `SupabaseRestClient.table`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `39-40`
- **Signature:** `def table(self, table_name: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles table.

**Code:**
```python
def table(self, table_name: str):
        return SupabaseRestQuery(self, table_name)
```

**Explanation:** It accepts `table_name`. See the code below for the full implementation. Key calls include `SupabaseRestQuery()`.

### `SupabaseRestQuery.__init__`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `44-50`
- **Signature:** `def __init__(self, client: SupabaseRestClient, table: str):`
- **Purpose:** Method of `SupabaseRestQuery` that handles   init  .

**Code:**
```python
def __init__(self, client: SupabaseRestClient, table: str):
        self._client = client
        self._table = table
        self._select_cols = "*"
        self._filters: list[tuple[str, str, str]] = []
        self._order: str | None = None
        self._range: tuple[int, int] | None = None
```

**Explanation:** It accepts `client`, `table`. See the code below for the full implementation.

### `SupabaseRestQuery.select`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `52-54`
- **Signature:** `def select(self, columns: str = "*") -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles select.

**Code:**
```python
def select(self, columns: str = "*") -> "SupabaseRestQuery":
        self._select_cols = columns
        return self
```

**Explanation:** It accepts `columns` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.eq`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `56-58`
- **Signature:** `def eq(self, column: str, value: str | int) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles eq.

**Code:**
```python
def eq(self, column: str, value: str | int) -> "SupabaseRestQuery":
        self._filters.append((column, "eq", str(value)))
        return self
```

**Explanation:** It accepts `column`, `value` and returns `'SupabaseRestQuery'`. See the code below for the full implementation. Key calls include `append()`, `str()`.

### `SupabaseRestQuery.in_`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `60-62`
- **Signature:** `def in_(self, column: str, values: list) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles in .

**Code:**
```python
def in_(self, column: str, values: list) -> "SupabaseRestQuery":
        self._filters.append((column, "in", f"({','.join(str(v) for v in values)})"))
        return self
```

**Explanation:** It accepts `column`, `values` and returns `'SupabaseRestQuery'`. See the code below for the full implementation. Key calls include `append()`, `join()`, `str()`.

### `SupabaseRestQuery.not_`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `64-66`
- **Signature:** `def not_(self) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles not .

**Code:**
```python
def not_(self) -> "SupabaseRestQuery":
        self._negate_next = True
        return self
```

**Explanation:** It accepts zero arguments and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.is_`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `68-74`
- **Signature:** `def is_(self, column: str, value: str) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles is .

**Code:**
```python
def is_(self, column: str, value: str) -> "SupabaseRestQuery":
        op = "is"
        if getattr(self, "_negate_next", False):
            op = "not.is"
            self._negate_next = False
        self._filters.append((column, op, str(value)))
        return self
```

**Explanation:** It accepts `column`, `value` and returns `'SupabaseRestQuery'`. See the code below for the full implementation. Key calls include `getattr()`, `append()`, `str()`.

### `SupabaseRestQuery.not_is`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `76-78`
- **Signature:** `def not_is(self, column: str, value: str) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles not is.

**Code:**
```python
def not_is(self, column: str, value: str) -> "SupabaseRestQuery":
        self._filters.append((column, "not.is", str(value)))
        return self
```

**Explanation:** It accepts `column`, `value` and returns `'SupabaseRestQuery'`. See the code below for the full implementation. Key calls include `append()`, `str()`.

### `SupabaseRestQuery.order`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `80-82`
- **Signature:** `def order(self, column: str, desc: bool = False) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles order.

**Code:**
```python
def order(self, column: str, desc: bool = False) -> "SupabaseRestQuery":
        self._order = f"{column}.{'desc' if desc else 'asc'}"
        return self
```

**Explanation:** It accepts `column`, `desc` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.range`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `84-86`
- **Signature:** `def range(self, start: int, end: int) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles range.

**Code:**
```python
def range(self, start: int, end: int) -> "SupabaseRestQuery":
        self._range = (start, end)
        return self
```

**Explanation:** It accepts `start`, `end` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.insert`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `88-90`
- **Signature:** `def insert(self, rows: list[dict]) -> "SupabaseRestQuery":`
- **Purpose:** Method of `SupabaseRestQuery` that handles insert.

**Code:**
```python
def insert(self, rows: list[dict]) -> "SupabaseRestQuery":
        self._rows = rows
        return self
```

**Explanation:** It accepts `rows` and returns `'SupabaseRestQuery'`. See the code below for the full implementation.

### `SupabaseRestQuery.execute`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `92-110`
- **Signature:** `def execute(self):`
- **Purpose:** Method of `SupabaseRestQuery` that handles execute.

**Code:**
```python
def execute(self):
        if hasattr(self, "_rows"):
            url = f"{self._client.base_url}/rest/v1/{self._table}"
            response = self._client.http.post(url, json=self._rows, headers=self._client.headers)
            response.raise_for_status()
            return type("Response", (), {"data": response.json() if response.text else []})()

        params: dict[str, str] = {"select": self._select_cols}
        for column, op, value in self._filters:
            params[column] = f"{op}.{value}"
        if self._order:
            params["order"] = self._order
        url = f"{self._client.base_url}/rest/v1/{self._table}"
        headers = dict(self._client.headers)
        if self._range:
            headers["Range"] = f"{self._range[0]}-{self._range[1]}"
        response = self._client.http.get(url, params=params, headers=headers)
        response.raise_for_status()
        return type("Response", (), {"data": response.json()})()
```

**Explanation:** It accepts zero arguments. See the code below for the full implementation. Key calls include `hasattr()`, `post()`, `raise_for_status()`, `type()`, `json()`.

### `load_gap_municipality_ids`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `113-131`
- **Signature:** `def load_gap_municipality_ids() -> set[int]:`
- **Purpose:** Loads gap municipality ids.

**Code:**
```python
def load_gap_municipality_ids() -> set[int]:
    ids: set[int] = set()
    # From null_scores.csv
    null_path = OUTPUT_DIR / "null_scores.csv"
    if null_path.exists():
        with open(null_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                mid = row.get("municipality_id")
                if mid:
                    ids.add(int(mid))
    # From missing_from_db.csv (use geo_psgc as ID since we just inserted them)
    missing_path = OUTPUT_DIR / "missing_from_db.csv"
    if missing_path.exists():
        with open(missing_path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                mid = row.get("geo_psgc")
                if mid:
                    ids.add(int(mid))
    return ids
```

**Explanation:** It accepts zero arguments and returns `set[int]`. See the code below for the full implementation. Key calls include `set()`, `exists()`, `open()`, `DictReader()`, `get()`.

### `fetch_db_gap_municipalities`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `134-192`
- **Signature:** `def fetch_db_gap_municipalities(client: SupabaseRestClient) -> list[dict]:`
- **Purpose:** Find all municipalities that have coordinates but no climate data.

**Code:**
```python
def fetch_db_gap_municipalities(client: SupabaseRestClient) -> list[dict]:
    """Find all municipalities that have coordinates but no climate data.

    Queries the DB for municipalities with lat/lon that don't have
    any rows in municipality_climate_monthly. This catches newly inserted
    municipalities from the PSGC sync.
    """
    # 1. Fetch all municipalities with lat/lon
    all_munis: list[dict] = []
    start = 0
    batch = 1000
    while True:
        resp = (
            client.table("municipalities")
            .select("municipality_id,name,lat,lon")
            .not_is("lat", "null")
            .range(start, start + batch - 1)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            break
        all_munis.extend(rows)
        if len(rows) < batch:
            break
        start += batch

    # 2. Fetch all municipality_ids that already have climate data
    climate_ids: set[int] = set()
    start = 0
    while True:
        resp = (
            client.table("municipality_climate_monthly")
            .select("municipality_id")
            .range(start, start + batch - 1)
            .execute()
        )
        rows = resp.data or []
        if not rows:
            break
        for r in rows:
            mid = r.get("municipality_id")
            if mid is not None:
                climate_ids.add(int(mid))
        if len(rows) < batch:
            break
        start += batch

    # 3. Return municipalities without climate data
    gaps = []
    for m in all_munis:
        if m["municipality_id"] not in climate_ids:
            gaps.append({
                "municipality_id": m["municipality_id"],
                "name": m.get("name", ""),
                "lat": float(m["lat"]),
                "lon": float(m["lon"]),
            })
    return gaps
```

**Explanation:** It accepts `client` and returns `list[dict]`. See the code below for the full implementation. Key calls include `execute()`, `extend()`, `len()`, `range()`, `not_is()`.

### `fetch_gap_municipalities`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `195-216`
- **Signature:** `def fetch_gap_municipalities(client: SupabaseRestClient, ids: set[int]) -> list[dict]:`
- **Purpose:** Fetches gap municipalities.

**Code:**
```python
def fetch_gap_municipalities(client: SupabaseRestClient, ids: set[int]) -> list[dict]:
    all_rows = []
    id_list = sorted(ids)
    batch = 100
    for i in range(0, len(id_list), batch):
        chunk = id_list[i : i + batch]
        resp = (
            client.table("municipalities")
            .select("municipality_id,name,lat,lon")
            .in_("municipality_id", chunk)
            .execute()
        )
        rows = resp.data or []
        for r in rows:
            if r.get("lat") is not None and r.get("lon") is not None:
                all_rows.append({
                    "municipality_id": r["municipality_id"],
                    "name": r.get("name", ""),
                    "lat": float(r["lat"]),
                    "lon": float(r["lon"]),
                })
    return all_rows
```

**Explanation:** It accepts `client`, `ids` and returns `list[dict]`. See the code below for the full implementation. Key calls include `sorted()`, `range()`, `len()`, `execute()`, `in_()`.

### `fetch_nasa_data`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `219-236`
- **Signature:** `def fetch_nasa_data(lat: float, lon: float) -> dict | None:`
- **Purpose:** Fetches nasa data.

**Code:**
```python
def fetch_nasa_data(lat: float, lon: float) -> dict | None:
    params = {
        "parameters": ",".join(PARAMETERS),
        "community": "RE",
        "format": "JSON",
        "latitude": f"{lat:.6f}",
        "longitude": f"{lon:.6f}",
        "start": "2010",
        "end": "2023",
    }
    try:
        resp = httpx.get(NASA_URL, params=params, timeout=30.0)
        if resp.status_code == 200:
            return resp.json()
        logging.warning("NASA HTTP %s for lat=%s lon=%s", resp.status_code, lat, lon)
    except Exception as exc:
        logging.warning("NASA request failed: %s", exc)
    return None
```

**Explanation:** It accepts `lat`, `lon` and returns `dict | None`. See the code below for the full implementation. Key calls include `join()`, `get()`, `warning()`, `json()`.

### `coerce_value`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `239-245`
- **Signature:** `def coerce_value(value) -> float | None:`
- **Purpose:** Handles coerce value.

**Code:**
```python
def coerce_value(value) -> float | None:
    if value in MISSING_VALUES or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
```

**Explanation:** It accepts `value` and returns `float | None`. See the code below for the full implementation. Key calls include `float()`.

### `build_climate_rows`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `248-268`
- **Signature:** `def build_climate_rows(municipality_id: int, payload: dict) -> list[dict]:`
- **Purpose:** Builds climate rows.

**Code:**
```python
def build_climate_rows(municipality_id: int, payload: dict) -> list[dict]:
    parameter_map = payload.get("properties", {}).get("parameter", {})
    rows = []
    for year in range(2010, 2024):
        for month in range(1, 13):
            key = f"{year}{month:02d}"
            row = {
                "municipality_id": municipality_id,
                "year": year,
                "month": month,
                "t2m": coerce_value(parameter_map.get("T2M", {}).get(key)),
                "t2m_max": coerce_value(parameter_map.get("T2M_MAX", {}).get(key)),
                "t2m_min": coerce_value(parameter_map.get("T2M_MIN", {}).get(key)),
                "rh2m": coerce_value(parameter_map.get("RH2M", {}).get(key)),
                "prectotcorr": coerce_value(parameter_map.get("PRECTOTCORR", {}).get(key)),
                "ws10m": coerce_value(parameter_map.get("WS10M", {}).get(key)),
                "allsky_sfc_sw_dwn": coerce_value(parameter_map.get("ALLSKY_SFC_SW_DWN", {}).get(key)),
                "cloud_amt": coerce_value(parameter_map.get("CLOUD_AMT", {}).get(key)),
            }
            rows.append(row)
    return rows
```

**Explanation:** It accepts `municipality_id`, `payload` and returns `list[dict]`. See the code below for the full implementation. Key calls include `get()`, `range()`, `append()`, `coerce_value()`.

### `main`

- **File:** `scripts/run_nasa_for_gaps.py`
- **Lines:** `271-330`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Fetch NASA POWER climate data for gap municipalities")
    parser.add_argument("--db-only", action="store_true", help="Query DB for gaps instead of using CSV files")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    load_dotenv(dotenv_path=REPO_ROOT / ".env", override=False)

    url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_KEY")
        or os.getenv("VITE_SUPABASE_ANON_KEY")
    )
    if not url or not key:
        print("ERROR: Missing Supabase credentials", file=sys.stderr)
        return 1

    client = SupabaseRestClient(url, key)

    if args.db_only:
        print("Querying DB for municipalities without climate data...")
        munis = fetch_db_gap_municipalities(client)
    else:
        gap_ids = load_gap_municipality_ids()
        print(f"Gap municipalities from CSVs: {len(gap_ids)}")
        munis = fetch_gap_municipalities(client, gap_ids)

    print(f"Municipalities to process (with coordinates): {len(munis)}")

    if not munis:
        print("No gap municipalities found. All municipalities have climate data.")
        return 0

    processed = 0
    failed = 0
    for i, m in enumerate(munis, 1):
        mid = m["municipality_id"]
        payload = fetch_nasa_data(m["lat"], m["lon"])
        if not payload:
            failed += 1
            continue

        rows = build_climate_rows(mid, payload)
        if rows:
            try:
                client.table("municipality_climate_monthly").insert(rows).execute()
                processed += 1
                if i % 50 == 0:
                    print(f"  Progress: {i}/{len(munis)} (processed={processed}, failed={failed})")
            except Exception as exc:
                logging.warning("Insert failed for municipality %s: %s", mid, exc)
                failed += 1
        time.sleep(0.6)  # NASA rate limit

    print(f"\nDone. Processed: {processed}, Failed: {failed}")
    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `ArgumentParser()`, `add_argument()`, `parse_args()`, `basicConfig()`, `load_dotenv()`.


## `scripts/scrape_philatlas.py`

**File:** `scripts/scrape_philatlas.py`

**Summary:** Scrape PhilAtlas to build a complete geographic hierarchy

### `norm_name`

- **File:** `scripts/scrape_philatlas.py`
- **Lines:** `60-96`
- **Signature:** `def norm_name(name: str) -> str:`
- **Purpose:** Handles norm name.

**Code:**
```python
def norm_name(name: str) -> str:
    if not name:
        return ""
    n = name.strip().lower()
    # Strip parenthetical names: "davao de oro (compostela valley)" -> "davao de oro"
    n = re.sub(r'\s*\([^)]*\)\s*', ' ', n).strip()
    for prefix in ("province of ", "city of ", "municipality of "):
        if n.startswith(prefix):
            n = n[len(prefix):]
    # Strip common suffixes
    for suffix in (" city", " municipality"):
        if n.endswith(suffix):
            n = n[: -len(suffix)]
    # Common aliases
    aliases = {
        "compostela valley": "davao de oro",
        "maguindanao": "maguindanao del norte",
        "western samar": "samar",
        "samar (western samar)": "samar",
        "north cotabato": "cotabato",
        "cotabato (north cot.)": "cotabato",
        # NCR province in PhilAtlas maps to NCR 1st District in DB (handled in province matching)
        "region iv-b (mimaropa)": "mimaropa",
        "region iv-a (calabarzon)": "calabarzon",
        "cordillera administrative region": "car",
        "bangsamoro autonomous region in muslim mindanao": "barmm",
        "muñoz": "munoz",
        "science city of muñoz": "munoz",
        "pi v. corpuz": "pio v. corpuz",
        "gen. s.k. pendatun": "general salipada k. pendatun",
        # DB has "DAVAO (DAVAO DEL NORTE)" which strips to "davao"
        "davao": "davao del norte",
        # NCR province in PhilAtlas maps to NCR 1st District in DB
        # DB "NCR - 1st DISTRICT (MANILA)" normalizes to "ncr - 1st district"
        "national capital region": "ncr - 1st district",
    }
    return aliases.get(n, n)
```

**Explanation:** It accepts `name` and returns `str`. See the code below for the full implementation. Key calls include `lower()`, `strip()`, `sub()`, `startswith()`, `len()`.

### `load_geojson_province_map`

- **File:** `scripts/scrape_philatlas.py`
- **Lines:** `103-119`
- **Signature:** `def load_geojson_province_map() -> dict[str, dict]:`
- **Purpose:** Return {normalized_name: {psgc, region_psgc, name}} from per-region GeoJSON.

**Code:**
```python
def load_geojson_province_map() -> dict[str, dict]:
    """Return {normalized_name: {psgc, region_psgc, name}} from per-region GeoJSON."""
    with open(GEOJSON_REGION_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    result = {}
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        psgc = props.get("adm2_psgc")
        name = props.get("adm2_en", "")
        region_psgc = props.get("adm1_psgc")
        if psgc and name:
            result[norm_name(name)] = {
                "psgc": int(psgc),
                "region_psgc": int(region_psgc) if region_psgc else None,
                "name": name,
            }
    return result
```

**Explanation:** It accepts zero arguments and returns `dict[str, dict]`. See the code below for the full implementation. Key calls include `open()`, `load()`, `get()`, `norm_name()`, `int()`.

### `load_geojson_municipality_map`

- **File:** `scripts/scrape_philatlas.py`
- **Lines:** `122-137`
- **Signature:** `def load_geojson_municipality_map() -> dict[int, list[dict]]:`
- **Purpose:** Return {province_psgc: [{psgc, name, lat, lon}, ...]} from per-provinces GeoJSON.

**Code:**
```python
def load_geojson_municipality_map() -> dict[int, list[dict]]:
    """Return {province_psgc: [{psgc, name, lat, lon}, ...]} from per-provinces GeoJSON."""
    with open(GEOJSON_MUNI_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    result: dict[int, list[dict]] = {}
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        muni_psgc = props.get("adm3_psgc")
        muni_name = props.get("adm3_en", "")
        prov_psgc = props.get("adm2_psgc")
        if muni_psgc and muni_name and prov_psgc:
            result.setdefault(int(prov_psgc), []).append({
                "psgc": int(muni_psgc),
                "name": muni_name,
            })
    return result
```

**Explanation:** It accepts zero arguments and returns `dict[int, list[dict]]`. See the code below for the full implementation. Key calls include `open()`, `load()`, `get()`, `append()`, `setdefault()`.

### `fetch_page`

- **File:** `scripts/scrape_philatlas.py`
- **Lines:** `144-147`
- **Signature:** `def fetch_page(client: httpx.Client, url: str) -> str:`
- **Purpose:** Fetches page.

**Code:**
```python
def fetch_page(client: httpx.Client, url: str) -> str:
    resp = client.get(url, follow_redirects=True)
    resp.raise_for_status()
    return resp.text
```

**Explanation:** It accepts `client`, `url` and returns `str`. See the code below for the full implementation. Key calls include `get()`, `raise_for_status()`.

### `parse_index_page`

- **File:** `scripts/scrape_philatlas.py`
- **Lines:** `150-173`
- **Signature:** `def parse_index_page(html: str) -> list[dict]:`
- **Purpose:** Parse the barangays index page to extract province links.

**Code:**
```python
def parse_index_page(html: str) -> list[dict]:
    """Parse the barangays index page to extract province links.

    Returns list of {name, slug, url}.
    PhilAtlas uses single-quoted href attributes.
    """
    # Match: <a href='lists/barangays-SLUG.html' title='...'>NAME</a>
    pattern = re.compile(
        r"<a\s+href=['\"](?:/?)lists/barangays-([a-z0-9-]+)\.html['\"][^>]*>([^<]+)</a>",
        re.IGNORECASE,
    )
    results = []
    seen = set()
    for m in pattern.finditer(html):
        slug = m.group(1)
        name = m.group(2).strip()
        if slug not in seen:
            seen.add(slug)
            results.append({
                "name": name,
                "slug": slug,
                "url": f"{PHILATLAS_BASE}/lists/barangays-{slug}.html",
            })
    return results
```

**Explanation:** It accepts `html` and returns `list[dict]`. See the code below for the full implementation. Key calls include `compile()`, `set()`, `finditer()`, `group()`, `strip()`.

### `parse_province_page`

- **File:** `scripts/scrape_philatlas.py`
- **Lines:** `176-206`
- **Signature:** `def parse_province_page(html: str) -> list[dict]:`
- **Purpose:** Parse a province barangays page to extract barangay entries.

**Code:**
```python
def parse_province_page(html: str) -> list[dict]:
    """Parse a province barangays page to extract barangay entries.

    Each entry: {barangay_name, municipality_name, url}

    PhilAtlas uses single-quoted href attributes. Entries look like:
    <a href='luzon/car/abra/bangued/agtangao.html'>Agtangao</a>, Bangued
    """
    # Match: <a href='...'>BARANGAYNAME</a>, MUNINAME (single or double quotes)
    pattern = re.compile(
        r"<a\s+href=['\"]([^'\"]+)['\"][^>]*>([^<]+)</a>\s*,\s*([^\n<]+)",
        re.IGNORECASE,
    )
    results = []
    for m in pattern.finditer(html):
        url = m.group(1)
        barangay_name = m.group(2).strip()
        municipality_name = m.group(3).strip()
        # Skip non-geographic links (e.g., navigation links without path separators)
        if '/' not in url:
            continue
        # Clean up municipality name (remove trailing punctuation/whitespace)
        municipality_name = municipality_name.rstrip(".,;").strip()
        if not barangay_name or not municipality_name:
            continue
        results.append({
            "barangay_name": barangay_name,
            "municipality_name": municipality_name,
            "url": f"{PHILATLAS_BASE}/{url}" if not url.startswith("/") else f"{PHILATLAS_BASE}{url}",
        })
    return results
```

**Explanation:** It accepts `html` and returns `list[dict]`. See the code below for the full implementation. Key calls include `compile()`, `finditer()`, `group()`, `strip()`, `append()`.

### `scrape_philatlas`

- **File:** `scripts/scrape_philatlas.py`
- **Lines:** `209-284`
- **Signature:** `def scrape_philatlas() -> dict:`
- **Purpose:** Scrape PhilAtlas and return structured geographic data.

**Code:**
```python
def scrape_philatlas() -> dict:
    """Scrape PhilAtlas and return structured geographic data.

    Returns:
        {
            "provinces": [{name, slug, url, region_slug, municipalities: [...]}],
            "regions": set of region slugs discovered,
        }
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }

    all_data = {
        "provinces": [],
        "regions_discovered": set(),
    }

    with httpx.Client(headers=headers, timeout=30.0, follow_redirects=True) as client:
        # 1. Fetch index page
        print("Fetching index page...")
        index_html = fetch_page(client, INDEX_URL)
        province_links = parse_index_page(index_html)
        print(f"  Found {len(province_links)} province/special links")

        # 2. Fetch each province page
        for i, prov in enumerate(province_links):
            slug = prov["slug"]
            name = prov["name"]
            print(f"  [{i+1}/{len(province_links)}] {name}...", end="", flush=True)

            try:
                prov_html = fetch_page(client, prov["url"])
            except Exception as exc:
                print(f" FAILED: {exc}")
                continue

            entries = parse_province_page(prov_html)
            print(f" {len(entries)} barangays")

            # Extract region slug from barangay URLs
            # URL pattern: /{island}/{region}/{province}/{muni}/{barangay}.html
            region_slug = None
            for entry in entries:
                url_path = entry["url"]
                if PHILATLAS_BASE in url_path:
                    url_path = url_path[len(PHILATLAS_BASE):]
                parts = url_path.strip("/").split("/")
                if len(parts) >= 4:
                    region_slug = parts[1]
                    break

            if region_slug:
                all_data["regions_discovered"].add(region_slug)

            # Group barangays by municipality
            municipalities: dict[str, list[str]] = {}
            for entry in entries:
                muni_name = entry["municipality_name"]
                if muni_name not in municipalities:
                    municipalities[muni_name] = []
                municipalities[muni_name].append(entry["barangay_name"])

            all_data["provinces"].append({
                "name": name,
                "slug": slug,
                "url": prov["url"],
                "region_slug": region_slug,
                "municipalities": municipalities,
            })

            # Polite delay
            time.sleep(1)

    return all_data
```

**Explanation:** It accepts zero arguments and returns `dict`. See the code below for the full implementation. Key calls include `set()`, `Client()`, `fetch_page()`, `parse_index_page()`, `enumerate()`.

### `SupabaseRestClient.__init__`

- **File:** `scripts/scrape_philatlas.py`
- **Lines:** `292-299`
- **Signature:** `def __init__(self, base_url: str, api_key: str):`
- **Purpose:** Method of `SupabaseRestClient` that handles   init  .

**Code:**
```python
def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.http = httpx.Client(timeout=30.0)
```

**Explanation:** It accepts `base_url`, `api_key`. See the code below for the full implementation. Key calls include `rstrip()`, `Client()`.

### `SupabaseRestClient.get_all`

- **File:** `scripts/scrape_philatlas.py`
- **Lines:** `301-319`
- **Signature:** `def get_all(self, table: str, select: str = "*") -> list[dict]:`
- **Purpose:** Method of `SupabaseRestClient` that retrieves all.

**Code:**
```python
def get_all(self, table: str, select: str = "*") -> list[dict]:
        all_rows = []
        offset = 0
        batch = 1000
        while True:
            url = f"{self.base_url}/rest/v1/{table}"
            params = {"select": select}
            headers = dict(self.headers)
            headers["Range"] = f"{offset}-{offset + batch - 1}"
            resp = self.http.get(url, params=params, headers=headers)
            resp.raise_for_status()
            rows = resp.json()
            if not rows:
                break
            all_rows.extend(rows)
            if len(rows) < batch:
                break
            offset += batch
        return all_rows
```

**Explanation:** It accepts `table`, `select` and returns `list[dict]`. See the code below for the full implementation. Key calls include `dict()`, `get()`, `raise_for_status()`, `json()`, `extend()`.

### `main`

- **File:** `scripts/scrape_philatlas.py`
- **Lines:** `326-655`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    load_dotenv(dotenv_path=REPO_ROOT / ".env", override=False)

    # --- Scrape PhilAtlas ---
    print("=" * 60)
    print("Scraping PhilAtlas...")
    print("=" * 60)
    scraped = scrape_philatlas()

    total_munis = sum(len(p["municipalities"]) for p in scraped["provinces"])
    total_barangays = sum(
        len(baries) for p in scraped["provinces"] for baries in p["municipalities"].values()
    )
    print(f"\nScrape complete:")
    print(f"  Provinces/special: {len(scraped['provinces'])}")
    print(f"  Municipalities:   {total_munis}")
    print(f"  Barangays:         {total_barangays}")
    print(f"  Region slugs:      {sorted(scraped['regions_discovered'])}")

    # --- Load GeoJSON mappings ---
    print("\nLoading GeoJSON mappings...")
    geo_provinces = load_geojson_province_map()
    geo_munis = load_geojson_municipality_map()
    print(f"  GeoJSON provinces: {len(geo_provinces)}")
    print(f"  GeoJSON municipalities: {sum(len(v) for v in geo_munis.values())}")

    # --- Build scraped hierarchy with PSGC codes ---
    print("\nBuilding hierarchy with PSGC codes...")

    # Regions: map from province PSGC -> region PSGC
    scraped_regions: dict[int, str] = {}  # region_psgc -> name
    scraped_provinces: list[dict] = []     # {psgc, region_psgc, name}
    scraped_municipalities: list[dict] = []  # {psgc, province_psgc, name}
    scraped_barangays: list[dict] = []    # {barangay_id, municipality_psgc, name}

    unmatched_provinces: list[str] = []
    unmatched_munis: list[dict] = []

    for prov in scraped["provinces"]:
        prov_name = prov["name"]
        prov_key = norm_name(prov_name)

        # Match province to GeoJSON
        geo_match = geo_provinces.get(prov_key)
        if not geo_match:
            # Try without NCR/HUC special names
            if prov_name in ("National Capital Region (NCR)",
                             "Highly urbanized cities outside NCR, and Cotabato City"):
                # These are special groupings, not provinces
                # Assign a synthetic PSGC
                if "ncr" in prov_name.lower():
                    prov_psgc = 1300000000
                    region_psgc = 1300000000
                else:
                    # HUCs - assign to their respective provinces later
                    prov_psgc = None
                    region_psgc = None
            else:
                unmatched_provinces.append(prov_name)
                continue
        else:
            prov_psgc = geo_match["psgc"]
            region_psgc = geo_match["region_psgc"]

        if prov_psgc and region_psgc:
            # Add region
            region_name = REGION_PSGC_TO_NAME.get(region_psgc, f"Region {region_psgc}")
            scraped_regions[region_psgc] = region_name

            # Add province
            scraped_provinces.append({
                "province_id": prov_psgc,
                "region_id": region_psgc,
                "name": prov_name,
            })

        # Process municipalities
        for muni_name, barangay_list in prov["municipalities"].items():
            muni_key = norm_name(muni_name)

            # Match municipality to GeoJSON
            muni_psgc = None
            if prov_psgc and prov_psgc in geo_munis:
                for gm in geo_munis[prov_psgc]:
                    if norm_name(gm["name"]) == muni_key:
                        muni_psgc = gm["psgc"]
                        break

            if not muni_psgc and prov_psgc:
                # Try matching across all provinces (for HUCs)
                for gp_psgc, gm_list in geo_munis.items():
                    for gm in gm_list:
                        if norm_name(gm["name"]) == muni_key:
                            muni_psgc = gm["psgc"]
                            # Use this province's PSGC
                            if not prov_psgc:
                                prov_psgc = gp_psgc
                                region_psgc = geo_provinces.get(
                                    norm_name(prov_name), {}
                                ).get("region_psgc")
                                if not region_psgc:
                                    # Find region from geo_provinces by province psgc
                                    for gp_name, gp_info in geo_provinces.items():
                                        if gp_info["psgc"] == gp_psgc:
                                            region_psgc = gp_info["region_psgc"]
                                            break
                            break
                    if muni_psgc:
                        break

            if not muni_psgc:
                unmatched_munis.append({
                    "name": muni_name,
                    "province": prov_name,
                })
                # Still add with a generated ID
                # Use province_psgc * 1000 + sequential
                if prov_psgc:
                    existing_count = len([
                        m for m in scraped_municipalities
                        if m.get("province_psgc") == prov_psgc
                    ])
                    muni_psgc = prov_psgc * 1000 + existing_count + 1
                else:
                    muni_psgc = 99000000000 + len(scraped_municipalities) + 1

            scraped_municipalities.append({
                "municipality_id": muni_psgc,
                "province_id": prov_psgc or 0,
                "name": muni_name,
            })

            # Add barangays
            for idx, barangay_name in enumerate(barangay_list, 1):
                # Generate barangay ID: municipality_psgc * 100 + sequential
                barangay_id = muni_psgc * 100 + idx
                scraped_barangays.append({
                    "barangay_id": barangay_id,
                    "municipality_id": muni_psgc,
                    "name": barangay_name,
                })

    print(f"  Regions: {len(scraped_regions)}")
    print(f"  Provinces: {len(scraped_provinces)}")
    print(f"  Municipalities: {len(scraped_municipalities)}")
    print(f"  Barangays: {len(scraped_barangays)}")
    if unmatched_provinces:
        print(f"  Unmatched provinces: {len(unmatched_provinces)}")
        for p in unmatched_provinces:
            print(f"    - {p}")
    if unmatched_munis:
        print(f"  Unmatched municipalities: {len(unmatched_munis)}")
        for m in unmatched_munis[:20]:
            print(f"    - {m['name']} ({m['province']})")
        if len(unmatched_munis) > 20:
            print(f"    ... and {len(unmatched_munis) - 20} more")

    # --- Fetch DB state ---
    print("\nFetching DB state from Supabase...")
    url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_KEY")
        or os.getenv("VITE_SUPABASE_ANON_KEY")
    )
    if not url or not key:
        print("ERROR: Missing Supabase credentials", file=sys.stderr)
        return 1

    client = SupabaseRestClient(url, key)

    try:
        db_regions = client.get_all("regions", "region_id,name")
        print(f"  DB regions: {len(db_regions)}")
    except Exception as exc:
        print(f"  WARNING: Could not fetch regions: {exc}")
        db_regions = []

    try:
        db_provinces = client.get_all("provinces", "province_id,name,region_id")
        print(f"  DB provinces: {len(db_provinces)}")
    except Exception as exc:
        print(f"  WARNING: Could not fetch provinces: {exc}")
        db_provinces = []

    try:
        db_munis = client.get_all("municipalities", "municipality_id,name,province_id")
        print(f"  DB municipalities: {len(db_munis)}")
    except Exception as exc:
        print(f"  WARNING: Could not fetch municipalities: {exc}")
        db_munis = []

    try:
        db_barangays = client.get_all("barangays", "barangay_id,name,municipality_id")
        print(f"  DB barangays: {len(db_barangays)}")
    except Exception as exc:
        print(f"  WARNING: Could not fetch barangays: {exc}")
        db_barangays = []

    # --- Compare by normalized name (DB uses sequential IDs, not PSGC) ---
    print("\nComparing scraped vs DB (by normalized name)...")

    # Build DB lookup by normalized name
    db_region_by_name = {norm_name(r["name"]): r for r in db_regions}
    db_province_by_name = {norm_name(p["name"]): p for p in db_provinces}
    db_muni_by_name: dict[str, dict] = {}
    for m in db_munis:
        key_m = norm_name(m["name"])
        if key_m not in db_muni_by_name:
            db_muni_by_name[key_m] = m
    db_barangay_by_key: set[str] = set()
    for b in db_barangays:
        bkey = f"{norm_name(b['name'])}|{b['municipality_id']}"
        db_barangay_by_key.add(bkey)

    # Compute max IDs for new entries
    max_region_id = max((r["region_id"] for r in db_regions), default=0)
    max_province_id = max((p["province_id"] for p in db_provinces), default=0)
    max_muni_id = max((m["municipality_id"] for m in db_munis), default=0)
    max_barangay_id = max((b["barangay_id"] for b in db_barangays), default=0)

    # --- Find missing regions ---
    missing_regions: list[dict] = []
    region_id_map: dict[int, int] = {}  # scraped region_psgc -> DB region_id (existing or new)
    next_region_id = max_region_id + 1

    for psgc, name in scraped_regions.items():
        region_norm = norm_name(name)
        db_match = db_region_by_name.get(region_norm)
        # Special case: scraped "National Capital Region" -> DB "NCR"
        if not db_match and region_norm == "national capital region":
            db_match = db_region_by_name.get("ncr")
        if db_match:
            region_id_map[psgc] = db_match["region_id"]
        else:
            missing_regions.append({"region_id": next_region_id, "name": name})
            region_id_map[psgc] = next_region_id
            next_region_id += 1

    # --- Find missing provinces ---
    missing_provinces: list[dict] = []
    province_id_map: dict[int, int] = {}  # scraped province_psgc -> DB province_id
    next_province_id = max_province_id + 1

    for p in scraped_provinces:
        prov_norm = norm_name(p["name"])
        db_match = db_province_by_name.get(prov_norm)
        # Special case: PhilAtlas "National Capital Region (NCR)" -> DB "NCR - 1st DISTRICT (MANILA)"
        if not db_match and prov_norm == "national capital region":
            db_match = db_province_by_name.get("ncr - 1st district")
        if db_match:
            province_id_map[p["province_id"]] = db_match["province_id"]
        else:
            region_id = region_id_map.get(p["region_id"], p["region_id"])
            missing_provinces.append({
                "province_id": next_province_id,
                "region_id": region_id,
                "name": p["name"],
            })
            province_id_map[p["province_id"]] = next_province_id
            next_province_id += 1

    # --- Find missing municipalities ---
    missing_munis: list[dict] = []
    muni_id_map: dict[int, int] = {}  # scraped muni_psgc -> DB municipality_id
    next_muni_id = max_muni_id + 1

    for m in scraped_municipalities:
        db_match = db_muni_by_name.get(norm_name(m["name"]))
        if db_match:
            muni_id_map[m["municipality_id"]] = db_match["municipality_id"]
        else:
            province_id = province_id_map.get(m["province_id"], m["province_id"])
            missing_munis.append({
                "municipality_id": next_muni_id,
                "province_id": province_id,
                "name": m["name"],
            })
            muni_id_map[m["municipality_id"]] = next_muni_id
            next_muni_id += 1

    # --- Find missing barangays ---
    missing_barangays: list[dict] = []
    next_barangay_id = max_barangay_id + 1

    for b in scraped_barangays:
        muni_id = muni_id_map.get(b["municipality_id"])
        if not muni_id:
            continue
        bkey = f"{norm_name(b['name'])}|{muni_id}"
        if bkey in db_barangay_by_key:
            continue
        missing_barangays.append({
            "barangay_id": next_barangay_id,
            "municipality_id": muni_id,
            "name": b["name"],
        })
        next_barangay_id += 1

    # --- Write CSVs ---
    def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    write_csv(OUTPUT_DIR / "missing_regions.csv", missing_regions, ["region_id", "name"])
    write_csv(OUTPUT_DIR / "missing_provinces.csv", missing_provinces, ["province_id", "region_id", "name"])
    write_csv(OUTPUT_DIR / "missing_municipalities.csv", missing_munis, ["municipality_id", "province_id", "name"])
    write_csv(OUTPUT_DIR / "missing_barangays.csv", missing_barangays, ["barangay_id", "municipality_id", "name"])

    # Summary
    summary = [
        {"table": "regions", "scraped": len(scraped_regions), "db": len(db_regions), "missing": len(missing_regions)},
        {"table": "provinces", "scraped": len(scraped_provinces), "db": len(db_provinces), "missing": len(missing_provinces)},
        {"table": "municipalities", "scraped": len(scraped_municipalities), "db": len(db_munis), "missing": len(missing_munis)},
        {"table": "barangays", "scraped": len(scraped_barangays), "db": len(db_barangays), "missing": len(missing_barangays)},
    ]
    write_csv(OUTPUT_DIR / "scrape_summary.csv", summary, ["table", "scraped", "db", "missing"])

    print(f"\n{'='*60}")
    print(f"COMPARISON RESULTS")
    print(f"{'='*60}")
    for s in summary:
        print(f"  {s['table']:20s}  scraped={s['scraped']:6d}  db={s['db']:6d}  missing={s['missing']:6d}")
    print(f"\nCSVs written to: {OUTPUT_DIR}")
    print(f"\nTo insert missing entries, run:")
    print(f"  py scripts/insert_from_csvs.py")
    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `load_dotenv()`, `scrape_philatlas()`, `sum()`, `len()`, `values()`.


## `scripts/sync_psgc_data.py`

**File:** `scripts/sync_psgc_data.py`

**Summary:** Sync PSGC data from the authenticated PSA API to Supabase.

### `normalize_name`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `65-75`
- **Signature:** `def normalize_name(name: str) -> str:`
- **Purpose:** Normalize a geographic name for matching.

**Code:**
```python
def normalize_name(name: str) -> str:
    """Normalize a geographic name for matching."""
    if not name:
        return ""
    s = name.strip().lower()
    s = _CITY_PREFIX.sub("", s)
    s = _PARENTHETICAL.sub(" ", s)
    s = _MUNI_SUFFIXES.sub("", s)
    s = _SPECIAL_CHARS.sub("", s)
    s = _MULTI_SPACE.sub(" ", s).strip()
    return s
```

**Explanation:** It accepts `name` and returns `str`. See the code below for the full implementation. Key calls include `lower()`, `strip()`, `sub()`.

### `extract_parenthetical`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `81-88`
- **Signature:** `def extract_parenthetical(name: str) -> str:`
- **Purpose:** Extract the text inside the first pair of parentheses, normalized.

**Code:**
```python
def extract_parenthetical(name: str) -> str:
    """Extract the text inside the first pair of parentheses, normalized."""
    if not name:
        return ""
    m = _PAREN_EXTRACT.search(name)
    if m:
        return normalize_name(m.group(1))
    return ""
```

**Explanation:** It accepts `name` and returns `str`. See the code below for the full implementation. Key calls include `search()`, `normalize_name()`, `group()`.

### `normalize_with_old_name`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `91-108`
- **Signature:** `def normalize_with_old_name(name: str, old_name: str = "") -> list[str]:`
- **Purpose:** Return all possible normalized forms of a name for matching.

**Code:**
```python
def normalize_with_old_name(name: str, old_name: str = "") -> list[str]:
    """Return all possible normalized forms of a name for matching.

    Includes the primary normalized name, the parenthetical content,
    and the old_name field if provided.
    """
    results = [normalize_name(name)]
    paren = extract_parenthetical(name)
    if paren and paren not in results:
        results.append(paren)
    if old_name:
        old_norm = normalize_name(old_name)
        if old_norm and old_norm not in results:
            results.append(old_norm)
        old_paren = extract_parenthetical(old_name)
        if old_paren and old_paren not in results:
            results.append(old_paren)
    return results
```

**Explanation:** It accepts `name`, `old_name` and returns `list[str]`. See the code below for the full implementation. Key calls include `normalize_name()`, `extract_parenthetical()`, `append()`.

### `PsaApiClient.__init__`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `133-136`
- **Signature:** `def __init__(self, token: str):`
- **Purpose:** Method of `PsaApiClient` that handles   init  .

**Code:**
```python
def __init__(self, token: str):
        self.token = token
        self.base = f"{PSGC_BASE}/{PSGC_VERSION}"
        self.http = httpx.Client(timeout=60.0)
```

**Explanation:** It accepts `token`. See the code below for the full implementation. Key calls include `Client()`.

### `PsaApiClient.fetch_all`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `138-187`
- **Signature:** `def fetch_all(self, level: str) -> list[dict[str, Any]]:`
- **Purpose:** Fetch all records for a given level, handling pagination.

**Code:**
```python
def fetch_all(self, level: str) -> list[dict[str, Any]]:
        """Fetch all records for a given level, handling pagination."""
        cache_path = CACHE_DIR / f"{level}.json"
        if cache_path.exists():
            logger.info("Loading cached %s from %s", level, cache_path)
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)

        records: list[dict[str, Any]] = []
        url = f"{self.base}/{level}?token={self.token}&perPage={PAGE_SIZE}&page=1"

        page = 1
        while url:
            logger.info("Fetching %s page %s...", level, page)
            try:
                resp = self.http.get(url)
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:
                logger.error("API error on %s page %s: %s", level, page, exc)
                break

            # API returns {"count": N, "next": url, "previous": null, "results": {"psgc_data": [...]}}
            results_obj = data.get("results", {})
            if isinstance(results_obj, dict):
                page_records = results_obj.get("psgc_data", [])
            else:
                page_records = results_obj if isinstance(results_obj, list) else []
            records.extend(page_records)

            # Check for next page
            next_url = data.get("next")
            if next_url:
                # Append token if not already in URL
                if "token=" not in next_url:
                    separator = "&" if "?" in next_url else "?"
                    next_url = f"{next_url}{separator}token={self.token}"
                url = next_url
                page += 1
                time.sleep(API_DELAY)
            else:
                url = None

        logger.info("Fetched %s total %s records", level, len(records))

        # Cache to disk
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        return records
```

**Explanation:** It accepts `level` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `exists()`, `info()`, `open()`, `load()`, `get()`.

### `SupabaseClient.__init__`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `196-204`
- **Signature:** `def __init__(self, base_url: str, api_key: str):`
- **Purpose:** Method of `SupabaseClient` that handles   init  .

**Code:**
```python
def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        }
        self.http = httpx.Client(timeout=120.0)
```

**Explanation:** It accepts `base_url`, `api_key`. See the code below for the full implementation. Key calls include `rstrip()`, `Client()`.

### `SupabaseClient.fetch_all_rows`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `206-225`
- **Signature:** `def fetch_all_rows(self, table: str, select: str = "*") -> list[dict[str, Any]]:`
- **Purpose:** Fetch all rows from a table with pagination.

**Code:**
```python
def fetch_all_rows(self, table: str, select: str = "*") -> list[dict[str, Any]]:
        """Fetch all rows from a table with pagination."""
        all_rows: list[dict[str, Any]] = []
        start = 0
        batch = 1000
        while True:
            url = f"{self.base_url}/rest/v1/{table}?select={select}"
            url += f"&limit={batch}&offset={start}"
            try:
                resp = self.http.get(url, headers=self.headers)
                resp.raise_for_status()
                rows = resp.json()
            except Exception as exc:
                logger.error("Error fetching from %s (offset %s): %s", table, start, exc)
                break
            all_rows.extend(rows)
            if len(rows) < batch:
                break
            start += batch
        return all_rows
```

**Explanation:** It accepts `table`, `select` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `extend()`, `get()`, `raise_for_status()`, `json()`, `len()`.

### `SupabaseClient.update_row`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `227-237`
- **Signature:** `def update_row(self, table: str, pk_col: str, pk_val: int, data: dict[str, Any]) -> bool:`
- **Purpose:** Update a single row by primary key.

**Code:**
```python
def update_row(self, table: str, pk_col: str, pk_val: int, data: dict[str, Any]) -> bool:
        """Update a single row by primary key."""
        url = f"{self.base_url}/rest/v1/{table}?{pk_col}=eq.{pk_val}"
        headers = {**self.headers, "Prefer": "return=minimal"}
        try:
            resp = self.http.patch(url, json=data, headers=headers)
            resp.raise_for_status()
            return True
        except Exception as exc:
            logger.warning("Update failed %s/%s=%s: %s", table, pk_col, pk_val, exc)
            return False
```

**Explanation:** It accepts `table`, `pk_col`, `pk_val`, `data` and returns `bool`. See the code below for the full implementation. Key calls include `patch()`, `raise_for_status()`, `warning()`.

### `SupabaseClient.insert_batch`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `239-252`
- **Signature:** `def insert_batch(self, table: str, rows: list[dict[str, Any]]) -> tuple[int, str]:`
- **Purpose:** Insert a batch of rows. Returns (count, error_msg).

**Code:**
```python
def insert_batch(self, table: str, rows: list[dict[str, Any]]) -> tuple[int, str]:
        """Insert a batch of rows. Returns (count, error_msg)."""
        if not rows:
            return 0, ""
        url = f"{self.base_url}/rest/v1/{table}"
        try:
            resp = self.http.post(url, json=rows, headers=self.headers)
            resp.raise_for_status()
            return len(rows), ""
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500] if exc.response else ""
            return 0, f"HTTP {exc.response.status_code}: {body}"
        except Exception as exc:
            return 0, str(exc)
```

**Explanation:** It accepts `table`, `rows` and returns `tuple[int, str]`. See the code below for the full implementation. Key calls include `post()`, `raise_for_status()`, `len()`, `str()`.

### `SupabaseClient.upsert_batch`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `254-271`
- **Signature:** `def upsert_batch(self, table: str, rows: list[dict[str, Any]], on_conflict: str = "") -> tuple[int, str]:`
- **Purpose:** Upsert a batch of rows using merge-duplicates.

**Code:**
```python
def upsert_batch(self, table: str, rows: list[dict[str, Any]], on_conflict: str = "") -> tuple[int, str]:
        """Upsert a batch of rows using merge-duplicates."""
        if not rows:
            return 0, ""
        url = f"{self.base_url}/rest/v1/{table}"
        prefer = "resolution=merge-duplicates"
        if on_conflict:
            prefer += f",on_conflict=({on_conflict})"
        headers = {**self.headers, "Prefer": prefer}
        try:
            resp = self.http.post(url, json=rows, headers=headers)
            resp.raise_for_status()
            return len(rows), ""
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500] if exc.response else ""
            return 0, f"HTTP {exc.response.status_code}: {body}"
        except Exception as exc:
            return 0, str(exc)
```

**Explanation:** It accepts `table`, `rows`, `on_conflict` and returns `tuple[int, str]`. See the code below for the full implementation. Key calls include `post()`, `raise_for_status()`, `len()`, `str()`.

### `SupabaseClient.get_max_id`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `273-284`
- **Signature:** `def get_max_id(self, table: str, id_col: str) -> int:`
- **Purpose:** Get the maximum ID from a table.

**Code:**
```python
def get_max_id(self, table: str, id_col: str) -> int:
        """Get the maximum ID from a table."""
        url = f"{self.base_url}/rest/v1/{table}?select={id_col}&order={id_col}.desc&limit=1"
        try:
            resp = self.http.get(url, headers=self.headers)
            resp.raise_for_status()
            data = resp.json()
            if data:
                return data[0].get(id_col, 0)
        except Exception:
            pass
        return 0
```

**Explanation:** It accepts `table`, `id_col` and returns `int`. See the code below for the full implementation. Key calls include `get()`, `raise_for_status()`, `json()`.

### `_parse_population_value`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `292-305`
- **Signature:** `def _parse_population_value(value) -> int | None:`
- **Purpose:** Parse a population value that may be a string with commas/spaces.

**Code:**
```python
def _parse_population_value(value) -> int | None:
    """Parse a population value that may be a string with commas/spaces."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    # String like " 5,026,128 " or "5,342,453"
    cleaned = str(value).strip().replace(",", "").replace(" ", "")
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except (TypeError, ValueError):
        return None
```

**Explanation:** It accepts `value` and returns `int | None`. See the code below for the full implementation. Key calls include `isinstance()`, `int()`, `replace()`, `strip()`, `str()`.

### `extract_population`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `308-328`
- **Signature:** `def extract_population(record: dict[str, Any]) -> dict[str, int | None]:`
- **Purpose:** Extract population data from a PSA API record.

**Code:**
```python
def extract_population(record: dict[str, Any]) -> dict[str, int | None]:
    """Extract population data from a PSA API record."""
    pop_data = record.get("population_data", [])
    result = {"population_2015": None, "population_2020": None, "population_2024": None}
    if not pop_data:
        return result
    for entry in pop_data:
        year = entry.get("year")
        pop = entry.get("population")
        if year and pop is not None:
            year_str = str(year)
            parsed = _parse_population_value(pop)
            if parsed is None:
                continue
            if "2015" in year_str:
                result["population_2015"] = parsed
            elif "2020" in year_str:
                result["population_2020"] = parsed
            elif "2024" in year_str:
                result["population_2024"] = parsed
    return result
```

**Explanation:** It accepts `record` and returns `dict[str, int | None]`. See the code below for the full implementation. Key calls include `get()`, `str()`, `_parse_population_value()`.

### `sync_regions`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `336-428`
- **Signature:** `def sync_regions(`
- **Purpose:** Sync regions from PSA API to Supabase.

**Code:**
```python
def sync_regions(
    api_records: list[dict[str, Any]],
    sb: SupabaseClient,
    report: list[dict[str, Any]],
) -> dict[str, int]:
    """Sync regions from PSA API to Supabase."""
    logger.info("=== Syncing REGIONS ===")
    db_rows = sb.fetch_all_rows("regions", "region_id,name,psgc_code,lat,lon")

    if not db_rows:
        logger.warning("No existing regions fetched from DB — skipping sync to avoid duplicates (possible network issue)")
        return {"matched": 0, "updated": 0, "inserted": 0, "unmatched": 0}

    # Build lookup by normalized name
    db_by_name: dict[str, dict[str, Any]] = {}
    for row in db_rows:
        norm = normalize_name(row.get("name", ""))
        if norm:
            db_by_name[norm] = row

    # Alternate name mapping for abbreviated DB region names
    alt_names: dict[str, str] = {
        "ncr": "national capital region",
        "car": "cordillera administrative region",
        "barmm": "bangsamoro autonomous region in muslim mindanao",
        "region ivb": "mimaropa region",
    }

    matched = 0
    updated = 0
    inserted = 0
    unmatched = 0
    max_id = sb.get_max_id("regions", "region_id")
    new_regions: list[dict[str, Any]] = []

    for rec in api_records:
        api_name = rec.get("area_name", "").strip()
        api_norm = normalize_name(api_name)
        psgc_code = rec.get("psgc_code", "")
        pop = extract_population(rec)
        island_group = rec.get("island_region", "")
        geo_level = rec.get("geographic_level", "")

        db_row = db_by_name.get(api_norm)

        # Try alternate name mapping (e.g., API "National Capital Region (NCR)" -> DB "NCR")
        if not db_row:
            for db_norm, db_row_val in db_by_name.items():
                alt_target = alt_names.get(db_norm)
                if alt_target and alt_target == api_norm:
                    db_row = db_row_val
                    break

        if db_row:
            matched += 1
            region_id = db_row["region_id"]
            update_data = {
                "psgc_code": psgc_code,
                "island_group": island_group,
                "geographic_level": geo_level,
                "population_2015": pop["population_2015"],
                "population_2020": pop["population_2020"],
                "population_2024": pop["population_2024"],
            }
            if sb.update_row("regions", "region_id", region_id, update_data):
                updated += 1
        else:
            # Insert new region (e.g., NIR - Negros Island Region)
            max_id += 1
            new_regions.append({
                "region_id": max_id,
                "name": api_name,
                "psgc_code": psgc_code,
                "island_group": island_group,
                "geographic_level": geo_level,
                "population_2015": pop["population_2015"],
                "population_2020": pop["population_2020"],
                "population_2024": pop["population_2024"],
            })
            inserted += 1
            db_by_name[api_norm] = {"region_id": max_id}
            logger.info("Inserting new region: %s (psgc: %s)", api_name, psgc_code)

    # Batch insert new regions
    if new_regions:
        count, err = sb.insert_batch("regions", new_regions)
        if err:
            logger.error("Region insert error: %s", err)
        else:
            logger.info("Inserted %s new regions", count)

    logger.info("Regions: matched=%s updated=%s unmatched=%s", matched, updated, unmatched)
    return {"matched": matched, "updated": updated, "inserted": inserted, "unmatched": unmatched}
```

**Explanation:** It accepts `api_records`, `sb`, `report` and returns `dict[str, int]`. See the code below for the full implementation. Key calls include `info()`, `fetch_all_rows()`, `warning()`, `normalize_name()`, `get()`.

### `sync_provinces`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `431-590`
- **Signature:** `def sync_provinces(`
- **Purpose:** Sync provinces from PSA API to Supabase.

**Code:**
```python
def sync_provinces(
    api_records: list[dict[str, Any]],
    sb: SupabaseClient,
    report: list[dict[str, Any]],
) -> dict[str, int]:
    """Sync provinces from PSA API to Supabase."""
    logger.info("=== Syncing PROVINCES ===")
    db_rows = sb.fetch_all_rows("provinces", "province_id,region_id,name,psgc_code,lat,lon")
    db_regions = sb.fetch_all_rows("regions", "region_id,name,psgc_code")

    if not db_rows:
        logger.warning("No existing provinces fetched from DB — skipping sync (possible network issue)")
        return {"matched": 0, "updated": 0, "inserted": 0, "unmatched": 0}

    # Build region lookup by psgc_code and by normalized name
    region_by_psgc: dict[str, int] = {}
    region_by_name: dict[str, int] = {}
    for r in db_regions:
        if r.get("psgc_code"):
            region_by_psgc[r["psgc_code"]] = r["region_id"]
        region_by_name[normalize_name(r.get("name", ""))] = r["region_id"]

    # Build province lookup by normalized name within region
    db_by_name: dict[tuple[str, int], dict[str, Any]] = {}
    db_by_psgc: dict[str, dict[str, Any]] = {}
    db_by_norm_only: dict[str, dict[str, Any]] = {}
    for row in db_rows:
        norm = normalize_name(row.get("name", ""))
        region_id = row.get("region_id", 0)
        if norm:
            db_by_name[(norm, region_id)] = row
            db_by_norm_only[norm] = row
        # Also index by parenthetical content (old name)
        paren = extract_parenthetical(row.get("name", ""))
        if paren and paren not in db_by_norm_only:
            db_by_norm_only[paren] = row
        if row.get("psgc_code"):
            db_by_psgc[row["psgc_code"]] = row

    # Build reverse NAME_OVERRIDES: API normalized name -> DB normalized name
    api_to_db_override: dict[str, str] = {}
    for db_norm, api_norm in NAME_OVERRIDES.items():
        api_to_db_override[api_norm] = db_norm

    matched = 0
    updated = 0
    inserted = 0
    unmatched = 0
    max_id = sb.get_max_id("provinces", "province_id")

    new_provinces: list[dict[str, Any]] = []

    for rec in api_records:
        api_name = rec.get("area_name", "").strip()
        api_norm = normalize_name(api_name)
        psgc_code = rec.get("psgc_code", "")
        pop = extract_population(rec)
        island_group = rec.get("island_region", "")
        income_class = rec.get("income_classification", "")
        geo_level = rec.get("geographic_level", "")
        old_name = rec.get("old_name", "")

        # Find parent region
        reg_code = rec.get("reg")
        parent_region_id = None
        if reg_code:
            # Try to find region by reg code in psgc_code
            for r_psgc, r_id in region_by_psgc.items():
                if r_psgc.startswith(str(reg_code).zfill(2)):
                    parent_region_id = r_id
                    break

        # Try match by psgc_code first
        db_row = db_by_psgc.get(psgc_code) if psgc_code else None

        # Try match by name within region
        if not db_row and parent_region_id is not None:
            db_row = db_by_name.get((api_norm, parent_region_id))

        # Try match by name only (any region)
        if not db_row:
            db_row = db_by_norm_only.get(api_norm)

        # Try NAME_OVERRIDES (API name -> DB name)
        if not db_row:
            db_norm_override = api_to_db_override.get(api_norm)
            if db_norm_override:
                db_row = db_by_norm_only.get(db_norm_override)

        # Try matching API old_name to DB names
        if not db_row and old_name:
            for alt in normalize_with_old_name(api_name, old_name):
                if alt == api_norm:
                    continue
                db_row = db_by_norm_only.get(alt)
                if db_row:
                    break

        # Try matching API name to DB parenthetical/old names
        if not db_row:
            for db_norm, db_row_val in db_by_norm_only.items():
                db_paren = extract_parenthetical(db_norm)
                if db_paren and db_paren == api_norm:
                    db_row = db_row_val
                    break

        if db_row:
            matched += 1
            province_id = db_row["province_id"]
            update_data = {
                "psgc_code": psgc_code,
                "island_group": island_group,
                "income_classification": income_class,
                "geographic_level": geo_level,
                "old_name": old_name if old_name else None,
                "population_2015": pop["population_2015"],
                "population_2020": pop["population_2020"],
                "population_2024": pop["population_2024"],
            }
            if sb.update_row("provinces", "province_id", province_id, update_data):
                updated += 1
        else:
            # Insert new province
            if parent_region_id is not None:
                max_id += 1
                new_provinces.append({
                    "province_id": max_id,
                    "region_id": parent_region_id,
                    "name": api_name,
                    "psgc_code": psgc_code,
                    "island_group": island_group,
                    "income_classification": income_class,
                    "geographic_level": geo_level,
                    "old_name": old_name if old_name else None,
                    "population_2015": pop["population_2015"],
                    "population_2020": pop["population_2020"],
                    "population_2024": pop["population_2024"],
                })
                inserted += 1
                db_by_psgc[psgc_code] = {"province_id": max_id, "region_id": parent_region_id}
            else:
                unmatched += 1
                report.append({
                    "level": "province",
                    "api_name": api_name,
                    "psgc_code": psgc_code,
                    "status": "unmatched_no_parent",
                })
                logger.warning("Unmatched province (no parent): %s (psgc: %s)", api_name, psgc_code)

    # Batch insert new provinces
    if new_provinces:
        count, err = sb.insert_batch("provinces", new_provinces)
        if err:
            logger.error("Province insert error: %s", err)
        else:
            logger.info("Inserted %s new provinces", count)

    logger.info("Provinces: matched=%s updated=%s inserted=%s unmatched=%s", matched, updated, inserted, unmatched)
    return {"matched": matched, "updated": updated, "inserted": inserted, "unmatched": unmatched}
```

**Explanation:** It accepts `api_records`, `sb`, `report` and returns `dict[str, int]`. See the code below for the full implementation. Key calls include `info()`, `fetch_all_rows()`, `warning()`, `get()`, `normalize_name()`.

### `sync_municipalities`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `593-792`
- **Signature:** `def sync_municipalities(`
- **Purpose:** Sync municipalities from PSA API to Supabase.

**Code:**
```python
def sync_municipalities(
    api_records: list[dict[str, Any]],
    sb: SupabaseClient,
    report: list[dict[str, Any]],
) -> dict[str, int]:
    """Sync municipalities from PSA API to Supabase."""
    logger.info("=== Syncing MUNICIPALITIES ===")
    db_rows = sb.fetch_all_rows(
        "municipalities",
        "municipality_id,province_id,name,psgc_code,lat,lon",
    )
    db_provinces = sb.fetch_all_rows("provinces", "province_id,region_id,name,psgc_code")

    if not db_rows:
        logger.warning("No existing municipalities fetched from DB — skipping sync (possible network issue)")
        return {"matched": 0, "updated": 0, "inserted": 0, "unmatched": 0}

    # Build province lookup by psgc_code
    prov_by_psgc: dict[str, dict[str, Any]] = {}
    for p in db_provinces:
        if p.get("psgc_code"):
            prov_by_psgc[p["psgc_code"]] = p

    # Build municipality lookup
    db_by_name: dict[tuple[str, int], dict[str, Any]] = {}
    db_by_psgc: dict[str, dict[str, Any]] = {}
    db_by_norm_only: dict[str, dict[str, Any]] = {}
    for row in db_rows:
        norm = normalize_name(row.get("name", ""))
        province_id = row.get("province_id", 0)
        if norm:
            db_by_name[(norm, province_id)] = row
            if norm not in db_by_norm_only:
                db_by_norm_only[norm] = row
        # Also index by parenthetical content (old name in parentheses)
        paren = extract_parenthetical(row.get("name", ""))
        if paren and paren not in db_by_norm_only:
            db_by_norm_only[paren] = row
        if row.get("psgc_code"):
            db_by_psgc[row["psgc_code"]] = row

    matched = 0
    updated = 0
    inserted = 0
    unmatched = 0
    max_id = sb.get_max_id("municipalities", "municipality_id")

    new_munis: list[dict[str, Any]] = []
    pop_rows: list[dict[str, Any]] = []

    for rec in api_records:
        api_name = rec.get("area_name", "").strip()
        api_norm = normalize_name(api_name)
        psgc_code = rec.get("psgc_code", "")
        pop = extract_population(rec)
        island_group = rec.get("island_region", "")
        income_class = rec.get("income_classification", "")
        city_class = rec.get("city_class", "")
        geo_level = rec.get("geographic_level", "")
        old_name = rec.get("old_name", "")
        is_city = bool(city_class and city_class.strip())

        # Find parent province via PSGC code prefix
        # Province psgc_code is the first 7 digits of municipality psgc_code (without last 3)
        parent_province_id = None
        if psgc_code and len(psgc_code) >= 7:
            prov_psgc = psgc_code[:7] + "000"
            prov_row = prov_by_psgc.get(prov_psgc)
            if prov_row:
                parent_province_id = prov_row["province_id"]
            else:
                # Try progressively shorter prefixes
                for length in [7, 6, 5]:
                    prefix = psgc_code[:length]
                    for p_psgc, p_row in prov_by_psgc.items():
                        if p_psgc.startswith(prefix):
                            parent_province_id = p_row["province_id"]
                            break
                    if parent_province_id:
                        break

        # Try match by psgc_code first
        db_row = db_by_psgc.get(psgc_code) if psgc_code else None

        # Try match by name within province
        if not db_row and parent_province_id is not None:
            db_row = db_by_name.get((api_norm, parent_province_id))

        # Try match by name only (any province)
        if not db_row:
            db_row = db_by_norm_only.get(api_norm)

        # Try matching API old_name to DB names
        if not db_row and old_name:
            for alt in normalize_with_old_name(api_name, old_name):
                if alt == api_norm:
                    continue
                db_row = db_by_norm_only.get(alt)
                if db_row:
                    break

        # Try matching API name to DB parenthetical/old names
        if not db_row:
            api_paren = extract_parenthetical(api_name)
            if api_paren:
                db_row = db_by_norm_only.get(api_paren)
        if not db_row:
            for db_norm_key, db_row_val in db_by_norm_only.items():
                db_paren = extract_parenthetical(db_norm_key)
                if db_paren and db_paren == api_norm:
                    db_row = db_row_val
                    break

        if db_row:
            matched += 1
            muni_id = db_row["municipality_id"]
            update_data = {
                "psgc_code": psgc_code,
                "island_group": island_group,
                "income_classification": income_class if income_class else None,
                "city_class": city_class if city_class else None,
                "is_city": is_city,
                "geographic_level": geo_level,
                "old_name": old_name if old_name else None,
                "population_2015": pop["population_2015"],
                "population_2020": pop["population_2020"],
                "population_2024": pop["population_2024"],
            }
            if sb.update_row("municipalities", "municipality_id", muni_id, update_data):
                updated += 1

            # Populate municipal_population
            if any(v is not None for v in pop.values()):
                pop_rows.append({
                    "municipality_id": muni_id,
                    "province_id": db_row.get("province_id", parent_province_id or 0),
                    "population_2015": pop["population_2015"],
                    "population_2020": pop["population_2020"],
                    "population_2024": pop["population_2024"],
                })
        else:
            if parent_province_id is not None:
                max_id += 1
                new_munis.append({
                    "municipality_id": max_id,
                    "province_id": parent_province_id,
                    "name": api_name,
                    "psgc_code": psgc_code,
                    "island_group": island_group,
                    "income_classification": income_class if income_class else None,
                    "city_class": city_class if city_class else None,
                    "is_city": is_city,
                    "geographic_level": geo_level,
                    "old_name": old_name if old_name else None,
                    "population_2015": pop["population_2015"],
                    "population_2020": pop["population_2020"],
                    "population_2024": pop["population_2024"],
                })
                inserted += 1
                db_by_psgc[psgc_code] = {"municipality_id": max_id, "province_id": parent_province_id}

                if any(v is not None for v in pop.values()):
                    pop_rows.append({
                        "municipality_id": max_id,
                        "province_id": parent_province_id,
                        "population_2015": pop["population_2015"],
                        "population_2020": pop["population_2020"],
                        "population_2024": pop["population_2024"],
                    })
            else:
                unmatched += 1
                report.append({
                    "level": "municipality",
                    "api_name": api_name,
                    "psgc_code": psgc_code,
                    "status": "unmatched_no_parent",
                })
                logger.warning("Unmatched municipality (no parent): %s (psgc: %s)", api_name, psgc_code)

    # Batch insert new municipalities
    if new_munis:
        count, err = sb.insert_batch("municipalities", new_munis)
        if err:
            logger.error("Municipality insert error: %s", err)
        else:
            logger.info("Inserted %s new municipalities", count)

    # Upsert municipal_population
    if pop_rows:
        # Do in batches of 500
        for i in range(0, len(pop_rows), 500):
            batch = pop_rows[i : i + 500]
            count, err = sb.upsert_batch("municipal_population", batch, on_conflict="municipality_id")
            if err:
                logger.warning("municipal_population upsert error (batch %s): %s", i // 500, err)
            else:
                logger.info("Upserted %s municipal_population rows (batch %s)", count, i // 500)

    logger.info("Municipalities: matched=%s updated=%s inserted=%s unmatched=%s", matched, updated, inserted, unmatched)
    return {"matched": matched, "updated": updated, "inserted": inserted, "unmatched": unmatched}
```

**Explanation:** It accepts `api_records`, `sb`, `report` and returns `dict[str, int]`. See the code below for the full implementation. Key calls include `info()`, `fetch_all_rows()`, `warning()`, `get()`, `normalize_name()`.

### `sync_barangays`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `795-973`
- **Signature:** `def sync_barangays(`
- **Purpose:** Sync barangays from PSA API to Supabase.

**Code:**
```python
def sync_barangays(
    api_records: list[dict[str, Any]],
    sb: SupabaseClient,
    report: list[dict[str, Any]],
) -> dict[str, int]:
    """Sync barangays from PSA API to Supabase."""
    logger.info("=== Syncing BARANGAYS ===")
    db_rows = sb.fetch_all_rows("barangays", "barangay_id,municipality_id,name,psgc_code,lat,lon")
    db_munis = sb.fetch_all_rows("municipalities", "municipality_id,province_id,name,psgc_code")

    if not db_rows:
        logger.warning("No existing barangays fetched from DB — skipping sync (possible network issue)")
        return {"matched": 0, "updated": 0, "inserted": 0, "unmatched": 0}

    # Build municipality lookup by psgc_code and by name
    muni_by_psgc: dict[str, dict[str, Any]] = {}
    muni_by_name: dict[str, dict[str, Any]] = {}
    for m in db_munis:
        if m.get("psgc_code"):
            muni_by_psgc[m["psgc_code"]] = m
        norm = normalize_name(m.get("name", ""))
        if norm and norm not in muni_by_name:
            muni_by_name[norm] = m
        paren = extract_parenthetical(m.get("name", ""))
        if paren and paren not in muni_by_name:
            muni_by_name[paren] = m

    # Build barangay lookup by (normalized name, municipality_id)
    db_by_name: dict[tuple[str, int], dict[str, Any]] = {}
    db_by_psgc: dict[str, dict[str, Any]] = {}
    for row in db_rows:
        norm = normalize_name(row.get("name", ""))
        muni_id = row.get("municipality_id", 0)
        if norm:
            db_by_name[(norm, muni_id)] = row
        if row.get("psgc_code"):
            db_by_psgc[row["psgc_code"]] = row

    # Build API municipality lookup by PSGC code for parent matching fallback
    api_muni_by_psgc: dict[str, str] = {}  # psgc_code -> normalized name
    api_muni_cache = CACHE_DIR / "municipalities.json"
    if api_muni_cache.exists():
        with open(api_muni_cache, "r", encoding="utf-8") as f:
            api_munis = json.load(f)
            for am in api_munis:
                ac = am.get("psgc_code", "")
                if ac:
                    api_muni_by_psgc[ac] = normalize_name(am.get("area_name", ""))

    matched = 0
    updated = 0
    inserted = 0
    unmatched = 0
    max_id = sb.get_max_id("barangays", "barangay_id")

    new_barangays: list[dict[str, Any]] = []
    INSERT_BATCH_SIZE = 200
    total_inserted = 0

    for rec in api_records:
        api_name = rec.get("area_name", "").strip()
        api_norm = normalize_name(api_name)
        psgc_code = rec.get("psgc_code", "")
        pop = extract_population(rec)
        island_group = rec.get("island_region", "")
        urban_rural = rec.get("urban_rural", "")
        geo_level = rec.get("geographic_level", "")
        old_name = rec.get("old_name", "")
        status = rec.get("status", "")

        # Find parent municipality via PSGC code prefix
        # Municipality psgc_code is the first 7 digits + "000" of barangay psgc_code
        parent_muni_id = None
        if psgc_code and len(psgc_code) >= 7:
            muni_psgc = psgc_code[:7] + "000"
            muni_row = muni_by_psgc.get(muni_psgc)
            if muni_row:
                parent_muni_id = muni_row["municipality_id"]
            else:
                # Try matching by shorter prefix
                for length in [7, 6, 5]:
                    prefix = psgc_code[:length]
                    for m_psgc, m_row in muni_by_psgc.items():
                        if m_psgc.startswith(prefix):
                            parent_muni_id = m_row["municipality_id"]
                            break
                    if parent_muni_id:
                        break

        # Fallback: use API municipality cache to find parent by name
        if not parent_muni_id and psgc_code and len(psgc_code) >= 7:
            muni_psgc = psgc_code[:7] + "000"
            api_muni_norm = api_muni_by_psgc.get(muni_psgc)
            if api_muni_norm:
                # Try exact name match
                m_row = muni_by_name.get(api_muni_norm)
                if m_row:
                    parent_muni_id = m_row["municipality_id"]
                else:
                    # Try parenthetical match
                    for mn, mr in muni_by_name.items():
                        if extract_parenthetical(mn) == api_muni_norm:
                            parent_muni_id = mr["municipality_id"]
                            break

        # Try match by psgc_code first
        db_row = db_by_psgc.get(psgc_code) if psgc_code else None

        # Try match by name within municipality
        if not db_row and parent_muni_id is not None:
            db_row = db_by_name.get((api_norm, parent_muni_id))

        if db_row:
            matched += 1
            barangay_id = db_row["barangay_id"]
            update_data = {
                "psgc_code": psgc_code,
                "island_group": island_group,
                "urban_rural": urban_rural if urban_rural else None,
                "geographic_level": geo_level,
                "old_name": old_name if old_name else None,
                "status": status if status else None,
                "population_2015": pop["population_2015"],
                "population_2020": pop["population_2020"],
                "population_2024": pop["population_2024"],
            }
            if sb.update_row("barangays", "barangay_id", barangay_id, update_data):
                updated += 1
        else:
            if parent_muni_id is not None:
                max_id += 1
                new_barangays.append({
                    "barangay_id": max_id,
                    "municipality_id": parent_muni_id,
                    "name": api_name,
                    "psgc_code": psgc_code,
                    "island_group": island_group,
                    "urban_rural": urban_rural if urban_rural else None,
                    "geographic_level": geo_level,
                    "old_name": old_name if old_name else None,
                    "status": status if status else None,
                    "population_2015": pop["population_2015"],
                    "population_2020": pop["population_2020"],
                    "population_2024": pop["population_2024"],
                })
                inserted += 1

                # Batch insert
                if len(new_barangays) >= INSERT_BATCH_SIZE:
                    count, err = sb.insert_batch("barangays", new_barangays)
                    if err:
                        logger.error("Barangay insert error: %s", err)
                    else:
                        total_inserted += count
                        logger.info("Inserted %s barangays (total new: %s)", count, total_inserted)
                    new_barangays = []
            else:
                unmatched += 1
                if unmatched <= 100:  # Log only first 100 to avoid spam
                    report.append({
                        "level": "barangay",
                        "api_name": api_name,
                        "psgc_code": psgc_code,
                        "status": "unmatched_no_parent",
                    })
                if unmatched == 1:
                    logger.warning("First unmatched barangay (no parent): %s (psgc: %s)", api_name, psgc_code)

    # Insert remaining batch
    if new_barangays:
        count, err = sb.insert_batch("barangays", new_barangays)
        if err:
            logger.error("Barangay insert error (final batch): %s", err)
        else:
            total_inserted += count

    logger.info("Barangays: matched=%s updated=%s inserted=%s(total=%s) unmatched=%s",
                matched, updated, inserted, total_inserted, unmatched)
    return {"matched": matched, "updated": updated, "inserted": total_inserted, "unmatched": unmatched}
```

**Explanation:** It accepts `api_records`, `sb`, `report` and returns `dict[str, int]`. See the code below for the full implementation. Key calls include `info()`, `fetch_all_rows()`, `warning()`, `get()`, `normalize_name()`.

### `sync_population_data`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `976-1033`
- **Signature:** `def sync_population_data(`
- **Purpose:** Populate population_data table with all historical population records.

**Code:**
```python
def sync_population_data(
    api_data: dict[str, list[dict[str, Any]]],
    sb: SupabaseClient,
) -> int:
    """Populate population_data table with all historical population records."""
    logger.info("=== Populating population_data table ===")
    rows: list[dict[str, Any]] = []

    level_map = {
        "regions": "region",
        "provinces": "province",
        "municipalities": "municipality",
        "barangays": "barangay",
    }

    for level_key, level_name in level_map.items():
        records = api_data.get(level_key, [])
        for rec in records:
            psgc_code = rec.get("psgc_code", "")
            if not psgc_code:
                continue
            pop_data = rec.get("population_data", [])
            for entry in pop_data:
                year = entry.get("year")
                pop = entry.get("population")
                if year and pop is not None:
                    parsed = _parse_population_value(pop)
                    if parsed is None:
                        continue
                    rows.append({
                        "psgc_code": psgc_code,
                        "geographic_level": level_name,
                        "year": int(year),
                        "population": parsed,
                    })

    # Delete existing population_data, then insert fresh (on_conflict doesn't work
    # with the unique constraint on this PostgREST version)
    delete_url = f"{sb.base_url}/rest/v1/population_data?psgc_code=neq.0000000000"
    try:
        resp = sb.http.delete(delete_url, headers=sb.headers)
        resp.raise_for_status()
        logger.info("Cleared existing population_data rows")
    except Exception as exc:
        logger.warning("Could not clear population_data: %s", exc)

    # Insert in batches of 500
    total = 0
    for i in range(0, len(rows), 500):
        batch = rows[i : i + 500]
        count, err = sb.insert_batch("population_data", batch)
        if err:
            logger.warning("population_data insert error (batch %s): %s", i // 500, err)
        else:
            total += count

    logger.info("Population_data: inserted %s records", total)
    return total
```

**Explanation:** It accepts `api_data`, `sb` and returns `int`. See the code below for the full implementation. Key calls include `info()`, `items()`, `get()`, `_parse_population_value()`, `append()`.

### `sync_municipal_population`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `1036-1080`
- **Signature:** `def sync_municipal_population(`
- **Purpose:** Populate municipal_population table from municipality API data.

**Code:**
```python
def sync_municipal_population(
    api_data: dict[str, list[dict[str, Any]]],
    sb: SupabaseClient,
) -> int:
    """Populate municipal_population table from municipality API data."""
    logger.info("=== Populating municipal_population table ===")

    # Fetch existing municipalities to get municipality_id and province_id by psgc_code
    db_munis = sb.fetch_all_rows("municipalities", "municipality_id,province_id,psgc_code")
    muni_by_psgc: dict[str, dict[str, Any]] = {}
    for m in db_munis:
        code = m.get("psgc_code")
        if code:
            muni_by_psgc[code] = m

    rows: list[dict[str, Any]] = []
    muni_records = api_data.get("municipalities", [])
    for rec in muni_records:
        psgc_code = rec.get("psgc_code", "")
        if not psgc_code:
            continue
        db_muni = muni_by_psgc.get(psgc_code)
        if not db_muni:
            continue
        pop = extract_population(rec)
        rows.append({
            "municipality_id": db_muni["municipality_id"],
            "province_id": db_muni["province_id"],
            "population_2015": pop["population_2015"],
            "population_2020": pop["population_2020"],
            "population_2024": pop["population_2024"],
        })

    # Upsert in batches of 500
    total = 0
    for i in range(0, len(rows), 500):
        batch = rows[i : i + 500]
        count, err = sb.upsert_batch("municipal_population", batch, on_conflict="municipality_id")
        if err:
            logger.warning("municipal_population upsert error (batch %s): %s", i // 500, err)
        else:
            total += count

    logger.info("Municipal_population: upserted %s records", total)
    return total
```

**Explanation:** It accepts `api_data`, `sb` and returns `int`. See the code below for the full implementation. Key calls include `info()`, `fetch_all_rows()`, `get()`, `extract_population()`, `append()`.

### `main`

- **File:** `scripts/sync_psgc_data.py`
- **Lines:** `1088-1180`
- **Signature:** `def main() -> int:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> int:
    parser = argparse.ArgumentParser(description="Sync PSGC data from PSA API to Supabase")
    parser.add_argument("--skip-fetch", action="store_true", help="Use cached JSON instead of fetching from API")
    parser.add_argument("--level", choices=LEVELS, help="Sync only one level")
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")

    psgc_token = os.getenv("PSGC_API_CODE")
    sb_url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
    sb_key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("VITE_SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_SERVICE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
        or os.getenv("VITE_SUPABASE_ANON_KEY")
    )

    if not sb_url or not sb_key:
        logger.error("Missing SUPABASE_URL or SUPABASE key in .env")
        return 1

    if not args.skip_fetch and not psgc_token:
        logger.error("Missing PSGC_API_CODE in .env")
        return 1

    # Initialize clients
    sb = SupabaseClient(sb_url, sb_key)

    # Fetch or load cached data
    api_data: dict[str, list[dict[str, Any]]] = {}
    levels_to_sync = [args.level] if args.level else LEVELS

    if not args.skip_fetch:
        api_client = PsaApiClient(psgc_token)
        for level in levels_to_sync:
            api_data[level] = api_client.fetch_all(level)
    else:
        for level in levels_to_sync:
            cache_path = CACHE_DIR / f"{level}.json"
            if cache_path.exists():
                with open(cache_path, "r", encoding="utf-8") as f:
                    api_data[level] = json.load(f)
                logger.info("Loaded cached %s: %s records", level, len(api_data[level]))
            else:
                logger.error("No cached data for %s. Run without --skip-fetch first.", level)
                return 1

    # Sync each level
    report: list[dict[str, Any]] = []
    summary: dict[str, dict[str, int]] = {}

    if "regions" in levels_to_sync:
        summary["regions"] = sync_regions(api_data.get("regions", []), sb, report)
    if "provinces" in levels_to_sync:
        summary["provinces"] = sync_provinces(api_data.get("provinces", []), sb, report)
    if "municipalities" in levels_to_sync:
        summary["municipalities"] = sync_municipalities(api_data.get("municipalities", []), sb, report)
    if "barangays" in levels_to_sync:
        summary["barangays"] = sync_barangays(api_data.get("barangays", []), sb, report)

    # Populate population tables (only when syncing all levels)
    if not args.level:
        sync_population_data(api_data, sb)
        sync_municipal_population(api_data, sb)

    # Write report
    report_path = CACHE_DIR / "sync_report.csv"
    if report:
        with open(report_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["level", "api_name", "psgc_code", "status"])
            writer.writeheader()
            writer.writerows(report)
        logger.info("Unmatched report written to %s (%s entries)", report_path, len(report))
    else:
        logger.info("No unmatched entries — all records matched!")

    # Print summary
    logger.info("=" * 60)
    logger.info("SYNC SUMMARY")
    logger.info("=" * 60)
    for level, stats in summary.items():
        logger.info(
            "  %s: matched=%s updated=%s inserted=%s unmatched=%s",
            level.ljust(15),
            stats["matched"],
            stats["updated"],
            stats["inserted"],
            stats["unmatched"],
        )
    logger.info("=" * 60)

    return 0
```

**Explanation:** It accepts zero arguments and returns `int`. See the code below for the full implementation. Key calls include `ArgumentParser()`, `add_argument()`, `parse_args()`, `load_dotenv()`, `getenv()`.


## `scripts/temp_db_check.py`

**File:** `scripts/temp_db_check.py`

**Summary:** Source file `scripts/temp_db_check.py`.

_No module-level or class-level functions in this file._

## `scripts/test_api.py`

**File:** `scripts/test_api.py`

**Summary:** Test PSA API pagination.

_No module-level or class-level functions in this file._

## `scripts/verify_sync.py`

**File:** `scripts/verify_sync.py`

**Summary:** Source file `scripts/verify_sync.py`.

_No module-level or class-level functions in this file._

## `supabase/table_scripts/auth_admin_schema.sql`

**File:** `supabase/table_scripts/auth_admin_schema.sql`

**Summary:** SQL schema or migration script that defines the LUMI database tables.

**First lines:**
```sql
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
```


## `supabase/table_scripts/climate_schema.sql`

**File:** `supabase/table_scripts/climate_schema.sql`

**Summary:** SQL schema or migration script that defines the LUMI database tables.

**First lines:**
```sql
-- Historical monthly climate data per municipality (NASA POWER).

create table if not exists public.municipality_climate_monthly (
  municipality_id integer not null,
  year smallint not null,
  month smallint not null,
  t2m double precision,
  t2m_max double precision,
  t2m_min double precision,
  rh2m double precision,
  prectotcorr double precision,
  ws10m double precision,
  allsky_sfc_sw_dwn double precision,
  source text not null default 'NASA POWER',
  created_at timestamptz not null default now(),
  constraint municipality_climate_monthly_pkey primary key (municipality_id, year, month),
  constraint municipality_climate_monthly_municipality_id_fkey foreign key (municipality_id)
    references public.municipalities (municipality_id)
    on update cascade
    on delete restrict,
  constraint municipality_climate_monthly_year_check check (year >= 2018),
  constraint municipality_climate_monthly_month_check check (month between 1 and 12)
);

comment on table public.municipality_climate_monthly is
  'Monthly historical climate data by municipality from NASA POWER.';

comment on column public.municipality_climate_monthly.t2m is
  'Mean air temperature at 2m (C).';
comment on column public.municipality_climate_monthly.t2m_max is
```


## `supabase/table_scripts/geothermal_schema.sql`

**File:** `supabase/table_scripts/geothermal_schema.sql`

**Summary:** SQL schema or migration script that defines the LUMI database tables.

**First lines:**
```sql
-- ============================================================
-- Geothermal tables for LUMI
-- Run this in the Supabase SQL Editor before deploying
-- the geothermal backend integration.
-- ============================================================

-- 1. Geothermal suitability scores per municipality
--    (pre-computed from heat flow, fault, volcano, aquifer data)
CREATE TABLE IF NOT EXISTS "public"."geothermal_suitability" (
    "municipality_id" integer NOT NULL,
    "heat_flow_score" double precision,
    "fault_density" double precision,
    "fault_distance_km" double precision,
    "volcano_distance_km" double precision,
    "aquifer_score" double precision,
    "temperature_score" double precision,
    "geothermal_score" double precision,
    "geothermal_score_mcda" double precision,
    "classification" text,
    "aquifer_fallback" boolean,
    "aquifer_distance_km" double precision,
    CONSTRAINT "geothermal_suitability_pkey" PRIMARY KEY ("municipality_id"),
    CONSTRAINT "geothermal_suitability_municipality_id_fkey"
        FOREIGN KEY ("municipality_id") REFERENCES "public"."municipalities"("municipality_id")
        ON UPDATE CASCADE ON DELETE RESTRICT
);

COMMENT ON TABLE "public"."geothermal_suitability" IS 'Pre-computed geothermal suitability metrics per municipality derived from IHFC heat flow, PHIVOLCS fault data, Smithsonian volcano data, and Zenodo aquifer properties.';
COMMENT ON COLUMN "public"."geothermal_suitability"."heat_flow_score" IS 'Normalized IHFC heat flow score (0-1), range 40-120 mW/m².';
COMMENT ON COLUMN "public"."geothermal_suitability"."fault_density" IS 'Fault length (km) / municipality area (km²).';
```


## `supabase/table_scripts/mcda_weights_schema.sql`

**File:** `supabase/table_scripts/mcda_weights_schema.sql`

**Summary:** SQL schema or migration script that defines the LUMI database tables.

**First lines:**
```sql
-- ============================================================
-- MCDA Weights configuration table for LUMI
-- Stores AHP-derived criterion weights per renewable energy type.
-- Run this in the Supabase SQL Editor.
-- ============================================================

CREATE TABLE IF NOT EXISTS "public"."mcda_weights" (
    "id" serial PRIMARY KEY,
    "energy_type" text NOT NULL,          -- 'geothermal', 'solar', 'wind', 'hydro'
    "criterion" text NOT NULL,              -- e.g. 'heat_flow', 'fault', 'volcano'
    "weight" double precision NOT NULL,     -- 0.0 - 1.0
    "version" integer NOT NULL DEFAULT 1,   -- versioning for AHP revision history
    "is_active" boolean NOT NULL DEFAULT true,
    "updated_at" timestamp with time zone DEFAULT now()
);

-- Unique constraint: only one active weight per criterion per energy type
CREATE UNIQUE INDEX IF NOT EXISTS "idx_mcda_weights_active"
    ON "public"."mcda_weights" ("energy_type", "criterion")
    WHERE "is_active" = true;

COMMENT ON TABLE "public"."mcda_weights" IS 'AHP-derived MCDA criterion weights for renewable energy suitability scoring. Manage via admin panel or SQL.';

-- Grants
GRANT ALL ON TABLE "public"."mcda_weights" TO "anon";
GRANT ALL ON TABLE "public"."mcda_weights" TO "authenticated";
GRANT ALL ON TABLE "public"."mcda_weights" TO "service_role";

-- ============================================================
-- Default geothermal weights (AHP-calculated)
```


## `supabase/table_scripts/municipal_population.sql`

**File:** `supabase/table_scripts/municipal_population.sql`

**Summary:** SQL schema or migration script that defines the LUMI database tables.

**First lines:**
```sql
-- Municipal Population Table
-- --------------------------
-- Stores PSA population census data for population-weighted municipal
-- energy demand estimation (Revision 8).
--
-- Data source: Philippine Statistics Authority (PSA) 2020 Census of Population
-- and Housing, or 2025 population projections.
--
-- Load instruction: Insert rows with province_id referencing provinces table,
-- municipality_id referencing municipalities table, and population count.

create table if not exists public.municipal_population (
  id bigint generated always as identity primary key,
  province_id integer not null references public.provinces(province_id) on delete cascade,
  municipality_id integer not null references public.municipalities(municipality_id) on delete cascade,
  population integer not null check (population >= 0),
  year integer not null default 2020,
  source text default 'PSA 2020 Census',
  created_at timestamp with time zone default now()
);

create index if not exists idx_municipal_population_province_id on public.municipal_population(province_id);
create index if not exists idx_municipal_population_municipality_id on public.municipal_population(municipality_id);

-- Prevent duplicate census rows for the same municipality and year
alter table public.municipal_population
  add constraint if not exists uq_municipal_population_unique
  unique (province_id, municipality_id, year);

-- Example insert (replace with actual PSA data):
```


## `supabase/table_scripts/national_energy_schema.sql`

**File:** `supabase/table_scripts/national_energy_schema.sql`

**Summary:** SQL schema or migration script that defines the LUMI database tables.

**First lines:**
```sql
-- ============================================================
-- LUMI ML Forecasting Module — National Energy Schema
-- Run this in Supabase SQL Editor
-- ============================================================

-- --------------------------------------------------------
-- 1. national_energy_annual
--    Stores DOE Power Statistics (2003–2024) for ML training
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.national_energy_annual (
    year smallint PRIMARY KEY,

    -- Consumption by sector (GWh)
    total_consumption_gwh             decimal(12, 2),
    residential_consumption_gwh       decimal(12, 2),
    commercial_consumption_gwh        decimal(12, 2),
    industrial_consumption_gwh        decimal(12, 2),
    others_consumption_gwh            decimal(12, 2),
    electricity_sales_gwh           decimal(12, 2),
    utilities_own_use_gwh           decimal(12, 2),
    system_losses_gwh               decimal(12, 2),

    -- Peak demand by grid (MW)
    luzon_peak_demand_mw              decimal(12, 2),
    visayas_peak_demand_mw            decimal(12, 2),
    mindanao_peak_demand_mw           decimal(12, 2),
    total_peak_demand_mw              decimal(12, 2),

    -- Generation by grid (GWh)
    luzon_generation_gwh              decimal(12, 2),
```


## `supabase/table_scripts/schema.sql`

**File:** `supabase/table_scripts/schema.sql`

**Summary:** SQL schema or migration script that defines the LUMI database tables.

**First lines:**
```sql
-- Supabase schema for regions, provinces, municipalities, barangays.

create table if not exists public.regions (
  region_id integer primary key,
  name text not null,
  lat double precision,
  lon double precision
);

create table if not exists public.provinces (
  province_id integer primary key,
  region_id integer not null references public.regions(region_id) on update cascade on delete restrict,
  name text not null,
  lat double precision,
  lon double precision
);

create table if not exists public.municipalities (
  municipality_id integer primary key,
  province_id integer not null references public.provinces(province_id) on update cascade on delete restrict,
  name text not null,
  lat double precision,
  lon double precision
);

create table if not exists public.barangays (
  barangay_id integer primary key,
  municipality_id integer not null references public.municipalities(municipality_id) on update cascade on delete restrict,
  name text not null,
  lat double precision,
```


## `supabase/table_scripts/supabase_suitability_migration.sql`

**File:** `supabase/table_scripts/supabase_suitability_migration.sql`

**Summary:** SQL schema or migration script that defines the LUMI database tables.

**First lines:**
```sql
-- LUMI Municipality Suitability Migration
-- Adds renewable energy suitability scoring columns to the municipalities table.
-- Run this against your Supabase project after confirming the municipalities table exists.

-- =============================================================================
-- SOLAR SUITABILITY
-- =============================================================================
ALTER TABLE public.municipalities
ADD COLUMN IF NOT EXISTS solar_suitability_score NUMERIC(5,2) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS solar_classification VARCHAR(20) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS solar_factors JSONB DEFAULT NULL;

-- =============================================================================
-- WIND SUITABILITY
-- =============================================================================
ALTER TABLE public.municipalities
ADD COLUMN IF NOT EXISTS wind_suitability_score NUMERIC(5,2) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS wind_classification VARCHAR(20) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS wind_factors JSONB DEFAULT NULL;

-- =============================================================================
-- HYDRO SUITABILITY
-- =============================================================================
ALTER TABLE public.municipalities
ADD COLUMN IF NOT EXISTS hydro_suitability_score NUMERIC(5,2) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS hydro_classification VARCHAR(20) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS hydro_factors JSONB DEFAULT NULL;

-- =============================================================================
-- GEOTHERMAL SUITABILITY
```


## `vercel.json`

**File:** `vercel.json`

**Summary:** JSON configuration or data file.

**First lines:**
```json
{
  "version": 2,
  "framework": null,
  "buildCommand": null,
  "installCommand": "pip install -r api/requirements.txt",
  "rewrites": [
    { "source": "/api/v1/(.*)", "destination": "/api" }
  ],
  "functions": {
    "api/index.py": {
      "maxDuration": 10,
      "memory": 1024,
      "excludeFiles": "{__pycache__/**,.pytest_cache/**,fastapi-backend/app/services/local_data/**,fastapi-backend/scripts/**}",
      "includeFiles": "{fastapi-backend/**,api/**,DOE_Data_Extracted/data_v2_preprocessed/**}"
    }
  }
}
```


## `scripts/verify_fixes.py`

**File:** `scripts/verify_fixes.py`

**Summary:** Verification script for LUMI v2.1 bug fixes.

_No module-level or class-level functions in this file._

## `windsurf_data_extraction/cleaner.py`

**File:** `windsurf_data_extraction/cleaner.py`

**Summary:** cleaner.py

### `_clean_header`

- **File:** `windsurf_data_extraction/cleaner.py`
- **Lines:** `41-60`
- **Signature:** `def _clean_header(header) -> str:`
- **Purpose:** Normalize column header to snake_case.

**Code:**
```python
def _clean_header(header) -> str:
    """Normalize column header to snake_case."""
    h = str(header).strip().lower() if header is not None else ""
    h = re.sub(r"[^\w\s]", " ", h)
    h = re.sub(r"\s+", "_", h)
    h = re.sub(r"_+", "_", h)
    h = h.strip("_")
    # Common abbreviations
    h = h.replace("mw", "megawatts")
    h = h.replace("kw", "kilowatts")
    h = h.replace("mwh", "megawatt_hours")
    h = h.replace("kwh", "kilowatt_hours")
    h = h.replace("php", "php")
    h = h.replace("us", "")
    h = h.replace("no_", "number")
    h = h.replace("yr", "year")
    h = h.replace("gen", "generation")
    if not h:
        h = "unnamed"
    return h[:80]
```

**Explanation:** It accepts `header` and returns `str`. See the code below for the full implementation. Key calls include `lower()`, `strip()`, `str()`, `sub()`, `replace()`.

### `_parse_number`

- **File:** `windsurf_data_extraction/cleaner.py`
- **Lines:** `63-82`
- **Signature:** `def _parse_number(val: Any) -> float | None:`
- **Purpose:** Extract a numeric value from a string, handling commas, parens, units.

**Code:**
```python
def _parse_number(val: Any) -> float | None:
    """Extract a numeric value from a string, handling commas, parens, units."""
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s:
        return None
    # Remove common wrappers
    s = re.sub(r"[\$,\u20b1\u00a5\u20ac\£]", "", s)  # currency symbols
    s = s.replace(",", "")
    s = s.replace("%", "")
    s = s.replace("(", "-").replace(")", "")
    s = re.sub(r"[A-Za-z/\s]+", "", s)  # strip trailing units like " MW"
    s = s.strip()
    try:
        return float(s)
    except ValueError:
        return None
```

**Explanation:** It accepts `val` and returns `float | None`. See the code below for the full implementation. Key calls include `isna()`, `isinstance()`, `float()`, `strip()`, `str()`.

### `_extract_unit`

- **File:** `windsurf_data_extraction/cleaner.py`
- **Lines:** `85-106`
- **Signature:** `def _extract_unit(val: Any) -> str | None:`
- **Purpose:** Guess the unit from a string value.

**Code:**
```python
def _extract_unit(val: Any) -> str | None:
    """Guess the unit from a string value."""
    if pd.isna(val):
        return None
    s = str(val).strip().lower()
    units = [
        ("megawatts", r"\b(mw|megawatt|megawatts)\b"),
        ("kilowatts", r"\b(kw|kilowatt|kilowatts)\b"),
        ("megawatt_hours", r"\b(mwh|megawatt[-_]?hour|megawatt[-_]?hours)\b"),
        ("kilowatt_hours", r"\b(kwh|kilowatt[-_]?hour|kilowatt[-_]?hours)\b"),
        ("gwh", r"\b(gwh)\b"),
        ("php", r"\b(php|\u20b1)\b"),
        ("usd", r"\b(usd|\$)\b"),
        ("percent", r"%"),
        ("tonnes", r"\b(ton|tons|tonne|tonnes|mt)\b"),
        ("hectares", r"\b(ha|hectare|hectares)\b"),
        ("percent", r"\b(percent|pct)\b"),
    ]
    for unit_name, pattern in units:
        if re.search(pattern, s):
            return unit_name
    return None
```

**Explanation:** It accepts `val` and returns `str | None`. See the code below for the full implementation. Key calls include `isna()`, `lower()`, `strip()`, `str()`, `search()`.

### `_normalize_date`

- **File:** `windsurf_data_extraction/cleaner.py`
- **Lines:** `109-143`
- **Signature:** `def _normalize_date(val: Any) -> str | None:`
- **Purpose:** Try to normalize a date string to YYYY-MM.

**Code:**
```python
def _normalize_date(val: Any) -> str | None:
    """Try to normalize a date string to YYYY-MM."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    # Patterns
    # "January 2024" or "Jan 2024"
    m = re.search(r"([A-Za-z]+)\s+(\d{4})", s)
    if m:
        month_str, year = m.group(1), m.group(2)
        month_map = {
            "jan": "01", "january": "01",
            "feb": "02", "february": "02",
            "mar": "03", "march": "03",
            "apr": "04", "april": "04",
            "may": "05",
            "jun": "06", "june": "06",
            "jul": "07", "july": "07",
            "aug": "08", "august": "08",
            "sep": "09", "sept": "09", "september": "09",
            "oct": "10", "october": "10",
            "nov": "11", "november": "11",
            "dec": "12", "december": "12",
        }
        key = month_str.lower()[:3]
        if key in month_map:
            return f"{year}-{month_map[key]}"
    # "2024" alone
    if re.fullmatch(r"\d{4}", s):
        return f"{s}-01"
    # "2024-01" or "2024/01"
    m = re.search(r"(\d{4})[-/](\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return None
```

**Explanation:** It accepts `val` and returns `str | None`. See the code below for the full implementation. Key calls include `isna()`, `strip()`, `str()`, `search()`, `group()`.

### `_is_noise_row`

- **File:** `windsurf_data_extraction/cleaner.py`
- **Lines:** `146-165`
- **Signature:** `def _is_noise_row(row: pd.Series) -> bool:`
- **Purpose:** Detect footer / header-repeat / page-number rows.

**Code:**
```python
def _is_noise_row(row: pd.Series) -> bool:
    """Detect footer / header-repeat / page-number rows."""
    text = " ".join(str(v).strip().lower() for v in row if pd.notna(v))
    noise_patterns = [
        r"^page\s+\d+",
        r"^source:\s",
        r"^note:\s",
        r"^notes:\s",
        r"^\d+\s+of\s+\d+",
        r"^department\s+of\s+energy",
        r"^doe\s",
        r"^republic\s+of\s+the\s+philippines",
        r"^data\s+as\s+of",
        r"^prepared\s+by",
        r"^\d+$",  # lone page number
    ]
    for pat in noise_patterns:
        if re.search(pat, text):
            return True
    return False
```

**Explanation:** It accepts `row` and returns `bool`. See the code below for the full implementation. Key calls include `join()`, `lower()`, `notna()`, `strip()`, `str()`.

### `_is_mostly_empty`

- **File:** `windsurf_data_extraction/cleaner.py`
- **Lines:** `168-171`
- **Signature:** `def _is_mostly_empty(row: pd.Series, threshold: float = 0.8) -> bool:`
- **Purpose:** Return True if > threshold fraction of cells are empty.

**Code:**
```python
def _is_mostly_empty(row: pd.Series, threshold: float = 0.8) -> bool:
    """Return True if > threshold fraction of cells are empty."""
    empty = sum(1 for v in row if pd.isna(v) or str(v).strip() == "")
    return empty / len(row) >= threshold
```

**Explanation:** It accepts `row`, `threshold` and returns `bool`. See the code below for the full implementation. Key calls include `sum()`, `isna()`, `strip()`, `str()`, `len()`.

### `_detect_category`

- **File:** `windsurf_data_extraction/cleaner.py`
- **Lines:** `179-214`
- **Signature:** `def _detect_category(df: pd.DataFrame, filename: str) -> str:`
- **Purpose:** Guess the renewable / energy category from data content + filename.

**Code:**
```python
def _detect_category(df: pd.DataFrame, filename: str) -> str:
    """Guess the renewable / energy category from data content + filename."""
    try:
        cols_str = " ".join(str(c) for c in df.columns).lower()
        sample = df.head(10).fillna("").astype(str)
        vals_str = " ".join(sample.values.flatten()).lower()
        text_blob = cols_str + " " + vals_str
    except Exception:
        text_blob = ""
    fname = filename.lower()

    scores: dict[str, int] = {
        "solar": 0, "wind": 0, "hydro": 0,
        "geothermal": 0, "biomass": 0,
        "coal": 0, "oil": 0, "natural_gas": 0,
        "general": 0,
    }

    keywords = {
        "solar": ["solar", "photovoltaic", "pv", "sun", "irradiance", "insolation"],
        "wind": ["wind", "turbine", "windspeed", "wind_speed", "onshore", "offshore"],
        "hydro": ["hydro", "hydropower", "dam", "reservoir", "run-of-river", "pumped storage"],
        "geothermal": ["geothermal", "steam", "binary", "flash"],
        "biomass": ["biomass", "bagasse", "rice husk", "municipal solid waste", "msw"],
        "coal": ["coal", "subcritical", "supercritical", "ultra supercritical"],
        "oil": ["diesel", "oil", "bunker", "fuel oil", "petroleum"],
        "natural_gas": ["natural gas", "lng", "liquefied natural gas", "gas turbine"],
    }

    for cat, words in keywords.items():
        for w in words:
            scores[cat] += text_blob.count(w)
            scores[cat] += fname.count(w) * 3

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"
```

**Explanation:** It accepts `df`, `filename` and returns `str`. See the code below for the full implementation. Key calls include `lower()`, `astype()`, `join()`, `fillna()`, `flatten()`.

### `_has_title_row`

- **File:** `windsurf_data_extraction/cleaner.py`
- **Lines:** `222-237`
- **Signature:** `def _has_title_row(df: pd.DataFrame) -> bool:`
- **Purpose:** Heuristic: first row is a title if most cells are empty or it's very long.

**Code:**
```python
def _has_title_row(df: pd.DataFrame) -> bool:
    """Heuristic: first row is a title if most cells are empty or it's very long."""
    if df.empty or len(df) < 2:
        return False
    first = df.iloc[0]
    non_empty = sum(1 for v in first if pd.notna(v) and str(v).strip() != "")
    # If only 1 cell is non-empty in first row, it's likely a title
    if non_empty == 1 and len(df.columns) > 1:
        return True
    # If first row text is much longer than second row header text
    first_text_len = sum(len(str(v)) for v in first if pd.notna(v))
    second = df.iloc[1]
    second_text_len = sum(len(str(v)) for v in second if pd.notna(v))
    if first_text_len > second_text_len * 3 and non_empty <= 2:
        return True
    return False
```

**Explanation:** It accepts `df` and returns `bool`. See the code below for the full implementation. Key calls include `len()`, `sum()`, `notna()`, `strip()`, `str()`.

### `read_csv_smart`

- **File:** `windsurf_data_extraction/cleaner.py`
- **Lines:** `240-264`
- **Signature:** `def read_csv_smart(path: Path) -> pd.DataFrame | None:`
- **Purpose:** Read a CSV, attempting to skip title rows.

**Code:**
```python
def read_csv_smart(path: Path) -> pd.DataFrame | None:
    """Read a CSV, attempting to skip title rows."""
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=True)
    except Exception:
        return None
    if df.empty:
        return df

    # Try to detect and skip title row(s)
    attempts = 0
    while _has_title_row(df) and attempts < 3 and len(df) > 1:
        # Use second row as header
        new_headers = df.iloc[1]
        df = df.iloc[2:].reset_index(drop=True)
        df.columns = new_headers
        attempts += 1

    # If still looks like title (first row has 1 non-empty cell), skip it
    if _has_title_row(df) and len(df) > 1:
        new_headers = df.iloc[1]
        df = df.iloc[2:].reset_index(drop=True)
        df.columns = new_headers

    return df
```

**Explanation:** It accepts `path` and returns `pd.DataFrame | None`. See the code below for the full implementation. Key calls include `read_csv()`, `_has_title_row()`, `reset_index()`, `len()`.

### `clean_table`

- **File:** `windsurf_data_extraction/cleaner.py`
- **Lines:** `272-329`
- **Signature:** `def clean_table(df: pd.DataFrame, filename: str) -> pd.DataFrame | None:`
- **Purpose:** Apply full cleaning pipeline to a raw DataFrame.

**Code:**
```python
def clean_table(df: pd.DataFrame, filename: str) -> pd.DataFrame | None:
    """
    Apply full cleaning pipeline to a raw DataFrame.

    Returns cleaned DataFrame or None if table is unusable.
    """
    if df.empty:
        return None

    # --- headers ---
    df.columns = [_clean_header(c) for c in df.columns]

    # --- deduplicate columns ---
    seen: dict[str, int] = {}
    new_cols: list[str] = []
    for c in df.columns:
        if c in seen:
            seen[c] += 1
            new_cols.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            new_cols.append(c)
    df.columns = new_cols

    # --- drop noise rows ---
    mask = df.apply(lambda row: not (_is_noise_row(row) or _is_mostly_empty(row)), axis=1)
    df = df[mask].reset_index(drop=True)

    if df.empty:
        return None

    # --- normalize numeric-looking columns ---
    for col in df.columns:
        # Try to extract numbers
        numeric_vals = df[col].apply(_parse_number)
        non_null = numeric_vals.notna().sum()
        # If >50% of non-empty cells are numeric, create _numeric + _unit columns
        total_non_empty = df[col].apply(lambda x: pd.notna(x) and str(x).strip() != "").sum()
        if total_non_empty > 0 and non_null / total_non_empty >= 0.5:
            df[f"{col}_numeric"] = numeric_vals
            # Try to infer unit from first few non-null values
            units = df[col].apply(_extract_unit)
            most_common = units.mode()
            if len(most_common) > 0 and most_common.iloc[0] is not None:
                df[f"{col}_unit"] = most_common.iloc[0]

    # --- normalize date-like columns ---
    for col in df.columns:
        if "date" in col or "year" in col or "month" in col or "period" in col:
            norm_dates = df[col].apply(_normalize_date)
            if norm_dates.notna().sum() > 0:
                df[f"{col}_normalized"] = norm_dates

    # --- add provenance ---
    df["source_pdf"] = filename
    df["detected_category"] = _detect_category(df, filename)

    return df
```

**Explanation:** It accepts `df`, `filename` and returns `pd.DataFrame | None`. See the code below for the full implementation. Key calls include `_clean_header()`, `append()`, `apply()`, `_is_noise_row()`, `_is_mostly_empty()`.

### `export_by_category`

- **File:** `windsurf_data_extraction/cleaner.py`
- **Lines:** `337-372`
- **Signature:** `def export_by_category(all_cleaned: list[pd.DataFrame]) -> dict[str, list[Path]]:`
- **Purpose:** Group cleaned tables by detected category and write consolidated CSVs.

**Code:**
```python
def export_by_category(all_cleaned: list[pd.DataFrame]) -> dict[str, list[Path]]:
    """
    Group cleaned tables by detected category and write consolidated CSVs.
    """
    category_dfs: dict[str, list[pd.DataFrame]] = {}
    for df in all_cleaned:
        cat = str(df["detected_category"].iloc[0]) if "detected_category" in df.columns else "general"
        category_dfs.setdefault(cat, []).append(df)

    exported: dict[str, list[Path]] = {}
    for cat, dfs in category_dfs.items():
        cat_dir = OUTPUT_DIR / cat
        cat_dir.mkdir(parents=True, exist_ok=True)

        # Write individual files
        for idx, df in enumerate(dfs, start=1):
            out_path = cat_dir / f"{cat}_consolidated_{idx:03d}.csv"
            df.to_csv(out_path, index=False, encoding="utf-8-sig")
            exported.setdefault(cat, []).append(out_path)

        # Also write a mega-consolidated file if >1 table
        if len(dfs) > 1:
            try:
                # Only keep columns common to all tables
                common_cols = set(dfs[0].columns)
                for d in dfs[1:]:
                    common_cols &= set(d.columns)
                if common_cols:
                    mega = pd.concat([d[list(common_cols)] for d in dfs], ignore_index=True)
                    mega_path = cat_dir / f"{cat}_all.csv"
                    mega.to_csv(mega_path, index=False, encoding="utf-8-sig")
                    exported.setdefault(cat, []).append(mega_path)
            except Exception as exc:
                logger.warning("Could not build mega-consolidated for %s: %s", cat, exc)

    return exported
```

**Explanation:** It accepts `all_cleaned` and returns `dict[str, list[Path]]`. See the code below for the full implementation. Key calls include `append()`, `str()`, `setdefault()`, `items()`, `mkdir()`.

### `run_cleaning`

- **File:** `windsurf_data_extraction/cleaner.py`
- **Lines:** `380-446`
- **Signature:** `def run_cleaning() -> dict[str, Any]:`
- **Purpose:** Runs cleaning.

**Code:**
```python
def run_cleaning() -> dict[str, Any]:
    csv_files = sorted(INPUT_DIR.glob("*.csv"))
    if not csv_files:
        logger.error("No raw CSVs found in %s", INPUT_DIR)
        return {}

    cleaned: list[pd.DataFrame] = []
    report_rows: list[dict[str, Any]] = []

    for path in csv_files:
        try:
            df = read_csv_smart(path)
            if df is None:
                report_rows.append({
                    "file": path.name,
                    "original_rows": 0,
                    "cleaned_rows": 0,
                    "columns": 0,
                    "category": "error",
                    "error": "Could not read CSV",
                })
                continue
            cleaned_df = clean_table(df, path.name)
            if cleaned_df is not None and not cleaned_df.empty:
                cleaned.append(cleaned_df)
                report_rows.append({
                    "file": path.name,
                    "original_rows": len(df),
                    "cleaned_rows": len(cleaned_df),
                    "columns": len(cleaned_df.columns),
                    "category": cleaned_df["detected_category"].iloc[0],
                })
            else:
                report_rows.append({
                    "file": path.name,
                    "original_rows": len(df),
                    "cleaned_rows": 0,
                    "columns": 0,
                    "category": "discarded",
                })
        except Exception as exc:
            logger.error("Failed to clean %s: %s", path.name, exc)
            report_rows.append({
                "file": path.name,
                "original_rows": 0,
                "cleaned_rows": 0,
                "columns": 0,
                "category": "error",
                "error": str(exc),
            })

    exported = export_by_category(cleaned)

    summary = {
        "raw_files_processed": len(csv_files),
        "tables_cleaned": len(cleaned),
        "tables_discarded": len([r for r in report_rows if r["cleaned_rows"] == 0]),
        "category_counts": {cat: len(dfs) for cat, dfs in {str(df["detected_category"].iloc[0]): [df] for df in cleaned}.items()},
        "files": report_rows,
        "exported_paths": {k: [str(p.relative_to(OUTPUT_DIR)) for p in v] for k, v in exported.items()},
    }

    report_path = REPORTS_DIR / "cleaning_report.json"
    with report_path.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False, default=str)
    logger.info("Cleaning report: %s", report_path)
    return summary
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `sorted()`, `glob()`, `error()`, `read_csv_smart()`, `clean_table()`.


## `windsurf_data_extraction/extract_compendium.py`

**File:** `windsurf_data_extraction/extract_compendium.py`

**Summary:** extract_compendium.py

### `_slugify`

- **File:** `windsurf_data_extraction/extract_compendium.py`
- **Lines:** `32-37`
- **Signature:** `def _slugify(name: str) -> str:`
- **Purpose:** Handles  slugify.

**Code:**
```python
def _slugify(name: str) -> str:
    import re
    base = Path(name).stem
    base = re.sub(r"[^\w\s-]", "", base)
    base = re.sub(r"[-\s]+", "_", base)
    return base.lower().strip("_")[:80]
```

**Explanation:** It accepts `name` and returns `str`. See the code below for the full implementation. Key calls include `Path()`, `sub()`, `strip()`, `lower()`.

### `extract_compendium`

- **File:** `windsurf_data_extraction/extract_compendium.py`
- **Lines:** `40-117`
- **Signature:** `def extract_compendium() -> dict[str, Any]:`
- **Purpose:** Extracts compendium.

**Code:**
```python
def extract_compendium() -> dict[str, Any]:
    slug = _slugify(PDF_PATH.name)
    logger.info("Extracting compendium: %s", PDF_PATH.name)

    # Get page count with PyMuPDF
    doc = fitz.open(str(PDF_PATH))
    total_pages = len(doc)
    doc.close()
    logger.info("  Total pages: %s", total_pages)

    all_tables: list[dict[str, Any]] = []
    text_pages: list[dict[str, Any]] = []

    with pdfplumber.open(str(PDF_PATH)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            if page_num % BATCH_SIZE == 0:
                logger.info("  Processing page %s/%s", page_num, total_pages)

            # Extract text
            text = page.extract_text() or ""
            if text.strip():
                text_pages.append({
                    "page_number": page_num,
                    "text": text,
                    "word_count": len(text.split()),
                })

            # Extract tables
            tables = page.find_tables()
            for t_idx, table in enumerate(tables):
                try:
                    df = pd.DataFrame(table.extract())
                    if df.empty:
                        continue
                    if len(df) > 1:
                        headers = [str(c).strip() if c is not None else "" for c in df.iloc[0]]
                        df = df.iloc[1:].reset_index(drop=True)
                        df.columns = headers
                    all_tables.append({
                        "page": page_num,
                        "table_index": t_idx,
                        "columns": list(df.columns),
                        "rows": df.to_dict(orient="records"),
                        "row_count": len(df),
                    })
                except Exception as exc:
                    logger.debug("Table skip on page %s: %s", page_num, exc)

    logger.info("  Extracted %s tables, %s text pages", len(all_tables), len(text_pages))

    # Write tables
    table_paths: list[str] = []
    for idx, table in enumerate(all_tables, start=1):
        df = pd.DataFrame(table["rows"])
        out_name = f"{slug}_table_{idx:04d}_p{table['page']}.csv"
        out_path = RAW_TABLES_DIR / out_name
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        table_paths.append(str(out_path.relative_to(OUTPUT_DIR)))

    # Write text
    text_out_dir = RAW_TEXT_DIR / slug
    text_out_dir.mkdir(parents=True, exist_ok=True)
    for page in text_pages:
        ppath = text_out_dir / f"page_{page['page_number']:04d}.txt"
        ppath.write_text(page["text"], encoding="utf-8")
    full_text = "\n\n---PAGE BREAK---\n\n".join(p["text"] for p in text_pages)
    (text_out_dir / "full_text.txt").write_text(full_text, encoding="utf-8")

    report = {
        "pdf_name": PDF_PATH.name,
        "slug": slug,
        "tables_extracted": len(all_tables),
        "table_files": table_paths,
        "pages": total_pages,
        "text_dir": str(text_out_dir.relative_to(OUTPUT_DIR)),
    }
    logger.info("  Done: %s tables written", len(all_tables))
    return report
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `_slugify()`, `info()`, `open()`, `str()`, `len()`.


## `windsurf_data_extraction/pdf_extractor.py`

**File:** `windsurf_data_extraction/pdf_extractor.py`

**Summary:** pdf_extractor.py

### `_slugify`

- **File:** `windsurf_data_extraction/pdf_extractor.py`
- **Lines:** `51-56`
- **Signature:** `def _slugify(name: str) -> str:`
- **Purpose:** Create a filesystem-safe slug from a filename.

**Code:**
```python
def _slugify(name: str) -> str:
    """Create a filesystem-safe slug from a filename."""
    base = Path(name).stem
    base = re.sub(r"[^\w\s-]", "", base)
    base = re.sub(r"[-\s]+", "_", base)
    return base.lower().strip("_")[:80]
```

**Explanation:** It accepts `name` and returns `str`. See the code below for the full implementation. Key calls include `Path()`, `sub()`, `strip()`, `lower()`.

### `_df_to_csv`

- **File:** `windsurf_data_extraction/pdf_extractor.py`
- **Lines:** `59-61`
- **Signature:** `def _df_to_csv(df: pd.DataFrame, path: Path) -> None:`
- **Purpose:** Write DataFrame to CSV with consistent settings.

**Code:**
```python
def _df_to_csv(df: pd.DataFrame, path: Path) -> None:
    """Write DataFrame to CSV with consistent settings."""
    df.to_csv(path, index=False, encoding="utf-8-sig")
```

**Explanation:** It accepts `df`, `path` and returns `None`. See the code below for the full implementation. Key calls include `to_csv()`.

### `extract_with_pdfplumber`

- **File:** `windsurf_data_extraction/pdf_extractor.py`
- **Lines:** `69-107`
- **Signature:** `def extract_with_pdfplumber(pdf_path: Path) -> list[dict[str, Any]]:`
- **Purpose:** Extract tables from a PDF using pdfplumber.

**Code:**
```python
def extract_with_pdfplumber(pdf_path: Path) -> list[dict[str, Any]]:
    """
    Extract tables from a PDF using pdfplumber.

    Returns a list of dicts:
      {
        "page": int,
        "table_index": int,
        "strategy": "pdfplumber",
        "columns": list,
        "rows": list[dict],
        "row_count": int,
      }
    """
    results: list[dict[str, Any]] = []
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.find_tables()
                for t_idx, table in enumerate(tables):
                    df = pd.DataFrame(table.extract())
                    if df.empty:
                        continue
                    # Use first row as header if it looks like headers
                    if len(df) > 1:
                        headers = [str(c).strip() if c is not None else "" for c in df.iloc[0]]
                        df = df.iloc[1:].reset_index(drop=True)
                        df.columns = headers
                    results.append({
                        "page": page_num,
                        "table_index": t_idx,
                        "strategy": "pdfplumber",
                        "columns": list(df.columns),
                        "rows": df.to_dict(orient="records"),
                        "row_count": len(df),
                    })
    except Exception as exc:
        logger.warning("pdfplumber failed for %s: %s", pdf_path.name, exc)
    return results
```

**Explanation:** It accepts `pdf_path` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `open()`, `enumerate()`, `warning()`, `str()`, `find_tables()`.

### `extract_with_camelot`

- **File:** `windsurf_data_extraction/pdf_extractor.py`
- **Lines:** `115-148`
- **Signature:** `def extract_with_camelot(pdf_path: Path) -> list[dict[str, Any]]:`
- **Purpose:** Extract tables using camelot (lattice + stream modes).

**Code:**
```python
def extract_with_camelot(pdf_path: Path) -> list[dict[str, Any]]:
    """
    Extract tables using camelot (lattice + stream modes).
    """
    results: list[dict[str, Any]] = []
    try:
        import camelot
    except ImportError:
        logger.warning("camelot not installed; skipping")
        return results

    for flavor in ("lattice", "stream"):
        try:
            tables = camelot.read_pdf(str(pdf_path), flavor=flavor, pages="all")
            for t_idx, table in enumerate(tables):
                df = table.df
                if df.empty:
                    continue
                # Try to promote first row to header
                if len(df) > 1:
                    headers = [str(c).strip() if c is not None else "" for c in df.iloc[0]]
                    df = df.iloc[1:].reset_index(drop=True)
                    df.columns = headers
                results.append({
                    "page": table.page,
                    "table_index": t_idx,
                    "strategy": f"camelot-{flavor}",
                    "columns": list(df.columns),
                    "rows": df.to_dict(orient="records"),
                    "row_count": len(df),
                })
        except Exception as exc:
            logger.warning("camelot-%s failed for %s: %s", flavor, pdf_path.name, exc)
    return results
```

**Explanation:** It accepts `pdf_path` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `warning()`, `read_pdf()`, `enumerate()`, `str()`, `append()`.

### `extract_text_with_pymupdf`

- **File:** `windsurf_data_extraction/pdf_extractor.py`
- **Lines:** `156-176`
- **Signature:** `def extract_text_with_pymupdf(pdf_path: Path) -> dict[str, Any]:`
- **Purpose:** Extract full text and metadata with PyMuPDF.

**Code:**
```python
def extract_text_with_pymupdf(pdf_path: Path) -> dict[str, Any]:
    """
    Extract full text and metadata with PyMuPDF.
    """
    doc = fitz.open(str(pdf_path))
    metadata = doc.metadata
    pages_text: list[dict[str, Any]] = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        pages_text.append({
            "page_number": page_num + 1,
            "text": text,
            "word_count": len(text.split()),
        })
    doc.close()
    return {
        "metadata": metadata,
        "pages": pages_text,
        "total_pages": len(pages_text),
    }
```

**Explanation:** It accepts `pdf_path` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `open()`, `str()`, `range()`, `len()`, `load_page()`.

### `extract_pdf`

- **File:** `windsurf_data_extraction/pdf_extractor.py`
- **Lines:** `184-250`
- **Signature:** `def extract_pdf(pdf_path: Path) -> dict[str, Any]:`
- **Purpose:** Run the full extraction pipeline on a single PDF.

**Code:**
```python
def extract_pdf(pdf_path: Path) -> dict[str, Any]:
    """
    Run the full extraction pipeline on a single PDF.

    Returns extraction report dict.
    """
    slug = _slugify(pdf_path.name)
    logger.info("Extracting: %s", pdf_path.name)

    # --- 1. pdfplumber ---
    plumber_tables = extract_with_pdfplumber(pdf_path)
    logger.info("  pdfplumber: %s tables", len(plumber_tables))

    # --- 2. camelot ---
    camelot_tables = extract_with_camelot(pdf_path)
    logger.info("  camelot: %s tables", len(camelot_tables))

    # Merge tables (deduplicate by row count + first 3 column names)
    all_tables = plumber_tables.copy()
    seen_signatures = set()
    for t in plumber_tables:
        sig = (t["row_count"], tuple(t["columns"][:3]))
        seen_signatures.add(sig)

    for t in camelot_tables:
        sig = (t["row_count"], tuple(t["columns"][:3]))
        if sig not in seen_signatures:
            all_tables.append(t)
            seen_signatures.add(sig)

    # --- 3. PyMuPDF text ---
    text_data = extract_text_with_pymupdf(pdf_path)
    logger.info("  PyMuPDF: %s pages", text_data["total_pages"])

    # --- Write outputs ---
    # Tables as individual CSVs
    table_paths: list[str] = []
    for idx, table in enumerate(all_tables, start=1):
        df = pd.DataFrame(table["rows"])
        out_name = f"{slug}_table_{idx:03d}_p{table['page']}.csv"
        out_path = RAW_TABLES_DIR / out_name
        _df_to_csv(df, out_path)
        table_paths.append(str(out_path.relative_to(OUTPUT_DIR)))

    # Text per page
    text_out_dir = RAW_TEXT_DIR / slug
    text_out_dir.mkdir(parents=True, exist_ok=True)
    for page in text_data["pages"]:
        ppath = text_out_dir / f"page_{page['page_number']:04d}.txt"
        ppath.write_text(page["text"], encoding="utf-8")

    # Full text concatenated
    full_text_path = text_out_dir / "full_text.txt"
    full_text = "\n\n---PAGE BREAK---\n\n".join(p["text"] for p in text_data["pages"])
    full_text_path.write_text(full_text, encoding="utf-8")

    report = {
        "pdf_name": pdf_path.name,
        "slug": slug,
        "tables_extracted": len(all_tables),
        "table_files": table_paths,
        "pages": text_data["total_pages"],
        "text_dir": str(text_out_dir.relative_to(OUTPUT_DIR)),
        "pdf_metadata": text_data["metadata"],
    }
    logger.info("  Done: %s tables -> %s", len(all_tables), RAW_TABLES_DIR.name)
    return report
```

**Explanation:** It accepts `pdf_path` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `_slugify()`, `info()`, `extract_with_pdfplumber()`, `len()`, `extract_with_camelot()`.

### `run_all`

- **File:** `windsurf_data_extraction/pdf_extractor.py`
- **Lines:** `258-281`
- **Signature:** `def run_all() -> dict[str, Any]:`
- **Purpose:** Extract every PDF in DOE_Data/.

**Code:**
```python
def run_all() -> dict[str, Any]:
    """Extract every PDF in DOE_Data/."""
    pdfs = sorted(DOE_DIR.glob("*.pdf"))
    if not pdfs:
        logger.error("No PDFs found in %s", DOE_DIR)
        return {}

    reports: list[dict[str, Any]] = []
    for pdf in pdfs:
        report = extract_pdf(pdf)
        reports.append(report)

    summary = {
        "pdfs_processed": len(reports),
        "total_tables": sum(r["tables_extracted"] for r in reports),
        "total_pages": sum(r["pages"] for r in reports),
        "per_pdf": reports,
    }

    meta_path = OUTPUT_DIR / "metadata.json"
    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False, default=str)
    logger.info("Summary written to %s", meta_path)
    return summary
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `sorted()`, `glob()`, `error()`, `extract_pdf()`, `append()`.


## `windsurf_data_extraction/rag_converter.py`

**File:** `windsurf_data_extraction/rag_converter.py`

**Summary:** rag_converter.py

### `_row_to_sentence`

- **File:** `windsurf_data_extraction/rag_converter.py`
- **Lines:** `51-89`
- **Signature:** `def _row_to_sentence(row: dict[str, Any], category: str) -> str:`
- **Purpose:** Turn a data row into a concise natural-language statement.

**Code:**
```python
def _row_to_sentence(row: dict[str, Any], category: str) -> str:
    """Turn a data row into a concise natural-language statement."""
    parts: list[str] = []
    region = row.get("region") or row.get("location") or row.get("area") or row.get("province")
    year = row.get("year") or row.get("date") or row.get("period")

    # Build a descriptive sentence
    if region:
        parts.append(f"In {region}")
    if year:
        parts.append(f"for {year}")

    # Add key metrics
    metrics: list[str] = []
    for k, v in row.items():
        if k in _SKIP_COLS or v is None or pd.isna(v):
            continue
        # Try to find numeric + unit pairs
        if k.endswith("_numeric"):
            base = k.replace("_numeric", "")
            unit_key = f"{base}_unit"
            unit = row.get(unit_key)
            val_str = f"{v} {unit}" if unit else str(v)
            metrics.append(f"{base.replace('_', ' ')} was {val_str}")
        elif not k.endswith("_unit") and not k.endswith("_normalized"):
            # Skip raw columns that have a _numeric counterpart
            numeric_key = f"{k}_numeric"
            if numeric_key not in row:
                metrics.append(f"{k.replace('_', ' ')} was {v}")

    if metrics:
        parts.append(", ".join(metrics[:6]))  # limit to avoid overly long chunks

    sentence = ", ".join(p for p in parts if p)
    if not sentence:
        sentence = f"Data point in {category}: " + ", ".join(
            f"{k}={v}" for k, v in row.items() if k not in _SKIP_COLS and pd.notna(v)
        )[:200]
    return sentence.strip() + "."
```

**Explanation:** It accepts `row`, `category` and returns `str`. See the code below for the full implementation. Key calls include `get()`, `append()`, `items()`, `endswith()`, `isna()`.

### `_chunk_from_row`

- **File:** `windsurf_data_extraction/rag_converter.py`
- **Lines:** `92-109`
- **Signature:** `def _chunk_from_row(`
- **Purpose:** Build a single RAG chunk from a CSV row.

**Code:**
```python
def _chunk_from_row(
    row: dict[str, Any],
    idx: int,
    source_file: str,
    category: str,
    columns: list[str],
) -> dict[str, Any]:
    """Build a single RAG chunk from a CSV row."""
    return {
        "content": _row_to_sentence(row, category),
        "metadata": {
            "source": row.get("source_pdf", source_file),
            "category": category,
            "table": source_file,
            "row_id": idx,
            "columns": columns,
        },
    }
```

**Explanation:** It accepts `row`, `idx`, `source_file`, `category`, `columns` and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `_row_to_sentence()`, `get()`.

### `convert_csv_to_chunks`

- **File:** `windsurf_data_extraction/rag_converter.py`
- **Lines:** `112-135`
- **Signature:** `def convert_csv_to_chunks(csv_path: Path, category: str) -> list[dict[str, Any]]:`
- **Purpose:** Read a CSV and turn every row into a RAG chunk.

**Code:**
```python
def convert_csv_to_chunks(csv_path: Path, category: str) -> list[dict[str, Any]]:
    """Read a CSV and turn every row into a RAG chunk."""
    try:
        df = pd.read_csv(csv_path, dtype=str)
    except Exception as exc:
        logger.warning("Could not read %s: %s", csv_path.name, exc)
        return []

    if df.empty:
        return []

    # Add row_id if missing
    if "row_id" not in df.columns:
        df["row_id"] = df.index + 1

    chunks: list[dict[str, Any]] = []
    columns = [c for c in df.columns if c not in _SKIP_COLS]
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        chunk = _chunk_from_row(row_dict, int(idx), csv_path.name, category, columns)
        chunks.append(chunk)

    logger.info("  %s -> %s chunks", csv_path.name, len(chunks))
    return chunks
```

**Explanation:** It accepts `csv_path`, `category` and returns `list[dict[str, Any]]`. See the code below for the full implementation. Key calls include `read_csv()`, `warning()`, `iterrows()`, `to_dict()`, `_chunk_from_row()`.

### `run_conversion`

- **File:** `windsurf_data_extraction/rag_converter.py`
- **Lines:** `138-187`
- **Signature:** `def run_conversion() -> dict[str, Any]:`
- **Purpose:** Convert every CSV in csv/ into RAG JSON files.

**Code:**
```python
def run_conversion() -> dict[str, Any]:
    """Convert every CSV in csv/ into RAG JSON files."""
    if not CSV_DIR.exists():
        logger.error("CSV dir not found: %s", CSV_DIR)
        return {}

    all_chunks_by_cat: dict[str, list[dict[str, Any]]] = {}
    total_files = 0

    for cat_dir in CSV_DIR.iterdir():
        if not cat_dir.is_dir():
            continue
        category = cat_dir.name
        for csv_file in cat_dir.glob("*.csv"):
            # Skip mega-consolidated files; they only contain common columns
            # (usually just metadata) and produce empty chunks. The individual
            # *_consolidated_*.csv files have the full schema.
            if csv_file.name.endswith("_all.csv"):
                logger.info("Skipping mega-consolidated file: %s", csv_file.name)
                continue
            chunks = convert_csv_to_chunks(csv_file, category)
            if chunks:
                all_chunks_by_cat.setdefault(category, []).extend(chunks)
                total_files += 1

    # Write per-category JSON
    summary: dict[str, Any] = {"categories": {}, "total_chunks": 0}
    for cat, chunks in all_chunks_by_cat.items():
        out_path = RAG_DIR / f"{cat}_chunks.json"
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(chunks, fh, indent=2, ensure_ascii=False)
        summary["categories"][cat] = {
            "file": str(out_path.relative_to(REPO_ROOT / "windsurf_data_extraction")),
            "chunks": len(chunks),
        }
        summary["total_chunks"] += len(chunks)
        logger.info("Wrote %s (%s chunks)", out_path.name, len(chunks))

    # Also write a master index
    master_path = RAG_DIR / "all_chunks.json"
    all_chunks: list[dict[str, Any]] = []
    for chunks in all_chunks_by_cat.values():
        all_chunks.extend(chunks)
    with master_path.open("w", encoding="utf-8") as fh:
        json.dump(all_chunks, fh, indent=2, ensure_ascii=False)
    summary["master_file"] = str(master_path.relative_to(REPO_ROOT / "windsurf_data_extraction"))
    summary["total_files"] = total_files

    logger.info("RAG conversion complete: %s total chunks", summary["total_chunks"])
    return summary
```

**Explanation:** It accepts zero arguments and returns `dict[str, Any]`. See the code below for the full implementation. Key calls include `exists()`, `error()`, `iterdir()`, `glob()`, `is_dir()`.


## `windsurf_data_extraction/run_extraction.py`

**File:** `windsurf_data_extraction/run_extraction.py`

**Summary:** run_extraction.py

### `generate_quality_report`

- **File:** `windsurf_data_extraction/run_extraction.py`
- **Lines:** `41-140`
- **Signature:** `def generate_quality_report(`
- **Purpose:** Write a human-readable data-quality markdown report.

**Code:**
```python
def generate_quality_report(
    extraction_meta: dict[str, Any],
    cleaning_summary: dict[str, Any],
    rag_summary: dict[str, Any],
) -> Path:
    """Write a human-readable data-quality markdown report."""
    now = datetime.now().isoformat()
    lines: list[str] = [
        "# DOE Data Extraction — Quality Report",
        "",
        f"**Generated:** {now}",
        "",
        "---",
        "",
        "## 1. Overview",
        "",
        f"- **PDFs processed:** {extraction_meta.get('pdfs_processed', 'N/A')}",
        f"- **Total pages:** {extraction_meta.get('total_pages', 'N/A')}",
        f"- **Total raw tables extracted:** {extraction_meta.get('total_tables', 'N/A')}",
        f"- **Tables cleaned & kept:** {cleaning_summary.get('tables_cleaned', 'N/A')}",
        f"- **Tables discarded:** {cleaning_summary.get('tables_discarded', 'N/A')}",
        f"- **RAG chunks generated:** {rag_summary.get('total_chunks', 'N/A')}",
        "",
        "---",
        "",
        "## 2. PDFs Processed",
        "",
    ]

    for pdf_report in extraction_meta.get("per_pdf", []):
        lines.extend([
            f"### {pdf_report['pdf_name']}",
            "",
            f"- **Slug:** `{pdf_report['slug']}`",
            f"- **Pages:** {pdf_report['pages']}",
            f"- **Tables extracted:** {pdf_report['tables_extracted']}",
            f"- **Table files:**",
        ])
        for tf in pdf_report.get("table_files", []):
            lines.append(f"  - `{tf}`")
        lines.append(f"- **Text dir:** `{pdf_report.get('text_dir', 'N/A')}`")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## 3. Cleaning Report",
        "",
    ])

    for row in cleaning_summary.get("files", []):
        lines.append(
            f"| `{row['file']}` | {row['original_rows']} | {row['cleaned_rows']} | "
            f"{row['columns']} | {row['category']} |"
        )
    lines.insert(-len(cleaning_summary.get("files", [])), "| File | Original Rows | Cleaned Rows | Columns | Category |")
    lines.insert(-len(cleaning_summary.get("files", [])), "|------|--------------|--------------|---------|----------|")

    lines.extend([
        "",
        "---",
        "",
        "## 4. RAG Documents",
        "",
    ])
    for cat, info in rag_summary.get("categories", {}).items():
        lines.append(f"- **{cat}:** {info['chunks']} chunks (`{info['file']}`)")
    lines.append("")

    lines.extend([
        "---",
        "",
        "## 5. Assumptions & Notes",
        "",
        "- Numeric values with commas, currency symbols, and percentage signs were stripped and stored in separate `_numeric` and `_unit` columns.",
        "- Dates were normalized to `YYYY-MM` format where possible.",
        "- Rows containing only page numbers, footers, or repeated headers were removed.",
        "- Category detection is heuristic-based on column names and content keywords.",
        "- Tables with >80% empty cells were discarded.",
        "- RAG chunks are generated per-row; each chunk contains a natural-language sentence plus metadata.",
        "",
        "---",
        "",
        "## 6. Extraction Issues",
        "",
    ])

    issues = [r for r in cleaning_summary.get("files", []) if r.get("category") in ("discarded", "error")]
    if issues:
        for row in issues:
            lines.append(f"- `{row['file']}` → {row.get('error', 'discarded (empty/noisy)')}")
    else:
        lines.append("- No major issues detected.")

    lines.append("")

    report_path = REPORTS_DIR / "data_quality_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Quality report: %s", report_path)
    return report_path
```

**Explanation:** It accepts `extraction_meta`, `cleaning_summary`, `rag_summary` and returns `Path`. See the code below for the full implementation. Key calls include `isoformat()`, `now()`, `get()`, `extend()`, `append()`.

### `main`

- **File:** `windsurf_data_extraction/run_extraction.py`
- **Lines:** `143-173`
- **Signature:** `def main() -> None:`
- **Purpose:** Handles main.

**Code:**
```python
def main() -> None:
    logger.info("=" * 60)
    logger.info("STEP 1: PDF EXTRACTION")
    logger.info("=" * 60)
    extraction_meta = pdf_extractor.run_all()

    logger.info("")
    logger.info("=" * 60)
    logger.info("STEP 2: CLEANING & NORMALIZATION")
    logger.info("=" * 60)
    cleaning_summary = cleaner.run_cleaning()

    logger.info("")
    logger.info("=" * 60)
    logger.info("STEP 3: RAG CONVERSION")
    logger.info("=" * 60)
    rag_summary = rag_converter.run_conversion()

    logger.info("")
    logger.info("=" * 60)
    logger.info("STEP 4: QUALITY REPORT")
    logger.info("=" * 60)
    report_path = generate_quality_report(extraction_meta, cleaning_summary, rag_summary)

    logger.info("")
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 60)
    logger.info("Report: %s", report_path)
    logger.info("CSV output: %s", cleaner.OUTPUT_DIR)
    logger.info("RAG output: %s", rag_converter.RAG_DIR)
```

**Explanation:** It accepts zero arguments and returns `None`. See the code below for the full implementation. Key calls include `info()`, `run_all()`, `run_cleaning()`, `run_conversion()`, `generate_quality_report()`.

