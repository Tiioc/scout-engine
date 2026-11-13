# Output templates

Plain language. Lead with the play. No generic advice anywhere.

## Weekly edition

```
# The Scout: Edition YYYY-MM-DD

**Headline:** <one sentence: the best play this week, or "No strong play this week">

## Play 1: <specific name>
**What:** <the opportunity in two sentences, with the named company / role / deal / program / deadline>
**Why now:** <the dated evidence that makes this timely, with sources>
**Forecast:** <probability of the main payoff> | short checks: <sub-question: probability, resolves by date>
**Upside:** <size, in dollars or position>
**Cost:** <money at risk> and <hours>
**If it misses:** <what it still leaves behind>
**Requires:** <money, skills, access, location>   (universal mode)
**Your path in:** <fastest realistic route>        (only with a profile)
**Wrong if:** <the evidence that would prove it wrong>
**Exit:** <the point to stop, and the review date>
**Where agents disagreed:** <one line, or "none">

## Play 2 / Play 3
(same fields)

## Watchlist
- <thing>: <what would turn it into a play>

## Killed this week
- <idea>: <reason, and the rule or check that killed it>

## Due and resolved
- <forecast id>: forecast <p>, outcome <yes/no>, source

## Scoreboard
<three lines from the latest scoring run, or "Insufficient data: N resolved forecasts">
```

Rules the checker enforces: at most three `## Play` sections; each play has Forecast, Cost, Wrong if, and Exit lines; no banned generic-advice phrases.

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
