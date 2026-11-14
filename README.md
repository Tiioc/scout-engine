# The Scout

A research and portfolio manager that runs on Claude. It does three jobs:

1. **Holds the core.** 70% VTI, 30% AVUV (90/10 until the 2026-11-14 dose test), chosen by a pre-registered test of ten candidates over a century of data and attacked by two Red Teams (`editions/2026-11-14-core-verdict.md`). Set once; rebalanced only when a slice drifts more than 5 points.
2. **Hunts.** Twice a month it digs for one opportunity with a real edge, runs it past five forecasters and a Red Team, and puts survivors on a paper scoreboard against the S&P 500. Real money follows picks only after the scoreboard earns it.
3. **Watches and keeps score.** A quick check every weekday (texts only when something needs attention), a watch on companies the owner has a stake in, and every forecast logged before the outcome and graded after.

It gives advice only. It never places trades or moves money. It is not a financial advisor.

## Everyday commands
```
python3 scout.py scoreboard                                   # paper picks against the S&P 500
python3 scout.py check --deposit 500 --holdings profile/holdings.json   # where a deposit goes, any rebalance
python3 scout.py size --years 1 --scenario 0.3:1.5 --scenario 0.7:0.9   # size one play
python3 scout.py test                                         # all automated tests
python3 scripts/portfolio_lab.py --data <folder>              # the pre-registered core tests (January review)
```

## Map
| Folder | What is in it |
|---|---|
| `CLAUDE.md` | The constitution Claude reads first |
| `engine/` | Rules, settings (`config.json`), runbook, templates, data sources |
| `scripts/` | The tools: portfolio, signal, sizing, calculator, safety gate, backtest, stress tests, simulator, scoring |
| `.claude/agents/` | The research agents (radar, specialists, forecaster, red team) |
| `research/` | Evidence. Current: `CORE-PREREGISTRATION-2026-11-14.md`, `AGGRESSIVE-2026-11-13.md`, `REDTEAM-2026-11-13.md`, `INVESTOR_PLAYBOOKS.md`. Older 2026-11-13 files are the record of the retired growth mix |
| `editions/` | What the Scout has published |
| `ledger/` | Forecasts, plays, outcomes: the permanent record |
| `profile/` | Your private details and holdings (optional) |
| `tests/` | Automated tests |

## Setup
1. Merge the open pull request so the rules take effect (the scheduled runs use the pull request's branch until then).
2. Copy `profile/holdings.template.json` to `profile/holdings.json` and keep the two balances current, so the daily drift check works.
