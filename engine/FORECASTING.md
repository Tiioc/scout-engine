# Forecasting method

This copies what the best published AI forecasting systems do: independent forecasts from fresh evidence, combined statistically, checked against markets, then graded. Evidence for each step is in `research/FINDINGS.md`.

## The steps

1. **Decompose.** Turn the play into 2 to 5 sub-questions. Each must be yes/no, have an exact resolution source, and resolve in 30 to 90 days. These short questions are what make grading possible, because the play itself may take years. Also write one long-horizon question for the play's main payoff.
   - Good: "Will Company X file a Form D for a new raise by 2027-02-15? Source: SEC EDGAR."
   - Bad: "Will Company X do well?"

2. **Base rate first.** Before any search, name the reference class and look it up in `engine/BASE_RATES.md`. Write the number down. If no reference class fits, say so; the play is then "I don't know" unless strong direct evidence exists.

3. **Evidence pack.** The specialist gathers dated excerpts from at least two different source types (for example a filing plus news, or government data plus a company page). Record the URL and the date of each. Prefer primary sources. Flag seller sources.

4. **Sealed samples.** Launch `samples_per_question` separate `forecaster` agents in parallel (see `config.json`; default 5, 7 for memos). Run most samples on the strongest model and at least two on a different model, because mixed models disagree in useful ways. Each gets only: the question, the base rate, the evidence pack, and one framing from this list, a different one each:
   - outside view (start from the base rate, adjust slowly)
   - inside view (reason from the specifics)
   - devil's advocate (assume it fails; how likely is that)
   - what would have to be true
   - pre-mortem (it is the deadline and it did not happen; why)
   Never pass one sample's answer to another. Save each to `ledger/samples/<forecast-id>/sample-N.json` before aggregating.

5. **Aggregate with the script.** Run `python3 scripts/aggregate.py` on the sample probabilities. It takes the median in log-odds and clips to the range in `config.json`. Do not average by hand and do not adjust the result.

6. **Spread check.** If the script reports the spread is above `spread_flag`, send the disagreement to `red-team` to investigate before the number is final. One round only. A sample may be re-run once with the new evidence; log why.

7. **Market check.** If a prediction market or market price exists for the question, record it. If the Scout differs by more than `market_deviation_flag`, `red-team` must justify the gap in writing or the forecast moves halfway to the market. Log both numbers.

8. **Scenario table for the play.** Four rows: big win, modest win, flat, loss. Each with a probability (summing to 100%) and the outcome in dollars and in what it leaves behind (skills, contacts, position). State the maximum loss in dollars and hours.

9. **Log.** Append the forecast record to `ledger/forecasts.jsonl` in the format in `ledger/README.md`.

## Honesty rules
- Long shots stay long shots. A 12% chance of a large payoff is reported as 12%.
- Never raise a probability to make a play publishable.
- "I don't know" is required when evidence is thin (constitution rule 6).
- Agents on the same model share blind spots. Diversity comes from different evidence and different framings, so never give all samples the same framing.
