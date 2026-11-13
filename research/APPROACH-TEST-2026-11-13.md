# Approach test, 2026-11-13

What was tested: the Scout's rules, by mechanical replay in `scripts/simulate.py` (4,000 simulated lifetimes per row). What was not tested: the Scout's forecasting skill. A replay of its own picks on past data would measure memory, not skill, so it is not done (hard rule 4). Skill can only be shown by graded forward forecasts.

Inputs: an example saver adding $1,500 a month, rising 5% a year. Market 7% a year with 16% swings. Each play is one small company: market return plus an edge, large company-specific swings, 3% chance a year of a total loss.

## Single-play success rate
| Edge per year | Plays that beat the market over 3 years |
|---|---|
| -3% (bad picks) | 32% |
| 0% (no skill) | 36% |
| +5% | 43% |
| +10% | 50% |
| +20% | 61% |

## Ten years
| Approach | Typical result | Bad luck (1 in 10) | Good luck (1 in 10) | Reaches $500K |
|---|---|---|---|---|
| Core only | $305K | $209K | $458K | 6% |
| 30 small plays, no skill | $306K | $206K | $471K | 7% |
| 6 deep plays, no skill | $307K | $200K | $475K | 8% |
| 6 deep plays, bad picks | $292K | $192K | $450K | 6% |
| 6 deep plays, +10% edge | $362K | $233K | $570K | 18% |
| 6 deep plays, +20% edge | $427K | $270K | $684K | 34% |
| Core + contributions stepped up ($3,000 in year 4, $5,000 in year 7) | $553K | $391K | $793K | 65% |
| Step-ups + 6 deep plays, +10% edge | $638K | $428K | $952K | 78% |

## Fifteen and twenty years (chance of reaching $1M)
| Approach | 15 years | 20 years |
|---|---|---|
| Core only | 10% | 55% |
| 6 deep plays, +10% edge | 27% | 77% |
| Step-ups only | 72% | 98% |
| Step-ups + 6 deep plays, +10% edge | 86% | 99% |

## What the test shows
1. Concentration does nothing by itself. Without an edge, six plays and thirty plays both land where the core does, with a slightly worse bad-luck case.
2. A real edge of 10 points a year adds about 19% to the typical ten-year result and about 35% at twenty years. Useful, not life-changing alone.
3. Raising the amount invested adds about 80% at ten years. It is the largest lever by far.
4. Being wrong costs little at these caps (about 4% at ten years). The caps do their job.

## Flaws found and fixed
| Flaw | Fix |
|---|---|
| No target for "good enough" | Target set: half of plays beat the market (no-skill line is 36%) |
| At six plays a year it would take about seven years to know if the Scout has skill | Short-cycle paper plays every week to build a graded record fast |
| Sizing rejected every short play: a 2% edge in four weeks failed a bar meant for multi-year holds | Bar now scales with time for holds under a year |
| Sizing could recommend more dollars than a play can hold | New capacity limit |
| Nothing said when to stop | Money plays switch off if the record is below the no-skill line after 40 plays |
| Live scan leaned on newsletters for insider data | Needs the SEC domain on the allowed list so filings are read directly (owner setting) |

## Verdict
The approach is confirmed with one correction to expectations: the money-play engine is the second lever, not the first. Order of importance while the portfolio is small: raise the amount invested, then a few deep plays with a proven edge, then the core.
