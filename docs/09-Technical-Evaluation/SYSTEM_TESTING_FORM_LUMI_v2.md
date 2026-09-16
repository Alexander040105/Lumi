# **TECHNICAL TESTING FORM — Manual Evaluation Edition (v2)**

**Title:** LUMI — Data-Driven Environmental Intelligence System **Group Name:** \_________________\_ **Technical Evaluators (IT Experts):** \____________________________________\_ **Form Version:** 2.0 — Manual evaluation edition (2026-09-16)

> **How to use this form.** Everything in this form is done by a person using the live LUMI web app in an ordinary browser — you open pages, click, type, and watch what appears on screen. No tools, code, or technical setup are required beyond a browser, an internet connection, and the test accounts listed in §6. Pre-filled cells contain facts verified against the system — leave them unless the app has visibly changed. Blank cells (`____` / Pass-Fail checkboxes) are yours to complete during the session. When a step says "open the address," type the given page address after the Application URL from §1 (for example, if the app is at `https://lumi-app.example.com`, the address `/dashboard` means `https://lumi-app.example.com/dashboard`).

---

## **1. Document Information**

| Item | Details |
| --- | --- |
| **Project/System Name** | LUMI |
| **Project Title** | LUMI — Data-Driven Environmental Intelligence System |
| **Version** | 0.1.0 |
| **Application URL** | https://\___________________\_ |
| **Testing Date** | \_____\_ |
| **Testing Environment** | Evaluator's own device(s) and browser(s) — record in §6 |
| **Tested By** | \_____\_ |
| **Developer/Team** | LUMI Development Team |
| **Test Report Version** | \_____\_ |
| **Status** | ☐ Draft ☐ Final |

---

## **2. Executive Summary**

### **2.1 Purpose of Testing** *(pre-filled)*

This form records the procedures, observations, identified defects, corrective actions, and overall assessment of LUMI as experienced by a person using the deployed application — covering functional, performance, security, usability, compatibility, and reliability requirements.

### **2.2 Testing Objectives** *(pre-filled)*

1. Verify all visible functions work as described. 2. Identify defects a user would notice. 3. Judge responsiveness by direct observation and a stopwatch. 4. Verify the app works across browsers and devices. 5. Assess access control as seen by guest, user, and admin accounts. 6. Verify that saved data persists and stays private to its owner. 7. Evaluate against ISO/IEC 25010. 8. Confirm previously fixed defects stay fixed. 9. Determine deployment readiness from a user's point of view.

### **2.3 Result Summary** *(fill after execution)*

| Activity | Result |
| --- | --- |
| Guest walkthrough (public pages, login walls) | \___\_ |
| Sign-up, login, logout, password reset | \___\_ |
| EcoSim end-to-end (wizard → results → AI → save) | \___\_ |
| EnergyHub dashboards, forecast, and map | \___\_ |
| Saved simulations | \___\_ |
| Profile and security settings | \___\_ |
| Admin console (admin account) | \___\_ |
| Input validation checks | \___\_ |
| Security checks (observable behavior) | \___\_ |
| Data persistence and privacy checks | \___\_ |
| Performance observation (stopwatch) | \___\_ |
| Browser and device matrix | \___\_ |
| Usability tasks + SUS questionnaire | \___\_ |
| Regression retest of old defects | \___\_ |

---

## **3. System Overview**

### **3.1 System Description** *(pre-filled)*

**System Name:** LUMI

**Description:** A web system with four working parts. **EcoSim** estimates which renewable energy source fits a household in any Philippine municipality, with costs and savings. **EnergyHub** is a national energy dashboard with historical statistics, forecasts, and province-level renewable-potential maps. An **AI assistant** writes plain-language explanations of the results. Registered users can save simulations and manage a profile; administrators get a management console for users, analytics, and logs.

### **3.2 Intended Users** *(pre-filled)*

| User Type | What they can do | How they get in |
| --- | --- | --- |
| Administrator | Everything a user can do, plus manage users, view analytics, edit configuration, inspect usage and logs | Admin account — an "Admin Portal" entry appears in the account menu |
| Registered user | EcoSim simulations, EnergyHub, saved simulations, profile and security settings, MFA | Email/password or Google sign-in |
| Guest | Home, About, Terms, Privacy pages only — every feature page asks for login | No account |

### **3.3 Pages a tester can reach** *(pre-filled)*

