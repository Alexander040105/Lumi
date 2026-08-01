import { createContext, Fragment, useContext, useState, useCallback, useMemo } from "react";
import en from "./en.json";
import fil from "./fil.json";

const DICTIONARIES = { en, fil };

function getByPath(obj, path) {
  return path.split(".").reduce((acc, part) => (acc ? acc[part] : undefined), obj);
}

export const I18nContext = createContext(null);

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
      if (Array.isArray(template) || typeof template !== "string") return template;
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

export function Trans({ k, components = {} }) {
  const { t } = useI18n();
  const template = t(k);
  if (typeof template !== "string") return null;

  const parts = template.split(/(\{\{\w+\}\})/g);
  return parts.map((part, i) => {
    const match = part.match(/^\{\{(\w+)\}\}$/);
    if (match && components[match[1]] !== undefined) {
      return <Fragment key={i}>{components[match[1]]}</Fragment>;
    }
    return <Fragment key={i}>{part}</Fragment>;
  });
}
