import { Button } from "@/components/ui/button";
import { useI18n } from "@/i18n";

export default function LanguageToggle() {
  const { t, locale, setLocale } = useI18n();

  return (
    <div
      className="inline-flex items-center rounded-full border border-border bg-background p-0.5"
      role="group"
      aria-label={t("common.language")}
    >
      <Button
        variant={locale === "en" ? "default" : "ghost"}
        size="sm"
        className="h-7 rounded-full px-2.5 text-xs font-semibold"
        onClick={() => setLocale("en")}
        aria-pressed={locale === "en"}
      >
        EN
      </Button>
      <Button
        variant={locale === "fil" ? "default" : "ghost"}
        size="sm"
        className="h-7 rounded-full px-2.5 text-xs font-semibold"
        onClick={() => setLocale("fil")}
        aria-pressed={locale === "fil"}
      >
        FIL
      </Button>
    </div>
  );
}
