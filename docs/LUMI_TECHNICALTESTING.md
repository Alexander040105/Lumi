# **TECHNICAL TESTING REPORT** 

# **Title: LUMI: Data-Driven Environmental Intelligence System for Renewable Energy** 

Group Name: LUMI  Alexander Jon Solis, Lerrica Jeremy Torreno, Sean Maverick Virata   
Technical Evaluators ( IT Experts ) 

# **Instructions :**

# 1)This report is to be done and tested by the programmers and system analysts of the group and 10 IT experts . 

2\) Fill out the details before starting the testing procedure . LIST ALL THE MODULES / FUNCTIONALITY OF YOUR SYSTEM, DELETE THOSE WHO ARE NOT INCLUDED IN YOUR SYSTEM. (YOU CAN ALSO GET THEM FROM YOUR MIDTERM PROGRESS REPORT IF AVAILABLE)  
3\. Record and document the testing specially when there are bugs or errors.   
4\) Functional Testing / Test Case or / Testing Plan (copy paste when you are done to your documentation Testing and Procedures)  
5\) When the testing is completed , errors are fixed then you can proceed to SYSTEM EVALUATION. 

# **COMPREHENSIVE SOFTWARE TECHNICAL TESTING REPORT**

## **1\. Document Information**

| Item | Details |
| ----- | ----- |
| **Project/System Name** | LUMI |
| **Project Title** | LUMI: Data-Driven Environmental Intelligence System for Renewable Energy |
| **Version** | Version1.0 |
| **Testing Date** | September 1-10, 2026 |
| **Testing Environment** | Web-Based Application / Deployed LUMI system |
| **Tested By** | LUMI Development Team and 10 IT Expert Evaluators |
| **Developer/Development Team** | Alexander Jon Solis, Lerrica Jeremy Torreno, Sean Maverick Virata  |
| **Test Report Version** | Version 1.0 |
| **Status** | ☐ Draft ☐ **Final** |

---

# **2\. Executive Summary**

### **2.1 Purpose of Testing**

This form records the procedures, observations, identified defects, corrective actions, and overall assessment of LUMI as experienced by a person using the deployed application — covering functional, performance, security, usability, compatibility, and reliability requirements.

### **2.2 Testing Objectives**

The testing objectives are to:

1. Verify all visible functions work as described.   
2. Identify defects a user would notice.   
3. Judge responsiveness by direct observation and a stopwatch.   
4. Verify the app works across browsers and devices.   
5. Assess access control as seen by guest, user, and admin accounts.   
6. Verify that saved data persists and stays private to its owner.   
7. Evaluate against ISO/IEC 25010\.   
8. Confirm previously fixed defects stay fixed.   
9. Determine deployment readiness from a user's point of view.

---

# **3\. System Overview**

### **3.1 System Description**

**System Name:** LUMI 

**Description:**

A web system with four working parts. EcoSim estimates which renewable energy source fits a household in any Philippine municipality, with costs and savings. EnergyHub is a national energy dashboard with historical statistics, forecasts, and province-level renewable-potential maps. An AI assistant writes plain-language explanations of the results. Registered users can save simulations and manage a profile; administrators get a management console for users, analytics, and logs.

### **3.2 Intended Users**

| User Type | Description | Access Level |
| ----- | ----- | ----- |
| Administrator | Everything a user can do, plus manage users, view analytics, edit configuration, inspect usage and logs | Admin account — an "Admin Portal" entry appears in the account menu |
| Registered user | EcoSim simulations, EnergyHub, saved simulations, profile and security settings, MFA | Email/password or Google sign-in |
| Guest | Home, About, Terms, Privacy pages only — every feature page asks for login | No account |

### **3.3 Major System Modules**

| No. | Module/Feature | Description |
| ----- | ----- | ----- |
| 1 | Home (`/`) | Landing page |
| 2 | About (`/about`), Terms (`/terms`), Privacy (`/privacy`) | Public information pages |
| 3 | Login (`/login`), Reset password (`/reset-password`) | Sign-in, sign-up, Google sign-in, password reset, MFA code step |
| 4 | Dashboard (`/dashboard`) | Profile view/edit, avatar, saved locations, saved simulations; admins also see a forecast panel |
| 5 | EcoSim (`/ecosim`) | Simulation wizard, results, AI analysis, save-simulation dialog, PDF download |
| 6 | EnergyHub (`/energyhub`) | National overview, trends, forecast chart, choropleth map, source breakdowns, provincial demand, AI insight |

