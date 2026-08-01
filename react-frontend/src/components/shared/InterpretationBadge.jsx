import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/i18n";

/**
 * InterpretationBadge — converts a score (0-100) into a human-readable badge
 * with star rating and a one-sentence plain-English interpretation.
 */

const RATINGS = [
  { pct: 0.80, label: "Excellent", color: "bg-primary text-primary-foreground", text: "text-primary", bg: "bg-secondary", border: "border-primary/30" },
  { pct: 0.60, label: "Good", color: "bg-chart-wind/10 text-foreground", text: "text-chart-wind", bg: "bg-chart-wind/10", border: "border-chart-wind/30" },
  { pct: 0.40, label: "Moderate", color: "bg-warning/10 text-foreground", text: "text-warning", bg: "bg-warning/10", border: "border-warning/30" },
  { pct: 0.20, label: "Fair", color: "bg-chart-geothermal/10 text-foreground", text: "text-chart-geothermal", bg: "bg-chart-geothermal/10", border: "border-chart-geothermal/30" },
  { pct: 0.00, label: "Poor", color: "bg-destructive/10 text-foreground", text: "text-destructive", bg: "bg-destructive/10", border: "border-destructive/30" },
];

export function getRating(score, max = 100) {
  const pct = (score ?? 0) / max;
  return RATINGS.find((r) => pct >= r.pct) || RATINGS[RATINGS.length - 1];
}

export function getStars(score, max = 100) {
  const pct = Math.max(0, Math.min(1, (score ?? 0) / max));
  const full = Math.floor(pct * 5);
  let s = "";
  for (let i = 0; i < full; i++) s += "★";
  while (s.length < 5) s += "☆";
  return s;
}

export default function InterpretationBadge({ score, max = 100, showStars = true, className = "" }) {
  const { t } = useI18n();
  const rating = getRating(score, max);
  const stars = getStars(score, max);
  return (
    <div className={`flex items-center gap-2 flex-wrap ${className}`}>
      <Badge className={`${rating.color} hover:${rating.color}`}>{t("common.ratings." + rating.label.toLowerCase())}</Badge>
      {showStars && <span className="text-warning tracking-widest text-sm">{stars}</span>}
    </div>
  );
}
