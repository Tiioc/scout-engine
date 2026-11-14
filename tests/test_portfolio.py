"""Tests for the portfolio manager, trend signal, backtest parser and entry point."""
import json, os, subprocess, sys, tempfile, unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import importlib.util


def load(name):
    spec = importlib.util.spec_from_file_location("scout_" + name, os.path.join(ROOT, "scripts", name + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


portfolio, sig, backtest = load("portfolio"), load("signal"), load("backtest")
FUNDS = {"small_value": "AVUV", "momentum": "MTUM", "gold": "GLDM", "trend_2x_stocks": {"on": "SSO", "off": "SGOV"},
         "trend_small_value": {"on": "AVUV", "off": "SGOV"}}
MIX = {"small_value": 0.3, "momentum": 0.2, "trend_2x_stocks": 0.4, "gold": 0.1}


class Targets(unittest.TestCase):
    def test_signal_on_uses_stock_fund(self):
        t = portfolio.targets(MIX, FUNDS, True)
        self.assertAlmostEqual(t["SSO"], 0.4); self.assertNotIn("SGOV", t)

    def test_signal_off_moves_block_to_cash(self):
        t = portfolio.targets(MIX, FUNDS, False)
        self.assertAlmostEqual(t["SGOV"], 0.4); self.assertNotIn("SSO", t)

    def test_blocks_sharing_a_fund_are_merged(self):
        t = portfolio.targets({"small_value": 0.2, "momentum": 0.4, "trend_small_value": 0.3, "gold": 0.1}, FUNDS, True)
        self.assertAlmostEqual(t["AVUV"], 0.5); self.assertAlmostEqual(sum(t.values()), 1.0)

    def test_pie_adds_to_100(self):
        for w in ({"A": 1 / 3, "B": 1 / 3, "C": 1 / 3}, {"A": 0.335, "B": 0.335, "C": 0.33}, portfolio.targets(MIX, FUNDS, True)):
            self.assertEqual(sum(portfolio.pie(w).values()), 100)


class PerFundSignals(unittest.TestCase):
    F = {"small_value": "AVUV", "gold": "GLDM", "trend_momentum": {"on": "MTUM", "off": "SGOV", "signal": "MTUM"},
         "trend_small_value": {"on": "AVUV", "off": "SGOV", "signal": "AVUV"}, "trend_2x_stocks": {"on": "SSO", "off": "SGOV", "signal": "SP500"}}
    M = {"small_value": 0.2, "trend_small_value": 0.1, "trend_momentum": 0.5, "trend_2x_stocks": 0.1, "gold": 0.1}

    def test_each_block_follows_its_own_signal(self):
        t = portfolio.targets(self.M, self.F, {"MTUM": False, "AVUV": True, "SP500": True})
        self.assertAlmostEqual(t["SGOV"], 0.5); self.assertAlmostEqual(t["AVUV"], 0.3); self.assertAlmostEqual(t["SSO"], 0.1)

    def test_all_off_leaves_only_unconditional_blocks_invested(self):
        t = portfolio.targets(self.M, self.F, {"default": False})
        self.assertAlmostEqual(t["SGOV"], 0.7); self.assertAlmostEqual(t["AVUV"], 0.2); self.assertAlmostEqual(sum(t.values()), 1.0)

    def test_risk_levels_in_config_are_ordered(self):
        c = json.load(open(os.path.join(ROOT, "engine", "config.json")))["core"]["risk_levels"]
        ks = sorted((int(k) for k in c if k.isdigit()))
        g = [c[str(k)]["real_growth_per_year"] for k in ks]
        self.assertEqual(g, sorted(g))                       # more room to fall never means less growth
        for k in ks:
            self.assertGreaterEqual(c[str(k)]["worst_fall"], -k / 100 - 1e-9); self.assertAlmostEqual(sum(c[str(k)]["mix"].values()), 1.0)


class Plan(unittest.TestCase):
    def setUp(self): self.tw = portfolio.targets(MIX, FUNDS, True)

    def test_first_deposit_follows_the_mix(self):
        p = portfolio.plan({}, 1500, self.tw)
        self.assertAlmostEqual(p["deposit_goes_to"]["SSO"], 600); self.assertFalse(p["rebalance_needed"])
        self.assertAlmostEqual(sum(p["deposit_goes_to"].values()), 1500)

    def test_deposit_goes_to_the_underweight_slice(self):
        p = portfolio.plan({"AVUV": 3000, "MTUM": 2000, "SSO": 3000, "GLDM": 1000}, 1000, self.tw)
        self.assertEqual(list(p["deposit_goes_to"]), ["SSO"]); self.assertAlmostEqual(p["deposit_goes_to"]["SSO"], 1000)
        self.assertFalse(p["rebalance_needed"])

    def test_big_drift_triggers_rebalance_that_sums_to_zero(self):
        p = portfolio.plan({"AVUV": 1000, "MTUM": 2000, "SSO": 9000, "GLDM": 1000}, 0, self.tw)
        self.assertTrue(p["rebalance_needed"]); self.assertAlmostEqual(sum(p["rebalance_trades"].values()), 0, places=1)
        self.assertLess(p["rebalance_trades"]["SSO"], 0)

    def test_signal_flip_sells_the_whole_stock_block(self):
        off = portfolio.targets(MIX, FUNDS, False)
        p = portfolio.plan({"AVUV": 3000, "MTUM": 2000, "SSO": 4000, "GLDM": 1000}, 0, off)
        self.assertTrue(p["rebalance_needed"]); self.assertAlmostEqual(p["rebalance_trades"]["SSO"], -4000)
        self.assertAlmostEqual(p["rebalance_trades"]["SGOV"], 4000)

    def test_never_spends_more_than_the_deposit(self):
        p = portfolio.plan({"AVUV": 100}, 50, self.tw)
        self.assertLessEqual(sum(p["deposit_goes_to"].values()), 50 + 1e-6)

    def test_empty_account_and_no_deposit_is_an_error(self):
        with self.assertRaises(ValueError): portfolio.plan({}, 0, self.tw)

    def test_steps_are_plain_sentences(self):
        p = portfolio.plan({}, 1500, self.tw); s = portfolio.steps(p, True)
        self.assertTrue(s[0].startswith("Set the pie to")); self.assertIn("on", s[-1])


class Policy(unittest.TestCase):
    ST = [{"name": "growth", "below_multiple_of_yearly_deposits": 10}, {"name": "build", "below_multiple_of_yearly_deposits": 25},
          {"name": "protect", "below_multiple_of_yearly_deposits": None}]

    def test_stage_follows_size_against_deposits(self):
        self.assertEqual(portfolio.stage(50000, 18000, self.ST), "growth")
        self.assertEqual(portfolio.stage(300000, 18000, self.ST), "build")
        self.assertEqual(portfolio.stage(900000, 18000, self.ST), "protect")
        self.assertEqual(portfolio.stage(900000, None, self.ST), "growth")

    def test_risk_report_is_in_dollars_and_never_claims_zero_risk(self):
        r = portfolio.risk(10000, {"worst_fall": 0.7, "worst_year": 0.33, "losing_years_share": 0.34, "worst_single_day": 0.14}, 18000, 12500)
        self.assertIn("$7000", r["worst_fall_in_history"]); self.assertEqual(r["below_its_high_by"], "20%")
        self.assertAlmostEqual(r["worst_fall_in_years_of_deposits"], 0.4)

    def test_every_action_step_names_a_rule(self):
        tw = portfolio.targets(MIX, FUNDS, False)
        p = portfolio.plan({"AVUV": 3000, "MTUM": 2000, "SSO": 4000, "GLDM": 1000}, 500, tw)
        for line in portfolio.steps(p, False)[1:]:
            self.assertRegex(line, r"\[Rule R[1-8]\]")

    def test_policy_file_defines_every_rule_used(self):
        text = open(os.path.join(ROOT, "engine", "POLICY.md")).read()
        for r in ("R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"): self.assertIn("| %s |" % r, text)


class Signal(unittest.TestCase):
    def rows(self, closes, start=(2025, 1)):
        y, m = start; out = []
        for c in closes:
            out.append(("%d-%02d-15" % (y, m), "1")); out.append(("%d-%02d-28" % (y, m), str(c)))
            m += 1
            if m > 12: y, m = y + 1, 1
        return out

    def test_rising_market_is_on(self):
        self.assertEqual(sig.compute(self.rows(range(100, 112)))["signal"], "on")

    def test_falling_market_is_off(self):
        self.assertEqual(sig.compute(self.rows(range(120, 108, -1)))["signal"], "off")

    def test_uses_month_end_and_skips_blank_days(self):
        r = self.rows(range(100, 112)) + [("2025-12-31", ".")]
        self.assertEqual(sig.compute(r)["close"], 111.0)

    def test_unfinished_month_is_ignored(self):
        r = self.rows(range(100, 112)) + [("2026-01-05", "1")]
        self.assertEqual(sig.compute(r, today="2026-01-06")["as_of_month"], "2025-12")

    def test_near_tie_is_flagged(self):
        self.assertTrue(sig.compute(self.rows([100] * 9 + [100.5]))["near_tie"])

    def test_too_little_history_is_an_error(self):
        with self.assertRaises(ValueError): sig.compute(self.rows(range(5)))


class Backtest(unittest.TestCase):
    def test_parser_reads_monthly_block_and_stops_at_annual(self):
        d = tempfile.mkdtemp(); p = os.path.join(d, "f.csv")
        open(p, "w").write("notes\n\n,Mkt-RF,RF\n192607,  1.00,  0.20\n192608, -2.00,  0.20\n\n Annual\n,Mkt-RF,RF\n1927, 5, 1\n")
        f = backtest.french(p, ",Mkt-RF")
        self.assertEqual(len(f), 2); self.assertAlmostEqual(f.loc[192608, "Mkt-RF"], -0.02)

    def test_trend_rule_sits_in_cash_after_a_fall(self):
        import pandas as pd
        ret = pd.Series([0.02] * 12 + [-0.2] + [0.0] * 3); bills = pd.Series([0.001] * 16)
        t = backtest.trend(ret, bills)
        self.assertAlmostEqual(t.iloc[12], -0.2)             # the fall itself is taken
        self.assertAlmostEqual(t.iloc[14], 0.001, places=6)  # then it is in cash

    def test_trend_uses_only_past_data(self):
        import pandas as pd
        a = pd.Series([0.01] * 15 + [0.5]); b = pd.Series([0.01] * 15 + [-0.5]); bills = pd.Series([0.0] * 16)
        self.assertTrue((backtest.trend(a, bills).iloc[:15] == backtest.trend(b, bills).iloc[:15]).all())

    def test_search_prefers_the_better_asset(self):
        import numpy as np, pandas as pd
        real = pd.DataFrame({"x": [0.10] * 30, "y": [0.02] * 30}, index=range(1990, 2020))
        best, n = backtest.search(real, 10)
        self.assertEqual(n, 11); self.assertTrue(all(abs(w[0] - 1.0) < 1e-9 for w in best.values()))


class EntryPoint(unittest.TestCase):
    def test_help_and_unknown_command(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "scout.py")], capture_output=True, text=True)
        self.assertIn("monthly", r.stdout)
        r = subprocess.run([sys.executable, os.path.join(ROOT, "scout.py"), "nope"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)

    def test_plan_command_end_to_end(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "scout.py"), "plan", "--deposit", "1000", "--signal", "off",
                            "--config", os.path.join(ROOT, "engine", "config.json")], capture_output=True, text=True, cwd=ROOT)
        p = json.loads(r.stdout); self.assertEqual(sum(p["pie_weights"].values()), 100); self.assertIn("SGOV", p["pie_weights"])

    def test_config_mixes_add_to_one_and_have_funds(self):
        c = json.load(open(os.path.join(ROOT, "engine", "config.json")))["core"]
        for m in ("software_mix", "no_borrowing_mix", "growth_mix"):
            self.assertAlmostEqual(sum(c[m].values()), 1.0)
            for block in c[m]: self.assertIn(block, c["funds"])


if __name__ == "__main__":
    unittest.main()
