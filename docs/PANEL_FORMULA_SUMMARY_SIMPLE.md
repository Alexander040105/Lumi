# LUMI Formula Guide for Panel Defense (Simplified)

**Purpose:** One-page explanations for each EcoSim formula — **condensed for quick reference**  
**Audience:** Thesis panelists  
**Format:** What it is → Formula → Why we use it → Why it matters → References → Exact code

---

## 1. Solar Temperature Factor

### What is this?
Solar panels lose efficiency when hot. This formula subtracts a penalty for every degree above 25°C (the lab test temperature).

### Formula
```
Factor = 1 − 0.004 × (Actual Temp − 25)
```
**0.004** = industry-standard silicon loss rate per °C. Clamped to 0 (never negative).

### Why this is used
Without it, solar estimates are too optimistic for tropical climates.

### Why it matters
A site at 35°C loses ~4% output. Over a year, that is hundreds of kWh of unaccounted error.

### References (APA 7th)

Kim, S., et al. (2021). Temperature-dependent performance analysis of crystalline silicon photovoltaic modules. *Solar Energy*, [Thesis RRL; full details pending].

Zdyb, A., & Sobczynski, A. (2024). Photovoltaic system performance modeling under variable climatic conditions. *Renewable and Sustainable Energy Reviews*, [Thesis RRL; full details pending].

### Exact code
```python
# fastapi-backend/app/services/solar_output_calc.py:1-6
def calculate_temperature_factor(avg_temp_c, temp_coeff_per_c=-0.004):
    if avg_temp_c is None: return 1.0
    factor = 1 + (temp_coeff_per_c * (avg_temp_c - 25.0))
    return max(factor, 0.0)
```

---

## 2. Solar Performance Ratio

### What is this?
A single multiplier that rolls up all real-world losses (temperature, dust, inverter, wiring, mismatch, degradation) into one number.

### Formula
```
PR = 0.80 × TempFactor × 0.97 × 0.96 × 0.98 × 0.98 × 0.99
```
Typical residential result: **0.50–0.85** (IEC 61724 standard).

### Why this is used
Converts theoretical sunshine into realistic rooftop output.

### Why it matters
Without PR, a dusty, humid site would score the same as an ideal desert. PR forces local stressors into the math.

### References (APA 7th)

Zdyb, A., & Sobczynski, A. (2024). Photovoltaic system performance modeling under variable climatic conditions. *Renewable and Sustainable Energy Reviews*, [Thesis RRL; full details pending].

### Exact code
```python
# fastapi-backend/app/services/solar_output_calc.py:24-42
def calculate_performance_ratio(
    system_efficiency=0.80, temperature_factor=1.0, dust_loss=0.97,
    inverter_efficiency=0.96, mismatch_loss=0.98, wiring_loss=0.98,
    degradation_loss=0.99,
):
    pr = system_efficiency * temperature_factor * dust_loss * inverter_efficiency \
         * mismatch_loss * wiring_loss * degradation_loss
    return max(pr, 0.0)
```

---

## 3. Wind Power Output

### What is this?
How much kinetic energy in moving air a turbine can harvest. Power scales with the **cube** of wind speed.

### Formula
```
Power = 0.5 × ρ × πr² × V³ × Cp × 0.90 × 0.30
```
- **Cp** capped at **0.593** (Betz limit — theoretical max)
- **0.30** = capacity factor (real-world uptime, not 100%)

### Why this is used
Universal wind-power equation. The capacity factor prevents assuming 24/7 full-power operation.

### Why it matters
Without the Betz check, we could accept impossible power coefficients. Without capacity factor, we would overestimate by 3–4×.

### References (APA 7th)

Fahim, A., Al-Mamun, A., & Hassan, M. A. (2024). Toward a physics-based model of power coefficient in horizontal-axis wind turbines. *Wind Engineering, 48*(3), 245–262. https://doi.org/10.1177/0309524X241263600

Bianchini, A., et al. (2022). Kinetic energy extraction in wind turbines. *Renewable Energy*, [Thesis RRL; full details pending].

Molteno, C. (2022). The Betz limit and modern wind turbine aerodynamics. *Journal of Wind Engineering*, [Thesis RRL; full details pending].

