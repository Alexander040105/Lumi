import { chromium } from "playwright";

const pages = ["/", "/about", "/login", "/ecosim", "/energyhub", "/dashboard", "/saved-simulations"];
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
const page = await ctx.newPage();
await page.route("**/api/v1/ecosim**", (r) =>
  r.request().method() === "POST"
    ? r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({
        recommendation: { recommended_source: "Solar", suitability_score: 78, estimated_generation_kwh: 240, estimated_savings_php: 2800 },
        monthly_bill: 5000, monthly_consumption_kwh: 350, user_consumption_kwh: 350, effective_consumption_kwh: 350,
        climate: { avg_allsky_sfc_sw_dwn: 4.9, avg_ws10m: 2.1, avg_precipitation: 4.2 },
        renewable_energy_results: { solar_output: { suitability_score: 78 }, wind_output: { suitability_score: 31 }, hydro_output: { hydro_score: 22 }, geothermal_output: { suitability_score: 40 } },
        ai_analysis: { status: "done", summary: "Solar is your strongest option." },
        sizing: { panels_needed: 7, actual_system_kwp: 3.85, bom_items: [], disclaimers: [], citations: [] },
        results: [], monthly_savings_php: 2800, payback_period_years: 6.3 }) })
    : r.continue());
await page.addInitScript(() => {
  localStorage.setItem("sb-husnkzlccdrjpwlqcfbt-auth-token", JSON.stringify({
    access_token: "t", refresh_token: "r", token_type: "bearer",
    expires_at: Math.floor(Date.now() / 1000) + 86400,
    user: { id: "u", email: "t@t.com", user_metadata: {} } }));
});

const report = {};
for (const route of pages) {
  const issues = await page.goto("http://localhost:5173" + route, { waitUntil: "domcontentloaded" })
    .then(() => page.waitForTimeout(2500))
    .then(() => page.evaluate(() => {
      const out = { hscroll: document.documentElement.scrollWidth > 390, small: [], offscreen: [] };
      document.querySelectorAll("button, a, input, select, textarea, [role=button], [role=tab], [role=switch], [aria-label]").forEach((el) => {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return;
        const label = (el.getAttribute("aria-label") || el.textContent || el.tagName).trim().slice(0, 40);
        if (r.width < 40 || r.height < 40) out.small.push(`${el.tagName} ${Math.round(r.width)}x${Math.round(r.height)} "${label}"`);
        if (r.right > 391) out.offscreen.push(`${el.tagName} right=${Math.round(r.right)} "${label}"`);
      });
      return out;
    }));
  report[route] = issues;
  await page.screenshot({ path: `mob_${route === "/" ? "home" : route.slice(1)}.png` });
}
// wizard step-by-step on /ecosim
await page.goto("http://localhost:5173/ecosim", { waitUntil: "domcontentloaded" });
await page.waitForTimeout(2500);
for (let s = 1; s <= 6; s++) {
  const issues = await page.evaluate(() => {
    const out = { hscroll: document.documentElement.scrollWidth > 390, small: [] };
    document.querySelectorAll("button, a, input, select, [role=button], [aria-label]").forEach((el) => {
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height) return;
      if (r.width < 40 || r.height < 40) out.small.push(`${el.tagName} ${Math.round(r.width)}x${Math.round(r.height)} "${(el.getAttribute("aria-label") || el.textContent || "").trim().slice(0, 40)}"`);
    });
    return out;
  });
  report[`wizard_step${s}`] = issues;
  await page.screenshot({ path: `mob_wiz${s}.png` });
  if (s < 6) {
    if (s === 1) { await page.locator("#ecosim-location-search").fill("Lucena"); await page.waitForTimeout(900); await page.locator("button, [role=option], li").filter({ hasText: /Lucena/i }).first().click().catch(() => {}); }
    if (s === 2) { await page.locator("#ecosim-consumption").fill("350"); await page.locator("#ecosim-rate").fill("14.29"); await page.locator("#ecosim-bill").fill("5000"); }
    await page.getByRole("button", { name: /^next/i }).click({ timeout: 4000 }).catch(() => {});
    await page.waitForTimeout(700);
  }
}
await page.getByRole("button", { name: /run|analyze|simulate/i }).last().click().catch(() => {});
await page.waitForTimeout(3500);
await page.keyboard.press("Escape");
await page.waitForTimeout(500);
report.results = await page.evaluate(() => {
  const out = { hscroll: document.documentElement.scrollWidth > 390, small: [] };
  document.querySelectorAll("button, a, input, [role=button], [aria-label]").forEach((el) => {
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) return;
    if (r.width < 40 || r.height < 40) out.small.push(`${el.tagName} ${Math.round(r.width)}x${Math.round(r.height)} "${(el.getAttribute("aria-label") || el.textContent || "").trim().slice(0, 40)}"`);
  });
  return out;
});
await page.screenshot({ path: "mob_results.png", fullPage: false });
console.log(JSON.stringify(report, null, 1));
await browser.close();
