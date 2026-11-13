#!/usr/bin/env python3
"""Check a weekly edition against the edition rules. Plain code, no AI.

Checks:
  - at most three plays
  - every play has Forecast, Cost, Wrong if and Exit lines
  - every play's Forecast line contains a probability
  - no banned filler phrases anywhere

Usage:
    python3 scripts/check_edition.py editions/2026-11-16.md
Exit code 0 = pass, 1 = fail.
"""
import re
import sys

MAX_PLAYS = 3
REQUIRED = ["**Forecast:**", "**Cost:**", "**Wrong if:**", "**Exit:**"]
BANNED = [
    "build a budget", "budgeting tip", "pay yourself first",
    "live below your means", "network more", "skip the latte",
]
PLAY_HEADER = re.compile(r"^##\s+Play\b", re.IGNORECASE)
SECTION_HEADER = re.compile(r"^##\s+")
PROBABILITY = re.compile(r"\d{1,3}(\.\d+)?\s*%")


def split_plays(text):
    plays, current = [], None
    for line in text.splitlines():
        if PLAY_HEADER.match(line):
            if current is not None:
                plays.append(current)
            current = [line]
        elif SECTION_HEADER.match(line):
            if current is not None:
                plays.append(current)
                current = None
        elif current is not None:
            current.append(line)
    if current is not None:
        plays.append(current)
    return ["\n".join(p) for p in plays]


def check(text):
    problems = []
    plays = split_plays(text)
    if len(plays) > MAX_PLAYS:
        problems.append("Too many plays: %d (maximum %d)" % (len(plays), MAX_PLAYS))
    for i, play in enumerate(plays, 1):
        for field in REQUIRED:
            if field not in play:
                problems.append("Play %d is missing %s" % (i, field))
        for line in play.splitlines():
            if line.startswith("**Forecast:**") and not PROBABILITY.search(line):
                problems.append("Play %d has no probability on its Forecast line" % i)
    lower = text.lower()
    for phrase in BANNED:
        if phrase in lower:
            problems.append("Filler is banned: found '%s'" % phrase)
    if not plays and "no strong play this week" not in lower:
        problems.append("No plays and no 'No strong play this week' statement")
    return problems


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: check_edition.py <edition.md>")
        return 1
    with open(argv[0]) as f:
        problems = check(f.read())
    if problems:
        print("FAIL")
        for p in problems:
            print("- " + p)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
