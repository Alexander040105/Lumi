import React, { useEffect, useMemo, useState } from "react";
import { MapPin, Layers, Map as MapIcon } from "lucide-react";

const METRIC_OPTIONS = [
  { value: "renewable_potential", label: "Renewable Potential" },
  { value: "solar_potential", label: "Solar Potential" },
  { value: "wind_potential", label: "Wind Potential" },
  { value: "hydro_potential", label: "Hydropower Potential" },
  { value: "geothermal_potential", label: "Geothermal Potential" },
  { value: "energy_consumption", label: "Energy Consumption" },
  { value: "peak_demand", label: "Peak Demand" },
  { value: "generation", label: "Generation" },
  { value: "forecasted_demand", label: "Forecasted Demand" },
];

const LEVEL_OPTIONS = [
  { value: "province", label: "Province" },
  { value: "municipality", label: "Municipality" },
];

const SUITABILITY_METRICS = [
  "renewable_potential",
  "solar_potential",
  "wind_potential",
  "hydro_potential",
  "geothermal_potential",
];

function isSuitabilityMetric(metric) {
  return SUITABILITY_METRICS.includes(metric);
}

function getColorForValue(value, metric) {
  if (value === null || value === undefined) {
    return "#94a3b8"; // slate-400 for no data
  }
  if (isSuitabilityMetric(metric)) {
    // 5-tier classification for all suitability metrics
    if (value >= 81) return "#15803d"; // green-700 — Very High
    if (value >= 61) return "#22c55e"; // green-500 — High
    if (value >= 41) return "#eab308"; // yellow-500 — Moderate
    if (value >= 21) return "#f97316"; // orange-500 — Low
    return "#ef4444"; // red-500 — Very Low
  }
  // For national metrics, single value — use a blue scale
  if (value > 100000) return "#1e40af";
  if (value > 50000) return "#3b82f6";
  if (value > 10000) return "#60a5fa";
  return "#93c5fd";
}

function getClassificationLabel(value) {
  if (value === null || value === undefined) return "No data";
  if (value >= 81) return "Very High";
  if (value >= 61) return "High";
  if (value >= 41) return "Moderate";
  if (value >= 21) return "Low";
  return "Very Low";
}

function formatFactors(factors) {
  // Supabase JSONB may return a string; parse lazily
  let parsed = factors;
  if (typeof factors === "string") {
    try { parsed = JSON.parse(factors); } catch { return factors; }
  }
  if (!parsed || typeof parsed !== "object") return "";
  const parts = [];
  for (const [key, val] of Object.entries(parsed)) {
    if (val !== null && val !== undefined) {
      const label = key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
      parts.push(`${label}: ${val}`);
    }
  }
  return parts.join("<br/>");
}

// ---------------------------------------------------------------------------
// GeoJSON localStorage cache — avoids re-downloading the large polygon file
// ---------------------------------------------------------------------------
const GEOJSON_CACHE_TTL_MS = 24 * 60 * 60 * 1000; // 24 hours

async function fetchGeoJsonCached(url) {
  const cacheKey = `lumi_geojson_${url}`;
  try {
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      const { ts, data } = JSON.parse(cached);
      if (Date.now() - ts < GEOJSON_CACHE_TTL_MS) {
        return data;
      }
    }
  } catch {
    // ignore parse errors
  }
  const resp = await fetch(url);
  if (!resp.ok) return null;
  const data = await resp.json();
  try {
    localStorage.setItem(cacheKey, JSON.stringify({ ts: Date.now(), data }));
  } catch {
    // ignore quota errors
  }
  return data;
}

