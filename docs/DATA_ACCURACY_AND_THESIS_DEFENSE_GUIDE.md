# Improving Municipal Accuracy and Defending LUMI Calculations in a Thesis Defense

> Generated from the LUMI repository analysis, August 2026.
> This guide explains why the current Philippine municipality-level results may look inaccurate, which datasets will fix them, and how to justify the current implementation to a thesis panel.

---

## 1. Why the current results can look inaccurate

1. **Municipal `lat/lon` may not be the true geometric centroid.**
   The `municipalities` table stores bare `lat`/`lon` columns, but the authoritative centroid should come from `geospatial_metadata`, produced by `scripts/extract_centroids.py` and `scripts/insert_geospatial_metadata.py`. If those tables are not populated, the fallback to `municipalities.lat`/`lon` can place a municipality in the wrong climate cell.

2. **NASA POWER is ~0.5° (~50 km) gridded satellite data.**
   Many nearby municipalities receive identical climate values because they fall inside the same grid cell. You can see this in `fastapi-backend/app/services/local_data/municipality_climate_averages.csv`: adjacent municipalities often have identical irradiance, wind, and rainfall, which is physically unrealistic at the LGU scale.

3. **Solar uses only GHI and a fixed 2 × 400 W residential configuration.**
   EcoSim currently uses the legacy `solar_calc` path, which does not use DNI/DHI, tilted-plane transposition, rooftop area, or local shading. An advanced `solar_calc_advanced` function exists but is not called by EcoSim.

4. **Wind uses NASA POWER 10 m wind speed, not hub-height wind, plus a generic 30 % capacity factor.**
   The Philippines has very local wind regimes (coastal, ridge-crest, passes) that a 50 km grid cannot resolve.

5. **Hydro uses a fixed 0.5 km² catchment and the rational method.**
   It has no measured stream gauges, no DEM flow-accumulation network, and no land-cover layer.

6. **Geothermal interpolates sparse IHFC heat-flow points over a 300 km radius,** assumes a 2,000 m reservoir, and estimates flow rate from aquifer score. It has no MT/resistivity, gravity, hot-spring chemistry, or well-log data.

7. **Municipal demand is not measured; it is disaggregated from provincial DOE totals using PSA population.**
   This assumes uniform per-capita consumption, which is not true for urban vs. rural or industrial provinces.

---

## 2. Datasets to improve accuracy

### A. Fix the geography first

| Dataset | What it fixes | How to use it | Free? |
|---|---|---|---|
| **PSA 2020 Census `municipal_population` + PSGC boundary GeoJSON** | Municipal `lat`/`lon`, `area_km2`, and population | Re-run `scripts/extract_centroids.py` -> `scripts/insert_geospatial_metadata.py`; load `supabase/table_scripts/municipal_population.sql` | Yes |
| **SRTM 1-arcsec (30 m) or NAMRIA DEM** | Elevation, slope, head, flow accumulation | Derive `mean_slope_deg`, `hydraulic_head_m`, `watershed_gradient` from real DEM instead of NASA POWER elevation | Yes |
| **HydroSHEDS river network / catchments** | Real catchment area and river reach | Replace the fixed 0.5 km² catchment with the actual upstream catchment for each municipality | Yes |
| **OpenStreetMap building footprints** | Rooftop area for solar; building density for demand | Filter residential/commercial buildings; compute rooftop area per municipality | Yes |

### B. Solar

| Dataset | Improvement over NASA POWER |
|---|---|
| **Global Solar Atlas (World Bank)** | 250 m GHI/DNI/DHI, temperature, and PV-out maps; enables the `solar_calc_advanced` transposition model in `fastapi-backend/app/services/solar_output_calc.py` |
| **NREL PVWatts API** | Hourly simulated yield using real meteorological data and user-defined system configuration |
| **Solargis (free maps / paid API)** | 250 m - 1 km solar resource data, more accurate for tropical conditions |
| **PAGASA ground station data** | Local cloud/irradiance measurements for validation and bias correction |

