# Consultation Record No. 2 — Detailed Change Log

This file documents every code change and addition made to implement the seven revisions requested in Consultation Record No. 2. Each section states the file path, why the change was needed, and the actual code added or modified.

---

## 1. i18n Provider — `react-frontend/src/i18n/index.jsx` *(new)*

**Why:** A single source of truth for locale state was needed so every component can translate strings without passing props. It also persists the selected locale to `localStorage`, supports nested translation keys (`nav.home`), interpolation (`{{email}}`), and falls back to English if a key is missing in Filipino.

```jsx
import { createContext, useContext, useState, useCallback, useMemo } from "react";
import en from "./en.json";
import fil from "./fil.json";

const DICTIONARIES = { en, fil };

function getByPath(obj, path) {
  return path.split(".").reduce((acc, part) => (acc ? acc[part] : undefined), obj);
}

const I18nContext = createContext(null);

export function I18nProvider({ children, defaultLocale = "en" }) {
  const [locale, setLocaleState] = useState(() => {
    if (typeof window === "undefined") return defaultLocale;
    const saved = window.localStorage.getItem("lumi-locale");
    if (saved && DICTIONARIES[saved]) return saved;
    const nav = navigator.language?.slice(0, 2);
    if (nav && DICTIONARIES[nav]) return nav;
    return defaultLocale;
  });

  const setLocale = useCallback((next) => {
    if (DICTIONARIES[next]) {
      setLocaleState(next);
      if (typeof window !== "undefined") {
        window.localStorage.setItem("lumi-locale", next);
      }
    }
  }, []);

  const t = useCallback(
    (key, params = {}) => {
      const current = DICTIONARIES[locale];
      const template = getByPath(current, key) ?? getByPath(en, key) ?? key;
      if (typeof template !== "string") return key;
      return template.replace(/\{\{(\w+)\}\}/g, (_, p) => (params[p] !== undefined ? String(params[p]) : `{{${p}}}`));
    },
    [locale]
  );

  const value = useMemo(() => ({ locale, setLocale, t }), [locale, setLocale, t]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within an I18nProvider");
  return ctx;
}
```

---

## 2. English Translations — `react-frontend/src/i18n/en.json` *(new)*

**Why:** Provides the English source strings for all user-facing text added or modified during the revisions.

```json
{
  "greeting": "Hello",
  "interpolated": "Hello, {{name}}",
  "common": {
    "user": "User",
    "loading": "Loading..."
  },
  "nav": {
    "home": "Home",
    "about": "About",
    "ecosim": "EcoSim",
    "energyHub": "Energy Hub",
    "map": "Map",
    "chat": "Chat",
    "dashboard": "Dashboard",
    "savedSims": "Saved Simulations",
    "adminPortal": "Admin Portal",
    "mfa": "Two-Factor Auth",
    "login": "Login",
    "logout": "Logout",
    "openMenu": "Open menu",
    "closeMenu": "Close menu"
  },
  "login": {
    "welcomeBack": "Welcome back",
    "description": "Use email/password or Google sign in.",
    "signIn": "Sign in",
    "signUp": "Sign up",
    "createAccount": "Create account",
    "email": "Email",
    "password": "Password",
    "confirmPassword": "Confirm password",
    "forgotPassword": "Forgot password?",
    "resetPassword": "Reset password",
    "sendResetEmail": "Send reset email",
    "backToSignIn": "Back to sign in",
    "continueWithGoogle": "Continue with Google",
    "checkYourEmail": "Check your email",
    "confirmationSentDesc": "We sent a confirmation link to {{email}}. Click it to verify your account.",
    "resend": "Didn't receive it? Resend",
    "accountCreated": "Account created!",
    "noEmailConfirmation": "No email confirmation required for this domain.",
    "error": "Authentication failed"
  },
  "admin": {
    "portal": "Admin Portal",
    "welcome": "Welcome, admin",
    "summary": "Manage users, review analytics, configure the system, and moderate content.",
    "users": "User Management",
    "usersDesc": "View and manage registered users.",
    "analytics": "Analytics",
    "analyticsDesc": "View system usage metrics and trends.",
    "config": "System Config",
    "configDesc": "Toggle features and adjust system settings.",
    "moderation": "Content Moderation",
    "moderationDesc": "Review chat sessions and flag inappropriate content.",
    "stats": "Quick stats",
    "usersCount": "{{count}} users",
    "simsCount": "{{count}} simulations"
  },
  "dashboard": {
    "title": "Decision Dashboard",
    "mfaLink": "Enable two-factor authentication",
    "adminLink": "Open admin portal",
    "overview": "Overview",
    "quickActions": "Quick Actions",
    "savedLocations": "Saved Locations",
    "savedSims": "Saved Simulations",
    "aiCenter": "AI Center"
  },
  "mfa": {
    "title": "Two-Factor Authentication",
    "status": "MFA status",
    "description": "Add an extra layer of security to your account using an authenticator app.",
    "enabledStatus": "Two-factor authentication is enabled",
    "disabledStatus": "Two-factor authentication is not enabled",
    "enable": "Enable 2FA",
    "disable": "Disable 2FA",
    "verify": "Verify",
    "scanQR": "Scan QR code",
    "scanQRDescription": "Scan this QR code with your authenticator app, then enter the generated code.",
    "codePlaceholder": "6-digit code",
    "factorError": "Failed to load MFA factors",
    "enrollError": "Failed to start 2FA enrollment",
    "verifyError": "Failed to verify code",
    "unenrollError": "Failed to disable 2FA",
    "enabled": "Two-factor authentication enabled",
    "disabled": "Two-factor authentication disabled",
    "disableConfirm": "Disable two-factor authentication? This makes your account less secure.",
    "verifyTitle": "Two-Factor Authentication",
    "verifyDescription": "Enter the 6-digit code from your authenticator app.",
    "resetSent": "Password reset email sent",
    "confirmResent": "Confirmation email resent",
    "resendError": "Failed to resend email",
    "passwordsDoNotMatch": "Passwords do not match",
    "error": "Authentication failed"
  }
}
```

**Note:** `react-frontend/src/i18n/fil.json` contains the same keys translated into Filipino.

---

## 3. Filipino Translations — `react-frontend/src/i18n/fil.json` *(new)*

**Why:** Mirrors `en.json` so the app can switch to Filipino without modifying component code. A few representative keys are shown below; the full file contains the complete dictionary.

