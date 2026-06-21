import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import MainLayout from "../layouts/MainLayout";
import Home from "../pages/Home";
import About from "../pages/About";
import Login from "../pages/Login";
import ResetPassword from "../pages/ResetPassword";
import Dashboard from "../pages/Dashboard";
import Ecosim from "../pages/Ecosim";
import EnergyHub from "../pages/EnergyHub";
import ChatPage from "../pages/ChatPage";
import AdminDashboard from "../pages/admin/AdminDashboard";
import AdminUsers from "../pages/admin/AdminUsers";
import AdminAnalytics from "../pages/admin/AdminAnalytics";
import AdminConfig from "../pages/admin/AdminConfig";
import AdminModeration from "../pages/admin/AdminModeration";
import NotFound from "../pages/NotFound";
import ProtectedRoute from "../components/shared/ProtectedRoute";
import AdminRoute from "../components/shared/AdminRoute";

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
          <Route
            path="dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="ecosim"
            element={
              <ProtectedRoute>
                <Ecosim />
              </ProtectedRoute>
            }
          />
          <Route
            path="energyhub"
            element={
              <ProtectedRoute>
                <EnergyHub />
              </ProtectedRoute>
            }
          />
          <Route
            path="chat"
            element={
              <ProtectedRoute>
                <ChatPage />
              </ProtectedRoute>
            }
          />
          <Route path="profile" element={<Navigate to="/dashboard" replace />} />
          <Route
            path="admin"
            element={
              <AdminRoute>
                <AdminDashboard />
              </AdminRoute>
            }
          />
          <Route
            path="admin/users"
            element={
              <AdminRoute>
                <AdminUsers />
              </AdminRoute>
            }
          />
          <Route
            path="admin/analytics"
            element={
              <AdminRoute>
                <AdminAnalytics />
              </AdminRoute>
            }
          />
          <Route
            path="admin/config"
            element={
              <AdminRoute>
                <AdminConfig />
              </AdminRoute>
            }
          />
          <Route
            path="admin/moderate"
            element={
              <AdminRoute>
                <AdminModeration />
              </AdminRoute>
            }
          />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
