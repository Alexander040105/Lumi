import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import Markdown from "@/components/shared/Markdown";

export default function ExplanationModal({ title, content, triggerText }) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <button
          type="button"
          className="text-xs text-foreground underline decoration-dotted"
        >
          {triggerText}
        </button>
      </DialogTrigger>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        <div className="max-h-[60vh] overflow-y-auto text-sm text-muted-foreground leading-relaxed">
          <Markdown>{content}</Markdown>
        </div>
      </DialogContent>
    </Dialog>
  );
}
