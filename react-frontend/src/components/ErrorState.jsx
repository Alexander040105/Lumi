import { AlertCircle, Inbox } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function ErrorState({ title = "Error", message, onRetry, retryLabel = "Try Again" }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[200px] p-6">
      <div className="max-w-sm w-full bg-card rounded-xl shadow-sm border border-border p-5 text-center">
        <div className="w-10 h-10 mx-auto mb-3 rounded-full bg-destructive/10 flex items-center justify-center">
          <AlertCircle className="w-5 h-5 text-destructive" />
        </div>
        <h4 className="text-base font-semibold text-foreground mb-1">{title}</h4>
        <p className="text-sm text-muted-foreground mb-3">{message}</p>
        {onRetry && (
          <Button size="sm" onClick={onRetry}>
            {retryLabel}
          </Button>
        )}
      </div>
    </div>
  );
}

export function LoadingState({ label = "Loading..." }) {
  return (
    <div className="flex items-center justify-center min-h-[200px]">
      <div className="flex flex-col items-center gap-3" role="status" aria-live="polite">
        <div className="w-8 h-8 border-2 border-muted border-t-primary rounded-full animate-spin" />
        <span className="text-sm text-muted-foreground">{label}</span>
      </div>
    </div>
  );
}

export function EmptyState({ title = "No data", message, actionLabel, onAction }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[200px] p-6">
      <div className="max-w-sm w-full text-center">
        <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-muted flex items-center justify-center">
          <Inbox className="w-6 h-6 text-muted-foreground" />
        </div>
        <h4 className="text-base font-semibold text-foreground mb-1">{title}</h4>
        {message && <p className="text-sm text-muted-foreground mb-3">{message}</p>}
        {actionLabel && onAction && (
          <Button size="sm" onClick={onAction}>
            {actionLabel}
          </Button>
        )}
      </div>
    </div>
  );
}
