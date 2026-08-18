import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function ExpandableBlock({
  title,
  children,
  defaultOpen = false,
  className = "",
  contentClassName = "",
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className={cn("rounded-xl border bg-card", className)}>
      <Button
        type="button"
        variant="ghost"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="w-full justify-between px-4 py-3 h-auto text-left font-semibold hover:bg-muted/50"
      >
        <span className="text-sm">{title}</span>
        {open ? (
          <ChevronUp className="h-4 w-4 shrink-0 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
        )}
      </Button>
      {open && (
        <div className={cn("px-4 pb-4 text-sm text-muted-foreground", contentClassName)}>
          {children}
        </div>
      )}
    </div>
  );
}
