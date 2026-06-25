# Cross-agent adapters

The methodology (plan → spec → bounded loop with a grader → review) is universal.
The *mechanics* differ per agent. This skill targets Claude Code natively and
degrades gracefully elsewhere. Map the three primitives — **plan posture**,
**stop condition**, **act posture** — onto whatever your agent provides.

## The three primitives

| Primitive | What it must give you |
|---|---|
| **Plan posture** | A read-only mode to interview + draft the spec without changing anything. |
| **Stop condition** | A way to check a grader after each turn and keep going until it passes or a bound is hit. |
| **Act posture** | A way to run the loop without approving every single edit, while the hard gate stays in force. |

---

## Claude Code (native)

| Primitive | Mechanism |
|---|---|
| Plan posture | **Plan mode** — `Shift+Tab` to cycle in; read-only by design. `--permission-mode plan` or `defaultMode: "plan"` to start there. |
| Stop condition | **`/goal <condition>`** — session-scoped prompt Stop hook; a fast model checks after each turn, continues if unmet, auto-clears when met. `/goal clear` to cancel. |
| Act posture | `Shift+Tab` to **acceptEdits**/auto; hard gate (tests/build/lint) remains the guardrail. |
| Skill | This `SKILL.md` auto-loads from `.claude/skills/goal-loop/` or `~/.claude/skills/`. |
| State | `STATE.md` re-read each turn; survives `/clear` + compaction. |
| Scale-out | Sub-agent `isolation: worktree`; Agent/Task tool for writer/reviewer split. |

Native flow: enter plan mode → interview → write `SPEC.md` → `ExitPlanMode` on
approval → `/goal "<condition>"` → act mode → loop.

## Codex (CLI / cloud)

| Primitive | Mechanism |
|---|---|
| Plan posture | Start in a read-only / suggest posture; discuss + draft `SPEC.md` before granting write/auto. |
| Stop condition | No native `/goal`. **Emulate:** wrap the run in a driver loop — `while ! <grader>; do codex exec "<continue from STATE.md>"; (( n++ >= BOUND )) && break; done`. The grader's exit code is the stop condition. |
| Act posture | Full-auto / workspace-write mode with the grader as the gate. |
| State | Same `SPEC.md` + `STATE.md` files. |

## Hermes agent

| Primitive | Mechanism |
|---|---|
| Plan posture | Use its planning/clarification phase to run the interview and emit the spec as the task contract. |
| Stop condition | Encode the grader as the task's completion check / success predicate; bound by max-steps. Re-evaluate each step. |
| Act posture | Execution phase; keep the hard gate as a required step before "complete." |
| State | Persist `SPEC.md` + `STATE.md` in the workspace; reload each step. |

## openclaw (and other generic agent runners)

| Primitive | Mechanism |
|---|---|
| Plan posture | Read-only/dry-run first pass; produce `SPEC.md`. |
| Stop condition | External driver: re-invoke the agent with "resume from STATE.md" until `<grader>` exits 0 or the bound trips. The driver *is* your `/goal`. |
| Act posture | Normal run; CI/tests/linter as the non-negotiable gate. |
| State | `SPEC.md` + `STATE.md` on disk. |

---

## Generic `/goal` emulation (works anywhere)

When there's no native stop hook, this shell pattern reproduces it:

```bash
#!/usr/bin/env bash
# goal-loop.sh — emulate /goal for any agent CLI
BOUND=${BOUND:-20}; n=0
until <YOUR_GRADER_COMMAND>; do          # e.g. ./check.sh  (exit 0 == done)
  (( n++ >= BOUND )) && { echo "bound hit at $n turns"; exit 1; }
  echo "turn $n: grader red, continuing"
  <AGENT_CLI> "Resume the task. Read SPEC.md and STATE.md. Do the smallest next \
step, run the grader, update STATE.md. Stop and report if blocked."
done
echo "goal met after $n turns"
```

Swap `<YOUR_GRADER_COMMAND>` and `<AGENT_CLI>`. The invariants are the same on
every agent: **a written spec, a mechanical grader, a bounded loop, a state file,
and human review of the diff.** Lose any of those and it stops being safe
automation and becomes an expensive random walk.

> Mechanism details (flags, mode names) evolve per agent version — treat the table
> entries as the *role* each feature plays, and check your agent's current docs for
> the exact command.
