# Scenario 3 — Listing optimization (fuzzy merchant request)

> Exact prompt given to both A/B arms.

"My product pages are weak and some are getting flagged by the marketplace. Can you
rewrite the listings in `data/products.json` so they're better and compliant? Keep
the real product details accurate."

## Assets
- `data/products.json` — 40 products: `id, brand, category, raw_title, specs{capacity_ml,color,material,warranty_years,weight_kg}`
- `data/banned_claims.txt` — phrases the marketplace prohibits
- `tools/qc_listings.py` — the grader

## Hidden rubric
Per product, all must hold for `hard_pass`: present in output; title 1–80 chars;
≥5 non-empty bullets; meta description 50–160 chars; no banned claim anywhere; the
source specs (capacity number, color, material, warranty years) preserved in the
text. Score weights each check across all products. Output expected at
`out/listings.json` (list of `{id,title,bullets[],meta_description,specs?}`).
