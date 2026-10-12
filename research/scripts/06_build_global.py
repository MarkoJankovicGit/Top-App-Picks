"""Gradi output/global.html iz: data/global/candidates.json + analysis/global_profiles_*.json + analysis/reddit_global_*.json
Radi i sa delimičnim podacima (preskače fajlove koji ne postoje).
Pokretanje: python scripts/06_build_global.py
"""
import re
from datetime import datetime

from common import DATA, OUTPUT, ROOT, TODAY, http_get, load_json, save_json, thresholds


def norm(s):
    return re.sub(r"[^a-z0-9Ѐ-ӿ֐-ۿऀ-ॿ぀-ヿ一-鿿가-힯]+", "", (s or "").lower())


CANON = ["India", "China", "Japan", "South Korea", "Korea", "Russia", "Ukraine", "Poland", "Turkey", "Brazil", "Mexico",
         "Indonesia", "Vietnam", "Thailand", "Philippines", "Pakistan", "Bangladesh", "Nigeria", "South Africa", "Egypt",
         "Saudi Arabia", "United Arab Emirates", "UAE", "Israel", "Serbia", "Iran", "Estonia", "Finland", "Germany",
         "Taiwan", "Hong Kong", "Singapore", "Malaysia", "Kenya", "Ghana", "Argentina", "Colombia", "Chile", "Peru",
         "Romania", "Armenia", "Palestin", "Sri Lanka", "Nepal", "Lebanon", "Jordan", "Morocco", "Tunisia"]
ALIAS = {"Korea": "South Korea", "UAE": "United Arab Emirates", "Palestin": "Palestine"}


def clean_country(c):
    if not c:
        return "Global / unknown"
    for k in CANON:
        if re.search(r"\b" + re.escape(k), c, re.I):
            return ALIAS.get(k, k)
    return "Global / unknown"


def glob_json(pattern):
    out = []
    for p in sorted((ROOT / "analysis").glob(pattern)):
        try:
            out.append(load_json(p))
        except Exception as e:  # pokvaren fajl ne sme da obori izgradnju
            print("preskačem", p.name, e)
    return out