### C. Wind

| Dataset | Improvement |
|---|---|
| **Global Wind Atlas (DTU/World Bank)** | 250 m wind speed and power density; gives hub-height data and avoids the 10 m extrapolation problem |
| **ERA5 reanalysis (Copernicus)** | Hourly 31 km wind data; can be downscaled with the DEM |
| **PAGASA anemometer / WAsP / microscale model** | Site-specific hub-height wind; best for coastal/ridge sites |
| **Actual Philippine wind-farm SCADA** | Validation/calibration of capacity factors |

### D. Hydropower

| Dataset | Improvement |
|---|---|
| **SRTM/NAMRIA DEM + flow accumulation** | Compute real contributing catchment area and stream order, not the fixed 0.5 km² |
| **PAGASA rain gauges / CHIRPS** | Ground- or satellite-corrected rainfall at higher spatial and temporal resolution |
| **DENR / NIA stream-gauge records** | Replace rational-method design flow with real measured flow-duration curves |
| **ESA WorldCover / NAMRIA land use** | Improve runoff coefficient beyond slope-only |

### E. Geothermal

| Dataset | Improvement |
|---|---|
| **PHIVOLCS fault/volcano data (already used)** | Keep; this is the best available in the Philippines |
| **IHFC 2024 GHFDB (already used)** | Keep, but bias-correct with local heat-flow campaign data if available |
| **DOE Geothermal Prospectivity Maps / PHIVOLCS heat-flow campaigns** | Official prospectivity ranking; use as validation or as an additional MCDA criterion |
| **Magnetotellurics (MT), gravity, Curie-depth maps** | Resolve reservoir geometry, not just surface heat flow |
| **Hot spring / fumarole geochemistry** | Surface temperature proxy for active systems |
| **EDC / FGHC well logs** | Measured reservoir temperature and flow rate where available; validate `compute_geothermal_output` assumptions |

### F. Municipal demand and economics

| Dataset | Use |
|---|---|
| **PSA 2020 population + income class** | Population-weighted disaggregation; income class as an economic weight |
| **NASA VIIRS DNB nighttime lights** | Proxy for actual electricity consumption per municipality; replace pure population weighting |
| **MERALCO / VECO / DU sales data** | Ground-truth municipal demand if a data-sharing MOU can be secured |
| **PSA/DTI business registry** | Industrial/commercial load concentration |
| **DU-specific tariff schedules** | Replace the single national rate with regional tariffs for more accurate savings calculations |

---

## 3. Suggested implementation order

1. **Recompute municipal centroids** from the PSA/PSGC GeoJSON and upsert to `geospatial_metadata` using the existing scripts.
2. **Regenerate `municipality_climate_averages.csv`** from the new centroids, or replace it with Global Solar Atlas / Global Wind Atlas extracts.
3. **Rebuild suitability scores** once climate and terrain inputs are updated.
4. **Add DEM-derived terrain metrics** (`hydraulic_head_m`, `mean_slope_deg`, `runoff_potential`, `watershed_gradient`) to `hydropower_suitability` and/or `municipality_terrain_metrics`.
5. **Add VIIRS nighttime lights and PSA population** to `municipal_population` and municipal demand for realistic consumption estimates.
6. **Validate outputs** against measured plant data and publish the validation table for the defense.

---

## 4. How to justify the current calculations in a thesis defense

### 4.1 Use the "first-order screening tool" framing

LUMI is a **pre-feasibility decision support system**, not a detailed engineering design tool. It therefore uses conservative, computationally cheap first-order models: performance ratio for solar, the kinetic-power equation with Betz limit for wind, the rational method for ungauged catchments, and IDW heat flow for geothermal. These are the same first-screening methods used in the cited literature.

### 4.2 Every formula is literature- or government-backed

