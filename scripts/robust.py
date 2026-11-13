#!/usr/bin/env python3
"""Stress tests for the backtest: tries to break the result before anyone trusts it.

Guards against the usual failure of backtesting tools (a mix tuned to one lucky period):
different trend settings, doubled costs, different horizons, different start years,
removing each block, halving the known edges, reshuffled history, and other countries.

Usage: python3 scripts/robust.py --data /path/to/data [--out file.json]
"""
import argparse, json, os
import numpy as np
import pandas as pd
import backtest as B

A = B.ASSETS


def vec(m): return np.array([m.get(a, 0.0) for a in A])
def cagr(x): x = np.asarray(x); return float(np.prod(1 + x) ** (1 / len(x)) - 1)
def short(w, names=A): return {a: round(float(x), 1) for a, x in zip(names, w) if x > 0}


def pick(real, window=20, goal="best bad-luck result", names=A):
    best, _ = B.search(real[names], window)
    return best[goal]


def line(real, w, window=20):
    s = B.stats(real, w, window)
    return {"mix": short(w), "per_year": s["real_return_per_year"], "worst_year": s["worst_year"],
            "typical": s["window_median"], "bad_luck": s["window_p10"]}


def bootstrap(real, w, years=20, block=5, n=4000, seed=11):
    rng = np.random.default_rng(seed); R = real.values; T = len(R)
    si = A.index("stocks"); wins = 0; mix_end = []; st_end = []
    for _ in range(n):
        rows = []
        while len(rows) < years:
            s = rng.integers(0, T); rows += [(s + j) % T for j in range(block)]
        X = R[rows[:years]]
        a = b = 0.0
        for j in range(years):
            c = 1.02 ** j
            a = (a + c) * (1 + X[j] @ w); b = (b + c) * (1 + X[j, si])
        wins += a > b; mix_end.append(a); st_end.append(b)
    return {"chance_mix_beats_stocks": round(wins / n, 3),
            "mix_typical_vs_stocks": round(float(np.median(mix_end) / np.median(st_end)), 2),
            "mix_bad_luck_vs_stocks": round(float(np.percentile(mix_end, 10) / np.percentile(st_end, 10)), 2)}


def international(data):
    out = {}
    try:
        f = B.french(os.path.join(data, "Developed_ex_US_3_Factors.csv"), ",Mkt-RF")
        s = B.french(os.path.join(data, "Developed_ex_US_6_Portfolios_ME_BE-ME.csv"), ",SMALL LoBM")
        m = B.french(os.path.join(data, "Developed_ex_US_25_Portfolios_ME_Prior_12_2.csv"), ",SMALL LoPRIOR")
    except (FileNotFoundError, StopIteration, ValueError) as e:
        return {"error": str(e)}
    mkt = f["Mkt-RF"] + f["RF"]
    hi = [c for c in m.columns if "HiPRIOR" in c or c.endswith("PRIOR5")]
    d = pd.DataFrame({"market": mkt, "small_value": s["SMALL HiBM"], "momentum_big": m["BIG HiPRIOR"] if "BIG HiPRIOR" in m else m[hi].mean(axis=1)}).dropna()
    d = d[(d > -0.99).all(axis=1)]
    idx = (1 + d["market"]).cumprod()
    sig = (idx > idx.rolling(10).mean()).shift(1).fillna(False).astype(bool)
    d["trend_market"] = np.where(sig, d["market"], f["RF"].reindex(d.index))
    yrs = len(d) / 12
    out["period"] = [int(d.index[0]), int(d.index[-1])]
    out["nominal_usd_per_year"] = {c: round(float((1 + d[c]).prod() ** (1 / yrs) - 1), 4) for c in d.columns}
    cum = (1 + d).cumprod(); out["worst_fall"] = {c: round(float((cum[c] / cum[c].cummax() - 1).min()), 3) for c in d.columns}
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--out", default=None)
    a = ap.parse_args(); D = a.data
    real, df, mo = B.build(D)
    rep = {"years": [int(real.index[0]), int(real.index[-1])]}
    base = pick(real); nb = [x for x in A if x != "trend_2x_stocks"]
    base_nb = np.array([dict(zip(nb, pick(real, names=nb))).get(x, 0.0) for x in A])
    stocks = vec({"stocks": 1})
    rep["1_baseline_daily_2x"] = {"software_mix": line(real, base), "no_borrowing_mix": line(real, base_nb), "plain_stocks": line(real, stocks)}
    rep["2_trend_lookback"] = {}
    for lb in (6, 8, 10, 12):
        r2, _, _ = B.build(D, lookback=lb)
        rep["2_trend_lookback"][str(lb) + " months"] = {"base_mix_per_year": round(cagr(r2.values @ base), 4), "its_own_pick": short(pick(r2))}
    r3, _, _ = B.build(D, cost_mult=2.0)
    rep["3_costs_doubled"] = {"base_mix_per_year": round(cagr(r3.values @ base), 4), "stocks": round(cagr(r3["stocks"]), 4), "its_own_pick": short(pick(r3))}
    rep["4_horizons"] = {str(w) + " years": {g: short(v) for g, v in B.search(real, w)[0].items()} for w in (10, 15, 30)}
    rep["5_start_years"] = {}
    for y in (1950, 1970, 1990):
        sub = real.loc[y:]; w = min(20, len(sub) - 5)
        rep["5_start_years"]["from %d" % y] = {"base_mix_per_year": round(cagr(sub.values @ base), 4), "no_borrowing_per_year": round(cagr(sub.values @ base_nb), 4),
                                               "stocks": round(cagr(sub["stocks"]), 4), "its_own_pick": short(pick(sub, w))}
    rep["6_remove_one_block"] = {}
    for drop in ("small_value", "momentum", "trend_2x_stocks", "gold", "trend_small_value"):
        names = [x for x in A if x != drop]; w = np.array([dict(zip(names, pick(real, names=names))).get(x, 0.0) for x in A])
        rep["6_remove_one_block"]["without " + drop] = line(real, w)
    h = real.copy()
    for c in ("small_value", "momentum", "trend_small_value"):
        base_c = "stocks" if c != "trend_small_value" else "trend_stocks"
        h[c] = h[base_c] + 0.5 * (real[c] - real[base_c])
    rep["7_known_edges_halved"] = {"base_mix_per_year": round(cagr(h.values @ base), 4), "stocks": round(cagr(h["stocks"]), 4), "its_own_pick": line(h, pick(h))}
    rep["8_reshuffled_history"] = {"software_mix": bootstrap(real, base), "no_borrowing_mix": bootstrap(real, base_nb)}
    rng = np.random.default_rng(5); nb_res = []
    for _ in range(300):
        w = np.clip(base + rng.normal(0, 0.07, len(A)) * (base > 0), 0, None); w = w / w.sum()
        nb_res.append(cagr(real.values @ w))
    rep["9_nearby_mixes"] = {"lowest": round(min(nb_res), 4), "typical": round(float(np.median(nb_res)), 4), "highest": round(max(nb_res), 4)}
    rep["10_other_countries"] = international(D)
    dec = {}
    for d0 in range(1930, 2030, 10):
        sub = real.loc[d0:d0 + 9]
        if len(sub) >= 5: dec[str(d0) + "s"] = [round(cagr(sub.values @ base), 3), round(cagr(sub.values @ base_nb), 3), round(cagr(sub["stocks"]), 3)]
    rep["11_decades_mix_noborrow_stocks"] = dec
    txt = json.dumps(rep, indent=1)
    if a.out: open(a.out, "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
