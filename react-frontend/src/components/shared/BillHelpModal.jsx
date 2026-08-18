import { HelpCircle } from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

export default function BillHelpModal({
  triggerText = "Where can I find this on my bill?",
  title = "Finding your actual consumption",
  description = "Look for the \"Actual Consumption\" line on your Meralco bill. It is usually shown in kWh near the usage or metering section.",
  className = "",
}) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <button
          type="button"
          className={`inline-flex items-center gap-1 text-xs font-medium text-primary underline-offset-2 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded ${className}`}
          aria-haspopup="dialog"
        >
          <HelpCircle className="h-3.5 w-3.5" />
          {triggerText}
        </button>
      </DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>
        <div className="mt-2 aspect-video w-full rounded-lg border bg-muted p-4 flex items-center justify-center relative overflow-hidden">
          <div className="w-full max-w-sm rounded-md border border-border bg-card p-3 shadow-sm">
            <div className="space-y-2">
              <div className="h-2 w-1/2 rounded bg-muted-foreground/20" />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Account Details</span>
                <span>Billing Period</span>
              </div>
              <div className="h-px bg-border" />
              <div className="rounded border border-dashed border-primary/50 bg-primary/5 p-2">
                <div className="text-[10px] uppercase tracking-wide text-muted-foreground">Actual Consumption</div>
                <div className="text-lg font-semibold text-foreground">300 kWh</div>
              </div>
              <div className="h-2 w-3/4 rounded bg-muted-foreground/20" />
            </div>
          </div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none">
            <svg width="120" height="80" viewBox="0 0 120 80" fill="none" className="opacity-80">
              <circle cx="60" cy="40" r="32" stroke="hsl(var(--primary))" strokeWidth="2" fill="none" strokeDasharray="4 4" />
            </svg>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
