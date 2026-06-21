# Plan-Mode Interview — the question bank

Goal of this phase: extract just enough to write a spec a loop can run without you.
**Ask 3–6 questions, batched into one message.** Every question you ask should be
one whose answer would *change the spec*. If you can infer an answer from the
request or the repo, state your assumption instead of asking.

> Posture: read-only. Claude Code → plan mode (`Shift+Tab`). Other agents → discuss
> only, no edits yet.

## The six load-bearing questions

| # | Ask | Why it matters | Feeds spec section |
|---|---|---|---|
| 1 | **Done-looks-like:** "When this is finished, what is true that isn't true now?" | Forces a finish line, not a vibe. | Background & Goal |
| 2 | **The grader:** "How do we *mechanically* know it worked — which command, metric, or check decides pass/fail?" | No grader → no loop. Becomes the `/goal` condition. | Success Criteria |
| 3 | **Guardrails:** "What must NOT change or break? What's off-limits?" | Prevents the loop from 'fixing' the wrong thing. | Constraints |
| 4 | **Inputs & access:** "What data / credentials / repos / tools are needed, and are they available now?" | A loop blocked on access just burns tokens. | Background, Workflow |
| 5 | **Budget & bound:** "How many turns / how long / how much spend before we stop and check in?" | Every loop must be bounded. | Success Criteria / Stop |
| 6 | **Prior art:** "Any existing example, past good run, or house style to imitate?" | Lets the agent match, not invent. | Proven Methods |

## Sharpening follow-ups (use only if the answer is fuzzy)

- If the grader is subjective ("make it good"): "If two people disagreed on whether it's done, what fact would settle it?" → convert to a rubric or threshold.
- If success is a metric: "What's the baseline today, and what target counts as success?" → get a number.
- If scope is huge: "If we could only ship one slice this week, which one?" → shrink to a runnable loop.
- If access is unclear: "Can you confirm the agent can run X right now?" → de-risk before looping.

## How to default instead of asking

You usually have a repo, a CLAUDE.md, prior commits, and the user's phrasing. Mine
them. Examples of good defaulting:
- Tests exist → assume the grader is `<test command>`; confirm in one line.
- There's a lint/CI config → assume those are part of the gate.
- The request says "until all tests pass" → criterion #2 is already answered.
- House style is visible in the codebase → assume "match surrounding code."

State assumptions as: **"I'll assume X — tell me if that's wrong."** Then proceed.
Re-asking something the user already told you is a worse failure than a wrong
assumption they can correct in one word.

## Anti-patterns

- ❌ A 12-question intake form. (You will lose the user before the work starts.)
- ❌ Asking things you can read from the repo.
- ❌ Accepting "make it better" as a success criterion. Pin it to a check.
- ❌ Skipping the grader question because the task "seems obvious." It never is.
