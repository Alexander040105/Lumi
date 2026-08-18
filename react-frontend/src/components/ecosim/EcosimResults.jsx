import { useState } from "react";
import { useI18n } from "@/i18n";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Zap, PiggyBank, TreePine, ArrowRight, Sun, Wind, Droplets, Flame,
  CheckCircle, AlertTriangle, HelpCircle, ChevronDown, ChevronUp,
  ExternalLink, Building2, MapPin, TrendingUp, Wallet,
} from "lucide-react";
import InterpretationBadge, { getRating, getStars } from "@/components/shared/InterpretationBadge";
import HelpTooltip from "@/components/shared/HelpTooltip";
import NextStepList from "@/components/shared/NextStepList";
import ProviderRecommendations from "./ProviderRecommendations";
import EcosimBOM from "./EcosimBOM";

const formatNumber = (value, digits = 0) =>
  new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value ?? 0);
const formatCurrency = (value) =>
  new Intl.NumberFormat("en-PH", { style: "currency", currency: "PHP", maximumFractionDigits: 0 }).format(value ?? 0);

const sourceMeta = {
  Solar: { icon: Sun, iconColor: "text-foreground", bg: "bg-warning/10", bar: "bg-warning", name: "Solar" },
  Wind: { icon: Wind, iconColor: "text-foreground", bg: "bg-chart-wind/10", bar: "bg-chart-wind", name: "Wind" },
  Hydro: { icon: Droplets, iconColor: "text-foreground", bg: "bg-chart-hydro/10", bar: "bg-chart-hydro", name: "Hydro" },
  Geothermal: { icon: Flame, iconColor: "text-foreground", bg: "bg-chart-geothermal/10", bar: "bg-chart-geothermal", name: "Geothermal" },
};

function solarInfo(ghi, t) {
  if (ghi >= 5.0) return { level: "excellent", label: t("common.ratings.excellent"), desc: t("ecosim.results.info.Solar.excellent") };
  if (ghi >= 4.0) return { level: "good", label: t("common.ratings.good"), desc: t("ecosim.results.info.Solar.good") };
  if (ghi >= 3.0) return { level: "moderate", label: t("common.ratings.moderate"), desc: t("ecosim.results.info.Solar.moderate") };
  return { level: "fair", label: t("common.ratings.fair"), desc: t("ecosim.results.info.Solar.fair") };
}
function windInfo(ws, t) {
  if (ws >= 5.0) return { level: "excellent", label: t("common.ratings.excellent"), desc: t("ecosim.results.info.Wind.excellent") };
  if (ws >= 3.5) return { level: "good", label: t("common.ratings.good"), desc: t("ecosim.results.info.Wind.good") };
  if (ws >= 2.5) return { level: "moderate", label: t("common.ratings.moderate"), desc: t("ecosim.results.info.Wind.moderate") };
  return { level: "poor", label: t("common.ratings.poor"), desc: t("ecosim.results.info.Wind.poor") };
}
function hydroInfo(score, t) {
  if (score >= 70) return { level: "good", label: t("common.ratings.good"), desc: t("ecosim.results.info.Hydro.good") };
  if (score >= 40) return { level: "moderate", label: t("common.ratings.moderate"), desc: t("ecosim.results.info.Hydro.moderate") };
  return { level: "fair", label: t("common.ratings.fair"), desc: t("ecosim.results.info.Hydro.fair") };
}
function geoInfo(score, t) {
  if (score >= 70) return { level: "good", label: t("common.ratings.good"), desc: t("ecosim.results.info.Geothermal.good") };
  return { level: "limited", label: t("common.ratings.limited"), desc: t("ecosim.results.info.Geothermal.limited") };
}