| No. | Page (address) | What it is |
| --- | --- | --- |
| 1 | Home (`/`) | Landing page |
| 2 | About (`/about`), Terms (`/terms`), Privacy (`/privacy`) | Public information pages |
| 3 | Login (`/login`), Reset password (`/reset-password`) | Sign-in, sign-up, Google sign-in, password reset, MFA code step |
| 4 | Dashboard (`/dashboard`) | Profile view/edit, avatar, saved locations, saved simulations; admins also see a forecast panel |
| 5 | EcoSim (`/ecosim`) | Simulation wizard, results, AI analysis, save-simulation dialog, PDF download |
| 6 | EnergyHub (`/energyhub`) | National overview, trends, forecast chart, choropleth map, source breakdowns, provincial demand, AI insight |
| 7 | Saved Simulations (`/saved-simulations`) | The logged-in user's saved simulation list |
| 8 | MFA setup (`/mfa`) | Authenticator-app enrollment |
| 9 | Security settings (`/settings/security`) | Change email, change password, delete account |
| 10 | Admin console (`/admin` + Users, Analytics, Config, Usage, Logs) | Administrator-only pages |
| 11 | Not Found (any invalid address) | Friendly "page not found" screen |

---

## **4. Testing Scope**

### **4.1 In-Scope** *(pre-filled)*

Every screen, feature, and flow reachable through the app's interface on the deployed site: public pages, sign-up/login/logout, EcoSim, EnergyHub, saved simulations, profile and security settings, the admin console, input handling, on-screen security behavior, data persistence, responsiveness, multiple browsers and devices, and a moderated usability session.

### **4.2 Boundary of this form** *(pre-filled)*

Checks are limited to what a person can see and operate in the browser. If a behavior cannot be observed on screen, it is not part of this evaluation.

---

## **5. Testing Methodology**

Process: **Requirements → Test Planning → Walkthrough Execution → Observation Recording → Defect Identification → Correction → Retesting → Final Evaluation**

| Testing Type | What the evaluator does | Performed? |
| --- | --- | --- |
| Functional walkthrough | Follow each §8 scenario and compare what appears | ☐ |
| Exploratory clicking | Wander the app freely and note anything broken or confusing | ☐ |
| Negative-input testing | Type bad, weird, or hostile-looking input into forms (§9) | ☐ |
| Permission checks | Try the same pages as guest, user, and admin (§13) | ☐ |
| Persistence checks | Save data, log out, log back in, and look for it (§10) | ☐ |
| Timed observation | Stopwatch the actions in §12 | ☐ |
| Compatibility pass | Repeat key flows on each browser/device in §14 | ☐ |
| Usability / UAT | Run the moderated tasks and SUS questionnaire in §15 | ☐ |
| Regression | Repeat the previously-fixed-defect checks in §19 | ☐ |

---

## **6. Test Environment**

### **6.1 Evaluator equipment** *(fill per evaluator)*

| Item | Details |
| --- | --- |
| Browser(s) and version(s) | \_____\_ |
| Screen size / resolution | \_____\_ |
| Computer (OS, rough specs) | \_____\_ |
| Phone or tablet used (if any) | \_____\_ |
| Internet connection | \_____\_ |

### **6.2 Pre-session checklist** *(the team prepares these before evaluators arrive)*

- ☐ Application URL confirmed working: the site loads and shows the LUMI home page
- ☐ Test account 1 — registered user (email \_____\_ / password supplied privately)
- ☐ Test account 2 — second registered user, for the privacy check in §10
- ☐ Admin account (if the admin console is in scope): email \_____\_
- ☐ MFA-enrolled account (optional, for the MFA code step)
- ☐ At least one phone or tablet available for the compatibility pass
- ☐ A stopwatch or phone timer for §12
- ☐ A way to take screenshots for evidence (Appendix B)

---

## **7. Test Data** *(pre-filled — what you should expect to see)*

| What you look at | What healthy data looks like |
| --- | --- |
| EcoSim location picker | A long, searchable list of real Philippine municipalities and provinces — e.g., typing "Tagaytay" finds Tagaytay City |
| EcoSim defaults | Monthly consumption and bill fields arrive pre-filled with reasonable numbers |
| EnergyHub overview | Real national statistics (consumption, generation, demand) with recent years shown |
| EnergyHub forecast | A chart projecting roughly to 2030, with an upper/lower range around the line |
| EnergyHub map | A Philippine map colored by province; a selector switches between renewable/solar/wind/hydro/geothermal views |
| Provider recommendations (inside EcoSim results) | Real installer/provider names relevant to the chosen location |
| Saved simulations (new account) | Empty list until the user saves one |

**Test accounts used this session:**

| Role | Email/username | Notes |
| --- | --- | --- |
| Registered user 1 | \_____\_ | \_____\_ |
| Registered user 2 | \_____\_ | \_____\_ |
| Administrator | \_____\_ | \_____\_ |
| MFA-enrolled user (optional) | \_____\_ | \_____\_ |

---

## **8. Functional Test Cases**

*For each row: follow the steps, write what actually happened, and mark Pass or Fail. "The app" means the Application URL in §1.*

