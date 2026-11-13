#!/usr/bin/env python3
"""Mechanical replay of the Scout's portfolio rules. Tests the RULES, not forecasting skill.

Each simulated year: contributions go in, the core earns a random market return, and a
share of the portfolio sits in N plays whose returns are the market's plus an edge
(alpha) plus large stock-specific noise. alpha = 0 means the Scout has no skill.

Usage: python3 scripts/simulate.py --years 10 --monthly 1500 --raise-pct 0.05
"""
import argparse, json, math, random, statistics

def run(years, monthly, raise_pct, play_share, n_plays, alpha, core_mu=0.07, core_vol=0.16,
        idio_vol=0.45, wipe_p=0.03, stepups=None, trials=4000, seed=7):
    rng = random.Random(seed); out = []
    for _ in range(trials):
        bal = 0.0; m = monthly
        for y in range(years):
            if stepups and y in stepups: m = stepups[y]
            bal += m * 12
            mkt = math.exp(rng.gauss(math.log(1 + core_mu) - core_vol**2 / 2, core_vol)) - 1
            if play_share > 0 and n_plays > 0:
                rs = []
                for _ in range(n_plays):
                    if rng.random() < wipe_p: rs.append(-1.0); continue
                    idio = math.exp(rng.gauss(-idio_vol**2 / 2, idio_vol))
                    rs.append((1 + mkt) * (1 + alpha) * idio / (1 - wipe_p) - 1)
                pr = sum(rs) / len(rs)
            else: pr = mkt
            bal *= 1 + (1 - play_share) * mkt + play_share * pr
            m *= 1 + raise_pct
        out.append(bal)
    out.sort()
    q = lambda p: out[int(p * (len(out) - 1))]
    return {"p10": round(q(.10)), "median": round(q(.50)), "p90": round(q(.90)),
            "mean": round(statistics.mean(out)),
            "p_500k": round(sum(o >= 5e5 for o in out) / len(out), 3),
            "p_1m": round(sum(o >= 1e6 for o in out) / len(out), 3)}

def hit_rate(alpha, hold=3, idio_vol=0.45, wipe_p=0.03, trials=40000, seed=3):
    """Share of single plays that beat the market over the holding period."""
    rng = random.Random(seed); wins = 0
    for _ in range(trials):
        rel = 1.0
        for _ in range(hold):
            if rng.random() < wipe_p: rel = 0; break
            rel *= (1 + alpha) * math.exp(rng.gauss(-idio_vol**2 / 2, idio_vol)) / (1 - wipe_p)
        wins += rel > 1
    return round(wins / trials, 3)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", type=int, default=10); ap.add_argument("--monthly", type=float, default=1500)
    ap.add_argument("--raise-pct", type=float, default=0.05); ap.add_argument("--play-share", type=float, default=0.30)
    ap.add_argument("--plays", type=int, default=6); ap.add_argument("--alpha", type=float, default=0.0)
    a = ap.parse_args()
    print(json.dumps({"result": run(a.years, a.monthly, a.raise_pct, a.play_share, a.plays, a.alpha),
                      "hit_rate_3y": hit_rate(a.alpha)}, indent=2))
