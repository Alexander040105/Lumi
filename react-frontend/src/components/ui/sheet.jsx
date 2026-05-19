import * as React from "react";
import * as SheetPrimitive from "@radix-ui/react-dialog";

import { cn } from "@/lib/utils";

export const Sheet = SheetPrimitive.Root;
export const SheetTrigger = SheetPrimitive.Trigger;
export const SheetClose = SheetPrimitive.Close;

const sheetVariants = {
  top: "inset-x-0 top-0 border-b",
  bottom: "inset-x-0 bottom-0 border-t",
  left: "inset-y-0 left-0 h-full w-80 border-r",
  right: "inset-y-0 right-0 h-full w-80 border-l"
};

export function SheetContent({ side = "right", className, ...props }) {
  return (
    <SheetPrimitive.Portal>
      <SheetPrimitive.Overlay className="fixed inset-0 z-50 bg-black/50" />
      <SheetPrimitive.Content
        className={cn(
          "fixed z-50 bg-background p-6 shadow-lg transition",
          sheetVariants[side],
          className
        )}
        {...props}
      />
    </SheetPrimitive.Portal>
  );
}

export function SheetHeader({ className, ...props }) {
  return <div className={cn("flex flex-col gap-2", className)} {...props} />;
}

export function SheetFooter({ className, ...props }) {
  return <div className={cn("flex items-center justify-end gap-3", className)} {...props} />;
}

export function SheetTitle({ className, ...props }) {
  return <SheetPrimitive.Title className={cn("text-lg font-semibold", className)} {...props} />;
}

export function SheetDescription({ className, ...props }) {
  return <SheetPrimitive.Description className={cn("text-sm text-muted-foreground", className)} {...props} />;
}
