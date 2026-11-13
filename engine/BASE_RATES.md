# Base-rate library

Start every forecast from one of these, or add a new one with a dated source. Status "from research report" means the figure came from the November 2026 research reports in `research/` and has not been re-checked against the original source. Re-verify a figure the first time it is used in a published play, then change its status to "verified YYYY-MM-DD".

## Startups and equity
| Reference class | Base rate | Source | Status |
|---|---|---|---|
| US venture-backed company returns nothing to its founders (common stock) | 73% | Hall & Woodward, AER 2010; 20,961 companies, cohorts 1987 to about 2008 | from research report |
| Venture-backed company delivers over $100M to founders | about 2.4% | Hall & Woodward 2010 | from research report |
| Venture-backed company delivers over $1B to founders | about 0.04% | Hall & Woodward 2010 | from research report |
| Seed-funded startup reaches Series A within 1 year | 9% (Q2 2024 seed cohort) | Carta, Sept 2025 | from research report |
| Seed-funded startup reaches Series A within 2 years | 32.9% (Q1 2021 seed cohort) | Carta, Sept 2025 | from research report |
| New funding rounds with liquidation preference above 1x | 8% (Q1 2024) | Carta | from research report |

Note: founder outcomes are the closest primary-source proxy for employee common stock. No direct figure was found for how often exits pay common holders nothing.

## Businesses
| Reference class | Base rate | Source | Status |
|---|---|---|---|
| New employer business survives 5 years | 51.4% (2020 cohort) | BLS Business Employment Dynamics | from research report |
| New employer business survives 10 years | 34.7% | BLS Business Employment Dynamics | from research report |
| US families owning a private business | 20% | Fed Survey of Consumer Finances 2022 | from research report |
| Share of top-1% wealth held as business wealth | over 40% | Kuhn and Rios-Rull, SCF 2022 update | from research report |

## Careers
| Reference class | Base rate | Source | Status |
|---|---|---|---|
| Median wage growth, job switchers vs stayers | 4.4% vs 3.6% (July 2026); gap is cyclical and noisy | Atlanta Fed Wage Growth Tracker | from research report |

## Markets and trading
| Reference class | Base rate | Source | Status |
|---|---|---|---|
| Active US large-cap funds trailing the S&P 500 over 15 years | 89.9% | SPIVA US Year-End 2025 | from research report |
| Same, over 20 years | 92.9% | SPIVA US Year-End 2025 | from research report |
| Persistent day traders (300+ days) who lose money | 97% | Chague, De-Losso & Giovannetti 2020 (Brazil) | from research report |
| Retail crypto-app users who likely lost money on bitcoin | 73 to 81% | BIS Bulletin 69 / Working Paper 1049 | from research report |
| MLM participants earning $1,000 a year or less | "vast majority" | FTC staff report, Sept 2024 | from research report |

## AI forecasting (for judging the Scout itself)
| Reference class | Base rate | Source | Status |
|---|---|---|---|
| Brier score for always saying 50% | 0.25 | arithmetic | verified |
| Best AI systems vs superforecasters on ForecastBench | statistically indistinguishable as of July 2026, with caveats | Forecasting Research Institute | from research report |
| LLM backtest accuracy with leaky search vs leak-free | Brier 0.108 vs 0.24 | El Lahib et al., ACL 2026 | from research report |

## Adding a base rate
Add a row with the reference class, the number, the source and its date, and status. A base rate with no dated source may not be used.
