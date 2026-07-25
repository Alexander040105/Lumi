import { useState, useEffect } from "react";
import { getCoverageSummary } from "../services/apiClient";

export default function CoverageDashboard() {
  const [level, setLevel] = useState("municipality");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getCoverageSummary(level)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [level]);

  const items = data?.items || [];
  const total = data?.total_units ?? items.length;
  const withClimate = data?.with_climate_data ?? items.filter((i) => i.has_climate_data).length;
  const coveragePct = data?.coverage_pct ?? (total > 0 ? (withClimate / total) * 100 : 0);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">Data Coverage</h3>
        <select
          value={level}
          onChange={(e) => setLevel(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
        >
          <option value="municipality">Municipality</option>
          <option value="province">Province</option>
        </select>
      </div>

      {loading && <div className="text-gray-400 text-sm">Loading...</div>}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {!loading && !error && (
        <>
          {/* Overall coverage gauge */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Climate Data Coverage</span>
              <span className={`text-sm font-bold ${
                coveragePct >= 80 ? "text-green-600" : coveragePct >= 50 ? "text-yellow-600" : "text-red-600"
              }`}>
                {coveragePct.toFixed(1)}%
              </span>
            </div>
            <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  coveragePct >= 80 ? "bg-green-500" : coveragePct >= 50 ? "bg-yellow-500" : "bg-red-500"
                }`}
                style={{ width: `${Math.min(coveragePct, 100)}%` }}
              />
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {withClimate.toLocaleString()} / {total.toLocaleString()} {level}s with climate data
            </div>
          </div>

          {/* Per-source breakdown if items have detailed data */}
          {items.length > 0 && items[0]?.renewable_type && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">By Renewable Type</h4>
              {items.map((item) => {
                const pct = item.coverage_pct ?? 0;
                return (
                  <div key={item.renewable_type} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="capitalize text-gray-700">{item.renewable_type}</span>
                      <span className="text-gray-500">{pct.toFixed(1)}%</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          pct >= 80 ? "bg-green-500" : pct >= 50 ? "bg-yellow-500" : "bg-red-500"
                        }`}
                        style={{ width: `${Math.min(pct, 100)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Summary stats */}
          <div className="mt-4 pt-3 border-t border-gray-100 grid grid-cols-3 gap-3 text-center">
            <div>
              <div className="text-2xl font-bold text-gray-900">{total.toLocaleString()}</div>
              <div className="text-xs text-gray-500">Total Units</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">{withClimate.toLocaleString()}</div>
              <div className="text-xs text-gray-500">With Data</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-600">
                {(total - withClimate).toLocaleString()}
              </div>
              <div className="text-xs text-gray-500">Gaps</div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
