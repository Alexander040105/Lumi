import { useEffect, useRef, useState } from "react";

import { useAuth } from "@/hooks/useAuth";
import { useI18n } from "@/i18n";
import { supabase } from "@/services/supabaseClient";
import { getApiBaseUrl } from "@/utils/env";
import { Button } from "@/components/ui/button";

export default function ProfilePage() {
  const { t } = useI18n();
  const { user, accessToken, emailConfirmed } = useAuth();
  const [profile, setProfile] = useState({
    full_name: "",
    organization: "",
    location: "",
    avatar_url: "",
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!user) return;
    supabase
      .from("profiles")
      .select("full_name, organization, location, avatar_url")
      .eq("id", user.id)
      .single()
      .then(({ data }) => {
        if (data) setProfile((p) => ({ ...p, ...data }));
      });

    // Sync OAuth avatar from auth metadata to profiles on first load
    fetch(`${getApiBaseUrl()}/protected/sync-avatar`, {
      method: "POST",
      headers: { Authorization: `Bearer ${accessToken}` },
    }).catch(() => {});
  }, [user, accessToken]);

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      await fetch(`${getApiBaseUrl()}/protected/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(profile),
      });
      setMessage(t("profile.updated"));
    } catch {
      setMessage(t("profile.updateFailed"));
    } finally {
      setSaving(false);
    }
  };

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setMessage("");
    try {
      const ext = file.name.split(".").pop();
      const path = `${user.id}/avatar.${ext}`;
      const { error: uploadError } = await supabase.storage
        .from("avatars")
        .upload(path, file, { upsert: true, contentType: file.type });
      if (uploadError) throw uploadError;

      const { data: urlData } = supabase.storage.from("avatars").getPublicUrl(path);
      const publicUrl = urlData?.publicUrl;
      if (!publicUrl) throw new Error("Failed to get public URL");

      // Update profile in DB
      await fetch(`${getApiBaseUrl()}/protected/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ avatar_url: publicUrl }),
      });

      setProfile((p) => ({ ...p, avatar_url: publicUrl }));
      setMessage(t("profile.avatarUpdated"));
    } catch (err) {
      setMessage(t("profile.avatarUploadFailed") + err.message);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleRemoveAvatar = async () => {
    setUploading(true);
    try {
      await fetch(`${getApiBaseUrl()}/protected/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ avatar_url: null }),
      });
      setProfile((p) => ({ ...p, avatar_url: "" }));
      setMessage(t("profile.avatarRemoved"));
    } catch {
      setMessage(t("profile.avatarRemoveFailed"));
    } finally {
      setUploading(false);
    }
  };

  const initials = (profile.full_name || user?.email || "U")
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const currentAvatar =
    profile.avatar_url || user?.user_metadata?.avatar_url || user?.user_metadata?.picture;

  if (!user) return <p>{t("common.loading")}</p>;

  return (
    <div className="max-w-xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-2">{t("profile.title")}</h1>

      <div className="flex items-center gap-2 mb-6 text-sm text-muted-foreground">
        <span>{user?.email}</span>
        {emailConfirmed ? (
          <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800">
            ✓ {t("profile.verified")}
          </span>
        ) : (
          <span className="inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
            ⚠ {t("profile.unverified")}
          </span>
        )}
      </div>

      {/* Avatar Section */}
      <div className="flex items-center gap-4 mb-6">
        <div className="relative">
          {currentAvatar ? (
            <img
              src={currentAvatar}
              alt=""
              className="h-20 w-20 rounded-full object-cover border"
            />
          ) : (
            <div className="h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center text-xl font-bold text-primary border">
              {initials}
            </div>
          )}
        </div>
        <div className="flex flex-col gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileChange}
          />
          <Button
            variant="outline"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            {uploading ? t("common.saving") : t("profile.changePhoto")}
          </Button>
          {currentAvatar && (
            <Button
              variant="ghost"
              size="sm"
              className="text-destructive"
              onClick={handleRemoveAvatar}
              disabled={uploading}
            >
              {t("profile.removePhoto")}
            </Button>
          )}
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">{t("profile.fullName")}</label>
          <input
            type="text"
            value={profile.full_name || ""}
            onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">{t("profile.organization")}</label>
          <input
            type="text"
            value={profile.organization || ""}
            onChange={(e) => setProfile({ ...profile, organization: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">{t("profile.location")}</label>
          <input
            type="text"
            value={profile.location || ""}
            onChange={(e) => setProfile({ ...profile, location: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
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
          {saving ? t("common.saving") : t("profile.saveChanges")}
        </button>
      </div>
    </div>
  );
}