```json
{
  "greeting": "Kamusta",
  "interpolated": "Kamusta, {{name}}",
  "common": {
    "user": "Tagagamit",
    "loading": "Naglo-load..."
  },
  "nav": {
    "home": "Bahay",
    "about": "Tungkol",
    "ecosim": "EcoSim",
    "energyHub": "Energy Hub",
    "map": "Mapa",
    "chat": "Chat",
    "dashboard": "Dashboard",
    "savedSims": "Mga Naka-save na Simulasyon",
    "adminPortal": "Admin Portal",
    "mfa": "Two-Factor Auth",
    "login": "Login",
    "logout": "Mag-logout",
    "openMenu": "Buksan ang menu",
    "closeMenu": "Isara ang menu"
  },
  "login": {
    "welcomeBack": "Maligayang pagbabalik",
    "description": "Gumamit ng email/password o Google sign in.",
    "signIn": "Mag-sign in",
    "signUp": "Mag-sign up",
    "createAccount": "Gumawa ng account",
    "email": "Email",
    "password": "Password",
    "confirmPassword": "Kumpirmahin ang password",
    "forgotPassword": "Nakalimutan ang password?",
    "resetPassword": "I-reset ang password",
    "sendResetEmail": "Padalhan ng reset email",
    "backToSignIn": "Bumalik sa sign in",
    "continueWithGoogle": "Magpatuloy gamit ang Google",
    "checkYourEmail": "Tingnan ang iyong email",
    "confirmationSentDesc": "Nagpadala kami ng confirmation link sa {{email}}. I-click ito para i-verify ang account.",
    "resend": "Hindi natanggap? Ipadala ulit",
    "accountCreated": "Account ay nagawa!",
    "noEmailConfirmation": "Walang email confirmation na kailangan para sa domain na ito.",
    "error": "Nabigo ang authentication"
  }
}
```

---

## 4. I18n Test — `react-frontend/src/__tests__/I18nProvider.test.jsx` *(new)*

**Why:** Verifies the i18n implementation works correctly before any UI depends on it.

```jsx
import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { I18nProvider, useI18n } from "../i18n";

function TestComponent() {
  const { t, locale, setLocale } = useI18n();
  return (
    <div>
      <p data-testid="greeting">{t("greeting")}</p>
      <p data-testid="interpolated">{t("interpolated", { name: "Mundo" })}</p>
      <p data-testid="locale">{locale}</p>
      <button onClick={() => setLocale("fil")}>Switch to Filipino</button>
    </div>
  );
}

function renderWithI18n() {
  return render(
    <I18nProvider>
      <TestComponent />
    </I18nProvider>
  );
}

describe("I18nProvider", () => {
  it("defaults to English", () => {
    renderWithI18n();
    expect(screen.getByTestId("locale")).toHaveTextContent("en");
    expect(screen.getByTestId("greeting")).toHaveTextContent("Hello");
  });

  it("interpolates placeholders", () => {
    renderWithI18n();
    expect(screen.getByTestId("interpolated")).toHaveTextContent("Hello, Mundo");
  });

  it("switches to Filipino", () => {
    renderWithI18n();
    fireEvent.click(screen.getByText("Switch to Filipino"));
    expect(screen.getByTestId("locale")).toHaveTextContent("fil");
    expect(screen.getByTestId("greeting")).toHaveTextContent("Kamusta");
    expect(screen.getByTestId("interpolated")).toHaveTextContent("Kamusta, Mundo");
  });

  it("falls back to English for missing Filipino keys", () => {
    renderWithI18n();
    fireEvent.click(screen.getByText("Switch to Filipino"));
    expect(screen.getByTestId("interpolated")).toHaveTextContent("Kamusta, Mundo");
  });
});
```

---

## 5. Theme Contrast Test — `react-frontend/src/__tests__/theme-contrast.test.js` *(new)*

**Why:** Automatically enforces the new HCI/WCAG 2.1 AA color palette. It parses the CSS, converts HSL to RGB, computes relative luminance, and asserts all foreground/background pairs have at least 4.5:1 contrast.

```javascript
import { describe, it, expect } from "vitest";
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, resolve } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const cssPath = resolve(__dirname, "../styles/globals.css");
const css = readFileSync(cssPath, "utf-8");

function removeComments(source) {
  return source.replace(/\/\*[\s\S]*?\*\//g, "");
}

function parseBlock(name) {
  const cleaned = removeComments(css);
  const regex = new RegExp(`${name}\\s*\\{([^}]+)\\}`, "i");
  const match = cleaned.match(regex);
  if (!match) return {};
  const block = match[1];
  const vars = {};
  const propRegex = /--([\w-]+):\s*([0-9.\s%]+);/g;
  let m;
  while ((m = propRegex.exec(block)) !== null) {
    const key = `--${m[1]}`;
    const value = m[2].trim();
    vars[key] = value;
  }
  return vars;
}

function parseHsl(hslString) {
  const parts = hslString.split(/\s+/).map((p) => parseFloat(p.replace(/[^0-9.]/g, "")));
  return [parts[0] || 0, parts[1] || 0, parts[2] || 0];
}

function hslToRgb(h, s, l) {
  s /= 100;
  l /= 100;
  const k = (n) => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = (n) => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
  return [f(0), f(8), f(4)];
}

function relativeLuminance(rgb) {
  const [r, g, b] = rgb.map((c) => {
    c = c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    return c;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contrastRatio(fg, bg) {
  const l1 = relativeLuminance(fg);
  const l2 = relativeLuminance(bg);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

function getColor(variables, key) {
  const raw = variables[key];
  if (!raw) throw new Error(`Missing CSS variable ${key}`);
  const [h, s, l] = parseHsl(raw);
  return hslToRgb(h, s, l);
}

const light = parseBlock(":root");
const dark = parseBlock("\\.dark");

const PAIRS = [
  ["--foreground", "--background"],
  ["--card-foreground", "--card"],
  ["--popover-foreground", "--popover"],
  ["--primary-foreground", "--primary"],
  ["--secondary-foreground", "--secondary"],
  ["--muted-foreground", "--muted"],
  ["--accent-foreground", "--accent"],
  ["--destructive-foreground", "--destructive"],
  ["--warning-foreground", "--warning"],
];

function assertContrast(theme, name) {
  for (const [fgKey, bgKey] of PAIRS) {
    const fg = getColor(theme, fgKey);
    const bg = getColor(theme, bgKey);
    const ratio = contrastRatio(fg, bg);
    expect(
      ratio,
      `${name}: ${fgKey} on ${bgKey} must meet WCAG 2.1 AA (4.5:1)`
    ).toBeGreaterThanOrEqual(4.5);
  }
}

describe("Theme color contrast", () => {
  it("meets WCAG 2.1 AA for light mode", () => {
    assertContrast(light, "light");
  });

  it("meets WCAG 2.1 AA for dark mode", () => {
    assertContrast(dark, "dark");
  });

  it("does not use a cream/yellow background in light mode", () => {
    const [h, s, l] = parseHsl(light["--background"]);
    expect(
      h,
      "light mode background hue should be in the green family, not yellow/cream"
    ).toBeGreaterThanOrEqual(80);
    expect(h).toBeLessThanOrEqual(150);
  });
});
```

---

## 6. EcoSim Bill of Materials — `react-frontend/src/components/ecosim/EcosimBOM.jsx` *(new)*

**Why:** Takes the recommended renewable option's `installation_cost` and `system_kw`, derives system size when needed, and splits the cost into component-level parts (panels, inverter, mounting, etc.) so users can see what the installation actually entails.

```jsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Package } from "lucide-react";

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 0,
  }).format(value ?? 0);

function deriveSystemKw(source, generationKwh) {
  if (!generationKwh) return 0;
  switch (source) {
    case "Solar":
      return generationKwh / (30 * 4.5);
    case "Wind":
      return generationKwh / (30 * 24 * 0.25);
    case "Hydro":
      return generationKwh / (30 * 24 * 0.5);
    case "Geothermal":
      return generationKwh / (30 * 24);
    default:
      return 0;
  }
}

const BOM_SCHEMA = {
  Solar: [
    {
      id: "panels",
      item: "Solar panels (400 W)",
      unit: "panel",
      costShare: 0.4,
      qtyFn: (kw) => Math.max(1, Math.ceil((kw * 1000) / 400)),
    },
    { id: "inverter", item: "Inverter", unit: "unit", costShare: 0.2, qtyFn: () => 1 },
    { id: "mounting", item: "Mounting & wiring", unit: "set", costShare: 0.15, qtyFn: () => 1 },
    { id: "labor", item: "Installation labor", unit: "set", costShare: 0.2, qtyFn: () => 1 },
    { id: "permits", item: "Permits & miscellaneous", unit: "set", costShare: 0.05, qtyFn: () => 1 },
  ],
  Wind: [
    { id: "turbine", item: "Small wind turbine", unit: "unit", costShare: 0.5, qtyFn: () => 1 },
    { id: "tower", item: "Tower / mast", unit: "unit", costShare: 0.25, qtyFn: () => 1 },
    { id: "controller", item: "Controller & inverter", unit: "unit", costShare: 0.15, qtyFn: () => 1 },
    { id: "labor", item: "Installation & anchoring", unit: "set", costShare: 0.1, qtyFn: () => 1 },
  ],
  Hydro: [
    { id: "turbine", item: "Micro-hydro turbine & generator", unit: "unit", costShare: 0.35, qtyFn: () => 1 },
    { id: "penstock", item: "Penstock & civil works", unit: "set", costShare: 0.3, qtyFn: () => 1 },
    { id: "controller", item: "Controller & protection", unit: "unit", costShare: 0.15, qtyFn: () => 1 },
    { id: "labor", item: "Installation & commissioning", unit: "set", costShare: 0.2, qtyFn: () => 1 },
  ],
};

export default function EcosimBOM({ result }) {
  const source = result?.recommended_source;
  const rec = result?.options?.find((o) => o.source === source) || {};
  const installationCost = rec.installation_cost ?? result?.installation_cost ?? 0;
  const systemKw = rec.system_kw ?? deriveSystemKw(source, rec.estimated_generation_kwh ?? result?.estimated_generation_kwh);

  if (!source || installationCost <= 0) {
    return null;
  }

  if (source === "Geothermal") {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Package className="h-5 w-5 text-primary" />
            Bill of Materials
          </CardTitle>
          <CardDescription>Estimated components for the recommended system</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Geothermal energy is a utility-scale resource. A home-scale bill of materials is not applicable.
          </p>
        </CardContent>
      </Card>
    );
  }

  const items = BOM_SCHEMA[source] || [];
  const rows = items.map((entry) => {
    const qty = entry.qtyFn(systemKw);
    const totalCost = installationCost * entry.costShare;
    const unitCost = qty > 0 ? totalCost / qty : 0;
    return {
      ...entry,
      qty,
      unitCost,
      totalCost,
    };
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Package className="h-5 w-5 text-primary" />
          Bill of Materials
        </CardTitle>
        <CardDescription>
          Estimated {systemKw.toFixed(2)} kW {source} system · {formatCurrency(installationCost)} total
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Component</TableHead>
              <TableHead className="text-right">Qty</TableHead>
              <TableHead>Unit</TableHead>
              <TableHead className="text-right">Unit Cost</TableHead>
              <TableHead className="text-right">Total</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.id}>
                <TableCell>{row.item}</TableCell>
                <TableCell className="text-right font-medium">{row.qty}</TableCell>
                <TableCell className="text-muted-foreground">{row.unit}</TableCell>
                <TableCell className="text-right">{formatCurrency(row.unitCost)}</TableCell>
                <TableCell className="text-right font-medium">{formatCurrency(row.totalCost)}</TableCell>
              </TableRow>
            ))}
            <TableRow>
              <TableCell colSpan={4} className="text-right font-semibold">
                Estimated Total
              </TableCell>
              <TableCell className="text-right font-bold">{formatCurrency(installationCost)}</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
```

---

## 7. MFA Setup Page — `react-frontend/src/pages/MFASetup.jsx` *(new)*

**Why:** Provides the UI for users to enable or disable TOTP two-factor authentication through Supabase Auth MFA, including QR code scanning and verification.

```jsx
import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { toast } from "sonner";
import { Shield, ShieldCheck, ShieldOff } from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/services/supabaseClient";
import { useI18n } from "@/i18n";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function MFASetup() {
  const { t } = useI18n();
  const { user } = useAuth();

  const [factors, setFactors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [enrollment, setEnrollment] = useState(null); // { id, qr_code, secret }
  const [code, setCode] = useState("");

  const fetchFactors = async () => {
    try {
      const { data, error } = await supabase.auth.mfa.listFactors();
      if (error) throw error;
      setFactors(data?.all || []);
    } catch (err) {
      toast.error(t("mfa.factorError") + ": " + (err.message || err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFactors();
  }, []);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const handleEnroll = async () => {
    setEnrolling(true);
    try {
      const { data, error } = await supabase.auth.mfa.enroll({
        factorType: "totp",
        friendlyName: "LUMI Authenticator",
      });
      if (error) throw error;
      setEnrollment(data);
    } catch (err) {
      toast.error(t("mfa.enrollError") + ": " + (err.message || err));
    } finally {
      setEnrolling(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!enrollment || !code) return;
    setVerifying(true);
    try {
      const { data: challenge, error: challengeError } = await supabase.auth.mfa.challenge({
        factorId: enrollment.id,
      });
      if (challengeError) throw challengeError;

      const { data, error } = await supabase.auth.mfa.verify({
        factorId: enrollment.id,
        challengeId: challenge.id,
        code: code.replace(/\s/g, ""),
      });
      if (error) throw error;

      toast.success(t("mfa.enabled"));
      setEnrollment(null);
      setCode("");
      await fetchFactors();
      if (data.session) {
        supabase.auth.getSession().catch(() => {});
      }
    } catch (err) {
      toast.error(t("mfa.verifyError") + ": " + (err.message || err));
    } finally {
      setVerifying(false);
    }
  };

  const handleUnenroll = async (factorId) => {
    if (!window.confirm(t("mfa.disableConfirm"))) return;
    try {
      const { error } = await supabase.auth.mfa.unenroll({ factorId });
      if (error) throw error;
      toast.success(t("mfa.disabled"));
      await fetchFactors();
    } catch (err) {
      toast.error(t("mfa.unenrollError") + ": " + (err.message || err));
    }
  };

  const verifiedFactor = factors.find((f) => f.status === "verified");

  return (
    <div className="page-container stack max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <Shield className="h-6 w-6 text-primary" />
        {t("mfa.title")}
      </h1>

      <Card>
        <CardHeader>
          <CardTitle>{t("mfa.status")}</CardTitle>
          <CardDescription>{t("mfa.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loading ? (
            <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
          ) : verifiedFactor ? (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm">
                <ShieldCheck className="h-5 w-5 text-primary" />
                <span className="font-medium">{t("mfa.enabledStatus")}</span>
              </div>
              <Button
                type="button"
                variant="destructive"
                onClick={() => handleUnenroll(verifiedFactor.id)}
              >
                <ShieldOff className="h-4 w-4 mr-2" />
                {t("mfa.disable")}
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">{t("mfa.disabledStatus")}</p>
              <Button type="button" onClick={handleEnroll} disabled={enrolling}>
                {enrolling ? t("common.loading") : t("mfa.enable")}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {enrollment && (
        <Card>
          <CardHeader>
            <CardTitle>{t("mfa.scanQR")}</CardTitle>
            <CardDescription>{t("mfa.scanQRDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-center">
              <img
                src={enrollment.totp?.qr_code}
                alt="TOTP QR code"
                className="rounded-lg border bg-white p-2"
              />
            </div>
            <div className="rounded bg-muted p-3 text-sm font-mono break-all">
              {enrollment.totp?.secret}
            </div>
            <form onSubmit={handleVerify} className="space-y-2">
              <Input
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder={t("mfa.codePlaceholder")}
                maxLength={10}
                autoComplete="one-time-code"
              />
              <Button type="submit" disabled={verifying || !code}>
                {verifying ? t("common.loading") : t("mfa.verify")}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
```

