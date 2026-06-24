import { getApiBaseUrl } from "../utils/env";

const BASE_URL = getApiBaseUrl();

function getStoredToken() {
  try {
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith("sb-") && key.endsWith("-auth-token")) {
        const session = JSON.parse(localStorage.getItem(key));
        return session?.access_token || null;
      }
    }
  } catch {}
  return null;
}

export async function request(path, { token, ...options } = {}) {
  const headers = new Headers(options.headers || {});
  const effectiveToken = token || getStoredToken();
  if (effectiveToken) {
    headers.set("Authorization", `Bearer ${effectiveToken}`);
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

  return request(`/ecosim/?${search.toString()}`);
}

export function getMunicipalities() {
  return request("/ecosim/municipalities");
}

export function getGeothermal(municipalityId) {
  return request(`/geothermal/${municipalityId}`);
}
