# -*- coding: utf-8 -*-
import os, csv, re, sys, time

CSV_PATH = "data/offers.csv"
OUT_DIR  = "site/content"          # varje sida blir /site/content/<slug>/index.html
BASE_URL = os.environ.get("BASE_URL", "https://morandasings.github.io/Klaraval-site")
SITEMAP  = "sitemap.xml"

REQUIRED = [
    "slug","type","keyword","intent","title","h1","meta_title","meta_desc",
    "pick_1","pick_2","pick_3","persona","USP_1","USP_2","USP_3",
    "cta_text","aff_link_1","aff_link_2","aff_link_3","status"
]

def safe(x): return (x or "").strip()

def slugify(s):
    s = safe(s).lower()
    s = s.replace("å","a").replace("ä","a").replace("ö","o")
    s = re.sub(r"[^a-z0-9\- ]+","", s)
    s = re.sub(r"\s+","-", s)
    return s or "saknar-slug"

PAGE_TMPL = """<!doctype html>
<html lang="sv"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{meta_title}</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="{canonical}">
<link rel="stylesheet" href="/Klaraval-site/styles.css">
</head><body>
<div class="container">
<header>
  <div class="logo">KlaraVal</div>
  <nav><ul>
    <li><a href="/Klaraval-site/">Start</a></li>
    <li><a href="/Klaraval-site/robots.txt" rel="nofollow">robots.txt</a></li>
    <li><a href="/Klaraval-site/sitemap.xml">Sitemap</a></li>
  </ul></nav>
</header>

<section class="hero">
  <h1>{h1}</h1>
  <p class="description">{meta_desc}</p>
</section>

<section class="cards">
  <div class="card">
    <h3>Rekommenderad #1</h3>
    <p>{usp1}</p>
    <a href="{aff1}" rel="nofollow">{pick1} →</a>
  </div>
  <div class="card">
    <h3>Alternativ #2</h3>
    <p>{usp2}</p>
    <a href="{aff2}" rel="nofollow">{pick2} →</a>
  </div>
  <div class="card">
    <h3>Alternativ #3</h3>
    <p>{usp3}</p>
    <a href="{aff3}" rel="nofollow">{pick3} →</a>
  </div>
</section>

<footer>© 2025 KlaraVal – Vissa länkar kan vara affiliatelänkar.</footer>
</div></body></html>
"""

def ensure_dirs():
    os.makedirs(OUT_DIR, exist_ok=True)

def validate_headers(headers):
    missing = [h for h in REQUIRED if h not in (headers or [])]
    if missing:
        print("ERROR: Saknade kolumner:", ", ".join(missing)); sys.exit(1)

def write_page(row):
    slug = safe(row.get("slug")) or slugify(row.get("keyword"))
    folder = os.path.join(OUT_DIR, slug)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "index.html")
    html = PAGE_TMPL.format(
        meta_title = safe(row.get("meta_title") or row.get("title") or slug),
        meta_desc  = safe(row.get("meta_desc") or "Snabb jämförelse och rekommendationer."),
        canonical  = f"{BASE_URL}/content/{slug}/",
        h1   = safe(row.get("h1") or row.get("title") or slug),
        pick1= safe(row.get("pick_1") or "Val 1"),
        pick2= safe(row.get("pick_2") or "Val 2"),
        pick3= safe(row.get("pick_3") or "Val 3"),
        usp1 = safe(row.get("USP_1") or "Stark helhetslösning."),
        usp2 = safe(row.get("USP_2") or "Prisvärd för start."),
        usp3 = safe(row.get("USP_3") or "Bra för tillväxt."),
        aff1 = safe(row.get("aff_link_1") or "#"),
        aff2 = safe(row.get("aff_link_2") or "#"),
        aff3 = safe(row.get("aff_link_3") or "#"),
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return f"/content/{slug}/"

def build_sitemap(urls):
    ts = time.strftime("%Y-%m-%d")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    # startsida
    lines.append(f"  <url><loc>{BASE_URL}/</loc><lastmod>{ts}</lastmod></url>")
    # varje genererad sida
    for u in urls:
        lines.append(f"  <url><loc>{BASE_URL}{u}</loc><lastmod>{ts}</lastmod></url>")
    lines.append("</urlset>")
    with open(SITEMAP, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    ensure_dirs()
    if not os.path.exists(CSV_PATH):
        print("ERROR: Hittar inte", CSV_PATH); sys.exit(1)

    urls, n = [], 0
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        if not r.fieldnames: 
            print("ERROR: CSV saknar header-rad."); sys.exit(1)
        validate_headers(r.fieldnames)
        for row in r:
            if not safe(row.get("keyword")): 
                continue
            urls.append(write_page(row)); n += 1

    build_sitemap(urls)
    print(f"OK: genererade {n} sidor och uppdaterade sitemap.")

if __name__ == "__main__":
    main()
