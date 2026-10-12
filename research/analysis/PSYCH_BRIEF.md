# Psychological extraction brief

Goal: find the psychological root of why Gen Z women in the US adopt, keep using and pay for self-improvement apps. You get a packet of apps with a description and a sample of US App Store reviews (mostly 4–5 star, some 1–3 star). Work only from the packet. Do not invent. Quote reviews verbatim (short).

For EACH app, write:
- `core`: one sentence: the psychological job the app does for the user (not the feature).
- `trigger`: why users came (what state/need; from reviews).
- `retention`: what keeps them (the loop: cue → action → reward → feeling).
- `emotional_tone`: how users describe the feeling. Classify: gentle/safe/cozy vs. pressure/guilt/shame vs. hype/competition. Give 1–2 quotes.
- `identity`: identity statements if any ("I'm finally the kind of person who…", "that girl", "it makes me feel like…").
- `aesthetics`: do users mention cute, aesthetic, design, colors, characters? How important is it (high/medium/low)?
- `social`: friends, sharing, accountability, community mentions.
- `money`: what they pay for, price points mentioned, paywall complaints (count in sample).
- `female_signal`: evidence the audience skews female Gen Z (language, references), low/medium/high.
- `quotes`: up to 5 verbatim quotes with the rating.
- `anti_patterns`: what users reject (from negative reviews).

Then a `synthesis` section (this is the most important part):
1. `mechanisms`: ranked list of the 8–10 psychological mechanisms that recur across the apps, each with: name, one-sentence explanation of WHY it works for this audience, which apps show it (ids), approximate count of reviews supporting it in the packet, best quote.
2. `common_root`: your hypothesis in 3–5 sentences of the single deepest common root behind the successful ones.
3. `what_fails`: patterns that generate backlash (with evidence).
4. `paid_for`: what this audience demonstrably pays for vs. refuses to pay for.
5. `gaps`: unmet needs or recurring requests that no app in the packet fully serves.

Output: valid JSON (UTF-8) with keys `apps` (object keyed by id) and `synthesis`. English. Verify it loads with Python. Reply with a 10-line summary of the synthesis.
