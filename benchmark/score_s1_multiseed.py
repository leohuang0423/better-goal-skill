#!/usr/bin/env python3
"""Aggregate the Scenario-1 (repricing) replication: grade the canonical run plus
every seed under benchmark/seeds/, for both arms, and print a control-vs-treatment
table with hard-pass rate and mean score.

Usage: python benchmark/score_s1_multiseed.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GRADER = os.path.join(HERE, "scenario-1-repricing", "tools", "check_reprice.py")\
    if False else os.path.join(HERE, "scenarios", "scenario-1-repricing", "tools", "check_reprice.py")


def grade(skus, plan):
    if not os.path.exists(plan):
        return None
    r = subprocess.run([sys.executable, GRADER, "--skus", skus, "--plan", plan, "--json"],
                       capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"hard_pass": False, "score": 0.0}


def instances():
    # (label, skus_path, run_root)
    out = [("canonical",
            os.path.join(HERE, "scenarios", "scenario-1-repricing", "data", "skus.csv"),
            os.path.join(HERE, "runs"))]
    seeds_dir = os.path.join(HERE, "seeds")
    if os.path.isdir(seeds_dir):
        for s in sorted(os.listdir(seeds_dir)):
            skus = os.path.join(seeds_dir, s, "scenario-1-repricing", "data", "skus.csv")
            runs = os.path.join(seeds_dir, s, "runs")
            if os.path.exists(skus):
                out.append((s, skus, runs))
    return out


def main():
    rows = []
    for label, skus, runs in instances():
        c = grade(skus, os.path.join(runs, "s1-control", "out", "reprice.csv"))
        t = grade(skus, os.path.join(runs, "s1-treatment", "out", "reprice.csv"))
        rows.append((label, c, t))

    print(f"{'Instance':<12}{'Ctl pass':<10}{'Ctl score':<11}"
          f"{'Trt pass':<10}{'Trt score':<11}{'Δ':<8}")
    print("-" * 62)
    cp = tp = 0; cs = []; ts = []; n = 0
    for label, c, t in rows:
        if not c or not t:
            print(f"{label:<12}{'(pending/missing output)'}")
            continue
        n += 1
        cp += int(c["hard_pass"]); tp += int(t["hard_pass"])
        cs.append(c["score"]); ts.append(t["score"])
        d = t["score"] - c["score"]
        print(f"{label:<12}{str(c['hard_pass']):<10}{c['score']:<11}"
              f"{str(t['hard_pass']):<10}{t['score']:<11}{d:+.1f}")
    if n:
        print("-" * 62)
        mc = sum(cs) / n; mt = sum(ts) / n
        print(f"{'MEAN/RATE':<12}{f'{cp}/{n}':<10}{mc:<11.1f}{f'{tp}/{n}':<10}"
              f"{mt:<11.1f}{mt-mc:+.1f}")


if __name__ == "__main__":
    main()
