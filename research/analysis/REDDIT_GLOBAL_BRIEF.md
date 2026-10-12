# Global Reddit scan via Google (Chrome): small-developer apps outside the US

## Project context
We look for ideas for a consumer app for US Gen Z women (self-improvement, subscription). The team has a go-to-market crew (organic micro/nano influencers) and a 6-month validation budget. Three concepts (lenses) frame the search:

- **K1 – Gentle self-improvement for women:** habits, rituals, routines, mood/journal, identity, cute pets/companions, cycle-aware wellness, "that girl"/soft-discipline, accountability with friends.
- **K2 – Micro-learning:** the user supplies their own material (PDF, notes, links, lectures) and the app turns it into short reel-style videos, cards, quizzes; any "learn in minutes" mechanics.
- **K3 – Audio on the go:** the user picks a topic or goal and gets personalised audio (podcast/mp3, TTS, summaries, guided walks) for walking, commuting, driving; habit- and interest-aware.

We want apps made by **small developers/teams** (solo, 2–10 people) that have **some relation** to these lenses (loose relation is fine) and that are **popular or praised locally but not global/viral**, discussed or announced by their makers on Reddit. We also want the **regional communities** themselves (subreddits) where makers and users talk about apps, so we can keep them as sources.

## Access rules (important)
- reddit.com cannot be opened by our tools (blocked). We read Reddit **only through Google results in Chrome**: `https://www.google.com/search?q=<query>` then `get_page_text`. Results show title, subreddit, comment count, age and a snippet. Do not try to open reddit.com, mirrors, archives or proxies.
- For links use `javascript_tool` on the results page: `Array.from(document.querySelectorAll('a h3')).map(h=>({t:h.innerText,u:h.closest('a').href}))`.
- Create your own tab with `tabs_create_mcp` (call `tabs_context_mcp` first), work only in it, close it at the end.
- **Pace: at least 20 seconds between Google searches.** Maximum **32 searches** per run. If Google shows a CAPTCHA, "unusual traffic" or a /sorry/ page: **stop immediately**, do NOT try to solve it, save what you have and report it.
- Read only. No logins, no posting, no accounts.
- Use quotes and OR; `site:reddit.com/r/NAME` for a subreddit. Non-Reddit community sites listed in your query plan are allowed through the same Google flow.
- To identify an app a thread mentions, use the App Store Search API from Bash (`curl "https://itunes.apple.com/search?term=<name>&country=<cc>&entity=software&limit=5"`, try `us` and the local country code, at least 3 seconds between calls). Record trackId, store URL, seller, ratings count, release date. If it is Android-only or cannot be found, say so.

## What to extract
For every app that fits (small developer + some relation to a lens + talked about on Reddit/community by maker or users): 
- name, store URL/trackId if found, developer name, developer type (solo/small team/company/unknown), country/language of the audience
- which lens(es): K1/K2/K3 (can be several)
- what it is in one sentence; **what sets it apart** (the mechanic/twist); monetization if stated
- traction signals as stated (users, ratings, MRR, downloads, "#1 in X", comments count)
- women-oriented? (true/false/unknown) and evidence
- evidence: thread title, subreddit, age, comments, URL (from Google results)
- confidence: low/medium/high (is the maker really small? is the claim verifiable?)

Also record **every regional subreddit or community** you see that is relevant (name, region, language, role: builders / users / both, why relevant, size hint if shown such as "1.2k followers").

Skip: big companies, famous global apps, pure promotion with no substance, spam.

## Output
Write valid UTF-8 JSON to the file given in your task:
```json
{
 "run": {"region": "...", "searches_done": 0, "stopped_by_captcha": false, "notes": ""},
 "queries": [{"q": "...", "useful_results": 0, "note": ""}],
 "subreddits": [{"name": "developersIndia", "region": "India", "language": "en", "role": "builders", "why": "...", "size_hint": null, "evidence_url": "..."}],
 "finds": [{"app": "", "store_id": null, "store_url": null, "country": "", "developer": "", "dev_type": "", "lenses": ["K1"], "what_it_is": "", "sets_apart": "", "traction": "", "monetization": "", "women_oriented": "unknown", "evidence": [{"title": "", "subreddit": "", "age": "", "comments": "", "url": ""}], "confidence": "medium"}]
}
```
Save the file after every 8 searches so nothing is lost. Verify it loads with Python at the end. Reply with: searches done, number of finds, number of subreddits, top 8 finds (one line each), and whether you hit a CAPTCHA.
