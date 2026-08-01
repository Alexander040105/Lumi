# Free Alternative Data Sources for LUMI EnergyHub

## Overview
This document catalogs **free, publicly accessible data sources** that can replace or augment premium/paid datasets currently used in LUMI. Each entry includes the provider, URL, update frequency, granularity, and integration notes.

---

## 1. Department of Energy (DOE) — Philippines
**What:** National electricity statistics, power plant lists, generation mix, demand forecasts.
**URL:** https://www.doe.gov.ph/
**Free?:** Yes — all reports and statistical tables are public.
**Granularity:** National, regional, provincial (Annex tables in annual reports).
**Used in LUMI?** Yes — currently the primary data source.
**Gaps:** Municipal-level consumption is not published; only regional/provincial totals exist.

---

## 2. Philippine Statistics Authority (PSA)
**What:** Population census, household energy access surveys, economic indicators.
**URL:** https://openstat.psa.gov.ph/
**Free?:** Yes — open data portal.
**Granularity:** Barangay-level population; province-level economic data.
**Used in LUMI?** Partial — population data is needed for municipal demand estimation but not yet loaded.
**Integration note:** Load PSA 2020 Census `municipal_population` table into Supabase for Phase 3 disaggregation.

---

## 3. NASA POWER / LAADS DAAC
**What:** Solar irradiance, wind speed, temperature, humidity, cloud cover.
**URL:** https://power.larc.nasa.gov/
**Free?:** Yes — global satellite-derived climate data.
**Granularity:** 0.5° × 0.5° grid (≈ 50 km); daily and monthly averages.
**Used in LUMI?** Yes — used for EcoSim solar, wind, and hydro suitability scoring.
**Gaps:** Not ground-measured; local microclimates may differ.

---

## 4. Global Wind Atlas (DTU / World Bank)
**What:** Wind speed and power density maps.
**URL:** https://globalwindatlas.info/
**Free?:** Yes — interactive web tool and downloadable GIS layers.
**Granularity:** 250 m resolution for some regions; country-level wind resource maps.
**Used in LUMI?** No — could replace NASA POWER wind estimates with higher-resolution data.

---

## 5. Solargis / SolarGIS
**What:** High-resolution solar resource maps and PV yield estimates.
**URL:** https://solargis.com/
**Free?:** Limited free maps; full dataset is paid.
**Granularity:** 250 m – 1 km.
**Used in LUMI?** No — could augment NASA POWER solar data if budget allows.
**Alternative free option:** PVWatts (NREL) — https://pvwatts.nrel.gov/

---

## 6. OpenStreetMap (OSM)
**What:** Infrastructure, building footprints, roads, waterways.
**URL:** https://www.openstreetmap.org/
**Free?:** Yes — open data licensed under ODbL.
**Granularity:** Building-level for many Philippine municipalities.
**Used in LUMI?** No — could be used to estimate rooftop solar potential at the municipal level.

---

## 7. Philippine Power Statistics (DOE Annual Reports)
**What:** Comprehensive electricity statistics including generation, consumption, sales by region.
**URL:** https://www.doe.gov.ph/energy-statistics/philippine-power-statistics
**Free?:** Yes — PDF and Excel downloads.
**Granularity:** Regional and provincial.
**Used in LUMI?** Yes — Annex 8 data is extracted from these reports.

---

## 8. MERALCO / Distribution Utility Tariff Schedules
**What:** Retail electricity tariffs by customer class and region.
**URL:** https://www.meralco.com.ph/ (and other DUs)
**Free?:** Yes — published regulatory filings.
**Granularity:** Customer class (residential, commercial, industrial) per franchise area.
**Used in LUMI?** Partial — EcoSim uses a single national average rate (PHP 14.35/kWh).
**Improvement:** Integrate DU-specific rates for more accurate savings calculations.

---

## 9. Climate Change Commission (CCC) — Philippines
**What:** Climate risk assessments, GHG inventories, NDC tracking.
**URL:** https://climate.gov.ph/
**Free?:** Yes — public reports.
**Granularity:** National and sectoral.
**Used in LUMI?** No — could add carbon-reduction context to EcoSim recommendations.

---

## 10. International Renewable Energy Agency (IRENA)
**What:** Global renewable energy statistics, cost trends, policy databases.
**URL:** https://www.irena.org/Data/View-data-by-topic/Capacity-and-Generation
**Free?:** Yes — annual reports and data downloads.
**Granularity:** Country-level.
**Used in LUMI?** No — useful for benchmarking Philippines against ASEAN peers.

---

## Data Gaps & Next Steps

| Gap | Current Source | Free Alternative | Action Required |
|-----|---------------|----------------|-----------------|
| Municipal electricity demand | None (estimated) | PSA population + DOE regional totals | Load PSA population; implement disaggregation |
| High-res wind data | NASA POWER | Global Wind Atlas | Download PH wind layers; replace NASA estimates |
| High-res solar data | NASA POWER | Solargis free maps / PVWatts | Evaluate Solargis free tier vs. PVWatts API |
| Real-time grid data | None | DOE Grid Status (if published) | Scrape or request API access |
| Building rooftop area | None | OSM building footprints | Extract OSM data for major cities |
| DU-specific tariffs | Single average | MERALCO / ERC filings | Scrape or manual entry per region |

---

*Last updated: June 2026*
