# Wikipedia Wind/Hydro Plant Recalibration Report (v5)

**Date:** 2026-09-03

**Source:** Wikipedia: List of power plants in the Philippines

**Warning:** Wikipedia explicitly states this list is incomplete; it is used as supplementary evidence, not a definitive national registry.

## v5 Change: Hydro Output Floor for Proven Plant Provinces

Approach C (generation scaling) is extended with a capacity-linked **output floor** for provinces that host operating hydropower plants. The floor is derived from the square root of total installed capacity (MW) and is capped so it does not become a 1:1 utility-to-household conversion.

### Plant Data Summary

**Wind plants**
- **total:** 10
- **operating:** 6
- **missing_coordinates:** 5
- **provinces_covered:** 5
- **operating_capacity_mw:** 408.0
- **provinces:** Aklan, Guimaras, Ilocos Norte, Oriental Mindoro, Rizal

**Hydro plants**
- **total:** 17
- **operating:** 17
- **missing_coordinates:** 11
- **provinces_covered:** 13
- **operating_capacity_mw:** 1235.92
- **provinces:** Agusan del Norte, Benguet, Bukidnon, Bulacan, Catanduanes, Davao City, Ilocos Norte, Isabela, La Union, Lanao del Sur, Mountain Province, Nueva Ecija, Oriental Mindoro

## Settings

- **wind_hydro_plant_boost_mode:** generation
- **hydro_plants_generation_scale_factor:** 0.6
- **hydro_plants_max_generation_scale:** 2.5
- **hydro_plant_floor_enabled:** True
- **hydro_plant_floor_factor:** 15.0 (kWh per sqrt(MW))
- **hydro_plant_max_floor_kwh:** 150.0
- **hydro_plant_absolute_cap_kwh:** 250.0
- **hydro_plant_floor_provinces:** Agusan del Norte, Benguet, Bukidnon, Bulacan, Catanduanes, Ilocos Norte, Isabela, La Union, Lanao del Sur, Mountain Province, Nueva Ecija, Oriental Mindoro
- **scoring_version:** v5

## All 120 Provinces — v5 Results

Counts: {'Solar': 41, 'Hydropower': 8, 'Wind': 35, 'error': 36}

- Solar: {'min': 124.92, 'max': 154.55, 'mean': 137.99, 'median': 137.04}
- Wind: {'min': 0.0, 'max': 260.28, 'mean': 133.53, 'median': 133.1}
- Hydro: {'min': 0.01, 'max': 250.0, 'mean': 31.44, 'median': 6.08}

## Hydropower-Recommending Provinces (v5)

| Province | Hydro kWh | Floor | Generation Scale |
|---|---|---|---|
| AGUSAN DEL NORTE | 227.3731 | 86.04 | 1.171 |
| BENGUET | 237.4587 | 150.0 | 1.431 |
| BULACAN | 150.0 | 150.0 | 1.694 |
| IFUGAO | 244.177 | 0.0 | 1.916 |
| ISABELA | 150.0 | 150.0 | 1.916 |
| KALINGA | 186.821 | 0.0 | 1.0 |
| LANAO DEL SUR | 134.16 | 134.16 | 1.353 |
| MOUNTAIN PROVINCE | 250.0 | 150.0 | 1.916 |

## 9 Target Provinces

| Province | Solar | Wind | Hydro | Recommendation |
|---|---|---|---|---|
| BULACAN | 135.4358 | 134.9691 | 150.0 | Hydropower |
| CAMARINES SUR | 135.7569 | 190.08 | 25.899 | Wind |
| LEYTE | 131.5114 | 150.9207 | 0.948 | Wind |
| EASTERN SAMAR | 134.6249 | 103.8462 | 2.785 | Solar |
| CAVITE | 142.709 | 190.08 | 4.519 | Wind |
| LAGUNA | 136.779 | 137.5477 | 4.504 | Wind |
| BATANGAS | 144.7388 | 141.5756 | 8.397 | Solar |
| RIZAL | 139.713 | 126.9746 | 11.306 | Solar |
| QUEZON | 137.924 | 118.7175 | 0.599 | Solar |

## Notes

- Davao City is excluded from the floor list because the Wikipedia records map to 'Davao City' rather than a province and lack coordinates.
- The floor flips provinces with large operating hydro plants (e.g., Bulacan/Angat 218 MW, Isabela/Magat 360 MW, Lanao del Sur/Agus 1 80 MW) where the base household catchment model returned low output.
- Provinces with strong wind resources (Ilocos Norte, Catanduanes) or small plants remain wind/solar.
- Hydro remains the minority recommendation (~10% of successful provinces), preserving a mixed national distribution.
