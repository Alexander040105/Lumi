# LUMI System Revisions — Implementation Instructions

> Source: LUMI-System-Revisions.pdf (design review notes)
> Purpose: Feed this to SWE1.7 Max as a task list to implement all requested copy, UI, and feature changes across the Home, About, EcoSim, and EnergyHub pages.
> Legend: `[COPY]` = text/content change only · `[UI]` = component/layout/style change · `[FEATURE]` = new functionality · `[OPEN]` = needs a decision before implementing

---

## 0. Global

- `[UI]` Increase base font size slightly and darken the default font color site-wide (navbar + body text). Confirm exact hex/size with design tokens before implementing; use a subtle bump (e.g. +1-2px, darken text color one shade) rather than a drastic change.
- `[COPY]` Navbar link rename:
  - "EcoSim" → keep nav label "EcoSim", but add a descriptor/subtitle under it reading **"Compare Options"** (page subtitle, not the nav item itself).
  - "Energy Hub" → nav label stays "Energy Hub", subtitle **"Explore Energy"**.
  - "Login" → subtitle/tooltip **"Sign in"**.

---

## 1. Home Page

### 1.1 Hero Section
- `[COPY]` Headline: "Data-Driven Insights for a Sustainable Future" → **"Find the Best Renewable Energy Option for your Area"**
- `[COPY]` Subheading/description → **"LUMI helps you compare solar, wind, and hydro energy using weather and energy data from different parts of the Philippines. See which options may work in your area, their estimated costs, and their possible benefits."**
- `[COPY]` CTA button "Try EnergyHub" → **"Explore Energy in my Area"**
- `[COPY]` CTA button "Learn More" → **"How LUMI Works"**

### 1.2 Stats Row (4 stat cards)
Update each card's header + description:
1. `[COPY]` "17+ Regions Covered" → Header: **"Philippine Regions Covered"**, Description: **"Explore climate and energy information across the country"**
2. `[COPY]` "3 Energy Sources" → Header: **"Solar, Wind & Hydro"**, Description: **"Compare three renewable energy options"**
3. `[COPY]` "10K+ Data Points" → Header: **"Reliable Data Sources"**, Description: **"Information from recognized weather and energy sources"**
4. `[COPY]` "Real-time AI Insights" → Header: **"Easy-to-Understand Results"**, Description: **"Get simple explanations and recommendations"**

### 1.3 "Intelligent Tools for Energy Decisions" Section (3 module cards)
- **EnergyHub card**
  - `[COPY]` Description → **"Explore energy and weather information in your area. See temperature, rainfall, electricity use, and other trends through easy-to-read charts and explanations."**
  - `[COPY]` Label "KPIs & Charts" → **"Charts & Key Information"**
  - `[UI]` Remove label "NGCP & OpenWeather" from this card. Relocate this data-source attribution to a different page (e.g. EnergyHub page footer or a data-sources tooltip — see Section 3).
- **EcoSim card**
  - `[COPY]` Description → **"Compare renewable energy options. Choose a location and compare solar, wind, and hydro based on estimated cost, savings, and local conditions."**
  - `[COPY]` Label "ROI Estimation" → **"Estimated Savings"**
- **AI Intelligence card**
  - `[COPY]` Card title/description → **"Get simple explanations. LUMI can explain charts, forecasts, and recommendations using everyday language."**
  - `[UI]` Add "(Powered by AI)" as a parenthetical/badge next to the title.
  - `[COPY]` Label "Natural Language" → **"Simple Explanations"**

### 1.4 "How LUMI Works" Section (4-step process)
- `[FEATURE]/[UI]` Reframe this section to show the **user journey / how a user uses the app**, not backend/system architecture. Replace the current data-pipeline framing (Data Collection → Climate & Energy Analysis → AI Processing → Decision Support) with a user-flow framing:
  1. `[COPY]` Step 1 — Header: **"Choose your Location"**, Description: **"Select your province, city, or region"**
  2. `[COPY]` Step 2 — Header: **"Explore Local Conditions"**, Description: **"See rainfall, sunlight, wind, electricity use, and other information"**
  3. `[COPY]` Step 3 — Header: **"Compare your Options"**, Description: **"Compare solar, wind, and hydro based on your area's conditions"**
  4. `[COPY]` Step 4 — Header: **"See your Recommendation"**, Description: **"Get an easy-to-understand explanation of which options may suit your area"**

