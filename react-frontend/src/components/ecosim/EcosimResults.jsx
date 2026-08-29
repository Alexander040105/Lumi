import { useState } from "react";
import { useI18n } from "@/i18n";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Zap, TreePine, Sun, Wind, Droplets, Flame,
  CheckCircle, AlertTriangle, ChevronDown, ChevronUp,
  TrendingUp,
} from "lucide-react";
import InterpretationBadge, { getRating } from "@/components/shared/InterpretationBadge";
import NextStepList from "@/components/shared/NextStepList";
import Markdown from "@/components/shared/Markdown";
import ProviderRecommendations from "./ProviderRecommendations";

const formatNumber = (value, digits = 0) =>
  new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value ?? 0);
const formatCurrency = (value) =>
  new Intl.NumberFormat("en-PH", { style: "currency", currency: "PHP", maximumFractionDigits: 0 }).format(value ?? 0);

const sourceMeta = {
  Solar: { icon: Sun, iconColor: "text-foreground", bg: "bg-warning/10", bar: "bg-warning", name: "Solar" },
  Wind: { icon: Wind, iconColor: "text-foreground", bg: "bg-chart-wind/10", bar: "bg-chart-wind", name: "Wind" },
  Hydro: { icon: Droplets, iconColor: "text-foreground", bg: "bg-chart-hydro/10", bar: "bg-chart-hydro", name: "Hydro" },
  Hydropower: { icon: Droplets, iconColor: "text-foreground", bg: "bg-chart-hydro/10", bar: "bg-chart-hydro", name: "Hydro" },
  Geothermal: { icon: Flame, iconColor: "text-foreground", bg: "bg-chart-geothermal/10", bar: "bg-chart-geothermal", name: "Geothermal" },
};

const sourceDisplayName = (source) => (source === "Hydropower" ? "Hydro" : source);

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

