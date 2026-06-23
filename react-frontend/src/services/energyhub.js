import { request } from "./apiClient";

const ENERGYHUB_BASE = "/energyhub";

export function getEnergyHubOverview() {
  return request(`${ENERGYHUB_BASE}/overview`);
}

export function getEnergyHubForecast(metric = "consumption") {
  return request(`${ENERGYHUB_BASE}/forecast?metric=${encodeURIComponent(metric)}`);
}

export function getEnergyHubTrends() {
  return request(`${ENERGYHUB_BASE}/trends`);
}

export function getEnergyHubMapData(metric = "renewable_potential", level = "province") {
  return request(
    `${ENERGYHUB_BASE}/map-data?metric=${encodeURIComponent(metric)}&level=${encodeURIComponent(level)}`
  );
}

export function getEnergyHubSourceBreakdown(year) {
  const qs = year ? `?year=${year}` : "";
  return request(`${ENERGYHUB_BASE}/source-breakdown${qs}`);
}

export function getEnergyHubGridBreakdown(year) {
  const qs = year ? `?year=${year}` : "";
  return request(`${ENERGYHUB_BASE}/grid-breakdown${qs}`);
}

export function getEnergyHubModelComparison() {
  return request(`${ENERGYHUB_BASE}/model-comparison`);
}

export function getEnergyHubAiInsight(useLlm = false, token) {
  return request(`${ENERGYHUB_BASE}/ai-insight?use_llm=${useLlm}`, { token });
}

export function getGeothermalSummary() {
  return request("/geothermal/ecohub/geothermal-summary");
}

export function getGeothermalPlants() {
  return request("/geothermal/plants");
}

export function analyzeChart(chartType, chartData, forceRefresh = false, token) {
  const qs = forceRefresh ? "?force_refresh=true" : "";
  return request(`${ENERGYHUB_BASE}/analyze-chart${qs}`, {
    token,
    method: "POST",
    body: JSON.stringify({ chart_type: chartType, chart_data: chartData }),
  });
}
