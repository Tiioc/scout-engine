#!/usr/bin/env python3
"""Paper scoreboard: every hunt pick against the S&P 500 (SPY) over the same days.

Ledger: ledger/paper.jsonl, add-only. Two kinds of record:
  {"id": "H-2026-11-16-01", "kind": "open", "date": "2026-11-16", "symbol": "XYZ", "thesis": "...", "edge": "...",
   "exit": {"stop": 8.0, "target": 15.0, "review_by": "2027-03-01"}, "forecast_beats_spy": 0.6}
  {"id": "H-2026-11-16-01", "kind": "close", "date": "2027-02-01", "reason": "target hit"}
A pick is entered at the close of the first trading day AFTER its date, so the price cannot be known when it is logged.
A close is taken at the close of the first trading day on or after its date. Prices are dividend-adjusted.

Usage:
  scoreboard.py [--ledger ledger/paper.jsonl] [--config engine/config.json] [--json]
  scoreboard.py --open ID SYMBOL --thesis "..." [--edge "..."] [--stop X] [--target Y] [--review-by DATE] [--forecast P] [--date D]
  scoreboard.py --close ID --reason "..." [--date D]
"""
import argparse, datetime, json, os, sys, urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "ScoutResearch research@example.com"}


def yahoo(symbol, start):
    """[(date, adjusted close)] from a few days before `start` to now."""
    p1 = int(datetime.datetime.combine(start - datetime.timedelta(days=7), datetime.time()).timestamp())
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?period1=%d&period2=%d&interval=1d&events=div%%2Csplit" % (symbol, p1, int(datetime.datetime.now().timestamp()) + 86400)
    d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))["chart"]["result"][0]
    adj = d["indicators"]["adjclose"][0]["adjclose"]
    return [(datetime.date.fromtimestamp(t), a) for t, a in zip(d["timestamp"], adj) if a is not None]


def read(path):
    if not os.path.exists(path): return []
    return [json.loads(x) for x in open(path) if x.strip()]


def picks(records):
    out = {}
    for r in records:
        if r["kind"] == "open": out[r["id"]] = dict(r, closed=None)
        elif r["kind"] == "close" and r["id"] in out: out[r["id"]].update(closed=r["date"], close_reason=r.get("reason", ""))
    return list(out.values())


def first_on_or_after(rows, day):
    for d, p in rows:
        if d >= day: return d, p
    return None


def measure(pick, prices, bench="SPY", today=None):
    """Return of the pick and of the benchmark from entry to exit (or to the latest close)."""
    day = datetime.date.fromisoformat(pick["date"]); today = today or datetime.date.today()
    rows, brow = prices(pick["symbol"], day), prices(bench, day)
    e, be = first_on_or_after(rows, day + datetime.timedelta(days=1)), first_on_or_after(brow, day + datetime.timedelta(days=1))
    if not e or not be: return dict(pick, status="waiting for entry")
    if pick["closed"]:
        x, bx = first_on_or_after(rows, datetime.date.fromisoformat(pick["closed"])), first_on_or_after(brow, datetime.date.fromisoformat(pick["closed"]))
        if not x or not bx: x, bx = rows[-1], brow[-1]
    else:
        x, bx = rows[-1], brow[-1]
    r, b = x[1] / e[1] - 1, bx[1] / be[1] - 1
    out = dict(pick, status="closed" if pick["closed"] else "open", entered=e[0].isoformat(), entry_price=round(e[1], 4), last_date=x[0].isoformat(),
               last_price=round(x[1], 4), pick_return=round(r, 4), spy_return=round(b, 4), lead=round(r - b, 4), days=(x[0] - e[0]).days)
    ex = pick.get("exit") or {}
    if not pick["closed"]:
        flags = []
        if ex.get("stop") and x[1] <= ex["stop"]: flags.append("STOP HIT: close it")
        if ex.get("target") and x[1] >= ex["target"]: flags.append("TARGET HIT: close it")
        if ex.get("review_by") and today.isoformat() >= ex["review_by"]: flags.append("REVIEW DATE REACHED: close or renew with a reason")
        if flags: out["flags"] = flags
    return out