export default function EcosimResults({ result, aiLoading = false }) {
  const { t } = useI18n();
  const [showDetails, setShowDetails] = useState(false);
  if (!result) return null;

  const HOME_SOURCES = ["Solar", "Wind", "Hydro"];
  const rawRecommended = result.recommended_source || "";
  const isGeothermalRec = rawRecommended === "Geothermal";
  const fallbackRec = isGeothermalRec
    ? (result.options || [])
        .filter((o) => HOME_SOURCES.includes(o.source))
        .sort((a, b) => (b.monthly_output || 0) - (a.monthly_output || 0))[0] ||
      (result.options || [])[0] ||
      {}
    : null;
  const rec = fallbackRec || result.options?.find((o) => o.source === rawRecommended) || {};
  const recSource = rec.source || rawRecommended;
  const recDisplay = sourceDisplayName(recSource);
  const recScore = rec.generation_score ?? rec.suitability_score ?? 0;
  const recLabel = getRating(recScore, 100);
  const RecIcon = sourceMeta[recSource]?.icon || Zap;

  const climate = result.climate || {};
  const sInfo = solarInfo(climate.avg_allsky_sfc_sw_dwn, t);
  const wInfo = windInfo(climate.avg_ws10m, t);
  const hInfo = hydroInfo(result.renewable_energy_results?.hydro_output?.hydro_score, t);
  const gInfo = geoInfo(result.renewable_energy_results?.geothermal_output?.suitability_score, t);
  const recInfo = { Solar: sInfo, Wind: wInfo, Hydro: hInfo, Geothermal: gInfo }[recDisplay];

  const climateValue = (() => {
    if (recDisplay === "Solar") {
      const v = climate.avg_allsky_sfc_sw_dwn;
      return v != null ? `${v.toFixed(2)} kWh/m²/day` : "—";
    }
    if (recDisplay === "Wind") {
      const v = climate.avg_ws10m;
      return v != null ? `${v.toFixed(2)} m/s` : "—";
    }
    if (recDisplay === "Hydro") {
      const v = result.renewable_energy_results?.hydro_output?.hydro_score;
      return v != null ? `${v.toFixed(0)}` : "—";
    }
    const v = result.renewable_energy_results?.geothermal_output?.suitability_score;
    return v != null ? `${v.toFixed(0)}` : "—";
  })();

  const bill = result.monthly_bill || 0;
  const cons = result.monthly_consumption_kwh || 0;
  const userCons = result.user_consumption_kwh ?? cons;
  const effectiveCons = result.effective_consumption_kwh ?? cons;
  const rate = cons > 0 ? bill / cons : 0;
  const coverage = cons > 0 ? (rec.estimated_generation_kwh / cons) * 100 : 0;



  return (
    <div className="space-y-6">
      {result.input_warning && (
        <div className="rounded-lg border border-warning bg-warning/10 p-4 flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-warning shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-sm">{t("ecosim.results.inputWarning.title")}</p>
            <p className="text-sm text-muted-foreground">
              {t("ecosim.results.inputWarning.body", { entered: userCons.toFixed(0), effective: effectiveCons.toFixed(0) })}
            </p>
          </div>
        </div>
      )}

      {/* Hero Recommendation */}
      <div className={`rounded-2xl border-2 ${recLabel.border || "border-primary/30"} ${recLabel.bg || "bg-secondary"} p-6 md:p-8`}>
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge className={recLabel.color || "bg-primary text-primary-foreground"}>{t("ecosim.results.bestMatch", { match: t("common.ratings." + (recLabel.label || "excellent").toLowerCase()) })}</Badge>
            </div>
            <h2 className="text-2xl md:text-3xl font-bold text-foreground">
              <span className="inline-flex items-center gap-2">
                <RecIcon className="h-8 w-8" />
                {t("ecosim.results.isBestFor", { source: t("ecosim.results.sources." + recDisplay) })}
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
            <p className="text-2xl font-bold">
              {formatNumber(rec.estimated_generation_kwh, 0)} <span className="text-base font-normal text-muted-foreground">kWh/month</span>
            </p>
            {result.remaining_anonymous_requests !== undefined && result.remaining_anonymous_requests !== null && (
              <p className="text-xs text-muted-foreground mt-1">
                {t("ecosim.results.anonymousQuota", { remaining: result.remaining_anonymous_requests })}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Quick Benefits */}
      <div className="grid gap-4 md:grid-cols-2">
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
            {t("ecosim.results.whyRecommended.title", { source: t("ecosim.results.sources." + recDisplay) })}
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
                {t(
                  recInfo?.level === "poor"
                    ? "ecosim.results.whyRecommended.climateAdvantageTextPoor"
                    : "ecosim.results.whyRecommended.climateAdvantageText",
                  {
                    source: t("ecosim.results.sources." + recDisplay),
                    level: recInfo?.label?.toLowerCase(),
                    value: climateValue,
                  }
                )}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI Analysis */}
      {(aiLoading || result.ai_analysis) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">AI Analysis</CardTitle>
            <CardDescription>
              {aiLoading && !result.ai_analysis
                ? "Analyzing your results with AI..."
                : "AI-generated insight for this location."}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            {aiLoading && !result.ai_analysis && (
              <div className="h-2 w-24 rounded bg-muted animate-pulse" />
            )}
            {result.ai_analysis?.summary && (
              <Markdown className="text-sm text-muted-foreground leading-relaxed">
                {result.ai_analysis.summary}
              </Markdown>
            )}
            {aiLoading && result.ai_analysis?.error && (
              <p className="text-xs text-muted-foreground">Full analysis is still being generated and will appear here shortly.</p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Renewable Potential Comparison */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t("ecosim.results.potentialTitle")}</CardTitle>
          <CardDescription>{t("ecosim.results.potentialDescription")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {[
            { source: "Solar", info: sInfo, output: result.renewable_energy_results?.solar_output },
            { source: "Wind", info: wInfo, output: result.renewable_energy_results?.wind_output },
            { source: "Hydro", info: hInfo, output: result.renewable_energy_results?.hydro_output },
            { source: "Geothermal", info: gInfo, output: result.renewable_energy_results?.geothermal_output, referenceOnly: true },
          ].map((item) => {
            if (result.mode === "province" && item.source === "Geothermal") {
              return null;
            }
            const isRec = item.source === recDisplay;
            const meta = sourceMeta[item.source];
            const optionSource = item.source === "Hydro" ? "Hydropower" : item.source;
            const option = result.options?.find((o) => o.source === optionSource) || {};
            const isUtility = item.referenceOnly;
            const scoreVal = isUtility
              ? (item.output?.suitability_score || 0)
              : (option.generation_score ?? 0);
            const outputKwh = isUtility
              ? (item.output?.annual_energy_gwh ? (item.output.annual_energy_gwh * 1_000_000) / 12 : 0)
              : (option.monthly_output || 0);
            const rating = getRating(scoreVal, 100);
            const sourceAnalysis = result.ai_analysis?.renewable_analysis?.[item.source.toLowerCase()] || item.info.desc;
            return (
              <div key={item.source} className={`flex items-start gap-4 p-3 rounded-lg border ${isRec ? "border-primary/30 bg-secondary/50" : ""}`}>
                <div className={`shrink-0 w-10 h-10 rounded-full ${meta.bg} flex items-center justify-center`}>
                  <meta.icon className={`h-5 w-5 ${meta.iconColor}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold">{t("ecosim.results.sources." + item.source)}</span>
                    {isRec && <Badge className="bg-primary text-primary-foreground text-xs">{t("ecosim.results.recommended")}</Badge>}
                    {item.referenceOnly && <Badge className="bg-muted text-muted-foreground text-xs">{t("ecosim.results.referenceOnly")}</Badge>}
                    {!isRec && <Badge className={`${rating.color} text-xs`}>{item.info.label}</Badge>}
                  </div>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    {isUtility
                      ? `${formatNumber(outputKwh, 0)} kWh/month (${t("ecosim.results.utilityScaleNote")})`
                      : `${formatNumber(outputKwh, 0)} kWh/month`}
                  </p>
                  {sourceAnalysis && (
                    <details className="mt-2 group">
                      <summary className="text-xs text-foreground cursor-pointer list-none flex items-center gap-1 marker:hidden">
                        <span className="underline decoration-dotted">{t("ecosim.results.aiExplanation")}</span>
                        <ChevronDown className="h-3 w-3 group-open:rotate-180 transition-transform" />
                      </summary>
                      <div className="mt-1 text-xs text-muted-foreground leading-relaxed border-l-2 border-muted pl-2">
                        <Markdown>{sourceAnalysis}</Markdown>
                      </div>
                    </details>
                  )}
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>

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

      {/* Provider Recommendations */}
      <ProviderRecommendations municipalityName={result.municipality} provinceName={result.province || result.municipality} />

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
          <NextStepList steps={t("ecosim.results.nextStepsList." + recDisplay)} />
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
                const title = key === "geothermal" ? "Geothermal" : key.charAt(0).toUpperCase() + key.slice(1);
                const meta = sourceMeta[title] || sourceMeta.Solar;
                const isUtility = key === "geothermal";
                const sourceAnalysis = result.ai_analysis?.renewable_analysis?.[key];
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
                      <div className="flex justify-between"><span className="text-muted-foreground">{t("ecosim.results.technical.annual")}</span><span className="font-medium">{formatNumber(data.annual_solar_output || data.annual_wind_output_kwh || data.annual_hydro_output || data.annual_energy_kwh, 0)} kWh</span></div>
                      {sourceAnalysis && (
                        <details className="mt-2 group">
                          <summary className="text-xs text-foreground cursor-pointer list-none flex items-center gap-1 marker:hidden">
                            <span className="underline decoration-dotted">{t("ecosim.results.aiExplanation")}</span>
                            <ChevronDown className="h-3 w-3 group-open:rotate-180 transition-transform" />
                          </summary>
                          <p className="mt-1 text-xs text-muted-foreground leading-relaxed border-l-2 border-muted pl-2">
                            {sourceAnalysis}
                          </p>
                        </details>
                      )}
                      {isUtility && data.citation && (
                        <p className="text-xs text-muted-foreground mt-2 leading-snug">{data.citation}</p>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}

          {/* Scenario comparison hidden until financial modeling is reliable */}
        </div>
      )}
    </div>
  );
}
