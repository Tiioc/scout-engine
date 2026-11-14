# Core portfolio selection: pre-registration (written 2026-11-14, before any of these tests were run)

Purpose: choose the portfolio the owner may put money into now. This file fixes the candidates, the tests and the decision rule BEFORE results exist, so the winner cannot be picked after seeing them. The commit time of this file is the proof. Lesson from 2026-11-13: a mix chosen as the best of 92,378 on the same history was a start-date artifact. Here there is no search: a short list of candidates is judged by rules fixed in advance.

## Candidates (fixed; nothing is added or tuned after results)
Unlevered cores:
- C1 US total market 100 (VTI)
- C2 Global market weights: US 60, international 40 (VT)
- C3 US 80, international 20 (VTI + VXUS)
- C4 US 90, US small value 10 (VTI + AVUV)  [current core]
- C5 US 70, US small value 15, international 15 (VTI + AVUV + VXUS)
- C6 US 80, US large growth 20 (VTI + QQQM)
- C7 US 90, 10-year Treasuries 10 (VTI + VGIT/IEF)
With borrowed exposure (Roth IRA only):
- L1 US 85, 2x S&P 500 held only while the S&P 500 is above its 200-day average (2% band, daily check, next-day trade; otherwise bills) 15
- L2 US 50, same 2x-with-exit 50
- L3 US 50, 2x S&P 500 held always 50 (isolates what the exit adds)

Rebalance: monthly look, rebalance only if a slice is more than 5 points off target (the tested check-in rule). Fees: VTI 0.03%, VXUS 0.05%, AVUV 0.25%, QQQM 0.15%, IEF 0.15%, SSO 0.89% plus financing modeled at bills + 1.5%.

## Data (all free, all dated in the output)
US market, small value (Small-High), large growth (Big-Low): Ken French monthly and daily, 1926-07 to 2026-09. International: French Developed ex US, Europe, Japan, Asia Pacific ex Japan, Emerging (monthly from 1989/1990; daily from 1990). Bonds: 10-year Treasury total return built from FRED GS10 (1953 on). Bills: French. Real fund prices: Yahoo daily adjusted closes.

## Tests
- T1 US long history, monthly 1927-2026 (candidates without international: C1, C4, C6, C7 from 1953, L1-L3).
- T2 Out of sample: the same on 1927-1976 and on 1977-2026 separately.
- T3 1990-2026 with international (all candidates).
- T4 Rules outside the US: the small-value tilt, the growth tilt and the 2x-with-exit rule replayed inside Developed ex US, Europe and Japan.
- T5 Real fund prices, daily, from each fund's start (proxies spliced where a fund is younger, and marked).
- T6 Named crises: 1929-32, 1937-38, 1973-74, 1987, 2000-02, 2007-09, 2020, 2022, Japan 1990-2009.
- T7 Block bootstrap (12-month blocks) of 1927-2026: 25 years of equal monthly deposits.
- T8 Today's conditions: T7 with stock returns lowered so the expected real return matches a CAPE near 41 (about 3% real), and bills at 4%.
- T9 Costs: borrowing spread 0.5% to 3%.
Every test reports, against C1: median ending wealth from monthly deposits, the chance of ending behind C1, the 10th-percentile outcome, the deepest fall, the worst 12 months and the longest time under water.

## Decision rule (fixed)
A candidate can replace C1 only if ALL hold:
1. Median ending wealth ahead of C1 in T8 (today's conditions) by at least 3%.
2. Ahead of C1 in BOTH halves of T2 (where it can be tested) and in T3.
3. Its rule works in the same direction outside the US (T4), where testable.
4. Deepest fall no more than 10 points worse than C1 in every test, and no single-day loss above 35%.
5. The chance of ending behind C1 in T8 is below 50%.
6. Survives both Red Teams without a KILL and passes the safety gate.
Among those that pass, the highest T8 median wins; if two are within 3% of each other, the simpler one wins. If none passes, C1 wins by default (C2 if it is within 3% of C1 in T8 with a smaller deepest fall).
The riskier slice (L1) is judged separately as an optional add-on to the winning core by the same rules.

## Run through the Scout
Evidence pack in ledger/packs/, five sealed forecasters with different framings, two Red Teams (one re-implements the tests independently; one attacks fit, practicality and facts), the safety gate and the sizing tool, every forecast logged before outcomes, a written verdict checked by scripts/check_edition.py.
