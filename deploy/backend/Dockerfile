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

# Runtime libs for GIS packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgeos3.12.1 libproj25 libgdal36 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY fastapi-backend/ ./

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
