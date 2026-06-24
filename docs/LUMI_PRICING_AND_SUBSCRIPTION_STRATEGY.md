# LUMI Pricing & Subscription Strategy

## 1. Executive Summary

LUMI (Data-Driven Environmental Intelligence System for Renewable Energy Decision Support) is a FastAPI + React web application that provides municipality-level renewable energy suitability analysis, EcoSim simulation, EnergyHub national energy dashboards, and a RAG-powered AI chat assistant. This document designs a realistic three-tier SaaS pricing model grounded in actual infrastructure costs, Groq LLM token costs, and Philippine market conditions.

**Key Decisions:**

| Decision | Rationale |
|---|---|
| **Three Tiers: Free / Pro / Premium** | Free drives adoption; Pro captures students/researchers; Premium captures professionals |
| **llama-3.1-8b-instant for all AI** | Lowest-cost Groq model ($0.05/1M input, $0.08/1M output) keeps AI marginal cost negligible |
| **PHP-denominated pricing** | Primary market is Philippines; PHP avoids FX friction for local users |
| **Annual discount: 17% (2 months free)** | Standard SaaS practice; improves cash flow and reduces churn |
| **Chat requires login on all tiers** | Enables usage tracking, plan enforcement, and upgrade conversion |

**Final Prices:**

| Tier | Monthly | Annual | Target User |
|---|---|---|---|
| Free | ₱0 | ₱0 | Casual explorers, first-time visitors |
| Pro | ₱199/mo | ₱1,990/yr | Students, researchers, enthusiasts |
| Premium | ₱799/mo | ₱7,990/yr | Professionals, planners, businesses, power users |

**Break-even: 2 Premium users OR 8 Pro users per month** (at Scenario A infrastructure).

---

## 2. Infrastructure Cost Analysis

### 2.1 DigitalOcean Droplet Options

| Scenario | vCPU | RAM | SSD | Transfer | Monthly Cost |
|---|---|---|---|---|---|
| **A** | 2 | 2 GB | 60 GB | 3,000 GB | **$18.00** |
| **B** | 2 | 4 GB | 80 GB | 4,000 GB | **$24.00** |

**Selected Scenario for calculations: A ($18/mo)** — sufficient for <100 MAU with background ML/GIS workloads. Scenario B provides headroom for growth to 250+ users.

### 2.2 Operational Overhead

| Item | Monthly Cost | Annual Cost | Notes |
|---|---|---|---|
| Domain (`.com` or `.ph`) | — | ~$10 | Cloudflare or Namecheap |
| Monitoring (UptimeRobot free tier + logs) | ₱0 | ₱0 | Free tier sufficient at this scale |
| Backups (DO automated + manual) | ~$4 | ~$48 | 20% of droplet cost for snapshots |
| Misc (SSL certs, CDN edge) | ₱0 | ₱0 | Let's Encrypt + Cloudflare free |
| **Total Operational** | **~$4.83** | **~$58** | ~₱280/mo |

### 2.3 Total Fixed Infrastructure Cost

```
Total Fixed Cost = Droplet Cost + Operational Overhead

Scenario A: $18.00 + $4.83 = $22.83/mo = ₱1,324/mo
Scenario B: $24.00 + $4.83 = $28.83/mo = ₱1,674/mo
```

**Conversion rate used:** **$1 = ₱58** (approximate mid-2026 rate).

---

## 3. Groq Cost Analysis

### 3.1 Model Selection

| Model | Input Cost | Output Cost | Context Window | Speed |
|---|---|---|---|---|
| **llama-3.1-8b-instant** | **$0.05 / 1M tokens** | **$0.08 / 1M tokens** | 128K | ~560 tps |
| llama-3.3-70b-versatile | $0.59 / 1M tokens | $0.79 / 1M tokens | 128K | ~280 tps |
| mixtral-8x7b-32768 | $0.24 / 1M tokens | $0.24 / 1M tokens | 32K | ~500 tps |

**Selected:** **llama-3.1-8b-instant** for all tiers. At $0.05/$0.08, it is **11.8x cheaper** than the current 70B model, making AI costs negligible relative to infrastructure.

### 3.2 Token Consumption Per Interaction

#### Chat Message (RAG-enabled)

| Component | Tokens | Notes |
|---|---|---|
| System prompt | ~800 | 7-step instruction set |
| RAG context (5 chunks) | ~2,000 | ~400 tokens per chunk |
| User message | ~50 | Average question length |
| **Total Input** | **~2,850** | |
| **Total Output** | **~300** | Concise 3-5 sentence response |

```
Chat Cost = (Input Tokens / 1,000,000 * $0.05) + (Output Tokens / 1,000,000 * $0.08)
         = (2,850 / 1,000,000 * 0.05) + (300 / 1,000,000 * 0.08)
         = $0.0001425 + $0.000024
         = $0.0001665 per chat message
         = ₱0.0097 per chat message
```

#### EcoSim AI Insight

| Component | Tokens | Notes |
|---|---|---|
| System prompt + template | ~500 | Structured renewable analysis prompt |
| Ecosim results JSON | ~2,000 | Full simulation output |
| **Total Input** | **~2,500** | |
| **Total Output** | **~500** | Narrative analysis with recommendations |

```
EcoSim Insight Cost = (2,500 / 1,000,000 * 0.05) + (500 / 1,000,000 * 0.08)
                    = $0.000125 + $0.00004
                    = $0.000165 per insight
                    = ₱0.0096 per insight
```

