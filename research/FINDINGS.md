# What the research found

Three rounds of research in November 2026 shaped this design. This file is the summary. The first full report is in `report-1-design.md`. Figures here were reported by the research agents with citations; they have not all been re-checked against the original sources, and anything marked "secondary" or "unverified" in the reports should be confirmed on first use.

## 1. Where an AI analyst has an edge and where it does not

- **Trading: no edge.** Live tests of AI trading agents show the ones that look best on static benchmarks do not win when actually trading. Published backtest gains shrink or vanish once the model is tested on a period it has not read about.
- **Forecasting: now close to the best humans, with caveats.** On the ForecastBench leaderboard, several AI systems were reported in July 2026 as statistically indistinguishable from superforecasters. Metaculus notes that live head-to-head results still slightly favor top humans, and that parity claims rest largely on benchmarks.
- **So the limit is not raw forecasting skill.** It is the quality of the questions, the quality of the evidence, and whether the owner acts.
- **Real edges:** breadth of scanning, discipline (base rates, checklists, written exits), no emotion, and decisions specific to one person that no fund or tool covers.

## 2. How the best AI forecasters work (what the Scout copies)

- Search that the system directs itself, iterating, beats a single fixed search.
- Several independent forecasts, combined statistically. Gains level off after about ten.
- A supervisor that investigates where the forecasts disagree.
- Calibration after the fact, and capping forecasts away from 0% and 100%.
- Comparing with market prices. One system trailed the market alone but blending with the market beat the market.
- Winning Metaculus bots used more distinct research sources than non-winners.
- A plain baseline (one search, five forecasts, aggregate) is already strong, and the underlying model matters more than elaborate scaffolding.

## 3. Agents arguing does not help; independent answers do

- A NeurIPS 2025 study found that pooling independent answers accounts for most of the gain credited to multi-agent debate, and that debate alone does not improve expected correctness.
- Other studies found majority pressure stops agents from correcting each other, and more debate rounds can make results worse.
- Agents on the same model share blind spots. Real diversity comes from different evidence, different framings, and different reference classes.

Design consequence: sealed samples, one targeted challenge at most, and fewer agents with distinct data rather than many agents with the same view.

## 4. Where wealth comes from for people who start with little

- Business ownership is how the top gets rich: over 40% of top-1% wealth is business wealth, and about 80% of households worth $30M or more own businesses. The median attempt is modest: about half of new employer businesses survive five years.
- Startup equity is skewed: about 73% of venture-backed companies returned nothing to founders, about 2.4% returned over $100M.
- Early career, future earnings are the largest asset. Job switchers out-earn stayers on average, but the gap moves with the labor market.
- Winners in public markets are rare: about 4% of listed US companies account for the market's entire net gain since 1926, and about 90% of professional large-cap funds trail the index over 15 years.

Design consequence: favor ownership, equity and positioning plays with capped cost; count what a miss leaves behind; keep public-market picks on paper.

## 5. What reliably loses money

| Activity | Finding |
|---|---|
| Day trading | 97% of those who persisted over 300 days lost money (Brazil, 2020 study); no evidence of learning |
| Most active retail traders | Trailed the market by about 6 to 7% a year after costs (Barber & Odean) |
| Retail options | Losses concentrated in short-dated options; size of losses is disputed, but no study shows an edge |
| Crypto speculation | An estimated 73 to 81% of retail app users lost money on bitcoin (BIS) |
| MLMs | The vast majority received $1,000 a year or less (FTC, 2024) |
| Active stock picking | About 90% of professional funds trail the index over 15 years (SPIVA) |

Design consequence: these are blocked by the safety gate unless the owner explicitly overrides one.

## 6. Why risk-adjusted ranking, not raw expected value

A typical venture-backed founder's outcomes are worth about $4.4M to someone indifferent to risk, and only slightly more than zero to someone with normal risk aversion (Hall & Woodward). A small chance of a huge payoff is not worth its average to a person who cannot absorb the misses. So the Scout caps the cost of each shot and seeks many different shots.

## 7. Why a 10-year replay of the AI's forecasts does not work

- Current Claude models have read text through June 2026. Replaying 2016 to 2026 tests memory.
- One benchmark found returns fell by 15 to 17 percentage points once models left the period they had memorized.
- Telling a model to "pretend it is 2018" fails: its reasoning looks compliant while its accuracy still reflects what it knows.
- Search-engine date filters leak: Google's "before:" filter returned pages with later information for 71% of test questions, and the outright answer for 41%. With leaky documents a model scored at superforecaster level; with clean documents it scored barely better than a coin flip.

What can be tested honestly is in `docs/TESTING.md`.

## 8. How to build and run it (verified against official docs unless noted)

- Claude Code cloud scheduled tasks run a full cloud session on a schedule against a GitHub repo, with the computer off. They are a research preview, available on paid plans, with a one-hour minimum interval, and draw on plan usage.
- A scheduled run can use subagents, web search and fetch, and commit to the repo.
- "Succeeded" only means the session did not crash, so the run must check its own output.
- The default cloud environment blocks most outside sites. Data domains must be added to the allowed list.
- Subagents are Markdown files in `.claude/agents/`. Each can set its own model and tools. Misspelled settings are silently ignored.
- There is no built-in email on completion. Opening a pull request or issue makes GitHub send the notification, which keeps the Scout's "never sends messages" rule clean.
- Fallbacks: a desktop scheduled task (computer must be on), or GitHub Actions with an API key (pay per use, so outside the no-cost rule).

## 9. How long before the scoreboard means anything

- About 100 resolved short forecasts (three to four months) to see gross miscalibration.
- About 300 or more (nine to twelve months) to detect a real advantage over base rates.
- Two to three years before results on the plays themselves mean much, with wide error bars even then.

## 10. Known gaps

- Several data-source details (FRED limits, EDGAR full-text search, Polymarket reads, Atlanta Fed downloads) came from secondary sources.
- Kalshi's data terms were not reviewed, so it is not used.
- Scheduled-task limits changed several times in 2026. Recheck before relying on any one number.
- The first report contains one inconsistent Carta figure on option exercise rates; it is not used anywhere in the engine.
- Descriptions of famous investors' methods were paraphrased, not page-cited. The agent checklists use general principles only.
