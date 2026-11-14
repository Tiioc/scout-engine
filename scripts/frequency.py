#!/usr/bin/env python3
"""How often should exits be checked? Replays the growth mix on daily data (1927 on) with the
exit rule checked monthly, weekly or daily, with and without a buffer band, and reports
growth, the deepest fall on the daily path, the worst day and week, and trades per year.

Usage: python3 scripts/frequency.py --data /path/to/data [--out file.json]
"""
import argparse, json, os, sys
import numpy as np
import pandas as pd
import backtest as B

COST = {"small_value": .005, "momentum": .015}


def daily_panel(data, costs=True):
    f = B.french(os.path.join(data, "F-F_Research_Data_Factors_daily.csv"), ",Mkt-RF", digits=8)
    s = B.french(os.path.join(data, "6_Portfolios_2x3_Daily.csv"), ",SMALL LoBM", digits=8)
    m = B.french(os.path.join(data, "10_Portfolios_Prior_12_2_Daily.csv"), ",Lo PRIOR", digits=8)
    d = pd.DataFrame({"stocks": f["Mkt-RF"] + f["RF"], "bills": f["RF"], "small_value": s["SMALL HiBM"] - (COST["small_value"] / 252 if costs else 0),
                      "momentum": m["Hi PRIOR"] - (COST["momentum"] / 252 if costs else 0)}).dropna()
    d = d[(d > -0.99).all(axis=1)]
    d["two_x"] = (2 * d["stocks"] - d["bills"] - B.BORROW_SPREAD / 252).clip(lower=-1)
    return d


def weekly_blocks(data, band=0.02, lag_days=0, switch_cost=0.001):
    """Monthly returns of each block under the weekly exit rule, built from daily data, for the
    level search and the whole-life test. Costs of the underlying funds are not included here."""
    d = daily_panel(data, costs=False); b = d["bills"].values; out = {}
    for name, src, sig_src in (("trend_small_value", "small_value", "small_value"), ("trend_momentum", "momentum", "momentum"),
                               ("trend_stocks", "stocks", "stocks"), ("trend_2x_stocks", "two_x", "stocks")):
        h = signal(d[sig_src], "weekly", band)
        if lag_days: h = np.r_[np.zeros(lag_days, bool), h[:-lag_days]]
        r = np.where(h, d[src].values, b) - switch_cost * np.r_[False, h[1:] != h[:-1]]
        out[name] = (1 + pd.Series(r, index=d.index)).groupby(d.index // 100).prod() - 1
    return pd.DataFrame(out)


def signal(ret, mode, band=0.0, days=200):
    """True on days the block is held. Decided on check days from the close, used from the next day."""
    idx = (1 + ret).cumprod().values; n = len(idx); dates = ret.index.values
    ym = dates // 100
    if mode == "monthly":
        last = np.r_[ym[1:] != ym[:-1], True]; me = idx[last]
        avg = pd.Series(me).rolling(10).mean().values; ref = np.full(n, np.nan); ref[last] = avg; check = last
    else:
        ref = pd.Series(idx).rolling(days).mean().values
        check = np.ones(n, bool) if mode == "daily" else (np.arange(n) % 5 == 4)
    hold = np.zeros(n, bool); cur = False
    for i in range(n):
        hold[i] = cur
        if check[i] and not np.isnan(ref[i]):
            if cur and idx[i] < ref[i] * (1 - band): cur = False
            elif not cur and idx[i] > ref[i] * (1 + band): cur = True
    return hold


def run(d, gold_monthly, mode, band=0.0, switch_cost=0.001):
    w = {"sv": 0.2, "tsv": 0.1, "tmom": 0.5, "t2x": 0.1, "gold": 0.1}
    h_sv, h_mom, h_mkt = signal(d["small_value"], mode, band), signal(d["momentum"], mode, band), signal(d["stocks"], mode, band)
    b = d["bills"].values
    def blk(r, h):
        out = np.where(h, r, b); sw = np.r_[False, h[1:] != h[:-1]]; return out - switch_cost * sw, sw.sum()
    tsv, n1 = blk(d["small_value"].values, h_sv); tmom, n2 = blk(d["momentum"].values, h_mom); t2x, n3 = blk(d["two_x"].values, h_mkt)
    ym = d.index.values // 100; g = pd.Series(ym).map(gold_monthly).values
    cnt = pd.Series(ym).map(pd.Series(ym).value_counts()).values
    gold = (1 + np.nan_to_num(g)) ** (1 / cnt) - 1
    port = w["sv"] * d["small_value"].values + w["tsv"] * tsv + w["tmom"] * tmom + w["t2x"] * t2x + w["gold"] * gold
    L = np.cumsum(np.log1p(port)); yrs = len(port) / 252
    wk = L[5:] - L[:-5]; r12 = L[252:] - L[:-252]
    return {"growth_per_year_before_inflation": round(float(np.expm1(L[-1] / yrs)), 4),
            "deepest_fall": round(float(np.expm1((L - np.maximum.accumulate(L)).min())), 3),
            "worst_day": round(float(port.min()), 3), "worst_week": round(float(np.expm1(wk.min())), 3),
            "worst_12_months": round(float(np.expm1(r12.min())), 3),
            "trades_per_year": round(float((n1 + n2 + n3) / yrs), 1),
            "share_of_time_momentum_block_in_cash": round(float(1 - h_mom.mean()), 2)}


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--out")
    a = ap.parse_args(argv)
    d = daily_panel(a.data); real, df, mo = B.build(a.data)
    gm = {int(k): v for k, v in mo["year"].map(lambda y: (1 + df.loc[y, "gold"]) ** (1 / 12) - 1 if y in df.index else np.nan).items()}
    rep = {"days": len(d), "from": int(d.index[0]), "to": int(d.index[-1]), "results": {}}
    for label, mode, band in (("monthly check (the current rule)", "monthly", 0.0), ("weekly check", "weekly", 0.0), ("weekly check, 2% buffer", "weekly", 0.02),
                              ("weekly check, 4% buffer", "weekly", 0.04), ("daily check", "daily", 0.0), ("daily check, 2% buffer", "daily", 0.02), ("daily check, 4% buffer", "daily", 0.04)):
        rep["results"][label] = run(d, gm, mode, band)
    h = len(d) // 2
    for label, mode, band in (("monthly check", "monthly", 0.0), ("weekly check, 2% buffer", "weekly", 0.02), ("daily check, 2% buffer", "daily", 0.02)):
        rep.setdefault("first_half", {})[label] = run(d.iloc[:h], gm, mode, band); rep.setdefault("second_half", {})[label] = run(d.iloc[h:], gm, mode, band)
    txt = json.dumps(rep, indent=1)
    if a.out: open(a.out, "w").write(txt)
    print(txt); return 0


if __name__ == "__main__":
    sys.exit(main())
