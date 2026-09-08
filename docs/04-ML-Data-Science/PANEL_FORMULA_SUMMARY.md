# LUMI Formula Guide for Panel Defense

**Purpose:** One-page explanations for each EcoSim formula  
**Audience:** Thesis panelists  
**Format:** What it is → The formula → Why we use it → Why it matters → Studies that back it up → Exact code

---

## 1. Solar Temperature Factor

### What is this?
Solar panels are tested at 25°C. In the Philippines, ambient temperatures often exceed that. This formula adjusts the power output downward for every degree above 25°C.

### Formula (simplified)
```
Temperature Factor = 1 − 0.004 × (Actual Temperature − 25)
```
- **0.004** = industry-standard loss per °C for silicon panels
- **Result clamped to 0** so we never predict negative power

### Why this is used
Without this correction, solar estimates would be too optimistic for tropical climates. It converts standard test-condition ratings into real-world expectations.

### Why is it important
A municipality at 35°C loses roughly 4% output versus the sticker rating. At 40°C, the loss is 6%. Over a whole year, that is hundreds of kilowatt-hours of unaccounted error if we ignore it.

### Reference studies (APA 7th)

Kim, S., et al. (2021). Temperature-dependent performance analysis of crystalline silicon photovoltaic modules. *Solar Energy*, [Reconstructed from thesis text; full details pending].

Zdyb, A., & Sobczynski, A. (2024). Photovoltaic system performance modeling under variable climatic conditions. *Renewable and Sustainable Energy Reviews*, [Reconstructed from thesis text; full details pending].

### Exact code
```python
# fastapi-backend/app/services/solar_output_calc.py:1-6
def calculate_temperature_factor(avg_temp_c: float | None, temp_coeff_per_c: float = -0.004) -> float:
    if avg_temp_c is None:
        return 1.0
    reference_temp_c = 25.0
    factor = 1 + (temp_coeff_per_c * (avg_temp_c - reference_temp_c))
    return max(factor, 0.0)
```

---

## 2. Solar Performance Ratio

### What is this?
A single multiplier that rolls up every real-world loss — temperature, dust, inverter, wiring, mismatch, and degradation — into one number. Think of it as "how much of the theoretical sunshine actually becomes usable electricity."

### Formula (simplified)
```
Performance Ratio = System Efficiency × Temperature Factor × Dust Loss × Inverter Efficiency × Mismatch Loss × Wiring Loss × Degradation Loss
```
Typical result: **0.50 to 0.85** for residential systems.

### Why this is used
It is the international standard (IEC 61724) for translating irradiance-based theory into realistic output. We use it so our solar numbers reflect actual rooftop conditions, not laboratory perfection.

### Why is it important
If we skipped this step, a user in a dusty, humid province would see the same solar score as a user in an ideal desert climate. The ratio forces the model to account for local stressors.

### Reference studies (APA 7th)

Zdyb, A., & Sobczynski, A. (2024). Photovoltaic system performance modeling under variable climatic conditions. *Renewable and Sustainable Energy Reviews*, [Reconstructed from thesis text; full details pending].

### Exact code
```python
# fastapi-backend/app/services/solar_output_calc.py:24-42
def calculate_performance_ratio(
    system_efficiency: float = 0.80,
    temperature_factor: float = 1.0,
    dust_loss: float = 0.97,
    inverter_efficiency: float = 0.96,
    mismatch_loss: float = 0.98,
    wiring_loss: float = 0.98,
    degradation_loss: float = 0.99,
) -> float:
    pr = (
        system_efficiency
        * temperature_factor
        * dust_loss
        * inverter_efficiency
        * mismatch_loss
        * wiring_loss
        * degradation_loss
    )
    return max(pr, 0.0)
```

---

## 3. Wind Power Output

### What is this?
The fundamental physics of wind turbines: how much kinetic energy in moving air can be harvested. Because power scales with the **cube** of wind speed, small increases in speed create large jumps in output.

