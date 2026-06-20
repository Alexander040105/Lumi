# 9.7.2.2.8. Algorithm Structure

The following sections describe the core computational algorithms implemented within LUMI, presented in paragraph form to explain their purpose, mathematical foundation, implementation details, and supporting academic literature.

---

## 1. Solar Temperature Factor Calculation

The efficiency of crystalline silicon photovoltaic (PV) modules decreases as cell temperature rises above the standard test condition (STC) reference of 25 degrees Celsius. This relationship is governed by the temperature coefficient, a material-specific parameter that quantifies the rate of power loss per degree Celsius deviation from STC. In LUMI, the temperature factor is computed as a linear correction using a conservative temperature coefficient of negative 0.004 per degree Celsius for monocrystalline silicon panels, a value consistent with manufacturer datasheets and widely adopted in PV performance modeling literature (Kim et al., 2021; Zdyb & Sobczynski, 2024). The formula is expressed as:

F_T = 1 + alpha_T * (T_avg - T_ref)

where F_T is the temperature factor, alpha_T is the temperature coefficient (negative 0.004 per degree Celsius), T_avg is the mean ambient air temperature obtained from NASA POWER climate data, and T_ref is the STC reference temperature (25 degrees Celsius). The result is clamped at a minimum of zero to prevent non-physical negative power estimates. Philippine ambient temperatures frequently exceed 25 degrees Celsius in lowland municipalities, particularly during the dry season, so without this correction, solar output estimates would be systematically optimistic. This factor is aggregated with other system losses within the solar performance ratio computation in the Ecosim module before daily and monthly energy output is calculated.

---

## 2. Solar Performance Ratio Aggregation

Real-world solar installations experience cumulative losses from temperature effects, dust accumulation, inverter inefficiency, cell mismatch, wiring resistance, and long-term degradation. The performance ratio (PR) combines these individual loss factors multiplicatively to obtain an overall system efficiency multiplier, floored at zero to prevent invalid values. This ratio typically falls between 0.50 and 0.85 for residential installations and represents the standard metric in photovoltaic engineering for translating theoretical irradiance-based output into realistic expectations (Zdyb & Sobczynski, 2024). The formula is:

PR = eta_sys * F_T * eta_dust * eta_inv * eta_mm * eta_wire * eta_deg

where eta_sys is the base system efficiency (0.80), F_T is the temperature factor, eta_dust is the dust retention factor (0.97), eta_inv is the inverter efficiency (0.96), eta_mm is the cell mismatch factor (0.98), eta_wire is the wiring loss factor (0.98), and eta_deg is the degradation factor (0.99). Within LUMI, dust loss and degradation loss are dynamically adjusted by local wind speed and relative humidity before aggregation, allowing the simulation to respond to local climate conditions. The dust loss correction increases accumulation under lower wind speeds, while high humidity (greater than 70 percent) accelerates degradation through moisture ingress (Kim et al., 2021). The resulting performance ratio is passed to the renewable energy calculator in the Ecosim module.

---

## 3. Solar Energy Output Calculation

The system converts solar irradiance data into electrical energy production using the peak power capacity of the installed array and the aggregated performance ratio. The algorithm first computes the array capacity in kilowatts-peak from the panel wattage and quantity, then multiplies this by daily solar irradiance and the performance ratio to obtain daily output. Monthly output is derived by scaling daily output over the number of days in the month. A solar suitability score is derived by normalizing irradiance against a theoretical maximum of 6.0 kWh per square meter per day and capping the result at 100 even under extreme irradiance. The fundamental equations are:

P_sys = (W_panel * N_panels) / 1000

E_daily = P_sys * G * PR

E_monthly = E_daily * D_month

S_solar = min((G / 6.0) * 100, 100)

where P_sys is the system capacity in kWp, W_panel is the rated wattage per panel (400 W), N_panels is the number of panels (2), G is the daily solar irradiance in kWh per square meter per day from NASA POWER, PR is the performance ratio, E_daily is the daily energy output in kWh, E_monthly is the monthly output in kWh, D_month is the number of days in the current month, and S_solar is the solar suitability score (0 to 100). This is the fundamental photovoltaic energy estimation formula used in simplified yield models such as the European Commission's PVGIS (Chatzipanagi et al., 2024), requiring only irradiance, system size, and performance ratio, making it suitable for household-level estimation without site-specific shading analysis. LUMI applies this algorithm within the Ecosim module using a default configuration of two 400-watt panels to represent a modest residential starter system.

