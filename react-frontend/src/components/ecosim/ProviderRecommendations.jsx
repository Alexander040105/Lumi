import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertTriangle, MapPin, ExternalLink, Building2, ShieldCheck, Phone, ChevronDown, ChevronUp, Package, Globe } from "lucide-react";
import { useI18n } from "@/i18n";
import providersData from "@/data/providers.json";
import { getRegionFromProvince, getRegionFromMunicipality } from "@/utils/regionMap";
import { matchProviders, normalizeTechnology } from "@/utils/matchProviders";

const VISIBLE_LIMIT = 6;

function providerTechnologies(p) {
  return String(p.technology || "Solar")
    .split("/")
    .map((s) => s.trim());
}

function ProviderCard({ p, visitLabel, verifiedLabel, registryBadgeLabel, retailerBadgeLabel, productsLabel, nationwideLabel }) {
  const isRetailer = p.category === "retailer";
  const className =
    "rounded-lg border bg-card p-4 shadow-sm flex flex-col gap-2";
  const inner = (
    <>
      <div className="flex items-start gap-2">
        <MapPin className="h-4 w-4 text-primary shrink-0 mt-0.5" aria-hidden="true" />
        <div className="min-w-0">
          <p className="text-sm font-medium line-clamp-2">{p.name}</p>
          <p className="text-xs text-muted-foreground mt-0.5">{p.type}</p>
        </div>
      </div>
      <p className="text-xs text-muted-foreground line-clamp-2">{p.address}</p>
      {p.contact && (
        <p className="text-xs text-muted-foreground flex items-center gap-1.5">
          <Phone className="h-3 w-3 shrink-0" aria-hidden="true" />
          <span className="line-clamp-1">{p.contact}</span>
        </p>
      )}
      {isRetailer && p.products && (
        <p className="text-xs text-muted-foreground flex items-center gap-1.5">
          <Package className="h-3 w-3 shrink-0" aria-hidden="true" />
          <span className="line-clamp-2">{productsLabel}: {p.products}</span>
        </p>
      )}
      {isRetailer && p.nationwide && (
        <p className="text-xs text-muted-foreground flex items-center gap-1.5">
          <Globe className="h-3 w-3 shrink-0" aria-hidden="true" />
          <span>{nationwideLabel}</span>
        </p>
      )}
      {isRetailer ? (
        <Badge variant="outline" className="w-fit">
          {retailerBadgeLabel}
        </Badge>
      ) : p.verified ? (
        <Badge className="w-fit gap-1">
          <ShieldCheck className="h-3 w-3" aria-hidden="true" />
          {verifiedLabel}
        </Badge>
      ) : p.registry === "doe-2025" ? (
        <Badge variant="secondary" className="w-fit">
          {registryBadgeLabel}
        </Badge>
      ) : null}
      {!isRetailer && p.verification && (
        <p className="text-[11px] leading-snug text-muted-foreground line-clamp-2">{p.verification}</p>
      )}
      <div className="flex items-center justify-between mt-auto pt-1">
        <span className="text-xs text-muted-foreground">{p.years || ""}</span>
        {p.url && (
          <span className="text-xs text-primary flex items-center gap-1">
            {visitLabel} <ExternalLink className="h-3 w-3" aria-hidden="true" />
          </span>
        )}
      </div>
    </>
  );

  return p.url ? (
    <a
      href={p.url}
      target="_blank"
      rel="noopener noreferrer"
      className={`${className} hover:shadow-md transition-shadow`}
    >
      {inner}
    </a>
  ) : (
    <div className={className}>{inner}</div>
  );
}

