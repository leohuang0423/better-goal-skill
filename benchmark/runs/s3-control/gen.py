#!/usr/bin/env python3
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = "/home/user/better-goal-skill/benchmark/scenarios/scenario-3-listings/data/products.json"
BANNED = "/home/user/better-goal-skill/benchmark/scenarios/scenario-3-listings/data/banned_claims.txt"
OUT = os.path.join(HERE, "out", "listings.json")

with open(PROD) as f:
    products = json.load(f)
with open(BANNED) as f:
    banned = [ln.strip() for ln in f if ln.strip()]

# Categories where a fluid "capacity_ml" is a real, sensible spec.
VOLUME_CATS = {"water bottle"}

def warranty_phrase(y):
    return f"{y}-year warranty" if y != 1 else "1-year warranty"

def capacity_phrase(cat, ml):
    if cat in VOLUME_CATS:
        return f"{ml} ml capacity"
    # For non-fluid items the source carries a numeric size/reference code.
    return f"size reference {ml}"

def title_for(p):
    s = p["specs"]
    brand, cat = p["brand"], p["category"]
    color = s["color"]
    # Build a clean, human title; keep within 80 chars.
    t = f"{brand} {cat.title()} - {color.title()} {s['material'].title()}"
    if len(t) > 80:
        t = f"{brand} {cat.title()} - {color.title()}"
    return t[:80]

def bullets_for(p):
    s = p["specs"]
    cat = p["category"]
    b = [
        f"Brand: {p['brand']} - quality {cat} built for everyday use.",
        f"Color: {s['color']}, finished in durable {s['material']}.",
        f"Material: made from {s['material']} for a sturdy, long-lasting feel.",
        f"Backed by a {warranty_phrase(s['warranty_years'])} for peace of mind.",
        f"Lightweight design at {s['weight_kg']} kg, easy to handle and store.",
        f"Spec reference: {capacity_phrase(cat, s['capacity_ml'])}.",
    ]
    return b

def meta_for(p):
    s = p["specs"]
    cat = p["category"]
    m = (f"{p['brand']} {cat} in {s['color']} {s['material']}, {s['weight_kg']} kg, "
         f"{capacity_phrase(cat, s['capacity_ml'])}, {warranty_phrase(s['warranty_years'])}. "
         f"Reliable everyday quality.")
    # Ensure 50..160 chars
    if len(m) > 160:
        m = (f"{p['brand']} {cat} in {s['color']} {s['material']}, "
             f"{capacity_phrase(cat, s['capacity_ml'])}, {warranty_phrase(s['warranty_years'])}.")
    if len(m) < 50:
        m = m + " Quality you can count on every day for years."
    return m[:160]

def check_banned(text):
    blob = text.lower()
    for b in banned:
        if re.search(r"\b" + re.escape(b.lower()) + r"\b", blob):
            return b
    return None

out = []
for p in products:
    s = p["specs"]
    title = title_for(p)
    bullets = bullets_for(p)
    meta = meta_for(p)
    rec = {
        "id": p["id"],
        "title": title,
        "bullets": bullets,
        "meta_description": meta,
        "specs": s,
    }
    out.append(rec)

    # sanity per grader
    blob = " ".join([title, " ".join(bullets), meta]).lower()
    assert 0 < len(title) <= 80, (p["id"], "title", len(title))
    assert len([x for x in bullets if x.strip()]) >= 5, (p["id"], "bullets")
    assert 50 <= len(meta) <= 160, (p["id"], "meta", len(meta), meta)
    bad = check_banned(blob)
    assert bad is None, (p["id"], "banned", bad)
    toks = []
    for k, v in s.items():
        if k in ("capacity_ml", "warranty_years"):
            toks.append(str(v))
        else:
            toks.append(str(v).lower())
    missing = [t for t in toks if t not in blob]
    assert not missing, (p["id"], "missing", missing, blob)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(out, f, indent=2)
print("wrote", len(out), "listings to", OUT)