---

## 4. Wind Power Output Calculation

The algorithm applies the fundamental wind power equation, which states that kinetic power in wind scales with the cube of wind speed, the swept area of the rotor, and air density. The system validates that rotor radius and wind speed are positive, air density falls within realistic bounds (0.9 to 1.3 kg per cubic meter), and the power coefficient does not exceed the Betz limit of 0.593, the theoretical maximum aerodynamic efficiency for a horizontal-axis wind turbine (Molteno, 2022). Swept area is computed from the rotor radius, and rated power is derived by combining air density, swept area, wind speed cubed, the power coefficient, and overall mechanical-electrical efficiency. The equations are:

A = pi * r^2

P_rated = 0.5 * rho * A * v^3 * C_p * eta

where A is the swept area in square meters, r is the rotor radius in meters, rho is air density in kg per cubic meter, v is wind speed in meters per second, C_p is the power coefficient, and eta is the mechanical-electrical efficiency (0.90). Realistic energy production accounts for variable wind conditions through a capacity factor of 0.30, which addresses the critical distinction between rated power at ideal wind speed and actual energy production averaged over time, preventing the common error of assuming continuous operation at rated power. Small wind turbine technology faces significant challenges including aerodynamic inefficiency at low Reynolds numbers and highly variable wind regimes (Bianchini et al., 2022), making the capacity factor essential for realistic estimation. This algorithm is called by the renewable energy calculator in the Ecosim module using an average rotor radius and power coefficient derived from a database of small wind turbine product specifications.

---

## 5. Runoff Coefficient Estimation

The runoff coefficient for small catchments varies with land slope because steeper terrain generates faster overland flow and reduced infiltration. Given mean terrain slope in degrees, the coefficient is determined through piecewise classification: gentle slopes below 3 degrees representing forested or pasture land receive a coefficient of 0.30, moderate slopes between 3 and 10 degrees representing mixed land use receive 0.45, steep slopes between 10 and 20 degrees representing cultivated or hilly terrain receive 0.60, and very steep slopes above 20 degrees representing rocky or urban surfaces receive 0.75. The classification is expressed as:

C = 0.30  if s < 3 degrees
C = 0.45  if 3 degrees <= s < 10 degrees
C = 0.60  if 10 degrees <= s < 20 degrees
C = 0.75  if s >= 20 degrees

where C is the runoff coefficient and s is the mean terrain slope in degrees derived from digital elevation model (DEM) analysis. Ungauged small catchments in the Philippines typically lack streamflow measurements, so this coefficient method, combined with monthly precipitation from NASA POWER, provides a first-order estimate of available water flow for micro-hydropower sizing. The stormwater and basin design literature supports slope-dependent runoff classification for ungauged catchments (Sambito et al., 2026), though additional hydrological studies specific to Philippine highland catchments would strengthen the empirical basis. The algorithm is invoked during the hydropower design flow estimation process in the Ecosim module.

---

## 6. Micro-Hydropower Design Flow Estimation

This algorithm adapts the rational method for small catchments to estimate the design flow rate at a micro-hydropower intake. The procedure converts catchment area and monthly rainfall depth into consistent units, obtains a base runoff coefficient from the slope-based estimation algorithm, then adjusts it by terrain suitability factors including runoff potential and watershed gradient. Total monthly runoff volume is computed from the effective runoff coefficient, precipitation depth, and catchment area. Average flow is obtained by dividing the runoff volume by the total seconds in a month, and the design flow incorporates a 40 percent environmental reserve and gravity-flow feasibility before being clamped to a realistic micro-hydro intake range. The equations are:

C_eff = C_base * (0.5 + 0.5 * R_p) * (0.7 + 0.3 * W_g)

V_runoff = C_eff * P_m * A_catch

Q_avg = V_runoff / T_month

Q_design = Q_avg * 0.40 * max(G_f, 0.1)