---

# **4\. Testing Scope**

## **4.1 In-Scope**

The following components were included in testing:

Every screen, feature, and flow reachable through the app's interface on the deployed site: public pages, sign-up/login/logout, EcoSim, EnergyHub, saved simulations, profile and security settings, the admin console, input handling, on-screen security behavior, data persistence, responsiveness, multiple browsers and devices, and a moderated usability session.

## **4.2 Out-of-Scope**

The following were excluded from the current testing cycle:

> ---

---

---

# **5\. Testing Methodology**

The testing process followed a structured testing approach consisting of:

**Requirements → Test Planning → Test Case Development → Test Execution → Defect Identification → Correction → Retesting → Final Evaluation**

### **Testing Types**

| Testing Type | Purpose | Performed? |
| ----- | ----- | ----- |
| Functional walkthrough | Follow each §8 scenario and compare what appears | ☐ |
| Exploratory clicking | Wander the app freely and note anything broken or confusing | ☐ |
| Negative-input testing | Type bad, weird, or hostile-looking input into forms  | ☐ |
| Permission checks | Try the same pages as guest, user, and admin (§13) | ☐ |
| Persistence checks | Save data, log out, log back in, and look for it (§10) | ☐ |
| Timed observation | Stopwatch the actions in §12 | ☐ |
| Compatibility pass | Repeat key flows on each browser/device  | ☐ |

---

# **6\. Test Environment**

## **6.1 Evaluator Equipment**

| Item | Details |
| ----- | ----- |
| Browser(s) and version(s) |  |
| Screen size / resolution |  |
| Computer (OS, rough specs) |  |
| Phone or tablet used (if any) |  |
| Internet connection |  |

## ---

# **7\. Test Data**

| What you look at | What healthy data looks like |
| ----- | ----- |
| EcoSim location picker | A long, searchable list of real Philippine municipalities and provinces — e.g., typing "Tagaytay" finds Tagaytay City |
| EcoSim defaults | Monthly consumption and bill fields arrive pre-filled with reasonable numbers |
| EnergyHub overview | Real national statistics (consumption, generation, demand) with recent years shown |
| EnergyHub forecast | A chart projecting roughly to 2030, with an upper/lower range around the line |
| EnergyHub map | A Philippine map colored by province; a selector switches between renewable/solar/wind/hydro/geothermal views |
| Provider recommendations (inside EcoSim results) | Real installer/provider names relevant to the chosen location |
| Saved simulations (new account) | Empty list until the user saves one |

---

# **8\. Functional Test Cases**

### **Test Case Format**

| Field | Details |
| ----- | ----- |
| **Test Case ID** | TC-F-001 |
| **Module** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| **Test Objective** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| **Precondition** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| **Test Input** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| **Test Steps** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| **Expected Result** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| **Actual Result** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |
| **Status** | ☐ Pass ☐ Fail |
| **Remarks** | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ |

### **8.1 Public pages and navigation**

### 

| Test ID | Area | Steps | Expected on screen | Actual | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| FT-001 | Home | Open the app address | LUMI home page loads fully — logo, navigation, page content |  | ☐Pass ☐Fail |
| FT-002 | About | Click "About" in the navigation | About page with readable content |  | ☐Pass ☐Fail |
| FT-003 | Terms/Privacy | Open `/terms`, then `/privacy` | Both legal pages render readable text |  | ☐Pass ☐Fail |
| FT-004 | Navigation | Click every link in the top navigation while logged out | Each leads somewhere sensible; EcoSim and EnergyHub ask for login |  | ☐Pass ☐Fail |
| FT-005 | Theme | Click the theme toggle | The app visibly switches light/dark |  | ☐Pass ☐Fail |
| FT-006 | Language | Click the language toggle and switch language | On-screen text changes language |  | ☐Pass ☐Fail |
| FT-007 | Bad address | Open `/this-page-does-not-exist` | A friendly "not found" page, not a blank screen or raw error |  | ☐Pass ☐Fail |

### **8.2 Accounts: sign-up, login, logout**