#### EnergyHub Chart AI Insight

| Component | Tokens | Notes |
|---|---|---|
| System prompt | ~500 | Chart-specific analysis template |
| Chart data JSON | ~1,500 | Historical/forecast data points |
| **Total Input** | **~2,000** | |
| **Total Output** | **~400** | Structured insight text |

```
EnergyHub Insight Cost = (2,000 / 1,000,000 * 0.05) + (400 / 1,000,000 * 0.08)
                       = $0.0001 + $0.000032
                       = $0.000132 per insight
                       = ₱0.0077 per insight
```

### 3.3 Monthly AI Cost Per User by Tier

| Tier | Chats/Month | Insights/Month | Chat Cost | Insight Cost | **Total AI Cost** |
|---|---|---|---|---|---|
| **Free** | 5 | 1 (EcoSim or EnergyHub) | ₱0.048 | ₱0.0096 | **₱0.058** |
| **Pro** | 50 | 5 | ₱0.485 | ₱0.048 | **₱0.533** |
| **Premium** | 200 | 20 | ₱1.940 | ₱0.192 | **₱2.132** |

**Conclusion:** AI costs are **negligible** at the 8B model tier. Even a Premium user consuming maximum allocated usage costs only ₱2.13/month in Groq tokens. Pricing is therefore driven by **infrastructure recovery + value capture**, not marginal AI cost.

---

## 4. Pricing Formulas

### 4.1 Core Formula

```
Price = (Infrastructure Cost per Paying User + AI Cost per User + Operational Allocation) / (1 - Target Margin)
```

Where:
- `Infrastructure Cost per Paying User` = Total Fixed Cost / Number of Paying Users
- `AI Cost per User` = Estimated token consumption * token price
- `Operational Allocation` = Overhead per user (support, maintenance, admin time)
- `Target Margin` = Desired profit margin (0.50 for 50%)

### 4.2 Infrastructure Cost Per Paying User

**Assumption:** 100 total MAU with 70% Free, 20% Pro, 10% Premium distribution.

```
Paying Users = 20 Pro + 10 Premium = 30 paying users
Infrastructure per Paying User = Total Fixed Cost / Paying Users

Scenario A: $22.83 / 30 = $0.761 per paying user = ₱44.14
Scenario B: $28.83 / 30 = $0.961 per paying user = ₱55.74
```

### 4.3 Operational Allocation Per User

**Assumption:** ₱200/mo per paying user for support, maintenance, and administrative overhead (modest at <100 users).

### 4.4 Cost-Plus Price Calculation

```
Pro Tier Base Cost = Infrastructure Allocation + AI Cost + Operational Allocation
                  = ₱44.14 + ₱0.533 + ₱200.00
                  = ₱244.67

With 50% Margin:
Pro Price = ₱244.67 / (1 - 0.50) = ₱489.34

Premium Tier Base Cost = ₱44.14 + ₱2.132 + ₱200.00
                       = ₱246.27

With 50% Margin:
Premium Price = ₱246.27 / (1 - 0.50) = ₱492.54
```

**Problem:** Cost-plus pricing yields nearly identical prices for Pro and Premium because AI costs are negligible and infrastructure is shared. This is economically correct but **fails to capture value differentiation**.

### 4.5 Value-Based Pricing Adjustment

Since marginal cost is flat, pricing must reflect **perceived value** to each segment:

| Segment | Value Perception | Willingness to Pay | Adjusted Price |
|---|---|---|---|
| Students / Researchers | Useful for thesis, projects, learning | Low (~₱150-300) | **₱199/mo** |
| Professionals / Planners | Decision-making tool, ROI-driven | Medium-High (~₱500-1,000) | **₱799/mo** |
| Enterprises / Government | Scale deployment, compliance | High (custom) | Contact Sales |

**Final prices** are set below maximum willingness-to-pay to maximize conversion while maintaining healthy unit economics.

---

## 5. Assumptions

### 5.1 Infrastructure Assumptions

| # | Assumption | Value | Rationale |
|---|---|---|---|
| 1 | Server scenario | A ($18/mo) | Sufficient for <100 MAU; B for scaling |
| 2 | USD/PHP exchange rate | ₱58 | Approximate mid-2026 rate |
| 3 | Domain cost | $10/yr | Cloudflare/Namecheap standard |
| 4 | Backup cost | 20% of droplet | DO automated snapshots |
| 5 | Monitoring cost | ₱0 | Free tiers sufficient (UptimeRobot, DO monitoring) |
| 6 | CDN cost | ₱0 | Cloudflare free tier |
| 7 | Operational labor | ₱200/user/mo | Modest support at small scale |

### 5.2 AI Usage Assumptions

| # | Assumption | Value | Rationale |
|---|---|---|---|
| 8 | Groq model | llama-3.1-8b-instant | Lowest cost, 128K context, sufficient quality for Q&A |
| 9 | Chat input tokens | 2,850 | System prompt + 5 RAG chunks + user message |
| 10 | Chat output tokens | 300 | Concise 3-5 sentence responses |
| 11 | EcoSim insight input | 2,500 | Simulation JSON + analysis template |
| 12 | EcoSim insight output | 500 | Narrative with recommendations |
| 13 | EnergyHub insight input | 2,000 | Chart data + analysis template |
| 14 | EnergyHub insight output | 400 | Structured insight text |
| 15 | Free tier chat limit | 5/mo | Enough to demonstrate value, not replace need |
| 16 | Pro tier chat limit | 50/mo | Sufficient for active student/researcher use |
| 17 | Premium chat limit | 200/mo | Heavy professional use |
| 18 | Free AI insight limit | 1/mo | Teaser for premium analysis |
| 19 | Pro AI insight limit | 5/mo | Moderate analysis for research |
| 20 | Premium AI insight limit | 20/mo | Full decision-support capability |

