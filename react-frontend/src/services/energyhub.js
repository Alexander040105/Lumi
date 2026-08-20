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

export function getEnergyHubAiInsight(useLlm = false) {
  return request(`${ENERGYHUB_BASE}/ai-insight?use_llm=${useLlm}`);
}

export function getGeothermalSummary() {
  return request("/geothermal/ecohub/geothermal-summary");
}

export function getGeothermalPlants() {
  return request("/geothermal/plants");
}

export function getProvincialDemand(region = null) {
  const qs = region ? `?region=${encodeURIComponent(region)}` : "";
  return request(`${ENERGYHUB_BASE}/provincial-demand${qs}`);
}

export function getIrenaOverview() {
  return request(`${ENERGYHUB_BASE}/irena/overview`);
}

export function getIrenaCapacity(year = null) {
  const qs = year ? `?year=${year}` : "";
  return request(`${ENERGYHUB_BASE}/irena/capacity${qs}`);
}

export function getIrenaGeneration(year = null) {
  const qs = year ? `?year=${year}` : "";
  return request(`${ENERGYHUB_BASE}/irena/generation${qs}`);
}

export function getIrenaRenewableShare() {
  return request(`${ENERGYHUB_BASE}/irena/renewable-share`);
}

export function getMeralcoRate(year = null) {
  const qs = year ? `?year=${year}` : "";
  return request(`${ENERGYHUB_BASE}/meralco-rate${qs}`);
}

export function getSolarAtlas(location = null) {
  const qs = location ? `?location=${encodeURIComponent(location)}` : "";
  return request(`${ENERGYHUB_BASE}/solar-atlas${qs}`);
}

export function analyzeChart(chartType, chartData, forceRefresh = false) {
  const qs = forceRefresh ? "?force_refresh=true" : "";
  return request(`${ENERGYHUB_BASE}/analyze-chart${qs}`, {
    method: "POST",
    body: JSON.stringify({ chart_type: chartType, chart_data: chartData }),
  });
}

export function getEnergyHubMapExplanation(metric, level = "province", forceRefresh = false) {
  const params = new URLSearchParams({
    metric,
    level,
    force_refresh: forceRefresh ? "true" : "false",
  });
  return request(`${ENERGYHUB_BASE}/map-explanation?${params.toString()}`);
}
