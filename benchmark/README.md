# Benchmark — does `goal-loop` actually help?

A reproducible A/B that tests the skill on three e-commerce merchant long-horizon
tasks, modeled on public agent benchmarks (EcomBench, RetailBench, YC-Bench,
EcoGym). Same model + same fuzzy prompt + same files in both arms; the only
variable is whether the agent follows the `goal-loop` skill.

## TL;DR

| | Control (no skill) | Treatment (skill) |
|---|:---:|:---:|
| Hard-pass (policy-safe) | **2 / 3** | **3 / 3** |
| Avg score (0–100) | 91.5 | **99.5** |

The whole gap is one scenario — repricing — where the naive run *declared success*
while breaching a ±15% price-move cap on 20 SKUs and eroding margin. The skill
caught it because it made the grader the stop condition. Full write-up:
[`results.md`](results.md). It's an honest result: the other two scenarios tie at
ceiling because the base model is strong and both arms found the grader.

## Layout

```
benchmark/
├── generate_data.py        # seeded, deterministic fixtures
├── reference_solvers.py    # oracle baseline — proves the ceilings are reachable
├── score_all.py            # grades runs/ and prints the comparison table
├── rubric.md               # hard constraints + score weights per scenario
├── harness.md              # how to reproduce; threats to validity
├── results.md              # the findings, with the decisive case analyzed
├── scenarios/
│   ├── scenario-1-repricing/      (task.md, data/, tools/check_reprice.py)
│   ├── scenario-2-replenishment/  (task.md, data/, tools/check_replenish.py)
│   └── scenario-3-listings/       (task.md, data/, tools/qc_listings.py)
└── runs/                   # the A/B outputs (control + treatment per scenario)
```

## Scenarios

1. **Repricing** — reprice 200 SKUs to be competitive without breaching cost/MAP
   floors, a ±15% move cap, or `hold` flags, while keeping blended margin ≥ current.
2. **Replenishment** — order-up-to PO quantities for 120 SKUs that avoid stockouts
   over lead+review at a 95% service level, within budget and MOQ/pack rules.
3. **Listings** — rewrite 40 product listings to be marketplace-compliant (length,
   bullets, no banned claims) while preserving the source specs.

Each has a deterministic grader emitting `hard_pass` (all constraints) + `score`
(0–100). Run `python3 benchmark/harness.md`'s steps to reproduce.
