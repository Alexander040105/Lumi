/**
 * Glossary — plain-English definitions for technical energy terms.
 * Used by HelpTooltip throughout LUMI.
 */

export const GLOSSARY = {
  "solar irradiance":
    "The amount of sunlight reaching your area. More sunlight generally means more electricity can be produced by solar panels.",
  "capacity factor":
    "Shows how efficiently a renewable energy system is expected to operate compared to its maximum possible output.",
  "hydraulic head":
    "The height difference of flowing water. Greater height usually means more electricity can be generated.",
  "payback period":
    "The estimated number of years needed to recover the cost of your renewable energy investment.",
  "net metering":
    "A program where you can sell excess electricity back to the power company, reducing your bill even further.",
  "kWh":
    "Kilowatt-hour — the unit of electricity on your bill. One kWh is like running a 1,000-watt appliance for one hour.",
  "MW":
    "Megawatt — a large unit of power. One MW equals 1,000 kilowatts, enough to power hundreds of homes.",
  "GWh":
    "Gigawatt-hour — a very large amount of electricity, often used to measure national or regional energy use.",
  "renewable share":
    "The percentage of electricity that comes from clean sources like solar, wind, hydro, or geothermal instead of fossil fuels.",
  "fossil fuels":
    "Coal, oil, and natural gas. Burning them produces electricity but also releases pollution and carbon dioxide.",
  "carbon reduction":
    "The amount of CO₂ (carbon dioxide) pollution you avoid by using clean energy instead of fossil fuels.",
  "suitability score":
    "A rating from 0 to 100 that tells you how well a renewable energy type matches your location's conditions.",
  "elevation":
    "How high above sea level your location is. Higher areas can have different wind and temperature conditions.",
  "transmission charge":
    "The cost of moving electricity from power plants to your area through large power lines.",
  "distribution charge":
    "The cost of delivering electricity from local substations to your home through neighborhood power lines.",
  "generation charge":
    "The cost of actually producing electricity at power plants. This is the biggest part of your electric bill.",
  "utility-scale":
    "Large power plants that serve thousands of homes, not something you can install in your backyard.",
  "micro-hydro":
    "A small water-powered generator for homes or small communities, using nearby streams or rivers.",
  "rooftop solar":
    "Solar panels installed on your roof to generate electricity for your home.",
  "off-grid":
    "Being completely independent from the electric company by generating all your own power.",
  "grid-tied":
    "Connected to the electric company lines. You can use grid power when your solar or wind isn't producing enough.",
  "inverter":
    "A device that converts the electricity from solar panels into the type of electricity your home appliances use.",
  "battery storage":
    "Batteries that store excess solar or wind energy for use at night or during cloudy days.",
  "peak demand":
    "The highest amount of electricity the country needs at any single moment. High peaks can cause brownouts.",
  "brownout":
    "A temporary drop in electricity supply, causing lights to dim and appliances to work poorly.",
  "blackout":
    "A complete loss of electricity in an area, usually caused by storms or overloaded power systems.",
};

export function getGlossary(term) {
  const normalized = (term || "").toLowerCase().trim();
  return GLOSSARY[normalized] || null;
}
