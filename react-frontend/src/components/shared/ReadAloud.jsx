import { useEffect, useState } from "react";
import { Volume2, Square } from "lucide-react";
import { useI18n } from "@/i18n";

const toPlainText = (s) =>
  String(s)
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`([^`]*)`/g, "$1")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/\*\*|__|~~/g, "")
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
    .replace(/^\s*[>*-]+\s+/gm, "")
    .replace(/\s+/g, " ")
    .trim();

export default function ReadAloud({ text, className = "" }) {
  const { t, locale } = useI18n();
  const [speaking, setSpeaking] = useState(false);
  const supported = typeof window !== "undefined" && "speechSynthesis" in window;

  useEffect(() => {
    if (!supported) return undefined;
    return () => window.speechSynthesis.cancel();
  }, [supported, text]);

  if (!supported || !text || !String(text).trim()) return null;

  const toggle = () => {
    const synth = window.speechSynthesis;
    if (speaking) {
      synth.cancel();
      setSpeaking(false);
      return;
    }
    const utterance = new SpeechSynthesisUtterance(toPlainText(text));
    utterance.lang = locale === "fil" ? "fil-PH" : "en-US";
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    synth.cancel();
    synth.speak(utterance);
    setSpeaking(true);
  };

  const label = speaking ? t("common.stopReading") : t("common.readAloud");
  return (
    <button
      type="button"
      onClick={toggle}
      aria-pressed={speaking}
      title={label}
      className={`inline-flex h-10 shrink-0 items-center gap-1.5 rounded-md px-3 text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
        speaking
          ? "bg-primary/10 text-primary hover:bg-primary/15"
          : "text-muted-foreground hover:bg-muted hover:text-foreground"
      } ${className}`}
    >
      {speaking ? (
        <Square className="h-3.5 w-3.5" aria-hidden="true" />
      ) : (
        <Volume2 className="h-3.5 w-3.5" aria-hidden="true" />
      )}
      <span>{label}</span>
    </button>
  );
}
