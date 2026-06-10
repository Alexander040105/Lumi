import { Link, useLocation } from "react-router-dom";

import ThemeToggle from "@/components/shared/ThemeToggle";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";

const navLinks = [
  { to: "/", label: "Home" },
  { to: "/about", label: "About" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/ecosim", label: "Ecosim" },
  { to: "/energyhub", label: "EnergyHub" },
];

export default function Navbar() {
  const { session, signOut } = useAuth();
  const location = useLocation();

  return (
    <header className="border-b bg-card/80 backdrop-blur supports-[backdrop-filter]:bg-card/60">
      <div className="page-container flex items-center justify-between">
        <Link to="/" className="text-lg font-bold tracking-tight text-primary">
          Lumi
        </Link>
        <nav className="flex items-center gap-1">
          {navLinks.map((link) => {
            const isActive = location.pathname === link.to || (link.to !== "/" && location.pathname.startsWith(link.to));
            return (
              <Link
                key={link.to}
                to={link.to}
                className={
                  "rounded-md px-3 py-2 text-sm font-medium transition-colors " +
                  (isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground")
                }
              >
                {link.label}
              </Link>
            );
          })}
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