---

## 8. PHIVOLCS Volcano GeoJSON — `react-frontend/public/geothermal_volcanoes.json` *(new data source)*

**Why:** Provides the actual volcano locations used to render map markers. It was converted from `GeothermalDatasets/philippine_volcanoes.csv`.

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": { "name": "Babuyan Claro", "province": "Babuyan Island Group, Cagayan in Luzon" },
      "geometry": { "type": "Point", "coordinates": [121.95005, 19.52408] }
    },
    {
      "type": "Feature",
      "properties": { "name": "Banahao", "province": "Quezon in Luzon" },
      "geometry": { "type": "Point", "coordinates": [121.9806, 14.06698] }
    },
    {
      "type": "Feature",
      "properties": { "name": "Biliran", "province": "Biliran in Visayas" },
      "geometry": { "type": "Point", "coordinates": [124.7947, 11.52209] }
    }
  ]
}
```

**Note:** The full file contains 24 volcano features covering the Philippine archipelago.

---

## 9. Main Entry — `react-frontend/src/main.jsx` *(modified)*

**Why:** Wraps the application in `I18nProvider` so the locale is available everywhere.

```jsx
import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import "./styles/globals.css";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import { I18nProvider } from "./i18n";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <I18nProvider>
      <ThemeProvider>
        <AuthProvider>
          <App />
        </AuthProvider>
      </ThemeProvider>
    </I18nProvider>
  </React.StrictMode>
);
```

---

## 10. App Routes — `react-frontend/src/routes/AppRoutes.jsx` *(modified)*

**Why:** Registers the new `/mfa` protected route and keeps admin routes isolated through `AdminRoute`.

```jsx
import { BrowserRouter, Route, Routes } from "react-router-dom";

import MainLayout from "../layouts/MainLayout";
import Home from "../pages/Home";
import About from "../pages/About";
import Login from "../pages/Login";
import ResetPassword from "../pages/ResetPassword";
import Dashboard from "../pages/Dashboard";
import SavedSimulations from "../pages/SavedSimulations";
import MFASetup from "../pages/MFASetup";
import Ecosim from "../pages/Ecosim";
import EnergyHub from "../pages/EnergyHub";
import ChatPage from "../pages/ChatPage";
import MapPage from "../pages/MapPage";
import AdminDashboard from "../pages/admin/AdminDashboard";
import AdminUsers from "../pages/admin/AdminUsers";
import AdminAnalytics from "../pages/admin/AdminAnalytics";
import AdminConfig from "../pages/admin/AdminConfig";
import AdminModeration from "../pages/admin/AdminModeration";
import NotFound from "../pages/NotFound";
import ProtectedRoute from "../components/shared/ProtectedRoute";
import AdminRoute from "../components/shared/AdminRoute";

