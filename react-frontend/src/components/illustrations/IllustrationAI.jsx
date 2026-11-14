
/**
 * IllustrationAI
 * Depicts an intelligent synthesis document with neural AI sparkle nodes.
 * Uses brand tokens: muted doc, accent sparkles (Solar Gold), primary nodes.
 */
export default function IllustrationAI({
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
      {/* Background Soft Ambient Aura */}
      <circle
        cx="80"
        cy="80"
        r="62"
        fill="hsl(var(--muted))"
        opacity="0.45"
      />
      <circle
        cx="110"
        cy="45"
        r="28"
        fill="hsl(var(--secondary))"
        opacity="0.5"
      />

      {/* Document Backdrop / Shadow */}
      <rect
        x="42"
        y="30"
        width="76"
        height="102"
        rx="8"
        fill="hsl(var(--primary) / 0.12)"
      />

      {/* Main Document Body */}
      <rect
        x="38"
        y="26"
        width="76"
        height="102"
        rx="8"
        fill="hsl(var(--card))"
        stroke="hsl(var(--border))"
        strokeWidth="1.75"
      />

      {/* Document Folded Top-Right Corner */}
      <path
        d="M98 26L114 42H102C99.79 42 98 40.21 98 38V26Z"
        fill="hsl(var(--muted))"
        stroke="hsl(var(--border))"
        strokeWidth="1.25"
      />

      {/* Document Header Line */}
      <rect x="48" y="40" width="34" height="4.5" rx="2.25" fill="hsl(var(--primary))" />

      {/* Document Content Lines */}
      <rect x="48" y="52" width="56" height="3" rx="1.5" fill="hsl(var(--muted-foreground) / 0.3)" />
      <rect x="48" y="60" width="46" height="3" rx="1.5" fill="hsl(var(--muted-foreground) / 0.25)" />
      <rect x="48" y="68" width="52" height="3" rx="1.5" fill="hsl(var(--muted-foreground) / 0.25)" />

      {/* Analysis Chip inside Document */}
      <rect
        x="48"
        y="80"
        width="56"
        height="32"
        rx="6"
        fill="hsl(var(--secondary))"
        stroke="hsl(var(--primary) / 0.4)"
        strokeWidth="1"
      />
      {/* Mini Energy Wave inside Chip */}
      <path
        d="M54 98L62 92L70 99L78 88L86 94L96 86"
        stroke="hsl(var(--primary))"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* Major AI Sparkle Star (Top Right) */}
      <g transform="translate(112, 34)">
        <path
          d="M12 0C12 6.63 17.37 12 24 12C17.37 12 12 17.37 12 24C12 17.37 6.63 12 0 12C6.63 12 12 6.63 12 0Z"
          fill="hsl(var(--accent))"
        />
        <circle cx="12" cy="12" r="2.5" fill="hsl(var(--card))" />
      </g>

      {/* Secondary Sparkle Star (Bottom Left) */}
      <g transform="translate(24, 98) scale(0.65)">
        <path
          d="M12 0C12 6.63 17.37 12 24 12C17.37 12 12 17.37 12 24C12 17.37 6.63 12 0 12C6.63 12 12 6.63 12 0Z"
          fill="hsl(var(--accent))"
        />
      </g>

      {/* Minor Sparkle Star (Top Left) */}
      <g transform="translate(32, 20) scale(0.45)">
        <path
          d="M12 0C12 6.63 17.37 12 24 12C17.37 12 12 17.37 12 24C12 17.37 6.63 12 0 12C6.63 12 12 6.63 12 0Z"
          fill="hsl(var(--primary))"
        />
      </g>
    </svg>
  );
}
