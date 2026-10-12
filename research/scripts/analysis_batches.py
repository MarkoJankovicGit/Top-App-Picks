"""Pomocni alat za rucnu analizu.

prepare: iz najnovijeg stage1_progress/candidates pravi pakete za analizu (opis + uzorak recenzija)
         za aplikacije koje su prosle automatske filtere, a jos nisu analizirane.
merge:   spaja analysis/batches/result_*.json u analysis/scores.json.

python scripts/analysis_batches.py prepare --size 15
python scripts/analysis_batches.py merge
"""
import argparse
import json
from pathlib import Path

from common import DATA, ROOT, load_json, save_json

BATCH_DIR = ROOT / "analysis" / "batches"
SCORES = ROOT / "analysis" / "scores.json"


def source_apps():
    cands = sorted(DATA.glob("candidates_*.json"))
    if cands:
        return load_json(cands[-1])
    prog = sorted(DATA.glob("stage1_progress_*.json"))
    apps = load_json(prog[-1]) if prog else []
    return [a for a in apps if a.get("alive") in ("pass", "borderline")
            and a.get("small_developer_auto") in ("pass", "borderline", "unknown")]


def review_sample(app_id, n=40):
    p = DATA / "sources" / "reviews" / f"{app_id}.json"
    if not p.exists():
        return []
    revs = load_json(p)["reviews"]
    low = [r for r in revs if r["rating"] <= 3][: n // 2]
    high = [r for r in revs if r["rating"] >= 4][: n - len(low)]
    return [{"date": r["date"][:10], "rating": r["rating"], "text": (r["title"] + ". " + r["text"])[:400]}
            for r in low + high]


def prepare(size):
    scores = load_json(SCORES) if SCORES.exists() else {}
    done = set(scores)
    for f in BATCH_DIR.glob("batch_*.json"):
        done |= {str(a["id"]) for a in load_json(f)}
    todo = [a for a in source_apps() if str(a["id"]) not in done]
    existing = len(list(BATCH_DIR.glob("batch_*.json")))
    made = []
    for i in range(0, len(todo), size):
        chunk = todo[i:i + size]
        packet = [{
            "id": a["id"], "name": a["name"], "seller": a["seller"], "genre": a["genre"],
            "release_date": (a["release_date"] or "")[:10], "ratings_us": a["ratings_us"],
            "avg_rating": a["avg_rating"], "ratings_per_day": a["ratings_per_day_since_launch"],
            "reviews_30d": a.get("reviews_30d"), "reviews_prev_30d": a.get("reviews_prev_30d"),
            "developer_app_count": a.get("developer_app_count"), "tracking_label": a.get("tracking_label"),
            "price": a.get("price"), "url": a["url"], "matched_keywords": a["matched_keywords"],
            "description": a["description"][:1500], "reviews": review_sample(a["id"]),
        } for a in chunk]
        n = existing + len(made) + 1
        save_json(BATCH_DIR / f"batch_{n:03d}.json", packet)
        made.append(n)
    print(f"Novih paketa: {len(made)} ({len(todo)} aplikacija): {made}")


def merge():
    scores = load_json(SCORES) if SCORES.exists() else {}
    for f in sorted(BATCH_DIR.glob("result_*.json")):
        for app_id, an in load_json(f).items():
            prev = scores.get(app_id, {})
            scores[app_id] = {**an, **{k: v for k, v in prev.items() if k.startswith("manual_")}} | \
                {k: prev[k] for k in ("marketing_level", "marketing_evidence", "subreddits", "reddit_threads")
                 if k in prev and prev[k] not in (None, [], "")}
    save_json(SCORES, scores)
    print(f"scores.json: {len(scores)} aplikacija")


def checklist():
    """Spisak aplikacija koje su prosle analizu, a nisu prosle proveru marketinga."""
    scores = load_json(SCORES)
    done = set()
    for f in (ROOT / "analysis").glob("marketing_*.json"):
        done |= set(load_json(f))
    for f in (ROOT / "analysis").glob("check_*.json"):
        done |= {str(a["id"]) for a in load_json(f)}
    todo = [{"id": k, "name": v["name"]} for k, v in scores.items() if not v.get("exclude") and k not in done]
    n = len(list((ROOT / "analysis").glob("check_*.json"))) + 1
    if todo:
        save_json(ROOT / "analysis" / f"check_{n:03d}.json", todo)
    print(f"check_{n:03d}.json: {len(todo)} aplikacija")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prepare", "merge", "checklist"])
    ap.add_argument("--size", type=int, default=15)
    args = ap.parse_args()
    {"prepare": lambda: prepare(args.size), "merge": merge, "checklist": checklist}[args.cmd]()
