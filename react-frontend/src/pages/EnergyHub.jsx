import { useEffect, useState } from "react";
import { toast } from "sonner";

import {
  getEnergyHubOverview,
  getEnergyHubTrends,
  getEnergyHubMapData,
  getEnergyHubSourceBreakdown,
  getEnergyHubAiInsight,
  analyzeChart,
} from "../services/energyhub";

import EnergyOverview from "@/components/energyhub/EnergyOverview";
import EnergyMap from "@/components/energyhub/EnergyMap";
import EnergyTrends from "@/components/energyhub/EnergyTrends";
import EnergySources from "@/components/energyhub/EnergySources";
import AiInsightPanel from "@/components/energyhub/AiInsightPanel";

export default function EnergyHub() {
  const [overview, setOverview] = useState(null);
  const [trends, setTrends] = useState(null);
  const [mapData, setMapData] = useState(null);
  const [sourceBreakdown, setSourceBreakdown] = useState(null);
  const [insight, setInsight] = useState(null);
  const [mapMetric, setMapMetric] = useState("renewable_potential");
  const [loading, setLoading] = useState(true);
  const [useLlm, setUseLlm] = useState(true);
  const [llmLoading, setLlmLoading] = useState(false);
  const [chartAnalyses, setChartAnalyses] = useState({});

  useEffect(() => {
    let cancelled = false;

    async function loadAll() {
      setLoading(true);
      setLlmLoading(true);
      try {
        const [ov, tr, mp, src] = await Promise.all([
          getEnergyHubOverview(),
          getEnergyHubTrends(),
          getEnergyHubMapData(mapMetric),
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

      // Load LLM insight in background
      try {
        const ai = await getEnergyHubAiInsight(true);
        if (!cancelled) setInsight(ai);
      } catch (err) {
        if (!cancelled) {
          toast.error("LLM insight failed", { description: err.message });
          // Fallback to static
          try {
            const staticAi = await getEnergyHubAiInsight(false);
            if (!cancelled) setInsight(staticAi);
          } catch {}
        }
      } finally {
        if (!cancelled) setLlmLoading(false);
      }
    }

    loadAll();
    return () => {
      cancelled = true;
    };
  }, []);

  // Refetch map data when metric changes
  useEffect(() => {
    let cancelled = false;
    getEnergyHubMapData(mapMetric)
      .then((mp) => {
        if (!cancelled) setMapData(mp);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [mapMetric]);

  const handleToggleLlm = async () => {
    const next = !useLlm;
    setUseLlm(next);
    if (next && !insight?.insight?.includes("LLM")) {
      setLlmLoading(true);
      try {
        const ai = await getEnergyHubAiInsight(true);
        setInsight(ai);
      } catch (err) {
        toast.error("LLM insight failed", { description: err.message });
      } finally {
        setLlmLoading(false);
      }
    }
  };

  const handleAnalyzeChart = async (chartType, forceRefresh = false) => {
    if (chartAnalyses[chartType] && !forceRefresh) return;
    setLlmLoading(true);
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
      toast.error(`Failed to analyze ${chartType}`, { description: err.message });
    } finally {
      setLlmLoading(false);
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
            onMetricChange={setMapMetric}
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
