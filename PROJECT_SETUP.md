# Project Setup

## Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase account

## Repository Layout
- fastapi-backend/ (FastAPI API)
- react-frontend/ (React + Supabase OAuth)

## Backend Setup
1. Create a virtual environment and install dependencies.

```bash
cd fastapi-backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Create environment file.

```bash
copy .env.example .env
```

3. Run the API.

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Setup
1. Install dependencies.

```bash
cd react-frontend
npm install
```

2. Create environment file.

```bash
copy .env.example .env
```

3. Run the dev server.

```bash
npm run dev
```

## Supabase Setup (Quick Start)
1. Create a new Supabase project.
2. Open Project Settings -> API.
3. Copy the following values into fastapi-backend/.env:
   - SUPABASE_URL
   - SUPABASE_ANON_KEY
   - SUPABASE_JWT_SECRET
4. Copy these values into react-frontend/.env:
   - VITE_SUPABASE_URL
   - VITE_SUPABASE_ANON_KEY
5. Configure OAuth providers:
   - Authentication -> Providers
   - Enable Google, GitHub, or others
   - Add redirect URLs:
     - http://localhost:5173
6. Set the API base URL for React in react-frontend/.env:
   - VITE_API_BASE_URL=http://localhost:8000/api/v1

## Test the Flow
- Visit http://localhost:5173
- Login with OAuth
- Open the Dashboard to see protected API data

## Troubleshooting
- If login loops, confirm the redirect URL is saved in Supabase.
- If protected routes fail, confirm SUPABASE_JWT_SECRET matches the project settings.
- If CORS blocks requests, update CORS_ORIGINS in fastapi-backend/.env.
