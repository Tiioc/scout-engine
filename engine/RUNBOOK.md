# Runbook

The Chair (main session) follows these procedures. Dates are YYYY-MM-DD. Read `engine/config.json` for all numbers.

## A. Weekly edition

1. **Load state.** Read `CLAUDE.md`, `engine/config.json`, the last four editions, open plays in `ledger/plays.jsonl`, unresolved forecasts in `ledger/forecasts.jsonl`, and `profile/profile.md` if it exists.
2. **Resolve what is due.** For every forecast whose `resolves_by` date has passed, check the stated `resolution_source`, and append a record to `ledger/outcomes.jsonl` with the evidence link. If it cannot be resolved, record `"outcome": null` with the reason.
3. **Radar.** Launch the `radar` agent. It returns 30 to 80 raw candidates across all categories, tagged by category, deadline and source quality, and skips anything already in the ledger unless something material changed.
4. **Shortlist.** Pick the 6 to 10 candidates with the best mix of asymmetry (capped cost, large upside), specificity, and evidence quality. Keep at least four of the seven areas on the shortlist. No area may supply more than a third of it.
5. **Specialists, sealed.** Send each shortlisted candidate to the one or two relevant specialists (`markets`, `ventures`, `digital-assets`, `real-assets`, `money-strategy`, `business-income`, `themes`), in parallel. Give each only the candidate and its sources. Never show one specialist another's view. Each returns an evidence pack with dated excerpts from at least two source types, a reference class, and its own view.
6. **Forecast.** For each candidate still alive, follow `engine/FORECASTING.md`: sub-questions, base rate, sealed `forecaster` samples, `scripts/aggregate.py`.
7. **Red Team.** Send each candidate with its evidence pack and forecasts to `red-team`. It argues against, checks every number against its source, and returns KEEP, KILL or FIX with reasons. Killed candidates are logged in the edition.
8. **Safety gate.** Run `scripts/safety_gate.py` on each surviving play. BLOCK means killed and logged. No exceptions.
9. **Rank and select.** Rank survivors by the rule in `engine/RULES.md`. Take at most three deep plays. Then write The Board: for each of the seven areas, the best current read in one or two lines, with numbers from `scripts/fincalc.py` where they apply, or "nothing new". If none clears the bar in `config.json`, publish "No strong play this week" with the watchlist.
10. **Write.** Create `editions/YYYY-MM-DD.md` from `engine/TEMPLATES.md`. Append plays to `ledger/plays.jsonl` and forecasts to `ledger/forecasts.jsonl`.
11. **Check.** Run `python3 scripts/check_edition.py editions/YYYY-MM-DD.md`. Fix and re-run until it passes.
11b. **Dossiers and positions.** For each deep play write `editions/dossiers/<play-id>.md` from `engine/DOSSIER_TEMPLATE.md`. Review every open position in `ledger/positions.jsonl` against its thesis and triggers and write the Positions section.
12. **Commit and notify.** Commit everything and open a pull request titled `Edition YYYY-MM-DD` with the edition text as the description.
13. **Self-check.** Confirm the edition file exists, the checker passed, and the ledger gained records. If anything failed, open an issue titled `FAILED YYYY-MM-DD` saying what and why. A run that ends without an edition or a FAILED issue is a bug.

Budget guard: the default settings are the full-power ones. If a run cannot finish inside the plan's allowance, finish the plays already in progress, publish what is done, note it in the edition, and open an issue titled `USAGE` so the owner can choose lite mode (three samples per question, specialists on the mid-tier model). Never loop.

## B. Decision memo (on demand)

Triggered when the owner brings a live decision.
1. Restate the decision and the deadline. Ask at most three questions, only for facts that cannot be found.
2. Run steps 5 to 8 of the weekly procedure on this one decision, with `memo_samples` forecaster samples.
3. Write `editions/memo-YYYY-MM-DD-<slug>.md` from the memo template: recommendation first, then base rate, scenario table, strongest case against, questions to ask before committing, exit plan.
4. Log the forecasts and commit.

## B2. Analysis on request

When the owner asks a financial question (compare two holdings, dividends versus growth, which account, is this rate good, what would this be worth in ten years), answer it as a full analysis: gather current figures with dated sources, run the numbers with `scripts/fincalc.py`, show the comparison in a table, give the case for each side, and state what would change the answer. Use the relevant specialist and Red Team for anything that leads to a real-money decision.

## C. Alerts (light, daily if scheduled)

Check only: entry and exit conditions on open plays, deadlines within `alert_deadline_days`, and forecasts due for resolution. If something fired, open an issue titled `ALERT: <what>`. If nothing fired, do nothing and write nothing.

## D. Owner feedback

When the owner says what they acted on, append to `ledger/actions.jsonl` (play id, date, what they did, money and hours spent). When a play ends, record the result in `ledger/outcomes.jsonl` with `"kind": "play"`.

## E. Monthly scoring

1. Run `python3 scripts/score.py ledger/ > ledger/calibration-YYYY-MM.md`.
2. If there are fewer resolved forecasts than `min_resolved_for_calibration`, the report says "insufficient data". Do not draw conclusions from it.
3. Otherwise, summarize in three lines at the top of the next edition: overall score versus the base-rate-only baseline, the worst-calibrated range, and any correction now in effect.

## F. Quarterly review

1. Score by category. Count wins and losses on closed plays with money and hours spent versus forecast.
2. A category's share of Radar and specialist effort may shift by at most `max_quarterly_weight_shift`, and only if it has at least `min_resolved_per_category` resolved forecasts.
3. Extremizing or other calibration corrections may be fitted only with at least `min_resolved_for_extremizing` resolved forecasts.
4. Write proposals as a pull request titled `Quarterly review YYYY-Qn`. Nothing changes until the owner merges it.

## G. Practice mode (for the owner)

On request, build one blinded historical case from public data (names and years removed), ask the owner for a probability, record it in `ledger/practice.jsonl`, then reveal the outcome. Always state that this trains the owner and does not validate the Scout.
