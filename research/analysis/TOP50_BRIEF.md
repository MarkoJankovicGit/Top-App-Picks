# Scoring apps for "Top 50 picks"

We pick small, little-known foreign apps (App Store storefronts and Reddit finds) that we could rebuild or adapt quickly for US Gen Z (women first), launched through TikTok-led distribution. The team's edge is Gen Z and TikTok distribution, so a product must be simple to build and easy to market there.

Score each app 1–5 on four criteria, using only the packet (no web):
1. `build`: is it simple to build as a full iOS+Android app by 3 developers with AI in about 2 months? 5 = simple, 1 = heavy (hardware, large content library, complex AI/backend).
2. `marketing`: is it easy to market to Gen Z on TikTok? Think of a filmable hook: a visible transformation, a reaction, a challenge, a shareable result, a relatable pain. 5 = obvious viral format, 1 = hard to show.
3. `retention`: is there a built-in reason to come back daily? Streak, ritual, character/pet, friends or group, accumulating collection, time-anchored routine. 5 = strong mechanism, 1 = one-off tool.
4. `revenue`: the most important. Would people pay (subscription, or ads inside the app), and why would they not just use a free alternative? 5 = clear paid value that free tools cannot match (personal, ongoing, emotional, social, or convenience-critical) and evidence of paying users; 1 = commodity people get free (ChatGPT/NotebookLM-style tools, plain trackers).

Then write a very simple brief (plain English, 1–2 short sentences each, no jargon):
- `product`: what is the product?
- `audience`: who is our target audience in the US?
- `revenue_why`: why would it generate revenue (and why not free)?
- `retention_how`: where is the retention mechanism?
- `tiktok_hook`: one line, the video we would film.
- `risk`: biggest risk in one short line.

Also set `exclude` true (with a short `exclude_reason`) if the app is not a fit: games, finance, kids, religious content, big company, medical, or copyright/IP-bound (e.g. LOTR themed).

Output: valid UTF-8 JSON object keyed by packet `key`: {"exclude": false, "scores": {"build":1-5,"marketing":1-5,"retention":1-5,"revenue":1-5}, "product": "", "audience": "", "revenue_why": "", "retention_how": "", "tiktok_hook": "", "risk": ""}. Be honest and discriminating: use the full 1–5 range, do not give everything 4. Mark inferences as "(inference)". Verify the file loads and every key is present. Reply with the count, number excluded and the 6 highest-scoring apps with a one-line reason each.
