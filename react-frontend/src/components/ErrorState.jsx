export default function ErrorState({ title = "Error", message, onRetry, retryLabel = "Try Again" }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[200px] p-6">
      <div className="max-w-sm w-full bg-card rounded-xl shadow-sm border border-border p-5 text-center">
        <div className="w-10 h-10 mx-auto mb-3 rounded-full bg-destructive/10 flex items-center justify-center">
          <svg className="w-5 h-5 text-destructive" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h4 className="text-base font-semibold text-foreground mb-1">{title}</h4>
        <p className="text-sm text-muted-foreground mb-3">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="bg-primary text-primary-foreground px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-primary/90"
          >
            {retryLabel}
          </button>
        )}
      </div>
    </div>
  );
}

export function LoadingState({ label = "Loading..." }) {
  return (
    <div className="flex items-center justify-center min-h-[200px]">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-3 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
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
          <svg className="w-6 h-6 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
        </div>
        <h4 className="text-base font-semibold text-foreground mb-1">{title}</h4>
        {message && <p className="text-sm text-muted-foreground mb-3">{message}</p>}
        {actionLabel && onAction && (
          <button
            onClick={onAction}
            className="bg-primary text-primary-foreground px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-primary/90"
          >
            {actionLabel}
          </button>
        )}
      </div>
    </div>
  );
}
