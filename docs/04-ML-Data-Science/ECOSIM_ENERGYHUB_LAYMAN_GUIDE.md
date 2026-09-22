# EcoSim + EnergyHub: The Complete Layman Guide

**Purpose:** One document that explains every formula, decision rule, data-processing step, and AI component behind EcoSim and EnergyHub — in plain English, so the team can explain the system to panelists and consultants without opening the code.

**Audience:** Thesis panelists, consultants, and anyone asking "how does the system actually decide that?"

**How to read it:** Every item follows the same pattern — what it is, the math in simple terms, why it matters, and where it lives in the code. If you only have a few minutes, read Section 2 (the 30-second version) and the cheat sheet in Section 12.

---

## 1. What this document covers

LUMI has two main features that do math and AI work:

- **EcoSim** — the simulator. A user picks a municipality, enters their electric bill, and the system estimates how much energy solar, wind, micro-hydro, and geothermal could produce there, then recommends the best option for a home.
- **EnergyHub** — the dashboard. It shows national and provincial energy statistics, forecasts demand out to 2030, scores every province and municipality for renewable potential on a map, and generates written explanations of the charts using AI.

Everything below is what those two features actually compute.

---

## 2. The 30-second version

**EcoSim:** "You tell us your electric bill and where you live. We convert the bill into kilowatt-hours, pull up real climate data for your municipality — sunlight, wind speed, rainfall, temperature — and run physics formulas for each renewable source. Solar output comes from irradiance times a performance ratio that accounts for heat, dust, and equipment losses. Wind uses the standard power equation where output grows with the cube of wind speed. Hydro estimates stream flow from rainfall and terrain, then applies the hydropower equation. Geothermal reads a precomputed suitability table built from heat-flow and volcano data. We score each option, run the financial math, and recommend the source that covers the most of your bill — with a confidence score telling you how much we trust the data."

**EnergyHub:** "It is the national view. It pulls historical electricity statistics from DOE data, runs ARIMA time-series forecasts to project consumption, peak demand, and renewable generation to 2030 — and we validated the model by replaying history, predicting one year at a time, and measuring the error. The map colors every province and municipality by renewable suitability scores we precomputed and stored in the database, with a boost for places near operating plants. Municipal demand is estimated by splitting provincial consumption proportionally to population. When you click a chart, the system builds a prompt from the actual numbers and asks a language model to explain it — with a deterministic fallback text if the AI is unavailable, and a cache so we don't pay for the same explanation twice."

---

## 3. EcoSim: how a user's answers become a recommendation

The whole pipeline lives in one function, `renewable_energy_calculator`, wrapped by `build_ecosim_dashboard_response`.

`fastapi-backend/app/services/ecosim.py:933` (`renewable_energy_calculator`), `ecosim.py:1815` (`build_ecosim_dashboard_response`)

The steps, in order:

1. **Fetch the place.** Load the municipality's climate row (NASA POWER and Atlas fields) plus terrain data (slope, elevation, watershed stats). In "province mode" it aggregates across all municipalities in the province.
2. **Convert the bill to consumption.** See 3.1 below.
3. **Compute each source's output.** Solar, wind, hydro, geothermal — Sections 4.1–4.4.
4. **Score each option.** Suitability score and generation score — Section 5.1–5.2.
5. **Run the financial math.** NPV, IRR, LCOE, payback — Section 6.
6. **Attach a confidence score.** Section 7.
7. **Pick the recommendation.** Section 5.8.
8. **Write the explanations.** Static physics text always; optional AI text on top — Section 10.
9. **Cache the result.** The full result is cached in Redis keyed by a hash of all inputs and tuning settings, so a settings change automatically invalidates old answers (`ecosim.py:962-1018`, `ecosim.py:1444-1453`).

### 3.1 Converting the bill into energy terms

**What it is:** Users give a peso bill, not kilowatt-hours. This step converts money into electricity use.

**The math (simplified):**

```
monthly kWh   = monthly bill (PHP) / electricity rate (PHP per kWh)
daily kWh     = monthly kWh / days in current month
target kWh    = monthly kWh × (1 − desired savings fraction)
```

- `electricity rate` — defaults to Meralco's rate if the user doesn't supply one; the app uses the user's value when given.
- `desired savings` — e.g. 0.5 means "I want to cut my bill in half."

**Why it matters:** Every downstream number — savings, payback, percent-of-bill-covered — starts from this conversion. If the rate is wrong, everything scales wrong with it.

**Where it lives:** `fastapi-backend/app/services/ecosim.py:908-918` (`consumption_calculator`)

### 3.2 The input sanity check

**What it is:** A guard for when the user types both a bill and a kWh consumption that disagree.

**How it decides:** The system derives consumption from `bill / rate`. If the user's stated consumption differs from the derived value by more than 20%, the system trusts the bill-derived number and sets an `input_warning` flag so the UI can tell the user.

**Why it matters:** Typos in the consumption field would silently corrupt every estimate. The 20% tolerance allows for rate tiering noise while catching real mistakes.

**Where it lives:** `fastapi-backend/app/services/ecosim.py:1833-1843`

### 3.3 Where the climate numbers come from

**What it is:** Every energy formula needs local weather. The system stores monthly climate averages per municipality.

| LUMI variable | Source column | Used for |
|---|---|---|
| `solar_irradiance` | `avg_allsky_sfc_sw_dwn` (NASA POWER) or `solar_ghi_kwh_m2_day` (Atlas) | Solar output |
| `wind_speed` | `wind_speed_50m_ms` (Wind Atlas) → `wind_speed_10m_ms` / `era5_wind_speed_10m_ms` → `avg_ws10m` (NASA) | Wind output |
| `rainfall` | `avg_prectotcorr` (NASA POWER) | Hydro flow |
| `temperature` | `solar_temp_c` or `avg_t2m` | Solar derating |
| `humidity` | `avg_rh2m` | Solar soiling/degradation |
| `cloud_cover` | `avg_cloud_amt` | Solar explanation |
| `surface_pressure` | `avg_surface_pressure` | Air-density correction |
| `pvout` | `solar_pvout_annual_kwh_kwp` (Global Solar Atlas) | Preferred solar path |

**Why it matters:** The fallback chain (Atlas 50m → Atlas 10m → ERA5 10m → NASA 10m for wind, `ecosim.py:1037-1057`) means the system prefers higher-quality measured/modeled data and only falls back to coarser sources when needed. Panelists often ask "where does your data come from" — this is the answer.

