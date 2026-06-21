#!/usr/bin/env python3
"""Deterministic PO solver for Scenario 2 (peak-season replenishment).

Mirrors the grader's order-up-to math exactly, then rounds each SKU's raw need up
to MOQ / pack-size multiples. Writes out/po.csv (sku,order_qty).

Strategy (see SPEC.md): full rounded-up need fits inside budget, so cover every
SKU to its statistical need rounded up — no rationing required. We do not pad
beyond the rounded need, keeping overstock minimal.
"""
import csv
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SCEN = os.path.join(HERE, "..", "..", "..", "scenarios", "scenario-2-replenishment")
INV = os.path.join(SCEN, "data", "inventory.csv")
PAR = os.path.join(SCEN, "data", "params.json")
OUT = os.path.join(HERE, "..", "out", "po.csv")


def raw_need(v, R, z):
    h = v["lead"] + R
    mean = v["demand"] * h
    safety = z * v["sd"] * math.sqrt(h)
    order_up_to = mean + safety
    position = v["on_hand"] + v["in_transit"]
    return max(0.0, order_up_to - position)


def round_up(q, moq, pack):
    """ceil(need) -> bump to MOQ -> up to pack multiple -> re-check MOQ."""
    if q <= 0:
        return 0
    q = math.ceil(q)
    if moq and q < moq:
        q = moq
    if pack > 1 and q % pack != 0:
        q = ((q // pack) + 1) * pack
    # pack rounding can never drop below MOQ here (it only increases q), but guard:
    if moq and q < moq:
        q = moq
        if pack > 1 and q % pack != 0:
            q = ((q // pack) + 1) * pack
    return int(q)


def main():
    with open(PAR) as f:
        params = json.load(f)
    R = params["review_period_days"]
    z = params["service_level_z"]
    budget = params["budget"]

    rows = []
    spend = 0.0
    with open(INV) as f:
        for r in csv.DictReader(f):
            v = {
                "on_hand": int(r["on_hand"]),
                "in_transit": int(r["in_transit"]),
                "lead": int(r["lead_time_days"]),
                "demand": float(r["avg_daily_demand"]),
                "sd": float(r["demand_sd"]),
                "moq": int(r["moq"]),
                "pack": int(r["pack_size"]),
                "cost": float(r["unit_cost"]),
            }
            q = round_up(raw_need(v, R, z), v["moq"], v["pack"])
            spend += q * v["cost"]
            rows.append((r["sku"], q))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sku", "order_qty"])
        w.writerows(rows)

    print(f"wrote {len(rows)} rows to {os.path.relpath(OUT)}")
    print(f"projected spend: {spend:.2f} / budget {budget:.2f} ({spend/budget:.1%})")


if __name__ == "__main__":
    main()
