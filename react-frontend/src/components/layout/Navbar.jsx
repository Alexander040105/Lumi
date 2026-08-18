import { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Menu, X } from "lucide-react";

import ThemeToggle from "@/components/shared/ThemeToggle";
import LanguageToggle from "@/components/shared/LanguageToggle";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/hooks/useAuth";
import { useI18n } from "@/i18n";

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
  { to: "/", key: "nav.home" },
  { to: "/about", key: "nav.about" },
  { to: "/ecosim", key: "nav.ecosim" },
  { to: "/energyhub", key: "nav.energyHub" },
];

function LumLogo() {
  return (
    <div className="flex items-center gap-2">
      <img src="/logo.png" alt="LUMI" className="h-14 w-auto object-contain" />
    </div>
  );
}

export default function Navbar() {
  const { t, locale, setLocale } = useI18n();
  const { session, user, profile, signOut, isAdmin } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  const links = navLinks.map((link) => ({ ...link, label: t(link.key) }));

  const displayName =
    profile?.full_name ||
    user?.user_metadata?.full_name ||
    user?.email?.split("@")[0] ||
    t("common.user");
  const userEmail = user?.email || "";

  const NavLink = ({ link, onClick }) => {
    const isActive =
      location.pathname === link.to ||
      (link.to !== "/" && location.pathname.startsWith(link.to));
    return (
      <Link
        to={link.to}
        onClick={onClick}
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
  };

  return (
    <header className="relative border-b bg-card/80 backdrop-blur supports-[backdrop-filter]:bg-card/60">
      <div className="page-container flex items-center justify-between">
        <Link to="/" aria-label={t("nav.home")}>
          <LumLogo />
        </Link>

        <nav className="flex items-center gap-1">
          {/* Desktop navigation */}
          <div className="hidden md:flex items-center gap-1">
            {links.map((link) => (
              <NavLink key={link.to} link={link} />
            ))}
          </div>

          {session ? (
            <div className="flex items-center gap-2 ml-2">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="flex items-center gap-2 rounded-md hover:bg-muted transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring px-2 py-1">
                    <UserAvatar user={user} profile={profile} className="h-8 w-8" />
                    <span
                      className="text-sm font-medium hidden md:inline max-w-[120px] truncate"
                      title={displayName}
                    >
                      {displayName}
                    </span>
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-64 p-2">
                  <div className="flex items-center gap-3 px-2 py-2">
                    <UserAvatar user={user} profile={profile} className="h-10 w-10" />
                    <div className="flex flex-col min-w-0">
                      <span className="text-sm font-semibold truncate" title={displayName}>
                        {displayName}
                      </span>
                      <span className="text-xs text-muted-foreground truncate" title={userEmail}>
                        {userEmail}
                      </span>
                    </div>
                  </div>
                  <DropdownMenuSeparator />
                  {isAdmin && (
                    <DropdownMenuItem
                      onClick={() => navigate("/admin")}
                      className="flex items-center gap-2 text-primary focus:text-primary"
                    >
                      <span className="text-base">🛡️</span>
                      <span>{t("nav.adminPortal")}</span>
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuItem onClick={() => navigate("/dashboard")} className="flex items-center gap-2">
                    <span className="text-base">👤</span>
                    <span>{t("nav.dashboard")}</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate("/saved-simulations")} className="flex items-center gap-2">
                    <span className="text-base">📊</span>
                    <span>{t("nav.savedSims")}</span>
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
                    <span>{t("nav.logout")}</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ) : (
            <TooltipProvider delayDuration={150}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Link to="/login" aria-label={t("login.signIn")}>
                    <Button size="sm">{t("nav.login")}</Button>
                  </Link>
                </TooltipTrigger>
                <TooltipContent side="bottom">
                  <p>{t("login.signIn")}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}

          <div className="hidden md:flex items-center gap-2 ml-2">
            <LanguageToggle />
            <ThemeToggle />
          </div>

          {/* Mobile hamburger */}
          <button
            type="button"
            aria-label={mobileOpen ? t("nav.closeMenu") : t("nav.openMenu")}
            onClick={() => setMobileOpen((v) => !v)}
            className="md:hidden ml-2 rounded-md p-2 text-foreground hover:bg-muted"
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </nav>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden absolute inset-x-0 top-full z-50 border-b bg-card p-4 shadow-lg">
          <div className="flex flex-col gap-1">
            {links.map((link) => (
              <NavLink key={link.to} link={link} onClick={() => setMobileOpen(false)} />
            ))}
          </div>
          <div className="mt-4 flex items-center justify-between border-t pt-4">
            <LanguageToggle />
            <ThemeToggle />
          </div>
        </div>
      )}
    </header>
  );
}