| Test ID | Area | Steps | Expected on screen | Actual | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| AC-001 | Sign up | On `/login`, choose Sign Up, enter a new email \+ password \+ confirm, submit | Confirmation message appears (check-email notice or immediate sign-in) |  | ☐Pass ☐Fail |
| AC-002 | Sign-up guard | Sign Up with two different passwords in the two boxes | A polite "passwords do not match" message; nothing crashes |  | ☐Pass ☐Fail |
| AC-003 | Bad email | Sign Up with `not-an-email` | The form refuses with a clear message |  | ☐Pass ☐Fail |
| AC-004 | Login | Sign in as registered user 1 | You land inside the app (dashboard or the page you asked for); the account menu shows your name/email |  | ☐Pass ☐Fail |
| AC-005 | Wrong password | Sign in with the right email, wrong password | A clear "invalid credentials"-style message; no access granted |  | ☐Pass ☐Fail |
| AC-006 | Google sign-in | On `/login`, click "Continue with Google" | A real Google sign-in prompt opens (cancel it after confirming it appears) |  | ☐Pass ☐Fail |
| AC-007 | Password reset | Choose "Forgot password," enter the account email | A "reset email sent" confirmation appears (verify the inbox if accessible) |  | ☐Pass ☐Fail |
| AC-008 | MFA *(optional — needs the MFA account)* | Sign in as the MFA-enrolled user | After the password, a code-entry step appears; a correct authenticator code lets you in, a wrong one is refused |  | ☐Pass ☐Fail |
| AC-009 | Logout | From the account menu, choose Logout | You return to a signed-out state; protected pages no longer open |  | ☐Pass ☐Fail |

### **8.3 EcoSim — the simulation flow**

| Test ID | Area | Steps | Expected on screen | Actual | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| FT-010 | Wizard loads | Logged in, open EcoSim | The wizard appears: location picker (municipality/province mode), consumption, bill, and options |  | ☐Pass ☐Fail |
| FT-011 | Location list | Open the municipality picker and type "Tagaytay" | Tagaytay City is found and selectable from a long real list |  | ☐Pass ☐Fail |
| FT-012 | Province mode | Switch to province mode and open the picker | Real provinces list and select |  | ☐Pass ☐Fail |
| FT-013 | Run simulation | Pick a municipality, leave defaults (or enter bill PHP 2,500), run | Results appear: recommended source(s), estimated output, costs/savings, figures are plausible |  | ☐Pass ☐Fail |
| FT-014 | AI analysis | With AI enabled, run or view the analysis panel | Readable plain-language analysis appears; a waiting/progress indicator during slow answers is normal |  | ☐Pass ☐Fail |
| FT-015 | Save simulation | After results, choose Save and give it a label | A save confirmation appears |  | ☐Pass ☐Fail |
| FT-016 | PDF download | Download the results PDF if the button is offered | A PDF downloads and opens showing the same results |  | ☐Pass ☐Fail |

### **8.4 EnergyHub — the national dashboard**

### 

| Test ID | Area | Steps | Expected on screen | Actual | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| FT-017 | Overview | Logged in, open EnergyHub | National overview cards/figures load with real numbers |  | ☐Pass ☐Fail |
| FT-018 | Trends | Scroll to the trends/history section | Historical charts render (years \~2003 to present) |  | ☐Pass ☐Fail |
| FT-019 | Forecast | Find the forecast chart | Projection to roughly 2030, including a visible upper/lower range |  | ☐Pass ☐Fail |
| FT-020 | Map | View the choropleth map; switch the metric selector through renewable/solar/wind/hydro/geothermal | The Philippine map recolors for each metric; a legend explains the colors |  | ☐Pass ☐Fail |
| FT-021 | Map level | Switch the map level (province ↔ municipality if offered) | The map redraws at the new level |  | ☐Pass ☐Fail |
| FT-022 | Breakdowns | View source/grid breakdown sections | Charts render with plausible shares |  | ☐Pass ☐Fail |
| FT-023 | Provincial demand | View the provincial demand section | Provincial figures/charts load |  | ☐Pass ☐Fail |
| FT-024 | AI insight | Open the AI insight panel | Either a readable insight appears, or a polite message that the service is temporarily unavailable (quota) — both are acceptable behavior |  | ☐Pass ☐Fail |
| FT-025 | Chart explanations | Where an "explain" button exists on charts, use it | A readable explanation appears |  | ☐Pass ☐Fail |

