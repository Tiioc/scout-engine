# The Scout

A research and portfolio manager that runs on Claude. It does three jobs:

1. **Manages the long-term core.** A mix chosen by backtest on a century of public data. Once a month it checks one trend signal and prints the exact changes to make at your broker.
2. **Finds plays.** A weekly scan for a few deep opportunities where a small investor can have an edge, each researched, forecast, sized and tracked.
3. **Keeps score.** Every forecast is logged before the outcome and graded after. The record decides how much the Scout is trusted.

It gives advice only. It never places trades or moves money. It is not a financial advisor.

## Everyday commands
```
python3 scout.py monthly --deposit 1500 --holdings profile/holdings.json   # signal + exact changes
python3 scout.py size --years 3 --scenario 0.3:5 --scenario 0.7:0.2         # size one play
python3 scout.py calc compare ...                                           # financial calculator
python3 scout.py test                                                       # all automated tests
python3 scout.py backtest --data <folder>      python3 scout.py robust --data <folder>
```

## Map
| Folder | What is in it |
|---|---|
| `CLAUDE.md` | The constitution Claude reads first |
| `engine/` | Rules, settings (`config.json`), runbook, templates, data sources |
| `scripts/` | The tools: portfolio, signal, sizing, calculator, safety gate, backtest, stress tests, simulator, scoring |
| `.claude/agents/` | The research agents (radar, specialists, forecaster, red team) |
| `research/` | Evidence: investor playbooks, backtest, stress tests, approach test, source data |
| `editions/` | What the Scout has published |
| `ledger/` | Forecasts, plays, outcomes: the permanent record |
| `profile/` | Your private details and holdings (optional) |
| `tests/` | Automated tests |

## What it borrows from existing tools, and what it fixes
| Tool | What it does well | Its gap | What the Scout does |
|---|---|---|---|
| Backtesting sites | Deep historical tests | Easy to tune a mix to one lucky period; not linked to what you hold; not a monitor | A century of data, walk-forward and eleven stress tests built in; reads your holdings; monthly check |
| Rule-automation apps | Turn rules into automatic trades | Backtests look better than live results; short fund histories | Tests on research data back to 1928, assumes results will be worse, and shows by how much |
| Pie-based brokers | Automatic deposits and rebalancing to target weights | No research, no signal, no reason for the weights | Supplies the weights, the signal and the exact change list to enter |
| Robo-advisors | Hands-off | One generic portfolio | A mix chosen by test, plus a research engine with a graded record |

## Setup
1. Merge the open pull request so the rules take effect.
2. In the Claude Code cloud environment settings, add the domains in `engine/DATA_SOURCES.md` to the allowed list.
3. Optional: copy `profile/holdings.template.json` to `profile/holdings.json` and keep it current.
