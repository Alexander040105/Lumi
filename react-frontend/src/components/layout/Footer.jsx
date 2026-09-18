import { Link } from "react-router-dom";
import { Sun } from "lucide-react";

import { useI18n } from "@/i18n";

export default function Footer() {
  const { t } = useI18n();

  return (
    <footer className="border-t bg-background/95 py-8">
      <div className="page-container grid gap-6 md:grid-cols-3">
        <div className="space-y-2">
          <div className="flex items-center gap-2 font-semibold">
            <Sun className="h-5 w-5 text-primary" />
            <span>LUMI</span>
          </div>
          <p className="text-sm text-muted-foreground">
            {t("footer.tagline")}
          </p>
        </div>

        <nav className="flex flex-col gap-2 text-sm" aria-label="Site">
          <Link to="/" className="hover:text-primary">{t("nav.home")}</Link>
          <Link to="/about" className="hover:text-primary">{t("nav.about")}</Link>
          <Link to="/energyhub" className="hover:text-primary">{t("nav.energyHub")}</Link>
          <Link to="/ecosim" className="hover:text-primary">{t("nav.ecosim")}</Link>
        </nav>

        <nav className="flex flex-col gap-2 text-sm" aria-label="Legal">
          <Link to="/terms" className="hover:text-primary">{t("footer.terms")}</Link>
          <Link to="/privacy" className="hover:text-primary">{t("footer.privacy")}</Link>
          <a
            href="mailto:alexanderjonsolis0401@gmail.com"
            className="hover:text-primary"
          >
            {t("footer.contact")}
          </a>
        </nav>
      </div>

      <div className="page-container mt-8 text-center text-xs text-muted-foreground">
        {t("footer.copyright", { year: new Date().getFullYear() })}
      </div>
    </footer>
  );
}
