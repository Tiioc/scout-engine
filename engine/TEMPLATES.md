# Output templates

Plain language. Lead with the play. No filler anywhere.

## Weekly edition

```
# The Scout: Edition YYYY-MM-DD

**Headline:** <one sentence: the best play this week, or "No strong play this week">

## Play 1: <specific name>
**Kind:** <money play / build play>   **Confidence:** <A or B, with the one-line reason>
**What:** <the opportunity in two sentences, with the named company / role / deal / program / deadline>
**Why now:** <the dated evidence that makes this timely, with sources>
**Forecast:** <probability of the main payoff> | short checks: <sub-question: probability, resolves by date>
**Scenarios:** <each outcome with its probability and ending multiple>
**Expected return:** <from scripts/sizing.py: expected multiple and annual return, versus the benchmark>
**Risk:** <chance of losing money, average loss when it loses, worst case>
**Bet:** <recommended share of the portfolio from scripts/sizing.py, in dollars if numbers exist, and what the best and worst case would do to the whole portfolio>
**Upside:** <size, in dollars or position>
**Cost:** <money at risk> and <hours>
**If it misses:** <what it still leaves behind>
**How to get exposure:** <the actual instruments or routes, minimums, fees, lock-ups, investor-status rules>
**The numbers:** <key figures from scripts/fincalc.py: yield, growth, valuation, projected value, versus the comparison>
**Compared with:** <the plain alternative, usually a total-market index over the same period>
**Entry:** <exactly what to do first: the instrument or first step, where, the price or condition to enter at, and whether to enter in stages>
**Wrong if:** <the evidence that would prove it wrong>
**Exit:** <the point to stop, and the review date>
**Where agents disagreed:** <one line, or "none">

## Play 2 / Play 3
(same fields)

## Positions
- <position>: <status against thesis> | <any exit or add condition triggered> | <next date to watch>
(or "No open positions.")

## The Board
- Markets: <best current read or "nothing new">
- Private companies: ...
- Digital assets: ...
- Real assets: ...
- Money strategy: ...
- Business and income: ...
- Emerging themes: ...

## Watchlist
- <thing>: <what would turn it into a play>

## Killed this week
- <idea>: <reason, and the rule or check that killed it>

## Due and resolved
- <forecast id>: forecast <p>, outcome <yes/no>, source

## Scoreboard
<three lines from the latest scoring run, or "Insufficient data: N resolved forecasts">
```

Rules the checker enforces: at most three `## Play` sections; each play has Forecast, Cost, Wrong if, and Exit lines; no banned filler phrases.

## Decision memo

```
# Scout memo: <decision> (YYYY-MM-DD)

**Recommendation:** <do it / don't / do it if X and Y check out>
**Confidence that this beats doing nothing over <period>:** <probability>

## Base rate
<reference class, number, source>

## Scenarios
| Scenario | Probability | Outcome | What it leaves behind |
|---|---|---|---|
| Big win | | | |
| Modest win | | | |
| Flat | | | |
| Loss | | | |

**Maximum loss:** <dollars and hours>

## Strongest case against
<Red Team's best argument>

## Ask before committing
- <question>

## Exit plan
Wrong if: ... | Stop at: ... | Review on: ...

## Market check
<market price if one exists, or "no external price available">
```

## Alert (issue body)
```
ALERT: <what fired>
Play: <id and name>
Condition: <the pre-set condition, quoted from the play>
Evidence: <source and date>
Suggested next step: <one line>
```
