from pydantic import BaseModel, Field


class GetHouse(BaseModel):
    municipality : str
    # pesos per kilowhuttttttttt-hour
    electricity_rate : float = 14.35
    current_electricity_bill : float = 0.0
    # default is 50% savings but users may change it blah blah blah
    desired_savings : float = Field(0.50, ge=0.0, le=1.0)


class PostHouse(BaseModel):
    # NOTE: We'll get the house name to label the current house the user puts so that in case some of them got more than one house, they can easily identify which one is which
    house_name: str
    municipality: str
    # pesos per kilowhuttttttttt-hour
    electricity_rate : float
    current_electricity_bill : float
    # default is 50% savings but users may change it blah blah blah
    desired_savings : float = Field(..., ge=0.0, le=1.0)


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


class HydroOutput(BaseModel):
    system_kwp: float
    daily_hydro_output: float
    monthly_hydro_output: float
    annual_hydro_output: float
    hydro_score: float


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


class WindOutput(BaseModel):
    swept_area_m2: float
    rated_power_kw: float
    capacity_factor: float
    daily_energy_kwh: float
    monthly_energy_kwh: float
    annual_wind_output_kwh: float


class RenewableEnergyResults(BaseModel):
    municipality: str | None = None
    municipality_id: int | None = None
    climate: dict | None = None
    assumptions: dict | None = None
    solar_output: SolarOutput
    hydro_output: HydroOutput
    wind_output: WindOutput
    geothermal_output: GeothermalOutput
    consumption_results: ConsumptionResults


class EcosimResponse(BaseModel):
    municipality_data: list[MunicipalityClimate]
    consumption_results: ConsumptionResults
    renewable_energy_results: RenewableEnergyResults
    ai_analysis: dict | None = None


class EcosimQueryParams(BaseModel):
    municipality_id: int = Field(..., gt=0)
    monthly_consumption: float = Field(..., gt=0)
    monthly_bill: float = Field(..., gt=0)
    desired_savings: float = Field(0.50, ge=0.0, le=1.0)


class EcosimOption(BaseModel):
    source: str
    suitability_score: float
    estimated_generation_kwh: float
    monthly_savings: float
    installation_cost: float
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
    monthly_consumption_kwh: float
    monthly_bill: float
    recommended_source: str
    suitability_score: float
    estimated_generation_kwh: float
    monthly_savings: float
    installation_cost: float
    payback_years: float | None = None
    carbon_reduction: float
    explanation: str
    options: list[EcosimOption]
    comparison: EcosimComparison
    climate: dict | None = None
    renewable_energy_results: RenewableEnergyResults | None = None
    consumption_results: ConsumptionResults | None = None
    municipality_data: list[MunicipalityClimate] | None = None
    ai_analysis: dict | None = None


class MunicipalityOption(BaseModel):
    municipality_id: int
    name: str


class MunicipalityListResponse(BaseModel):
    items: list[MunicipalityOption]


# we get house list in order for the users to have more than one house on their accounts
class HouseList(BaseModel):
    items: list[PostHouse]
