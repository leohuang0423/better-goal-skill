# /goal prompt cookbook

The `/goal` condition is what a fast evaluator checks after every turn to decide
"keep going" vs "done." It is a **finish line, not a plan**. The plan lives in the
spec; the goal is the single line that says when to stop.

## The shape

```
/goal <one-line end state>. Verified by: <exact command / metric / check that
decides pass>. Must stay true: <invariants>. Stop and ask me if <ambiguity / risk
/ missing access>, or after <N turns / T minutes / $X> even if not done.
```

Four ingredients, in order of importance:

1. **End state** — one measurable finish line. Not a list. ("all tests green", "queue empty", "report.csv exists and validates").
2. **Verified by** — the concrete check. If a stranger couldn't run it and get a yes/no, it's not a check yet.
3. **Must stay true** — invariants the loop must not break while chasing the goal.
4. **Bound + escape hatch** — a turn/time/spend cap, and when to stop and escalate.

## Rules of thumb

- **Falsifiable beats aspirational.** "Code is clean" → ✗. "`ruff check` and `pytest` exit 0" → ✓.
- **One end state.** Multiple finish lines? Either AND them into one verifiable check, or run sequential goals.
- **Always bound it.** No cap = possible runaway spend. Cap every goal.
- **Verify the verifier.** The check must be runnable by the agent *now*. A check that needs missing access is not a check.
- **Keep it under the limit.** `/goal` conditions cap at ~4,000 chars; put detail in the spec, keep the goal lean.
- **Re-read, don't remember.** The goal should point the loop back to `SPEC.md`/`STATE.md` each turn rather than restating everything.

## Worked examples

**Software — make CI green**
```
/goal All CI checks pass on this branch. Verified by: `npm test` and `npm run
lint` and `npm run build` all exit 0 locally, and the pushed commit shows a green
check. Must stay true: no test is deleted or skipped to pass; public API unchanged.
Stop and ask me if a fix needs an API change, or after 25 turns even if red.
```

**Migration / cleanup — bounded sweep**
```
/goal Every file under src/ uses the new logger API. Verified by: `rg "oldLogger\("
src/` returns no matches AND `npm test` exits 0. Must stay true: log output format
unchanged; no behaviour change beyond the logger swap. Stop after 20 turns or if
any test needs a non-mechanical change.
```

**E-commerce ops — metric threshold (see benchmark/)**
```
/goal A repricing plan for the 200 SKUs in data/skus.csv is written to
out/reprice.csv. Verified by: `python tools/check_reprice.py` exits 0 — every SKU
has a new price, none violates the MAP floor or the +/-15% move cap, and projected
margin in the report is >= current. Must stay true: never price below cost; never
touch SKUs flagged hold=true. Stop and ask me before any price cut >15%, or after
15 turns.
```

**Content / catalog — checklist grader**
```
/goal All 50 product listings in queue.csv are rewritten and pass QC. Verified by:
`python tools/qc_listings.py out/` exits 0 — each listing has title <=80 chars,
>=5 bullet features, no banned claims, and a filled meta description. Must stay
true: keep every factual spec from the source; don't invent certifications. Stop
and ask me if a source spec is missing, or after 20 turns.
```

## Converting a fuzzy ask into a goal

| Fuzzy ask | Make it checkable | Goal end state |
|---|---|---|
| "Clean up the codebase" | linter + tests | "`ruff` & `pytest` exit 0" |
| "Optimize our pricing" | margin/constraint checker | "reprice.csv passes check_reprice.py" |
| "Improve the listings" | QC script / rubric | "qc_listings.py exits 0 for all" |
| "Fix the flaky tests" | repeated runs | "`pytest -p no:randomly` green 5x in a row" |
| "Make it faster" | benchmark threshold | "bench p95 < 200ms, `make bench` confirms" |

If you can't fill the right column, you don't have a loop yet — go build the
grader first (a script, a rubric, a metric). That *is* the work.
