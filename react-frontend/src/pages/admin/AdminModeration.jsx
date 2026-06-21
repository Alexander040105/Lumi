import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { getApiBaseUrl } from "@/utils/env";

export default function AdminModeration() {
  const { accessToken } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState({});

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `${getApiBaseUrl()}/admin/chat-sessions?limit=50`,
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      const data = await res.json();
      setSessions(data.sessions || []);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const toggleFlag = async (sessionId, currentFlag) => {
    try {
      await fetch(
        `${getApiBaseUrl()}/admin/chat-sessions/${sessionId}/flag`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({ is_flagged: !currentFlag }),
        }
      );
      setSessions((prev) =>
        prev.map((s) =>
          s.id === sessionId ? { ...s, is_flagged: !currentFlag } : s
        )
      );
    } catch {
      // ignore
    }
  };

  const toggleExpand = (id) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const formatDate = (d) => (d ? new Date(d).toLocaleString() : "—");

  if (loading) return <p className="p-6">Loading chat sessions...</p>;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Content Moderation</h1>
      <div className="border rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted">
            <tr>
              <th className="text-left p-3">Session</th>
              <th className="text-left p-3">User ID</th>
              <th className="text-left p-3">Messages</th>
              <th className="text-left p-3">Created</th>
              <th className="text-left p-3">Flagged</th>
              <th className="text-left p-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((s) => (
              <>
                <tr key={s.id} className="border-t hover:bg-muted/50">
                  <td className="p-3 font-medium">{s.title || "Untitled"}</td>
                  <td className="p-3 text-xs text-muted-foreground truncate max-w-[120px]">
                    {s.user_id}
                  </td>
                  <td className="p-3">{(s.chat_messages || []).length}</td>
                  <td className="p-3">{formatDate(s.created_at)}</td>
                  <td className="p-3">
                    {s.is_flagged ? (
                      <Badge variant="destructive">Flagged</Badge>
                    ) : (
                      <Badge variant="outline">Clean</Badge>
                    )}
                  </td>
                  <td className="p-3">
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => toggleExpand(s.id)}
                      >
                        {expanded[s.id] ? "Hide" : "View"}
                      </Button>
                      <Button
                        size="sm"
                        variant={s.is_flagged ? "default" : "destructive"}
                        onClick={() => toggleFlag(s.id, s.is_flagged)}
                      >
                        {s.is_flagged ? "Unflag" : "Flag"}
                      </Button>
                    </div>
                  </td>
                </tr>
                {expanded[s.id] && (
                  <tr>
                    <td colSpan={6} className="p-3 bg-muted/30">
                      <div className="space-y-2 max-h-64 overflow-y-auto">
                        {(s.chat_messages || []).map((msg, idx) => (
                          <div
                            key={idx}
                            className={`text-sm p-2 rounded ${
                              msg.role === "user"
                                ? "bg-primary/10 ml-4"
                                : "bg-secondary/50 mr-4"
                            }`}
                          >
                            <span className="text-xs font-semibold uppercase text-muted-foreground">
                              {msg.role}
                            </span>
                            <p className="mt-1">{msg.content}</p>
                          </div>
                        ))}
                        {(s.chat_messages || []).length === 0 && (
                          <p className="text-sm text-muted-foreground">No messages.</p>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </>
            ))}
            {sessions.length === 0 && (
              <tr>
                <td colSpan={6} className="p-6 text-center text-muted-foreground">
                  No chat sessions found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
