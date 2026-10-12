# Research: viralne self-improvement aplikacije (US App Store)

Traže se aplikacije koje je napravio mali developer, koje imaju kritičnu masu korisnika uz malo marketinga, uklapaju se u self-improvement nišu, lako se prave i lako se reklamiraju. Metodologija i šablon profila su u `../.claude/skills/viral-app-research/SKILL.md`.

## Pokretanje
Potreban je samo Python 3 (standardna biblioteka, bez paketa).

```
python scripts/01_discover.py     # otkrivanje: Apple pretraga + US top liste
python scripts/02_filter.py       # automatski filteri, recenzije, developer, oznaka praćenja
```

Apple dozvoljava oko 20 poziva u minuti, pa pun sken traje oko sat vremena.

## Folderi
- `config/` – ključne reči, kategorije, pragovi i težine (menjaju se bez diranja koda)
- `scripts/` – skripte
- `data/raw/<datum>/` – sirovi Apple odgovori i log
- `data/pool_<datum>.json` – sve pronađene aplikacije
- `data/candidates_<datum>.json` – A i B lista posle automatskih filtera
- `data/sources/` – recenzije po aplikaciji, registar subreddita i Reddit tema
- `data/snapshots/` – dnevna istorija
- `analysis/apps/` – profil svake aplikacije
- `output/` – kandidati (CSV za Excel), top pikovi, dashboard

## Ograničenja
- Za iOS nema broja preuzimanja. Koristimo relativne signale: ocene u US, ocene po danu, recenzije po nedeljama, rang na listama.
- Reach i potrošnja za reklame u US nisu javni. Intenzitet marketinga je složena procena (0–3).
- Reddit se čita kroz Google pretragu u Chrome-u, jer je reddit.com direktno blokiran.
