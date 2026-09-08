# LUMI React Frontend

React 18 + Vite + Tailwind CSS single-page app for EcoSim, EnergyHub, and the
chat/admin surfaces of LUMI.

## Structure

```
react-frontend/
├── public/                 # Static assets + GeoJSON overlays (geo boundaries,
│                           # geothermal volcanoes/faults) served at site root
├── src/
│   ├── components/         # Reusable components (ui/ = shadcn primitives,
│   │                       # energyhub/, ecosim/ feature components)
│   ├── context/            # React contexts (AuthContext, etc.)
│   ├── hooks/              # Custom hooks
│   ├── layouts/            # Page layouts
│   ├── pages/              # Route-level pages (Dashboard, EcoSim, EnergyHub,
│   │                       # admin/)
│   ├── routes/             # React Router config
│   ├── services/           # API client + Supabase client
│   ├── styles/             # Global/Tailwind CSS
│   ├── data/               # Static frontend data
│   ├── App.jsx             # Root component
│   └── main.jsx            # Entry point
├── .env.example            # Frontend environment template (VITE_* vars)
├── package.json
└── vite.config.js
```

## Setup

```bash
cd react-frontend
npm install
cp .env.example .env          # VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, etc.
npm run dev                   # http://localhost:5173
```

## Tests & Build

```bash
npm test          # Vitest suite (src/__tests__)
npm run build     # production build -> dist/
```

The dev server expects the FastAPI backend on `http://localhost:8000`
(see `../fastapi-backend/README.md`). Root `npm run dev` starts both via
`concurrently`.
