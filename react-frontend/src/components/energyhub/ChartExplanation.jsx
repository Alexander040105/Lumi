import { Card, CardContent } from "@/components/ui/card";
import { Info } from "lucide-react";
import { useI18n } from "@/i18n";

/**
 * ChartExplanation — reusable "What / Why / Action" explanation block
 * for every visualization in EnergyHub.
 */
export default function ChartExplanation({ title, what, why, action }) {
  const { t } = useI18n();
  return (
    <Card className="mt-3 border-l-4 border-l-primary bg-muted/40">
      <CardContent className="py-3 px-4">
        <div className="flex items-start gap-2">
          <Info className="mt-0.5 h-4 w-4 text-primary shrink-0" />
          <div className="space-y-1 text-sm">
            {title && <p className="font-semibold text-foreground">{title}</p>}
            {what && (
              <p className="text-muted-foreground">
                <span className="font-medium text-foreground">{t("energyHub.chartExplanation.what")}</span> {what}
              </p>
            )}
            {why && (
              <p className="text-muted-foreground">
                <span className="font-medium text-foreground">{t("energyHub.chartExplanation.why")}</span> {why}
              </p>
            )}
            {action && (
              <p className="text-muted-foreground">
                <span className="font-medium text-foreground">{t("energyHub.chartExplanation.action")}</span> {action}
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
