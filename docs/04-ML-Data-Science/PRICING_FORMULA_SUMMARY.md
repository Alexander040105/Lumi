# LUMI Pricing & Subscription Strategy: Formula Summary

**Project:** LUMI (Lightweight Utility for Municipal Intelligence)  
**Module:** Pricing & Subscription Economics  
**Date:** June 2026

---

## Executive Summary

LUMI's three-tier SaaS pricing model (Free / Pro / Premium) is built on a cost-plus foundation with value-based adjustments. The model uses six core formulas: fixed infrastructure allocation, per-interaction AI token cost, operational overhead per user, cost-plus pricing with margin, break-even analysis, and portfolio-margin aggregation. Because AI marginal costs are negligible (₱0.01 per interaction using llama-3.1-8b-instant), pricing is driven by infrastructure recovery and value capture rather than usage-based scaling. The model achieves break-even at 7 paying users, 27% margin at 50 users, and scales to 48% margin at 1,000 users.

---

## 1. Core Pricing Formulas

### 1.1 Fixed Infrastructure Cost

**What it is:** The baseline monthly cost to keep the platform running regardless of user count.

**Formula:**
```
Total Fixed Cost = Droplet Cost + Domain + Backups + Monitoring + CDN
```

| Component | Monthly Cost |
|---|---|
| DigitalOcean Droplet (2 vCPU, 2 GB) | $18.00 |
| Backups (20% of droplet) | $3.60 |
| Domain (amortized) | $0.83 |
| Monitoring + CDN | $0.00 (free tiers) |
| **Total Fixed** | **$22.83/mo = ₱1,324/mo** |

**Key constant:** $1 = ₱58 (mid-2026 approximate rate).

**Why this matters:** Infrastructure is fixed — you pay the same whether 1 person or 100 people use the platform. This means the cost per user drops dramatically as you scale.

---

### 1.2 AI Token Cost Per Interaction

**What it is:** The marginal cost of one AI chat message or insight, calculated from Groq's token pricing.

**Formula:**
```
Chat Cost = (Input Tokens / 1,000,000 × $0.05) + (Output Tokens / 1,000,000 × $0.08)
```

**Typical chat (2,850 input + 300 output tokens):**
```
= (2,850 / 1,000,000 × 0.05) + (300 / 1,000,000 × 0.08)
= $0.0001425 + $0.000024
= $0.0001665 = ₱0.0097 per chat
```

**Typical EcoSim AI insight (2,500 input + 500 output tokens):**
```
= (2,500 / 1,000,000 × 0.05) + (500 / 1,000,000 × 0.08)
= $0.000125 + $0.00004
= $0.000165 = ₱0.0096 per insight
```

**Why this matters:** At less than 1 centavo per interaction, AI costs are effectively zero compared to the ₱199–₱799 subscription price. The pricing model is not usage-sensitive.

---

### 1.3 Infrastructure Allocation Per Paying User

**What it is:** How much of the fixed server cost each paying user must cover.

**Formula:**
```
Infrastructure per Paying User = Total Fixed Cost / Number of Paying Users
```

**Example (30 paying users out of 100 total):**
```
= $22.83 / 30 = $0.761 = ₱44.14 per paying user
```

**Why this matters:** Free users do not pay, so their infrastructure cost is subsidized by paying users. The more paying users, the lighter the load on each.

---

### 1.4 Total Cost Per User (Cost-Plus Base)

**What it is:** The full cost to serve one user, combining infrastructure share, AI usage, and operational overhead.

**Formula:**
```
Total Cost per User = Infrastructure Allocation + AI Cost + Operational Allocation
```

**Example (Pro tier at 100 MAU):**
```
= ₱44.14 + ₱0.533 + ₱200.00
= ₱244.67
```

| Component | Value | Rationale |
|---|---|---|
| Infrastructure | ₱44.14 | Fixed cost divided by 30 paying users |
| AI (50 chats + 5 insights) | ₱0.533 | 50 × ₱0.0097 + 5 × ₱0.0096 |
| Operational | ₱200.00 | Support, maintenance, admin (modest at small scale) |

