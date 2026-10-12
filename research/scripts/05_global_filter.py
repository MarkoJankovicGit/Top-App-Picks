"""Globalni filter: spaja bazene po prodavnicama, filtrira, proverava prisutnost u US, developera i rangira.

Koraci:
 1. osnovni filter (žanr, ocene u zemlji, prosek, ažuriranje) + broj aplikacija developera u bazenu
 2. pre-skor, top N po prodavnici -> batch lookup u US prodavnici (da li je poznata u SAD)
 3. skor (relevantnost, trakcija, neizvezenost, mali developer), kvote po konceptu i prodavnici
 4. lookup developera (broj aplikacija) samo za finalne kandidate
Izlaz: data/global/candidates.json, output/global_candidates.csv, analysis/global_batches/gbatch_NNN.json
Pokretanje: python scripts/05_global_filter.py [--only in,cn] [--top 70] [--per-lens 6] [--batch 20]
"""
import argparse
import math
from collections import Counter

from common import (DATA, OUTPUT, ROOT, days_since, http_get, load_json, log, parse_date, save_json, thresholds,
                    write_csv)

GENRE_SKIP = {"Games", "Finance", "Shopping", "Travel", "Navigation", "Food & Drink", "Business", "Medical",
              "Weather", "Sports", "Photo & Video", "Developer Tools", "Graphics & Design", "Catalogs", "Stickers",
              "Magazines & Newspapers"}
MIN_RATINGS = 50
MAX_RATINGS = 150000
MIN_AVG = 3.8
MAX_UPDATE_DAYS = 450
MAX_DEV_APPS_POOL = 12
MAX_DEV_APPS = 10


def trac(r):
    return min(1.0, math.log10(max(r, 1)) / 5)


