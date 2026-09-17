import { lazy, Suspense } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import MainLayout from "../layouts/MainLayout";
import Home from "../pages/Home";
import About from "../pages/About";
import Login from "../pages/Login";
import ResetPassword from "../pages/ResetPassword";
import NotFound from "../pages/NotFound";
import Terms from "../pages/Terms";
import Privacy from "../pages/Privacy";
import ProtectedRoute from "../components/shared/ProtectedRoute";
import AdminRoute from "../components/shared/AdminRoute";

// Route-level code splitting: authenticated and admin pages (which pull in
// plotly/pdfmake/leaflet/recharts) load on demand instead of in the entry
// chunk. Public entry pages stay eager for fast first paint.
const Dashboard = lazy(() => import("../pages/Dashboard"));
const SavedSimulations = lazy(() => import("../pages/SavedSimulations"));
const MFASetup = lazy(() => import("../pages/MFASetup"));
const SecuritySettings = lazy(() => import("../pages/SecuritySettings"));
const Ecosim = lazy(() => import("../pages/Ecosim"));
const EnergyHub = lazy(() => import("../pages/EnergyHub"));
const AdminDashboard = lazy(() => import("../pages/admin/AdminDashboard"));
const AdminUsers = lazy(() => import("../pages/admin/AdminUsers"));
const AdminAnalytics = lazy(() => import("../pages/admin/AdminAnalytics"));
const AdminConfig = lazy(() => import("../pages/admin/AdminConfig"));
const AdminUsage = lazy(() => import("../pages/admin/AdminUsage"));
const AdminLogs = lazy(() => import("../pages/admin/AdminLogs"));

function RouteFallback() {
  return (
    <div
      className="flex min-h-[40vh] items-center justify-center"
      role="status"
      aria-label="Loading page"
    >
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-muted-foreground border-t-transparent" />
    </div>
  );
}

const withSuspense = (element) => (
  <Suspense fallback={<RouteFallback />}>{element}</Suspense>
);

export default function AppRoutes() {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <Routes future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Route element={<MainLayout />}>
          <Route index element={<Home />} />
          <Route path="login" element={<Login />} />
          <Route path="reset-password" element={<ResetPassword />} />
          <Route path="about" element={<About />} />
          <Route path="terms" element={<Terms />} />
          <Route path="privacy" element={<Privacy />} />
          <Route
            path="dashboard"
            element={
              <ProtectedRoute>
                {withSuspense(<Dashboard />)}
              </ProtectedRoute>
            }
          />
          <Route
            path="ecosim"
            element={
              <ProtectedRoute>
                {withSuspense(<Ecosim />)}
              </ProtectedRoute>
            }
          />
          <Route
            path="energyhub"
            element={
              <ProtectedRoute>
                {withSuspense(<EnergyHub />)}
              </ProtectedRoute>
            }
          />
          <Route
            path="saved-simulations"
            element={
              <ProtectedRoute>
                {withSuspense(<SavedSimulations />)}
              </ProtectedRoute>
            }
          />
          <Route
            path="mfa"
            element={
              <ProtectedRoute>
                {withSuspense(<MFASetup />)}
              </ProtectedRoute>
            }
          />
          <Route
            path="settings/security"
            element={
              <ProtectedRoute>
                {withSuspense(<SecuritySettings />)}
              </ProtectedRoute>
            }
          />
          <Route
            path="admin"
            element={
              <AdminRoute>
                {withSuspense(<AdminDashboard />)}
              </AdminRoute>
            }
          />
          <Route
            path="admin/users"
            element={
              <AdminRoute>
                {withSuspense(<AdminUsers />)}
              </AdminRoute>
            }
          />
          <Route
            path="admin/analytics"
            element={
              <AdminRoute>
                {withSuspense(<AdminAnalytics />)}
              </AdminRoute>
            }
          />
          <Route
            path="admin/config"
            element={
              <AdminRoute>
                {withSuspense(<AdminConfig />)}
              </AdminRoute>
            }
          />
          <Route
            path="admin/usage"
            element={
              <AdminRoute>
                {withSuspense(<AdminUsage />)}
              </AdminRoute>
            }
          />
          <Route
            path="admin/logs"
            element={
              <AdminRoute>
                {withSuspense(<AdminLogs />)}
              </AdminRoute>
            }
          />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
