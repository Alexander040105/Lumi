/**
 * Provider matching for EcoSim recommendations.
 * Filters providers by category and region, ranks them by technology fit
 * and verification, and appends nationwide entries after regional matches.
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

function providerCategory(provider) {
  return provider.category || "provider";
}

function byFitThenVerified(tech) {
  return (a, b) =>
    Number(providerHasTechnology(b, tech)) - Number(providerHasTechnology(a, tech)) ||
    Number(Boolean(b.verified)) - Number(Boolean(a.verified));
}

/**
 * @param {{ providers: Array, region: string|null, technology: string|null, category?: string }}
 * @returns {{ matched: Array, fallback: Array }}
 *   matched — regional matches (technology fit, then verified), followed by
 *   nationwide entries with the same ordering. A nationwide entry whose `region`
 *   also matches counts as regional.
 *   fallback — up to 3 verified providers (only when matched is empty),
 *   preferring technology fit and region diversity.
 */
export function matchProviders({ providers, region, technology, category }) {
  const tech = normalizeTechnology(technology);
  const all = (providers || []).filter(
    (p) => !category || category === "all" || providerCategory(p) === category
  );
  const order = byFitThenVerified(tech);

  const matched = all
    .filter((p) => p.region === region)
    .sort(order)
    .concat(all.filter((p) => p.nationwide && p.region !== region).sort(order));

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
