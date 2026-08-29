from pydantic import BaseModel, Field


class PostHouse(BaseModel):
    # NOTE: We'll get the house name to label the current house the user puts so that in case some of them got more than one house, they can easily identify which one is which
    house_name: str
    municipality: str
    # pesos per kilowhuttttttttt-hour
    electricity_rate : float
    current_electricity_bill : float
    # default is 50% savings but users may change it blah blah blah
    desired_savings : float = Field(..., ge=0.0, le=1.0)
    mode: str = Field(default="municipality", pattern="^(municipality|province|barangay)$")


class ProvinceOption(BaseModel):
    province_id: int
    name: str


class ProvinceListResponse(BaseModel):
    items: list[ProvinceOption]


class MunicipalityClimate(BaseModel):
    municipality_id: int
    avg_t2m: float
    avg_t2m_max: float
    avg_t2m_min: float
    avg_rh2m: float
    avg_prectotcorr: float
    avg_ws10m: float
    avg_allsky_sfc_sw_dwn: float
    avg_cloud_amt: float
    avg_surface_pressure: float


class ConsumptionResults(BaseModel):
    monthly_consumption_kwh: float
    daily_consumption_kwh: float
    target_monthly_consumption_kwh: float


class SolarOutput(BaseModel):
    system_kwp: float
    daily_solar_output: float
    monthly_solar_output: float
    annual_solar_output: float
    solar_score: float | None = None
    generation_score: float | None = None


class HydroOutput(BaseModel):
    system_kwp: float
    daily_hydro_output: float
    monthly_hydro_output: float
    annual_hydro_output: float
    hydro_score: float
    generation_score: float | None = None


class GeothermalOutput(BaseModel):
    energy_type: str = "geothermal"
    suitability_score: float | None = None
    classification: str | None = None
    reservoir_temperature_c: float | None = None
    thermal_power_mw: float | None = None
    electric_power_mw: float | None = None
    daily_energy_kwh: float | None = None
    monthly_energy_kwh: float | None = None
    annual_energy_kwh: float | None = None
    annual_energy_gwh: float | None = None
    confidence: float | None = None
    source: str | None = None
    assumption: str | None = None
    citation: str | None = None


class WindOutput(BaseModel):
    swept_area_m2: float
    rated_power_kw: float
    capacity_factor: float
    daily_energy_kwh: float
    monthly_energy_kwh: float
    annual_wind_output_kwh: float
    generation_score: float | None = None
    wind_score: float | None = None


class RenewableEnergyResults(BaseModel):
    municipality: str | None = None
    municipality_id: int | None = None
    climate: dict | None = None
    assumptions: dict | None = None
    solar_output: SolarOutput
    hydro_output: HydroOutput
    wind_output: WindOutput
    geothermal_output: GeothermalOutput | None = None
    consumption_results: ConsumptionResults


class EcosimResponse(BaseModel):
    municipality_data: list[MunicipalityClimate]
    consumption_results: ConsumptionResults
    renewable_energy_results: RenewableEnergyResults
    ai_analysis: dict | None = None
    remaining_anonymous_requests: int | None = None
    province: str | None = None


class EcosimQueryParams(BaseModel):
    municipality_id: int = Field(..., gt=0)
    monthly_consumption: float = Field(..., gt=0)
    monthly_bill: float = Field(..., gt=0)
    electricity_rate: float | None = None
    desired_savings: float = Field(0.50, ge=0.0, le=1.0)
    mode: str = Field(default="municipality", pattern="^(municipality|province|barangay)$")


class EcosimOption(BaseModel):
    source: str
    suitability_score: float
    estimated_generation_kwh: float
    monthly_output: float | None = None
    generation_score: float | None = None
    source_type: str | None = None
    monthly_savings: float | None = None
    installation_cost: float | None = None
    payback_years: float | None = None
    carbon_reduction: float
    explanation: str


class EcosimComparison(BaseModel):
    current_monthly_consumption_kwh: float
    current_monthly_bill: float
    renewable_monthly_consumption_kwh: float
    renewable_monthly_bill: float


class EcosimDashboardResponse(BaseModel):
    municipality: str
    municipality_id: int
    province: str | None = None
    mode: str = "municipality"
    monthly_consumption_kwh: float
    user_consumption_kwh: float | None = None
    effective_consumption_kwh: float | None = None
    monthly_bill: float
    input_warning: bool = False
    recommended_source: str
    suitability_score: float
    generation_score: float | None = None
    source_type: str | None = None
    estimated_generation_kwh: float
    monthly_savings: float | None = None
    installation_cost: float | None = None
    payback_years: float | None = None
    carbon_reduction: float
    explanation: str
    options: list[EcosimOption]
    comparison: EcosimComparison | None = None
    climate: dict | None = None
    renewable_energy_results: RenewableEnergyResults | None = None
    consumption_results: ConsumptionResults | None = None
    municipality_data: list[MunicipalityClimate] | None = None
    ai_analysis: dict | None = None
    remaining_anonymous_requests: int | None = None
    # Hidden: suitability-score-based recommendation (for future reactivation)
    suitability_recommended_source: str | None = None
    suitability_recommended_score: float | None = None


class EcosimAIResponse(BaseModel):
    ai_analysis: dict | None = None
    remaining_anonymous_requests: int | None = None


class MunicipalityOption(BaseModel):
    municipality_id: int
    name: str
    province_name: str | None = None


class MunicipalityListResponse(BaseModel):
    items: list[MunicipalityOption]


class BarangayOption(BaseModel):
    barangay_id: int
    name: str
    municipality_id: int


class BarangayListResponse(BaseModel):
    items: list[BarangayOption]


# we get house list in order for the users to have more than one house on their accounts
class HouseList(BaseModel):
    items: list[PostHouse]
