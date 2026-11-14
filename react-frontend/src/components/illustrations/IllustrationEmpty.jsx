
/**
 * IllustrationEmpty
 * Depicts a thoughtful nature leaf with a magnifying glass search motif.
 * Designed for empty states, no-data conditions, and search fallbacks.
 * Uses brand tokens: muted, primary, accent, card, border.
 */
export default function IllustrationEmpty({
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
      {/* Background Soft Ambient Plate */}
      <circle
        cx="80"
        cy="80"
        r="64"
        fill="hsl(var(--muted))"
        opacity="0.45"
      />

      {/* Dashed Discovery Orbit */}
      <circle
        cx="72"
        cy="72"
        r="44"
        stroke="hsl(var(--border))"
        strokeWidth="1.5"
        strokeDasharray="4 4"
        opacity="0.8"
      />

      {/* Gentle Base Shadow */}
      <ellipse
        cx="76"
        cy="126"
        rx="36"
        ry="6"
        fill="hsl(var(--primary) / 0.12)"
      />

      {/* Botanical Leaf Motif (Center Left) */}
      <path
        d="M52 96C52 96 46 64 74 48C94 36 98 58 92 78C86 98 52 96 52 96Z"
        fill="hsl(var(--secondary))"
        stroke="hsl(var(--primary))"
        strokeWidth="2"
      />
      {/* Leaf Central Vein */}
      <path
        d="M56 94C66 84 76 74 86 54"
        stroke="hsl(var(--primary))"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      {/* Lateral Veins */}
      <path
        d="M68 82C74 80 80 82 82 84"
        stroke="hsl(var(--primary))"
        strokeWidth="1.25"
        strokeLinecap="round"
        opacity="0.7"
      />
      <path
        d="M74 72C80 70 86 72 88 74"
        stroke="hsl(var(--primary))"
        strokeWidth="1.25"
        strokeLinecap="round"
        opacity="0.7"
      />

      {/* Magnifying Glass (Overlaid at 45 degree angle) */}
      <g transform="translate(62, 42)">
        {/* Glass Lens Circle */}
        <circle
          cx="30"
          cy="30"
          r="26"
          fill="hsl(var(--card))"
          stroke="hsl(var(--primary))"
          strokeWidth="3.5"
        />
        {/* Lens Inner Accent Rim (Solar Gold reflection) */}
        <circle
          cx="30"
          cy="30"
          r="21"
          stroke="hsl(var(--accent))"
          strokeWidth="1.5"
          opacity="0.75"
        />
        {/* Specular Glint Reflection */}
        <path
          d="M18 24C20 18 26 14 32 14"
          stroke="hsl(var(--muted-foreground))"
          strokeWidth="2"
          strokeLinecap="round"
          opacity="0.4"
        />

        {/* Sturdy Angled Handle */}
        <path
          d="M48 48L68 68"
          stroke="hsl(var(--primary))"
          strokeWidth="6"
          strokeLinecap="round"
        />
        <path
          d="M52 52L66 66"
          stroke="hsl(var(--accent))"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </g>
    </svg>
  );
}
