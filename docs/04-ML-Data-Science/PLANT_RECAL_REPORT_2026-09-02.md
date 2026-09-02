# Wikipedia Wind/Hydro Plant Recalibration Report

**Date:** 2026-09-02

**Source:** Wikipedia: List of power plants in the Philippines

**Warning:** Wikipedia explicitly states this list is incomplete; it is used as supplementary evidence, not a definitive national registry.

## Plant Data Summary

### Wind Plants

- **total:** 10
- **operating:** 6
- **under_construction:** 0
- **proposed:** 1
- **missing_coordinates:** 5
- **with_province:** 10
- **provinces_covered:** 5
- **operating_capacity_mw:** 408.0
- **provinces:** Aklan, Guimaras, Ilocos Norte, Oriental Mindoro, Rizal

### Hydro Plants

- **total:** 17
- **operating:** 17
- **under_construction:** 0
- **proposed:** 0
- **missing_coordinates:** 11
- **with_province:** 15
- **provinces_covered:** 13
- **operating_capacity_mw:** 1235.92
- **provinces:** Agusan del Norte, Benguet, Bukidnon, Bulacan, Catanduanes, Davao City, Ilocos Norte, Isabela, La Union, Lanao del Sur, Mountain Province, Nueva Ecija, Oriental Mindoro

## Settings

- **wind_plants_boost_enabled:** True
- **wind_plants_boost_radius_km:** 25.0
- **wind_plants_max_bonus:** 25.0
- **wind_plants_generation_scale_factor:** 0.3
- **wind_plants_max_generation_scale:** 1.5
- **hydro_plants_boost_enabled:** True
- **hydro_plants_boost_radius_km:** 50.0
- **hydro_plants_max_bonus:** 25.0
- **hydro_plants_generation_scale_factor:** 0.4
- **hydro_plants_max_generation_scale:** 2.0
- **wind_hydro_plant_boost_mode:** generation
- **scoring_version:** v4

## Approach B (Suitability Boost) — All 120 Provinces

Counts: {'Solar': 46, 'Hydropower': 3, 'Wind': 35, 'error': 36}

Solar: {'min': 124.92, 'max': 154.55, 'mean': 137.99, 'median': 137.04}

Wind: {'min': 0.0, 'max': 190.08, 'mean': 132.05, 'median': 133.1}

Hydro: {'min': 0.01, 'max': 194.17, 'mean': 18.87, 'median': 4.85}

## Approach C (Generation Scaling) — All 120 Provinces

Counts: {'Solar': 44, 'Hydropower': 5, 'Wind': 35, 'error': 36}

Solar: {'min': 124.92, 'max': 154.55, 'mean': 137.99, 'median': 137.04}

Wind: {'min': 0.0, 'max': 260.28, 'mean': 133.53, 'median': 133.1}

Hydro: {'min': 0.01, 'max': 219.68, 'mean': 21.85, 'median': 5.41}

## Provinces that Changed from B to C

| Province | Approach B | Approach C | Solar kWh | Wind kWh | Hydro kWh | Wind Scale | Hydro Scale | Nearby Wind | Nearby Hydro |
|---|---|---|---|---|---|---|---|---|---|
| IFUGAO | Solar | Hydropower | 139.4252 | 0.0 | 205.18 | 1.0 | 1.61 | 0 | 1 |
| MOUNTAIN PROVINCE | Solar | Hydropower | 141.8622 | 129.226 | 219.6781 | 1.0 | 1.61 | 0 | 1 |

## 9 Target Provinces — Approach C

| Province | Solar | Wind | Hydro | Recommendation | Nearby Wind | Nearby Hydro | Wind Scale | Hydro Scale |
|---|---|---|---|---|---|---|---|---|
| Bulacan | 135.4358 | 134.9691 | 0.7022 | Solar | 0 | 1 | 1.0 | 1.463 |
| Camarines Sur | 135.7569 | 190.08 | 25.899 | Wind | 0 | 0 | 1.0 | 1.0 |
| Leyte | 131.5114 | 150.9207 | 0.948 | Wind | 0 | 0 | 1.0 | 1.0 |
| Eastern Samar | 134.6249 | 103.8462 | 2.785 | Solar | 0 | 0 | 1.0 | 1.0 |
| Cavite | 142.709 | 190.08 | 4.519 | Wind | 0 | 0 | 1.0 | 1.0 |
| Laguna | 136.779 | 137.5477 | 4.504 | Wind | 0 | 0 | 1.0 | 1.0 |
| Batangas | 144.7388 | 141.5756 | 8.397 | Solar | 0 | 0 | 1.0 | 1.0 |
| Rizal | 139.713 | 126.9746 | 11.306 | Solar | 1 | 0 | 1.13 | 1.0 |
| Quezon | 137.924 | 118.7175 | 0.599 | Solar | 0 | 0 | 1.0 | 1.0 |

## Chosen Default

Approach C (generation scaling) because it translates existing plant capacity into bounded household-output multipliers and produced a more geographically balanced national distribution.

## Limitations

- Wikipedia list is incomplete and may omit small run-of-river hydro plants and newer wind farms.
- Some hydro records have missing coordinates or province values; these are excluded from geographic proximity and matched by province where possible.
- Province centroids are coarse; a plant in one corner of a province does not mean every household in that province has the same resource.
- Generation scaling is bounded and log-scaled to prevent utility-scale capacity from directly becoming household output.
