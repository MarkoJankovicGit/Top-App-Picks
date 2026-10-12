# Profiling foreign small-developer apps (App Store, non-US storefronts)

## Context
We look for ideas for a consumer app for US Gen Z women (self-improvement, subscription). Three concepts (lenses):
- **K1 – Gentle self-improvement for women:** habits, rituals, routines, mood/journal, identity, cute companions/pets, cycle-aware wellness, soft discipline, accountability with friends.
- **K2 – Micro-learning:** the user supplies their own material (PDF, notes, links, lectures) and the app turns it into short reel-style videos, cards, quizzes; any "learn in minutes" mechanic.
- **K3 – Audio on the go:** the user picks a topic/goal and gets personalised audio (podcast/mp3, TTS, summaries, guided walks) for walking, commuting, driving; habit- and interest-aware.

The apps in your packet come from non-US App Store storefronts (country given). They were found with local-language searches, have real local traction, are small-ish developers and are mostly little known in the US. We want to understand **what each app really does, what makes it different, and which ideas could travel** to US Gen Z women. Loosely related apps are fine.

## Packet
A JSON list; each item has: key (`cc:trackId`), country, name, seller, genre, released, updated, ratings_local, avg_rating, ratings_us (null = not found in the US store), in_us, dev_apps (number of apps by the developer), languages, price, lens_hits (how many keyword hits per lens), matched_keywords, url, seller_url, description (may be in a local language, translate it).

## For EACH app write (English, concise)
- `name_en`: the app name translated or transliterated if useful
- `exclude`: true only if clearly irrelevant: pure games, finance/trading, children's apps, religious-content apps, medical devices, big corporation, adult/gambling, app factory. Give `exclude_reason`. Then the other fields can be omitted.
- `what_it_is`: one sentence
- `sets_apart`: the twist/mechanic that differentiates it from a standard app in its category (1–2 sentences). Be specific, not generic.
- `lens_fit`: {"K1":0-3,"K2":0-3,"K3":0-3} where 0 none, 1 loose, 2 relevant, 3 core; plus `lens_note`
- `women_oriented`: "yes" | "no" | "unknown" (evidence from the description: e.g. "for girls", female characters, cycle, beauty, aesthetic)
- `dev_type`: "solo" | "small team" | "company" | "unknown" (infer from the seller name; person name = likely solo)
- `monetization`: from the description/price (subscription, IAP, ads, free, one-time)
- `traction`: one line using ratings_local, release date and US presence (e.g. "42k ratings in KR since 2021, not in US store")
- `export_potential`: 1–5 + `export_reason` (is the mechanic language-agnostic? culture-bound? content-bound? regulated?)
- `idea_seed`: one sentence: the transferable idea for our concepts, phrased as a product idea for US Gen Z women
- `build_effort`: "low" | "medium" | "high" for 3 developers with AI assistance (full iOS+Android), plus the main components
- `confidence`: "low" | "medium" | "high"

Work only from the packet (descriptions, metrics). Do not search the web. Do not invent facts that are not in the description; mark inferences as such.

## Output
Valid UTF-8 JSON to the file given in your task: an object keyed by the packet `key`. Verify it loads with Python and that every key from every packet is present. Reply with: number of apps, number excluded, and the 8 most interesting apps (name, country, one line why).
