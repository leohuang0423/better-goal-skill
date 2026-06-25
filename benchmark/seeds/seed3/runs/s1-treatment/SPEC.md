# SPEC: Catalog repricing — competitive without losing margin

> Status: DONE
> Owner: merchant (leo.huang20240423@gmail.com)   Agent: Claude Code   Date: 2026-06-25

## 1. Background & Goal
Margins are being squeezed and competitors keep undercutting us. We have a 200-SKU
catalog (`data/skus.csv`: `sku, cost, current_price, map_floor, competitor_price,
units_30d, hold`). The merchant wants prices made more competitive without losing
money, plus a reviewable plan.

**Goal (one line):** Produce a validated repricing plan (`out/reprice.csv`,
`sku,new_price`) that prices more SKUs at or below competitor while keeping blended
margin at least where it is today and breaking no pricing-policy hard constraint.

## 2. Success Criteria  ← the heart of the spec
The plan is "done" only when the grader passes and competitiveness is near its
feasible ceiling.

- [x] Plan exists at `out/reprice.csv` with header `sku,new_price` — **verified by:** `head -1 out/reprice.csv` == `sku,new_price`.
- [x] Grader hard-passes — **verified by:** `python ../../scenario-1-repricing/tools/check_reprice.py --plan out/reprice.csv` exits 0. This enforces: full coverage of active SKUs, no price below cost or MAP, no per-SKU move beyond ±15%, no `hold=1` SKU touched, and projected blended margin ≥ current.
- [x] Competitiveness is materially improved and near the feasible ceiling — **verified by:** grader `--json` `competitiveness` field (achieved **0.7967**; ceiling ≈ 0.885 = 161/182 reachable within the ±15% cap; remainder is economically infeasible, not an algorithm gap). Score **98.0/100**.

**Bound:** stop and check in after ~15 turns / once hard_pass holds and
competitiveness stops improving meaningfully.

## 3. Proven Methods & Recommendations  (the "skill")
- **Mirror the grader exactly.** Constraints come straight from `tools/check_reprice.py`:
  floor = `max(cost, map_floor)`; move cap = ±15% of `current_price`; margin is
  units-weighted `(price-cost)*units / (price*units)`; `hold=1` rows must be left
  out / unchanged. Re-implementing these in the generator means the generator's own
  print and the grader agree.
- **Cent-rounding trap:** the grader rounds plan prices to 2 dp and the ±15% cap is
  checked against the rounded value. Stay `EPS=0.005` inside the cap so rounding a
  boundary price never tips a SKU over the move cap. (Hit early; fixed by the epsilon.)
- **The real tension is margin, not feasibility.** Cutting prices toward competitors
  spends margin; the grader requires blended margin ≥ current, so naive "drop
  everyone to competitor" fails the margin floor. You must *fund* the cuts.
- **Two-pass "build surplus, then buy competitiveness":**
  1. SKUs priced *below* competitor have headroom — raise them up toward
     `min(competitor, +15% cap)`. They stay competitive (≤ competitor) yet earn
     more margin, creating a surplus.
  2. Spend that surplus making *above-competitor* SKUs competitive, cheapest
     margin-dollar (`(price-comp)*units`) first, accepting each cut only while
     blended margin stays ≥ current. Greedy-cheapest-first maximises the count.
  This lifted competitiveness from ~0.41 (margin-locked) to 0.80.
- **Omit hold SKUs entirely** rather than echoing current price — simplest way to
  guarantee `touched_hold = 0`.

## 4. Workflow Standard  (the repeatable loop)
1. Re-orient: read this SPEC + `STATE.md`.
2. Adjust `gen_reprice.py` (the single coherent unit of work).
3. Run `python gen_reprice.py` to regenerate `out/reprice.csv`.
4. **Verify** with the grader: `python ../../scenario-1-repricing/tools/check_reprice.py --plan out/reprice.csv --json`.
5. Record competitiveness/score + decision in `STATE.md`.
6. Repeat until hard_pass and competitiveness plateaus.

**Hard gate (auto-reject a turn):** grader must exit 0 (`hard_pass: true`). A turn
that drops hard_pass to false does not count as progress — fix before advancing.

## 5. Constraints & Guardrails
- Must NOT: price below `max(cost, map_floor)`; move any SKU more than ±15% of its
  current price; modify or include any `hold=1` SKU; let blended margin fall below
  current.
- Scope: only `out/reprice.csv` and the generator are produced; `data/skus.csv` and
  the grader are read-only and untouched.
- Permissions: free to iterate on the generator and re-run the grader autonomously.

## 6. State & Hand-off
- State file: `STATE.md` (template: references/state-file-template.md).
- Generator: `gen_reprice.py` (deterministic; re-running reproduces the plan).
- On resume, read SPEC + STATE, then re-run gen + grader.

## 7. Out of Scope / Stop & Escalate
- Out of scope: changing the ±15% policy, sourcing fresh competitor data, demand
  modelling, or pricing the 18 `hold=1` SKUs.
- Stop and ask a human if: the merchant wants competitiveness beyond the feasible
  ceiling (would require relaxing the ±15% cap or the margin floor — a policy call),
  or if input data changes.

## Assumptions (no merchant interview available)
- "Don't lose money" = keep units-weighted blended margin ≥ current (the grader's
  definition) and never price below cost/MAP.
- "More competitive" = maximise the count of active SKUs priced ≤ competitor_price;
  matching the competitor (not undercutting) is sufficient to count as competitive.
- `hold=1` means do-not-reprice; those 18 SKUs are left out of the plan.
- The ±15% move cap is a fixed business guardrail, not negotiable this run.