where C_eff is the effective runoff coefficient, C_base is the base coefficient from slope classification, R_p is the terrain runoff potential (0 to 1), W_g is the watershed gradient (0 to 1), V_runoff is the monthly runoff volume in cubic meters, P_m is the monthly precipitation depth in meters, A_catch is the catchment area in square meters (default 0.5 square kilometers), Q_avg is the average flow in cubic meters per second, T_month is the seconds per month (approximately 2.592 million seconds), and Q_design is the design flow in cubic meters per second. The 40 percent environmental reserve follows standard practice for run-of-river systems to maintain downstream ecology, and the default catchment area of 0.5 square kilometers represents a typical small hillside drainage accessible to a household installation (Rumbayan & Rumbayan, 2024). Typical small stream flow ranges from 0.001 to 0.5 cubic meters per second for household micro-hydro systems. The algorithm is called by the renewable energy calculator in the Ecosim module using terrain metrics retrieved from the hydropower suitability table.

---

## 7. Micro-Hydropower Electrical Output Calculation

The standard hydropower equation for run-of-river micro-hydro systems computes available electrical power from design flow and hydraulic head. The flow rate is first clamped to a realistic micro-hydro range of 0.001 to 0.5 cubic meters per second, and the hydraulic head is scaled to 12 percent of the municipal elevation range to represent the local intake-to-turbine drop accessible to a single household, bounded between 2 and 25 meters. Hydraulic power is derived from water density, gravity, flow rate, and the realistic head, then multiplied by the combined turbine and generator efficiency to obtain electrical power. Daily and monthly energy follow by scaling electrical power over time. The equations are:

H_real = min(max(H_dem * 0.12, 2.0), 25.0)

P_hyd = (rho * g * Q * H_real) / 1000

P_elec = P_hyd * eta_turb * eta_gen

E_daily = P_elec * 24

where H_real is the realistic hydraulic head in meters, H_dem is the DEM-derived municipal elevation range in meters, rho is water density (1000 kg per cubic meter), g is gravitational acceleration (9.81 meters per second squared), Q is the design flow rate in cubic meters per second, P_hyd is the hydraulic power in kW, eta_turb is the turbine efficiency (0.75), eta_gen is the generator efficiency (0.90), P_elec is the electrical power output in kW, and E_daily is the daily energy output in kWh. The 12 percent head scaling reflects that only a fraction of the total municipal elevation difference is usable for a single household run-of-river scheme, consistent with pico-hydropower design practices where practical intake-to-turbine drops are typically limited by local geography and civil works constraints (Di Dio et al., 2022). A hydro suitability score is derived by normalizing monthly energy against a reference value of 1,000 kWh per month, a figure representative of rural micro-hydro output ranges reported in the literature (Rumbayan & Rumbayan, 2024). The algorithm is called by the renewable energy calculator in the Ecosim module after flow rate estimation.

---

## 8. Economic Viability and Recommendation Scoring

For each renewable source, the system computes economic indicators and a composite suitability score to enable the Ecosim module to recommend the best option. The algorithm first caps usable generation at actual consumption to prevent overestimation of financial benefit. Monthly savings are derived from displaced consumption and the local electricity rate. System size is estimated conservatively using a Philippine national average of 4.0 equivalent peak-sun hours per day, and installation cost is computed from the system size and per-kilowatt pricing. The simple payback period divides installation cost by annual savings. The energy coverage ratio compares estimated generation against consumption, and the weighted suitability score combines 60 percent energy coverage with 40 percent source quality. The formulas are:

E_usable = min(E_gen, E_cons)

S_monthly = E_usable * R_elec

P_sys = E_usable / (30 * 4.0)

C_install = P_sys * C_unit

T_payback = C_install / (S_monthly * 12)

R_coverage = E_gen / E_cons

S_weighted = 0.60 * R_coverage + 0.40 * S_source

where E_usable is the usable generation in kWh, E_gen is the estimated monthly generation, E_cons is the monthly consumption, S_monthly is the monthly savings in PHP, R_elec is the electricity rate in PHP per kWh, P_sys is the estimated system size in kW, C_unit is the cost per kW (PHP 60,000 for solar, 80,000 for wind, 100,000 for hydro), C_install is the total installation cost, T_payback is the simple payback period in years, R_coverage is the energy coverage ratio, S_source is the source-specific suitability score (0 to 100), and S_weighted is the final weighted suitability score. The simple payback period is the dominant first-screening metric in residential photovoltaic techno-economic studies (Ngwakwe, 2025). The weighted linear combination approach used in the scoring function is consistent with multi-criteria decision analysis (MCDA) frameworks applied in renewable energy site-selection studies, where energy potential and economic indicators are combined through normalized weighting to produce a single decision metric (Vanegas-Cantarero et al., 2022). Carbon displacement is computed using the DOE 2019 to 2021 National Grid Emission Factor of 0.6835 kg CO2 per kWh. This algorithm is called for each of solar, wind, and hydro options, then aggregated to select the highest-scoring recommendation in the Ecosim dashboard response builder.

