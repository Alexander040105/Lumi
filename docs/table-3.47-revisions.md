# Table 3.47 — Revised Text (paste-ready)

Corrected wording for the three reviewer-flagged claims in **§3.9.22 — Table 3.47: LUMI
Forecasting Error and Response Time Metrics** (`1-4-CCS_LUMI_Thesis`, Google Doc, p. 202–203),
per `docs/megaplan-thesis-revision.md`. Every figure below is verbatim from the thesis's own
§3.3.13 results.

**How to use:** for each REV, open the Google Doc at the named part, select the quoted current
text, and paste the replacement *inside the existing table cell* (or paragraph). Do not rebuild
the table — keep its rows, headers, and formatting.

---

## REV-1 — Table 3.47 → MAE row → **Result** cell

*Current text ends with:* "…across the held-out 2021–2024 test years **— comparable to or better
than all five baseline models in the same evaluation run.**"

**Replace the entire Result cell with:**

> ARIMA(1,1,1) forecasts deviated by an average of 6,829.09 GWh/yr on national consumption (≈5.7%
> of the ~120 TWh annual figure), 1,019.66 MW on peak demand (≈5.6%), and 3,597.39 GWh/yr on
> renewable generation (≈13.7%) across the held-out 2021–2024 test years. In the six-model
> benchmark, the model was competitive — within about one percentage point of the best performer
> on national consumption (5.667% MAPE versus 4.965% for Linear Trend) — although it was not the
> best-performing model on every target: SARIMAX achieved the lowest error on peak demand
> (3.868%), and the linear-trend and Holt models achieved the lowest on renewable generation
> (9.405%). ARIMA(1,1,1) was retained for its diagnostic adequacy, its native prediction
> intervals, and the best direction-of-change accuracy among the evaluated models (72.7% of test
> years).

*Interpretation cell: leave as-is — its "single-digit…both headline targets" claim is accurate.*

## REV-2 — Table 3.47 → RMSE row → **Result** cell

*Current text:* "…**each roughly 20–30% higher than its corresponding MAE, indicating errors were
concentrated in a single year rather than spread evenly.**"

**Replace the entire Result cell with:**

> RMSE values of 8,257.12 GWh (consumption), 1,299.08 MW (peak demand), and 3,939.69 GWh
> (renewable generation) — 20.91%, 27.40%, and 9.52% higher than the corresponding MAE,
> respectively. The wider gaps on consumption and peak demand indicate that a few large errors —
> principally the 2024 demand surge — dominated the error totals for those series, whereas the
> smaller gap on renewable generation indicates errors were distributed more evenly.

*Interpretation cell: leave as-is — the 2024-surge / shared-under-forecast explanation stays.*

## REV-3 — Table 3.47 → ART row → **Result** cell AND **Interpretation** cell

**Replace the Result cell with:**

> The system responded in ~104 ms on average across 21 measured API endpoints (30 runs each for
> standard endpoints, 5 for compute-heavy flows), excluding live AI calls: standard endpoints
> averaged ~49 ms — most under 10 ms — while the heaviest user flow, a full EcoSim simulation
> including an AI recommendation served from the cached/fallback path, completed in ~612 ms.
> Live generative-AI calls form a separate latency class and are reported in the interpretation.

**Replace the Interpretation cell with:**

> The measured API response times remain well under the 2,000 ms limit used for this evaluation —
> the slowest recorded flow is more than three times below that limit, and the standard-endpoint
> average is under 50 ms per request — so dashboards, maps, and suggestions appear almost
> instantaneous to users. These figures cover the local API benchmark only; the two auth-gated
> endpoints are excluded from the total, so the figures reflect the actual time taken to handle
> requests. Live AI calls form a separate latency class not covered by the benchmark: a live
> generative-AI call averaged about 7.1 seconds in testing (up to 18.5 seconds at the longest),
> exceeding the 5,000 ms target, while the cached/fallback path answered in about 1.9 seconds
> and covers the common case once content is warm; the interface presents the AI feature with
> progress indicators to accommodate this slower path. The values are based on a local
> benchmark, and latency varies with network conditions, so further adjustment remains possible.

*What changed:* the old text claimed all response times met "predetermined limits — API below
2,000 ms, AI below 5,000 ms, web page loads below 3,000 ms." The benchmark never measured a live
AI call (§3.3.13.13/.17 record ~7.1 s mean, up to 18.5 s — over the 5 s target), and no page-load
measurement exists in the table. The rewrite scopes "below limits" to what was measured and
reports the AI latencies separately, as the reviewer required.

## REV-4 — §3.9.22 narrative paragraph (directly under Table 3.47)

*Current text:* "Table 3.47 shows the forecasting accuracy and system response‑time measurements
that were collected during LUMIs technical performance evaluation. The MAE and RMSE results
reveal that the ARIMA(1,1,1) forecasting model produced levels of prediction error, across
national electricity consumption peak demand and renewable‑energy generation. Meanwhile the
average API response time of 104 milliseconds indicates that LUMI responds quickly under local
testing conditions. These findings demonstrate LUMIs strengths while highlighting chances to
improve forecasting performance and to test LUMIs responsiveness under other operating
conditions."

**Replace the whole paragraph with:**

> Table 3.47 presents the forecasting-accuracy and system response-time measurements collected
> during LUMI's technical performance evaluation. The MAE and RMSE results show that the
> ARIMA(1,1,1) forecasting model produced competitive prediction errors across national
> electricity consumption, peak demand, and renewable-energy generation — performing within
> about one percentage point of the best baseline on consumption, though not achieving the
> lowest error on every target. The measured API results indicate that LUMI responds quickly
> under local testing conditions, while live AI calls form a separate, slower latency class
> addressed through progress indicators and a fallback path. These findings demonstrate the
> system's measured strengths while identifying opportunities to improve forecasting
> performance and to test responsiveness under other operating conditions.

## REV-5 *(optional)* — §4.1.4 System Performance

The section reports raw figures only and makes no overclaim — no edit required. For coherence
with REV-3, you may optionally add after "…Standard endpoints averaged approximately 49
milliseconds.":

> Live generative-AI calls form a separate latency class, averaging about 7.1 seconds, with the
> cached/fallback path answering in about 1.9 seconds.

---

## After pasting — acceptance checklist

- [ ] Table 3.47 no longer contains "comparable to or better than all five" or any superiority
      claim; ARIMA is described as competitive, consistent with §3.3.13.17
- [ ] The RMSE row states 20.91% / 27.40% / 9.52% (or an honest 10–27% range), and the
      error-concentration claim is scoped accordingly
- [ ] The ART interpretation distinguishes local-API vs live-AI latencies, reports ~7.1 s / ~1.9 s
      separately, and no longer asserts all-below-limits / "entitling…Excellent" for the AI class
      (the old "eight times" figure compared the 612 ms flow to the 5,000 ms AI limit — replaced
      with the correct ~3× margin vs the 2,000 ms API limit)
- [ ] The narrative paragraph under the table matches the corrected rows
- [ ] TOC repagination checked (Table 3.47 listed at p. 203; reviewer cited p. 202 — cosmetic)

*Awareness note (not part of this fix set):* §3.3.13.14 contains a duplicated paragraph block —
the literature-comparison passage is pasted twice, concatenated mid-sentence after
"…comparison file." — worth removing in a separate pass.
