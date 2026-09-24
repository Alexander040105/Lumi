# PSC XI Submission Checklist — LUMI

> Verified against public PSC XI sources on 2026-09-24. Where a source could not be reached,
> items are marked `[UNVERIFIED]` — confirm on the official site before submitting.

## Eligibility

| Requirement | Status | Evidence |
|---|---|---|
| SHS / college / tech-voc student team | ✅ Fits — college track | Team is BSCS-DS students, University of Perpetual Help System DALTA – Molino (README) |
| ICT-enabled solution (software, AI, IoT, Web3, blockchain, MR) | ✅ Fits — software + AI | Deployed web app; Gemini/Groq + RAG; ARIMA forecasting |
| Stage: ideation → prototype | ✅ Exceeds — working deployed product | Live Vercel deployment, verified 200s on prod API |
| Team size / roles (3–4 members + leader; prior cycles allowed 1 mentor, same school) | ⚠️ `[TEAM INPUT: confirm current-year team rules]` | Prior-cycle flipbook; verify on the application form |
| School clearance | ⚠️ `[TEAM INPUT: request from school registrar]` | Required in prior cycles |
| Regional channel | Region IV-A CALABARZON (Cavite) | Form: `https://tinyurl.com/DICT-PSC11-Region4A-AppForm` |

## Deadlines & channels

- **Original application window:** Aug 27 – Sep 20, 2026 (DICT/IIDB announcements).
- **Extension:** team-reported extended deadline — `[UNVERIFIED]`; confirm the actual close date on
  the official site `https://iidb2026.my.canva.site/psc-xi-website` (JS-rendered; open in browser)
  and/or the Region IV-A form (a closed form shows "no longer accepting responses").
- **Sources:** DICT LinkedIn announcement; Amianan Ventures PSC XI guide (regional form list);
  StartupLab CALABARZON post; Kabayan Daily PSC 2026 launch article.

## Required submissions tracker

| Item | Source | Status |
|---|---|---|
| Application form (Region IV-A) | tinyurl link above | ☐ `[TEAM INPUT]` |
| Concept note (this template's 10 sections) | `02-concept-note-draft.md` | 🟡 Drafted — resolve `[TEAM INPUT]` markers |
| 3–5 min video pitch | Guidelines below | ☐ Not started |
| Pitch deck | Prior cycles required | ☐ Not started |
| Business Model Canvas + Validation Board (PDF) | Prior cycles required | ☐ Not started |
| School clearance | Registrar | ☐ `[TEAM INPUT]` |
| Team member list + roles | Application form | ☐ `[TEAM INPUT]` |

## Video pitch outline (3–5 min, per published guidelines)

Required content per the PSC video-pitch guidelines: problem, target market, business model,
progress/traction, use of funds — plus founder introductions and rationale. Natural human voices
from founders.

Suggested arc mapped to LUMI's strongest demonstrable assets:

1. **Hook (0:00–0:30)** — the bill problem in one line + "can solar actually help *my* house in
   *my* town?"
2. **Problem (0:30–1:00)** — high PH electricity costs; generic tools can't answer
   municipality-level; homeowners fly blind.
3. **Solution demo (1:00–2:30)** — screen-record the live app: municipality pick (Quezon City),
   bill entry via the bill guide, results: best source + savings + DOE-verified installers + PDF.
   **Requires W1 (public access) or a logged-in demo account — record after Slice 1–2 land.**
4. **Why it's real (2:30–3:15)** — NASA POWER/DOE/Atlas/ERA5/SRTM data fusion; 1,600
   municipalities; bilingual; security-audited; 192 automated tests.
5. **Business model + traction (3:15–4:00)** — freemium tiers (already implemented), B2G/LGU
   analytics, installer referrals; traction = deployed product + `[TEAM INPUT: user-testing
   numbers once real-user testing runs]`.
6. **Ask (4:00–4:30)** — funding goes to users/evidence (cloud, LLM credits, user-testing
   incentives), not engineering — the engineering is done.
7. **Close (4:30–5:00)** — founders on camera, school + program, vision: municipal energy
   intelligence for every Filipino household.

## Consolidated `[TEAM INPUT]` list (from `02-concept-note-draft.md`)

- Team name, member names/roles, mentor, school clearance
- Current PH residential ₱/kWh figure + citation (ERC/DOE)
- Market sizing: household counts, net-metering growth figures (cite PSA/ERC/DOE)
- Business-model choice + pricing point for premium
- Financial requirement table (real numbers)
- User-testing targets + any traction evidence once testing runs
- Confirmed extended deadline + final submission channel

## Pre-demo technical checklist (from `01-evaluation-report.md`)

- [ ] W1 shipped — `/ecosim` reachable logged-out; friendly quota wall; quota ≥3/day
- [ ] W2 shipped — hero CTA → EcoSim; verifiable stats only
- [ ] W3 decided + shipped — financial card visible (or promise de-scoped)
- [ ] W6 shipped — `ENVIRONMENT=production`, localhost CORS rejected on prod
- [ ] W7 — error tracking live before judges touch it
- [ ] Supabase custom SMTP verified (password resets/confirmations at volume)
- [ ] Rehearse demo on a phone over mobile data (target persona's reality)
- [ ] Backup plan: pre-recorded demo video + screenshots if venue Wi-Fi fails
