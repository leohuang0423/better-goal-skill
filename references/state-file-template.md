# State / hand-off file template

The state file is the loop's memory. Agents work in discrete turns/sessions with
no reliable memory between them; after context compaction the loop must be able to
resume from this file **alone**. Update it at the end of every turn.

Write it to a fixed path (e.g. `STATE.md`) named in the spec.

---

```markdown
# STATE: <task name>

> Last updated: <turn N, timestamp>   Goal: <one-line stop condition>

## Done
- [x] <completed step> — verified by <check that passed> @ turn <n>
- [x] <…>

## Next (in order)
1. <the single next action>
2. <then>
3. <then>

## Blocked / needs human
- <thing> — blocked on <what> — escalate? <y/n>

## Key decisions & rationale
- <decision> because <reason> (so we don't relitigate it next turn)

## Grader status
- <check 1>: PASS/FAIL (last run: turn <n>)
- <check 2>: PASS/FAIL

## Budget
- Turns used: <n> / <bound>   |   Spend: <$ / bound>   |   Notable cost spikes: <…>

## Scratch / breadcrumbs
- <where the relevant files are, commands that work, gotchas hit>
```

---

## Rules

- **One source of truth.** The state file + spec are authoritative; conversation
  memory is not. Each turn: read both first.
- **Smallest-next-step on top.** "Next" should let a cold-start agent act in one read.
- **Record decisions, not just actions.** Prevents the loop from re-debating settled choices.
- **Track the grader and the budget.** These two tables are how you know whether to
  keep looping or stop.
- **Keep it current, keep it short.** Prune stale "Next" items; move them to Done or
  drop them. A stale state file is worse than none.
