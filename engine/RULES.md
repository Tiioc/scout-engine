# Rules

The numbers live in `engine/config.json`. The safety rules are enforced by `scripts/safety_gate.py`, which is plain code. This file explains them in words.

## 1. Safety floor (silent, enforced by the script)

The floor exists so the owner can keep taking shots for ten years. It caps money at risk. It does not cap time, effort, or career moves.

| Rule | What it means |
|---|---|
| S1 Blocked activities | Day trading, short-dated options, leverage and margin, crypto speculation, MLMs, and paid "opportunity" or trading courses are blocked unless the owner has explicitly overridden that item in `config.json`. The loss data on these is the strongest evidence in the research. |
| S2 Limited loss only | Nothing that can lose more than is put in. Blocks margin, short selling, writing options, personal guarantees, and unlimited-liability partnerships. Overrides do not lift this. |
| S3 Hours declared | Every play states a maximum number of hours in advance. Reaching it triggers the exit review. |
| S4 Single-bet cap | Money at risk in one play is at most `single_bet_pct` of net worth (the lower `single_bet_pct_thin` while net worth is under `thin_months` months of expenses). |
| S5 Speculative total cap | All money at risk across open speculative plays is at most `sleeve_pct` of net worth. |
| S6 Runway | No money-at-risk play while liquid savings are under `runway_months` months of essential expenses or while high-interest debt exists. Zero-cash plays are unaffected. |
| S7 Circuit breaker | If speculative money is down `breaker_drawdown` from its peak, no new money-at-risk plays for one quarter. |

With no profile, S4 to S7 cannot be computed. The gate then passes the play as "PASS (universal)" and the edition must state the money required so the reader can size it themselves.

These rules never appear in an edition as advice. A blocked play is listed under "Killed" with the rule number.

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

- At most three plays per edition.
- At most one big move (job, home, location, or anything using more than `big_move_hours` hours) recommended per quarter.
- A big move needs supporting evidence in three consecutive editions, unless a real deadline forces an on-demand memo.

## 5. Every play ships with an exit plan

Thesis in one sentence. What evidence would prove it wrong. The point at which the owner stops. Maximum loss in dollars and hours. Review date. What "doing nothing" would have produced, which is what the play is scored against.

## 6. Public-market picks

Individual stock or fund picks are paper-only: logged and tracked against a total-market index fund, never recommended for real money, until at least `paper_min_calls` resolved pre-registered calls beat the index after costs. Evidence says professionals rarely clear this bar, so expect it to stay paper.
