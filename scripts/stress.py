#!/usr/bin/env python3
"""Rough-up tests for the three-stage plan: named crashes and booms, late exits, doubled
costs, different exit settings, halved edges, and the whole-life result under each.

Usage: python3 scripts/stress.py --data /path/to/data [--out file.json]
"""
import argparse, json, sys
import numpy as np
import levels as Lv, lifecycle as LC

BAD = {"1929 crash": (192909, 193206), "1937 slump": (193703, 193803), "1973-74 bear market": (197301, 197409),
       "October 1987": (198709, 198711), "2000-02 tech bust": (200009, 200209), "2008 financial crisis": (200711, 200902),
       "2020 virus crash": (202002, 202003), "2022 rate shock": (202201, 202209)}
GOOD = {"1933-36 recovery": (193303, 193612), "1950s boom": (194907, 195607), "1982-87 bull": (198208, 198708),
        "late 1990s": (199501, 199912), "2009-19 bull": (200903, 201912), "2023-25": (202301, 202512)}


def span(r, dates, a, b):
    m = (dates >= a) & (dates <= b); return float(np.prod(1 + r[m]) - 1)


def plan_summary(M, infl, mixes, years=30, pol=None):
    R = LC.level_returns(M, mixes); W = LC.windows(len(M), years * 12)
    s = LC.summary(LC.simulate(R, infl, W, pol or LC.POLICIES["the plan: step down as the account grows"]))
    st = LC.summary(LC.simulate(M[:, Lv.A.index("stocks")][None, :], infl, W, {"kind": "fixed", "level": 0}))
    return {"typical": s["typical"], "bad_luck": s["bad_luck"], "worst": s["worst"], "worst_fall_ever": s["worst_fall_ever"],
            "plain_stocks_typical": st["typical"], "plain_stocks_bad_luck": st["bad_luck"]}


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--out"); ap.add_argument("--config", default="engine/config.json")
    a = ap.parse_args(argv)
    core = json.load(open(a.config))["core"]; mixes = [core[k] for k in ("growth_mix", "build_mix", "protect_mix")]
    M, infl, dates = Lv.panel(a.data, with_dates=True); R = LC.level_returns(M, mixes); S = M[:, Lv.A.index("stocks")]
    rep = {"episodes_bad": {}, "episodes_good": {}, "whole_life_30_years": {}, "each_level": {}}
    for name, grp in (("episodes_bad", BAD), ("episodes_good", GOOD)):
        for k, (x, y) in grp.items():
            rep[name][k] = {"growth": round(span(R[0], dates, x, y), 3), "build": round(span(R[1], dates, x, y), 3),
                            "protect": round(span(R[2], dates, x, y), 3), "plain_stocks": round(span(S, dates, x, y), 3)}
    rep["whole_life_30_years"]["as tested"] = plan_summary(M, infl, mixes)
    variants = {"exits acted on one month late": dict(lag=2), "all costs doubled": dict(cost_mult=2.0),
                "exit rule at 6 months": dict(lookback=6), "exit rule at 8 months": dict(lookback=8), "exit rule at 12 months": dict(lookback=12),
                "known edges cut in half": dict(edge=0.5), "known edges gone entirely": dict(edge=0.0)}
    for k, kw in variants.items():
        M2, i2 = Lv.panel(a.data, **kw); rep["whole_life_30_years"][k] = plan_summary(M2, i2, mixes)
    for half, sl in (("first half of history only", slice(0, len(M) // 2)), ("second half of history only", slice(len(M) // 2, None))):
        rep["whole_life_30_years"][half] = plan_summary(M[sl], infl[sl], mixes, years=20)
    for i, nm in enumerate(("growth", "build", "protect")):
        g, dd, w12 = Lv.measure(np.array([[mixes[i].get(x, 0.0) for x in Lv.A]]), M, infl)
        L = np.cumsum(np.log1p(R[i])); r12 = L[12:] - L[:-12]; r60 = L[60:] - L[:-60]
        rep["each_level"][nm] = {"mix": mixes[i], "real_growth_per_year": round(float(g[0]), 4), "worst_fall": round(float(dd[0]), 3), "worst_12_months": round(float(w12[0]), 3),
                                 "best_12_months": round(float(np.expm1(r12.max())), 3), "share_of_12_month_periods_down": round(float(np.mean(r12 < 0)), 3),
                                 "share_of_5_year_periods_down": round(float(np.mean(r60 < 0)), 3), "worst_month": round(float(R[i].min()), 3)}
    txt = json.dumps(rep, indent=1)
    if a.out: open(a.out, "w").write(txt)
    print(txt); return 0


if __name__ == "__main__":
    sys.exit(main())
