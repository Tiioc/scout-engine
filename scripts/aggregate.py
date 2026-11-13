#!/usr/bin/env python3
"""Combine sealed forecast samples into one probability.

Method: median in log-odds, optional extremizing, clip to a safe range.
Usage:
    python3 scripts/aggregate.py 0.22 0.30 0.25 [--market 0.40] [--config engine/config.json]
Prints JSON with the aggregate and any flags the Chair must act on.
"""
import argparse
import json
import math
import statistics
import sys

DEFAULTS = {
    "clip_low": 0.03,
    "clip_high": 0.97,
    "spread_flag": 0.20,
    "market_deviation_flag": 0.10,
    "extremize_factor": 1.0,
}


def logit(p):
    return math.log(p / (1.0 - p))


def inv_logit(x):
    return 1.0 / (1.0 + math.exp(-x))


def aggregate(samples, market=None, settings=None):
    cfg = dict(DEFAULTS)
    if settings:
        cfg.update({k: v for k, v in settings.items() if k in DEFAULTS})
    if not samples:
        raise ValueError("at least one sample is required")
    for p in samples:
        if not (0.0 < p < 1.0):
            raise ValueError("each sample must be strictly between 0 and 1, got %r" % p)

    lo, hi = cfg["clip_low"], cfg["clip_high"]
    clipped = [min(max(p, lo), hi) for p in samples]
    med = statistics.median(logit(p) for p in clipped)
    agg = inv_logit(med * cfg["extremize_factor"])
    agg = min(max(agg, lo), hi)

    spread = max(samples) - min(samples)
    flags = []
    if len(samples) < 3:
        flags.append("FEW_SAMPLES")
    if spread > cfg["spread_flag"]:
        flags.append("WIDE_SPREAD")
    result = {
        "aggregate": round(agg, 4),
        "samples": samples,
        "spread": round(spread, 4),
        "market_price": market,
        "flags": flags,
    }
    if market is not None:
        if not (0.0 <= market <= 1.0):
            raise ValueError("market price must be between 0 and 1")
        gap = abs(agg - market)
        result["market_gap"] = round(gap, 4)
        if gap > cfg["market_deviation_flag"]:
            flags.append("MARKET_GAP")
            result["halfway_to_market"] = round((agg + market) / 2.0, 4)
    return result


def load_settings(path):
    try:
        with open(path) as f:
            return json.load(f).get("forecasting", {})
    except FileNotFoundError:
        return {}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("samples", nargs="+", type=float)
    ap.add_argument("--market", type=float, default=None)
    ap.add_argument("--config", default="engine/config.json")
    args = ap.parse_args(argv)
    try:
        out = aggregate(args.samples, args.market, load_settings(args.config))
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        return 2
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
