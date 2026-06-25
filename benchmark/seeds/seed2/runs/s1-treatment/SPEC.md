# SPEC: Catalog repricing for competitiveness without margin loss

> Status: APPROVED (auto-defaulted; user unavailable for interview)
> Owner: leo.huang20240423@gmail.com   Agent: Claude Code   Date: 2026-06-25

## 1. Background & Goal
Margins are being squeezed and competitors are undercutting the merchant on much of
the catalog (107 of 188 active SKUs are currently priced above the competitor). The
merchant wants prices made more competitive without losing money. The catalog is
`data/skus.csv` (200 SKUs: `sku, cost, current_price, map_floor, competitor_price,
units_30d, hold`). A grader `tools/check_reprice.py` encodes the hard policy and
scores quality, so this task is mechanically auto-gradable.

**Goal (one line):** Produce `out/reprice.csv` (`sku,new_price`) that covers every
active SKU, obeys all pricing floors/caps, leaves held SKUs alone, keeps blended
margin at or above today's, and moves prices toward competitor levels where allowed.

## 2. Success Criteria  ← the heart of the spec
The single mechanical grader is `tools/check_reprice.py`. "Done" = it exits 0.

- [ ] Full coverage of active (`hold=0`) SKUs — **verified by:** `coverage == 1.0` in grader output.
- [ ] No price below cost or MAP floor — **verified by:** `below_floor_count == 0`.
- [ ] No per-SKU move beyond ±15% of current price — **verified by:** `over_move_count == 0`.
- [ ] Held SKUs (`hold=1`) untouched — **verified by:** `touched_hold_count == 0` (we simply omit them).
- [ ] Projected blended (units-weighted) margin ≥ current — **verified by:** `margin_ok == true`, `new_blended_margin >= current_blended_margin`.
- [ ] More competitive than today — **verified by:** `competitiveness` (share of covered SKUs priced ≤ competitor) materially higher than the current-price baseline.
- [ ] Overall: **`python tools/check_reprice.py` exits 0** (`hard_pass == true`).

**Bound:** stop and check in after 15 turns / obvious algorithmic dead-end even if unmet.

## 3. Proven Methods & Recommendations  (the "skill")
- **Per-SKU price band first.** For each active SKU the legal price is the intersection
  of: `>= cost`, `>= map_floor`, and `current_price*(1±0.15)`. Pick a target inside that band.
- **Target = competitor price**, then clamp into the band: `price = clamp(competitor, lo, hi)`
  where `lo = max(cost, map_floor, current*0.85)` and `hi = current*1.15`. Round to 2dp.
- **Use grader-consistent rounding.** Compare against `round(cost,2)` / `round(map_floor,2)`
  and use the same `current*0.15 + 0.01` tolerance the grader uses; stay a cent inside every bound.
- **Margin is the binding global constraint, not a per-SKU one.** Naively matching
  competitor everywhere can drop blended margin below current. Fix it globally: SKUs
  whose competitor sits *above* current can be raised (within +15%) to add margin and
  fund the cuts elsewhere. If blended margin still lags, walk back the lowest-margin-impact
  cuts (highest `units_30d * price_drop`) toward current until `margin_ok`.
- **Held SKUs: omit entirely.** The grader only flags a hold SKU if it appears with a
  changed price; leaving it out of the plan is the safe, clean way to "not touch" it.
- **Known trap:** floating-point edges. Always re-run the grader after generating; never
  hand-trust the math.

## 4. Workflow Standard  (the repeatable loop)
1. Re-orient: read this SPEC + `runs/s1-treatment/STATE.md`.
2. Smallest next step: generate or adjust `out/reprice.csv` with the repricing script.
3. **Verify:** run `python tools/check_reprice.py --json` from the scenario folder.
4. Record results (coverage, the four violation counts, margins, competitiveness) in STATE.md.
5. If the gate fails, fix the specific failing constraint; do not advance.
6. Repeat until `hard_pass == true`.

**Hard gate (auto-reject a turn):** `python tools/check_reprice.py` must exit 0. Any
turn that leaves it exit 1 does not count as progress.

## 5. Constraints & Guardrails
- Must NOT change: `data/skus.csv`, the grader, or any held (`hold=1`) SKU's price.
- Scope limits: output is exactly `out/reprice.csv` with header `sku,new_price`; no other catalog edits.
- Never price below cost or MAP; never move a SKU more than ±15%; never reduce blended margin.
- Permissions: may create/overwrite files only under `runs/s1-treatment/`.

## 6. State & Hand-off
- State file: `runs/s1-treatment/STATE.md` (template: references/state-file-template.md).
- On stop/compaction the next turn resumes from STATE.md alone.

## 7. Out of Scope / Stop & Escalate
- Out of scope: changing held SKUs, sourcing new competitor data, demand modelling.
- Stop and ask a human if: a feasible plan cannot satisfy `margin_ok` and competitiveness
  simultaneously within the ±15% band (would signal a genuine cost/MAP problem), or after 15 turns.