### 5.3 Market Assumptions

| # | Assumption | Value | Rationale |
|---|---|---|---|
| 21 | Total MAU | < 100 | Thesis project scope; realistic for MVP |
| 22 | Free user share | 70% | Standard freemium conversion funnel |
| 23 | Pro user share | 20% | Students and researchers |
| 24 | Premium user share | 10% | Professionals and planners |
| 25 | Target profit margin | 50% minimum | Sustainable SaaS economics |
| 26 | Annual discount | 17% (2 months free) | Industry standard; improves LTV |
| 27 | Churn rate assumption | 5%/mo | Conservative for niche B2B/SaaS |
| 28 | Payment currency | PHP | Primary market is Philippines |

## 6. Free Tier Breakdown

### 6.1 Price

| Period | Amount |
|---|---|
| Monthly | **₱0** |
| Annual | **₱0** |

### 6.2 Target User

Casual explorers, first-time visitors, students on tight budgets, and users evaluating the platform before committing. The Free tier must remain genuinely useful to drive organic adoption and word-of-mouth.

### 6.3 Included Features

- **EcoSim Basic Calculator:** Full solar, wind, hydro, and geothermal calculation without AI analysis
- **EnergyHub Dashboard:** Overview cards, historical trends (2003–2024), and ARIMA forecast charts
- **EnergyHub Choropleth Map:** Province-level renewable potential, geothermal scores, source breakdown
- **Geothermal Analysis:** Municipality-level suitability scores and plant proximity data
- **RAG Chatbot:** 5 messages per month (login required)
- **Saved Simulations:** 3 total saved simulations
- **AI Insights:** 1 per month (EcoSim OR EnergyHub)

### 6.4 Feature Limits

| Feature | Limit | Rationale |
|---|---|---|
| Saved Simulations | 3 total | Sufficient for 2-3 project scenarios; creates upgrade pressure |
| Chat Messages | 5/month | Enough to ask 4-5 questions and see value; not enough for research |
| AI Insights | 1/month | Teaser only; demonstrates premium value without replacing it |
| Map Interactions | Unlimited | Public data; no marginal cost to serve |
| Forecast Views | Unlimited | Pre-computed CSVs; no LLM cost |

### 6.5 Operating Cost per Free User

```
Infrastructure Share = Total Fixed Cost / Total Users
                     = $22.83 / 100 = $0.2283 = ₱13.24

AI Cost = 5 chats * ₱0.0097 + 1 insight * ₱0.0096 = ₱0.058

Total Cost per Free User = ₱13.24 + ₱0.058 = ₱13.30/month
```

**Revenue per Free User:** ₱0 (acquisition cost only).

### 6.6 Premium Value Potential

Free users who exceed simulation or chat limits receive an upgrade prompt. Conversion funnel:
- 70% of MAU = Free users
- Estimated 5-10% monthly conversion to paid = 3.5-7 new paying users/month

---

## 7. Pro Tier Breakdown

### 7.1 Price

| Period | Amount |
|---|---|
| Monthly | **₱199/mo** |
| Annual | **₱1,990/yr** (17% discount = 2 months free) |
| Equivalent Monthly (Annual) | **₱165.83/mo** |

### 7.2 Target User

Students writing theses on renewable energy, researchers studying Philippine energy policy, environmental science enthusiasts, and small NGO workers. Price point is below the cost of a single textbook or research journal subscription.

### 7.3 Included Features

All Free features, plus:

- **EcoSim AI Analysis:** Full LLM-powered renewable energy analysis with RAG context
- **EnergyHub AI Insights:** Chart-specific LLM insights with prescriptive recommendations
- **RAG Chatbot:** 50 messages per month (10x Free tier)
- **Saved Simulations:** 20 total saved simulations (6.7x Free tier)
- **AI Insights:** 5 per month (EcoSim + EnergyHub combined)
- **Chat History Persistence:** Sessions stored in `chat_sessions` / `chat_messages` tables
- **No ads or upgrade banners** within the app

### 7.4 Feature Limits

| Feature | Limit | Rationale |
|---|---|---|
| Saved Simulations | 20 total | Sufficient for multi-municipality thesis research |
| Chat Messages | 50/month | ~1-2 per day; adequate for active student use |
| AI Insights | 5/month | Weekly deep analysis for ongoing research |
| Map Data Export | ✗ | Premium-only feature |
| Batch Municipality Analysis | ✗ | Premium-only feature |

### 7.5 Operating Cost per Pro User

```
Infrastructure Share = $22.83 / 30 paying users = $0.761 = ₱44.14
AI Cost = 50 chats * ₱0.0097 + 5 insights * ₱0.0096 = ₱0.533
Operational Allocation = ₱200.00

Total Cost per Pro User = ₱44.14 + ₱0.533 + ₱200.00 = ₱244.67

Revenue per Pro User = ₱199.00
Profit Margin = (199 - 244.67) / 199 = -22.9%
```

