# Repricing Plan (for review)

Goal: be more price-competitive without losing money.

## Rules applied to each SKU
1. **Held SKUs (hold=1):** price left UNCHANGED. These were flagged to not touch
   (9 SKUs: 0004, 0016, 0023, 0071, 0075, 0089, 0105, 0133, 0176, 0177).
2. **All other SKUs:** set new price to undercut the competitor by 1%
   (target = competitor_price x 0.99).
3. **Guardrails (never break, so we don't lose money / stay legal):**
   - Never price below `cost` (no negative margin).
   - Never price below `map_floor` (MAP / contractual minimum).
   - Effective lower bound = max(cost, map_floor).
4. **Direction:** we only lower prices to gain competitiveness; we do not raise a
   price above its current level unless a floor (cost or MAP) requires it.

## Effect
- 200 SKUs processed, 0 priced below cost, 0 below MAP floor.
- Where the competitor is cheaper than our floor, we sit at the floor (we can't
  legally/profitably match — flagged implicitly by the price equaling the floor).
- units_30d was reviewed but not used as a hard input; it is available if you want
  volume-weighted aggressiveness later.

## Assumptions
- "Don't lose money" = price >= cost. Margin above cost is acceptable even if thin.
- 1% undercut is a reasonable, conservative competitiveness margin; adjust if you
  want to undercut harder.
- competitor_price is current and trustworthy.

Output: reprice.csv (sku,new_price)
