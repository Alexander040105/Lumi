// Creates a throwaway LUMI demo account via the Supabase Admin API and writes
// video/tools/creds.json for the recorder. Needs the service-role key in the
// ROOT .env (SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY). Never commit creds.json.
// Usage: node video/tools/make-user.mjs [--admin]
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const envFile = fs.readFileSync(path.join(ROOT, ".env"), "utf8");
const env = Object.fromEntries(
  envFile.split("\n").filter((l) => /^\w+=/.test(l)).map((l) => {
    const i = l.indexOf("=");
    return [l.slice(0, i).trim(), l.slice(i + 1).trim().replace(/^"|"$/g, "")];
  })
);
const SUPA = env.SUPABASE_URL || env.VITE_SUPABASE_URL;
const KEY = env.SUPABASE_SERVICE_ROLE_KEY;
if (!SUPA || !KEY) throw new Error("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY missing in root .env");

const email = `lumi-video-demo-${Date.now()}@example.com`;
const password = `Demo!${Math.random().toString(36).slice(2, 10)}${Date.now() % 1000}`;

const res = await fetch(`${SUPA}/auth/v1/admin/users`, {
  method: "POST",
  headers: { apikey: KEY, Authorization: `Bearer ${KEY}`, "Content-Type": "application/json" },
  body: JSON.stringify({ email, password, email_confirm: true }),
});
const user = await res.json();
if (!res.ok) throw new Error(`create user failed: ${res.status} ${JSON.stringify(user)}`);
console.log("user:", user.id, email);

if (process.argv.includes("--admin")) {
  // Role source is public.user_roles (backend's /protected/me reads it)
  const r = await fetch(`${SUPA}/rest/v1/user_roles?on_conflict=user_id`, {
    method: "POST",
    headers: {
      apikey: KEY, Authorization: `Bearer ${KEY}`, "Content-Type": "application/json",
      Prefer: "resolution=merge-duplicates,return=minimal",
    },
    body: JSON.stringify({ user_id: user.id, role: "admin" }),
  });
  console.log("admin role:", r.ok ? "granted" : `FAILED ${r.status} ${await r.text()}`);
}

fs.writeFileSync(
  path.join(ROOT, "video", "tools", "creds.json"),
  JSON.stringify({ id: user.id, email, password }, null, 2)
);
console.log("wrote video/tools/creds.json (gitignored)");
