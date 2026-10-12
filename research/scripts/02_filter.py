"""Korak 2: automatski filteri i obogacivanje.

Za svaku aplikaciju iz pool-a:
  - nisa (zanr + iskljucene reci u nazivu), kriticna masa (ocene u US), kvalitet (prosek)
  - za one koji prodju: broj aplikacija developera, recenzije za 90 dana, oznaka pracenja (privacy label)
Izlaz: data/candidates_<datum>.json i output/kandidati_<datum>.csv
Pokretanje: python scripts/02_filter.py [--max N]
"""
import argparse
import re
from datetime import datetime, timedelta, timezone

from common import (DATA, OUTPUT, TODAY, days_since, http_get, latest, load_json, log, parse_date, save_json,
                    thresholds, write_csv)

TIKTOK_RE = re.compile(r"tik\s?tok", re.I)
FRIEND_RE = re.compile(r"\bfriends?\b.*\b(recommend|told|showed)|\brecommended\b", re.I)


def status(value, pass_min, border_min):
    if value >= pass_min:
        return "pass"
    if value >= border_min:
        return "borderline"
    return "fail"


def fetch_reviews(app_id, country, delay, window_days, logfile):
    """Najnovije recenzije iz Apple RSS-a (do 10 strana x 50) dok ne pokrijemo prozor."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    reviews = []
    for page in range(1, 5):
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
        data = http_get(url, delay, logfile=logfile)
        entries = (data or {}).get("feed", {}).get("entry", [])
        if isinstance(entries, dict):
            entries = [entries]
        if not entries:
            break
        for e in entries:
            if "im:rating" not in e:
                continue
            content = e.get("content", {})
            if isinstance(content, list):
                content = content[0] if content else {}
            reviews.append({
                "date": e.get("updated", {}).get("label"),
                "rating": int(e["im:rating"]["label"]),
                "title": e.get("title", {}).get("label", ""),
                "text": content.get("label", ""),
                "version": e.get("im:version", {}).get("label", ""),
            })
        oldest = parse_date(reviews[-1]["date"]) if reviews else None
        if oldest and oldest < cutoff:
            break
        # vrlo aktivne aplikacije: 60 dana pokrivenosti je dovoljno za poredjenje dva meseca
        if oldest and oldest < datetime.now(timezone.utc) - timedelta(days=60):
            break
    return reviews


def review_stats(reviews):
    now = datetime.now(timezone.utc)
    dated = [(parse_date(r["date"]), r) for r in reviews if parse_date(r["date"])]
    d30 = sum(1 for d, _ in dated if d >= now - timedelta(days=30))
    p30 = sum(1 for d, _ in dated if now - timedelta(days=60) <= d < now - timedelta(days=30))
    d90 = sum(1 for d, _ in dated if d >= now - timedelta(days=90))
    last = max((d for d, _ in dated), default=None)
    first = min((d for d, _ in dated), default=None)
    texts = [f"{r['title']} {r['text']}" for _, r in dated]
    return {
        "reviews_30d": d30,
        "reviews_prev_30d": p30,
        "reviews_90d": d90,
        "days_since_last_review": round(days_since(last)) if last else None,
        "reviews_mention_tiktok": sum(1 for t in texts if TIKTOK_RE.search(t)),
        "reviews_mention_friend": sum(1 for t in texts if FRIEND_RE.search(t)),
        "reviews_fetched": len(reviews),
        "reviews_coverage_days": round((now - first).days) if first else 0,
    }


def tracking_label(app_id, country, delay, logfile):
    html = http_get(f"https://apps.apple.com/{country}/app/id{app_id}", delay, as_json=False, logfile=logfile)
    if not html:
        return None
    return "Data Used to Track You" in html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=0, help="obradi najvise N aplikacija posle prvih filtera (za test)")
    args = ap.parse_args()

    cfg = thresholds()
    delay, country = cfg["requestDelaySeconds"], cfg["market"]
    logfile = DATA / "raw" / TODAY / "run_log.txt"
    pool_file = latest("pool_*.json")
    pool = load_json(pool_file)
    log(f"Filtriranje {len(pool)} aplikacija iz {pool_file.name}", logfile)

    allowed = set(cfg["allowedGenres"])
    excl = [k.lower() for k in cfg["excludeNameKeywords"]]
    cm, qu, al, sd = cfg["criticalMass"], cfg["quality"], cfg["alive"], cfg["smallDeveloper"]

    pf = cfg["prefilter"]
    from collections import Counter
    artist_counts = Counter(a["artist_id"] for a in pool)
    stage1 = []
    for a in pool:
        name = (a["name"] or "").lower()
        in_genre = a["genre"] in allowed and not any(k in name for k in excl)
        if not in_genre:
            a["niche"] = "fail"
        elif a["matched_keywords"]:
            a["niche"] = "pass"
        else:
            # samo sa top liste, bez poklapanja kljucne reci: rucna provera, osim ako nije Health & Fitness
            a["niche"] = "borderline" if a["genre"] == "Health & Fitness" else "fail"
        if a["ratings_us"] >= sd["bigBrandRatingsFlag"]:
            a["niche"] = "fail" if a["niche"] == "fail" else a["niche"]
            a["critical_mass"] = "pass"
            a["small_developer_auto"] = "fail"
            a["auto_tier"] = "out"
            continue
        a["critical_mass"] = status(a["ratings_us"], cm["minRatingsPass"], cm["minRatingsBorderline"])
        a["quality"] = status(a["avg_rating"], qu["minAvgRatingPass"], qu["minAvgRatingBorderline"])
        days = days_since(parse_date(a["release_date"]))
        a["age_days"] = round(days) if days else None
        a["ratings_per_day_since_launch"] = round(a["ratings_us"] / days, 2) if days else 0
        upd = days_since(parse_date(a["current_version_date"]))
        a["days_since_update"] = round(upd) if upd else None
        if "fail" in (a["niche"], a["critical_mass"], a["quality"]):
            continue
        # jeftini predfilteri pre skupih poziva
        if upd and upd > pf["maxDaysSinceUpdate"]:
            continue
        if a["ratings_per_day_since_launch"] < pf["minRatingsPerDay"]:
            continue
        if artist_counts[a["artist_id"]] > sd["maxAppsBorderline"]:
            continue
        stage1.append(a)
    log(f"Posle nise, kriticne mase, kvaliteta i predfiltera: {len(stage1)}", logfile)

    stage1.sort(key=lambda a: -a["ratings_per_day_since_launch"])
    if args.max:
        stage1 = stage1[: args.max]

    # nastavak: aplikacije vec obradjene u sacuvanom napretku se ne obradjuju ponovo
    prog_file = DATA / f"stage1_progress_{TODAY}.json"
    done = {p["id"]: p for p in load_json(prog_file)} if prog_file.exists() else {}
    if done:
        stage1 = [done.get(a["id"], a) for a in stage1]
        log(f"Nastavak: {sum(1 for a in stage1 if a['id'] in done)} vec obradjeno", logfile)

    dev_cache = {}
    for i, a in enumerate(stage1, 1):
        if i % 25 == 0:
            save_json(prog_file, stage1[:i - 1])
        if a["id"] in done:
            continue
        reviews = fetch_reviews(a["id"], country, delay, al["windowDays"], logfile)
        save_json(DATA / "sources" / "reviews" / f"{a['id']}.json",
                  {"app": a["name"], "fetched": TODAY, "country": country, "reviews": reviews})
        a.update(review_stats(reviews))
        last = a["days_since_last_review"]
        if a["reviews_90d"] >= al["minReviewsInWindow"] and a["reviews_30d"] >= a["reviews_prev_30d"] * 0.8:
            a["alive"] = "pass"
        elif last is not None and last <= al["maxDaysSinceLastReview"]:
            a["alive"] = "borderline"
        else:
            a["alive"] = "fail"
        a["review_growth_ratio"] = round(a["reviews_30d"] / max(1, a["reviews_prev_30d"]), 2)
        if a["alive"] == "fail":
            log(f"  [{i}/{len(stage1)}] {a['name'][:40]} | neaktivna, preskacem", logfile)
            continue

        aid = a["artist_id"]
        if aid not in dev_cache:
            data = http_get(f"https://itunes.apple.com/lookup?id={aid}&entity=software&country={country}", delay,
                            logfile=logfile)
            apps = [r for r in (data or {}).get("results", []) if r.get("wrapperType") == "software"]
            dev_cache[aid] = len(apps) if data else None
        a["developer_app_count"] = dev_cache[aid]
        n = a["developer_app_count"]
        if n is None:
            a["small_developer_auto"] = "unknown"
        elif a["ratings_us"] >= sd["bigBrandRatingsFlag"]:
            a["small_developer_auto"] = "fail"
        else:
            a["small_developer_auto"] = "pass" if n <= sd["maxAppsPass"] else (
                "borderline" if n <= sd["maxAppsBorderline"] else "fail")

        if a["small_developer_auto"] == "fail":
            continue
        a["tracking_label"] = tracking_label(a["id"], country, delay, logfile)
        log(f"  [{i}/{len(stage1)}] {a['name'][:40]} | dev apps {n} | rec 30d {a['reviews_30d']} | "
            f"tracking {a['tracking_label']}", logfile)

    auto_keys = ["niche", "critical_mass", "quality", "small_developer_auto", "alive"]
    for a in stage1:
        vals = [a.get(k) for k in auto_keys]
        borders = sum(1 for v in vals if v in ("borderline", "unknown"))
        a["auto_tier"] = "out" if "fail" in vals else ("A" if borders == 0 else ("B" if borders == 1 else "out"))

    candidates = [a for a in stage1 if a["auto_tier"] in ("A", "B")]
    candidates.sort(key=lambda a: (a["auto_tier"], -a["ratings_per_day_since_launch"]))
    save_json(DATA / f"candidates_{TODAY}.json", candidates)

    fields = ["auto_tier", "name", "seller", "genre", "release_date", "age_days", "ratings_us", "avg_rating",
              "ratings_per_day_since_launch", "reviews_30d", "reviews_prev_30d", "review_growth_ratio",
              "developer_app_count", "tracking_label", "reviews_mention_tiktok", "reviews_mention_friend",
              "matched_keywords", "keyword_groups", "chart_ranks", "url", "id"]
    rows = [{**a, "matched_keywords": ", ".join(a["matched_keywords"]),
             "keyword_groups": ", ".join(a["keyword_groups"]),
             "chart_ranks": ", ".join(f"{k} #{v}" for k, v in a["chart_ranks"].items()),
             "release_date": (a["release_date"] or "")[:10]} for a in candidates]
    write_csv(OUTPUT / f"kandidati_{TODAY}.csv", rows, fields)
    log(f"Gotovo: {len(candidates)} kandidata (A: {sum(a['auto_tier'] == 'A' for a in candidates)}, "
        f"B: {sum(a['auto_tier'] == 'B' for a in candidates)})", logfile)


if __name__ == "__main__":
    main()
