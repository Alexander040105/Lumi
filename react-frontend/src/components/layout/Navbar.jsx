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
  { to: "/chat", label: "Chat" },
];

function LumLogo() {
  return (
    <div className="flex items-center gap-2">
      <img src="/logo.png" alt="LUMI" className="h-14 w-auto object-contain" />
    </div>
  );
}

export default function Navbar() {
  const { session, signOut, isAdmin } = useAuth();
  const location = useLocation();

  const links = [...navLinks];
  if (isAdmin) {
    links.push({ to: "/admin", label: "Admin" });
  }

  return (
    <header className="border-b bg-card/80 backdrop-blur supports-[backdrop-filter]:bg-card/60">
      <div className="page-container flex items-center justify-between">
        <Link to="/" aria-label="LUMI Home">
          <LumLogo />
        </Link>
        <nav className="flex items-center gap-1">
          {links.map((link) => {
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
