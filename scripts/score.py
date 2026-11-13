#!/usr/bin/env python3
"""Grade the Scout's forecasts. Plain code, no AI.

Reads <ledger>/forecasts.jsonl and <ledger>/outcomes.jsonl and prints a
Markdown report: Brier score and log score for the Scout, the same scores for
two baselines (base rate only, market price only), a bootstrap confidence
interval on the difference, a calibration table, and results by category.

Usage:
    python3 scripts/score.py ledger/ [--min 30] [--seed 7]
"""
import argparse
import json
import math
import os
import random
import sys


def read_jsonl(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def brier(p, y):
    return (p - y) ** 2


def log_score(p, y):
    p = min(max(p, 1e-6), 1 - 1e-6)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def join(forecasts, outcomes):
    """Return resolved forecasts as dicts with p, y, base, market, category."""
    out_by_id = {}
    for o in outcomes:
        if o.get("kind", "forecast") != "forecast":
            continue
        if o.get("outcome") in (0, 1):
            out_by_id[o["id"]] = o["outcome"]
    rows = []
    for f in forecasts:
        if f.get("id") in out_by_id and f.get("aggregate") is not None:
            rows.append({
                "id": f["id"],
                "p": float(f["aggregate"]),
                "y": int(out_by_id[f["id"]]),
                "base": f.get("base_rate"),
                "market": f.get("market_price"),
                "category": f.get("category", "uncategorized"),
            })
    return rows


def bootstrap_diff(rows, key, n=2000, seed=7):
    """95% CI for mean(Brier baseline) - mean(Brier scout). Positive = Scout better."""
    pairs = [(brier(r[key], r["y"]) - brier(r["p"], r["y"])) for r in rows if r.get(key) is not None]
    if len(pairs) < 2:
        return None
    rng = random.Random(seed)
    means = []
    for _ in range(n):
        sample = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        means.append(mean(sample))
    means.sort()
    return (mean(pairs), means[int(0.025 * n)], means[int(0.975 * n) - 1], len(pairs))


def calibration(rows, bins=10):
    table = []
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        inb = [r for r in rows if (lo <= r["p"] < hi) or (b == bins - 1 and r["p"] == 1.0)]
        if inb:
            table.append((lo, hi, len(inb), mean([r["p"] for r in inb]), mean([r["y"] for r in inb])))
    return table


def summarize(rows):
    return {
        "n": len(rows),
        "brier": mean([brier(r["p"], r["y"]) for r in rows]),
        "log": mean([log_score(r["p"], r["y"]) for r in rows]),
    }


def baseline(rows, key):
    have = [r for r in rows if r.get(key) is not None]
    if not have:
        return None
    return {
        "n": len(have),
        "brier": mean([brier(r[key], r["y"]) for r in have]),
        "scout_brier_same_set": mean([brier(r["p"], r["y"]) for r in have]),
    }


def report(rows, min_n=30, seed=7):
    lines = ["# Scout scoreboard", ""]
    s = summarize(rows)
    lines.append("Resolved forecasts: **%d**" % s["n"])
    lines.append("")
    if s["n"] == 0:
        lines.append("No resolved forecasts yet.")
        return "\n".join(lines)
    if s["n"] < min_n:
        lines.append("**Insufficient data.** Fewer than %d resolved forecasts. The numbers below are shown for the record only; do not draw conclusions from them." % min_n)
        lines.append("")
    lines.append("Lower is better for both scores. Always saying 50%% scores a Brier of 0.250.")
    lines.append("")
    lines.append("| Forecaster | N | Brier | Scout Brier on same questions |")
    lines.append("|---|---|---|---|")
    lines.append("| Scout | %d | %.4f | |" % (s["n"], s["brier"]))
    for key, label in (("base", "Base rate only"), ("market", "Market price only")):
        b = baseline(rows, key)
        if b:
            lines.append("| %s | %d | %.4f | %.4f |" % (label, b["n"], b["brier"], b["scout_brier_same_set"]))
    lines.append("")
    lines.append("Scout log score: %.4f" % s["log"])
    lines.append("")
    lines.append("## Is the Scout adding anything?")
    for key, label in (("base", "base rate only"), ("market", "market price only")):
        d = bootstrap_diff(rows, key, seed=seed)
        if d:
            m, lo, hi, n = d
            verdict = "better" if lo > 0 else ("worse" if hi < 0 else "no clear difference")
            lines.append("- vs %s (N=%d): Brier improvement %.4f, 95%% interval %.4f to %.4f: **%s**" % (label, n, m, lo, hi, verdict))
    lines.append("")
    lines.append("## Calibration")
    lines.append("When the Scout says X%, does it happen about X% of the time? A row needs about 10 forecasts to mean much.")
    lines.append("")
    lines.append("| Forecast range | N | Average forecast | Actual rate |")
    lines.append("|---|---|---|---|")
    for lo, hi, n, avg_p, rate in calibration(rows):
        lines.append("| %d-%d%% | %d | %.0f%% | %.0f%% |" % (lo * 100, hi * 100, n, avg_p * 100, rate * 100))
    lines.append("")
    lines.append("## By category")
    lines.append("| Category | N | Brier |")
    lines.append("|---|---|---|")
    cats = sorted(set(r["category"] for r in rows))
    for c in cats:
        cr = [r for r in rows if r["category"] == c]
        lines.append("| %s | %d | %.4f |" % (c, len(cr), mean([brier(r["p"], r["y"]) for r in cr])))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Score the Scout's forecasts")
    ap.add_argument("ledger_dir")
    ap.add_argument("--min", type=int, default=30)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args(argv)
    forecasts = read_jsonl(os.path.join(args.ledger_dir, "forecasts.jsonl"))
    outcomes = read_jsonl(os.path.join(args.ledger_dir, "outcomes.jsonl"))
    print(report(join(forecasts, outcomes), args.min, args.seed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
