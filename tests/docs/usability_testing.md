# LUMI Usability Testing Plan

**Document Type:** Usability Evaluation Protocol  
**Project:** LUMI — Data-Driven Environmental Intelligence System for Renewable Energy Decision Support  
**Version:** 1.0  
**Date:** June 2026  

---

## 1. Introduction

This document outlines the usability evaluation methodology for the LUMI web application. The evaluation is designed to measure how effectively target users can interact with the system, complete core tasks, and interpret the data-driven insights provided.

The usability testing aligns with **Specific Objective 1.3.2.6** of the LUMI thesis: *"To evaluate the usability, usefulness, and acceptability of the proposed renewable energy recommendation system among potential users."*

---

## 2. Target User Profiles

| User Profile | Description | Expected Frequency |
|---|---|---|
| **Energy Researchers** | Academics or analysts studying renewable energy trends and climate data. | Occasional |
| **Community Planners** | LGU staff or NGO workers evaluating renewable energy options for communities. | Regular |
| **Students** | Undergraduate or graduate students learning about renewable energy and climate change. | Frequent |
| **Renewable Energy Users** | Homeowners or community members considering solar, wind, or hydro installations. | Regular |

**Participant Recruitment:**
- Minimum 10 participants per user profile (40 total).
- Participants should have basic computer literacy and internet access.
- No prior knowledge of LUMI is assumed.

---

## 3. Test Environment

| Component | Specification |
|---|---|
| **Device** | Laptop or desktop with a modern browser |
| **Browser** | Google Chrome 120+ / Mozilla Firefox 121+ / Microsoft Edge |
| **Screen Resolution** | 1920×1080 (minimum 1366×768) |
| **Internet Connection** | Stable broadband (≥5 Mbps) |
| **Input Method** | Mouse and keyboard |
| **Test Duration** | 45–60 minutes per participant |

---

## 4. Test Scenarios (Task-Based Evaluation)

Each participant will complete the following 5 tasks. Tasks are presented in a fixed order to ensure consistency across sessions.

### Task 1: View Regional Energy Consumption

**Objective:** Assess the user's ability to locate and interpret energy statistics on the EnergyHub dashboard.

**Instructions:**
> "You are a community planner interested in understanding the energy consumption trends in the Philippines. Open the EnergyHub dashboard and find the latest national energy consumption figure."

**Expected Steps:**
1. Navigate to the EnergyHub page from the main navigation.
2. Locate the "Overview" or "Latest Statistics" section.
3. Identify the latest consumption value (e.g., 76,500 GWh).

**Success Criteria:**
- **Complete:** User identifies the correct figure within 60 seconds.
- **Partial:** User navigates to EnergyHub but cannot locate the exact figure.
- **Fail:** User cannot find the EnergyHub page or abandons the task.

---

### Task 2: Run a Renewable Energy Simulation

**Objective:** Assess the user's ability to configure and execute a renewable energy simulation.

**Instructions:**
> "You live in Tagaytay City, Cavite, and your monthly electricity bill is PHP 2,500. You want to know which renewable energy source is most suitable for your home. Use the EcoSim tool to find out."

**Expected Steps:**
1. Navigate to the EcoSim page.
2. Select "Tagaytay City" from the municipality dropdown.
3. Enter monthly consumption or bill amount (PHP 2,500).
4. Click "Run Simulation" or equivalent action.
5. View the simulation results.

**Success Criteria:**
- **Complete:** User successfully runs the simulation and views results within 3 minutes.
- **Partial:** User configures inputs but encounters an error or cannot interpret results.
- **Fail:** User cannot locate EcoSim or abandons the task.

---

### Task 3: Check Forecast Results

**Objective:** Assess the user's ability to locate and interpret the ML-generated energy demand forecast.

**Instructions:**
> "You want to understand how energy demand in the Philippines is expected to grow over the next 5 years. Find the forecast chart and identify the predicted consumption for 2030."

**Expected Steps:**
1. Navigate to the EnergyHub page.
2. Locate the forecast chart or "Forecast" section.
3. Identify the 2030 predicted consumption value.

**Success Criteria:**
- **Complete:** User identifies the 2030 forecast value within 90 seconds.
- **Partial:** User finds the chart but cannot identify the exact value.
- **Fail:** User cannot locate the forecast section.

---

### Task 4: Interpret the Choropleth Map

**Objective:** Assess the user's ability to interpret geographic visualizations of renewable energy potential.

**Instructions:**
> "You are researching which province in the Philippines has the highest solar energy potential. Use the choropleth map on the EnergyHub page to find the answer."

**Expected Steps:**
1. Navigate to the EnergyHub page.
2. Locate the map visualization.
3. Identify the color legend (e.g., darker = higher potential).
4. Identify the province with the darkest shade.

**Success Criteria:**
- **Complete:** User correctly identifies the top province within 2 minutes.
- **Partial:** User interacts with the map but cannot confidently identify the top province.
- **Fail:** User cannot locate or interact with the map.

---

