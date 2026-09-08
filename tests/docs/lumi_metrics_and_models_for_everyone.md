# LUMI Metrics and Models — Explained Like You're Ten

**Document Type:** Plain-Language Guide for Thesis Defense Q&A and Non-Technical Stakeholders  
**Project:** LUMI (Lightweight Utility for Municipal Intelligence)  
**Date:** June 2026  

---

## Part 1: What Is LUMI Trying to Do?

Imagine you are running a lemonade stand. Every day, you write down how many cups you sold. After a month, you have a list like this:

- Monday: 20 cups
- Tuesday: 25 cups
- Wednesday: 22 cups
- ...

Now your friend asks: **"How many cups will you sell next Monday?"**

That's basically what LUMI does — except instead of lemonade, it predicts **how much electricity the Philippines will use** next year. And instead of guessing randomly, it uses "smart math" (we call them **models**) to make the best guess possible.

LUMI also tells you things like:
- "How much solar power could a small town make?"
- "Should this city build a wind farm or a hydro plant?"

To do all this, LUMI uses **machine learning models**. But how do we know if the model is doing a good job? That's where **metrics** come in.

---

## Part 2: What Is a "Metric"?

A metric is just a **score** that tells you how good (or bad) a guess was.

Think of it like a test in school. If you guess the answer to a math problem, your teacher marks it right or wrong. If you get 8 out of 10 right, your score is 80%.

For predicting electricity, we don't have "right or wrong" answers — because nobody knows the future! Instead, we have **"how close was your guess to what actually happened?"**

That's what metrics measure: **closeness.**

---

## Part 3: The Metrics LUMI Uses

### 1. MAE — Mean Absolute Error

#### Kid Version
Imagine you guess your friend is 130 cm tall. But your friend is actually 140 cm tall. You were off by 10 cm.

Now imagine you make 4 guesses about how tall different friends are:
- Guess 130, actual 140 → off by 10
- Guess 150, actual 145 → off by 5
- Guess 120, actual 125 → off by 5
- Guess 160, actual 160 → off by 0

MAE says: "On average, how many cm was I off?"
(10 + 5 + 5 + 0) ÷ 4 = **5 cm**

#### LUMI Version
MAE tells us: **"On average, how many GWh (gigawatt-hours) was LUMI's electricity forecast off by?"**

- If MAE = 5,000 GWh, that means LUMI's guesses were, on average, 5,000 GWh away from the real number.
- **Lower is better.** The best LUMI model has MAE = 5,994 GWh.

#### Why It Matters
MAE is easy to understand. If your model has MAE = 6,000 GWh, you can tell your parents: "Our guess was off by about 6,000 GWh on average." That's like being off by the electricity use of a small city.

---

### 2. RMSE — Root Mean Squared Error

#### Kid Version
This is like MAE, but it **punishes really bad guesses more**.

Imagine you guess how many candies are in a jar:
- Guess 50, actual 52 → off by 2
- Guess 30, actual 60 → off by 30

RMSE says: "That second guess was REALLY bad, so I'm going to make your score worse than MAE would."

It does this by **squaring** the errors before averaging them. Big errors become HUGE after squaring.

#### LUMI Version
RMSE tells us the same thing as MAE, but it cares more about **catastrophically wrong guesses**. If LUMI accidentally predicts 200,000 GWh when the real number is 100,000 GWh, RMSE will scream much louder than MAE.

- **Lower is better.**
- Best LUMI model: RMSE = 7,342 GWh.

#### Why It Matters
Sometimes one terrible guess is worse than many small misses. If you're planning the national power grid, a HUGE wrong guess could cause blackouts. RMSE makes sure we don't ignore those disasters.

---

### 3. MAPE — Mean Absolute Percentage Error

#### Kid Version
Your teacher gives a test. The highest possible score is 100. You got 80.

How wrong were you? You missed 20 points out of 100. That's **20% wrong**.

MAPE does the same thing, but for predictions. It says: "How wrong was your guess, as a **percentage** of the real answer?"

- Real answer: 100,000 GWh
- Your guess: 105,000 GWh
- You were off by 5,000
- MAPE = (5,000 ÷ 100,000) × 100 = **5%**

#### LUMI Version
MAPE is super useful because it's a **percentage**. It doesn't matter if you're predicting big numbers or small numbers — MAPE always gives you a percentage.

- If MAPE = 5%, you can say: "Our model was wrong by about 5%."
- **Lower is better.**
- Best LUMI model: MAPE = 4.97%.

#### Why It Matters
Imagine telling a government planner: "We predict 120,000 GWh." They ask: "How sure are you?" If you say "MAPE = 5%," they instantly understand: "Okay, it could be 5% higher or lower." Percentages are easy to explain.

