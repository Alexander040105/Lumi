function cssVarToHsl(name, fallback = "#334155") {
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim();
  if (!value) return fallback;
  const [h, s, l] = value.split(/\s+/);
  if (!h || !s || !l) return fallback;
  return `hsl(${h}, ${s}, ${l})`;
}

export default cssVarToHsl;
