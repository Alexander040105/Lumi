# =============================================================================
# LUMI FastAPI Backend — Production Dockerfile
# =============================================================================
# Build context: repository ROOT (so we can COPY fastapi-backend/)
#
# Multi-stage build keeps image small while installing heavy ML/GIS deps.
# Uses Python 3.11 slim with build-essential for compiling rasterio, GDAL, etc.
# =============================================================================

FROM python:3.11-slim-bookworm AS builder

# Install build deps for rasterio, shapely, faiss, sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgdal-dev \
    gdal-bin \
    libgeos-dev \
    libproj-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment for pip compilation
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /build

# Install dependencies into a virtualenv (clean isolation + smaller final layer)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY fastapi-backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Runtime stage
# ---------------------------------------------------------------------------
FROM python:3.11-slim-bookworm AS runtime

# Runtime libs for GDAL, proj, geos (much smaller than -dev packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgdal32 \
    gdal-bin \
    libgeos-c1v5 \
    libproj25 \
    libtiff6 \
    libjpeg62-turbo \
    libpng16-16 \
    libxml2 \
    libxslt1.1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtualenv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy backend source
COPY fastapi-backend/ .

# Uvicorn runs on port 8080 inside the container
EXPOSE 8080

# Use a single worker to keep RAM low on a 4 GB Droplet.
# --proxy-headers trusts X-Forwarded-* from Nginx.
# --forwarded-allow-ips=* is safe because Nginx is the only upstream.
CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8080", \
     "--workers", "1", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"]
