# The Scout: Research Report and Recommended Design for a Personal Opportunity Finder Built with Claude

**Bottom line: build The Scout mainly as a career-and-decision engine with hard loss rules enforced in code, not as an investing engine. For someone early in their career with little capital, the evidence says the largest controllable gains come from income growth, cheap tax-advantaged saving, and a few capped asymmetric bets, while active trading, options, crypto speculation, courses and MLMs lose money for most participants.** This is research and design for your approval, not financial advice. I am not a financial advisor, and nothing below has been built.

## TL;DR

- **Where the edge is:** Your premise mostly holds, with one important correction. Live benchmarks still show no reliable LLM trading edge, so public markets should be a cheap index core plus mistake-prevention, and stock-picking should stay on paper. But in a July 16, 2026 post, the Forecasting Research Institute reported that "the top current system is from Cassi AI, with models from xAI and Google DeepMind also ranked as indistinguishable from superforecaster-level accuracy" on ForecastBench. For Cassi, equal accuracy could not be rejected (p = 0.41). Raw forecasting skill is therefore no longer the bottleneck. The real constraints are the quality of the questions, personal data, and your follow-through.
- **What to rank highest:** Career and income moves, employer benefits and tax savings, and people/programs/access rank highest on risk-adjusted value. Startup equity is a lottery ticket worth taking only when it comes free as part of a good job: Hall & Woodward found about 73% of venture-backed companies return nothing to their entrepreneurs. Day trading (97% of persistent Brazilian day traders lost money), retail options, crypto speculation and MLMs are noise or negative.
- **What to build:** v1 runs within a week on Claude Code. It uses subagent files with per-agent memory, one weekly cloud scheduled task, a git-based ledger, free data sources, and a deterministic loss-rule checker. Cost is roughly $15–40/month in API tokens at November 2026 list prices. Spending stops improving results around the "strong" tier (about $100–250/month). Past that, outcomes are limited by data access, by how many resolved outcomes the scoreboard has, and by what you actually do, not by model intelligence.

## Key Findings

### 1. Facts versus judgment: how to read this report

Statements tied to a named study, filing or official doc are **facts** as reported by that source on the date given. Statements marked **Judgment** are my design opinions. Probabilities in the sample memo are illustrative estimates anchored to named base rates, not forecasts about any real company. Some framework descriptions (Buffett, Marks, Thiel, Taleb, Tetlock, Naval and others) are drawn from those authors' own books and letters. I paraphrased them and did not re-verify them in this research pass; the build should attach page-level citations before treating them as rules.

### 2. Testing your premise: where I agree and where I disagree

**Premise A: "LLM agents do not reliably beat buy-and-hold at trading." Agree.**
- Live benchmarks were built precisely because backtests are contaminated. Agent Market Arena (live trading from August 1, 2025) and LiveTradeBench (50 trading days, August 18 to October 24, 2025, 21 LLMs) both moved to live evaluation.
- LiveTradeBench's authors found that "high LMArena scores do not imply superior trading outcomes."
- The AI-Trader benchmark concluded that "general intelligence does not automatically translate to effective trading capability."
- Look-ahead bias is serious enough that a standardized benchmark, Look-Ahead-Bench (2026), now exists just to measure it in point-in-time financial LLMs. Any backtest of an LLM on dates inside its training window is not evidence. Your forward-test-only rule is correct.

**Premise B: "LLMs still trail elite human forecasters." Outdated as of mid-2026.**
- FRI's original ForecastBench paper had superforecasters at a Brier score of 0.096, against 0.122 for the best LLM (Claude 3.5 Sonnet).
- By July 16, 2026, FRI reported that several systems (Cassi AI, xAI, Google DeepMind) are statistically indistinguishable from superforecasters. Cassi's system ranked above the superforecaster median on market questions, "the first time that any model has achieved this." 17 submissions ranked above superforecasters on dataset questions.
- FRI's own caveats: superforecasters were last elicited in 2024, and the comparison relies on statistical adjustment. The AIA Forecaster report also calls ForecastBench "a relatively easy forecasting benchmark."
- **Judgment:** this changes the design. The Scout should copy what the top systems actually do, not just "be careful." Cassi's published pipeline generates sub-questions and search queries, retrieves up-to-date context, filters for relevance and recency, forecasts with an ensemble of models, and has another LLM analyze the reasoning to produce the final number.

