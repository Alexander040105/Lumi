import { useState } from "react";

import { useAuth } from "@/hooks/useAuth";

export default function AdminConfig() {
  const { accessToken } = useAuth();
  const [config, setConfig] = useState({
    chatbot_enabled: true,
    maintenance_mode: false,
    free_chat_limit: 5,
    free_sim_limit: 3,
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      await fetch(`${import.meta.env.VITE_API_URL}/api/v1/admin/config`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(config),
      });
      setMessage("Configuration saved.");
    } catch {
      setMessage("Failed to save configuration.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">System Configuration</h1>
      <div className="space-y-4">
        <label className="flex items-center justify-between p-3 border rounded-lg">
          <span>Chatbot Enabled</span>
          <input
            type="checkbox"
            checked={config.chatbot_enabled}
            onChange={(e) => setConfig({ ...config, chatbot_enabled: e.target.checked })}
            className="w-5 h-5"
          />
        </label>
        <label className="flex items-center justify-between p-3 border rounded-lg">
          <span>Maintenance Mode</span>
          <input
            type="checkbox"
            checked={config.maintenance_mode}
            onChange={(e) => setConfig({ ...config, maintenance_mode: e.target.checked })}
            className="w-5 h-5"
          />
        </label>
        <div className="p-3 border rounded-lg">
          <label className="block text-sm font-medium mb-1">Free Chat Messages / Month</label>
          <input
            type="number"
            value={config.free_chat_limit}
            onChange={(e) => setConfig({ ...config, free_chat_limit: parseInt(e.target.value) || 0 })}
            className="w-full px-3 py-2 border rounded-lg"
          />
        </div>
        <div className="p-3 border rounded-lg">
          <label className="block text-sm font-medium mb-1">Free Saved Simulations</label>
          <input
            type="number"
            value={config.free_sim_limit}
            onChange={(e) => setConfig({ ...config, free_sim_limit: parseInt(e.target.value) || 0 })}
            className="w-full px-3 py-2 border rounded-lg"
          />
        </div>
        {message && (
          <p className={`text-sm ${message.includes("Failed") ? "text-destructive" : "text-green-600"}`}>
            {message}
          </p>
        )}
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
        >
          {saving ? "Saving..." : "Save Configuration"}
        </button>
      </div>
    </div>
  );
}
