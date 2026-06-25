# STATE: Catalog repricing

> Last updated: turn 3, 2026-06-25   Goal: out/reprice.csv passes check_reprice.py (hard_pass) with max legal competitiveness

## Done
- [x] Triage + read SKILL/references; confirmed loop justified (grader exists) @ turn 1
- [x] Wrote engine reprice.py (clamp-to-band + margin repair) @ turn 2 — grader hard_pass, score 98.1
- [x] Improved repair to preserve competitiveness @ turn 3 — score 98.3, competitiveness 0.828
- [x] Wrote SPEC.md and STATE.md @ turn 3

## Next (in order)
1. (optional) None required — hard_pass achieved and competitiveness at legal ceiling.

## Blocked / needs human
- ~33 active SKUs have competitor_price below our cost/MAP/-15% floor; cannot match
  without losing money or breaking MAP. Left non-competitive by design. Escalate only
  if merchant wants loss-leader pricing on specific SKUs. escalate? n (default)

## Key decisions & rationale
- hold=1 SKUs omitted entirely from plan (cleanest "untouched"); grader counts only touched holds.
- Target = competitor_price clamped to [max(cost,map,0.85*cur), 1.15*cur]; round 2dp, +0.005 floor guard.
- Blended margin is a ratio → repair loop bumps damaging cuts back toward current (prices only go UP, so constraints stay safe), preferring already-non-competitive SKUs first.

## Grader status
- check_reprice.py --plan out/reprice.csv: PASS (hard_pass=true, score 98.3) — last run turn 3
  coverage 1.0, below_floor 0, over_move 0, touched_hold 0, margin_ok true, competitiveness 0.828

## Budget
- Turns used: 3 / ~15   |   Spend: minimal   |   No cost spikes

## Scratch / breadcrumbs
- Engine: reprice.py (run `python3 reprice.py` from this dir).
- Grader: ../../scenario-1-repricing/tools/check_reprice.py (pass --plan out/reprice.csv --json).
- Output: out/reprice.csv (header sku,new_price; 180 active SKUs, holds omitted).
