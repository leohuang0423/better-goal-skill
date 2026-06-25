#!/usr/bin/env python3
"""Deterministic synthetic data generator for the three e-commerce benchmark
scenarios. Seeded so the benchmark is fully reproducible: same data every run.

Usage:
  python benchmark/generate_data.py                  # canonical fixtures
  python benchmark/generate_data.py --seed-offset 100 --dest benchmark/seeds/seed1
      # independent variant under a different root (for multi-seed hardening)
"""
import argparse
import csv
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "scenarios")


def ensure(p):
    os.makedirs(p, exist_ok=True)
    return p


# ---------------------------------------------------------------- Scenario 1
# Catalog repricing: each SKU has cost, current price, MAP floor, competitor
# price, 30-day units, and a hold flag.
def gen_repricing(seed=11, root=SC):
    rng = random.Random(seed)
    d = ensure(os.path.join(root, "scenario-1-repricing", "data"))
    rows = []
    for i in range(1, 201):
        cost = round(rng.uniform(4, 80), 2)
        margin = rng.uniform(0.25, 0.6)
        price = round(cost / (1 - margin), 2)
        mapf = round(cost * rng.uniform(1.05, 1.25), 2)        # MAP >= cost
        # competitor sits in a band around our price
        comp = round(price * rng.uniform(0.82, 1.12), 2)
        units = int(max(0, rng.gauss(120, 90)))
        hold = 1 if rng.random() < 0.08 else 0
        rows.append({
            "sku": f"SKU{i:04d}",
            "cost": cost,
            "current_price": price,
            "map_floor": mapf,
            "competitor_price": comp,
            "units_30d": units,
            "hold": hold,
        })
    with open(os.path.join(d, "skus.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return len(rows)


# ---------------------------------------------------------------- Scenario 2
# Replenishment: per-SKU on-hand, in-transit, lead-time, daily demand stats,
# MOQ, pack size, unit cost, and a budget cap. Agent must produce PO quantities
# that avoid stockouts over the lead time + review period without overspending.
def gen_replenishment(seed=23, root=SC):
    rng = random.Random(seed)
    d = ensure(os.path.join(root, "scenario-2-replenishment", "data"))
    rows = []
    for i in range(1, 121):
        demand = round(max(0.2, rng.gauss(8, 6)), 2)           # units/day
        demand_sd = round(max(0.1, demand * rng.uniform(0.2, 0.6)), 2)
        lead = rng.choice([7, 10, 14, 21, 30])
        on_hand = int(max(0, rng.gauss(demand * lead * 0.6, demand * 5)))
        in_transit = int(max(0, rng.gauss(demand * 5, demand * 3)))
        moq = rng.choice([0, 0, 10, 24, 50])
        pack = rng.choice([1, 1, 6, 12])
        unit_cost = round(rng.uniform(2, 40), 2)
        rows.append({
            "sku": f"SKU{i:04d}",
            "on_hand": on_hand,
            "in_transit": in_transit,
            "lead_time_days": lead,
            "avg_daily_demand": demand,
            "demand_sd": demand_sd,
            "moq": moq,
            "pack_size": pack,
            "unit_cost": unit_cost,
        })
    with open(os.path.join(d, "inventory.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    params = {
        "review_period_days": 14,
        "service_level_z": 1.65,      # ~95% service level
        "budget": 500000.0,
    }
    with open(os.path.join(d, "params.json"), "w") as f:
        json.dump(params, f, indent=2)
    return len(rows)


# ---------------------------------------------------------------- Scenario 3
# Listing optimization: raw product records the agent must rewrite into compliant
# listings (title <=80 chars, >=5 bullets, meta description, no banned claims,
# must preserve given factual specs).
def gen_listings(seed=37, root=SC):
    rng = random.Random(seed)
    d = ensure(os.path.join(root, "scenario-3-listings", "data"))
    brands = ["Acme", "NorthPeak", "Lumen", "Cedar&Co", "Vela"]
    cats = ["water bottle", "yoga mat", "desk lamp", "backpack", "knife set",
            "headphones", "coffee grinder", "rain jacket"]
    mats = ["stainless steel", "cork", "aluminum", "recycled polyester", "bamboo"]
    products = []
    for i in range(1, 41):
        brand = rng.choice(brands)
        cat = rng.choice(cats)
        cap = rng.choice([350, 500, 750, 1000])
        color = rng.choice(["black", "slate", "sand", "forest", "white"])
        warranty = rng.choice([1, 2, 5])
        mat = rng.choice(mats)
        weight = round(rng.uniform(0.2, 2.5), 2)
        specs = {
            "capacity_ml": cap,
            "color": color,
            "material": mat,
            "warranty_years": warranty,
            "weight_kg": weight,
        }
        products.append({
            "id": f"P{i:03d}",
            "brand": brand,
            "category": cat,
            "raw_title": f"{brand} {cat} {color} {cap}ml",   # messy short title
            "specs": specs,
        })
    with open(os.path.join(d, "products.json"), "w") as f:
        json.dump(products, f, indent=2)
    # banned-claims list the QC grader enforces
    with open(os.path.join(d, "banned_claims.txt"), "w") as f:
        f.write("\n".join([
            "cures", "cure", "FDA approved", "100% guaranteed", "best in the world",
            "miracle", "clinically proven", "lifetime guarantee", "#1 rated",
        ]) + "\n")
    return len(products)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-offset", type=int, default=0,
                    help="added to each scenario's base seed for an independent variant")
    ap.add_argument("--dest", default=SC,
                    help="root dir to write scenario-*/data under (default: canonical)")
    ap.add_argument("--only", choices=["1", "2", "3"], action="append",
                    help="generate only these scenarios (repeatable)")
    a = ap.parse_args()
    o, root = a.seed_offset, a.dest
    want = set(a.only) if a.only else {"1", "2", "3"}
    if "1" in want:
        print(f"scenario-1-repricing: {gen_repricing(11 + o, root)} SKUs")
    if "2" in want:
        print(f"scenario-2-replenishment: {gen_replenishment(23 + o, root)} SKUs")
    if "3" in want:
        print(f"scenario-3-listings: {gen_listings(37 + o, root)} products")