**Note:** At the individual Pro user level, the margin is **negative** because infrastructure is fixed and shared. Pro tier profitability requires the **portfolio effect**: Premium users subsidize Pro users, and aggregate revenue exceeds aggregate cost.

### 7.6 Portfolio Economics (All Users Combined)

```
Total Monthly Cost (Scenario A):
  = Fixed Infrastructure + Total AI + Operational
  = ₱1,324 + (70*₱0.058 + 20*₱0.533 + 10*₱2.132) + (30*₱200)
  = ₱1,324 + ₱34.87 + ₱6,000
  = ₱7,358.87

Total Monthly Revenue:
  = 20 Pro * ₱199 + 10 Premium * ₱799
  = ₱3,980 + ₱7,990
  = ₱11,970

Portfolio Profit = ₱11,970 - ₱7,358.87 = ₱4,611.13
Portfolio Margin = 4,611.13 / 11,970 = 38.6%
```

At 100 MAU with this distribution, LUMI achieves a **38.6% gross margin** before taxes and payment processor fees.

---

## 8. Premium Tier Breakdown

### 8.1 Price

| Period | Amount |
|---|---|
| Monthly | **₱799/mo** |
| Annual | **₱7,990/yr** (17% discount = 2 months free) |
| Equivalent Monthly (Annual) | **₱665.83/mo** |

### 8.2 Target User

Energy consultants, municipal planners, LGU (Local Government Unit) officials, renewable energy developers, ESG analysts, and business decision-makers. The price is positioned below professional tools like ArcGIS Pro ($700/yr) or HOMER Pro ($600/yr) while offering Philippine-specific data and AI assistance.

### 8.3 Included Features

All Pro features, plus:

- **Unlimited Saved Simulations:** No cap on saved scenarios
- **RAG Chatbot:** 200 messages per month (4x Pro, 40x Free)
- **AI Insights:** 20 per month (4x Pro, 20x Free)
- **Priority AI Response:** Slightly faster Groq inference (lower temperature, optimized prompt)
- **Admin Dashboard Access:** If assigned admin/dev role by system owner
- **Export Capabilities:** CSV export of simulation results and map data (future feature)
- **Dedicated Support:** Email support with 48-hour response SLA

### 8.4 Feature Limits

| Feature | Limit | Rationale |
|---|---|---|
| Saved Simulations | Unlimited | No artificial ceiling for power users |
| Chat Messages | 200/month | ~6-7 per day; generous for professional use |
| AI Insights | 20/month | Daily analysis capability |
| Map Data Export | ✓ | CSV/JSON export for reporting |
| Batch Municipality Analysis | ✓ | Compare multiple municipalities side-by-side (future) |

### 8.5 Operating Cost per Premium User

```
Infrastructure Share = $22.83 / 30 = $0.761 = ₱44.14
AI Cost = 200 chats * ₱0.0097 + 20 insights * ₱0.0096 = ₱2.132
Operational Allocation = ₱200.00

Total Cost per Premium User = ₱44.14 + ₱2.132 + ₱200.00 = ₱246.27

Revenue per Premium User = ₱799.00
Profit Margin = (799 - 246.27) / 799 = 69.1%
```

Premium users are **highly profitable** on an individual basis, subsidizing the Free and Pro tiers.

---

## 9. Feature Comparison Matrix

| Feature | Free | Pro | Premium |
|---|---|---|---|
| **EcoSim Basic Calculator** | ✓ | ✓ | ✓ |
| **EcoSim AI Analysis** | 1/mo | 5/mo | 20/mo |
| **EnergyHub Dashboard** | ✓ | ✓ | ✓ |
| **EnergyHub Forecast/Trends** | ✓ | ✓ | ✓ |
| **EnergyHub Choropleth Map** | ✓ | ✓ | ✓ |
| **EnergyHub AI Insight** | 1/mo | 5/mo | 20/mo |
| **Geothermal Suitability Analysis** | ✓ | ✓ | ✓ |
| **Geothermal Plant Locator** | ✓ | ✓ | ✓ |
| **RAG Chatbot** | 5 msgs/mo | 50 msgs/mo | 200 msgs/mo |
| **Chat History Persistence** | ✗ | ✓ | ✓ |
| **Saved Simulations** | 3 total | 20 total | Unlimited |
| **Simulation Sharing** | ✗ | ✗ | ✓ |
| **Map Data Export (CSV/JSON)** | ✗ | ✗ | ✓ |
| **Batch Municipality Compare** | ✗ | ✗ | ✓ |
| **Priority AI Response** | ✗ | ✗ | ✓ |
| **Admin Dashboard Access** | ✗ | ✗ | Admin role only |
| **Dedicated Email Support** | ✗ | ✗ | ✓ (48h SLA) |
| **Monthly Price** | ₱0 | ₱199 | ₱799 |
| **Annual Price** | ₱0 | ₱1,990 | ₱7,990 |

### 9.1 Feature Tiering Rationale

**Free Tier Philosophy:**
- All **computationally cheap** features are fully available: EcoSim calculator, EnergyHub charts, maps, geothermal data
- All **LLM-expensive** features are severely limited: 1 AI insight, 5 chats
- **Persisted state** is restricted: 3 saved simulations
- **Rationale:** Users can fully evaluate the platform's analytical value without paying, but must upgrade to access AI-powered decision support and persistent workflows.

