/**
 * Province/area → DOE region code mapping for provider lookup.
 * Used to match EcoSim locations with DOE Solar PV Installer Registry entries.
 */

export const PROVINCE_TO_REGION = {
  // Region I — Ilocos
  "ilocos norte": "I", "ilocos sur": "I", "la union": "I", "pangasinan": "I",
  // Region II — Cagayan Valley
  "batanes": "II", "cagayan": "II", "isabela": "II", "nueva vizcaya": "II", "quirino": "II",
  // Region III — Central Luzon
  "aurora": "III", "bataan": "III", "bulacan": "III", "nueva ecija": "III",
  "pampanga": "III", "tarlac": "III", "zambales": "III",
  // Region IV-A — Calabarzon
  "batangas": "IV-A", "cavite": "IV-A", "laguna": "IV-A", "quezon": "IV-A", "rizal": "IV-A",
  // Region IV-B — Mimaropa
  "marinduque": "IV-B", "occidental mindoro": "IV-B", "oriental mindoro": "IV-B",
  "palawan": "IV-B", "romblon": "IV-B",
  // Region V — Bicol
  "albay": "V", "camarines norte": "V", "camarines sur": "V", "catanduanes": "V",
  "masbate": "V", "sorsogon": "V",
  // Region VI — Western Visayas
  "aklan": "VI", "antique": "VI", "capiz": "VI", "guimaras": "VI", "iloilo": "VI",
  "negros occidental": "VI",
  // Region VII — Central Visayas
  "bohol": "VII", "cebu": "VII", "negros oriental": "VII", "siquijor": "VII",
  // Region VIII — Eastern Visayas
  "biliran": "VIII", "eastern samar": "VIII", "leyte": "VIII", "northern samar": "VIII",
  "samar": "VIII", "southern leyte": "VIII",
  // Region IX — Zamboanga Peninsula
  "zamboanga del norte": "IX", "zamboanga del sur": "IX", "zamboanga sibugay": "IX",
  // Region X — Northern Mindanao
  "bukidnon": "X", "camiguin": "X", "lanao del norte": "X", "misamis occidental": "X",
  "misamis oriental": "X",
  // Region XI — Davao
  "davao de oro": "XI", "davao del norte": "XI", "davao del sur": "XI",
  "davao occidental": "XI", "davao oriental": "XI",
  // Region XII — Soccsksargen
  "cotabato": "XII", "sarangani": "XII", "south cotabato": "XII", "sultan kudarat": "XII",
  // Region XIII — Caraga
  "agusan del norte": "XIII", "agusan del sur": "XIII", "dinagat islands": "XIII",
  "surigao del norte": "XIII", "surigao del sur": "XIII",
  // NCR — National Capital Region
  "metro manila": "NCR", "ncr": "NCR", "manila": "NCR", "caloocan": "NCR",
  "las piñas": "NCR", "las pinas": "NCR", "makati": "NCR", "malabon": "NCR",
  "mandaluyong": "NCR", "marikina": "NCR", "muntinlupa": "NCR", "navotas": "NCR",
  "parañaque": "NCR", "paranaque": "NCR", "pasay": "NCR", "pasig": "NCR",
  "pateros": "NCR", "quezon city": "NCR", "san juan": "NCR", "taguig": "NCR",
  "valenzuela": "NCR",
  // CAR — Cordillera (no providers in registry, map to Region I as nearest)
  "abra": "I", "apayao": "I", "benguet": "I", "ifugao": "I", "kalinga": "I",
  "mountain province": "I",
  // BARMM — Bangsamoro (no providers in registry, map to XII as nearest)
  "basilan": "XII", "lanao del sur": "XII", "maguindanao": "XII", "sulu": "XII",
  "tawi-tawi": "XII",
};

export function getRegionFromProvince(provinceName) {
  if (!provinceName) return null;
  const normalized = provinceName.toLowerCase().trim();
  return PROVINCE_TO_REGION[normalized] || null;
}

export function getRegionFromMunicipality(muniName) {
  if (!muniName) return null;
  // Try common city names that map directly to NCR
  const ncrCities = [
    "manila", "caloocan", "las piñas", "las pinas", "makati", "malabon",
    "mandaluyong", "marikina", "muntinlupa", "navotas", "parañaque", "paranaque",
    "pasay", "pasig", "pateros", "quezon city", "san juan", "taguig", "valenzuela",
  ];
  const normalized = muniName.toLowerCase().trim();
  if (ncrCities.some((c) => normalized.includes(c))) return "NCR";
  return null;
}
