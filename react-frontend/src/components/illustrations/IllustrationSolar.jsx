
/**
 * IllustrationSolar
 * Depicts a high-efficiency rooftop/ground solar PV panel array with a glowing sun.
 * Uses brand tokens: accent sun (Solar Gold), primary panel frames/cells.
 */
export default function IllustrationSolar({
  className = "w-36 h-36",
  ariaHidden = true,
  ...props
}) {
  return (
    <svg
      viewBox="0 0 160 160"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden={ariaHidden}
      {...props}
    >
      {/* Background Solar Aura */}
      <circle
        cx="115"
        cy="45"
        r="32"
        fill="hsl(var(--accent) / 0.25)"
      />

      {/* Solar Gold Sun */}
      <circle
        cx="115"
        cy="45"
        r="18"
        fill="hsl(var(--accent))"
      />
      {/* Sun Ray Beams */}
      <line x1="115" y1="18" x2="115" y2="24" stroke="hsl(var(--accent))" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="115" y1="66" x2="115" y2="72" stroke="hsl(var(--accent))" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="88" y1="45" x2="94" y2="45" stroke="hsl(var(--accent))" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="136" y1="45" x2="142" y2="45" stroke="hsl(var(--accent))" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="96" y1="26" x2="101" y2="31" stroke="hsl(var(--accent))" strokeWidth="2" strokeLinecap="round" />
      <line x1="129" y1="59" x2="134" y2="64" stroke="hsl(var(--accent))" strokeWidth="2" strokeLinecap="round" />
      <line x1="96" y1="64" x2="101" y2="59" stroke="hsl(var(--accent))" strokeWidth="2" strokeLinecap="round" />
      <line x1="129" y1="31" x2="134" y2="26" stroke="hsl(var(--accent))" strokeWidth="2" strokeLinecap="round" />

      {/* Ground / Roof Line Base */}
      <ellipse
        cx="75"
        cy="134"
        rx="58"
        ry="8"
        fill="hsl(var(--primary) / 0.12)"
      />

      {/* Solar Panel Racking Stand */}
      <line x1="42" y1="124" x2="52" y2="88" stroke="hsl(var(--border))" strokeWidth="3" strokeLinecap="round" />
      <line x1="102" y1="124" x2="112" y2="88" stroke="hsl(var(--border))" strokeWidth="3" strokeLinecap="round" />
      <line x1="72" y1="130" x2="82" y2="94" stroke="hsl(var(--border))" strokeWidth="3" strokeLinecap="round" />

      {/* Angled Solar Array Surface (Isometric 3D perspective) */}
      {/* Panel Outer Perimeter */}
      <polygon
        points="22,118 64,68 134,68 92,118"
        fill="hsl(var(--primary))"
        stroke="hsl(var(--card))"
        strokeWidth="2.5"
      />

      {/* Solar Cell Grid Lines */}
      {/* Longitudinal Dividers */}
      <line x1="43" y1="93" x2="113" y2="93" stroke="hsl(var(--card))" strokeWidth="1.25" opacity="0.6" />
      <line x1="32.5" y1="105.5" x2="102.5" y2="105.5" stroke="hsl(var(--card))" strokeWidth="1.25" opacity="0.6" />
      <line x1="53.5" y1="80.5" x2="123.5" y2="80.5" stroke="hsl(var(--card))" strokeWidth="1.25" opacity="0.6" />

      {/* Lateral Cell Dividers */}
      <line x1="46" y1="68" x2="32" y2="118" stroke="hsl(var(--card))" strokeWidth="1.25" opacity="0.6" />
      <line x1="68" y1="68" x2="54" y2="118" stroke="hsl(var(--card))" strokeWidth="1.25" opacity="0.6" />
      <line x1="90" y1="68" x2="76" y2="118" stroke="hsl(var(--card))" strokeWidth="1.25" opacity="0.6" />
      <line x1="112" y1="68" x2="98" y2="118" stroke="hsl(var(--card))" strokeWidth="1.25" opacity="0.6" />

      {/* Energy Sparkle Glow on Corner */}
      <circle cx="28" cy="112" r="3.5" fill="hsl(var(--accent))" opacity="0.9" />
    </svg>
  );
}