### **8.5 Saved data and account pages**

### 

| Test ID | Area | Steps | Expected on screen | Actual | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| FT-026 | Saved list | Open Saved Simulations after saving in FT-015 | The saved simulation is listed with its label and municipality |  | ☐Pass ☐Fail |
| FT-027 | Delete saved | Delete the test simulation and confirm | It disappears from the list |  | ☐Pass ☐Fail |
| FT-028 | Dashboard | Open Dashboard | Profile card, saved locations/simulations sections render |  | ☐Pass ☐Fail |
| FT-029 | Profile edit | Edit full name / organization / location and save | A confirmation appears and the new values display |  | ☐Pass ☐Fail |
| FT-030 | Avatar | Upload a profile picture if offered | The avatar updates on screen |  | ☐Pass ☐Fail |
| FT-031 | Security page | Open Settings → Security | Change-email, change-password, and delete-account sections render |  | ☐Pass ☐Fail |
| FT-032 | Change password | Change password (record the new one), log out, log in with it | The new password works; the old one no longer does |  | ☐Pass ☐Fail |
| FT-033 | MFA page | Open the MFA setup page (`/mfa`) | Authenticator enrollment instructions/QR appear |  | ☐Pass ☐Fail |

### 

### **8.6 Admin console *(admin account only — skip the whole block if unavailable)***

| Test ID | Area | Steps | Expected on screen | Actual | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| AD-001 | Admin menu | Sign in as admin; open the account menu | An "Admin Portal" entry exists (absent for normal users) |  | ☐Pass ☐Fail |
| AD-002 | Admin home | Open `/admin` | The admin dashboard renders |  | ☐Pass ☐Fail |
| AD-003 | Users | Open Users | A real user list appears; opening a user shows detail/actions |  | ☐Pass ☐Fail |
| AD-004 | Create user | Create a test user via the Users page form | The new user appears in the list (delete/flag it after if possible) |  | ☐Pass ☐Fail |
| AD-005 | User actions | Try a non-destructive action (open detail drawer; view simulations/reports tabs) | Details display correctly |  | ☐Pass ☐Fail |
| AD-006 | Analytics | Open Analytics | Charts/figures render |  | ☐Pass ☐Fail |
| AD-007 | Config | Open Config | Configuration page renders; do not save changes |  | ☐Pass ☐Fail |
| AD-008 | Usage | Open Usage | Usage statistics render |  | ☐Pass ☐Fail |
| AD-009 | Logs | Open Logs | Log entries render |  | ☐Pass ☐Fail |
| AD-010 | Forecast panel | Open Dashboard as admin | The forecast-runner panel is visible (admin-only feature) |  | ☐Pass ☐Fail |

---

# **9\. Input Validation Testing**

| Test ID | Field | What you type | Expected on screen | Actual | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| IV-001 | EcoSim — monthly bill | letters, e.g. `abc` | Refused or ignored — never a broken result |  | ☐Pass ☐Fail |
| IV-002 | EcoSim — consumption | a huge number, e.g. `99999999999` | Rejected politely or handled sensibly |  | ☐Pass ☐Fail |
| IV-003 | EcoSim — consumption | a negative number, e.g. `-50` | Rejected politely |  | ☐Pass ☐Fail |
| IV-004 | EcoSim — run with nothing chosen | leave location empty and run | A clear "choose a location"-style message |  | ☐Pass ☐Fail |
| IV-005 | Any search/filter box | `' OR '1'='1` | Treated as plain text — no error page, no odd data shown |  | ☐Pass ☐Fail |

---

# **10\. Database Persistence and Privacy Testing**