**Why this matters:** This is the "floor" price — anything below this loses money on every user.

---

### 1.5 Cost-Plus Pricing with Margin

**What it is:** The theoretical price derived by adding a profit margin to the total cost.

**Formula:**
```
Price = Total Cost per User / (1 − Target Margin)
```

**Example (Pro tier, 50% margin):**
```
= ₱244.67 / (1 − 0.50)
= ₱244.67 / 0.50
= ₱489.34
```

**Problem:** Cost-plus gives almost identical prices for Pro and Premium because infrastructure is shared and AI costs are negligible. This is economically correct but fails to capture value differentiation.

**Solution:** Switch to **value-based pricing**.

---

### 1.6 Value-Based Price Adjustment

**What it is:** Prices set based on what each user segment is willing to pay, not what it costs to serve them.

| Segment | Value Perception | Willingness to Pay | Final Price |
|---|---|---|---|
| Students / Researchers | Thesis tool, learning aid | ~₱150–300 | **₱199/mo** |
| Professionals / Planners | Decision-making, ROI-driven | ~₱500–1,000 | **₱799/mo** |
| Enterprises / Government | Scale deployment, compliance | Custom | Contact Sales |

**Why this matters:** A student values LUMI as a ₱200 textbook alternative. A consultant values it as a ₱800 substitute for ArcGIS Pro ($700/yr). Same product, different perceived value.

---

## 2. Break-Even & Portfolio Formulas

### 2.1 Break-Even Formula

**What it is:** The minimum number of paying users needed to cover fixed costs.

**Formula:**
```
Break-Even Users = Total Fixed Cost / Contribution Margin per User
```

**Example:**
```
= ₱1,324 / (₱399 − ₱200)
= ₱1,324 / ₱199
= 6.65 → 7 paying users
```

| Metric | Value |
|---|---|
| Total Fixed Cost | ₱1,324/mo |
| Average Revenue Per User (ARPU) | ₱399/mo |
| Contribution Margin per User | ₱199/mo |
| **Break-Even Paying Users** | **7 users** |
| Break-Even Total Users (70% free) | ~23 users |

**Why this matters:** With only 7 paying subscribers, the platform covers its server costs. This is achievable through a single university partnership.

---

### 2.2 Portfolio Profit Formula

**What it is:** The aggregate profit when all tiers are combined, accounting for cross-subsidization.

**Formula:**
```
Portfolio Profit = Total Revenue − Total Cost
Portfolio Margin = Portfolio Profit / Total Revenue
```

**Example (100 MAU: 70 Free, 20 Pro, 10 Premium):**
```
Total Cost = ₱1,324 + (70×₱0.058 + 20×₱0.533 + 10×₱2.132) + (30×₱200)
           = ₱1,324 + ₱36.04 + ₱6,000
           = ₱7,360.04

Total Revenue = (20 × ₱199) + (10 × ₱799)
              = ₱3,980 + ₱7,990
              = ₱11,970

Portfolio Profit = ₱11,970 − ₱7,360.04 = ₱4,609.96
Portfolio Margin = ₱4,609.96 / ₱11,970 = 38.5%
```

**Why this matters:** Pro users are individually unprofitable (₱199 revenue vs ₱244 cost), but Premium users (₱799 revenue vs ₱246 cost) subsidize them. The portfolio as a whole is healthy.

---

### 2.3 Profit Margin by Tier (Individual)

| Tier | Revenue | Cost | Margin | Notes |
|---|---|---|---|---|
| **Free** | ₱0 | ₱13.30 | — | Acquisition cost only |
| **Pro** | ₱199 | ₱244.67 | **−22.9%** | Subsidized by Premium |
| **Premium** | ₱799 | ₱246.27 | **69.1%** | Subsidizes Free + Pro |

---

### 2.4 Margin at Scale