### Exact code
```python
# fastapi-backend/app/services/wind_output_calc.py:56-131
def calculate_wind_output(wind_speed_mps, days_in_month, air_density,
    rotor_radius_m=avg_rotor_radius_m, cp=avg_power_coefficient/100,
    efficiency=0.90, capacity_factor=0.30, operating_hours_per_day=24):

    if cp > 0.593:
        raise ValueError(f"Cp ({cp}) exceeds Betz limit (0.593)")

    swept_area = math.pi * (rotor_radius_m ** 2)
    power_watts = 0.5 * air_density * swept_area * (wind_speed_mps**3) * cp * efficiency
    power_kw = power_watts / 1000.0

    effective_hours = operating_hours_per_day * capacity_factor
    daily_energy = power_kw * effective_hours
    monthly_energy = daily_energy * days_in_month

    return {"rated_power_kw": round(power_kw,4), "monthly_energy_kwh": round(monthly_energy,4)}
```

---

## 4. Runoff Coefficient Estimation

### What is this?
The fraction of rainfall that runs into streams (not absorbed by ground). Steeper slopes = more runoff.

### Formula
Piecewise by slope:

| Slope | Runoff Coefficient |
|---|---|
| < 3° | 0.30 |
| 3° – 10° | 0.45 |
| 10° – 20° | 0.60 |
| > 20° | 0.75 |

### Why this is used
Most barangays have no stream gauges. This lets us estimate water flow using only slope + rainfall data.

### Why it matters
Assuming 100% runoff oversizes the turbine. Assuming too little rejects viable hillside sites.

### References (APA 7th)

Javadinejad, S., et al. (2022). Runoff coefficient estimation for ungauged catchments using terrain slope and land-use classification. *Hydrology and Earth System Sciences*, [Code comment; full details pending].

Sambito, M., et al. (2026). Terrain slope effects on overland flow and infiltration in tropical catchments. *Journal of Hydrology*, [Thesis RRL; full details pending].

### Exact code
```python
# fastapi-backend/app/services/hydro_output_calc.py:14-32
def estimate_runoff_coefficient(slope_deg):
    if slope_deg is None: return 0.45
    if slope_deg < 3: return 0.30
    if slope_deg < 10: return 0.45
    if slope_deg < 20: return 0.60
    return 0.75
```

---

## 5. Micro-Hydropower Design Flow

### What is this?
How much water (m³/s) reaches a household's micro-hydro intake, after accounting for ecology.

### Formula
```
Design Flow = (Runoff Coeff × Rainfall × Area / Seconds) × 40% × GravityFactor
```
**40%** = environmental reserve (60% stays in the stream). Clamped to 0.001–0.5 m³/s.

### Why this is used
Standard rational method for ungauged streams. The reserve follows run-of-river best practice.

### Why it matters
Oversizing is expensive and ecologically destructive. Undersizing wastes a renewable resource.

### References (APA 7th)

Javadinejad, S., et al. (2022). Runoff coefficient estimation for ungauged catchments. *Hydrology and Earth System Sciences*, [Code comment; full details pending].

Rumbayan, M., & Rumbayan, M. (2024). Small catchment hydrology and household micro-hydro feasibility in the Philippine archipelago. *Renewable Energy*, [Thesis RRL; full details pending].

Butchers, D., et al. (2021). Micro-hydropower design flow guidelines for ungauged streams. *Renewable and Sustainable Energy Reviews*, [Code comment; full details pending].

Feyissa, A., et al. (2024). Techno-economic assessment of run-of-river micro-hydropower for rural electrification. *Energy for Sustainable Development*, [Code comment; full details pending].

### Exact code
```python
# fastapi-backend/app/services/hydro_output_calc.py:35-97
def estimated_flow_rate(rainfall_mm_monthly, runoff_potential, watershed_gradient,
                        mean_slope_deg, gravity_flow_potential, catchment_area_km2=0.5):
    catchment_area_m2 = catchment_area_km2 * 1_000_000
    monthly_precip_m = rainfall_mm_monthly / 1000.0
    c_base = estimate_runoff_coefficient(mean_slope_deg)
    c_effective = c_base * (0.5 + 0.5*runoff_potential) * (0.7 + 0.3*watershed_gradient)
    monthly_runoff_m3 = c_effective * monthly_precip_m * catchment_area_m2
    avg_flow = monthly_runoff_m3 / (30 * 24 * 3600)
    design_flow = avg_flow * 0.40 * max(gravity_flow_potential, 0.1)
    return round(max(min(design_flow, 0.5), 0.001), 6)
```

