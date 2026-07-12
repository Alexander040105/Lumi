import { useState } from "react";
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

const formatNumber = (value, digits = 0) =>
  new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value ?? 0);
const formatCurrency = (value) =>
  new Intl.NumberFormat("en-PH", { style: "currency", currency: "PHP", maximumFractionDigits: 0 }).format(value ?? 0);

const sourceMeta = {
  Solar: { icon: Sun, iconColor: "text-amber-600", bg: "bg-amber-100", bar: "bg-amber-500", name: "Solar" },
  Wind: { icon: Wind, iconColor: "text-sky-600", bg: "bg-sky-100", bar: "bg-sky-500", name: "Wind" },
  Hydro: { icon: Droplets, iconColor: "text-cyan-600", bg: "bg-cyan-100", bar: "bg-cyan-500", name: "Hydro" },
  Geothermal: { icon: Flame, iconColor: "text-rose-600", bg: "bg-rose-100", bar: "bg-rose-500", name: "Geothermal" },
};

function solarInfo(ghi) {
  if (ghi >= 5.0) return { label: "Excellent", desc: "Your area receives plenty of sunlight, making solar panels a highly recommended option." };
  if (ghi >= 4.0) return { label: "Good", desc: "Your location gets good sunlight. Solar panels can work well here with proper placement." };
  if (ghi >= 3.0) return { label: "Moderate", desc: "Sunlight is moderate. Solar may still work but may need a larger system." };
  return { label: "Fair", desc: "Sunlight is limited. Solar panels may not be the best choice here." };
}
function windInfo(ws) {
  if (ws >= 5.0) return { label: "Excellent", desc: "Strong winds make this location suitable for small wind turbines." };
  if (ws >= 3.5) return { label: "Good", desc: "Moderate wind speeds. Small turbines may generate some power in open areas." };
  if (ws >= 2.5) return { label: "Moderate", desc: "Wind is present but limited. Turbines may not be cost-effective for homes." };
  return { label: "Poor", desc: "Wind speeds are low. Consider solar instead." };
}
function hydroInfo(score) {
  if (score >= 70) return { label: "Good", desc: "Sufficient water flow and elevation. Micro-hydro could be viable if you have a stream." };
  if (score >= 40) return { label: "Moderate", desc: "Some water resources, but may not be reliable year-round." };
  return { label: "Fair", desc: "Limited water or flat terrain. Hydro is not recommended here." };
}
function geoInfo(score) {
  if (score >= 70) return { label: "Good", desc: "Nearby geothermal activity. This is a utility resource, not for home installation." };
  return { label: "Limited", desc: "No significant geothermal activity nearby. Not a home-scale option." };
}

function getNextSteps(source) {
  const steps = {
    Solar: [
      { title: "Get quotes from local solar installers", description: "Compare at least 3 quotes for a system that covers your energy needs." },
      { title: "Check net metering eligibility", description: "Ask your electric utility about selling excess power back to the grid." },
      { title: "Assess your roof condition", description: "Ensure your roof can support panels and is not heavily shaded." },
      { title: "Research government incentives", description: "Check DOE and LGU programs for renewable energy subsidies." },
    ],
    Wind: [
      { title: "Consult a wind energy specialist", description: "Small turbines require proper siting and wind assessment." },
      { title: "Check local zoning regulations", description: "Some areas restrict turbine height or require permits." },
      { title: "Consider hybrid systems", description: "Combining wind with solar can provide more consistent power." },
      { title: "Monitor wind for 3-6 months", description: "Install a small anemometer before investing in a turbine." },
    ],
    Hydro: [
      { title: "Survey local water sources", description: "Identify streams or rivers with consistent year-round flow." },
      { title: "Check water rights regulations", description: "You may need permits to use water flow for power generation." },
      { title: "Consult a micro-hydro expert", description: "Site assessment and system design require specialized knowledge." },
      { title: "Measure head and flow", description: "These two measurements determine how much power you can generate." },
    ],
    Geothermal: [
      { title: "Geothermal is not a home-scale option", description: "This is a utility-scale resource. Consider solar or wind instead for your home." },
      { title: "Switch to a renewable energy provider", description: "Some utilities offer geothermal or green power programs." },
      { title: "Advocate for community geothermal", description: "Support local initiatives for geothermal district heating if applicable." },
      { title: "Re-run EcoSim with alternative sources", description: "Try Solar or Wind simulation to see home-scale options." },
    ],
  };
  return steps[source] || steps.Solar;
}

