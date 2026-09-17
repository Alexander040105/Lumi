import { Link } from "react-router-dom";

import { useI18n } from "@/i18n";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  const { t } = useI18n();

  return (
    <section className="page-container stack">
      <div className="space-y-2">
        <h1>{t("notFound.title")}</h1>
        <p>{t("notFound.description")}</p>
      </div>
      <div>
        <Button variant="outline" size="sm" asChild>
          <Link to="/">{t("notFound.goHome")}</Link>
        </Button>
      </div>
    </section>
  );
}
