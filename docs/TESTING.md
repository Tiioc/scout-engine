# Testing plan

The request was to replay the past ten years the way traders practice on old charts. A straight replay of the Scout's forecasts cannot work, because the model has already read how those years turned out (see `research/FINDINGS.md`, section 7). This plan tests everything that can be tested honestly, at no extra cost.

## Lane 1: mechanical replay (valid, do first)

Tests the parts that are plain code or plain rules. Outcomes do not depend on the AI's judgment.

- `python3 -m unittest discover -s tests` must pass. It includes historical wipeout shapes (margin in a crash, weekly options, buying a crypto top, a personal guarantee, an oversized single bet) and confirms each is blocked.
- Extend it: for each real shock of the last ten years (2020 crash, 2022 rate rise, 2022 crypto collapse, 2023 regional bank failures), write the play a person might have been tempted by and confirm the gate's verdict.
- Check each base rate in `engine/BASE_RATES.md` against its original source and mark it verified.
- Feed the edition checker deliberately bad editions (four plays, missing exits, generic advice) and confirm it fails them.
- Plant wrong numbers in a test evidence pack and confirm Red Team catches them.

Proves: the machinery is sound. Does not prove: the Scout finds good plays.

## Lane 2: sealed exam on recent questions (valid, small version is free)

Tests forecasting skill on questions the model cannot have memorized.

1. Collect yes/no questions that opened and resolved after June 2026 from public forecasting sites (Metaculus, ForecastBench question sets, resolved prediction markets).
2. For each, build an evidence pack only from sources with real publication dates before the question date. Do not rely on search-engine date filters.
3. Run the normal pipeline: base rate, sealed samples, aggregate, market check.
4. Score with `scripts/score.py` against base rate only and market price only. Report the confidence interval, not just the average.
5. Decide the pass bar before running, and report every run.

Free version: 30 to 50 questions spread over a few sessions on the plan. This shows gross problems but cannot prove a small edge. The full version (300 questions) was estimated at $500 to $1,500 through paid API use and is outside the no-cost rule.

## Lane 3: live forward record (the only real proof)

Every edition logs short forecasts that resolve in 30 to 90 days. `scripts/score.py` grades them monthly.

- About 100 resolved: enough to see if it is badly miscalibrated.
- About 300: enough to see whether it beats base rates.
- Two to three years: before results on the plays themselves mean much.

Every week of forward record is worth more than any replay.

## Lane 4: practice mode (for the owner, the chart-practice experience)

The Scout builds a blinded historical case from public data with names and years removed: a company's financials and funding history, or a region's housing and jobs data. The owner gives a probability, it is logged in `ledger/practice.jsonl`, and the outcome is revealed. Over time the owner gets a personal score.

This trains the owner's judgment. It proves nothing about the Scout, and famous cases may be recognizable.

## Rules for not fooling ourselves

- Never show the Scout's score without the baselines beside it.
- Always show the interval, not just the average.
- "Insufficient data" is the correct output until there is enough.
- Never present a replay of past years as evidence that the Scout's forecasts work.
