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
        tk = (f["on"] if signal_on else f["off"]) if isinstance(f, dict) else f
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


def steps(p, signal_on):
    out = ["Set the pie to: " + ", ".join("%s %d%%" % kv for kv in sorted(p["pie_weights"].items(), key=lambda x: -x[1])) + "."]
    if p["deposit_goes_to"]:
        out.append("Deposit: " + ", ".join("$%.0f to %s" % (v, k) for k, v in sorted(p["deposit_goes_to"].items(), key=lambda x: -x[1])) + " (the broker does this automatically if the pie weights are set).")
    if p["rebalance_needed"]:
        sells = ["sell $%.0f of %s" % (-v, k) for k, v in p["rebalance_trades"].items() if v < 0]
        buys = ["buy $%.0f of %s" % (v, k) for k, v in p["rebalance_trades"].items() if v > 0]
        out.append("Rebalance (" + p["why"] + "): " + "; ".join(sells + buys) + ".")
    else:
        out.append("No rebalance needed.")
    out.append("Trend signal is %s." % ("on: the stock block stays invested" if signal_on else "off: the stock block sits in the cash fund until the signal turns on"))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--holdings"); ap.add_argument("--deposit", type=float, default=0.0)
    ap.add_argument("--signal", choices=["on", "off"], required=True)
    ap.add_argument("--mix", default="software_mix"); ap.add_argument("--config", default="engine/config.json")
    a = ap.parse_args(argv)
    core = json.load(open(a.config))["core"]
    pos = json.load(open(a.holdings))["positions"] if a.holdings else {}
    on = a.signal == "on"
    p = plan(pos, a.deposit, targets(core[a.mix], core["funds"], on), core.get("rebalance_band", 0.05))
    p["steps"] = steps(p, on)
    print(json.dumps(p, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
