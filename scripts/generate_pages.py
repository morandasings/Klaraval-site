import csv, os, re, sys

SRC = "data/offers.csv"
OUTDIR = "site/content"
os.makedirs(OUTDIR, exist_ok=True)

REQUIRED = [
    "slug","type","keyword","intent","title","h1","meta_title","meta_desc",
    "pick_1","pick_2","pick_3","persona","USP_1","USP_2","USP_3",
    "cta_text","aff_link_1","aff_link_2","aff_link_3","status"
]

def slugify(s):
    s = (s or "").strip().lower()
    s = s.replace("å","a").replace("ä","a").replace("ö","o")
    s = re.sub(r"[^a-z0-9\- ]+","", s)
    s = re.sub(r"\s+","-", s)
    return s or "saknar-slug"

def safe(x): return (x or "").strip()

def validate_headers(headers):
    missing = [h for h in REQUIRED if h not in (headers or [])]
    if missing:
        print("ERROR: Saknade kolumner:", ", ".join(missing))
        sys.exit(1)

def write_page(row):
    slug = safe(row.get("slug")) or slugify(row.get("keyword"))
    title = safe(row.get("title")) or slug
    h1 = safe(row.get("h1")) or title
    meta_desc = safe(row.get("meta_desc"))[:155]

    p1, p2, p3 = safe(row.get("pick_1")), safe(row.get("pick_2")), safe(row.get("pick_3"))
    a1 = safe(row.get("aff_link_1")) or "#"
    a2 = safe(row.get("aff_link_2")) or "#"
    a3 = safe(row.get("aff_link_3")) or "#"

    usp1, usp2, usp3 = safe(row.get("USP_1")), safe(row.get("USP_2")), safe(row.get("USP_3"))
    cta = safe(row.get("cta_text")) or "Prova rekommendation #1"

    body = f"""---
layout: post
title: "{title}"
description: "{meta_desc}"
---

# {h1}

**Snabbt svar:** Rek. #1 → [{p1}]({a1})

## Varför dessa val?
- {usp1}
- {usp2}
- {usp3}

### Fördelar
- …

### Nackdelar
- …

## Jämförelse
| Tjänst | Bäst för | Pris/plan | Noter |
|---|---|---|---|
| {p1} | … | … | … |
| {p2} | … | … | … |
| {p3} | … | … | … |

**Rekommenderad nästa åtgärd:** {cta}

---
*Affiliate-disclaimer: Vissa länkar är affiliatelänkar och kan ge oss provision utan extra kostnad för dig.*
"""
    path = os.path.join(OUTDIR, f"{slug}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)

def main():
    if not os.path.exists(SRC):
        print("ERROR: Hittar inte", SRC); sys.exit(1)
    with open(SRC, newline='', encoding="utf-8") as f:
        r = csv.DictReader(f)
        validate_headers(r.fieldnames)
        n=0
        for row in r:
            if safe(row.get("keyword")):
                write_page(row); n+=1
        print(f"OK: Genererade {n} sidor → {OUTDIR}")

if __name__ == "__main__":
    main()
