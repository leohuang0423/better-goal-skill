#!/usr/bin/env python3
"""Repricing plan generator for Scenario 1.

Policy (mirrors the grader's hard constraints in tools/check_reprice.py):
  - Cover every active (hold=0) SKU.
  - new_price >= max(cost, map_floor)  (never below cost or MAP).
  - |new_price - current_price| <= 15% of current_price.
  - Leave hold=1 SKUs out of the plan entirely (never touched).
  - Units-weighted blended margin must be >= current blended margin.

Objective: maximise competitiveness (count of active SKUs priced at or below the
competitor) subject to the margin floor.

Method -- "buy the cheapest competitiveness":
  A SKU is competitive iff price <= competitor. For each SKU define its competitive
  price = clamp(min(current, competitor)) to [floor, current*1.15] within the move
  cap. Going from current down to that competitive price costs margin dollars
  (delta_margin = (current - comp_price) * units). We start everyone at `current`
  (which maximises margin, since current >= floor) and then make SKUs competitive
  in increasing order of margin-dollar cost, spending only the surplus margin we
  have over the current blended margin. SKUs that are already competitive at
  current, or competitive for free, are taken first. This yields the maximum number
  of competitive SKUs the margin floor allows.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SKUS = os.path.join(HERE, "..", "..", "scenario-1-repricing", "data", "skus.csv")
OUT = os.path.join(HERE, "out", "reprice.csv")
MOVE_CAP = 0.15
EPS = 0.005  # stay just inside the +/-15% cap so cent-rounding never trips it


def load(p):
    rows = []
    with open(p) as f:
        for r in csv.DictReader(f):
            rows.append({
                "sku": r["sku"],
                "cost": float(r["cost"]),
                "current": float(r["current_price"]),
                "floor": max(float(r["cost"]), float(r["map_floor"])),
                "comp": float(r["competitor_price"]),
                "units": int(r["units_30d"]),
                "hold": int(r["hold"]),
            })
    return rows


def blended(rows, price):
    num = den = 0.0
    for r in rows:
        p = price[r["sku"]]
        num += (p - r["cost"]) * r["units"]
        den += p * r["units"]
    return (num / den) if den else 0.0


def comp_price(r):
    """Lowest 'just competitive' price for r, within all hard constraints.
    Target the competitor price (no need to undercut), but never below floor and
    never more than 15% under current."""
    cap_lo = r["current"] * (1 - MOVE_CAP) + EPS
    target = min(r["current"], r["comp"])      # never raise above current here
    target = max(target, cap_lo, r["floor"])   # respect cap + floor
    return round(target, 2)


def main():
    rows = load(SKUS)
    active = [r for r in rows if r["hold"] == 0]

    cur_blended = blended(active, {r["sku"]: r["current"] for r in active})

    # Start everyone at current (always >= floor).
    price = {r["sku"]: round(r["current"], 2) for r in active}

    # PASS 1 -- build a margin surplus *without* losing competitiveness.
    # SKUs priced strictly below the competitor have headroom: raise them up
    # toward min(competitor, +15% cap). They stay competitive (price <= comp)
    # but earn more margin, funding price cuts elsewhere.
    for r in active:
        if r["current"] <= r["comp"] - 0.01:  # below competitor -> headroom
            cap_hi = r["current"] * (1 + MOVE_CAP) - EPS
            target = min(r["comp"], cap_hi)
            target = max(target, r["floor"])
            if round(target, 2) > price[r["sku"]]:
                price[r["sku"]] = round(target, 2)

    # PASS 2 -- spend the surplus buying competitiveness on above-competitor SKUs,
    # cheapest (least margin-$) first, while blended margin stays >= current.
    candidates = []
    for r in active:
        cp = comp_price(r)
        already = price[r["sku"]] <= r["comp"] + 0.01
        can = cp <= r["comp"] + 0.01
        if already or not can:
            continue
        cost_margin = (price[r["sku"]] - cp) * r["units"]
        candidates.append((cost_margin, r, cp))

    candidates.sort(key=lambda t: t[0])
    for cost_margin, r, cp in candidates:
        trial = dict(price)
        trial[r["sku"]] = cp
        if blended(active, trial) >= cur_blended - 1e-9:
            price = trial  # affordable -- make it competitive

    # Write plan: active SKUs only (hold SKUs deliberately omitted).
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sku", "new_price"])
        for r in active:
            w.writerow([r["sku"], f'{price[r["sku"]]:.2f}'])

    nm = blended(active, price)
    comp_ok = sum(1 for r in active if price[r["sku"]] <= r["comp"] + 0.01)
    print(f"active={len(active)} cur_margin={cur_blended:.4f} "
          f"new_margin={nm:.4f} margin_ok={nm >= cur_blended - 1e-9} "
          f"competitiveness={comp_ok/len(active):.4f}")


if __name__ == "__main__":
    main()