function removeAccents(str) {
  return str
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

function normalizeGeoName(name) {
  if (!name) return "";
  return removeAccents(name)
    .toLowerCase()
    .trim()
    .replace(/^city of\s+/i, "")
    .replace(/^municipality of\s+/i, "")
    .replace(/\s+capital$/i, "")
    .replace(/\s+\(capital\)$/i, "")
    .replace(/\bsta\.?\b/g, "santa")
    .replace(/\bsto\.?\b/g, "santo")
    .replace(/\bsan\b/g, "san")
    .replace(/[-']/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

// ---------------------------------------------------------------------------
// Coordinate-based polygon matching — eliminates name-mismatch grey areas
// ---------------------------------------------------------------------------
function computeCentroid(geometry) {
  if (!geometry?.coordinates) return { lat: 0, lon: 0 };
  const coords = geometry.coordinates;
  const lats = [];
  const lons = [];

  function visit(c) {
    if (Array.isArray(c[0])) {
      c.forEach(visit);
    } else {
      lons.push(c[0]);
      lats.push(c[1]);
    }
  }
  visit(coords);

  if (lats.length === 0) return { lat: 0, lon: 0 };
  const lat = lats.reduce((a, b) => a + b, 0) / lats.length;
  const lon = lons.reduce((a, b) => a + b, 0) / lons.length;
  return { lat, lon };
}

function matchByCoordinates(geojson, data, maxDeg = 0.8) {
  // maxDeg ≈ 0.8° ≈ 90 km radius — generous enough for municipality centroids
  if (!geojson?.features || !data?.length) return {};

  // 1. Pre-compute centroids (skip null geometries), build lookup by original index
  const centroidByIdx = new Map();
  const centroidList = [];
  geojson.features.forEach((f, idx) => {
    const c = computeCentroid(f.geometry);
    if (c.lat !== 0 || c.lon !== 0) {
      const entry = { idx, ...c };
      centroidByIdx.set(idx, entry);
      centroidList.push(entry);
    }
  });

  // 2. For each data item, find nearest centroid
  const map = {};
  for (const item of data) {
    if (item.lat == null || item.lon == null) continue;

    let bestIdx = -1;
    let bestDist = Infinity;

    for (const c of centroidList) {
      const dLat = c.lat - item.lat;
      const dLon = c.lon - item.lon;
      const dist = dLat * dLat + dLon * dLon;
      if (dist < bestDist) {
        bestDist = dist;
        bestIdx = c.idx;
      }
    }

    if (bestIdx >= 0 && bestDist <= maxDeg * maxDeg) {
      // Prefer coordinate match, but if a feature already has a closer item, keep closer
      const existing = map[bestIdx];
      if (!existing) {
        map[bestIdx] = item;
      } else {
        const cent = centroidByIdx.get(bestIdx);
        if (cent) {
          const dLatE = cent.lat - existing.lat;
          const dLonE = cent.lon - existing.lon;
          const distE = dLatE * dLatE + dLonE * dLonE;
          if (bestDist < distE) {
            map[bestIdx] = item;
          }
        }
      }
    }
  }

  return map;
}

function FallbackMapGrid({ data, metric, level }) {
  if (!data || data.length === 0) return null;
  const labelKey = level === "municipality" ? "municipality" : "province";
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
      {data.map((item, idx) => {
        const hasData = item.value !== null && item.value !== undefined;
        const displayName = item[labelKey] || item.province || item.region;
        return (
          <div
            key={`${item.region}-${item.province || idx}-${item.municipality || ""}`}
            className="rounded-lg border p-3 text-center transition-transform hover:scale-[1.02]"
            style={{ borderLeft: `4px solid ${getColorForValue(item.value, metric)}` }}
          >
            <p className="text-xs text-muted-foreground truncate">
              {displayName}
            </p>
            <p className="mt-1 text-lg font-bold" style={{ color: getColorForValue(item.value, metric) }}>
              {hasData
                ? (isSuitabilityMetric(metric) ? `${item.value}` : item.value.toLocaleString())
                : "N/A"}
              {hasData && isSuitabilityMetric(metric) && <span className="text-xs ml-0.5">/100</span>}
            </p>
            {hasData && item.classification && (
              <p className="text-[10px] text-muted-foreground">{item.classification}</p>
            )}
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide">{metric.replace("_", " ")}</p>
          </div>
        );
      })}
    </div>
  );
}

function LeafletMap({ data, metric, level, geothermalPlants = [] }) {
  const [L, setL] = useState(null);
  const [RL, setRL] = useState(null);
  const [rawGeojson, setRawGeojson] = useState(null);

  const geojsonUrl =
    level === "municipality"
      ? "/philippine_geojson_file_per_provinces.min.json"
      : "/philippine_geojson_file_per_region.json";

  const nameProperty = level === "municipality" ? "adm3_en" : "adm2_en";

  // 1. Name-based lookup (fallback)
  const nameLookup = useMemo(() => {
    const map = {};
    for (const item of data) {
      const rawName = level === "municipality"
        ? item.municipality || ""
        : item.province || "";
      const key = normalizeGeoName(rawName);
      const altKey = rawName.toLowerCase().trim();
      if (key) {
        const entry = {
          value: item.value,
          classification: item.classification,
          factors: item.factors,
          province: item.province,
          municipality: item.municipality,
        };
        map[key] = entry;
        map[altKey] = entry;
      }
    }
    return map;
  }, [data, level]);

  // 2. Coordinate-based matching (primary) + name fallback
  const enrichedGeojson = useMemo(() => {
    if (!rawGeojson?.features) return null;

    const coordMap = matchByCoordinates(rawGeojson, data);

    const features = rawGeojson.features.map((feature, idx) => {
      // Try coordinate match first
      let matched = coordMap[idx];

      // Fallback to name match
      if (!matched) {
        const name = normalizeGeoName(feature.properties?.[nameProperty] || "");
        matched = nameLookup[name];
      }

      return {
        ...feature,
        properties: {
          ...feature.properties,
          _lumi_data: matched || null,
        },
      };
    });

    return { ...rawGeojson, features };
  }, [rawGeojson, data, nameLookup, nameProperty]);

  // Load Leaflet + GeoJSON once per level change
  useEffect(() => {
    let mounted = true;
    setRawGeojson(null);
    Promise.all([
      import("leaflet"),
      import("react-leaflet"),
      fetchGeoJsonCached(geojsonUrl),
    ])
      .then(([leafletMod, reactLeafletMod, geoData]) => {
        if (!mounted) return;
        const leaflet = leafletMod.default || leafletMod;
        const rl = reactLeafletMod;
        setL(leaflet);
        setRL(rl);
        setRawGeojson(geoData);
      })
      .catch(() => {
        // Silently fall back
      });
    return () => {
      mounted = false;
    };
  }, [geojsonUrl]);

  if (!L || !RL || !enrichedGeojson) {
    return <FallbackMapGrid data={data} metric={metric} level={level} />;
  }

  const { MapContainer, TileLayer, GeoJSON } = RL;

  const styleFeature = (feature) => {
    const item = feature.properties?._lumi_data;
    const val = item?.value ?? null;
    return {
      fillColor: getColorForValue(val, metric),
      weight: level === "municipality" ? 0.6 : 1.5,
      opacity: 1,
      color: "#64748b",
      dashArray: "",
      fillOpacity: level === "municipality" ? 0.6 : 0.65,
    };
  };

  const onEachFeature = (feature, layer) => {
    const geoName = feature.properties?.[nameProperty] || "Unknown";
    const item = feature.properties?._lumi_data;
    const hasData = item && item.value !== null && item.value !== undefined;
    const displayName = item?.municipality || geoName;
    const province = item?.province || "";

    let tooltipHtml = `<div style="font-family:sans-serif;font-size:13px;line-height:1.4;min-width:160px">
      <div style="font-size:14px;font-weight:600;color:#111827;margin-bottom:2px">${displayName}</div>`;

    if (level === "municipality" && province) {
      tooltipHtml += `<div style="color:#64748b;font-size:12px;margin-bottom:4px">${province}</div>`;
    }

    if (hasData) {
      const unit = isSuitabilityMetric(metric) ? "/100" : metric.includes("demand") ? " MW" : " GWh";
      const color = getColorForValue(item.value, metric);
      tooltipHtml += `<div style="margin-top:4px">
        <span style="color:#64748b;font-size:12px">${metric.replace(/_/g, " ")}:</span>
        <strong style="font-size:14px;color:${color}">${item.value.toLocaleString()}${unit}</strong>
      </div>`;
      if (item.classification) {
        tooltipHtml += `<div style="margin-top:2px;font-size:12px;color:${color};font-weight:500">${item.classification}</div>`;
      }
      const factorsHtml = formatFactors(item.factors);
      if (factorsHtml) {
        tooltipHtml += `<div style="margin-top:6px;padding-top:4px;border-top:1px solid #e2e8f0;color:#64748b;font-size:11px;line-height:1.5">${factorsHtml}</div>`;
      }
    } else {
      tooltipHtml += `<div style="margin-top:4px;color:#94a3b8;font-size:12px">No data available</div>`;
    }

    tooltipHtml += `</div>`;
    layer.bindTooltip(tooltipHtml, { sticky: true, className: "lumi-tooltip" });
  };

  // Filter operating plants for markers
  const showPlantMarkers = metric === "geothermal_potential";
  const operatingPlants = geothermalPlants.filter((p) => p.status === "operating");

  return (
    <div className="rounded-xl border overflow-hidden" style={{ height: 480 }}>
      <MapContainer
        center={[12.8797, 121.774]}
        zoom={level === "municipality" ? 7 : 6}
        scrollWheelZoom={false}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />
        <GeoJSON data={enrichedGeojson} style={styleFeature} onEachFeature={onEachFeature} />
        {showPlantMarkers && L && RL && operatingPlants.map((p) => {
          const icon = L.divIcon({
            className: "",
            html: `<div style="width:14px;height:14px;border-radius:50%;background:#f97316;border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,0.3);"></div>`,
            iconSize: [14, 14],
            iconAnchor: [7, 7],
          });
          return (
            <RL.Marker
              key={p.project_name + (p.unit_name || "")}
              position={[p.latitude, p.longitude]}
              icon={icon}
            >
              <RL.Popup>
                <div style={{ fontFamily: "sans-serif", fontSize: 13, lineHeight: 1.4, minWidth: 160 }}>
                  <div style={{ fontWeight: 600, color: "#111827", marginBottom: 4 }}>
                    {p.project_name}
                  </div>
                  <div style={{ color: "#64748b", fontSize: 12 }}>
                    {p.capacity_mw !== null && p.capacity_mw !== undefined ? `${p.capacity_mw} MW` : ""}
                    {p.technology ? ` · ${p.technology}` : ""}
                  </div>
                  <div style={{ color: "#64748b", fontSize: 12, marginTop: 2 }}>
                    Status: <span style={{ color: "#15803d", fontWeight: 500 }}>{p.status}</span>
                  </div>
                  {p.wiki_url && (
                    <div style={{ marginTop: 6 }}>
                      <a
                        href={p.wiki_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ color: "#2563eb", fontSize: 12 }}
                      >
                        View on GEM Wiki →
                      </a>
                    </div>
                  )}
                </div>
              </RL.Popup>
            </RL.Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}

function EnergyMap({ mapData, metric, level, onMetricChange, onLevelChange, mapLoading = false, geothermalPlants = [] }) {
  const [leafletReady, setLeafletReady] = useState(false);

  useEffect(() => {
    import("leaflet")
      .then(() => setLeafletReady(true))
      .catch(() => setLeafletReady(false));
  }, []);

  const data = mapData?.items || [];

  const showSuitabilityLegend = isSuitabilityMetric(metric);

  return (
    <div className="rounded-xl border bg-card p-6 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <MapPin className="h-5 w-5 text-emerald-500" />
            Energy Choropleth Map
          </h3>
          <p className="text-sm text-muted-foreground">
            {showSuitabilityLegend
              ? `${level === "municipality" ? "Municipality-level" : "Province-level"} renewable potential derived from climate & terrain data`
              : "National-level metric (DOE data is not disaggregated below grid level)"}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Level toggle */}
          <div className="flex items-center gap-1.5 rounded-md border bg-background px-2 py-1">
            <MapIcon className="h-3.5 w-3.5 text-muted-foreground" />
            <select
              className="bg-transparent text-sm focus:outline-none"
              value={level}
              onChange={(e) => onLevelChange(e.target.value)}
            >
              {LEVEL_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Metric selector */}
          <div className="flex items-center gap-1.5 rounded-md border bg-background px-2 py-1">
            <Layers className="h-3.5 w-3.5 text-muted-foreground" />
            <select
              className="bg-transparent text-sm focus:outline-none"
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
      </div>

      {mapLoading && (
        <div className="mt-4 flex items-center justify-center gap-2 text-sm text-muted-foreground" style={{ height: 480 }}>
          <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
          Loading map data...
        </div>
      )}

      {!mapLoading && (
        <div className="mt-4">
          {leafletReady ? (
            <LeafletMap data={data} metric={metric} level={level} geothermalPlants={geothermalPlants} />
          ) : (
            <FallbackMapGrid data={data} metric={metric} level={level} />
          )}
        </div>
      )}

      {showSuitabilityLegend && (
        <div className="mt-3 flex flex-wrap gap-3 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded-sm bg-green-700" />
            Very High (81-100)
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded-sm bg-green-500" />
            High (61-80)
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded-sm bg-yellow-500" />
            Moderate (41-60)
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded-sm bg-orange-500" />
            Low (21-40)
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-3 w-3 rounded-sm bg-red-500" />
            Very Low (0-20)
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

export default React.memo(EnergyMap);
