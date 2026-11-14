#!/usr/bin/env python3
"""Pre-registered core portfolio tests (research/CORE-PREREGISTRATION-2026-11-14.md).
Usage: python3 scripts/portfolio_lab.py --data /home/claude/scout-data [--out research/data/portfolio-lab-2026-11-14.json]
Monthly framework; borrowed-exposure slices are built from daily data with the daily 200-day rule (2% band, trade next day)."""
import argparse, json, os, numpy as np, pandas as pd

FEES = {"us": .0003, "intl": .0005, "sv": .0025, "lg": .0015, "bond": .0015, "x2exit": 0, "x2": 0, "cash": .0009}
CANDS = {"C1": {"us": 1}, "C2": {"us": .6, "intl": .4}, "C3": {"us": .8, "intl": .2}, "C4": {"us": .9, "sv": .1},
         "C5": {"us": .7, "sv": .15, "intl": .15}, "C6": {"us": .8, "lg": .2}, "C7": {"us": .9, "bond": .1},
         "L1": {"us": .85, "x2exit": .15}, "L2": {"us": .5, "x2exit": .5}, "L3": {"us": .5, "x2": .5}}

# ---------- loaders ----------
def ff(path, first_table_only=True, daily=False):
    rows, started = [], False
    for line in open(path, encoding="latin-1"):
        p = [x.strip() for x in line.split(",")]
        k = p[0]
        ok = k.isdigit() and len(k) == (8 if daily else 6)
        if ok: rows.append(p); started = True
        elif started and first_table_only and k and not k.isdigit(): break
    df = pd.DataFrame(rows); idx = pd.to_datetime(df[0], format="%Y%m%d" if daily else "%Y%m")
    if not daily: idx = idx + pd.offsets.MonthEnd(0)
    out = df.iloc[:, 1:].astype(float).replace([-99.99, -999], np.nan) / 100; out.index = idx; return out

def bond_returns(gs10_csv):
    y = pd.read_csv(gs10_csv, parse_dates=[0], index_col=0).iloc[:, 0].astype(float) / 100
    y.index = y.index + pd.offsets.MonthEnd(0)
    def price(c, yld, n=119):           # par bond paying monthly-equivalent coupons, n months left
        i = yld / 12; return (c / 12) * (1 - (1 + i) ** -n) / i + (1 + i) ** -n
    r = [price(y.iloc[k - 1], y.iloc[k]) - 1 + y.iloc[k - 1] / 12 for k in range(1, len(y))]
    return pd.Series(r, index=y.index[1:])

def gated_2x(mkt_d, rf_d, spread=.015, fee=.0089, band=.02, days=200, gate=True):
    """Daily 2x fund (daily reset): 2*mkt - (rf+spread) - fee. Gate: held only above 200-day average, decided at close t, traded at close t+1."""
    lev = 2 * mkt_d - (rf_d + spread / 252) - fee / 252
    if not gate: return lev
    px = (1 + mkt_d).cumprod(); ma = px.rolling(days).mean().values; p = px.values; on = np.ones(len(px), bool); st = True
    for i in range(len(px)):
        if not np.isnan(ma[i]):
            if st and p[i] < ma[i] * (1 - band): st = False
            elif not st and p[i] > ma[i] * (1 + band): st = True
        on[i] = st
    held = pd.Series(on, index=px.index).shift(2).fillna(True).astype(bool)
    sw = held.astype(int).diff().abs().fillna(0) * 0.0005
    return pd.Series(np.where(held, lev, rf_d), index=lev.index) - sw

def to_month(d):
    m = (1 + d).groupby([d.index.year, d.index.month]).prod() - 1
    m.index = pd.to_datetime([f"{y}-{mo:02d}-01" for y, mo in m.index]) + pd.offsets.MonthEnd(0); return m