### **8.1 Public pages and navigation**

| Test ID | Area | Steps | Expected on screen | Actual | Status |
| --- | --- | --- | --- | --- | --- |
| FT-001 | Home | Open the app address | LUMI home page loads fully — logo, navigation, page content | \___\_ | ☐P ☐F |
| FT-002 | About | Click "About" in the navigation | About page with readable content | \___\_ | ☐P ☐F |
| FT-003 | Terms/Privacy | Open `/terms`, then `/privacy` | Both legal pages render readable text | \___\_ | ☐P ☐F |
| FT-004 | Navigation | Click every link in the top navigation while logged out | Each leads somewhere sensible; EcoSim and EnergyHub ask for login | \___\_ | ☐P ☐F |
| FT-005 | Theme | Click the theme toggle | The app visibly switches light/dark | \___\_ | ☐P ☐F |
| FT-006 | Language | Click the language toggle and switch language | On-screen text changes language | \___\_ | ☐P ☐F |
| FT-007 | Bad address | Open `/this-page-does-not-exist` | A friendly "not found" page, not a blank screen or raw error | \___\_ | ☐P ☐F |

### **8.2 Accounts: sign-up, login, logout**

| Test ID | Area | Steps | Expected on screen | Actual | Status |
| --- | --- | --- | --- | --- | --- |
| AC-001 | Sign up | On `/login`, choose Sign Up, enter a new email + password + confirm, submit | Confirmation message appears (check-email notice or immediate sign-in) | \___\_ | ☐P ☐F |
| AC-002 | Sign-up guard | Sign Up with two different passwords in the two boxes | A polite "passwords do not match" message; nothing crashes | \___\_ | ☐P ☐F |
| AC-003 | Bad email | Sign Up with `not-an-email` | The form refuses with a clear message | \___\_ | ☐P ☐F |
| AC-004 | Login | Sign in as registered user 1 | You land inside the app (dashboard or the page you asked for); the account menu shows your name/email | \___\_ | ☐P ☐F |
| AC-005 | Wrong password | Sign in with the right email, wrong password | A clear "invalid credentials"-style message; no access granted | \___\_ | ☐P ☐F |
| AC-006 | Google sign-in | On `/login`, click "Continue with Google" | A real Google sign-in prompt opens (cancel it after confirming it appears) | \___\_ | ☐P ☐F |
| AC-007 | Password reset | Choose "Forgot password," enter the account email | A "reset email sent" confirmation appears (verify the inbox if accessible) | \___\_ | ☐P ☐F |
| AC-008 | MFA *(optional — needs the MFA account)* | Sign in as the MFA-enrolled user | After the password, a code-entry step appears; a correct authenticator code lets you in, a wrong one is refused | \___\_ | ☐P ☐F |
| AC-009 | Logout | From the account menu, choose Logout | You return to a signed-out state; protected pages no longer open | \___\_ | ☐P ☐F |

### **8.3 EcoSim — the simulation flow**

| Test ID | Area | Steps | Expected on screen | Actual | Status |
| --- | --- | --- | --- | --- | --- |
| FT-010 | Wizard loads | Logged in, open EcoSim | The wizard appears: location picker (municipality/province mode), consumption, bill, and options | \___\_ | ☐P ☐F |
| FT-011 | Location list | Open the municipality picker and type "Tagaytay" | Tagaytay City is found and selectable from a long real list | \___\_ | ☐P ☐F |
| FT-012 | Province mode | Switch to province mode and open the picker | Real provinces list and select | \___\_ | ☐P ☐F |
| FT-013 | Run simulation | Pick a municipality, leave defaults (or enter bill PHP 2,500), run | Results appear: recommended source(s), estimated output, costs/savings, figures are plausible | \___\_ | ☐P ☐F |
| FT-014 | AI analysis | With AI enabled, run or view the analysis panel | Readable plain-language analysis appears; a waiting/progress indicator during slow answers is normal | \___\_ | ☐P ☐F |
| FT-015 | Save simulation | After results, choose Save and give it a label | A save confirmation appears | \___\_ | ☐P ☐F |
| FT-016 | PDF download | Download the results PDF if the button is offered | A PDF downloads and opens showing the same results | \___\_ | ☐P ☐F |

### **8.4 EnergyHub — the national dashboard**

