#!/usr/bin/env python3
"""Aggressive portfolios with an exit rule, on real fund prices (daily) and on long history (modeled 2x).
Rule: checked every 5th trading day (all five phases reported), exit when the index is >2% below its
200-day average, re-enter when >2% above, traded at the NEXT day's close, 0.05% cost per switch.
Usage: python3 scripts/aggressive.py --data /home/claude/scout-data [--out file.json]"""
import argparse, json, datetime, numpy as np, pandas as pd

def load(D, t):
    d = json.load(open(f"{D}/yd/{t}.json"))["chart"]["result"][0]
    s = pd.Series(d["indicators"]["adjclose"][0]["adjclose"], index=pd.to_datetime([datetime.date.fromtimestamp(x) for x in d["timestamp"]])).dropna()
    return s[~s.index.duplicated()]

def held(price, phase, days=200, band=0.02, lag=1):
    """True on days the risky fund is held. Decision at close of check day t, position changes from close of t+lag."""
    ma = price.rolling(days).mean(); n = len(price); on = np.zeros(n, bool); state = True; p = price.values; m = ma.values
    for i in range(n):
        if i % 5 == phase and not np.isnan(m[i]):
            if state and p[i] < m[i] * (1 - band): state = False
            elif not state and p[i] > m[i] * (1 + band): state = True
        on[i] = state
    h = pd.Series(on, index=price.index).shift(1 + lag).fillna(True).astype(bool)  # return on day d earned if held from close d-1
    return h

def gated(r_fund, r_cash, h, cost=0.0005):
    r = np.where(h, r_fund, r_cash); sw = h.astype(int).diff().abs().fillna(0).values
    return pd.Series(r - sw * cost, index=r_fund.index)

def stats(r, ppy=252):
    v = (1 + r).cumprod(); yrs = (r.index[-1] - r.index[0]).days / 365.25 if hasattr(r.index[0], "year") else len(r) / ppy
    return {"per_year": round(float(v.iloc[-1] ** (1 / yrs) - 1), 4), "deepest_fall": round(float((v / v.cummax() - 1).min()), 3), "worst_day": round(float(r.min()), 3)}

def dca(r, step=21):
    v = 0.0; x = r.values
    for i in range(len(x)):
        if i % step == 0: v += 1
        v *= 1 + x[i]
    return v

def roll_win(r, b, n=252 * 5, step=21):
    lr, lb = np.log1p(r).cumsum().values, np.log1p(b).cumsum().values
    w = [(lr[i + n] - lr[i]) > (lb[i + n] - lb[i]) for i in range(0, len(lr) - n, step)]
    return round(float(np.mean(w)), 2) if w else None

def mixes(R, H):
    """R: dict of daily return series; H: dict of held-flags. Returns dict name -> series."""
    c = R["cash"]; g = lambda k, sig: gated(R[k], c, H[sig])
    out = {"A plain stocks": R["spy"], "B stocks with exit": g("spy", "sp"), "C 2x stocks with exit": g("x2", "sp"),
           "D half stocks, half 2x with exit": .5 * R["spy"] + .5 * g("x2", "sp"), "E 70 stocks, 30 2x with exit": .7 * R["spy"] + .3 * g("x2", "sp"),
           "J 2x stocks, no exit": R["x2"]}
    if "gold" in R: out["I 40 stocks, 40 2x with exit, 20 gold"] = .4 * R["spy"] + .4 * g("x2", "sp") + .2 * R["gold"]
    if "x3" in R: out["F 3x stocks with exit"] = g("x3", "sp"); out["G half stocks, half 3x with exit"] = .5 * R["spy"] + .5 * g("x3", "sp")
    if "q2" in R: out["H 2x Nasdaq with exit (hindsight pick)"] = g("q2", "nq")
    return out

