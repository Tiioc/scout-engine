"""Fire drills for the decision engine: feed it crashes, booms and signal flips and check
that it does only what the written policy allows, with a rule named for every step."""
import json, os, sys, unittest
import importlib.util

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "scripts"))


def load(name):
    spec = importlib.util.spec_from_file_location("scout2_" + name, os.path.join(ROOT, "scripts", name + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


pf, sg, bt = load("portfolio"), load("signal"), load("backtest")
CORE = json.load(open(os.path.join(ROOT, "engine", "config.json")))["core"]
ALL_ON = {"default": True}


def balanced(total, signals=ALL_ON, mix="growth_mix"):
    return {k: total * w for k, w in pf.targets(CORE[mix], CORE["funds"], signals).items()}


class Drills(unittest.TestCase):
    def test_market_drop_alone_changes_nothing(self):
        pos = {k: v * 0.70 for k, v in balanced(100000).items()}          # everything down 30%, signals still on
        p = pf.decide(CORE, pos, 1500, ALL_ON, "growth", month=6, peak=100000)
        self.assertFalse(p["rebalance_needed"]); self.assertEqual(p["stage"], "growth")
        self.assertTrue(any("inside what the plan expects" in s for s in p["steps"]))

    def test_exit_signal_moves_only_that_block(self):
        pos = balanced(100000); sig = {"default": True, "MTUM": False}
        p = pf.decide(CORE, pos, 0, sig, "growth", month=6)
        tr = p["rebalance_trades"]
        self.assertAlmostEqual(tr["MTUM"], -pos["MTUM"], places=0); self.assertAlmostEqual(tr["SGOV"], pos["MTUM"], places=0)
        self.assertEqual(set(tr), {"MTUM", "SGOV"})

    def test_signal_back_on_moves_the_block_back(self):
        sig_off = {"default": True, "MTUM": False}; pos = balanced(100000, sig_off)
        tr = pf.decide(CORE, pos, 0, ALL_ON, "growth", month=6)["rebalance_trades"]
        self.assertGreater(tr["MTUM"], 0); self.assertLess(tr["SGOV"], 0)

    def test_fall_past_the_record_steps_down_one_level(self):
        pos = {k: v * 0.40 for k, v in balanced(100000).items()}          # 60% below the high; record is 46%
        p = pf.decide(CORE, pos, 0, ALL_ON, "growth", month=6, peak=100000)
        self.assertEqual(p["stage"], "build"); self.assertTrue(any("[Rule R8]" in s for s in p["steps"]))

    def test_fall_inside_the_record_never_triggers_the_breaker(self):
        for drop in (0.2, 0.35, 0.46, 0.50):
            pos = {k: v * (1 - drop) for k, v in balanced(100000).items()}
            self.assertEqual(pf.decide(CORE, pos, 0, ALL_ON, "growth", month=6, peak=100000)["stage"], "growth")

    def test_growing_past_the_threshold_waits_for_january(self):
        pos = balanced(500000)                                             # 27 times yearly deposits of 18,000
        p = pf.decide(CORE, pos, 1500, ALL_ON, "growth", month=7)
        self.assertEqual(p["stage"], "growth"); self.assertTrue(any("waits for the January review" in s for s in p["steps"]))
        p = pf.decide(CORE, pos, 1500, ALL_ON, "growth", month=1)
        self.assertEqual(p["stage"], "build"); self.assertTrue(any("[Rule R4]" in s for s in p["steps"]))

    def test_never_steps_back_up_to_more_risk(self):
        pos = balanced(50000, mix="build_mix")                             # small again after a fall
        self.assertEqual(pf.decide(CORE, pos, 1500, ALL_ON, "build", month=1)["stage"], "build")

    def test_boom_does_not_chase(self):
        pos = balanced(100000); pos["SSO"] *= 1.3                          # one block ran up, still inside the band
        p = pf.decide(CORE, pos, 1500, ALL_ON, "growth", month=6)
        self.assertFalse(p["rebalance_needed"]); self.assertNotIn("SSO", p["deposit_goes_to"])

    def test_big_run_up_is_trimmed_not_added_to(self):
        pos = balanced(100000); pos["SSO"] *= 2.5
        p = pf.decide(CORE, pos, 0, ALL_ON, "growth", month=6)
        self.assertTrue(p["rebalance_needed"]); self.assertLess(p["rebalance_trades"]["SSO"], 0)

    def test_every_step_cites_the_policy(self):
        pos = {k: v * 0.40 for k, v in balanced(100000).items()}
        for line in pf.decide(CORE, pos, 1500, {"default": True, "AVUV": False}, "growth", month=1, peak=100000)["steps"][:-0 or None]:
            if line.startswith("Set the pie") or line.startswith("No rebalance"): continue
            self.assertRegex(line, r"\[(Rule R[1-8]|Policy [0-9.]+)\]")

    def test_all_exits_on_still_leaves_no_borrowing_and_full_allocation(self):
        t = pf.targets(CORE["growth_mix"], CORE["funds"], {"default": False})
        self.assertAlmostEqual(sum(t.values()), 1.0); self.assertTrue(all(v >= 0 for v in t.values()))

    def test_stage_mixes_get_calmer(self):
        h = CORE["history"]; falls = [h[s["mix"]]["worst_fall"] for s in CORE["stages"]]
        self.assertEqual(falls, sorted(falls, reverse=True))
        lim = [s["below_multiple_of_yearly_deposits"] for s in CORE["stages"]]
        self.assertTrue(lim[0] < lim[1] and lim[2] is None)


class SignalMatchesBacktest(unittest.TestCase):
    def test_live_signal_equals_the_rule_that_was_backtested(self):
        import pandas as pd, random
        rng = random.Random(4); ret = pd.Series([rng.gauss(0.006, 0.05) for _ in range(120)])
        idx = (1 + ret).cumprod(); want = (idx > idx.rolling(10).mean())
        for t in (20, 47, 83, 119):
            rows = []
            for j in range(t + 1):
                y, m = 2000 + j // 12, j % 12 + 1
                rows.append(("%d-%02d-28" % (y, m), str(float(idx.iloc[j]))))
            self.assertEqual(sg.compute(rows)["signal"] == "on", bool(want.iloc[t]))


class WeeklyExit(unittest.TestCase):
    def rows(self, closes, start="2024-01-01"):
        import datetime
        d = datetime.date.fromisoformat(start); out = []
        for c in closes:
            while d.weekday() >= 5: d += datetime.timedelta(days=1)
            out.append((d.isoformat(), str(c))); d += datetime.timedelta(days=1)
        return out

    def test_steady_rise_is_held(self):
        r = sg.weekly_state(self.rows([100 + i * 0.2 for i in range(300)]))
        self.assertEqual(r["signal"], "on"); self.assertIsNone(r["last_flip"])

    def test_clear_fall_exits_and_recovery_returns(self):
        up = [100 + i * 0.2 for i in range(260)]; down = [up[-1] * (1 - 0.01 * i) for i in range(1, 41)]
        r = sg.weekly_state(self.rows(up + down)); self.assertEqual(r["signal"], "off"); self.assertIsNotNone(r["last_flip"])
        back = [down[-1] * (1 + 0.012 * i) for i in range(1, 80)]
        self.assertEqual(sg.weekly_state(self.rows(up + down + back))["signal"], "on")

    def test_small_dip_inside_the_buffer_does_not_exit(self):
        flat = [100.0] * 260 + [99.0] * 15                     # 1% under the average: inside the 2% buffer
        r = sg.weekly_state(self.rows(flat)); self.assertEqual(r["signal"], "on"); self.assertTrue(r["inside_buffer"])

    def test_buffer_prevents_flip_flopping(self):
        import math
        wig = [100 + 1.5 * math.sin(i / 3.0) for i in range(600)]      # wobbles 1.5% around a flat average
        states = set()
        for n in range(260, 600, 5): states.add(sg.weekly_state(self.rows(wig[:n]))["signal"])
        self.assertEqual(len(states), 1)

    def test_week_in_progress_is_ignored(self):
        rows = self.rows([100 + i * 0.2 for i in range(300)]); last = rows[-1][0]
        import datetime
        d = datetime.date.fromisoformat(last)
        while d.weekday() != 2: d += datetime.timedelta(days=1)      # a Wednesday after the data
        crash = rows + [(d.isoformat(), "10")]
        r = sg.weekly_state(crash, today=d.isoformat()); self.assertEqual(r["signal"], "on"); self.assertLess(r["as_of"], d.isoformat())

    def test_only_week_end_closes_decide(self):
        up = [100 + i * 0.2 for i in range(261)]                      # ends on a Monday close
        rows = self.rows(up); dip = rows[:-3] + [(rows[-3][0], "50")] + rows[-2:]   # a mid-week plunge that recovers by the week's end
        self.assertEqual(sg.weekly_state(dip)["signal"], "on")

    def test_too_little_history_is_an_error(self):
        with self.assertRaises(ValueError): sg.weekly_state(self.rows([100] * 50))


class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.lc = load("lifecycle")

    def test_flat_market_ends_with_exactly_the_deposits(self):
        import numpy as np
        R = np.zeros((3, 240)); infl = np.zeros(240); W = self.lc.windows(240, 120)
        s = self.lc.simulate(R, infl, W, {"kind": "size", "m1": 20, "m2": 60, "ratchet": True}, profile=lambda j: 100.0)
        self.assertTrue(np.allclose(s["end"], 12000.0)); self.assertTrue((s["worst_fall"] == 0).all())

    def test_steps_down_once_the_account_is_large_and_never_back(self):
        import numpy as np
        R = np.zeros((3, 600)); R[0, :] = 0.03; R[1, :] = -0.02; infl = np.zeros(600)
        s = self.lc.simulate(R, infl, self.lc.windows(600, 480), {"kind": "size", "m1": 20, "m2": 60, "ratchet": True}, profile=lambda j: 100.0)
        share = s["share_of_time"]; self.assertGreater(share[0], 0); self.assertGreater(share[1], 0.5)

    def test_crash_placed_at_the_end_lowers_the_result(self):
        import numpy as np
        rng = np.random.default_rng(1); R = rng.normal(0.008, 0.03, size=(3, 400)); R[:, 380:] = -0.10; infl = np.zeros(400)
        W = self.lc.windows(360, 240)
        a = self.lc.simulate(R, infl, W, {"kind": "fixed", "level": 0})["end"].mean()
        b = self.lc.simulate(R, infl, self.lc.crash_at(W, np.arange(380, 400), "end"), {"kind": "fixed", "level": 0})["end"].mean()
        self.assertLess(b, a)

    def test_reshuffled_paths_have_the_right_shape_and_stay_in_range(self):
        idx = self.lc.reshuffled(500, 240, n=50)
        self.assertEqual(idx.shape, (50, 240)); self.assertTrue((idx >= 0).all() and (idx < 500).all())


if __name__ == "__main__":
    unittest.main()
