"""Gradi output/top50.html: skor po 4 kriterijuma (prihod x2) iz analysis/top50_scores_*.json + katalog global_items.json.
Pokretanje: python scripts/07_build_top50.py
"""
import json

from common import DATA, OUTPUT, ROOT, TODAY, load_json

MAX_US = 3000
NAV = ('<nav class="top"><a href="index.html">Top 100 apps</a><a href="top50.html" class="on">Top 50 picks</a>'
       '<a href="global.html">Global Finds</a><a href="insights.html">Insights</a></nav>')


def main():
    items = {i["key"]: i for i in load_json(DATA / "global" / "global_items.json")}
    scores = {}
    for p in sorted((ROOT / "analysis").glob("top50_scores_*.json")):
        scores.update(load_json(p))
    rows = []
    for key, s in scores.items():
        it = items.get(key)
        if not it or s.get("exclude"):
            continue
        if (it.get("ratings_us") or 0) > MAX_US:  # vec popularna u SAD
            continue
        sc = s["scores"]
        total = round((sc["build"] + sc["marketing"] + sc["retention"] + 2 * sc["revenue"]) / 30 * 100)
        rows.append({**{k: s.get(k) for k in ("product", "audience", "revenue_why", "retention_how", "tiktok_hook", "risk")},
                     "scores": sc, "total": total, "name": it.get("name_en") or it["name"], "country": it["country"],
                     "lenses": it.get("lenses"), "icon": it.get("icon"), "url": it.get("url"),
                     "ratings_local": it.get("ratings_local"), "ratings_us": it.get("ratings_us"), "in_us": it.get("in_us")})
    rows.sort(key=lambda r: (-r["total"], -r["scores"]["revenue"], -(r["ratings_local"] or 0)))
    seen, top = set(), []
    for r in rows:  # bez duplikata po nazivu
        k = r["name"].lower()[:18]
        if k in seen:
            continue
        seen.add(k)
        top.append(r)
    top = top[:50]
    for n, r in enumerate(top, 1):
        r["rank"] = n
    data = {"items": top, "pool": len(scores), "date": TODAY}
    tpl = (ROOT / "scripts" / "top50_template.html").read_text(encoding="utf-8")
    page = tpl.replace("__NAV__", NAV).replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    (OUTPUT / "top50.html").write_text(page, encoding="utf-8")
    print(f"top50.html: {len(top)} izbora od {len(scores)} ocenjenih, prosek {sum(r['total'] for r in top) / max(1, len(top)):.0f}")


if __name__ == "__main__":
    main()
