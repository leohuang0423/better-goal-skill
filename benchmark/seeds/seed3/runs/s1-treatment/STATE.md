# STATE: Catalog repricing

> Last updated: turn 4, 2026-06-25   Goal: out/reprice.csv hard-passes check_reprice.py with competitiveness near ceiling.

## Done
- [x] Read SKU data + grader; confirmed loop gate (auto-gradable) @ turn 1.
- [x] v1 generator (compete then recover margin) — hard_pass, comp 0.44, score 94.4 @ turn 2.
- [x] v2 greedy "buy cheapest competitiveness" — hard_pass, comp 0.41 (margin-locked) @ turn 3.
- [x] v3 two-pass "build surplus then buy competitiveness" — hard_pass, comp 0.7967, score 98.0 @ turn 4. ← current.
- [x] Verified hold SKUs omitted (0 in plan), header `sku,new_price`, 182 active rows.

## Next (in order)
1. None required — hard_pass holds and competitiveness has plateaued near the
   feasible ceiling (145/161 reachable SKUs competitive; remaining 16 are
   margin-budget-infeasible). Ship.

## Blocked / needs human
- Pushing competitiveness past ~0.80 would require relaxing the ±15% cap or the
  margin floor — a merchant policy decision. Escalate? only if asked for more.

## Key decisions & rationale
- Fund price cuts by first raising below-competitor SKUs (still ≤ competitor) to
  create margin surplus, because the margin floor otherwise leaves zero budget to cut.
- Greedy cheapest-margin-dollar-first when spending surplus — maximises competitive count.
- EPS=0.005 inside the ±15% cap to survive the grader's cent-rounding of plan prices.
- Omit hold SKUs from the plan entirely to guarantee touched_hold=0.

## Grader status
- check_reprice.py: PASS (hard_pass=true, score 98.0, coverage 1.0, margin_ok=true,
  comp 0.7967, all violation counts 0) — last run turn 4.

## Budget
- Turns used: 4 / ~15. No cost spikes.

## Scratch / breadcrumbs
- Generate: `python gen_reprice.py`
- Grade:    `python ../../scenario-1-repricing/tools/check_reprice.py --plan out/reprice.csv --json`
- Feasible competitiveness ceiling = 161/182 = 0.885 (21 SKUs can't reach competitor
  within -15%). Achieved 145 competitive.