def board(records, prices, cfg, today=None):
    rule = cfg.get("hunt", {}).get("unlock", {"min_closed": 20, "min_hit_rate": 0.5, "min_average_lead": 0.0})
    rows = [measure(p, prices, cfg.get("hunt", {}).get("benchmark", "SPY"), today) for p in picks(records)]
    live = [r for r in rows if "lead" in r]; closed = [r for r in live if r["status"] == "closed"]
    avg = lambda xs: round(sum(xs) / len(xs), 4) if xs else None
    s = {"picks": len(rows), "open": len([r for r in live if r["status"] == "open"]), "closed": len(closed),
         "average_pick_return": avg([r["pick_return"] for r in live]), "average_spy_return": avg([r["spy_return"] for r in live]),
         "average_lead": avg([r["lead"] for r in live]),
         "closed_hit_rate": avg([1.0 if r["lead"] > 0 else 0.0 for r in closed]), "closed_average_lead": avg([r["lead"] for r in closed])}
    need = []
    if len(closed) < rule["min_closed"]: need.append("%d more closed picks (have %d of %d)" % (rule["min_closed"] - len(closed), len(closed), rule["min_closed"]))
    if closed and s["closed_hit_rate"] < rule["min_hit_rate"]: need.append("hit rate %.0f%%, needs %.0f%%" % (s["closed_hit_rate"] * 100, rule["min_hit_rate"] * 100))
    if closed and s["closed_average_lead"] <= rule["min_average_lead"]: need.append("closed picks are not ahead of the S&P 500 on average")
    s["real_money"] = "UNLOCKED" if not need else "LOCKED"; s["still_needed"] = need
    return {"summary": s, "picks": rows}


def text(b):
    s = b["summary"]; pc = lambda x: "n/a" if x is None else "%+.1f%%" % (x * 100); L = []
    L.append("SCOREBOARD: %d picks (%d open, %d closed)" % (s["picks"], s["open"], s["closed"]))
    L.append("Average pick %s against S&P 500 %s, lead %s" % (pc(s["average_pick_return"]), pc(s["average_spy_return"]), pc(s["average_lead"])))
    L.append("Closed picks beating the S&P 500: %s" % ("n/a" if s["closed_hit_rate"] is None else "%.0f%%" % (s["closed_hit_rate"] * 100)))
    L.append("Real money: %s%s" % (s["real_money"], "" if not s["still_needed"] else " (needs " + "; ".join(s["still_needed"]) + ")"))
    for r in b["picks"]:
        if "lead" in r: L.append("  %-6s %-6s %s  pick %s  S&P %s  lead %s  %d days%s" % (r["symbol"], r["status"], r["entered"], pc(r["pick_return"]), pc(r["spy_return"]), pc(r["lead"]), r["days"], "  " + "; ".join(r["flags"]) if r.get("flags") else ""))
        else: L.append("  %-6s %s (logged %s)" % (r["symbol"], r["status"], r["date"]))
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", default=os.path.join(HERE, "ledger", "paper.jsonl")); ap.add_argument("--config", default=os.path.join(HERE, "engine", "config.json"))
    ap.add_argument("--json", action="store_true"); ap.add_argument("--open", nargs=2, metavar=("ID", "SYMBOL")); ap.add_argument("--close", metavar="ID")
    ap.add_argument("--thesis"); ap.add_argument("--edge"); ap.add_argument("--stop", type=float); ap.add_argument("--target", type=float)
    ap.add_argument("--review-by"); ap.add_argument("--forecast", type=float); ap.add_argument("--reason"); ap.add_argument("--date", default=datetime.date.today().isoformat())
    a = ap.parse_args(argv); cfg = json.load(open(a.config)); recs = read(a.ledger)
    if a.open:
        if not a.thesis: sys.exit("--thesis is required")
        if any(r["id"] == a.open[0] and r["kind"] == "open" for r in recs): sys.exit("that id is already open")
        mx = cfg.get("hunt", {}).get("max_open", 6)
        if len([p for p in picks(recs) if not p["closed"]]) >= mx: sys.exit("already %d open picks; close one first" % mx)
        rec = {"id": a.open[0], "kind": "open", "date": a.date, "symbol": a.open[1].upper(), "thesis": a.thesis, "edge": a.edge,
               "exit": {"stop": a.stop, "target": a.target, "review_by": a.review_by}, "forecast_beats_spy": a.forecast}
        open(a.ledger, "a").write(json.dumps(rec) + "\n"); print("logged", rec["id"]); return 0
    if a.close:
        if not any(p["id"] == a.close and not p["closed"] for p in picks(recs)): sys.exit("no open pick with that id")
        open(a.ledger, "a").write(json.dumps({"id": a.close, "kind": "close", "date": a.date, "reason": a.reason or ""}) + "\n"); print("closed", a.close); return 0
    cache = {}
    def prices(sym, day):
        k = (sym, day)
        if k not in cache: cache[k] = yahoo(sym, day)
        return cache[k]
    b = board(recs, prices, cfg)
    print(json.dumps(b, indent=1) if a.json else text(b)); return 0


if __name__ == "__main__":
    sys.exit(main())
