# better-goal-skill — `goal-loop`

A portable **Skill package** that helps ordinary users actually get value out of an
agent's long-horizon / autonomous features — Claude Code's plan mode + `/goal` +
act mode, and the equivalent "run until done" loops in Codex, Hermes, and openclaw.

It turns a vague, ambitious request into a runnable, trustworthy loop:

```
  PLAN MODE  ──►  /goal  ──►  ACT MODE
  interview +     set a          run the loop:
  write a SPEC    verifiable      act → verify → record → repeat,
                  stop condition  guarded by a hard gate
```

## The problem it solves

People point a powerful agent at a big goal ("fix our pricing", "clean up the
codebase", "get CI green") and let it run. Without structure, the loop burns tokens
wandering, and — worse — it can **confidently declare success while silently
breaking a constraint nobody wrote down.** Our benchmark caught exactly this: a
naive repricing run reported *"0 SKUs below cost or MAP"* while breaching a ±15%
move cap on 20 SKUs and eroding margin. The skill prevents that by making success
**mechanically checkable** before the loop is allowed to stop.

## What the skill does

1. **Triage** (should this even be a loop?) — 5 gates; the make-or-break one is "is
   there something that can mechanically judge failure?" No grader → no loop.
2. **Plan mode** — asks **3–6 sharp questions** (or defaults from context if you're
   away), then writes a **high-quality SPEC**: background & goal, **success criteria
   tied to checks**, proven methods, workflow standard, guardrails, state/hand-off,
   stop-&-escalate.
3. **`/goal`** — converts the success criterion into a **verifiable, bounded stop
   condition**.
4. **Act mode** — runs the loop: act → verify against the grader → record state →
   repeat, with a hard gate (tests/build/check) and a turn/spend bound.

Built on a 14-step **Loop Engineering** roadmap (decide → build a minimal loop →
keep it safe in production). See [`references/loop-engineering-14-steps.md`](references/loop-engineering-14-steps.md).

## Install

```bash
# Personal (all projects):
cp -r . ~/.claude/skills/goal-loop
# or project-scoped:
mkdir -p .claude/skills && cp -r . .claude/skills/goal-loop
```

Then in Claude Code, it auto-triggers on long-horizon phrasing, or invoke it
explicitly: `/goal-loop <your task>`. For Codex / Hermes / openclaw, see
[`references/cross-agent-adapters.md`](references/cross-agent-adapters.md) — the
methodology is identical; only the plan/stop/act mechanics differ.

## Does it work? (benchmark)

A reproducible A/B on three e-commerce merchant long-horizon scenarios — same
model, same fuzzy prompt, same file access, skill vs. no skill:

| | Control (no skill) | Treatment (skill) |
|---|:---:|:---:|
| Hard-pass (policy-safe) | **2 / 3** | **3 / 3** |
| Avg score (0–100) | 91.5 | **99.5** |

The gap concentrates on the scenario with a non-obvious constraint (repricing:
**74.9 FAIL → 99.0 PASS**), which **replicates across 4 independent seeds —
control 0/4 pass, treatment 4/4 pass, Δ+23.4**. The two well-bounded scenarios tie
at ceiling because the base model is strong and both arms found the grader. We
report that honestly. Full analysis + how to reproduce: [`benchmark/`](benchmark/).

## Repository layout

```
SKILL.md                       # the orchestrator (plan → /goal → act)
references/                    # progressive-disclosure detail:
  plan-mode-interview.md       #   the question bank + how to default
  spec-template.md             #   the required spec sections
  goal-prompt-cookbook.md      #   /goal condition patterns + examples
  state-file-template.md       #   the loop's memory / hand-off file
  loop-engineering-14-steps.md #   the methodology
  cross-agent-adapters.md      #   Codex / Hermes / openclaw equivalents
examples/ecommerce-spec-example.md   # a complete worked spec + /goal
benchmark/                     # the A/B: scenarios, graders, runs, results
```

## Design principle

**A loop is only as trustworthy as its grader and your review of the diff.**
Everything in this skill exists to protect that one idea: make "done" something a
machine can check, bound the loop, and keep a human reviewing what it ships.

## References

- [Effective harnesses for long-running agents — Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Claude Code best practices](https://code.claude.com/docs/en/best-practices)
- E-commerce agent benchmarks the scenarios draw on: EcomBench, RetailBench, YC-Bench, EcoGym.