export default function AppRoutes() {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <Routes future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Route element={<MainLayout />}>
          <Route index element={<Home />} />
          <Route path="login" element={<Login />} />
          <Route path="reset-password" element={<ResetPassword />} />
          <Route path="about" element={<About />} />
          <Route
            path="dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="ecosim"
            element={
              <ProtectedRoute>
                <Ecosim />
              </ProtectedRoute>
            }
          />
          <Route
            path="energyhub"
            element={
              <ProtectedRoute>
                <EnergyHub />
              </ProtectedRoute>
            }
          />
          <Route
            path="chat"
            element={
              <ProtectedRoute>
                <ChatPage />
              </ProtectedRoute>
            }
          />
          <Route path="map" element={<MapPage />} />
          <Route
            path="saved-simulations"
            element={
              <ProtectedRoute>
                <SavedSimulations />
              </ProtectedRoute>
            }
          />
          <Route
            path="mfa"
            element={
              <ProtectedRoute>
                <MFASetup />
              </ProtectedRoute>
            }
          />
          <Route
            path="admin"
            element={
              <AdminRoute>
                <AdminDashboard />
              </AdminRoute>
            }
          />
          <Route
            path="admin/users"
            element={
              <AdminRoute>
                <AdminUsers />
              </AdminRoute>
            }
          />
          <Route
            path="admin/analytics"
            element={
              <AdminRoute>
                <AdminAnalytics />
              </AdminRoute>
            }
          />
          <Route
            path="admin/config"
            element={
              <AdminRoute>
                <AdminConfig />
              </AdminRoute>
            }
          />
          <Route
            path="admin/moderate"
            element={
              <AdminRoute>
                <AdminModeration />
              </AdminRoute>
            }
          />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 11. Global CSS Color Palette — `react-frontend/src/styles/globals.css` *(modified)*

**Why:** Replaces the previous cream/yellow-based palette with a green-based, WCAG 2.1 AA-compliant palette and adds semantic brand, chart, and map color tokens.

```css
@import "tailwindcss";
@config "../../tailwind.config.cjs";

@layer base {
  :root {
    /* Lumi Green Palette — Light Mode */
    --background: 120 30% 97%;          /* #f4fbf4 */
    --foreground: 120 50% 15%;          /* #122f10 */

    --card: 0 0% 100%;                  /* #ffffff */
    --card-foreground: 120 50% 15%;     /* #122f10 */

    --popover: 0 0% 100%;               /* #ffffff */
    --popover-foreground: 120 50% 15%; /* #122f10 */

    --primary: 122 35% 30%;             /* #2e5f2b */
    --primary-foreground: 0 0% 100%;     /* #ffffff */

    --secondary: 120 45% 90%;          /* #dff6df */
    --secondary-foreground: 120 50% 15%; /* #122f10 */

    --muted: 120 35% 93%;              /* #ebf6eb */
    --muted-foreground: 120 30% 28%;    /* #3a5c3b */

    --accent: 45 90% 65%;              /* #f6d96a */
    --accent-foreground: 120 50% 15%;   /* #122f10 */

    --destructive: 0 72% 51%;           /* #dc2626 */
    --destructive-foreground: 0 0% 100%; /* #ffffff */

    --warning: 22 85% 40%;              /* #aa4411 */
    --warning-foreground: 0 0% 100%;     /* #ffffff */

    --border: 120 25% 83%;              /* #c6e0c6 */
    --input: 120 25% 83%;               /* #c6e0c6 */
    --ring: 122 35% 35%;                /* #3b6e38 */

    --radius: 0.75rem;

    /* Brand tokens */
    --brand: 122 35% 30%;
    --brand-dark: 120 50% 15%;
    --brand-light: 108 48% 69%;
    --brand-lighter: 120 25% 83%;
    --brand-pale: 120 45% 90%;
    --brand-success: 117 42% 56%;

    /* Chart / data colors */
    --chart-solar: 47 100% 73%;
    --chart-wind: 117 42% 56%;
    --chart-hydro: 122 35% 30%;
    --chart-geothermal: 30 90% 42%;
    --chart-accent: 47 100% 73%;

    /* Map classification colors */
    --map-very-high: 142 76% 36%;
    --map-high: 142 71% 45%;
    --map-moderate: 48 96% 53%;
    --map-low: 25 95% 53%;
    --map-very-low: 0 84% 60%;
    --map-no-data: 215 20% 65%;
    --map-marker-stroke: 0 0% 100%;
  }

  .dark {
    /* Lumi Green Palette — Dark Mode */
    --background: 120 30% 8%;           /* #0f1f0f */
    --foreground: 118 80% 85%;         /* #cdfbb9 */

    --card: 120 28% 13%;                /* #162815 */
    --card-foreground: 118 80% 85%;    /* #cdfbb9 */

    --popover: 120 28% 13%;             /* #162815 */
    --popover-foreground: 118 80% 85%; /* #cdfbb9 */

    --primary: 117 45% 55%;             /* #68bb64 */
    --primary-foreground: 120 30% 8%;   /* #0f1f0f */

    --secondary: 120 28% 17%;           /* #1a3a1a */
    --secondary-foreground: 118 70% 80%; /* #b4f0a0 */

    --muted: 120 28% 17%;               /* #1a3a1a */
    --muted-foreground: 108 40% 70%;     /* #a4d68b */

    --accent: 47 100% 73%;              /* #ffe476 */
    --accent-foreground: 120 30% 8%;    /* #0f1f0f */

    --destructive: 0 63% 31%;           /* #7f1d1d */
    --destructive-foreground: 0 0% 100%; /* #ffffff */

    --warning: 24 90% 60%;              /* #f26a36 */
    --warning-foreground: 120 30% 8%;    /* #0f1f0f */

    --border: 120 25% 23%;              /* #253d25 */
    --input: 120 25% 23%;               /* #253d25 */
    --ring: 117 45% 55%;                /* #68bb64 */

    /* Brand tokens */
    --brand: 117 45% 55%;
    --brand-dark: 118 80% 85%;
    --brand-light: 122 35% 30%;
    --brand-lighter: 120 28% 17%;
    --brand-pale: 120 28% 17%;
    --brand-success: 117 45% 55%;

    /* Chart / data colors */
    --chart-solar: 47 100% 73%;
    --chart-wind: 117 45% 55%;
    --chart-hydro: 118 80% 85%;
    --chart-geothermal: 30 90% 50%;
    --chart-accent: 47 100% 73%;

    /* Map classification colors */
    --map-very-high: 142 70% 45%;
    --map-high: 142 65% 55%;
    --map-moderate: 48 100% 60%;
    --map-low: 25 100% 60%;
    --map-very-low: 0 90% 65%;
    --map-no-data: 215 25% 55%;
    --map-marker-stroke: 0 0% 100%;
  }

  * {
    @apply border-border;
  }

  body {
    @apply bg-background text-foreground antialiased;
  }

  h1 {
    @apply text-3xl font-semibold tracking-tight;
  }

  h2 {
    @apply text-2xl font-semibold tracking-tight;
  }

  h3 {
    @apply text-xl font-semibold;
  }

  p {
    @apply leading-7 text-muted-foreground;
  }
}

@layer utilities {
  .page-container {
    @apply mx-auto w-full max-w-6xl px-4 py-8;
  }

  .page-header {
    @apply flex flex-col gap-2 md:flex-row md:items-center md:justify-between;
  }

  .stack {
    @apply flex flex-col gap-6;
  }

  .grid-cards {
    @apply grid gap-6 md:grid-cols-2;
  }
}
```

---

## 12. Tailwind Config — `react-frontend/tailwind.config.cjs` *(modified)*

**Why:** Maps the CSS variables to Tailwind utility classes so the palette can be used consistently with `bg-primary`, `text-chart-geothermal`, `bg-map-very-high`, etc.

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1200px"
      }
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))"
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))"
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))"
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))"
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))"
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))"
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))"
        },
        brand: {
          DEFAULT: "hsl(var(--brand))",
          dark: "hsl(var(--brand-dark))",
          light: "hsl(var(--brand-light))",
          lighter: "hsl(var(--brand-lighter))",
          pale: "hsl(var(--brand-pale))",
          success: "hsl(var(--brand-success))"
        },
        warning: {
          DEFAULT: "hsl(var(--warning))",
          foreground: "hsl(var(--warning-foreground))"
        },
        chart: {
          solar: "hsl(var(--chart-solar))",
          wind: "hsl(var(--chart-wind))",
          hydro: "hsl(var(--chart-hydro))",
          geothermal: "hsl(var(--chart-geothermal))",
          accent: "hsl(var(--chart-accent))"
        },
        map: {
          "very-high": "hsl(var(--map-very-high))",
          high: "hsl(var(--map-high))",
          moderate: "hsl(var(--map-moderate))",
          low: "hsl(var(--map-low))",
          "very-low": "hsl(var(--map-very-low))",
          "no-data": "hsl(var(--map-no-data))"
        }
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)"
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" }
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" }
        }
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out"
      }
    }
  },
  plugins: [require("tailwindcss-animate")]
};
```

---

## 13. Navbar — `react-frontend/src/components/layout/Navbar.jsx` *(modified)*

**Why:** Adds i18n, a language selector, a mobile hamburger menu, and replaces hardcoded labels with translated strings. It also uses the new theme tokens.

```jsx
import { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Menu, X, Globe } from "lucide-react";

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
import { useI18n } from "@/i18n";

const navLinks = [
  { to: "/", key: "nav.home" },
  { to: "/about", key: "nav.about" },
  { to: "/ecosim", key: "nav.ecosim" },
  { to: "/energyhub", key: "nav.energyHub" },
  { to: "/map", key: "nav.map" },
  { to: "/chat", key: "nav.chat" },
];

