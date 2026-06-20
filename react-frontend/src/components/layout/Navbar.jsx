import { Link, useLocation } from "react-router-dom";

import ThemeToggle from "@/components/shared/ThemeToggle";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";

function UserAvatar({ user, className = "" }) {
  const initials = (user?.user_metadata?.full_name || user?.email || "U")
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  const url = user?.user_metadata?.avatar_url || user?.user_metadata?.picture;
  return (
    <div className={`relative inline-flex items-center justify-center rounded-full overflow-hidden border bg-primary/10 ${className}`}>
      {url ? (
        <img
          src={url}
          alt=""
          className="h-full w-full object-cover"
          onError={(e) => { e.target.style.display = "none"; }}
        />
      ) : (
        <span className="text-xs font-bold text-primary">{initials}</span>
      )}
    </div>
  );
}

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
  const { session, user, signOut, isAdmin } = useAuth();
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
            <div className="flex items-center gap-2 ml-2">
              <Link to="/profile" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                <UserAvatar user={user} className="h-8 w-8" />
                <span className="text-sm font-medium hidden sm:inline">
                  {user?.user_metadata?.full_name || user?.email?.split("@")[0] || "User"}
                </span>
              </Link>
              <Button variant="outline" size="sm" onClick={signOut}>
                Logout
              </Button>
            </div>
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