def evaluate(build, starts, bench="A plain stocks"):
    rep = {}
    for st in starts:
        per = {}
        for ph in range(5):
            M = build(ph); M = {k: v[v.index >= st].dropna() for k, v in M.items()}
            for k, v in M.items():
                if len(v) < 252 or v.index[0] > pd.Timestamp(st) + pd.Timedelta(days=30): continue
                b = M[bench].reindex(v.index); s = stats(v); s["deposits_vs_stocks"] = round(dca(v) / dca(b) - 1, 3); s["five_year_win_rate"] = roll_win(v, b)
                per.setdefault(k, []).append(s)
        rep[str(st)[:10]] = {k: {m: {"typical": float(np.median([x[m] for x in L if x[m] is not None] or [np.nan])), "worst_phase": float(min([x[m] for x in L if x[m] is not None] or [np.nan]))} for m in L[0]} for k, L in per.items()}
    return rep

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--out"); a = ap.parse_args(argv); D = a.data
    P = {k: load(D, t) for k, t in (("spy", "SPY"), ("x2", "SSO"), ("x3", "UPRO"), ("q", "QQQ"), ("q2", "QLD"), ("gold", "GLD"), ("cash", "BIL"))}
    def real(ph):
        idx = P["spy"].index[P["spy"].index >= "2007-06-01"]; R = {k: P[k].pct_change().reindex(idx) for k in ("spy", "x2", "q2", "gold", "cash")}
        R["x3"] = P["x3"].pct_change().reindex(idx); H = {"sp": held(P["spy"], ph).reindex(idx), "nq": held(P["q"], ph).reindex(idx)}
        return mixes(R, H)
    rep = {"real_funds": evaluate(real, ["2007-06-01", "2009-04-01", "2010-01-01", "2015-01-01", "2020-01-01", "2022-01-01"])}
    # long history: French daily market, modeled 2x and 3x (daily reset, borrow at bills + 1.5%, 0.9% fee)
    f = open(f"{D}/F-F_Research_Data_Factors_daily.csv").read().splitlines(); rows = [x.split(",") for x in f if x[:8].strip().isdigit() and len(x.split(",")) >= 5]
    df = pd.DataFrame(rows).iloc[:, :5]; df.columns = ["d", "mkt", "smb", "hml", "rf"]; df.index = pd.to_datetime(df.d.str.strip()); df = df.drop(columns="d").astype(float) / 100
    mk = df.mkt + df.rf; rf = df.rf; price = (1 + mk).cumprod()
    lev = lambda L: L * mk - (L - 1) * (rf + 0.015 / 252) - 0.009 / 252
    def hist(ph):
        R = {"spy": mk, "x2": lev(2), "x3": lev(3), "cash": rf}; return mixes(R, {"sp": held(price, ph)})
    rep["long_history_modeled"] = evaluate(hist, ["1926-07-01", "1950-01-01", "1970-01-01", "1990-01-01", "2000-01-01", "2010-01-01"])
    eras = {}
    for lo, hi in (("1926", "1949"), ("1950", "1969"), ("1970", "1989"), ("1990", "2009"), ("2010", "2026")):
        M = hist(2); eras[f"{lo}-{hi}"] = {k: stats(v[lo:hi]) for k, v in M.items()}
    rep["long_history_by_era_phase2"] = eras
    if a.out: json.dump(rep, open(a.out, "w"), indent=1)
    for sec in ("real_funds", "long_history_modeled"):
        print("==", sec)
        for st, d in rep[sec].items():
            print(" start", st)
            for k, s in sorted(d.items()):
                print(f"   {k:42s} yr {s['per_year']['typical']*100:5.1f}% (worst {s['per_year']['worst_phase']*100:5.1f})  fall {s['deepest_fall']['typical']*100:4.0f}% (worst {s['deepest_fall']['worst_phase']*100:4.0f})  deposits {s['deposits_vs_stocks']['typical']*100:+5.0f}% (worst {s['deposits_vs_stocks']['worst_phase']*100:+5.0f})  5y-win {s['five_year_win_rate']['typical']}")
    print("== eras"); 
    for e, d in eras.items():
        print(" ", e); [print(f"   {k:42s} yr {s['per_year']*100:5.1f}%  fall {s['deepest_fall']*100:4.0f}%  worst day {s['worst_day']*100:4.0f}%") for k, s in sorted(d.items())]
if __name__ == "__main__": main()
