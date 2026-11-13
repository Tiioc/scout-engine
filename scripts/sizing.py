#!/usr/bin/env python3
"""Bet sizing for one play. Plain code, no AI.

Takes the scenario table for a play (probability and ending multiple of the
money put in), compares it with simply holding the benchmark over the same
period, and returns the expected return, the chance and size of a loss, and a
recommended bet as a share of the portfolio.

Method: the growth-optimal (Kelly) fraction, found by maximizing expected log
wealth when the rest of the money stays in the benchmark, then scaled down by
`kelly_fraction` and capped. A play with no edge over the benchmark gets zero.

Build plays (the stake is hours): add --hours N --hourly-value V and give scenarios as
probability:dollars. Returns expected pay per hour and a go / no-go against the bar.

Usage:
  python3 scripts/sizing.py --years 3 --scenario 0.30:5 --scenario 0.70:0.2 \
      [--benchmark-return 0.07] [--portfolio 50000] [--open-plays 0.10] [--config engine/config.json]
Each --scenario is probability:multiple (multiple 0 = total loss, 1 = money back).
Prints JSON.
"""
import argparse
import json
import math
import sys

DEFAULTS = {"hours_multiple_to_publish": 2.0, "kelly_fraction": 0.5, "max_single": 0.10, "max_total": 0.30, "benchmark_return": 0.07,
            "min_edge_to_publish": 0.10}


def _bar(min_edge, years):
    """Minimum edge to publish. The full bar applies to holds of a year or more; shorter
    holds scale it down in proportion to time, with a 1% floor, so a quick play is not
    rejected for failing a multi-year hurdle."""
    return min_edge if years >= 1.0 else max(0.01, min_edge * years) if min_edge > 0 else 0.0


def analyze(scenarios, years, benchmark_return=0.07, kelly_fraction=0.5,
            max_single=0.10, max_total=0.30, open_plays=0.0, portfolio=None, min_edge=0.0, capacity=None):
    if years <= 0:
        raise ValueError("years must be positive")
    if not scenarios:
        raise ValueError("at least one scenario is required")
    total_p = sum(p for p, _ in scenarios)
    if abs(total_p - 1.0) > 0.011:
        raise ValueError("scenario probabilities must sum to 1 (got %.3f)" % total_p)
    for p, m in scenarios:
        if p < 0 or m < 0:
            raise ValueError("probabilities and multiples cannot be negative")
    scen = [(p / total_p, m) for p, m in scenarios]

    bench = (1.0 + benchmark_return) ** years
    ev = sum(p * m for p, m in scen)
    p_loss = sum(p for p, m in scen if m < 1.0)
    loss_given = (sum(p * (1.0 - m) for p, m in scen if m < 1.0) / p_loss) if p_loss else 0.0
    p_trail = sum(p for p, m in scen if m < bench)
    worst = min(m for _, m in scen)
    best = max(m for _, m in scen)

    # Growth-optimal fraction against the benchmark: maximize E[log((1-f)*bench + f*m)]
    def growth(f):
        g = 0.0
        for p, m in scen:
            w = (1.0 - f) * bench + f * m
            if w <= 0:
                return float("-inf")
            g += p * math.log(w)
        return g

    full_kelly, best_g = 0.0, growth(0.0)
    steps = 2000
    for i in range(1, steps + 1):
        f = i / steps
        g = growth(f)
        if g > best_g + 1e-12:
            best_g, full_kelly = g, f

    edge = ev / bench - 1.0
    room = max(0.0, max_total - open_plays)
    if edge <= 0 or full_kelly <= 0:
        bet = 0.0
        reason = "No edge over the benchmark on these odds: no bet."
    elif edge < _bar(min_edge, years):
        bet = 0.0
        reason = "Edge over the benchmark is %.1f%%, below the %.1f%% bar for a %.2g-year hold: no bet." % (
            edge * 100, _bar(min_edge, years) * 100, years)
    else:
        bet = min(full_kelly * kelly_fraction, max_single, room)
        limits = []
        if bet == max_single and full_kelly * kelly_fraction > max_single:
            limits.append("single-play cap")
        if bet == room and room < min(full_kelly * kelly_fraction, max_single):
            limits.append("total open-plays cap")
        reason = "Sized at %.0f%% of the growth-optimal fraction%s." % (
            kelly_fraction * 100, (", limited by the " + " and ".join(limits)) if limits else "")

    out = {
        "expected_multiple": ev,
        "expected_annual_return": ev ** (1.0 / years) - 1.0 if ev > 0 else -1.0,
        "benchmark_multiple": bench,
        "edge_over_benchmark": edge,
        "chance_of_losing_money": p_loss,
        "average_loss_when_it_loses": loss_given,
        "chance_of_trailing_benchmark": p_trail,
        "worst_case_multiple": worst,
        "best_case_multiple": best,
        "growth_optimal_fraction": full_kelly,
        "recommended_bet_fraction": bet,
        "effect_on_portfolio_if_best_case": bet * (best - bench),
        "effect_on_portfolio_if_worst_case": bet * (worst - bench),
        "reason": reason,
    }
    if portfolio is not None:
        dollars = bet * portfolio
        if capacity is not None and dollars > capacity:
            dollars = capacity
            out["recommended_bet_fraction"] = bet = capacity / portfolio
            out["effect_on_portfolio_if_best_case"] = bet * (best - bench)
            out["effect_on_portfolio_if_worst_case"] = bet * (worst - bench)
            out["reason"] += " Limited by the play's capacity of $%.0f." % capacity
        out["recommended_bet_dollars"] = dollars
        out["dollars_lost_in_worst_case"] = bet * portfolio * (1.0 - worst)
        out["dollars_gained_in_best_case"] = bet * portfolio * (best - 1.0)
    return out


