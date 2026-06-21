# Benchmark harness — how to reproduce the A/B

Everything here is deterministic and rerunnable. The comparison measures one
variable: **does the agent follow the `goal-loop` skill or not?** Same model, same
fuzzy prompt, same file access — only the methodology differs.

## Design

| | Control arm | Treatment arm |
|---|---|---|
| Prompt | The verbatim fuzzy merchant request + data paths | Same request, plus "read and follow `SKILL.md` + `references/`" |
| File access | Identical: scenario `data/` and `tools/` | Identical |
| Model | Same | Same |
| User available for interview? | n/a | No — skill says default from context & proceed |
| Leakage guard | — | Forbidden from reading `examples/` and `benchmark/` docs (which contain worked answers), so the result reflects *methodology*, not a memorized solution |

Both arms can discover the grader in `tools/` — equal opportunity. The question is
whether the methodology *reliably* leads to constraint-aware, verified output, vs
relying on the model happening to find and respect every hidden constraint.

## Steps

```bash
# 1. Generate fixtures (seeded; identical every run)
python3 benchmark/generate_data.py

# 2. (optional) Confirm the graders' ceilings are reachable
python3 benchmark/reference_solvers.py        # oracle baseline

# 3. Run each arm. In the real run these were 6 sub-agents (Claude Code Task
#    tool), one per scenario×arm, writing to benchmark/runs/<scenario>-<arm>/.
#    To reproduce manually, give each agent the prompt in scenarios/*/task.md
#    (control) or that prompt + "follow SKILL.md" (treatment).

# 4. Grade every output
python3 benchmark/score_all.py                # prints the comparison table
```

## Honesty notes / threats to validity

- **Strong base model.** Both arms run on a capable model (Opus). On well-bounded
  tasks where the control agent happens to discover and use the grader, the gap
  closes — and the results say so. The skill's edge is largest where a constraint
  is non-obvious (S1) and in *process reliability*, not in beating an oracle.
- **n=1 per cell.** Single runs, not averaged over seeds/models. Treat the numbers
  as a directional demonstration on a reproducible harness, not a statistical claim.
  Re-run with more seeds (`generate_data.py` seeds are per-scenario) to harden it.
- **Synthetic data.** Modeled on public e-commerce-agent benchmarks (EcomBench,
  RetailBench, YC-Bench, EcoGym) but not real merchant data. The *mechanics*
  (constraints, graders) are realistic; the rows are generated.
- **Treatment leakage guard is conservative.** Blocking `examples/` means treatment
  scores are a *lower bound* on what the full skill (with its worked example) would
  achieve.
