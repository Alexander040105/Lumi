import { chromium } from "playwright";
const payload = {
  recommendation: { recommended_source: "Solar", suitability_score: 78, estimated_generation_kwh: 240, estimated_savings_php: 2800, explanation: "Solar is your strongest source here." },
  monthly_bill: 5000, monthly_consumption_kwh: 350, user_consumption_kwh: 350, effective_consumption_kwh: 350,
  climate: { avg_allsky_sfc_sw_dwn: 4.9, avg_ws10m: 2.1, avg_precipitation: 4.2 },
  renewable_energy_results: { solar_output: { suitability_score: 78, estimated_generation_kwh: 240 }, wind_output: { suitability_score: 31 }, hydro_output: { hydro_score: 22 }, geothermal_output: { suitability_score: 40 } },
  ai_analysis: { status: "done", summary: "## Observation\nLucena City receives solid sunlight and low wind.\n\n## Interpretation\n**Solar** is your strongest option." },
  sizing: { panels_needed: 7, actual_system_kwp: 3.85, bom_items: [], disclaimers: [], citations: [] },
  results: [], monthly_savings_php: 2800, payback_period_years: 6.3,
};
const browser = await chromium.launch();
const page = await (await browser.newContext({ viewport: { width: 1280, height: 900 } })).newPage();
await page.route("**/api/v1/ecosim**", (r) =>
  r.request().method() === "POST"
    ? r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(payload) })
    : r.continue());
await page.addInitScript(() => {
  localStorage.setItem("sb-husnkzlccdrjpwlqcfbt-auth-token", JSON.stringify({
    access_token: "t", refresh_token: "r", token_type: "bearer",
    expires_at: Math.floor(Date.now() / 1000) + 86400,
    user: { id: "u", email: "t@t.com", user_metadata: {} },
  }));
});
await page.goto("http://localhost:5173/ecosim", { waitUntil: "domcontentloaded" });
await page.waitForTimeout(3000);
await page.locator("#ecosim-location-search").fill("Lucena");
await page.waitForTimeout(900);
await page.locator("button, [role=option], li").filter({ hasText: /Lucena/i }).first().click({ timeout: 5000 }).catch(() => {});
const next = () => page.getByRole("button", { name: /^next/i }).click({ timeout: 4000 }).catch(() => {});
await next();
await page.locator("#ecosim-consumption").fill("350");
await page.locator("#ecosim-rate").fill("14.29");
await page.locator("#ecosim-bill").fill("5000");
await next(); await next(); await next(); await next();
await page.waitForTimeout(400);
await page.getByRole("button", { name: /run|analyze|simulate/i }).last().click({ timeout: 5000 }).catch(() => {});
await page.waitForTimeout(3500);
// spy on speechSynthesis
await page.evaluate(() => {
  window.__spoken = [];
  const s = window.speechSynthesis;
  const orig = s.speak.bind(s);
  s.speak = (u) => { window.__spoken.push({ lang: u.lang, chars: u.text.length }); return orig(u); };
});
// count read-aloud buttons on the results page
await page.keyboard.press("Escape"); await page.waitForTimeout(500);
await page.getByRole("button", { name: /view results/i }).last().click().catch(() => {});
await page.waitForTimeout(400);
const raButtons = page.locator("main button[aria-pressed]");
console.log("read-aloud buttons:", await raButtons.count());
await page.locator("text=AI Analysis").first().scrollIntoViewIfNeeded({ timeout: 8000 }).catch(() => {});
await page.waitForTimeout(600);
await page.screenshot({ path: "ra_results.png" });
// click the first read-aloud button (AI Analysis card)
const first = await raButtons.first().elementHandle();
console.log("label before:", await first.getAttribute("aria-label"));
await first.click();
await page.waitForTimeout(600);
console.log("aria-pressed after click:", await first.getAttribute("aria-pressed"));
console.log("label after:", await first.getAttribute("aria-label"));
console.log("spoken:", JSON.stringify(await page.evaluate(() => window.__spoken)));
await first.click(); // stop
await page.waitForTimeout(300);
console.log("after stop:", await first.getAttribute("aria-pressed"));
// open a per-source explanation modal and verify its button
const triggers = page.getByRole("button", { name: /why this estimate/i });
console.log("modal triggers:", await triggers.count());
await triggers.first().scrollIntoViewIfNeeded().catch(() => {});
await triggers.first().click({ timeout: 5000 }).catch((e) => console.log("trigger click failed:", e.message.split("\n")[0]));
await page.waitForTimeout(800);
console.log("dialogs open:", await page.locator('[role="dialog"]').count());
const dlgBtn = page.locator('[role="dialog"] button[aria-pressed]');
console.log("buttons in dialog:", await dlgBtn.count());
if (await dlgBtn.count()) {
  const h = await dlgBtn.first().elementHandle();
  await h.click();
  await page.waitForTimeout(500);
  console.log("dialog speak:", JSON.stringify(await page.evaluate(() => window.__spoken)), "pressed:", await h.getAttribute("aria-pressed"));
}
await page.screenshot({ path: "ra_dialog.png" });
console.log("done");
await browser.close();
