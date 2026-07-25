# LUMI Backend — multi-stage Dockerfile
# Python 3.11 slim image with ML/GIS dependencies

FROM python:3.11-slim AS builder

WORKDIR /build

# System deps for compiling native extensions (rasterio, pyproj, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ libffi-dev \
    libgeos-dev libproj-dev libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

COPY fastapi-backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --user -r requirements.txt

# ---------- runtime stage ----------
FROM python:3.11-slim

WORKDIR /app

# Runtime libs for GIS packages + libgomp1 (FAISS) + curl (healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgeos3.12.1 libproj25 libgdal36 libgomp1 curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r lumi && useradd -r -g lumi -d /app lumi \
    && mkdir -p /app/.cache /app/app/services/local_data \
    && chown -R lumi:lumi /app

COPY --from=builder /root/.local /home/lumi/.local
ENV PATH=/home/lumi/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HOME=/app

COPY --chown=lumi:lumi fastapi-backend/ ./

USER lumi

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/api/v1/health/ || exit 1

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
