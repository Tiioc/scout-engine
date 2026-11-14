#!/usr/bin/env python3
"""One entry point for every Scout tool.  python3 scout.py <command> [options]

  check     weekly exit signals + the exact portfolio changes   (--deposit 1500 [--holdings file])
  signal    trend signal only
  plan      portfolio changes for a given signal
  size      size one play            calc    financial calculator
  gate      safety gate              check   check an edition file
  score     grade resolved forecasts aggregate pool forecaster samples
  backtest  long-term portfolio backtest      robust  stress tests on the backtest
  simulate  rules simulator          levels  best mix for each loss limit
  lifecycle whole-life test, 10 to 50 years   stress  crashes, booms and rough-up tests
  test      run every automated test
"""
import io, json, os, runpy, subprocess, sys, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
MAP = {"signal": "signal", "plan": "portfolio", "size": "sizing", "calc": "fincalc", "gate": "safety_gate",
       "check": "check_edition", "score": "score", "aggregate": "aggregate", "backtest": "backtest",
       "robust": "robust", "simulate": "simulate", "frequency": "frequency", "realfunds": "realfunds", "levels": "levels", "lifecycle": "lifecycle", "stress": "stress"}


def run(script, args):
    sys.argv = [script] + args
    sys.path.insert(0, os.path.join(HERE, "scripts"))
    runpy.run_path(os.path.join(HERE, "scripts", script + ".py"), run_name="__main__")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(__doc__); return 0
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "test":
        if subprocess.call([sys.executable, "-c", "import pytest"], stderr=subprocess.DEVNULL) == 0:
            return subprocess.call([sys.executable, "-m", "pytest", "-q", os.path.join(HERE, "tests")])
        return subprocess.call([sys.executable, "-m", "unittest", "discover", "-s", os.path.join(HERE, "tests"), "-q"])
    if cmd in ("monthly", "weekly", "check"):
        import datetime
        sig = runpy.run_path(os.path.join(HERE, "scripts", "signal.py"))
        core = json.load(open(os.path.join(HERE, "engine", "config.json")))["core"]
        mix = {}
        for st in core["stages"]: mix.update(core[st["mix"]])                 # signals for every fund any stage could hold
        today = datetime.date.today().isoformat(); out = {}; flags = []
        for block in mix:
            f = core["funds"][block]
            if isinstance(f, dict):
                key = f.get("signal", f["on"])
                if key in out: continue
                if key == "SP500":
                    import csv
                    out[key] = sig["weekly_state"](list(csv.reader(io.StringIO(sig["fetch"]())))[1:], today=today)
                else:
                    out[key] = sig["fund_signal"](key, today=today)
                flags.append("%s=%s" % (key, out[key]["signal"]))
        print(json.dumps({"exit_signals": out}, indent=2))
        state = {}
        sp = os.path.join(HERE, "profile", "state.json")
        if os.path.exists(sp): state = json.load(open(sp))
        extra = [] if "--stage" in args or "--mix" in args else ["--stage", state.get("stage", "growth")]
        if "--month" not in args: extra += ["--month", str(datetime.date.today().month)]
        if state.get("peak") and "--peak" not in args: extra += ["--peak", str(state["peak"])]
        return run("portfolio", ["--signals", ",".join(flags)] + extra + args) or 0
    if cmd not in MAP:
        print("unknown command: %s\n%s" % (cmd, __doc__)); return 2
    try:
        run(MAP[cmd], args)
    except SystemExit as e:
        return e.code or 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
