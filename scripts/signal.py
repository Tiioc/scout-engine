#!/usr/bin/env python3
"""Monthly trend signal for the core: is the S&P 500 above its 10-month average?

Uses month-end closes of the S&P 500 from FRED (free). The backtest used a total-return
index; the price index gives the same answer except in rare near-ties, which are flagged.

Usage: python3 scripts/signal.py [--file SP500.csv] [--lookback 10]
"""
import argparse, csv, io, json, subprocess, sys, urllib.request

URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500"


def month_ends(rows):
    """rows: iterable of (YYYY-MM-DD, close). Returns [(YYYY-MM, last close of month)]."""
    out = {}
    for d, v in rows:
        try: out[d[:7]] = float(v)
        except (TypeError, ValueError): continue
    return sorted(out.items())


def compute(rows, lookback=10, today=None):
    me = month_ends(rows)
    if today and me and me[-1][0] == today[:7]:
        me = me[:-1]                      # ignore the month still in progress
    if len(me) < lookback: raise ValueError("need at least %d completed months" % lookback)
    last = me[-lookback:]
    avg = sum(v for _, v in last) / lookback
    gap = last[-1][1] / avg - 1
    return {"as_of_month": last[-1][0], "close": last[-1][1], "average": round(avg, 2), "gap": round(gap, 4),
            "signal": "on" if gap > 0 else "off", "near_tie": abs(gap) < 0.01,
            "meaning": "hold the stock block" if gap > 0 else "hold cash in place of the stock block"}


YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=2y&interval=1d"


def fund_rows(ticker):
    """Daily dividend-adjusted closes for one fund, as (date, close) rows."""
    import datetime
    url = YAHOO % ticker
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        raw = urllib.request.urlopen(req, timeout=30).read().decode()
    except Exception:
        raw = subprocess.run(["curl", "-sS", "-m", "30", "-A", "Mozilla/5.0", url], capture_output=True, text=True, check=True).stdout
    r = json.loads(raw)["chart"]["result"][0]
    px = r["indicators"].get("adjclose", [{}])[0].get("adjclose") or r["indicators"]["quote"][0]["close"]
    return [(datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d"), v) for t, v in zip(r["timestamp"], px) if v is not None]


def fund_signal(ticker, lookback=10, today=None):
    out = compute(fund_rows(ticker), lookback, today); out["ticker"] = ticker
    return out


def fetch():
    try:
        return urllib.request.urlopen(URL, timeout=30).read().decode()
    except Exception:
        return subprocess.run(["curl", "-sS", "-m", "30", URL], capture_output=True, text=True, check=True).stdout


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--file"); ap.add_argument("--lookback", type=int, default=10)
    ap.add_argument("--ticker", help="signal for one fund from its own price")
    ap.add_argument("--today", default=None, help="YYYY-MM-DD; drops the unfinished month")
    a = ap.parse_args(argv)
    if a.ticker:
        print(json.dumps(fund_signal(a.ticker, a.lookback, a.today), indent=2)); return 0
    text = open(a.file).read() if a.file else fetch()
    rows = list(csv.reader(io.StringIO(text)))[1:]
    print(json.dumps(compute(rows, a.lookback, a.today), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
