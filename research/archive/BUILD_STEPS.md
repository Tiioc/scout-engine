# Build steps

Written for someone who does not code. Claude does the technical work. Your part is a few clicks and reading the output.

## What you need
- A GitHub account (free).
- A Claude plan that includes Claude Code on the web and scheduled tasks.
- About 30 minutes for setup, then about 30 minutes a week.

## Step 1: Create an empty private repo (2 minutes)
1. Go to github.com/new.
2. Repository name: `the-scout`.
3. Choose **Private**.
4. Do not add a README or any other file.
5. Click **Create repository**.

If Claude asks for access to the new repo, approve it for `the-scout` only.

## Step 2: Hand Claude the package (1 minute)
In a Claude chat that has this package, say:

> The repo the-scout is ready. Put the starter package in it, run the tests, and show me the result.

Claude adds the files, runs `python3 -m unittest discover -s tests`, and reports. All tests should pass.

## Step 3: Let the Scout reach its data (5 minutes, one time)
1. Open Claude Code on the web and go to the cloud environment settings.
2. Set network access to **Limited** and paste the domain list from `engine/DATA_SOURCES.md` into **Allowed domains**. Keep package managers allowed.
3. Optional and free: get keys for BLS and FRED and add them as secrets in the same settings. The Scout works without them, using web search instead.

## Step 4: Run Edition #1 by hand
Say:

> Run the weekly Scout edition now, following engine/RUNBOOK.md. Stop for my review after Radar, after the specialists, and after Red Team.

Read what it produces. Tell Claude what was vague, generic, or wrong. This is where most of the tuning happens.

## Step 5: Run two more by hand
Repeat for Editions #2 and #3, tightening as you go. Do not automate until an edition reads the way you want.

## Step 6: Automate
Say:

> Schedule the weekly Scout edition for Sunday evening. Open a pull request with each edition, and an issue titled FAILED if anything breaks.

Each edition then arrives as a GitHub notification. Turn on GitHub email or phone notifications for the repo so you see it.

## Step 7: Each week (30 minutes)
1. Read the edition.
2. Tell Claude what you acted on, in plain words. It logs it.
3. Merge the pull request.

## Later
- **Add your profile** whenever you want: see `profile/README.md`.
- **Monthly:** the scoreboard updates itself. It will say "insufficient data" for the first few months. That is correct.
- **Quarterly:** Claude proposes small adjustments as a pull request. Nothing changes unless you merge it.
- **Live decision:** say "run a Scout memo on this" and describe it.
- **Practice mode:** say "give me a Scout practice case."

## For a friend
1. Make a copy of this repo with `profile/`, `ledger/` and `editions/` emptied. Ask Claude: "Make a clean shareable copy of the Scout engine with nothing personal in it."
2. They create their own private repo from it, connect their own Claude plan, and follow Steps 3 to 7.
3. Their profile and ledger stay in their repo. Yours stay in yours.

## If something breaks
- No edition and no FAILED issue: tell Claude "the Scout did not run this week, find out why."
- An agent cannot reach a site: add its domain in Step 3.
- Editions are getting generic: tell Claude which lines, and ask it to add those phrases to the banned list in `scripts/check_edition.py`.
- Scheduled tasks stop working (the feature is a preview): run the edition by hand as in Step 4 until it is fixed.

## What this costs
Nothing beyond the Claude plan you already have. The package ships at full power: strongest model for every judgment role and five forecasts per question. A weekly run uses a real share of the plan's allowance, so schedule it for a time you are not using Claude. If a run ever cannot finish, the Scout says so and you can switch to lite mode in `engine/config.json`.
