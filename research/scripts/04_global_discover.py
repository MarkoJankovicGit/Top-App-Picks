"""Globalni sken: Apple Search API po prodavnicama (zemljama), lokalne ključne reči, tri koncepta.

Izlaz: data/global/<cc>.json  {"cc", "done": [...], "apps": {id: {...}}}
Pokretanje: python scripts/04_global_discover.py [--only in,cn] [--limit N]
Nastavlja gde je stao (preskače već obrađene upite).
"""
import argparse

from common import CONFIG, DATA, http_get, load_json, log, q, save_json, thresholds

OUT = DATA / "global"
ORDER = ["in", "cn", "ru", "kr", "jp", "tr", "sa", "eg", "ae", "br", "mx", "id", "vn", "th", "pl", "ua", "il",
         "ph", "ng", "za", "pk"]


def slim(r):
    return {
        "id": r.get("trackId"), "name": r.get("trackName"), "seller": r.get("sellerName"),
        "artist_id": r.get("artistId"), "genre": r.get("primaryGenreName"),
        "release_date": r.get("releaseDate"), "updated": r.get("currentVersionReleaseDate"),
        "price": r.get("price"), "ratings": r.get("userRatingCount", 0) or 0,
        "avg_rating": round(r.get("averageUserRating", 0) or 0, 2),
        "langs": r.get("languageCodesISO2A") or [], "seller_url": r.get("sellerUrl"),
        "url": (r.get("trackViewUrl") or "").split("?")[0], "age_rating": r.get("contentAdvisoryRating"),
        "bundle": r.get("bundleId"), "description": (r.get("description") or "")[:700], "hits": [],
    }


def queries_for(cfg, cc):
    sf = cfg["storefronts"][cc]
    out = []
    for lens in ("K1", "K2", "K3"):
        base = cfg["english_base"][lens][: sf["use_english"]]
        for kw in base + sf["local"].get(lens, []):
            out.append((lens, kw))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="lista zemalja odvojena zarezom")
    ap.add_argument("--limit", type=int, default=0, help="najviše N upita po zemlji (test)")
    args = ap.parse_args()

    cfg = load_json(CONFIG / "global_keywords.json")
    delay = thresholds()["requestDelaySeconds"]
    OUT.mkdir(parents=True, exist_ok=True)
    logfile = OUT / "run_log.txt"
    countries = [c for c in ORDER if c in cfg["storefronts"]]
    if args.only:
        countries = [c for c in args.only.split(",") if c in cfg["storefronts"]]

    for cc in countries:
        path = OUT / f"{cc}.json"
        pool = load_json(path) if path.exists() else {"cc": cc, "done": [], "apps": {}}
        todo = [(l, k) for l, k in queries_for(cfg, cc) if f"{l}|{k}" not in pool["done"]]
        if args.limit:
            todo = todo[: args.limit]
        log(f"[{cc}] {cfg['storefronts'][cc]['name']}: {len(todo)} upita", logfile)
        for i, (lens, kw) in enumerate(todo, 1):
            url = f"https://itunes.apple.com/search?term={q(kw)}&country={cc}&entity=software&limit=200"
            data = http_get(url, delay, logfile=logfile)
            if data is None:
                continue
            for r in data.get("results", []):
                aid = str(r.get("trackId"))
                app = pool["apps"].get(aid) or slim(r)
                app["hits"].append([lens, kw])
                pool["apps"][aid] = app
            pool["done"].append(f"{lens}|{kw}")
            if i % 8 == 0:
                save_json(path, pool)
                log(f"[{cc}] {i}/{len(todo)} upita, {len(pool['apps'])} aplikacija", logfile)
        save_json(path, pool)
        log(f"[{cc}] gotovo: {len(pool['apps'])} aplikacija", logfile)
    log("SVE GOTOVO", logfile)


if __name__ == "__main__":
    main()