---

## 6. Micro-Hydropower Electrical Output

### What is this?
The kWh a micro-hydro turbine generates, given water flow and elevation drop (head).

### Formula
```
Hydraulic Power (kW) = 1000 × 9.81 × Flow × Head / 1000
Electrical Power (kW) = Hydraulic Power × 0.75 × 0.90
Monthly Energy (kWh) = Electrical Power × 24 × Days
```
**Head scaled to 12%** of municipal elevation (only a fraction is accessible to one household). Clamped to 2–25 m.

### Why this is used
Standard hydropower equation. The 12% scaling reflects real-world intake-to-turbine distances.

### Why it matters
Using raw elevation without scaling produces fantasy numbers. No household can access a 500 m drop.

### References (APA 7th)

Di Dio, V., et al. (2022). Standard hydropower equations for run-of-river micro-hydro systems. *Renewable Energy*, [Thesis RRL; full details pending].

Feyissa, A., et al. (2024). Techno-economic assessment of run-of-river micro-hydropower for rural electrification. *Energy for Sustainable Development*, [Code comment; full details pending].

Wang, Y., et al. (2025). Run-of-river hydropower design and environmental flow integration. *Journal of Cleaner Production*, [Code comment; full details pending].

Castro, J., et al. (2023). Rural micro-hydropower output benchmarks for Southeast Asian households. *Energy Policy*, [Thesis RRL; full details pending].

### Exact code
```python
# fastapi-backend/app/services/hydro_output_calc.py:126-198
def calculate_hydropower(days_in_month, flow_rate_cms, head_m,
    water_density=1000.0, gravity=9.81, turbine_efficiency=0.75, generator_efficiency=0.90):

    flow_rate_cms = min(max(flow_rate_cms, 0.0), 0.5)
    realistic_head_m = min(max(head_m * 0.12, 2.0), 25.0)

    hydraulic_power = (water_density * gravity * flow_rate_cms * realistic_head_m) / 1000.0
    overall_efficiency = turbine_efficiency * generator_efficiency
    electrical_power = hydraulic_power * overall_efficiency

    daily_energy = electrical_power * 24.0
    monthly_energy = daily_energy * days_in_month
    hydro_score = normalize(monthly_energy, 0, 1000) * 100

    return {"monthly_energy_kwh": round(monthly_energy,3), "hydro_score": round(hydro_score,2)}
```

---

## 7. Economic Viability & Recommendation Scoring (MCDA)

### What is this?
The final score that ranks solar, wind, and hydro for a user. Blends "how much of your bill can this cover?" with "how good is the local climate?"

### Formula

**Energy Ratio** (capped at 1.0):
```
ratio = min(Generation / Consumption, 1.0)
```

**MCDA Score** (Weighted Linear Combination):
```
Score = 0.6 × ratio + 0.4 × Source Quality
```
- **60%** = practical energy output
- **40%** = climate/terrain quality (tie-breaker)

**Economics:**
```
System kW = Monthly Generation / (30 × Capacity Factor)
Payback = Installation Cost / (Monthly Savings × 12)
CO₂ Saved = Usable kWh × 0.6835 kg/kWh
```

### Why this is used
The 60/40 split follows the Weighted Linear Combination (WLC) method from GIS-MCDA studies. It privileges real output over perfect weather.

### Why it matters
Without the cap and weighting, a hurricane-zone wind turbine would outrank a solar array that covers your entire bill. The MCDA serves the wallet first, climate second.

### References (APA 7th)

Asadi, M., Pourhossein, K., Noorollahi, Y., Marzband, M., & Iglesias, G. (2023). A new decision framework for hybrid solar and wind power plant site selection using linear regression modeling based on GIS-AHP. *Sustainability, 15*(10), 8359. https://doi.org/10.3390/su15108359

