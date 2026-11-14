# Whole-life test of the three-stage plan

Run 2026-11-13 with `python3 scout.py lifecycle` and `python3 scout.py stress`. Real monthly market data, 1928 to 2025. All dollar figures are in today's money, before taxes. The plan: growth level until the account is 20 times yearly deposits, build level to 60 times, protect level after.

## 1. Every real stretch of history

Saver adding $1,500 a month, rising 2% a year above inflation.

| Years | Typical | Bad luck (1 in 10) | Worst ever | Plain stocks, typical | Plain stocks, bad luck | Time in growth / build / protect |
|---|---|---|---|---|---|---|
| 10 | $322K | $247K | $166K | $298K | $195K | 100% / 0% / 0% |
| 20 | $1.10M | $841K | $616K | $949K | $504K | 62% / 37% / 0% |
| 30 | $2.90M | $2.18M | $1.46M | $2.27M | $1.32M | 41% / 39% / 20% |
| 40 | $6.06M | $4.55M | $3.20M | $4.80M | $3.32M | 31% / 27% / 42% |
| 50 | $12.47M | $7.99M | $6.77M | $9.40M | $6.68M | 24% / 23% / 53% |

Same saver stepping up to $3,000 a month in year 4 and $5,000 in year 7.

| Years | Typical | Bad luck | Worst ever | Plain stocks, typical | Plain stocks, bad luck |
|---|---|---|---|---|---|
| 10 | $661K | $523K | $348K | $621K | $439K |
| 20 | $2.84M | $2.28M | $1.57M | $2.48M | $1.33M |
| 30 | $7.92M | $6.03M | $3.87M | $6.13M | $3.46M |
| 40 | $17.35M | $12.84M | $8.70M | $13.62M | $9.00M |
| 50 | $35.32M | $23.88M | $19.98M | $26.64M | $19.18M |

## 2. The cost of stepping down

Staying at the growth level for life ended higher in ordinary history, and far higher over 40 to 50 years. The plan gives that up on purpose so that a crash late in life hits a calmer account.

| Years | The plan, typical | Growth level for life, typical | Worst fall in the final 10 years if 1929 repeats then: plan | Same, growth for life |
|---|---|---|---|---|
| 10 | $322K | $322K | -72% | -72% |
| 20 | $1.10M | $1.22M | -42% | -60% |
| 30 | $2.90M | $3.94M | -37% | -60% |
| 40 | $6.06M | $11.05M | -34% | -60% |
| 50 | $12.47M | $30.57M | -34% | -60% |

## 3. Worst-order test: the 1929 crash placed in the final years

| Years | Plan, bad luck | Growth for life, bad luck | Plain stocks, bad luck |
|---|---|---|---|
| 10 | $161K | $161K | $51K |
| 20 | $743K | $533K | $108K |
| 30 | $1.94M | $1.61M | $240K |
| 40 | $3.91M | $4.36M | $572K |
| 50 | $7.13M | $11.63M | $1.18M |

At 20 and 30 years the plan ends ahead of staying in growth when the crash comes last. At 40 and 50 years growth-for-life has built so much that it still ends ahead, but with a 60% loss at the end instead of about 35%.

## 4. Reshuffled history (2,000 made-up lifetimes per row, built from real two-year pieces)

| Years | Typical | Bad luck | Worst of 2,000 | Deepest fall seen | Plain stocks, bad luck | Plain stocks, deepest fall |
|---|---|---|---|---|---|---|
| 10 | $326K | $217K | $129K | -65% | $176K | -92% |
| 20 | $1.09M | $689K | $277K | -70% | $441K | -94% |
| 30 | $2.61M | $1.52M | $411K | -82% | $910K | -98% |
| 40 | $5.31M | $2.92M | $957K | -70% | $1.72M | -98% |
| 50 | $10.42M | $5.21M | $1.32M | -70% | $2.95M | -98% |

**Reshuffling produced falls far deeper than the record: up to about 80%.** The loss limits are what happened, not a ceiling. Rule R8 exists for this.

## 5. Named crashes and booms

| Episode | Growth | Build | Protect | Plain stocks |
|---|---|---|---|---|
| 1929 crash | -45% | -20% | -21% | -84% |
| 1937 slump | -28% | -10% | -15% | -50% |
| 1973-74 bear market | -10% | +1% | -6% | -47% |
| October 1987 | -27% | -18% | -15% | -30% |
| 2000-02 tech bust | -4% | -3% | +10% | -45% |
| 2008 financial crisis | -23% | -9% | -5% | -50% |
| 2020 virus crash | -16% | -10% | -8% | -20% |
| 2022 rate shock | -6% | -3% | -10% | -25% |
| 1933-36 recovery | +276% | +142% | +126% | +261% |
| 1950s boom | +366% | +232% | +133% | +368% |
| 1982-87 bull | +212% | +151% | +161% | +260% |
| late 1990s | +207% | +182% | +124% | +238% |
| 2009-19 bull | +206% | +117% | +105% | +454% |
| 2023-25 | +57% | +51% | +26% | +86% |

The plan lost far less in every crash. It also made less in long steady booms: in 2009 to 2019 the growth level made about half of what plain stocks did.

## 6. Rough-up tests (30-year plan, $1,500 a month)

| Change | Typical | Bad luck | Worst | Deepest fall | Plain stocks, typical |
|---|---|---|---|---|---|
| as tested | $2.90M | $2.18M | $1.46M | -50% | $2.27M |
| exits acted on one month late | $2.75M | $2.00M | $1.34M | -55% | $2.27M |
| all costs doubled | $2.44M | $1.91M | $1.22M | -52% | $2.25M |
| exit rule at 6 months | $2.50M | $2.00M | $1.46M | -60% | $2.27M |
| exit rule at 8 months | $2.44M | $1.95M | $1.36M | -59% | $2.27M |
| exit rule at 12 months | $2.88M | $2.06M | $1.32M | -55% | $2.27M |
| known edges cut in half (20-year plan) | $2.09M | $1.70M | $1.46M | -53% | $2.27M |
| known edges gone entirely | $1.53M | $1.15M | $915K | -53% | $2.27M |
| first half of history only (20-year plan) | $1.30M | $917K | $736K | -50% | $1.24M |
| second half of history only (20-year plan) | $1.03M | $751K | $616K | -27% | $930K |

## 7. What broke, and what did not

- **Held:** late exits, doubled costs, 12-month exit rule, either half of history, the 1929 crash at the start or the end. In every case the bad-luck result stayed above plain stocks.
- **Weakened:** exit rules of 6 or 8 months cost about 15% of the typical result. The 10-month setting is not magic; nearby settings work, some less well.
- **Broke:** if the advantage of small cheap companies and momentum disappears completely, the plan ends well behind plain stocks (about $1.5M against $2.3M at 30 years) while still falling less. With the advantage halved it ends slightly behind in a typical run and ahead in a bad one. **The plan's extra growth depends on those two edges continuing. Its loss protection does not.**
- **Not a ceiling:** made-up histories fell up to about 80%.
- **Trails in booms:** expect to lag the stock market for years at a time in a strong bull run.

## 8. What cannot be tested

- Real funds against the research blocks they stand in for.
- Taxes on the swaps.
- A future unlike any stretch of the last 98 years.
- Whether the owner follows the plan through a deep fall.
