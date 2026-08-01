import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Package } from "lucide-react";
import { useI18n } from "@/i18n";

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 0,
  }).format(value ?? 0);

function deriveSystemKw(source, generationKwh) {
  if (!generationKwh) return 0;
  switch (source) {
    case "Solar":
      return generationKwh / (30 * 4.5);
    case "Wind":
      return generationKwh / (30 * 24 * 0.25);
    case "Hydro":
      return generationKwh / (30 * 24 * 0.5);
    case "Geothermal":
      return generationKwh / (30 * 24);
    default:
      return 0;
  }
}

const BOM_SCHEMA = {
  Solar: [
    {
      id: "solar_panels",
      costShare: 0.4,
      qtyFn: (kw) => Math.max(1, Math.ceil((kw * 1000) / 400)),
    },
    { id: "solar_inverter", costShare: 0.2, qtyFn: () => 1 },
    { id: "solar_mounting", costShare: 0.15, qtyFn: () => 1 },
    { id: "solar_labor", costShare: 0.2, qtyFn: () => 1 },
    { id: "solar_permits", costShare: 0.05, qtyFn: () => 1 },
  ],
  Wind: [
    { id: "wind_turbine", costShare: 0.5, qtyFn: () => 1 },
    { id: "wind_tower", costShare: 0.25, qtyFn: () => 1 },
    { id: "wind_controller", costShare: 0.15, qtyFn: () => 1 },
    { id: "wind_labor", costShare: 0.1, qtyFn: () => 1 },
  ],
  Hydro: [
    { id: "hydro_turbine", costShare: 0.35, qtyFn: () => 1 },
    { id: "hydro_penstock", costShare: 0.3, qtyFn: () => 1 },
    { id: "hydro_controller", costShare: 0.15, qtyFn: () => 1 },
    { id: "hydro_labor", costShare: 0.2, qtyFn: () => 1 },
  ],
};

export default function EcosimBOM({ result }) {
  const { t } = useI18n();
  const source = result?.recommended_source;
  const rec = result?.options?.find((o) => o.source === source) || {};
  const installationCost = rec.installation_cost ?? result?.installation_cost ?? 0;
  const systemKw = rec.system_kw ?? deriveSystemKw(source, rec.estimated_generation_kwh ?? result?.estimated_generation_kwh);

  if (!source || installationCost <= 0) {
    return null;
  }

  if (source === "Geothermal") {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Package className="h-5 w-5 text-primary" />
            {t("ecosim.bom.title")}
          </CardTitle>
          <CardDescription>{t("ecosim.bom.description")}</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {t("ecosim.bom.notApplicable")}
          </p>
        </CardContent>
      </Card>
    );
  }

  const items = BOM_SCHEMA[source] || [];
  const rows = items.map((entry) => {
    const qty = entry.qtyFn(systemKw);
    const totalCost = installationCost * entry.costShare;
    const unitCost = qty > 0 ? totalCost / qty : 0;
    return {
      ...entry,
      qty,
      unitCost,
      totalCost,
    };
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Package className="h-5 w-5 text-primary" />
          {t("ecosim.bom.title")}
        </CardTitle>
        <CardDescription>
          {t("ecosim.bom.estimated", { kw: systemKw.toFixed(2), source: t("ecosim.results.sources." + source), cost: formatCurrency(installationCost) })}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("ecosim.bom.component")}</TableHead>
              <TableHead className="text-right">{t("ecosim.bom.qty")}</TableHead>
              <TableHead>{t("ecosim.bom.unit")}</TableHead>
              <TableHead className="text-right">{t("ecosim.bom.unitCost")}</TableHead>
              <TableHead className="text-right">{t("ecosim.bom.total")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.id}>
                <TableCell>{t("ecosim.bom.items." + row.id + ".item")}</TableCell>
                <TableCell className="text-right font-medium">{row.qty}</TableCell>
                <TableCell className="text-muted-foreground">{t("ecosim.bom.items." + row.id + ".unit")}</TableCell>
                <TableCell className="text-right">{formatCurrency(row.unitCost)}</TableCell>
                <TableCell className="text-right font-medium">{formatCurrency(row.totalCost)}</TableCell>
              </TableRow>
            ))}
            <TableRow>
              <TableCell colSpan={4} className="text-right font-semibold">
                {t("ecosim.bom.estimatedTotal")}
              </TableCell>
              <TableCell className="text-right font-bold">{formatCurrency(installationCost)}</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
