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
