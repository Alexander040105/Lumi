# =============================================================================
# LUMI FastAPI Backend - Production Dockerfile
# =============================================================================
FROM python:3.11-slim-bookworm

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies required for compiled Python packages
# (sentence-transformers, faiss-cpu, numpy, pandas, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory to repo root so backend can reach data dirs
WORKDIR /app

# Copy and install backend Python dependencies first (layer caching)
COPY fastapi-backend/requirements.txt /app/fastapi-backend/requirements.txt
RUN pip install --no-cache-dir -r /app/fastapi-backend/requirements.txt

# Copy the entire repo into the container.
# The backend expects certain data folders at repo root:
#   DOE_Data_Extracted/, philippine_geojson/, GeothermalDatasets/
# And .env at repo root.
COPY . /app/

# Working directory for running the app
WORKDIR /app/fastapi-backend

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/')" || exit 1

# Run with uvicorn (single process) — sufficient for thesis/demo workloads.
# For production scale, switch to: gunicorn -k uvicorn.workers.UvicornWorker
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