| Test ID | Area | Steps | Expected on screen | Actual | Status |
| --- | --- | --- | --- | --- | --- |
| FT-017 | Overview | Logged in, open EnergyHub | National overview cards/figures load with real numbers | \___\_ | ☐P ☐F |
| FT-018 | Trends | Scroll to the trends/history section | Historical charts render (years \~2003 to present) | \___\_ | ☐P ☐F |
| FT-019 | Forecast | Find the forecast chart | Projection to roughly 2030, including a visible upper/lower range | \___\_ | ☐P ☐F |
| FT-020 | Map | View the choropleth map; switch the metric selector through renewable/solar/wind/hydro/geothermal | The Philippine map recolors for each metric; a legend explains the colors | \___\_ | ☐P ☐F |
| FT-021 | Map level | Switch the map level (province ↔ municipality if offered) | The map redraws at the new level | \___\_ | ☐P ☐F |
| FT-022 | Breakdowns | View source/grid breakdown sections | Charts render with plausible shares | \___\_ | ☐P ☐F |
| FT-023 | Provincial demand | View the provincial demand section | Provincial figures/charts load | \___\_ | ☐P ☐F |
| FT-024 | AI insight | Open the AI insight panel | Either a readable insight appears, or a polite message that the service is temporarily unavailable (quota) — both are acceptable behavior | \___\_ | ☐P ☐F |
| FT-025 | Chart explanations | Where an "explain" button exists on charts, use it | A readable explanation appears | \___\_ | ☐P ☐F |

### **8.5 Saved data and account pages**

| Test ID | Area | Steps | Expected on screen | Actual | Status |
| --- | --- | --- | --- | --- | --- |
| FT-026 | Saved list | Open Saved Simulations after saving in FT-015 | The saved simulation is listed with its label and municipality | \___\_ | ☐P ☐F |
| FT-027 | Delete saved | Delete the test simulation and confirm | It disappears from the list | \___\_ | ☐P ☐F |
| FT-028 | Dashboard | Open Dashboard | Profile card, saved locations/simulations sections render | \___\_ | ☐P ☐F |
| FT-029 | Profile edit | Edit full name / organization / location and save | A confirmation appears and the new values display | \___\_ | ☐P ☐F |
| FT-030 | Avatar | Upload a profile picture if offered | The avatar updates on screen | \___\_ | ☐P ☐F |
| FT-031 | Security page | Open Settings → Security | Change-email, change-password, and delete-account sections render | \___\_ | ☐P ☐F |
| FT-032 | Change password | Change password (record the new one), log out, log in with it | The new password works; the old one no longer does | \___\_ | ☐P ☐F |
| FT-033 | MFA page | Open the MFA setup page (`/mfa`) | Authenticator enrollment instructions/QR appear | \___\_ | ☐P ☐F |

### **8.6 Admin console** *(admin account only — skip the whole block if unavailable)*

| Test ID | Area | Steps | Expected on screen | Actual | Status |
| --- | --- | --- | --- | --- | --- |
| AD-001 | Admin menu | Sign in as admin; open the account menu | An "Admin Portal" entry exists (absent for normal users) | \___\_ | ☐P ☐F |
| AD-002 | Admin home | Open `/admin` | The admin dashboard renders | \___\_ | ☐P ☐F |
| AD-003 | Users | Open Users | A real user list appears; opening a user shows detail/actions | \___\_ | ☐P ☐F |
| AD-004 | Create user | Create a test user via the Users page form | The new user appears in the list (delete/flag it after if possible) | \___\_ | ☐P ☐F |
| AD-005 | User actions | Try a non-destructive action (open detail drawer; view simulations/reports tabs) | Details display correctly | \___\_ | ☐P ☐F |
| AD-006 | Analytics | Open Analytics | Charts/figures render | \___\_ | ☐P ☐F |
| AD-007 | Config | Open Config | Configuration page renders; **do not save changes** | \___\_ | ☐P ☐F |
| AD-008 | Usage | Open Usage | Usage statistics render | \___\_ | ☐P ☐F |
| AD-009 | Logs | Open Logs | Log entries render | \___\_ | ☐P ☐F |
| AD-010 | Forecast panel | Open Dashboard as admin | The forecast-runner panel is visible (admin-only feature) | \___\_ | ☐P ☐F |

**Functional summary:** total \___\_ · passed \___\_ · failed \___\_ · notes: \_____\_

---

## **9. Input Validation Testing**

*Type each bad input by hand into the named field. Expected everywhere: a polite refusal (inline message or toast), the app keeps working, and nothing strange is rendered or stored.*

