# Uputstvo za analizu paketa aplikacija

Kontekst: tražimo aplikacije u US App Store-u koje je napravio mali developer, imaju kritičnu masu korisnika uz malo marketinga, uklapaju se u self-improvement nišu (navike, kretanje, trčanje, spavanje i buđenje, fokus, odvikavanje, takmičenje, učenje sa bodovanjem, zdrave navike), lako se prave (najviše 2 meseca, 3 developera + AI, kompletna aplikacija za iOS i Android) i lako se reklamiraju kroz TikTok i Instagram influencere (publika 18–24, USA). Psihološki most: male stvari koje se slažu kroz vreme (doslednost, nizovi, vidljiv napredak, takmičenje). Finansije NISU niša.

Ulaz: `analysis/batches/batch_NNN.json`: opis aplikacije, metrike i uzorak recenzija (najviše polovina sa ocenom ≤3).
Izlaz: `analysis/batches/result_NNN.json`, jedan JSON objekat čiji su ključevi ID-jevi aplikacija (kao string). Sav tekst piši na srpskom (latinica), kratko i konkretno. Ne izmišljaj činjenice. Ono što ne vidiš u podacima označi kao procenu.

## Isključi aplikaciju (`"exclude": true` + `exclude_reason`) ako:
- osnovna vrednost nije lična navika, disciplina, kretanje, učenje ili odvikavanje (npr. čisti sadržaj, verski sadržaj, klinički ili medicinski tracker bolesti, utility, dating, finansije, kupovina, sportski rezultati i klađenje)
- iza je velika firma, poznat brend ili fabrika aplikacija (mnogo sličnih aplikacija, generički šablon)
- ne može da se napravi za 2 meseca (hardver, licencirani sadržaj, sopstveni veliki ML modeli, velika biblioteka profesionalnog sadržaja, regulisan domen)

Za isključene je dovoljno: `{"exclude": true, "exclude_reason": "...", "name": "..."}`.

## Za ostale popuni:
```json
{
  "<id>": {
    "name": "...",
    "exclude": false,
    "list": "A ili B (A = sve deluje kao prolaz; B = jedan kriterijum granični)",
    "principle": "jedna oznaka iz kataloga ispod",
    "differentiator": "Šta je izdvaja: konkretan zaokret u odnosu na standardnu aplikaciju iz kategorije, 1–2 rečenice. Primer: 'Aplikacija za trčanje, ali trčanjem u krug osvajaš teritoriju na mapi i braniš je od drugih trkača.'",
    "specifics": ["Ključna mehanika: ...", "Šta je deljivo: ...", "Društveni sloj: ...", "Monetizacija: ..."],
    "psych": "Psihološki princip i zašto radi, sa kratkim citatom iz recenzije kao dokazom",
    "developer_type": "solo / mali tim / firma / nepoznato (+ zašto, iz naziva prodavca i broja aplikacija)",
    "build_weeks": 6,
    "build_notes": "Šta je potrebno: backend, HealthKit/Health Connect, AlarmKit, Screen Time API, mape, AI, sadržaj; najveći tehnički rizik",
    "marketability": {"one_sentence": true, "visual_3s": true, "creator_format": true, "shareable": false},
    "marketability_score": 3,
    "hook": "Ideja za TikTok hook u jednoj rečenici",
    "monetization": "Model i cene ako se vide (pretplata, freemium, kupovine, reklame)",
    "complaints": ["Top žalbe iz recenzija, najviše 4, sa okvirnim brojem pominjanja u uzorku"],
    "suggestions": ["Konkretni predlozi korisnika za unapređenje, najviše 4"],
    "praise": ["Šta korisnici najviše hvale, najviše 3"],
    "opportunity": "Šta bismo mi unapredili ili promenili, 1–2 rečenice",
    "growth": "Kratko: ocene po danu od izlaska, recenzije 30d naspram prethodnih 30d, šta to govori",
    "scores": {"marketabilityVirality": 1-5, "marketingGap": 1-5, "buildEase": 1-5, "voiceOfCustomer": 1-5, "monetization": 1-5, "principleFit": 1-5},
    "confidence": "visoka / srednja / niska",
    "sources": [{"label": "App Store", "url": "<url iz paketa>", "date": "2026-10-12"}],
    "checked": "2026-10-12"
  }
}
```

## Ocene 1–5
- marketabilityVirality: koliko se lako snima, deli i širi (4 pitanja + društveni sloj)
- marketingGap (privremeno, dok se ne proveri Meta Ad Library): 5 = bez oznake praćenja i solo ili mali developer; 3 = jedno od toga; 1 = oznaka praćenja i jasni znaci plaćenog marketinga (npr. recenzije pominju reklame)
- buildEase: 5 = do 4 nedelje; 4 = 5–6; 3 = 7–8; 2 = granično; 1 = preko 2 meseca
- voiceOfCustomer: koliko jasnih, ponovljenih žalbi i predloga postoji, tj. koliko je očigledno šta se može unaprediti
- monetization: 5 = jasna pretplata koju korisnici prihvataju; 3 = freemium ili nejasno; 1 = nema monetizacije ili je korisnici odbijaju
- principleFit: snaga psihološkog principa i uklapanje u narativ doslednosti za Gen Z

## Katalog principa
Obaveza unapred i trenje · Niz dana i strah od gubitka · Takmičenje i rang · Osvajanje i posedovanje · Vidljiv napredak · Polaganje računa · Grupni izazov · Nagrada za akciju · Ocena sebe i kvantifikacija · Identitet i samoizražavanje · Igrifikacija učenja · Odvikavanje i oporavak · Virtuelni ljubimac i briga
