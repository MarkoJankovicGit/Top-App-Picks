"""Korak 3: spaja automatske podatke (candidates) i rucnu analizu (analysis/scores.json),
racuna ukupnu ocenu i pravi output/top-picks_<datum>.csv i output/dashboard.html.
Pokretanje: python scripts/03_build_output.py
"""
import json
from datetime import datetime

from common import DATA, OUTPUT, ROOT, TODAY, latest, load_json, thresholds, write_csv

CRITERIA = [("demand", "Demand"), ("marketabilityVirality", "Marketability and virality"),
            ("marketingGap", "Marketing gap"), ("buildEase", "Ease of build"),
            ("voiceOfCustomer", "Voice of customer"), ("monetization", "Monetization"),
            ("principleFit", "Principle and fit")]

PRINCIPLE_EN = {
    "Obaveza unapred i trenje": "Precommitment and friction", "Vidljiv napredak": "Visible progress",
    "Virtuelni ljubimac i briga": "Virtual pet and care", "Niz dana i strah od gubitka": "Streaks and loss aversion",
    "Nagrada za akciju": "Reward for action", "Odvikavanje i oporavak": "Quitting and recovery",
    "Ocena sebe i kvantifikacija": "Self-scoring and quantification",
    "Identitet i samoizražavanje": "Identity and self-expression", "Grupni izazov": "Group challenge",
    "Takmičenje i rang": "Competition and rank", "Polaganje računa": "Accountability",
    "Igrifikacija učenja": "Gamified learning", "Osvajanje i posedovanje": "Conquest and ownership",
}
CATEGORY_EN = {
    "75 Hard izazov": "75 Hard challenge", "Blokator: vežbe za skrol": "Blocker: exercise to scroll",
    "Blokator: navike za skrol": "Blocker: habits to scroll", "Blokator: trenje i prijatelji": "Blocker: friction and friends",
    "Dumbphone launcher": "Dumbphone launcher", "Alarm sa misijom": "Mission alarm",
    "Odvikavanje: pornografija": "Quitting: porn", "Odvikavanje: trava, pušenje, alkohol": "Quitting: weed, smoking, alcohol",
    "Odvikavanje: brojač dana": "Quitting: day counter", "Koraci kao igra": "Steps as a game",
    "Grupni izazov i polaganje računa": "Group challenge and accountability",
    "Trening kao igra (RPG, rang)": "Workout as a game (RPG, rank)", "Trening: plan i brojač": "Workout: plan and counter",
    "Trčanje": "Running", "Fokus tajmer": "Focus timer", "Habit tracker": "Habit tracker",
    "Dnevnik i raspoloženje": "Journal and mood", "Self-care ljubimac": "Self-care pet", "Glow-up i izgled": "Glow-up and looks",
    "Ishrana, post i voda": "Nutrition, fasting and water", "Afirmacije i samospoznaja": "Affirmations and self-discovery",
    "Zdravlje i san": "Health and sleep", "Učenje": "Learning", "Ostalo": "Other",
}


def demand_score(app, all_apps):
    """1-5 iz percentila ocena/dan medju kandidatima, korigovano rastom recenzija."""
    vals = sorted(a["ratings_per_day_since_launch"] for a in all_apps)
    pct = sum(1 for v in vals if v <= app["ratings_per_day_since_launch"]) / max(1, len(vals))
    score = 1 + 4 * pct
    g = app.get("review_growth_ratio")
    if g is not None:
        score += 0.5 if g >= 1.3 else (-0.5 if g < 0.7 else 0)
    return round(min(5, max(1, score)), 1)


def stage1_breakdown(pool, cfg):
    """Koliko je aplikacija ispalo na kom automatskom filteru (redosled kao u 02_filter.py)."""
    from collections import Counter
    from common import days_since, parse_date
    allowed, excl = set(cfg["allowedGenres"]), [k.lower() for k in cfg["excludeNameKeywords"]]
    cm, qu, pf, sd = cfg["criticalMass"], cfg["quality"], cfg["prefilter"], cfg["smallDeveloper"]
    artist = Counter(a["artist_id"] for a in pool)
    c = Counter()
    for a in pool:
        name = (a["name"] or "").lower()
        age = days_since(parse_date(a["release_date"])) or 1
        upd = days_since(parse_date(a["current_version_date"])) or 0
        if a["genre"] not in allowed or any(k in name for k in excl):
            c["genre"] += 1
        elif not a["matched_keywords"] and a["genre"] != "Health & Fitness":
            c["chart_only"] += 1
        elif a["ratings_us"] >= sd["bigBrandRatingsFlag"]:
            c["big_brand"] += 1
        elif a["ratings_us"] < cm["minRatingsBorderline"]:
            c["few_ratings"] += 1
        elif a["avg_rating"] < qu["minAvgRatingBorderline"]:
            c["low_rating"] += 1
        elif upd > pf["maxDaysSinceUpdate"]:
            c["stale"] += 1
        elif a["ratings_us"] / age < pf["minRatingsPerDay"]:
            c["slow"] += 1
        elif artist[a["artist_id"]] > sd["maxAppsBorderline"]:
            c["factory"] += 1
        else:
            c["kept"] += 1
    return dict(c)


