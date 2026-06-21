# Scenario 1 — Catalog repricing (fuzzy merchant request)

> This is the *exact* prompt given to both arms of the A/B (with-skill and
> without-skill). It is deliberately vague, the way a real merchant asks.

"Our margins are getting squeezed and competitors keep undercutting us. Can you go
through our catalog in `data/skus.csv` and fix the pricing so we're more
competitive but we don't lose money? Put your plan somewhere I can review it."

## Assets (provided, not explained to the agent)
- `data/skus.csv` — 200 SKUs: `sku, cost, current_price, map_floor, competitor_price, units_30d, hold`
- `tools/check_reprice.py` — the grader (agents may or may not discover/use it)

## Hidden rubric (how the run is scored — not shown to the agent)
Hard constraints (all must hold for `hard_pass`): full coverage of active SKUs;
never below cost or MAP; no per-SKU move beyond ±15%; `hold=1` SKUs untouched;
projected blended margin ≥ current. Score 0–100 weights coverage, each
constraint, and competitiveness. Output expected at `out/reprice.csv`
(`sku,new_price`).