| Test ID | Check | Steps | Expected on screen | Actual | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| DP-001 | Simulation persists | As user 1, save a simulation; log out; log back in; open Saved Simulations | The simulation is still there |  | ☐Pass ☐Fail |
| DP-002 | Profile persists | Edit profile details; log out and back in | The edits are still shown |  | ☐Pass ☐Fail |
| DP-003 | Data isolation — saved sims | Note user 1's saved simulation labels; sign in as user 2; open Saved Simulations | User 1's data is nowhere visible |  | ☐Pass ☐Fail |
| DP-004 | Data isolation — profile | As user 2, open Dashboard | Only user 2's own profile/details appear |  | ☐Pass ☐Fail |
| DP-005 | Session survives refresh | While logged in, reload the page | You stay signed in |  | ☐Pass ☐Fail |
| DP-006 | Logout really ends it | Log out, then use the browser Back button to return to a protected page | You land on the login page, not the protected content |  | ☐Pass ☐Fail |

---

# **11\. AI and Connected-Service Behavior**

For systems using APIs, cloud services, AI/LLM services, or third-party services:

| Test ID | Service | Steps | Expected on screen | Actual | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| AI-001 | EcoSim AI narrative | Run a simulation with AI enabled | A coherent, on-topic plain-language analysis appears |  | ☐Pass ☐Fail |
| AI-002 | AI waiting behavior | Watch the AI panel while it generates | A progress/waiting indicator shows; the page stays usable |  | ☐Pass ☐Fail |
| AI-003 | AI unavailable path | If the AI quota is exhausted during the session, observe the message | A polite, human-readable notice — not a crash or technical dump |  | ☐Pass ☐Fail |
| AI-004 | EnergyHub AI insight | Open the insight panel on EnergyHub | Readable insight, or the same polite unavailable message |  | ☐Pass ☐Fail |
| AI-005 | Map tiles | View the EnergyHub map | Map imagery and province shapes load |  | ☐Pass ☐Fail |
| AI-006 | Google sign-in service | Start "Continue with Google" | The genuine Google account chooser appears |  | ☐Pass ☐Fail |

---

# 

# 

# 

# **12\. Performance Testing**

| Test ID | Action | Expected feel | Measured | Status |
| ----- | ----- | ----- | ----- | ----- |
| PT-001 | Open the app home page (cold) | Loads in reasonable time; note it | \_\_\_\_ s | ☐Pass ☐Fail |
| PT-002 | Open the app home page (warm, second visit) | Feels quick | \_\_\_\_ s | ☐Pass ☐Fail |
| PT-003 | Log in → land on Dashboard | A few seconds at most | \_\_\_\_ s | ☐Pass ☐Fail |
| PT-004 | Run an EcoSim simulation | Result appears without feeling stuck | \_\_\_\_ s | ☐Pass ☐Fail |
| PT-005 | EcoSim AI analysis | May legitimately take tens of seconds; a progress indicator must show | \_\_\_\_ s | ☐Pass ☐Fail |
| PT-006 | Open EnergyHub | Dashboard sections render progressively; no long blank screen | \_\_\_\_ s | ☐Pass ☐Fail |
| PT-007 | Switch the EnergyHub map metric | Recolors without a long wait | \_\_\_\_ s | ☐Pass ☐Fail |
| PT-008 | Overall impression | The app feels responsive in normal use |  | ☐Pass ☐Fail |
| PT-009 *(optional)* | Several evaluators use the app at the same time | Note any visible slowdown |  | ☐Pass ☐Fail |

---

# **13\. Security Testing**

| Test ID | Area | Steps | Expected on screen | Actual | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| SO-001 | Login wall — EcoSim | Logged out, open `/ecosim` directly | You land on the login page |  | ☐Pass ☐Fail |
| SO-002 | Login wall — Dashboard | Logged out, open `/dashboard` directly | You land on the login page |  | ☐Pass ☐Fail |
| SO-003 | Login wall — Saved | Logged out, open `/saved-simulations` directly | You land on the login page |  | ☐Pass ☐Fail |
| SO-004 | Login wall — Settings | Logged out, open `/settings/security` directly | You land on the login page |  | ☐Pass ☐Fail |
| SO-005 | Admin wall — guest | Logged out, open `/admin` directly | You land on the login page |  | ☐Pass ☐Fail |
| SO-006 | Admin wall — normal user | As a non-admin user, open `/admin` directly | You are sent away (e.g., to the dashboard) — the admin console never renders |  | ☐Pass ☐Fail |
| SO-007 | Admin menu hidden | As a non-admin user, open the account menu | No "Admin Portal" entry exists |  | ☐Pass ☐Fail |
| SO-008 | Password masking | Type into any password field | Characters show as dots |  | ☐Pass ☐Fail |
| SO-009 | Secure connection | Look at the address bar | The site is served over HTTPS (padlock icon) |  | ☐Pass ☐Fail |
| SO-010 | No internal leaks | Force errors (bad address, refused form inputs, failed login) | Messages are friendly and human — never technical details, code, or stack traces |  | ☐Pass ☐Fail |
| SO-011 | Session after logout | Log out, then try Back button and re-opened tabs | Protected content does not reappear |  | ☐Pass ☐Fail |
| SO-012 | Other users' data | Throughout the session, look for anything belonging to another account | Only your own data is ever shown |  | ☐Pass ☐Fail |
| SO-013 | Polite throttling *(approximate)* | Repeat the same action rapidly many times (e.g., re-run a search dozens of times) | Worst case: a polite "too many requests"-style message; the app must never crash or corrupt data |  | ☐Pass ☐Fail |
| SO-014 | Private pages need login — spot sweep | While logged out, try deep addresses: `/ecosim`, `/energyhub`, `/dashboard`, `/admin`, `/mfa` | Every one lands on login |  | ☐Pass ☐Fail |

