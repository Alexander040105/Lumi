
/**
 * IllustrationReview
 * Depicts a review clipboard with verified energy checklist items.
 * Uses brand tokens: primary checks, border, card, accent confirmation badge.
 */
export default function IllustrationReview({
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
      {/* Background Glow */}
      <circle
        cx="80"
        cy="84"
        r="64"
        fill="hsl(var(--muted))"
        opacity="0.45"
      />

      {/* Board Shadow */}
      <rect
        x="36"
        y="26"
        width="88"
        height="112"
        rx="10"
        fill="hsl(var(--primary) / 0.12)"
      />

      {/* Main Clipboard Backing */}
      <rect
        x="32"
        y="22"
        width="88"
        height="112"
        rx="10"
        fill="hsl(var(--card))"
        stroke="hsl(var(--border))"
        strokeWidth="1.75"
      />

      {/* Top Metallic Clamp */}
      <rect
        x="60"
        y="16"
        width="32"
        height="14"
        rx="4"
        fill="hsl(var(--primary))"
      />
      <circle cx="76" cy="20" r="2.5" fill="hsl(var(--card))" />

      {/* Paper Sheet Inner Inset */}
      <rect
        x="42"
        y="36"
        width="68"
        height="88"
        rx="4"
        fill="hsl(var(--secondary) / 0.35)"
      />

      {/* Checklist Item 1 (Location & Climate) */}
      <circle cx="52" cy="50" r="5" fill="hsl(var(--primary))" />
      <path
        d="M49.5 50L51.5 52L54.5 48"
        stroke="hsl(var(--primary-foreground))"
        strokeWidth="1.25"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <rect x="62" y="48" width="38" height="4" rx="2" fill="hsl(var(--foreground))" opacity="0.85" />

      {/* Checklist Item 2 (Consumption & Bill) */}
      <circle cx="52" cy="68" r="5" fill="hsl(var(--primary))" />
      <path
        d="M49.5 68L51.5 70L54.5 66"
        stroke="hsl(var(--primary-foreground))"
        strokeWidth="1.25"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <rect x="62" y="66" width="34" height="4" rx="2" fill="hsl(var(--foreground))" opacity="0.85" />

      {/* Checklist Item 3 (Savings Target) */}
      <circle cx="52" cy="86" r="5" fill="hsl(var(--primary))" />
      <path
        d="M49.5 86L51.5 88L54.5 84"
        stroke="hsl(var(--primary-foreground))"
        strokeWidth="1.25"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <rect x="62" y="84" width="40" height="4" rx="2" fill="hsl(var(--foreground))" opacity="0.85" />

      {/* Checklist Item 4 (AI Analysis Option) */}
      <circle cx="52" cy="104" r="5" fill="hsl(var(--primary))" />
      <path
        d="M49.5 104L51.5 106L54.5 102"
        stroke="hsl(var(--primary-foreground))"
        strokeWidth="1.25"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <rect x="62" y="102" width="28" height="4" rx="2" fill="hsl(var(--foreground))" opacity="0.85" />

      {/* Floating Ready Seal / Badge (Bottom Right) */}
      <g transform="translate(104, 102)">
        <circle cx="16" cy="16" r="16" fill="hsl(var(--accent))" stroke="hsl(var(--card))" strokeWidth="2" />
        <path
          d="M10 16L14 20L22 12"
          stroke="hsl(var(--accent-foreground))"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </g>
    </svg>
  );
}
