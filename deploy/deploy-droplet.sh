#!/bin/bash
# =============================================================================
# LUMI Droplet Deploy Script
# =============================================================================
# Run this ON THE DROPLET after cloning the repo and creating .env
# Usage:
#   chmod +x deploy/deploy-droplet.sh
#   ./deploy/deploy-droplet.sh
# =============================================================================

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

echo "========================================"
echo "LUMI Deployment Script"
echo "========================================"

# Check prerequisites
echo "[1/6] Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { echo "Docker is not installed. Install it first."; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo "Docker Compose is not installed. Install it first."; exit 1; }

if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found at repo root."
    echo "Create it by copying deploy/env-template.txt and filling in real values."
    exit 1
fi

# Check required vars
echo "[2/6] Validating environment variables..."
for var in SUPABASE_URL SUPABASE_ANON_KEY GEMINI_API_KEY GROQ_API_KEY; do
    if ! grep -q "^${var}=" .env || grep "^${var}=" .env | grep -q "xxxxxx"; then
        echo "WARNING: $var is missing or contains a placeholder in .env"
    fi
done

# Check frontend build exists
echo "[3/6] Checking frontend build..."
if [ ! -d "react-frontend/dist" ] || [ ! -f "react-frontend/dist/index.html" ]; then
    echo "ERROR: Frontend build not found."
    echo "Build it locally first and push the dist/ folder, or install Node.js and run:"
    echo "  cd react-frontend && npm install && npm run build"
    exit 1
fi

# Stop existing containers
echo "[4/6] Stopping existing containers (if any)..."
docker compose down --remove-orphans 2>/dev/null || true

# Build and start
echo "[5/6] Building and starting services..."
docker compose up -d --build

# Wait for backend health
echo "[6/6] Waiting for backend health check..."
for i in {1..30}; do
    if curl -sf http://localhost:8080/ >/dev/null 2>&1; then
        echo "Backend is healthy!"
        break
    fi
    echo "  Waiting... ($i/30)"
    sleep 2
done

echo ""
echo "========================================"
echo "Deployment complete!"
echo "========================================"
echo "Services:"
echo "  Website : http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_DROPLET_IP')"
echo "  API     : http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_DROPLET_IP')/api/v1"
echo "  Health  : http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_DROPLET_IP')/"
echo ""
echo "View logs:  docker compose logs -f backend"
echo "Stop all:   docker compose down"
echo "========================================"
