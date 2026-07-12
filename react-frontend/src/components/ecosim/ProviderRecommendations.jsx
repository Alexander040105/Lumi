import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, MapPin, ExternalLink, Building2 } from "lucide-react";
import providersData from "@/data/providers.json";
import { getRegionFromProvince, getRegionFromMunicipality } from "@/utils/regionMap";

/**
 * ProviderRecommendations — shows DOE-registered solar installers in the user's region.
 */

export default function ProviderRecommendations({ municipalityName, provinceName }) {
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
          <Building2 className="h-5 w-5 text-sky-500" />
          Trusted Solar Installers in Your Region
        </CardTitle>
        <CardDescription>
          These companies are registered with the DOE Solar PV Installer Registry (as of June 2025).
          Always verify current status before hiring.
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
                  <MapPin className="h-4 w-4 text-sky-500 shrink-0 mt-0.5" />
                  <div className="min-w-0">
                    <p className="text-sm font-medium line-clamp-2">{p.name}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{p.type}</p>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2">{p.address}</p>
                <div className="flex items-center justify-between mt-auto pt-1">
                  <span className="text-xs text-slate-500">{p.years}</span>
                  <span className="text-xs text-sky-600 flex items-center gap-1">
                    Visit <ExternalLink className="h-3 w-3" />
                  </span>
                </div>
              </a>
            ))}
          </div>
        ) : (
          <div className="rounded-lg border bg-muted/30 p-4 text-sm text-muted-foreground">
            <AlertTriangle className="h-4 w-4 inline mr-1 text-amber-500" />
            No registered providers found in your region.
            Consider contacting providers in nearby regions, or search online for
            "{municipalityName || provinceName || "your area"} solar installer".
          </div>
        )}
        <p className="mt-3 text-xs text-muted-foreground">
          This registry is solar-focused. Wind, hydro, and geothermal providers are not listed yet.
        </p>
      </CardContent>
    </Card>
  );
}
