#!/usr/bin/env python3
"""T5 of the pre-registered core test: the same candidates on real fund prices (Yahoo daily adjusted closes).
Proxies before a fund existed: international EFA before VXUS (2011-01); small value IJS before AVUV (2019-09).
Usage: python3 scripts/portfolio_lab_realfunds.py --data /home/claude/scout-data"""
import argparse, importlib.util, os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location("ct", os.path.join(HERE, "coretest.py")); ct = importlib.util.module_from_spec(sp); sp.loader.exec_module(ct); ag = ct.ag
CANDS = {"C1": {"us": 1}, "C2": {"us": .6, "intl": .4}, "C3": {"us": .8, "intl": .2}, "C4": {"us": .9, "sv": .1}, "C5": {"us": .7, "sv": .15, "intl": .15},
         "C6": {"us": .8, "lg": .2}, "C7": {"us": .9, "bond": .1}, "L1": {"us": .85, "x2exit": .15}, "L2": {"us": .5, "x2exit": .5}, "L3": {"us": .5, "x2": .5}}

def band_mix(R, w, band=.05):
    df = pd.DataFrame({k: R[k] for k in w}).dropna(); keys = list(w); W = np.array([w[k] for k in keys], float); W /= W.sum()
    cur = W.copy(); out = np.empty(len(df)); X = df[keys].values; m = df.index.month.values
    for i in range(len(df)):
        if i and m[i] != m[i - 1] and np.abs(cur - W).max() > band: cur = W.copy()
        r = float((cur * X[i]).sum()); out[i] = r; cur = cur * (1 + X[i]) / (1 + r)
    return pd.Series(out, index=df.index)

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); a = ap.parse_args(argv); D = a.data
    P = {t: ag.load(D, t).pct_change().dropna() for t in ("VTI", "QQQ", "EFA", "VXUS", "IJS", "AVUV", "SSO", "BIL", "IEF")}
    spy = ag.load(D, "SPY"); held = ag.held(spy, 0, days=200, band=.02, lag=1)   # placeholder replaced below by a daily check
    # daily check (every day), decided at close t, traded at close t+1
    ma = spy.rolling(200).mean().values; p = spy.values; on = []; st = True
    for i in range(len(spy)):
        if not np.isnan(ma[i]):
            if st and p[i] < ma[i] * .98: st = False
            elif not st and p[i] > ma[i] * 1.02: st = True
        on.append(st)
    held = pd.Series(on, index=spy.index).shift(2).fillna(True).astype(bool)
    idx = P["SSO"].index.intersection(P["BIL"].index); h = held.reindex(idx).fillna(True).astype(bool)
    sw = h.astype(int).diff().abs().fillna(0) * .0005
    R = {"us": P["VTI"], "intl": ct.splice(P["EFA"], P["VXUS"]), "sv": ct.splice(P["IJS"], P["AVUV"]), "lg": P["QQQ"], "bond": P["IEF"],
         "x2exit": pd.Series(np.where(h, P["SSO"].reindex(idx), P["BIL"].reindex(idx)), index=idx) - sw, "x2": P["SSO"]}
    for st in ("2007-06-01", "2009-04-01", "2012-01-01", "2015-01-01", "2020-01-01", "2022-01-01"):
        S = {k: v[v.index >= st] for k, v in R.items()}; rets = {c: band_mix(S, w) for c, w in CANDS.items()}
        common = rets["C1"].index
        for c in rets: common = common.intersection(rets[c].index)
        print("REAL FUNDS from", str(common[0].date()))
        b = rets["C1"].reindex(common)
        for c, r in rets.items():
            r = r.reindex(common); s = ag.stats(r)
            print("  %-3s %5.1f%%/yr  deepest fall %4.0f%%  worst day %4.0f%%  monthly deposits vs C1 %+6.1f%%" % (c, 100 * s["per_year"], 100 * s["deepest_fall"], 100 * s["worst_day"], 100 * (ag.dca(r) / ag.dca(b) - 1)))
if __name__ == "__main__": main()