---

### 4. R² — R-Squared (The "Goodness" Score)

#### Kid Version
Imagine your teacher gives you a super hard puzzle. You solve most of it, but leave a few pieces blank.

R² asks: **"How much of the puzzle did you actually solve?"**

- R² = 1.0 → You solved 100% of the puzzle. Perfect!
- R² = 0.0 → You solved 0%. Your guess was no better than just guessing the average every time.
- R² = -0.5 → You solved **negative** puzzle. Your guesses were actually WORSE than just guessing the average.

#### LUMI Version
R² tells us: **"How much of the 'ups and downs' in electricity use did our model actually capture?"**

- If R² = 0.95, the model explains 95% of why electricity use changes.
- If R² = 0.30, the model only explains 30% — most of the pattern is still a mystery.
- **Higher is better** (closer to 1.0).

#### Why It Matters
A high R² means your model "gets it." It understands WHY electricity goes up and down. A low R² means your model is basically just lucky guessing.

---

### 5. MPE — Mean Percentage Error

#### Kid Version
MAPE tells you HOW WRONG you were. MPE tells you WHICH DIRECTION you were wrong.

- MPE = +5% → You usually guessed **too high** (over-forecast).
- MPE = -5% → You usually guessed **too low** (under-forecast).
- MPE = 0% → You were wrong equally in both directions. No bias!

It's like if you always aim a little too far to the right when throwing a ball. MPE tells you: "You have a right-leaning problem."

#### LUMI Version
MPE reveals **systematic bias**.

- If MPE = +3%, LUMI consistently predicts MORE electricity than reality.
- This matters for policy: if you always over-predict, you might build too many power plants.
- **Closer to 0% is better.**

#### Why It Matters
If your model is always too high or always too low, that's a **fixable problem**. MPE helps you spot the bias so you can correct it.

---

### 6. AIC and BIC — The "Keep It Simple" Scores

#### Kid Version
Imagine two kids both solve a math problem correctly:
- Kid A uses 2 steps.
- Kid B uses 20 steps.

Who did it better? Kid A! They got the same answer with way less work.

AIC and BIC are like that. They ask: **"How good was your answer, AND how complicated was your method?"**

A model that uses 50 fancy rules to get a slightly better answer might actually be WORSE than a simple model, because it's too complicated and might break later.

#### LUMI Version
AIC and BIC **penalize complexity**. If you add extra bells and whistles to your model but only get a tiny improvement, AIC and BIC will say: "Not worth it."

- **Lower is better.**
- If ARIMA(1,1,1) has AIC = 325 and SARIMAX(1,1,1) has AIC = 340, ARIMA wins — it's simpler AND better.

#### Why It Matters
In science, we love simple answers. AIC and BIC stop us from building overly complicated models that "cheat" by memorizing the past but fail at predicting the future.

---

### 7. Directional Accuracy (DA)

#### Kid Version
Your friend asks: "Will it rain tomorrow?" You don't need to know exactly how many millimeters of rain. You just need to know: **up or down?**

Directional Accuracy asks: **"Did you correctly guess whether the number went UP or DOWN?"**

- Real: 100 → 110 (went UP)
- You guessed: 100 → 105 (went UP) → **Correct direction!**

You don't need to guess the exact number. Just the direction.

#### LUMI Version
For energy planners, knowing **"demand will increase"** is sometimes more useful than knowing "demand will be exactly 118,004 GWh."

- DA = 80% means: "Our model correctly predicted 'up or down' 80% of the time."
- **Higher is better.**

#### Why It Matters
If you're a government planner deciding whether to build a new power plant, you mainly care: "Is demand going up or down?" Directional Accuracy answers that.

---

### 8. PICP — Prediction Interval Coverage Probability

#### Kid Version
Imagine your mom asks: "What time will you be home?" You say: "Between 4:00 PM and 5:00 PM."

If you actually get home at 4:30 PM — **you were right!** Your "interval" covered the real answer.

If you get home at 6:00 PM — **you were wrong.** Your interval was too small.

PICP asks: **"How often does your 'between X and Y' guess actually contain the real answer?"**

#### LUMI Version
When LUMI forecasts electricity, it doesn't just give one number. It gives a **range**:

- "We predict 120,000 GWh, and we're 95% sure it will be between 115,000 and 125,000 GWh."

PICP checks: **"Out of 4 test years, how many actual values fell inside our predicted range?"**