### 1.5 "Solar, Wind & Hydro Analysis" Section
For each of the 3 cards (Solar / Wind / Hydro):
- `[COPY]` **Solar Energy** — Sub-header: **"Best where there is strong sunlight"**, Description: **"LUMI examines sunlight and local weather conditions to help estimate whether solar energy may work well in your area."**
- `[COPY]` **Wind Energy** — Sub-header: **"Best in locations with reliable wind"**, Description: **"LUMI examines wind conditions to help determine whether wind energy may be suitable for your location."**
- `[COPY]` **Hydro Energy** — Sub-header: **"Best near suitable water resources"**, Description: **"LUMI examines rainfall and water-related conditions to help determine the potential for small-scale hydropower."**
- `[FEATURE]` For each card, add a small clickable line: **"Based on the Philippine and international research"** — clicking it expands/reveals the citation list for that card (accordion or modal/tooltip; use the same interaction pattern as `[FEATURE]` in Section 1.6).

### 1.6 "Why the Philippines Needs Renewable Intelligence" Section
- `[COPY]` Replace body copy (currently has inline citations like "(Gonocruz et al., 2024)") with:
  > "Much of the country's electricity still comes from fossil fuels. Renewable sources such as solar, wind, and hydro can provide cleaner alternatives, but choosing the right option can be difficult.
  >
  > LUMI brings weather, energy, and cost information together so people can compare their options more easily."
- `[UI]` Remove inline citation text from the paragraph body. Do NOT show raw citations in running text anywhere on the site.
- `[COPY]` Button "Read the Research" → **"See Our Data Sources"**

### 1.7 Final CTA Section
- `[COPY]` Headline "Start Analyzing Your Energy Future" → **"Find the Right Renewable Energy Option for You"**
- `[COPY]` Add description under headline: **"Choose your location to explore climate information or compare solar, wind, and hydro options."**
- `[COPY]` Button "Try EcoSim" → **"Compare Energy Options"**
- `[COPY]` Button "Try EnergyHub" → **"Explore Climate Data"**

### 1.8 References Section
- `[COPY]` Section title "References" → **"Our Data & Research"**
- `[COPY]` Add intro line under the new title: **"LUMI uses published research and trusted climate and energy data sources."**
- `[FEATURE]` Add a button under that intro line: **"View Sources & References"** (opens/links to the full reference list — do not render raw citation entries inline on the page body).

---

## 2. About Page

### 2.1 Global note for this page
- `[UI]` Same as Home Section 1.6: do not place raw citations inline in body text. Instead, wrap any sourced statement with a parenthetical link/badge (e.g. "View Sources") that reveals the citation on click/hover.

### 2.2 Hero
- `[COPY]` Headline "Understanding LUMI" → **"Making Renewable Energy Information Easier to Understand"**
- `[COPY]` Description → **"LUMI is a Philippine-based platform that helps people understand climate and energy information, compare renewable energy options, and make more informed decisions."**
- `[COPY]` Button "Try EnergyHub" → **"Explore Energy Data"**
- `[COPY]` Button "Try EcoSim" → **"Compare Energy Options"**

### 2.3 "Why LUMI Was Developed" Section
- `[COPY]` Section title → **"Why LUMI Was Created"**
- `[COPY]` Body copy → **"Choosing renewable energy can be difficult. Information about costs, weather conditions, energy use, and available technologies is often spread across different sources and can be hard to understand. LUMI brings this information together in one place and explains it in a simpler way."**
- `[UI]` Keep the 3 stat containers (Fossil Fuel Share / Renewable Share / 3 Barriers) below this text, but strip inline citations from their descriptions per the global citation rule (2.1).
- `[COPY]` Add CTA button below the 3 containers: **"Want to see the evidence?"** with button label **"View Research & Sources"**.

### 2.4 Mission & Vision Section
- `[COPY]` Mission → **"To make climate and renewable energy information easier for Filipinos to understand and use when making energy decisions."**
- `[COPY]` Vision → **"A Philippines where students, households, communities, and decision-makers can easily access reliable information and make better choices about renewable energy."**

### 2.5 "The Need for Environmental Intelligence" Section
- `[COPY]` Section title → **"Who can use LUMI?"**
- `[COPY]` Reframe the 3 cards (Educational Resource / Decision Support / Research Groundwork) as **"Significance of the Study (Beneficiaries)"** — i.e., rewrite each card to describe who benefits from LUMI (e.g., students, households, government/policymakers) rather than academic research framing.
- `[UI]` Remove the research problem statement content from this section entirely.

