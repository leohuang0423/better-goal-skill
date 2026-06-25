# Loop Engineering — the 14-step roadmap

The methodology behind this skill. "Loop engineering" = building a self-running
agent loop you can trust, instead of babysitting a chat. It compresses to a
checklist in three parts: **decide → build the minimal loop → keep it safe in
production.** Grounded in practitioner experience and Anthropic's guidance on
[effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
and the gather→act→verify loop in [Claude Code best practices](https://code.claude.com/docs/en/best-practices).

---

## Part 1 · Decide whether to build a loop at all (steps 1–5)

A loop is overhead. It only pays off when the work is repetitive *and* mechanically
checkable. Run all five gates before building; if any fails, prefer a single good
prompt or a manual run.

1. **Confirm the work repeats.** One-off jobs are cheaper with a good one-shot prompt than with a loop.
2. **Confirm something can auto-judge "this failed."** A test, type check, linter, metric threshold, or verifiable checklist — at least one. *This is the make-or-break gate.* No grader → no loop.
3. **Confirm the token budget can absorb waste.** A loop burns tokens even on turns that make zero progress. Budget for the misses.
4. **Confirm the agent can run its own output.** Logs, reproducibility, visible failure points — the loop must see where it broke to fix it.
5. **Confirm you'll actually review the output.** If nobody reads the diff, don't build the loop. Unreviewed autonomy is how damage ships.

## Part 2 · Build a minimal loop that runs (steps 6–13)

6. **Get one manual run stable first.** Walk the whole task by hand once. Don't skip steps — the loop automates a sequence you've proven works.
7. **Distill project background into a Skill.** So every turn doesn't re-explain the context. (This repo is itself an example.)
8. **Add a state file.** Record what's done and what's next, so the loop survives compaction and resumes cleanly. (`state-file-template.md`)
9. **Set a hard gate.** If tests/build/checks don't pass, the turn is auto-rejected. The gate — not your attention — is what keeps quality up.
10. **Add automation + a stop condition.** Trigger the loop on a cadence and use `/goal` to define when it stops. (`goal-prompt-cookbook.md`)
11. **Parallelize with worktrees.** Multiple agents at once → give each its own git worktree so they don't clobber the same files.
12. **Wire up connectors.** Let the loop open PRs, update tickets, post to Slack — close the loop with the outside world.
13. **Split into sub-agents.** Separate the writer (does the work) from the reviewer/grader (judges it). An independent second opinion catches what the writer rationalizes.

## Part 3 · Keep it safe after it's live (step 14 — the hardest)

14. **Watch the cost of every accepted change.** Periodically re-review permissions, read the diffs, and never let the loop quietly own the architecture. Autonomy is a standing liability, not a one-time setup; the discipline is ongoing.

---

## How this skill maps to the roadmap

| Skill phase | Roadmap steps |
|---|---|
| Phase 0 — Triage gate | 1–5 |
| Phase 1 — Interview + spec (+ Skill, state file) | 6, 7, 8 |
| Phase 2 — `/goal` stop condition | 9, 10 |
| Phase 3 — Run the loop (+ scale-out) | 9, 10, 11, 12, 13 |
| Landing it / review discipline | 14 |

**The one idea to keep:** a loop is only as trustworthy as its grader and its
review. Steps 2 and 5/14 are the spine; the rest is plumbing around them.
