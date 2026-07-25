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

echo ""
echo "[2/5] Stopping existing containers..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod down

echo ""
echo "[3/5] Starting stack..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod up -d

echo ""
echo "[4/5] Waiting for backend health check..."
for i in $(seq 1 30); do
    if curl -sf http://localhost/api/v1/health/ > /dev/null 2>&1; then
        echo "  Backend is healthy!"
        break
    fi
    echo "  Waiting... ($i/30)"
    sleep 5
    if [ $i -eq 30 ]; then
        echo "ERROR: Backend did not become healthy within 150 seconds."
        docker compose logs --tail=50 backend
        exit 1
    fi
done

echo ""
echo "[5/5] Verifying frontend..."
if curl -sf http://localhost/ > /dev/null 2>&1; then
    echo "  Frontend is serving!"
else
    echo "  WARNING: Frontend not responding. Check nginx logs."
fi

echo ""
echo "============================================"
echo "  Deployment Complete!"
echo "============================================"
echo ""
echo "  Backend:  http://localhost/api/v1/health/"
echo "  Frontend: http://localhost/"
echo "  Detailed: http://localhost/api/v1/health/detailed"
echo ""
echo "  Logs:     docker compose logs -f backend"
echo "  Status:   docker compose ps"
echo ""