**Pro Tier Philosophy:**
- **Moderate AI access:** 50 chats and 5 insights per month — sufficient for a student research project or thesis
- **Persistent workflows:** 20 saved simulations allow semester-long research
- **No ads:** Clean experience for serious users
- **Rationale:** Priced below a textbook subscription; captures the student/researcher segment who needs more than teaser access but cannot afford enterprise tools.

**Premium Tier Philosophy:**
- **Generous AI access:** 200 chats and 20 insights per month — professional daily use
- **Data portability:** Export and sharing features for business reporting
- **Priority support:** Dedicated channel for business-critical issues
- **Rationale:** Priced at a fraction of professional GIS/energy software; captures consultants, planners, and LGU officials who derive direct business value from the platform.

---

## 10. Cost Simulations

### 10.1 Scenario A — $18/mo Droplet

#### 10.1.1 10 Users (7 Free, 2 Pro, 1 Premium)

```
Infrastructure: $22.83 = ₱1,324
AI Costs: 7*₱0.058 + 2*₱0.533 + 1*₱2.132 = ₱3.61
Operational: 3 * ₱200 = ₱600
Total Cost = ₱1,324 + ₱3.61 + ₱600 = ₱1,927.61
Revenue: 2*₱199 + 1*₱799 = ₱1,197
Profit = ₱1,197 - ₱1,927.61 = -₱730.61 (Loss)
Cost per Paying User = ₱1,927.61 / 3 = ₱642.54
```

**At 10 users, LUMI is NOT profitable.** Fixed infrastructure exceeds revenue.

#### 10.1.2 50 Users (35 Free, 10 Pro, 5 Premium)

```
Total Cost = ₱1,324 + ₱18.02 + ₱3,000 = ₱4,342.02
Revenue = ₱5,985
Profit = ₱5,985 - ₱4,342.02 = ₱1,642.98
Margin = 1,642.98 / 5,985 = 27.4%
Cost per Paying User = ₱4,342.02 / 15 = ₱289.47
```

**At 50 users, LUMI is profitable with a 27.4% margin.**

#### 10.1.3 100 Users (70 Free, 20 Pro, 10 Premium)

```
Total Cost = ₱1,324 + ₱36.04 + ₱6,000 = ₱7,360.04
Revenue = ₱11,970
Profit = ₱11,970 - ₱7,360.04 = ₱4,609.96
Margin = 4,609.96 / 11,970 = 38.5%
```

**At 100 users, LUMI achieves a 38.5% margin.**

#### 10.1.4 250 Users (175 Free, 50 Pro, 25 Premium)

```
Total Cost = ₱1,324 + ₱90.10 + ₱15,000 = ₱16,414.10
Revenue = ₱29,925
Profit = ₱13,510.90
Margin = 13,510.90 / 29,925 = 45.1%
```

**At 250 users, margin improves to 45.1%.** Scenario B server ($24/mo) is recommended.

#### 10.1.5 500 Users (350 Free, 100 Pro, 50 Premium)

```
Total Cost = ₱1,674 + ₱180.20 + ₱30,000 = ₱31,854.20
Revenue = ₱59,850
Profit = ₱27,995.80
Margin = 46.8%
```

#### 10.1.6 1000 Users (700 Free, 200 Pro, 100 Premium)

```
Total Cost = ₱1,674 + ₱360.40 + ₱60,000 = ₱62,034.40
Revenue = ₱119,700
Profit = ₱57,665.60
Margin = 48.2%
```

### 10.2 Cost Summary Table (Scenario A)

| Users | Free | Pro | Premium | Total Cost | Revenue | Profit | Margin |
|---|---|---|---|---|---|---|---|
| 10 | 7 | 2 | 1 | ₱1,928 | ₱1,197 | **-₱731** | **-61%** |
| 50 | 35 | 10 | 5 | ₱4,342 | ₱5,985 | **₱1,643** | **27.4%** |
| 100 | 70 | 20 | 10 | ₱7,360 | ₱11,970 | **₱4,610** | **38.5%** |
| 250 | 175 | 50 | 25 | ₱16,414 | ₱29,925 | **₱13,511** | **45.1%** |
| 500 | 350 | 100 | 50 | ₱31,854 | ₱59,850 | **₱27,996** | **46.8%** |
| 1000 | 700 | 200 | 100 | ₱62,034 | ₱119,700 | **₱57,666** | **48.2%** |

**Key Insight:** LUMI reaches profitability at approximately **30-35 paying users**.

---

## 11. Break-Even Analysis

### 11.1 Break-Even Formula

```
Break-Even Paying Users = Total Fixed Cost / Contribution Margin per User
                        = ₱1,324 / (₱399 - ₱200)
                        = ₱1,324 / ₱199
                        ≈ 6.65 → 7 paying users
```

### 11.2 Break-Even Metrics

| Metric | Value |
|---|---|
| Total Fixed Cost | ₱1,324/mo |
| ARPU | ₱399/mo |
| Contribution Margin per User | ₱199/mo |
| **Break-Even Paying Users** | **7 users** |
| **Break-Even Total Users** | **~23 users** |
| Time to Break-Even (at 5 new users/mo) | **~5 months** |

### 11.3 Margin Sensitivity

| Paying Users | Total Users | Revenue | Cost | Margin | Status |
|---|---|---|---|---|---|
| 3 | 10 | ₱1,197 | ₱1,928 | -61% | ❌ Loss |
| 7 | 23 | ₱2,793 | ₱2,718 | 2.7% | ⚠️ Break-even |
| 15 | 50 | ₱5,985 | ₱4,342 | 27% | ✅ Profitable |
| 30 | 100 | ₱11,970 | ₱7,360 | 39% | ✅ Healthy |
| 75 | 250 | ₱29,925 | ₱16,414 | 45% | ✅ Strong |