---

# 

# 

# **14\. Compatibility Testing**

### **Browser Compatibility**

| Browser | Version | Result | Remarks |
| ----- | ----- | ----- | ----- |
| Google Chrome |  | ☐Pass ☐Fail |  |
| Microsoft Edge |  | ☐Pass ☐Fail |  |
| Mozilla Firefox |  | ☐Pass ☐Fail |  |
| Safari |  | ☐Pass ☐Fail |  |

### **Device Compatibility**

| Device | OS | Screen Size | Result |
| ----- | ----- | ----- | ----- |
| Desktop | Windows |  | ☐Pass ☐Fail |
| Laptop | Windows |  | ☐Pass ☐Fail |
| Tablet | Android/iOS |  | ☐Pass ☐Fail |
| Smartphone | Android/iOS |  | ☐Pass ☐Fail |

---

# **15\. Usability and User Interface Testing**

| Task | Instruction to the participant | Success standard | Result |
| ----- | ----- | ----- | ----- |
| UAT-1 | "Open EnergyHub and find the latest national energy consumption figure." | Found within \~60 s | ☐Pass ☐Fail |
| UAT-2 | "You live in Tagaytay City, Cavite and pay PHP 2,500/month. Use EcoSim to find the best renewable source for your home." | Simulation run and results viewed within \~3 min | ☐Pass ☐Fail |
| UAT-3 | "Find the forecast chart and identify predicted consumption for 2030." | Value identified within \~90 s | ☐Pass ☐Fail |
| UAT-4 | "Using the map, find which province has the highest solar potential." | Top province identified within \~2 min | ☐Pass ☐Fail |
| UAT-5 | "After your simulation, find and read the AI-generated explanation. What was the main reason given?" | Panel found; reason extracted | ☐Pass ☐Fail |

---

# **16\. ISO/IEC 25010 Software Quality Evaluation**

If the technical testing is aligned with **ISO/IEC 25010**, the following characteristics can be included:

| Quality Characteristic | Evaluation Focus | Result |
| ----- | ----- | ----- |
| **Functional Suitability** | Completeness, correctness, appropriateness |  |
| **Performance Efficiency** | Time behavior, resource utilization, capacity |  |
| **Compatibility** | Co-existence and interoperability |  |
| **Interaction Capability** | Ease and effectiveness of user interaction |  |
| **Reliability** | Availability, fault tolerance, recoverability |  |
| **Security** | Confidentiality, integrity, authentication, accountability |  |
| **Maintainability** | Modularity, reusability, analysability, modifiability, testability |  |
| **Flexibility** | Adaptability, scalability, installability, replaceability |  |
| **Safety** | Risk identification and mitigation, where applicable |  |

> **Note:** The exact ISO/IEC 25010 edition and terminology used should be stated in the methodology, because the quality model has been revised across editions.

---

# **17\. Defect / Bug Report**

