#!/usr/bin/env python3
"""Grader for Scenario 1 (catalog repricing).

Reads the SKU fixture and an agent-produced plan, then enforces hard pricing
policy and scores quality. Exit 0 iff all hard constraints pass.

Usage: python check_reprice.py [--skus PATH] [--plan PATH] [--json]
Plan format: CSV with columns `sku,new_price` (extra columns ignored).
"""
import argparse
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEF_SKUS = os.path.join(HERE, "..", "data", "skus.csv")
DEF_PLAN = os.path.join(HERE, "..", "out", "reprice.csv")
MOVE_CAP = 0.15  # +/- 15% per-SKU move


def load_skus(p):
    out = {}
    with open(p) as f:
        for r in csv.DictReader(f):
            out[r["sku"]] = {
                "cost": float(r["cost"]),
                "current_price": float(r["current_price"]),
                "map_floor": float(r["map_floor"]),
                "competitor_price": float(r["competitor_price"]),
                "units_30d": int(r["units_30d"]),
                "hold": int(r["hold"]),
            }
    return out


def load_plan(p):
    out = {}
    if not os.path.exists(p):
        return out
    with open(p) as f:
        for r in csv.DictReader(f):
            sku = (r.get("sku") or "").strip()
            raw = (r.get("new_price") or r.get("price") or "").strip()
            if not sku or not raw:
                continue
            try:
                out[sku] = round(float(raw), 2)
            except ValueError:
                continue
    return out


def grade(skus, plan):
    active = {s: v for s, v in skus.items() if v["hold"] == 0}
    violations = []

    covered = [s for s in active if s in plan]
    coverage = len(covered) / len(active) if active else 0.0

    below_floor = []     # below cost or MAP
    over_move = []       # moved more than +/-15%
    touched_hold = []    # modified a hold SKU vs leaving it / matching current

    for s, v in skus.items():
        if s not in plan:
            continue
        np = plan[s]
        if v["hold"] == 1:
            if abs(np - v["current_price"]) > 0.01:
                touched_hold.append(s)
            continue
        if np < round(v["cost"], 2) - 0.001 or np < round(v["map_floor"], 2) - 0.001:
            below_floor.append(s)
        if abs(np - v["current_price"]) > v["current_price"] * MOVE_CAP + 0.01:
            over_move.append(s)

    # projected blended margin: weight by 30d units (use new price where set,
    # else current). Margin $ = (price - cost) * units.
    def blended_margin(price_fn):
        num = den = 0.0
        for s, v in active.items():
            price = price_fn(s, v)
            num += (price - v["cost"]) * v["units_30d"]
            den += price * v["units_30d"]
        return (num / den) if den else 0.0

    cur_margin = blended_margin(lambda s, v: v["current_price"])
    new_margin = blended_margin(lambda s, v: plan.get(s, v["current_price"]))
    margin_ok = new_margin >= cur_margin - 1e-9

    # competitiveness: share of covered active SKUs priced <= competitor
    comp_ok = sum(1 for s in covered if plan[s] <= active[s]["competitor_price"] + 0.01)
    competitiveness = comp_ok / len(covered) if covered else 0.0

    hard_pass = (
        coverage >= 0.999
        and not below_floor
        and not over_move
        and not touched_hold
        and margin_ok
    )

    # score (0-100): coverage 30, then a 70-pt quality block (no floor breaches
    # 25, no over-move 15, hold respected 10, margin 10, competitiveness 10).
    # The quality block is scaled by coverage so a do-nothing plan scores ~0
    # rather than earning credit for vacuously "not violating" anything.
    quality = (
        25 * (0 if below_floor else 1)
        + 15 * (0 if over_move else 1)
        + 10 * (0 if touched_hold else 1)
        + 10 * (1 if margin_ok else 0)
        + 10 * competitiveness
    )
    score = 30 * coverage + coverage * quality

    return {
        "hard_pass": hard_pass,
        "score": round(score, 1),
        "coverage": round(coverage, 4),
        "below_floor_count": len(below_floor),
        "over_move_count": len(over_move),
        "touched_hold_count": len(touched_hold),
        "current_blended_margin": round(cur_margin, 4),
        "new_blended_margin": round(new_margin, 4),
        "margin_ok": margin_ok,
        "competitiveness": round(competitiveness, 4),
        "active_skus": len(active),
        "priced": len(covered),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skus", default=DEF_SKUS)
    ap.add_argument("--plan", default=DEF_PLAN)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    res = grade(load_skus(a.skus), load_plan(a.plan))
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        for k, v in res.items():
            print(f"{k}: {v}")
    sys.exit(0 if res["hard_pass"] else 1)


if __name__ == "__main__":
    main()
