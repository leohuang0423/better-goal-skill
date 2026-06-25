# Repricing Plan — Scenario 1

## Objective
Make pricing more competitive without losing money or breaking pricing constraints.

## Rules applied (per SKU)
1. **Held SKUs (`hold=1`): left unchanged.** 12 SKUs flagged hold are kept at their current price.
2. **Hard floor — never lose money or break MAP:** new price is never below
   `max(cost × 1.10, map_floor)`. This guarantees a minimum 10% gross margin over
   cost AND respects the minimum advertised price (MAP) floor.
3. **Competitiveness target:** aim to sit ~1% under the competitor price
   (`competitor_price × 0.99`).
4. **Only lower, never raise:** new price = `min(current_price, target)`, then clamped
   up to the floor. We never raise a price above today's price (the goal is to stop
   getting undercut, not to hike). If the competitiveness target sits below the floor,
   we hold at the floor rather than sell at a loss.

## Result summary (200 SKUs)
- 12 held unchanged.
- 115 prices lowered to be more competitive; 0 raised.
- 0 SKUs priced below cost; 0 active SKUs below MAP floor.
- 186 of 188 active SKUs now priced at or below the competitor's price. The remaining
  2 are floor-constrained — beating the competitor there would mean selling below the
  cost+margin/MAP floor, so they hold.

## Assumptions
- "Don't lose money" = maintain at least a 10% margin over `cost` (not merely break-even).
- `map_floor` is a binding minimum advertised price and must not be violated.
- `hold=1` means "do not reprice" (e.g., contractual/promo locks), so those are excluded.
- Competitiveness = match-or-slightly-undercut competitor; prices are not raised even
  when we have headroom, to avoid further margin/volume risk.
- `units_30d` was not used to weight changes in this pass; the rules are uniform.

## Output
`reprice.csv` — columns `sku,new_price`.
