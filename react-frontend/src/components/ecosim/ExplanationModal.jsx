import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import Markdown from "@/components/shared/Markdown";
import ReadAloud from "@/components/shared/ReadAloud";
import { useI18n } from "@/i18n";

export default function ExplanationModal({ title, content, aiSummary, aiPending, triggerText }) {
  const { t } = useI18n();
  const showAiSection = aiPending || (typeof aiSummary === "string" && aiSummary.trim());
  return (
    <Dialog>
      <DialogTrigger asChild>
        <button
          type="button"
          aria-haspopup="dialog"
          className="text-xs text-foreground underline decoration-dotted"
        >
          {triggerText}
        </button>
      </DialogTrigger>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between gap-2 pr-6">
            {title}
            <ReadAloud text={`${content || ""} ${aiSummary || ""}`} />
          </DialogTitle>
        </DialogHeader>
        <div className="max-h-[60vh] overflow-y-auto text-sm text-muted-foreground leading-relaxed">
          <Markdown>{content}</Markdown>
          {showAiSection && (
            <div className="border-t pt-3 mt-3 space-y-2">
              <p className="text-sm font-semibold text-foreground">{t("ecosim.results.aiAnalysis.title")}</p>
              {aiPending && (
                <p className="text-xs text-muted-foreground">{t("ecosim.results.aiAnalysis.pendingBody")}</p>
              )}
              {aiSummary && aiSummary.trim() && <Markdown>{aiSummary}</Markdown>}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