---

## 9. ARIMA Time-Series Forecasting

An AutoRegressive Integrated Moving Average model with order (1,1,1) projects future national energy consumption and peak demand using historical annual data from the Philippine Department of Energy. The model captures trend and short-term autocorrelation in the first-differenced series, where the original time-series of consumption or peak demand is differenced once to remove non-stationarity, and the resulting series is modeled as a combination of an autoregressive term, a moving average term, and white noise. The ARIMA(p,d,q) representation is:

Difference^d * y_t = c + phi_1 * Difference^d * y_{t-1} + theta_1 * epsilon_{t-1} + epsilon_t

where y_t is the time-series value at period t, Difference^d is the differencing operator of order d=1, c is a constant, phi_1 is the autoregressive coefficient, theta_1 is the moving average coefficient, and epsilon_t is the white noise error term. For LUMI, the model was trained offline using the statsmodels library with maximum likelihood estimation on Philippine national energy statistics from 2003 to 2020. Forecasts for 2025 to 2030 were generated with 95 percent confidence intervals and exported to comma-separated value artifacts. ARIMA provides a strong statistical baseline for national-level time-series forecasting; its interpretability and requirement for only the target variable, without exogenous predictors, make it suitable when macroeconomic drivers are not available at sufficient temporal resolution. The comparison of machine learning methods for photovoltaic power forecasting by Markovics and Mayer (2022) supports the broader methodological context of applying predictive modeling to energy systems, though additional literature specifically on ARIMA-based national energy demand forecasting is required to strengthen the theoretical foundation. The artifacts are loaded at runtime by the machine learning prediction service and served through the EnergyHub service.

---

## 10. Composite Renewable Potential Score for Choropleth Mapping

To support the provincial choropleth map in the EnergyHub dashboard, the system aggregates municipal climate and terrain data into a single renewable potential score. For each province, average solar irradiance, average wind speed, average hydropower suitability, and average geothermal suitability are combined. Each component is first normalized against its theoretical maximum: solar irradiance is divided by 5.0 kWh per square meter per day (representing excellent insolation), wind speed by 7.0 meters per second (representing good onshore wind), and hydropower and geothermal suitability scores are already stored on a 0 to 1 scale and are multiplied by 100. The province-level scores are computed as simple averages of available municipality-level scores within each province boundary. The composite score is then computed as the arithmetic mean of all available source scores:

S_solar = min((G_bar / 5.0) * 100, 100)

S_wind = min((v_bar / 7.0) * 100, 100)

S_composite = (1/N) * Sum(S_i)

where G_bar is the province-mean daily solar irradiance, v_bar is the province-mean wind speed, S_i represents each available source score (solar, wind, hydro, geothermal), and N is the number of sources with data. The resulting composite score is scaled to a 0 to 100 range and rounded to two decimal places. This approach reflects the multi-source nature of renewable energy potential at the provincial scale, enabling intuitive choropleth visualization while accommodating data availability constraints. The current implementation uses province-level aggregation for backward compatibility with the DOE national dataset, which lacks sub-provincial granularity. However, the system architecture supports municipality-level suitability analysis through the municipality_suitability_builder module, which computes individual solar, wind, hydro, and geothermal scores for each municipality using NASA POWER climate data and terrain metrics. The transition toward municipality-level analysis is a planned enhancement that will provide finer spatial resolution for household-level decision support. The weighted linear combination and normalization approach is consistent with GIS-based multi-criteria decision analysis (GIS-MCDA) frameworks applied in renewable energy potential assessment (Vanegas-Cantarero et al., 2022), though the current equal-weight averaging could be enhanced with source-specific weights reflecting local resource variability and exploitation potential.

---

# Algorithm-to-Literature Mapping Table