| Test ID | Field | What you type | Expected on screen | Actual | Status |
| --- | --- | --- | --- | --- | --- |
| IV-001 | EcoSim — monthly bill | letters, e.g. `abc` | Refused or ignored — never a broken result | \___\_ | ☐P ☐F |
| IV-002 | EcoSim — consumption | a huge number, e.g. `99999999999` | Rejected politely or handled sensibly | \___\_ | ☐P ☐F |
| IV-003 | EcoSim — consumption | a negative number, e.g. `-50` | Rejected politely | \___\_ | ☐P ☐F |
| IV-004 | EcoSim — run with nothing chosen | leave location empty and run | A clear "choose a location"-style message | \___\_ | ☐P ☐F |
| IV-005 | Any search/filter box | `' OR '1'='1` | Treated as plain text — no error page, no odd data shown | \___\_ | ☐P ☐F |
| IV-006 | Any text field | `<script>alert(1)</script>` | Displayed as harmless text or refused; no popup runs | \___\_ | ☐P ☐F |
| IV-007 | Login — email | `not-an-email` | Format refused before submit | \___\_ | ☐P ☐F |
| IV-008 | Sign-up — password | a very short password, e.g. `123` | A minimum-length message | \___\_ | ☐P ☐F |
| IV-009 | Profile — name fields | extremely long text (paste \~500 characters) | Accepted-and-truncated or politely refused — layout never breaks | \___\_ | ☐P ☐F |
| IV-010 | Security — change password | new password `abc` (under 6 chars) | "At least 6 characters" message | \___\_ | ☐P ☐F |
| IV-011 | Security — wrong current password | a wrong current password with a valid new one | Refused with a clear message; password unchanged | \___\_ | ☐P ☐F |
| IV-012 | Empty form submit | submit any required form empty | Required-field messages; nothing submits | \___\_ | ☐P ☐F |

---

## **10. Data Persistence and Privacy Testing**

| Test ID | Check | Steps | Expected on screen | Actual | Status |
| --- | --- | --- | --- | --- | --- |
| DP-001 | Simulation persists | As user 1, save a simulation; log out; log back in; open Saved Simulations | The simulation is still there | \___\_ | ☐P ☐F |
| DP-002 | Profile persists | Edit profile details; log out and back in | The edits are still shown | \___\_ | ☐P ☐F |
| DP-003 | Data isolation — saved sims | Note user 1's saved simulation labels; sign in as user 2; open Saved Simulations | User 1's data is nowhere visible | \___\_ | ☐P ☐F |
| DP-004 | Data isolation — profile | As user 2, open Dashboard | Only user 2's own profile/details appear | \___\_ | ☐P ☐F |
| DP-005 | Session survives refresh | While logged in, reload the page | You stay signed in | \___\_ | ☐P ☐F |
| DP-006 | Logout really ends it | Log out, then use the browser Back button to return to a protected page | You land on the login page, not the protected content | \___\_ | ☐P ☐F |

---

## **11. AI and Connected-Service Behavior**

| Test ID | Service | Steps | Expected on screen | Actual | Status |
| --- | --- | --- | --- | --- | --- |
| AI-001 | EcoSim AI narrative | Run a simulation with AI enabled | A coherent, on-topic plain-language analysis appears | \___\_ | ☐P ☐F |
| AI-002 | AI waiting behavior | Watch the AI panel while it generates | A progress/waiting indicator shows; the page stays usable | \___\_ | ☐P ☐F |
| AI-003 | AI unavailable path | If the AI quota is exhausted during the session, observe the message | A polite, human-readable notice — not a crash or technical dump | \___\_ | ☐P ☐F |
| AI-004 | EnergyHub AI insight | Open the insight panel on EnergyHub | Readable insight, or the same polite unavailable message | \___\_ | ☐P ☐F |
| AI-005 | Map tiles | View the EnergyHub map | Map imagery and province shapes load | \___\_ | ☐P ☐F |
| AI-006 | Google sign-in service | Start "Continue with Google" | The genuine Google account chooser appears | \___\_ | ☐P ☐F |

---

## **12. Performance Observation**

*Use a stopwatch (a phone timer is fine). Time from the click/keypress until the page looks ready. Repeat each twice and record the better time — the first visit after idle can legitimately be slower (cold start), so re-time it once warm.*

| Test ID | Action | Expected feel | Measured | Status |
| --- | --- | --- | --- | --- |
| PT-001 | Open the app home page (cold) | Loads in reasonable time; note it | \___\_ s | ☐P ☐F |
| PT-002 | Open the app home page (warm, second visit) | Feels quick | \___\_ s | ☐P ☐F |
| PT-003 | Log in → land on Dashboard | A few seconds at most | \___\_ s | ☐P ☐F |
| PT-004 | Run an EcoSim simulation | Result appears without feeling stuck | \___\_ s | ☐P ☐F |
| PT-005 | EcoSim AI analysis | May legitimately take tens of seconds; a progress indicator must show | \___\_ s | ☐P ☐F |
| PT-006 | Open EnergyHub | Dashboard sections render progressively; no long blank screen | \___\_ s | ☐P ☐F |
| PT-007 | Switch the EnergyHub map metric | Recolors without a long wait | \___\_ s | ☐P ☐F |
| PT-008 | Overall impression | The app feels responsive in normal use | \___\_ | ☐P ☐F |
| PT-009 *(optional)* | Several evaluators use the app at the same time | Note any visible slowdown | \___\_ | ☐P ☐F |

