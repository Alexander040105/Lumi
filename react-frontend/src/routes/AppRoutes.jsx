import { BrowserRouter, Route, Routes } from "react-router-dom";

import MainLayout from "../layouts/MainLayout";
import Home from "../pages/Home";
import About from "../pages/About";
import Login from "../pages/Login";
import ResetPassword from "../pages/ResetPassword";
import Dashboard from "../pages/Dashboard";
import Ecosim from "../pages/Ecosim";
import EnergyHub from "../pages/EnergyHub";
import MyHomes from "../pages/MyHomes";
import HomeDetail from "../pages/HomeDetail";
import NotFound from "../pages/NotFound";
import ProtectedRoute from "../components/shared/ProtectedRoute";

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
          <Route
            path="dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="homes"
            element={
              <ProtectedRoute>
                <MyHomes />
              </ProtectedRoute>
            }
          />
          <Route
            path="homes/:homeId"
            element={
              <ProtectedRoute>
                <HomeDetail />
              </ProtectedRoute>
            }
          />
          <Route path="about" element={<About />} />
          <Route path="ecosim" element={<Ecosim />} />
          <Route path="energyhub" element={<EnergyHub />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
