
/**
 * IllustrationWind
 * Depicts a wind turbine with dynamic aerodynamic air motion lines.
 * Uses brand tokens: brand-success/chart-wind, primary, muted airstream curves.
 */
export default function IllustrationWind({
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
      {/* Background Soft Sky Backdrop */}
      <circle
        cx="80"
        cy="80"
        r="64"
        fill="hsl(var(--muted))"
        opacity="0.45"
      />

      {/* Aerodynamic Wind Streamlines */}
      <path
        d="M24 48C42 48 52 42 72 42C92 42 108 50 138 50"
        stroke="hsl(var(--chart-wind))"
        strokeWidth="2.5"
        strokeLinecap="round"
        opacity="0.5"
      />
      <path
        d="M18 72C36 72 48 66 68 66C88 66 102 76 144 76"
        stroke="hsl(var(--chart-wind))"
        strokeWidth="2.5"
        strokeLinecap="round"
        opacity="0.75"
      />
      <path
        d="M32 94C48 94 58 88 78 88C98 88 114 96 136 96"
        stroke="hsl(var(--chart-wind))"
        strokeWidth="2"
        strokeLinecap="round"
        opacity="0.4"
      />

      {/* Turbine Foundation / Ground Mound */}
      <ellipse
        cx="80"
        cy="142"
        rx="42"
        ry="7"
        fill="hsl(var(--primary) / 0.15)"
      />

      {/* Tapered Wind Turbine Tower */}
      <polygon
        points="77,66 83,66 85,140 75,140"
        fill="hsl(var(--primary))"
      />

      {/* Nacelle (Rotor Hub Enclosure) */}
      <rect
        x="73"
        y="60"
        width="14"
        height="9"
        rx="4"
        fill="hsl(var(--chart-wind))"
        stroke="hsl(var(--card))"
        strokeWidth="1.25"
      />

      {/* Rotor Nose Cone */}
      <circle
        cx="80"
        cy="64"
        r="4.5"
        fill="hsl(var(--card))"
      />

      {/* Three Aerodynamic Rotor Blades */}
      {/* Blade 1 (Pointing Up) */}
      <path
        d="M80 64C78 48 76 34 80 18C84 34 82 48 80 64Z"
        fill="hsl(var(--chart-wind))"
        stroke="hsl(var(--card))"
        strokeWidth="1"
      />
      {/* Blade 2 (Pointing Down-Right) */}
      <path
        d="M80 64C93 72 106 81 120 90C108 92 95 86 80 64Z"
        fill="hsl(var(--chart-wind))"
        stroke="hsl(var(--card))"
        strokeWidth="1"
      />
      {/* Blade 3 (Pointing Down-Left) */}
      <path
        d="M80 64C65 72 52 81 38 90C50 92 63 86 80 64Z"
        fill="hsl(var(--chart-wind))"
        stroke="hsl(var(--card))"
        strokeWidth="1"
      />

      {/* Blade Center Fastener */}
      <circle cx="80" cy="64" r="2" fill="hsl(var(--primary))" />
    </svg>
  );
}