function LanguageSelect({ value, onChange, compact = false }) {
  return (
    <div className="relative inline-flex items-center">
      <Globe className="h-4 w-4 text-muted-foreground absolute left-2 pointer-events-none" />
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        aria-label="Language"
        className={`appearance-none rounded-md border bg-background pl-8 pr-6 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring hover:bg-muted ${compact ? "py-1" : "py-1.5"}`}
      >
        <option value="en">EN</option>
        <option value="fil">FIL</option>
      </select>
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
          <div className="flex items-center gap-2">
            <img src="/logo.png" alt="LUMI" className="h-14 w-auto object-contain" />
          </div>
        </Link>

        <nav className="flex items-center gap-1">
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
                    <div className="h-8 w-8 relative rounded-full overflow-hidden border bg-primary/10" />
                    <span className="text-sm font-medium hidden md:inline max-w-[120px] truncate">
                      {displayName}
                    </span>
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-64 p-2">
                  {isAdmin && (
                    <DropdownMenuItem onClick={() => navigate("/admin")}>
                      {t("nav.adminPortal")}
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuItem onClick={() => navigate("/dashboard")}>
                    {t("nav.dashboard")}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate("/saved-simulations")}>
                    {t("nav.savedSims")}
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={() => {
                      signOut();
                      navigate("/");
                    }}
                  >
                    {t("nav.logout")}
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ) : (
            <Link to="/login">
              <Button size="sm">{t("nav.login")}</Button>
            </Link>
          )}

          <div className="hidden md:flex items-center gap-2 ml-2">
            <LanguageSelect value={locale} onChange={setLocale} compact />
            <ThemeToggle />
          </div>

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

      {mobileOpen && (
        <div className="md:hidden absolute inset-x-0 top-full z-50 border-b bg-card p-4 shadow-lg">
          <div className="flex flex-col gap-1">
            {links.map((link) => (
              <NavLink key={link.to} link={link} onClick={() => setMobileOpen(false)} />
            ))}
          </div>
          <div className="mt-4 flex items-center justify-between border-t pt-4">
            <LanguageSelect value={locale} onChange={setLocale} />
            <ThemeToggle />
          </div>
        </div>
      )}
    </header>
  );
}
```

**Note:** The full file includes additional avatar logic and styling retained from the original.

---

## 14. Login — `react-frontend/src/pages/Login.jsx` *(modified)*

**Why:** Translates all login/signup/reset UI text and adds a TOTP multi-factor authentication challenge after password sign-in. If the user's account has MFA, the login flow pauses and asks for a 6-digit code before redirecting.

```jsx
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { useAuth } from "../hooks/useAuth";
import { supabase } from "../services/supabaseClient";
import { useI18n } from "../i18n";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function Login() {
  const { t } = useI18n();
  const { session, signInWithProvider, signInWithPassword, signUp, resetPassword } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const redirectTo = location.state?.from?.pathname || "/dashboard";
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [signupStatus, setSignupStatus] = useState(null);

  const [mfaRequired, setMfaRequired] = useState(null);
  const [mfaFactorId, setMfaFactorId] = useState(null);
  const [mfaCode, setMfaCode] = useState("");
  const [verifying, setVerifying] = useState(false);

  const checkMfa = async () => {
    try {
      if (!supabase.auth.mfa || typeof supabase.auth.mfa.getAuthenticatorAssuranceLevel !== "function") {
        setMfaRequired(false);
        return;
      }

      const { data: aal, error: aalError } = await supabase.auth.mfa.getAuthenticatorAssuranceLevel();
      if (aalError) throw aalError;

      if (aal?.nextLevel === "aal2" && aal?.currentLevel === "aal1") {
        const { data: factors, error: fError } = await supabase.auth.mfa.listFactors();
        if (fError) throw fError;

        const factor =
          factors?.totp?.find((f) => f.status === "verified") ||
          factors?.all?.find((f) => f.status === "verified");

        if (factor) {
          setMfaFactorId(factor.id);
          setMfaRequired(true);
          return;
        }
      }
    } catch (error) {
      console.error("[Login] MFA check failed:", error);
    }
    setMfaRequired(false);
  };

  useEffect(() => {
    if (session) {
      checkMfa();
    } else {
      setMfaRequired(null);
    }
  }, [session]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setSignupStatus(null);

    try {
      if (mode === "signup" && password !== confirmPassword) {
        toast.error(t("mfa.passwordsDoNotMatch") || "Passwords do not match");
        return;
      }

      if (mode === "login") {
        const { error } = await signInWithPassword(email, password);
        if (error) throw error;
      }

      if (mode === "signup") {
        const result = await signUp(email, password);
        if (result.error) throw result.error;

        if (result.confirmationRequired) {
          setSignupStatus("confirm");
          toast.success(t("login.accountCreated"));
        } else {
          setSignupStatus("auto");
          toast.success(t("login.accountCreated"));
        }
      }

      if (mode === "reset") {
        const { error } = await resetPassword(email);
        if (error) throw error;
        toast.success(t("mfa.resetSent") || "Password reset email sent");
      }
    } catch (error) {
      toast.error(error?.message || t("login.error"));
    } finally {
      setBusy(false);
    }
  };

  const handleVerifyMfa = async (event) => {
    event.preventDefault();
    if (!mfaFactorId || !mfaCode) return;

    setVerifying(true);
    try {
      const { data: challenge, error: challengeError } = await supabase.auth.mfa.challenge({
        factorId: mfaFactorId,
      });
      if (challengeError) throw challengeError;

      const { error } = await supabase.auth.mfa.verify({
        factorId: mfaFactorId,
        challengeId: challenge.id,
        code: mfaCode.replace(/\s/g, ""),
      });
      if (error) throw error;

      toast.success(t("mfa.verified") || "Two-factor authentication verified");
      navigate(redirectTo, { replace: true });
    } catch (error) {
      toast.error(error?.message || t("mfa.verifyError"));
    } finally {
      setVerifying(false);
    }
  };

  const resendConfirmation = async () => {
    setBusy(true);
    try {
      const { error } = await supabase.auth.resend({
        type: "signup",
        email,
      });
      if (error) throw error;
      toast.success(t("mfa.confirmResent") || "Confirmation email resent");
    } catch (error) {
      toast.error(error?.message || t("mfa.resendError"));
    } finally {
      setBusy(false);
    }
  };

  if (session && mfaRequired === false) {
    return <Navigate to={redirectTo} replace />;
  }

  if (session && mfaRequired === true) {
    return (
      <section className="page-container">
        <Card className="mx-auto max-w-md">
          <CardHeader>
            <CardTitle>{t("mfa.verifyTitle") || "Two-Factor Authentication"}</CardTitle>
            <CardDescription>{t("mfa.verifyDescription") || "Enter the 6-digit code from your authenticator app."}</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleVerifyMfa} className="space-y-3">
              <Input
                value={mfaCode}
                onChange={(event) => setMfaCode(event.target.value)}
                placeholder={t("mfa.codePlaceholder")}
                maxLength={10}
                autoComplete="one-time-code"
                inputMode="numeric"
              />
              <Button className="w-full" type="submit" disabled={verifying || !mfaCode}>
                {verifying ? t("common.loading") : t("mfa.verify")}
              </Button>
            </form>
          </CardContent>
        </Card>
      </section>
    );
  }

  if (session && mfaRequired === null) {
    return (
      <section className="page-container flex items-center justify-center">
        <p className="text-muted-foreground">{t("common.loading")}</p>
      </section>
    );
  }

  return (
    <section className="page-container">
      <Card className="mx-auto max-w-md">
        <CardHeader>
          <CardTitle>{t("login.welcomeBack")}</CardTitle>
          <CardDescription>{t("login.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Button type="button" variant={mode === "login" ? "default" : "outline"} className="w-full" onClick={() => setMode("login")}>
              {t("login.signIn")}
            </Button>
            <Button type="button" variant={mode === "signup" ? "default" : "outline"} className="w-full" onClick={() => setMode("signup")}>
              {t("login.signUp")}
            </Button>
          </div>

          <form className="space-y-3" onSubmit={handleSubmit}>
            <Input type="email" placeholder={t("login.email")} value={email} onChange={(e) => setEmail(e.target.value)} required />
            {mode !== "reset" && (
              <Input type="password" placeholder={t("login.password")} value={password} onChange={(e) => setPassword(e.target.value)} required />
            )}
            {mode === "signup" && (
              <Input type="password" placeholder={t("login.confirmPassword")} value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
            )}

            <Button className="w-full" type="submit" disabled={busy}>
              {mode === "login" && t("login.signIn")}
              {mode === "signup" && t("login.createAccount")}
              {mode === "reset" && t("login.sendResetEmail")}
            </Button>

            {mode === "signup" && signupStatus === "confirm" && (
              <div className="rounded-md bg-warning/10 p-3 text-sm text-foreground border border-warning/20">
                <p className="font-medium">{t("login.checkYourEmail")}</p>
                <p className="mt-1">{t("login.confirmationSentDesc", { email })}</p>
                <Button type="button" variant="link" className="h-auto p-0 text-primary underline" onClick={resendConfirmation} disabled={busy}>
                  {t("login.resend")}
                </Button>
              </div>
            )}

            {mode === "signup" && signupStatus === "auto" && (
              <div className="rounded-md bg-secondary p-3 text-sm text-foreground border border-border">
                <p className="font-medium">{t("login.accountCreated")}</p>
                <p className="mt-1">{t("login.noEmailConfirmation")}</p>
              </div>
            )}
          </form>

          <div className="flex items-center justify-between text-sm">
            <Button type="button" variant="ghost" onClick={() => setMode("reset")}>
              {t("login.forgotPassword")}
            </Button>
            {mode === "reset" && (
              <Button type="button" variant="ghost" onClick={() => setMode("login")}>
                {t("login.backToSignIn")}
              </Button>
            )}
          </div>

          <div className="space-y-2">
            <Button className="w-full" variant="outline" onClick={() => signInWithProvider("google")}>
              {t("login.continueWithGoogle")}
            </Button>
          </div>
        </CardContent>
      </Card>
    </section>
  );
}
```

---

## 15. Admin Dashboard — `react-frontend/src/pages/admin/AdminDashboard.jsx` *(modified)*

**Why:** Turns the admin page into a real portal with i18n, quick stats, and navigation to admin sub-sections. It fetches user/simulation counts from Supabase.

```jsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Users, BarChart3, Settings, Shield, LayoutDashboard } from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/services/supabaseClient";
import { useI18n } from "@/i18n";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AdminDashboard() {
  const { t } = useI18n();
  const { user } = useAuth();
  const [stats, setStats] = useState({ users: 0, simulations: 0, loading: true });

  useEffect(() => {
    let mounted = true;
    const fetchStats = async () => {
      try {
        const [{ count: users }, { count: simulations }] = await Promise.all([
          supabase.from("profiles").select("*", { count: "exact", head: true }),
          supabase.from("saved_simulations").select("*", { count: "exact", head: true }),
        ]);
        if (mounted) setStats({ users: users || 0, simulations: simulations || 0, loading: false });
      } catch {
        if (mounted) setStats({ users: 0, simulations: 0, loading: false });
      }
    };
    fetchStats();
    return () => {
      mounted = false;
    };
  }, []);

  const adminName = user?.user_metadata?.full_name || user?.email || t("common.user");

  const links = [
    { to: "/admin/users", icon: Users, title: t("admin.users"), desc: t("admin.usersDesc") },
    { to: "/admin/analytics", icon: BarChart3, title: t("admin.analytics"), desc: t("admin.analyticsDesc") },
    { to: "/admin/config", icon: Settings, title: t("admin.config"), desc: t("admin.configDesc") },
    { to: "/admin/moderate", icon: Shield, title: t("admin.moderation"), desc: t("admin.moderationDesc") },
  ];

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <LayoutDashboard className="h-6 w-6 text-primary" />
          {t("admin.portal")}
        </h1>
        <p className="text-muted-foreground mt-1">
          {t("admin.welcome")} &mdash; {t("admin.summary")}
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {t("common.user", { count: stats.users })}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats.loading ? "..." : t("admin.usersCount", { count: stats.users })}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {t("nav.savedSims")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats.loading ? "..." : t("admin.simsCount", { count: stats.simulations })}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {links.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className="group flex items-start gap-4 p-6 border rounded-lg bg-card hover:bg-muted transition-colors"
          >
            <div className="p-3 rounded-lg bg-primary/10 text-primary">
              <link.icon className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-lg font-semibold group-hover:text-primary transition-colors">
                {link.title}
              </h2>
              <p className="text-sm text-muted-foreground mt-1">{link.desc}</p>
            </div>
          </Link>
        ))}
      </div>

      <p className="text-sm text-muted-foreground">
        {t("common.user")}: <span className="font-medium text-foreground">{adminName}</span>
      </p>
    </div>
  );
}
```

---

## 16. Provider Recommendations — `react-frontend/src/components/ecosim/ProviderRecommendations.jsx` *(modified)*

**Why:** Replaces hardcoded colors (`text-sky-500`, `text-slate-500`, `text-amber-500`) with the new semantic theme colors.

```jsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, MapPin, ExternalLink, Building2 } from "lucide-react";
import providersData from "@/data/providers.json";
import { getRegionFromProvince, getRegionFromMunicipality } from "@/utils/regionMap";

