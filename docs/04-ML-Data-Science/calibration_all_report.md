# Comprehensive Calibration Report — All Provinces & Municipalities

**Provinces tested:** 78
**Municipalities tested:** 1287

**Raw data:** [`calibration_all_results.csv`](calibration_all_results.csv)

---

## PROVINCE LEVEL

### Score Distribution

| Source | Score Stats |
|--------|-------------|
| Solar Score | min=70.4  median=77.0  max=87.0  mean=77.7  std=3.6 |
| Solar Output (kWh) | min=129.1  median=141.2  max=159.7  mean=142.5  std=6.6 |
| Wind Score | min=5.1  median=36.0  max=100.0  mean=46.5  std=30.2 |
| Wind Output (kWh) | min=15.4  median=108.1  max=624.5  mean=148.5  std=113.6 |
| Hydro Score | min=0.0  median=1.0  max=41.7  mean=3.9  std=8.3 |
| Hydro Output (kWh) | min=0.0  median=1.0  max=41.7  mean=3.9  std=8.3 |

### Recommendation Distribution (generation-based)

| Source | Count | Percentage |
|--------|-------|------------|
| Solar | 46 | 59.0% |
| Wind | 32 | 41.0% |
| Hydropower | 0 | 0.0% |
| None | 0 | 0.0% |

### Suitability Recommendation Distribution (hidden field)

| Source | Count | Percentage |
|--------|-------|------------|
| Solar | 58 | 74.4% |
| Wind | 20 | 25.6% |
| Hydropower | 0 | 0.0% |
| None | 0 | 0.0% |

**Agreement (gen vs suitability):** 66/78 (84.6%)

### Hydro Enrichment

- Using enrichment: 78/78 (100.0%)
- Stream feasibility: {'moderate': 15, 'none': 25, 'low': 18, 'high': 20}
- Hydro > 0: 78/78 (100.0%)
- Hydro > 5 kWh: 14/78 (17.9%)
- Hydro > 10 kWh: 5/78 (6.4%)

### Score-Output Correlation

- solar: r=1.000
- wind: r=0.941
- hydro: r=1.000

### Bias Check

**OK:** No source dominates (>80% threshold). Max = 59.0%

### Top 10 Hydro Output

| Name | Hydro kWh | Hydro Score | Catchment | Feasibility |
|------|-----------|-------------|-----------|-------------|
| AGUSAN DEL NORTE | 41.7 | 41.7 | Asiga | moderate |
| KALINGA | 40.3 | 40.3 | Cagayan | high |
| BENGUET | 30.1 | 30.1 | Amburayan | high |
| MOUNTAIN PROVINCE | 29.5 | 29.5 | Cagayan | high |
| IFUGAO | 27.5 | 27.5 | Cagayan | high |
| ABRA | 9.8 | 9.8 | Abra | high |
| OCCIDENTAL MINDORO | 9.4 | 9.4 | Mamburao | none |
| APAYAO | 8.0 | 8.0 | Abulug | high |
| ALBAY | 5.9 | 5.9 | Bicol | low |
| QUIRINO | 5.6 | 5.6 | Cagayan | high |

### Bottom 10 Hydro Output

| Name | Hydro kWh | Hydro Score | Catchment | Feasibility |
|------|-----------|-------------|-----------|-------------|
| BULACAN | 0.1 | 0.1 | Angat | low |
| NORTHERN SAMAR | 0.1 | 0.1 | Mano | moderate |
| PALAWAN | 0.1 | 0.1 | Rizal | none |
| PAMPANGA | 0.1 | 0.1 | Pampanga | moderate |
| SORSOGON | 0.0 | 0.0 | Ogod | none |
| CEBU | 0.0 | 0.0 | Tanjay | none |
| ROMBLON | 0.0 | 0.0 | Bongabong | none |
| BILIRAN | 0.0 | 0.0 | Pagsangahan | none |
| MASBATE | 0.0 | 0.0 | Ogod | none |
| GUIMARAS | 0.0 | 0.0 | Tigum | none |
---

