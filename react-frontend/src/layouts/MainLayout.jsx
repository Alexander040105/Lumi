import { Link, Outlet } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";

export default function MainLayout() {
  const { session, signOut } = useAuth();

  return (
    <div>
      <header>
        <Link to="/">Lumi Starter</Link>
        <nav>
          <Link to="/">Home</Link>
          <Link to="/dashboard">Dashboard</Link>
          {session ? (
            <button type="button" onClick={signOut}>
              Logout
            </button>
          ) : (
            <Link to="/login">Login</Link>
          )}
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
