import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { AlertTriangle, ExternalLink, Package } from "lucide-react";
import { useI18n } from "@/i18n";

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 0,
  }).format(value ?? 0);

function MatchedProduct({ product }) {
  const { t } = useI18n();
  if (!product) return null;
  const label = [product.brand, product.product_name]
    .filter(Boolean)
    .join(" ");
  return (
    <div className="mt-1.5 text-xs text-muted-foreground">
      <span className="font-medium text-foreground">{label}</span>
      {" — "}
      {product.price_php != null ? (
        <span>{formatCurrency(product.price_php)}</span>
      ) : (
        <span className="italic">{t("ecosim.bom.quoteOnly")}</span>
      )}
      {product.source_site && <span> · {product.source_site}</span>}
      {/^https?:\/\//i.test(product.url ?? "") && (
        <a
          href={product.url}
          target="_blank"
          rel="noopener noreferrer"
          className="ml-1.5 inline-flex items-center gap-0.5 text-primary hover:underline"
        >
          {t("ecosim.bom.viewProduct")}
          <ExternalLink className="h-3 w-3" aria-hidden="true" />
        </a>
      )}
    </div>
  );
}

export default function EcosimBOM({ sizing }) {
  const { t } = useI18n();
  const items = sizing?.bom_items ?? [];
  if (!items.length) return null;

  const totalCost = sizing?.total_installation_cost_php ?? 0;
  const solarShare = items.filter((i) => i.id !== "battery_storage");
  const batteryItems = items.filter((i) => i.id === "battery_storage");

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Package className="h-5 w-5 text-primary" aria-hidden="true" />
          {t("ecosim.bom.title")}
        </CardTitle>
        <CardDescription>
          {t("ecosim.bom.sizingEstimate", {
            kw: (sizing.actual_system_kwp ?? 0).toFixed(2),
            panels: sizing.panels_needed ?? 0,
            cost: formatCurrency(totalCost),
          })}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("ecosim.bom.component")}</TableHead>
              <TableHead className="text-right">{t("ecosim.bom.qty")}</TableHead>
              <TableHead className="text-right">{t("ecosim.bom.share")}</TableHead>
              <TableHead className="text-right">{t("ecosim.bom.total")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {solarShare.map((row) => (
              <TableRow key={row.id}>
                <TableCell>
                  <span className="text-sm">{row.name}</span>
                  <MatchedProduct product={row.matched_product} />
                </TableCell>
                <TableCell className="text-right font-medium align-top">{row.qty}</TableCell>
                <TableCell className="text-right text-muted-foreground align-top">
                  {Math.round((row.cost_share ?? 0) * 100)}%
                </TableCell>
                <TableCell className="text-right font-medium align-top">
                  {formatCurrency(row.total_php)}
                </TableCell>
              </TableRow>
            ))}
            {batteryItems.map((row) => (
              <TableRow key={row.id} className="bg-primary/5">
                <TableCell>
                  <span className="text-sm">{row.name}</span>
                  <MatchedProduct product={row.matched_product} />
                </TableCell>
                <TableCell className="text-right font-medium align-top">{row.qty}</TableCell>
                <TableCell className="text-right text-muted-foreground align-top">—</TableCell>
                <TableCell className="text-right font-medium align-top">
                  {formatCurrency(row.total_php)}
                </TableCell>
              </TableRow>
            ))}
            <TableRow>
              <TableCell colSpan={3} className="text-right font-semibold">
                {t("ecosim.bom.estimatedTotal")}
              </TableCell>
              <TableCell className="text-right font-bold">{formatCurrency(totalCost)}</TableCell>
            </TableRow>
          </TableBody>
        </Table>

        {sizing.disclaimers?.length > 0 && (
          <div className="rounded-lg border border-warning/40 bg-warning/10 p-3 space-y-1.5" role="note">
            {sizing.disclaimers.map((d, i) => (
              <p key={i} className="text-xs text-warning-foreground flex items-start gap-2">
                <AlertTriangle className="h-3.5 w-3.5 shrink-0 mt-0.5" aria-hidden="true" />
                <span>{d}</span>
              </p>
            ))}
          </div>
        )}

        {sizing.citations?.length > 0 && (
          <details className="rounded-lg border bg-muted/30 p-3 text-sm">
            <summary className="cursor-pointer font-medium text-primary">
              {t("ecosim.bom.sourcesTitle")}
            </summary>
            <ul className="mt-3 space-y-2 list-disc pl-5">
              {sizing.citations.map((c) => (
                <li key={c.id} className="text-xs text-muted-foreground">
                  <span>{c.apa_citation}</span>
                  {c.parameter_supported && (
                    <span className="block italic mt-0.5">
                      {t("ecosim.bom.supports", { param: c.parameter_supported })}
                    </span>
                  )}
                  {c.url && (
                    <a
                      href={c.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-1 inline-flex items-center gap-0.5 text-primary hover:underline"
                    >
                      {t("ecosim.bom.viewSource")}
                      <ExternalLink className="h-3 w-3" aria-hidden="true" />
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </details>
        )}
      </CardContent>
    </Card>
  );
}