## MUNICIPALITY LEVEL

### Score Distribution

| Source | Score Stats |
|--------|-------------|
| Solar Score | min=60.6  median=78.5  max=94.1  mean=78.9  std=5.4 |
| Solar Output (kWh) | min=111.2  median=143.9  max=172.6  mean=144.6  std=9.9 |
| Wind Score | min=0.1  median=38.4  max=100.0  mean=46.7  std=33.6 |
| Wind Output (kWh) | min=0.4  median=115.1  max=3387.8  mean=191.1  std=258.6 |
| Hydro Score | min=0.0  median=0.3  max=91.9  mean=3.5  std=10.0 |
| Hydro Output (kWh) | min=0.0  median=0.3  max=91.9  mean=3.5  std=10.0 |

### Recommendation Distribution (generation-based)

| Source | Count | Percentage |
|--------|-------|------------|
| Solar | 748 | 58.1% |
| Wind | 539 | 41.9% |
| Hydropower | 0 | 0.0% |
| None | 0 | 0.0% |

### Suitability Recommendation Distribution (hidden field)

| Source | Count | Percentage |
|--------|-------|------------|
| Solar | 931 | 72.3% |
| Wind | 355 | 27.6% |
| Hydropower | 1 | 0.1% |
| None | 0 | 0.0% |

**Agreement (gen vs suitability):** 1102/1287 (85.6%)

### Hydro Enrichment

- Using enrichment: 1287/1287 (100.0%)
- Stream feasibility: {'moderate': 125, 'none': 357, 'high': 634, 'low': 171}
- Hydro > 0: 1287/1287 (100.0%)
- Hydro > 5 kWh: 170/1287 (13.2%)
- Hydro > 10 kWh: 112/1287 (8.7%)

### Score-Output Correlation

- solar: r=0.992
- wind: r=0.703
- hydro: r=1.000

### Bias Check

**OK:** No source dominates (>80% threshold). Max = 58.1%

### Top 10 Hydro Output

| Name | Hydro kWh | Hydro Score | Catchment | Feasibility |
|------|-----------|-------------|-----------|-------------|
| TINOC | 91.9 | 91.9 | Cagayan | high |
| PASIL | 83.8 | 83.8 | Cagayan | high |
| TADIAN | 70.8 | 70.8 | Abra | high |
| LUBUAGAN | 69.0 | 69.0 | Cagayan | high |
| BANAUE | 68.8 | 68.8 | Cagayan | high |
| LAGAYAN | 63.6 | 63.6 | Abra | high |
| BARLIG | 63.6 | 63.5 | Cagayan | high |
| ITOGON | 62.6 | 62.6 | Agno | high |
| AMBAGUIO | 61.9 | 61.9 | Cagayan | high |
| HUNGDUAN | 61.1 | 61.1 | Cagayan | high |

### Bottom 10 Hydro Output

| Name | Hydro kWh | Hydro Score | Catchment | Feasibility |
|------|-----------|-------------|-----------|-------------|
| MINGLANILLA | 0.0 | 0.0 | Inabanga | none |
| ISLAND GARDEN CITY OF SAMAL | 0.0 | 0.0 | Davao | none |
| POLA | 0.0 | 0.0 | Lumangbayan | low |
| BUSUANGA | 0.0 | 0.0 | Mongpong | none |
| TIGBAUAN | 0.0 | 0.0 | Tigum | none |
| BIEN UNIDO | 0.0 | 0.0 | Inabanga | none |
| MAYORGA | 0.0 | 0.0 | Daguitan_Marabang | low |
| GOVERNOR GENEROSO | 0.0 | 0.0 | Sumlog | none |
| BULUAN | 0.0 | 0.0 | Rio_Grande_de_Mindanao | high |
| PANDAG | 0.0 | 0.0 | Rio_Grande_de_Mindanao | high |
