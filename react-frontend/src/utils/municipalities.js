export function filterMunicipalities(items, query) {
  const q = (query || "").trim().toLowerCase();
  if (!q) return items;
  return items
    .map((m) => {
      const name = m.name.toLowerCase();
      const prov = (m.province_name || "").toLowerCase();
      const nameIdx = name.indexOf(q);
      const provIdx = prov.indexOf(q);
      // Match if query is in municipality name OR province name
      const matchIdx = nameIdx >= 0 ? nameIdx : provIdx;
      return { ...m, _matchIdx: matchIdx, _startsWith: nameIdx === 0, _provinceMatch: provIdx >= 0 && nameIdx < 0 };
    })
    .filter((m) => m._matchIdx >= 0)
    .sort((a, b) => {
      if (a._startsWith !== b._startsWith) return a._startsWith ? -1 : 1;
      if (a._provinceMatch !== b._provinceMatch) return a._provinceMatch ? 1 : -1;
      return a._matchIdx - b._matchIdx || a.name.localeCompare(b.name);
    });
}

export function formatMunicipalityLabel(m) {
  return m.province_name ? `${m.name}, ${m.province_name}` : m.name;
}
