# data branch: full research database

Archive of the complete database behind Top App Picks (raw Apple responses, per-storefront pools, per-app reviews, analysis batches). It is a backup, not a deployable branch.

- **Do not merge into `main`.** `main` is deployed on Vercel and must stay small. Vercel deployments are disabled on this branch (`vercel.json`).
- Everything under `research/data/` and the batch and packet files under `research/analysis/` were generated locally by the scripts in `research/scripts/`.
- Restore: `git worktree add ../top-app-picks-data data`.
- Size: about 334 MB in 1,313 files; the largest file is 27.5 MB.

| Folder | What it holds |
|---|---|
| `research/data/raw/` | Raw Apple Search API and chart responses (US scan), run log |
| `research/data/pool_*.json`, `stage1_progress_*.json` | All 11,551 US apps found and the filter progress |
| `research/data/global/` | Per-storefront pools for 21 countries (60,009 apps), candidates, leaders, icon cache |
| `research/data/sources/` | App Store reviews per app, community registry, Reddit thread log |
| `research/analysis/batches/`, `global_batches/`, `reddit_batches/` | Packets handed to the analysis agents |
| `research/analysis/psych_packet_*.json` | Review packets used for the psychology extraction |
