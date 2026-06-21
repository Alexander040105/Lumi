# 9.7.2.2.8. Algorithm Structure

The following sections describe the core computational algorithms implemented within LUMI. Each algorithm is categorized by its domain and presented in concise paragraph form to explain its purpose, mechanism, and application within the system.

**Solar Temperature Factor Calculation**

The system adjusts photovoltaic output for deviations from the standard test condition temperature of 25 degrees Celsius. Solar panel efficiency decreases as cell temperature rises above this reference, and the temperature factor quantifies this loss as a linear function of temperature deviation (Kim et al., 2021; Zdyb & Sobczynski, 2024). Given a mean air temperature and a conservative industry-standard temperature coefficient of negative 0.004 per degree Celsius for crystalline silicon panels, the factor is computed and clamped at a minimum of zero to prevent negative power estimates. Philippine ambient temperatures frequently exceed 25 degrees Celsius in lowland municipalities, so without this correction, solar output estimates would be systematically optimistic. This factor is aggregated with other system losses within the solar performance ratio computation in the Ecosim module before daily and monthly energy output is calculated.

**Solar Performance Ratio Aggregation**

Real-world solar installations experience losses from temperature, dust accumulation, inverter inefficiency, cell mismatch, wiring resistance, and long-term degradation. The performance ratio combines these individual loss factors multiplicatively to obtain an overall system efficiency multiplier, floored at zero to prevent invalid values (Zdyb & Sobczynski, 2024). This ratio typically falls between 0.5 and 0.85 for residential installations and is the standard metric in photovoltaic engineering for translating theoretical irradiance-based output into realistic expectations, consistent with IEC 61724 guidelines. Within LUMI, dust loss and degradation loss are optionally adjusted by wind speed and humidity before aggregation, allowing the simulation to respond to local climate conditions. The result is passed to the renewable energy calculator in the Ecosim module.

**Solar Energy Output Calculation**

The system converts solar irradiance data into electrical energy production using the peak power capacity of the installed array and the aggregated performance ratio. The algorithm first computes the array capacity in kilowatts-peak from the panel wattage and quantity, then multiplies this by daily solar irradiance and the performance ratio to obtain daily output. Monthly output is derived by scaling daily output over the number of days in the month. A solar suitability score is derived by normalizing irradiance against a theoretical maximum and capping the result at 100 even under extreme irradiance. This is the fundamental photovoltaic energy estimation formula used worldwide, consistent with the simplified yield model methodology for recent PV technologies (Chatzipanagi et al., 2024), requiring only irradiance from NASA POWER, system size, and performance ratio, making it suitable for household-level estimation without site-specific shading analysis. LUMI applies this algorithm within the Ecosim module using a default configuration of two 400-watt panels to represent a modest residential starter system.

**Wind Power Output Calculation**

The algorithm applies the fundamental wind power equation, which states that kinetic power in wind scales with the cube of wind speed, the swept area of the rotor, and air density (Bianchini et al., 2022). The system validates that rotor radius and wind speed are positive, air density falls within realistic bounds, and the power coefficient does not exceed the Betz limit of 0.593, the theoretical maximum aerodynamic efficiency for a horizontal-axis wind turbine (Molteno, 2022). Swept area is computed from the rotor radius, and rated power is derived by combining air density, swept area, wind speed cubed, the power coefficient, and overall mechanical-electrical efficiency. Realistic energy production accounts for variable wind conditions through a capacity factor, which addresses the critical distinction between rated power at ideal wind speed and actual energy production averaged over time, preventing the common error of assuming continuous operation at rated power. This algorithm is called by the renewable energy calculator in the Ecosim module using average rotor radius and power coefficient derived from small wind turbine product databases.

**Runoff Coefficient Estimation**

The runoff coefficient for small catchments varies with land slope because steeper terrain generates faster overland flow and less infiltration (Sambito et al., 2026). Given mean terrain slope in degrees, the coefficient is determined through piecewise classification: gentle slopes below 3 degrees representing forested or pasture land receive a coefficient of 0.30, moderate slopes between 3 and 10 degrees representing mixed land use receive 0.45, steep slopes between 10 and 20 degrees representing cultivated or hilly terrain receive 0.60, and very steep slopes above 20 degrees representing rocky or urban surfaces receive 0.75. Ungauged small catchments in the Philippines typically lack streamflow measurements, so this coefficient method, combined with monthly precipitation from NASA POWER, provides a first-order estimate of available water flow for micro-hydropower sizing. The algorithm is invoked during the hydropower design flow estimation process in the Ecosim module.

**Micro-Hydropower Design Flow Estimation**