### Task 5: View AI-Generated Explanation

**Objective:** Assess the user's ability to locate and understand the AI-generated analysis of renewable energy results.

**Instructions:**
> "After running your EcoSim simulation, you want to understand why solar was recommended. Find and read the AI-generated explanation."

**Expected Steps:**
1. Return to the EcoSim results page (or re-run simulation).
2. Locate the "AI Analysis" or "Explanation" panel.
3. Read the explanation text.
4. Answer: "What is the primary reason solar was recommended?"

**Success Criteria:**
- **Complete:** User locates the AI panel and correctly identifies the primary reason.
- **Partial:** User finds the AI panel but cannot extract the key reason.
- **Fail:** User cannot locate the AI analysis panel.

---

## 5. Measurement Metrics

For each task, the evaluator will record the following:

| Metric | Description | Recording Method |
|---|---|---|
| **Task Success Rate** | Percentage of participants who complete each task successfully. | Observer checklist |
| **Completion Time** | Time taken to complete each task (seconds). | Stopwatch / screen recording |
| **Errors** | Number of incorrect actions or deviations from the optimal path. | Observer notes |
| **User Satisfaction** | Subjective rating of ease-of-use and usefulness. | Post-test questionnaire |

### Task Success Scoring

| Level | Score | Definition |
|---|---|---|
| Complete | 1.0 | User completes task without assistance within time limit. |
| Partial | 0.5 | User completes task with assistance or exceeds time limit. |
| Fail | 0.0 | User cannot complete task or abandons. |

**Overall Task Success Rate =** Σ(Task Scores) / (Number of Tasks × Number of Participants)

---

## 6. System Usability Scale (SUS)

After completing all tasks, participants will complete the **System Usability Scale (SUS)** questionnaire. SUS is a standardized 10-item questionnaire that provides a reliable measure of perceived usability.

### SUS Questionnaire

**Instructions:** For each statement below, indicate your level of agreement using a scale of 1 to 5, where:
- **1 = Strongly Disagree**
- **2 = Disagree**
- **3 = Neutral**
- **4 = Agree**
- **5 = Strongly Agree**

| # | Statement | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
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

### SUS Scoring Method

1. For **odd-numbered items** (1, 3, 5, 7, 9): **Subtract 1** from the user response.
2. For **even-numbered items** (2, 4, 6, 8, 10): **Subtract the user response from 5**.
3. **Sum all 10 converted scores** and **multiply by 2.5**.

**Interpretation:**

| SUS Score | Adjective Rating | Acceptability |
|---|---|---|
| 85–100 | Excellent | Best imaginable |
| 70–84 | Good | Acceptable |
| 50–69 | Okay | Marginal |
| 0–49 | Poor | Not acceptable |

**Target for LUMI:** Average SUS score ≥ 68 (above-average usability).

---

## 7. Post-Test Interview Questions

After the SUS questionnaire, conduct a brief 5-minute interview:

1. "What was the most useful feature of LUMI?"
2. "What was the most confusing or difficult part of the system?"
3. "Would you recommend LUMI to a friend or colleague? Why or why not?"
4. "What additional feature would you like to see in LUMI?"
5. "How does LUMI compare to other tools you have used for energy research?"

---

## 8. Usability Test Report Template

### 8.1 Summary Statistics

| Metric | Value |
|---|---|
| **Total Participants** | ___ |
| **Average Age** | ___ |
| **Gender Distribution** | ___ |
| **Average Computer Experience** | ___ years |
| **Average Task Success Rate** | ___% |
| **Average Task Completion Time** | ___ seconds |
| **Average Errors per Participant** | ___ |
| **Average SUS Score** | ___ / 100 |
| **SUS Adjective Rating** | ___ |

### 8.2 Task-Level Results

| Task | Success Rate | Avg Time (s) | Avg Errors | Notes |
|---|---|---|---|---|
| T1: View regional energy consumption | ___% | ___ | ___ | ___ |
| T2: Run renewable energy simulation | ___% | ___ | ___ | ___ |
| T3: Check forecast results | ___% | ___ | ___ | ___ |
| T4: Interpret choropleth map | ___% | ___ | ___ | ___ |
| T5: View AI-generated explanation | ___% | ___ | ___ | ___ |

### 8.3 SUS Score Distribution

| SUS Score Range | # Participants | % of Total |
|---|---|---|
| 85–100 (Excellent) | ___ | ___% |
| 70–84 (Good) | ___ | ___% |
| 50–69 (Okay) | ___ | ___% |
| 0–49 (Poor) | ___ | ___% |

### 8.4 Key Findings

*Document qualitative observations, common pain points, and positive feedback here.*

### 8.5 Recommendations

*List actionable recommendations for improving usability based on test results.*

---

## 9. Ethical Considerations

- All participants will provide **informed consent** before testing.
- Participant data will be **anonymized** and stored securely.
- Participants may withdraw from the test at any time without penalty.
- No personal data collected during testing will be shared outside the research team.

---

*End of Usability Testing Plan*