### 2.6 "How LUMI Is Structured" Section
- `[COPY]` Section title stays **"How LUMI is Structured"**
- Update 4 module cards:
  1. `[COPY]` **EnergyHub** — Sub-heading: **"Explore climate and energy data"**, Description: **"View easy-to-read charts showing weather, electricity use, and energy trends across different Philippine regions."**
  2. `[COPY]` **EcoSim** — Sub-heading: **"Compare renewable energy options"**, Description: **"Compare solar, wind, and hydro using local conditions, estimated costs, and possible savings."**
  3. `[COPY]` **AI Explanations** — Sub-heading: **"Understand your results"**, Description: **"Get simple explanations of charts, forecasts, and recommendations."**
  4. `[COPY]` **Data & Charts** — Sub-heading: **"See information clearly"**, Description: **"Turn complex information into maps, graphs, and comparisons that are easier to understand."**

### 2.7 "Technology Stack" Section
- `[FEATURE]` Add a small collapsible/linked section: **"Interested in how LUMI was built?"** with a button **"View Technical Architecture"** (reveals/links to Frontend/Backend/Database/AI & ML stack details currently shown).

### 2.8 "Designed for Real-World Impact" Section
- `[COPY]` Section title → **"Made for Everyone"**
- Update the feature badges/pills into sub-heading + description pairs:
  1. `[COPY]` **"Works on Phones & Computers"** — **"Use LUMI on different screen sizes"**
  2. `[COPY]` **"English & Filipino"** — **"Choose the language you're more comfortable with."**
  3. `[COPY]` **"Easy-to-Read Design"** — **"Clear text, icons, and explanations."**
  4. `[COPY]` **"Light & Dark Modes"** — **"Choose the display that's comfortable for you."**

### 2.9 Final CTA Section
- `[COPY]` Headline stays "Ready to Explore LUMI?" → add/confirm description: **"Check energy and weather information for your area or compare solar, wind, and hydro options."**
- `[COPY]` Button "Try EnergyHub" → **"Explore my Area"**
- `[COPY]` Button "Launch EcoSim" → **"Compare Energy Options"**

---

## 3. EcoSim Page

### 3.1 Page Header
- `[COPY]` Title "Renewable Energy Simulation" → **"Find the Best Renewable Energy Options for your Area"**
- `[COPY]` Description → **"EcoSim looks at your location, electricity use, and local environmental conditions to help estimate which renewable energy option may fit you best."**
- `[COPY]` Step labels (stepper component):
  1. **"Location"**
  2. **"Electricity Use"**
  3. **"Savings Goal"**
  4. **"Review"**

### 3.2 Step 1 — Location
- `[COPY]` Field label "Search mode" → **"Select area type"**
- `[COPY]` Option "Municipality" → **"City/Municipality"**
- `[COPY]` Helper text "Choose municipality for the most accurate local climate data." → **"We use your location to estimate local solar, wind, and water conditions."**

### 3.3 Step 2 — Electricity Use
- `[COPY]` Field label "Monthly consumption (kWh)" → **"Electricity used this billing period (kWh)"**
- `[COPY]` Helper text "Find this on your electric bill..." → **"Look for 'Actual Consumption' on your Meralco bill"**
- `[FEATURE]` Add a **"Where can I find this on my bill?"** help link/modal that shows a sample Meralco bill screenshot with the "Actual Consumption" field circled/highlighted.
- `[UI]` Currency label "PHP" → replace with **"₱"** symbol throughout this step (and anywhere else PHP appears as a label).
- `[COPY]` Rate helper text → **"Based on your inputs, you currently pay about ₱13.66 per kWh. We use this to estimate your possible savings."** (dynamic value, keep bold on the rate figure)

### 3.4 Step 3 — Savings Goal
- `[COPY]` Question text "How much of your bill would you like to eliminate with renewable energy?" → **"How much would you like to reduce your monthly electricity bill?"**
- `[COPY]` Slider labels (left → right): **"Reduce a little"** → **"Reduce more"** → **"Reduce as much as possible"**
- `[FEATURE]` `[OPEN]` Consider adding quick-select buttons for **25% / 50% / 75% / 100%** alongside/instead of manual slider dragging. Confirm with design whether both slider + buttons should coexist or buttons replace slider.
- `[COPY]` Checkbox label "Include AI analysis" → **"Include simple explanation"**
- `[COPY]` Add helper text below checkbox: **"Adds a simple explanation of why a renewable option is recommended for your area."**

