# Scenario 2 — Inventory replenishment (fuzzy merchant request)

> Exact prompt given to both A/B arms.

"Going into peak season I'm scared of stocking out, but I also can't blow my
purchasing budget. Look at `data/inventory.csv` and tell me how much of each SKU to
reorder. Don't overspend."

## Assets
- `data/inventory.csv` — 120 SKUs: `sku, on_hand, in_transit, lead_time_days, avg_daily_demand, demand_sd, moq, pack_size, unit_cost`
- `data/params.json` — `review_period_days`, `service_level_z`, `budget`
- `tools/check_replenish.py` — the grader

## Hidden rubric
Hard constraints: PO spend ≤ budget; respect MOQ and pack-size multiples; no
negative quantities; demand coverage ≥ 90% of statistical need (order-up-to over
lead+review at the given service level). Score weights demand coverage, per-SKU
fill rate, budget adherence, MOQ/pack compliance, and leanness (avoid overstock).
Output expected at `out/po.csv` (`sku,order_qty`).
