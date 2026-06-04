# Lumi

Renewable energy recommendation platform with AI-powered simulation, forecasting, and feasibility analysis. Built with React (web), React Native (mobile), FastAPI (backend), and Supabase (auth/database).

## Repository Structure

```
Lumi/
├── fastapi-backend/      # FastAPI + Redis + Supabase
├── react-frontend/       # React + Vite + Tailwind + shadcn/ui
├── expo-mobile/          # React Native + Expo
├── docs/                 # Architecture and setup guides
├── data/                 # Datasets, raster data, and pipeline scripts
│   ├── municipality_climate_averages.csv
│   ├── phl_msk_alt/      # Raster elevation data
│   ├── regionalData/     # Regional datasets
│   ├── scraped_data/     # Scraped source data
│   ├── scripts/          # Python data processing pipelines
│   └── supabase/         # SQL schema scripts
```

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Supabase account
- Expo Go app (for mobile)

### 1. Backend

```bash
cd fastapi-backend
python -m venv .venv
.venv\Scripts\activate           # Windows
source .venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
copy .env.example .env          # Fill in your Supabase keys
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Web Frontend

```bash
cd react-frontend
npm install
copy .env.example .env          # Fill in your Supabase URL and anon key
npm run dev
```

Open `http://localhost:5173`.

### 3. Mobile App (Expo)

```bash
cd expo-mobile
npm install
copy .env.example .env          # Fill in EXPO_PUBLIC_* vars
npx expo start
```

Scan the QR code with **Expo Go** on your Android device.

> **LAN access**: If testing the mobile app against your local backend, update `EXPO_PUBLIC_API_BASE_URL` to your machine's LAN IP (e.g., `http://10.214.200.125:8000/api/v1`).

## Supabase Configuration

1. Create a project at [supabase.com](https://supabase.com).
2. Go to **Project Settings -> API** and copy:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_JWT_SECRET`
3. Add them to both `fastapi-backend/.env` and `react-frontend/.env`.
4. Go to **Authentication -> URL Configuration** and add redirect URLs:
   - `http://localhost:5173`
   - `http://10.214.200.125:5173` (if testing web on LAN)
   - `exp://*` (for Expo Go)
   - `lumi://*` (custom scheme)
5. Enable **Google OAuth** under Authentication -> Providers.

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/PROJECT_SETUP.md`](docs/PROJECT_SETUP.md) | Full setup guide with env vars and troubleshooting |
| [`docs/TECH_STACK_MVP_GUIDE.md`](docs/TECH_STACK_MVP_GUIDE.md) | Code patterns, CRUD example, 4-week plan |
| [`docs/backend/`](docs/backend/) | API structure, auth/Redis, FastAPI architecture |
| [`docs/frontend/`](docs/frontend/) | Component guide, Tailwind, shadcn/ui, structure |
| [`docs/supabase/`](docs/supabase/) | Supabase project setup |
| [`expo-mobile/README.md`](expo-mobile/README.md) | Mobile app details and feature parity |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Web Frontend | React, Vite, Tailwind CSS, shadcn/ui |
| Mobile | React Native, Expo, TypeScript |
| Backend | FastAPI, Pydantic, python-jose |
| Auth / DB | Supabase (Postgres + Auth + RLS) |
| Cache | Redis (Upstash or local) |
| AI / ML | Google Gemini, sentence-transformers, FAISS |

## Common Commands

```bash
# Backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Web dev server
npm run dev

# Mobile dev server
npx expo start --clear

# TypeScript check (mobile)
cd expo-mobile && npx tsc --noEmit
```

## License

Thesis project.