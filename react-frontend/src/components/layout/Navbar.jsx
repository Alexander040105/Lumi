import { Link } from "react-router-dom";

import ThemeToggle from "@/components/shared/ThemeToggle";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";

export default function Navbar() {
  const { session, signOut } = useAuth();

  return (
    <header className="border-b bg-background">
      <div className="page-container flex items-center justify-between">
        <Link to="/" className="text-lg font-semibold">
          Lumi UI
        </Link>
        <nav className="flex items-center gap-3">
          <Link to="/" className="text-sm text-muted-foreground">
            Home
          </Link>
          <Link to="/dashboard" className="text-sm text-muted-foreground">
            Dashboard
          </Link>
          <Link to="/ecosim" className="text-sm text-muted-foreground">
            Ecosim
          </Link>
          {session ? (
            <Button variant="outline" size="sm" onClick={signOut}>
              Logout
            </Button>
          ) : (
            <Link to="/login">
              <Button size="sm">Login</Button>
            </Link>
          )}
          <ThemeToggle />
        </nav>
      </div>
    </header>
  );
}
