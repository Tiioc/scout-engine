#!/usr/bin/env python3
"""Whole-life test: a saver who starts at the growth level and steps down to calmer mixes as
the account grows. Run on every stretch of real market history and on reshuffled and
worst-order histories, for 10 to 50 years.

The plan is judged on four things: the typical result, the bad-luck result, the worst loss
in the final ten years (when the account is largest), and the worst result of all.

Usage: python3 scripts/lifecycle.py --data /path/to/data [--out file.json]
"""
import argparse, itertools, json, sys
import numpy as np
import levels as Lv

HORIZONS = (10, 20, 30, 40, 50)


def flat(j): return 1500.0 * 1.02 ** (j // 12)                 # today's dollars, pay growth 2% above inflation
def stepup(j):
    y = j // 12
    return (1500.0 if y < 3 else 3000.0 if y < 6 else 5000.0) * 1.02 ** y


def level_returns(M, mixes):
    return np.stack([M @ np.array([m.get(a, 0.0) for a in Lv.A]) for m in mixes])


def simulate(R, infl, idx, policy, profile=flat):
    """R: (levels, T) monthly returns, calmest level last. idx: (paths, months) row numbers.
    policy: {"kind": "size", "m1":, "m2":, "ratchet": bool} | {"kind": "time", "f1":, "f2":} | {"kind": "fixed", "level": i}"""
    n, months = idx.shape
    bal = np.zeros(n); price = np.ones(n); stage = np.zeros(n, dtype=int)
    unit = np.ones(n); peak = np.ones(n); dd = np.zeros(n); late_peak = np.ones(n); late_dd = np.zeros(n)
    rows = np.arange(n); time_in = np.zeros((R.shape[0], n))
    if policy["kind"] == "fixed": stage[:] = policy["level"]
    for j in range(months):
        c = profile(j) * price
        if j % 12 == 0 and j > 0 and policy["kind"] != "fixed":
            if policy["kind"] == "size":
                m = bal / (12 * c)
                new = np.where(m < policy["m1"], 0, np.where(m < policy["m2"], 1, 2))
                stage = np.maximum(stage, new) if policy.get("ratchet", True) else new
            else:
                f = j / months; stage[:] = 0 if f < policy["f1"] else 1 if f < policy["f2"] else 2
        r = R[stage, idx[:, j]]
        bal = (bal + c) * (1 + r); price = price * (1 + infl[idx[:, j]])
        unit = unit * (1 + r); peak = np.maximum(peak, unit); dd = np.minimum(dd, unit / peak - 1)
        if j == months - 120: late_peak = unit.copy()
        if j >= months - 120:
            late_peak = np.maximum(late_peak, unit); late_dd = np.minimum(late_dd, unit / late_peak - 1)
        time_in[stage, rows] += 1
    return {"end": bal / price, "worst_fall": dd, "late_fall": late_dd, "share_of_time": time_in.sum(axis=1) / (n * months)}


def summary(s):
    e = s["end"]
    return {"typical": round(float(np.median(e))), "bad_luck": round(float(np.percentile(e, 10))), "worst": round(float(e.min())),
            "good_luck": round(float(np.percentile(e, 90))), "chance_of_1m": round(float(np.mean(e >= 1e6)), 3),
            "worst_fall_ever": round(float(s["worst_fall"].min()), 3), "typical_worst_fall": round(float(np.median(s["worst_fall"])), 3),
            "worst_fall_in_last_10_years": round(float(s["late_fall"].min()), 3),
            "typical_fall_in_last_10_years": round(float(np.median(s["late_fall"])), 3),
            "time_at_each_level": [round(float(x), 2) for x in s["share_of_time"]]}


def windows(T, months): return np.arange(T - months + 1)[:, None] + np.arange(months)[None, :]


def reshuffled(T, months, n=2000, block=24, seed=3):
    rng = np.random.default_rng(seed); k = months // block + 1
    st = rng.integers(0, T, size=(n, k))
    return ((st[:, :, None] + np.arange(block)[None, None, :]) % T).reshape(n, -1)[:, :months]


def crash_at(idx, crash_rows, where):
    out = idx.copy(); k = len(crash_rows)
    if where == "end": out[:, -k:] = crash_rows
    else: out[:, :k] = crash_rows
    return out


POLICIES = {
    "the plan: step down as the account grows": {"kind": "size", "m1": 20, "m2": 60, "ratchet": True},
    "step down by the calendar (thirds)": {"kind": "time", "f1": 1 / 3, "f2": 2 / 3},
    "growth level the whole time": {"kind": "fixed", "level": 0},
    "middle level the whole time": {"kind": "fixed", "level": 1},
    "calm level the whole time": {"kind": "fixed", "level": 2},
}


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--out")
    ap.add_argument("--config", default="engine/config.json"); ap.add_argument("--levels", default="50,35,25")
    a = ap.parse_args(argv)
    cfg = json.load(open(a.config))["core"]["risk_levels"]; names = a.levels.split(",")
    M, infl, dates = Lv.panel(a.data, with_dates=True); T = len(M)
    R = level_returns(M, [cfg[k]["mix"] for k in names])
    S = M[:, Lv.A.index("stocks")][None, :]; B6040 = (0.6 * M[:, Lv.A.index("stocks")] + 0.4 * M[:, Lv.A.index("bonds")])[None, :]
    crash = np.where((dates >= 192909) & (dates <= 193206))[0]
    rep = {"levels_used": names, "months_of_history": T, "real_history": {}, "reshuffled_history": {}, "crash_in_final_years": {}, "crash_in_first_years": {}, "threshold_search": {}}
    for yrs in HORIZONS:
        months = yrs * 12; W = windows(T, months); key = "%d years" % yrs
        for prof_name, prof in (("1500 a month", flat), ("stepping up to 5000", stepup)):
            block = {n: summary(simulate(R, infl, W, p, prof)) for n, p in POLICIES.items()}
            block["plain stocks"] = summary(simulate(S, infl, W, {"kind": "fixed", "level": 0}, prof))
            block["60% stocks 40% bonds"] = summary(simulate(B6040, infl, W, {"kind": "fixed", "level": 0}, prof))
            rep["real_history"].setdefault(key, {})[prof_name] = block
        Bs = reshuffled(T, months)
        rep["reshuffled_history"][key] = {n: summary(simulate(R, infl, Bs, POLICIES[n])) for n in list(POLICIES)[:3]}
        rep["reshuffled_history"][key]["plain stocks"] = summary(simulate(S, infl, Bs, {"kind": "fixed", "level": 0}))
        for where, slot in (("end", "crash_in_final_years"), ("start", "crash_in_first_years")):
            C = crash_at(W, crash, where)
            rep[slot][key] = {n: summary(simulate(R, infl, C, POLICIES[n])) for n in list(POLICIES)[:3]}
            rep[slot][key]["plain stocks"] = summary(simulate(S, infl, C, {"kind": "fixed", "level": 0}))
    # let the software choose the step-down points: best bad-luck result at 30 years with the final-decade fall capped
    W = windows(T, 360); best = []
    for m1, m2, ratchet in itertools.product((5, 10, 15, 20, 30), (15, 25, 40, 60, 100), (True, False)):
        if m2 <= m1: continue
        s = summary(simulate(R, infl, W, {"kind": "size", "m1": m1, "m2": m2, "ratchet": ratchet}))
        best.append({"m1": m1, "m2": m2, "ratchet": ratchet, **{k: s[k] for k in ("typical", "bad_luck", "worst", "worst_fall_in_last_10_years")}})
    rep["threshold_search"]["all"] = best
    ok = [b for b in best if b["worst_fall_in_last_10_years"] >= -0.30]
    rep["threshold_search"]["best_with_final_decade_fall_under_30pct"] = max(ok, key=lambda b: b["bad_luck"]) if ok else None
    rep["threshold_search"]["best_with_final_decade_fall_under_25pct"] = max([b for b in best if b["worst_fall_in_last_10_years"] >= -0.25] or [None], key=lambda b: b["bad_luck"] if b else 0)
    txt = json.dumps(rep, indent=1)
    if a.out: open(a.out, "w").write(txt)
    print(txt); return 0


if __name__ == "__main__":
    sys.exit(main())