### 3.5 Step 4 — Review
- `[FEATURE]` `[OPEN]` Decide on geothermal: either (a) add geothermal support consistently throughout the rest of the system (EnergyHub source comparisons, etc.) or (b) remove geothermal from EcoSim's comparison entirely for consistency. Do not leave it inconsistently mentioned only in EcoSim.
- `[COPY]` Savings goal display "75% — Go almost off-grid" → **"75% - Reduce most of your electricity cost"** (apply equivalent copy pattern to other percentage tiers, consistent with Step 3 slider label rewording).
- `[FEATURE]` Allow users to edit any of their inputs (location, consumption, bill, savings goal) directly from the Review step without navigating back through Steps 1-3 (e.g., inline "Edit" links per field that jump back to that step or allow inline editing with return-to-review).

---

## 4. EnergyHub Page

### 4.1 Page Header
- `[COPY]` Intro copy → **"Explore electricity use, renewable energy, and climate information across the Philippines. See past trends, future estimates, and renewable energy potential for different locations."**
- `[COPY]` Add small text below: **"Data sources: Department of Energy (DOE), IRENA, and NASA POWER."** (this is where the "NGCP & OpenWeather" label removed from Home Section 1.3 should conceptually be replaced/relocated — confirm final source list with Jon, since PDF references DOE/IRENA/NASA POWER here, not NGCP/OpenWeather).
- `[COPY]` Disclaimer → **"For educational use: EnergyHub helps you understand energy information but should not replace professional advice for energy projects or investments."**
- `[FEATURE]` Add a quick navigation row (sticky or top-of-page) with anchor links: **Philippines Overview | Explore Map | Energy Trends | Energy Sources | Regional Data**

### 4.2 National Overview Section (4 stat cards)
1. `[COPY]` "Total Consumption" → **"Electricity use"**
   - Small description: **"Total electricity used across the Philippines in 2025."**
   - `[FEATURE]` Add info tooltip: **"What is GWh?"**
2. `[COPY]` "Peak Demand" → **"Highest electricity demand"**
   - Small description: **"The highest amount of electricity needed at one time during 2025."**
3. `[COPY]` "Renewable Share" description → **"About 1 out of every 4 units of electricity came from renewable sources."**
4. `[OPEN]` "Forecast Growth" description currently shows "+-6.08%" — need to confirm sign convention (positive vs. negative growth) with the data/logic team before finalizing copy and sign display. Flag this as a data-validation task, not just copy.

### 4.3 Provincial Demand Chart ("Electricity Use by Region")
- `[COPY]` Chart title "Provincial Demand (2025)" → **"Electricity Use by Region (2025)"**
- `[UI]` Add a legend above the chart (not just relying on bar color alone).
- `[FEATURE]` Add region full names on hover/tooltip (currently only abbreviated region codes like NCR, IV-A shown on axis).
- `[UI]` Convert the "What you are seeing" and "Why 17 regions?" info blocks into expandable/collapsible sections so they don't take up permanent vertical space.

### 4.4 IRENA Benchmark Section
- `[COPY]` Section title "IRENA Benchmark" → **"Renewable Energy: International Data"**
- `[COPY]` Add explanatory text below title: **"IRENA provides international renewable-energy statistics. Figures may differ from Philippine DOE data because the sources may use different reporting years or definitions."**
- `[FEATURE]` "Latest RE Capacity" — if data is unavailable, display **"Data currently unavailable"** instead of a blank/dash.
- `[COPY]` "Latest RE Generation" → **"Renewable Energy Generation"**; display value as `<data> GWh` with sub-label **"IRENA | Data year: [YYYY]"**
- `[COPY]` "RE Share (latest)" → **"Renewable Energy Share"**; display value as `<data>%` with sub-label **"IRENA | Data year: [YYYY]"**
- `[FEATURE]` Add info tooltip: **"What is IRENA?"** → **"The International Renewable Energy Agency collects renewable-energy statistics from countries around the world."**

