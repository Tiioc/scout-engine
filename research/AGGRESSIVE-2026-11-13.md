# Aggressive portfolio with an exit, 2026-11-13

Status: Chair's test, NOT yet passed by the Red Team. Run: `python3 scripts/aggressive.py --data <data dir>`.

Method: real daily fund prices (SPY, SSO, UPRO, BIL; Yahoo, pulled 2026-11-13) from 2007-06, and Ken French daily market returns from 1926-07 with a modeled 2x and 3x fund (daily reset, borrowing at bills + 1.5%, 0.9% fee). Exit: leave the borrowed fund when the S&P 500 is more than 2% below its 200-day average, return when more than 2% above, traded at the next day's close, 0.05% per switch. Every start date, all five check-day phases, monthly deposits, rolling 5 and 10 year windows. Model check: the modeled 2x made 14.8% a year over SSO's life against 15.7% for the real fund, so the model is not flattering.

Candidate D: 50% stocks always held, 50% in a 2x S&P fund with the exit (exit check spread over five slices).

| Start | D per year | Stocks per year | D deepest fall | Stocks deepest fall | Monthly deposits, D against stocks |
|---|---|---|---|---|---|
| 2007-06 (real funds) | 12.9% | 10.5% | -39% | -55% | +22% |
| 2009-04 (real) | 16.9% | 15.6% | -33% | -34% | +17% |
| 2010-01 (real) | 15.3% | 14.0% | -33% | -34% | +16% |
| 2015-01 (real) | 13.9% | 13.4% | -33% | -34% | +10% |
| 2020-01 (real) | 15.8% | 14.8% | -33% | -34% | +7% |
| 2022-01 (real) | 11.3% | 11.4% | -28% | -24% | +4% |
| 1926-07 (modeled) | 12.8% | 10.3% | -69% | -84% | n/a |
| 1950-01 (modeled) | 13.8% | 11.6% | -45% | -55% | n/a |
| 1990-01 (modeled) | 13.0% | 11.0% | -45% | -55% | n/a |
| 2000-01 (modeled) | 10.6% | 8.5% | -45% | -55% | n/a |

D beat stocks in 76% to 92% of 5-year windows and 90% or more of 10-year windows.

Weak points found by the Chair:
- The gain comes from borrowing in rising markets. The exit is what stops a 2x fund's -85% (real, 2007 to 2009) or -98% (modeled, 1929 to 1932).
- A single check day can be unlucky: with one weekly check instead of five slices, the worst check day trailed stocks from some starts (5-year win rate as low as 22%).
- One-day crashes get through: a 1987-style day costs D about 26%.
- The deepest fall is about the same as plain stocks, not smaller.
- A 1x fund with the same exit lost to stocks from every start since 2007. The exit alone does not add return.
- 3x version (half stocks, half 3x with exit): 16% to 21% a year on real funds since 2009, but no real-fund 2008 test, modeled deepest fall -53% to -77%, worst day -35%.
- Ten candidates were tried; D and its 70/30 sibling were the simplest and were not tuned.
- Taxes on switches are not modeled.