export default function EcosimResults({ result, productRecs, productLoading }) {
  const { t } = useI18n();
  const [showDetails, setShowDetails] = useState(false);
  if (!result) return null;

  const HOME_SOURCES = ["Solar", "Wind", "Hydro"];
  const rawRecommended = result.recommended_source || "";
  const isGeothermalRec = rawRecommended === "Geothermal";
  const fallbackRec = isGeothermalRec
    ? (result.options || [])
        .filter((o) => HOME_SOURCES.includes(o.source))
        .sort((a, b) => (b.suitability_score || 0) - (a.suitability_score || 0))[0] ||
      (result.options || [])[0] ||
      {}
    : null;
  const rec = fallbackRec || result.options?.find((o) => o.source === rawRecommended) || {};
  const recSource = rec.source || rawRecommended;
  const recScore = rec.suitability_score || 0;
  const recLabel = getRating(recScore, 100);
  const RecIcon = sourceMeta[recSource]?.icon || Zap;

  const climate = result.climate || {};
  const sInfo = solarInfo(climate.avg_allsky_sfc_sw_dwn, t);
  const wInfo = windInfo(climate.avg_ws10m, t);
  const hInfo = hydroInfo(result.renewable_energy_results?.hydro_output?.hydro_score, t);
  const gInfo = geoInfo(result.renewable_energy_results?.geothermal_output?.suitability_score, t);

  const bill = result.monthly_bill || 0;
  const cons = result.monthly_consumption_kwh || 0;
  const rate = cons > 0 ? bill / cons : 0;
  const netBill = result.comparison?.renewable_monthly_bill || 0;
  const savings = bill - netBill;
  const savingsPct = bill > 0 ? (savings / bill) * 100 : 0;
  const coverage = cons > 0 ? (rec.estimated_generation_kwh / cons) * 100 : 0;

  const maxGen = Math.max(...(result.options || []).map((o) => o.estimated_generation_kwh || 0), 1);

  return (
    <div className="space-y-6">
      {/* Hero Recommendation */}
      <div className={`rounded-2xl border-2 ${recLabel.border || "border-primary/30"} ${recLabel.bg || "bg-secondary"} p-6 md:p-8`}>
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge className={recLabel.color || "bg-primary text-primary-foreground"}>{t("ecosim.results.bestMatch", { match: t("common.ratings." + (recLabel.label || "excellent").toLowerCase()) })}</Badge>
              <span className="text-2xl tracking-widest">{getStars(recScore, 100)}</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-bold text-foreground">
              <span className="inline-flex items-center gap-2">
                <RecIcon className="h-8 w-8" />
                {t("ecosim.results.isBestFor", { source: t("ecosim.results.sources." + recSource) })}
              </span>
            </h2>
            <p className="text-muted-foreground max-w-2xl leading-relaxed">
              {isGeothermalRec
                ? t("ecosim.results.geothermalNote", { source: t("ecosim.results.sources." + recSource) })
                : result.explanation}
            </p>
            {isGeothermalRec && (
              <p className="mt-2 text-xs text-muted-foreground bg-muted/50 border rounded-md p-2 inline-block">
                {t("ecosim.results.geothermalReference")}
              </p>
            )}
          </div>
          <div className="shrink-0 text-center md:text-right">
            <p className="text-sm text-muted-foreground">{t("ecosim.results.suitabilityScore")}</p>
            <p className="text-4xl font-bold">
              {formatNumber(recScore, 0)}<span className="text-lg text-muted-foreground">/100</span>
            </p>
          </div>
        </div>
      </div>

      {/* Quick Benefits */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-l-4 border-l-primary">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 text-primary mb-1">
              <PiggyBank className="h-4 w-4" />
              <span className="text-sm font-medium">{t("ecosim.results.benefits.monthlySavings")}</span>
            </div>
            <p className="text-2xl font-bold">{formatCurrency(savings)}</p>
            <p className="text-xs text-muted-foreground mt-1">{t("ecosim.results.benefits.offYourCurrentBill", { pct: savingsPct.toFixed(0) })}</p>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-chart-wind">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 text-primary mb-1">
              <Zap className="h-4 w-4" />
              <span className="text-sm font-medium">{t("ecosim.results.benefits.energyCoverage")}</span>
            </div>
            <p className="text-2xl font-bold">{formatNumber(coverage, 0)}%</p>
            <p className="text-xs text-muted-foreground mt-1">{t("ecosim.results.benefits.ofYourMonthlyConsumption")}</p>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-warning">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 text-foreground mb-1">
              <ArrowRight className="h-4 w-4" />
              <span className="text-sm font-medium">{t("ecosim.results.benefits.paybackPeriod")}</span>
            </div>
            <p className="text-2xl font-bold">{result.payback_years ? `${formatNumber(result.payback_years, 1)} yrs` : t("common.notAvailable")}</p>
            <p className="text-xs text-muted-foreground mt-1">{t("ecosim.results.benefits.timeToBreakEven")}</p>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-primary">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 text-primary mb-1">
              <TreePine className="h-4 w-4" />
              <span className="text-sm font-medium">{t("ecosim.results.benefits.co2Reduction")}</span>
            </div>
            <p className="text-2xl font-bold">{formatNumber(result.carbon_reduction)} kg</p>
            <p className="text-xs text-muted-foreground mt-1">{t("ecosim.results.benefits.lessCarbonPerMonth")}</p>
          </CardContent>
        </Card>
      </div>

      {/* Why Recommended */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-primary" />
            {t("ecosim.results.whyRecommended.title", { source: t("ecosim.results.sources." + recSource) })}
          </CardTitle>
          <CardDescription>{t("ecosim.results.whyRecommended.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-lg border bg-muted/30 p-4">
              <p className="font-semibold mb-1">{t("ecosim.results.whyRecommended.yourLocation")}</p>
              <p className="text-sm text-muted-foreground">{t("ecosim.results.whyRecommended.locationText", { municipality: result.municipality, id: result.municipality_id })}</p>
              <p className="text-sm mt-2">
                {t("ecosim.results.whyRecommended.usageText", { consumption: cons.toFixed(0), bill: formatCurrency(bill), rate: formatCurrency(rate) })}
              </p>
            </div>
            <div className="rounded-lg border bg-muted/30 p-4">
              <p className="font-semibold mb-1">{t("ecosim.results.whyRecommended.climateAdvantage")}</p>
              <p className="text-sm text-muted-foreground">
                {t("ecosim.results.climateTemplates." + recSource, {
                  value: recSource === "Hydro"
                    ? result.renewable_energy_results?.hydro_output?.hydro_score?.toFixed(0)
                    : (recSource === "Solar" ? climate.avg_allsky_sfc_sw_dwn?.toFixed(2) : climate.avg_ws10m?.toFixed(2)),
                  desc: { Solar: sInfo.desc, Wind: wInfo.desc, Hydro: hInfo.desc, Geothermal: gInfo.desc }[recSource]
                })}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Renewable Potential Comparison */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t("ecosim.results.potentialTitle")}</CardTitle>
          <CardDescription>{t("ecosim.results.potentialDescription")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {[
            { source: "Solar", info: sInfo, score: climate.avg_allsky_sfc_sw_dwn, max: 6, unit: "kWh/m²/day", output: result.renewable_energy_results?.solar_output },
            { source: "Wind", info: wInfo, score: climate.avg_ws10m, max: 6, unit: "m/s", output: result.renewable_energy_results?.wind_output },
            { source: "Hydro", info: hInfo, score: result.renewable_energy_results?.hydro_output?.hydro_score, max: 100, unit: "score", output: result.renewable_energy_results?.hydro_output },
            { source: "Geothermal", info: gInfo, score: result.renewable_energy_results?.geothermal_output?.suitability_score, max: 100, unit: "score", output: result.renewable_energy_results?.geothermal_output, referenceOnly: true },
          ].map((item) => {
            const isRec = item.source === recSource;
            const meta = sourceMeta[item.source];
            const scoreVal = parseFloat(item.score) || 0;
            const rating = getRating(scoreVal, item.max);
            const stars = getStars(scoreVal, item.max);
            const pct = maxGen > 0 ? ((item.output?.estimated_generation_kwh || item.output?.monthly_energy_kwh || item.output?.monthly_solar_output || 0) / maxGen) * 100 : 0;
            return (
              <div key={item.source} className={`flex items-center gap-4 p-3 rounded-lg border ${isRec ? "border-primary/30 bg-secondary/50" : ""}`}>
                <div className={`shrink-0 w-10 h-10 rounded-full ${meta.bg} flex items-center justify-center`}>
                  <meta.icon className={`h-5 w-5 ${meta.iconColor}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold">{t("ecosim.results.sources." + item.source)}</span>
                    {isRec && <Badge className="bg-primary text-primary-foreground text-xs">{t("ecosim.results.recommended")}</Badge>}
                    {item.referenceOnly && <Badge className="bg-muted text-muted-foreground text-xs">{t("ecosim.results.referenceOnly")}</Badge>}
                    <Badge className={`${rating.color} text-xs`}>{item.info.label}</Badge>
                    <span className="tracking-widest text-sm">{stars}</span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    {item.score?.toFixed ? item.score.toFixed(2) : item.score} {item.unit} — {item.info.desc}
                  </p>
                  {pct > 0 && (
                    <div className="mt-2 h-2 rounded-full bg-muted overflow-hidden">
                      <div className={`h-2 rounded-full ${meta.bar} transition-all`} style={{ width: `${Math.min(pct, 100)}%` }} />
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>

      {/* Financial Impact */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Wallet className="h-5 w-5 text-primary" />
            {t("ecosim.results.financial.title")}
          </CardTitle>
          <CardDescription>{t("ecosim.results.financial.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-xl border bg-destructive/10 p-5 text-center">
              <p className="text-sm text-foreground font-medium">{t("ecosim.results.financial.currentBill")}</p>
              <p className="text-3xl font-bold text-foreground mt-1">{formatCurrency(bill)}</p>
              <p className="text-xs text-foreground mt-1">{t("ecosim.results.financial.used", { consumption: cons.toFixed(0) })}</p>
            </div>
            <div className="rounded-xl border bg-secondary p-5 text-center">
              <p className="text-sm text-primary font-medium">{t("ecosim.results.financial.newBill")}</p>
              <p className="text-3xl font-bold text-primary mt-1">{formatCurrency(netBill)}</p>
              <p className="text-xs text-primary mt-1">{t("ecosim.results.financial.afterOffset", { source: t("ecosim.results.sources." + recSource).toLowerCase() })}</p>
            </div>
            <div className="rounded-xl border bg-warning/10 p-5 text-center">
              <p className="text-sm text-foreground font-medium">{t("ecosim.results.financial.monthlySavings")}</p>
              <p className="text-3xl font-bold text-foreground mt-1">{formatCurrency(savings)}</p>
              <p className="text-xs text-warning mt-1">{t("ecosim.results.financial.reduction", { pct: savingsPct.toFixed(0) })}</p>
            </div>
          </div>
          <div className="rounded-lg border bg-muted/30 p-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-muted-foreground">{t("ecosim.results.financial.installationCost")}</p>
                <p className="text-xl font-semibold">{formatCurrency(result.installation_cost)}</p>
                <p className="text-xs text-muted-foreground mt-1">{t("ecosim.results.financial.costNote")}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{t("ecosim.results.financial.payback")}</p>
                <p className="text-xl font-semibold">
                  {result.payback_years ? t("ecosim.results.financial.years", { years: formatNumber(result.payback_years, 1) }) : t("ecosim.results.financial.notCalculable")}
                </p>
                <p className="text-xs text-muted-foreground mt-1">{t("ecosim.results.financial.paybackNote")}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      {/* Bill of Materials */}
      <EcosimBOM result={result} />

      {/* Meralco Rate */}
      {result.meralco_rate && result.meralco_rate.rate_php_per_kwh && (
        <Card>
          <CardHeader>
            <CardTitle>{t("ecosim.results.meralco.title")}</CardTitle>
            <CardDescription>{t("ecosim.results.meralco.description")}</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-3">
            <div>
              <p className="text-sm text-muted-foreground">{t("ecosim.results.meralco.generationCharge", { year: result.meralco_rate.year })}</p>
              <p className="text-lg font-semibold">{formatCurrency(result.meralco_rate.rate_php_per_kwh)} / kWh</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{t("ecosim.results.meralco.yourEffectiveRate")}</p>
              <p className="text-lg font-semibold">{formatCurrency(rate)} / kWh</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{t("ecosim.results.meralco.customerClass")}</p>
              <p className="text-lg font-semibold">{result.meralco_rate.customer_class}</p>
            </div>
          </CardContent>
          <p className="px-6 pb-4 text-xs text-muted-foreground">{result.meralco_rate.note}</p>
        </Card>
      )}

      {/* Product Recommendations */}
      {(productRecs || productLoading) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Zap className="h-5 w-5 text-warning" />
              {t("ecosim.results.productRecs.title", { source: t("ecosim.results.sources." + recSource) })}
            </CardTitle>
            <CardDescription>{t("ecosim.results.productRecs.description")}</CardDescription>
          </CardHeader>
          <CardContent>
            {productLoading && <div className="h-24 animate-pulse rounded bg-muted" />}
            {!productLoading && productRecs?.items?.length > 0 && (
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {productRecs.items.map((item) => (
                  <a key={item.url || item.product_name} href={item.url} target="_blank" rel="noopener noreferrer" className="rounded-lg border bg-card p-4 shadow-sm hover:shadow-md transition-shadow">
                    <p className="text-sm font-medium line-clamp-2">{item.product_name}</p>
                    <p className="mt-1 text-sm font-semibold text-primary">{item.currency} {item.price_value?.toLocaleString?.() || item.price_value}</p>
                    <p className="text-xs text-muted-foreground capitalize">{item.source_site} · {item.energy_subcategory}</p>
                    {item.ratings && <p className="text-xs text-foreground mt-1">{item.ratings}</p>}
                  </a>
                ))}
              </div>
            )}
            {!productLoading && productRecs && (!productRecs.items || productRecs.items.length === 0) && (
              <div className="rounded-lg border bg-muted/30 p-4 text-sm text-muted-foreground">
                <AlertTriangle className="h-4 w-4 inline mr-1 text-warning" />
                {t("ecosim.results.productRecs.none", { source: recSource.toLowerCase() })}
              </div>
            )}
            {productRecs?.note && <p className="mt-2 text-xs text-muted-foreground">{t("ecosim.results.productRecs.note", { note: productRecs.note })}</p>}
          </CardContent>
        </Card>
      )}

      {/* Provider Recommendations */}
      <ProviderRecommendations municipalityName={result.municipality} provinceName={result.municipality} />

      {/* Next Steps */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            {t("ecosim.results.nextSteps.title")}
          </CardTitle>
          <CardDescription>{t("ecosim.results.nextSteps.description")}</CardDescription>
        </CardHeader>
        <CardContent>
          <NextStepList steps={t("ecosim.results.nextStepsList." + recSource)} />
        </CardContent>
      </Card>

      {/* Technical Details Toggle */}
      <div className="text-center">
        <Button variant="ghost" size="sm" onClick={() => setShowDetails(!showDetails)} className="text-muted-foreground hover:text-foreground">
          {showDetails ? <ChevronUp className="h-4 w-4 mr-1" /> : <ChevronDown className="h-4 w-4 mr-1" />}
          {showDetails ? t("ecosim.results.technical.hide") : t("ecosim.results.technical.show")}
        </Button>
      </div>

      {showDetails && (
        <div className="space-y-6">
          {/* Climate data */}
          {climate && (
            <Card>
              <CardHeader>
                <CardTitle>{t("ecosim.results.technical.climateData")}</CardTitle>
                <CardDescription>{t("ecosim.results.technical.climateDescription")}</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-3 md:grid-cols-3 lg:grid-cols-4">
                {[
                  { label: t("ecosim.results.climateLabels.temperature"), value: climate.avg_t2m, unit: "°C", digits: 1 },
                  { label: t("ecosim.results.climateLabels.humidity"), value: climate.avg_rh2m, unit: "%", digits: 1 },
                  { label: t("ecosim.results.climateLabels.rainfall"), value: climate.avg_prectotcorr, unit: "mm/day", digits: 1 },
                  { label: t("ecosim.results.climateLabels.solarIrradiance"), value: climate.avg_allsky_sfc_sw_dwn, unit: "kWh/m²/day", digits: 2 },
                  { label: t("ecosim.results.climateLabels.windSpeed"), value: climate.avg_ws10m, unit: "m/s", digits: 2 },
                  { label: t("ecosim.results.climateLabels.cloudCoverage"), value: climate.avg_cloud_amt, unit: "%", digits: 1 },
                  { label: t("ecosim.results.climateLabels.surfacePressure"), value: climate.avg_surface_pressure, unit: "kPa", digits: 1 },
                  { label: t("ecosim.results.climateLabels.elevation"), value: climate.elevation, unit: "m", digits: 0 },
                ].map((item) => (
                  <div key={item.label}>
                    <p className="text-sm text-muted-foreground">{item.label}</p>
                    <p className="text-lg font-semibold">{formatNumber(item.value, item.digits)} {item.unit}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Detailed renewable outputs */}
          {result.renewable_energy_results && (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {["solar", "wind", "hydro", "geothermal"].map((key) => {
                const data = result.renewable_energy_results[`${key}_output`];
                if (!data) return null;
                const title = key.charAt(0).toUpperCase() + key.slice(1);
                const meta = sourceMeta[title] || sourceMeta.Solar;
                return (
                  <Card key={key} className={`border-t-4 border-t-${meta.bar.replace("bg-", "")}`}>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-sm">
                        <span className={`inline-block h-3 w-3 rounded-full ${meta.bar}`} />
                        {t("ecosim.results.technical.output", { source: t("ecosim.results.sources." + title) })}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <div className="flex justify-between"><span className="text-muted-foreground">{t("ecosim.results.technical.daily")}</span><span className="font-medium">{formatNumber(data.daily_solar_output || data.daily_energy_kwh || data.daily_hydro_output, 2)} kWh</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">{t("ecosim.results.technical.monthly")}</span><span className="font-medium">{formatNumber(data.monthly_solar_output || data.monthly_energy_kwh || data.monthly_hydro_output, 1)} kWh</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">{t("ecosim.results.technical.annual")}</span><span className="font-medium">{formatNumber(data.annual_solar_output || data.annual_wind_output_kwh || data.annual_hydro_output, 0)} kWh</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">{t("ecosim.results.technical.score")}</span><span className="font-medium">{formatNumber(data.solar_score || data.capacity_factor || data.hydro_score || data.suitability_score, 0)} / 100</span></div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}

          {/* Scenario comparison */}
          {result.comparison && (
            <Card>
              <CardHeader>
                <CardTitle>{t("ecosim.results.technical.scenarioComparison")}</CardTitle>
                <CardDescription>{t("ecosim.results.technical.scenarioDescription")}</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-3 md:grid-cols-2">
                <div className="rounded-lg border bg-destructive/10 p-4">
                  <p className="text-sm font-medium text-foreground">{t("ecosim.results.technical.current")}</p>
                  <p className="text-xl font-bold text-foreground">{formatCurrency(result.comparison.current_monthly_bill)}</p>
                  <p className="text-xs text-foreground">{formatNumber(result.comparison.current_monthly_consumption_kwh)} kWh</p>
                </div>
                <div className="rounded-lg border bg-secondary p-4">
                  <p className="text-sm font-medium text-primary">{t("ecosim.results.technical.withSource", { source: t("ecosim.results.sources." + recSource) })}</p>
                  <p className="text-xl font-bold text-primary">{formatCurrency(result.comparison.renewable_monthly_bill)}</p>
                  <p className="text-xs text-primary">{formatNumber(result.comparison.renewable_monthly_consumption_kwh)} kWh</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