export default function EcosimResults({ result, productRecs, productLoading }) {
  const [showDetails, setShowDetails] = useState(false);
  if (!result) return null;

  const rec = result.options?.find((o) => o.source === result.recommended_source) || {};
  const recScore = rec.suitability_score || 0;
  const recLabel = getRating(recScore, 100);
  const RecIcon = sourceMeta[result.recommended_source]?.icon || Zap;

  const climate = result.climate || {};
  const sInfo = solarInfo(climate.avg_allsky_sfc_sw_dwn);
  const wInfo = windInfo(climate.avg_ws10m);
  const hInfo = hydroInfo(result.renewable_energy_results?.hydro_output?.hydro_score);
  const gInfo = geoInfo(result.renewable_energy_results?.geothermal_output?.suitability_score);

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
      <div className={`rounded-2xl border-2 ${recLabel.border || "border-emerald-200"} ${recLabel.bg || "bg-emerald-50"} p-6 md:p-8`}>
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge className={`${recLabel.color || "bg-emerald-500"} text-white`}>{recLabel.label || "Excellent"} Match</Badge>
              <span className="text-2xl tracking-widest">{getStars(recScore, 100)}</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-bold text-slate-900">
              <span className="inline-flex items-center gap-2">
                <RecIcon className="h-8 w-8" />
                {result.recommended_source} Energy is Best for Your Location
              </span>
            </h2>
            <p className="text-slate-600 max-w-2xl leading-relaxed">{result.explanation}</p>
          </div>
          <div className="shrink-0 text-center md:text-right">
            <p className="text-sm text-muted-foreground">Suitability Score</p>
            <p className="text-4xl font-bold">
              {formatNumber(recScore, 0)}<span className="text-lg text-muted-foreground">/100</span>
            </p>
          </div>
        </div>
      </div>

      {/* Quick Benefits */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-l-4 border-l-emerald-500">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 text-emerald-700 mb-1">
              <PiggyBank className="h-4 w-4" />
              <span className="text-sm font-medium">Monthly Savings</span>
            </div>
            <p className="text-2xl font-bold">{formatCurrency(savings)}</p>
            <p className="text-xs text-muted-foreground mt-1">{savingsPct.toFixed(0)}% off your current bill</p>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-sky-500">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 text-sky-700 mb-1">
              <Zap className="h-4 w-4" />
              <span className="text-sm font-medium">Energy Coverage</span>
            </div>
            <p className="text-2xl font-bold">{formatNumber(coverage, 0)}%</p>
            <p className="text-xs text-muted-foreground mt-1">of your monthly consumption</p>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-amber-500">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 text-amber-700 mb-1">
              <ArrowRight className="h-4 w-4" />
              <span className="text-sm font-medium">Payback Period</span>
            </div>
            <p className="text-2xl font-bold">{result.payback_years ? `${formatNumber(result.payback_years, 1)} yrs` : "N/A"}</p>
            <p className="text-xs text-muted-foreground mt-1">time to break even</p>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-green-600">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 text-green-700 mb-1">
              <TreePine className="h-4 w-4" />
              <span className="text-sm font-medium">CO₂ Reduction</span>
            </div>
            <p className="text-2xl font-bold">{formatNumber(result.carbon_reduction)} kg</p>
            <p className="text-xs text-muted-foreground mt-1">less carbon per month</p>
          </CardContent>
        </Card>
      </div>

      {/* Why Recommended */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-emerald-500" />
            Why {result.recommended_source} Was Recommended
          </CardTitle>
          <CardDescription>How your location and climate led to this recommendation</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-lg border bg-muted/30 p-4">
              <p className="font-semibold mb-1">Your Location</p>
              <p className="text-sm text-muted-foreground">{result.municipality} — ID {result.municipality_id}</p>
              <p className="text-sm mt-2">
                Based on {cons.toFixed(0)} kWh/month usage and {formatCurrency(bill)} monthly bill
                (effective rate: {formatCurrency(rate)}/kWh).
              </p>
            </div>
            <div className="rounded-lg border bg-muted/30 p-4">
              <p className="font-semibold mb-1">Climate Advantage</p>
              <p className="text-sm text-muted-foreground">
                {result.recommended_source === "Solar" && (
                  <>{climate.avg_allsky_sfc_sw_dwn?.toFixed(2)} kWh/m²/day — {sInfo.desc}</>
                )}
                {result.recommended_source === "Wind" && (
                  <>{climate.avg_ws10m?.toFixed(2)} m/s — {wInfo.desc}</>
                )}
                {result.recommended_source === "Hydro" && (
                  <>Score {result.renewable_energy_results?.hydro_output?.hydro_score?.toFixed(0)} — {hInfo.desc}</>
                )}
                {result.recommended_source === "Geothermal" && (
                  <>{gInfo.desc}</>
                )}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Renewable Potential Comparison */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Renewable Energy Potential at Your Location</CardTitle>
          <CardDescription>How suitable your area is for each type of renewable energy</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {[
            { source: "Solar", info: sInfo, score: climate.avg_allsky_sfc_sw_dwn, max: 6, unit: "kWh/m²/day", output: result.renewable_energy_results?.solar_output },
            { source: "Wind", info: wInfo, score: climate.avg_ws10m, max: 6, unit: "m/s", output: result.renewable_energy_results?.wind_output },
            { source: "Hydro", info: hInfo, score: result.renewable_energy_results?.hydro_output?.hydro_score, max: 100, unit: "score", output: result.renewable_energy_results?.hydro_output },
            { source: "Geothermal", info: gInfo, score: result.renewable_energy_results?.geothermal_output?.suitability_score, max: 100, unit: "score", output: result.renewable_energy_results?.geothermal_output },
          ].map((item) => {
            const isRec = item.source === result.recommended_source;
            const meta = sourceMeta[item.source];
            const scoreVal = parseFloat(item.score) || 0;
            const rating = getRating(scoreVal, item.max);
            const stars = getStars(scoreVal, item.max);
            const pct = maxGen > 0 ? ((item.output?.estimated_generation_kwh || item.output?.monthly_energy_kwh || item.output?.monthly_solar_output || 0) / maxGen) * 100 : 0;
            return (
              <div key={item.source} className={`flex items-center gap-4 p-3 rounded-lg border ${isRec ? "border-emerald-300 bg-emerald-50/50" : ""}`}>
                <div className={`shrink-0 w-10 h-10 rounded-full ${meta.bg} flex items-center justify-center`}>
                  <meta.icon className={`h-5 w-5 ${meta.iconColor}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold">{item.source}</span>
                    {isRec && <Badge className="bg-emerald-500 text-white text-xs">Recommended</Badge>}
                    <Badge className={`${rating.color} text-white text-xs`}>{item.info.label}</Badge>
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
            <Wallet className="h-5 w-5 text-emerald-500" />
            Your Financial Impact
          </CardTitle>
          <CardDescription>How your electricity bill would change with the recommended system</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-xl border bg-red-50 p-5 text-center">
              <p className="text-sm text-red-600 font-medium">Current Monthly Bill</p>
              <p className="text-3xl font-bold text-red-700 mt-1">{formatCurrency(bill)}</p>
              <p className="text-xs text-red-500 mt-1">{cons.toFixed(0)} kWh used</p>
            </div>
            <div className="rounded-xl border bg-emerald-50 p-5 text-center">
              <p className="text-sm text-emerald-600 font-medium">New Monthly Bill</p>
              <p className="text-3xl font-bold text-emerald-700 mt-1">{formatCurrency(netBill)}</p>
              <p className="text-xs text-emerald-500 mt-1">After {result.recommended_source.toLowerCase()} offset</p>
            </div>
            <div className="rounded-xl border bg-amber-50 p-5 text-center">
              <p className="text-sm text-amber-600 font-medium">Monthly Savings</p>
              <p className="text-3xl font-bold text-amber-700 mt-1">{formatCurrency(savings)}</p>
              <p className="text-xs text-amber-500 mt-1">{savingsPct.toFixed(0)}% reduction</p>
            </div>
          </div>
          <div className="rounded-lg border bg-muted/30 p-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-muted-foreground">Estimated Installation Cost</p>
                <p className="text-xl font-semibold">{formatCurrency(result.installation_cost)}</p>
                <p className="text-xs text-muted-foreground mt-1">Actual costs vary by installer, system size, and brand.</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Payback Period</p>
                <p className="text-xl font-semibold">
                  {result.payback_years ? `${formatNumber(result.payback_years, 1)} years` : "Not calculable"}
                </p>
                <p className="text-xs text-muted-foreground mt-1">Time for savings to equal the installation cost.</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Meralco Rate */}
      {result.meralco_rate && result.meralco_rate.rate_php_per_kwh && (
        <Card>
          <CardHeader>
            <CardTitle>Meralco Generation Charge Reference</CardTitle>
            <CardDescription>Your selected location falls within the Meralco franchise area.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-3">
            <div>
              <p className="text-sm text-muted-foreground">Generation charge ({result.meralco_rate.year})</p>
              <p className="text-lg font-semibold">{formatCurrency(result.meralco_rate.rate_php_per_kwh)} / kWh</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Your effective rate</p>
              <p className="text-lg font-semibold">{formatCurrency(rate)} / kWh</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Customer class</p>
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
              <Zap className="h-5 w-5 text-amber-500" />
              Recommended Equipment for {result.recommended_source}
            </CardTitle>
            <CardDescription>Marketplace listings you can explore for your installation</CardDescription>
          </CardHeader>
          <CardContent>
            {productLoading && <div className="h-24 animate-pulse rounded bg-muted" />}
            {!productLoading && productRecs?.items?.length > 0 && (
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {productRecs.items.map((item) => (
                  <a key={item.url || item.product_name} href={item.url} target="_blank" rel="noopener noreferrer" className="rounded-lg border bg-card p-4 shadow-sm hover:shadow-md transition-shadow">
                    <p className="text-sm font-medium line-clamp-2">{item.product_name}</p>
                    <p className="mt-1 text-sm font-semibold text-emerald-700">{item.currency} {item.price_value?.toLocaleString?.() || item.price_value}</p>
                    <p className="text-xs text-muted-foreground capitalize">{item.source_site} · {item.energy_subcategory}</p>
                    {item.ratings && <p className="text-xs text-amber-600 mt-1">{item.ratings}</p>}
                  </a>
                ))}
              </div>
            )}
            {!productLoading && productRecs && (!productRecs.items || productRecs.items.length === 0) && (
              <div className="rounded-lg border bg-muted/30 p-4 text-sm text-muted-foreground">
                <AlertTriangle className="h-4 w-4 inline mr-1 text-amber-500" />
                No matching products with links found. Try searching "{result.recommended_source.toLowerCase()} panels Philippines" or "{result.recommended_source.toLowerCase()} turbine home" on your preferred marketplace.
              </div>
            )}
            {productRecs?.note && <p className="mt-2 text-xs text-muted-foreground">{productRecs.note}</p>}
          </CardContent>
        </Card>
      )}

      {/* Provider Recommendations */}
      <ProviderRecommendations municipalityName={result.municipality} provinceName={result.municipality} />

      {/* Next Steps */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-sky-500" />
            Recommended Next Steps
          </CardTitle>
          <CardDescription>Practical actions to move forward with your renewable energy plan</CardDescription>
        </CardHeader>
        <CardContent>
          <NextStepList steps={getNextSteps(result.recommended_source)} />
        </CardContent>
      </Card>

      {/* Technical Details Toggle */}
      <div className="text-center">
        <Button variant="ghost" size="sm" onClick={() => setShowDetails(!showDetails)} className="text-muted-foreground hover:text-foreground">
          {showDetails ? <ChevronUp className="h-4 w-4 mr-1" /> : <ChevronDown className="h-4 w-4 mr-1" />}
          {showDetails ? "Hide technical details" : "Show technical details for advanced users"}
        </Button>
      </div>

      {showDetails && (
        <div className="space-y-6">
          {/* Climate data */}
          {climate && (
            <Card>
              <CardHeader>
                <CardTitle>Climate Data</CardTitle>
                <CardDescription>Average conditions for this location (NASA POWER)</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-3 md:grid-cols-3 lg:grid-cols-4">
                {[
                  { label: "Temperature", value: climate.avg_t2m, unit: "°C", digits: 1 },
                  { label: "Humidity", value: climate.avg_rh2m, unit: "%", digits: 1 },
                  { label: "Rainfall", value: climate.avg_prectotcorr, unit: "mm/day", digits: 1 },
                  { label: "Solar irradiance", value: climate.avg_allsky_sfc_sw_dwn, unit: "kWh/m²/day", digits: 2 },
                  { label: "Wind speed", value: climate.avg_ws10m, unit: "m/s", digits: 2 },
                  { label: "Cloud coverage", value: climate.avg_cloud_amt, unit: "%", digits: 1 },
                  { label: "Surface pressure", value: climate.avg_surface_pressure, unit: "kPa", digits: 1 },
                  { label: "Elevation", value: climate.elevation, unit: "m", digits: 0 },
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
                        {title} output
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <div className="flex justify-between"><span className="text-muted-foreground">Daily</span><span className="font-medium">{formatNumber(data.daily_solar_output || data.daily_energy_kwh || data.daily_hydro_output, 2)} kWh</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">Monthly</span><span className="font-medium">{formatNumber(data.monthly_solar_output || data.monthly_energy_kwh || data.monthly_hydro_output, 1)} kWh</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">Annual</span><span className="font-medium">{formatNumber(data.annual_solar_output || data.annual_wind_output_kwh || data.annual_hydro_output, 0)} kWh</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">Score</span><span className="font-medium">{formatNumber(data.solar_score || data.capacity_factor || data.hydro_score || data.suitability_score, 0)} / 100</span></div>
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
                <CardTitle>Scenario Comparison</CardTitle>
                <CardDescription>Current usage vs recommended renewable offset</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-3 md:grid-cols-2">
                <div className="rounded-lg border bg-red-50 p-4">
                  <p className="text-sm font-medium text-red-600">Current</p>
                  <p className="text-xl font-bold text-red-700">{formatCurrency(result.comparison.current_monthly_bill)}</p>
                  <p className="text-xs text-red-500">{formatNumber(result.comparison.current_monthly_consumption_kwh)} kWh</p>
                </div>
                <div className="rounded-lg border bg-emerald-50 p-4">
                  <p className="text-sm font-medium text-emerald-600">With {result.recommended_source}</p>
                  <p className="text-xl font-bold text-emerald-700">{formatCurrency(result.comparison.renewable_monthly_bill)}</p>
                  <p className="text-xs text-emerald-500">{formatNumber(result.comparison.renewable_monthly_consumption_kwh)} kWh</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
