# Decisions and reasons

Each choice in the design, why it was made, and what it costs. Evidence is in `research/`.

| # | Decision | Why | Trade-off |
|---|---|---|---|
| 1 | Opportunity finder and forecaster, not a stock picker | Live tests show no reliable AI trading edge; wealth for people starting with little comes mainly from ownership, equity and position | Fewer "exciting" market calls |
| 2 | Lives in a private GitHub repo, run by Claude | Copyable for friends, independent of any one chat, and every forecast is timestamped by history so nothing can be backdated | One-time setup on GitHub |
| 3 | Engine, profile and ledger are separate | The owner's situation will change and friends should be able to use it. No profile means universal mode | Universal-mode plays cannot be sized to a person until numbers are added |
| 4 | Forecasting pipeline copied from top AI forecasters | It is what the systems now near superforecaster level actually do | More steps per play |
| 5 | Sealed independent samples, one challenge at most | Research: pooling independent answers gives the gain, debate does not | Agents cannot "talk it out" |
| 6 | Five specialists plus Red Team and forecaster; the main session is the Chair | Same-model agents share blind spots, so more agents add little; fewer parts fail less | Less fine-grained expertise at first |
| 7 | Five samples per question, seven for memos, on mixed models | Research: winning forecasting bots pool about five forecasts and gains level off near ten | Uses more plan allowance per run; drop to lite mode if a run cannot finish |
| 8 | Strongest model for specialists, forecasters, Red Team and Chair; mid-tier for the Radar sweep | Research: the underlying model matters more than scaffolding | Heaviest setting the plan allows |
| 9 | At most three plays; "no strong play" allowed; generic advice banned | The owner asked for specific, non-obvious, forecasted plays, not advice available anywhere | Some weeks are empty |
| 10 | Ranking favors capped cost and large upside, counting what a miss leaves behind | Outcomes are skewed; many different survivable shots is the realistic route to one large hit | Steady, low-upside moves rank low |
| 11 | Silent safety floor in plain code | Agents can be talked into things; code cannot. The loss data on blocked activities is the strongest evidence in the research | The owner must explicitly override to do a blocked activity |
| 12 | Floor caps money, not time or career moves | The largest early bets are made with time and position | Time can still be wasted; hence the hours budget |
| 13 | Short forecasts (30 to 90 days) attached to every play | Plays take years to resolve; short questions make grading possible within months | Extra bookkeeping |
| 14 | Small, bounded self-adjustment; rule changes need approval | Prevents overreacting to a lucky or unlucky streak | Slow to adapt |
| 15 | No backtests as evidence | The model has read the past; replays measure memory | No ten-year track record on day one |
| 16 | Free only: existing Claude plan, free data, GitHub | The owner does not want extra bills | Uses plan allowance; no paid startup databases; friends need their own plan |
| 17 | Notifications through GitHub pull requests and issues | Keeps "never sends messages" clean | The owner must have GitHub notifications on |
| 18 | Public-market picks paper-only | About 90% of professionals trail the index over 15 years | No real-money stock calls |

## Changes after Edition #1 (2026-11-13)

| Decision | Why | Trade-off |
|---|---|---|
| Scope widened to all of finance, seven areas with equal weight | Edition #1 came out as a startup job tracker; the owner wants investing, strategy and opportunities from every angle | More ground to cover each week |
| Companies and startups covered as investments, with the route for a non-insider | The owner cannot and does not want to take jobs at them | Many private companies have no honest route in |
| Career module off by default | Not what the tool is for | Can be switched on in config |
| Public markets and digital assets are researched and compared, not paper-only; every idea tracked against a total-market index | The owner wants long-term comparison and strategy, not tips | The Scout has no proven edge here, so the benchmark is always shown |
| Day trading, short-dated options, leverage and coin punts stay blocked | Strongest loss evidence in the research | Owner must override explicitly |
| The Board added: all seven areas every week | "All sorts of opportunities", without padding the deep plays | Longer edition |
| Financial calculator script | Arithmetic must be exact and repeatable | None |
| Concentrated sizing: few plays, each sized by scripts/sizing.py (half of the growth-optimal fraction), caps of 10% per play and 30% in total | The owner wants plays that add real money when one hits, not many tiny bets | Larger losses when a play misses; multiplies the Scout's skill in both directions, and that skill is not yet proven |
| A deep play must show an edge over the benchmark | Bigger bets are only defensible when the odds are clearly good | Most weeks will have no deep play |
| One forecaster call per framing covering all questions | Edition #1 used about 45 agents, too heavy to run weekly | Slightly less isolation between questions |

## Confidence in the finished product

Estimates by Claude on 2026-11-13. Not measured.

| Outcome | Estimate |
|---|---|
| Runs reliably each week within two weeks of starting | about 85% |
| Most editions pass the specific / non-obvious / forecasted test | about 75% |
| Forecasts reasonably calibrated within six months | about 65% |
| A few plays a year the owner would not have found and judges worth acting on | about 60% |
| Owner meaningfully ahead in ten years because of it, if they act consistently | about 55 to 65% |
| At least one large, life-changing hit in ten years | about 20 to 35% |

Biggest risks, in order: not acting on plays; thin public data on private companies; the model stating a specific that is wrong (Red Team's source check exists for this); the scheduled-task feature changing while it is a preview.

## What would change these decisions
- If the scoreboard shows a category beating base rates with enough data, it earns more effort.
- If three-sample forecasts prove poorly calibrated, raise samples before anything else.
- If the owner adds money to the budget later, the first upgrades are more samples per question and a larger Lane 2 exam, not paid data.

## 2026-11-13 (later): research and portfolio manager
| Decision | Why |
|---|---|
| The Scout also manages the long-term core | The owner asked for stable long-term holdings handled by the same tool |
| The core mix is chosen by backtest, not set by hand | Owner: "let the software decide." 92,378 mixes on 98 years of data; walk-forward and eleven stress tests passed |
| The 2x block is allowed inside the core only, under the trend rule | The software picked it and it survived daily-data modeling; it stays blocked for plays |
| Advice-only link to the broker | The owner's broker has no trading interface for outside software, and the Scout never trades in any case |
| One entry point, `scout.py` | Fewer commands to remember; every tool tested |
| Old design report and build steps moved to `research/archive/` | They describe the first version |
