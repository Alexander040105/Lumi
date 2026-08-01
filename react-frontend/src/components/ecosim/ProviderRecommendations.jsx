import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, MapPin, ExternalLink, Building2 } from "lucide-react";
import { useI18n } from "@/i18n";
import providersData from "@/data/providers.json";
import { getRegionFromProvince, getRegionFromMunicipality } from "@/utils/regionMap";

/**
 * ProviderRecommendations — shows DOE-registered solar installers in the user's region.
 */

export default function ProviderRecommendations({ municipalityName, provinceName }) {
  const { t } = useI18n();
  // Determine region
  let region = getRegionFromProvince(provinceName) || getRegionFromMunicipality(municipalityName);

  // Fallback: try to extract region from municipality name itself (e.g., "Quezon City" → NCR)
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
          {t("ecosim.providers.title")}
        </CardTitle>
        <CardDescription>
          {t("ecosim.providers.description")}
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
                    {t("ecosim.providers.visit")} <ExternalLink className="h-3 w-3" />
                  </span>
                </div>
              </a>
            ))}
          </div>
        ) : (
          <div className="rounded-lg border bg-muted/30 p-4 text-sm text-muted-foreground">
            <AlertTriangle className="h-4 w-4 inline mr-1 text-warning" />
            {t("ecosim.providers.none", { area: municipalityName || provinceName || t("common.notAvailable") })}
          </div>
        )}
        <p className="mt-3 text-xs text-muted-foreground">
          {t("ecosim.providers.note")}
        </p>
      </CardContent>
    </Card>
  );
}
