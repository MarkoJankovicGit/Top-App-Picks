---
name: viral-app-research
description: Research US App Store aplikacija u self-improvement niši koje su mali developeri napravili, koje imaju kritičnu masu korisnika uz malo marketinga, a lako se prave i reklamiraju. Koristi kad Marko traži sken, osvežavanje liste, profil aplikacije, glas korisnika (recenzije, Reddit) ili ažuriranje top pikova u folderu research/.
---

# Viral app research

Cilj: lista od 50–100 top pikova za partnera iz USA (Gen Z, edukacija o investiranju, mreža mikroinfluencera). Tražimo aplikacije koje je napravio mali developer, imaju kritičnu masu korisnika bez ozbiljnog marketinga, uklapaju se u self-improvement nišu, lako se prave (do 2 meseca, 3 developera + AI) i lako se reklamiraju.

Psihološki most ka partnerovom biznisu: male stvari koje se slažu kroz vreme (doslednost, nizovi dana, vidljiv napredak, takmičenje). Finansije NISU niša.

## Pravila izvora
- Koristimo samo primarne i javne izvore: Apple (Search API, lookup, RSS top liste, RSS recenzije, stranica aplikacije), Google Play stranica, Meta Ad Library, Google Trends, Wayback Machine, TikTok hashtag stranice, Google pretraga `site:reddit.com` i `site:tiktok.com` kroz Chrome, sajt developera, privacy policy, OpenCorporates, X, Product Hunt.
- Ne koristimo alate za app intelligence (Sensor Tower, AppMagic, Appfigures, FoxData, AppGoblin, Sonar) i ne tražimo naloge za TikTok, LinkedIn ili Facebook.
- reddit.com je blokiran direktno; Reddit čitamo kroz Google rezultate u Chrome-u (naslov, subreddit, broj komentara, izvod).
- Svaki broj ima izvor i datum. Procena se uvek označava kao procena, sa pouzdanošću (visoka / srednja / niska).
- U Chrome-u samo čitamo: bez objava, lajkova, praćenja, poruka. Ljudski tempo.

## Levak
1. Otkrivanje: `python scripts/01_discover.py` (ključne reči iz `config/keywords.json` + US top liste iz `config/categories.json`).
2. Automatski filteri: `python scripts/02_filter.py` (niša, kritična masa, kvalitet, mali developer, živa je, oznaka praćenja). Izlaz `output/kandidati_<datum>.csv`, A i B lista.
3. Ručna provera za A + B (Claude): intenzitet marketinga (Meta Ad Library za US, TikTok #ad), izrada, lakoća reklamiranja, princip, glas korisnika, Reddit.
4. Dubinski profil za top 15–20: ko stoji iza (sajt, privacy policy, OpenCorporates, X, Google), Google Trends, Wayback istorija, TikTok.
5. Izlaz: `output/top-picks.xlsx`, `output/dashboard.html`, metodologija.

Pragovi i težine su u `config/thresholds.json`. Ne menjati ih bez Markove potvrde.

## Intenzitet marketinga (0–3)
Meta Ad Library ne prikazuje reach ni potrošnju za reklame samo u US. Zato:
- 0: nema aktivnih reklama, nema #ad na TikToku, nema "Data Used to Track You"
- 1: do ~5 reklama, malo varijanti, kratko trajanje, ili EU reach < 100k
- 2: 6–20 reklama, kampanje 60+ dana, više varijanti kreativa
- 3: 20+ reklama, mnogo kreativa, redovne influencer saradnje
Prolazi 0–1, granično 2.

## Ocena (0–100)
Tražnja 20, lakoća reklamiranja i viralnost 20, jaz u marketingu 15, lakoća izrade 15, glas korisnika i prostor za unapređenje 10, monetizacija 10, psihološki princip i fit 10. Svaka ocena ima obrazloženje u jednoj rečenici.

## Šablon profila: `analysis/apps/<id>-<slug>.md`

```
# <Naziv> (<id>)
Developer: <prodavac> · Tip: solo / mali tim / firma (pouzdanost) · Aplikacija developera: N
Izašla: <datum> · Ocene US: N (prosek X) · Ocene/dan od izlaska: N · Recenzije 30d / prethodnih 30d: N / N
Linkovi: App Store · Google Play (opseg instalacija ili "nema") · sajt

## Šta je izdvaja
Konkretan zaokret u odnosu na standardnu aplikaciju iz kategorije, u 1–2 rečenice.
Primer: INTVL je aplikacija za trčanje, ali trčanjem u krug osvajaš teritoriju na mapi i braniš je od drugih trkača.

## Specifičnosti
- Ključna mehanika (šta korisnik radi svaki dan)
- Šta je deljivo (rezultat, mapa, niz, rang)
- Društveni sloj (prijatelji, takmičenje, zajednica)
- Monetizacija (model, cene, šta je iza paywall-a)

## Psihološki princip
Princip i zašto radi, sa dokazom iz recenzija ili Reddita (kratki citati sa linkom).

## Marketing
Nivo 0–3 sa dokazima: broj aktivnih reklama u Meta Ad Library (US), od kada traju, varijante; TikTok organski / #ad; oznaka praćenja.

## Rast
Oblik krive (eksplozija / stabilan rast / plato / pad) iz recenzija po nedeljama, Wayback tačaka, Google Trends. Pouzdanost.

## Glas korisnika
- Top žalbe (tema, broj pominjanja)
- Predlozi za unapređenje
- Pohvale
- Subrediti gde se pominje (upisati i u data/sources/subreddits.csv i reddit_threads.csv)

## Izrada
Procena za kompletnu aplikaciju (iOS + Android, 3 developera + AI): N nedelja. Tehnički rizici i zavisnosti (HealthKit, AlarmKit, Screen Time API, backend, sadržaj).

## Lakoća reklamiranja
4 pitanja (jedna rečenica / vizuelno za 3 sekunde / format za kreatore / deljiv rezultat), rezultat N/4, i ideja za hook.

## Ocena
Tabela kriterijuma sa ocenom i obrazloženjem, ukupno 0–100, lista A/B.

## Izvori
Link · datum provere · šta je preuzeto
```

## Kolone finalne liste
rang, lista (A/B), naziv, developer, tip developera, princip, šta je izdvaja, ocene US, ocene/dan, trend 30d, intenzitet marketinga, izrada (nedelje), lakoća reklamiranja (N/4), monetizacija, top žalba / prilika, subrediti, ukupna ocena, pouzdanost, linkovi, datum provere.

## Dnevno osvežavanje
Ponoviti korake 1–2, uporediti sa prethodnim `candidates_*.json` (nove aplikacije, skokovi u ocenama i recenzijama), ručno obraditi samo nove i promenjene.
