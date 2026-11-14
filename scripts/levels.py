#!/usr/bin/env python3
"""Risk levels: for each limit on the worst account-wide fall, the mix with the highest
growth in 98 years of monthly data. Each risky block can carry its own exit (the trend
rule on that block's own price). Losses are measured in dollars on the monthly path;
growth is after inflation.

Usage: python3 scripts/levels.py --data /path/to/data [--out file.json]
"""
import argparse, json, sys
import numpy as np
import pandas as pd
import backtest as B

A = ["stocks", "small_value", "momentum", "trend_stocks", "trend_small_value", "trend_momentum", "trend_2x_stocks", "gold", "bonds", "bills"]
COST = {"stocks": .0005, "small_value": .005, "momentum": .015, "trend_small_value": .005, "trend_momentum": .015, "gold": .002, "bonds": .0005}
LIMITS = (0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60, 1.0)


def panel(data, lookback=10, cost_mult=1.0, lag=1, edge=1.0, with_dates=False, exits="weekly", lag_days=0):
    """Monthly returns for every block. lag=2 acts on each exit one month late; edge=0.5
    halves the advantage of small cheap companies and momentum over the plain market."""
    real, df, mo = B.build(data, lookback=lookback)
    if edge != 1.0:
        for c in ("small_value", "momentum"): mo[c] = mo["stocks"] + edge * (mo[c] - mo["stocks"])
        mo["trend_small_value"] = B.trend(mo["small_value"], mo["bills"], lookback=lookback)
    mo["trend_momentum"] = B.trend(mo["momentum"], mo["bills"], lookback=lookback)
    if lag > 1:
        for blk, src in (("trend_stocks", "stocks"), ("trend_small_value", "small_value"), ("trend_momentum", "momentum")):
            idx = (1 + mo[src]).cumprod(); sig = (idx > idx.rolling(lookback).mean()).shift(lag).fillna(False).astype(bool)
            mo[blk] = np.where(sig, mo[src], mo["bills"]) - B.SWITCH_COST * (sig != sig.shift(1)).fillna(False).astype(float)
    if exits == "weekly" and edge == 1.0 and lookback == 10 and lag == 1:
        import frequency as Fq
        wb = Fq.weekly_blocks(data, lag_days=lag_days)
        for c in wb.columns: mo[c] = wb[c].reindex(mo.index)
    for c in ("bonds", "gold"):
        mo[c] = mo["year"].map(lambda y: (1 + df.loc[y, c]) ** (1 / 12) - 1 if y in df.index else np.nan)
    mo["infl"] = mo["year"].map(lambda y: (1 + df.loc[y, "infl"]) ** (1 / 12) - 1 if y in df.index else np.nan)
    mo = mo.dropna()
    M = mo[A].values.copy()
    for i, a in enumerate(A): M[:, i] -= COST.get(a, 0) * cost_mult / 12
    if with_dates: return M, mo["infl"].values, np.array(mo.index)
    return M, mo["infl"].values


def measure(W, M, infl):
    n = len(W); dd = np.empty(n); g = np.empty(n); w12 = np.empty(n); yrs = len(M) / 12
    Li = np.cumsum(np.log1p(infl))
    for s in range(0, n, 4000):
        L = np.cumsum(np.log1p(W[s:s + 4000] @ M.T), axis=1)
        dd[s:s + 4000] = np.expm1((L - np.maximum.accumulate(L, axis=1)).min(axis=1))
        g[s:s + 4000] = np.expm1((L[:, -1] - Li[-1]) / yrs)
        w12[s:s + 4000] = np.expm1((L[:, 12:] - L[:, :-12]).min(axis=1))
    return g, dd, w12


def levels(M, infl, limits=LIMITS):
    W = np.array(list(B.weights_grid(M.shape[1]))) / 10.0
    g, dd, w12 = measure(W, M, infl); out = {}
    for lim in limits:
        ok = dd >= -lim
        if not ok.any(): continue
        i = np.where(ok)[0][np.argmax(g[ok])]
        out["%d" % round(lim * 100)] = {"mix": {a: float(x) for a, x in zip(A, W[i]) if x > 0}, "real_growth_per_year": round(float(g[i]), 4),
                                        "worst_fall": round(float(dd[i]), 3), "worst_12_months": round(float(w12[i]), 3)}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--out")
    a = ap.parse_args(argv)
    M, infl = panel(a.data); h = len(M) // 2
    rep = {"full_history": levels(M, infl),
           "chosen_on_first_half_tested_on_second": {}}
    first = levels(M[:h], infl[:h], (0.25, 0.35, 0.50))
    for k, v in first.items():
        w = np.array([[v["mix"].get(x, 0.0) for x in A]]); g, dd, w12 = measure(w, M[h:], infl[h:])
        rep["chosen_on_first_half_tested_on_second"][k] = {"mix": v["mix"], "real_growth_per_year": round(float(g[0]), 4), "worst_fall": round(float(dd[0]), 3)}
    for nm, m in (("plain stocks", {"stocks": 1.0}), ("60% stocks 40% bonds", {"stocks": .6, "bonds": .4})):
        w = np.array([[m.get(x, 0.0) for x in A]]); g, dd, w12 = measure(w, M, infl)
        rep.setdefault("for_comparison", {})[nm] = {"real_growth_per_year": round(float(g[0]), 4), "worst_fall": round(float(dd[0]), 3), "worst_12_months": round(float(w12[0]), 3)}
    txt = json.dumps(rep, indent=1)
    if a.out: open(a.out, "w").write(txt)
    print(txt); return 0


if __name__ == "__main__":
    sys.exit(main())
