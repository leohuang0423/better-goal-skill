# STATE: Catalog repricing

> Last updated: turn 3, 2026-06-21   Goal: out/reprice.csv passes check_reprice.py (exit 0), margin >= baseline, competitiveness maximized.   STATUS: DONE — goal met.

## Done
- [x] Read SKILL + references; read grader + data @ turn 1
- [x] Wrote SPEC.md @ turn 1
- [x] Built solver (solve.py) @ turn 2 — first plan: hard_pass, score 98.7, competitiveness 0.8737
- [x] Proved theoretical max competitiveness = 0.90 (171/190 reachable under floor + 15% cap) @ turn 3
- [x] Rewrote solver to optimal strategy: competitive SKUs priced AT competitor, infeasible SKUs to ceiling @ turn 3
- [x] Final plan passes grader exit 0, score 99.0, competitiveness 0.90 (= max), margin 0.4360 -> 0.4394 @ turn 3

## Next (in order)
1. (none — goal met) optionally hand off to merchant for review.

## Blocked / needs human
- none

## Key decisions & rationale
- Omit hold=1 SKUs from the plan (coverage counts active only; avoids touched_hold). 10 hold SKUs excluded; 190 active priced.
- Margin is a units-weighted RATIO. Pricing competitive SKUs AT competitor (not below) keeps them competitive while maximizing margin -> margin rises above baseline.
- 19 SKUs cannot reach competitor under the -15% move cap / MAP floor; pushed to their +15% ceiling to fund blended margin. These are the only non-competitive SKUs, so competitiveness hits the structural max of 0.90.

## Grader status
- check_reprice.py: PASS (exit 0) @ turn 3. coverage 1.0, below_floor 0, over_move 0, touched_hold 0, margin_ok true, competitiveness 0.90, score 99.0.

## Budget
- Turns used: 3 / ~12

## Scratch / breadcrumbs
- Solver: solve.py (regenerates out/reprice.csv). Grader: ../../scenarios/scenario-1-repricing/tools/check_reprice.py
- Plan header: sku,new_price. 190 rows. Run grader: python3 ../../scenarios/scenario-1-repricing/tools/check_reprice.py --plan out/reprice.csv --json
