#!/usr/bin/env python3
"""Grade every run under benchmark/runs/ and print the control-vs-treatment table.

Usage: python benchmark/score_all.py
Assumes generate_data.py has been run and runs/<scenario>-<arm>/out/ exist.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "scenarios")
RUNS = os.path.join(HERE, "runs")

# scenario -> (grader path, plan-flag, run output relative path)
GRADERS = {
    "s1": (os.path.join(SC, "scenario-1-repricing", "tools", "check_reprice.py"),
           "--plan", "out/reprice.csv"),
    "s2": (os.path.join(SC, "scenario-2-replenishment", "tools", "check_replenish.py"),
           "--plan", "out/po.csv"),
    "s3": (os.path.join(SC, "scenario-3-listings", "tools", "qc_listings.py"),
           "--out", "out/listings.json"),
}
NAMES = {"s1": "Repricing", "s2": "Replenishment", "s3": "Listings"}


def grade(scenario, arm):
    grader, flag, rel = GRADERS[scenario]
    plan = os.path.join(RUNS, f"{scenario}-{arm}", rel)
    r = subprocess.run([sys.executable, grader, flag, plan, "--json"],
                       capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"hard_pass": False, "score": 0.0, "error": r.stderr.strip()[:200]}


def main():
    rows = []
    for s in ("s1", "s2", "s3"):
        c = grade(s, "control")
        t = grade(s, "treatment")
        rows.append((s, c, t))

    w = 14
    print(f"{'Scenario':<16}{'Control pass':<14}{'Control score':<15}"
          f"{'Treat pass':<13}{'Treat score':<13}{'Δscore':<8}")
    print("-" * 79)
    cp = tp = cs = ts = 0
    for s, c, t in rows:
        d = t["score"] - c["score"]
        cs += c["score"]; ts += t["score"]
        cp += int(c["hard_pass"]); tp += int(t["hard_pass"])
        print(f"{NAMES[s]:<16}{str(c['hard_pass']):<14}{c['score']:<15}"
              f"{str(t['hard_pass']):<13}{t['score']:<13}{d:+.1f}")
    print("-" * 79)
    print(f"{'TOTAL':<16}{cp}/3 pass{'':<6}{cs/3:<15.1f}{tp}/3 pass{'':<5}"
          f"{ts/3:<13.1f}{(ts-cs)/3:+.1f}")


if __name__ == "__main__":
    main()