- PICP = 100% → All real values were inside our range. (But maybe our range was too wide — like saying "between 1 and 1 million.")
- PICP = 50% → Only half were inside. Our range was too narrow.
- **Target: ~95%** → Just right. We said "95% confident" and 95% of real values landed inside.

#### Why It Matters
Knowing a single number is nice. But knowing **"it's probably between X and Y"** is much more honest and useful for planning.

---

## Part 4: Metrics That DON'T Work for LUMI

### Accuracy, Recall, and F1-Score

#### Kid Version
Imagine a game where someone shows you an animal, and you have to say: "Cat or dog?"

- Accuracy = How many did you get right?
- Recall = Of all the cats, how many did you correctly identify?
- F1 = A mix of both.

These are great for **sorting things into boxes** (cat box, dog box).

But LUMI doesn't sort things into boxes. It predicts **numbers** like "118,004 GWh." There's no "cat box" or "dog box" for 118,004.

#### LUMI Version
Accuracy, Recall, and F1 only work when:
1. You have **discrete categories** (e.g., spam vs. not spam, cat vs. dog).
2. You can make a **confusion matrix** (a table of right/wrong answers).

LUMI predicts continuous values. You can't make a confusion matrix for "predicted 118,004, actual 120,000." So these metrics are **meaningless** here.

#### The Right Tools for the Right Job
- **Sorting emails into spam/not spam** → Use Accuracy, Recall, F1.
- **Predicting how much electricity a country uses** → Use MAE, RMSE, MAPE, R².
- **Writing a recommendation letter about renewable energy** → Use Hallucination Rate, Faithfulness, Relevance (see LLM evaluation doc).

---

## Part 5: The Machine Learning Models — Explained Simply

LUMI tested 6 different "smart math recipes" to predict electricity. Here's what each one does.

---

### Model 1: Naive with Drift (The "Keep Doing What You Did" Model)

#### Kid Version
You sold 20 lemonade cups on Monday, 22 on Tuesday, 24 on Wednesday.

Your guess for Thursday? **26 cups!**

Why? Because you noticed you're selling about 2 more cups every day. So you just "keep going in the same direction."

That's the Naive model. It looks at the last number and the first number, figures out the average "drift" (how fast things are changing), and just keeps going in that direction.

#### Math-Brain Version
```
Forecast = Last Value + (How Many Steps × Average Change Per Step)
```

#### Why It Matters
This is the **dumbest smart model** — and that's on purpose! Any real model must beat the Naive model. If your fancy ARIMA model does WORSE than just "keep going in the same direction," then your fancy model is useless.

#### LUMI Result
- MAPE = 5.57%
- Not the best, but surprisingly close! Sometimes simple is powerful.

---

### Model 2: Linear Trend Regression (The "Draw a Straight Line" Model)

#### Kid Version
You plot your lemonade sales on a graph. You see the dots going up. You grab a ruler and draw a straight line through the dots.

Then you extend that line into the future. Where does it land next year? That's your guess.

#### Math-Brain Version
```
Electricity = (Some Number) + (Year × Slope)
```

The "slope" tells you: "Every year, electricity use goes up by about 3,190 GWh."

#### Why It Matters
This is the **most honest model** because it's just a straight line. You can explain it to anyone: "Every year, we use about 3,190 more GWh. So next year will be about this much."

#### LUMI Result
- MAPE = 4.97% — **BEST MODEL!**
- Sometimes the simplest answer is the right one.

---

### Model 3: ARIMA(1,1,1) (The "Memory" Model)

#### Kid Version
Imagine you're walking. Each step you take depends on:
1. **Where you were before** (memory)
2. **How fast you were going** (momentum)
3. **Random bumps in the road** (shocks)

ARIMA is like that. It remembers what happened last year, considers the trend, and adjusts for unexpected events.

The numbers (1,1,1) mean:
- **1** = Remember last year
- **1** = Look at the trend once
- **1** = Adjust for one recent shock

#### Math-Brain Version
ARIMA = **Auto**Regressive (remember past) + **Integrated** (difference to remove trend) + **Moving Average** (adjust for recent shocks).

#### Why It Matters
ARIMA is the **classic forecasting model** that economists and scientists have used for decades. It's like a wise old professor who says: "I've seen this pattern before."

#### LUMI Result
- MAPE = 5.67%
- Good, but Linear Trend beat it. This happens when the data is very close to a straight line.

---

### Model 4: Holt's Linear Exponential Smoothing (The "Forget the Past Slowly" Model)

#### Kid Version
You remember what happened yesterday, but you also remember what happened last week — just not as clearly.

Holt's model does the same thing. It gives **more weight to recent years** and gradually forgets the distant past. It also tracks the trend separately.

