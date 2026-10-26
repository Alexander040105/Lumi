// Demo take recorder v3. One continuous take per chapter; session.mark(label)
// drops timestamped markers that assemble.mjs uses to cut footage into beats
// aligned with narration. Every take fires a black syncFlash near its start so
// the assembler can calibrate wall-clock markers onto the video timeline.
// Usage: node run.mjs <take-name|all>
import { newSession, login, hold, slowScroll, hideOverlays, hideCardByHeading, hideAiMentions, scrubLandingAi, syncFlash, CREDS, BASE } from "./common.mjs";

const segments = {
  // 01 — public landing page (welcome backdrop)
  async "seg01-landing"(s) {
    await s.page.goto(BASE + "/", { waitUntil: "networkidle" });
    await hold(s.page, 1500);
    await scrubLandingAi(s.page);
    await syncFlash(s);
    await hold(s.page, 2500);
    s.mark("hero");
    await slowScroll(s.page, 500);
    await hold(s.page, 2500);
    s.mark("features");
    await slowScroll(s.page, 700);
    await hold(s.page, 3000);
    s.mark("tools");
    await hold(s.page, 2000);
  },

  // 02 — account: signup form shown, then real login
  async "seg02-account"(s) {
    const { page } = s;
    await page.goto(BASE + "/login", { waitUntil: "networkidle" });
    await hold(page, 1200);
    await syncFlash(s);
    await hold(page, 1500);
    // show the sign-up form (don't submit — account already exists)
    const signUpTab = page.getByRole("button", { name: /sign ?up|create account|register/i }).first();
    if (await signUpTab.count()) { await signUpTab.click(); await hold(page, 2500); }
    s.mark("signup");
    await hold(page, 2500);
    const signInTab = page.getByRole("button", { name: /^sign ?in$/i }).first();
    if (await signInTab.count()) { await signInTab.click(); await hold(page, 1500); }
    s.mark("loginform");
    await page.getByPlaceholder(/email/i).first().fill(CREDS.email);
    await hold(page, 700);
    await page.getByPlaceholder(/password/i).first().fill(CREDS.password);
    await hold(page, 900);
    s.mark("submit");
    await page.locator("form").getByRole("button", { name: /^sign in$/i }).click();
    await page.waitForURL(/dashboard/, { timeout: 60000 });
    await page.waitForLoadState("networkidle").catch(() => {});
    await hold(page, 4000);
    s.mark("dashboard-arrive");
    await hold(page, 2000);
  },

  // 03 — dashboard tour
  async "seg03-dashboard"(s) {
    const { page } = s;
    await login(page, s);
    await page.goto(BASE + "/dashboard", { waitUntil: "networkidle" });
    await hold(page, 4000);
    s.mark("top");
    await slowScroll(page, 650);
    await hold(page, 2500);
    s.mark("quick-actions");
    for (const label of [/ecosim/i, /energy.?hub/i, /saved/i]) {
      const link = page.getByRole("link", { name: label }).first();
      if (await link.count()) { await link.hover().catch(() => {}); await hold(page, 1100); }
    }
    s.mark("nav-hover");
    await slowScroll(page, -700);
    await hold(page, 2500);
    s.mark("saved");
    await hold(page, 1500);
  },

  // 04 — EcoSim end-to-end (hero chapter): Calamba, Laguna
  async "seg04-ecosim"(s) {
    const { page } = s;
    await login(page, s);
    await page.goto(BASE + "/ecosim", { waitUntil: "networkidle" });
    await hold(page, 3000);
    await hideAiMentions(page); // sidebar "AI analysis" row is visible from step 1
    s.mark("wizard-start");

    // Step 1: municipality search — pick CALAMBA, LAGUNA (a second Calamba exists
    // in Misamis Occidental). Wait for options first: cold backend lists empty.
    const search = page.getByPlaceholder(/calamba|santa rosa|municipality/i).first();
    await search.click();
    await page.getByRole("option").first().waitFor({ timeout: 90000 });
    await hold(page, 800);
    await search.fill("Calamba");
    await hold(page, 2200);
    let opt = page.getByRole("option", { name: /calamba.*laguna|laguna.*calamba/i }).first();
    if (!(await opt.count())) {
      console.warn("  ! Calamba-Laguna option not matched — falling back to first Calamba");
      opt = page.getByRole("option", { name: /calamba/i }).last();
    }
    await opt.click({ timeout: 20000 });
    await hold(page, 1600);
    s.mark("location-selected");
    await page.getByRole("button", { name: /^next$/i }).click();
    await hold(page, 1400);
    await hideAiMentions(page);

    // Step 2: electricity use — rate required; "Use this rate" fills it
    s.mark("bill-details");
    await page.getByPlaceholder(/e\.?g\.?\s*300|kwh|consumption/i).first().fill("300");
    await hold(page, 800);
    const bill = page.getByPlaceholder(/e\.?g\.?\s*5000|bill/i).first();
    if (await bill.count()) { await bill.fill("5000"); await hold(page, 900); }
    const useRate = page.getByRole("button", { name: /use this rate/i });
    if (await useRate.count()) {
      await useRate.click();
      await hold(page, 1000);
    } else {
      await page.getByPlaceholder(/e\.?g\.?\s*13\.66|rate/i).first().fill("16.67");
      await hold(page, 800);
    }
    s.mark("rate-filled");
    await page.getByRole("button", { name: /^next$/i }).click();
    await hold(page, 1400);
    await hideAiMentions(page);

    // Step 3: savings goal — nudge slider
    s.mark("coverage");
    const slider = page.locator('[role="slider"]').first();
    if (await slider.count()) {
      await slider.focus();
      await page.keyboard.press("ArrowRight");
      await page.keyboard.press("ArrowRight");
      await hold(page, 900);
    }
    await page.getByRole("button", { name: /^next$/i }).click();
    await hold(page, 1400);

    // Step 4: decline the optional analysis add-on (block is hidden on camera),
    // then continue — keeps the saved record AI-free too.
    await page.evaluate(() => {
      const cb = document.getElementById("ecosim-include-ai");
      if (cb?.checked) cb.click();
    }).catch(() => {});
    await hideAiMentions(page);
    await page.getByRole("button", { name: /^next$/i }).click();
    await hold(page, 1600);
    await hideAiMentions(page); // step-5 review cell

    // Step 5: review → run → modal appears → View Results → results
    s.mark("review");
    await hold(page, 2500);
    await page.getByRole("button", { name: /run simulation/i }).click();
    s.mark("running");
    await page.getByText(/recommended/i).first().waitFor({ timeout: 120000 });
    await hold(page, 1200);
    s.mark("computed"); // ready-modal on screen
    const viewResults = page.getByRole("button", { name: /view results/i }).first();
    if (await viewResults.count()) { await viewResults.click(); await hold(page, 1200); }
    s.mark("results");
    await hold(page, 1500);
    await hideAiMentions(page); // belt-and-suspenders for the results card
    await slowScroll(page, 800);
    await hold(page, 2200);
    s.mark("breakdown");
    await slowScroll(page, 900);
    await hold(page, 2200);
    s.mark("summary");
    await hold(page, 1500);
    await hideOverlays(page);
    await slowScroll(page, 900);
    await hold(page, 2500);
  },

  // 05 — EnergyHub
  async "seg05-energyhub"(s) {
    const { page } = s;
    await login(page, s);
    await page.goto(BASE + "/energyhub", { waitUntil: "networkidle" });
    await hold(page, 4500);
    s.mark("overview");
    await slowScroll(page, 650);
    await hold(page, 2800);
    s.mark("trends");
    await slowScroll(page, 650);
    await hold(page, 2800);
    s.mark("forecast");
    await slowScroll(page, 650);
    await hold(page, 2800);
    s.mark("breakdown");
    await slowScroll(page, 650);
    await hold(page, 2800);
    s.mark("benchmark");
    await slowScroll(page, -2600);
    await hold(page, 2000);
  },

  // 06 — maps & geospatial (inside EnergyHub)
  async "seg06-maps"(s) {
    const { page } = s;
    await login(page, s);
    await page.goto(BASE + "/energyhub", { waitUntil: "networkidle" });
    await hold(page, 3000);
    const map = page.locator(".leaflet-container").first();
    if (await map.count()) {
      await map.scrollIntoViewIfNeeded();
      await hold(page, 1500);
      // collapse the "About …" explainer so the map canvas fills the viewport
      const hideBtn = page.locator('button[aria-label*="Hide"], button[title*="Hide"]').last();
      if (await hideBtn.count()) { await hideBtn.click().catch(() => {}); await hold(page, 1000); }
      await map.scrollIntoViewIfNeeded();
      await hold(page, 2500);
      s.mark("map-visible");
      const layerSel = page.locator("select").last();
      if (await layerSel.count()) {
        const opts = await layerSel.locator("option").allTextContents();
        if (opts.length > 1) { await layerSel.selectOption({ index: 1 }); await hold(page, 2200); }
      }
      s.mark("layer-switch");
      // zoom via Leaflet's own controls — wheel events scroll the page instead
      const zoomIn = page.locator(".leaflet-control-zoom-in").first();
      if (await zoomIn.count()) {
        await zoomIn.click(); await hold(page, 1600);
        await zoomIn.click(); await hold(page, 1600);
      }
      s.mark("zoom");
      const box = await map.boundingBox();
      if (box) {
        await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
        await page.mouse.down();
        await page.mouse.move(box.x + box.width * 0.4, box.y + box.height * 0.55, { steps: 15 });
        await page.mouse.up();
        await hold(page, 2200);
      }
      s.mark("pan");
    }
    await hold(page, 2000);
  },

  // 07 — saved simulations + security ("Open" is a link, not a button)
  async "seg07-saved"(s) {
    const { page } = s;
    await login(page, s);
    await page.goto(BASE + "/saved-simulations", { waitUntil: "networkidle" });
    await hideAiMentions(page); // observer stays armed for the loaded-sim render
    await hold(page, 3500);
    // trim duplicate saves from re-shot EcoSim takes — keep 1 Wind + the Hydro
    // card so the on-camera list looks curated (pre-marker footage is trimmed)
    page.on("dialog", (d) => d.accept());
    for (let i = 0; i < 8; i++) {
      const delBtns = page.getByRole("button", { name: /^delete$/i });
      const n = await delBtns.count();
      if (n <= 2) break; // 1 wind + 1 hydro left
      await delBtns.nth(0).click(); // confirm dialog auto-accepted
      await hold(page, 1200);
      await page.waitForLoadState("networkidle").catch(() => {});
    }
    await hold(page, 1500);
    s.mark("list");
    await hold(page, 2500); // dwell on the list so narration covers it before Open
    const openLink = page.getByRole("link", { name: /open|view/i }).first();
    if (await openLink.count()) {
      await openLink.click();
      s.mark("opening");
      await page.waitForLoadState("networkidle").catch(() => {});
      await hideAiMentions(page); // full reload would reset the observer
      await hold(page, 3000);
      await slowScroll(page, 1400);
      await hold(page, 1800);
      await hideAiMentions(page);
      s.mark("open-sim");
      await page.goBack().catch(() => {});
      await page.waitForLoadState("networkidle").catch(() => {});
      await hold(page, 1500);
    }
    await page.goto(BASE + "/settings/security", { waitUntil: "networkidle" });
    await hold(page, 3500);
    s.mark("security");
    await slowScroll(page, 400);
    await hold(page, 2500);
  },

  // 08 — recap: back to dashboard top
  async "seg08-recap"(s) {
    const { page } = s;
    await login(page, s);
    await page.goto(BASE + "/dashboard", { waitUntil: "networkidle" });
    await hold(page, 4000);
    s.mark("recap");
    await slowScroll(page, 300);
    await hold(page, 2500);
  },
};

const which = process.argv[2] || "all";
const names = which === "all" ? Object.keys(segments) : which.split(",");
for (const name of names) {
  const fn = segments[name];
  if (!fn) { console.error("unknown segment", name); process.exit(1); }
  console.log("=== recording", name);
  const session = await newSession(name);
  try {
    await fn(session);
  } catch (e) {
    console.error(name, "FAILED:", e.message);
    try { await session.page.screenshot({ path: `video/footage/${name}-error.png` }); } catch {}
  }
  await session.finish();
}
