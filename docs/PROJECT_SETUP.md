# Project Setup

## Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase account

## Repository Layout
- `fastapi-backend/` — FastAPI API with Redis + Supabase
- `react-frontend/` — React + Vite + Tailwind + shadcn/ui
- `expo-mobile/` — React Native + Expo (Android via Expo Go)
- `docs/` — Architecture and setup guides

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

## Web Frontend Setup
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

## Mobile App Setup (Expo)
1. Install dependencies.

```bash
cd expo-mobile
npm install
```

2. Create environment file.

```bash
copy .env.example .env
```

3. Fill in `.env`:
   ```
   EXPO_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   EXPO_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   EXPO_PUBLIC_API_BASE_URL=http://YOUR_LAN_IP:8000/api/v1
   ```

4. Start the dev server.

```bash
npx expo start
```

5. Scan the QR code with **Expo Go** on your Android device.

> **Tip**: For local backend access, replace `YOUR_LAN_IP` with your machine's LAN IP (e.g., `10.214.200.125`). Use `ipconfig` (Windows) or `ip addr` (Linux/macOS) to find it.

## Supabase Setup (Quick Start)
1. Create a new Supabase project.
2. Open **Project Settings -> API**.
3. Copy the following values into `fastapi-backend/.env`:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_JWT_SECRET`
4. Copy these values into `react-frontend/.env`:
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
5. Copy these values into `expo-mobile/.env`:
   - `EXPO_PUBLIC_SUPABASE_URL`
   - `EXPO_PUBLIC_SUPABASE_ANON_KEY`
6. Configure OAuth providers:
   - Go to **Authentication -> Providers**
   - Enable **Google**
   - Add redirect URLs under **Authentication -> URL Configuration**:
     - `http://localhost:5173`
     - `exp://*` (Expo Go)
     - `lumi://*` (custom scheme)
7. Set the API base URL:
   - `react-frontend/.env`: `VITE_API_BASE_URL=http://localhost:8000/api/v1`
   - `expo-mobile/.env`: `EXPO_PUBLIC_API_BASE_URL=http://YOUR_LAN_IP:8000/api/v1`

## Test the Flow
- **Web**: Visit `http://localhost:5173`, login with Google or email/password.
- **Mobile**: Tap "Continue with Google" in the Expo app, confirm deep link returns to the app.
- **Protected data**: Open the Dashboard to see JWT claims and protected API data.

## Troubleshooting
- If login loops, confirm redirect URLs are saved in Supabase Authentication settings.
- If protected routes fail, confirm `SUPABASE_JWT_SECRET` matches the project settings.
- If CORS blocks requests, update `CORS_ORIGINS` in `fastapi-backend/.env`.
- If the mobile app can't reach the backend, confirm the LAN IP and that the backend runs with `--host 0.0.0.0`.
