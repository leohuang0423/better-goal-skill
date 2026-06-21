---
name: goal-loop
description: >-
  Turn a vague long-horizon request into a runnable autonomous loop. Use when a
  task is big, multi-step, repetitive, or will run unattended across many turns
  ("set a goal", "run until done", "keep going until tests pass", "/goal", "loop
  on this", "spec this out", "long-running task", "automate this workflow"). The
  skill interviews the user with a few sharp questions, writes a high-quality
  SPEC (background, goal, success criteria, proven methods, workflow standard),
  defines a verifiable stop condition, then sets the goal and runs in act mode.
when_to_use: >-
  Long-horizon / autonomous / unattended work; anything you want to "/goal";
  repeated operational tasks (e-commerce ops, pricing, inventory, content,
  migrations, refactors, data pipelines). Skip for one-shot questions.
argument-hint: "[one-line description of the long-horizon task]"
---

# goal-loop — make a long-horizon task actually runnable

You are about to help the user turn a fuzzy, ambitious request into a loop that a
general agent (Claude Code, Codex, Hermes, openclaw, …) can run mostly on its own
and that you can trust. Do **not** jump straight to doing the work. A long-horizon
loop that starts from a vague goal burns tokens going in circles. Five minutes of
structure up front is the highest-leverage thing you can do.

This skill drives three phases in order. Announce each phase in one line so the
user knows where they are.

```
  PLAN MODE  ──►  /goal  ──►  ACT MODE
  (interview      (set stop      (run the
   + write spec)   condition)     loop)
```

---

## Phase 0 — Triage (do this silently, ~10s)

Before interviewing, decide whether a loop is even the right tool. Run the
**"should I build a loop?" gate** from `references/loop-engineering-14-steps.md`
(steps 1–5). The short version — a loop is worth it only if **all five** hold:

1. **Repetitive / long.** Worth more than one good one-shot prompt. *(One-off → just do it well, skip this skill.)*
2. **Auto-gradable.** There is something that can mechanically say "this is wrong" — a test, a build, a type check, a linter, a metric threshold, a checklist the agent can verify. **No grader → no loop.** This is the single most important gate.
3. **Budget tolerates waste.** Loops burn tokens even when they make no progress.
4. **Reproducible & observable.** The agent can run its own output, see logs, and tell where it broke.
5. **You will actually review the output.** If nobody reads the diff, don't build it.

If a gate fails, say so plainly and offer the cheaper alternative (a single
well-formed prompt, or a manual run first). Do not build a loop just because you
were asked to.

---

## Phase 1 — PLAN MODE: interview, then write the spec

> **Claude Code:** enter plan mode now (the user can press `Shift+Tab`, or you can
> work read-only). Plan mode is read-only by design — perfect for interviewing and
> drafting without touching anything. **Other agents:** stay in a read-only /
> discussion posture; do not edit files yet. See `references/cross-agent-adapters.md`.

### 1a. Ask a few sharp questions — not a survey

Ask **3–6 questions max**, batched into one message, and only the ones whose
answers would change the spec. Default aggressively from context; ask only what
you genuinely cannot infer. The standard interview set lives in
`references/plan-mode-interview.md`. The backbone is:

1. **Done-looks-like.** "When this is finished, what is true that isn't true now?" (one or two sentences)
2. **The grader.** "How will we *mechanically* know it worked — which command, metric, or check decides pass/fail?" (this becomes the `/goal` stop condition)
3. **Guardrails.** "What must NOT change or break? What is off-limits to touch?"
4. **Inputs & access.** "What data, credentials, repos, or tools does the agent need, and does it have them now?"
5. **Budget & bound.** "How long / how many turns / how much spend before we stop and check in even if not done?"
6. **Prior art.** "Is there an existing example, a past good run, or a house style to imitate?"

If the user already answered some of these in their request, reflect them back
("I'll assume X — correct me") instead of re-asking. Never ask more than you need.

### 1b. Write the SPEC

Produce a single high-quality spec using `references/spec-template.md`. It **must**
contain all of these sections (this is the quality bar — a spec missing any of
these is incomplete):

- **Background & Goal** — why this exists and the one-line objective.
- **Success Criteria** — *measurable*, *verifiable* end states. Each one names the check that proves it. This is the heart of the spec.
- **Proven Methods & Recommendations** — concrete, battle-tested guidance for *this kind* of task so the agent doesn't rediscover it each loop (the "Skill" from step 7).
- **Workflow Standard** — the repeatable loop: gather context → act → verify → record state → repeat; plus the hard gate (what auto-rejects a turn).
- **Constraints & Guardrails** — what must not change, scope limits, permissions.
- **State & Hand-off** — where progress is recorded (`references/state-file-template.md`) so the next turn/session resumes cleanly.
- **Out of scope / Stop & escalate** — when to stop and ask a human.

Write the spec to a file in the working repo (e.g. `SPEC.md` or
`specs/<task>.md`) so it survives context compaction and the loop can re-read it.

### 1c. Get one approval

Show the user the spec and the proposed `/goal` stop condition **together** and
ask for a single go/no-go. This is the last cheap checkpoint before tokens start
burning. Refine on feedback; loop here, not in act mode.

> **Claude Code:** this is the natural `ExitPlanMode` moment — present the plan +
> spec, and on approval switch out of plan mode into act mode.

---

## Phase 2 — /goal: set a verifiable stop condition

Convert the **grader** (success criterion) into a `/goal` condition. A good
condition is one *measurable end state* + *how it's checked* + *what must stay
true* + an *upper bound*. Use `references/goal-prompt-cookbook.md` for patterns
and worked examples. Shape:

```
/goal <end state in one line>. Verified by: <exact command / metric / check that
decides pass>. Must stay true: <invariants that must not break>. Stop and ask me
if <ambiguity / risk / missing access>, or after <N turns / T minutes / $X> even
if not done.
```

Rules of thumb:
- **One end state, not a to-do list.** The condition is a *finish line*, not the plan. The plan lives in the spec.
- **Make it falsifiable.** If a fresh evaluator can't tell pass from fail by reading it, rewrite it.
- **Always bound it.** A loop with no turn/time/spend cap is how you wake up to a surprise bill.
- **Name the escape hatch.** Tell the loop when to stop and escalate instead of guessing.

> **Claude Code:** `/goal` is a session-scoped Stop hook — after each turn a fast
> model checks the condition; if unmet the agent continues automatically; it
> auto-clears when met. **Codex / Hermes / openclaw:** there's no native `/goal`;
> emulate it with the loop driver + state file in `references/cross-agent-adapters.md`
> (run-verify-record until the check passes or the bound is hit).

---

## Phase 3 — ACT MODE: run the loop

> **Claude Code:** switch to act mode (e.g. acceptEdits) so the loop runs without a
> prompt on every edit. Keep the hard gate (tests/build/linter) as the real
> guardrail — speed comes from the gate, not from skipping review.

Each turn follows the **Workflow Standard** from the spec:

1. **Re-orient** — read the spec + state file. Never trust memory across turns.
2. **Smallest next step** — pick the next incomplete item; do one coherent unit.
3. **Verify** — run the grader (test/build/check/metric). If it fails, treat that as the signal and fix; do not advance.
4. **Record state** — update the state file: what's done, what's next, what's blocked, key decisions/costs.
5. **Respect the gate & bound** — if the hard gate fails, the turn doesn't count as progress. If a bound or escalation trigger is hit, stop and report.

Scale-out (only when the task warrants it — steps 10–13 of the 14-step roadmap):
- **Parallel work** → give each agent its own git **worktree** so they don't fight over the same files.
- **Connectors** → let the loop open a PR, update a ticket, post a status.
- **Sub-agents** → split *doing* (writer) from *judging* (reviewer/grader) for an independent second opinion.

### Landing it (step 14 — the hardest one)
When the goal condition is met, stop and **report cost + diff**, not just "done":
what changed, what it cost, what you'd watch next, and which permissions the loop
held. Long-horizon autonomy is only safe if every accepted change is reviewed and
the loop is never quietly handed the architecture.

---

## Files in this skill

| File | When to read it |
|---|---|
| `references/plan-mode-interview.md` | Phase 1 — the question bank + how to default |
| `references/spec-template.md` | Phase 1 — fill-in spec with all required sections |
| `references/goal-prompt-cookbook.md` | Phase 2 — `/goal` condition patterns + examples |
| `references/state-file-template.md` | Phase 1/3 — the progress/hand-off file |
| `references/loop-engineering-14-steps.md` | Phase 0 + scale-out — the full methodology |
| `references/cross-agent-adapters.md` | Any phase — Codex / Hermes / openclaw equivalents |
| `examples/ecommerce-spec-example.md` | A complete worked spec + `/goal` you can imitate |
| `benchmark/` | Evidence this skill helps (3 e-commerce scenarios, rubric, results) |

**Golden rule:** the loop is only as good as its grader. Spend your effort making
success *mechanically checkable*; everything else in this skill exists to protect
that one idea.