| Total Users | Free | Pro | Premium | Revenue | Cost | Profit | Margin |
|---|---|---|---|---|---|---|---|
| 10 | 7 | 2 | 1 | ₱1,197 | ₱1,928 | **−₱731** | **−61%** |
| 50 | 35 | 10 | 5 | ₱5,985 | ₱4,342 | **₱1,643** | **27.4%** |
| 100 | 70 | 20 | 10 | ₱11,970 | ₱7,360 | **₱4,610** | **38.5%** |
| 250 | 175 | 50 | 25 | ₱29,925 | ₱16,414 | **₱13,511** | **45.1%** |
| 500 | 350 | 100 | 50 | ₱59,850 | ₱31,854 | **₱27,996** | **46.8%** |
| 1000 | 700 | 200 | 100 | ₱119,700 | ₱62,034 | **₱57,666** | **48.2%** |

**Key insight:** LUMI reaches profitability at approximately **30–35 paying users** (~100 total users). Margins asymptote toward ~50% as the fixed infrastructure is spread across more users.

---

## 3. Tier Feature Allocation Logic

### 3.1 Feature Gating Rationale

| Feature Type | Free | Pro | Premium |
|---|---|---|---|
| **Computationally cheap** (charts, maps, calculators) | ✓ Full | ✓ Full | ✓ Full |
| **LLM-expensive** (AI insights, chat) | 1–5/mo | 5–50/mo | 20–200/mo |
| **Persisted state** (saved simulations) | 3 total | 20 total | Unlimited |
| **Data portability** (export, sharing) | ✗ | ✗ | ✓ |
| **Priority support** | ✗ | ✗ | ✓ |

**Logic:** Free users get full analytical value (no marginal cost to serve), but limited AI access (the expensive part). Upgrading unlocks persistent workflows and AI-powered decision support.

---

### 3.2 Annual Discount Formula

**What it is:** Incentive for annual commitment.

**Formula:**
```
Annual Price = Monthly Price × 10 (2 months free)
Discount = 1 − (10/12) = 16.7% ≈ 17%
```

| Tier | Monthly | Annual | Effective Monthly | Savings |
|---|---|---|---|---|
| Pro | ₱199 | ₱1,990 | ₱165.83 | ₱398/yr |
| Premium | ₱799 | ₱7,990 | ₱665.83 | ₱1,598/yr |

**Why this matters:** Annual subscriptions improve cash flow and reduce churn. A user paying ₱7,990 upfront is locked in for 12 months.

---

## 4. The "One Big Formula"

### Unified Pricing Equation

If you had to express LUMI's entire pricing strategy as a single master formula:

```
Price(tier) = MAX(
    (FixedCost / PayingUsers + AI(tier) + OpEx) / (1 − Margin),   ← Cost floor
    Value(tier) × WillingnessToPay(tier)                            ← Value ceiling
)

Where:
  FixedCost = $22.83/mo = ₱1,324/mo
  AI(tier) = (chats × ₱0.0097) + (insights × ₱0.0096)
  OpEx = ₱200/user/mo
  Margin = 0.50 (target)
  Value(free) = ₱0 (acquisition)
  Value(pro) = ₱199 (student/researcher WTP)
  Value(premium) = ₱799 (professional WTP)
```

**In plain English:** The price is the **greater of** (a) what it costs to serve the user plus a 50% profit margin, or (b) what the user segment is willing to pay. In practice, (b) always wins because cost-plus yields ~₱490 for both tiers, which fails to differentiate value.

---

## 5. Payment Processing Cost

### 5.1 Transaction Fee

**Formula:**
```
Processing Fee = (Price × 2.9%) + ₱15
Effective Rate = Processing Fee / Price
```

| Tier | Price | Fee | Effective Rate | Net Revenue |
|---|---|---|---|---|
| Pro | ₱199 | ₱20.77 | 10.4% | ₱178.23 |
| Premium | ₱799 | ₱38.17 | 4.8% | ₱760.83 |

**Why this matters:** Small transactions hurt more. PayMongo's ₱15 flat fee is 7.5% of a ₱199 Pro subscription but only 1.9% of a ₱799 Premium subscription.

---

## 6. Thesis Justification Summary

