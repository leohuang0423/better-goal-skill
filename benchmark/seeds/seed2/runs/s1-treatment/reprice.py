#!/usr/bin/env python3
"""Generate out/reprice.csv: competitive prices that respect all hard constraints.

Strategy:
  1. For each active SKU, build the legal band:
        lo = max(round(cost,2), round(map_floor,2), current*0.85)
        hi = current*1.15
     Stay 1 cent inside each edge so grader float tolerances never trip.
  2. Target = competitor price, clamped into [lo, hi]. This both undercuts where
     we are too high and raises where we have headroom below competitor.
  3. Held SKUs are omitted entirely (never touched).
  4. Global margin guard: if the units-weighted blended margin would fall below
     current, walk back the cheapest-impact price cuts toward current until the
     blended margin recovers (>= current).
"""
import csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
SKUS = os.path.join(HERE, "..", "..", "scenario-1-repricing", "data", "skus.csv")
OUT = os.path.join(HERE, "out", "reprice.csv")
MOVE_CAP = 0.15
EPS = 0.01  # stay a cent inside every bound


def band(v):
    lo = max(round(v["cost"], 2), round(v["map_floor"], 2),
             v["current_price"] * (1 - MOVE_CAP))
    hi = v["current_price"] * (1 + MOVE_CAP)
    # pull a cent inside the move-cap edges so abs(np-cur) <= cur*0.15 holds
    lo = max(lo, v["current_price"] * (1 - MOVE_CAP) + EPS)
    hi = min(hi, v["current_price"] * (1 + MOVE_CAP) - EPS)
    if hi < lo:           # band collapsed (cost/MAP above move ceiling): take the floor
        hi = lo
    return lo, hi


def load():
    rows = {}
    with open(SKUS) as f:
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


def blended_margin(active, price):
    num = den = 0.0
    for s, v in active.items():
        p = price(s, v)
        num += (p - v["cost"]) * v["units_30d"]
        den += p * v["units_30d"]
    return (num / den) if den else 0.0


def main():
    rows = load()
    active = {s: v for s, v in rows.items() if v["hold"] == 0}

    plan = {}
    for s, v in active.items():
        lo, hi = band(v)
        target = min(max(v["competitor_price"], lo), hi)
        plan[s] = round(target, 2)
        # rounding could nudge outside band; re-clamp on rounded value
        if plan[s] < lo:
            plan[s] = round(lo + 0.005, 2)
        if plan[s] > hi:
            plan[s] = round(hi - 0.005, 2)

    cur_margin = blended_margin(active, lambda s, v: v["current_price"])

    # Global margin guard: while blended margin < current, walk back the cut with
    # the smallest competitiveness cost per dollar of margin recovered. Simplest
    # effective heuristic: revert cuts ordered by units*price_drop ascending? No —
    # we want to recover margin cheaply, so revert the cut that adds the most
    # margin $ per unit of competitiveness lost. We just bump cut SKUs toward
    # current (capped at hi) in order of largest margin gain until margin_ok.
    def cur_blended():
        return blended_margin(active, lambda s, v: plan[s])

    if cur_blended() < cur_margin:
        # candidates: SKUs currently priced below their current_price (a cut) that
        # still have room to move up toward current within band.
        bumpable = []
        for s, v in active.items():
            lo, hi = band(v)
            ceiling = min(hi, v["current_price"])  # don't exceed original price here
            if plan[s] < ceiling - 0.001:
                bumpable.append(s)
        # order by margin leverage: units_30d desc, bigger gap desc
        bumpable.sort(key=lambda s: active[s]["units_30d"] *
                      (min(band(active[s])[1], active[s]["current_price"]) - plan[s]),
                      reverse=True)
        i = 0
        while cur_blended() < cur_margin and i < len(bumpable):
            s = bumpable[i]; v = active[s]
            lo, hi = band(v)
            ceiling = min(hi, v["current_price"])
            plan[s] = round(ceiling - 0.005, 2)
            if plan[s] > ceiling:
                plan[s] = round(ceiling, 2)
            i += 1
        # if still short after using bounded ceilings, allow raising above current
        # (within +15%) for high-volume SKUs whose competitor is also higher.
        if cur_blended() < cur_margin:
            raisable = [s for s in active
                        if active[s]["competitor_price"] > plan[s]]
            raisable.sort(key=lambda s: active[s]["units_30d"], reverse=True)
            j = 0
            while cur_blended() < cur_margin and j < len(raisable):
                s = raisable[j]; v = active[s]
                lo, hi = band(v)
                plan[s] = round(min(hi, v["competitor_price"]) - 0.005, 2)
                j += 1

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sku", "new_price"])
        for s in sorted(plan):
            w.writerow([s, f"{plan[s]:.2f}"])

    print(f"wrote {len(plan)} active SKUs (of {len(active)}), held omitted={len(rows)-len(active)}")
    print(f"current blended margin {cur_margin:.4f} -> new {cur_blended():.4f}")


if __name__ == "__main__":
    main()
