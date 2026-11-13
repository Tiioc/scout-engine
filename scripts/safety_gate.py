#!/usr/bin/env python3
"""The safety gate. Plain code, no AI. Decides PASS or BLOCK for one play.

A play is a JSON object:
{
  "id": "P-2026-11-16-01",
  "type": "career_move",            # free text; compared with blocked_types
  "money_at_risk": 0,               # dollars the owner could lose
  "max_loss": 0,                    # worst case in dollars (must not exceed money_at_risk)
  "max_hours": 20,                  # declared hours budget
  "uses_leverage": false,
  "unlimited_liability": false,
  "speculative": true               # counts against the speculative total
}

The owner's numbers (optional) are a JSON object:
{
  "net_worth": 12000,
  "monthly_expenses": 2500,
  "liquid_savings": 6000,
  "high_interest_debt": 0,
  "speculative_at_risk": 0,         # money already at risk in open speculative plays
  "speculative_peak": 0,            # highest value the speculative money has reached
  "speculative_value": 0            # its value now
}

With no owner numbers the gate runs in universal mode: it enforces the rules
that do not depend on a person (blocked types, limited loss, declared hours)
and reports the money required so the reader can size it themselves.

Usage:
    python3 scripts/safety_gate.py play.json [--numbers profile/numbers.json] [--config engine/config.json]
Exit code 0 = PASS, 1 = BLOCK, 2 = bad input.
"""
import argparse
import json
import sys

DEFAULT_SAFETY = {
    "single_bet_pct": 0.02,
    "single_bet_pct_thin": 0.01,
    "thin_months": 6,
    "sleeve_pct": 0.10,
    "runway_months": 3,
    "breaker_drawdown": 0.50,
    "blocked_types": [
        "day_trading",
        "short_dated_options",
        "leverage",
        "crypto_speculation",
        "mlm",
        "paid_course",
    ],
    "owner_overrides": [],
}


def check(play, numbers=None, safety=None):
    cfg = dict(DEFAULT_SAFETY)
    if safety:
        cfg.update(safety)
    reasons = []
    notes = []

    money = float(play.get("money_at_risk", 0) or 0)
    max_loss = float(play.get("max_loss", money) or 0)
    ptype = str(play.get("type", "")).strip().lower()

    if money < 0 or max_loss < 0:
        raise ValueError("money_at_risk and max_loss cannot be negative")

    # S1 blocked activities (owner may override an item explicitly)
    if ptype in cfg["blocked_types"] and ptype not in cfg["owner_overrides"]:
        reasons.append("S1: '%s' is a blocked activity" % ptype)

    # S2 limited loss only (never overridable)
    if play.get("uses_leverage"):
        reasons.append("S2: uses leverage or borrowed money")
    if play.get("unlimited_liability"):
        reasons.append("S2: unlimited liability")
    if max_loss > money:
        reasons.append("S2: can lose more than is put in (max loss %.0f > at risk %.0f)" % (max_loss, money))

    # S3 hours declared
    hours = play.get("max_hours")
    if hours is None or float(hours) < 0:
        reasons.append("S3: no maximum hours declared")

    mode = "universal"
    if numbers:
        mode = "profile"
        nw = float(numbers.get("net_worth", 0) or 0)
        exp = float(numbers.get("monthly_expenses", 0) or 0)
        liquid = float(numbers.get("liquid_savings", 0) or 0)
        debt = float(numbers.get("high_interest_debt", 0) or 0)
        at_risk = float(numbers.get("speculative_at_risk", 0) or 0)
        peak = float(numbers.get("speculative_peak", 0) or 0)
        value = float(numbers.get("speculative_value", 0) or 0)

        if money > 0:
            # S6 runway
            if exp > 0 and liquid < cfg["runway_months"] * exp:
                reasons.append("S6: liquid savings below %s months of expenses" % cfg["runway_months"])
            if debt > 0:
                reasons.append("S6: high-interest debt outstanding")

            # S4 single-bet cap
            if nw <= 0:
                reasons.append("S4: net worth is zero or negative, so no money may be put at risk")
            else:
                thin = exp > 0 and nw < cfg["thin_months"] * exp
                pct = cfg["single_bet_pct_thin"] if thin else cfg["single_bet_pct"]
                cap = pct * nw
                if money > cap:
                    reasons.append("S4: at risk %.0f exceeds single-bet cap %.0f (%.0f%% of net worth)" % (money, cap, pct * 100))
                # S5 speculative total
                if play.get("speculative", True):
                    sleeve = cfg["sleeve_pct"] * nw
                    if at_risk + money > sleeve:
                        reasons.append("S5: speculative total %.0f would exceed cap %.0f" % (at_risk + money, sleeve))

            # S7 circuit breaker
            if peak > 0 and value <= (1 - cfg["breaker_drawdown"]) * peak:
                reasons.append("S7: speculative money is down %.0f%% or more from its peak" % (cfg["breaker_drawdown"] * 100))
    else:
        if money > 0:
            notes.append("Universal mode: requires %.0f at risk. Size it against your own numbers." % money)

    verdict = "BLOCK" if reasons else "PASS"
    return {
        "id": play.get("id"),
        "verdict": verdict,
        "mode": mode,
        "reasons": reasons,
        "notes": notes,
    }


def _load(path):
    with open(path) as f:
        return json.load(f)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Safety gate for one play")
    ap.add_argument("play")
    ap.add_argument("--numbers", default=None)
    ap.add_argument("--config", default="engine/config.json")
    args = ap.parse_args(argv)
    try:
        play = _load(args.play)
        numbers = _load(args.numbers) if args.numbers else None
        try:
            safety = _load(args.config).get("safety", {})
        except FileNotFoundError:
            safety = {}
        result = check(play, numbers, safety)
    except (ValueError, json.JSONDecodeError, FileNotFoundError) as e:
        print(json.dumps({"error": str(e)}))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