---

## **13. Security Testing — what a person can observe**

| Test ID | Area | Steps | Expected on screen | Actual | Status |
| --- | --- | --- | --- | --- | --- |
| SO-001 | Login wall — EcoSim | Logged out, open `/ecosim` directly | You land on the login page | \___\_ | ☐P ☐F |
| SO-002 | Login wall — Dashboard | Logged out, open `/dashboard` directly | You land on the login page | \___\_ | ☐P ☐F |
| SO-003 | Login wall — Saved | Logged out, open `/saved-simulations` directly | You land on the login page | \___\_ | ☐P ☐F |
| SO-004 | Login wall — Settings | Logged out, open `/settings/security` directly | You land on the login page | \___\_ | ☐P ☐F |
| SO-005 | Admin wall — guest | Logged out, open `/admin` directly | You land on the login page | \___\_ | ☐P ☐F |
| SO-006 | Admin wall — normal user | As a non-admin user, open `/admin` directly | You are sent away (e.g., to the dashboard) — the admin console never renders | \___\_ | ☐P ☐F |
| SO-007 | Admin menu hidden | As a non-admin user, open the account menu | No "Admin Portal" entry exists | \___\_ | ☐P ☐F |
| SO-008 | Password masking | Type into any password field | Characters show as dots | \___\_ | ☐P ☐F |
| SO-009 | Secure connection | Look at the address bar | The site is served over HTTPS (padlock icon) | \___\_ | ☐P ☐F |
| SO-010 | No internal leaks | Force errors (bad address, refused form inputs, failed login) | Messages are friendly and human — never technical details, code, or stack traces | \___\_ | ☐P ☐F |
| SO-011 | Session after logout | Log out, then try Back button and re-opened tabs | Protected content does not reappear | \___\_ | ☐P ☐F |
| SO-012 | Other users' data | Throughout the session, look for anything belonging to another account | Only your own data is ever shown | \___\_ | ☐P ☐F |
| SO-013 | Polite throttling *(approximate)* | Repeat the same action rapidly many times (e.g., re-run a search dozens of times) | Worst case: a polite "too many requests"-style message; the app must never crash or corrupt data | \___\_ | ☐P ☐F |
| SO-014 | Private pages need login — spot sweep | While logged out, try deep addresses: `/ecosim`, `/energyhub`, `/dashboard`, `/admin`, `/mfa` | Every one lands on login | \___\_ | ☐P ☐F |

---

## **14. Compatibility Testing**

*Repeat a short smoke pass on each target — open the app, sign in, run one EcoSim simulation, open EnergyHub and the map, sign out. Record the result and anything that looked wrong.*

| Target | Browser/device used | Result | Remarks |
| --- | --- | --- | --- |
| Chrome (desktop) | \___\_ | \___\_ | \___\_ |
| Microsoft Edge (desktop) | \___\_ | \___\_ | \___\_ |
| Firefox (desktop) | \___\_ | \___\_ | \___\_ |
| Safari (Mac/iPhone) | \___\_ | \___\_ | \___\_ |
| Phone (your device + its browser) | \___\_ | \___\_ | \___\_ |
| Tablet (your device + its browser) | \___\_ | \___\_ | \___\_ |
| Narrow window (shrink desktop browser to phone width) | \___\_ | Hamburger menu appears; content stays readable; no sideways scrolling | \___\_ |
| Dark theme on a second browser | \___\_ | Readable and consistent | \___\_ |

---

## **15. Usability and UAT**

### **15.1 Moderated tasks** *(run with each participant; protocol follows* `tests/docs/usability_testing.md`*)*

| Task | Instruction to the participant | Success standard | Result |
| --- | --- | --- | --- |
| UAT-1 | "Open EnergyHub and find the latest national energy consumption figure." | Found within \~60 s | ☐ Complete ☐ Partial ☐ Fail |
| UAT-2 | "You live in Tagaytay City, Cavite and pay PHP 2,500/month. Use EcoSim to find the best renewable source for your home." | Simulation run and results viewed within \~3 min | ☐ Complete ☐ Partial ☐ Fail |
| UAT-3 | "Find the forecast chart and identify predicted consumption for 2030." | Value identified within \~90 s | ☐ Complete ☐ Partial ☐ Fail |
| UAT-4 | "Using the map, find which province has the highest solar potential." | Top province identified within \~2 min | ☐ Complete ☐ Partial ☐ Fail |
| UAT-5 | "After your simulation, find and read the AI-generated explanation. What was the main reason given?" | Panel found; reason extracted | ☐ Complete ☐ Partial ☐ Fail |

