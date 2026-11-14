# Investment policy

The foundation. Every action the Scout advises must trace back to a line here. Written 2026-11-13; changes need the owner's approval.

## 1. Goal
Build real wealth while young, with the strongest odds the evidence supports, and never lose the ability to keep investing.

## 1b. Everything is in percent
This is the owner's whole investment portfolio. Dollar size does not change any rule. Targets, limits, exits and reports are all in percent of the account; dollars appear only as a translation.

## 1c. Three sleeves
| Sleeve | Purpose | Holds | Limit |
|---|---|---|---|
| Safety | Money needed within three years, and the emergency fund | A Treasury bill fund | Set by the owner's needs, not by the software |
| Core | Long-term growth with loss limits | The mix for the chosen risk level, each risky block with its own exit | The level's worst fall |
| Plays | Rapid growth from researched opportunities | A few sized positions, each with a written exit | Caps in `config.json`; counted inside the core's risk, never on top with borrowed money |

## 2. What "safe" means here
- **It does not mean no losses.** The growth mix fell 46% at its worst in 98 years of daily history, lost 17% in its worst single day, and lost money in about a quarter of all 12-month stretches. Something like that will happen again.
- **The loss limit is chosen, not hoped for.** `scripts/levels.py` finds, for each limit on the worst account-wide fall, the mix with the most growth. The owner picks the limit; the software supplies the mix. Limits come from history and are not guarantees, which is why rule R8 exists.
- **It means no wipeout.** The portfolio cannot go to zero unless every fund in it does. These protections make that so:
  1. Funds only in the core. No single company can sink it.
  2. No borrowed money in the account (no margin loan, no credit line). The 2x fund can lose most of its own value but never more than what was put in.
  3. Money needed within three years, and the emergency fund, are never in this portfolio.
  4. No single play above its cap; all plays together capped; the caps come from `config.json`.
  5. Every risky block in the core has its own exit, checked every week: when the fund ends a week more than 2% below its own 200-day average, the block moves to the cash fund; it returns when the fund ends a week more than 2% above it.
  6. An account-wide breaker (R8) steps the whole core down a risk level if losses ever exceed anything in the historical record.

## 3. Stages (elevated risk early, less later)
The stage depends on how large the account is compared with what goes in each year. Early on, a crash costs little because future deposits outweigh the balance. Later the balance is what matters.

| Stage | When | Growth per year in the record | Deepest fall in the record | Worst single day |
|---|---|---|---|---|
| **Growth** | Account under 20 times yearly deposits | 8.8% | 46% | 17% |
| **Build** | 20 to 60 times | re-chosen by test when the stage arrives | | |
| **Protect** | Over 60 times, or within 5 years of needing the money | re-chosen by test when the stage arrives | | |

Figures are after inflation, on daily prices from 1927 to 2025 with weekly exits. Earlier figures from month-end data (9.7% and 50%) were replaced on 2026-11-13: daily data gives lower growth and shows the monthly rule's true deepest fall was 60%.

The mixes now stored for Build and Protect fell 44% and 29% on daily data, which is not calm enough. They are placeholders. The growth stage lasts roughly the first decade, and the later mixes will be chosen by a fresh test before they are needed.

- The step-down points were chosen by `scripts/lifecycle.py`, not by hand: they gave the best result when a 1929-style crash was placed in the final years of a 20 or 30 year plan.
- A stage change happens only at a January review, and only downward. The plan never moves back to more risk by itself.
- With steady deposits the growth stage lasts roughly the first 11 to 13 years. Larger deposits keep the account in growth longer, which is intended: the stage follows how much is at stake, not the calendar.
- Evidence and limits: `research/LIFECYCLE-2026-11-13.md`.

## 4. The only reasons to change anything
| # | Trigger | Action | When |
|---|---|---|---|
| R1 | New deposit | Goes to the slice furthest below target | Any time |
| R2 | A block's exit signal flips at a week's end | Swap that block to the cash fund, or back | Next trading day |
| R3 | A slice is more than 5 points off target | Rebalance to target | Weekly check |
| R4 | January review: the backtest on new data picks a different mix, or the stage changes | Propose the new mix | January |
| R5 | A fund closes, changes what it does, or raises its fee sharply | Replace with the closest fund | When it happens |
| R6 | A play hits its written exit or "wrong if" condition | Exit as its dossier says | Weekly edition |
| R7 | The owner's situation changes (income, goal, need for cash) | Update the profile and the safety sleeve, then R4 | When told |
| R8 | The account is more than 5 points below the worst fall its risk level ever showed | Step the core down one risk level | Next weekly check; step back up only in January |

Nothing else is a reason. Not headlines, not a bad week, not a forecast about the economy, not a tip, not a price target.

## 5. No-panic rules
1. **Scheduled decisions only.** The core is checked once a week, after the week's last close. Plays are reviewed in the weekly edition. Nothing is decided between those dates. Weekly beat both monthly and daily checking in the test on daily data since 1927.
2. **Every action carries its reason.** Each advised step names the rule (R1 to R8) behind it. An action with no rule is not advised.
3. **Exits are written before entries.** No play is opened without its exit and "wrong if" conditions on paper.
4. **Falls are expected and pre-answered.** In a decline the only actions are R1 (keep depositing, which buys low), R2 (the exits) and, past the historical worst, R8. The monthly report shows the fall against the worst in history so it has context.
5. **Cooling-off.** Any change the owner or the Scout wants outside these rules waits until the next weekly check and must be tested first.
6. **No chasing.** Nothing is added because it went up. A new asset enters only through the backtest.

## 6. What the owner does
Put money in. Enter the monthly steps at the broker. Tell the Scout when life changes. That is all.

## 7. What the Scout reports every week
The stage, the signal, the exact steps with their rule numbers, how far the portfolio is from its high, and what the worst historical fall would mean in dollars today.