**Where it lives:** `fastapi-backend/app/services/ecosim.py:921-929` (variable map), `ecosim.py:1026-1062` (fetch order)

---

## 4. EcoSim formulas by energy source

### 4.1 Solar

Solar has three computation paths, tried in order of data quality (`ecosim.py:1101-1133`):

1. **PVOUT path** — if Global Solar Atlas's PVOUT value exists (kWh per kWp per year, already including all system losses), use it directly.
2. **Advanced path** — if the Atlas provides split irradiance (DNI = direct beam, DHI = diffuse sky light), compute plane-of-array irradiance with a transposition model, then apply the full loss model.
3. **Legacy path** — plain global horizontal irradiance × performance ratio.

#### 4.1.1 Temperature factor (simple)

**What it is:** Solar panels lose efficiency when hot. This subtracts a penalty for every degree above 25°C (the lab test temperature).

**The math:**

```
Factor = 1 + (−0.004) × (T − 25)
```

- `−0.004` = −0.4% output per °C, the industry-standard silicon coefficient.
- `T` = average ambient temperature in °C.
- Result is clamped at 0 so it can never go negative.

**Why it matters:** Without it, a hot tropical site would look identical to a cool one. At 35°C ambient, panels lose about 4% output.

**Where it lives:** `fastapi-backend/app/services/solar_output_calc.py:70-76` (`calculate_temperature_factor`)

#### 4.1.2 NOCT cell temperature (advanced path)

**What it is:** The panel's actual cell temperature — which is hotter than the air because the panel absorbs sunlight — estimated with the NOCT model (Nominal Operating Cell Temperature, an IEC-standard rating).

**The math:**

```
T_cell = T_air + (NOCT − 20) × (G / 800) / wind_factor
wind_factor = max(0.5, 1 + 0.1 × wind speed)
```

- `NOCT` = 45°C for standard modules — the cell temperature the manufacturer measured at 20°C air, 800 W/m² sun, 1 m/s wind.
- `G` = plane-of-array irradiance in W/m².
- Wind cools the panel, so higher wind lowers the cell temperature.

The derating then uses the same −0.4%/°C coefficient but against `T_cell` instead of air temperature.

**Why it matters:** Cell temperature in strong Philippine sun runs well above air temperature. Using air temperature alone understates the heat penalty.

**Where it lives:** `fastapi-backend/app/services/solar_output_calc.py:15-42` (`calculate_noct_cell_temp`), `:45-67` (`calculate_temperature_factor_noct`)

#### 4.1.3 Soiling loss (dust, rain, humidity)

**What it is:** An estimate of how much output is lost to dirt on the panels, using weather as the driver.

**How it decides:**

- Start at `base_soiling = 0.97` (3% loss).
- Dry and windy (rain < 10 mm): dust accumulates faster — divide by `1 + 0.003 × (wind − 2) × (days since cleaning / 30)`.
- Rainy (rain > 50 mm): rain washes panels — multiply by `1 + 0.001 × min(rain − 50, 100)`, capped at 0.99.
- Very humid (> 80%): extra 0.5% loss for fungal/dust binding.
- Result bounded to [0.80, 1.0].

**Why it matters:** A dusty dry season and a monsoon month genuinely differ; this makes the estimate respond to the local season instead of a flat guess.

**Where it lives:** `fastapi-backend/app/services/solar_output_calc.py:79-109` (`calculate_soiling_loss`); legacy variants `calculate_dust_loss_from_wind` (:112-117) and `calculate_degradation_from_humidity` (:120-126)

#### 4.1.4 Air-density correction

**What it is:** A small adjustment for altitude/pressure — thinner air changes panel cooling and output slightly.

**The math:**

```
rho_ratio = (surface pressure / 101325 Pa) × (288.15 / (T + 273.15))
correction = 1 + 0.01 × (rho_ratio − 1),   clamped to [0.98, 1.02]
```

**Why it matters:** Small (±2%), but it lets highland sites like Baguio differ from coastal sites.

**Where it lives:** `fastapi-backend/app/services/solar_output_calc.py:129-146` (`calculate_air_density_correction`)

#### 4.1.5 Performance ratio — the loss multiplier

**What it is:** One number that rolls every real-world loss into a single multiplier applied to theoretical output.

**The math:**

```
PR = system_efficiency × temperature_factor × soiling_or_dust
     × inverter_efficiency × mismatch_loss × wiring_loss × degradation_loss
     [× air_density_correction]
```

Default factors: system 0.80, inverter 0.96, mismatch 0.98, wiring 0.98, degradation 0.99 — the temperature and soiling terms are computed from local weather as shown above.

**Why it matters:** This is what turns "the sunshine hitting your roof" into "the electricity you actually get." A typical result of 0.50–0.85 matches the IEC 61724 range for real residential systems.

**Where it lives:** `fastapi-backend/app/services/solar_output_calc.py:149-172` (`calculate_performance_ratio`); default config `ecosim.py:1069-1078`

#### 4.1.6 The three output formulas

**Legacy path:**

```
system_kWp   = panel_wattage × number_of_panels / 1000
daily kWh    = system_kWp × GHI × PR
monthly kWh  = daily × days_in_month
solar_score  = min(GHI / 6.0 × 100, 100)     — 6 kWh/m²/day = excellent
```

`fastapi-backend/app/services/solar_output_calc.py:175-192`

**Advanced path:** replaces GHI with POA (plane-of-array) irradiance. If DNI+DHI exist, a Hay–Davies-style transposition projects sky + beam + ground-reflected light onto the tilted panel; otherwise a simple tilt correction `GHI × (1 + 0.05 × cos(tilt − latitude))` is used. Output = `kWp × POA × PR` where PR now uses NOCT temp, modeled soiling, and air-density terms. Same score formula on GHI.

`fastapi-backend/app/services/solar_output_calc.py:195-309` (`solar_calc_advanced`)

**PVOUT path:**

```
daily kWh   = kWp × PVOUT / 365
solar_score = min(PVOUT / 1800 × 100, 100)   — 1800 kWh/kWp/yr = excellent for PH
performance_ratio reported as 1.0 because PVOUT already includes losses.
```

`fastapi-backend/app/services/solar_output_calc.py:312-349` (`solar_calc_pvout`)

**Why it matters:** The three paths mean the system always answers, but answers get more honest as better data exists. Panelist answer: "We prefer measured satellite-derived yield (PVOUT); we only estimate from first principles when that's unavailable."

