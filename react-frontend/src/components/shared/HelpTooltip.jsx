import { HelpCircle } from "lucide-react";
import { useI18n } from "@/i18n";
import { getGlossary } from "@/utils/glossary";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

/**
 * HelpTooltip — wraps children with a hover tooltip that shows a plain-English
 * definition of a technical term from the glossary.
 */

export default function HelpTooltip({ term, children, className = "" }) {
  const { t } = useI18n();

  const key = (term || "").toLowerCase().trim().replace(/\s+/g, "_");
  const glossaryKey = `glossary.${key}`;
  const translated = t(glossaryKey);
  const definition = translated !== glossaryKey ? translated : getGlossary(term);

  if (!definition) {
    return <span className={className}>{children}</span>;
  }

  return (
    <TooltipProvider delayDuration={150}>
      <Tooltip>
        <span className={`inline-flex items-center gap-1 ${className}`}>
          {children}
          <TooltipTrigger asChild>
            <button
              type="button"
              aria-label={definition}
              className="text-muted-foreground hover:text-foreground transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
            >
              <HelpCircle className="h-3.5 w-3.5" />
            </button>
          </TooltipTrigger>
        </span>
        <TooltipContent side="top" align="center" className="max-w-64">
          <p>{definition}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
