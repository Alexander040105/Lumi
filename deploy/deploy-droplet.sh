#!/usr/bin/env bash
# =============================================================================
# LUMI — One-Click Droplet Deployment Script
# =============================================================================
# Run this ONCE on a fresh DigitalOcean Droplet (Ubuntu 22.04/24.04).
# It installs Docker, clones the repo, builds images, and starts the stack.
# =============================================================================
set -euo pipefail

REPO_URL="https://github.com/Alexander040105/Lumi.git"
PROJECT_DIR="$HOME/Lumi"

echo "=== LUMI Droplet Deployment ==="

# ---------------------------------------------------------------------------
# 1. Update system & install prerequisites
# ---------------------------------------------------------------------------
echo "[1/7] Updating packages..."
sudo apt-get update -y
sudo apt-get install -y curl git ca-certificates gnupg lsb-release

# ---------------------------------------------------------------------------
# 2. Install Docker & Docker Compose
# ---------------------------------------------------------------------------
echo "[2/7] Installing Docker..."
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker "$USER"
    sudo systemctl enable docker
    sudo systemctl start docker
fi

if ! docker compose version &>/dev/null; then
    echo "Docker Compose plugin not found — ensure Docker CE >= 20.10"
    exit 1
fi

# ---------------------------------------------------------------------------
# 3. Clone repository
# ---------------------------------------------------------------------------
echo "[3/7] Cloning repository..."
if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
    git pull origin main || git pull origin master || true
else
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# ---------------------------------------------------------------------------
# 4. Build frontend
# ---------------------------------------------------------------------------
echo "[4/7] Building React frontend..."
cd react-frontend
npm install
npm run build
cd ..

# ---------------------------------------------------------------------------
# 5. Verify .env exists
# ---------------------------------------------------------------------------
echo "[5/7] Checking .env file..."
if [ ! -f .env ]; then
    echo "ERROR: .env file not found at $PROJECT_DIR/.env"
    echo "Please copy deploy/env-template.txt to .env and fill in real values."
    exit 1
fi

# ---------------------------------------------------------------------------
# 6. Build & start containers
# ---------------------------------------------------------------------------
echo "[6/7] Building Docker images..."
docker compose build --no-cache

echo "[7/7] Starting stack..."
docker compose up -d

# ---------------------------------------------------------------------------
# 7. Summary
# ---------------------------------------------------------------------------
IP=$(hostname -I | awk '{print $1}')
echo ""
echo "=========================================="
echo "  LUMI deployed successfully!"
echo "=========================================="
echo "  App URL:       http://$IP"
echo "  Health check:  http://$IP/health/"
echo "  API docs:      http://$IP/api/v1/docs"
echo ""
echo "  Next steps:"
echo "    1. Buy a domain and point A record to $IP"
echo "    2. Update CORS_ORIGINS in .env"
echo "    3. Set up SSL with Certbot (see DEPLOYMENT_GUIDE.md)"
echo "=========================================="
