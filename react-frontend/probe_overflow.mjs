import { chromium } from "playwright";
const browser = await chromium.launch();
const page = await (await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true })).newPage();
await page.addInitScript(() => {
  localStorage.setItem("sb-husnkzlccdrjpwlqcfbt-auth-token", JSON.stringify({
    access_token: "t", refresh_token: "r", token_type: "bearer",
    expires_at: Math.floor(Date.now() / 1000) + 86400,
    user: { id: "u", email: "t@t.com", user_metadata: {} } }));
});
for (const route of ["/ecosim", "/energyhub"]) {
  await page.goto("http://localhost:5173" + route, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(3000);
  const res = await page.evaluate(() => {
    const out = { sw: document.documentElement.scrollWidth, offenders: [] };
    document.querySelectorAll("*").forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.right > 391 && r.width < 390) {
        const cls = (el.className && el.className.baseVal === undefined ? el.className : "").toString().slice(0, 70);
        out.offenders.push(`${el.tagName} right=${Math.round(r.right)} w=${Math.round(r.width)} "${cls}"`);
      }
    });
    return out;
  });
  console.log(route, "scrollWidth=", res.sw, "->", JSON.stringify(res.offenders.slice(0, 15), null, 1));
}
await browser.close();
