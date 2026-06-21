import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";
import { getApiBaseUrl } from "@/utils/env";

export default function CreateUserModal({ open, onClose, onCreated }) {
  const { accessToken } = useAuth();
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("user");
  const [plan, setPlan] = useState("free");

  // Admins are always premium
  const isAdminRole = role === "admin" || role === "dev";
  const displayPlan = isAdminRole ? "premium" : plan;
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const reset = () => {
    setEmail("");
    setFullName("");
    setRole("user");
    setPlan("free");
    setResult(null);
    setError("");
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${getApiBaseUrl()}/admin/users`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ email, full_name: fullName, role, plan }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to create user");
      setResult(data);
      onCreated?.();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Create New User</DialogTitle>
          <DialogDescription>
            Create a new account with a temporary password.
          </DialogDescription>
        </DialogHeader>

        {result ? (
          <div className="space-y-4">
            <div className="rounded-lg bg-green-50 p-4 text-sm text-green-700">
              <p className="font-semibold">User created successfully!</p>
              <p className="mt-1">Email: {result.email}</p>
              <p className="mt-1">Role: {result.role}</p>
              <p className="mt-1">Plan: {result.plan}</p>
              <p className="mt-2 break-all">
                <span className="font-semibold">Temp Password:</span>{" "}
                {result.temp_password}
              </p>
            </div>
            <Button onClick={reset} className="w-full">
              Create Another
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium">Email</label>
              <Input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="user@example.com"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Full Name</label>
              <Input
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="John Doe"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Role</label>
                <select
                  value={role}
                  onChange={(e) => {
                    const newRole = e.target.value;
                    setRole(newRole);
                    if (newRole === "admin" || newRole === "dev") {
                      setPlan("premium");
                    }
                  }}
                  className="w-full rounded-md border px-3 py-2 text-sm"
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                  <option value="dev">Dev</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">Plan</label>
                <select
                  value={displayPlan}
                  onChange={(e) => setPlan(e.target.value)}
                  disabled={isAdminRole}
                  className="w-full rounded-md border px-3 py-2 text-sm disabled:opacity-50"
                >
                  <option value="free">Free</option>
                  <option value="premium">Premium</option>
                </select>
                {isAdminRole && (
                  <p className="text-xs text-muted-foreground mt-1">Admins are always premium.</p>
                )}
              </div>
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={handleClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? "Creating..." : "Create User"}
              </Button>
            </div>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
