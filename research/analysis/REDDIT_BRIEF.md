# Reddit kroz Google pretragu (Chrome)

reddit.com je blokiran za direktno otvaranje. Reddit čitamo kroz Google rezultate u Chrome-u (alati `mcp__claude-in-chrome__*`; prvo `tabs_context_mcp` sa createIfEmpty, pa napravi svoj tab sa `tabs_create_mcp` i zatvori ga na kraju). Samo čitaj.

## Postupak po aplikaciji
1. Kratko ime aplikacije (do ":" ili " - ").
2. `navigate` na `https://www.google.com/search?q=site%3Areddit.com+%22<kratko ime>%22+app` (URL-enkodovano), pa `get_page_text` (koristi `browser_batch`). Za linkove pokreni `javascript_tool` (učitaj ga kroz ToolSearch): `Array.from(document.querySelectorAll('a h3')).map(h=>({t:h.innerText,u:h.closest('a').href}))`. Ako je ime generičko, dodaj ime developera ili ključnu reč iz kategorije.
3. Iz rezultata izvuci teme koje su stvarno o toj aplikaciji: naslov, subreddit, okvirni broj komentara, starost ("pre 3 meseca"), izvod najpopularnijeg odgovora ako postoji.
4. Klasifikuj svaku temu: preporuka / žalba / predlog / objava developera / pitanje / UGC oglas (developer traži plaćene kreatore). Ako postoji bar jedan UGC oglas ili regrutacija kreatora, stavi `"ugc_hiring": true`. To je dokaz plaćenog influencer marketinga.
5. Druga pretraga za plaćene kreatore: `https://www.google.com/search?q=site%3Areddit.com+%22<kratko ime>%22+(UGC+OR+creators+OR+%22paid+per+video%22)`. Ako nađeš oglas gde developer traži kreatore za tu aplikaciju, `"ugc_hiring": true` i dodaj temu tipa "UGC oglas".
6. Ako Google prikaže CAPTCHA ili "unusual traffic", stani, sačuvaj ono što imaš i javi u izveštaju.

## Izlaz
JSON u zadatom fajlu, ključ je ID aplikacije (string):
```json
{"<id>": {"name": "...", "subreddits": ["INTVL", "running"], "threads": [{"title": "...", "subreddit": "INTVL", "comments": "60+", "age": "pre 1 godine", "type": "preporuka", "url": "https://www.reddit.com/..."}], "suggestions": ["konkretni predlozi korisnika, na srpskom"], "ugc_hiring": false, "notes": "1–2 rečenice na srpskom: koliko se pominje, organski ili od developera, dominantan ton", "date": "2026-10-12"}}
```
Ako nema rezultata: `{"subreddits": [], "threads": [], "notes": "Nema pominjanja na Redditu u Google rezultatima", "date": "2026-10-12"}`.
Pauza od bar 20 sekundi između pretraga (Google je posle ~40 brzih pretraga uveo CAPTCHA). Samo jedan agent u isto vreme sme da pretražuje Google. Aplikacije koje su u postojećem izlazu označene sa "status": "not_checked" obradi i zameni.