def unexported(local, us):
    if us is None:
        return 1.0
    if us < 0.05 * local:
        return 0.9
    if us < 0.25 * local:
        return 0.6
    if us < local:
        return 0.3
    return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--top", type=int, default=300, help="koliko po prodavnici ide na US proveru")
    ap.add_argument("--per-lens", type=int, default=8, help="kvota po konceptu i prodavnici")
    ap.add_argument("--batch", type=int, default=20)
    args = ap.parse_args()

    cfg = load_json(ROOT / "config" / "global_keywords.json")
    delay = thresholds()["requestDelaySeconds"]
    logfile = DATA / "global" / "run_log.txt"
    only = set(args.only.split(",")) if args.only else None

    # 1. osnovni filter
    cands = []
    leaders = []
    for p in sorted((DATA / "global").glob("??.json")):
        cc = p.stem
        if only and cc not in only:
            continue
        pool = load_json(p)
        devs = Counter(a["artist_id"] for a in pool["apps"].values())
        for a in pool["apps"].values():
            if a["genre"] in GENRE_SKIP or a["avg_rating"] < MIN_AVG or a["ratings"] < MIN_RATINGS:
                continue
            upd = days_since(parse_date(a["updated"]))
            if upd is None or upd > MAX_UPDATE_DAYS:
                continue
            if a["ratings"] > MAX_RATINGS:
                leaders.append({"cc": cc, "id": a["id"], "name": a["name"], "seller": a["seller"],
                                "ratings": a["ratings"], "hits": len(a["hits"]), "url": a["url"]})
                continue
            if devs[a["artist_id"]] > MAX_DEV_APPS_POOL:
                continue
            lens = Counter(h[0] for h in a["hits"])
            a = dict(a, cc=cc, country=cfg["storefronts"][cc]["name"], lens_hits=dict(lens),
                     dev_pool=devs[a["artist_id"]], age_days=round(days_since(parse_date(a["release_date"])) or 0),
                     update_days=round(upd))
            a["pre"] = 0.45 * min(1.0, len(a["hits"]) / 6) + 0.35 * trac(a["ratings"]) + \
                0.20 * (1.0 if a["dev_pool"] == 1 else 0.6 if a["dev_pool"] <= 3 else 0.3)
            cands.append(a)
    log(f"Osnovni filter: {len(cands)} kandidata, {len(leaders)} lidera (preko {MAX_RATINGS} ocena)", logfile)

    # 2. top N po prodavnici -> US provera
    by_cc = {}
    for a in cands:
        by_cc.setdefault(a["cc"], []).append(a)
    shortlist = []
    for cc, lst in by_cc.items():
        lst.sort(key=lambda a: -a["pre"])
        shortlist += lst[: args.top]
    ids = [str(a["id"]) for a in shortlist]
    us = {}
    for i in range(0, len(ids), 100):
        data = http_get(f"https://itunes.apple.com/lookup?id={','.join(ids[i:i + 100])}&country=us", delay,
                        logfile=logfile)
        for r in (data or {}).get("results", []):
            us[str(r.get("trackId"))] = r.get("userRatingCount", 0) or 0
    log(f"US provera: {len(us)} od {len(ids)} dostupno u SAD", logfile)
    for a in shortlist:
        a["us_ratings"] = us.get(str(a["id"]))
        a["us_available"] = str(a["id"]) in us
        a["unexported"] = unexported(a["ratings"], a["us_ratings"])
        a["score"] = round(0.30 * min(1.0, len(a["hits"]) / 6) + 0.25 * trac(a["ratings"]) + 0.25 * a["unexported"] +
                           0.20 * (1.0 if a["dev_pool"] == 1 else 0.6 if a["dev_pool"] <= 3 else 0.3), 3)

    # globalne aplikacije (poznatije u SAD nego lokalno) ispadaju: trazimo lokalne hitove
    before = len(shortlist)
    shortlist = [a for a in shortlist if a["unexported"] >= 0.3]
    log(f"Neizvezeno (US ocene manje od lokalnih): {len(shortlist)} od {before}", logfile)

    # 3. kvote po konceptu i prodavnici
    pick = {}
    for cc in by_cc:
        pool = [a for a in shortlist if a["cc"] == cc]
        for lens in ("K1", "K2", "K3"):
            lst = sorted([a for a in pool if a["lens_hits"].get(lens)],
                         key=lambda a: (-a["lens_hits"][lens], -a["score"]))
            lst = sorted(lst[: args.per_lens * 3], key=lambda a: -a["score"])[: args.per_lens]
            for a in lst:
                pick[(cc, a["id"])] = a
    final = list(pick.values())
    log(f"Kvote: {len(final)} kandidata za proveru developera", logfile)

    # 4. developer
    for i, a in enumerate(final, 1):
        d = http_get(f"https://itunes.apple.com/lookup?id={a['artist_id']}&entity=software&country={a['cc']}", delay,
                     logfile=logfile)
        apps = [r for r in (d or {}).get("results", []) if r.get("wrapperType") == "software"]
        a["dev_apps"] = len(apps) if d else None
        a["icon"] = next((r.get("artworkUrl100") for r in apps if r.get("trackId") == a["id"]), None)
        if i % 40 == 0:
            log(f"developer {i}/{len(final)}", logfile)
    final = [a for a in final if a["dev_apps"] is None or a["dev_apps"] <= MAX_DEV_APPS]
    final.sort(key=lambda a: -a["score"])
    save_json(DATA / "global" / "candidates.json", final)
    save_json(DATA / "global" / "leaders.json", sorted(leaders, key=lambda x: -x["ratings"])[:300])

    rows = [{"country": a["country"], "name": a["name"], "seller": a["seller"],
             "lenses": "".join(f"{k}:{v} " for k, v in a["lens_hits"].items()), "ratings_local": a["ratings"],
             "ratings_us": a["us_ratings"] if a["us_available"] else "not in US", "dev_apps": a["dev_apps"],
             "released": (a["release_date"] or "")[:10], "updated": (a["updated"] or "")[:10], "score": a["score"],
             "url": a["url"]} for a in final]
    write_csv(OUTPUT / "global_candidates.csv", rows, list(rows[0].keys()) if rows else ["name"])

    # 5. paketi za analizu
    bdir = ROOT / "analysis" / "global_batches"
    bdir.mkdir(parents=True, exist_ok=True)
    for f in bdir.glob("gbatch_*.json"):
        f.unlink()
    for n, i in enumerate(range(0, len(final), args.batch), 1):
        save_json(bdir / f"gbatch_{n:03d}.json", [{
            "key": f"{a['cc']}:{a['id']}", "country": a["country"], "name": a["name"], "seller": a["seller"],
            "genre": a["genre"], "released": (a["release_date"] or "")[:10], "updated": (a["updated"] or "")[:10],
            "ratings_local": a["ratings"], "avg_rating": a["avg_rating"], "ratings_us": a["us_ratings"],
            "in_us": a["us_available"], "dev_apps": a["dev_apps"], "languages": a["langs"], "price": a["price"],
            "lens_hits": a["lens_hits"], "matched_keywords": [h[1] for h in a["hits"]][:8],
            "url": a["url"], "seller_url": a["seller_url"], "description": a["description"], "icon": a.get("icon")}
            for a in final[i:i + args.batch]])
    log(f"Gotovo: {len(final)} kandidata, {len(list(bdir.glob('gbatch_*.json')))} paketa", logfile)


if __name__ == "__main__":
    main()