def load(D):
    S = {}
    f = ff(f"{D}/F-F_Research_Data_Factors.csv"); S["us"] = f[1] + f[4]; S["cash"] = f[4]
    six = ff(f"{D}/6_Portfolios_2x3.csv"); S["sv"] = six[3]; S["lg"] = six[4]
    fd = ff(f"{D}/F-F_Research_Data_Factors_daily.csv", daily=True); mkt_d, rf_d = fd[1] + fd[4], fd[4]
    S["_mkt_d"], S["_rf_d"] = mkt_d, rf_d
    S["x2exit"] = to_month(gated_2x(mkt_d, rf_d)); S["x2"] = to_month(gated_2x(mkt_d, rf_d, gate=False))
    di = ff(f"{D}/Developed_ex_US_3_Factors.csv"); S["intl"] = di[1] + di[4]
    S["bond"] = bond_returns(f"{D}/GS10.csv")
    return pd.DataFrame(S).drop(columns=["_mkt_d", "_rf_d"], errors="ignore") if False else S

# ---------- engine ----------
def frame(S, keys):
    return pd.DataFrame({k: S[k] for k in keys}).dropna()

def mix(df, w, band=.05):
    keys = list(w); W = np.array([w[k] for k in keys], float); W /= W.sum(); fee = np.array([FEES[k] for k in keys]) / 12
    cur = W.copy(); X = df[keys].values; out = np.empty(len(df))
    for i in range(len(df)):
        if np.abs(cur - W).max() > band: cur = W.copy()
        r = float((cur * (X[i] - fee)).sum()); out[i] = r; cur = cur * (1 + X[i] - fee) / (1 + r)
    return pd.Series(out, index=df.index)

def dca(r):
    v = 0.0
    for x in r: v = (v + 1) * (1 + x)
    return v

def dd(r):
    v = (1 + r).cumprod(); peak = v.cummax(); d = v / peak - 1; under = (d < 0).astype(int)
    longest = cur = 0
    for u in under.values: cur = cur + 1 if u else 0; longest = max(longest, cur)
    return float(d.min()), int(longest)

def summarize(rets, base="C1", horizons=(120, 240, 300)):
    out = {}
    for n, r in rets.items():
        b = rets[base]; yrs = len(r) / 12; fall, under = dd(r)
        s = {"per_year": (1 + r).prod() ** (1 / yrs) - 1, "deepest_fall": fall, "longest_under_water_months": under,
             "worst_12_months": float(((1 + r).rolling(12).apply(np.prod, raw=True) - 1).min()),
             "deposits_vs_C1": dca(r) / dca(b) - 1}
        for h in horizons:
            if len(r) <= h: continue
            ratios = np.array([dca(r.iloc[i:i + h]) / dca(b.iloc[i:i + h]) for i in range(0, len(r) - h, 3)])
            s[f"{h // 12}y_median_vs_C1"] = float(np.median(ratios) - 1); s[f"{h // 12}y_chance_behind_C1"] = float((ratios < 1).mean())
            s[f"{h // 12}y_worst_vs_C1"] = float(ratios.min() - 1)
        out[n] = {k: round(v, 4) if isinstance(v, float) else v for k, v in s.items()}
    return out

