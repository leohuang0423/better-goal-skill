# Benchmark rubric

Each scenario is graded by a deterministic script (the "grader") that emits two
numbers:

- **`hard_pass`** (bool) — did the output satisfy *every* hard constraint? This is
  the merchant-relevant bar: one MAP breach, one over-budget PO, or one banned
  claim can mean a policy violation, a contract penalty, or a delisting. Partial
  credit doesn't save you in the real world, so `hard_pass` is the headline metric.
- **`score`** (0–100) — graded quality, weighting coverage + each constraint +
  the soft objective (competitiveness / leanness / copy quality). Lets us compare
  two passing (or two failing) runs.

## Why two metrics

A long-horizon ops task is judged the way a merchant judges it: first "is it even
safe to ship?" (`hard_pass`), then "how good is it?" (`score`). The goal-loop
skill's thesis is that **making success mechanically checkable** is what moves
`hard_pass` from "sometimes" to "reliably," because the loop can't declare victory
until the grader is green.

## Per-scenario hard constraints

| Scenario | `hard_pass` requires |
|---|---|
| 1 · Repricing | Full coverage of active SKUs · never below cost or MAP · no move beyond ±15% · `hold` SKUs untouched · blended margin ≥ current |
| 2 · Replenishment | Spend ≤ budget · MOQ honored · pack-size multiples · no negative qty · demand coverage ≥ 90% of statistical need |
| 3 · Listings | Every product present · title 1–80 chars · ≥5 bullets · meta 50–160 chars · no banned claim · source specs preserved |

## Score weights

| Scenario | Weighting (0–100) |
|---|---|
| 1 · Repricing | coverage 30 · (no floor breach 25 · no over-move 15 · hold respected 10 · margin ok 10 · competitiveness 10) × coverage |
| 2 · Replenishment | demand coverage 45 · sku fill 20 · (budget 10 · MOQ/pack 10 · leanness 15) × coverage |
| 3 · Listings | present 10 · title 15 · bullets 20 · meta 15 · no-banned 20 · specs preserved 20 (each × pass-rate across products) |

The quality blocks in scenarios 1–2 are scaled by coverage so a do-nothing plan
scores ~0 instead of earning credit for vacuously "not violating" anything.

## Reachability (oracle ceiling)

`reference_solvers.py` provides an expert baseline proving each `hard_pass` is
attainable and each score has headroom: **S1 96.8 · S2 99.6 · S3 100.0**, all
`hard_pass: true`. So any failure is a real shortfall, not an impossible grader.
