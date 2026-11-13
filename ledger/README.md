# Ledger

The long-term log. One JSON record per line. Records are only ever added, never edited. Git history is the timestamp that proves a forecast was logged before its outcome.

## forecasts.jsonl
```json
{"id":"F-2026-11-16-03","play_id":"P-2026-11-16-01","created":"2026-11-16","question":"Will Company X file a Form D for a new raise by 2027-02-15?","resolution_source":"SEC EDGAR Form D search","resolves_by":"2027-02-15","horizon":"short","base_rate":0.18,"samples":[0.22,0.30,0.25],"aggregate":0.25,"market_price":null,"category":"ventures","models":["sonnet"]}
```
`horizon` is `short` (30 to 90 days) or `long` (the play's main payoff). `category` is one of `career`, `ventures`, `trends_access`, `assets`.

## plays.jsonl
```json
{"id":"P-2026-11-16-01","created":"2026-11-16","edition":"2026-11-16","name":"Company X before it hires ops","category":"ventures","thesis":"...","money_at_risk":0,"max_hours":6,"main_probability":0.15,"upside":"...","wrong_if":"...","exit":"...","review_on":"2027-02-15","status":"open","safety":"PASS (universal)","depends_on":[]}
```
`status` moves from `open` to `acted`, `passed`, `won`, `lost` or `expired` by adding a new record with the same id and a `status_date`.

## outcomes.jsonl
```json
{"id":"F-2026-11-16-03","kind":"forecast","resolved":"2027-02-10","outcome":1,"evidence_url":"https://..."}
{"id":"P-2026-11-16-01","kind":"play","resolved":"2027-06-01","outcome":"won","money_spent":0,"hours_spent":5,"result":"..."}
```
For forecasts, `outcome` is 1, 0, or null with a `reason` if it could not be resolved.

## actions.jsonl
```json
{"play_id":"P-2026-11-16-01","date":"2026-11-18","action":"Emailed their head of people","money_spent":0,"hours_spent":1}
```

## Other files
- `samples/<forecast-id>/sample-N.json`: each sealed forecaster's answer, saved before aggregation.
- `calibration-YYYY-MM.md`: the monthly scoreboard written by `scripts/score.py`.
- `practice.jsonl`: the owner's own forecasts in practice mode.
