import { Card, CardContent } from "@/components/ui/card";

/**
 * InsightCard — displays a metric with:
 * 1. Title
 * 2. Big number
 * 3. Plain-English interpretation
 * 4. Optional recommendation / next step
 */

export default function InsightCard({
  icon: Icon,
  iconColor = "text-slate-600",
  iconBg = "bg-slate-100",
  borderColor = "border-l-4 border-l-slate-400",
  title,
  value,
  subtitle,
  interpretation,
  recommendation,
  nextStep,
}) {
  return (
    <Card className={borderColor}>
      <CardContent className="p-5">
        <div className="flex items-start gap-3">
          {Icon && (
            <div className={`shrink-0 rounded-lg p-2 ${iconBg}`}>
              <Icon className={`h-5 w-5 ${iconColor}`} />
            </div>
          )}
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="mt-1 text-2xl font-bold tracking-tight">{value}</p>
            {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
            {interpretation && (
              <p className="mt-2 text-sm text-slate-700 leading-relaxed">{interpretation}</p>
            )}
            {recommendation && (
              <p className="mt-1.5 text-sm font-medium text-emerald-700">{recommendation}</p>
            )}
            {nextStep && (
              <p className="mt-1 text-xs text-slate-500">{nextStep}</p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