- Solar temperature coefficient `-0.004 / °C` and performance ratio: Kim et al. (2021), Zdyb & Sobczynski (2024), IEC 61724.
- Wind: Betz limit 0.593 and `P = 0.5 * rho * A * V^3 * Cp * eta`: Fahim et al. (2024), Molteno (2022).
- Hydro: runoff coefficients from Javadinejad et al. (2022); 40 % environmental reserve from Butchers et al. (2021) and Wang et al. (2025); standard `P = eta * rho * g * Q * H` from Di Dio et al. (2022).
- Geothermal: IHFC heat flow, standard conduction gradient, and AHP-MCDA site selection.
- Economics: simple payback from Ngwakwe (2025); CO2 factor 0.6835 kg/kWh from DOE Philippines (2022).

### 4.3 Uncertainty is made explicit

The system returns `confidence_score`, `source`, and `assumption` strings for every renewable output. This is not a bug; it is a feature of scientific transparency. A low confidence score means the data is sparse; the model does not pretend otherwise.

### 4.4 Validation against reality

- Solar: compare a few municipalities to the measured 2.72 kWp Tarlac system from Taduran & Piao (2025) and show the numbers are in the same order of magnitude.
- Geothermal: compare predicted high-suitability municipalities to the DOE/PHIVOLCS list of operating and prospective geothermal areas (Tiwi, Tongonan, Palinpinon, Bacman, Mt. Apo).
- Wind: compare predicted high-wind municipalities to DOE-approved wind-farm locations (Bangui, Pililla, Guimaras).
- Hydro: sanity-check against known micro-hydro communities in the Cordillera and Mindanao.

### 4.5 Sensitivity analysis

Pick one municipality and vary the most uncertain inputs (`+/- 20 %` rainfall for hydro, `+/- 0.5 m/s` wind speed, `+/- 5 %` heat flow for geothermal). Show how the output changes. This demonstrates that you understand the uncertainty rather than hiding it.

### 4.6 Turn limitations into "future work"

The limitations you are seeing (NASA POWER coarseness, no DNI/DHI, no stream gauges, no measured geothermal flow) are not flaws of the thesis. They are contributions because the thesis:

- identifies exactly which datasets are missing in the Philippine municipal renewable-energy space;
- provides an open, reproducible pipeline (`extract_centroids.py` -> `municipality_climate_monthly` -> `*_suitability` tables) that can ingest those better datasets as they become available.

### 4.7 One-slide summary for the panel

> "LUMI's EcoSim uses peer-reviewed, conservative, first-order physics and GIS-MCDA models. Where high-resolution municipal data does not yet exist in the Philippines, the system explicitly propagates uncertainty into a confidence score and reports the assumptions. The tool is therefore appropriate for screening and prioritization, not final engineering design. All improvements -- DEM, Global Solar/Wind Atlas, stream gauges, DU tariffs, and nighttime lights -- are documented as forward-compatible data upgrades in the repository."

---

## 5. Key code and data files

- `fastapi-backend/app/services/solar_output_calc.py` -- solar temperature, soiling, and performance ratio.
- `fastapi-backend/app/services/wind_output_calc.py` -- wind power, Betz limit, capacity factor.
- `fastapi-backend/app/services/hydro_output_calc.py` -- runoff coefficient, design flow, micro-hydro power.
- `fastapi-backend/app/services/geothermal/features.py` -- heat flow IDW, gradient, reservoir temperature, MCDA scoring.
- `fastapi-backend/app/services/geothermal/plants.py` -- proximity boost from operating plants.
- `fastapi-backend/app/services/ecosim.py` -- EcoSim orchestration, MCDA scoring, economics.
- `fastapi-backend/app/services/confidence.py` -- confidence and uncertainty scoring.
- `fastapi-backend/app/services/financials.py` -- NPV, IRR, LCOE, payback.
- `fastapi-backend/app/services/local_data/municipality_climate_averages.csv` -- NASA POWER climate averages.
- `scripts/extract_centroids.py` -- compute centroids from GeoJSON.
- `scripts/insert_geospatial_metadata.py` -- upload centroids to Supabase.
- `supabase/table_scripts/schema.sql` -- regions, provinces, municipalities, barangays schema.
- `supabase/table_scripts/supabase_suitability_migration.sql` -- suitability score columns.
- `docs/FREE_ALTERNATIVE_DATA.md` -- existing catalog of free public data sources.
- `docs/municipal_demand_granularity_study.md` -- demand disaggregation methodology and limitations.
- `docs/geospatial_data_pipeline.md` -- full geospatial data pipeline.
- `docs/GEOTHERMAL_FORMULAS.md` -- full geothermal formula reference.
- `docs/PANEL_FORMULA_SUMMARY.md` -- panel-defense explanations for every EcoSim formula.
- `docs/COMPLETE_FORMULA_SUMMARY_WITH_RRL.md` -- all formulas with thesis RRL references.