**Scoring:** Complete = 1.0 · Partial = 0.5 · Fail = 0.0. Task success rate = Σ scores ÷ (5 × participants).

| Metric | Value |
| --- | --- |
| Participants | \___\_ |
| Average task success rate | \___\_ % |
| Average completion time | \___\_ s |
| Common stumbling points | \___\_ |

### **15.2 System Usability Scale (SUS)** — each participant rates 1 (strongly disagree) to 5 (strongly agree)

| \# | Statement | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | I think that I would like to use LUMI frequently. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 2 | I found LUMI unnecessarily complex. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 3 | I thought LUMI was easy to use. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 4 | I think that I would need the support of a technical person to be able to use LUMI. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 5 | I found the various functions in LUMI were well integrated. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 6 | I thought there was too much inconsistency in LUMI. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 7 | I would imagine that most people would learn to use LUMI very quickly. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 8 | I found LUMI very cumbersome to use. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 9 | I felt very confident using LUMI. | ☐ | ☐ | ☐ | ☐ | ☐ |
| 10 | I would need to learn a lot of things before I could get going with LUMI. | ☐ | ☐ | ☐ | ☐ | ☐ |

**Scoring:** odd items → response − 1; even items → 5 − response; sum all ten and multiply by 2.5. Target: average ≥ 68.

| Metric | Value |
| --- | --- |
| Average SUS score | \___\_ / 100 |
| Rating (85+ Excellent · 70–84 Good · 50–69 Marginal · &lt;50 Poor) | \___\_ |

### **15.3 Post-test interview** *(5 minutes per participant — note answers)*

1. Most useful feature? \_____\_
2. Most confusing or difficult part? \_____\_
3. Would you recommend LUMI? Why? \_____\_
4. What feature would you add? \_____\_
5. How does it compare to tools you have used? \_____\_

### **15.4 Evaluator's own usability observations**

| Criterion | What to look at | Observation | Status |
| --- | --- | --- | --- |
| Navigation | Can you always tell where you are and how to get back? | \___\_ | ☐P ☐F |
| Readability | Text size, contrast in both themes | \___\_ | ☐P ☐F |
| Consistency | Buttons, menus, and messages behave the same way everywhere | \___\_ | ☐P ☐F |
| Feedback | Every action acknowledges (loading spinner, toast, confirmation) | \___\_ | ☐P ☐F |
| Error messages | Understandable to a non-technical person | \___\_ | ☐P ☐F |
| Mobile usability | Menus and forms usable on a phone | \___\_ | ☐P ☐F |

---

## **16. ISO/IEC 25010 Evaluation**

| Characteristic | Evidence to weigh | Result |
| --- | --- | --- |
| Functional Suitability | §8 pass rate | \___\_ |
| Performance Efficiency | §12 timings and overall feel | \___\_ |
| Compatibility | §14 matrix | \___\_ |
| Interaction Capability | §15 usability results and SUS | \___\_ |
| Reliability | Did anything break, freeze, or lose data during the whole session? | \___\_ |
| Security | §13 observations | \___\_ |
| Maintainability | Consistency of behavior and messaging across pages | \___\_ |
| Flexibility | Behavior across different devices/screen sizes | \___\_ |
| Safety | Graceful handling of bad input, unavailable services, and quota limits | \___\_ |

---

## **17. Defect / Bug Report**

| Defect ID | Where | What the evaluator saw | Severity | Priority | Status |
| --- | --- | --- | --- | --- | --- |
| BUG-\__\_ | \___\_ | \___\_ | Critical/High/Med/Low | \___\_ | \___\_ |
| BUG-\__\_ | \___\_ | \___\_ | \___\_ | \___\_ | \___\_ |
| BUG-\__\_ | \___\_ | \___\_ | \___\_ | \___\_ | \___\_ |
| BUG-\__\_ | \___\_ | \___\_ | \___\_ | \___\_ | \___\_ |
| BUG-\__\_ | \___\_ | \___\_ | \___\_ | \___\_ | \___\_ |

**Severity guide:** Critical = unusable system, lost data, or a security exposure a user can trigger · High = a major feature does not work · Medium = works with visible limitations · Low = cosmetic or minor annoyance.

---

## **18. Corrective Action and Retesting**

| Defect ID | Corrective Action | Date Fixed | Retest Result | Final Status |
| --- | --- | --- | --- | --- |
| \___\_ | \___\_ | \___\_ | \___\_ | \___\_ |
| \___\_ | \___\_ | \___\_ | \___\_ | \___\_ |
| \___\_ | \___\_ | \___\_ | \___\_ | \___\_ |

---

## **19. Regression Testing**

