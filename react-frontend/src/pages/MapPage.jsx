import { useI18n } from "@/i18n";
import MapPanel from "../components/MapPanel";
import CoverageDashboard from "../components/CoverageDashboard";

export default function MapPage() {
  const { t } = useI18n();

  return (
    <section className="container mx-auto px-4 py-8 space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-bold">{t("map.title")}</h1>
        <p className="text-muted-foreground">
          {t("map.description")}
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <MapPanel />
        </div>
        <div>
          <CoverageDashboard />
        </div>
      </div>
    </section>
  );
}
