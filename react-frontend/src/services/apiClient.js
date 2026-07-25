import { getApiBaseUrl } from "../utils/env";

const BASE_URL = getApiBaseUrl();

export async function request(path, { token, ...options } = {}) {
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    let message = "Request failed";
    const text = await response.clone().text();
    try {
      const errorBody = JSON.parse(text);
      if (Array.isArray(errorBody.detail)) {
        message = errorBody.detail.map((d) => d.msg || String(d)).join("; ");
      } else if (typeof errorBody.detail === "string") {
        message = errorBody.detail;
      } else if (errorBody.message) {
        message = errorBody.message;
      } else {
        message = JSON.stringify(errorBody);
      }
    } catch {
      if (text) message = text;
    }
    throw new Error(message);
  }

  return response.json();
}

export function getHealth() {
  return request("/health/");
}

export function getProtectedMe(token) {
  return request("/protected/me", { token });
}

export function createItem(token, payload) {
  return request("/items/", {
    token,
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getEcosim(params) {
  const search = new URLSearchParams({
    municipality_id: params.municipalityId,
    monthly_consumption: params.monthlyConsumption,
    monthly_bill: params.monthlyBill,
  });
  if (params.desiredSavings !== undefined && params.desiredSavings !== null) {
    search.append("desired_savings", String(params.desiredSavings));
  }
  if (params.includeAi) {
    search.append("include_ai", "true");
  }
  if (params.useRag && params.ragQuery) {
    search.append("use_rag", "true");
    search.append("rag_query", params.ragQuery);
  }
  if (params.mode) {
    search.append("mode", params.mode);
  }

  return request(`/ecosim/?${search.toString()}`);
}

export function getMunicipalities() {
  return request("/ecosim/municipalities");
}

export function getProvinces() {
  return request("/ecosim/provinces");
}

export function getProductRecommendations(energyType, budgetPhp = null, limit = 5) {
  const params = new URLSearchParams({ energy_type: energyType, limit: String(limit) });
  if (budgetPhp) params.append("budget_php", String(budgetPhp));
  return request(`/products/recommend?${params.toString()}`);
}

export function browseProducts(filters = {}) {
  const params = new URLSearchParams();
  if (filters.category) params.append("category", filters.category);
  if (filters.subcategory) params.append("subcategory", filters.subcategory);
  if (filters.source_site) params.append("source_site", filters.source_site);
  if (filters.min_price) params.append("min_price", String(filters.min_price));
  if (filters.max_price) params.append("max_price", String(filters.max_price));
  params.append("page", String(filters.page || 1));
  params.append("page_size", String(filters.page_size || 20));
  return request(`/products/browse?${params.toString()}`);
}

export function getProductAudit() {
  return request("/products/audit");
}

export function getGeothermal(municipalityId) {
  return request(`/geothermal/${municipalityId}`);
}

// --- Forecasting ---

export function runForecast(metric = "consumption", orderP = 1, orderD = 1, orderQ = 1, forecastTo = 2030) {
  const params = new URLSearchParams({
    metric,
    order_p: String(orderP),
    order_d: String(orderD),
    order_q: String(orderQ),
    forecast_to: String(forecastTo),
  });
  return request(`/forecast/run?${params.toString()}`);
}

export function runBacktest(metric = "consumption", trainEndYear = 2020) {
  const params = new URLSearchParams({ metric, train_end_year: String(trainEndYear) });
  return request(`/forecast/backtest?${params.toString()}`);
}

export function getModelRuns(limit = 20) {
  return request(`/forecast/models?limit=${limit}`);
}

// --- Map / GIS ---

export function getSuitabilityMap(renewableType, level = "municipality") {
  return request(`/map/${renewableType}?level=${level}`);
}

export function getPsgcHierarchy(municipalityId = null, provinceId = null) {
  const params = new URLSearchParams();
  if (municipalityId) params.append("municipality_id", String(municipalityId));
  if (provinceId) params.append("province_id", String(provinceId));
  return request(`/map/psgc/hierarchy?${params.toString()}`);
}

export function getCoverageSummary(level = "municipality") {
  return request(`/map/coverage?level=${level}`);
}

// --- ETL ---

export function runClimateEtl() {
  return request("/etl/run/climate", { method: "POST" });
}

export function getLineage(source = null, table = null, limit = 50) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (source) params.append("source", source);
  if (table) params.append("table", table);
  return request(`/etl/lineage?${params.toString()}`);
}

// --- Chat ---

export function sendChatMessage(message, sessionId = null) {
  const body = { message };
  if (sessionId) body.session_id = sessionId;
  return request("/chat/", { method: "POST", body: JSON.stringify(body) });
}

export function getChatSessions() {
  return request("/chat/sessions");
}

export function getChatSessionMessages(sessionId) {
  return request(`/chat/sessions/${sessionId}`);
}

// --- Health ---

export function getDetailedHealth() {
  return request("/health/detailed");
}
