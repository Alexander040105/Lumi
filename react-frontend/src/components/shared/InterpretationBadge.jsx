import { Badge } from "@/components/ui/badge";

/**
 * InterpretationBadge — converts a score (0-100) into a human-readable badge
 * with star rating and a one-sentence plain-English interpretation.
 */

const RATINGS = [
  { pct: 0.80, label: "Excellent", color: "bg-emerald-500", text: "text-emerald-700" },
  { pct: 0.60, label: "Good", color: "bg-lime-500", text: "text-lime-700" },
  { pct: 0.40, label: "Moderate", color: "bg-amber-400", text: "text-amber-700" },
  { pct: 0.20, label: "Fair", color: "bg-orange-400", text: "text-orange-700" },
  { pct: 0.00, label: "Poor", color: "bg-red-400", text: "text-red-700" },
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
  const rating = getRating(score, max);
  const stars = getStars(score, max);
  return (
    <div className={`flex items-center gap-2 flex-wrap ${className}`}>
      <Badge className={`${rating.color} text-white hover:${rating.color}`}>{rating.label}</Badge>
      {showStars && <span className="text-amber-500 tracking-widest text-sm">{stars}</span>}
    </div>
  );
}
