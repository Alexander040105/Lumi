import React, { useCallback, useEffect, useRef, useState } from "react";
import { useI18n } from "@/i18n";
import { Card, CardContent } from "@/components/ui/card";
import { getEnergyHubMapExplanation } from "@/services/energyhub";
import { Info, Loader2, RefreshCw, Eye, EyeOff } from "lucide-react";

const HIDDEN_KEY = "lumi:hidden_map_explanations";

function getHiddenSet() {
  try {
    return new Set(JSON.parse(localStorage.getItem(HIDDEN_KEY) || "[]"));
  } catch {
    return new Set();
  }
}

function saveHiddenSet(set) {
  try {
    localStorage.setItem(HIDDEN_KEY, JSON.stringify(Array.from(set)));
  } catch {}
}

export default function MapExplanationCard({ metric, level }) {
  const { t } = useI18n();
  const [hidden, setHidden] = useState(() => getHiddenSet().has(metric));
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const cacheRef = useRef({});

  const cacheKey = `${metric}|${level}`;

  const load = useCallback(
    async (forceRefresh = false) => {
      if (hidden && !forceRefresh) return;

      if (!forceRefresh) {
        const cached = cacheRef.current[cacheKey];
        if (cached) {
          setResult(cached);
          return;
        }
      }

      setLoading(true);
      setError(null);
      try {
        const response = await getEnergyHubMapExplanation(metric, level, forceRefresh);
        cacheRef.current[cacheKey] = response;
        setResult(response);
      } catch (err) {
        setError(err.message || t("energyHub.map.explanationError"));
      } finally {
        setLoading(false);
      }
    },
    [metric, level, hidden, cacheKey, t]
  );

  useEffect(() => {
    setHidden(getHiddenSet().has(metric));
  }, [metric]);

  useEffect(() => {
    if (!hidden) {
      load();
    }
  }, [load, hidden]);

  const handleToggleHidden = () => {
    const next = !hidden;
    const set = getHiddenSet();
    if (next) {
      set.add(metric);
    } else {
      set.delete(metric);
    }
    saveHiddenSet(set);
    setHidden(next);
  };

  const metricTitle = t(`energyHub.map.explanationTitle.${metric}`);
  const title =
    metricTitle && !String(metricTitle).startsWith("energyHub.")
      ? metricTitle
      : t("energyHub.map.explanationTitleDefault");

  return (
    <Card className="mb-4 border-l-4 border-l-primary bg-muted/40">
      <CardContent className="py-3 px-4">
        {hidden ? (
          <div className="flex items-center justify-between gap-2 text-sm">
            <span className="text-muted-foreground">{t("energyHub.map.explanationHidden")}</span>
            <button
              type="button"
              onClick={handleToggleHidden}
              className="inline-flex items-center gap-1 text-primary hover:underline"
            >
              <Eye className="h-4 w-4" />
              {t("energyHub.map.showExplanation")}
            </button>
          </div>
        ) : (
          <div className="flex items-start gap-2">
            <Info className="mt-0.5 h-4 w-4 text-primary shrink-0" />
            <div className="space-y-1 text-sm flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <p className="font-semibold text-foreground">{title}</p>
                <div className="flex items-center gap-1 shrink-0">
                  <button
                    type="button"
                    onClick={() => load(true)}
                    disabled={loading}
                    title={t("energyHub.map.refreshExplanation")}
                    className="inline-flex h-6 w-6 items-center justify-center rounded-md text-muted-foreground hover:bg-muted disabled:opacity-50"
                  >
                    {loading ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <RefreshCw className="h-3.5 w-3.5" />
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={handleToggleHidden}
                    title={t("energyHub.map.hideExplanation")}
                    className="inline-flex h-6 w-6 items-center justify-center rounded-md text-muted-foreground hover:bg-muted"
                  >
                    <EyeOff className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
              {loading && !result && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  {t("energyHub.map.explanationLoading")}
                </div>
              )}
              {error && <p className="text-destructive text-xs">{error}</p>}
              {result?.insight && (
                <p className="text-muted-foreground whitespace-pre-wrap leading-relaxed">
                  {result.insight}
                </p>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
