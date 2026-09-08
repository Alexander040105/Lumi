# Municipal-Level Energy Demand Granularity Study

## 1. Problem Statement
The Department of Energy (DOE) publishes electricity statistics at the **regional** and **provincial** levels (e.g., Annex 8 of the Philippine Power Statistics), but **municipal-level consumption data is not publicly available** for the majority of Philippine municipalities. This limits the ability of tools like LUMI EcoSim to provide fine-grained demand assessments at the local government unit (LGU) level.

## 2. Methodology: Population-Weighted Disaggregation
Given the absence of direct municipal consumption data, we propose a **population-weighted disaggregation** method:

### Formula
```
D_municipality = D_province × (P_municipality / P_province)
```

Where:
- **D_municipality** = Estimated annual electricity demand of a municipality (MWh)
- **D_province** = Total provincial electricity demand from DOE Annex 8 (MWh)
- **P_municipality** = Municipality population from PSA 2020 Census
- **P_province** = Total province population (sum of all municipalities)

### Assumptions & Limitations
1. **Uniform per-capita consumption:** The method assumes every person in a province consumes the same amount of electricity. In reality, urban centers (e.g., Cebu City, Davao City) have much higher per-capita demand than rural municipalities.
2. **Industrial load concentration:** Provinces with heavy industrial zones (e.g., Batangas with LNG terminals, Laguna with industrial parks) will have concentrated demand that population ratios cannot capture.
3. **Temporal stability:** PSA 2020 census data may not reflect 2025–2030 population shifts (urban migration, new cities).
4. **Data latency:** DOE Annex 8 is released annually with a ~1 year lag. Real-time municipal estimates are impossible without smart-meter deployments.

## 3. Data Sources
| Layer | Source | Granularity | Access |
|-------|--------|-------------|--------|
| Provincial demand | DOE Annex 8 / Philippine Power Statistics | Provincial | Free (PDF/CSV extraction) |
| Municipal population | PSA 2020 Census of Population and Housing | Municipal | Free (openstat.psa.gov.ph) |
| Municipal boundaries | PSA / OSM | Municipal polygon | Free |
| Economic indicators | PSA / NEDA | Provincial / regional | Free |

## 4. Implementation in LUMI
The backend `estimate_municipal_demand()` service implements this methodology:
1. Fetches province total consumption from `provincial_consumption_2003_2025.csv` (DOE v2).
2. Queries the `municipal_population` table for all municipalities within the province.
3. Computes population ratio for each municipality.
4. Allocates provincial demand proportionally.
5. Returns estimated demand per municipality with a confidence note.

### API Endpoint
```
GET /energyhub/municipal-demand/{province_id}
```

### Database Schema
```sql
create table public.municipal_population (
  id bigint generated always as identity primary key,
  province_id integer not null references public.provinces(province_id),
  municipality_id integer not null references public.municipalities(municipality_id),
  population integer not null,
  year integer not null default 2020,
  source text default 'PSA 2020 Census'
);
```

## 5. Suggested Improvements (Beyond Population Weighting)
To improve accuracy, future work could incorporate:

1. **Economic activity weighting:** Use PSA-provided municipal income class (1st–6th class) or number of registered businesses as a secondary weight.
2. **Nighttime lights (NTL):** NASA VIIRS/DNB nighttime lights satellite imagery correlates strongly with electricity consumption. NTL intensity per municipality could replace pure population weighting.
3. **Distribution utility (DU) data:** Some DUs (e.g., Meralco, Visayan Electric) may have municipal-level sales data. Negotiate data-sharing MOUs.
4. **Building footprint proxy:** OSM building footprints + building type (residential vs. commercial) could refine estimates.
5. **ML downscaling:** Train a small random-forest or gradient-boosting model on provinces where both consumption and population/economic features are known, then predict for municipalities using the same features.

## 6. Conclusion
Population-weighted disaggregation is a **pragmatic and scientifically defensible first step** for municipal demand estimation in the absence of direct measurements. It provides LUMI users with actionable, locality-specific insights while transparently communicating the limitations. Future iterations should incorporate economic and satellite proxies to reduce the uniform-consumption assumption bias.

---

*Document prepared for LUMI Thesis Revisions — Phase 7*
*June 2026*
