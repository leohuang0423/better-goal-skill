# STATE: Rewrite & compliance-fix 40 product listings

> Last updated: turn 2, 2026-06-21   Goal: `qc_listings.py` exits 0 (hard_pass=true) for all 40 products

## Done
- [x] Decoded grader `qc_listings.py` (spec tokens, banned regex, length bounds) @ turn 1
- [x] Wrote SPEC.md with measurable success criteria @ turn 1
- [x] Wrote deterministic generator `gen_listings.py` (bakes spec tokens into bullets) @ turn 1
- [x] Generated out/listings.json (40 listings) — grader hard_pass=true, score=100.0 @ turn 1
- [x] Grammar polish: "{n}-year warranty" compound form; regen + re-grade still pass @ turn 2

## Next (in order)
1. (none — goal met) Optional: vary bullet phrasing per category for richer copy.

## Blocked / needs human
- none

## Key decisions & rationale
- Capacity stated as neutral "{cap} ml capacity" line — preserves required token without
  asserting a nonsensical claim on non-container items (data is intentionally noisy).
- weight_kg included for richness though grader does not check it.
- No superlative/health claims at all -> structurally immune to banned-phrase list.

## Grader status
- present/title_ok/bullets_ok/meta_ok/no_banned/specs_preserved: all PASS (rate 1.0) @ turn 2
- python tools/qc_listings.py exit 0, score 100.0, compliance_rate 1.0

## Budget
- Turns used: 2 / 10   |   Spend: minimal   |   No cost spikes

## Scratch / breadcrumbs
- Regenerate: `cd runs/s3-treatment && python gen_listings.py`
- Grade: `python ../../scenarios/scenario-3-listings/tools/qc_listings.py --out out/listings.json --json`
