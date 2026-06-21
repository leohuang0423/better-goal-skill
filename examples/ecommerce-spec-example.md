# Worked example — a complete spec + /goal for an e-commerce merchant task

This is what Phase 1–2 of `goal-loop` produces for a real-feeling task. Imitate the
shape. (Matches benchmark Scenario 1.)

---

## The user's original (fuzzy) request

> "Our margins are getting squeezed. Can you go through our catalog and fix the
> pricing? Make us more competitive but don't lose money."

## The interview (Phase 1 — 5 questions, one message)

1. **Done-looks-like?** → "A new price for every active SKU that protects margin and respects our floors."
2. **Grader?** → "We have `tools/check_reprice.py` that validates a reprice CSV against our rules; it must exit 0."
3. **Guardrails?** → "Never below cost. Never below MAP. Don't touch SKUs we've flagged `hold`. No single move over ±15%."
4. **Inputs/access?** → "`data/skus.csv` (cost, current price, MAP, competitor price, 30-day units, hold flag). Read-only — output a plan CSV, don't push to the store."
5. **Budget/bound?** → "Cap it ~15 turns; ping me before any cut deeper than 15%."

## The SPEC (written to `SPEC.md`)

```markdown
# SPEC: Q3 catalog repricing plan

> Status: APPROVED  Owner: merchant  Agent: Claude Code  Date: 2026-06-21

## 1. Background & Goal
Margins are compressing as competitors undercut us. We need a defensible repricing
plan across the active catalog that improves competitiveness without sacrificing
margin or breaking pricing-policy floors.
**Goal:** Produce a validated repricing plan (`out/reprice.csv`) for every active SKU.

## 2. Success Criteria
- [ ] Every active SKU in data/skus.csv has exactly one new price in out/reprice.csv — verified by: `python tools/check_reprice.py` (coverage check) exits 0.
- [ ] No price below cost or below MAP; no move beyond ±15% of current — verified by: same script's constraint checks exit 0.
- [ ] Projected blended margin >= current blended margin — verified by: script prints `margin_ok=True`.
- [ ] SKUs with hold=true are unchanged — verified by: script's hold check exits 0.
**Bound:** stop and check in after 15 turns even if unmet.

## 3. Proven Methods & Recommendations
- Reprice toward `min(competitor_price - $0.01, current)` but clamp to the floors and the ±15% band. Don't chase competitors below MAP/cost.
- Prioritize high-velocity SKUs (top 30-day units) for cuts; raise prices only where we're well under competitor and demand is inelastic.
- Leave margin headroom: target blended margin >= current, not merely break-even.
- Trap: floating-point cost compares — round to cents before the floor check.

## 4. Workflow Standard
1. Read SPEC.md + STATE.md. 2. Load skus.csv. 3. Compute proposed prices in batches
of ~50 SKUs. 4. Run check_reprice.py. 5. Fix any violations it reports. 6. Update
STATE.md. 7. Repeat until all checks pass.
**Hard gate:** `python tools/check_reprice.py` must exit 0 for the turn to count.

## 5. Constraints & Guardrails
- Must NOT: price below cost or MAP; move any SKU >±15%; modify hold=true SKUs; write anywhere except out/.
- Read-only on the live store — this produces a *plan*, not a push.

## 6. State & Hand-off
- State file: STATE.md. Next turn resumes from it alone.

## 7. Out of Scope / Stop & Escalate
- Out of scope: pushing prices live; changing the policy floors themselves.
- Stop and ask if: any SKU's best option needs a cut >15%, or cost/MAP data is missing.
```

## The /goal (Phase 2)

```
/goal out/reprice.csv contains a validated new price for every active SKU in
data/skus.csv. Verified by: `python tools/check_reprice.py` exits 0 — full
coverage, no price below cost or MAP, no move beyond ±15%, hold=true SKUs
untouched, and margin_ok=True. Must stay true: never below cost/MAP; never modify
hold SKUs; write only under out/. Stop and ask me before proposing any cut deeper
than 15%, or after 15 turns even if checks are red.
```

## Why this works
- The grader (`check_reprice.py`) makes "done" mechanical — the loop can't fool itself.
- Constraints are encoded as checks, not hopes.
- It's bounded (15 turns) with an explicit escalation trigger (>15% cut).
- The plan/push split keeps a human in the loop for the irreversible action.