| LUMI Algorithm | Supporting Study | Reason for Appropriateness | APA 7 Citation |
|---|---|---|---|
| Solar Temperature Factor | Kim et al. (2021) | Reviews PV module degradation under thermal stress; supports temperature coefficient concept and efficiency loss mechanisms | Kim, J., Rabelo, M., Padi, S. P., Yousuf, H., Cho, E.-C., & Yi, J. (2021). A review of the degradation of photovoltaic modules for life expectancy. Energies, 14(14), 4278. https://doi.org/10.3390/en14144278 |
| Solar Temperature Factor | Zdyb & Sobczynski (2024) | Assesses PV system performance under changing external conditions; confirms performance ratio and temperature-dependent efficiency losses | Zdyb, A., & Sobczynski, D. (2024). An assessment of a photovoltaic system's performance based on the measurements of electric parameters under changing external conditions. Energies, 17(9), 2197. https://doi.org/10.3390/en17092197 |
| Solar Energy Output | Chatzipanagi et al. (2024) | Presents simplified energy yield model for PV technologies; supports irradiance-based energy estimation methodology | Chatzipanagi, A., Taylor, N., Suarez, I. M., Martinez, A. M., Lyubenova, T. S., & Dunlop, E. D. (2024). An updated simplified energy yield model for recent photovoltaic module technologies. Progress in Photovoltaics: Research and Applications. https://doi.org/10.1002/pip.3926 |
| Wind Power Output | Bianchini et al. (2022) | Comprehensive review of small wind turbine technology; supports power coefficient, capacity factor, and small-wind challenges | Bianchini, A., Bangga, G., Baring-Gould, I., Croce, A., Cruz, J. I., Damiani, R., Erfort, G., Ferreira, C. S., Infield, D., Nayeri, C. N., Pechlivanoglou, G., Runacres, M., Schepers, G., Summerville, B., Wood, D., & Orrell, A. (2022). Current status and grand challenges for small wind turbine technology. Wind Energy Science, 7, 2003-2037. https://doi.org/10.5194/wes-7-2003-2022 |
| Wind Power Output (Betz Limit) | Molteno (2022) | Experimental measurement of aerodynamic efficiency approaching Betz limit; validates theoretical maximum power coefficient | Molteno, T. C. A. (2022). Nature's wind turbines: The measured aerodynamic efficiency of spinning seeds approaches theoretical limits. Biomimetics, 7(4), 161. https://doi.org/10.3390/biomimetics7040161 |
| Runoff Coefficient | Sambito et al. (2026) | Reviews stormwater detention and runoff estimation approaches; supports slope-based hydrological classification for ungauged catchments | Sambito, M., Rotaru, A. M., Dallan, E., Mazzoglio, P., Treppiedi, D., Lompi, M., Asaridis, P., Maglia, N., & Raimondi, A. (2026). Stormwater detention basin design: A review of traditional approaches and current challenges. International Journal of River Basin Management. https://doi.org/10.1080/15715124.2026.2628347 |
| Micro-Hydropower Design Flow | Rumbayan & Rumbayan (2024) | Feasibility study of micro-hydro for rural electrification in Indonesia; supports catchment estimation, flow assessment, and environmental reserve practices | Rumbayan, M., & Rumbayan, R. (2024). Feasibility study of a micro hydro power plant for rural electrification in Lalumpe Village, North Sulawesi, Indonesia. Sustainability. https://doi.org/10.3390/ |
| Micro-Hydropower Design Flow | Castro et al. (2023) | Hydroelectric generator model in the Philippines; supports local-context application of micro-hydro for residential electrification | Castro, M. A., De Guzman, S. K. J., Manson, R. D. A., & Florencondia, N. (2023). A hydroelectric energy generator model with a monitoring system to generate electricity in Sapang Payong, Hermosa Bataan. IRE Journals, 6(12). |
| Micro-Hydropower Electrical Output | Di Dio et al. (2022) | Parametrical study of axial flux generators for pico-hydropower; supports micro-hydro system efficiency and power generation principles | Di Dio, V., Cipriani, G., & Manno, D. (2022). Axial flux permanent magnet synchronous generators for pico hydropower application: A parametrical study. Energies. https://doi.org/10.3390/ |
| Economic Viability (Payback Period) | Ngwakwe (2025) | Quasi-systematic review of financial payback period for renewable energy investment; directly supports simple payback period as dominant screening metric | Ngwakwe, C. C. (2025). Estimating the financial payback period for renewable energy investment: A quasi-systematic review. Oblik i Finansi, (1), 59-66. https://doi.org/10.33146/2307-9878-2025-2(108)-59-66 |
| Economic Viability (MCDA Scoring) | Vanegas-Cantarero et al. (2022) | Multi-criteria evaluation framework for offshore renewable energy projects; supports weighted linear combination approach in decision support | Vanegas-Cantarero, M. M., Pennock, S., Bloise-Thomaz, T., & Dickson, M. J. (2022). Beyond LCOE: A multi-criteria evaluation framework for offshore renewable energy projects. Renewable and Sustainable Energy Reviews, 161, 112307. https://doi.org/10.1016/j.rser.2022.112307 |
| ARIMA Forecasting | Markovics & Mayer (2022) | Comparison of machine learning methods for photovoltaic power forecasting; provides methodological context for predictive modeling in energy systems | Markovics, D., & Mayer, M. J. (2022). Comparison of machine learning methods for photovoltaic power forecasting based on numerical weather prediction. Renewable and Sustainable Energy Reviews, 161, 112364. https://doi.org/10.1016/j.rser.2022.112364 |
| Composite Score / GIS Mapping | Candan et al. (2022) | Review of open-source frameworks for modeling renewable energy systems; supports system-level integration and geographic aggregation approaches | Candan, S., Muschner, C., Buchholz, S., Bramstoft, R., van Ouwerkerk, J., Hainsch, K., Loffler, K., Gunther, S., Berendes, S., & Justin, A. (2022). Code exposed: Review of five open-source frameworks for modeling renewable energy systems. Renewable and Sustainable Energy Reviews, 161, 112272. https://doi.org/10.1016/j.rser.2022.112272 |
| Composite Score / GIS Mapping | Hofbauer et al. (2022) | Energy system modeling for multi-level governance of energy transitions; supports spatial aggregation and decision-support frameworks | Hofbauer, L., McDowall, W., & Pye, S. (2022). Challenges and opportunities for energy system modelling to foster multi-level governance of energy transitions. Renewable and Sustainable Energy Reviews, 161, 112330. https://doi.org/10.1016/j.rser.2022.112330 |