def bootstrap(df, cands, months=300, block=12, n=4000, seed=7, shift=None, rf_level=None):
    rng = np.random.default_rng(seed); X = df.copy()
    if shift is not None:
        for k, a in shift.items():
            if k in X: X[k] = (1 + X[k]) * np.exp(-a / 12) - 1
    if rf_level is not None and "cash" in X:
        adj = rf_level / 12 - X["cash"].mean(); X["cash"] = X["cash"] + adj
    T = len(X); res = {c: [] for c in cands}; falls = {c: [] for c in cands}
    for _ in range(n):
        starts = rng.integers(0, T - block, months // block + 1); idx = np.concatenate([np.arange(s, s + block) for s in starts])[:months]
        sample = X.iloc[idx].reset_index(drop=True)
        for c, w in cands.items():
            r = mix(sample, w); res[c].append(dca(r)); falls[c].append(dd(r)[0])
    base = np.array(res["C1"]); tot = months
    out = {}
    for c in cands:
        a = np.array(res[c]); ratio = a / base
        out[c] = {"median_vs_C1": round(float(np.median(ratio) - 1), 4), "chance_behind_C1": round(float((ratio < 1).mean()), 3),
                  "median_ending_per_dollar_deposited": round(float(np.median(a) / tot), 3), "p10_ending_per_dollar": round(float(np.percentile(a, 10) / tot), 3),
                  "p10_vs_C1_p10": round(float(np.percentile(a, 10) / np.percentile(base, 10) - 1), 4),
                  "chance_end_below_deposits": round(float((a < tot).mean()), 3), "median_deepest_fall": round(float(np.median(falls[c])), 3),
                  "worst_5pct_deepest_fall": round(float(np.percentile(falls[c], 5)), 3)}
    return out

# ---------- tests ----------
def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--out"); ap.add_argument("--boot", type=int, default=3000)
    a = ap.parse_args(argv); D = a.data; S = load(D); R = {}
    def run(keys_needed, start=None, end=None, cands=CANDS):
        sel = {c: w for c, w in cands.items() if set(w) <= set(keys_needed)}
        df = frame(S, sorted(set().union(*[set(w) for w in sel.values()]) | {"us"}))
        if start: df = df[df.index >= start]
        if end: df = df[df.index <= end]
        return summarize({c: mix(df, w) for c, w in sel.items()}), (str(df.index[0].date()), str(df.index[-1].date()))
    usk = ["us", "sv", "lg", "x2exit", "x2", "cash"]
    R["T1_us_1927_2026"], span = run(usk, "1927-01-01"); R["T1_span"] = span
    R["T1b_us_with_bonds_1953_2026"], R["T1b_span"] = run(usk + ["bond"], "1953-05-01")
    R["T2_first_half_1927_1976"], _ = run(usk, "1927-01-01", "1976-12-31")
    R["T2_second_half_1977_2026"], _ = run(usk, "1977-01-01")
    R["T3_with_international_1990_2026"], R["T3_span"] = run(usk + ["intl", "bond"], "1990-07-01")
    R["T3b_1990_2009"], _ = run(usk + ["intl", "bond"], "1990-07-01", "2009-12-31")
    R["T3c_2010_2026"], _ = run(usk + ["intl", "bond"], "2010-01-01")
    # T4: rules outside the US
    T4 = {}
    for name, fac, six, daily in (("Developed ex US", "Developed_ex_US_3_Factors.csv", "Developed_ex_US_6_Portfolios_ME_BE-ME.csv", "ff/Developed_ex_US_3_Factors_Daily.csv"),
                                  ("Europe", "ff/Europe_3_Factors.csv", "Europe_6_Portfolios_ME_BE-ME.csv", "ff/Europe_3_Factors_Daily.csv"),
                                  ("Japan", "ff/Japan_3_Factors.csv", "Japan_6_Portfolios_ME_BE-ME.csv", "ff/Japan_3_Factors_Daily.csv")):
        f = ff(f"{D}/{fac}"); sx = ff(f"{D}/{six}"); fd = ff(f"{D}/{daily}", daily=True)
        mk_d = fd[1] + fd[4]; rf_d = fd[4]
        loc = {"us": f[1] + f[4], "sv": sx[3], "lg": sx[4], "x2exit": to_month(gated_2x(mk_d, rf_d)), "x2": to_month(gated_2x(mk_d, rf_d, gate=False)), "cash": f[4]}
        df = pd.DataFrame(loc).dropna(); sel = {c: CANDS[c] for c in ("C1", "C4", "C6", "L1", "L2", "L3")}
        T4[name] = {"span": (str(df.index[0].date()), str(df.index[-1].date())), "results": summarize({c: mix(df, w) for c, w in sel.items()})}
    R["T4_rules_outside_us"] = T4
    # T6: named crises (monthly, deepest fall inside the window)
    crises = {"1929-32": ("1929-08-31", "1932-12-31"), "1937-38": ("1937-02-28", "1938-12-31"), "1973-74": ("1972-12-31", "1974-12-31"), "1987": ("1987-08-31", "1987-12-31"),
              "2000-02": ("2000-03-31", "2002-12-31"), "2007-09": ("2007-10-31", "2009-06-30"), "2020": ("2020-01-31", "2020-06-30"), "2022": ("2021-12-31", "2022-12-31")}
    allk = frame(S, ["us", "sv", "lg", "x2exit", "x2", "cash", "intl", "bond"])
    T6 = {}
    for nm, (s0, s1) in crises.items():
        T6[nm] = {}
        for c, w in CANDS.items():
            if not set(w) <= set(S): continue
            df = frame(S, list(w))
            df = df[(df.index >= s0) & (df.index <= s1)]
            if len(df) < 2: continue
            T6[nm][c] = round(dd(mix(df, w))[0], 3)
    # 1987 single day
    fd = ff(f"{D}/F-F_Research_Data_Factors_daily.csv", daily=True); mk_d, rf_d = fd[1] + fd[4], fd[4]
    day = pd.Timestamp("1987-10-19"); g = gated_2x(mk_d, rf_d); x = gated_2x(mk_d, rf_d, gate=False)
    T6["1987-10-19 one day"] = {"C1": round(float(mk_d[day]), 3), "L1": round(float(.85 * mk_d[day] + .15 * g[day]), 3), "L2": round(float(.5 * mk_d[day] + .5 * g[day]), 3), "L3": round(float(.5 * mk_d[day] + .5 * x[day]), 3)}
    R["T6_crises_deepest_fall"] = T6
    # T7 / T8 / T9: bootstrap
    usb = frame(S, ["us", "sv", "lg", "x2exit", "x2", "cash"]); usb = usb[usb.index >= "1927-01-01"]
    uc = {c: w for c, w in CANDS.items() if set(w) <= set(usb.columns)}
    R["T7_bootstrap_us_1927_2026_25y"] = bootstrap(usb, uc, n=a.boot)
    # T8: lower stock returns to ~6% nominal (about 3% real) and set bills at 4%: subtract the gap from every equity series; rebuild the 2x slices on the lowered market.
    hist_geo = float(np.log1p(usb["us"]).mean() * 12); gap = hist_geo - np.log(1.06)
    low = S.copy(); f = fd.copy()
    mk_low = (1 + mk_d) * np.exp(-gap / 252) - 1; rf_adj = rf_d - rf_d.mean() + .04 / 252
    T8 = {}
    for spread in (.005, .015, .03):
        low = {"us": (1 + S["us"]) * np.exp(-gap / 12) - 1, "sv": (1 + S["sv"]) * np.exp(-gap / 12) - 1, "lg": (1 + S["lg"]) * np.exp(-gap / 12) - 1,
               "x2exit": to_month(gated_2x(mk_low, rf_adj, spread=spread)), "x2": to_month(gated_2x(mk_low, rf_adj, spread=spread, gate=False)),
               "cash": S["cash"] - S["cash"].mean() + .04 / 12}
        lb = pd.DataFrame(low).dropna(); lb = lb[lb.index >= "1927-01-01"]
        T8[f"borrow_spread_{spread}"] = bootstrap(lb, uc, n=a.boot)
    R["T8_today_conditions_us_25y"] = T8; R["T8_note"] = "US stocks, small value and large growth each lowered by %.2f%% a year (log), so US stocks compound near 6%% nominal (about 3%% real); bills set to average 4%%." % (gap * 100)
    # T3 bootstrap with international (1990-2026 joint sample), historical and lowered (US lowered as above; international lowered by half the US gap, a CAPE near 20)
    ib = frame(S, ["us", "sv", "lg", "x2exit", "x2", "cash", "intl", "bond"]); ib = ib[ib.index >= "1990-07-01"]
    R["T7b_bootstrap_1990_2026_25y_all"] = bootstrap(ib, CANDS, n=a.boot)
    ib2 = ib.copy()
    for k in ("us", "sv", "lg"): ib2[k] = (1 + ib2[k]) * np.exp(-gap / 12) - 1
    ib2["intl"] = (1 + ib2["intl"]) * np.exp(-gap / 2 / 12) - 1; ib2["cash"] = ib2["cash"] - ib2["cash"].mean() + .04 / 12
    lowd = {"x2exit": to_month(gated_2x(mk_low, rf_adj)), "x2": to_month(gated_2x(mk_low, rf_adj, gate=False))}
    for k, v in lowd.items(): ib2[k] = v.reindex(ib2.index)
    R["T8b_today_conditions_1990_2026_25y_all_intl_cut_half"] = bootstrap(ib2.dropna(), CANDS, n=a.boot)
    ib3 = ib2.copy(); ib3["intl"] = (1 + ib["intl"]) * np.exp(-gap / 12) - 1
    R["T8c_today_conditions_1990_2026_25y_all_intl_cut_same"] = bootstrap(ib3.dropna(), CANDS, n=a.boot)
    if a.out: json.dump(R, open(a.out, "w"), indent=1, default=str)
    show(R)

def show(R):
    pc = lambda x: "%+6.1f%%" % (100 * x)
    for t in [k for k in R if k.startswith(("T1_", "T1b", "T2", "T3"))]:
        if not isinstance(R[t], dict) or "C1" not in R[t]: continue
        print("\n" + t)
        for c, s in R[t].items():
            print("  %-3s %5.1f%%/yr  fall %4.0f%%  12m %4.0f%%  under %3d mo  deposits %s  10y med %s behind %s  20y med %s behind %s" % (c, 100 * s["per_year"], 100 * s["deepest_fall"], 100 * s["worst_12_months"], s["longest_under_water_months"], pc(s["deposits_vs_C1"]),
                  pc(s.get("10y_median_vs_C1", 0)), s.get("10y_chance_behind_C1", "-"), pc(s.get("20y_median_vs_C1", 0)), s.get("20y_chance_behind_C1", "-")))
    print("\nT4 rules outside the US")
    for m, v in R["T4_rules_outside_us"].items():
        print(" ", m, v["span"])
        for c, s in v["results"].items():
            print("    %-3s %5.1f%%/yr  fall %4.0f%%  deposits vs market %s  10y behind %s" % (c, 100 * s["per_year"], 100 * s["deepest_fall"], pc(s["deposits_vs_C1"]), s.get("10y_chance_behind_C1", "-")))
    print("\nT6 crises (deepest fall)")
    for k, v in R["T6_crises_deepest_fall"].items(): print("  %-18s" % k, "  ".join("%s %4.0f%%" % (c, 100 * x) for c, x in v.items()))
    for t in ("T7_bootstrap_us_1927_2026_25y", "T7b_bootstrap_1990_2026_25y_all", "T8b_today_conditions_1990_2026_25y_all_intl_cut_half", "T8c_today_conditions_1990_2026_25y_all_intl_cut_same"):
        print("\n" + t); [print("  %-3s median vs C1 %s  behind %4.2f  ending/deposits %5.2f  p10 %5.2f  p10 vs C1 %s  below deposits %4.2f  fall med %4.0f%% worst5%% %4.0f%%" % (c, pc(s["median_vs_C1"]), s["chance_behind_C1"], s["median_ending_per_dollar_deposited"], s["p10_ending_per_dollar"], pc(s["p10_vs_C1_p10"]), s["chance_end_below_deposits"], 100 * s["median_deepest_fall"], 100 * s["worst_5pct_deepest_fall"])) for c, s in R[t].items()]
    print("\nT8 today's conditions (US, 25y)", R["T8_note"])
    for sp, v in R["T8_today_conditions_us_25y"].items():
        print(" ", sp); [print("    %-3s median vs C1 %s  behind %4.2f  ending/deposits %5.2f  p10 vs C1 %s  below deposits %4.2f  fall worst5%% %4.0f%%" % (c, pc(s["median_vs_C1"]), s["chance_behind_C1"], s["median_ending_per_dollar_deposited"], pc(s["p10_vs_C1_p10"]), s["chance_end_below_deposits"], 100 * s["worst_5pct_deepest_fall"])) for c, s in v.items()]

if __name__ == "__main__": main()