#### Math-Brain Version
Holt maintains two things:
- **Level** = What's the current "average"?
- **Trend** = How fast is it changing?

Both get smoothed over time, with recent data mattering more.

#### Why It Matters
Holt is great when you have a short history and just want to say: "What's happening NOW, and where is it going?"

#### LUMI Result
- MAPE = 5.44%
- Very close to the best! Good for short, simple data.

---

### Model 5: SARIMAX(1,1,1) + Exogenous (The "Use Extra Clues" Model)

#### Kid Version
You predict lemonade sales. But instead of just looking at past sales, you also look at:
- **The weather forecast** (hot days = more lemonade!)
- **Local events** (festival in town = more customers!)

SARIMAX is ARIMA, but it also uses **extra clues** (exogenous variables) like:
- Renewable energy share (%)
- Capacity margin (%)

#### Math-Brain Version
SARIMAX = ARIMA + **EX**ogenous variables (outside information).

#### Why It Matters
Using extra clues SOUNDS smart. But in LUMI's case, adding extra clues actually made the model WORSE.

Why? Because we only had 18 years of data. Adding 2 extra clues means the model has to learn more stuff with the same amount of data. It's like trying to learn 10 subjects when you only have time for 5.

#### LUMI Result
- MAPE = 8.28% — **Worst among statistical models!**
- Lesson: More information isn't always better if you don't have enough data.

---

### Model 6: Random Forest Regression (The "Overconfident Student" Model)

#### Kid Version
Imagine a student who memorizes every single answer from last year's test. They get a perfect score on practice. But on the real test, they fail — because the questions are different.

Random Forest is like that student. It builds hundreds of mini-decision trees and memorizes the training data perfectly.

- Training MAPE = 1.45% ("I know EVERYTHING!")
- Test MAPE = 13.41% ("Wait, these questions are different...")

The difference between training and test is called **overfitting**.

#### Math-Brain Version
Random Forest = 100+ decision trees, each trained on a random subset of data. Final answer = average of all trees.

It works great with **thousands** of observations. With only 18, it memorizes instead of learning.

#### Why It Matters
Random Forest was included as a **controlled experiment** — to PROVE why LUMI uses simple statistical models instead of fancy ML.

The thesis says: "We use basic statistical methods instead of advanced ML." Random Forest proves this was the right choice.

#### LUMI Result
- MAPE = 13.41% — **Worst overall!**
- But it served its purpose: it proved that ML overfits on tiny datasets.

---

## Part 6: Model Comparison Table (The "Report Card")

| Model | MAPE | Grade | What It Did |
|---|---|---|---|
| **Linear Trend Regression** | 4.97% | **A+** | Drew a straight line. Simple and perfect. |
| **Holt Smoothing** | 5.44% | **A** | Remembered recent years. Almost as good. |
| **Naive with Drift** | 5.57% | **A-** | Just kept going. Surprisingly smart. |
| **ARIMA(1,1,1)** | 5.67% | **A-** | Used memory + momentum. Good but beaten by a line. |
| **SARIMAX + Exog** | 8.28% | **B** | Tried too hard with extra clues. Not enough data. |
| **Random Forest** | 13.41% | **D** | Memorized training. Failed on real test. |

**Winner:** Linear Trend Regression. Why? Because Philippine electricity use from 2003–2024 is almost a perfect straight line going up. The simplest model saw that clearly.

---

## Part 7: The Big Takeaways

### For Metrics
1. **MAE** = "How far off, on average?" (Easy to explain)
2. **RMSE** = "How far off, but BIG mistakes hurt more" (Punishes disasters)
3. **MAPE** = "How far off, as a percentage?" (Easy to compare)
4. **R²** = "How much of the puzzle did we solve?" (Higher = better understanding)
5. **MPE** = "Do we always guess too high or too low?" (Reveals bias)
6. **AIC/BIC** = "Is our model too complicated for the answer it gives?" (Simpler is better)
7. **Directional Accuracy** = "Did we guess UP or DOWN correctly?" (Useful for planning)
8. **PICP** = "Did our 'range guess' actually cover the real answer?" (Honest uncertainty)

### For Models
1. **Simple models** (Linear Trend, Naive) can beat **fancy models** (Random Forest) when data is limited.
2. **More features** (SARIMAX with extra variables) can hurt if you don't have enough data.
3. **Fancy ML** (Random Forest) overfits — it memorizes instead of learning.
4. **The best model** is the one that captures the real pattern without cheating.

### The Golden Rule
> **"The best model is not the fanciest one. It's the one that understands the data honestly and tells you the truth about its own uncertainty."**

---

*End of Plain-Language Guide*
