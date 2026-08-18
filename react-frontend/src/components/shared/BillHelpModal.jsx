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
        <div className="mt-2 w-full rounded-lg border bg-muted p-4">
          <img
            src="/MeralcoBillWithBoxes.png"
            alt={title}
            className="w-full h-auto rounded-lg"
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}