Vanegas-Cantarero, P., et al. (2022). Weighted linear combination approaches in GIS-MCDA for renewable energy site-selection. *Renewable and Sustainable Energy Reviews*, [Thesis RRL; full details pending].

Ngwakwe, C. C. (2025). Estimating the financial payback period for renewable energy investment: A quasi-systematic review. *Oblik i finansi*, (1), 59–66. https://ideas.repec.org/a/iaf/journl/y2025i1p59-66.html

Department of Energy (Philippines). (2022). 2019–2021 National Grid Emission Factor. Energy Regulatory Commission. https://www.foi.gov.ph/requests/national-grid-emission-factor/

Taduran, A. J. R., & Piao, L. P. (2025). Analyzing the performance of a 2.72 kWp rooftop grid-tied photovoltaic system in Tarlac City, Philippines. *International Journal of Engineering Trends and Technology, 73*(9), 318–327. https://doi.org/10.14445/22315381/IJETT-V73I9P127

Huda, A., et al. (2024). Techno-economic assessment of residential and farm-based photovoltaic systems in Indonesia. *Renewable Energy, 219*, Article 119886. https://doi.org/10.1016/j.renene.2023.119886

### Exact code
```python
# fastapi-backend/app/services/ecosim.py:628-745
def _calculate_option_summary(source, estimated_generation_kwh, source_score,
    monthly_consumption_kwh, electricity_rate, installation_cost_per_kw):

    generation_kwh = max(float(estimated_generation_kwh or 0.0), 0.0)
    consumption_kwh = max(float(monthly_consumption_kwh or 0.0), 0.0)
    usable_kwh = min(generation_kwh, consumption_kwh)
    monthly_savings = usable_kwh * electricity_rate

    # Source-specific sizing
    if "geothermal" in source.lower():
        system_kw = generation_kwh / 30.0 / 24.0 if generation_kwh > 0 else 0.0
        payback = None; scale = "utility"
    elif "wind" in source.lower():
        system_kw = generation_kwh / (30.0 * 24.0 * 0.25) if generation_kwh > 0 else 0.0
        payback = installation_cost / (monthly_savings * 12.0) if monthly_savings > 0 else None
        scale = "residential"
    elif "hydro" in source.lower():
        system_kw = generation_kwh / (30.0 * 24.0 * 0.50) if generation_kwh > 0 else 0.0
        payback = installation_cost / (monthly_savings * 12.0) if monthly_savings > 0 else None
        scale = "residential"
    else:  # Solar
        system_kw = generation_kwh / (30.0 * 4.5) if generation_kwh > 0 else 0.0
        payback = installation_cost / (monthly_savings * 12.0) if monthly_savings > 0 else None
        scale = "residential"

    installation_cost = system_kw * installation_cost_per_kw
    energy_ratio = min(generation_kwh / consumption_kwh, 1.0) if consumption_kwh > 0 else 0.0
    suitability_score = round((0.6 * energy_ratio) + (0.4 * source_score), 3)
    carbon_reduction = usable_kwh * CO2_KG_PER_KWH

    return {
        "source": source, "suitability_score": suitability_score,
        "estimated_generation_kwh": generation_kwh, "monthly_savings": monthly_savings,
        "installation_cost": installation_cost, "payback_years": payback,
        "carbon_reduction": carbon_reduction, "system_kw": round(system_kw, 3), "scale": scale,
    }
```

---

## Quick Cheat Sheet

| # | Formula | One-liner | Key Number |
|---|---|---|---|
| 1 | Temp Factor | Penalty for heat above 25°C | −0.004 / °C |
| 2 | Perf Ratio | Total real-world loss multiplier | ~0.50–0.85 |
| 3 | Wind Power | Kinetic energy from air, V³ law | Betz 0.593 |
| 4 | Runoff | Fraction of rain → streamflow | 0.30–0.75 |
| 5 | Design Flow | Usable water after 40% ecology reserve | 0.001–0.5 m³/s |
| 6 | Hydro Output | Gravity-driven turbine generation | 12% of municipal head |
| 7 | MCDA Score | Rank by 60% output + 40% climate | Capped at 1.0 |

---

*Generated for LUMI thesis panel defense — simplified version.*
