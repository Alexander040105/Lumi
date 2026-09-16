import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

export default function SearchableSelect({
  query, onQueryChange,
  open, onOpenChange,
  items,
  getOptionId, getOptionLabel,
  selectedId, onSelect,
  placeholder, disabled, error,
  emptyText, moreResultsText,
  maxVisible = 50,
}) {
  return (
    <div>
      <div className="relative">
        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          className="pl-9"
          placeholder={placeholder}
          value={query}
          onChange={(e) => { onQueryChange(e.target.value); onOpenChange(true); }}
          onFocus={() => onOpenChange(true)}
          onBlur={() => onOpenChange(false)}
          disabled={disabled}
          autoComplete="off"
        />
      </div>
      {open && (
        <div className="mt-1 max-h-64 overflow-y-auto rounded-lg border bg-card shadow-sm z-10 relative">
          {items.length ? (
            <>
              {items.slice(0, maxVisible).map((item) => (
                <button
                  key={getOptionId(item)}
                  type="button"
                  className={"w-full px-3 py-2 text-left text-sm hover:bg-muted transition-colors " + (String(getOptionId(item)) === String(selectedId) ? "bg-accent font-medium" : "")}
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => onSelect(item)}
                >
                  {getOptionLabel(item)}
                </button>
              ))}
              {items.length > maxVisible && (
                <div className="px-3 py-2 text-xs text-muted-foreground border-t">
                  {moreResultsText(items.length - maxVisible, items.length)}
                </div>
              )}
            </>
          ) : (
            <div className="px-3 py-2 text-sm text-muted-foreground">{emptyText}</div>
          )}
        </div>
      )}
      {error && <p className="text-xs text-destructive mt-1">{error}</p>}
    </div>
  );
}
