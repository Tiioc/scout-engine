#!/usr/bin/env python3
"""Sensitivity run requested by both Red Teams on 2026-11-14 (NOT part of the pre-registered decision; reported beside it).
Bootstrap of 1990-2026 joint monthly data, 25 years of monthly deposits, bills at 4%.
US stocks lowered so they compound near 6% nominal (CAPE 35-41, about 3% real). International set by its own valuation:
CAPE about 20 implies about 5% real, about 7.7% nominal. Small-value premium over the US market scaled to full, half, half minus 1% a year (real-fund shortfall) or zero.
Usage: python3 scripts/portfolio_lab_sensitivity.py --data /home/claude/scout-data [--boot 1500]"""
import argparse, importlib.util, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location("lab", os.path.join(HERE, "portfolio_lab.py")); lab = importlib.util.module_from_spec(sp); sp.loader.exec_module(lab)
CANDS = {c: lab.CANDS[c] for c in ("C1", "C2", "C3", "C4", "C5")}

def geo(x): return float(np.log1p(x).mean() * 12)

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--boot", type=int, default=1500); a = ap.parse_args(argv)
    S = lab.load(a.data); df = lab.frame(S, ["us", "sv", "intl", "cash"]); df = df[df.index >= "1990-07-01"].copy()
    us_g, intl_g, sv_g = geo(df["us"]), geo(df["intl"]), geo(df["sv"])
    print("1990-2026 log returns a year: US %.2f%%, international %.2f%%, small value %.2f%%" % (100 * us_g, 100 * intl_g, 100 * sv_g))
    us_target, intl_targets = np.log(1.06), {"intl at its own CAPE (about 7.7% nominal)": np.log(1.077), "intl same as US (6%)": np.log(1.06), "intl cut half as much as US (T8b)": intl_g - (us_g - np.log(1.06)) / 2}
    prem_hist = sv_g - us_g
    rows = []
    for iname, itarget in intl_targets.items():
        for pname, prem in (("full premium", prem_hist), ("half premium", prem_hist / 2), ("half premium minus 1%", prem_hist / 2 - .01), ("zero premium", 0.0)):
            X = df.copy()
            X["us"] = (1 + df["us"]) * np.exp((us_target - us_g) / 12) - 1
            X["sv"] = (1 + df["sv"]) * np.exp((us_target + prem - sv_g) / 12) - 1
            X["intl"] = (1 + df["intl"]) * np.exp((itarget - intl_g) / 12) - 1
            X["cash"] = df["cash"] - df["cash"].mean() + .04 / 12
            r = lab.bootstrap(X, CANDS, n=a.boot)
            print("\n%s | %s" % (iname, pname))
            for c, s in r.items():
                print("  %-3s median vs C1 %+6.1f%%  chance behind %4.2f  p10 vs C1 p10 %+6.1f%%  worst5%% fall %4.0f%%" % (c, 100 * s["median_vs_C1"], s["chance_behind_C1"], 100 * s["p10_vs_C1_p10"], 100 * s["worst_5pct_deepest_fall"]))
if __name__ == "__main__": main()
