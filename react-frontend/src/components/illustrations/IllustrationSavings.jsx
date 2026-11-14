
/**
 * IllustrationSavings
 * Depicts a target efficiency and savings speedometer/gauge dial arc.
 * Uses brand tokens: primary arc, accent needle (Solar Gold), secondary backdrop.
 */
export default function IllustrationSavings({
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
      {/* Background Subtle Dial Glow */}
      <circle
        cx="80"
        cy="86"
        r="64"
        fill="hsl(var(--muted))"
        opacity="0.45"
      />

      {/* Outer Dial Track (Grayed/Border) */}
      <path
        d="M32 108 A 54 54 0 1 1 128 108"
        stroke="hsl(var(--border))"
        strokeWidth="10"
        strokeLinecap="round"
        fill="none"
      />

      {/* Progress Arc (Eco Primary Green) */}
      <path
        d="M32 108 A 54 54 0 1 1 118 64"
        stroke="hsl(var(--primary))"
        strokeWidth="10"
        strokeLinecap="round"
        fill="none"
      />

      {/* Scale Tick Marks */}
      <line x1="38" y1="102" x2="44" y2="98" stroke="hsl(var(--muted-foreground))" strokeWidth="2" strokeLinecap="round" opacity="0.6" />
      <line x1="48" y1="68" x2="55" y2="72" stroke="hsl(var(--muted-foreground))" strokeWidth="2" strokeLinecap="round" opacity="0.6" />
      <line x1="80" y1="46" x2="80" y2="54" stroke="hsl(var(--muted-foreground))" strokeWidth="2.5" strokeLinecap="round" opacity="0.8" />
      <line x1="112" y1="68" x2="105" y2="72" stroke="hsl(var(--muted-foreground))" strokeWidth="2" strokeLinecap="round" opacity="0.6" />
      <line x1="122" y1="102" x2="116" y2="98" stroke="hsl(var(--muted-foreground))" strokeWidth="2" strokeLinecap="round" opacity="0.6" />

      {/* Target Marker Star (High Savings Goal) */}
      <circle cx="118" cy="64" r="5" fill="hsl(var(--accent))" stroke="hsl(var(--card))" strokeWidth="1.5" />

      {/* Needle Pivot Center Shadow */}
      <circle cx="80" cy="98" r="14" fill="hsl(var(--primary) / 0.15)" />

      {/* Gauge Needle (Solar Gold accent, pointing up-right toward 75-100% savings) */}
      <g transform="rotate(35 80 98)">
        <polygon
          points="78,98 80,48 82,98"
          fill="hsl(var(--accent))"
          stroke="hsl(var(--card))"
          strokeWidth="1.5"
        />
        <circle cx="80" cy="98" r="8" fill="hsl(var(--primary))" stroke="hsl(var(--card))" strokeWidth="2" />
        <circle cx="80" cy="98" r="3.5" fill="hsl(var(--accent))" />
      </g>

      {/* Metric Badge at Bottom Center */}
      <rect
        x="54"
        y="114"
        width="52"
        height="22"
        rx="6"
        fill="hsl(var(--card))"
        stroke="hsl(var(--border))"
        strokeWidth="1.25"
      />
      <text
        x="80"
        y="129"
        textAnchor="middle"
        fill="hsl(var(--primary))"
        fontSize="11"
        fontWeight="bold"
        fontFamily="sans-serif"
      >
        75% - 100%
      </text>
    </svg>
  );
}