def analyze_hours(scenarios, hours, hourly_value, money_at_risk=0.0, min_multiple=2.0):
    """A build play: the stake is hours (and optionally some money).
    scenarios: list of (probability, dollars earned or equity value created)."""
    if hours <= 0 or hourly_value <= 0:
        raise ValueError("hours and hourly_value must be positive")
    total_p = sum(p for p, _ in scenarios)
    if abs(total_p - 1.0) > 0.011:
        raise ValueError("scenario probabilities must sum to 1 (got %.3f)" % total_p)
    scen = [(p / total_p, d) for p, d in scenarios]
    ev = sum(p * d for p, d in scen) - money_at_risk
    cost_of_time = hours * hourly_value
    per_hour = ev / hours
    p_below = sum(p for p, d in scen if (d - money_at_risk) < cost_of_time)
    p_nothing = sum(p for p, d in scen if d <= money_at_risk)
    multiple = per_hour / hourly_value
    go = multiple >= min_multiple
    return {
        "expected_net_dollars": ev,
        "expected_dollars_per_hour": per_hour,
        "multiple_of_hourly_value": multiple,
        "cost_of_time": cost_of_time,
        "chance_it_pays_less_than_your_time_is_worth": p_below,
        "chance_it_returns_nothing": p_nothing,
        "best_case_dollars": max(d for _, d in scen) - money_at_risk,
        "worst_case_dollars": min(d for _, d in scen) - money_at_risk,
        "max_money_lost": money_at_risk,
        "verdict": "worth the hours" if go else "not worth the hours on these odds",
        "reason": "Expected pay per hour is %.1fx the hourly value; the bar is %.1fx." % (multiple, min_multiple),
    }


def _round(obj):
    if isinstance(obj, float):
        return round(obj, 4)
    if isinstance(obj, dict):
        return {k: _round(v) for k, v in obj.items()}
    return obj


def main(argv=None):
    ap = argparse.ArgumentParser(description="Size one play")
    ap.add_argument("--years", type=float, default=3.0)
    ap.add_argument("--scenario", action="append", required=True, help="probability:multiple")
    ap.add_argument("--benchmark-return", type=float, default=None)
    ap.add_argument("--portfolio", type=float, default=None)
    ap.add_argument("--capacity", type=float, default=None, help="most dollars the play can absorb")
    ap.add_argument("--open-plays", type=float, default=0.0, help="share of portfolio already in open plays")
    ap.add_argument("--config", default="engine/config.json")
    ap.add_argument("--hours", type=float, default=None, help="build play: total hours staked; scenarios are probability:dollars")
    ap.add_argument("--hourly-value", type=float, default=30.0)
    ap.add_argument("--money-at-risk", type=float, default=0.0)
    a = ap.parse_args(argv)
    cfg = dict(DEFAULTS)
    try:
        with open(a.config) as f:
            cfg.update(json.load(f).get("sizing", {}))
    except FileNotFoundError:
        pass
    if a.benchmark_return is not None:
        cfg["benchmark_return"] = a.benchmark_return
    try:
        scen = []
        for s in a.scenario:
            p, m = s.split(":")
            scen.append((float(p), float(m)))
        if a.hours is not None:
            print(json.dumps(_round(analyze_hours(scen, a.hours, a.hourly_value, a.money_at_risk,
                                                  cfg.get("hours_multiple_to_publish", 2.0))), indent=2))
            return 0
        out = analyze(scen, a.years, cfg["benchmark_return"], cfg["kelly_fraction"],
                      cfg["max_single"], cfg["max_total"], a.open_plays, a.portfolio,
                      cfg["min_edge_to_publish"], a.capacity)
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        return 2
    print(json.dumps(_round(out), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
