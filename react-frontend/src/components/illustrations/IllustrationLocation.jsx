
/**
 * IllustrationLocation
 * Depicts the Philippine archipelago silhouette with a target location pin.
 * Uses brand tokens: primary, accent, muted, secondary.
 */
export default function IllustrationLocation({
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
      {/* Background Soft Ambient Glow */}
      <circle
        cx="80"
        cy="80"
        r="68"
        fill="hsl(var(--muted))"
        opacity="0.55"
      />
      <circle
        cx="80"
        cy="80"
        r="54"
        fill="hsl(var(--secondary))"
        opacity="0.45"
      />

      {/* Archipelago Water Rings / Map Grid Accents */}
      <circle
        cx="80"
        cy="80"
        r="44"
        stroke="hsl(var(--border))"
        strokeWidth="1.25"
        strokeDasharray="3 3"
        opacity="0.7"
      />
      <ellipse
        cx="80"
        cy="120"
        rx="38"
        ry="8"
        fill="hsl(var(--primary) / 0.12)"
      />

      {/* Stylized Philippine Archipelago Islands */}
      {/* Luzon Group */}
      <path
        d="M62 42C64 36 74 34 82 37C88 39 94 45 92 51C90 56 81 57 76 63C72 67 69 73 64 71C59 69 60 56 61 51C61 47 60 45 62 42Z"
        fill="hsl(var(--primary))"
        opacity="0.85"
      />
      {/* Palawan Ridge */}
      <path
        d="M48 76C49 74 54 83 51 90C49 94 43 99 41 97C39 95 44 87 46 82L48 76Z"
        fill="hsl(var(--primary))"
        opacity="0.7"
      />
      {/* Visayas Islands Cluster */}
      <path
        d="M74 76C78 74 84 75 83 78C82 81 77 82 74 80C72 79 72 77 74 76Z"
        fill="hsl(var(--primary))"
        opacity="0.8"
      />
      <path
        d="M87 77C91 76 96 79 93 83C91 85 86 83 87 77Z"
        fill="hsl(var(--primary))"
        opacity="0.8"
      />
      <path
        d="M78 84C82 83 85 86 83 89C81 91 76 88 78 84Z"
        fill="hsl(var(--primary))"
        opacity="0.8"
      />
      {/* Mindanao Landmass */}
      <path
        d="M68 96C74 94 88 95 94 99C98 102 99 108 94 113C88 119 76 118 71 114C66 110 65 102 68 96Z"
        fill="hsl(var(--primary))"
        opacity="0.85"
      />

      {/* Pin Shadow */}
      <ellipse
        cx="88"
        cy="68"
        rx="8"
        ry="3"
        fill="hsl(var(--primary) / 0.25)"
      />

      {/* Location Pin Head */}
      <g transform="translate(80, 36)">
        {/* Pulsing Base Ring */}
        <circle
          cx="8"
          cy="28"
          r="8"
          fill="none"
          stroke="hsl(var(--accent))"
          strokeWidth="1.5"
          opacity="0.7"
        />
        {/* Pin Body */}
        <path
          d="M8 2C3.58 2 0 5.58 0 10C0 16 8 26 8 26C8 26 16 16 16 10C16 5.58 12.42 2 8 2Z"
          fill="hsl(var(--primary))"
          stroke="hsl(var(--card))"
          strokeWidth="1.75"
        />
        {/* Inner Accent Core (Solar Gold) */}
        <circle cx="8" cy="10" r="3.25" fill="hsl(var(--accent))" />
      </g>
    </svg>
  );
}
