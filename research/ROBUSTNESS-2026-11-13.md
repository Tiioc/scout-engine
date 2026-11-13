# Stress tests on the backtest, 2026-11-13

Run with `python3 scout.py robust --data <folder>`. The aim was to break the result. Mix under test: 30% small cheap companies, 20% momentum, 40% stocks at 2x under the trend rule, 10% gold. All figures after inflation unless stated.

| # | Test | Result | Verdict |
|---|---|---|---|
| 1 | 2x block rebuilt from daily data, the way a real fund resets each day | 10.7% a year, same as before. Worst single day for that block -35% (October 1987); its worst fall -76%. The software still picks the same mix | Holds |
| 2 | Trend rule at 6, 8, 10 and 12 months | 10.1% to 10.7% a year | Holds; not tuned to one setting |
| 3 | All costs doubled | 10.2% a year against 6.7% for stocks; same mix picked | Holds |
| 4 | Saving horizons of 10, 15 and 30 years | Same four blocks chosen each time, weights shift | Holds in direction |
| 5 | History starting in 1950, 1970, 1990 | 11.5%, 10.3%, 10.7% a year against 7.8%, 6.8%, 8.0% for stocks | Holds |
| 6 | Remove each block in turn | 10.4% to 11.0% a year whichever block is removed | Holds; no single block carries it |
| 7 | Known edges cut in half | 9.6% a year against 6.8% | Holds, smaller |
| 8 | History reshuffled in 5-year pieces, 4,000 times | Beats plain stocks over 20 years in 94% of runs; typical result 1.5 times stocks | Holds |
| 9 | 300 nearby mixes | 9.8% to 11.2% a year | Holds; the peak is flat, not a spike |
| 10 | Other developed countries, 1990 to 2026 (US dollars, before inflation) | Small cheap companies 10.1% against 6.6% for the market; momentum 7.9%; trend rule same return with the worst fall cut from 56% to 25% | Holds outside the US |
| 11 | Decade by decade | Beat plain stocks in 8 of 10 decades; behind in the 1980s (by 0.1) and the 2010s (10.0% against 11.6%) | Holds |

## What did not hold
- **Choosing on recent data alone is dangerous.** Using only 1990 onward, the software picks 100% in the 2x block. That is what tuning to one lucky period looks like, and it is the main flaw of popular backtesting tools. The Scout uses the full century and the walk-forward check to avoid it.
- **The 2x block can fall 35% in a day.** At 40% of the portfolio that is a 14% hit from that block alone before the rule can react.

## What cannot be tested here
- Real funds are milder than the research blocks they stand in for, and most are under 20 years old.
- Taxes. Switching the stock block about 1.5 times a year creates taxable gains outside a retirement account.
- The owner's behavior during a fall of more than half.
