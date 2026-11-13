#!/usr/bin/env python3
"""Rule-based backtest of long-term portfolios on public historical data.

This tests mechanical rules (fixed mixes, a trend rule, tilts), never the Scout's own
forecasts, so it is a fair test. The software searches every mix in 10% steps and reports
the winners under three goals. A walk-forward check shows how a mix chosen on the first
half of history did on the second half.

Data (public, free): Damodaran annual returns 1928+, Ken French monthly portfolios 1926+.
Usage: python3 scripts/backtest.py --data /path/to/data [--window 20] [--out file.json]
"""
import argparse, itertools, json, os
import numpy as np
import pandas as pd

ASSETS = ["stocks", "small_value", "momentum", "trend_stocks", "trend_small_value",
          "trend_2x_stocks", "bonds", "gold", "real_estate", "bills"]
# Assumptions the data does not contain (flagged in the report):
COST = {"small_value": 0.005, "momentum": 0.015, "stocks": 0.0005, "gold": 0.002, "bonds": 0.0005}
SWITCH_COST = 0.001          # each move in or out under the trend rule
BORROW_SPREAD = 0.015        # yearly cost above bills for the 2x version, fees included
NET_RENT_YIELD = 0.04        # modeled rent after costs, added to house-price change


def french(path, header_starts, digits=6):
    rows, on = [], False
    for line in open(path):
        s = line.strip()
        if not on:
            if s.startswith(header_starts): on = True; cols = [c.strip() for c in s.split(",")[1:]]
            continue
        p = s.split(",")
        if len(p) < 2 or not p[0].strip().isdigit() or len(p[0].strip()) != digits: break
        rows.append([int(p[0])] + [float(v) / 100 for v in p[1:]])
    return pd.DataFrame(rows, columns=["ym"] + cols).set_index("ym")


def load(data):
    f = french(os.path.join(data, "F-F_Research_Data_Factors.csv"), ",Mkt-RF")
    s = french(os.path.join(data, "6_Portfolios_2x3.csv"), ",SMALL LoBM")
    m = french(os.path.join(data, "10_Portfolios_Prior_12_2.csv"), ",Lo PRIOR")
    mo = pd.DataFrame({"stocks": f["Mkt-RF"] + f["RF"], "bills": f["RF"],
                       "small_value": s["SMALL HiBM"], "momentum": m["Hi PRIOR"]}).dropna()
    x = pd.read_excel(os.path.join(data, "histretSP.xls"), sheet_name="Returns by year", header=None)
    h = next(i for i in range(40) if str(x.iloc[i, 0]).strip() == "Year")
    names = [str(c) for c in x.iloc[h]]
    col = lambda key, nth=0: [i for i, n in enumerate(names) if key in n][nth]
    rows = {}
    for i in range(h + 1, len(x)):
        try: y = int(float(x.iloc[i, 0]))
        except (ValueError, TypeError): break
        rows[y] = {"bonds": x.iloc[i, col("T. Bond")], "gold": x.iloc[i, col("Gold")],
                   "house": x.iloc[i, col("Real Estate")], "infl": x.iloc[i, col("Inflation")]}
    return mo, pd.DataFrame(rows).T.astype(float)


def trend(ret, bills, lev=1.0, lookback=10):
    """In the asset when its total-return index is above its 10-month average, else in bills."""
    idx = (1 + ret).cumprod()
    sig = (idx > idx.rolling(lookback).mean()).shift(1).fillna(False).astype(bool)
    r = np.where(sig, lev * ret - (lev - 1) * (bills + BORROW_SPREAD / 12), bills)
    r = pd.Series(r, index=ret.index) - SWITCH_COST * (sig != sig.shift(1)).fillna(False).astype(float)
    return r.clip(lower=-1.0)