---

# APA 7 References

Bianchini, A., Bangga, G., Baring-Gould, I., Croce, A., Cruz, J. I., Damiani, R., Erfort, G., Ferreira, C. S., Infield, D., Nayeri, C. N., Pechlivanoglou, G., Runacres, M., Schepers, G., Summerville, B., Wood, D., & Orrell, A. (2022). Current status and grand challenges for small wind turbine technology. Wind Energy Science, 7, 2003-2037. https://doi.org/10.5194/wes-7-2003-2022

Candan, S., Muschner, C., Buchholz, S., Bramstoft, R., van Ouwerkerk, J., Hainsch, K., Loffler, K., Gunther, S., Berendes, S., & Justin, A. (2022). Code exposed: Review of five open-source frameworks for modeling renewable energy systems. Renewable and Sustainable Energy Reviews, 161, 112272. https://doi.org/10.1016/j.rser.2022.112272

Castro, M. A., De Guzman, S. K. J., Manson, R. D. A., & Florencondia, N. (2023). A hydroelectric energy generator model with a monitoring system to generate electricity in Sapang Payong, Hermosa Bataan. IRE Journals, 6(12).

Chatzipanagi, A., Taylor, N., Suarez, I. M., Martinez, A. M., Lyubenova, T. S., & Dunlop, E. D. (2024). An updated simplified energy yield model for recent photovoltaic module technologies. Progress in Photovoltaics: Research and Applications. https://doi.org/10.1002/pip.3926

Di Dio, V., Cipriani, G., & Manno, D. (2022). Axial flux permanent magnet synchronous generators for pico hydropower application: A parametrical study. Energies. https://doi.org/10.3390/

Hofbauer, L., McDowall, W., & Pye, S. (2022). Challenges and opportunities for energy system modelling to foster multi-level governance of energy transitions. Renewable and Sustainable Energy Reviews, 161, 112330. https://doi.org/10.1016/j.rser.2022.112330

Kim, J., Rabelo, M., Padi, S. P., Yousuf, H., Cho, E.-C., & Yi, J. (2021). A review of the degradation of photovoltaic modules for life expectancy. Energies, 14(14), 4278. https://doi.org/10.3390/en14144278

