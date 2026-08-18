import { useMemo, useState } from "react";
import { BookOpen, ChevronDown, ChevronUp } from "lucide-react";

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
  mode = "dialog",
  inlineLabel,
  dialogLabel,
  className = "",
}) {
  const { t } = useI18n();
  const [expanded, setExpanded] = useState(false);

  const filtered = useMemo(() => {
    if (!ids || !ids.length) return [];
    return references.filter((r) => ids.includes(r.id));
  }, [ids]);

  const inlineText =
    inlineLabel || t("citationSources.basedOn") || "Based on the Philippine and international research";
  const buttonText =
    dialogLabel || t("citationSources.viewSources") || "View Sources";

  if (!filtered.length) return null;

  if (mode === "inline") {
    return (
      <div className={`citation-sources-inline ${className}`}>
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="inline-flex items-center gap-1 text-xs font-medium text-primary underline-offset-2 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
          aria-expanded={expanded}
        >
          <BookOpen className="h-3.5 w-3.5" />
          {inlineText}
          {expanded ? (
            <ChevronUp className="h-3.5 w-3.5" />
          ) : (
            <ChevronDown className="h-3.5 w-3.5" />
          )}
        </button>
        {expanded && (
          <div className="mt-2 rounded-lg border bg-card p-3 text-xs text-muted-foreground">
            <ol className="list-decimal list-inside space-y-1.5">
              {filtered.map((ref) => (
                <li key={ref.id}>{ref.text}</li>
              ))}
            </ol>
          </div>
        )}
      </div>
    );
  }

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
          {filtered.map((ref) => (
            <li key={ref.id}>{ref.text}</li>
          ))}
        </ol>
      </DialogContent>
    </Dialog>
  );
}
