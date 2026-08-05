import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { getApiBaseUrl } from "../utils/env";
import { useAuth } from "../hooks/useAuth";
import { supabase } from "../services/supabaseClient";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/i18n";

function formatCitations(text) {
  if (!text) return text;
  const parts = text.split(/(\[Source \d+:[^\]]+\])/g);
  return parts.map((part, idx) => {
    const match = part.match(/^\[Source (\d+):\s*(.+)]$/);
    if (match) {
      return (
        <span
          key={idx}
          className="inline-flex items-center gap-1 rounded-md bg-emerald-100 px-1.5 py-0.5 text-xs font-semibold text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200 mx-0.5"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          {match[2]}
        </span>
      );
    }
    return <span key={idx}>{part}</span>;
  });
}

export default function ChatPage() {
  const { t } = useI18n();
  const { user, accessToken } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(searchParams.get("session") || null);

  // Load existing session messages
  useEffect(() => {
    const sid = searchParams.get("session");
    if (!sid || !user?.id) return;

    setSessionId(sid);

    const loadMessages = async () => {
      const { data, error } = await supabase
        .from("chat_messages")
        .select("role, content, created_at")
        .eq("session_id", sid)
        .order("created_at", { ascending: true });

      if (error) {
        toast.error(t("chat.failedToLoadHistory"));
        return;
      }

      if (data) {
        setMessages(data.map((m) => ({ role: m.role, content: m.content })));
      }
    };

    loadMessages();
  }, [searchParams, user]);

  const handleNewChat = () => {
    setMessages([]);
    setSessionId(null);
    setSearchParams({});
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    let currentSessionId = sessionId;

    try {
      // Create session on first message
      if (!currentSessionId && user?.id) {
        const title = input.trim().slice(0, 30) + (input.length > 30 ? "..." : "");
        const { data: session, error } = await supabase
          .from("chat_sessions")
          .insert({ user_id: user.id, title })
          .select("id")
          .single();

        if (error) throw new Error(t("chat.failedToCreateSession"));
        currentSessionId = session.id;
        setSessionId(currentSessionId);
        setSearchParams({ session: currentSessionId });
      }

      // Persist user message
      if (currentSessionId) {
        await supabase.from("chat_messages").insert({
          session_id: currentSessionId,
          role: "user",
          content: userMsg.content,
        });
      }

      const res = await fetch(`${getApiBaseUrl()}/chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ message: userMsg.content }),
      });

      if (!res.ok) {
        throw new Error(t("chat.serverError", { status: res.status, statusText: res.statusText }));
      }

      const data = await res.json();
      if (data.message) {
        const assistantMsg = { role: "assistant", content: data.message };
        setMessages((prev) => [...prev, assistantMsg]);

        // Persist assistant message
        if (currentSessionId) {
          await supabase.from("chat_messages").insert({
            session_id: currentSessionId,
            role: "assistant",
            content: data.message,
          });
        }
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${err.message}` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-4xl mx-auto p-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">{t("chat.title")}</h1>
        <Button variant="outline" size="sm" onClick={handleNewChat}>
          {t("chat.newChat")}
        </Button>
      </div>
      <div className="flex-1 overflow-y-auto border rounded-lg p-4 space-y-3 bg-muted/30">
        {messages.length === 0 && (
          <p className="text-muted-foreground text-center mt-8">
            {t("chat.empty")}
          </p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg max-w-[80%] ${
              m.role === "user"
                ? "bg-primary text-primary-foreground ml-auto"
                : "bg-muted"
            }`}
          >
            {m.role === "assistant" ? formatCitations(m.content) : m.content}
          </div>
        ))}
        {isLoading && (
          <div className="bg-muted p-3 rounded-lg max-w-[80%] animate-pulse">
            {t("chat.thinking")}
          </div>
        )}
      </div>
      <div className="flex gap-2 mt-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder={t("chat.placeholder")}
          className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <button
          onClick={handleSend}
          disabled={isLoading}
          className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
        >
          {t("chat.send")}
        </button>
      </div>
    </div>
  );
}
