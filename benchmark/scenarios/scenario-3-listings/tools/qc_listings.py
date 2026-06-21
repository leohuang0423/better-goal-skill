#!/usr/bin/env python3
"""Grader for Scenario 3 (listing optimization / QC).

Checks agent-rewritten listings for marketplace compliance and fidelity to the
source specs. Exit 0 iff all hard constraints pass for every product.

Usage: python qc_listings.py [--products PATH] [--banned PATH] [--out PATH] [--json]
Output format: JSON list of objects:
  {"id","title","bullets":[...],"meta_description", optional "specs":{...}}
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEF_PROD = os.path.join(HERE, "..", "data", "products.json")
DEF_BANNED = os.path.join(HERE, "..", "data", "banned_claims.txt")
DEF_OUT = os.path.join(HERE, "..", "out", "listings.json")

TITLE_MAX = 80
MIN_BULLETS = 5
META_MIN, META_MAX = 50, 160


def load_json(p, default):
    if not os.path.exists(p):
        return default
    with open(p) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default


def spec_tokens(specs):
    """The factual values that must survive into the listing text."""
    toks = []
    for k, v in specs.items():
        if k == "capacity_ml":
            toks.append(str(v))            # number must appear
        elif k == "warranty_years":
            toks.append(str(v))
        else:
            toks.append(str(v).lower())
    return toks


def grade(products, banned, out):
    by_id = {o.get("id"): o for o in out if isinstance(o, dict)}
    n = len(products)
    per = []
    all_pass = True

    for p in products:
        pid = p["id"]
        o = by_id.get(pid)
        checks = {
            "present": False,
            "title_ok": False,
            "bullets_ok": False,
            "meta_ok": False,
            "no_banned": False,
            "specs_preserved": False,
        }
        if o:
            checks["present"] = True
            title = str(o.get("title", "")).strip()
            bullets = o.get("bullets", []) or []
            meta = str(o.get("meta_description", "")).strip()
            blob = " ".join([title, " ".join(map(str, bullets)), meta]).lower()

            checks["title_ok"] = 0 < len(title) <= TITLE_MAX
            checks["bullets_ok"] = (
                isinstance(bullets, list)
                and len([b for b in bullets if str(b).strip()]) >= MIN_BULLETS
            )
            checks["meta_ok"] = META_MIN <= len(meta) <= META_MAX
            checks["no_banned"] = not any(
                re.search(r"\b" + re.escape(b.lower()) + r"\b", blob) for b in banned
            )
            toks = spec_tokens(p["specs"])
            checks["specs_preserved"] = all(t in blob for t in toks)

        passed = all(checks.values())
        all_pass = all_pass and passed
        per.append({"id": pid, "pass": passed, "checks": checks})

    # aggregate score: average of per-check pass rates across products
    keys = ["present", "title_ok", "bullets_ok", "meta_ok", "no_banned", "specs_preserved"]
    weights = {"present": 10, "title_ok": 15, "bullets_ok": 20, "meta_ok": 15,
               "no_banned": 20, "specs_preserved": 20}
    score = 0.0
    for k in keys:
        rate = sum(1 for r in per if r["checks"][k]) / n if n else 0
        score += weights[k] * rate

    fully_compliant = sum(1 for r in per if r["pass"])
    return {
        "hard_pass": all_pass,
        "score": round(score, 1),
        "products": n,
        "fully_compliant": fully_compliant,
        "compliance_rate": round(fully_compliant / n, 4) if n else 0,
        "check_rates": {
            k: round(sum(1 for r in per if r["checks"][k]) / n, 4) if n else 0
            for k in keys
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--products", default=DEF_PROD)
    ap.add_argument("--banned", default=DEF_BANNED)
    ap.add_argument("--out", default=DEF_OUT)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    products = load_json(a.products, [])
    banned = []
    if os.path.exists(a.banned):
        with open(a.banned) as f:
            banned = [ln.strip() for ln in f if ln.strip()]
    out = load_json(a.out, [])
    res = grade(products, banned, out)
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        for k, v in res.items():
            print(f"{k}: {v}")
    sys.exit(0 if res["hard_pass"] else 1)


if __name__ == "__main__":
    main()
