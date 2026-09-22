/**
 * Provider matching for EcoSim recommendations.
 * Filters providers by region and ranks them by technology fit and verification.
 */

export function normalizeTechnology(source) {
  if (!source) return null;
  return source === "Hydropower" ? "Hydro" : source;
}

export function providerHasTechnology(provider, technology) {
  if (!technology) return true;
  const techs = String(provider.technology || "Solar")
    .split("/")
    .map((s) => s.trim());
  return techs.includes(technology);
}

/**
 * @param {{ providers: Array, region: string|null, technology: string|null }}
 * @returns {{ matched: Array, fallback: Array }}
 *   matched — providers in `region`, stable-sorted: technology fit first, then verified first.
 *   fallback — up to 3 verified providers (only when matched is empty), preferring
 *   technology fit and region diversity.
 */
export function matchProviders({ providers, region, technology }) {
  const tech = normalizeTechnology(technology);
  const all = providers || [];

  const matched = all
    .filter((p) => p.region === region)
    .sort(
      (a, b) =>
        Number(providerHasTechnology(b, tech)) - Number(providerHasTechnology(a, tech)) ||
        Number(Boolean(b.verified)) - Number(Boolean(a.verified))
    );

  let fallback = [];
  if (matched.length === 0) {
    const verified = all
      .filter((p) => p.verified)
      .sort(
        (a, b) =>
          Number(providerHasTechnology(b, tech)) - Number(providerHasTechnology(a, tech))
      );
    const seenRegions = new Set();
    const primary = [];
    const extra = [];
    for (const p of verified) {
      if (!seenRegions.has(p.region) && primary.length < 3) {
        seenRegions.add(p.region);
        primary.push(p);
      } else {
        extra.push(p);
      }
    }
    fallback = primary.concat(extra).slice(0, 3);
  }

  return { matched, fallback };
}