function ProviderList({ matched, fallback, showFallbackNotice, cardProps, emptyText, t }) {
  const [showAll, setShowAll] = useState(false);

  const visible = showAll ? matched : matched.slice(0, VISIBLE_LIMIT);
  const displayed = matched.length > 0 ? visible : fallback;

  const shownTechs = new Set(displayed.flatMap(providerTechnologies));

  return (
    <>
      {showFallbackNotice && matched.length === 0 && fallback.length > 0 && (
        <div className="rounded-lg border bg-muted/30 p-4 text-sm text-muted-foreground mb-3">
          <AlertTriangle className="h-4 w-4 inline mr-1 text-warning" aria-hidden="true" />
          {t("ecosim.providers.fallbackTitle")}
        </div>
      )}
      {displayed.length > 0 ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {displayed.map((p, i) => (
            <ProviderCard key={i} p={p} {...cardProps} />
          ))}
        </div>
      ) : (
        <div className="rounded-lg border bg-muted/30 p-4 text-sm text-muted-foreground">
          <AlertTriangle className="h-4 w-4 inline mr-1 text-warning" aria-hidden="true" />
          {emptyText}
        </div>
      )}
      {matched.length > VISIBLE_LIMIT && (
        <div className="mt-3 text-center">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowAll((v) => !v)}
            aria-expanded={showAll}
            className="text-muted-foreground hover:text-foreground"
          >
            {showAll ? (
              <ChevronUp className="h-4 w-4 mr-1" aria-hidden="true" />
            ) : (
              <ChevronDown className="h-4 w-4 mr-1" aria-hidden="true" />
            )}
            {showAll
              ? t("ecosim.providers.showLess")
              : t("ecosim.providers.showAll", { count: matched.length })}
          </Button>
        </div>
      )}
      <div className="mt-3 space-y-1.5 text-xs text-muted-foreground">
        {shownTechs.has("Solar") && <p>{t("ecosim.providers.disclaimerSolar")}</p>}
        {shownTechs.has("Wind") && <p>{t("ecosim.providers.disclaimerWind")}</p>}
        {shownTechs.has("Hydro") && <p>{t("ecosim.providers.disclaimerHydro")}</p>}
        <p>{t("ecosim.providers.note")}</p>
        <p>{t("ecosim.providers.generalNote")}</p>
      </div>
    </>
  );
}

/**
 * ProviderRecommendations — shows verified renewable-energy providers and
 * equipment retailers relevant to the user's region, ranked by the recommended
 * technology, in switchable Providers / Retailers tabs. Nationwide sellers are
 * appended after regional matches.
 */
export default function ProviderRecommendations({ municipalityName, provinceName, recommendedSource }) {
  const { t } = useI18n();

  // Determine region
  let region = getRegionFromProvince(provinceName) || getRegionFromMunicipality(municipalityName);

  // Fallback: try to extract region from municipality name itself (e.g., "Quezon City" → NCR)
  if (!region && municipalityName) {
    region = getRegionFromMunicipality(municipalityName);
  }

  const technology = normalizeTechnology(recommendedSource);
  const providers = matchProviders({ providers: providersData, region, technology, category: "provider" });
  const retailers = matchProviders({ providers: providersData, region, technology, category: "retailer" });

  const area = municipalityName || provinceName || t("common.notAvailable");
  const cardProps = {
    visitLabel: t("ecosim.providers.visit"),
    verifiedLabel: t("ecosim.providers.verified"),
    registryBadgeLabel: t("ecosim.providers.registryBadge"),
    retailerBadgeLabel: t("ecosim.providers.retailerBadge"),
    productsLabel: t("ecosim.providers.productsLabel"),
    nationwideLabel: t("ecosim.providers.nationwide"),
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Building2 className="h-5 w-5 text-primary" aria-hidden="true" />
          {t("ecosim.providers.title")}
        </CardTitle>
        <CardDescription>
          {t("ecosim.providers.description")}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="providers">
          <TabsList>
            <TabsTrigger value="providers">{t("ecosim.providers.tabProviders")}</TabsTrigger>
            <TabsTrigger value="retailers">{t("ecosim.providers.tabRetailers")}</TabsTrigger>
          </TabsList>
          <TabsContent value="providers">
            <ProviderList
              matched={providers.matched}
              fallback={providers.fallback}
              showFallbackNotice
              cardProps={cardProps}
              emptyText={t("ecosim.providers.none", { area })}
              t={t}
            />
          </TabsContent>
          <TabsContent value="retailers">
            <ProviderList
              matched={retailers.matched}
              fallback={[]}
              showFallbackNotice={false}
              cardProps={cardProps}
              emptyText={t("ecosim.providers.noneRetailers", { area })}
              t={t}
            />
            <p className="mt-3 text-xs text-muted-foreground">
              {t("ecosim.providers.retailerDisclaimer")}
            </p>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
