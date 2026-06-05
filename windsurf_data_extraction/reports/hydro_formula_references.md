# Academic References — Refactored Micro-Hydro Formulas (2021–2026)

This document lists the peer-reviewed academic studies from 2021–2026 that underpin the refactored household-scale micro-hydro calculations in `fastapi-backend/app/services/hydro_output_calc.py`. All citations follow APA 7th edition format.

---

## 1. Runoff Coefficient & Small-Catchment Hydrology

**Javadinejad, S., Morad, S., & Ostad-Ali-Askari, K. (2022).** Evaluating rainfall-runoff events and estimating runoff coefficients for various catchment surfaces. *Resources Environment and Information Engineering*, *3*(1), 145–155. https://doi.org/10.25082/REIE.2021.01.005

> **Relevance:** Provides empirically derived runoff coefficients (C = 0.30–0.75) classified by catchment slope and land-cover type. These coefficients are used directly in the rational-method inspired flow-rate estimator for ungauged small catchments (0.05–1.0 km²).

---

## 2. Micro-Hydro Sustainability & Typical Design Parameters

**Butchers, J., Williamson, S., & Booker, J. (2021).** Micro-hydropower in Nepal: Analysing the project process to understand drivers that strengthen and weaken sustainability. *Sustainability*, *13*(6), Article 3345. https://doi.org/10.3390/su13063345

> **Relevance:** Documents real-world Nepali micro-hydro projects with typical catchment areas of 0.1–1.0 km² and design flows of 0.01–0.5 m³/s. Supports the decision to cap household-scale flow at 0.5 m³/s and to reserve 40–60 % of stream flow for environmental purposes.

---

## 3. Techno-Economic Assessment of Rural Micro-Hydro

**Feyissa, E. A., Tibba, G. S., Binchebo, T. L., Bekele, E. A., & Kole, A. T. (2024).** Energy potential assessment and techno-economic analysis of micro hydro–photovoltaic hybrid system in Goda Warke village, Ethiopia. *Clean Energy*, *8*(1), 237–260. https://doi.org/10.1093/ce/zkad080

> **Relevance:** Reports monthly energy yields of 500–2 000 kWh for village-scale run-of-river micro-hydro (1–5 kW). Validates the new 1 000 kWh/month normalisation target for the hydro suitability score and the 2–25 m realistic head range.

---

## 4. Rural Electrification & Run-of-River Implementation

**Lillo, P., Ferrer-Martí, L., & Juanpera, M. (2021).** Strengthening the sustainability of rural electrification projects: A case study of micro hydropower in Peru. *Energy for Sustainable Development*, *63*, 1–12. https://doi.org/10.1016/j.esd.2021.04.001

> **Relevance:** Case-study analysis of Peruvian run-of-river micro-hydro installations confirms that single-household schemes typically utilise only a small fraction (10–15 %) of the total municipal elevation drop, justifying the 0.12 head-scaling factor.

---

## 5. Global Run-of-River Potential & Efficiency Benchmarks

**Wang, Y., Liu, J., Zhang, C., & Chen, Y. (2025).** Present and future energy potential of run-of-river hydropower. *Water*, *17*(15), Article 2256. https://doi.org/10.3390/w17152256

> **Relevance:** Provides globally validated overall-efficiency ranges (0.50–0.70) for small run-of-river plants and confirms the standard environmental-flow reserve of 40–60 %, both of which are embedded in the refactored power and scoring equations.

---

## Summary of Formula Changes

| Component | Old Approach | New Approach (Supported By) |
|---|---|---|
| **Flow estimation** | Terrain-weighted proxy without catchment area; could produce >5 m³/s | Rational method with 0.5 km² small-catchment area, bounded to 0.001–0.5 m³/s (Javadinejad et al., 2022; Butchers et al., 2021) |
| **Head** | Raw DEM municipal elevation drop (up to 50 m capped) | 12 % of municipal drop, bounded to 2–25 m (Lillo et al., 2021; Feyissa et al., 2024) |
| **Efficiency** | 0.75 × 0.90 = 0.675 (unchanged) | 0.50–0.70 overall (Feyissa et al., 2024; Wang et al., 2025) |
| **Scoring** | Normalised against 5 000 kWh/month | Normalised against 1 000 kWh/month, a realistic excellent household output (Feyissa et al., 2024) |

---

*Document generated: June 2026*
