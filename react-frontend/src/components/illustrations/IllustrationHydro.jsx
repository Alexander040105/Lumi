
/**
 * IllustrationHydro
 * Depicts run-of-river hydro generation, stream currents, and hydro energy droplets.
 * Uses brand tokens: chart-hydro (primary green-blue tone), accent droplet, secondary ripples.
 */
export default function IllustrationHydro({
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
      {/* Background Soft Basin Glow */}
      <circle
        cx="80"
        cy="80"
        r="64"
        fill="hsl(var(--muted))"
        opacity="0.45"
      />

      {/* Fluvial Mountain / Embankment Curves */}
      <path
        d="M20 120C36 102 54 98 72 108C90 118 108 104 140 126V142H20V120Z"
        fill="hsl(var(--secondary))"
      />

      {/* Flowing River Channel Path */}
      <path
        d="M60 28C60 52 44 68 44 88C44 116 84 112 84 138H112C112 96 74 100 74 76C74 54 88 44 88 28H60Z"
        fill="hsl(var(--chart-hydro))"
        opacity="0.75"
      />

      {/* Stream Flow Vectors / Velocity Wave Lines */}
      <path
        d="M68 42C68 54 58 64 58 78C58 92 78 96 78 116"
        stroke="hsl(var(--card))"
        strokeWidth="2.25"
        strokeLinecap="round"
        opacity="0.65"
      />
      <path
        d="M78 46C78 58 84 66 84 76"
        stroke="hsl(var(--card))"
        strokeWidth="1.75"
        strokeLinecap="round"
        opacity="0.5"
      />

      {/* Water Droplet Splash Ripple Rings */}
      <ellipse
        cx="108"
        cy="76"
        rx="22"
        ry="8"
        stroke="hsl(var(--chart-hydro))"
        strokeWidth="1.5"
        strokeDasharray="4 3"
        opacity="0.6"
      />
      <ellipse
        cx="108"
        cy="76"
        rx="14"
        ry="5"
        stroke="hsl(var(--chart-hydro))"
        strokeWidth="1.5"
        opacity="0.8"
      />

      {/* Major Hydro Energy Droplet (Suspended, Dynamic) */}
      <g transform="translate(98, 48)">
        <path
          d="M10 2C10 2 2 12 2 18C2 22.42 5.58 26 10 26C14.42 26 18 22.42 18 18C18 12 10 2 10 2Z"
          fill="hsl(var(--primary))"
          stroke="hsl(var(--card))"
          strokeWidth="1.75"
        />
        {/* Droplet Light Specular Glint */}
        <path
          d="M6 16C6 14 8 10 10 7"
          stroke="hsl(var(--card))"
          strokeWidth="1.25"
          strokeLinecap="round"
        />
        {/* Golden Energy Spark inside Drop */}
        <circle cx="10" cy="18" r="3" fill="hsl(var(--accent))" />
      </g>

      {/* Floating Micro Splash Drops */}
      <circle cx="90" cy="54" r="2.5" fill="hsl(var(--primary))" opacity="0.8" />
      <circle cx="124" cy="62" r="3" fill="hsl(var(--primary))" opacity="0.7" />
    </svg>
  );
}
