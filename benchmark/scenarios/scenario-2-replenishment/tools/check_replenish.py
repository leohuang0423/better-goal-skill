#!/usr/bin/env python3
"""Grader for Scenario 2 (inventory replenishment).

Computes the statistically correct order-up-to need per SKU and grades the
agent's PO plan on stockout coverage, MOQ/pack compliance, and budget. Exit 0
iff all hard constraints pass.

Usage: python check_replenish.py [--inv PATH] [--params PATH] [--plan PATH] [--json]
Plan format: CSV with columns `sku,order_qty`.
"""
import argparse
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEF_INV = os.path.join(HERE, "..", "data", "inventory.csv")
DEF_PAR = os.path.join(HERE, "..", "data", "params.json")
DEF_PLAN = os.path.join(HERE, "..", "out", "po.csv")


def load_inv(p):
    out = {}
    with open(p) as f:
        for r in csv.DictReader(f):
            out[r["sku"]] = {
                "on_hand": int(r["on_hand"]),
                "in_transit": int(r["in_transit"]),
                "lead": int(r["lead_time_days"]),
                "demand": float(r["avg_daily_demand"]),
                "sd": float(r["demand_sd"]),
                "moq": int(r["moq"]),
                "pack": int(r["pack_size"]),
                "cost": float(r["unit_cost"]),
            }
    return out


def load_plan(p):
    out = {}
    if not os.path.exists(p):
        return out
    with open(p) as f:
        for r in csv.DictReader(f):
            sku = (r.get("sku") or "").strip()
            raw = (r.get("order_qty") or r.get("qty") or "").strip()
            if not sku or not raw:
                continue
            try:
                out[sku] = int(float(raw))
            except ValueError:
                continue
    return out


def target_need(v, R, z):
    """Order-up-to level over lead+review, minus current position."""
    horizon = v["lead"] + R
    mean = v["demand"] * horizon
    safety = z * v["sd"] * math.sqrt(horizon)
    order_up_to = mean + safety
    position = v["on_hand"] + v["in_transit"]
    return max(0.0, order_up_to - position)


def grade(inv, params, plan):
    R = params["review_period_days"]
    z = params["service_level_z"]
    budget = params["budget"]

    spend = 0.0
    moq_viol = pack_viol = neg_viol = 0
    covered_need = total_need = 0.0
    overstock = 0.0
    skus_short = 0

    for s, v in inv.items():
        q = plan.get(s, 0)
        if q < 0:
            neg_viol += 1
            q = 0
        spend += q * v["cost"]
        if q > 0:
            if v["moq"] and q < v["moq"]:
                moq_viol += 1
            if v["pack"] > 1 and q % v["pack"] != 0:
                pack_viol += 1
        need = target_need(v, R, z)
        total_need += need
        covered_need += min(q, need)
        if q + 1e-9 < need:
            skus_short += 1
        overstock += max(0.0, q - need)

    coverage = covered_need / total_need if total_need else 1.0
    fill_rate = 1 - skus_short / len(inv) if inv else 1.0
    budget_ok = spend <= budget + 1e-6
    # overstock penalty: fraction of spend that is excess vs need
    overstock_cost = sum(
        max(0, plan.get(s, 0) - target_need(v, R, z)) * v["cost"]
        for s, v in inv.items()
    )
    overstock_ratio = overstock_cost / spend if spend else 0.0

    hard_pass = (
        budget_ok
        and neg_viol == 0
        and moq_viol == 0
        and pack_viol == 0
        and coverage >= 0.90
    )

    # score: demand coverage 45, sku fill rate 20, budget 10, MOQ/pack 10,
    # leanness (low overstock) 15. The 35-pt constraint/leanness block is scaled
    # by how much real coverage was achieved, so an empty plan (which trivially
    # "violates nothing" and has zero overstock) does not earn credit for
    # inaction.
    fulfilled = min(1.0, coverage)
    score = (
        45 * fulfilled
        + 20 * fill_rate
        + fulfilled * (
            10 * (1 if budget_ok else 0)
            + 10 * (1 if (moq_viol == 0 and pack_viol == 0 and neg_viol == 0) else 0)
            + 15 * (1 - min(1.0, overstock_ratio))
        )
    )

    return {
        "hard_pass": hard_pass,
        "score": round(score, 1),
        "demand_coverage": round(coverage, 4),
        "sku_fill_rate": round(fill_rate, 4),
        "skus_short": skus_short,
        "spend": round(spend, 2),
        "budget": budget,
        "budget_ok": budget_ok,
        "moq_violations": moq_viol,
        "pack_violations": pack_viol,
        "negative_qty": neg_viol,
        "overstock_ratio": round(overstock_ratio, 4),
        "skus": len(inv),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inv", default=DEF_INV)
    ap.add_argument("--params", default=DEF_PAR)
    ap.add_argument("--plan", default=DEF_PLAN)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with open(a.params) as f:
        params = json.load(f)
    res = grade(load_inv(a.inv), params, load_plan(a.plan))
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        for k, v in res.items():
            print(f"{k}: {v}")
    sys.exit(0 if res["hard_pass"] else 1)


if __name__ == "__main__":
    main()
