import os, urllib.request, ssl
BASE = "https://www.volkswagenbangalore.in/"
OUT  = "web/assets/img"
ssl._create_default_https_context = ssl._create_unverified_context

paths = set()
for root, _, files in os.walk("scrape"):
    for f in files:
        if not f.endswith(".html"): continue
        html = open(os.path.join(root, f), encoding="utf-8", errors="ignore").read()
        import re
        for m in re.finditer(r'(?:src|data-src)="(assets/images/[^"]+?\.(?:webp|jpg|jpeg|png))(?:\?[^"]*)?"', html):
            paths.add(m.group(1))

ok = fail = 0
for p in sorted(paths):
    dest = os.path.join(OUT, p.replace("assets/images/", ""))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        ok += 1; continue
    try:
        req = urllib.request.Request(BASE + p, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=30).read()
        if len(data) < 100: raise ValueError("too small")
        open(dest, "wb").write(data); ok += 1
    except Exception as e:
        fail += 1; print("  FAIL", p, e)
print(f"\nDownloaded {ok} assets, {fail} failed")
