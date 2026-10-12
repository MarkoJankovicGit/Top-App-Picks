"""Korak 1: otkrivanje. Apple pretraga po kljucnim recima niše + US top liste po kategorijama.

Izlaz: data/pool_<datum>.json (sve pronadjene aplikacije) i sirovi odgovori u data/raw/<datum>/.
Pokretanje: python scripts/01_discover.py [--limit-keywords N]
"""
import argparse

from common import (CONFIG, DATA, TODAY, http_get, load_json, log, normalize_app, q, save_json, slug,
                    thresholds)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-keywords", type=int, default=0, help="samo prvih N kljucnih reci (za test)")
    args = ap.parse_args()

    cfg = thresholds()
    delay = cfg["requestDelaySeconds"]
    country = cfg["market"]
    raw_dir = DATA / "raw" / TODAY
    logfile = raw_dir / "run_log.txt"
    raw_dir.mkdir(parents=True, exist_ok=True)

    kw_cfg = load_json(CONFIG / "keywords.json")["groups"]
    keywords = [(g, k) for g, ks in kw_cfg.items() for k in ks]
    if args.limit_keywords:
        keywords = keywords[: args.limit_keywords]

    pool = {}

    log(f"Pretraga: {len(keywords)} kljucnih reci, trziste {country}", logfile)
    for i, (group, kw) in enumerate(keywords, 1):
        url = f"https://itunes.apple.com/search?term={q(kw)}&country={country}&entity=software&limit=200"
        data = http_get(url, delay, logfile=logfile)
        if not data:
            continue
        save_json(raw_dir / "search" / f"{slug(kw)}.json", data)
        for r in data.get("results", []):
            app = pool.get(r.get("trackId")) or normalize_app(r)
            if kw not in app["matched_keywords"]:
                app["matched_keywords"].append(kw)
            if group not in app["keyword_groups"]:
                app["keyword_groups"].append(group)
            pool[app["id"]] = app
        log(f"  [{i}/{len(keywords)}] '{kw}': {data.get('resultCount', 0)} rezultata, ukupno {len(pool)}", logfile)

    cats = load_json(CONFIG / "categories.json")
    missing = set()
    for chart in cats["charts"]:
        for gid, gname in cats["genres"].items():
            url = f"https://itunes.apple.com/{country}/rss/{chart}/limit=100/genre={gid}/json"
            data = http_get(url, delay, logfile=logfile)
            if not data:
                continue
            save_json(raw_dir / "charts" / f"{chart}_{gid}.json", data)
            entries = data.get("feed", {}).get("entry", [])
            if isinstance(entries, dict):
                entries = [entries]
            for rank, e in enumerate(entries, 1):
                app_id = int(e["id"]["attributes"]["im:id"])
                key = f"{chart}:{gname}"
                if app_id in pool:
                    pool[app_id]["chart_ranks"][key] = rank
                else:
                    missing.add((app_id, key, rank))
            log(f"  Lista {chart} / {gname}: {len(entries)} aplikacija", logfile)

    # Aplikacije sa top lista koje pretraga nije nasla: dopuni preko lookup-a
    missing_ids = sorted({m[0] for m in missing})
    for start in range(0, len(missing_ids), 100):
        batch = missing_ids[start:start + 100]
        url = f"https://itunes.apple.com/lookup?id={','.join(map(str, batch))}&country={country}&entity=software"
        data = http_get(url, delay, logfile=logfile)
        for r in (data or {}).get("results", []):
            if r.get("wrapperType") == "software":
                pool[r["trackId"]] = normalize_app(r)
    for app_id, key, rank in missing:
        if app_id in pool:
            pool[app_id]["chart_ranks"][key] = rank

    out = DATA / f"pool_{TODAY}.json"
    save_json(out, sorted(pool.values(), key=lambda a: -a["ratings_us"]))
    log(f"Gotovo: {len(pool)} aplikacija u {out.name}", logfile)


if __name__ == "__main__":
    main()
