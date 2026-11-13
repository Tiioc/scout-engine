# Rules

The numbers live in `engine/config.json`. The safety rules are enforced by `scripts/safety_gate.py`, which is plain code. This file explains them in words.

## 1. Safety floor (silent, enforced by the script)

The floor exists so the owner can keep taking shots for ten years. It caps money at risk. It does not cap time, effort, or career moves.

| Rule | What it means |
|---|---|
| S1 Blocked activities | Day trading, short-dated options, leverage and margin, crypto speculation, MLMs, and paid "opportunity" or trading courses are blocked unless the owner has explicitly overridden that item in `config.json`. The loss data on these is the strongest evidence in the research. |
| S2 Limited loss only | Nothing that can lose more than is put in. Blocks margin, short selling, writing options, personal guarantees, and unlimited-liability partnerships. Overrides do not lift this. |
| S3 Hours declared | Every play states a maximum number of hours in advance. Reaching it triggers the exit review. |
| S4 Single-bet cap | Money at risk in one play is at most `single_bet_pct` of net worth (the lower `single_bet_pct_thin` while net worth is under `thin_months` months of expenses). Within that cap the size comes from `scripts/sizing.py`, never from judgment. |
| S5 Speculative total cap | All money at risk across open speculative plays is at most `sleeve_pct` of net worth. |
| S6 Runway | No money-at-risk play while liquid savings are under `runway_months` months of essential expenses or while high-interest debt exists. Zero-cash plays are unaffected. |
| S7 Circuit breaker | If speculative money is down `breaker_drawdown` from its peak, no new money-at-risk plays for one quarter. |

With no profile, S4 to S7 cannot be computed. The gate then passes the play as "PASS (universal)" and the edition must state the money required so the reader can size it themselves.

These rules never appear in an edition as advice. A blocked play is listed under "Killed" with the rule number.

## 1b. Sizing

The owner chose a concentrated design on 2026-11-13: a few plays a year, each large enough to matter, instead of many small ones. The caps in `engine/config.json` are 10% of the portfolio in one play and 30% across all open plays.

- Size is computed by `scripts/sizing.py` from the play's scenario table. It finds the growth-optimal fraction against holding the benchmark, takes `kelly_fraction` of it (half by default, because the probabilities are estimates and over-betting costs more than under-betting), and applies the caps.
- No edge over the benchmark means no bet, however good the story is.
- The scenario table must include the worst realistic case, including total loss where possible. Red Team reviews the table before sizing: an optimistic table produces an oversized bet.
- **Trust ladder.** Caps and the Kelly fraction step up when the scoreboard earns it (`sizing.trust_ladder` in the config): 10% per play and 30% in total at half Kelly while unproven; 15% and 40% at three-quarters Kelly once 50 or more forecasts have resolved and the Scout has beaten base rates with a confidence interval that excludes zero. Moving up a stage is proposed in a quarterly review and needs the owner's approval.
- **Build plays** stake hours, not money. `scripts/sizing.py --hours` compares expected pay per hour with the owner's hourly value. The bar is `hours_multiple_to_publish` times that value. Money put into a build play still obeys the money caps, and nothing that can lose more than is put in is allowed (no personal guarantees, no leases signed personally).
- **Why not bet more than this.** Betting the full growth-optimal fraction maximizes growth only if the odds are exactly right. With estimated odds, half of it gives about three-quarters of the growth with far smaller drawdowns, and betting above the optimal fraction lowers growth while raising the chance of ruin. The caps exist because the Scout's odds are estimates.
- Bigger bets multiply whatever skill the Scout has, in both directions. Until the scoreboard has at least `min_resolved_for_calibration` resolved forecasts, every sized bet is printed with the line "The Scout's forecasting record is not yet proven."

## 2. Ranking

Rank surviving plays by **asymmetry score**:

1. Expected upside: probability of each winning scenario times its payoff.
2. Divided by total cost: money at risk plus hours at the owner's hourly value (use `default_hourly_value` with no profile).
3. Multiplied by a **residual factor** from 1.0 to 1.5 for what a miss still leaves behind: 1.0 nothing, 1.25 real skills or contacts, 1.5 a clearly better position for the next shot.
4. Multiplied by an **evidence factor** from 0.5 to 1.0 for source quality and how many independent sources agree.

Report raw expected value and the chance of total loss next to the score. A play needs a score above `min_score_to_publish` and at least two independent non-seller sources to be published.

## 3. Diversity of shots

Twenty bets on the same thing are one bet. Across any rolling 12 editions, no single category should hold more than `max_category_share` of published plays unless the scoreboard has earned it in a quarterly review. Flag any new play that depends on the same underlying outcome as an open play.

## 4. Change budget

- At most three deep plays per edition, plus The Board.
- At most one large reallocation or big move (anything using more than `big_move_hours` hours, or moving more than a quarter of investable money) recommended per quarter.
- A big move needs supporting evidence in three consecutive editions, unless a real deadline forces an on-demand memo.

## 5. Every play ships with an exit plan

Thesis in one sentence. What evidence would prove it wrong. The point at which the owner stops. Maximum loss in dollars and hours. Review date. What "doing nothing" would have produced, which is what the play is scored against.

## 6. Public markets and digital assets

The Scout researches, compares and forecasts long-term holdings: companies, funds, sectors, dividend and growth strategies, and digital assets as an asset class. It does not day trade, time short-term moves, or tip individual coins.

- Every market idea states its holding period (one year or more), the case for and against, the valuation and income numbers from `scripts/fincalc.py`, and what it is being compared with.
- Every market idea is tracked in the ledger against a plain total-market index over the same period. The scoreboard reports whether the Scout's ideas beat it. Evidence says most professionals do not, so the comparison is always shown.
- Sizing caps S4 and S5 apply to any real money. With no profile, the edition states the caps as percentages.
- Still blocked by S1 unless the owner overrides: day trading, short-dated options, leverage, and speculative coin punts. Researching digital assets as an asset class (what they are, how they have behaved, how to hold them safely, what share of a portfolio the evidence supports) is not blocked.
- Private companies are covered as investments. Always state how a non-insider could get exposure (public companies with real exposure, funds, regulated crowdfunding, secondary markets), the minimums, fees, lock-ups and investor-status rules, and treat anything "open to any small investor" as a warning to check, not a recommendation.

## 7. Balance

Category weights in `engine/config.json` are equal. Over any rolling 8 editions the deep plays should span at least four of the seven areas. The Board covers all seven every week.
