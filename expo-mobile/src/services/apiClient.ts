import { getApiBaseUrl } from '@/utils/env';

const BASE_URL = getApiBaseUrl();

async function request<T>(
  path: string,
  { token, ...options }: { token?: string } & RequestInit = {}
): Promise<T> {
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  if (!headers.has('Content-Type') && options.body) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || 'Request failed');
  }

  return response.json() as Promise<T>;
}

export function getHealth() {
  return request<import('@/types').HealthResponse>('/health/');
}

export function getProtectedMe(token: string) {
  return request<import('@/types').ProtectedMeResponse>('/protected/me', {
    token,
  });
}

export function getEcosim(params: {
  municipalityId: string;
  monthlyConsumption: string;
  monthlyBill: string;
}) {
  const search = new URLSearchParams({
    municipality_id: params.municipalityId,
    monthly_consumption: params.monthlyConsumption,
    monthly_bill: params.monthlyBill,
  });
  return request<import('@/types').EcosimDashboardResponse>(
    `/ecosim/?${search.toString()}`
  );
}

export function getMunicipalities() {
  return request<import('@/types').MunicipalityListResponse>(
    '/ecosim/municipalities'
  );
}

export function postEcosim(
  body: import('@/types').PostHouse,
  include_ai = true,
  use_rag = true,
  rag_query?: string
) {
  const search = new URLSearchParams();
  search.set('include_ai', String(include_ai));
  search.set('use_rag', String(use_rag));
  if (rag_query) search.set('rag_query', rag_query);

  return request<import('@/types').EcosimResponse>(`/ecosim/?${search.toString()}`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export function storeSession(token: string, payload: unknown, ttl_seconds = 3600) {
  const query = new URLSearchParams();
  query.set('ttl_seconds', String(ttl_seconds));
  return request<{ stored: boolean; key: string }>(`/protected/session?${query.toString()}`, {
    token,
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
