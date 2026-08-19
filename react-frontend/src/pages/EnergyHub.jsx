import { useEffect, useState, useRef } from "react";
import { toast } from "sonner";

import {
  getEnergyHubOverview,
  getEnergyHubTrends,
  getEnergyHubMapData,
  getEnergyHubSourceBreakdown,
  getEnergyHubAiInsight,
  analyzeChart,
  getGeothermalPlants,
  getIrenaOverview,
} from "../services/energyhub";

import { useI18n } from "@/i18n";
import EnergyOverview from "@/components/energyhub/EnergyOverview";
import EnergyMap from "@/components/energyhub/EnergyMap";
import EnergyTrends from "@/components/energyhub/EnergyTrends";
import EnergySources from "@/components/energyhub/EnergySources";
import AiInsightPanel from "@/components/energyhub/AiInsightPanel";
import ProvincialDemand from "@/components/energyhub/ProvincialDemand";
import CitationSources from "@/components/shared/CitationSources";

const SUITABILITY_METRICS = [
  "renewable_potential",
  "solar_potential",
  "wind_potential",
  "hydro_potential",
  "geothermal_potential",
];

export default function EnergyHub() {
  const { t } = useI18n();
  const [overview, setOverview] = useState(null);
  const [trends, setTrends] = useState(null);
  const [mapData, setMapData] = useState(null);
  const [sourceBreakdown, setSourceBreakdown] = useState(null);
  const [insight, setInsight] = useState(null);
  const [mapMetric, setMapMetric] = useState("renewable_potential");
  const [mapLevel, setMapLevel] = useState("province");
  const [loading, setLoading] = useState(true);
  const [useLlm, setUseLlm] = useState(false);
  const [llmLoading, setLlmLoading] = useState({});
  const [chartAnalyses, setChartAnalyses] = useState({});
  const [mapLoading, setMapLoading] = useState(false);
  const [geothermalPlants, setGeothermalPlants] = useState([]);
  const [irena, setIrena] = useState(null);

  // Cache for map data: { [metric]: { [level]: response } }
  const mapCacheRef = useRef({});

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------
  const getCachedMapData = (metric, level) => {
    return mapCacheRef.current[metric]?.[level] ?? null;
  };

  const setCachedMapData = (metric, level, data) => {
    if (!mapCacheRef.current[metric]) mapCacheRef.current[metric] = {};
    mapCacheRef.current[metric][level] = data;
  };

  const fetchAndCacheMapData = async (metric, level) => {
    const cached = getCachedMapData(metric, level);
    if (cached) return cached;
    const data = await getEnergyHubMapData(metric, level);
    setCachedMapData(metric, level, data);
    return data;
  };

  // ---------------------------------------------------------------------------
  // Initial load — overview + trends + province map + pre-fetch all metrics
  // ---------------------------------------------------------------------------
  useEffect(() => {
    let cancelled = false;

    async function loadAll() {
      setLoading(true);
      setLlmLoading((prev) => ({ ...prev, overview: true }));
      try {
        const [ov, tr, mp, src, ir] = await Promise.all([
          getEnergyHubOverview(),
          getEnergyHubTrends(),
          fetchAndCacheMapData("renewable_potential", "province"),
          getEnergyHubSourceBreakdown(),
          getIrenaOverview().catch(() => null),
        ]);
        if (!cancelled) {
          setOverview(ov);
          setTrends(tr);
          setMapData(mp);
          setSourceBreakdown(src);
          setIrena(ir);
        }
      } catch (err) {
        if (!cancelled) {
          toast.error(t("energyHub.toast.loadError"), { description: err.message });
        }
      } finally {
        if (!cancelled) setLoading(false);
      }

      // Pre-fetch all suitability metrics in background (province level)
      Promise.all(
        SUITABILITY_METRICS.filter((m) => m !== "renewable_potential").map((m) =>
          fetchAndCacheMapData(m, "province").catch(() => null)
        )
      );

      // Fetch geothermal plant list for map markers
      try {
        const plants = await getGeothermalPlants();
        if (!cancelled) setGeothermalPlants(plants || []);
      } catch {
        // Non-critical; markers simply won't appear
      }

      // Load LLM insight in background
      try {
        const ai = await getEnergyHubAiInsight(useLlm);
        if (!cancelled) setInsight(ai);
      } catch (err) {
        if (!cancelled && useLlm) {
          toast.error(t("energyHub.toast.llmError"), { description: err.message });
          try {
            const staticAi = await getEnergyHubAiInsight(false);
            if (!cancelled) setInsight(staticAi);
          } catch {}
        }
      } finally {
        if (!cancelled) setLlmLoading((prev) => ({ ...prev, overview: false }));
      }
    }

    loadAll();
    return () => {
      cancelled = true;
    };
  }, []);

  // ---------------------------------------------------------------------------
  // Switch metric or level — use cache if available, else fetch + cache
  // ---------------------------------------------------------------------------
  useEffect(() => {
    let cancelled = false;
    const cached = getCachedMapData(mapMetric, mapLevel);
    if (cached) {
      setMapData(cached);
      return;
    }
    setMapLoading(true);
    fetchAndCacheMapData(mapMetric, mapLevel)
      .then((mp) => {
        if (!cancelled) setMapData(mp);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setMapLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [mapMetric, mapLevel]);

  const handleToggleLlm = async () => {
    const next = !useLlm;
    setUseLlm(next);
    if (next && !insight?.insight?.includes("LLM")) {
      setLlmLoading((prev) => ({ ...prev, overview: true }));
      try {
        const ai = await getEnergyHubAiInsight(true);
        setInsight(ai);
      } catch (err) {
        toast.error("LLM insight failed", { description: err.message });
      } finally {
        setLlmLoading((prev) => ({ ...prev, overview: false }));
      }
    }
  };

  const handleAnalyzeChart = async (chartType, forceRefresh = false) => {
    if (chartAnalyses[chartType] && !forceRefresh) return;
    setLlmLoading((prev) => ({ ...prev, [chartType]: true }));
    try {
      let chartData = {};
      if (chartType === "trends" && trends) {
        chartData = {
          years: trends.years,
          consumption: trends.series?.total_consumption_gwh || [],
          forecast: trends.forecast?.forecast_values || [],
        };
      } else if (chartType === "consumption_trend" && trends) {
        chartData = {
          years: trends.years,
          consumption: trends.series?.total_consumption_gwh || [],
          forecast_years: trends.forecast?.forecast_years || [],
          forecast_values: trends.forecast?.forecast_values || [],
        };
      } else if (chartType === "peak_demand" && trends) {
        chartData = {
          years: trends.years,
          peak_demand: trends.series?.total_peak_demand_mw || [],
        };
      } else if (chartType === "renewable_generation" && trends) {
        chartData = {
          years: trends.years,
          renewable_generation: trends.series?.renewable_generation_gwh || [],
          total_generation: trends.series?.total_generation_gwh || [],
        };
      } else if (chartType === "sources" && sourceBreakdown) {
        chartData = { shares: sourceBreakdown.share_pct || {} };
      } else if (chartType === "map") {
        chartData = { metric: mapMetric };
      }
      const result = await analyzeChart(chartType, chartData, forceRefresh);
      setChartAnalyses((prev) => ({ ...prev, [chartType]: result }));
    } catch (err) {
      toast.error(t("energyHub.toast.analyzeError", { chartType }), { description: err.message });
    } finally {
      setLlmLoading((prev) => ({ ...prev, [chartType]: false }));
    }
  };

  return (
    <div className="min-h-screen bg-background pb-12">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold tracking-tight">{t("energyHub.title")}</h1>
          <p className="mt-2 max-w-2xl text-muted-foreground">
            {t("energyHub.description")}
          </p>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <CitationSources ids={t("energyHub.citations")} />
            <p className="text-xs text-muted-foreground">
              {t("energyHub.disclaimer")}
            </p>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8">
        {/* Section 1: Overview Cards */}
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-4">
            {t("energyHub.sections.nationalOverview")}
          </h2>
          <EnergyOverview data={overview} />
        </section>

        {/* Section 2: Provincial Demand */}
        <section>
          <ProvincialDemand />
        </section>

        {/* Section 2b: IRENA Benchmark */}
        {irena && irena.capacity?.length > 0 && (
          <section className="rounded-xl border bg-card p-6 shadow-sm">
            <h2 className="text-lg font-semibold">{t("energyHub.sections.irena.title")}</h2>
            <p className="text-sm text-muted-foreground">{t("energyHub.sections.irena.description")}</p>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="rounded-lg border bg-muted/30 p-3">
                <p className="text-xs text-muted-foreground">{t("energyHub.sections.irena.latestReCapacity")}</p>
                <p className="text-lg font-semibold">
                  {irena.capacity.filter(c => c.technology === "Total renewable energy" && c.grid_connection === "On-grid").pop()?.capacity_mw?.toLocaleString?.() ?? "—"} {t("energyHub.sections.irena.unitMW")}
                </p>
              </div>
              <div className="rounded-lg border bg-muted/30 p-3">
                <p className="text-xs text-muted-foreground">{t("energyHub.sections.irena.latestReGeneration")}</p>
                <p className="text-lg font-semibold">
                  {irena.generation.filter(g => g.technology === "Total renewable" && g.grid_connection === "On-grid").pop()?.generation_gwh?.toLocaleString?.() || "—"} {t("energyHub.sections.irena.unitGWh")}
                </p>
              </div>
              <div className="rounded-lg border bg-muted/30 p-3">
                <p className="text-xs text-muted-foreground">{t("energyHub.sections.irena.reShareLatest")}</p>
                <p className="text-lg font-semibold">
                  {irena.renewable_share?.pop()?.renewable_share_pct ?? "—"}%
                </p>
              </div>
            </div>
            <p className="mt-2 text-xs text-muted-foreground">{irena.note}</p>
          </section>
        )}

        {/* Section 3: Choropleth Map */}
        <section>
          <EnergyMap
            mapData={mapData}
            metric={mapMetric}
            level={mapLevel}
            onMetricChange={setMapMetric}
            onLevelChange={setMapLevel}
            mapLoading={mapLoading}
            geothermalPlants={geothermalPlants}
          />
        </section>

        {/* Section 3: Energy Trends */}
        <section>
          <EnergyTrends
            trends={trends}
            chartAnalyses={chartAnalyses}
            llmLoading={llmLoading}
            onAnalyzeChart={handleAnalyzeChart}
          />
        </section>

        {/* Section 4: Energy Source Comparison */}
        <section>
          <EnergySources breakdown={sourceBreakdown} />
        </section>

        {/* Section 5: AI Insight Panel */}
        <section>
          <AiInsightPanel
            insight={insight}
            useLlm={useLlm}
            llmLoading={llmLoading}
            chartAnalyses={chartAnalyses}
            onToggleLlm={handleToggleLlm}
            onAnalyzeChart={handleAnalyzeChart}
          />
        </section>
      </div>
    </div>
  );
}
