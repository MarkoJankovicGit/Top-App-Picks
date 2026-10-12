# Provera marketinga u Meta Ad Library (US)

Za svaku aplikaciju sa spiska proveri aktivne reklame u US. Koristi ugrađeni browser (alati `mcp__Claude_Browser__*`), bez prijave. Samo čitaj: ne klikći "Log in" i ne prihvataj ništa.

## Postupak po aplikaciji
1. Kratko ime: naziv aplikacije do prvog ":" ili " - " (npr. "Liftoff - Ranked Gym Workouts" → "Liftoff"). Ako je ime generičko (jedna česta reč), dodaj drugu reč iz naziva.
2. `navigate` na:
   `https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&q=<kratko ime, URL-enkodovano>&search_type=keyword_unordered&media_type=all`
   pa `computer` wait 4 sekunde (koristi `browser_batch` za navigate + wait + javascript u jednom pozivu).
3. `javascript_tool` sa ovim kodom:
```js
(() => {
 const t = document.body.innerText;
 const total = (t.match(/~?([\d,.]+K?) results?/)||[])[1]||"0";
 const blocks = t.split("Library ID:").slice(1);
 const adv = {};
 for (const b of blocks) {
   const start = (b.match(/Started running on ([^\n]+)/)||[])[1];
   const lines = b.split("\n").map(s=>s.trim()).filter(Boolean);
   let i = lines.findIndex(l=>/^See (ad|summary) details$/.test(l));
   const name = i>=0 ? lines[i+1] : "?";
   const multi = (b.match(/(\d+) ads use this creative/)||[])[1];
   adv[name] = adv[name]||{cards:0, ads:0, starts:[]};
   adv[name].cards++; adv[name].ads += multi?+multi:1; if(start) adv[name].starts.push(start);
 }
 return {total, loaded: blocks.length, adv};
})()
```
4. Oglašivač je aplikacija ako ime oglašivača sadrži kratko ime ili ime developera. Ostale oglašivače ignoriši. Ako nema nijednog oglašivača koji odgovara, aplikacija nema aktivnih reklama u US.
5. Nivo:
   - 0: nema aktivnih reklama aplikacije
   - 1: 1–5 reklama, sve počele u poslednjih 30 dana ili mali broj varijanti
   - 2: 6–20 reklama, ili bar jedna traje 60+ dana
   - 3: više od 20 reklama, ili 10+ reklama od kojih neke traju 60+ dana
   Ako je `loaded` 30, a ukupno ima više rezultata koji pripadaju aplikaciji, računaj da ima više od 20 (nivo 3).

## Izlaz
JSON objekat u fajlu koji ti je zadat, ključ je ID aplikacije (string):
```json
{"<id>": {"name": "...", "query": "...", "level": 0, "ads": 0, "oldest_start": "25 Jun 2026", "advertiser": "...", "evidence": "Kratko na srpskom: npr. '38 aktivnih reklama u US, najstarija od 25.6.2026, aktivne kampanje u septembru'", "url": "<adresa pretrage>", "date": "2026-10-12"}}
```
Pravi pauzu od bar 3 sekunde između aplikacija. Ako Facebook traži prijavu ili prikaže CAPTCHA, stani, sačuvaj ono što imaš i javi to u izveštaju.

## Iskustva iz prve provere
- Kad je deo naziva do ":" ili " - " samo generički opis (npr. "Micro Learning", "Intermittent Fasting Tracker"), traži po brendu ili imenu developera.
- Kad obična pretraga vrati hiljade nepovezanih rezultata, traži tačnu frazu (stavi ime u navodnike, `%22Ime%22`).
- Oglašivač se može zvati drugačije od aplikacije (npr. "Turbolearn ai" za Turbo AI). Proveri link reklame i tekst.
- Isključi oglašivače sličnog imena koji nisu ta aplikacija (drugi brendovi, druge aplikacije) i to navedi u evidence.
- Za tačnu frazu koristi `search_type=keyword_exact_phrase` (ne navodnike uz keyword_unordered, to vraća desetine hiljada nepovezanih rezultata).
- Neke aplikacije se reklamiraju preko "persona" stranica (izmišljeni coach ili influencer) bez pominjanja brenda. Ako je nivo 0 a aplikacija ima oznaku praćenja i reviews pominju reklame, pretraži i domen sajta aplikacije i karakteristične fraze iz opisa. Lažna nula je gora od nepotvrđene: tada stavi nivo 1 i u evidence napiši "moguće persona reklame, nepotvrđeno".
- Kod deljenih imena proveri App Store ID u linku reklame.
- Meta Ad Library radi ISKLJUČIVO u ugrađenom browseru (bez prijave). Chrome je prijavljen na Markov Facebook nalog i ne koristi se za ovo.
- Sačekaj da se rezultati učitaju (ako je "loaded" 0, a stranica još učitava, sačekaj još 3 sekunde i ponovi skriptu), da ne bude lažnih nula.