def daily_2x(data, mo, lookback=10):
    """The 2x block the way a real fund works: leverage reset every trading day, so one-day
    crashes and the drag from choppy markets are both counted. Trend signal checked monthly."""
    d = french(os.path.join(data, "F-F_Research_Data_Factors_daily.csv"), ",Mkt-RF", digits=8)
    mkt, rf = d["Mkt-RF"] + d["RF"], d["RF"]
    fund = (2 * mkt - rf - BORROW_SPREAD / 252).clip(lower=-1.0)
    idx = (1 + mo["stocks"]).cumprod()
    sig = (idx > idx.rolling(lookback).mean()).shift(1).fillna(False).astype(bool)
    ym = pd.Series(d.index // 100, index=d.index)
    on = ym.map(sig).fillna(False).astype(bool)
    r = pd.Series(np.where(on, fund, rf), index=d.index)
    monthly = (1 + r).groupby(ym).prod() - 1
    monthly = monthly - SWITCH_COST * (sig != sig.shift(1)).reindex(monthly.index).fillna(False).astype(float)
    return monthly, r


def build(data, lookback=10, cost_mult=1.0, daily_leverage=True):
    mo, an = load(data)
    mo["trend_stocks"] = trend(mo["stocks"], mo["bills"], lookback=lookback)
    mo["trend_small_value"] = trend(mo["small_value"], mo["bills"], lookback=lookback)
    if daily_leverage and os.path.exists(os.path.join(data, "F-F_Research_Data_Factors_daily.csv")):
        mo["trend_2x_stocks"] = daily_2x(data, mo, lookback)[0].reindex(mo.index)
        mo = mo.dropna()
    else:
        mo["trend_2x_stocks"] = trend(mo["stocks"], mo["bills"], lev=2.0, lookback=lookback)
    mo["year"] = mo.index // 100
    cols = [c for c in mo.columns if c != "year"]
    yr = mo.groupby("year")[cols].apply(lambda d: (1 + d).prod() - 1)
    cnt = mo.groupby("year").size()
    yr = yr[cnt == 12]
    for k, c in COST.items():
        if k in yr: yr[k] = yr[k] - c * cost_mult
    df = yr.join(an, how="inner")
    df["real_estate"] = df["house"] + NET_RENT_YIELD
    real = pd.DataFrame({a: (1 + df[a]) / (1 + df["infl"]) - 1 for a in ASSETS})
    return real, df, mo


def weights_grid(n, step=10):
    k = 100 // step
    for c in itertools.combinations(range(k + n - 1), n - 1):
        prev, w = -1, []
        for x in c: w.append(x - prev - 1); prev = x
        w.append(k + n - 2 - prev)
        yield w


def terminal(P, window, growth=0.02):
    """P: (portfolios, years) real returns. Wealth at the end of every rolling window for a
    saver adding 1 unit a year (rising with real pay growth), in today's dollars."""
    n_years = P.shape[1]; out = []
    for s in range(n_years - window + 1):
        w = np.zeros(P.shape[0])
        for j in range(window):
            w = (w + (1 + growth) ** j) * (1 + P[:, s + j])
        out.append(w)
    return np.stack(out, axis=1)


def stats(real, w, window):
    p = (real.values @ np.array(w))[None, :]
    t = terminal(p, window)[0]
    g = np.prod(1 + p[0]) ** (1 / p.shape[1]) - 1
    cum = np.cumprod(1 + p[0]); dd = (cum / np.maximum.accumulate(cum) - 1).min()
    return {"real_return_per_year": round(float(g), 4), "worst_calendar_drawdown": round(float(dd), 3),
            "worst_year": round(float(p[0].min()), 3),
            "window_median": round(float(np.median(t)), 1), "window_p10": round(float(np.percentile(t, 10)), 1),
            "window_worst": round(float(t.min()), 1), "window_best": round(float(t.max()), 1)}


def search(real, window, lo=None, hi=None):
    R = real.values if lo is None else real.loc[lo:hi].values
    W = np.array(list(weights_grid(R.shape[1]))) / 10.0
    best = {}
    T = np.concatenate([terminal(W[i:i + 20000] @ R.T, window) for i in range(0, len(W), 20000)])
    for name, score in (("highest typical result", np.median(T, axis=1)),
                        ("best bad-luck result", np.percentile(T, 10, axis=1)),
                        ("best worst case", T.min(axis=1))):
        best[name] = W[int(np.argmax(score))]
    return best, len(W)


def fmt(w):
    return {a: round(float(x), 1) for a, x in zip(ASSETS, w) if x > 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True); ap.add_argument("--window", type=int, default=20)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    real, df, mo = build(a.data)
    y0, y1 = int(real.index[0]), int(real.index[-1]); mid = (y0 + y1) // 2
    rep = {"years": [y0, y1], "window": a.window,
           "assumptions": {"costs_per_year": COST, "switch_cost": SWITCH_COST, "borrow_spread_2x": BORROW_SPREAD,
                           "modeled_net_rent_yield": NET_RENT_YIELD, "all_figures": "after inflation, before taxes"}}
    rep["single_assets"] = {x: stats(real, [1.0 if b == x else 0.0 for b in ASSETS], a.window) for x in ASSETS}
    best, n = search(real, a.window)
    rep["mixes_tested"] = n
    rep["winners_full_history"] = {k: {"mix": fmt(w), **stats(real, w, a.window)} for k, w in best.items()}
    # walk-forward: choose on the first half, judge on the second half (and the reverse)
    wf = {}
    for label, (tr, te) in {"chosen on %d-%d, tested on %d-%d" % (y0, mid, mid + 1, y1): ((y0, mid), (mid + 1, y1)),
                            "chosen on %d-%d, tested on %d-%d" % (mid + 1, y1, y0, mid): ((mid + 1, y1), (y0, mid))}.items():
        b, _ = search(real, a.window, tr[0], tr[1]); test = real.loc[te[0]:te[1]]
        wf[label] = {k: {"mix": fmt(w), "test": stats(test, w, a.window)} for k, w in b.items()}
        wf[label]["plain stocks on the test years"] = stats(test, [1.0 if x == "stocks" else 0.0 for x in ASSETS], a.window)
    rep["walk_forward"] = wf
    txt = json.dumps(rep, indent=1)
    if a.out: open(a.out, "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
