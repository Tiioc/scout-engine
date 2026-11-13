# The Scout

A complete financial research and calculation analyst that finds opportunities across every area of money, forecasts them, and grades itself over years. It covers public markets, private companies, digital assets, real assets, money strategy, business and income, and emerging themes, with no area leading. It does not day trade or tip coins. It is research and advice only: it never trades, moves money, or sends messages for you. Nothing it produces is financial advice.

## The idea in four lines
1. Big wins are long shots one at a time, but not across many tries. The goal is many good, different, survivable shots over ten years.
2. Every play gets an honest probability, built the way the best AI forecasters build them.
3. Every forecast is logged before the outcome is known, then graded. The log is the proof.
4. One rule never bends: no play that can wipe you out.

## How you use it
- **Weekly edition.** Up to three deep plays, each specific, calculated and forecasted, plus The Board: the best current read in all seven areas. Read it, then tell Claude what you acted on.
- **Analysis on request.** Ask any financial question (compare two holdings, dividends versus growth, which account, rent versus buy) and get the numbers run with sources.
- **Decision memo.** Bring a live decision (job offer, equity grant, deal, business idea) and say "run a Scout memo on this."
- **Alerts.** It tells you when an entry, exit, or deadline condition is hit.
- **Practice mode.** It shows you a blinded historical case, you forecast, it reveals what happened. This trains you; it does not test the Scout.

Time needed: about 30 minutes a week.

## Folder map
| Folder | What is in it | Personal? |
|---|---|---|
| `CLAUDE.md` | The constitution: mission and hard rules | No |
| `engine/` | Runbook, forecasting method, rules, base rates, data sources, templates, settings | No |
| `.claude/agents/` | The specialist agents | No |
| `scripts/` | Safety gate, forecast aggregator, scorer, edition checker, financial calculator (plain code, tested) | No |
| `profile/` | Empty until you add `profile.md` | Yes |
| `ledger/` | Your forecasts, plays, actions, outcomes | Yes |
| `editions/` | Your weekly editions and memos | Yes |
| `research/` | The research this design is built on | No |
| `docs/` | Build steps, decisions and reasons, testing plan | No |

## It works with or without a profile
With no `profile/profile.md`, the Scout runs in universal mode: it finds the best plays that exist and states what each one requires (money, skills, access, location). Add a profile whenever you want and it also shows your fastest path in and applies sizing limits to your real numbers. Update the profile any time your situation changes. Nothing else needs rebuilding.

## Sharing with a friend
Give them a copy of this repo with `profile/`, `ledger/` and `editions/` emptied (see `docs/BUILD_STEPS.md`, "For a friend"). They need their own GitHub account and their own Claude plan. Your profile and ledger never leave your private repo.

## Cost
Designed to run on a Claude plan you already have, with free data sources only. No API billing, no paid data. Within that, it runs at full power: the strongest model for every judgment role and five independent forecasts per question. See `docs/DECISIONS.md`.

## Start here
`docs/BUILD_STEPS.md`
