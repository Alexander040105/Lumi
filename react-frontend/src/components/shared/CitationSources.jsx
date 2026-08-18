import { useMemo } from "react";
import { BookOpen } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useI18n } from "@/i18n";
import references from "@/data/references.json";

export default function CitationSources({
  ids,
  sources,
  dialogLabel,
  className = "",
}) {
  const { t } = useI18n();

  const items = useMemo(() => {
    const fromIds = Array.isArray(ids)
      ? references.filter((r) => ids.includes(r.id))
      : [];
    const fromSources = Array.isArray(sources)
      ? sources.map((text, i) => ({ id: `s-${i}`, text }))
      : [];
    return [...fromIds, ...fromSources];
  }, [ids, sources]);

  const buttonText = dialogLabel || t("citationSources.viewSources") || "View Sources";

  if (!items.length) return null;

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className={`gap-1.5 ${className}`}
          aria-haspopup="dialog"
        >
          <BookOpen className="h-4 w-4" />
          {buttonText}
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{t("citationSources.title") || "Sources & References"}</DialogTitle>
          <DialogDescription>
            {t("citationSources.description") ||
              "LUMI uses published research and trusted climate and energy data sources."}
          </DialogDescription>
        </DialogHeader>
        <ol className="mt-4 list-decimal list-inside space-y-3 text-sm text-muted-foreground">
          {items.map((ref) => (
            <li key={ref.id}>{ref.text}</li>
          ))}
        </ol>
      </DialogContent>
    </Dialog>
  );
}