---

### 4.2 Wind

#### 4.2.1 Wind speed height correction

**What it is:** Wind atlases report speed at 50m or 10m height; a home turbine sits lower. The power law rescales wind speed between heights.

**The math:**

```
V(h) = V_ref × (h / h_ref)^0.143
```

- `0.143` = the 1/7 power-law exponent used in the NREL Wind Energy Resource Atlas of the Philippines.

**Why it matters:** Wind power scales with the cube of speed, so a wrong height means a badly wrong answer — roughly 30% error in speed becomes roughly double in power.

**Where it lives:** `fastapi-backend/app/services/wind_output_calc.py:107-124` (`extrapolate_wind_speed`); fallback chain `ecosim.py:1037-1057`

#### 4.2.2 The turbine power curve

**What it is:** The physical power a turbine makes at a given wind speed, with real operating limits.

**The math:**

```
A    = π × r²                     (swept area of the rotor)
P    = 0.5 × ρ × A × V³ × Cp × η  (cubic power law)
```

- `ρ` = air density (kg/m³, must be in 0.9–1.3)
- `Cp` = power coefficient — how much of the wind's energy the blades capture; validated against the Betz limit of 0.593 (physics proves no turbine can exceed ~59.3%)
- `η` = mechanical/electrical efficiency (~0.90)

**How it decides (the four regions):**

| Wind speed | Power |
|---|---|
| Below cut-in (~3 m/s) | 0 — too weak to spin usefully |
| Cut-in to rated (~3–11 m/s) | `min(cubic power, rated cap ~1.2 kW)` |
| Rated to cut-out (~11–25 m/s) | flat at rated power |
| Above cut-out (~25 m/s) | 0 — turbine shuts down to avoid damage |

Then: `monthly kWh = power × 24 h × capacity factor × days`, where capacity factor (~0.25) accounts for the hours the wind is too low, too high, or the turbine is down.

**Why it matters:** The cubic term is the single most important wind fact for a panel: doubling wind speed gives 8× the power. The cut-in/rated/cut-out regions keep the estimate inside what a real small turbine does. Default rotor radius and Cp come from an actual catalog of small-wind products (`wind_products_joined_betz.csv` → Supabase `wind_products_summary`).

**Where it lives:** `fastapi-backend/app/services/wind_output_calc.py:127-255` (`calculate_wind_output`); product averages `:24-98`

#### 4.2.3 Province-mode median

**What it is:** In province mode the system uses the *median* of all municipality wind outputs rather than computing output from an area-weighted average wind speed.

**Why it matters:** One windy coastal municipality would otherwise dominate the whole province's answer. The median gives the "typical municipality" result.

**Where it lives:** `fastapi-backend/app/services/ecosim.py:1291-1298`

---

### 4.3 Hydro (micro-hydropower)

#### 4.3.1 Runoff coefficient from slope

**What it is:** The fraction of rainfall that becomes stream flow rather than soaking into the ground — read off terrain slope.

**How it decides (Javadinejad et al., 2022):**

| Mean slope | Coefficient C | Typical land |
|---|---|---|
| < 3° | 0.30 | Flat, forested/pasture |
| 3–10° | 0.45 | Mixed use |
| 10–20° | 0.60 | Cultivated/hilly |
| > 20° | 0.75 | Steep, rocky/urban |

Without catchment enrichment, C is further moderated: `C_effective = C × (0.5 + 0.5 × runoff_potential) × (0.7 + 0.3 × watershed_gradient)`.

**Where it lives:** `fastapi-backend/app/services/hydro_output_calc.py:14-32` (`estimate_runoff_coefficient`), adjustment `:97`

#### 4.3.2 Design flow rate

**What it is:** How much water a household micro-hydro intake can actually count on, in cubic meters per second.

**The math:**

```
monthly runoff volume = C × monthly rain (m) × catchment area (m²)
average flow          = runoff volume / seconds in a month
design flow           = average flow × 0.40 × max(gravity_flow_potential, 0.1)
```

- `0.40` = design flow factor — the turbine is sized for 40% of average flow so the river keeps an environmental reserve (standard run-of-river practice).
- `gravity_flow_potential` = how feasible gravity-fed intake is, derived from stream gradient: `min(gradient / 0.10, 1.0)` — a 10% stream grade means full potential.
- Result bounded to [0.001, 0.5] m³/s for the fallback path; with real catchment data the floor is removed so genuinely dry areas show 0.

**Why it matters:** This is the "how much water" half of hydro. It adapts the classic rational method (Q = C·P·A) to ungauged small catchments — places with no flow meters, which is almost everywhere at barangay scale.

**Where it lives:** `fastapi-backend/app/services/hydro_output_calc.py:35-117` (`estimated_flow_rate`); a simpler variant `estimate_discharge` at `:120-143`

#### 4.3.3 The hydropower equation

**What it is:** The standard physics for converting moving water into electricity.

**The math:**

```
P_electric = ρ × g × Q × H × η_turbine × η_generator   / 1000  (kW)
```

- `ρ` = water density, 1000 kg/m³
- `g` = 9.81 m/s²
- `Q` = design flow (m³/s)
- `H` = hydraulic head — the vertical drop. Municipal terrain head is scaled by `head_factor` (0.20) and clamped to [2, 25] m for household scale; with enrichment data, head comes from stream gradient × penstock distance directly.
- `η_turbine` = 0.75, `η_generator` = 0.90 → overall ~0.68, typical for micro-hydro.

