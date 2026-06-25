# Repricing Plan - Scenario 1

## Objective
Become more price-competitive vs. competitors without losing money or breaking pricing rules.

## Rules applied to every SKU
1. **Respect holds** - 20 SKUs flagged `hold=1` were left at their current price, untouched.
2. **Undercut competitor** - for non-held SKUs, target = competitor_price x (1 - 2%), i.e. priced ~2% under the competitor to win the comparison.
3. **Only move down** - we never raise a price above current. If the competitor is already at or above our current price, we keep current (no need to cut, no margin left on the table).
4. **Never lose money** - a hard floor of max(MAP floor, cost x 1.05) is enforced. No price ends below cost; every changed price keeps at least a 5% margin over cost. Legal MAP floors are always respected.

## Results
- SKUs total: 200
- Held / unchanged: 20
- Price cuts made: 112
- Priced below competitor (non-held): 176
- Below cost: 0 (guaranteed zero by the hard floor)
- Clamped up to MAP floor: 4; clamped up to margin floor: 0
- Projected 30-day gross margin (using current units as a proxy): 781,189 -> 669,026 (delta -112,163)

## Assumptions
- "Don't lose money" = stay above cost with a 5% cushion, not merely break-even.
- `map_floor` is a legal/contractual minimum and is never violated.
- We only reduce prices to gain competitiveness; we do not opportunistically raise prices even where the competitor is far above us (out of scope for this request).
- units_30d used only to estimate margin impact; demand elasticity (volume lift from lower prices) is not modeled, so the margin delta shown is a conservative worst case.

Output written to: /home/user/better-goal-skill/benchmark/seeds/seed1/runs/s1-control/out/reprice.csv
