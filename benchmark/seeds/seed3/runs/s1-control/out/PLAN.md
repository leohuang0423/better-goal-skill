# Repricing Plan

## Goal
Stay competitive against undercutting competitors without losing money or violating MAP.

## Rules applied (per SKU)
1. **Hold flag honored** — any SKU with `hold=1` keeps its current price unchanged (18 SKUs).
2. **Hard floor** = max(`map_floor`, `cost` x 1.05). New price never goes below MAP and always keeps >= 5% gross margin over cost.
3. **If competitor is cheaper than us** — set price to 0.5% below the competitor (`competitor_price` x 0.995), but never below the floor. If beating them would break the floor, we keep our current price (don't sell at a loss).
4. **If we're already at/below the competitor** — keep current price; no reason to give up margin.

## Outcome (200 SKUs)
- 115 repriced down to undercut a cheaper competitor
- 67 left at current price (already competitive, or floor-constrained)
- 18 held per the hold flag
- 0 priced below cost; 0 below MAP floor

## Output
`reprice.csv` (columns: sku,new_price)
