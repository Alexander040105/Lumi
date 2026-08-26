import { useState, useEffect } from "react";
import { getSuitabilityMap } from "../services/apiClient";

const RENEWABLE_TYPES = [
  { key: "solar", label: "Solar", color: "#f59e0b" },
  { key: "wind", label: "Wind", color: "#3b82f6" },
  { key: "hydro", label: "Hydro", color: "#06b6d4" },
  { key: "geothermal", label: "Geothermal", color: "#ef4444" },
];

export default function MapPanel() {
  const [renewableType, setRenewableType] = useState("solar");
  const [level, setLevel] = useState("municipality");
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getSuitabilityMap(renewableType, level)
      .then((result) => setData(result.items || []))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [renewableType, level]);

  const scores = data.map((d) => d.score).filter((s) => s != null);
  const maxScore = Math.max(...scores, 100);
  const minScore = Math.min(...scores, 0);

  function getScoreColor(score) {
    if (score == null) return "#e5e7eb";
    const pct = (score - minScore) / (maxScore - minScore || 1);
    if (pct >= 0.75) return "#16a34a";
    if (pct >= 0.5) return "#84cc16";
    if (pct >= 0.25) return "#facc15";
    return "#f87171";
  }

  return (
    <div className="bg-card rounded-xl shadow-sm border border-border p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-foreground">Suitability Map</h3>
        <div className="flex gap-2">
          <select
            value={renewableType}
            onChange={(e) => setRenewableType(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
          >
            {RENEWABLE_TYPES.map((rt) => (
              <option key={rt.key} value={rt.key}>{rt.label}</option>
            ))}
          </select>
          <select
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
          >
            <option value="municipality">Municipality</option>
            <option value="province">Province</option>
          </select>
        </div>
      </div>

      {loading && <div className="text-muted-foreground text-sm py-8 text-center">Loading map data...</div>}
      {error && (
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-3 text-sm text-destructive mb-4">
          {error}
        </div>
      )}

      {!loading && !error && (
        <>
          {/* Legend */}
          <div className="flex items-center gap-4 mb-3 text-xs text-muted-foreground">
            <span>Score:</span>
            <div className="flex items-center gap-1">
              <div className="w-4 h-4 rounded" style={{ background: "#f87171" }} />
              <span>Low</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-4 h-4 rounded" style={{ background: "#facc15" }} />
              <span>Medium</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-4 h-4 rounded" style={{ background: "#16a34a" }} />
              <span>High</span>
            </div>
            <span className="ml-auto text-muted-foreground">{data.length} {level}s</span>
          </div>

          {/* Data table (fallback for when no map renderer is available) */}
          <div className="overflow-x-auto max-h-96 overflow-y-auto">
            <table className="min-w-full text-sm">
              <thead className="sticky top-0 bg-card">
                <tr className="border-b border-border">
                  <th className="text-left py-2 px-3">Name</th>
                  <th className="text-left py-2 px-3">Score</th>
                  <th className="text-left py-2 px-3">Lat</th>
                  <th className="text-left py-2 px-3">Lon</th>
                </tr>
              </thead>
              <tbody>
                {data.slice(0, 200).map((item, i) => (
                  <tr
                    key={i}
                    onClick={() => setSelectedItem(item)}
                    className="border-b border-border hover:bg-muted cursor-pointer"
                  >
                    <td className="py-2 px-3 font-medium text-foreground">{item.name}</td>
                    <td className="py-2 px-3">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded" style={{ background: getScoreColor(item.score) }} />
                        <span>{item.score?.toFixed(1) ?? "—"}</span>
                      </div>
                    </td>
                    <td className="py-2 px-3 text-muted-foreground">{item.lat?.toFixed(4) ?? "—"}</td>
                    <td className="py-2 px-3 text-muted-foreground">{item.lon?.toFixed(4) ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Selected item detail */}
          {selectedItem && (
            <div className="mt-3 bg-muted rounded-lg p-3 text-sm">
              <div className="font-medium text-foreground">{selectedItem.name}</div>
              <div className="text-muted-foreground mt-1">
                Score: {selectedItem.score?.toFixed(2)} |
                Location: {selectedItem.lat?.toFixed(4)}, {selectedItem.lon?.toFixed(4)}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