**Premise C: "Independence first, one round of challenge at most." Strongly supported, with one caveat you missed.**
- "Debate or Vote" (NeurIPS 2025) found that "Majority Voting alone accounts for most of the performance gains typically attributed to MAD" (multi-agent debate). It also showed theoretically that debate alone does not improve expected correctness.
- "Should We Be Going MAD?" (ICML 2024) found that debate does not reliably beat self-consistency or ensembling.
- Huang et al. found that self-consistency with an equivalent number of responses can beat debate.
- **The caveat:** nine "specialists" running on the same base model are not nine independent forecasters. Their errors are correlated. Real diversity has to come from different evidence (each specialist gets different data feeds), different reference classes, and possibly different model tiers or temperatures. Otherwise the "council" is one opinion repeated nine times.

**Premise D: "Rank everything on one list by expected value per dollar and per hour." Partly wrong.**
- Expected value is the wrong objective when outcomes are extremely skewed and losses can be ruinous.
- Hall & Woodward (AER 2010) show this exactly. A risk-neutral person values a typical venture-backed founder's outcome distribution at a certainty equivalent of about $4.4 million. With "normal risk aversion" (relative risk aversion of 2), the same distribution is worth "only slightly positive."
- **Judgment:** rank by certainty-equivalent value under log utility, subject to the ruin constraints first, and show raw EV alongside it. That is the honest version of "per dollar and per hour."

**Premise E: "Small opportunities professionals ignore." True for decisions, mostly false for deals.**
- **Judgment:** Professionals do ignore your negotiation, your benefits elections, your choice of employer, and a $50 grant application. Those are real edges.
- Small private deals offered to people with little capital are usually adverse selection: the good ones get filled by insiders. The Scout should treat "a deal available to me because I'm small" as a red flag by default.

**Premise F: "A quarterly scoreboard proves itself." Too optimistic about speed.**
- **Judgment:** Career and business outcomes take years to resolve, so a quarterly hit rate on big moves will be statistically meaningless for a long time.
- The scoreboard has to score many small, fast-resolving forecasts for calibration: "Will this posting still be open in 30 days?", "Will this company announce a round by Q2?", "Will this negotiation produce a counter?". Big recommendations get scored on pre-registered intermediate milestones.

### 3. Where wealth actually comes from for people who start with little

