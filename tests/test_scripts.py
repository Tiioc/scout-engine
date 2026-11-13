#!/usr/bin/env python3
"""Tests for the plain-code parts of the Scout. Run: python3 -m unittest discover -s tests"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import aggregate  # noqa: E402
import check_edition  # noqa: E402
import fincalc  # noqa: E402
import sizing  # noqa: E402
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
        self.assertTrue(check_edition.check(GOOD + "\nRemember to pay yourself first.\n"))
        self.assertTrue(check_edition.check(GOOD + "\nLive below your means.\n"))


class TestFincalc(unittest.TestCase):
    def test_cagr(self):
        self.assertAlmostEqual(fincalc.cagr(100, 200, 10), 0.071773, places=5)
        with self.assertRaises(ValueError):
            fincalc.cagr(0, 100, 5)

    def test_future_value(self):
        self.assertAlmostEqual(fincalc.future_value(1000, 0.10, 1)["future_value"], 1100, places=6)
        r = fincalc.future_value(0, 0.0, 1, monthly=100)
        self.assertAlmostEqual(r["future_value"], 1200, places=6)
        self.assertAlmostEqual(r["contributed"], 1200, places=6)

    def test_real_return(self):
        self.assertAlmostEqual(fincalc.real_return(0.07, 0.03), 0.038835, places=5)

    def test_after_tax_yield(self):
        self.assertAlmostEqual(fincalc.after_tax_yield(0.05, 0.22, 0.05), 0.0365, places=6)
        self.assertAlmostEqual(fincalc.after_tax_yield(0.05, 0.22, 0.05, state_exempt=True), 0.039, places=6)

    def test_dividend_no_growth_no_reinvest(self):
        r = fincalc.dividend_path(100, 4, 0, 0, 10, reinvest=False)
        self.assertAlmostEqual(r["end_value_per_share_bought"], 140, places=6)
        self.assertAlmostEqual(r["start_yield"], 0.04)
        self.assertAlmostEqual(r["yield_on_cost_at_end"], 0.04)

    def test_dividend_reinvest_beats_not(self):
        a = fincalc.dividend_path(100, 4, 0.03, 0.02, 20, reinvest=True)
        b = fincalc.dividend_path(100, 4, 0.03, 0.02, 20, reinvest=False)
        self.assertGreater(a["end_value_per_share_bought"], b["end_value_per_share_bought"])

    def test_dividend_tax_lowers_value(self):
        a = fincalc.dividend_path(100, 4, 0.03, 0.02, 20, tax=0.0)
        b = fincalc.dividend_path(100, 4, 0.03, 0.02, 20, tax=0.15)
        self.assertGreater(a["end_value_per_share_bought"], b["end_value_per_share_bought"])

    def test_compare_income_vs_growth(self):
        r = fincalc.compare_income_vs_growth(
            20, {"yield": 0.045, "divgrowth": 0.03, "pricegrowth": 0.02},
            {"yield": 0.012, "divgrowth": 0.09, "pricegrowth": 0.08})
        self.assertEqual(r["higher_end_value"], "b")
        self.assertIsNotNone(r["income_crossover_year"])
        self.assertGreater(r["income_crossover_year"], 15)

    def test_fee_drag(self):
        r = fincalc.fee_drag(10000, 0.07, 30, 0.0003, 0.01)
        self.assertGreater(r["value_a"], r["value_b"])
        self.assertGreater(r["cost_of_higher_fee"], 15000)

    def test_bonus(self):
        r = fincalc.bonus_return(300, 5000, 3)
        self.assertAlmostEqual(r["period_return"], 0.06)
        self.assertAlmostEqual(r["annualized_return"], 1.06 ** 4 - 1, places=6)

    def test_payback(self):
        r = fincalc.payback(20000, 5000, 250)
        self.assertAlmostEqual(r["payback_years"], 4)
        self.assertAlmostEqual(r["profit_per_hour"], 20)
        self.assertIsNone(fincalc.payback(20000, -100)["payback_years"])

    def test_dcf_perpetuity(self):
        r = fincalc.dcf(100, 0, 10, 0, 0.10)
        self.assertAlmostEqual(r["present_value"], 1000, places=4)
        with self.assertRaises(ValueError):
            fincalc.dcf(100, 0.05, 10, 0.10, 0.09)

    def test_volatility_drag(self):
        self.assertAlmostEqual(fincalc.volatility_drag(0.10, 0.60)["approx_compound_return"], -0.08)

    def test_mortgage_payment(self):
        self.assertAlmostEqual(fincalc.mortgage_payment(300000, 0.06, 30), 1798.65, places=1)

    def test_rent_vs_buy_direction(self):
        cheap_rent = fincalc.rent_vs_buy(500000, 0.2, 0.07, 5, 1500)
        dear_rent = fincalc.rent_vs_buy(500000, 0.2, 0.07, 5, 4500)
        self.assertLess(cheap_rent["buying_wins_by"], dear_rent["buying_wins_by"])


class TestSizing(unittest.TestCase):
    def test_no_edge_no_bet(self):
        r = sizing.analyze([(0.5, 1.2), (0.5, 1.0)], 3, 0.07)   # EV 1.10 < benchmark 1.225
        self.assertEqual(r["recommended_bet_fraction"], 0.0)

    def test_good_asymmetric_play_gets_a_real_bet(self):
        r = sizing.analyze([(0.30, 5.0), (0.70, 0.2)], 3, 0.07)  # EV 1.64
        self.assertGreater(r["recommended_bet_fraction"], 0.03)
        self.assertLessEqual(r["recommended_bet_fraction"], 0.10)
        self.assertAlmostEqual(r["chance_of_losing_money"], 0.70)
        self.assertAlmostEqual(r["average_loss_when_it_loses"], 0.80)

    def test_thin_edge_below_bar_gets_no_bet(self):
        r = sizing.analyze([(0.5, 1.35), (0.5, 1.15)], 3, 0.07, min_edge=0.10)   # edge about 2%
        self.assertEqual(r["recommended_bet_fraction"], 0.0)

    def test_single_cap(self):
        r = sizing.analyze([(0.6, 4.0), (0.4, 0.8)], 3, 0.07)
        self.assertAlmostEqual(r["recommended_bet_fraction"], 0.10)

    def test_total_cap(self):
        r = sizing.analyze([(0.6, 4.0), (0.4, 0.8)], 3, 0.07, open_plays=0.26)
        self.assertAlmostEqual(r["recommended_bet_fraction"], 0.04)

    def test_total_loss_keeps_kelly_below_one(self):
        r = sizing.analyze([(0.5, 4.0), (0.5, 0.0)], 3, 0.07)
        self.assertLess(r["growth_optimal_fraction"], 1.0)

    def test_dollars(self):
        r = sizing.analyze([(0.30, 5.0), (0.70, 0.2)], 3, 0.07, portfolio=50000)
        self.assertAlmostEqual(r["recommended_bet_dollars"], r["recommended_bet_fraction"] * 50000)

    def test_probabilities_must_sum_to_one(self):
        with self.assertRaises(ValueError):
            sizing.analyze([(0.3, 2.0), (0.3, 0.5)], 3)

    def test_higher_kelly_fraction_bets_more(self):
        a = sizing.analyze([(0.30, 3.0), (0.70, 0.7)], 3, 0.07, kelly_fraction=0.25, max_single=1.0, max_total=1.0)
        b = sizing.analyze([(0.30, 3.0), (0.70, 0.7)], 3, 0.07, kelly_fraction=0.5, max_single=1.0, max_total=1.0)
        self.assertGreater(b["recommended_bet_fraction"], a["recommended_bet_fraction"])


class TestHoursSizing(unittest.TestCase):
    def test_good_build_play(self):
        r = sizing.analyze_hours([(0.2, 80000), (0.3, 15000), (0.5, 0)], 300, 30)
        self.assertAlmostEqual(r["expected_net_dollars"], 20500)
        self.assertAlmostEqual(r["expected_dollars_per_hour"], 20500 / 300)
        self.assertEqual(r["verdict"], "worth the hours")
        self.assertAlmostEqual(r["chance_it_returns_nothing"], 0.5)

    def test_weak_build_play(self):
        r = sizing.analyze_hours([(0.1, 20000), (0.9, 0)], 400, 30)
        self.assertEqual(r["verdict"], "not worth the hours on these odds")

    def test_money_at_risk_reduces_value(self):
        a = sizing.analyze_hours([(0.5, 10000), (0.5, 0)], 100, 30)
        b = sizing.analyze_hours([(0.5, 10000), (0.5, 0)], 100, 30, money_at_risk=2000)
        self.assertAlmostEqual(a["expected_net_dollars"] - b["expected_net_dollars"], 2000)
        self.assertEqual(b["max_money_lost"], 2000)


class TestRentBuyPayoff(unittest.TestCase):
    def test_no_payments_after_payoff(self):
        r = fincalc.rent_vs_buy(300000, 0.2, 0.06, 35, 1500)
        self.assertGreater(r["owner_net_worth"], 0)
        self.assertLess(r["owner_net_worth"], 300000 * (1.03 ** 35))


if __name__ == "__main__":
    unittest.main()


# --- added 2026-11-13: short holds, capacity, simulator ---
def test_sizing_short_hold_uses_scaled_bar():
    import sizing
    scen = [(0.25, 1.111), (0.30, 1.051), (0.20, 1.010), (0.15, 0.949), (0.10, 0.869)]
    r = sizing.analyze(scen, 0.08, min_edge=0.10)
    assert r["recommended_bet_fraction"] > 0
    r3 = sizing.analyze(scen, 3.0, min_edge=0.10)
    assert r3["recommended_bet_fraction"] == 0


def test_sizing_capacity_caps_dollars():
    import sizing
    scen = [(0.6, 1.2), (0.4, 0.95)]
    r = sizing.analyze(scen, 0.1, portfolio=100000, min_edge=0.10, capacity=490)
    assert r["recommended_bet_dollars"] == 490
    assert abs(r["recommended_bet_fraction"] - 0.0049) < 1e-9


def test_simulator_no_skill_does_not_beat_core_and_edge_does():
    import simulate
    core = simulate.run(10, 1500, 0.05, 0, 0, 0, trials=1500)
    none = simulate.run(10, 1500, 0.05, 0.3, 6, 0.0, trials=1500)
    edge = simulate.run(10, 1500, 0.05, 0.3, 6, 0.10, trials=1500)
    assert abs(none["median"] - core["median"]) / core["median"] < 0.05
    assert none["p10"] <= core["p10"] * 1.02
    assert edge["median"] > core["median"] * 1.1


def test_simulator_hit_rate_baseline():
    import simulate
    assert 0.30 < simulate.hit_rate(0.0, trials=8000) < 0.42
    assert simulate.hit_rate(0.10, trials=8000) > simulate.hit_rate(0.0, trials=8000) + 0.08


def test_backtest_grid_and_terminal_math():
    import numpy as np, backtest
    ws = list(backtest.weights_grid(3))
    assert len(ws) == 66 and all(sum(w) == 10 for w in ws)
    flat = np.zeros((1, 5))
    t = backtest.terminal(flat, 5, growth=0.0)
    assert t.shape == (1, 1) and abs(t[0, 0] - 5.0) < 1e-9
    up = np.full((1, 2), 0.10)
    assert abs(backtest.terminal(up, 2, growth=0.0)[0, 0] - (1.1 * 1.1 + 1.1)) < 1e-9
