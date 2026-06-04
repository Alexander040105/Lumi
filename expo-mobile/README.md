# Lumi Mobile (Expo)

React Native Android app for the Lumi renewable energy platform. Built with TypeScript and Expo for rapid prototyping without ADB.

## Quick Start

1. **Install dependencies** (already done if you cloned the repo):
   ```bash
   cd expo-mobile
   npm install
   ```

2. **Configure environment variables** in `.env`:
   ```
   EXPO_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   EXPO_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   EXPO_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
   ```

3. **Start the dev server**:
   ```bash
   npx expo start
   ```

4. **Open in Expo Go**: Scan the QR code with the Expo Go app on your Android device.

## Project Structure

```
src/
  navigation/       - React Navigation setup (stacks + tabs)
  screens/          - Feature screens (Home, Login, Dashboard, Ecosim, etc.)
  components/
    ui/             - Reusable UI primitives (Button, Card, Input, Badge, Skeleton, Modal)
    layout/         - Navbar and other layout components
    shared/         - ProtectedRoute, LoadingSkeleton
  context/          - AuthContext, ThemeContext
  hooks/            - useAuth, useTheme
  services/         - Supabase client, API client (FastAPI)
  theme/            - Light/dark color tokens
  types/            - Shared TypeScript types
  utils/            - Environment variable helpers
```

## Feature Parity

| Web Feature            | Mobile Screen           |
|------------------------|-------------------------|
| Home page              | HomeScreen              |
| Login (email + Google) | LoginScreen             |
| Reset password         | ResetPasswordScreen     |
| Dashboard              | DashboardScreen         |
| Ecosim GET simulation  | EcosimInputScreen       |
| Ecosim results         | EcosimResultsScreen     |
| AI/RAG Ecosim POST     | AdvancedEcosimScreen    |
| Protected routes       | RootNavigator logic     |
| Dark mode              | ThemeContext + Appearance |

## Backend Capabilities Exposed

- **GET `/ecosim/`** — Basic renewable energy simulation (web parity)
- **GET `/ecosim/municipalities`** — List municipalities (web parity)
- **POST `/ecosim/`** — AI/RAG-powered advanced simulation (beyond web UI)
- **GET `/protected/me`** — JWT claims validation (web parity)
- **POST `/protected/session`** — Redis session storage (beyond web UI)
- **Supabase Auth** — Email/password, Google OAuth, MFA/TOTP, password reset

## Notes

- All prototyping is done via **Expo Go** — no ADB or native build tools required.
- Google OAuth uses `expo-auth-session` + `expo-web-browser` with the `lumi://` custom URL scheme.
- Session persistence uses `@react-native-async-storage/async-storage`.
- The `@/` path alias maps to `./src/` via `tsconfig.json`.
