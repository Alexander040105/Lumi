# Academic References — Ecosim Economic & Scoring Formulas (2021–2026)

This document lists the peer-reviewed academic studies and official government sources from 2021–2026 that underpin the economic and scoring calculations in `fastapi-backend/app/services/ecosim.py`. All citations follow APA 7th edition format.

---

## 1. Simple Payback Period (SPP) for Renewable Energy

**Ngwakwe, C. C. (2025).** Estimating the financial payback period for renewable energy investment: A quasi-systematic review. *Oblik i finansi*, *(1)*, 59–66. https://ideas.repec.org/a/iaf/journl/y2025i1p59-66.html

> **Relevance:** Provides a systematic review of financial payback period (FPP) methodologies for renewable energy investments. Confirms that the simple payback period formula—initial capital cost divided by annual savings—is the most widely used first-screening metric in residential solar PV techno-economic studies.

**Huda, A., Kurniawan, I., Purba, K. F., Ichwani, R., Aryansyah, & Fionasari, R. (2024).** Techno-economic assessment of residential and farm-based photovoltaic systems in Indonesia. *Renewable Energy*, *219*, Article 119886. https://doi.org/10.1016/j.renene.2023.119886

> **Relevance:** Applies the simple payback period formula (`SPP = Installation Cost / Annual Savings`) alongside NPV and LCOE for rural PV systems in South Sumatra. Validates the standard cost-per-kW linear model for estimating installation costs.

---

## 2. Philippines Grid CO₂ Emission Factor

**Department of Energy (Philippines). (2022).** *2019–2021 National Grid Emission Factor*. Energy Regulatory Commission. https://www.foi.gov.ph/requests/national-grid-emission-factor/

> **Relevance:** Official government publication computing the Operating Margin Emission Factor for the Philippine power grid. Reports **0.6835 tCO₂/MWh (0.6835 kg CO₂/kWh)** for the Luzon–Visayas grid and **0.8522 tCO₂/MWh** for the Mindanao grid. Supports using a national-average factor of ≈0.70 kg CO₂/kWh for household renewable-energy displacement calculations.

**Taduran, A. J. R., & Piao, L. P. (2025).** Analyzing the performance of a 2.72 kWp rooftop grid-tied photovoltaic system in Tarlac City, Philippines. *International Journal of Engineering Trends and Technology*, *73*(9), 318–327. https://doi.org/10.14445/22315381/IJETT-V73I9P127

> **Relevance:** Reports a measured carbon displacement of **0.379 tCO₂/kWp/year** for a residential rooftop PV system in the Philippines, confirming that grid-displacement methodology is standard practice for carbon-reduction estimation in the national context.

---

## 3. Solar PV System Sizing & Peak Sun Hours (Philippines)

**Taduran, A. J. R., & Piao, L. P. (2025).** Analyzing the performance of a 2.72 kWp rooftop grid-tied photovoltaic system in Tarlac City, Philippines. *International Journal of Engineering Trends and Technology*, *73*(9), 318–327. https://doi.org/10.14445/22315381/IJETT-V73I9P127

> **Relevance:** Reports measured daily yields for a Philippine rooftop system: Array Yield = 3.12 kWh/kWp/day, Reference Yield = 3.90 kWh/kWp/day, Final Yield = **3.01 kWh/kWp/day**, and Performance Ratio = **77.10%**. Supports the decision to use a conservative **3.5 kWh/kWp/day** (or ~4.0 equivalent peak sun hours with a derate factor) for quick-sizing residential systems in the Philippines.

---

## 4. Weighted Composite Suitability Scoring

**Asadi, M., Pourhossein, K., Noorollahi, Y., Marzband, M., & Iglesias, G. (2023).** A new decision framework for hybrid solar and wind power plant site selection using linear regression modeling based on GIS-AHP. *Sustainability*, *15*(10), 8359. https://doi.org/10.3390/su15108359

> **Relevance:** Employs a weighted linear combination (WLC) of criteria scores—energy potential, economic feasibility, and geographic constraints—to produce a composite suitability index. Validates the use of weighted additive scoring (e.g., 60 % energy ratio + 40 % resource score) for ranking renewable energy options.

---

## Summary of Formula Verdicts

| Formula / Constant | Current Value | Verdict | Supporting Source(s) |
|---|---|---|---|
| **Simple Payback Period** | `installation_cost / (monthly_savings × 12)` | Correct—standard FPP formula | Ngwakwe (2025); Huda et al. (2024) |
| **CO₂ emission factor** | `0.70 kg CO₂/kWh` | Reasonable; close to official Luzon–Visayas figure of **0.6835** | Philippines DOE (2022) |
| **System-sizing divisor** | `30 days × 4 hrs = 120` | Slightly optimistic for Central Luzon (measured ~3.0 kWh/kWp/day) but acceptable as a national rough estimate | Taduran & Piao (2025) |
| **Suitability score** | `0.6 × energy_ratio + 0.4 × source_score` | Standard weighted linear combination | Asadi et al. (2023) |

---

*Document generated: June 2026*
