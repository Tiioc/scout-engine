#!/usr/bin/env python3
"""Set-and-forget core candidates on real fund prices (daily, dividend-adjusted, yearly rebalance).
Usage: python3 scripts/coretest.py --data /home/claude/scout-data"""
import argparse, importlib.util, os, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location("ag", os.path.join(HERE, "aggressive.py")); ag = importlib.util.module_from_spec(sp); sp.loader.exec_module(ag)

def splice(a, b):
    """Returns of a until b starts, then b."""
    return pd.concat([a[a.index < b.index[0]], b])

def mix(R, w, rebalance="Y"):
    """Daily returns of a weighted mix, rebalanced at each year end (drifts in between)."""
    df = pd.DataFrame({k: R[k] for k in w}).dropna(); keys = list(w); wt = np.array([w[k] for k in keys], float); wt /= wt.sum()
    cur = wt.copy(); out = np.empty(len(df)); yrs = df.index.year.values; X = df[keys].values
    for i in range(len(df)):
        if i and yrs[i] != yrs[i - 1]: cur = wt.copy()
        r = float((cur * X[i]).sum()); out[i] = r; cur = cur * (1 + X[i]) / (1 + r)
    return pd.Series(out, index=df.index)

def row(name, r, b):
    b = b.reindex(r.index); s = ag.stats(r)
    return "  %-46s %5.1f%% a year  deepest fall %4.0f%%  deposits vs VTI %+5.1f%%  10y-win %s" % (name, s["per_year"] * 100, s["deepest_fall"] * 100, 100 * (ag.dca(r) / ag.dca(b) - 1), ag.roll_win(r, b, n=2520))

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); a = ap.parse_args(argv); D = a.data
    P = {t: ag.load(D, t).pct_change().dropna() for t in ("VTI", "QQQ", "EFA", "VXUS", "IJS", "AVUV", "SSO", "BIL", "SPY")}
    R = {"us": P["VTI"], "nasdaq": P["QQQ"], "intl": splice(P["EFA"], P["VXUS"]), "smallvalue": splice(P["IJS"], P["AVUV"]), "cash": P["BIL"]}
    spy_price = ag.load(D, "SPY"); held = sum(ag.held(spy_price, ph).astype(float) for ph in range(5)) / 5   # five staggered slices
    idx = P["SSO"].index.intersection(P["BIL"].index)
    R["x2exit"] = (held.reindex(idx) * P["SSO"].reindex(idx) + (1 - held.reindex(idx)) * P["BIL"].reindex(idx)).dropna()
    CORES = {"A  VTI 100": {"us": 1},
             "B  VTI 90, small value 10 (current core)": {"us": .9, "smallvalue": .1},
             "C  VTI 60, QQQ 15, international 10 (proposed)": {"us": .60, "nasdaq": .15, "intl": .10},
             "D  VTI 80, international 20": {"us": .8, "intl": .2},
             "E  VTI 80, QQQ 20": {"us": .8, "nasdaq": .2},
             "F  VTI 70, QQQ 10, international 10, small value 10": {"us": .7, "nasdaq": .1, "intl": .1, "smallvalue": .1}}
    for st in ("2001-09-01", "2007-06-01", "2010-01-01", "2015-01-01", "2020-01-01", "2022-01-01"):
        print("CORES ONLY, start", st[:7]); b = R["us"][R["us"].index >= st]
        for n, w in CORES.items(): print(row(n, mix({k: v[v.index >= st] for k, v in R.items()}, w), b))
    print()
    for st in ("2007-06-01", "2010-01-01", "2015-01-01", "2020-01-01", "2022-01-01"):
        print("WHOLE PORTFOLIO with a 15% riskier slice (2x S&P 500 held only above its 200-day average), start", st[:7]); S = {k: v[v.index >= st] for k, v in R.items()}; b = S["us"]
        for n, w in (("A  VTI 100, no slice", {"us": 1}), ("C  proposed core 85, no slice", {"us": .60, "nasdaq": .15, "intl": .10}),
                     ("A+ VTI 85, slice 15", {"us": .85, "x2exit": .15}), ("C+ VTI 60, QQQ 15, intl 10, slice 15", {"us": .60, "nasdaq": .15, "intl": .10, "x2exit": .15}),
                     ("G+ VTI 65, intl 10, small value 10, slice 15", {"us": .65, "intl": .10, "smallvalue": .10, "x2exit": .15})):
            print(row(n, mix(S, w), b))
    print()
    # the Nasdaq tilt through the 2000 crash (SPY as the US market; QQQ starts 1999-03)
    S = {"us": P["SPY"][P["SPY"].index >= "1999-03-10"], "nasdaq": P["QQQ"]}
    for st in ("1999-03-10", "2000-03-01", "2003-01-01"):
        T = {k: v[v.index >= st] for k, v in S.items()}; b = T["us"]
        print("NASDAQ TILT against the S&P 500, start", st[:7]); print(row("S&P 500 only", b, b)); print(row("S&P 500 80, QQQ 20", mix(T, {"us": .8, "nasdaq": .2}), b)); print(row("QQQ only", T["nasdaq"], b))
    # yearly record
    yr = lambda r: (1 + r).groupby(r.index.year).prod() - 1
    t = pd.DataFrame({"VTI": yr(R["us"]), "QQQ": yr(R["nasdaq"]), "intl": yr(R["intl"])}).dropna().loc[2002:2025]
    print("\nYears QQQ beat VTI: %d of %d.  Years international beat VTI: %d of %d.  2002-2009 a year: VTI %.1f%%, intl %.1f%%.  2010-2025 a year: VTI %.1f%%, intl %.1f%%." % (
        (t.QQQ > t.VTI).sum(), len(t), (t.intl > t.VTI).sum(), len(t), 100 * ((1 + t.VTI.loc[2002:2009]).prod() ** (1 / 8) - 1), 100 * ((1 + t.intl.loc[2002:2009]).prod() ** (1 / 8) - 1),
        100 * ((1 + t.VTI.loc[2010:2025]).prod() ** (1 / 16) - 1), 100 * ((1 + t.intl.loc[2010:2025]).prod() ** (1 / 16) - 1)))
    # overlap risk
    c = pd.DataFrame({"VTI": R["us"], "QQQ": R["nasdaq"], "intl": R["intl"]}).dropna().loc["2016":]
    print("Daily correlation with VTI since 2016: QQQ %.2f, international %.2f" % (c.corr().loc["VTI", "QQQ"], c.corr().loc["VTI", "intl"]))

if __name__ == "__main__": main()