Then: `monthly kWh = P × 24 × days`, optionally multiplied by a stream-distance feasibility penalty (a household 8 km from the stream can't cheaply pipe water to a turbine).

**Hydro score:** `normalize(monthly kWh, 0, 100) × 100` — 100 kWh/month is treated as an excellent Philippine household site; most enriched sites produce 0–5.

**Why it matters:** Flow × head is the whole story of hydro — panelists can sanity-check it: a site needs both water *and* drop. The feasibility penalty encodes the economics of distance.

**Where it lives:** `fastapi-backend/app/services/hydro_output_calc.py:146-241` (`calculate_hydropower`)

#### 4.3.4 Catchment enrichment (real watershed data)

**What it is:** An upgrade path that replaces fixed assumptions with real catchment morphology from the Boothroyd et al. (2023) Philippine river geodatabase: actual catchment area (scaled to a household fraction), stream-gradient-derived head, an enriched runoff coefficient (drainage density + hypsometric integral), and distance-to-nearest-stream.

**How it decides (stream distance → feasibility):**

| Distance to stream | Feasibility |
|---|---|
| ≤ 2 km | high |
| ≤ 5 km | moderate |
| ≤ 10 km | low |
| > 10 km | none |

**Why it matters:** The fallback model uses a fixed 1 km² catchment and a fake flow floor — fine for demos, wrong for dry areas. Enrichment lets genuinely dry places score zero instead of a fictional minimum.

**Where it lives:** `fastapi-backend/app/services/ecosim.py:1140-1237` (enrichment branch), `hydro_output_calc.py:35-117`

---

### 4.4 Geothermal

Geothermal works differently — it is utility-scale, so EcoSim does not simulate a home device. It reads a precomputed suitability assessment.

**What it is:** For each municipality, a `geothermal_suitability` table (built offline) stores sub-scores: `heat_flow_score`, `fault_distance_km` + `fault_density`, `volcano_distance_km`, `aquifer_score`, `temperature_score`, and a combined `geothermal_score` (0–1) with a classification.

**The math:**

```
suitability_score (0–100) = geothermal_score × 100
energy: annual GWh → ×1,000,000 → monthly kWh for comparison
proximity boost: municipalities near operating geothermal plants get
                 their score boosted and the plant names attached
```

**Why it matters:** You cannot buy a home geothermal unit, so geothermal stays a *reference* option: it tells the user whether their area has real subsurface potential, while keeping it out of the household recommendation (Section 5.8).

**ML extension:** `geothermal/ml_classifier.py` trains a RandomForestClassifier (100 trees, depth 8, balanced classes) on those feature columns to report which subsurface factor drives the classification — used for analysis, with physics remaining primary.

**Where it lives:** `fastapi-backend/app/services/ecosim.py:754-848` (`get_geothermal_data`), `ecosim.py:1271-1278` (kWh conversion), `geothermal/plants.py:116` (`calculate_proximity_boost`), `geothermal/ml_classifier.py:74-119`

---

## 5. The decision matrix — how sources are compared and ranked

### 5.1 The weighted suitability score

**What it is:** The main "how good is this source here" number, 0–100.

**The math:**

```
suitability_score = source_score × (0.4 + 0.6 × energy_ratio) × 100

energy_ratio = min(monthly generation / monthly consumption, 1.0)
source_score = the source's natural-resource quality at this site, 0–1
               (solar: PVOUT or GHI score; wind/hydro: output vs baseline; geothermal: table score)
```

**Why this shape:** It is *multiplicative* — resource quality is the gate, and energy coverage only raises or lowers the score by up to 60%. A source with poor natural conditions can never win just by producing a big kWh number on paper. This directly implements the Weighted Linear Combination approach from Asadi et al. (2023).

**Where it lives:** `fastapi-backend/app/services/ecosim.py:1763-1767` (`_calculate_option_summary`), derivation in docstring `:1687-1693`

### 5.2 The generation score

**What it is:** The user-facing "how much of your bill this covers" number.

**The math:**

```
generation_score = min(generation / consumption × 100, 100)
```

Computed only for household-scale sources; geothermal gets none because it is reference-only.

**Where it lives:** `fastapi-backend/app/services/ecosim.py:1769-1775`

### 5.3 Scoring baselines (what "100" means)

Each source score is normalized against a site that would be excellent in the Philippines:

- Solar: `PVOUT / 1800 kWh/kWp/yr` (or `GHI / 6.0 kWh/m²/day`)
- Wind: `monthly output / 300 kWh` (a 1.5 kW turbine at a good 5 m/s site, CF ~25% → ~270 kWh/month)
- Hydro: `monthly output / 100 kWh`

`ecosim.py:1357-1359`, `ecosim.py:1915-1922`, `solar_output_calc.py:337`, `hydro_output_calc.py:226-232`

### 5.4 Per-source system sizing

**What it is:** To price each option, the system converts monthly generation into an implied system size, using each technology's real duty cycle.

**The math:**

| Source | system kW = | Why |
|---|---|---|
| Solar | `monthly kWh / (30 × 4.5)` | 4.5 peak-sun hours/day — conservative PH estimate |
| Wind | `monthly kWh / (30 × 24 × 0.25)` | ~25% capacity factor for small PH turbines |
| Hydro | `monthly kWh / (30 × 24 × 0.50)` | ~50% CF for run-of-river micro-hydro |
| Geothermal | `monthly kWh / (30 × 24)` | utility plant, ~100% dispatch |

`installation_cost = system_kW × cost_per_kW` for that source.

**Where it lives:** `fastapi-backend/app/services/ecosim.py:1723-1761`

### 5.5 The MCDA toolkit (`mcda.py`)

MCDA = Multi-Criteria Decision Analysis — the family of methods for combining several criteria into one ranking.

#### 5.5.1 Weighted Linear Combination (aggregate_score)

**What it is:** The textbook weighted sum: score each criterion 0–100, multiply by its weight, add up.

**The math:**

```
score = Σ (criterion_score × weight_i) / Σ weights,   clamped to [0, 100]
```

Weights are normalized to sum to 1 first; missing weights fall back to equal weights.

**Classification bands:** ≥81 Very High, ≥61 High, ≥41 Moderate, ≥21 Low, else Very Low.

**Where it lives:** `fastapi-backend/app/services/mcda.py:63-123` (`aggregate_score`)

#### 5.5.2 AHP consistency ratio

**What it is:** AHP (Analytic Hierarchy Process) builds weights from pairwise judgments ("is irradiance more important than slope, and by how much?"). Humans contradict themselves, so this checks whether the judgment matrix is self-consistent.

**The math:**

```
1. Normalize each column, average rows → priority vector (the weights)
2. λ_max = average of (weighted sums / priority)
3. CI  = (λ_max − n) / (n − 1)         — consistency index
4. CR  = CI / RI                       — RI from Saaty's table (n=4 → 0.90)
5. Consistent if CR < 0.10
```

**Why it matters:** This is the standard defense answer for "why should we trust your weights?" — a CR under 0.10 is the accepted AHP threshold.

**Where it lives:** `fastapi-backend/app/services/mcda.py:16-60` (`ahp_consistency_ratio`)

#### 5.5.3 PROMETHEE II

**What it is:** An outranking method — instead of summing scores, it compares options pairwise per criterion and counts how often each option beats the others.

**How it decides:** For each criterion, a preference function maps the score gap between option A and B into [0,1] — 0 if A is worse, partial credit within an indifference threshold (default 10% of the criterion's range), 1 above it. Weighted preferences sum into a preference index π(A,B). Each option gets:

- **positive flow** = average π of beating others
- **negative flow** = average π of being beaten
- **net flow** = positive − negative → sort by net flow to rank.

**Where it lives:** `fastapi-backend/app/services/mcda.py:126-213` (`promethee_ii`)

#### 5.5.4 Where the criterion weights come from

**What it is:** Per-source weights stored in a Supabase `mcda_weights` table (admin-tunable, cached in memory, `is_active` flag). If the table is unreachable, built-in defaults apply:

| Energy | Criteria weights |
|---|---|
| Geothermal | heat_flow .30, fault .15, aquifer .15, volcano .10, temperature .10 |
| Solar | irradiance .40, temperature .20, cloud_cover .20, terrain_slope .10, land_use .10 |
| Wind | wind_speed .40, terrain_roughness .20, elevation .20, land_use .10, air_density .10 |
| Hydro | rainfall .30, watershed_slope .25, catchment_area .25, hydraulic_head .20 |

**Where it lives:** `fastapi-backend/app/services/mcda_weights_service.py:16-44` (defaults), `:49-113` (loader + cache)

### 5.6 Plant-proximity recalibration (wind, hydro, geothermal)

**What it is:** A correction layer on top of the physics: if a municipality sits near *real, operating* wind/hydro/geothermal plants (from the Wikipedia-derived plant datasets), its score gets boosted — because an operating plant is direct proof the resource exists.

**How it decides:** Two modes, configurable:

- `"suitability"` mode — add a bonus to the score within a radius (default ~50 km), capped by a max bonus.
- `"generation"` mode — scale the household kWh estimate by a factor derived from nearby plant capacity (`wind_plants_generation_scale_factor`, `hydro_plants_generation_scale_factor`), with a max scale.

Hydro adds an **output floor**: in configured proven-hydro provinces, household output is floored at a fraction of nearby plant capacity — capped absolutely — so a province with a big operating dam never reports negligible hydro.

**Why it matters:** This is the answer to "why does Batangas show good wind when the average speed looks marginal?" — measured plant performance beats modeled weather.

**Where it lives:** `ecosim.py:1926-2023` (application), `wind_plants.py:129` (`calculate_wind_proximity_boost`), `:171` (`calculate_wind_generation_scale`), `hydro_plants.py:129`, `:171`, `:208` (`calculate_hydro_plant_floor`), `geothermal/plants.py:116` (`calculate_proximity_boost`)

### 5.7 Rating bands (the words users see)

**Household sources** (solar, wind, hydro), based on `generation_score`:

| Score | Rating | Meaning shown to user |
|---|---|---|
| ≥ 80 | Excellent | Can offset most of your monthly use |
| ≥ 50 | Good | Offsets a meaningful share |
| ≥ 25 | Moderate | Offsets some of your use |
| < 25 | Fair | Offsets a small share |

**Utility sources** (geothermal), based on `suitability_score`: Excellent ≥80, Good ≥60, Moderate ≥40, else Fair — labeled "reference-only match."

**Where it lives:** `fastapi-backend/app/services/ecosim.py:2064-2104`

### 5.8 The final recommendation

**How it decides:**

1. Take only household-scale options (geothermal excluded).
2. For each, compute `usable = min(monthly output, monthly consumption)` — a source gets no extra credit for generating more than you need.
3. Pick the max `usable`; break ties with `suitability_score` (best natural resource wins).
4. If AI analysis ran and returned a `best_option` *with a reason*, the AI choice overrides — but only for a recognized source name.

A hidden alternative — the option with the highest raw suitability score — is computed and stored (`suitability_recommended_source`) but not shown, kept for future use.

**Why it matters:** Capping at consumption is the honest choice: "the source that meets your need most cheaply/reliably," not "the biggest number." The AI override exists so the LLM can catch context the formulas miss, but it must justify itself.

**Where it lives:** `fastapi-backend/app/services/ecosim.py:2124-2190` (`_recommendation_key`, AI override, explanation string)

---

## 6. The money math (`financials.py`)

Every option runs a full techno-economic analysis with these inputs: discount rate 10%, system lifetime 25 years (residential) / 30 (utility), degradation 0.5%/year, O&M cost 1% of CapEx/year, tariff = the user's electricity rate (`ecosim.py:1780-1790`).

> **Important caveat for panelists:** the API currently *hides* the peso outputs (monthly savings, installation cost, payback, NPV, IRR, LCOE are nulled in the response at `ecosim.py:2192-2202`) until the cost-per-kW data is reliable. The math below exists and runs — the team chose to show generation and scores rather than display prices that could mislead.

### 6.1 Net Present Value (NPV)

```
NPV = Σ  cash_flow_t / (1 + r)^t
```

Year 0 is the negative installation cost; each later year is (energy × tariff − O&M) with energy degrading 0.5%/yr. Positive NPV = the investment pays for itself in today's pesos.

`fastapi-backend/app/services/financials.py:45-61` (`calculate_npv`), cash-flow construction `:188-208`

### 6.2 Internal Rate of Return (IRR)

The discount rate that makes NPV exactly zero — "what interest rate is this investment equivalent to?" Solved numerically by Newton–Raphson iteration (start at 10%, refine until NPV ≈ 0 or 100 iterations).

`financials.py:64-97` (`calculate_irr`)

### 6.3 Levelized Cost of Energy (LCOE)

```
LCOE = PV of all costs / PV of all energy produced   (PHP per kWh)
```

The lifetime average cost of each kWh the system makes — directly comparable to the grid tariff. If LCOE < Meralco rate, the system is cheaper than buying from the grid.

`financials.py:100-134` (`calculate_lcoe`)

### 6.4 Payback periods

- **Simple payback** = `capital cost / year-1 net savings` — the naive "how many years to break even."
- **Discounted payback** = same but each year's savings is discounted and degraded; the code interpolates within the crossover year for a fractional answer.

`financials.py:137-176` (`calculate_payback`)

### 6.5 Benefit-cost ratio

`PV(benefits) / PV(costs)` — above 1.0 means benefits outweigh costs.

`financials.py:234-244`

### 6.6 Carbon displacement

```
CO₂ avoided (kg) = usable kWh × 0.6835
```

0.6835 kg CO₂/kWh is the Philippine DOE 2019–2021 National Grid Emission Factor (Luzon–Visayas operating margin).

`ecosim.py:1777`; constant `CO2_KG_PER_KWH`

---

## 7. Confidence scoring (`confidence.py`)

**What it is:** A 0–100 "how much should you trust this number" attached to each energy option.

**The math:**

```
overall = coverage × 0.35 + recency × 0.15 + maturity × 0.30 + resolution × 0.20
score   = overall × 100
```

- **coverage** — how many of the 10 climate variables exist, plus bonuses for terrain, population, tariff, and user-supplied inputs (max 1.0, `confidence.py:32-53`)
- **recency** — 1.0 if data ≤2 years old, 0.8 ≤5y, 0.6 ≤10y, 0.4 older, 0.3 unknown (`:56-69`)
- **model maturity** — how established the method is per source: solar 0.85, wind 0.70, hydro 0.65, geothermal 0.40 (`:72-80`)
- **spatial resolution** — flat 0.55: NASA POWER's ~50 km grid is coarse for municipal work (`:83-87`)

**Labels:** ≥75 High, ≥55 Moderate, ≥35 Low, else Very Low. It also emits concrete recommendations ("fetch NASA POWER data", "add DU tariff data") when a factor is weak.

**Why it matters:** It is the honest answer to "how accurate is this?" — geothermal scores low on purpose because Philippine heat-flow measurements are sparse.

**Where it lives:** `fastapi-backend/app/services/confidence.py:90-141` (`calculate_confidence`)

---

## 8. EnergyHub: the forecasting engine

### 8.1 SARIMA and ARIMAX, plainly

**What it is:** ARIMA-family models — the standard statistical method for forecasting a single quantity through time. The name encodes three dials: how many past values it looks back at (p), how many times it differences the series to remove trend (d), and how much it smooths noise (q). SARIMA adds a seasonal copy of the same three dials for repeating yearly patterns; ARIMAX additionally feeds in outside variables (like GDP or population) that help explain the series.

**The math (concept):**

```
next value = weighted past values + weighted past errors + seasonal echo [+ exogenous inputs]
```

**Where it lives:** `fastapi-backend/app/services/forecasting.py:88-143` (`fit_sarima`, `fit_arimax`), config `:45-51`

### 8.2 Walk-forward backtesting — proving the forecast

**What it is:** The validation method. Train the model only on data up to a cutoff, predict the next year, add the real value to history, retrain, predict the following year, repeat.

**Why it matters:** It simulates exactly how the model performs in the real world — always predicting the future from the past, never peeking ahead. This is the standard answer to "how do you know your forecast works?"

**Where it lives:** `fastapi-backend/app/services/forecasting.py:176-247` (`backtest_walk_forward`)

### 8.3 The error metrics

| Metric | Plain meaning |
|---|---|
| **MAE** | Average absolute miss — "typically off by this many GWh" |
| **RMSE** | Like MAE but squares errors first — big misses hurt more, so RMSE > MAE |
| **MAPE** | Average percent error — "typically off by this many %" |
| **sMAPE** | Symmetric version of MAPE — treats over- and under-predicting the same |

`fastapi-backend/app/services/forecasting.py:250-272` (`calculate_metrics`)

### 8.4 What the dashboard actually serves

The trained forecasts are stored as offline artifacts and served by `EnergyHubML`:

- **Forecast endpoint:** years 2025–2030 with confidence intervals (the shaded "could be between X and Y" band), labeled `ARIMA(1,1,1)`, trained on 2003–2020, validated on 2021–2024 (`predictor.py:197-233`)
- **Model comparison:** all candidate models ranked by MAE/RMSE/MAPE on the test window (`predictor.py:235-255`)
- **Overview card growth:** `forecast_growth_% = ((forecast 2030 / latest consumption) − 1) × 100` (`energyhub.py:213-231`)
- **Breakdowns:** generation share by source (coal, gas, oil, geothermal, hydro, solar, wind, biomass) and by grid (Luzon/Visayas/Mindanao) — simple `source/total × 100` shares (`predictor.py:257-336`)
- **Cache reconciliation + run logging:** forecast results are versioned in the DB; stale caches are detected and refreshed (`forecasting.py:348-550`)

---

## 9. EnergyHub: map scores and municipal demand

### 9.1 Score → color bands

**How it decides:** Every map score 0–100 becomes a band: ≥81 `veryHigh`, ≥61 `high`, ≥41 `moderate`, ≥21 `low`, else `veryLow`; missing data → `noData`. These strings drive the map's color scale.

`fastapi-backend/app/services/energyhub.py:60-71` (`_classify_score`)

### 9.2 Where map scores come from

- **Municipality level:** reads precomputed `*_suitability_score` + `*_classification` + `*_factors` columns straight from the `municipalities` table (solar, wind, hydro, geothermal, composite) — built offline by `municipality_suitability_builder.py`, cached in Redis (`energyhub.py:835-897`)
- **Barangay level:** barangays *inherit* their parent municipality's score; centroids come from geospatial metadata (`energyhub.py:899-965`)
- **Province level:** aggregates — numeric factor values are averaged across municipalities (`_aggregate_factors`, `energyhub.py:775-804`)
- **Geothermal proximity boost:** each municipality's score is boosted if it sits near operating geothermal plants, and the plant names are injected into the factors text (`_apply_geothermal_boost`, `energyhub.py:806-833`)
- **Name alignment:** a hard-coded map aligns DB province names with GeoJSON names (e.g. "compostela valley" → "davao de oro", NCR districts) (`energyhub.py:130-153`)

### 9.3 Municipal demand estimation

**What it is:** DOE publishes consumption by *region*, not municipality. To get municipal demand, the system splits the province's regional total proportionally to population.

**The math:**

```
D_municipality = D_province × (population_municipality / population_province)
```

Inputs: DOE Annex 8 regional consumption (`Total Consumption` row, MWh) + PSA census population per municipality (`municipal_population` table). A lookup maps each province name to its DOE region code (e.g. "quezon" → "IV-A").

**Why it matters:** It is the standard top-down disaggregation — honest about its limits ("actual demand may vary" is attached to every item) and it fails loudly with a clear note if population data is missing.

**Where it lives:** `fastapi-backend/app/services/energyhub.py:1585-1673` (`estimate_municipal_demand`), region map `:1676-1769`, provincial consumption `:1576-1583`

### 9.4 External benchmarks

IRENA capacity/generation/renewable share, Meralco historical rates, and Global Solar Atlas lookups are read from loaded datasets and exposed for side-by-side benchmarking with DOE figures (`energyhub.py:1773-1798`, `predictor.py:430-501`).

---

## 10. The AI explanations (LLM features)

### 10.1 EcoSim's AI analysis

**What it is:** After the math runs, the system can ask Google's Gemini to write a natural-language analysis: a summary, per-source explanations, a recommendation with reasoning, cost context, and environmental impact.

**How it works:**

1. Build a payload: municipality climate data, consumption results, all four source outputs, nearby plants, mode (`gemini_funcs.py:214`, prompt builder `:514`)
2. Compute a cache key from the payload — identical inputs reuse a stored analysis (`:111-201`, backed by the Supabase `ecosim_ai_cache` table)
3. Call Gemini with a timeout + worker-thread pattern; parse the JSON block out of the reply; normalize it to a fixed schema (`:334-513`)
4. In province mode, geothermal text is stripped from the AI output (`:203`) to match the deterministic rule that geothermal is reference-only there
5. **Fallbacks:** if AI fails or is off, deterministic template explanations always exist (see 10.2); per-source AI gaps are filled with the static text so no card is ever empty (`ecosim.py:1419-1432`)
6. Optional RAG variant (`use_rag` + `rag_query`) routes through `rag_gemini_funcs.analyze_with_rag` to ground the answer in retrieved documents (`ecosim.py:1397-1404`)

**Where it lives:** `fastapi-backend/app/services/gemini_funcs.py` (whole flow), `ecosim.py:1386-1432`

### 10.2 The deterministic explanation templates

**What it is:** Hand-written physics explanations assembled from the actual numbers — the guaranteed fallback, cached per municipality in `municipality_renewable_explanations` with a staleness check (if recalculation changes the text, the cache regenerates).

Each template explains *why*, not just *what*: solar explains photons/irradiance/cloud/temperature; wind explains the V³ cubic law and capacity factor; hydro explains rainfall→flow and elevation→head; geothermal always explains the four subsurface drivers even when data is missing.

**Where it lives:** `fastapi-backend/app/services/ecosim.py:1458-1605` (`_build_static_renewable_explanations`), `:1608-1654` (`_get_or_build_explanations`)

### 10.3 EnergyHub's chart and map insights

**What it is:** Click a chart or map and get a written explanation of *these specific numbers*.

**How it works:**

1. Hash the chart's actual data (`_hash_chart_data`, `energyhub.py:1268`) and check the Supabase `chart_ai_insights` cache — same chart, same numbers → reuse (`:1281-1335`)
2. Build a prompt containing the real values — for charts, the series/forecast context (`_build_chart_prompt`, `:1399`); for maps, a compact summary of top items, data sources, nearby features (`_summarize_map_data`, `_map_data_sources`, `_nearest_geo_feature`, `:1051-1225`)
3. Call the LLM (Gemini primary; the AI panel also supports Groq via `groq_client.py`) with retry/backoff (`llm_client.py:31-107`)
4. Clean the response — strip any "thinking" blocks (`llm_sanitizer.py:19`), `_clean_llm_text` (`energyhub.py:1391`)
5. If the LLM path is off or fails, a static template summarizes the map deterministically (`_static_map_explanation`, `:1036-1050`)
6. Cache the result under the chart hash + `PROMPT_VERSION` so prompt changes invalidate cleanly (`energyhub.py:201`)

**Why it matters:** Hashing the *data* means a stale explanation can never be served for changed numbers — a panelist asking "how do you stop the AI from quoting old data?" gets this answer.

**Where it lives:** `fastapi-backend/app/services/energyhub.py:967-1575`

---

## 11. The chat / RAG pipeline

RAG = Retrieval-Augmented Generation: before the AI answers, the system retrieves relevant documents from its own knowledge base and feeds them to the model as grounding.

### 11.1 Indexing

Documents are chunked, embedded into vectors (via `rag_embeddings_client.py`), and stored in a FAISS index (local) or pgvector (Supabase) — built/maintained by `rag_knowledge_builder.py`, loaded by `rag_pipeline.py` (`build_faiss_index`, `ensure_index_built`, `retrieve_context`, `retrieve_with_filter` for per-renewable-type filtering).

### 11.2 Hybrid search — two searches combined

**What it is:** Semantic search finds text with similar *meaning* (vector similarity); BM25 keyword search finds text with the same *words*. Combining both catches synonyms and exact terms.

**BM25, simplified:** the industry-standard keyword ranking — terms that are rare across documents (high IDF) and frequent inside a document (high TF) score highest, with document-length normalization:

```
score += log((N − df + 0.5)/(df + 0.5) + 1) × tf(k1+1) / (tf + k1(1 − b + b·len/avg_len))
k1 = 1.5, b = 0.75
```

**Fusion:** candidates come from semantic search (4× over-retrieved); BM25 scores are computed on those candidates; both are normalized to 0–1 and blended:

```
fused = 0.7 × semantic + 0.3 × keyword,   keep if fused ≥ 0.15, take top 5
```

A Reciprocal Rank Fusion helper (`1/(60 + rank)` summed across lists) is also available for rank-based merging.

**Where it lives:** `fastapi-backend/app/services/rag_hybrid.py:33-83` (`_bm25_scores`), `:139-202` (`hybrid_search`), `:90-132` (`_reciprocal_rank_fusion`)

### 11.3 Reranking, citations, guardrails

- **Rerank:** retrieved chunks are re-scored against the query for final ordering (`rag_hybrid.py:209+`)
- **Citation verification:** checks that claims in the AI answer are supported by the retrieved chunks (`verify_citations`, `:269`)
- **Input validation + output sanitization:** blocks injection-style queries and strips unsafe content before answers reach users (`:361-402`)
- **Chat sessions:** conversation history persisted in Supabase for context (`:403-475`)

---

## 12. Data sources, processing, frontend map, and the cheat sheet

### 12.1 Where every input comes from

| Data | Source | How it's used |
|---|---|---|
| Climate monthly (temp, wind, rain, irradiance, humidity, pressure) | NASA POWER API → `municipality_climate_monthly` | All four energy formulas |
| Solar GHI/DNI/DHI/PVOUT/tilt | Global Solar Atlas | Solar paths + score |
| Wind 10/50/100m speeds | Global Wind Atlas + ERA5 | Wind extrapolation |
| Terrain (slope, elevation, watershed) | DEM-derived tables | Hydro + suitability |
| Catchment morphology | Boothroyd et al. 2023 geodatabase | Hydro enrichment |
| Volcanoes/faults/heat flow | PHIVOLCS-derived datasets + `geothermal_volcanoes.json` | Geothermal suitability |
| Operating plants | Wikipedia-derived plant lists | Proximity boosts |
| Provincial consumption | DOE Annex 8 | Demand disaggregation + charts |
| Population | PSA census → `municipal_population` | Demand split |
| Tariff | Meralco historical rates | Financial math + defaults |
| Capacity/generation benchmarks | IRENA | Benchmarking tab |

Processing pipelines: `etl_orchestrator.py` (load orchestration), `build_catchment_enrichment.py` (watershed features), `municipality_suitability_builder.py` (the precomputed map scores), `load_catchment_to_supabase.py`, `data_cache.py` + Redis (all caching), `geospatial_service.py` (GeoJSON/centroids), `climate_service.py` (NASA POWER fetch). DOE spreadsheet cleaning is documented in `DOE_datacleaning_EXPLAINED.md` and implemented under `python_scripts/`.

### 12.2 What the user sees (frontend → backend map)

| Component | Shows | Fed by |
|---|---|---|
| `pages/Ecosim.jsx` + `components/ecosim/EcosimWizard` | The input flow (bill, location, savings goal) | POST → `build_ecosim_dashboard_response` |
| `components/ecosim/EcosimResults` | Scores, kWh estimates, recommendation, ratings | `options[]`, `recommended_source`, `explanation` |
| `components/ecosim/EcosimBOM` | Bill of materials for the recommended system | option/system sizing data |
| `components/ecosim/ProviderRecommendations` | Nearby installers/providers | `data/providers.json` matching |
| `components/ecosim/ExplanationModal` | Per-source "why" text | `explanations` + `ai_analysis.renewable_analysis` |
| `pages/EnergyHub.jsx` + `EnergyOverview` | National stats, forecast summary, model table | `build_overview` |
| `components/energyhub/EnergyTrends` + `PlotlyChart` | Historical + forecast charts | `build_trends`, `get_forecast` |
| `components/energyhub/EnergyMap` | Province/municipality/barangay choropleth | `build_map_data` |
| `components/energyhub/EnergySources` | Source shares | `get_source_breakdown` |
| `components/energyhub/ProvincialDemand` | Regional + municipal demand | `get_provincial_consumption`, `estimate_municipal_demand` |
| `components/energyhub/AiInsightPanel`, `ChartExplanation`, `MapExplanationCard` | AI-written insights | `get_ai_insight`, `analyze_chart`, `get_map_explanation` |
| `utils/ecosimAnalysis.js` | Resolves which explanation text to show (AI → static → fallback) | — |

### 12.3 Panelist cheat sheet

| If they ask… | Point to |
|---|---|
| "How do you convert the bill to kWh?" | §3.1 |
| "Where does your climate data come from?" | §3.3, §12.1 |
| "Why does solar lose output in heat?" | §4.1.1–4.1.2 |
| "What is the performance ratio?" | §4.1.5 |
| "How does wind power scale with speed?" | §4.2.2 (V³ law) |
| "How do you estimate hydro without river gauges?" | §4.3.2, §4.3.4 |
| "How is geothermal scored without a home device?" | §4.4 |
| "How do you rank the four sources?" | §5.1, §5.8 |
| "Why trust your criteria weights?" | §5.5.2 (AHP CR < 0.10), §5.5.4 |
| "Why is X scored high when weather looks average?" | §5.6 (plant proximity) |
| "How accurate are the results?" | §7 (confidence), §8.2–8.3 (backtest metrics) |
| "How does the forecast work / is it validated?" | §8.1–8.4 |
| "How do you get municipal demand from regional data?" | §9.3 |
| "How does the AI explain charts — and what if it's wrong?" | §10.3, §10.2 |
| "How does the chatbot ground its answers?" | §11 |
| "What happens when the AI is down?" | §10.2, §10.3 step 5 (deterministic fallbacks) |

### 12.4 Sources (citations embedded in the code)

- Asadi, M., Pourhossein, K., Noorollahi, Y., Marzband, M., & Iglesias, G. (2023). A new decision framework for hybrid solar and wind power plant site selection using linear regression modeling based on GIS-AHP. *Sustainability, 15*(10), 8359. https://doi.org/10.3390/su15108359
- Department of Energy (Philippines). (2022). *2019–2021 National Grid Emission Factor* (OMEF 0.6835 kg CO₂/kWh). Energy Regulatory Commission.
- Huda, A., et al. (2024). Techno-economic assessment of residential and farm-based photovoltaic systems in Indonesia. *Renewable Energy, 219*, 119886.
- Ngwakwe, C. C. (2025). Estimating the financial payback period for renewable energy investment: A quasi-systematic review. *Oblik i finansi*, (1), 59–66.
- Taduran, A. J. R., & Piao, L. P. (2025). Analyzing the performance of a 2.72 kWp rooftop grid-tied photovoltaic system in Tarlac City, Philippines. *IJETT, 73*(9), 318–327.
- Fahim, A., Al-Mamun, A., & Hassan, M. A. (2024). Toward a physics-based model of power coefficient in horizontal-axis wind turbines. *Wind Engineering, 48*(3), 245–262.
- Baker et al. (2023). Small wind turbine capacity factors.
- González-Hernández & Salas-Cabrera (2021). Betz limit (Cp ≤ 0.593) validation reference.
- Javadinejad et al. (2022). Runoff coefficients for small catchments by terrain slope.
- Butchers et al. (2021). Micro-hydro intake flow ranges (0.001–0.5 m³/s).
- Feyissa et al. (2024); Wang et al. (2025); Lillo et al. (2021). Run-of-river micro-hydro design flow factors, head ranges, and efficiencies.
- Boothroyd et al. (2023). Philippine river catchment geodatabase (PMC9994713) — catchment area, stream gradient, drainage density, hypsometric integral.
- King et al. (2004) / IEC 61853 & IEC 61724 — NOCT cell temperature model; performance-ratio benchmarks.
- Kumar et al. (2022). Air density for wind power calculations.

---

*Generated September 2026. Line references are a snapshot — verify against current code before quoting exact numbers in the defense.*
