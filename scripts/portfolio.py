#!/usr/bin/env python3
"""Portfolio manager for the core: turns the target mix, the trend signal and current
holdings into the exact changes to make at the broker. Advice only; it places nothing.

Holdings file (private, in profile/): {"as_of": "YYYY-MM-DD", "positions": {"AVUV": 1200.0, ...}}
Usage: python3 scripts/portfolio.py --holdings profile/holdings.json --deposit 1500 --signal on
       python3 scripts/portfolio.py --deposit 1500 --signal on        (no holdings yet)
"""
import argparse, json, sys


def targets(mix, funds, signal_on):
    """Block weights -> ticker weights. A trend block holds its 'on' fund or its 'off' fund."""
    t = {}
    for block, w in mix.items():
        f = funds[block]
        if isinstance(f, dict):
            on = signal_on.get(f.get("signal", f["on"]), signal_on.get("default", True)) if isinstance(signal_on, dict) else signal_on
            tk = f["on"] if on else f["off"]
        else:
            tk = f
        t[tk] = t.get(tk, 0.0) + w
    s = sum(t.values())
    return {k: v / s for k, v in t.items()}


def pie(tw):
    """Whole-number slice weights that add to 100, as a broker pie needs."""
    raw = {k: v * 100 for k, v in tw.items()}
    out = {k: int(v) for k, v in raw.items()}
    for k in sorted(raw, key=lambda k: raw[k] - out[k], reverse=True)[: 100 - sum(out.values())]:
        out[k] += 1
    return out


def plan(positions, deposit, tw, band=0.05):
    pos = {k: float(v) for k, v in positions.items() if float(v) > 0}
    total = sum(pos.values()) + deposit
    if total <= 0: raise ValueError("nothing to invest")
    goal = {k: total * w for k, w in tw.items()}
    stray = {k: v for k, v in pos.items() if k not in tw}
    # 1) new money goes to whatever is furthest below target
    buys = {}; left = deposit
    gaps = {k: max(0.0, goal[k] - pos.get(k, 0.0)) for k in tw}
    gsum = sum(gaps.values())
    if left > 0 and gsum > 0:
        for k, g in gaps.items():
            buys[k] = min(g, left * g / gsum)
        left -= sum(buys.values())
    after = {k: pos.get(k, 0.0) + buys.get(k, 0.0) for k in set(pos) | set(tw)}
    drift = {k: after.get(k, 0.0) / total - tw.get(k, 0.0) for k in after}
    need = bool(stray) or any(abs(d) > band for d in drift.values())
    trades = {k: round(goal.get(k, 0.0) - after.get(k, 0.0), 2) for k in after} if need else {}
    trades = {k: v for k, v in trades.items() if abs(v) >= 1}
    return {"total_after_deposit": round(total, 2), "pie_weights": pie(tw),
            "deposit_goes_to": {k: round(v, 2) for k, v in buys.items() if v >= 0.01},
            "drift_after_deposit": {k: round(v, 4) for k, v in drift.items()},
            "rebalance_needed": need,
            "rebalance_trades": trades,
            "why": ("holding a fund that is not in the target mix" if stray else
                    "a slice is more than %d points off target" % round(band * 100)) if need else "all slices within the band"}


def stage(total, yearly_deposits, stages):
    if not yearly_deposits or yearly_deposits <= 0: return stages[0]["name"]
    m = total / yearly_deposits
    for st in stages:
        lim = st.get("below_multiple_of_yearly_deposits")
        if lim is None or m < lim: return st["name"]
    return stages[-1]["name"]


def risk(total, hist, yearly_deposits=None, peak=None):
    r = {"worst_fall_in_history": "%d%%, which today would be $%.0f" % (hist["worst_fall"] * 100, total * hist["worst_fall"]),
         "worst_year_in_history": "%d%%, $%.0f" % (hist["worst_year"] * 100, total * hist["worst_year"]),
         "worst_single_day": "%d%%, $%.0f" % (hist["worst_single_day"] * 100, total * hist["worst_single_day"]),
         "share_of_years_that_lost_money": "%d%%" % (hist["losing_years_share"] * 100),
         "can_it_go_to_zero": "only if every fund in it does; no borrowed money is used"}
    if yearly_deposits:
        r["worst_fall_in_years_of_deposits"] = round(total * hist["worst_fall"] / yearly_deposits, 1)
    if peak and peak > 0:
        r["below_its_high_by"] = "%.0f%%" % (max(0.0, 1 - total / peak) * 100)
    return r


def steps(p, signal_on):
    if isinstance(signal_on, dict):
        named = {k: v for k, v in signal_on.items() if k != "default"}
        desc = ", ".join("%s %s" % (k, "on" if v else "off") for k, v in sorted(named.items())) or ("on" if signal_on.get("default") else "off")
        tail = ["Exit signals: %s. A block whose signal is off sits in the cash fund until it turns on. [Rule R2]" % desc]
        return steps(p, None)[:-1] + tail
    out = ["Set the pie to: " + ", ".join("%s %d%%" % kv for kv in sorted(p["pie_weights"].items(), key=lambda x: -x[1])) + "."]
    if p["deposit_goes_to"]:
        out.append("Deposit: " + ", ".join("$%.0f to %s" % (v, k) for k, v in sorted(p["deposit_goes_to"].items(), key=lambda x: -x[1])) + " (the broker does this automatically if the pie weights are set). [Rule R1]")
    if p["rebalance_needed"]:
        sells = ["sell $%.0f of %s" % (-v, k) for k, v in p["rebalance_trades"].items() if v < 0]
        buys = ["buy $%.0f of %s" % (v, k) for k, v in p["rebalance_trades"].items() if v > 0]
        out.append("Rebalance (" + p["why"] + "): " + "; ".join(sells + buys) + ". [Rule %s]" % ("R2" if "not in the target mix" in p["why"] else "R3"))
    else:
        out.append("No rebalance needed.")
    out.append("Trend signal is %s. [Rule R2]" % ("on: the stock block stays invested" if signal_on else "off: the stock block sits in the cash fund until the signal turns on"))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--holdings"); ap.add_argument("--deposit", type=float, default=0.0)
    ap.add_argument("--signal", choices=["on", "off"], default="on", help="default for every exit")
    ap.add_argument("--signals", default="", help="per fund, e.g. MTUM=on,AVUV=off,SP500=on")
    ap.add_argument("--yearly-deposits", type=float, default=None); ap.add_argument("--peak", type=float, default=None)
    ap.add_argument("--mix", default="software_mix"); ap.add_argument("--config", default="engine/config.json")
    a = ap.parse_args(argv)
    core = json.load(open(a.config))["core"]
    pos = json.load(open(a.holdings))["positions"] if a.holdings else {}
    on = {"default": a.signal == "on"}
    for kv in filter(None, a.signals.split(",")):
        k, v = kv.split("="); on[k.strip()] = v.strip() == "on"
    p = plan(pos, a.deposit, targets(core[a.mix], core["funds"], on), core.get("rebalance_band", 0.05))
    yd = a.yearly_deposits or (a.deposit * 12 if a.deposit else None)
    p["stage"] = stage(p["total_after_deposit"], yd, core.get("stages", [{"name": "growth"}]))
    p["risk"] = risk(p["total_after_deposit"], core["history"][a.mix], yd, a.peak)
    p["steps"] = steps(p, on)
    print(json.dumps(p, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
