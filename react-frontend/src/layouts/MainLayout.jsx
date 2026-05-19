import { Outlet, useLocation } from "react-router-dom";

import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";

export default function MainLayout() {
  const location = useLocation();
  const isDashboard = location.pathname.startsWith("/dashboard");

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="flex">
        {isDashboard && <Sidebar />}
        <main className="flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
