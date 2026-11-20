import { Link } from "react-router-dom";

import { useI18n } from "@/i18n";

export default function Footer() {
  const { t } = useI18n();

  return (
    <footer className="bg-brand-dark text-white">
      <div className="page-container grid gap-8 py-10 md:grid-cols-3">
        <div className="space-y-2">
          <div className="flex items-center gap-2 font-semibold">
            <img src="/logo.png" alt="" className="h-7 w-auto object-contain" />
            <span className="text-lg font-bold tracking-tight">LUMI</span>
          </div>
          <p className="text-sm text-white/80">
            {t("footer.tagline")}
          </p>
        </div>

        <nav className="flex flex-col gap-2 text-sm" aria-label="Site">
          <Link to="/" className="text-white/80 hover:text-white">{t("nav.home")}</Link>
          <Link to="/about" className="text-white/80 hover:text-white">{t("nav.about")}</Link>
          <Link to="/energyhub" className="text-white/80 hover:text-white">{t("nav.energyHub")}</Link>
          <Link to="/ecosim" className="text-white/80 hover:text-white">{t("nav.ecosim")}</Link>
        </nav>

        <nav className="flex flex-col gap-2 text-sm" aria-label="Legal">
          <Link to="/terms" className="text-white/80 hover:text-white">{t("footer.terms")}</Link>
          <Link to="/privacy" className="text-white/80 hover:text-white">{t("footer.privacy")}</Link>
          <a
            href="mailto:alexanderjonsolis0401@gmail.com"
            className="text-white/80 hover:text-white"
          >
            {t("footer.contact")}
          </a>
        </nav>
      </div>

      <div className="page-container border-t border-white/15 pb-8 pt-6 text-center text-xs text-white/70">
        {t("footer.copyright", { year: new Date().getFullYear() })}
      </div>
    </footer>
  );
}
