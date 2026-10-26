// Debug probe: load /ecosim and dump every request/response + console errors.
import { newSession, login, hold } from "./common.mjs";

const s = await newSession("probe");
const { page } = s;
page.on("request", (r) => { if (!/localhost:5173|supabase/.test(r.url()) || /api|municipal|province/.test(r.url())) console.log("→", r.method(), r.url().slice(0, 140)); });
page.on("response", async (r) => { if (/api|municipal|province|supabase/.test(r.url())) console.log("←", r.status(), r.url().slice(0, 140)); });
page.on("console", (m) => { if (m.type() === "error") console.log("console:", m.text().slice(0, 200)); });
page.on("requestfailed", (r) => console.log("FAILED:", r.url().slice(0, 140), r.failure()?.errorText));

await login(page);
await page.goto("http://localhost:5173/ecosim", { waitUntil: "networkidle" });
await hold(page, 12000);
const search = page.getByPlaceholder(/calamba|santa rosa|municipality/i).first();
await search.click();
await hold(page, 4000);
console.log("option count:", await page.getByRole("option").count());
await s.finish();