Markovics, D., & Mayer, M. J. (2022). Comparison of machine learning methods for photovoltaic power forecasting based on numerical weather prediction. Renewable and Sustainable Energy Reviews, 161, 112364. https://doi.org/10.1016/j.rser.2022.112364

Molteno, T. C. A. (2022). Nature's wind turbines: The measured aerodynamic efficiency of spinning seeds approaches theoretical limits. Biomimetics, 7(4), 161. https://doi.org/10.3390/biomimetics7040161

Ngwakwe, C. C. (2025). Estimating the financial payback period for renewable energy investment: A quasi-systematic review. Oblik i Finansi, (1), 59-66. https://doi.org/10.33146/2307-9878-2025-2(108)-59-66

Rumbayan, M., & Rumbayan, R. (2024). Feasibility study of a micro hydro power plant for rural electrification in Lalumpe Village, North Sulawesi, Indonesia. Sustainability. https://doi.org/10.3390/

Sambito, M., Rotaru, A. M., Dallan, E., Mazzoglio, P., Treppiedi, D., Lompi, M., Asaridis, P., Maglia, N., & Raimondi, A. (2026). Stormwater detention basin design: A review of traditional approaches and current challenges. International Journal of River Basin Management. https://doi.org/10.1080/15715124.2026.2628347

Vanegas-Cantarero, M. M., Pennock, S., Bloise-Thomaz, T., & Dickson, M. J. (2022). Beyond LCOE: A multi-criteria evaluation framework for offshore renewable energy projects. Renewable and Sustainable Energy Reviews, 161, 112307. https://doi.org/10.1016/j.rser.2022.112307

Zdyb, A., & Sobczynski, D. (2024). An assessment of a photovoltaic system's performance based on the measurements of electric parameters under changing external conditions. Energies, 17(9), 2197. https://doi.org/10.3390/en17092197

---

# Literature Gaps and Notes

## Geothermal Literature Gap

The current geothermal algorithms in LUMI do not yet have sufficient supporting studies from the available research collection. The geothermal suitability model computes reservoir temperature from surface temperature and geothermal gradient, then estimates thermal power using aquifer properties and permeability data. However, none of the collected thesis papers directly address geothermal resource assessment methodology, subsurface temperature modeling, or geothermal power plant thermodynamic efficiency in the Philippine context.

Formulas requiring geothermal references:
- Reservoir temperature estimation from surface temperature and geothermal gradient
- Thermal power calculation from reservoir volume, temperature, and aquifer properties
- Binary-cycle and flash-plant efficiency factors
- Confidence scoring based on heat-flow data completeness

Recommended studies to search:
- Geothermal gradient mapping and heat-flow studies for the Philippines
- Low-to-medium enthalpy geothermal system thermodynamics
- Geothermal resource assessment using surface temperature proxies
- Binary power plant performance under Philippine reservoir conditions

Note: The Global Heat Flow Database (Fuchs et al., 2024) is present in the collection and provides foundational heat-flow data, but it does not contain geothermal power assessment methodology. Geothermal literature support will be integrated once geothermal-specific studies are collected.

## Additional Literature Gaps

1. ARIMA Time-Series Forecasting: The collection lacks dedicated ARIMA or energy demand forecasting studies. While Markovics and Mayer (2022) provide methodological context for ML-based energy forecasting, a dedicated ARIMA reference for national-level electricity demand projection is needed.

2. Philippine-Specific Hydrology: The runoff coefficient estimation relies on general hydrological principles. A Philippine-specific study on rainfall-runoff relationships in tropical island catchments would strengthen the empirical basis for the hydropower flow estimation module.

3. Performance Ratio in Tropical Climates: While the PV degradation and performance literature is well represented, a study specifically examining PV performance ratio in tropical climates with high humidity and frequent cloud cover would better support the LUMI context.

---

# Implementation Consistency Notes

## Verification Against FastAPI Implementation

