import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "@/hooks/useAuth";
import Loading from "@/components/shared/Loading";

export default function ProtectedRoute({ children }) {
  const { session, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <Loading />;
  }

  if (!session) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}
