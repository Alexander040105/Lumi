import { CheckCircle } from "lucide-react";

/**
 * NextStepList — renders a numbered checklist of actionable steps with
 * plain-English explanations of why each step matters.
 *
 * steps: Array of { title: string, description: string }
 */

export default function NextStepList({ steps, className = "" }) {
  if (!steps || steps.length === 0) return null;

  return (
    <div className={`grid gap-3 md:grid-cols-2 ${className}`}>
      {steps.map((step, i) => (
        <div
          key={i}
          className="flex items-start gap-3 p-3 rounded-lg border bg-muted/20 hover:bg-muted/30 transition-colors"
        >
          <CheckCircle className="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-sm">{step.title}</p>
            <p className="text-xs text-muted-foreground mt-0.5">{step.description}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
