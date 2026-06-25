# SPEC: Catalog repricing — competitive without losing money

> Status: IN PROGRESS → DONE (grader passes)
> Owner: merchant (leo.huang20240423@gmail.com)   Agent: Claude Code   Date: 2026-06-25

## 1. Background & Goal
Margins are being squeezed and competitors keep undercutting us. We need to reprice
the 200-SKU catalog in `data/skus.csv` to be more price-competitive without selling
below cost/MAP or eroding blended margin. The merchant wants a reviewable plan.
**Goal (one line):** Produce a validated repricing plan (`out/reprice.csv`,
`sku,new_price`) that is more competitive yet provably does not lose money.

## 2. Success Criteria  ← the heart of the spec
The mechanical grader `tools/check_reprice.py` is the source of truth. Done only when:

- [x] Plan exists at `out/reprice.csv` with header `sku,new_price` — **verified by:** file present + parses.
- [x] `hard_pass == true` from the grader — **verified by:**
      `python3 tools/check_reprice.py --plan out/reprice.csv` exits 0.
      This single check ANDs together all hard constraints:
  - full coverage of active (hold=0) SKUs (`coverage == 1.0`)
  - no price below cost or MAP floor (`below_floor_count == 0`)
  - no per-SKU move beyond ±15% of current (`over_move_count == 0`)
  - hold=1 SKUs untouched (`touched_hold_count == 0`)
  - projected blended margin ≥ current (`margin_ok == true`)
- [x] Competitiveness maximized subject to the above — **verified by:** grader
      `competitiveness` field; aim as high as constraints legally allow.

**Bound:** stop and check in after ~15 turns or if `hard_pass` cannot be reached.

### Assumptions (user unavailable; defaulted from data + grader)
- The grader `tools/check_reprice.py` encodes the merchant's real policy → it is the spec.
- "More competitive" = price ≤ competitor_price wherever legally possible.
- "Don't lose money" = never below cost/MAP AND blended (unit-weighted) margin ≥ today's.
- hold=1 SKUs are deliberately frozen → omit them from the plan entirely (cleanest way to leave untouched).
- Where competitor price is below our cost/MAP/-15% floor, we do NOT chase it (chasing it would lose money or break MAP). These SKUs stay non-competitive by design.

## 3. Proven Methods & Recommendations  (the "skill")
- **Clamp into a legal band per SKU:** `lower = max(cost, map_floor, current*0.85)`,
  `upper = current*1.15`. Target `competitor_price`, clamp into `[lower, upper]`, round 2dp.
- **Trap — 2dp rounding can dip below a floor:** if rounded price < rounded lower,
  nudge up by +0.005 and re-round. Grader uses a 0.001 tolerance; stay above it.
- **Trap — blended margin is a RATIO, not dollars.** Cutting prices toward competitors
  lowers the unit-weighted margin ratio. After the first pass, run a **repair loop:**
  while `new_margin < cur_margin`, pull the most-damaging cut back up toward current
  (prices only ever move UP in repair, so floor/move constraints stay satisfied).
- **Preserve competitiveness during repair:** prefer bumping SKUs that already aren't
  competitive (current ≥ competitor) before sacrificing ones that are.

## 4. Workflow Standard  (the repeatable loop)
1. Re-orient: read this SPEC + `STATE.md`.
2. Edit `reprice.py` (the engine) for the smallest next improvement.
3. Run `python3 reprice.py` to regenerate `out/reprice.csv`.
4. **Verify:** `python3 tools/check_reprice.py --plan out/reprice.csv --json`.
5. Record score/competitiveness + decisions in `STATE.md`.
6. Repeat until hard_pass and competitiveness is at its legal ceiling.

**Hard gate (auto-reject a turn):** grader must exit 0 (`hard_pass == true`). A turn
that breaks any hard constraint does not count as progress — fix before advancing.

## 5. Constraints & Guardrails
- Must NOT change: `data/skus.csv`, the grader `tools/check_reprice.py`, other runs/seeds.
- Never price below cost or MAP; never move a SKU more than ±15%; never touch hold=1 SKUs.
- Never let projected blended margin fall below current.
- Permissions: free to edit files under this run dir only.

## 6. State & Hand-off
- State file: `STATE.md` (template: references/state-file-template.md).
- On compaction, resume from `STATE.md` alone: re-run engine, re-run grader.

## 7. Out of Scope / Stop & Escalate
- Out of scope: changing the policy itself, sourcing/cost negotiation, demand modeling.
- Stop and ask a human if: the grader can't reach `hard_pass`; a constraint conflicts
  (e.g. cost > MAP making a SKU unpriceable); or the merchant wants to chase
  below-cost competitor prices (a loss-leader decision a human must own).
