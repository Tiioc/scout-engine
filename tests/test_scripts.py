#!/usr/bin/env python3
"""Tests for the plain-code parts of the Scout. Run: python3 -m unittest discover -s tests"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import aggregate  # noqa: E402
import check_edition  # noqa: E402
import safety_gate  # noqa: E402
import score  # noqa: E402

HEALTHY = {
    "net_worth": 50000, "monthly_expenses": 2500, "liquid_savings": 20000,
    "high_interest_debt": 0, "speculative_at_risk": 0,
    "speculative_peak": 0, "speculative_value": 0,
}


class TestAggregate(unittest.TestCase):
    def test_median_of_three(self):
        r = aggregate.aggregate([0.2, 0.3, 0.6])
        self.assertAlmostEqual(r["aggregate"], 0.3, places=4)

    def test_one_wild_sample_does_not_move_it(self):
        a = aggregate.aggregate([0.2, 0.25, 0.3])["aggregate"]
        b = aggregate.aggregate([0.2, 0.25, 0.95])["aggregate"]
        self.assertAlmostEqual(a, b, places=4)

    def test_clipping(self):
        self.assertEqual(aggregate.aggregate([0.999, 0.999, 0.999])["aggregate"], 0.97)
        self.assertEqual(aggregate.aggregate([0.001, 0.001, 0.001])["aggregate"], 0.03)

    def test_spread_flag(self):
        self.assertIn("WIDE_SPREAD", aggregate.aggregate([0.1, 0.3, 0.6])["flags"])
        self.assertNotIn("WIDE_SPREAD", aggregate.aggregate([0.25, 0.3, 0.35])["flags"])

    def test_market_gap(self):
        r = aggregate.aggregate([0.3, 0.3, 0.3], market=0.6)
        self.assertIn("MARKET_GAP", r["flags"])
        self.assertAlmostEqual(r["halfway_to_market"], 0.45, places=4)

    def test_few_samples_flag(self):
        self.assertIn("FEW_SAMPLES", aggregate.aggregate([0.3, 0.4])["flags"])

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            aggregate.aggregate([])
        with self.assertRaises(ValueError):
            aggregate.aggregate([1.2])


class TestSafetyGate(unittest.TestCase):
    def play(self, **kw):
        p = {"id": "P-1", "type": "career_move", "money_at_risk": 0, "max_loss": 0,
             "max_hours": 10, "uses_leverage": False, "unlimited_liability": False}
        p.update(kw)
        return p

    def test_zero_cash_play_passes_with_no_profile(self):
        r = safety_gate.check(self.play())
        self.assertEqual(r["verdict"], "PASS")
        self.assertEqual(r["mode"], "universal")

    def test_zero_cash_play_passes_even_when_broke(self):
        broke = dict(HEALTHY, net_worth=-5000, liquid_savings=0, high_interest_debt=3000)
        self.assertEqual(safety_gate.check(self.play(), broke)["verdict"], "PASS")

    def test_blocked_types(self):
        for t in ["day_trading", "short_dated_options", "leverage", "crypto_speculation", "mlm", "paid_course"]:
            self.assertEqual(safety_gate.check(self.play(type=t))["verdict"], "BLOCK", t)

    def test_owner_override_lifts_blocked_type_only(self):
        safety = dict(safety_gate.DEFAULT_SAFETY, owner_overrides=["crypto_speculation"])
        ok = safety_gate.check(self.play(type="crypto_speculation", money_at_risk=100, max_loss=100), HEALTHY, safety)
        self.assertEqual(ok["verdict"], "PASS")
        still = safety_gate.check(self.play(type="crypto_speculation", uses_leverage=True), HEALTHY, safety)
        self.assertEqual(still["verdict"], "BLOCK")

    def test_cannot_lose_more_than_put_in(self):
        self.assertEqual(safety_gate.check(self.play(money_at_risk=100, max_loss=500))["verdict"], "BLOCK")
        self.assertEqual(safety_gate.check(self.play(unlimited_liability=True))["verdict"], "BLOCK")
        self.assertEqual(safety_gate.check(self.play(uses_leverage=True))["verdict"], "BLOCK")

    def test_hours_must_be_declared(self):
        p = self.play()
        del p["max_hours"]
        self.assertEqual(safety_gate.check(p)["verdict"], "BLOCK")

    def test_single_bet_cap(self):
        # 2% of 50,000 = 1,000
        self.assertEqual(safety_gate.check(self.play(money_at_risk=1000, max_loss=1000), HEALTHY)["verdict"], "PASS")
        self.assertEqual(safety_gate.check(self.play(money_at_risk=1001, max_loss=1001), HEALTHY)["verdict"], "BLOCK")

    def test_thin_net_worth_uses_lower_cap(self):
        thin = dict(HEALTHY, net_worth=10000, liquid_savings=9000)  # under 6 months of 2,500
        self.assertEqual(safety_gate.check(self.play(money_at_risk=100, max_loss=100), thin)["verdict"], "PASS")
        self.assertEqual(safety_gate.check(self.play(money_at_risk=150, max_loss=150), thin)["verdict"], "BLOCK")

    def test_speculative_total_cap(self):
        n = dict(HEALTHY, speculative_at_risk=4500)  # cap is 5,000
        self.assertEqual(safety_gate.check(self.play(money_at_risk=500, max_loss=500), n)["verdict"], "PASS")
        self.assertEqual(safety_gate.check(self.play(money_at_risk=600, max_loss=600), n)["verdict"], "BLOCK")

    def test_runway_and_debt_block_money_plays(self):
        low = dict(HEALTHY, liquid_savings=5000)  # under 3 months of 2,500
        self.assertEqual(safety_gate.check(self.play(money_at_risk=100, max_loss=100), low)["verdict"], "BLOCK")
        debt = dict(HEALTHY, high_interest_debt=2000)
        self.assertEqual(safety_gate.check(self.play(money_at_risk=100, max_loss=100), debt)["verdict"], "BLOCK")

    def test_zero_net_worth_blocks_money(self):
        z = dict(HEALTHY, net_worth=0)
        self.assertEqual(safety_gate.check(self.play(money_at_risk=50, max_loss=50), z)["verdict"], "BLOCK")

    def test_circuit_breaker(self):
        n = dict(HEALTHY, speculative_peak=4000, speculative_value=1900)
        self.assertEqual(safety_gate.check(self.play(money_at_risk=100, max_loss=100), n)["verdict"], "BLOCK")

    def test_universal_mode_reports_money_required(self):
        r = safety_gate.check(self.play(money_at_risk=5000, max_loss=5000))
        self.assertEqual(r["verdict"], "PASS")
        self.assertTrue(r["notes"])

    def test_historical_shock_scenarios(self):
        """Replay well-known wipeout shapes: each must be blocked."""
        scenarios = [
            self.play(type="leverage", money_at_risk=5000, max_loss=50000, uses_leverage=True),   # margin in a crash
            self.play(type="short_dated_options", money_at_risk=2000, max_loss=2000),            # weekly options
            self.play(type="crypto_speculation", money_at_risk=10000, max_loss=10000),           # buying a top
            self.play(type="business", money_at_risk=1000, max_loss=80000, unlimited_liability=True),  # personal guarantee
            self.play(type="private_deal", money_at_risk=20000, max_loss=20000),                 # oversized single bet
        ]
        for s in scenarios:
            self.assertEqual(safety_gate.check(s, HEALTHY)["verdict"], "BLOCK", s["type"])


class TestScore(unittest.TestCase):
    def rows(self, n=40):
        f, o = [], []
        for i in range(n):
            y = 1 if i % 4 == 0 else 0            # 25% happen
            p = 0.7 if y else 0.15                # Scout is informative
            f.append({"id": "F%d" % i, "aggregate": p, "base_rate": 0.25,
                      "market_price": None, "category": "career" if i % 2 else "ventures"})
            o.append({"id": "F%d" % i, "outcome": y})
        return f, o

    def test_brier_known_values(self):
        self.assertAlmostEqual(score.brier(0.5, 1), 0.25)
        self.assertAlmostEqual(score.brier(1.0, 1), 0.0)
        self.assertAlmostEqual(score.brier(0.0, 1), 1.0)

    def test_join_ignores_unresolved_and_plays(self):
        f, o = self.rows(4)
        o[0]["outcome"] = None
        o.append({"id": "P-1", "kind": "play", "outcome": 1})
        self.assertEqual(len(score.join(f, o)), 3)

    def test_scout_beats_base_rate_when_informative(self):
        f, o = self.rows(40)
        d = score.bootstrap_diff(score.join(f, o), "base")
        self.assertGreater(d[1], 0)  # lower bound above zero

    def test_insufficient_data_message(self):
        f, o = self.rows(8)
        self.assertIn("Insufficient data", score.report(score.join(f, o), min_n=30))

    def test_empty(self):
        self.assertIn("No resolved forecasts", score.report([]))

    def test_calibration_bins(self):
        f, o = self.rows(40)
        table = score.calibration(score.join(f, o))
        self.assertEqual(sum(t[2] for t in table), 40)


GOOD = """# The Scout: Edition 2026-11-16
**Headline:** One play.
## Play 1: Company X
**What:** thing
**Forecast:** 15% main payoff
**Cost:** $0 and 4 hours
**Wrong if:** no hiring by March
**Exit:** stop after two attempts
## Watchlist
- none
"""


class TestCheckEdition(unittest.TestCase):
    def test_good_edition_passes(self):
        self.assertEqual(check_edition.check(GOOD), [])

    def test_no_play_week_is_valid(self):
        self.assertEqual(check_edition.check("# Edition\n**Headline:** No strong play this week\n## Watchlist\n- x\n"), [])

    def test_empty_edition_fails(self):
        self.assertTrue(check_edition.check("# Edition\n## Watchlist\n- x\n"))

    def test_four_plays_fails(self):
        play = GOOD.split("## Play 1: Company X")[1].split("## Watchlist")[0]
        text = "# E\n" + "".join("## Play %d: X%s" % (i, play) for i in range(1, 5))
        self.assertTrue(any("Too many" in p for p in check_edition.check(text)))

    def test_missing_field_fails(self):
        self.assertTrue(check_edition.check(GOOD.replace("**Exit:** stop after two attempts\n", "")))

    def test_forecast_needs_probability(self):
        self.assertTrue(check_edition.check(GOOD.replace("15% main payoff", "likely")))

    def test_generic_advice_fails(self):
        self.assertTrue(check_edition.check(GOOD + "\nAlso max out your 401(k).\n"))
        self.assertTrue(check_edition.check(GOOD + "\nConsider an index fund.\n"))


if __name__ == "__main__":
    unittest.main()