This algorithm adapts the rational method for small catchments to estimate the design flow rate at a micro-hydropower intake. The procedure converts catchment area and monthly rainfall depth into consistent units, obtains a base runoff coefficient from the slope-based estimation algorithm, then adjusts it by terrain suitability factors including runoff potential and watershed gradient. Total monthly runoff volume is computed from the effective runoff coefficient, precipitation depth, and catchment area. Average flow is obtained by dividing the runoff volume by the total seconds in a month, and the design flow incorporates a 40 percent environmental reserve and gravity-flow feasibility before being clamped to a realistic micro-hydro intake range. The 40 percent environmental reserve follows standard practice for run-of-river systems to maintain downstream ecology, and the default catchment area represents a typical small hillside drainage accessible to a household installation (Rumbayan & Rumbayan, 2024). The algorithm is called by the renewable energy calculator in the Ecosim module using terrain metrics retrieved from the hydropower suitability table.

**Micro-Hydropower Electrical Output Calculation**

The standard hydropower equation for run-of-river micro-hydro systems computes available electrical power from design flow and hydraulic head (Di Dio et al., 2022). The flow rate is first clamped to a realistic micro-hydro range, and the hydraulic head is scaled to 12 percent of the municipal elevation range to represent the local intake-to-turbine drop accessible to a single household, bounded between 2 and 25 meters. Hydraulic power is derived from water density, gravity, flow rate, and the realistic head, then multiplied by the combined turbine and generator efficiency to obtain electrical power. Daily and monthly energy follow by scaling electrical power over time. A hydro suitability score is derived by normalizing monthly energy against a reference value for rural micro-hydro systems (Castro et al., 2023). The 12 percent head scaling reflects that only a fraction of the total municipal elevation difference is accessible to a single household intake. The algorithm is called by the renewable energy calculator in the Ecosim module after flow rate estimation.

**Economic Viability and Recommendation Scoring**

For each renewable source, the system computes economic indicators and a composite suitability score to enable the Ecosim module to recommend the best option. The algorithm first caps usable generation at actual consumption to prevent overestimation of financial benefit. Monthly savings are derived from displaced consumption and the local electricity rate. System size is estimated conservatively using a Philippine national average of 4 equivalent peak-sun hours per day, and installation cost is computed from the system size and per-kilowatt pricing. The simple payback period divides installation cost by annual savings. The energy coverage ratio compares estimated generation against consumption, and the weighted suitability score combines 60 percent energy coverage with 40 percent source quality, following the weighted linear combination approach used in GIS-MCDA renewable energy site-selection studies (Vanegas-Cantarero et al., 2022). Carbon displacement is computed using the DOE 2019-2021 National Grid Emission Factor. The simple payback period is the dominant first-screening metric in residential photovoltaic techno-economic studies (Ngwakwe, 2025). This algorithm is called for each of solar, wind, and hydro options, then aggregated to select the highest-scoring recommendation in the Ecosim dashboard response builder.

**ARIMA Time-Series Forecasting**

An AutoRegressive Integrated Moving Average model with order one-one-one projects future national energy consumption and peak demand using historical annual data. The model captures trend and short-term autocorrelation in the first-differenced series, where the original time-series of consumption or peak demand is differenced once to remove non-stationarity, and the resulting series is modeled as a combination of an autoregressive term, a moving average term, and white noise. The model was trained offline using the statsmodels library with maximum likelihood estimation on Philippine national energy statistics from 2003 to 2020. Forecasts for 2025 to 2030 were generated with 95 percent confidence intervals and exported to comma-separated value artifacts. ARIMA provides a strong statistical baseline for national-level time-series forecasting; its interpretability and requirement for only the target variable, without exogenous predictors, make it suitable when macroeconomic drivers are not available at sufficient temporal resolution (Markovics & Mayer, 2022). The artifacts are loaded at runtime by the machine learning prediction service and served through the EnergyHub service.

**Composite Renewable Potential Score for Choropleth Mapping**

To support the provincial choropleth map in the EnergyHub dashboard, the system aggregates municipal climate and terrain data into a single renewable potential score. For each province, average solar irradiance, average wind speed, and average hydropower suitability are combined using weighted linear combination. Each component is normalized against its theoretical maximum, then weighted and summed: solar receives the largest weight at 40 percent, while wind and hydropower each receive 30 percent. The resulting composite score is scaled to a 0 to 100 range and rounded to two decimal places. The weighting reflects that solar irradiance is the most spatially variable and readily exploitable resource at the residential scale in the Philippines, while wind and hydropower contributions vary more strongly by local geography. This score enables intuitive choropleth mapping while reflecting the multi-source nature of renewable energy potential (Candan et al., 2022). It is computed within the renewable potential map builder in the EnergyHub service.

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

