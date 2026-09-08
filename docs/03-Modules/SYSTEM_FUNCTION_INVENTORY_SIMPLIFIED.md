# LUMI System Function Inventory — Simplified Version

**Version:** 1.0 (Simplified)  
**Date:** 2025-06-26  
**Purpose:** A plain-English companion to the technical inventory, written for non-technical readers such as thesis panel members, stakeholders, and reviewers.  
**Scope:** Covers everything LUMI currently does. Features that are only partly built are clearly labeled.

---

## Table of Contents

1. [Part 1: What LUMI Is Made Of](#part-1-what-lumi-is-made-of)
2. [Part 2: Who Uses LUMI](#part-2-who-uses-lumi)
3. [Part 3: What LUMI Can Do](#part-3-what-lumi-can-do)
4. [Part 4: How People Use LUMI (Step by Step)](#part-4-how-people-use-lumi-step-by-step)
5. [Part 5: Where Data Comes From and Where It Goes](#part-5-where-data-comes-from-and-where-it-goes)
6. [Part 6: How the Parts Work Together](#part-6-how-the-parts-work-together)
7. [Part 7: What Information LUMI Stores](#part-7-what-information-lumi-stores)
8. [Part 8: How the AI Chat Works](#part-8-how-the-ai-chat-works)
9. [Part 9: How LUMI Predicts Future Energy Trends](#part-9-how-lumi-predicts-future-energy-trends)
10. [Part 10: Suggested Diagrams for the Thesis](#part-10-suggested-diagrams-for-the-thesis)

---

## Part 1: What LUMI Is Made Of

LUMI is a web application with two main sides: what users see (the front end) and what runs in the background (the back end). The back end talks to a database, a cache system, and several outside services to fetch climate data and power AI responses.

### 1.1 User Login and Account Management

**What it does:** Lets people create accounts, log in, and controls who can see or do what inside LUMI.  
**Who it is for:** Everyone — guests who want to browse, registered users who want to save work, and administrators who manage the system.  
**Key abilities:**
- Sign up with email and password
- Log in with Google (or other social accounts through Supabase — a cloud service that handles user accounts)
- Reset forgotten passwords by email
- Give each user a role: regular user, admin, or developer
- Automatically create a profile when someone signs up

### 1.2 Personal Dashboard

**What it does:** The home screen after logging in. It shows your profile, your saved work, and a quick summary of how good your chosen location is for renewable energy.  
**Who it is for:** Registered users.  
**Key abilities:**
- View and edit your profile (name, photo, organization)
- Pick a favorite municipality (city or town) to track
- See a quick score that averages solar, wind, water, and geothermal potential for that location
- View past simulations you saved
- Jump quickly to EcoSim, AI Chat, or EnergyHub

### 1.3 EcoSim — Renewable Energy Simulator

**What it does:** Lets users enter their electricity bill and location, then estimates how much solar, wind, water, or geothermal energy they could generate locally. It also calculates costs, payback time, and carbon savings.  
**Who it is for:** All visitors (guests can try it; registered users can save results).  
**Key abilities:**
- Choose any municipality in the Philippines
- Enter monthly bill, electricity rate, and how much savings you want
- Calculate potential solar output based on sunshine, temperature, and panel performance
- Calculate potential wind power based on wind speed and air density
- Calculate potential small hydropower based on rainfall, slope, and terrain
- Calculate potential geothermal output based on underground heat and nearby fault lines
- Show a financial breakdown: cost per kilowatt-hour, installation estimate, payback period
- Estimate how much CO2 you would avoid by switching to renewable energy
- Get an AI-written recommendation based on your results

### 1.4 EnergyHub — National Energy Dashboard

**What it does:** Displays big-picture energy data for the whole Philippines: total energy use, how much comes from coal vs. renewables, forecasts for future demand, and an interactive map showing which areas are best for renewable energy.  
**Who it is for:** All visitors.  
**Key abilities:**
- Overview panel: total consumption, peak demand, total generation
- Historical trends: line charts showing how energy use changed over the years
- Forecasts: predicted energy consumption and peak demand for the next ~15 years
- Choropleth map (a color-coded map): click a region to see how suitable it is for solar, wind, water, or geothermal power
- Energy source breakdown: pie or bar charts showing how much of the grid comes from coal, natural gas, oil, hydro, geothermal, wind, solar, and biomass
- AI-generated insights for charts

### 1.5 Geothermal Explorer

**What it does:** Focuses specifically on geothermal energy. It lists known geothermal plants in the Philippines and can analyze any municipality for underground heat potential.  
**Who it is for:** All visitors.  
**Key abilities:**
- Browse a list of geothermal power plants
- Search any municipality to get a geothermal suitability score
- See estimates for underground reservoir temperature, thermal power, and electric power
- View province-level summaries of geothermal activity

### 1.6 LUMI AI Chat Assistant

**What it does:** A chatbot that answers questions about renewable energy in the Philippines. It searches through LUMI's own knowledge base before answering, so replies are grounded in real data rather than guessing.  
**Who it is for:** All visitors.  
**Key abilities:**
- Ask questions in plain English (e.g., "Is wind power good in Batangas?")
- Receive answers that include source citations (where the information came from)
- See structured responses: observation, interpretation, recommendation, and reason
- Sources include government energy reports, NASA climate data, and product pricing from e-commerce sites

**Note:** Saving chat history is only partly built. The database tables exist, but the current public version keeps chats in memory rather than storing them permanently.

### 1.7 Admin Control Panel

**What it does:** A special area only visible to administrators where they can manage users, view system activity, and change settings.  
**Who it is for:** Administrators and developers only.  
**Key abilities:**
- View all registered users and their roles
- Ban or unban users
- Change a user's role or subscription plan
- View system-wide statistics (how many users, how many simulations)
- Change global settings (e.g., turn the chatbot on or off, set usage limits)
- Review flagged chat sessions for moderation
- Every admin action is recorded in an audit log that cannot be changed

### 1.8 Suitability Engine

**What it does:** Runs in the background to score every municipality in the Philippines for how good it is for each type of renewable energy.  
**Who it is for:** The system itself (used by EcoSim, EnergyHub, and the Dashboard).  
**Key abilities:**
- Batch-calculate scores for all municipalities using climate and terrain data
- Classify each location as Excellent, Good, Moderate, Poor, or Unsuitable
- Store results so maps and simulations load quickly
- Cache frequently requested data in a fast temporary store (Redis — a high-speed memory database) so users do not wait

### 1.9 Energy Forecasting (Machine Learning)

**What it does:** Uses past energy data to predict future trends for the Philippines.  
**Who it is for:** The system itself (shown to users through EnergyHub charts).  
**Key abilities:**
- Load pre-computed predictions from files
- Serve forecasts for total energy consumption and peak electricity demand
- Show confidence bands (a range showing how uncertain the prediction is)
- Keep a registry of which prediction model is currently active

### 1.10 Data Import and Preparation Pipeline

**What it does:** Gathers raw information from outside sources, cleans it, and prepares it so the rest of LUMI can use it.  
**Who it is for:** The system itself and administrators who run updates.  
**Key abilities:**
- Fetch climate data from NASA for every municipality
- Extract energy statistics from Department of Energy (DOE) reports
- Scrape renewable energy product prices from online marketplaces
- Build a searchable knowledge library from all of the above
- Create a vector search index (FAISS — a tool for finding similar text quickly) so the AI chat can retrieve relevant facts
- Compute terrain metrics from elevation maps

---

## Part 2: Who Uses LUMI

### 2.1 Guest — Someone Who Has Not Logged In

**What they can do:**
- Browse the public pages: Home, EcoSim, EnergyHub, Geothermal Explorer, and AI Chat
- Run simulations as a visitor (but cannot save them)
- Ask the AI assistant questions
- View public energy statistics and maps

**What they cannot do:**
- Save simulations
- See a personal dashboard
- Access the admin panel

### 2.2 Registered User — Someone With an Account

**What they can do:**
- Everything a guest can do
- Save simulation results to their account
- Set a preferred municipality and see a personalized score on their dashboard
- Edit their profile (name, photo, organization)
- View their saved simulation history

### 2.3 Administrator — System Manager

**What they can do:**
- Everything a registered user can do
- View and manage all user accounts
- Ban or unban users
- Change user roles and plans
- View system-wide statistics
- Change global settings
- Review flagged chat sessions
- View an unchangeable log of every admin action

### 2.4 External Data Sources — Systems That Feed Data Into LUMI

These are not people, but they are important "actors" because they constantly send information into LUMI:

- **NASA POWER:** Sends weather and climate data (temperature, sunshine, wind, rainfall, air density) for every location in the Philippines.
- **Department of Energy (DOE):** Sends official energy statistics — how much electricity the country used, how much was generated, and what fuel types were used.
- **Global Energy Monitor / IHFC:** Sends data about geothermal plants and underground heat measurements.
- **Online Marketplaces:** Send product listings and prices for solar panels, wind turbines, and other renewable equipment.
- **Groq / Google Gemini:** These are AI services that generate text responses for the chatbot.

### 2.5 Quick Reference: Who Can Do What

| Feature | Guest | Registered User | Admin |
|---|---|---|---|
| Browse public pages | Yes | Yes | Yes |
| Run EcoSim simulation | Yes | Yes | Yes |
| Save simulation | No | Yes | Yes |
| View dashboard | No | Yes | Yes |
| Edit profile | No | Yes | Yes |
| Use AI chat | Yes | Yes | Yes |
| Access admin panel | No | No | Yes |
| Manage users | No | No | Yes |
| Change system settings | No | No | Yes |

---

## Part 3: What LUMI Can Do

This section lists LUMI's features in plain language. Each feature includes what it does, who uses it, what information goes in, and what comes out.

### 3.1 Account and Login Features

**Sign Up (Email and Password)**
- **What it does:** Creates a new account.
- **Who uses it:** New visitors.
- **What happens:** The visitor fills out a form. The system checks the email is new, creates the account, and automatically makes a profile and assigns the "user" role.
- **Input:** Email address and password.
- **Output:** New account + profile.
- **Status:** Fully built.

**Log In**
- **What it does:** Opens an existing account.
- **Who uses it:** Returning users.
- **What happens:** The user enters email and password. The system checks them and returns a secure session token (a digital pass that proves the user is logged in).
- **Input:** Email and password.
- **Output:** Access to the account.
- **Status:** Fully built.

**Log In With Google**
- **What it does:** Creates or opens an account using a Google account instead of a password.
- **Who uses it:** New or returning users.
- **What happens:** The user clicks the Google button. Google confirms their identity. LUMI creates a profile if this is the first time.
- **Input:** Google account confirmation.
- **Output:** Access to the account.
- **Status:** Fully built.

**Forgot Password**
- **What it does:** Sends a password reset link by email.
- **Who uses it:** Users who forgot their password.
- **What happens:** The user enters their email. The system sends a secure reset link.
- **Input:** Email address.
- **Output:** Email with reset link.
- **Status:** Fully built.

**View My Profile**
- **What it does:** Shows the user's account details.
- **Who uses it:** Logged-in users.
- **What happens:** The dashboard page asks the system for the user's profile and displays it.
- **Input:** Session token.
- **Output:** Name, photo, organization, location, plan, status.
- **Status:** Fully built.

**Edit My Profile**
- **What it does:** Lets users update their name, organization, or preferred municipality.
- **Who uses it:** Logged-in users.
- **What happens:** The user edits a form and clicks save. The system updates the stored profile.
- **Input:** Updated name, organization, preferred municipality.
- **Output:** Updated profile.
- **Status:** Fully built.

### 3.2 Dashboard Features

**Load My Dashboard**
- **What it does:** Shows the user's personal home screen.
- **Who uses it:** Logged-in users.
- **What happens:** The system fetches the user's profile, saved simulations, and preferred municipality scores all at the same time. It then displays a profile card, a list of past simulations, and a quick renewable energy score.
- **Input:** User ID.
- **Output:** Dashboard page content.
- **Status:** Fully built.

**View My Saved Simulations**
- **What it does:** Lists all EcoSim runs the user has saved.
- **Who uses it:** Logged-in users.
- **What happens:** The system looks up all simulation records tied to this user.
- **Input:** User ID.
- **Output:** List of past simulations with names and dates.
- **Status:** Fully built.

**View My Composite Score**
- **What it does:** Shows an overall renewable energy score for the user's chosen location.
- **Who uses it:** Logged-in users who selected a municipality.
- **What happens:** The system fetches solar, wind, water, and geothermal scores and averages them.
- **Input:** Municipality ID.
- **Output:** Average score and classification (Excellent, Good, etc.).
- **Status:** Fully built.

### 3.3 EcoSim — Simulation Features

**Get Municipality List**
- **What it does:** Loads the dropdown of all Philippine municipalities.
- **Who uses it:** Anyone using EcoSim.
- **What happens:** The system returns a list of all cities and towns from its database.
- **Input:** None.
- **Output:** List of municipality names.
- **Status:** Fully built.

**Run a Simulation**
- **What it does:** Calculates renewable energy potential for a chosen location.
- **Who uses it:** All visitors.
- **What happens:**
  1. The user picks a municipality and enters their monthly bill, electricity rate, and savings goal.
  2. The system fetches climate data for that location.
  3. It calculates solar output using sun intensity, temperature, humidity, and panel degradation.
  4. It calculates wind output using wind speed, air density, and turbine size.
  5. It calculates hydropower using rainfall, slope, and runoff.
  6. It calculates geothermal potential using underground heat and distance to faults or volcanoes.
  7. It converts the bill into kilowatt-hours and compares it to what each renewable source could produce.
  8. It estimates installation cost, cost per kilowatt-hour, and payback period.
  9. It estimates CO2 reduction.
  10. If requested, it asks the AI to write a recommendation.
- **Input:** Municipality, monthly bill, electricity rate, savings percentage, optional AI flag.
- **Output:** Detailed results for solar, wind, water, and geothermal; financial summary; optional AI recommendation.
- **Status:** Fully built.

**Save a Simulation**
- **What it does:** Stores a simulation result so the user can view it later.
- **Who uses it:** Logged-in users.
- **What happens:** The system saves the inputs and results into the user's account.
- **Input:** Simulation data.
- **Output:** Confirmation that it was saved.
- **Status:** Fully built.

**View Saved Simulation**
- **What it does:** Opens a previously saved simulation.
- **Who uses it:** Logged-in users.
- **What happens:** The system retrieves the stored simulation and displays it.
- **Input:** Simulation ID.
- **Output:** Full simulation record.
- **Status:** Fully built.

### 3.4 EnergyHub — National Dashboard Features

**Get National Overview**
- **What it does:** Shows headline numbers for the Philippines' energy situation.
- **Who uses it:** All visitors.
- **What happens:** The system reads the most recent official energy statistics.
- **Input:** None.
- **Output:** Total consumption, peak demand, total generation, year-over-year change.
- **Status:** Fully built.

**Get Historical Trends**
- **What it does:** Shows how energy use has changed over time.
- **Who uses it:** All visitors.
- **What happens:** The system filters historical data by the years the user selected.
- **Input:** Start year, end year, metric type.
- **Output:** Time series data for charts.
- **Status:** Fully built.

**Get Forecast**
- **What it does:** Shows predicted future energy consumption or peak demand.
- **Who uses it:** All visitors.
- **What happens:** The system loads pre-computed predictions and returns them as chart data.
- **Input:** Target variable (consumption or demand), forecast year.
- **Output:** Predicted value plus upper and lower confidence limits.
- **Status:** Fully built.

**Get Choropleth Map Data**
- **What it does:** Prepares the color-coded map of the Philippines.
- **Who uses it:** All visitors.
- **What happens:** The system first checks its fast cache (Redis). If the data is not there, it queries the database, groups scores by region, and stores the result in the cache for next time.
- **Input:** Metric type (solar/wind/water/geothermal/composite), geographic level (municipality or province).
- **Output:** List of locations with coordinates and color scores.
- **Status:** Fully built.

**Get Energy Source Breakdown**
- **What it does:** Shows how much electricity comes from each fuel type.
- **Who uses it:** All visitors.
- **What happens:** The system reads the official generation-by-source statistics.
- **Input:** Optional year filter.
- **Output:** Percentages and amounts for coal, gas, oil, hydro, geothermal, wind, solar, biomass.
- **Status:** Fully built.

**Get AI Chart Insights**
- **What it does:** Asks the AI to explain what a chart means.
- **Who uses it:** All visitors.
- **What happens:** The system sends chart data to the AI, gets back a plain-language explanation, and caches it so the same chart does not need to be analyzed twice.
- **Input:** Chart type and data.
- **Output:** AI-written insight text.
- **Status:** Fully built.

### 3.5 Geothermal Explorer Features

**Browse Geothermal Plants**
- **What it does:** Shows a list of known geothermal power plants in the Philippines.
- **Who uses it:** All visitors.
- **What happens:** The system reads from its geothermal plant database.
- **Input:** None.
- **Output:** List of plants with names, locations, and capacities.
- **Status:** Fully built.

**Analyze a Municipality for Geothermal Potential**
- **What it does:** Scores any municipality for underground heat potential.
- **Who uses it:** All visitors.
- **What happens:** The system checks if it already has a score saved. If not, it calculates one on the spot using heat flow data, fault distances, and temperature.
- **Input:** Municipality name.
- **Output:** Suitability score, classification, estimated reservoir temperature, power output.
- **Status:** Fully built.

**Get Province Summary**
- **What it does:** Summarizes geothermal activity for an entire province.
- **Who uses it:** All visitors.
- **What happens:** The system adds up data from all municipalities in that province.
- **Input:** Province name.
- **Output:** Number of plants, total capacity, average score.
- **Status:** Fully built.

### 3.6 AI Chat Features

**Send a Message to the AI**
- **What it does:** Answers a user's question using LUMI's own knowledge.
- **Who uses it:** All visitors.
- **What happens:**
  1. The user types a question.
  2. The system turns the question into a numeric fingerprint using a small language model called SentenceTransformer.
  3. It searches the FAISS index — a fast search tool that finds the most similar pieces of text from LUMI's knowledge library.
  4. It collects the top matching facts.
  5. It builds a prompt that includes a system personality, the matched facts, and the user's question.
  6. It sends the prompt to Groq (a fast AI service) using the Llama 3 model.
  7. It receives a raw text response.
  8. It cleans the response: removes code blocks, fixes formatting, and extracts structured sections.
  9. It attaches source citations.
  10. It sends the clean answer back to the user.
- **Input:** User's question text.
- **Output:** AI answer, source citations, structured sections.
- **Status:** Fully built.

**View Chat History**
- **What it does:** Lists past chat conversations.
- **Who uses it:** Logged-in users.
- **What happens:** The system would query the database for past sessions.
- **Status:** Only partly built. The database tables exist, but the public version keeps chats in memory rather than storing them.

### 3.7 Admin Features

**View All Users**
- **What it does:** Shows every registered account.
- **Who uses it:** Administrators.
- **What happens:** The system checks the admin is really an admin, then returns a list of all users with their roles and plans.
- **Input:** Admin session.
- **Output:** Paginated user list.
- **Status:** Fully built.

**Create a User**
- **What it does:** Adds a new account manually.
- **Who uses it:** Administrators.
- **What happens:** The admin fills out a form. The system creates the account and auto-creates a profile.
- **Input:** Email, password, role, plan, name.
- **Output:** New user confirmation.
- **Status:** Fully built.

**Ban / Unban a User**
- **What it does:** Disables or re-enables an account.
- **Who uses it:** Administrators.
- **What happens:** The system marks the account as inactive or active and records the action in the audit log.
- **Input:** Target user ID.
- **Output:** Confirmation.
- **Status:** Fully built.

**Change User Role or Plan**
- **What it does:** Promotes or demotes a user, or switches their subscription.
- **Who uses it:** Administrators.
- **What happens:** The system updates the role or plan field and logs the change.
- **Input:** Target user ID, new role or plan.
- **Output:** Confirmation.
- **Status:** Fully built.

**View System Analytics**
- **What it does:** Shows how many people use LUMI and how active they are.
- **Who uses it:** Administrators.
- **What happens:** The system counts users, simulations, and chats.
- **Input:** Date range.
- **Output:** Metrics dashboard.
- **Status:** Fully built.

**Change System Settings**
- **What it does:** Toggles features like chatbot availability or maintenance mode.
- **Who uses it:** Administrators.
- **What happens:** The system updates a settings table and logs the change.
- **Input:** Setting name and new value.
- **Output:** Updated settings.
- **Status:** Fully built.

**Review Flagged Chats**
- **What it does:** Shows chat sessions that may need moderation.
- **Who uses it:** Administrators.
- **What happens:** The system lists sessions marked with a flag.
- **Status:** Only partly built. The flagging field exists and the admin page is there, but automatic flagging logic is basic.

### 3.8 Background Score Calculator

**Calculate All Municipality Scores**
- **What it does:** Computes renewable energy scores for every municipality in the Philippines.
- **Who uses it:** Run automatically by the system or triggered by an admin.
- **What happens:** For each municipality, the system fetches climate data, calculates solar, wind, water, and geothermal scores, classifies each, and stores the results.
- **Input:** Climate data, terrain data, heat flow data.
- **Output:** Updated database tables and cached scores.
- **Status:** Fully built.

**Calculate Score for One Municipality**
- **What it does:** Computes scores on demand when cached data is missing.
- **Who uses it:** The system itself.
- **What happens:** Same as the batch version but for one location only.
- **Input:** Municipality ID.
- **Output:** Single score set.
- **Status:** Fully built.

### 3.9 Forecasting (Machine Learning) Features

**Load Forecasts**
- **What it does:** Reads pre-computed prediction files into memory.
- **Who uses it:** The system itself.
- **What happens:** The system reads CSV files created by offline training notebooks.
- **Input:** File path.
- **Output:** Forecast data in memory.
- **Status:** Fully built.

**Get a Specific Forecast**
- **What it does:** Returns a single predicted value.
- **Who uses it:** The system (via EnergyHub).
- **What happens:** The system looks up the requested year and variable in the loaded forecast data.
- **Input:** Variable name, forecast year.
- **Output:** Predicted value with confidence range.
- **Status:** Fully built.

### 3.10 Data Import Features

**Fetch NASA Climate Data**
- **What it does:** Downloads weather averages for every municipality.
- **Who uses it:** System scheduled task or admin script.
- **What happens:** The system sends coordinates to NASA's POWER API and stores the results.
- **Input:** Coordinates, API key, year range.
- **Output:** Climate records for every municipality.
- **Status:** Fully built.

**Clean Scraped Product Data**
- **What it does:** Organizes messy product data from online stores.
- **Who uses it:** System pipeline.
- **What happens:** Parses raw files, fixes prices, removes duplicates, standardizes units.
- **Input:** Raw scraped files.
- **Output:** Clean product listing file.
- **Status:** Fully built.

**Build Knowledge Chunks**
- **What it does:** Combines all LUMI data sources into small, searchable fact blocks.
- **Who uses it:** System startup.
- **What happens:** Loads products, energy statistics, climate averages, terrain data, and suitability scores. Groups them into short chunks by topic and labels each with its source.
- **Input:** All cleaned data files.
- **Output:** A file of searchable knowledge snippets.
- **Status:** Fully built.

**Build Search Index**
- **What it does:** Creates the fast search index the AI chat uses.
- **Who uses it:** System startup.
- **What happens:** Loads knowledge chunks, converts each to a numeric vector, and builds a FAISS index.
- **Input:** Knowledge chunks, embedding model.
- **Output:** Search index files.
- **Status:** Fully built.

**Calculate Terrain Metrics**
- **What it does:** Measures elevation, slope, and water flow potential for every municipality.
- **Who uses it:** Admin script.
- **What happens:** Reads a digital elevation map of the Philippines, measures each municipality's height and steepness, and estimates water runoff.
- **Input:** Elevation map, municipality boundaries.
- **Output:** Terrain metrics file or database table.
- **Status:** Fully built.

---

## Part 4: How People Use LUMI (Step by Step)

### 4.1 How to Sign Up and Log In

1. A visitor opens the LUMI website.
2. They click "Sign Up" and fill in their email and password, or click "Log In With Google."
3. If signing up by email, the system checks the email is new, creates the account, and automatically makes a profile.
4. If logging in, the system checks the password or Google confirmation.
5. The system returns a secure session token.
6. The front end stores this token so the user stays logged in.
7. The user is redirected to their dashboard or back to the page they came from.

**Decisions along the way:**
- Is this email already used? → Show an error.
- Is the password strong enough? → The form checks before sending.
- Did the user sign up with Google? → The system copies their profile photo.

### 4.2 How the Dashboard Works

1. A logged-in user clicks "Dashboard."
2. The system checks they are logged in. If not, it sends them to the login page.
3. The dashboard loads the user's profile, saved simulations, and preferred municipality all at once.
4. If the user picked a municipality, the system fetches that location's renewable energy scores and shows an average.
5. The dashboard displays: a profile card, a list of past simulations, a score gauge, and quick links to other tools.

**Decisions along the way:**
- Is the user logged in? → Route guard handles this.
- Does the user have saved simulations? → Show them or show an empty message.
- Did the user pick a favorite municipality? → Show the score or suggest picking one.

### 4.3 How to Run a Renewable Energy Simulation

1. The user opens EcoSim and sees a list of Philippine municipalities.
2. They pick their location.
3. They enter: monthly electricity bill, cost per kilowatt-hour, and how much they want to save.
4. They click "Simulate."
5. The system fetches weather data for that location.
6. It calculates how much solar, wind, water, and geothermal energy that location could produce.
7. It works out the cost, payback time, and carbon savings.
8. If the user asked for an AI recommendation, the system sends the results to the AI and gets back tailored advice.
9. The results appear as cards showing each energy source's potential.
10. If logged in, the user can click "Save" to store the simulation.

**Decisions along the way:**
- Is the location real? → Error if not found.
- Is weather data available? → Use defaults or show a warning.
- Is the user logged in? → Enable or disable the Save button.
- Did they ask for AI help? → Include or skip the recommendation.

### 4.4 How the Color-Coded Map Works

1. The user opens EnergyHub and clicks the Map tab.
2. They choose a renewable energy type (solar, wind, water, geothermal, or overall).
3. They pick whether to see municipalities or provinces.
4. The system first checks its fast cache. If the data is there, it returns it immediately.
5. If not, it queries the database, groups the scores, and saves the result in the cache.
6. The map colors each region: green for excellent, yellow for moderate, red for unsuitable.
7. Hovering over a region shows its name, score, and classification.

**Decisions along the way:**
- Is the data cached? → Fast response or database lookup.
- Is there no data for this area? → Show gray.
- Municipality or province view? → Different grouping logic.

### 4.5 How Forecasting Charts Work

1. The user opens EnergyHub and selects the Forecast view.
2. The front end asks the back end for future energy predictions.
3. The system loads pre-computed prediction files that were created offline.
4. It returns the predicted values plus upper and lower confidence bands.
5. The front end draws a line chart: solid line for past data, dashed line for predictions, shaded area for uncertainty.
6. The user can switch between total consumption and peak demand.

**Decisions along the way:**
- Are prediction files available? → Load them or show an error.
- Is the requested metric valid? → Reject unknown requests.

### 4.6 How the AI Chat Answers Questions

1. The user types a question and presses Enter.
2. The front end sends the question to the back end.
3. The back end turns the question into a numeric fingerprint using a small language model.
4. It searches LUMI's knowledge library for the most similar facts.
5. It collects the top matches.
6. It builds a detailed prompt that includes a system personality, the matched facts, and the user's question.
7. It sends the prompt to the Groq AI service.
8. The AI returns a raw text answer.
9. The system cleans the answer: removes code blocks, fixes spacing, and pulls out structured sections.
10. It adds source citations.
11. The clean answer appears on screen, broken into observation, interpretation, recommendation, and reason.

**Decisions along the way:**
- Is the knowledge library ready? → If not, answer from general knowledge.
- Were any relevant facts found? → Filter out poor matches.
- Did the AI return messy formatting? → The cleaning pipeline fixes it.
- Is the user logged in? → Skip saving the chat in the public version.

### 4.7 How Exporting Works

1. The user clicks an "Export" or "Download" button.
2. The front end gathers the current results into a text or JSON file.
3. The browser downloads the file.

**Note:** There is no PDF generation or email delivery yet. Only simple file downloads are available.

---

## Part 5: Where Data Comes From and Where It Goes

### 5.1 Sources That Send Data Into LUMI

LUMI does not create all of its own data. It regularly pulls information from outside organizations and services:

- **NASA POWER:** Provides weather and climate data for every municipality in the Philippines. This includes temperature, sunshine hours, wind speed, rainfall, humidity, and air density. The system sends municipality coordinates to NASA's API and stores the results.

- **Department of Energy (DOE):** Provides official Philippine energy statistics. These include total electricity consumption, peak demand, total generation, and how much electricity comes from each fuel type (coal, natural gas, oil, hydro, geothermal, wind, solar, biomass). These numbers come from DOE reports and are extracted using automated scripts.

- **Geothermal Databases (Global Energy Monitor, IHFC):** Provide locations and details of geothermal power plants, plus underground heat flow measurements used to score municipalities for geothermal potential.

- **Online Marketplaces:** Provide product listings and prices for renewable energy equipment such as solar panels, wind turbines, batteries, and inverters. These are collected using web scraping scripts.

- **Digital Elevation Model:** A map of the Philippines showing ground height everywhere. Used to calculate slope, ruggedness, and water runoff potential for every municipality.

### 5.2 What LUMI Does With the Data

**Climate Data:**
- NASA sends raw weather data → LUMI cleans and stores it per municipality → used by EcoSim to calculate solar, wind, and hydropower potential.

**Energy Statistics:**
- DOE reports are extracted into tables → stored in the database → shown on EnergyHub charts and used for historical trends.

**Product Pricing:**
- Scraped product data is cleaned and normalized → combined into a knowledge library → used by the AI chat to answer cost-related questions.

**Geothermal Data:**
- Plant locations and heat flow data are stored → used to score municipalities and show plant lists.

**Terrain Data:**
- Elevation maps are processed into metrics → stored per municipality → used for hydropower scoring and watershed analysis.

### 5.3 Where Data Goes After Processing

**To the Database:** Most structured data ends up in PostgreSQL tables hosted on Supabase. This includes user profiles, municipality scores, climate records, energy statistics, saved simulations, and chat records.

**To the Cache:** Frequently requested data (like map color scores) is stored in Redis, a fast memory database, so users do not have to wait for slow database queries.

**To the Search Index:** The AI chat's knowledge library is turned into a FAISS search index — a special file that lets the system find relevant facts in milliseconds.

**To the User:** Processed results are sent back to the web browser as web pages, charts, map colors, and chat messages.

---

## Part 6: How the Parts Work Together

LUMI is like a team of specialists who pass information to each other. Here is how the main modules communicate:

**The Front End (what users see) talks to the Back End (the server) through the internet.**
- When a user clicks a button or submits a form, the front end sends a message to the back end.
- The back end processes the request, talks to databases or external services, and sends a response back.
- The front end then updates the screen with the new information.

**Auth and Login talk to the User Database.**
- When someone signs up, the login system creates an account in Supabase Auth.
- A database trigger automatically creates a profile and assigns the "user" role.
- The front end stores a session token so the user stays logged in.

**EcoSim talks to the Climate Database and Calculation Services.**
- When a user runs a simulation, EcoSim fetches weather data for the chosen municipality.
- It then asks four calculation services to estimate solar, wind, water, and geothermal output.
- If the user is logged in, the results can be saved to the Saved Simulations table.

**EnergyHub talks to the Energy Statistics Database, the Cache, and the AI.**
- When a user views charts or maps, EnergyHub first checks the fast cache (Redis).
- If the data is not cached, it queries the database for historical statistics or municipality scores.
- For AI chart insights, it sends chart data to the AI service and caches the result.

**The AI Chat talks to the Search Index and the AI Service.**
- When a user asks a question, the chat system turns it into a numeric fingerprint.
- It searches the FAISS index for the most similar facts from LUMI's knowledge library.
- It sends those facts plus the question to the Groq AI service.
- The AI returns an answer, which is cleaned, structured, and shown to the user with source citations.

**The Admin Panel talks to the User Database and Audit Log.**
- When an admin makes a change (banning a user, changing a role, updating settings), the system records the action in an unchangeable audit log.

**The Suitability Engine talks to the Climate Database, Terrain Data, and the Cache.**
- It computes scores for every municipality and stores them.
- Frequently requested scores are also stored in Redis so maps and dashboards load quickly.

**The Data Pipeline talks to Outside Sources and the Database.**
- It fetches raw data from NASA, DOE, online stores, and elevation maps.
- It cleans the data and stores it in the database or in files.
- It builds the knowledge library and the FAISS search index so the AI chat can answer questions.

---

## Part 7: What Information LUMI Stores

LUMI stores information in a PostgreSQL database (hosted on Supabase). Here is what it keeps, organized by topic.

### 7.1 Geographic Information

- **Regions:** The top-level divisions of the Philippines (e.g., Luzon, Visayas, Mindanao groups).
- **Provinces:** The next level down (e.g., Batangas, Cebu, Davao del Sur).
- **Municipalities:** Cities and towns. This is the central unit of analysis. Each record includes coordinates and pre-computed renewable energy scores (solar, wind, water, geothermal, and an overall average).
- **Barangays:** Villages within municipalities. Stored for reference and potential future use.

### 7.2 Weather and Climate Data

- **Monthly climate averages per municipality:** Temperature, maximum and minimum temperature, humidity, rainfall, wind speed, sunshine hours, cloud cover, air pressure, elevation, and air density. Sourced from NASA POWER.

### 7.3 Renewable Energy Scores

- **Solar suitability:** Score, classification, average sun intensity, and estimated panel output per municipality.
- **Wind suitability:** Score, classification, average wind speed, air density, and estimated turbine output per municipality.
- **Hydropower suitability:** Score, classification, elevation, slope, hydraulic head, terrain ruggedness, watershed gradient, and estimated power potential per municipality.
- **Geothermal suitability:** Score, classification, underground heat flow, fault density, volcano proximity, and surface temperature per municipality.
- **Geothermal output estimates:** Reservoir temperature, flow rate, thermal power, electric power, and annual energy production per municipality.

### 7.4 National Energy Statistics

- **Annual energy records:** Total consumption, residential/commercial/industrial breakdown, total generation, peak demand, and generation by fuel type (coal, natural gas, oil, hydro, geothermal, wind, solar, biomass) for each year.
- **Forecast cache:** Pre-computed prediction values with upper and lower confidence limits.
- **Model registry:** Which prediction model is active, when it was trained, what its settings were, and how accurate it was.

### 7.5 User Information

- **Profiles:** Extended user details — name, photo, organization, location, preferred municipality, subscription plan, and whether the account is active.
- **User roles:** Whether someone is a regular user, admin, or developer.
- **Saved simulations:** The inputs and results of EcoSim runs that users chose to save.
- **Chat sessions and messages:** Conversation threads and individual messages. These tables exist but are only partly used in the current public version.

### 7.6 Admin and System Records

- **Audit log:** A permanent record of every admin action (who did what, when, and to whom). Cannot be changed.
- **System config:** Global settings like whether the chatbot is enabled, maintenance mode, and usage limits.

### 7.7 AI and Cache Records

- **Chart AI insights:** Cached AI-written explanations for charts so the same chart does not need to be analyzed twice.
- **Regional lookup view:** A combined view that links regions, provinces, municipalities, and barangays for easy searching.

### 7.8 Automatic Database Rules

- **Classification function:** Automatically turns a numeric score into a word label (Excellent, Good, Moderate, Poor, Unsuitable).
- **Auto-timestamp triggers:** Automatically update the "last modified" time when certain records change.
- **Auto-create profile trigger:** Automatically makes a profile and assigns a role whenever a new user signs up.

---

## Part 8: How the AI Chat Works

The LUMI AI Chat is not a simple chatbot that makes up answers. It is a Retrieval-Augmented Generation (RAG) system — meaning it searches LUMI's own knowledge library before answering, so its replies are grounded in real data.

### 8.1 The Big Picture

```
User types a question
    ↓
Front end sends it to the back end
    ↓
Back end turns the question into a numeric fingerprint
    ↓
Search the knowledge library for the most similar facts
    ↓
Collect the top matching facts
    ↓
Build a detailed prompt with a system personality, the facts, and the question
    ↓
Send the prompt to the Groq AI service
    ↓
AI returns a raw answer
    ↓
Clean the answer, extract structured sections, and add source citations
    ↓
Show the clean answer to the user
```

### 8.2 Step by Step

**Step 1: The user asks a question.**
- Example: "Is wind power good in Batangas?"

**Step 2: The system turns the question into a numeric fingerprint.**
- It uses a small language model called SentenceTransformer to convert the question into a 384-dimensional vector — a mathematical fingerprint that captures the meaning of the words.

**Step 3: Search the knowledge library.**
- The system loads a FAISS index — a special search file that stores numeric fingerprints of all knowledge chunks.
- It searches for the chunks whose fingerprints are most similar to the question's fingerprint.
- It collects the top 5 most relevant facts.

**Step 4: Build the prompt.**
- The system assembles a detailed prompt that includes:
  - A system personality: "You are LUMI, an expert renewable energy assistant for the Philippines."
  - The matched facts, labeled with their sources.
  - The user's original question.
  - Instructions: "Answer in plain text. Cite your sources. Structure your answer as Observation, Interpretation, Recommendation, and Reason."

**Step 5: Send to the AI service.**
- The prompt is sent to Groq, a fast AI service that runs the Llama 3 language model.
- If Groq is unavailable, the system can fall back to Google Gemini.

**Step 6: Receive and clean the answer.**
- The AI returns raw text, which may contain formatting artifacts like code blocks or JSON wrappers.
- The system strips these out, normalizes spacing, and extracts the four structured sections.

**Step 7: Add citations.**
- The system maps the matched chunks to their original sources (e.g., DOE report, NASA data, marketplace listing) and appends a "Sources" section.

**Step 8: Display to the user.**
- The front end shows the answer with bold headings for each section and clickable source chips.

### 8.3 Variants

**Chart Analysis:** When a user clicks "Analyze with AI" on a chart, the system sends the chart data to the AI and gets back a plain-language explanation. The result is cached so the same chart does not need to be analyzed twice.

**EcoSim Recommendation:** When a user runs a simulation with AI enabled, the system sends the simulation results to the AI and gets back a tailored recommendation.

---

## Part 9: How LUMI Predicts Future Energy Trends

LUMI does not predict the future in real time. Instead, it uses a machine learning model that was trained offline on historical data, and then serves those pre-computed predictions through the EnergyHub dashboard.

### 9.1 The Big Picture

```
DOE energy reports (PDFs and Excel files)
    ↓
Automated extraction scripts pull out the numbers
    ↓
Data cleaning notebook fixes formatting and inconsistencies
    ↓
Feature engineering prepares the data for modeling
    ↓
Offline training notebook builds an ARIMA model
    ↓
Model generates predictions for the next ~15 years
    ↓
Predictions are saved as CSV files
    ↓
Model registry records which model is active
    ↓
EnergyHub loads the predictions and shows them as charts
    ↓
User sees historical data + forecast line + confidence band
```

### 9.2 What ARIMA Means (In Simple Terms)

ARIMA stands for AutoRegressive Integrated Moving Average. It is a classic statistical method for forecasting time series — data that changes over time, like annual energy consumption.

- **AutoRegressive (AR):** The model looks at past values to predict the next one. The "1" means it uses the value from one year ago.
- **Integrated (I):** The model differences the data — it looks at how much values change from year to year rather than the raw values. The "1" means it does this once. This helps when the overall trend is rising or falling.
- **Moving Average (MA):** The model considers past prediction errors to adjust future predictions. The "1" means it uses the error from one year ago.

The model used by LUMI is ARIMA(1,1,1), which means one autoregressive term, one differencing, and one moving average term.

### 9.3 Why ARIMA Was Chosen

- **Interpretable:** Unlike black-box neural networks, ARIMA has clear parameters that analysts can understand.
- **Effective for annual data:** It works well when you have a long history of yearly observations but not enough data for complex deep learning models.
- **Widely used:** ARIMA is a standard tool in economics and energy forecasting.

### 9.4 The Forecasting Pipeline

**Data Collection:**
- Official DOE reports are downloaded and processed by automated scripts.
- Raw tables are extracted from PDFs and Excel files.

**Data Cleaning:**
- A Jupyter notebook parses the tables, handles merged cells, standardizes column names, resolves inconsistencies between different reports, and converts all units to GWh and MW.

**Feature Engineering:**
- Monthly and quarterly data are aggregated to annual totals.
- Time-series indices are created.
- Lag features and rolling averages are computed.
- Target variables are separated: total consumption and peak demand.

**Model Training (Offline):**
- The ARIMA(1,1,1) model is trained on the historical annual data.
- Validation is done by holding out the last 2–3 years and checking predictions against actuals.
- Accuracy metrics (MAE, RMSE, MAPE) are computed.

**Artifact Storage:**
- The trained model is saved as a pickle file (not used live, but kept for reference).
- Forecasts are exported as CSV files: one for consumption, one for peak demand.
- Model metadata is recorded in the `ml_model_registry` database table.

**Prediction Serving:**
- The EnergyHub backend loads the forecast CSVs into memory when the server starts.
- When a user requests a forecast, the system looks up the value in memory — no real-time calculation needed.
- Responses are sub-millisecond after the initial load.

**Visualization:**
- The front end draws a line chart:
  - Solid line for historical actuals.
  - Dashed line for the forecast.
  - Shaded band for the confidence interval (the range where the true value is likely to fall).
- Users can toggle between consumption and peak demand.

---

## Part 10: Suggested Diagrams for the Thesis

This section recommends diagrams the thesis team can create based on this inventory. They are organized by priority.

### 10.1 Must-Have Diagrams

These are essential for explaining the system to readers:

1. **System Architecture Diagram**
   - **What it shows:** The overall structure — React front end, FastAPI back end, Supabase database, Redis cache, FAISS search index, and external APIs (NASA, DOE, Groq).
   - **Why it matters:** Gives readers a high-level map of how everything connects.

2. **Use Case Diagram**
   - **What it shows:** The four types of users (Guest, Registered User, Admin, External Systems) and what each can do.
   - **Why it matters:** Clearly defines who interacts with the system and how.

3. **Data Flow Diagram (Level 0 and Level 1)**
   - **What it shows:** Level 0 shows LUMI as one box with external entities. Level 1 breaks it into 10 major processes (Auth, Dashboard, EcoSim, EnergyHub, Geothermal, AI Chat, Admin, Suitability, Forecasting, Data Pipeline).
   - **Why it matters:** Shows how data enters, moves through, and exits the system.

4. **Entity-Relationship Diagram (ERD)**
   - **What it shows:** All database tables and how they relate to each other (regions, provinces, municipalities, users, simulations, etc.).
   - **Why it matters:** Essential for understanding what information the system stores.

5. **Activity Diagram — EcoSim Simulation**
   - **What it shows:** The step-by-step flow from selecting a municipality to viewing results.
   - **Why it matters:** EcoSim is the core feature; this diagram makes the workflow easy to follow.

### 10.2 Important Diagrams

These add significant value if space allows:

6. **Module Interaction Diagram**
   - **What it shows:** How the 10 major modules send data to each other.
   - **Why it matters:** Complements the DFD with a focus on module relationships.

7. **Data Flow Diagram (Level 2)**
   - **What it shows:** Detailed breakdowns of the AI Chat process (embedding, search, prompt, generation, sanitization) and EcoSim calculations (solar, wind, hydro, geothermal).
   - **Why it matters:** Shows the internal logic of the two most complex processes.

8. **Activity Diagram — AI Chat (RAG)**
   - **What it shows:** The full question-to-answer pipeline.
   - **Why it matters:** The AI chat is a key differentiator; this diagram explains how it grounds answers in real data.

9. **Sequence Diagram — AI Chat**
   - **What it shows:** The exact order of messages between the user, front end, back end, search index, and AI service.
   - **Why it matters:** Shows timing and dependencies in the chat flow.

10. **Deployment Diagram**
    - **What it shows:** Where each component runs in production (web hosting, cloud database, cache, external APIs).
    - **Why it matters:** Helps readers understand the physical setup.

### 10.3 Optional Diagrams

Include these if there is room:

11. **Activity Diagram — Registration and Login**
    - Shows the auth workflow with decision points.

12. **Activity Diagram — Choropleth Map**
    - Shows how map data is fetched, cached, and colored.

13. **Class Diagram — Back-End Services**
    - Shows Python service classes and their methods.

14. **Component Diagram — Front End**
    - Shows React component hierarchy.

15. **State Machine — User Session**
    - Shows states (Guest, Authenticated, Admin) and transitions.

---

## Part 11: Features That Are Only Partly Built

This section lists features that exist in the code or database but are not fully active in the current public version:

| Feature | Status | Notes |
|---|---|---|
| Chat session saving | Partly built | Database tables exist, but the public version keeps chats in memory. |
| Chat moderation flagging | Partly built | The flag field and admin page exist, but automatic flagging is basic. |
| PDF or email export | Partly built | Only simple text/JSON downloads work. No PDF generation or email delivery. |
| Model comparison display | Partly built | The model registry tracks versions, but side-by-side comparison may be limited. |
| Premium plan restrictions | MVP public mode | The plan field exists, but most features are open to everyone. |
| Additional OAuth providers | Partly built | The code supports multiple providers, but the UI may only show Google. |
| Real-time notifications | Not built | Toasts show local feedback, but no push notifications or WebSockets. |
| Mobile app | Partly built | An Expo mobile project exists but may not be fully deployed. |

---

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2025-06-26 | LUMI System Analyst | Initial simplified inventory based on current codebase. |

---

**END OF DOCUMENT**