def main():
    cfg = load_json(ROOT / "config" / "global_keywords.json")
    delay = thresholds()["requestDelaySeconds"]
    cand_path = DATA / "global" / "candidates.json"
    cands = {f"{a['cc']}:{a['id']}": a for a in (load_json(cand_path) if cand_path.exists() else [])}
    profiles = {}
    for d in glob_json("global_profiles_*.json"):
        profiles.update(d)
    reds = glob_json("reddit_global_*.json")

    items = []
    for key, a in cands.items():
        p = profiles.get(key)
        if not p or p.get("exclude"):
            continue
        fit = p.get("lens_fit") or {}
        lenses = [k for k in ("K1", "K2", "K3") if (fit.get(k) or 0) >= 2] or \
                 [k for k in ("K1", "K2", "K3") if (fit.get(k) or 0) >= 1] or list(a["lens_hits"].keys())[:1]
        items.append({
            "key": key, "id": a["id"], "name": a["name"], "name_en": p.get("name_en") or a["name"],
            "country": a["country"], "cc": a["cc"], "seller": a["seller"], "dev_type": p.get("dev_type"),
            "icon": a.get("icon"), "url": a["url"], "seller_url": a.get("seller_url"), "genre": a["genre"],
            "lenses": lenses, "lens_fit": fit, "lens_note": p.get("lens_note"), "women": p.get("women_oriented"),
            "what_it_is": p.get("what_it_is"), "sets_apart": p.get("sets_apart"), "idea_seed": p.get("idea_seed"),
            "monetization": p.get("monetization"), "traction": p.get("traction"),
            "export_potential": p.get("export_potential"), "export_reason": p.get("export_reason"),
            "build_effort": p.get("build_effort"), "ratings_local": a["ratings"], "ratings_us": a.get("us_ratings"),
            "in_us": a.get("us_available"), "dev_apps": a.get("dev_apps"),
            "released": (a["release_date"] or "")[:10], "languages": a.get("langs"),
            "confidence": p.get("confidence"), "description": (a.get("description") or "")[:600],
            "evidence": [], "source": ["store"]})

    # ista aplikacija u vise prodavnica: jedna stavka (primarna = najvise lokalnih ocena)
    grouped = {}
    for it in items:
        grouped.setdefault(str(it["id"]), []).append(it)
    items = []
    for lst in grouped.values():
        lst.sort(key=lambda x: -(x["ratings_local"] or 0))
        lst[0]["also_in"] = [x["country"] for x in lst[1:] if x["country"] != lst[0]["country"]]
        items.append(lst[0])

    by_id = {str(i["id"]): i for i in items}
    by_name = {(norm(i["name"]), i["country"]): i for i in items}
    by_name_any = {}
    for i in items:
        by_name_any.setdefault(norm(i["name"]), i)

    communities = {}
    reddit_searches = 0
    n_finds = 0
    for r in reds:
        reddit_searches += (r.get("run") or {}).get("searches_done") or 0
        for s in r.get("subreddits", []):
            nm = str(s.get("name", "")).replace("r/", "").strip()
            if nm and nm.lower() not in communities:
                communities[nm.lower()] = {"name": "r/" + nm if not nm.startswith(("http", "site:")) else nm,
                                           "region": s.get("region"), "language": s.get("language"),
                                           "role": s.get("role"), "why": s.get("why"), "size_hint": s.get("size_hint"),
                                           "evidence_url": s.get("evidence_url")}
        for f in r.get("finds", []):
            n_finds += 1
            tgt = by_id.get(str(f.get("store_id"))) if f.get("store_id") else None
            tgt = tgt or by_name_any.get(norm(f.get("app")))
            ev = f.get("evidence") or []
            if tgt:
                tgt["evidence"] += ev
                if "reddit" not in tgt["source"]:
                    tgt["source"].append("reddit")
                continue
            lenses = [k for k in (f.get("lenses") or []) if k in ("K1", "K2", "K3")]
            it = {"key": f"r:{norm(f.get('app'))}", "id": f.get("store_id"), "name": f.get("app"), "name_en": f.get("app"),
                  "country": clean_country(f.get("country")), "seller": f.get("developer"), "dev_type": f.get("dev_type"),
                  "icon": None, "url": f.get("store_url"), "lenses": lenses, "lens_fit": {k: 2 for k in lenses},
                  "women": f.get("women_oriented"), "what_it_is": f.get("what_it_is"), "sets_apart": f.get("sets_apart"),
                  "idea_seed": None, "monetization": f.get("monetization"), "traction": f.get("traction"),
                  "export_potential": None, "ratings_local": None, "ratings_us": None, "in_us": None,
                  "confidence": f.get("confidence"), "evidence": ev, "source": ["reddit"]}
            items.append(it)
            if it["id"]:
                by_id[str(it["id"])] = it
            by_name_any.setdefault(norm(it["name"]), it)

    # profili za Reddit-only nalaze (ako postoje)
    rp = {}
    for d in glob_json("reddit_profiles_*.json"):
        rp.update(d)
    for it in items:
        if it["source"] == ["reddit"] and it["key"] in rp:
            p = rp[it["key"]]
            if p.get("exclude"):
                it["_drop"] = True
                continue
            for k in ("idea_seed", "export_potential", "export_reason", "build_effort", "lens_note", "lens_fit",
                      "name_en", "dev_type", "women_oriented"):
                if p.get(k) is not None:
                    it["women" if k == "women_oriented" else k] = p[k]
            if p.get("lens_fit"):
                it["lenses"] = [k for k in ("K1", "K2", "K3") if (p["lens_fit"].get(k) or 0) >= 2] or it["lenses"]
    items = [i for i in items if not i.get("_drop")]
    for i in items:
        nm = str(i.get("name") or "")
        i["unnamed"] = bool(re.match(r"^[\[\(]", nm)) or "name not shown" in nm.lower() or "unresolved" in nm.lower()

    # ikone za Reddit nalaze koji imaju store id (sa kesom, da se ne ponavljaju pozivi)
    cache_path = DATA / "global" / "icon_cache.json"
    cache = load_json(cache_path) if cache_path.exists() else {}
    for it in items:
        if it["source"] == ["reddit"] and it.get("id") and not it.get("icon"):
            key = str(it["id"])
            if key not in cache:
                d = http_get(f"https://itunes.apple.com/lookup?id={key}&country=us", delay)
                r0 = ((d or {}).get("results") or [None])[0]
                cache[key] = {"icon": r0.get("artworkUrl100"), "ratings": r0.get("userRatingCount")} if r0 else {}
            c = cache[key]
            if c.get("icon"):
                it["icon"] = c["icon"]
                it["ratings_us"] = c.get("ratings")
                it["in_us"] = True
                it["ratings_local"] = it["ratings_local"] or c.get("ratings")
    save_json(cache_path, cache)

    pool_total = 0
    searches = 0
    for p in (DATA / "global").glob("??.json"):
        d = load_json(p)
        pool_total += len(d["apps"])
        searches += len(d["done"])
    data = {
        "date": TODAY, "generated": datetime.now().strftime("%Y-%m-%d %H:%M"), "lenses": cfg["lenses"],
        "stats": {"Storefronts scanned": len(list((DATA / "global").glob("??.json"))), "Store searches": searches,
                  "Apps seen": pool_total, "Profiled": len(profiles), "Finds kept": len(items),
                  "Reddit searches": reddit_searches, "Communities": len(communities)},
        "items": items, "communities": sorted(communities.values(), key=lambda c: (c.get("region") or "", c["name"])),
    }
    tpl = (ROOT / "scripts" / "global_template.html").read_text(encoding="utf-8")
    payload = __import__("json").dumps(data, ensure_ascii=False).replace("</", "<\\/")
    (OUTPUT / "global.html").write_text(tpl.replace("__DATA__", payload), encoding="utf-8")
    save_json(DATA / "global" / "global_items.json", items)
    print(f"global.html: {len(items)} stavki, {len(communities)} zajednica, {n_finds} Reddit nalaza")


if __name__ == "__main__":
    main()