---

## 6. References

- Asadi, M., Pourhossein, K., Noorollahi, Y., Marzband, M., & Iglesias, G. (2023). A new decision framework for hybrid solar and wind power plant site selection using linear regression modeling based on GIS-AHP. *Sustainability, 15*(10), 8359.
- Baker, et al. (2023). Small wind capacity factor. (Cited in code comments.)
- Beriro, et al. (2022). WSM for ranking renewables.
- Bianchini, et al. (2022). Kinetic energy extraction in wind turbines.
- Butchers, D., Williamson, S., & Booker, J. (2021). Micro-hydropower in Nepal. *Sustainability, 13*(6), 3345.
- Castro, et al. (2023). Rural micro-hydropower output benchmarks for Southeast Asian households.
- Department of Energy (Philippines). (2022). *2019-2021 National Grid Emission Factor*. Energy Regulatory Commission.
- Di Dio, et al. (2022). Standard hydropower equations for run-of-river micro-hydro systems.
- Fahim, A., Al-Mamun, A., & Hassan, M. A. (2024). Toward a physics-based model of power coefficient in horizontal-axis wind turbines. *Wind Engineering, 48*(3), 245-262.
- Feyissa, et al. (2024). Techno-economic assessment of run-of-river micro-hydropower.
- Huda, A., et al. (2024). Techno-economic assessment of residential and farm-based photovoltaic systems in Indonesia. *Renewable Energy, 219*, 119886.
- Javadinejad, S., Morad, S., & Ostad-Ali-Askari, K. (2022). Evaluating rainfall-runoff events and estimating runoff coefficients. *Resources Environment and Information Engineering, 3*(1), 145-155.
- Kim, S., et al. (2021). Temperature-dependent performance analysis of crystalline silicon photovoltaic modules. *Solar Energy*.
- Lillo, P., Ferrer-Marti, L., & Juanpera, M. (2021). Strengthening the sustainability of rural electrification projects. *Energy for Sustainable Development, 63*, 1-12.
- Molteno, C. (2022). The Betz limit and modern wind turbine aerodynamics.
- Ngwakwe, C. C. (2025). Estimating the financial payback period for renewable energy investment: A quasi-systematic review. *Oblik i finansi, (1)*, 59-66.
- Rumbayan, M., & Rumbayan, M. (2024). Small catchment hydrology and household micro-hydro feasibility in the Philippine archipelago.
- Sambito, et al. (2026). Terrain slope effects on overland flow and infiltration.
- Taduran, A. J. R., & Piao, L. P. (2025). Analyzing the performance of a 2.72 kWp rooftop grid-tied photovoltaic system in Tarlac City, Philippines. *International Journal of Engineering Trends and Technology, 73*(9), 318-327.
- Vanegas-Cantarero, et al. (2022). Weighted linear combination approaches in GIS-MCDA for renewable energy site-selection.
- Wang, Y., et al. (2025). Present and future energy potential of run-of-river hydropower. *Water, 17*(15), 2256.
- Zdyb, A., & Sobczynski, A. (2024). Photovoltaic system performance modeling under variable climatic conditions. *Renewable and Sustainable Energy Reviews*.