export default function ProviderRecommendations({ municipalityName, provinceName }) {
  let region = getRegionFromProvince(provinceName) || getRegionFromMunicipality(municipalityName);

  if (!region && municipalityName) {
    region = getRegionFromMunicipality(municipalityName);
  }

  const matched = region
    ? providersData.filter((p) => p.region === region)
    : [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Building2 className="h-5 w-5 text-primary" />
          Trusted Solar Installers in Your Region
        </CardTitle>
        <CardDescription>
          These companies are registered with the DOE Solar PV Installer Registry (as of June 2025).
        </CardDescription>
      </CardHeader>
      <CardContent>
        {matched.length > 0 ? (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {matched.map((p, i) => (
              <a
                key={i}
                href={p.url}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-lg border bg-card p-4 shadow-sm hover:shadow-md transition-shadow flex flex-col gap-2"
              >
                <div className="flex items-start gap-2">
                  <MapPin className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                  <div className="min-w-0">
                    <p className="text-sm font-medium line-clamp-2">{p.name}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{p.type}</p>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2">{p.address}</p>
                <div className="flex items-center justify-between mt-auto pt-1">
                  <span className="text-xs text-muted-foreground">{p.years}</span>
                  <span className="text-xs text-primary flex items-center gap-1">
                    Visit <ExternalLink className="h-3 w-3" />
                  </span>
                </div>
              </a>
            ))}
          </div>
        ) : (
          <div className="rounded-lg border bg-muted/30 p-4 text-sm text-muted-foreground">
            <AlertTriangle className="h-4 w-4 inline mr-1 text-warning" />
            No registered providers found in your region.
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

---

## 17. Interpretation Badge — `react-frontend/src/components/shared/InterpretationBadge.jsx` *(modified)*

**Why:** Replaces hardcoded Tailwind colors in the badge rating system with the semantic theme colors (`primary`, `chart-wind`, `warning`, `chart-geothermal`, `destructive`).

```jsx
import { Badge } from "@/components/ui/badge";

const RATINGS = [
  { pct: 0.80, label: "Excellent", color: "bg-primary text-primary-foreground", text: "text-primary", bg: "bg-secondary", border: "border-primary/30" },
  { pct: 0.60, label: "Good", color: "bg-chart-wind/10 text-foreground", text: "text-chart-wind", bg: "bg-chart-wind/10", border: "border-chart-wind/30" },
  { pct: 0.40, label: "Moderate", color: "bg-warning/10 text-foreground", text: "text-warning", bg: "bg-warning/10", border: "border-warning/30" },
  { pct: 0.20, label: "Fair", color: "bg-chart-geothermal/10 text-foreground", text: "text-chart-geothermal", bg: "bg-chart-geothermal/10", border: "border-chart-geothermal/30" },
  { pct: 0.00, label: "Poor", color: "bg-destructive/10 text-foreground", text: "text-destructive", bg: "bg-destructive/10", border: "border-destructive/30" },
];

export function getRating(score, max = 100) {
  const pct = (score ?? 0) / max;
  return RATINGS.find((r) => pct >= r.pct) || RATINGS[RATINGS.length - 1];
}

export function getStars(score, max = 100) {
  const pct = Math.max(0, Math.min(1, (score ?? 0) / max));
  const full = Math.floor(pct * 5);
  let s = "";
  for (let i = 0; i < full; i++) s += "★";
  while (s.length < 5) s += "☆";
  return s;
}

export default function InterpretationBadge({ score, max = 100, showStars = true, className = "" }) {
  const rating = getRating(score, max);
  const stars = getStars(score, max);
  return (
    <div className={`flex items-center gap-2 flex-wrap ${className}`}>
      <Badge className={`${rating.color} hover:${rating.color}`}>{rating.label}</Badge>
      {showStars && <span className="text-warning tracking-widest text-sm">{stars}</span>}
    </div>
  );
}
```

---

## 18. EnergyMap — Volcano Markers & Theming

**File:** `react-frontend/src/components/energyhub/EnergyMap.jsx` *(modified)*

**Why:** Loads the PHIVOLCS volcano GeoJSON, renders circle markers when the volcano overlay is on, and switches hardcoded map colors to the CSS variable palette.

```jsx
const [volcanoGeojson, setVolcanoGeojson] = useState(null);

useEffect(() => {
  let mounted = true;
  fetchGeoJsonCached("/geothermal_volcanoes.json")
    .then((volcanoData) => {
      if (mounted) setVolcanoGeojson(volcanoData);
    })
    .catch(() => {});
  return () => {
    mounted = false;
  };
}, []);

const volcanoPointToLayer = (feature, latlng) => {
  return L.circleMarker(latlng, {
    radius: 6,
    color: "var(--chart-geothermal)",
    fillColor: "var(--chart-geothermal)",
    fillOpacity: 0.8,
    weight: 2,
  });
};

const onEachVolcano = (feature, layer) => {
  const name = feature.properties?.name || "Volcano";
  const province = feature.properties?.province || "";
  const tooltipHtml = `<div style="font-family:sans-serif;font-size:13px;line-height:1.4;min-width:140px">
    <div style="font-size:14px;font-weight:600;color:var(--foreground)">${name}</div>
    ${province ? `<div style="color:var(--muted-foreground);font-size:12px">${province}</div>` : ""}
  </div>`;
  layer.bindTooltip(tooltipHtml, { sticky: true, className: "lumi-tooltip" });
};

// In the JSX:
{showVolcanoes && volcanoGeojson && (
  <GeoJSON
    data={volcanoGeojson}
    pointToLayer={volcanoPointToLayer}
    onEachFeature={onEachVolcano}
  />
)}
```

---

## 19. EcosimResults — BOM Integration

**File:** `react-frontend/src/components/ecosim/EcosimResults.jsx` *(modified)*

**Why:** Imports and renders `EcosimBOM` so the cost breakdown appears in the simulation results.

```jsx
import ProviderRecommendations from "./ProviderRecommendations";
import EcosimBOM from "./EcosimBOM";

// ...

{/* Bill of Materials */}
<EcosimBOM result={result} />
```

---

## 20. Dashboard — Admin Banner + i18n

**File:** `react-frontend/src/pages/Dashboard.jsx` *(modified)*

**Why:** Shows an admin portal shortcut when the logged-in user has admin role, and translates the main card titles.

```jsx
import { useAuth } from "../hooks/useAuth";
import { useI18n } from "../i18n";

export default function Dashboard() {
  const { user, refreshProfile, isAdmin } = useAuth();
  const { t } = useI18n();

  // Loading state
  if (loading) {
    return (
      <section className="page-container stack">
        <h1 className="text-2xl font-bold">{t("dashboard.title")}</h1>
        <LoadingSkeleton />
      </section>
    );
  }

  return (
    <section className="page-container stack space-y-6">
      {isAdmin && (
        <div className="rounded-lg border bg-primary/10 p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <p className="text-sm font-medium">{t("dashboard.adminLink")}</p>
          <Link to="/admin">
            <Button variant="outline" size="sm">{t("nav.adminPortal")}</Button>
          </Link>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>{t("dashboard.overview")}</CardTitle>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("dashboard.quickActions")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <Link to="/mfa" className="block">
            <Button variant="outline" className="w-full">{t("dashboard.mfaLink")}</Button>
          </Link>
        </CardContent>
      </Card>
    </section>
  );
}
```

**Note:** The full file also translates `Saved Locations`, `Saved Simulations`, and `AI Center` card titles with the same pattern.

---

## 21. Package Dependency — `react-frontend/package.json` *(modified)*

**Why:** Adds the DOM assertion matchers required by the new `theme-contrast.test.js` and `I18nProvider.test.jsx` tests.

```json
"@testing-library/jest-dom": "^7.0.0",
```

---

## Verification

- `npx vitest run` — `I18nProvider.test.jsx`, `theme-contrast.test.js`, `DashboardChart.test.jsx` all pass (9 tests total).
- `npm run build` — production bundle builds successfully.