### 6.1 Business Viability

| Factor | Justification |
|---|---|
| **Low break-even** | Only 7 paying users needed; achievable through university partnerships |
| **High-margin Premium** | 69.1% unit margin subsidizes Free/Pro tiers |
| **Negligible AI cost** | llama-3.1-8b-instant costs <₱0.01 per interaction |
| **Fixed infrastructure** | $18/mo droplet serves all users until 250+ MAU |

### 6.2 Research Contribution

| Contribution | How Pricing Strengthens It |
|---|---|
| **Decision Support System Design** | Tiered access demonstrates how feature gating balances utility and resource constraints |
| **AI in Environmental Systems** | Cost-transparent AI pricing shows how LLM costs can be managed in resource-constrained apps |
| **Philippine RE Policy** | Student/Pro pricing makes the tool accessible to future energy researchers and policymakers |
| **Sustainability Science** | Freemium model is a sustainable business model for research tools — avoiding grant dependency |

---

## 7. Quick Cheat Sheet

| # | Formula | What It Does | Key Constant | Location |
|---|---|---|---|---|
| 1 | Fixed Infrastructure | Baseline monthly cost | $22.83/mo | Pricing doc §2 |
| 2 | AI Token Cost | Marginal cost per interaction | ₱0.0097/chat | Pricing doc §3 |
| 3 | Infrastructure per User | Fixed cost ÷ paying users | ₱44.14 @ 30 users | Pricing doc §4.2 |
| 4 | Total Cost per User | Cost-plus base | ₱244.67 (Pro) | Pricing doc §4.4 |
| 5 | Cost-Plus Price | Cost ÷ (1 − margin) | ₱489 (Pro) | Pricing doc §4.4 |
| 6 | Value-Based Price | WTP-driven final price | ₱199 / ₱799 | Pricing doc §4.5 |
| 7 | Break-Even Users | Fixed cost ÷ contribution | 7 paying users | Pricing doc §11 |
| 8 | Portfolio Profit | Revenue − total cost | ₱4,610 @ 100 users | Pricing doc §7.6 |
| 9 | Portfolio Margin | Profit ÷ revenue | 38.5% @ 100 users | Pricing doc §7.6 |
| 10 | Annual Discount | Monthly × 10 | 17% (2 months free) | Pricing doc §3.2 |
| 11 | Processing Fee | (Price × 2.9%) + ₱15 | 10.4% (Pro) | Pricing doc §15 |

---

## 8. Paragraph Summary for Panel Defense

LUMI's pricing model is a three-tier freemium SaaS strategy grounded in actual infrastructure costs and Philippine market conditions. The model begins with a cost-plus foundation: a $22.83 monthly fixed infrastructure cost (DigitalOcean droplet, backups, domain) is divided across paying users, adding a negligible AI token cost of less than one centavo per interaction using Groq's llama-3.1-8b-instant model, plus a ₱200 operational allocation per user for support and maintenance. Cost-plus pricing with a 50% margin target yields ~₱490 for both Pro and Premium tiers, which is economically correct but fails to differentiate value. Therefore, the model switches to value-based pricing: students and researchers who perceive LUMI as a thesis tool are charged ₱199 monthly, while professionals who use it for investment decisions are charged ₱799 monthly. At the individual level, Pro users are slightly unprofitable (−23% margin), but Premium users are highly profitable (+69% margin), creating a cross-subsidization structure where Premium pays for Free. The portfolio reaches break-even at just 7 paying users (~23 total users), achieves 27% margin at 50 users, 38% at 100 users, and asymptotes toward 48% at scale. Annual subscriptions offer a 17% discount (2 months free) to improve cash flow and reduce churn. Payment processing through PayMongo adds 4.8%–10.4% in fees, which is factored into net revenue calculations. The entire pricing architecture supports LUMI's mission of broad social impact through free access while ensuring financial sustainability through paid tiers.

---

*Pricing strategy sourced from LUMI_PRICING_AND_SUBSCRIPTION_STRATEGY document. All formulas and assumptions current as of June 2026.*
