"""Zajednicke funkcije za research skripte. Samo Python standardna biblioteka."""
import csv
import http.client
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
TODAY = datetime.now().strftime("%Y-%m-%d")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"

_last_call = {}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def thresholds():
    return load_json(CONFIG / "thresholds.json")


def log(msg, logfile=None):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8"),
          flush=True)
    if logfile:
        with open(logfile, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def http_get(url, delay, as_json=True, retries=3, logfile=None):
    """GET sa pauzom izmedju poziva (Apple limit ~20/min) i ponovnim pokusajem na 403/429/5xx."""
    host = urllib.parse.urlparse(url).netloc
    for attempt in range(retries + 1):
        wait = delay - (time.time() - _last_call.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        _last_call[host] = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US"})
        try:
            with urllib.request.urlopen(req, timeout=40) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                return json.loads(body) if as_json else body
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (403, 429) or e.code >= 500:
                backoff = 30 * (attempt + 1)
                log(f"HTTP {e.code}, pauza {backoff}s: {url}", logfile)
                time.sleep(backoff)
                continue
            log(f"HTTP {e.code}: {url}", logfile)
            return None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError, http.client.HTTPException) as e:
            log(f"Greska ({type(e).__name__}), pokusaj {attempt + 1}: {url}", logfile)
            time.sleep(10)
    log(f"Odustajem posle {retries + 1} pokusaja: {url}", logfile)
    return None


def parse_date(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def days_since(dt):
    if not dt:
        return None
    return max(1.0, (datetime.now(timezone.utc) - dt).total_seconds() / 86400)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def normalize_app(r):
    """Iz Apple Search/Lookup rezultata pravi zapis sa poljima koja koristimo."""
    return {
        "id": r.get("trackId"),
        "name": r.get("trackName"),
        "seller": r.get("sellerName"),
        "artist_id": r.get("artistId"),
        "artist_name": r.get("artistName"),
        "genre": r.get("primaryGenreName"),
        "genres": r.get("genres", []),
        "release_date": r.get("releaseDate"),
        "current_version_date": r.get("currentVersionReleaseDate"),
        "price": r.get("price"),
        "ratings_us": r.get("userRatingCount", 0) or 0,
        "avg_rating": round(r.get("averageUserRating", 0) or 0, 2),
        "content_rating": r.get("contentAdvisoryRating"),
        "url": r.get("trackViewUrl", "").split("?")[0],
        "seller_url": r.get("sellerUrl"),
        "bundle_id": r.get("bundleId"),
        "description": (r.get("description") or "")[:2000],
        "matched_keywords": [],
        "keyword_groups": [],
        "chart_ranks": {},
    }


def latest(pattern):
    files = sorted(DATA.glob(pattern))
    if not files:
        sys.exit(f"Nema fajla za obrazac {pattern}. Prvo pokreni prethodni korak.")
    return files[-1]


def write_csv(path, rows, fields):
    """CSV za Excel u srpskoj lokalizaciji: separator ';', UTF-8 sa BOM."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: (str(v).replace(".", ",") if isinstance(v, float) else v) for k, v in row.items()})


def q(s):
    return urllib.parse.quote(s)