def main():
    cfg = thresholds()
    weights = cfg["weights"]
    if list(DATA.glob("candidates_*.json")):
        cands = load_json(latest("candidates_*.json"))
    else:  # sken jos traje: koristi poslednji sacuvan napredak
        cands = [a for a in load_json(latest("stage1_progress_*.json"))
                 if a.get("alive") in ("pass", "borderline") and a.get("small_developer_auto") != "fail"]
    analysis_path = ROOT / "analysis" / "scores.json"
    analysis = load_json(analysis_path) if analysis_path.exists() else {}

    def opt(prefix):
        merged = {}
        for p in sorted((ROOT / "analysis").glob(f"{prefix}*.json")):
            merged.update(load_json(p))
        return merged

    marketing, reddit = opt("marketing"), opt("reddit")
    categories, icons = opt("categories"), opt("icons")

    for a in cands:
        # malo pokrivenosti recenzijama (vrlo aktivne aplikacije): poredjenje dva meseca nije pouzdano
        if a.get("reviews_coverage_days", 99) < 55:
            a["review_growth_ratio"] = None
    rows = []
    for a in cands:
        an = dict(analysis.get(str(a["id"]), {}))
        if not an or an.get("exclude"):
            continue
        sc = dict(an.get("scores", {}))
        mk = marketing.get(str(a["id"]))
        if mk:
            lvl = mk["level"]
            ev = mk.get("evidence") or ""
            prelim = (an.get("scores") or {}).get("marketingGap", 5)
            if lvl == 0 and prelim <= 2:
                lvl = 1
                ev += " Meta Ad Library je prazan, ali recenzije ukazuju na plaćeni marketing (npr. TikTok ili Instagram reklame)."
            elif lvl == 0 and a.get("tracking_label"):
                lvl = 1
                ev += " Aplikacija ima oznaku praćenja, pa su moguće reklame van Meta ili preko persona stranica (nepotvrđeno)."
            an["marketing_level"] = lvl
            an["marketing_evidence"] = ev
            sc["marketingGap"] = {0: 5, 1: 4, 2: 2, 3: 1}[lvl]
            if lvl >= 3:
                continue
            if lvl == 2:
                an["list"] = "B"
            an.setdefault("sources", []).append(
                {"label": "Meta Ad Library (US)", "url": mk.get("url"), "date": mk.get("date")})
        rd = reddit.get(str(a["id"]))
        if rd and rd.get("status") == "not_checked":
            rd = None
        if rd and rd.get("ugc_hiring"):
            # dokaz placenog influencer marketinga: marketing najmanje nivo 2
            lvl = max(an.get("marketing_level") or 0, 2)
            an["marketing_level"] = lvl
            an["marketing_evidence"] = (an.get("marketing_evidence") or "") + " Na Redditu traže plaćene UGC kreatore."
            sc["marketingGap"] = min(sc.get("marketingGap", 5), {0: 5, 1: 4, 2: 2, 3: 1}[lvl])
            an["list"] = "B"
            if lvl >= 3:
                continue
        if rd:
            an["subreddits"] = rd.get("subreddits", [])
            an["reddit_notes"] = rd.get("notes")
            for t in rd.get("threads", [])[:3]:
                an.setdefault("sources", []).append(
                    {"label": f"Reddit r/{t.get('subreddit')}: {t.get('title', '')[:60]}", "url": t.get("url"),
                     "date": rd.get("date")})
            if rd.get("suggestions"):
                an["suggestions"] = list(dict.fromkeys(an.get("suggestions", []) + rd["suggestions"]))
        sc["demand"] = demand_score(a, cands)
        an["category"] = categories.get(str(a["id"]), "Ostalo")
        an["icon"] = icons.get(str(a["id"]))
        total = round(sum(weights[k] * (sc.get(k, 0) / 5) for k, _ in CRITERIA))
        rows.append({**a, **an, "scores": sc, "total": total})

    english = opt("en_[0-9]")
    for r in rows:
        r.update(english.get(str(r["id"]), {}))
        r["principle"] = PRINCIPLE_EN.get(r.get("principle"), r.get("principle"))
        r["category"] = CATEGORY_EN.get(r.get("category"), r.get("category"))
    rows.sort(key=lambda r: (-r["total"], r.get("list", "B")))
    all_passed = len(rows)
    rows = rows[:100]
    for i, r in enumerate(rows, 1):
        r["rank"] = i

    pool = load_json(latest("pool_*.json"))
    pool_n = len(pool)
    cand_ids = {str(a["id"]) for a in cands}
    excluded_analysis = sum(1 for k, v in analysis.items() if k in cand_ids and v.get("exclude"))
    kept_analysis = sum(1 for k, v in analysis.items() if k in cand_ids and not v.get("exclude"))
    method = {"stage1": stage1_breakdown(pool, cfg), "excluded_analysis": excluded_analysis,
              "kept_analysis": kept_analysis, "keywords": sum(len(v) for v in load_json(ROOT / "config" / "keywords.json")["groups"].values()),
              "thresholds": {"min_ratings": cfg["criticalMass"]["minRatingsBorderline"],
                             "min_avg": cfg["quality"]["minAvgRatingBorderline"],
                             "max_days_since_update": cfg["prefilter"]["maxDaysSinceUpdate"],
                             "min_ratings_per_day": cfg["prefilter"]["minRatingsPerDay"],
                             "max_dev_apps": cfg["smallDeveloper"]["maxAppsBorderline"],
                             "big_brand": cfg["smallDeveloper"]["bigBrandRatingsFlag"],
                             "window_days": cfg["alive"]["windowDays"],
                             "min_reviews_window": cfg["alive"]["minReviewsInWindow"],
                             "build_months": cfg["build"]["maxMonths"], "team": cfg["build"]["teamSize"]}}
    funnel = {"pool": pool_n, "auto": len(cands), "analyzed": sum(1 for a in cands if str(a["id"]) in analysis),
              "top": len(rows), "passed": all_passed, "A": sum(r.get("list") == "A" for r in rows),
              "B": sum(r.get("list") == "B" for r in rows)}

    csv_rows = [{
        "rank": r["rank"], "list": r.get("list"), "app": r["name"], "developer": r["seller"],
        "developer_type": r.get("developer_type"), "category": r.get("category"), "principle": r.get("principle"),
        "what_sets_it_apart": r.get("differentiator"), "us_ratings": r["ratings_us"], "avg_rating": r["avg_rating"],
        "ratings_per_day": r["ratings_per_day_since_launch"], "review_growth_30d": r.get("review_growth_ratio"),
        "marketing_level": r.get("marketing_level"), "build_weeks": r.get("build_weeks"),
        "marketability_of_4": r.get("marketability_score"), "monetization": r.get("monetization"),
        "opportunity": r.get("opportunity"), "subreddits": ", ".join(r.get("subreddits", [])),
        "total_score": r["total"], "confidence": r.get("confidence"), "app_store": r["url"],
        "released": (r["release_date"] or "")[:10], "checked": r.get("checked", TODAY)} for r in rows]
    write_csv(OUTPUT / f"top-picks_{TODAY}.csv", csv_rows, list(csv_rows[0].keys()) if csv_rows else ["rang"])

    template = (ROOT / "scripts" / "dashboard_template.html").read_text(encoding="utf-8")
    payload = json.dumps({"rows": rows, "funnel": funnel, "date": TODAY,
                          "criteria": CRITERIA, "weights": weights, "method": method,
                          "generated": datetime.now().strftime("%Y-%m-%d %H:%M")}, ensure_ascii=False)
    payload = payload.replace("</", "<\\/")
    page = template.replace("__DATA__", payload)
    (OUTPUT / "dashboard.html").write_text(page, encoding="utf-8")
    (OUTPUT / "index.html").write_text(page, encoding="utf-8")  # Vercel i staticki hosting otvaraju index.html
    print(f"Top pikova: {len(rows)} (A {funnel['A']}, B {funnel['B']}) -> output/dashboard.html")


if __name__ == "__main__":
    main()