---

## 12. Subscription Architecture

### 12.1 Current Schema Capabilities

The existing LUMI schema already supports basic subscription management:

| Table / Column | Current State | Supports Subscriptions? |
|---|---|---|
| `profiles.plan` | `text` field ("free", "premium") | **Yes** — "pro" can be added without migration |
| `profiles.is_active` | `boolean` | **Yes** — soft-delete / ban capability |
| `user_roles.role` | `app_role` enum (user, admin, dev) | **Yes** — admin/dev auto-upgrade to premium |
| `saved_simulations` | Full CRUD table | **Yes** — can be gated by plan |
| `system_config` | JSON config store | **Yes** — stores `free_sim_limit`, `free_chat_limit` |
| `chat_sessions` / `chat_messages` | Chat persistence tables | **Yes** — can be gated by auth + plan |

**Verdict:** The current schema supports Free/Pro/Premium with **minor enhancements** — a `usage_tracking` table and a `feature_permissions` lookup table.

### 12.2 Required Schema Changes

#### `usage_tracking` Table

```sql
CREATE TABLE IF NOT EXISTS usage_tracking (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    feature_type text NOT NULL CHECK (feature_type IN (
        'chat', 'simulation', 'ai_insight_ecosim', 'ai_insight_energyhub'
    )),
    tokens_input int NOT NULL DEFAULT 0,
    tokens_output int NOT NULL DEFAULT 0,
    metadata jsonb DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_feature
    ON usage_tracking(user_id, feature_type, created_at);
```

**Purpose:** Track per-user AI consumption; enable usage analytics and billing.

#### `feature_permissions` Table

```sql
CREATE TABLE IF NOT EXISTS feature_permissions (
    plan text PRIMARY KEY CHECK (plan IN ('free', 'pro', 'premium')),
    limits jsonb NOT NULL DEFAULT '{}',
    features jsonb NOT NULL DEFAULT '{}',
    updated_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO feature_permissions (plan, limits, features)
VALUES
    ('free', '{"simulations": 3, "chat_messages": 5, "ai_insights": 1}',
     '{"chat_persistence": false, "data_export": false, "batch_compare": false, "priority_response": false}'),
    ('pro', '{"simulations": 20, "chat_messages": 50, "ai_insights": 5}',
     '{"chat_persistence": true, "data_export": false, "batch_compare": false, "priority_response": false}'),
    ('premium', '{"simulations": 999999, "chat_messages": 200, "ai_insights": 20}',
     '{"chat_persistence": true, "data_export": true, "batch_compare": true, "priority_response": true}')
ON CONFLICT (plan) DO UPDATE
    SET limits = EXCLUDED.limits,
        features = EXCLUDED.features,
        updated_at = now();
```

**Purpose:** Centralized, database-driven plan configuration. Admin can adjust limits without code deployment.

---

## 13. Database Changes

### 13.1 Full Migration Script

```sql
-- ============================================================
-- LUMI Subscription Schema Migration
-- Adds usage tracking and feature permissions for Free/Pro/Premium
-- ============================================================

-- 1. usage_tracking table
CREATE TABLE IF NOT EXISTS usage_tracking (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    feature_type text NOT NULL CHECK (feature_type IN (
        'chat', 'simulation', 'ai_insight_ecosim', 'ai_insight_energyhub'
    )),
    tokens_input int NOT NULL DEFAULT 0,
    tokens_output int NOT NULL DEFAULT 0,
    metadata jsonb DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_feature
    ON usage_tracking(user_id, feature_type, created_at);

CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_created
    ON usage_tracking(user_id, created_at);

-- 2. feature_permissions table
CREATE TABLE IF NOT EXISTS feature_permissions (
    plan text PRIMARY KEY CHECK (plan IN ('free', 'pro', 'premium')),
    limits jsonb NOT NULL DEFAULT '{}',
    features jsonb NOT NULL DEFAULT '{}',
    updated_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO feature_permissions (plan, limits, features)
VALUES
    ('free',
     '{"simulations": 3, "chat_messages": 5, "ai_insights": 1}',
     '{"chat_persistence": false, "data_export": false, "batch_compare": false, "priority_response": false}'
    ),
    ('pro',
     '{"simulations": 20, "chat_messages": 50, "ai_insights": 5}',
     '{"chat_persistence": true, "data_export": false, "batch_compare": false, "priority_response": false}'
    ),
    ('premium',
     '{"simulations": 999999, "chat_messages": 200, "ai_insights": 20}',
     '{"chat_persistence": true, "data_export": true, "batch_compare": true, "priority_response": true}'
    )
ON CONFLICT (plan) DO UPDATE
    SET limits = EXCLUDED.limits,
        features = EXCLUDED.features,
        updated_at = now();

-- 3. Auto-update trigger for feature_permissions
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_feature_permissions_updated_at ON feature_permissions;
CREATE TRIGGER trigger_feature_permissions_updated_at
    BEFORE UPDATE ON feature_permissions
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
```

### 13.2 Backward Compatibility

- All existing `free` and `premium` users remain functional
- `_get_effective_plan()` in `auth.py` handles any plan value gracefully
- `system_config` JSON fallback ensures old code paths work if `feature_permissions` is empty

---

## 14. Code Integration Plan