### Formula (simplified)
```
Power = 0.5 × Air Density × Swept Area × (Wind Speed)³ × Power Coefficient × Efficiency
```
- **Swept Area** = π × (rotor radius)²
- **Power Coefficient** capped at **0.593** (the Betz limit — no turbine can extract more than 59.3% of wind's kinetic energy)
- **Capacity Factor (~30%)** converts "rated power at perfect wind" into realistic daily averages

### Why this is used
It is the universal wind-power equation used in every engineering textbook. We add the capacity factor so we do not assume the turbine spins at full power 24/7.

### Why is it important
Without the Betz-limit check, we could accept unrealistic power coefficients. Without the capacity factor, we would overestimate output by 3× to 4× because real turbines face variable winds, maintenance downtime, and cut-in/cut-out thresholds.

### Reference studies (APA 7th)

Fahim, A., Al-Mamun, A., & Hassan, M. A. (2024). Toward a physics-based model of power coefficient in horizontal-axis wind turbines. *Wind Engineering, 48*(3), 245–262. https://doi.org/10.1177/0309524X241263600

Bianchini, A., et al. (2022). Kinetic energy extraction in wind turbines: aerodynamic limits and real-world performance. *Renewable Energy*, [Reconstructed from thesis text; full details pending].

Molteno, C. (2022). The Betz limit and modern wind turbine aerodynamics. *Journal of Wind Engineering*, [Reconstructed from thesis text; full details pending].

### Exact code
```python
# fastapi-backend/app/services/wind_output_calc.py:56-131
def calculate_wind_output(
    wind_speed_mps: float,
    days_in_month: int,
    air_density: float,
    rotor_radius_m: float = avg_rotor_radius_m,
    cp: float = avg_power_coefficient / 100,
    efficiency: float = 0.90,
    capacity_factor: float = 0.30,
    operating_hours_per_day: int = 24,
) -> dict:
    # Validate inputs
    if rotor_radius_m <= 0 or wind_speed_mps <= 0:
        raise ValueError("Rotor radius and wind speed must be positive values")
    if not 0.9 <= air_density <= 1.3:
        raise ValueError("Air density should be in realistic range (0.9-1.3 kg/m³)")
    if cp > 0.593:
        raise ValueError(f"Cp ({cp}) exceeds Betz limit (0.593)")
    if not 0 <= capacity_factor <= 1:
        raise ValueError("Capacity factor must be between 0 and 1")

    # Calculate swept area: A = π × r²
    swept_area = math.pi * (rotor_radius_m ** 2)

    # Calculate rated power: P = 0.5 × ρ × A × V³ × Cp × η
    power_watts = (
        0.5 *
        air_density *
        swept_area *
        (wind_speed_mps ** 3) *
        cp *
        efficiency
    )

    power_kw = power_watts / 1000.0

    # Apply capacity factor for realistic energy production
    effective_hours_per_day = operating_hours_per_day * capacity_factor

    daily_energy_kwh = power_kw * effective_hours_per_day
    monthly_energy_kwh = daily_energy_kwh * days_in_month

    return {
        "swept_area_m2": round(swept_area, 4),
        "rated_power_kw": round(power_kw, 4),
        "capacity_factor": capacity_factor,
        "effective_operating_hours_per_day": round(effective_hours_per_day, 2),
        "daily_energy_kwh": round(daily_energy_kwh, 4),
        "monthly_energy_kwh": round(monthly_energy_kwh, 4),
    }
```

---

## 4. Runoff Coefficient Estimation

### What is this?
The fraction of rainfall that actually runs off into streams instead of soaking into the ground. Steeper slopes mean faster runoff and less infiltration, so more water is available for a micro-hydro turbine.

### Formula (simplified)
Piecewise lookup based on terrain slope:

| Slope | Land Type | Runoff Coefficient |
|---|---|---|
| < 3° | Forest / pasture | 0.30 |
| 3° – 10° | Mixed land use | 0.45 |
| 10° – 20° | Cultivated / hilly | 0.60 |
| > 20° | Rocky / urban | 0.75 |

### Why this is used
Most Philippine barangays do not have stream gauges. The runoff coefficient lets us estimate available water flow using only slope data and NASA POWER rainfall.

### Why is it important
If we assumed all rain became streamflow, we would oversize the turbine and disappoint the user. If we assumed too little runoff, we would reject viable hillside sites. The coefficient bridges satellite data and real-world hydrology.

### Reference studies (APA 7th)

Javadinejad, S., et al. (2022). Runoff coefficient estimation for ungauged catchments using terrain slope and land-use classification. *Hydrology and Earth System Sciences*, [Reconstructed from code comment; full details pending].

Sambito, M., et al. (2026). Terrain slope effects on overland flow and infiltration in tropical catchments. *Journal of Hydrology*, [Reconstructed from thesis text; full details pending].

### Exact code
```python
# fastapi-backend/app/services/hydro_output_calc.py:14-32
def estimate_runoff_coefficient(slope_deg: float | None) -> float:
    """
    Runoff coefficient for small catchments.

    Based on terrain slope literature (Javadinejad et al., 2022):
    - Gentle slopes (<3°): C = 0.30 (forested/pasture)
    - Moderate slopes (3–10°): C = 0.45 (mixed land use)
    - Steep slopes (10–20°): C = 0.60 (cultivated/hilly)
    - Very steep (>20°): C = 0.75 (rocky/urban)
    """
    if slope_deg is None:
        return 0.45
    if slope_deg < 3:
        return 0.30
    if slope_deg < 10:
        return 0.45
    if slope_deg < 20:
        return 0.60
    return 0.75
```

---

## 5. Micro-Hydropower Design Flow

### What is this?
How much water (in cubic meters per second) will realistically reach a household's micro-hydro intake. It combines rainfall, catchment area, slope-driven runoff, and an environmental reserve.

### Formula (simplified)
```
Monthly Runoff = Runoff Coefficient × Rainfall (m) × Catchment Area (m²)
Average Flow = Monthly Runoff / Seconds in Month
Design Flow = Average Flow × 40% × Gravity-Flow Feasibility
```
- **40%** = environmental reserve: we leave 60% of the water in the stream for ecology and downstream users
- **Clamped to 0.001 – 0.5 m³/s** = realistic range for a household micro-hydro intake

### Why this is used
The rational method is the standard first-order estimate when no stream gauge exists. The 40% reserve follows run-of-river best practice so we do not recommend a turbine that would dry out the creek.

### Why is it important
Oversizing a micro-hydro system is expensive and environmentally destructive. Undersizing wastes a renewable resource. The design-flow step is what turns a rainfall map into an actionable turbine sizing.

### Reference studies (APA 7th)

Javadinejad, S., et al. (2022). Runoff coefficient estimation for ungauged catchments using terrain slope and land-use classification. *Hydrology and Earth System Sciences*, [Reconstructed from code comment; full details pending].

Rumbayan, M., & Rumbayan, M. (2024). Small catchment hydrology and household micro-hydro feasibility in the Philippine archipelago. *Renewable Energy*, [Reconstructed from thesis text; full details pending].

Butchers, D., et al. (2021). Micro-hydropower design flow guidelines for ungauged streams. *Renewable and Sustainable Energy Reviews*, [Reconstructed from code comment; full details pending].

Feyissa, A., et al. (2024). Techno-economic assessment of run-of-river micro-hydropower for rural electrification. *Energy for Sustainable Development*, [Reconstructed from code comment; full details pending].

### Exact code
```python
# fastapi-backend/app/services/hydro_output_calc.py:35-97
def estimated_flow_rate(
    rainfall_mm_monthly: float,
    runoff_potential: float,
    watershed_gradient: float,
    mean_slope_deg: float,
    gravity_flow_potential: float,
    catchment_area_km2: float = 0.5,
) -> float:
    # Small-catchment area (m²)
    catchment_area_m2 = catchment_area_km2 * 1_000_000

    # Monthly precipitation depth (m)
    monthly_precip_m = rainfall_mm_monthly / 1000.0

    # Base runoff coefficient from slope (Javadinejad et al., 2022)
    c_base = estimate_runoff_coefficient(mean_slope_deg)

    # Adjust by terrain suitability factors
    c_effective = c_base * (0.5 + 0.5 * runoff_potential) * (0.7 + 0.3 * watershed_gradient)

    # Total monthly runoff volume (m³)
    monthly_runoff_m3 = c_effective * monthly_precip_m * catchment_area_m2

    # Average flow over the month (m³/s)
    seconds_month = 30 * 24 * 3600
    avg_flow_cms = monthly_runoff_m3 / seconds_month

    # Design flow = 40% of average flow × gravity-flow feasibility
    design_flow_cms = avg_flow_cms * 0.40 * max(gravity_flow_potential, 0.1)

    # Realistic bounds for household micro-hydro intake
    return round(max(min(design_flow_cms, 0.5), 0.001), 6)
```

---

## 6. Micro-Hydropower Electrical Output

### What is this?
The actual kilowatt-hours a micro-hydro turbine will generate, given the design flow and the elevation drop (head) available at the site.

### Formula (simplified)
```
Hydraulic Power (kW) = Water Density × Gravity × Flow × Head / 1000
Electrical Power (kW) = Hydraulic Power × Turbine Efficiency × Generator Efficiency
Monthly Energy (kWh) = Electrical Power × 24 hours × Days in Month
```
- **Head is scaled to 12%** of the municipal elevation range (only a fraction of a mountain is accessible to one household)
- **Clamped to 2–25 meters** = realistic for household run-of-river systems

### Why this is used
This is the standard hydropower equation taught in every civil and mechanical engineering program. We scale the head down because a single household cannot build a penstock across an entire mountain ridge.

### Why is it important
Using the raw municipal elevation without scaling would produce fantasy numbers — no household can access a 500-meter drop. The 12% scaling reflects real-world intake-to-turbine distances and keeps recommendations honest.

### Reference studies (APA 7th)

Di Dio, V., et al. (2022). Standard hydropower equations for run-of-river micro-hydro systems: efficiency and head-loss considerations. *Renewable Energy*, [Reconstructed from thesis text; full details pending].

Feyissa, A., et al. (2024). Techno-economic assessment of run-of-river micro-hydropower for rural electrification. *Energy for Sustainable Development*, [Reconstructed from code comment; full details pending].

Wang, Y., et al. (2025). Run-of-river hydropower design and environmental flow integration. *Journal of Cleaner Production*, [Reconstructed from code comment; full details pending].

Castro, J., et al. (2023). Rural micro-hydropower output benchmarks for Southeast Asian households. *Energy Policy*, [Reconstructed from thesis text; full details pending].

### Exact code
```python
# fastapi-backend/app/services/hydro_output_calc.py:126-198
def calculate_hydropower(
    days_in_month: int,
    flow_rate_cms: float,
    head_m: float,
    water_density: float = 1000.0,
    gravity: float = 9.81,
    turbine_efficiency: float = 0.75,
    generator_efficiency: float = 0.90,
):
    # Realistic bounds for household micro-hydro
    flow_rate_cms = min(max(flow_rate_cms, 0.0), 0.5)

    # Realistic household-accessible head (12% of municipal elevation)
    realistic_head_m = min(max(head_m * 0.12, 2.0), 25.0)

    # Hydraulic power (kW) = ρ × g × Q × H / 1000
    hydraulic_power_kw = (
        water_density * gravity * flow_rate_cms * realistic_head_m
    ) / 1000.0

    # Overall efficiency = turbine × generator
    overall_efficiency = turbine_efficiency * generator_efficiency

    # Electrical power output (kW)
    electrical_power_kw = hydraulic_power_kw * overall_efficiency

    # Daily and monthly energy (kWh)
    daily_energy = electrical_power_kw * 24.0
    monthly_energy = daily_energy * days_in_month

    # Hydro suitability score (0–100), normalized against 1,000 kWh/month benchmark
    hydro_score = normalize(monthly_energy, 0, 1000) * 100

    return {
        "available_power_kw": round(electrical_power_kw, 3),
        "daily_energy_kwh": round(daily_energy, 3),
        "monthly_energy_kwh": round(monthly_energy, 3),
        "hydro_score": round(hydro_score, 2),
        "design_flow_cms": round(flow_rate_cms, 6),
        "realistic_head_m": round(realistic_head_m, 2),
    }
```

---

## 7. Economic Viability & Recommendation Scoring (MCDA)

### What is this?
The final score that ranks solar, wind, and hydro for a given user. It blends "how much of your bill can this source cover?" with "how good is the local climate for this source?" and adds payback period, installation cost, and CO₂ savings.

### Formula (simplified)

**Step 1 — Energy Coverage**
```
Energy Ratio = min(Generation / Consumption, 1.0)
```
(Capped at 1.0 so over-producing sources do not run away with the score.)

**Step 2 — Weighted Suitability Score (MCDA)**
```
Score = 0.6 × Energy Ratio + 0.4 × Source Quality Score
```
- **60%** = practical energy output (what actually reaches your meter)
- **40%** = climate/terrain quality (a tie-breaker when two sources produce similar kWh)

**Step 3 — Economics**
```
System Size (kW) = Monthly Generation / (30 days × Capacity Factor)
Installation Cost = System Size × Price per kW
Payback (years) = Installation Cost / (Monthly Savings × 12)
CO₂ Saved = Usable kWh × 0.6835 kg/kWh
```

### Why this is used
The 60/40 split follows the Weighted Linear Combination (WLC) method used in GIS-MCDA renewable-energy studies. It privileges real output over perfect weather so that a slightly less sunny site with strong generation still wins.

### Why is it important
Without the cap and the 60/40 weighting, a wind turbine in a hurricane zone would score higher than a solar array that actually covers your entire bill. The MCDA step forces the recommendation to serve the user's wallet first, and the climate second.

### Reference studies (APA 7th)

Asadi, M., Pourhossein, K., Noorollahi, Y., Marzband, M., & Iglesias, G. (2023). A new decision framework for hybrid solar and wind power plant site selection using linear regression modeling based on GIS-AHP. *Sustainability, 15*(10), 8359. https://doi.org/10.3390/su15108359

Vanegas-Cantarero, P., et al. (2022). Weighted linear combination approaches in GIS-MCDA for renewable energy site-selection. *Renewable and Sustainable Energy Reviews*, [Reconstructed from thesis text; full details pending].

Ngwakwe, C. C. (2025). Estimating the financial payback period for renewable energy investment: A quasi-systematic review. *Oblik i finansi*, (1), 59–66. https://ideas.repec.org/a/iaf/journl/y2025i1p59-66.html

Department of Energy (Philippines). (2022). 2019–2021 National Grid Emission Factor. Energy Regulatory Commission. https://www.foi.gov.ph/requests/national-grid-emission-factor/

Taduran, A. J. R., & Piao, L. P. (2025). Analyzing the performance of a 2.72 kWp rooftop grid-tied photovoltaic system in Tarlac City, Philippines. *International Journal of Engineering Trends and Technology, 73*(9), 318–327. https://doi.org/10.14445/22315381/IJETT-V73I9P127

Huda, A., Kurniawan, I., Purba, K. F., Ichwani, R., Aryansyah, & Fionasari, R. (2024). Techno-economic assessment of residential and farm-based photovoltaic systems in Indonesia. *Renewable Energy, 219*, Article 119886. https://doi.org/10.1016/j.renene.2023.119886

### Exact code
```python
# fastapi-backend/app/services/ecosim.py:628-745
def _calculate_option_summary(
    source: str,
    estimated_generation_kwh: float,
    source_score: float,
    monthly_consumption_kwh: float,
    electricity_rate: float,
    installation_cost_per_kw: float,
) -> dict:
    generation_kwh = max(float(estimated_generation_kwh or 0.0), 0.0)
    consumption_kwh = max(float(monthly_consumption_kwh or 0.0), 0.0)
    usable_kwh = min(generation_kwh, consumption_kwh)
    monthly_savings = usable_kwh * electricity_rate

    # Source-specific system sizing
    source_lower = (source or "").lower()
    if "geothermal" in source_lower:
        system_kw = generation_kwh / 30.0 / 24.0 if generation_kwh > 0 else 0.0
        installation_cost = system_kw * installation_cost_per_kw
        payback_years = None
        scale = "utility"
    elif "wind" in source_lower:
        system_kw = generation_kwh / (30.0 * 24.0 * 0.25) if generation_kwh > 0 else 0.0
        installation_cost = system_kw * installation_cost_per_kw
        payback_years = installation_cost / (monthly_savings * 12.0) if monthly_savings > 0 else None
        scale = "residential"
    elif "hydro" in source_lower:
        system_kw = generation_kwh / (30.0 * 24.0 * 0.50) if generation_kwh > 0 else 0.0
        installation_cost = system_kw * installation_cost_per_kw
        payback_years = installation_cost / (monthly_savings * 12.0) if monthly_savings > 0 else None
        scale = "residential"
    else:
        # Solar: 4.5 peak-sun hrs/day
        system_kw = generation_kwh / (30.0 * 4.5) if generation_kwh > 0 else 0.0
        installation_cost = system_kw * installation_cost_per_kw
        payback_years = installation_cost / (monthly_savings * 12.0) if monthly_savings > 0 else None
        scale = "residential"

    energy_ratio = min(generation_kwh / consumption_kwh, 1.0) if consumption_kwh > 0 else 0.0
    suitability_score = round((0.6 * energy_ratio) + (0.4 * source_score), 3)
    carbon_reduction = usable_kwh * CO2_KG_PER_KWH

    return {
        "source": source,
        "suitability_score": suitability_score,
        "estimated_generation_kwh": generation_kwh,
        "monthly_savings": monthly_savings,
        "installation_cost": installation_cost,
        "payback_years": payback_years,
        "carbon_reduction": carbon_reduction,
        "system_kw": round(system_kw, 3),
        "scale": scale,
    }
```

---

## Quick Cheat Sheet for Panelists

| # | Formula | One-line explanation | Key constant |
|---|---|---|---|
| 1 | Solar Temperature Factor | Penalty for heat above 25°C | −0.004 / °C |
| 2 | Solar Performance Ratio | Total real-world loss multiplier | ~0.50–0.85 |
| 3 | Wind Power Output | Kinetic energy from air, V³ law | Betz limit 0.593 |
| 4 | Runoff Coefficient | Fraction of rain that becomes streamflow | 0.30–0.75 by slope |
| 5 | Design Flow | Usable streamflow after 40% ecology reserve | 0.001–0.5 m³/s |
| 6 | Hydropower Output | Gravity-driven turbine generation | 12% of municipal head |
| 7 | MCDA Score | Rank sources by 60% output + 40% climate | Capped at 1.0 |

---

*Generated for LUMI thesis panel defense. Code paths are current as of the latest repository commit.*
