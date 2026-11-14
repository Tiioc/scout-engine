#!/usr/bin/env python3
"""Small-value dose test, pre-registered in research/CORE-PREREGISTRATION-2026-11-14-addendum-dose.md.
Usage: python3 scripts/dose_test.py --data /home/claude/scout-data [--boot 2000]"""
import argparse, json, sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
import portfolio_lab as L

C = {"C1": {"us": 1}, "C4": {"us": .9, "sv": .1}, "C8": {"us": .8, "sv": .2}, "C9": {"us": .7, "sv": .3}}

def rebase(d):  # bootstrap/summarize compare against key "C1"; to compare against C4, rename
    return {("C1" if k == "C4" else ("REF100" if k == "C1" else k)): v for k, v in d.items()}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--boot", type=int, default=2000)
    a = ap.parse_args(); D = a.data; S = L.load(D); R = {}
    cb = rebase(C)  # C4 is base "C1"
    def hist(start=None, end=None, S_=S):
        df = L.frame(S_, ["us", "sv"])
        if start: df = df[df.index >= start]
        if end: df = df[df.index <= end]
        return L.summarize({k: L.mix(df, w) for k, w in cb.items()}, horizons=(120, 240)), (str(df.index[0].date()), str(df.index[-1].date()))
    R["T1_1927_2026"], R["T1_span"] = hist("1927-01-01")
    R["T2a_1927_1976"], _ = hist("1927-01-01", "1976-12-31")
    R["T2b_1977_2026"], _ = hist("1977-01-01")
    R["T3_1990_2026"], _ = hist("1990-07-01")
    R["T3x_2011_2026"], _ = hist("2011-01-01")
    T4 = {}
    for name, fac, six in (("Developed ex US", "Developed_ex_US_3_Factors.csv", "Developed_ex_US_6_Portfolios_ME_BE-ME.csv"),
                           ("Europe", "ff/Europe_3_Factors.csv", "Europe_6_Portfolios_ME_BE-ME.csv"),
                           ("Japan", "ff/Japan_3_Factors.csv", "Japan_6_Portfolios_ME_BE-ME.csv")):
        f = L.ff(f"{D}/{fac}"); sx = L.ff(f"{D}/{six}")
        df = pd.DataFrame({"us": f[1] + f[4], "sv": sx[3]}).dropna()
        T4[name] = L.summarize({k: L.mix(df, w) for k, w in cb.items()}, horizons=(120,))
    R["T4"] = T4
    crises = {"1929-32": ("1929-08-31", "1932-12-31"), "1937-38": ("1937-02-28", "1938-12-31"), "1973-74": ("1972-12-31", "1974-12-31"), "1987": ("1987-08-31", "1987-12-31"),
              "2000-02": ("2000-03-31", "2002-12-31"), "2007-09": ("2007-10-31", "2009-06-30"), "2020": ("2020-01-31", "2020-06-30"), "2022": ("2021-12-31", "2022-12-31")}
    df = L.frame(S, ["us", "sv"])
    R["T6"] = {n: {k: round(L.dd(L.mix(df[(df.index >= s0) & (df.index <= s1)], w))[0], 3) for k, w in C.items()} for n, (s0, s1) in crises.items()}
    usb = L.frame(S, ["us", "sv", "cash"]); usb = usb[usb.index >= "1927-01-01"]
    R["T7"] = L.bootstrap(usb, cb, n=a.boot)
    gap = float(np.log1p(usb["us"]).mean() * 12) - np.log(1.06)
    prem = float(np.log1p(usb["sv"]).mean() * 12 - np.log1p(usb["us"]).mean() * 12)
    def lowered(cut):
        X = usb.copy(); X["us"] = (1 + X["us"]) * np.exp(-gap / 12) - 1
        X["sv"] = (1 + X["sv"]) * np.exp(-(gap + cut * prem) / 12) - 1
        X["cash"] = X["cash"] - X["cash"].mean() + .04 / 12; return X
    R["T8"] = L.bootstrap(lowered(0), cb, n=a.boot)
    R["T8s_half_premium"] = L.bootstrap(lowered(.5), cb, n=a.boot)
    R["T8s_zero_premium"] = L.bootstrap(lowered(1), cb, n=a.boot)
    R["note"] = "All comparisons are against C4 (shown as C1 in raw output; REF100 = 100%% VTI). Historical small-value premium over the market, 1927-2026: %.2f%%/yr (log). T8 lowers both by %.2f%%/yr." % (prem * 100, gap * 100)
    json.dump(R, open("research/data/dose-test-2026-11-14.json", "w"), indent=1, default=str)
    pc = lambda x: "%+6.1f%%" % (100 * x)
    print(R["note"])
    for t in ("T1_1927_2026", "T2a_1927_1976", "T2b_1977_2026", "T3_1990_2026", "T3x_2011_2026"):
        print("\n" + t); [print("  %-6s %5.1f%%/yr fall %4.0f%% deposits vs C4 %s 20y behind C4 %s" % (k, 100*s["per_year"], 100*s["deepest_fall"], pc(s["deposits_vs_C1"]), s.get("20y_chance_behind_C1", s.get("10y_chance_behind_C1")))) for k, s in R[t].items()]
    print("\nT4"); [print(" ", m, "  ".join("%s %s" % (k, pc(s["deposits_vs_C1"])) for k, s in v.items())) for m, v in T4.items()]
    print("\nT6"); [print("  %-8s" % n, "  ".join("%s %4.0f%%" % (k, 100*x) for k, x in v.items())) for n, v in R["T6"].items()]
    for t in ("T7", "T8", "T8s_half_premium", "T8s_zero_premium"):
        print("\n" + t); [print("  %-6s median vs C4 %s behind C4 %4.2f ending/deposits %5.2f p10 vs C4 %s fall worst5%% %4.0f%%" % (k, pc(s["median_vs_C1"]), s["chance_behind_C1"], s["median_ending_per_dollar_deposited"], pc(s["p10_vs_C1_p10"]), 100*s["worst_5pct_deepest_fall"])) for k, s in R[t].items()]
main()