### 14.1 New File: `app/dependencies/plan_limits.py`

**Purpose:** Centralized plan limit enforcement.

**Functions:**
- `get_plan_limits(plan: str) -> dict` — returns limits from `feature_permissions` or fallback defaults
- `check_feature_access(user: dict, feature_type: str) -> bool` — checks remaining quota
- `get_usage_this_month(user_id: str, feature_type: str) -> int` — counts usage in current month
- `increment_usage(user_id: str, feature_type: str, tokens_input, tokens_output)` — logs usage
- `require_plan(plan: str)` — FastAPI dependency factory for minimum plan enforcement

**Integration Points:** Used by `chat.py`, `simulations.py`, `ecosim.py`, `energyhub.py`.

### 14.2 Modified: `app/routes/chat.py`

**Current State:** Public, no auth, llama-3.3-70b-versatile, no usage tracking.

**Required Changes:**
1. Add `get_current_user_with_role_and_plan` dependency
2. Switch model to `llama-3.1-8b-instant`
3. Check monthly chat count against plan limit
4. Persist messages to `chat_messages` table
5. Log usage to `usage_tracking`
6. Return 403 with upgrade prompt when limit exceeded

### 14.3 Modified: `app/routes/simulations.py`

**Current State:** Hard-coded `free_sim_limit = 3`; checks `plan not in ("premium", "admin", "dev")`.

**Required Changes:**
1. Replace `_get_free_sim_limit()` with `get_plan_limits()`
2. Allow `pro` users up to 20 simulations; `premium` unlimited
3. Log simulation creation to `usage_tracking`

### 14.4 Modified: `app/routes/ecosim.py`

**Current State:** `include_ai` param exists but no plan gating.

**Required Changes:**
1. Check plan before generating AI insight
2. Count AI insights per month against plan limit
3. If limit exceeded, return results WITHOUT AI analysis
4. Include `ai_insight_remaining` in response

### 14.5 Modified: `app/routes/energyhub.py`

**Current State:** `use_llm` param exists but no plan gating; insights cached in `chart_ai_insights`.

**Required Changes:**
1. Check plan before generating new AI insight
2. Reuse cached insights regardless of plan (no double-charging)
3. Count new AI insights against monthly limit
4. Return 403 with upgrade prompt if limit exceeded and no cache

### 14.6 Frontend Changes Summary

| File | Current | Required |
|---|---|---|
| `AuthContext.jsx` | Exposes basic user | Add `plan`, `isFree`, `isPro`, `isPremium` |
| `ChatPage.jsx` | Public, no auth | Require auth, show message counter, disable on limit |
| `Ecosim.jsx` | Save sim + AI toggle | Show sim counter, disable AI if limit reached |
| `EnergyHub.jsx` | AI insight toggle | Show insight counter, disable if limit reached |

---

## 15. Payment System Recommendations

### 15.1 Market Context: Philippines

| Payment Method | Market Share | Notes |
|---|---|---|
| **GCash** | ~73M users | Dominant e-wallet; QR and online payments |
| **Maya** | ~13M users | Former PayMaya; strong checkout integration |
| **Credit/Debit Cards** | ~15% e-commerce | Growing but limited penetration |
| **Bank Transfers** | Moderate | InstaPay (₱25, real-time), PESONet (free, batch) |
| **7-Eleven / OTC** | Significant | Cash payments via CLiQQ or payment centers |

### 15.2 Provider Comparison

| Provider | Pros | Cons | Fee | PHP | Integration | Student Discount | **Recommend** |
|---|---|---|---|---|---|---|---|
| **PayMongo** | Philippine-native; GCash/Maya/card/GrabPay; great docs; student-friendly | Smaller ecosystem | 2.9% + ₱15 | ✅ Native | ⭐⭐⭐⭐⭐ | Custom plans | **✅ YES — Primary** |
| **Xendit** | Strong SEA; GCash/Maya/7-Eleven/bank; enterprise support | Higher small-transaction fees | 2.9% + ₱15 | ✅ Native | ⭐⭐⭐⭐ | Enterprise only | **✅ YES — Alternative** |
| **Stripe** | Best SDKs; global reliability | No native PHP payout; FX fees; GCash via partner | 3.5% + ₱15 | ⚠️ USD | ⭐⭐⭐⭐ | None | **⚠️ MAYBE — International later** |
| **GCash Direct** | Lowest fees; massive base | Complex merchant onboarding; manual integration | ~1.5% | ✅ Native | ⭐⭐ | None | **❌ NO — Too complex** |
| **Maya Direct** | Competitive rates | Smaller base; complex onboarding | ~1.5% | ✅ Native | ⭐⭐ | None | **❌ NO — Too complex** |

### 15.3 Recommended Implementation

**Primary: PayMongo**
- **Why:** Built for Philippine startups; supports GCash, Maya, credit/debit cards, and GrabPay in one integration; excellent FastAPI-compatible REST API.
- **Integration:** Webhook-based; create PaymentIntent → redirect to PayMongo checkout → webhook updates `profiles.plan` in Supabase.
- **Pricing:** 2.9% + ₱15 per transaction. On ₱199 Pro: fee = ₱5.77 + ₱15 = ₱20.77 (10.4% effective rate).

**Alternative: Xendit** — if PayMongo lacks specific features (7-Eleven cash payments, enterprise invoicing).

**Future: Stripe** — if LUMI expands internationally or needs advanced subscription management.

