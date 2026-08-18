import { Info } from "lucide-react";

import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export default function InfoTooltip({ label, content, className = "" }) {
  return (
    <TooltipProvider delayDuration={150}>
      <Tooltip>
        <TooltipTrigger
          type="button"
          className={`inline-flex items-center gap-1 text-xs font-medium text-primary underline-offset-2 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded ${className}`}
          aria-label={label}
        >
          <Info className="h-3.5 w-3.5" />
          <span>{label}</span>
        </TooltipTrigger>
        <TooltipContent side="top" align="start" className="max-w-xs">
          <p>{content}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
