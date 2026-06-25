# STATE: Catalog repricing

> Last updated: turn 1, 2026-06-25   Goal: `python tools/check_reprice.py` exits 0 (hard_pass=true), margin >= current, more competitive.

## Done
- [x] Read SKILL + references, scenario task.md, grader, data — @ turn 1
- [x] Wrote SPEC.md (all 7 sections) — @ turn 1
- [x] Built reprice.py (band-clamp to competitor + global margin guard) — @ turn 1
- [x] Generated out/reprice.csv (188 active SKUs, 12 held omitted) — @ turn 1
- [x] Grader passes — verified by `check_reprice.py --json` exit 0 @ turn 1

## Next (in order)
1. (none — goal met) Optional: hand plan to merchant for review.

## Blocked / needs human
- none

## Key decisions & rationale
- Held SKUs omitted from plan (not written) so touched_hold_count stays 0.
- Target = competitor price clamped into [max(cost,MAP,current*0.85)+1c, current*1.15-1c].
- Margin is a global constraint: guard re-bumps cut prices toward current until blended margin >= current. Not needed in practice this run (margin already held).

## Grader status
- check_reprice.py: PASS (turn 1). hard_pass=true, score=98.0, coverage=1.0,
  below_floor=0, over_move=0, touched_hold=0, margin_ok=true (0.4441->0.4443),
  competitiveness 0.4309 -> 0.8032.

## Budget
- Turns used: 1 / 15. No cost spikes.

## Scratch / breadcrumbs
- Run from runs/s1-treatment: `python3 reprice.py` then
  `python3 ../../scenario-1-repricing/tools/check_reprice.py --plan out/reprice.csv --json`.
- Output: out/reprice.csv (header sku,new_price).
