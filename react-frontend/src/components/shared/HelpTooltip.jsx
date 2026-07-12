import { useState } from "react";
import { HelpCircle } from "lucide-react";
import { getGlossary } from "@/utils/glossary";

/**
 * HelpTooltip — wraps children with a hover tooltip that shows a plain-English
 * definition of a technical term from the glossary.
 */

export default function HelpTooltip({ term, children, className = "" }) {
  const [show, setShow] = useState(false);
  const definition = getGlossary(term);

  if (!definition) {
    return <span className={className}>{children}</span>;
  }

  return (
    <span className={`relative inline-flex items-center gap-1 ${className}`}>
      {children}
      <span
        className="cursor-help text-muted-foreground hover:text-foreground transition-colors"
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        onClick={() => setShow(!show)}
      >
        <HelpCircle className="h-3.5 w-3.5" />
      </span>
      {show && (
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 rounded-lg bg-slate-800 px-3 py-2 text-xs text-white shadow-lg z-50">
          {definition}
        </span>
      )}
    </span>
  );
}
