export interface MunicipalityOption {
  municipality_id: number;
  name: string;
}

export interface MunicipalityListResponse {
  items: MunicipalityOption[];
}

export interface EcosimOption {
  source: string;
  suitability_score: number;
  estimated_generation_kwh: number;
  monthly_savings: number;
  installation_cost: number;
  payback_years: number | null;
  carbon_reduction: number;
  explanation: string;
}

export interface EcosimComparison {
  current_monthly_consumption_kwh: number;
  current_monthly_bill: number;
  renewable_monthly_consumption_kwh: number;
  renewable_monthly_bill: number;
}

export interface EcosimDashboardResponse {
  municipality: string;
  municipality_id: number;
  monthly_consumption_kwh: number;
  monthly_bill: number;
  recommended_source: string;
  suitability_score: number;
  estimated_generation_kwh: number;
  monthly_savings: number;
  installation_cost: number;
  payback_years: number | null;
  carbon_reduction: number;
  explanation: string;
  options: EcosimOption[];
  comparison: EcosimComparison;
}

export interface PostHouse {
  house_name: string;
  municipality: string;
  electricity_rate: number;
  current_electricity_bill: number;
  desired_savings: number;
}

export interface EcosimResponse {
  municipality_data: unknown[];
  consumption_results: {
    monthly_consumption_kwh: number;
    daily_consumption_kwh: number;
    target_monthly_consumption_kwh: number;
  };
  renewable_energy_results: {
    solar_output: unknown;
    hydro_output: unknown;
    wind_output: unknown;
  };
  ai_analysis: Record<string, unknown> | null;
}

export interface HealthResponse {
  status: string;
  service: string;
}

export interface ProtectedMeResponse {
  user: Record<string, unknown>;
}
