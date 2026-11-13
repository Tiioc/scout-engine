#!/usr/bin/env python3
"""One entry point for every Scout tool.  python3 scout.py <command> [options]

  monthly   trend signal + the exact portfolio changes   (--deposit 1500 [--holdings file])
  signal    trend signal only
  plan      portfolio changes for a given signal
  size      size one play            calc    financial calculator
  gate      safety gate              check   check an edition file
  score     grade resolved forecasts aggregate pool forecaster samples
  backtest  long-term portfolio backtest      robust  stress tests on the backtest
  simulate  rules simulator          test    run every automated test
"""
import io, json, os, runpy, subprocess, sys, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
MAP = {"signal": "signal", "plan": "portfolio", "size": "sizing", "calc": "fincalc", "gate": "safety_gate",
       "check": "check_edition", "score": "score", "aggregate": "aggregate", "backtest": "backtest",
       "robust": "robust", "simulate": "simulate"}


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
    if cmd == "monthly":
        sys.path.insert(0, os.path.join(HERE, "scripts")); import signal as _s  # noqa
        sig = runpy.run_path(os.path.join(HERE, "scripts", "signal.py"))
        import csv, datetime
        rows = list(csv.reader(io.StringIO(sig["fetch"]())))[1:]
        s = sig["compute"](rows, today=datetime.date.today().isoformat())
        print(json.dumps({"trend": s}, indent=2))
        return run("portfolio", ["--signal", s["signal"]] + args) or 0
    if cmd not in MAP:
        print("unknown command: %s\n%s" % (cmd, __doc__)); return 2
    try:
        run(MAP[cmd], args)
    except SystemExit as e:
        return e.code or 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
