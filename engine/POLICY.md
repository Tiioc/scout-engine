# Investment policy

The foundation. Every action the Scout advises must trace back to a line here. Written 2026-11-13; changes need the owner's approval.

## 1. Goal
Build real wealth while young, with the strongest odds the evidence supports, and never lose the ability to keep investing.

## 2. What "safe" means here
- **It does not mean no losses.** The growth mix fell about 70% at its worst in 98 years of history, and about a third of all years were down. That will happen again.
- **It means no wipeout.** The portfolio cannot go to zero unless every fund in it does. These protections make that so:
  1. Funds only in the core. No single company can sink it.
  2. No borrowed money in the account (no margin loan, no credit line). The 2x fund can lose most of its own value but never more than what was put in.
  3. Money needed within three years, and the emergency fund, are never in this portfolio.
  4. No single play above its cap; all plays together capped; the caps come from `config.json`.
  5. The trend rule moves the largest block to cash in long declines.

## 3. Stages (elevated risk early, less later)
The stage depends on how large the portfolio is compared with what goes in each year. Early on, a crash costs little because future deposits outweigh the balance.

| Stage | When | Mix | Why |
|---|---|---|---|
| **Growth** | Portfolio under 10 times yearly deposits | The software's growth mix | A 50% fall costs under 5 years of deposits and is bought back cheaply by new money |
| **Build** | 10 to 25 times yearly deposits | Re-chosen by the software with a limit on the worst fall | The balance now matters more than the next deposit |
| **Protect** | Over 25 times, or within 5 years of needing the money | Re-chosen with a tighter limit | Keeping it matters more than growing it |

The Build and Protect mixes are picked by rerunning the backtest when the stage arrives, not guessed today. A stage change happens only at a January review.

## 4. The only reasons to change anything
| # | Trigger | Action | When |
|---|---|---|---|
| R1 | New deposit | Goes to the slice furthest below target | Any time |
| R2 | Trend signal flips at a month end | Swap the stock block to the cash fund, or back | First trading day of the month |
| R3 | A slice is more than 5 points off target | Rebalance to target | Monthly check |
| R4 | January review: the backtest on new data picks a different mix, or the stage changes | Propose the new mix | January |
| R5 | A fund closes, changes what it does, or raises its fee sharply | Replace with the closest fund | When it happens |
| R6 | A play hits its written exit or "wrong if" condition | Exit as its dossier says | Weekly edition |
| R7 | The owner's situation changes (income, goal, need for cash) | Update the profile, then R4 | When told |

Nothing else is a reason. Not headlines, not a bad week, not a forecast about the economy, not a tip, not a price target.

## 5. No-panic rules
1. **Scheduled decisions only.** The core is touched on the first trading day of the month. Plays are reviewed in the weekly edition. Nothing is decided between those dates.
2. **Every action carries its reason.** Each advised step names the rule (R1 to R7) behind it. An action with no rule is not advised.
3. **Exits are written before entries.** No play is opened without its exit and "wrong if" conditions on paper.
4. **Falls are expected and pre-answered.** In a decline the only actions are R1 (keep depositing, which buys low) and R2 (the trend swap). The monthly report shows the fall against the worst in history so it has context.
5. **Cooling-off.** Any change the owner or the Scout wants outside these rules waits until the next monthly check and must be tested first.
6. **No chasing.** Nothing is added because it went up. A new asset enters only through the backtest.

## 6. What the owner does
Put money in. Enter the monthly steps at the broker. Tell the Scout when life changes. That is all.

## 7. What the Scout reports every month
The stage, the signal, the exact steps with their rule numbers, how far the portfolio is from its high, and what the worst historical fall would mean in dollars today.
