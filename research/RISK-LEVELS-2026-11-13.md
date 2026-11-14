# Risk levels: the best mix for each loss limit

Run 2026-11-13 with `python3 scout.py levels --data <folder>`. 98 years of monthly data, 92,378 mixes. Each risky block may carry its own exit: out to cash when that block closes a month below its own 10-month average. Losses are the worst peak-to-bottom fall of the whole account in dollars. Growth is per year after inflation, before taxes.

| Limit on worst account fall | Growth per year | Worst 12 months | Mix |
|---|---|---|---|
| 15% | 4.2% | -13% | 10% stocks with exit, 20% momentum with exit, 40% gold, 30% bonds |
| 25% | 6.2% | -16% | 10% small cheap, 10% small cheap with exit, 30% momentum with exit, 50% bonds |
| 35% | 7.6% | -23% | 70% momentum with exit, 10% gold, 20% bonds |
| 40% | 8.3% | -26% | 10% small cheap, 10% momentum, 10% small cheap with exit, 40% momentum with exit, 30% gold |
| **50%** | **9.7%** | **-30%** | **20% small cheap, 10% small cheap with exit, 50% momentum with exit, 10% stocks at 2x with exit, 10% gold** |
| 60% | 10.8% | -49% | 10% small cheap, 50% momentum, 30% small cheap with exit, 10% momentum with exit |
| No limit | 11.2% | -60% | 20% small cheap, 70% momentum, 10% stocks at 2x with exit (worst fall 77%) |
| Plain stocks, for comparison | 6.8% | -66% | worst fall 84% |
| 60% stocks, 40% bonds | 5.0% | -45% | worst fall 63% |

## Reading it
- **Exits are what buy the safety.** Level 50 grows almost as fast as the earlier no-limit pick (9.7% against 10.3%) with a worst fall of 50% instead of 70%.
- **Level 50 is the proposed growth-stage mix.** Above it, each extra point of growth costs far more in losses.
- **Honest check:** mixes chosen using only the first half of history stayed inside their limits in the second half (worst falls of 17%, 20% and 29% for the 25, 35 and 50 limits) and grew 6.1%, 7.3% and 8.9% a year.
- Level 50 lost money in 27% of 12-month stretches, its worst single month was -28%, and its longest wait to regain a high was about six years.

## Limits of this
- A limit is the worst that happened in 98 years. The future can be worse. Rule R8 in the policy covers that case.
- The momentum block carries most of the weight. The research version is more extreme than any fund on sale, and a 1.5% yearly cost is assumed.
- Gold and bond figures are yearly data spread evenly across months, so their month-to-month swings are understated.
- Exits are checked monthly. A crash inside one month is not avoided.
- When an exit is on, that block sits in cash. Today (end of October 2026) the momentum fund's exit is on, so half the growth mix would be in the cash fund.
