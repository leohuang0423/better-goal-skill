# SPEC: Catalog repricing — more competitive without losing margin

> Status: DONE (goal met — grader exit 0, score 99.0)
> Owner: leo.huang20240423@gmail.com   Agent: Claude Code   Date: 2026-06-21

## 1. Background & Goal
Margins are being squeezed and competitors keep undercutting us. The merchant wants
the catalog (200 SKUs in `data/skus.csv`) repriced to be more price-competitive
versus listed competitor prices, without reducing total profitability and without
breaking pricing policy (cost/MAP floors, a per-SKU move cap, and "hold" SKUs that
must not be touched).

**Goal (one line):** Produce a validated `out/reprice.csv` (`sku,new_price`) that
covers every active SKU, violates no hard pricing constraint, holds blended margin
at or above today's, and prices as many SKUs at/below competitor as the margin
constraint allows.

## 2. Success Criteria  ← the heart of the spec
The grader is the scenario's own script. The loop is "done" only when its hard
constraints all pass.

- [x] Every active (hold=0) SKU has a `new_price` — **verified:** `coverage == 1.0` (190/190).
- [x] No price below cost or MAP floor — **verified:** `below_floor_count == 0`.
- [x] No SKU moved more than ±15% off current price — **verified:** `over_move_count == 0`.
- [x] No hold SKU modified — **verified:** `touched_hold_count == 0` (10 hold SKUs omitted).
- [x] Blended (units-weighted) margin not reduced — **verified:** `margin_ok == true` (0.4360 → 0.4394).
- [x] Overall hard gate passes — **verified:** `check_reprice.py --plan out/reprice.csv` **exits 0**.
- [x] Quality: competitiveness maximized — **verified:** `competitiveness == 0.90`, the proven structural maximum (171/190 SKUs reachable); `score == 99.0`.

**Bound:** stop and check in after ~12 turns even if unmet.

## 3. Proven Methods & Recommendations  (the "skill")
Mechanics learned from reading the grader (`check_reprice.py`):
- Margin metric is a **units-weighted ratio**: `Σ(price-cost)*units / Σ price*units`
  over active SKUs only. Hold and zero-unit SKUs do not affect margin (units=0 ⇒
  zero weight), but zero-unit SKUs still need a price for coverage.
- Floor is `new_price >= max(round(cost,2), round(map_floor,2))`. Move cap is
  `|new - current| <= current*0.15 + 0.01`. Hold SKUs (hold=1) must equal
  current_price within 0.01 (simplest: omit them — coverage only counts active).
- Competitiveness = share of covered active SKUs with `new_price <= competitor + 0.01`.
- **The tension:** cutting prices toward competitor lowers the margin ratio; the
  margin floor is the binding constraint. Strategy that guarantees margin_ok:
  1. For each active SKU compute the competitive target
     `t = clamp(min(current, competitor), lo, hi)` where
     `lo = max(cost, map_floor)`, `hi = current*1.15`, `lo' = current*0.85`,
     i.e. target within `[max(lo, lo'), hi]`.
  2. A pure cut would reduce margin. Compensate by also *raising* SKUs that have
     headroom (current < competitor and below the move-cap ceiling) so the blended
     margin ratio is held >= baseline.
  3. Solve as: greedily cut the SKUs where being at/below competitor is achievable
     and cheap in margin terms, then raise high-headroom SKUs until the blended
     margin recovers to >= baseline. Verify numerically against the grader's exact
     formula before writing the file.
- **Known trap:** don't price hold SKUs; don't let any cut breach the floor or the
  -15% cap. Round to 2 decimals (grader rounds plan prices to 2 dp).
- Reference: `references/goal-prompt-cookbook.md` worked example matches this scenario.

## 4. Workflow Standard  (the repeatable loop)
1. Re-orient: read this SPEC + `STATE.md`.
2. Pick the smallest next step (build solver → tune competitiveness).
3. Run the solver to (re)generate `out/reprice.csv`.
4. **Verify:** `python ../../scenarios/scenario-1-repricing/tools/check_reprice.py
   --plan out/reprice.csv --json`.
5. Record result (hard_pass, score, counts, margins) in `STATE.md`.
6. Repeat until hard_pass and competitiveness is maximized within constraints.

**Hard gate (auto-reject a turn):** `check_reprice.py` must **exit 0**. If any of
coverage/floor/move/hold/margin fails, fix — do not advance.

## 5. Constraints & Guardrails
- Must NOT change: source `data/skus.csv`; the grader; hold=1 SKUs' prices.
- Scope limits: only produce `out/reprice.csv`; no pricing below floor; no move >15%.
- Permissions: may create/overwrite files under this run folder only.

## 6. State & Hand-off
- State file: `STATE.md` in this folder (template: references/state-file-template.md).
- On stop/compaction, the next turn resumes from `STATE.md` + this SPEC alone.

## 7. Out of Scope / Stop & Escalate
- Out of scope: changing cost/MAP data, competitor data, or hold flags.
- Stop and ask a human if: the margin constraint makes meaningful competitiveness
  impossible (can't beat competitor on any material share without losing margin),
  or the grader can't be run, or after ~12 turns if hard_pass is still false.
```
