
/**
 * IllustrationBill
 * Depicts a generic Philippine electric bill with 3 highlighted inspection zones:
 * Zone 1: Monthly consumption (kWh)
 * Zone 2: Amount Due (PHP)
 * Zone 3: Rate per kWh (PHP/kWh)
 *
 * Uses role="img" with title and descriptive markup for educational accessibility.
 */
export default function IllustrationBill({
  className = "w-44 h-44",
  title = "Electric Bill Inspection Guide",
  desc = "Guide highlighting where to locate monthly consumption, amount due, and electricity rate on a bill",
  ...props
}) {
  return (
    <svg
      viewBox="0 0 180 170"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      role="img"
      aria-label={title}
      {...props}
    >
      <title>{title}</title>
      <desc>{desc}</desc>

      {/* Bill Card Drop Shadow */}
      <rect
        x="28"
        y="16"
        width="124"
        height="142"
        rx="8"
        fill="hsl(var(--primary) / 0.12)"
      />

      {/* Main Electric Bill Card */}
      <rect
        x="24"
        y="12"
        width="124"
        height="142"
        rx="8"
        fill="hsl(var(--card))"
        stroke="hsl(var(--border))"
        strokeWidth="1.75"
      />

      {/* Bill Header Strip (Meralco / DU Style header) */}
      <path
        d="M25 20C25 15.58 28.58 12 33 12H139C143.42 12 147 15.58 147 20V32H25V20Z"
        fill="hsl(var(--primary))"
      />
      {/* Header Accent Bar */}
      <rect x="34" y="20" width="30" height="4" rx="2" fill="hsl(var(--accent))" />
      <rect x="120" y="20" width="18" height="4" rx="2" fill="hsl(var(--card))" opacity="0.6" />

      {/* Customer Info Placeholder Lines */}
      <rect x="34" y="38" width="46" height="3" rx="1.5" fill="hsl(var(--muted-foreground) / 0.3)" />
      <rect x="34" y="44" width="32" height="2.5" rx="1.25" fill="hsl(var(--muted-foreground) / 0.2)" />
      <rect x="112" y="38" width="26" height="3" rx="1.5" fill="hsl(var(--muted-foreground) / 0.25)" />

      {/* Horizontal Divider */}
      <line x1="32" y1="52" x2="140" y2="52" stroke="hsl(var(--border))" strokeWidth="1" />

      {/* ========================================================= */}
      {/* ZONE 1: Monthly Consumption (kWh Used)                     */}
      {/* ========================================================= */}
      <rect
        x="32"
        y="58"
        width="108"
        height="22"
        rx="4"
        fill="hsl(var(--secondary))"
        stroke="hsl(var(--primary))"
        strokeWidth="1.25"
      />
      {/* Zone 1 Icon & Text Badge */}
      <circle cx="43" cy="69" r="5" fill="hsl(var(--primary))" />
      <path
        d="M43 66.5L41.5 69H44.5L43 71.5"
        stroke="hsl(var(--card))"
        strokeWidth="1"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <text
        x="53"
        y="68"
        fill="hsl(var(--primary))"
        fontSize="6.5"
        fontWeight="bold"
        fontFamily="sans-serif"
      >
        kWh USED
      </text>
      <text
        x="53"
        y="75.5"
        fill="hsl(var(--foreground))"
        fontSize="6"
        fontFamily="sans-serif"
      >
        416.7 kWh
      </text>
      <rect x="110" y="65" width="22" height="8" rx="2" fill="hsl(var(--primary) / 0.15)" />
      <text
        x="113"
        y="71"
        fill="hsl(var(--primary))"
        fontSize="5"
        fontWeight="600"
        fontFamily="sans-serif"
      >
        ZONE 1
      </text>

      {/* ========================================================= */}
      {/* ZONE 2: Amount Due (₱ Total Bill)                         */}
      {/* ========================================================= */}
      <rect
        x="32"
        y="85"
        width="108"
        height="24"
        rx="4"
        fill="hsl(var(--accent) / 0.25)"
        stroke="hsl(var(--accent))"
        strokeWidth="1.5"
      />
      {/* Zone 2 Peso Symbol Icon */}
      <circle cx="43" cy="97" r="5" fill="hsl(var(--accent))" />
      <text
        x="41.2"
        y="99.5"
        fill="hsl(var(--accent-foreground))"
        fontSize="7"
        fontWeight="bold"
        fontFamily="sans-serif"
      >
        ₱
      </text>
      <text
        x="53"
        y="95"
        fill="hsl(var(--foreground))"
        fontSize="6.5"
        fontWeight="bold"
        fontFamily="sans-serif"
      >
        AMOUNT DUE
      </text>
      <text
        x="53"
        y="103"
        fill="hsl(var(--foreground))"
        fontSize="7"
        fontWeight="800"
        fontFamily="sans-serif"
      >
        ₱ 5,000.00
      </text>
      <rect x="110" y="93" width="22" height="8" rx="2" fill="hsl(var(--accent) / 0.5)" />
      <text
        x="113"
        y="99"
        fill="hsl(var(--accent-foreground))"
        fontSize="5"
        fontWeight="700"
        fontFamily="sans-serif"
      >
        ZONE 2
      </text>

      {/* ========================================================= */}
      {/* ZONE 3: Electricity Tariff Rate (₱ per kWh)               */}
      {/* ========================================================= */}
      <rect
        x="32"
        y="114"
        width="108"
        height="22"
        rx="4"
        fill="hsl(var(--muted))"
        stroke="hsl(var(--primary) / 0.6)"
        strokeWidth="1.25"
      />
      <circle cx="43" cy="125" r="5" fill="hsl(var(--primary) / 0.2)" />
      <text
        x="41"
        y="127.5"
        fill="hsl(var(--primary))"
        fontSize="6"
        fontWeight="bold"
        fontFamily="sans-serif"
      >
        %
      </text>
      <text
        x="53"
        y="124"
        fill="hsl(var(--muted-foreground))"
        fontSize="6"
        fontWeight="bold"
        fontFamily="sans-serif"
      >
        RATE / CHARGE
      </text>
      <text
        x="53"
        y="131.5"
        fill="hsl(var(--foreground))"
        fontSize="6"
        fontFamily="sans-serif"
      >
        ₱ 12.00 / kWh
      </text>
      <rect x="110" y="121" width="22" height="8" rx="2" fill="hsl(var(--border))" />
      <text
        x="113"
        y="127"
        fill="hsl(var(--muted-foreground))"
        fontSize="5"
        fontWeight="600"
        fontFamily="sans-serif"
      >
        ZONE 3
      </text>

      {/* Bill Barcode Bottom Motif */}
      <rect x="34" y="142" width="2" height="6" fill="hsl(var(--border))" />
      <rect x="38" y="142" width="4" height="6" fill="hsl(var(--border))" />
      <rect x="44" y="142" width="1.5" height="6" fill="hsl(var(--border))" />
      <rect x="48" y="142" width="3" height="6" fill="hsl(var(--border))" />
      <rect x="53" y="142" width="2" height="6" fill="hsl(var(--border))" />
      <rect x="57" y="142" width="4" height="6" fill="hsl(var(--border))" />
      <rect x="63" y="142" width="1.5" height="6" fill="hsl(var(--border))" />
      <rect x="67" y="142" width="5" height="6" fill="hsl(var(--border))" />
      <rect x="74" y="142" width="2" height="6" fill="hsl(var(--border))" />
      <rect x="78" y="142" width="3" height="6" fill="hsl(var(--border))" />
    </svg>
  );
}