- **Human capital is the dominant asset at the start of a career (Judgment, well supported).** The Atlanta Fed Wage Growth Tracker (primary) showed job changers at 4.4% median wage growth versus 3.6% for stayers in July 2026. In August, per the Atlanta Fed's own post, stayers "held at 3.6%" while changers "increased to 5.0% from 4.4%." For September, the Atlanta Fed reported the overall tracker "edged down to 3.9 percent" and that both the stayer and changer measures "edged down as well." The exact September split, 4.7% versus 3.4%, comes from secondary reports. The gap is cyclical and noisy: switchers fell to 3.7% versus stayers at 3.3% in May 2026. Economist Justin Bloesch, replying to WSJ reporter Nick Timiraos on June 11, 2026, said "the more likely story is just that the sample of switchers is smaller and noisier." Lesson: switching pays on average, but the premium varies with the labor market and should be timed against data, not habit.
- **Business ownership is how the top gets rich, but the median attempt is modest.**
  - In the Fed's 2022 Survey of Consumer Finances (SCF), 20% of families owned a privately held business, "the highest level on record." 78% of those businesses employed fewer than five people, and 52% were nonemployer firms.
  - Business wealth is more than 40% of the wealth of the top 1% (Kuhn and Ríos-Rull's SCF 2022 update). Zidar and Zwick's analysis of SCF 2022 data (as summarized by Edward Conard's Macro Roundup) puts private business at "roughly 45 to 50% of top wealth" for the top 0.1%, with "about 80% of households worth $30 million or more" owning businesses. A narrower tax-data measure in Smith, Zidar & Zwick (NBER w29374) puts pass-through business alone at 26% of top 0.1% wealth in 2016.
  - Outcomes are extremely dispersed: the self-employed wealth Gini is 0.84.
  - BLS Business Employment Dynamics data show about half of new employer establishments survive five years (51.4% for the 2020 cohort) and 34.7% survive ten.
- **Homeownership and broad equity ownership are the mass-market wealth builders.** In SCF 2022, 66.1% of families owned their home. In the top net-worth decile, 95.4% owned a home and 47.9% held business equity, versus 8.2% and 4.4% in the bottom quarter.
- **Public-market stock picking does not reliably add value, even for professionals.**
  - S&P's SPIVA U.S. Year-End 2025 scorecard: 79% of active large-cap funds underperformed the S&P 500 in 2025.
  - Over longer windows: 89.93% underperformed over 15 years and 92.89% over 20 years.

### 4. What fails, with data

| Activity | Best evidence | What it shows |
|---|---|---|
| Day trading | Chague, De-Losso & Giovannetti (2020), Brazilian regulator data | Of 19,646 people who started day trading mini-index futures in 2013–2015, 1,551 persisted more than 300 days. 97% of those lost money, and only about 0.5% (8 people) earned more than a bank teller's starting pay (about US$54/day). The best earned about US$310/day with a standard deviation of US$2,560. The authors found "no evidence of learning." |
| Retail options | Bryzgalova, Pavlova & Sikorskaya, *Journal of Finance* (2023) | Retail investors lost $2.10 billion assuming a 10-day holding period. Losses were concentrated in short-dated (weekly) options with quoted bid-ask spreads as high as 12.6%. **Contested:** Bogousslavsky & Muravyev estimate per-trade results of −5% to +1%, and a Cboe-hosted paper disputes the trade-direction method. Even the friendlier estimates show no edge for buyers of short-dated options. |
| Crypto speculation | BIS Bulletin 69 and BIS Working Paper 1049 (Aug 2015–Dec 2022 app data, 95 countries) | An estimated 73–81% of retail crypto-app users likely lost money on their bitcoin investment. Retail entry chased price rises: most app downloads came when bitcoin was above $20,000. |
| MLMs | FTC staff report (press release September 4, 2024; statements reviewed February 2023), 70 income disclosure statements | "Many participants in those MLMs received no payments from the MLMs, and the vast majority received $1,000 or less per year—that is, less than $84 per month, on average." In at least 17 MLMs most participants made nothing. None of the 70 statements accounted for all expenses. |
| Active stock picking | SPIVA U.S. Year-End 2025 | About 90% of professional large-cap funds trail the index over 15 years. |
| Trading "courses" | Chague et al. | Their conclusion: it is "virtually impossible for individuals to day trade for a living, contrary to what course providers claim." Courses sold by the people who profit from the course are seller-sourced evidence by definition. |

**Judgment:** The Scout should hard-block all six by default, and only let you override with an explicit, logged request. That matches your own rule 8.

### 5. Startup employee equity: real outcome distributions

- **Base rate.**
  - Hall & Woodward studied 20,961 U.S. venture-backed companies from 1987 onward. "About three-quarters of venture-backed companies expire without returning any cash to their entrepreneurs." Precisely, 73.0% delivered zero exit value.
  - Only about 2.4% delivered more than $100 million to entrepreneurs, and just 0.04% delivered more than $1 billion.
  - Founders hold common stock, as employees do, so this is the closest primary-source proxy for what common stock gets. The data end around 2008.
- **Current conditions.**
  - Carta counted 254 startup shutdowns on its platform in Q1 2024, up 58% year over year. TechCrunch reported Carta's 2024 total as 966 shutdowns versus 769 in 2023. Carta says these figures likely undercount.
  - Only 9% of startups that raised a seed round in Q2 2024 reached Series A within a year, and 32.9% of the Q1 2021 seed cohort reached it within two years (Carta, September 2025).
- **Most employees never capture value even when it exists.**
  - Carta found employees exercised just 32.2% of vested, in-the-money grants in Q4 2024, down from 23% of vested options exercised before expiration in Q4 2023.
  - At 386 private companies each valued above $1 billion, departing employees abandoned more than $1.8 billion of in-the-money options. That averages more than $47,000 per person.
  - In 2022, 85% of grants had a 90-day post-termination exercise window (Carta, as cited secondhand).
- **Terms that can zero out common stock.**
  - Liquidation preferences above 1x appeared in 8% of new rounds in Q1 2024, which Carta called tied for the highest rate this decade.
  - Participating preferred appeared in more than 10% of new primary rounds in Q1 2023, and that rate had fallen by more than half by Q4 2024.
  - I found no primary statistic on the share of exits that pay common holders nothing. Hall & Woodward's 73% is the best available proxy, and the true current figure is unknown.
- **Judgment on valuation:** value a startup offer on cash compensation, skills and network first. Count the equity at its probability-weighted after-tax value, which is usually small. Never buy or exercise beyond the speculative-sleeve cap. The questions to ask are in the sample memo below.

### 6. Category ranking: one list, risk-adjusted

Ranked by certainty-equivalent value for a generic early-career person with little capital (**Judgment**, anchored on the base rates above):

| Rank | Category | Verdict | Why |
|---|---|---|---|
| 1 | Career moves, negotiation, employer choice | **Strongest** | It acts on the largest asset (future earnings), has almost no downside in dollars, and the switcher premium is measurable. |
| 2 | Savings on big costs: employer match, tax-advantaged accounts, benefits, housing | **Strong, near-certain** | Money kept is a guaranteed return. An employer match is often an immediate 50–100% return on contributions (verify each plan). |
| 3 | People, programs, fellowships, grants, competitions | **Strong asymmetry** | Downside is an application's time; upside is access and credentials. |
| 4 | Skills and credentials | **Selective** | High value when tied to a measurable pay premium in your field; mostly noise when sold by the credential vendor. |
| 5 | Employer equity | **Free lottery ticket** | Worth having when it comes with a good job; worth almost nothing as a reason to take a bad one (73% zero base rate). |
| 6 | Small businesses and side income | **Capped bets** | About 50% five-year survival for employer establishments; upside is real but slow. Size by the sleeve rules. |
| 7 | Timing plays (emerging industries, regions, regulation) | **Express through career, not trading** | Getting hired into a rising industry captures the trend with a salary attached. |
| 8 | Real estate | **Later** | Housing is the mass-market wealth builder, but buying is a planned around-30 decision. Before then the Scout's job is saving and rent-versus-buy math. |
| 9 | Public-market stock picks | **Mostly noise** | SPIVA: about 90% of professionals lose to the index over 15 years. Keep these paper-only. |
| 10 | Day trading, options, crypto speculation, courses, MLMs | **Noise or negative** | See the failure table above. Blocked by default. |

### 7. Tools: verified capabilities and prices (as of November 2026)

| Tool | Verified facts | Verdict |
|---|---|---|
| **Claude API models** (official pricing page, fetched Nov 2026) | Per million tokens, input/output: Fable 5.2 $8/$40; Opus 5.5 $4/$20; Sonnet 5.5 $2/$10; Haiku 5.5 $0.10/$0.50 for prompts up to 100K tokens ($0.50/$2.50 above). Cache hits are $0.20 (Fable/Opus), $0.10 (Sonnet), $0.01 (Haiku). Claude 4.7 and later models use a tokenizer that produces "approximately 30% more tokens for the same text." Batch API is 50% off (secondary sources). | Legit. Haiku 5.5 makes a wide radar nearly free. |
| **Claude Managed Agents** | Public beta. Billed as standard token rates plus $0.08 per active session-hour; idle time is not billed. Web search is reported at $10 per 1,000 searches (secondary). | Legit but beta. Good for v3; unnecessary for v1. |
| **Claude Code cloud scheduled tasks** (formerly "routines") | Official docs: a saved Claude Code configuration (prompt, repositories, connectors) that "run[s] autonomously as full Claude Code cloud sessions" on a schedule, an API call, or a GitHub event. Still a **research preview**. Secondary sources report a one-hour minimum interval and caps of 5 runs/day on Pro, 15 on Max, and 25 on Team/Enterprise, drawn from subscription usage. | Legit and the fastest path to v1. Preview status means build a fallback. |
| **Claude Agent SDK / Claude Code subagents** | Official docs: subagents can be defined as markdown files in `.claude/agents/` or programmatically. Each can restrict its tools and have a persistent `memory` scope (user/project/local); the first 200 lines of its MEMORY.md load at startup. The only content passed from parent to subagent is the Agent tool's prompt string, which suits independence-first analysis. Default limits: 20 concurrent subagents, nesting depth 3. | Legit. This is how to build the council. |
| **Memory tool** (`memory_20250818`) | A client-side tool with view/create/str_replace/insert/delete/rename commands over a `/memories` directory. | Legit, but the ledger itself should be a git repository you control, not model memory. |
| **SEC EDGAR** (including Form D private raises) | Free U.S. regulatory filings. | Legit. Core source for funding signals and filings. |
| **Crunchbase** | The free API tier was discontinued. Pro is listed at $49/month billed yearly ($99 month-to-month), Business from $199/month. Full API is sales-only (Vendr-reported median contract about $20,000/yr). | Web plan is useful at the strong tier; the API is not worth it for one person. |
| **PitchBook / Harmonic** | No public prices. Third-party estimates: PitchBook about $12,000–$40,000 per user/yr; Harmonic about $10,000–$30,000/yr. | Hype for an individual. This is where spending stops paying. |
| **Kalshi** | Public market-data endpoints need no key and carry no API fee. **However**, Kalshi's Developer Agreement (as quoted by a secondary source) bars "collecting, caching, aggregating, or storing" API data except to facilitate your own trading on Kalshi. | Use it for read-only, on-the-spot price comparisons. Check the terms before storing any data. |
| **Polymarket** | Public Gamma, CLOB and Data APIs for market data. Some regions are geoblocked; Polymarket US is a separate CFTC-regulated exchange. | Legit for reading market odds. |
| **Free public data** (BLS, Atlanta Fed, FRED, Census, Grants.gov, USAJobs) | Free public-agency data. I did not re-verify each endpoint's current terms in this pass. | Legit. Verify endpoints at build time. |
| **Paid market-data APIs, job-posting APIs, business-for-sale listings** | Not verified in this pass. | Verify at build. Do not pay for these until the scoreboard shows the relevant category earns its keep. |

## Details: Recommended Design

### Design principles (Judgment)

1. **Rules in code, judgment in models.** Loss limits, sizing caps and the change budget are enforced by a deterministic script (the "Risk Gate") that no agent can argue past.
2. **Independence through different evidence.** Each specialist gets its own data feeds and its own reference-class library, so correlation between agents is reduced by design rather than by instruction.
3. **Copy the systems that actually perform.** Decompose each question into sub-questions, retrieve fresh evidence filtered for recency, sample several forecasts, and aggregate statistically. Debate is used only for one targeted challenge round.
4. **Steady by default.** "No action this week" is the expected output most weeks.

### Agents and exact roles

| Agent | Model (strong tier) | Role | Primary data |
|---|---|---|---|
| **Radar** | Haiku 5.5 sweep, Sonnet 5.5 dedupe | Weekly wide scan of every category. Outputs 30–80 raw candidates tagged by category, deadline and source quality, with a novelty check against the ledger so it doesn't keep returning the same few ideas. | RSS/news, EDGAR Form D, job boards, grants, prediction markets, Fed/BLS releases |
| **Career Strategist** | Sonnet 5.5 | Roles, employers, negotiation, timing of switches. | Wage tracker, BLS occupational data, postings, company funding signals |
| **Venture & Equity** | Sonnet 5.5 | Employer equity, startup offers, "join before obvious." | EDGAR Form D, Carta public data, funding news |
| **Business Builder** | Sonnet 5.5 | Side income, businesses to start or buy. | BLS survival tables, SBA data, listing sites |
| **Trends & Timing** | Sonnet 5.5 | Emerging industries, technologies, regions, regulations. | Federal Register, funding flows, research feeds |
| **Access** | Sonnet 5.5 | Mentors, communities, fellowships, grants, competitions. | Grants.gov, program pages, deadlines |
| **Real Estate & Alternatives** | Sonnet 5.5 | Rent-versus-buy, housing timing, alternatives screening. | Census, public housing-market data |
| **Public Markets** | Sonnet 5.5 | Core index maintenance, rebalancing, panic-prevention, paper picks only. | EDGAR, index data |
| **Macro & Risk** | Sonnet 5.5 | Recession and labor-market odds, prediction-market comparisons. | FRED, Kalshi/Polymarket reads |
| **Personal Finance & Tax** | Sonnet 5.5 | Match capture, account types, benefits, big-cost savings. | IRS publications, plan documents you supply |
| **Skeptic** | Opus 5.5 | Assigned to build the strongest case *against* every serious idea and to flag seller-sourced evidence. | Same feeds, plus failure base rates |
| **Fact-Checker** | Sonnet 5.5 | Traces every number to a dated primary source; marks anything untraceable "unverified." | Original documents |
| **Red Team** | Opus 5.5 | Has kill power. Kills ideas that break a loss rule, rest only on seller evidence, fail a base-rate sanity check, or depend on an unverified key number. Logs the reason. | Skeptic and Fact-Checker outputs |
| **Chair** | Opus 5.5 | Aggregates the independent forecasts, runs the one challenge round, writes the edition, shows where the specialists split. | All sealed views |
| **Risk Gate** | Python script, not an LLM | Enforces loss rules, sizing caps and the change budget. | Your net-worth and expense inputs |
| **Scorekeeper** | Sonnet 5.5 | Resolves forecasts, computes Brier scores and calibration, runs the quarterly review, and proposes rule rewrites for your approval. | The ledger |

### Forecasting protocol (every serious idea)

1. **Reference class first.** Name the class, give its base rate, and cite the source, for example "VC-backed company, common holders: 73% zero (Hall & Woodward)."
2. **Decompose** the question into sub-questions, as the top ForecastBench systems do.
3. **Scenario tree** with bull, base, bear and ruin branches. Probabilities must sum to 100%, and each branch carries dollar and hour outcomes.
4. **Pre-mortem:** "It's two years later and this failed. Why?"
5. **Market check:** compare against a prediction market or market price wherever one exists, and explain any disagreement.
6. **Sealed views:** each relevant specialist commits a probability before seeing anyone else's.
7. **Aggregate** with the median of log-odds across specialists and samples. Apply extremizing only after the scoreboard shows systematic under-confidence (Judgment; extremizing comes from the Good Judgment Project literature, which I did not re-verify in this pass).
8. **One challenge round:** the Chair sends targeted questions only to the outliers. Each outlier may revise once, with its reason logged. No open-ended debate.
9. **"I don't know" is mandatory** when evidence is thin. It is defined as fewer than two independent non-seller sources, or no usable reference class.

### Sizing: Kelly, done safely

- The Kelly fraction for a simple bet is f* = (bp − q)/b, where p is the win probability, q = 1 − p, and b is the net payoff odds.
- Kelly assumes you know p. For personal opportunities you never do, and over-betting is far worse than under-betting (Judgment, standard result).
- **Rule:** position size = min(¼ × Kelly, the single-bet cap below). Where p cannot be estimated from a reference class, size = the minimum viable amount or zero.

### Loss rules (enforced by the Risk Gate, as formulas)

| Rule | Formula / threshold |
|---|---|
| R1. Foundation first | No speculative bet until the emergency fund is at least 3 months of essential expenses (target 6) **and** no debt above the higher of 8% APR or the expected long-run equity return. |
| R2. Core | At least 90% of investable assets in a low-cost diversified core (for example a total-market or target-date index fund) until net worth exceeds 12 months of expenses. After that, at least 85%. |
| R3. Speculative sleeve cap | Total at-risk money in speculative bets ≤ min(10% of net worth, net worth − emergency fund − earmarked goal savings). If net worth is ≤ 0, the cap is 0. |
| R4. Single-bet cap | ≤ 2% of net worth per bet (≤ 1% while net worth is under 6 months of expenses), and also ≤ ¼ Kelly. |
| R5. Limited liability only | Nothing that can lose more than is put in. This blocks margin, shorting, writing options, personal guarantees above the sleeve cap, and unlimited-liability partnerships. |
| R6. Prohibited by default | Leverage, options, day trading, crypto speculation, MLMs, paid "opportunity" courses. Overriding requires your explicit, logged request **and** must still fit R3–R5. |
| R7. Employer concentration | Buying or exercising employer equity counts against the sleeve. Plans value unvested or illiquid equity at $0. |
| R8. Circuit breaker | If the sleeve loses 50% from its peak, no new speculative bets for one quarter. |
| R9. Hours ceiling per bet | Every bet declares a maximum hours budget in advance. Reaching it triggers the written exit review. The amount is yours to set. |

### Change budget

- At most **one big move per quarter**. Big moves are a job change, a housing change, or changing the core allocation.
- A big move needs the supporting evidence to hold across **three consecutive weekly editions**. Time-limited offers are handled in on-demand mode instead.
- At most **three small actions per week**.

### Every recommendation ships with an exit plan

- Thesis
- Disconfirming evidence that would prove it wrong
- Cut point
- Maximum loss in dollars and in hours
- Review date
- The "do-nothing" baseline it is scored against

### Ledger, scoreboard and self-grading

- **Ledger:** a git repository holding one JSON record per recommendation or forecast. Each record has a timestamp and commit hash (so nothing can be backdated), probability, scenario tree, your action, and the eventual outcome. Killed ideas get their own log with the reason.
- **Scoreboard by category:** Brier score and calibration plot (forecasts in each probability bucket against observed frequency), hit rate, and value added versus a do-nothing baseline.
  - The baseline for money is the index core.
  - The baseline for career is your current path projected at the median stayer wage growth.
  - Misses are always included.
- **Quarterly review:** effort shifts toward categories with better calibration and positive value added. Proposed rule rewrites are shown to you as diffs and only take effect when you approve them.

### Public-market rule

- Paper-only for the first 3 months, tracked against a total-market index fund, as you asked.
- **Judgment:** three months is far too short to show skill. I recommend keeping picks paper-only until at least 50 resolved, pre-registered calls beat the index after costs at conventional significance. Given SPIVA, expect that to never happen. The specialist's real value is preventing mistakes such as panic selling, chasing performance, and fee drag.

### Run modes

1. **Weekly edition** (cloud scheduled task, Sunday): Radar → sealed specialist views → Skeptic → Fact-Check → Red Team → Chair → Risk Gate → edition committed to the repository.
2. **On-demand** (slash command or API trigger): the same pipeline restricted to one decision, with a target turnaround under an hour.
3. **Alerts** (lightweight Haiku check, daily): fires only when a pre-registered entry or exit condition, or a deadline for a time-limited opportunity, is hit.
4. **Hard limit in all modes:** read-only tools. No brokerage, payment or outbound-messaging connectors are installed, so it cannot place trades, move money, or send messages on your behalf.

### Failure modes to design against

- **Correlated "independent" agents:** mitigated by separate data feeds and sampling.
- **Seller-sourced evidence:** auto-flagged, and it cannot be the sole support for any idea.
- **Stale or invented numbers:** the Fact-Checker requires a dated source for every figure.
- **Look-ahead contamination:** no backtests are accepted as evidence.
- **Novelty bias:** the Radar's freshness reward is capped so new ideas don't crowd out the boring right answer.
- **Action fatigue:** handled by the change budget.
- **Preview features changing or breaking:** keep the pipeline runnable locally via the Agent SDK.
- **Scoreboard too small for conclusions:** report confidence intervals and say "insufficient data" until enough forecasts have resolved.

## Cost: three tiers

Estimates use official November 2026 list prices. Token volumes are my assumptions and should be checked against the first month's actual bill.

| Tier | What runs | Est. monthly cost | What it adds |
|---|---|---|---|
| **Lean** | Haiku radar, Sonnet specialists, one Opus pass for Chair and Red Team, one sample per specialist, free data only, 2 on-demand memos | About $15–40 in API tokens, or runs inside an existing Claude subscription within scheduled-task caps | The full pipeline and ledger, minimal ensembling |
| **Strong (recommended)** | Opus for Skeptic, Red Team and Chair; 3 samples per specialist on serious ideas; Crunchbase Pro web plan ($49–99); about 4 on-demand memos; daily alerts | About $100–250 | Ensembling (where most of the measured accuracy gains come from), better startup signals, faster on-demand turnaround |
| **Max** | Fable 5.2 Chair and Red Team, 5+ samples, Managed Agents runtime, Harmonic or PitchBook-class data | About $1,000–3,500+ (dominated by $10,000–40,000/yr data contracts) | Marginal at best for one person |

**Where more spending stops helping (Judgment):** after the strong tier.
- The "Debate or Vote" results suggest gains come mostly from aggregating several samples, and returns from adding more fall off quickly.
- Paid VC databases are built for funds sourcing hundreds of deals, not for one person evaluating a few offers a year.
- The binding limits become the number of resolved outcomes and your own follow-through.

## Phased Build Plan

**v1, runnable within a week**
- A Claude Code project with a CLAUDE.md "constitution" containing the loss rules, change budget and source-quality ranking.
- Fourteen subagent files in `.claude/agents/`, each with restricted read-only tools and its own memory scope.
- A Python Risk Gate script.
- Ledger as JSON files in git.
- One weekly cloud scheduled task.
- An `/ondemand` command.
- Free data sources only (EDGAR, BLS, Atlanta Fed, FRED, Grants.gov, USAJobs, Polymarket and Kalshi reads).
- Templates for the edition and the decision memo.

**v2, weeks 2–4**
- A base-rate library with dated sources.
- Brier scoring and calibration tracking.
- A daily alert task.
- Prediction-market comparisons.
- A kill log.
- A 3-sample ensemble for serious ideas.

**v3, months 2–3**
- Move the orchestration to the Agent SDK (or Managed Agents) for reliability.
- SQLite ledger with a calibration dashboard.
- First quarterly self-review and rule-rewrite proposals.

**v4, month 4 onward**
- Add paid data only in categories where the scoreboard shows positive value added.
- Revisit model tiers each quarter against cost per resolved forecast.

## Sample Weekly Edition (hypothetical early-career user)

**THE SCOUT — Week of Nov 16, 2026 — Edition #1**
**Headline: No big moves this week. Two small actions, and one decision is still pending.**

**Actions (2 of 3 allowed)**
1. *Benefits check (Personal Finance):* Before the pending offer is accepted, get the 401(k) match formula and vesting schedule in writing. Confidence the match is worth more than any investment idea on this list: 90%. Max cost: 30 minutes.
2. *Access (Programs):* Two industry fellowship or scholarship applications have deadlines in the next 45 days. Estimated chance of acceptance per application: 5–15% (Judgment; acceptance data unavailable, so "I don't know" applies to the exact rate). Max loss: about 6 hours each. Kill condition: the program requires payment to apply.

**Watchlist (no action)**
- *Career:* switcher wage premium of 4.7% vs 3.4% for stayers (Atlanta Fed, September 2026, as reported). The premium is cyclical; it doesn't yet justify a switch beyond the pending decision.
- *Venture signal:* two Form D filings from Pacific Northwest aerospace companies. Logged as forecasts that each will post 3+ ops roles within 90 days: P = 35%.

**Killed this week (Red Team)**
- "Trading course with 'verified' returns." Killed: seller-sourced evidence, and the reference class says 97% of persistent day traders lose money.
- "Buy shares in a friend's startup round." Killed: breaks R1 (emergency fund below 3 months).

**Where the council split:** Career (P = 0.70) and Skeptic (P = 0.45) disagreed on whether the pending offer beats staying put for 12 more months. That decision goes to an on-demand memo.

**Scoreboard:** 0 forecasts resolved. Insufficient data.

## Sample On-Demand Decision Memo (hypothetical)

**Decision:** Accept an ops/recruiting role at a hypothetical Series A space-propulsion startup?
**Hypothetical offer:** base salary 25% above the current job; 4,000 options out of 20 million fully diluted shares (0.02%); $0.50 strike; 4-year vest with a 1-year cliff; 90-day post-termination exercise window.

**Recommendation: ACCEPT, if two terms check out.** Value it as a career move. The equity is a free lottery ticket.

**1. Reference class:** VC-backed company, common stock. 73% returned zero to entrepreneurs (Hall & Woodward). Only 9% of recent seed companies reached Series A within a year, so already being at Series A is a positive filter.

**2. Scenario tree for the equity** (assumes about 40% further dilution, leaving 0.012%; after strike, pre-tax):

| Scenario | P | Equity value |
|---|---|---|
| Ruin: shutdown, or exit below the preference stack | 70% | $0 |
| Bear: small exit ($50–150M) | 18% | about $6,000 |
| Base: mid exit ($300–700M) | 9% | about $50,000 |
| Bull: $1B+ exit | 3% | about $150,000+ |
| **Expected value** | | **about $10,000 over 5–8 years; certainty equivalent much lower** |

**3. Career value (main driver):** The salary gain is near-certain. Ops and recruiting experience in a growing industry is transferable even if the company fails. That combination has bounded downside and real upside. Council: Career 0.72, Venture 0.65, Skeptic 0.48, Chair aggregate 0.64 that accepting beats staying 12 more months on the do-nothing baseline.

**4. Pre-mortem:** The startup runs out of runway within 18 months. Mitigation: ask how many months of runway it has and when the last round closed. If it has under 12 months of runway, re-run the memo.

**5. Strongest case against (Skeptic):** Early-stage roles can be cut first in a downturn, and the 90-day exercise window means equity is likely forfeited if you leave.

**6. Questions to ask before signing:**
- Total fully diluted shares and the most recent 409A value.
- Total liquidation preference stack, and whether any preferred stock is participating or above 1x.
- Months of runway.
- Whether early exercise is allowed (with an 83(b) election).
- Whether the option exercise window can be extended.
- Refresh-grant policy.
- ISO or NSO.
- Any history of tender offers or secondary sales.

**7. Exit plan:**
- Wrong if: runway is under 12 months, or the role turns into non-ops work within 6 months.
- Cut point: reassess at the 12-month cliff.
- Max loss: the opportunity cost of the current job's hours, and $0 in cash (do not exercise beyond the R3/R4 caps).

**8. Market check:** No prediction market exists for this. Stated plainly: no external price is available.

## Recommendations

1. **Approve the "career-and-decision engine" framing.** It weights the council toward the top four categories and keeps public markets as core maintenance plus paper picks.
2. **Approve the formula-based loss rules R1–R9**, enforced by a deterministic Risk Gate rather than by agent judgment.
3. **Build v1 on Claude Code** with subagents and one weekly cloud scheduled task, using free data only, at the lean tier for month one. Move to the strong tier once the pipeline is stable.
4. **Replace "maximize EV" with certainty-equivalent ranking**, with raw EV and ruin probability shown alongside.
5. **Score calibration on many small forecasts** rather than waiting years for big outcomes.

## Open Decisions for Your Approval

1. Sleeve cap: 10% of net worth (recommended), or lower?
2. Single-bet cap: 2% of net worth (1% while net worth is under 6 months of expenses)?
3. Change budget: one big move per quarter and three small actions per week?
4. Keep public-market picks paper-only past 3 months until a statistical threshold is met (recommended), or allow small real positions after 3 months?
5. Delivery: commit editions to the repository only, or also email them to yourself? (The Scout never messages anyone else.)
6. Tier: start lean and upgrade to strong after month one?
7. Is the Kalshi data-terms risk acceptable (read-only, no storage), or should the Scout use Polymarket and other sources only?

## Caveats

- **Model names and prices** are from Anthropic's official pricing page as fetched in November 2026. Scheduled tasks are a research preview and Managed Agents is in beta, so both may change. Run caps and the web-search price come from secondary sources.
- **Hall & Woodward** covers founders in cohorts from 1987 to about 2008. It is a proxy for employee common stock, not a direct measure.
- **Wage-tracker figures for September 2026** come from a secondary report. The July 2026 figures come from the Atlanta Fed directly.
- **The retail-options loss estimates** are disputed in the literature.
- **ForecastBench parity** rests on 2024 superforecaster data and a benchmark FRI says is not saturated. Parity on benchmark questions does not mean parity on your personal decisions.
- **All probabilities in the sample memo are illustrative.**
- This is research and design only. I am not a financial advisor. Consult a licensed professional on tax and investment specifics.