| Defect ID | Module | Description | Severity | Priority | Status |
| ----- | ----- | ----- | ----- | ----- | ----- |
| BUG-001 |  |  | ☐ Critical ☐ High ☐ Medium ☐ Low | ☐ High ☐ Medium ☐ Low |  |
| BUG-002 |  |  | ☐ Critical ☐ High ☐ Medium ☐ Low | ☐ High ☐ Medium ☐ Low |  |
| BUG-003 |  |  | ☐ Critical ☐ High ☐ Medium ☐ Low | ☐ High ☐ Medium ☐ Low |  |

### **Severity Classification**

| Severity | Description |
| ----- | ----- |
| **Critical** | Prevents the system from operating or causes major data/security failure |
| **High** | Major function does not work correctly |
| **Medium** | Function works with limitations or workaround |
| **Low** | Minor defect with limited impact |

---

# **18\. Corrective Action and Retesting**

| Defect ID | Corrective Action | Date Fixed | Retest Result | Final Status |
| ----- | ----- | ----- | ----- | ----- |
| BUG-001 | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_ | Pass/Fail | Closed/Open |
| BUG-002 | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_ | Pass/Fail | Closed/Open |
| BUG-003 | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_ | Pass/Fail | Closed/Open |

---

# 

# **19\. Regression Testing**

Regression testing was conducted after corrections and system modifications to determine whether previously functioning features remained operational.

| Test ID | Previously fixed item | How to retest by hand | Result | Status |
| ----- | ----- | ----- | ----- | ----- |
| REG-01 | Missing geothermal data crashed with a raw error | Run an EcoSim simulation for a municipality away from geothermal/volcanic areas | The geothermal result card shows a friendly "no significant activity / not a home-scale option" note — never an error or crash | ☐Pass ☐Fail |
| REG-02 | Map accepted invalid energy types | Open the map's energy-type selector | Only valid choices are offered — nothing invalid can be picked | ☐Pass ☐Fail |
| REG-03 | Forecast accepted a bogus metric | Look at the forecast metric selector | Only valid metrics are offered | ☐Pass ☐Fail |
| REG-04 | Injection strings in inputs | Repeat IV-005/IV-006 results | All treated harmlessly | ☐Pass ☐Fail |
| REG-05 | Quota message named the wrong product | If the AI quota message appears during the session, read it | It refers to EnergyHub/the correct feature | ☐Pass ☐Fail |
| REG-06 | Protected pages reachable without login | Repeat SO-001–SO-006 and SO-014 | All still bounce to login | ☐Pass ☐Fail |

---

# **20\. Testing Results Summary**

| Category | Total | Passed | Failed | Pass Rate |
| ----- | ----- | ----- | ----- | ----- |
| Functional  |  |  |  | \_\_\_\_% |
| Input validation  |  |  |  | \_\_\_\_% |
| Persistence & privacy  |  |  |  | \_\_\_\_% |
| AI & services  |  |  |  | \_\_\_\_% |
| Performance  |  |  |  | \_\_\_\_% |
| Security  |  |  |  | \_\_\_\_% |
| Compatibility  |  |  |  | \_\_\_\_% |
| Regression |  |  |  | \_\_\_% |
| **TOTAL** |  |  |  | **\_\_\_%** |

### **Pass Rate Formula**

**Pass Rate \= (Number of Passed Test Cases ÷ Total Test Cases) × 100**

---

# **21\. Overall Technical Assessment**

### **Overall Testing Result**

☐ **Passed – Ready for Deployment**

☐ **Passed with Minor Issues**

☐ **For Further Improvement**

☐ **Failed – Major Corrections Required**

### **Technical Assessment**

Based on the testing activities conducted, the software system:

> ---

---

---

---

The identified defects and issues were:

> ---

---

The system is therefore assessed as:

**☐ Technically Acceptable**  
 **☐ Acceptable with Minor Revisions**  
 **☐ Requires Further Testing**  
 **☐ Not Acceptable**

---

# **22\. Recommendations**

Based on the testing results, the following recommendations are proposed:

1. ---

2. ---

3. ---

4. ---

5. ---

---

# 

# **23\. Testing Approval**

| Role | Name | Signature | Date |
| ----- | ----- | ----- | ----- |
| **Test Engineer/Tester** |  |  |  |
| **Developer** | Alexander Jon S. Solis |  | Sept. 16, 2026 |
| **Project Leader** |  |  |  |
| **Technical Adviser** |  |  |  |
| **Project Adviser** |  |  |  |

---