*Previously fixed defects, re-checked through the interface:*

| Test ID | Previously fixed item | How to retest by hand | Result | Status |
| --- | --- | --- | --- | --- |
| REG-01 | Missing geothermal data crashed with a raw error | Run an EcoSim simulation for a municipality away from geothermal/volcanic areas | The geothermal result card shows a friendly "no significant activity / not a home-scale option" note — never an error or crash | \___\_ |
| REG-02 | Map accepted invalid energy types | Open the map's energy-type selector | Only valid choices are offered — nothing invalid can be picked | \___\_ |
| REG-03 | Forecast accepted a bogus metric | Look at the forecast metric selector | Only valid metrics are offered | \___\_ |
| REG-04 | Injection strings in inputs | Repeat IV-005/IV-006 results | All treated harmlessly | \___\_ |
| REG-05 | Quota message named the wrong product | If the AI quota message appears during the session, read it | It refers to EnergyHub/the correct feature | \___\_ |
| REG-06 | Protected pages reachable without login | Repeat SO-001–SO-006 and SO-014 | All still bounce to login | \___\_ |

---

## **20. Testing Results Summary**

| Category | Total | Passed | Failed | Pass Rate |
| --- | --- | --- | --- | --- |
| Functional (§8) | \___\_ | \___\_ | \___\_ | \___\_% |
| Input validation (§9) | \___\_ | \___\_ | \___\_ | \___\_% |
| Persistence & privacy (§10) | \___\_ | \___\_ | \___\_ | \___\_% |
| AI & services (§11) | \___\_ | \___\_ | \___\_ | \___\_% |
| Performance (§12) | \___\_ | \___\_ | \___\_ | \___\_% |
| Security (§13) | \___\_ | \___\_ | \___\_ | \___\_% |
| Compatibility (§14) | \___\_ | \___\_ | \___\_ | \___\_% |
| Usability (§15) | \___\_ | \___\_ | \___\_ | \___\_% |
| Regression (§19) | \___\_ | \___\_ | \___\_ | \___\_% |
| **TOTAL** | \___\_ | \___\_ | \___\_ | \___\_% |

**Pass Rate = (Passed ÷ Total Executed) × 100** — exclude skipped/unavailable items (e.g., no admin account) from the denominator and note them.

---

## **21. Overall Technical Assessment**

### **Overall Testing Result**

☐ Passed – Ready for Deployment ☐ Passed with Minor Issues ☐ For Further Improvement ☐ Failed – Major Corrections Required

**Assessment narrative:**

> \____________________________________\_

**The system is assessed as:** ☐ Technically Acceptable ☐ Acceptable with Minor Revisions ☐ Requires Further Testing ☐ Not Acceptable

---

## **22. Recommendations**

1. \_____\_ 2. \_____\_ 3. \_____\_ 4. \_____\_ 5. \_____\_

---

## **23. Testing Approval**

| Role | Name | Signature | Date |
| --- | --- | --- | --- |
| Test Engineer/Tester | \___\_ | \___\_ | \___\_ |
| Evaluator (IT Expert) | \___\_ | \___\_ | \___\_ |
| Developer | \___\_ | \___\_ | \___\_ |
| Project Leader | \___\_ | \___\_ | \___\_ |
| Technical Adviser | \___\_ | \___\_ | \___\_ |
| Project Adviser | \___\_ | \___\_ | \___\_ |

---

## **24. Appendices**

### **Appendix A — Manual test kit**

| Item | Purpose |
| --- | --- |
| The Application URL (§1) | Everything happens here |
| Test accounts (§7) | Guest (no account), two registered users, optional admin and MFA accounts |
| Desktop + phone/tablet | The §14 matrix |
| Stopwatch / phone timer | §12 timings |
| Screenshot tool | Evidence for §17 and the sign-off package |

### **Appendix B — Evidence**

Attach or file alongside this form: the completed tables above, numbered screenshots of anything marked Fail and of key passes, and each participant's SUS sheet. Keep one folder per evaluation cycle labeled with the testing date.

### **Appendix C — Notes for the evaluator**

- **Login walls are expected, not bugs.** EcoSim, EnergyHub, Dashboard, Saved Simulations, settings, and admin pages all require an account — being sent to the login page is the system working correctly.
- **Cold starts are normal.** The first visit after the app has been idle can take noticeably longer; reload once before timing anything in §12.
- **AI features have a daily quota.** If the AI panel politely says it is temporarily unavailable, that is expected behavior — record what the message said, not a failure.
- **Type page addresses only.** When a step gives an address like `/dashboard`, it always means an app page — never type anything else into the address bar.
- **Do not save real changes in Admin → Config, and do not delete real users.** Admin checks are look-and-verify only unless the team says otherwise.