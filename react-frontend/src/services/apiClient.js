import { getApiBaseUrl } from "../utils/env";

const BASE_URL = getApiBaseUrl();

async function request(path, { token, ...options } = {}) {
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
    const message = await response.text();
    throw new Error(message || "Request failed");
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
    monthly_bill: params.monthlyBill
  });

  return request(`/ecosim/?${search.toString()}`);
}

export function getMunicipalities() {
  return request("/ecosim/municipalities");
}
