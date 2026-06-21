# SPEC: Peak-season inventory replenishment PO plan

> Status: APPROVED (auto-defaulted; user unavailable for interview)
> Owner: merchant (leo.huang20240423@gmail.com)   Agent: Claude Code   Date: 2026-06-21

## 1. Background & Goal
Going into peak season the merchant fears stockouts but has a hard purchasing
budget. We must decide a reorder quantity for each of the 120 SKUs in
`data/inventory.csv` that covers statistical demand over the replenishment horizon
without exceeding the budget, and without ordering quantities that the supplier
cannot fulfill (MOQ / pack-size rules).

**Goal (one line):** Produce `out/po.csv` (`sku,order_qty`) that fully covers
statistical demand need, respects every supplier/budget constraint, and stays lean
(minimal overstock) — i.e. passes `tools/check_replenish.py` with the highest
achievable score.

## 2. Success Criteria  ← the heart of the spec
The grader is `tools/check_replenish.py`, which computes the order-up-to need per
SKU = `avg_daily_demand*H + z*demand_sd*sqrt(H)` over horizon `H = lead_time + review_period (14d)`
at `z = 1.65`, minus current position (`on_hand + in_transit`), floored at 0.

- [ ] `out/po.csv` exists with header `sku,order_qty` and one row per SKU — **verified by:** file present, 120 data rows, integer qtys.
- [ ] Hard constraints all pass — **verified by:** `python3 tools/check_replenish.py --plan <run>/out/po.csv --json` exits 0 (`hard_pass: true`): spend ≤ budget ($500,000), no negative qty, zero MOQ violations, zero pack-size violations, demand_coverage ≥ 0.90.
- [ ] High score, leaning toward full coverage + leanness — **verified by:** grader `score` ≥ 95 / 100 (target: coverage ≈ 1.0, fill_rate ≈ 1.0, overstock_ratio small).

**Bound:** stop after 8 build/verify iterations even if score < target, as long as
`hard_pass: true` is achieved. (Feasibility already confirmed in planning: full
rounded-up need costs ~$475.7k < $500k budget.)

## 3. Proven Methods & Recommendations  (the "skill")
- **Replicate the grader's math exactly.** Horizon = `lead_time_days + review_period_days`.
  Order-up-to = `demand*H + z*sd*sqrt(H)`. Raw need = `max(0, order_up_to - on_hand - in_transit)`.
  Computing need any other way (e.g. ignoring in_transit, or using lead time only)
  silently loses coverage or wastes budget.
- **Round up, in the right order:** take `ceil(raw_need)`, then bump to MOQ, then up
  to the next pack-size multiple, then re-check MOQ (a pack-rounded value can dip
  below MOQ for odd combos). Both MOQ-violation and pack-violation are zero-tolerance
  hard fails in the grader.
- **`q=0` is allowed and is the lean choice when need is 0** (position already covers
  the horizon). The grader only penalizes MOQ/pack for `q>0`, so never emit a small
  sub-MOQ positive quantity.
- **Leanness matters to the score, not the hard gate.** Overstock_ratio = excess spend
  over need / total spend. Rounding up to MOQ/pack is the only unavoidable overstock;
  do NOT pad quantities beyond the rounded need. There is enough budget headroom that
  no trimming is needed, so the minimal-rounded plan is also the leanest feasible plan.
- **Budget headroom check first.** Full rounded-up need = ~$475.7k vs $500k budget
  (95.1%). Since it fits, the optimal strategy is simply "cover everyone to need,
  rounded up" — no rationing / knapsack trade-off is required.

## 4. Workflow Standard  (the repeatable loop)
1. Re-orient: read this SPEC + `STATE.md`.
2. Run the solver `tools/solve_po.py` (deterministic; reads data/params, writes `out/po.csv`).
3. **Verify** with the grader: `python3 tools/check_replenish.py --plan out/po.csv --json`.
4. Record result (hard_pass, score, spend, coverage, violations) in `STATE.md`.
5. If hard_pass is false or score below target, diagnose the failing field and adjust
   the solver (e.g. fix rounding order, fix need formula); repeat.

**Hard gate (auto-reject a turn):** `check_replenish.py` must exit 0 (`hard_pass: true`).
A turn that does not produce a passing plan is not progress.

## 5. Constraints & Guardrails
- Must NOT change: `data/inventory.csv`, `data/params.json`, `tools/check_replenish.py`
  (read-only inputs/grader). Do not edit the grader to make the plan pass.
- Scope limits: only reorder quantities are decided; no pricing, no supplier changes,
  no SKU additions/removals. Every SKU in inventory appears exactly once in the plan.
- Spend must never exceed budget ($500,000). Quantities are non-negative integers.

## 6. State & Hand-off
- State file: `STATE.md` (template: references/state-file-template.md).
- Solver: `tools/solve_po.py` (under the run folder), fully deterministic — re-running
  reproduces the same `out/po.csv`.

## 7. Out of Scope / Stop & Escalate
- Out of scope: forecasting beyond the supplied demand mean/sd; multi-echelon logic.
- Stop and ask a human if: full rounded-up need ever EXCEEDS budget (would require a
  rationing policy / priority weighting the merchant should choose), or if the grader
  reports a hard fail that cannot be resolved by correct rounding within 8 iterations.
