# Benchmark results — goal-loop skill vs. no skill

Three e-commerce merchant long-horizon scenarios, run as a controlled A/B: same
model, same verbatim fuzzy prompt, same file access — the only variable is whether
the agent followed the `goal-loop` skill. Fixtures and graders are deterministic;
reproduce with `benchmark/harness.md`.

> Run date: 2026-06-21 · Model: Claude (Opus-class) · n=1 per cell · Agent: Claude Code Task sub-agents

## Headline

| Scenario | Control `hard_pass` | Control score | Treatment `hard_pass` | Treatment score | Δscore |
|---|:---:|:---:|:---:|:---:|:---:|
| 1 · Repricing | ❌ **FAIL** | 74.9 | ✅ pass | **99.0** | **+24.1** |
| 2 · Replenishment | ✅ pass | 99.6 | ✅ pass | 99.6 | +0.0 |
| 3 · Listings | ✅ pass | 100.0 | ✅ pass | 100.0 | +0.0 |
| **Total** | **2 / 3 pass** | **91.5** | **3 / 3 pass** | **99.5** | **+8.0** |

Oracle ceiling (expert baseline, `reference_solvers.py`): S1 96.8 · S2 99.6 · S3 100.0.
Treatment matches or **exceeds** the oracle on every scenario (S1 treatment 99.0 > oracle 96.8).

## The decisive case — Scenario 1 (repricing)

This is where the skill earns its keep, and it's the most realistic kind of
long-horizon ops task: a vague goal with **non-obvious hard constraints**.

- **Control (no skill).** Read the data, applied a sensible-sounding rule ("undercut
  competitor by 1%, never below cost or MAP"), and **reported success**: *"0 SKUs
  priced below cost and 0 below MAP."* But against the real policy it **failed**:
  - **20 SKUs moved more than ±15%** (no awareness of the move cap — it never existed in the prompt, only in the grader the agent didn't consult).
  - **Blended margin fell** 0.436 → 0.401 — it literally *lost money* on margin while believing it was protecting it.
  - No spec, no verification, no state file. A merchant would have shipped a
    policy-violating, margin-eroding price change believing it was safe.
- **Treatment (skill).** Triaged the task, defaulted the interview from the data +
  the grader (user unavailable), wrote a 7-section `SPEC.md`, **discovered the
  grader and made it the stop condition**, and looped act→verify until green. Final:
  `hard_pass` true, **99.0** — full coverage, **0 move-cap breaches**, and margin
  *lifted* 0.436 → **0.439**. It even proved competitiveness 0.90 is the structural
  ceiling under the floors + move cap. Produced `SPEC.md`, `STATE.md`, and a
  reproducible `solve.py`.

**Δ +24.1 and a `hard_pass` flip — the difference between "ships a policy violation"
and "ships a verified, margin-positive plan."**

## The honest ties — Scenarios 2 & 3

On the two well-bounded scenarios, **both arms scored at ceiling** (99.6 and 100.0).
Why, and why that's the right thing to report:

- The base model is strong, and **both control agents independently found and used
  the grader** in `tools/`. When a capable model stumbles onto the mechanical check,
  it converges to the same place the skill would route it deliberately.
- So the skill's *score* advantage is ~0 where the naive path already happens to
  hit the check. We report this plainly rather than engineering a gap.

But two things still separate the runs even at a tied score:
1. **Reliability, not luck.** The skill makes "find the check and verify against it"
   the *procedure*, not a happy accident. Control passing S2/S3 depended on the
   agent choosing to look — exactly what failed it on S1.
2. **Reviewable artifacts.** Treatment leaves a `SPEC.md` (background, success
   criteria, methods, workflow, guardrails), a `STATE.md`, and a solver — so a human
   can review *why* the plan is right and re-run it. Control leaves an output file.

## What the benchmark does and doesn't show

**Shows:** When a long-horizon task hides a non-obvious constraint — the common
case in real ops — the skill turns a confident-but-wrong run (74.9, FAIL) into a
verified, oracle-beating one (99.0, PASS). Across the suite, hard-pass reliability
goes **2/3 → 3/3** and average score **+8.0**, with the entire gap concentrated
exactly where naive execution silently breaks policy.

**Doesn't show:** A uniform lift on every task. A strong model with grader access
can already one-shot well-scoped work; the skill's measured value is reliability and
the prevention of silent constraint violations, not beating an oracle on easy cases.
n=1 per cell on synthetic (if realistic) data — directional evidence on a
reproducible harness, not a statistical claim. See `harness.md` for threats to
validity.

## Reproduce

```bash
python3 benchmark/generate_data.py        # seeded fixtures
python3 benchmark/reference_solvers.py     # oracle ceilings (optional)
# run the 6 arms per harness.md, then:
python3 benchmark/score_all.py             # regenerates the table above
```