### 4.5 Energy Choropleth Map
- `[COPY]` Section title "Energy Choropleth Map" → **"Renewable Energy Potential by Area"**
- `[COPY]` Subtitle → **"See which cities and municipalities have more favorable conditions for solar, wind, or hydro energy."**
- `[UI]` Add label above the "Municipality" dropdown: **"View by:"**
- `[UI]` Add label above the "Solar Potential" dropdown: **"Energy source:"**
- `[FEATURE]` Add a location search input to jump to a specific city/municipality on the map, instead of requiring manual pan/zoom navigation.
- `[OPEN]` Consider adding an AI-generated explanation/insight about the displayed potential score. Not yet confirmed — flag as a design decision pending, don't build until validated.

### 4.6 Energy Trends Section — "Total Electricity Use Over Time" Chart
- `[UI]` `[OPEN]` Investigate making the x-axis (years) show consistently spaced/vertical labels, or reduce label density with intervals (e.g., 2002 | 2005 | 2010...) instead of every single year crowding the axis. Confirm chart library capability before implementing.
- `[COPY]` Info block "What: This chart shows..." → relabel section header **"What you're seeing:"** with content: **"How electricity use in the Philippines has changed over time. The solid line shows recorded data, while the dotted line shows estimated future use."**
- `[COPY]` "Why it matters" copy → **"Changes in electricity use help show whether the country may need more electricity supply in the future."**
- `[COPY]` "What to do" label → relabel as **"Possible takeaway"**
- `[COPY]` Button "AI Explain" → **"Explain this Chart"**

### 4.7 Peak Electricity Demand & Clean Energy Generation Charts (side-by-side)
- `[COPY]` Both charts: relabel "What: This chart shows..." header → **"What you're seeing:"**
- `[COPY]` Both charts: relabel "What to do" → **"Possible takeaway"**
- `[FEATURE]` `[OPEN]` Add ability to enlarge/expand charts (modal or full-width view). Alternative approach also requested: convert each chart section into a **tabbed interface** (button/tab per chart) instead of stacking them — pick one pattern and implement consistently across all trend charts on this page.
- `[COPY]` **Peak Electricity Demand** — description under title: **"The highest amount of electricity the country needed at one time during each year."**
  - `[FEATURE]` Add info tooltip: **"Peak demand means the highest level of electricity being used at one time."**
- `[COPY]` "Clean Energy Generation" → **"Renewable Electricity Generation"**
  - `[COPY]` Description under title: **"Electricity generated from renewable sources such as solar, wind, hydro, geothermal, and biomass."**
- `[COPY]` Both charts: Button "AI Explain" → **"Explain this Chart"**

### 4.8 Energy Source Comparison (Donut Chart)
- `[COPY]` Info block header "What: This chart shows..." → **"What you're seeing:"**
- `[COPY]` "What to do" → **"Main takeaway"**

### 4.9 AI Insight Panel
- `[COPY]` Section title "AI Insight" → **"What the Data Means"**
- `[COPY]` Add small text below title: **"Generated with AI based on the energy information shown above."**
- `[COPY]` Toggle/badge "LLM Mode" → **"Detailed Explanation"**

---

## 5. Cross-Cutting Implementation Notes

- `[UI]` **Citation handling policy (applies sitewide):** Never render raw academic citations (e.g., "(Author et al., Year)") inline in visible body copy. Instead:
  - Use a clickable "View Sources" / "Based on the Philippine and international research" link/badge next to sourced claims.
  - Clicking reveals the citation(s) in a tooltip, accordion, or modal.
  - Maintain a central references/sources page or component ("Our Data & Research") that all these links can point to or expand from.
- `[UI]` **Currency formatting:** Replace all instances of literal "PHP" text with the **₱** symbol across EcoSim and any other page displaying peso amounts.
- `[FEATURE]` **Geothermal consistency `[OPEN]`:** Resolve whether geothermal is a supported energy source across the whole system (EcoSim + EnergyHub + Home marketing copy currently says "Solar, Wind & Hydro" / "3 Energy Sources") or excluded. This affects copy in Section 1.2, 1.3, 1.5, and EcoSim Step 4 — pick one direction and update all affected copy together.
- `[FEATURE]` **Forecast sign convention `[OPEN]`:** Confirm whether Forecast Growth (2030) should be displayed as positive or negative growth before finalizing the stat card and any related copy in EnergyHub Section 4.2.
- `[UI]` **Chart interaction pattern `[OPEN]`:** Decide once (enlarge-on-click modal vs. tabbed chart switcher) and apply the same pattern consistently to: Total Electricity Use chart, Peak Electricity Demand chart, and Clean Energy/Renewable Electricity Generation chart.
