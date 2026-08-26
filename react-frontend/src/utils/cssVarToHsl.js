function hslToRgb(h, s, l) {
  s /= 100;
  l /= 100;
  const a = s * Math.min(l, 1 - l);
  const f = (n) => {
    const k = (n + h / 30) % 12;
    return l - a * Math.max(-1, Math.min(k - 3, 9 - k, 1));
  };
  const r = Math.round(255 * f(0));
  const g = Math.round(255 * f(8));
  const b = Math.round(255 * f(4));
  return `rgb(${r}, ${g}, ${b})`;
}

function cssVarToHsl(name, fallback = "#334155") {
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim();
  if (!value) return fallback;
  const [h, s, l] = value.split(/\s+/);
  if (!h || !s || !l) return fallback;
  const hi = parseFloat(h);
  const si = parseFloat(s);
  const li = parseFloat(l);
  if (Number.isNaN(hi) || Number.isNaN(si) || Number.isNaN(li)) return fallback;
  return hslToRgb(hi, si, li);
}

export default cssVarToHsl;
