# Data sources (free only)

Access details come from the November 2026 build research. Items marked "check" were not confirmed on an official page; verify on first use and update this file.

## Domains to allow in the cloud environment
Paste these, one per line, into the cloud environment's "Allowed domains" (network access: Limited), keeping package managers allowed:

```
www.sec.gov
data.sec.gov
efts.sec.gov
api.bls.gov
www.bls.gov
api.stlouisfed.org
fred.stlouisfed.org
api.census.gov
api.grants.gov
www.grants.gov
data.usajobs.gov
www.atlantafed.org
gamma-api.polymarket.com
clob.polymarket.com
www.treasurydirect.gov
home.treasury.gov
www.irs.gov
www.federalregister.gov
www.fdic.gov
```

Web search and web fetch are separate tools and cover ordinary public pages.

## Sources by agent
| Source | Used by | Access | Notes |
|---|---|---|---|
| SEC EDGAR filings, company financials, Form D private raises | radar, ventures, assets | No key. At most 10 requests per second. Must send a User-Agent header with a name and contact email | Form D shows private companies raising money, often before any news |
| SEC filings for public companies: 10-K, 10-Q, 8-K, Form 4 insider trades, S-1 listings, 13F holdings | markets, themes, ventures | Same EDGAR access | Company fundamentals come from filings first, data sites second |
| TreasuryDirect and Treasury daily rates | money-strategy | Public pages and data files | Auction results and yields; always record the date |
| IRS announcements and publications | money-strategy | Public pages | Limits and rules for the current and next tax year |
| EDGAR full-text search | radar | `efts.sec.gov/LATEST/search-index?q=...&forms=D` | check: works but is not an officially documented API |
| BLS (jobs, wages, occupations) | career, trends-access | Free key from bls.gov; 500 queries a day | Key is optional for light use of the public pages |
| FRED (economic series) | assets, trends-access | Free key required | check: rate limit about 120 requests a minute |
| Census Data API | trends-access, assets | No key up to 500 queries a day | |
| Grants.gov | trends-access | No key for search and fetch | |
| USAJobs | career | Free key required, plus User-Agent set to an email | |
| Atlanta Fed Wage Growth Tracker | career | Public page and downloads | check |
| Polymarket | chair (market check) | Public read endpoints, no key | check: read only, never trade |
| Federal Register, agency sites | trends-access | Public pages via web fetch | For regulation changes |
| Company career pages, funding news, program and fellowship pages | all | Web search and fetch | Respect each site's terms; do not scrape behind logins |

## Keys
The owner adds any free keys as secrets in the cloud environment, never in a file in this repo. If a key is missing, the agent uses web search for that source and notes it.

## Not used
- Kalshi: its data terms were not reviewed. Do not use until they are.
- Paid databases (Crunchbase API, PitchBook, Harmonic): out of scope by the no-cost rule.
- Anything requiring a login to the owner's personal accounts.

## Source quality ranking
1. Primary: filings, government data, court and regulatory records, the organization's own official pages.
2. Reputable secondary: established news and research outlets with named authors and dates.
3. Weak: blogs, forums, social posts. May prompt a search, may not support a play alone.
4. Seller: anyone who profits if the reader acts. Always flagged, never sole support.