### 15.4 Payment Flow

```
User clicks "Upgrade to Pro"
    |
    v
POST /billing/create-checkout { plan: "pro", interval: "monthly" }
    |
    v
Backend creates PayMongo PaymentIntent → returns checkout URL
    |
    v
Frontend redirects to PayMongo checkout
    |
    v
User pays (GCash / Maya / Card)
    |
    v
PayMongo webhook → /billing/webhook
    |
    v
Backend verifies signature, updates profiles.plan = "pro"
    |
    v
Redirect to /dashboard with success message
```

**New Endpoints Required:**
- `POST /billing/create-checkout`
- `POST /billing/webhook`
- `GET /billing/portal` (future)

---

## 16. Thesis Justification

### 16.1 Business Viability

| Factor | Justification |
|---|---|
| **Low break-even** | Only 7 paying users needed; achievable through university partnerships |
| **High-margin Premium** | 69.1% unit margin subsidizes Free/Pro tiers |
| **Negligible AI cost** | llama-3.1-8b-instant costs <₱0.01 per interaction |
| **Fixed infrastructure** | $18/mo droplet serves all users; no variable compute until 250+ MAU |

### 16.2 Sustainability

| Factor | Justification |
|---|---|
| **Self-funding at 50 MAU** | 27% margin covers costs without external funding |
| **Annual pricing improves cash flow** | 17% discount = 12 months of runway upfront |
| **Operational costs controllable** | ₱200/user allocation is conservative; reducible with automation |
| **Groq 8B is future-proof** | If token prices drop, margins improve automatically |

### 16.3 Scalability

| Factor | Justification |
|---|---|
| **Server upgrade path** | $18 → $24 → $48 → horizontal scaling; clear and affordable |
| **Database via Supabase** | RLS + connection pooling; free tier handles 10K+ MAU |
| **AI cost flat** | Caching (`chart_ai_insights`, Redis) reduces redundant LLM calls |
| **Modular permissions** | `feature_permissions` table enables A/B testing without code deploys |

### 16.4 Future Commercialization

| Path | Timeline | Action |
|---|---|---|
| LGU / Enterprise licensing | 12-18 months | Custom Premium with SLA, white-label |
| API access tier | 6-12 months | Developer plan with REST API key |
| Data marketplace | 18-24 months | Sell municipality reports |
| International expansion | 24+ months | Stripe, multi-currency, ASEAN localization |

### 16.5 Research Contribution

| Contribution | How Pricing Strengthens It |
|---|---|
| **Decision Support System Design** | Tiered access demonstrates how feature gating balances utility and resource constraints |
| **AI in Environmental Systems** | Cost-transparent AI pricing shows how LLM costs can be managed in resource-constrained apps |
| **Philippine RE Policy** | Student/Pro pricing makes the tool accessible to future energy researchers and policymakers |
| **Sustainability Science** | Freemium model is a sustainable business model for research tools — avoiding grant dependency |

### 16.6 Decision Support Objectives

LUMI's mission is to empower stakeholders with data-driven renewable energy decisions. The pricing model directly supports this:

- **Free:** Removes barriers for citizens exploring solar/wind for their homes
- **Pro:** Enables students and researchers to conduct rigorous multi-scenario analyses
- **Premium:** Equips professionals with unlimited AI analysis for confident investment decisions

By aligning price with value and user type, LUMI maximizes **social impact** (broad access) while ensuring **financial sustainability** (paid tiers cover costs).

---

## 17. Future Scaling Considerations

### 17.1 Infrastructure Scaling Triggers

| Trigger | Action | Cost Impact |
|---|---|---|
| > 150 MAU | Upgrade to Scenario B ($24/mo, 4 GB) | +$6/mo |
| > 250 MAU | Add managed Redis / load balancer | +$30/mo |
| > 500 MAU | Horizontal scaling: 2 droplets | +$30/mo |
| > 1000 MAU | Container orchestration (K8s / ECS) | +$50/mo |
| > 5000 MAU | CDN + Edge caching + read replicas | +$100/mo |

### 17.2 AI Cost Scaling Triggers

| Trigger | Action | Savings |
|---|---|---|
| > 50,000 chats/mo | Negotiate Groq volume discount | -20% to -50% |
| > 5,000 insights/mo | Aggressive caching (7-day Redis TTL) | -30% redundant calls |
| > 100,000 messages/mo | Fine-tune 3B model for common queries | -60% token cost |

### 17.3 Pricing Evolution

| Phase | Timeline | Changes |
|---|---|---|
| **MVP** | 0-6 months | Free / Pro / Premium; PayMongo integration |
| **Growth** | 6-12 months | Annual-only Pro (₱1,990/yr); test Premium at ₱999 |
| **Maturity** | 12-24 months | Team tier (5-user bundle ₱2,999/mo); API access |
| **Enterprise** | 24+ months | Custom contracts; SLA; on-premise option |

### 17.4 Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Low conversion from Free to Pro | Medium | High | Improve AI teaser quality; add in-app upgrade prompts |
| Groq price increases | Low | Medium | Cache aggressively; maintain fallback to local models |
| Competition from free tools | Medium | Medium | Differentiate with Philippine-specific data and RAG accuracy |
| Server downtime | Low | High | DO automated backups + UptimeRobot alerts + rollback plan |
| Payment fraud / chargebacks | Low | Low | PayMongo handles fraud detection; require verified email |

---

*End of LUMI Pricing & Subscription Strategy*
