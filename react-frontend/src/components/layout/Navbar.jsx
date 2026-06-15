import { useState } from "react";
import { Link, useLocation } from "react-router-dom";

import ThemeToggle from "@/components/shared/ThemeToggle";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";

const navLinks = [
  { to: "/", label: "Home" },
  { to: "/about", label: "About" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/homes", label: "My Homes" },
  { to: "/ecosim", label: "Ecosim" },
  { to: "/energyhub", label: "EnergyHub" },
];

export default function Navbar() {
  const { session, signOut } = useAuth();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="border-b bg-card/80 backdrop-blur supports-[backdrop-filter]:bg-card/60">
      <div className="page-container flex items-center justify-between">
        <Link to="/" className="text-lg font-bold tracking-tight text-primary">
          Lumi
        </Link>
        {/* Mobile menu toggle */}
        <button
          className="md:hidden touch-target rounded-md p-2 text-muted-foreground hover:bg-muted"
          onClick={() => setMenuOpen((s) => !s)}
          aria-label="Toggle menu"
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {menuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
        {/* Desktop nav */}
        <nav className="hidden items-center gap-1 md:flex">
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
      {/* Mobile nav dropdown */}
      {menuOpen && (
        <div className="md:hidden border-t bg-card px-4 pb-4">
          <nav className="flex flex-col gap-1 pt-2">
            {navLinks.map((link) => {
              const isActive = location.pathname === link.to || (link.to !== "/" && location.pathname.startsWith(link.to));
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  onClick={() => setMenuOpen(false)}
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
            <div className="mt-2 flex items-center gap-2">
              {session ? (
                <Button variant="outline" size="sm" className="w-full" onClick={signOut}>
                  Logout
                </Button>
              ) : (
                <Link to="/login" className="w-full" onClick={() => setMenuOpen(false)}>
                  <Button size="sm" className="w-full">Login</Button>
                </Link>
              )}
              <ThemeToggle />
            </div>
          </nav>
        </div>
      )}
    </header>
  );
}
