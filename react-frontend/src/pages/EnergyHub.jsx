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
} from "../services/energyhub";

import { useAuth } from "@/hooks/useAuth";

import EnergyOverview from "@/components/energyhub/EnergyOverview";
import EnergyMap from "@/components/energyhub/EnergyMap";
import EnergyTrends from "@/components/energyhub/EnergyTrends";
import EnergySources from "@/components/energyhub/EnergySources";
import AiInsightPanel from "@/components/energyhub/AiInsightPanel";

const SUITABILITY_METRICS = [
  "renewable_potential",
  "solar_potential",
  "wind_potential",
  "hydro_potential",
  "geothermal_potential",
];

export default function EnergyHub() {
  const { user, plan, isFree, isPro, isPremium } = useAuth();
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
  const [remainingInsights, setRemainingInsights] = useState(
    isFree ? 1 : isPro ? 5 : 20
  );

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
        const [ov, tr, mp, src] = await Promise.all([
          getEnergyHubOverview(),
          getEnergyHubTrends(),
          fetchAndCacheMapData("renewable_potential", "province"),
          getEnergyHubSourceBreakdown(),
        ]);
        if (!cancelled) {
          setOverview(ov);
          setTrends(tr);
          setMapData(mp);
          setSourceBreakdown(src);
        }
      } catch (err) {
        if (!cancelled) {
          toast.error("Failed to load EnergyHub data", { description: err.message });
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

      // Load static insight (always free); LLM requires auth
      try {
        const staticAi = await getEnergyHubAiInsight(false);
        if (!cancelled) setInsight(staticAi);
      } catch {}

      // Load LLM insight only if authenticated
      if (user) {
        try {
          const ai = await getEnergyHubAiInsight(true);
          if (!cancelled) {
            setInsight(ai);
            if (ai?.remaining_insights !== undefined) {
              setRemainingInsights(ai.remaining_insights);
            }
            if (ai?.upgrade_info) {
              toast.info(ai.upgrade_info.message || "AI insight limit reached", {
                action: { label: "Upgrade", onClick: () => window.location.href = "/pricing" },
              });
            }
          }
        } catch (err) {
          if (!cancelled) {
            toast.error("LLM insight failed", { description: err.message });
          }
        }
      }

      if (!cancelled) setLlmLoading((prev) => ({ ...prev, overview: false }));
    }

    loadAll();
    return () => {
      cancelled = true;
    };
  }, [user]);

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
    if (!next) return;
    if (!user) {
      toast.info("Sign in to access LLM-powered insights.");
      return;
    }
    if (remainingInsights <= 0) {
      toast.error("AI insight limit reached. Upgrade your plan to continue.");
      return;
    }
    if (!insight?.insight?.includes("LLM")) {
      setLlmLoading((prev) => ({ ...prev, overview: true }));
      try {
        const ai = await getEnergyHubAiInsight(true);
        setInsight(ai);
        if (ai?.remaining_insights !== undefined) {
          setRemainingInsights(ai.remaining_insights);
        }
        if (ai?.upgrade_info) {
          toast.info(ai.upgrade_info.message || "AI insight limit reached", {
            action: { label: "Upgrade", onClick: () => window.location.href = "/pricing" },
          });
        }
      } catch (err) {
        toast.error("LLM insight failed", { description: err.message });
      } finally {
        setLlmLoading((prev) => ({ ...prev, overview: false }));
      }
    }
  };

  const handleAnalyzeChart = async (chartType, forceRefresh = false) => {
    if (chartAnalyses[chartType] && !forceRefresh) return;
    if (!user) {
      toast.info("Sign in to analyze charts with AI.");
      return;
    }
    if (remainingInsights <= 0) {
      toast.error("AI insight limit reached. Upgrade your plan to continue.");
      return;
    }
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
      if (result?.remaining_insights !== undefined) {
        setRemainingInsights(result.remaining_insights);
      }
    } catch (err) {
      if (err.message?.toLowerCase().includes("limit reached") || err.message?.includes("upgrade")) {
        toast.error(err.message, {
          action: { label: "Upgrade", onClick: () => window.location.href = "/pricing" },
        });
      } else {
        toast.error(`Failed to analyze ${chartType}`, { description: err.message });
      }
    } finally {
      setLlmLoading((prev) => ({ ...prev, [chartType]: false }));
    }
  };

  return (
    <div className="min-h-screen bg-background pb-12">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold tracking-tight">EnergyHub</h1>
          <p className="mt-2 max-w-2xl text-muted-foreground">
            Explore Philippine national energy statistics, ARIMA-based demand
            forecasts, and renewable potential across regions. Data sourced from
            the Department of Energy (DOE) and NASA POWER climate archives.
          </p>
          <p className="mt-1 text-xs text-muted-foreground">
            Disclaimer: This module provides educational insights and is not a
            substitute for professional energy planning.
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8">
        {/* Section 1: Overview Cards */}
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-4">
            National Overview
          </h2>
          <EnergyOverview data={overview} />
        </section>

        {/* Section 2: Choropleth Map */}
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
            remainingInsights={remainingInsights}
            plan={plan}
            isFree={isFree}
            isPro={isPro}
            isPremium={isPremium}
          />
        </section>
      </div>
    </div>
  );
}
