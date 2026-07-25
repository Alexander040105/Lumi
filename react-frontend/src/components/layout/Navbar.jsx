import { Link, useLocation, useNavigate } from "react-router-dom";

import ThemeToggle from "@/components/shared/ThemeToggle";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/hooks/useAuth";

function UserAvatar({ user, profile, className = "" }) {
  const displayName =
    profile?.full_name ||
    user?.user_metadata?.full_name ||
    user?.email ||
    "U";
  const initials = displayName
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  // Priority: custom uploaded avatar > OAuth avatar_url > OAuth picture
  const url =
    profile?.avatar_url ||
    user?.user_metadata?.avatar_url ||
    user?.user_metadata?.picture;
  return (
    <div
      className={`relative inline-flex items-center justify-center rounded-full overflow-hidden border bg-primary/10 ${className}`}
    >
      {url ? (
        <img
          src={url}
          alt=""
          className="h-full w-full object-cover"
          onError={(e) => {
            e.currentTarget.style.display = "none";
          }}
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
  { to: "/ecosim", label: "Ecosim" },
  { to: "/energyhub", label: "EnergyHub" },
  { to: "/map", label: "Map" },
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
  const { session, user, profile, signOut, isAdmin } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const links = [...navLinks];

  const displayName =
    profile?.full_name ||
    user?.user_metadata?.full_name ||
    user?.email?.split("@")[0] ||
    "User";
  const userEmail = user?.email || "";

  return (
    <header className="border-b bg-card/80 backdrop-blur supports-[backdrop-filter]:bg-card/60">
      <div className="page-container flex items-center justify-between">
        <Link to="/" aria-label="LUMI Home">
          <LumLogo />
        </Link>
        <nav className="flex items-center gap-1">
          {links.map((link) => {
            const isActive =
              location.pathname === link.to ||
              (link.to !== "/" && location.pathname.startsWith(link.to));
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
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="flex items-center gap-2 rounded-md hover:bg-muted transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring px-2 py-1">
                    <UserAvatar
                      user={user}
                      profile={profile}
                      className="h-8 w-8"
                    />
                    <span
                      className="text-sm font-medium hidden md:inline max-w-[120px] truncate"
                      title={displayName}
                    >
                      {displayName}
                    </span>
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  align="end"
                  className="w-64 p-2"
                >
                  {/* User Info Header */}
                  <div className="flex items-center gap-3 px-2 py-2">
                    <UserAvatar
                      user={user}
                      profile={profile}
                      className="h-10 w-10"
                    />
                    <div className="flex flex-col min-w-0">
                      <span className="text-sm font-semibold truncate" title={displayName}>
                        {displayName}
                      </span>
                      <span
                        className="text-xs text-muted-foreground truncate"
                        title={userEmail}
                      >
                        {userEmail}
                      </span>
                    </div>
                  </div>
                  <DropdownMenuSeparator />
                  {/* Menu Items */}
                  {isAdmin && (
                    <DropdownMenuItem
                      onClick={() => navigate("/admin")}
                      className="flex items-center gap-2 text-primary focus:text-primary"
                    >
                      <span className="text-base">🛡️</span>
                      <span>Admin Portal</span>
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuItem
                    onClick={() => navigate("/dashboard")}
                    className="flex items-center gap-2"
                  >
                    <span className="text-base">👤</span>
                    <span>Dashboard</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => navigate("/saved-simulations")}
                    className="flex items-center gap-2"
                  >
                    <span className="text-base">📊</span>
                    <span>Saved Simulations</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={() => {
                      signOut();
                      navigate("/");
                    }}
                    className="flex items-center gap-2 text-destructive focus:text-destructive"
                  >
                    <span className="text-base">🚪</span>
                    <span>Logout</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
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
