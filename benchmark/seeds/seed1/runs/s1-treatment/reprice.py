#!/usr/bin/env python3
"""Repricing engine for Scenario 1.

Strategy (see SPEC.md):
  For each ACTIVE (hold=0) SKU, target the competitor price to be competitive,
  then clamp into the legal band:
      lower = max(cost, map_floor, current*(1-MOVE_CAP))
      upper = current*(1+MOVE_CAP)
  Round to 2 dp. hold=1 SKUs are left out of the plan entirely (untouched).

  The grader requires projected BLENDED margin (ratio, unit-weighted) >= current.
  Cutting prices toward competitors lowers that ratio, so after the first pass we
  repair: while new blended margin < current, take the SKU whose cut hurt the
  blended ratio most (largest revenue-weighted margin-ratio drop) and pull its
  price back up toward its current price, until margin_ok holds. Prices are only
  ever pulled UP during repair, so all floor/move constraints stay satisfied.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SKUS = os.path.join(HERE, "..", "..", "scenario-1-repricing", "data", "skus.csv")
OUT = os.path.join(HERE, "out", "reprice.csv")
MOVE_CAP = 0.15


def load(p):
    rows = {}
    with open(p) as f:
        for r in csv.DictReader(f):
            rows[r["sku"]] = {
                "cost": float(r["cost"]),
                "current_price": float(r["current_price"]),
                "map_floor": float(r["map_floor"]),
                "competitor_price": float(r["competitor_price"]),
                "units_30d": int(r["units_30d"]),
                "hold": int(r["hold"]),
            }
    return rows


def blended_margin(active, price_of):
    num = den = 0.0
    for s, v in active.items():
        p = price_of(s, v)
        num += (p - v["cost"]) * v["units_30d"]
        den += p * v["units_30d"]
    return (num / den) if den else 0.0


def main():
    skus = load(SKUS)
    active = {s: v for s, v in skus.items() if v["hold"] == 0}

    cur_margin = blended_margin(active, lambda s, v: v["current_price"])

    plan = {}
    for s, v in active.items():
        cur = v["current_price"]
        lower = max(v["cost"], v["map_floor"], cur * (1 - MOVE_CAP))
        upper = cur * (1 + MOVE_CAP)
        # Target competitor price to be competitive; clamp into the legal band.
        target = v["competitor_price"]
        price = min(max(target, lower), upper)
        # Keep a tiny epsilon above floors so 2dp rounding never dips below.
        price = round(price, 2)
        if price < round(lower, 2):
            price = round(lower + 0.005, 2)
        plan[s] = price

    # Repair margin: pull the most-damaging cuts back up toward current price
    # until blended margin >= current. Pulling up only relaxes constraints.
    def new_margin():
        return blended_margin(active, lambda s, v: plan[s])

    # Repair priority: pull up cut SKUs that are ALREADY non-competitive first
    # (price > competitor — bumping them loses no competitiveness), then SKUs
    # where the cut bought the least competitiveness per margin dollar. We bump
    # toward current only as far as needed to restore margin parity.
    def comp(s):
        return plan[s] <= active[s]["competitor_price"] + 0.01

    guard = 0
    while new_margin() < cur_margin - 1e-9 and guard < 100000:
        guard += 1
        candidates = [s for s in active if plan[s] < active[s]["current_price"] - 0.001]
        if not candidates:
            break
        # Tier 1: bumping to current would NOT cross the competitor line, or it is
        # already above it -> no competitiveness cost. Among those, max margin gain.
        # Tier 2: would lose competitiveness -> defer; pick min margin-dollars-per-
        # competitiveness so we sacrifice the cheapest competitive SKUs last.
        def key(s):
            v = active[s]
            cur = v["current_price"]
            gain = v["units_30d"] * (cur - plan[s])
            currently_comp = comp(s)
            would_stay_comp = cur <= v["competitor_price"] + 0.01
            loses_comp = currently_comp and not would_stay_comp
            # tier 0 (no comp loss) sorts before tier 1 (comp loss);
            # within tier, larger margin gain first.
            return (1 if loses_comp else 0, -gain)
        best = min(candidates, key=key)
        plan[best] = round(active[best]["current_price"], 2)

    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sku", "new_price"])
        for s in sorted(plan):
            w.writerow([s, f"{plan[s]:.2f}"])

    print(f"active={len(active)} written={len(plan)} "
          f"cur_margin={cur_margin:.4f} new_margin={new_margin():.4f}")


if __name__ == "__main__":
    main()
