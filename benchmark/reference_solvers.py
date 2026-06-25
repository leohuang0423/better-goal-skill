#!/usr/bin/env python3
"""Reference ("oracle") solvers for all three scenarios.

These are NOT what the agents run — they exist to prove each grader's high score
is reachable and to establish an expert-baseline ceiling. Run after generate_data.py:
    python benchmark/reference_solvers.py
Writes out/*.ref.csv|json next to each scenario and prints grader scores.
"""
import csv
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "scenarios")


def solve_repricing():
    base = os.path.join(SC, "scenario-1-repricing")
    rows = list(csv.DictReader(open(os.path.join(base, "data", "skus.csv"))))
    skus = {}
    price = {}
    for r in rows:
        s = r["sku"]
        skus[s] = dict(cost=float(r["cost"]), cur=float(r["current_price"]),
                       mapf=float(r["map_floor"]), comp=float(r["competitor_price"]),
                       units=int(r["units_30d"]), hold=int(r["hold"]))
        price[s] = skus[s]["cur"]            # start from current (margin == current)

    def margin_num_den():
        num = den = 0.0
        for s, v in skus.items():
            if v["hold"]:
                continue
            num += (price[s] - v["cost"]) * v["units"]
            den += price[s] * v["units"]
        return num, den
    n0, d0 = margin_num_den()
    cur_margin = n0 / d0 if d0 else 0

    # Step 1: raise underpriced active SKUs toward just under competitor (within
    # +15% and above floors). Pure win: more margin AND still competitive.
    for s, v in skus.items():
        if v["hold"]:
            continue
        floor = max(v["cost"], v["mapf"]); hi = v["cur"] * 1.15
        if v["cur"] < v["comp"] - 0.01:
            price[s] = round(min(v["comp"] - 0.01, hi, max(floor, v["cur"]) * 1e9), 2)
            price[s] = round(max(floor, min(v["comp"] - 0.01, hi)), 2)

    # Step 2: spend the margin surplus funding cuts on overpriced SKUs, highest
    # velocity first, while keeping blended margin >= current.
    over = sorted([s for s, v in skus.items()
                   if not v["hold"] and v["cur"] > v["comp"] + 0.01],
                  key=lambda s: -skus[s]["units"])
    for s in over:
        v = skus[s]
        floor = max(v["cost"], v["mapf"]); lo = v["cur"] * 0.85
        target = round(max(floor, lo, v["comp"] - 0.01), 2)
        old = price[s]; price[s] = target
        num, den = margin_num_den()
        if (num / den if den else 0) < cur_margin - 1e-9:
            price[s] = old                   # revert: this cut breaks margin floor

    out = [(s, round(price[s], 2)) for s in skus]
    od = os.path.join(base, "out"); os.makedirs(od, exist_ok=True)
    p = os.path.join(od, "reprice.ref.csv")
    with open(p, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["sku", "new_price"]); w.writerows(out)
    return base, "tools/check_reprice.py", p


def solve_replenishment():
    base = os.path.join(SC, "scenario-2-replenishment")
    inv = list(csv.DictReader(open(os.path.join(base, "data", "inventory.csv"))))
    params = json.load(open(os.path.join(base, "data", "params.json")))
    R, z, budget = params["review_period_days"], params["service_level_z"], params["budget"]
    plan = {}
    items = []
    for r in inv:
        v = {k: r[k] for k in r}
        demand = float(r["avg_daily_demand"]); sd = float(r["demand_sd"])
        lead = int(r["lead_time_days"]); moq = int(r["moq"]); pack = int(r["pack_size"])
        on = int(r["on_hand"]); it = int(r["in_transit"]); cost = float(r["unit_cost"])
        horizon = lead + R
        need = max(0.0, demand * horizon + z * sd * math.sqrt(horizon) - (on + it))
        q = math.ceil(need)
        if pack > 1 and q % pack:
            q += pack - (q % pack)
        if moq and 0 < q < moq:
            q = moq
        items.append((r["sku"], q, cost, need))
    # greedy under budget: prioritize SKUs by coverage shortfall value
    spend = sum(q * c for _, q, c, _ in items)
    if spend > budget:
        # trim from lowest-need-density first (keep high-demand coverage)
        items.sort(key=lambda x: x[3])     # ascending need; trim small-need first
        for i, (s, q, c, need) in enumerate(items):
            if spend <= budget:
                break
            items[i] = (s, 0, c, need); spend -= q * c
    for s, q, c, _ in items:
        plan[s] = q
    od = os.path.join(base, "out"); os.makedirs(od, exist_ok=True)
    p = os.path.join(od, "po.ref.csv")
    with open(p, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["sku", "order_qty"])
        for r in inv:
            w.writerow([r["sku"], plan[r["sku"]]])
    return base, "tools/check_replenish.py", p


def solve_listings():
    base = os.path.join(SC, "scenario-3-listings")
    prods = json.load(open(os.path.join(base, "data", "products.json")))
    out = []
    for p in prods:
        s = p["specs"]; brand = p["brand"]; cat = p["category"]
        title = f"{brand} {cat.title()} - {s['color'].title()} {s['material'].title()} {s['capacity_ml']}ml"[:80]
        bullets = [
            f"Capacity: {s['capacity_ml']}ml for everyday use",
            f"Made from durable {s['material']}",
            f"Color: {s['color']}",
            f"Backed by a {s['warranty_years']}-year warranty",
            f"Lightweight at {s['weight_kg']}kg",
            f"From {brand}, designed for reliable daily performance",
        ]
        meta = (f"{brand} {cat} in {s['color']} {s['material']}, {s['capacity_ml']}ml, "
                f"{s['warranty_years']}-year warranty. Durable everyday quality.")[:160]
        if len(meta) < 50:
            meta = (meta + " Shop now for dependable performance.")[:160]
        out.append({"id": p["id"], "title": title, "bullets": bullets,
                    "meta_description": meta})
    od = os.path.join(base, "out"); os.makedirs(od, exist_ok=True)
    pth = os.path.join(od, "listings.ref.json")
    json.dump(out, open(pth, "w"), indent=2)
    return base, "tools/qc_listings.py", pth


def run(base, grader, plan):
    flag = "--plan" if "qc_listings" not in grader else "--out"
    r = subprocess.run([sys.executable, os.path.join(base, grader), flag, plan, "--json"],
                       capture_output=True, text=True)
    return json.loads(r.stdout)


if __name__ == "__main__":
    for solver in (solve_repricing, solve_replenishment, solve_listings):
        base, grader, plan = solver()
        res = run(base, grader, plan)
        name = os.path.basename(base)
        print(f"{name}: hard_pass={res['hard_pass']} score={res['score']}")