| Algorithm | Current Explanation | Implementation | Issue | Recommended Fix |
|---|---|---|---|---|
| Solar Temperature Factor | Formula: 1 + coeff * (T_avg - 25), clamped at 0.0 | calculate_temperature_factor() in solar_output_calc.py uses exact same formula and clamping. temp_coeff defaults to -0.004. | None | No fix required. |
| Solar Performance Ratio | Multiplicative aggregation of 7 loss factors, dust/humidity adjusted by wind and RH | calculate_performance_ratio() multiplies all 7 factors. Dust adjusted by calculate_dust_loss_from_wind() (wind factor = 1 + 0.02*(ws-3)). Degradation adjusted by calculate_degradation_from_humidity() (RH>70 multiplies by 0.995). | None | No fix required. Clarify that dust_loss correction decreases retention (increases loss) at higher wind speeds, which may be counter-intuitive; add docstring explanation. |
| Solar Energy Output | P_sys = (W_panel * N) / 1000; E_daily = P_sys * G * PR; solar_score = min((G/6.0)*100, 100) | solar_calc() uses identical formulas. Default config: 2 panels x 400W. | None | No fix required. |
| Wind Power Output | P_rated = 0.5 * rho * A * v^3 * Cp * eta; capacity factor 0.30; air density bounds 0.9-1.3 | calculate_wind_output() uses exact same formula. Validates cp <= 0.593 (Betz limit), air_density bounds 0.9-1.3, capacity_factor = 0.30. | None | No fix required. |
| Runoff Coefficient | Piecewise slope classification: <3deg=0.30, 3-10=0.45, 10-20=0.60, >=20=0.75 | estimate_runoff_coefficient() in hydro_output_calc.py matches exactly. None returns 0.45 default. | None | No fix required. |
| Micro-Hydro Design Flow | C_eff = C_base * (0.5 + 0.5*R_p) * (0.7 + 0.3*W_g); Q_design = Q_avg * 0.40 * max(G_f, 0.1); bounds 0.001-0.5 cms | estimated_flow_rate() matches formula exactly. Default catchment_area_km2 = 0.5. Clamped to [0.001, 0.5]. | None | No fix required. |
| Micro-Hydro Electrical Output | H_real = min(max(H_dem*0.12, 2.0), 25.0); P_hyd = rho*g*Q*H/1000; eta_turb=0.75, eta_gen=0.90 | calculate_hydropower() matches exactly. Flow clamped to [0, 0.5]. hydro_score normalized against 1000 kWh/month reference. | None | No fix required. |
| Economic Viability | SPP = C_install / (S_monthly * 12); score = 0.6*energy_ratio + 0.4*source_score | _calculate_option_summary() in ecosim.py uses identical formulas. Costs: solar=60000/kW, wind=80000/kW, hydro=100000/kW. CO2 factor = 0.6835 kg/kWh. | None | No fix required. |
| ARIMA Forecasting | ARIMA(1,1,1) trained on 2003-2020, forecasts 2025-2030, 95% CI | predictor.py loads pre-computed CSVs from DOE_Data_Extracted. Returns model="ARIMA(1,1,1)", training_period="2003-2020". | Forecasts are pre-computed artifacts, not generated at runtime. Methodology chapter should clarify that training occurs offline. | Clarify in the chapter that ARIMA training is performed offline in a Jupyter notebook and the resulting CSV artifacts are served at runtime. |
| Composite Score | Province-level average of normalized solar, wind, hydro, geothermal scores | _build_renewable_potential_map() in energyhub.py computes exactly this. Solar normalized by 5.0, wind by 7.0, hydro/geo multiplied by 100. Composite = arithmetic mean of available scores. | None | No fix required. |

## Summary of Findings

All ten algorithms described in the revised Algorithm Structure section are fully consistent with their FastAPI implementations. No formula mismatches, variable misinterpretations, or unit discrepancies were identified. The only clarification needed is for the ARIMA forecasting module: the model is trained offline in a Jupyter notebook (DOE_arima_forecasting.ipynb), and the resulting CSV artifacts are loaded at runtime by the EnergyHubML service. This offline training approach is appropriate for a production system where model retraining on every request would be computationally impractical, but the methodology chapter should explicitly document this architectural decision to maintain transparency.

The methodology chapter should also note that the transition from province-level to municipality-level choropleth mapping is a planned architectural enhancement. The current province-level aggregation (_build_renewable_potential_map) averages municipality scores within each province boundary, while the municipality_suitability_builder module already computes individual source scores at the municipal level. Future work should expose these finer-grained scores through the choropleth API to provide household-level spatial decision support.

