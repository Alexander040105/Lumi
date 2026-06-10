import { useEffect, useMemo, useRef, useState } from "react";
import { MapPin, Layers } from "lucide-react";

const METRIC_OPTIONS = [
  { value: "renewable_potential", label: "Renewable Potential" },
  { value: "energy_consumption", label: "Energy Consumption" },
  { value: "peak_demand", label: "Peak Demand" },
  { value: "generation", label: "Generation" },
  { value: "forecasted_demand", label: "Forecasted Demand" },
];

function getColorForValue(value, metric) {
  if (value === null || value === undefined) {
    return "#94a3b8"; // slate-400 for no data
  }
  if (metric === "renewable_potential") {
    if (value >= 70) return "#15803d";
    if (value >= 50) return "#22c55e";
    if (value >= 30) return "#eab308";
    return "#ef4444";
  }
  // For national metrics, single value — use a blue scale
  if (value > 100000) return "#1e40af";
  if (value > 50000) return "#3b82f6";
  if (value > 10000) return "#60a5fa";
  return "#93c5fd";
}

function FallbackMapGrid({ data, metric }) {
  if (!data || data.length === 0) return null;
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
      {data.map((item, idx) => {
        const hasData = item.value !== null && item.value !== undefined;
        return (
          <div
            key={`${item.region}-${item.province || idx}`}
            className="rounded-lg border p-3 text-center transition-transform hover:scale-[1.02]"
            style={{ borderLeft: `4px solid ${getColorForValue(item.value, metric)}` }}
          >
            <p className="text-xs text-muted-foreground truncate">
              {item.province || item.region}
            </p>
            <p className="mt-1 text-lg font-bold" style={{ color: getColorForValue(item.value, metric) }}>
              {hasData
                ? (metric === "renewable_potential" ? `${item.value}` : item.value.toLocaleString())
                : "N/A"}
              {hasData && metric === "renewable_potential" && <span className="text-xs ml-0.5">/100</span>}
            </p>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide">{metric.replace("_", " ")}</p>
          </div>
        );
      })}
    </div>
  );
}

function LeafletMap({ data, metric }) {
  const mapRef = useRef(null);
  const [L, setL] = useState(null);
  const [RL, setRL] = useState(null);
  const [geojson, setGeojson] = useState(null);

  const valueByProvince = useMemo(() => {
    const map = {};
    for (const item of data) {
      const key = (item.province || "").toLowerCase().trim();
      if (key) map[key] = item.value;
    }
    return map;
  }, [data]);

  useEffect(() => {
    let mounted = true;
    Promise.all([
      import("leaflet"),
      import("react-leaflet"),
      fetch("/philippine_geojson_file_per_region.json").then((r) => (r.ok ? r.json() : null)),
    ])
      .then(([leafletMod, reactLeafletMod, geoData]) => {
        if (!mounted) return;
        const leaflet = leafletMod.default || leafletMod;
        const rl = reactLeafletMod;
        setL(leaflet);
        setRL(rl);
        setGeojson(geoData);
      })
      .catch(() => {
        // Silently fall back — outer component handles it
      });
    return () => {
      mounted = false;
    };
  }, []);

  if (!L || !RL || !geojson) {
    return <FallbackMapGrid data={data} metric={metric} />;
  }

  const { MapContainer, TileLayer, GeoJSON } = RL;

  const styleFeature = (feature) => {
    const name = (feature.properties?.adm2_en || "").toLowerCase().trim();
    const val = valueByProvince[name] || 0;
    return {
      fillColor: getColorForValue(val, metric),
      weight: 1.5,
      opacity: 1,
      color: "#64748b",
      dashArray: "",
      fillOpacity: 0.65,
    };
  };

  const onEachFeature = (feature, layer) => {
    const name = feature.properties?.adm2_en || "Unknown";
    const rawVal = valueByProvince[name.toLowerCase().trim()];
    const hasData = rawVal !== null && rawVal !== undefined;
    const unit = metric === "renewable_potential" ? "/100" : metric.includes("demand") ? " MW" : " GWh";
    const valueText = hasData ? `${rawVal.toLocaleString()}${unit}` : "No data";
    layer.bindTooltip(
      `<div style="font-family:sans-serif;font-size:13px">
        <strong>${name}</strong><br/>
        ${metric.replace("_", " ")}: <strong>${valueText}</strong>
       </div>`,
      { sticky: true }
    );
  };

  return (
    <div className="rounded-xl border overflow-hidden" style={{ height: 480 }}>
      <MapContainer
        center={[12.8797, 121.774]}
        zoom={6}
        scrollWheelZoom={false}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />
        <GeoJSON data={geojson} style={styleFeature} onEachFeature={onEachFeature} />
      </MapContainer>
    </div>
  );
}

export default function EnergyMap({ mapData, metric, onMetricChange }) {
  const [leafletReady, setLeafletReady] = useState(false);

  useEffect(() => {
    import("leaflet")
      .then(() => setLeafletReady(true))
      .catch(() => setLeafletReady(false));
  }, []);

  const data = mapData?.items || [];

  return (
    <div className="rounded-xl border bg-card p-6 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <MapPin className="h-5 w-5 text-emerald-500" />
            Energy Choropleth Map
          </h3>
          <p className="text-sm text-muted-foreground">
            {metric === "renewable_potential"
              ? "Province-level renewable potential derived from climate & terrain data"
              : "National-level metric (DOE data is not disaggregated below grid level)"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Layers className="h-4 w-4 text-muted-foreground" />
          <select
            className="rounded-md border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            value={metric}
            onChange={(e) => onMetricChange(e.target.value)}
          >
            {METRIC_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="mt-4">
        {leafletReady ? (
          <LeafletMap data={data} metric={metric} />
        ) : (
          <FallbackMapGrid data={data} metric={metric} />
        )}
      </div>

      {metric === "renewable_potential" && (
        <div className="mt-3 flex flex-wrap gap-3 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded-sm bg-green-700" />
            High (70+)
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded-sm bg-green-500" />
            Good (50-69)
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded-sm bg-yellow-500" />
            Moderate (30-49)
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded-sm bg-red-500" />
            Low (&lt;30)
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded-sm bg-slate-400" />
            No data
          </span>
        </div>
      )}
    </div>
  );
}
