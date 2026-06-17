import { useState } from "react";
import { Lightbulb, Info, Sparkles, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function AiInsightPanel({
  insight,
  onToggleLlm,
  useLlm = false,
  llmLoading = {},
  chartAnalyses = {},
  onAnalyzeChart,
}) {
  const [activeTab, setActiveTab] = useState("overview");

  const anyLoading = Object.values(llmLoading || {}).some(Boolean);
  const tabLoading = !!(llmLoading || {})[activeTab];

  if (!insight) {
    return (
      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-amber-500" />
          AI Insight
        </h3>
        <div className="mt-4 h-24 bg-muted rounded-lg animate-pulse" />
      </div>
    );
  }

  const activeAnalysis = chartAnalyses[activeTab];

  return (
    <div className="rounded-xl border bg-card p-6 shadow-sm">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-amber-500" />
          AI Insight
        </h3>
        <Button
          variant={useLlm ? "default" : "outline"}
          size="sm"
          onClick={onToggleLlm}
          disabled={anyLoading}
          className="gap-1.5"
        >
          {anyLoading ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Sparkles className="h-3.5 w-3.5" />
          )}
          {useLlm ? "LLM Mode" : "Static Mode"}
        </Button>
      </div>

      <p className="mt-1 text-xs text-muted-foreground">
        {useLlm
          ? "Powered by Gemini/Groq LLM — analyzing energy data dynamically."
          : `Data-driven observation based on ${insight.data_year} statistics and ARIMA forecast`}
      </p>

      {/* Tabs for different chart analyses */}
      {useLlm && onAnalyzeChart && (
        <div className="mt-3 flex gap-2 overflow-x-auto pb-1">
          {[
            { key: "overview", label: "Overview" },
            { key: "trends", label: "Trends" },
            { key: "sources", label: "Sources" },
            { key: "map", label: "Map" },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => {
                setActiveTab(tab.key);
                if (!chartAnalyses[tab.key]) {
                  onAnalyzeChart(tab.key);
                }
              }}
              disabled={!!(llmLoading || {})[tab.key]}
              className={`px-3 py-1 rounded-md text-xs font-medium whitespace-nowrap transition-colors disabled:opacity-50 ${
                activeTab === tab.key
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              }`}
            >
              {tab.label}
              {chartAnalyses[tab.key] && <span className="ml-1 text-[10px]">✓</span>}
            </button>
          ))}
        </div>
      )}

      <div className="mt-4 rounded-lg bg-amber-50 border border-amber-100 p-4">
        {tabLoading && !activeAnalysis?.insight ? (
          <div className="flex items-center gap-2 text-sm text-amber-800">
            <Loader2 className="h-4 w-4 animate-spin" />
            Generating LLM analysis...
          </div>
        ) : (
          <p className="text-sm leading-relaxed text-amber-900 whitespace-pre-line">
            {activeAnalysis?.insight || insight?.insight || ""}
          </p>
        )}
      </div>

      {(activeAnalysis?.recommendation || insight.recommendation) && (
        <div className="mt-3 rounded-lg bg-sky-50 border border-sky-100 p-4 flex gap-3">
          <Info className="h-4 w-4 text-sky-600 shrink-0 mt-0.5" />
          <p className="text-sm leading-relaxed text-sky-900">
            {activeAnalysis?.recommendation || insight.recommendation}
          </p>
        </div>
      )}
    </div>
  );
}
