# STATE: Peak-season inventory replenishment PO plan

> Last updated: turn 1, 2026-06-21   Goal: out/po.csv passes check_replenish.py (hard_pass) with max score

## Done
- [x] Read SKILL.md + references; applied goal-loop methodology — @ turn 1
- [x] Confirmed budget feasibility: full rounded-up need ~$475.7k < $500k budget — @ turn 1
- [x] Wrote SPEC.md with measurable success criteria + grader command — @ turn 1
- [x] Built deterministic solver tools/solve_po.py (mirrors grader order-up-to math) — @ turn 1
- [x] Generated out/po.csv (120 rows, header sku,order_qty) — @ turn 1
- [x] Verified: grader exits 0, hard_pass:true, score 99.6 — @ turn 1

## Next (in order)
1. (none — goal met) Optionally re-run solver if input data changes.

## Blocked / needs human
- (none)

## Key decisions & rationale
- Cover every SKU to statistical need rounded up to MOQ/pack — because full need fits
  budget (95.1%), so no rationing/knapsack trade-off is needed and this is also the
  leanest feasible plan (only rounding overstock).
- Round order: ceil(need) -> MOQ -> pack multiple -> re-check MOQ, because grader
  treats both MOQ and pack violations as zero-tolerance hard fails.
- Emit q=0 (not a sub-MOQ qty) when position already covers need, to avoid MOQ
  violations and minimize overstock.

## Grader status
- check_replenish.py (--plan out/po.csv): PASS (hard_pass:true, exit 0) — last run turn 1
- score: 99.6 / 100 | demand_coverage 1.0 | sku_fill_rate 1.0 | skus_short 0
- spend 475726.06 / 500000 (95.1%) | moq_viol 0 | pack_viol 0 | neg 0 | overstock_ratio 0.0242

## Budget
- Turns used: 1 / 8   |   Spend cap: $500,000 (used $475,726 = 95.1%)   |   No cost spikes

## Scratch / breadcrumbs
- Solver: runs/s2-treatment/tools/solve_po.py (deterministic, reproducible)
- Grader: scenarios/scenario-2-replenishment/tools/check_replenish.py
- Verify cmd: python3 ../../scenarios/scenario-2-replenishment/tools/check_replenish.py --plan out/po.csv --json
- Horizon = lead_time_days + review_period_days(14); z=1.65; need uses on_hand+in_transit position.
