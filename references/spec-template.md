# SPEC template

Copy this into `SPEC.md` (or `specs/<task>.md`) in the working repo and fill every
section. The spec is the **durable** artifact — it survives context compaction and
is re-read at the top of every loop turn. A spec missing any required section below
is incomplete.

> Keep it tight. A good spec is 1–2 pages, scannable, and every line earns its place.

---

```markdown
# SPEC: <task name>

> Status: DRAFT | APPROVED | IN PROGRESS | DONE
> Owner: <human>   Agent: <Claude Code / Codex / Hermes / openclaw>   Date: <date>

## 1. Background & Goal
<2–4 sentences: why this exists, what problem it solves, who cares.>
**Goal (one line):** <the single objective, stated as an outcome.>

## 2. Success Criteria  ← the heart of the spec
Each criterion is measurable and names the check that proves it. The loop is "done"
only when all of these pass.

- [ ] <End state #1> — **verified by:** `<exact command / metric / check>`
- [ ] <End state #2> — **verified by:** `<…>`
- [ ] <End state #3> — **verified by:** `<…>`

**Bound:** stop and check in after <N turns / T minutes / $X spend> even if unmet.

## 3. Proven Methods & Recommendations  (the "skill" — so the loop doesn't relearn)
Concrete, battle-tested guidance for THIS class of task. Steal from prior runs,
house style, and the references. Examples:
- <Do X this way because Y.>
- <Known trap: Z — avoid by …>
- <Reference / example to imitate: …>

## 4. Workflow Standard  (the repeatable loop)
1. Re-orient: read this spec + the state file.
2. Pick the smallest next incomplete step.
3. Do one coherent unit of work.
4. **Verify** with the grader (Section 2 checks).
5. Record progress in the state file.
6. Repeat.

**Hard gate (auto-reject a turn):** <test/build/lint/metric that MUST pass for a
turn to count as progress>. If the gate fails, fix — do not advance.

## 5. Constraints & Guardrails
- Must NOT change: <files/systems/behaviour that are off-limits>.
- Scope limits: <what's explicitly excluded>.
- Permissions: <what the agent may/may not do without asking>.

## 6. State & Hand-off
- State file: `<path, e.g. STATE.md>` (template: references/state-file-template.md).
- On stop/compaction, the next turn resumes from the state file alone.

## 7. Out of Scope / Stop & Escalate
- Out of scope: <…>.
- Stop and ask a human if: <ambiguity / risk / missing access / repeated failure>.
```

---

## Why every section is required

| Section | What breaks if you skip it |
|---|---|
| Background & Goal | Loop optimizes the wrong thing. |
| **Success Criteria** | No grader → loop can't tell done from not-done → never stops or stops wrong. |
| Proven Methods | Loop rediscovers the same lessons every turn, wasting tokens. |
| Workflow Standard | Turns become inconsistent; no hard gate → bad work passes. |
| Constraints | Loop "helpfully" breaks something it shouldn't have touched. |
| State & Hand-off | Context compaction wipes progress; loop restarts from zero. |
| Stop & Escalate | Loop guesses on ambiguity instead of asking; small error compounds. |
