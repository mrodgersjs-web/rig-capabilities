# Discover AI corpus — provenance record

Captured 2026-09-02 by `scripts/scrape_channel_corpus.py`, re-run weekly by
`scripts/weekly_capability_scout.py`. This file records what was taken, what was
verified, and what was refused. The transcripts themselves are **not** in git; see
`docs/SOURCE-LICENSE.md`.

## Channel

| field | value |
|---|---|
| name | Discover AI |
| handle | `@code4AI` |
| subscribers | ~91,000 |
| videos on channel | 1,402 (no streams tab; 104 shorts) |
| cadence | roughly daily, agent-research readouts |

## Capture window

- Lookback: 15 days from capture (`--since-days 15`), covering 2026-08-19 → 2026-09-02.
- Targets in window: **21 videos**, ~10.2 h total, mean ~29 min. Shorts in window: 0.
- Transcribed: **18** videos, **82,444 words**, 18 descriptions.
- Implied speech rate 158 wpm over the 10.2 h of audio, which is the check that the
  word-level caption overlap-merge deduplicated correctly rather than double-counting.

### Excluded, and why

| video | title topic | tool-reported failure |
|---|---|---|
| `OrpXpMd8mEY` | AutoPolicy for SKILLS | `no_captions` |
| `thrFWdF0K4Q` | Anthropic IPO | `no_captions` |
| `9CaOPAqu0Jg` | Query-specific Context Generation | `no_captions` |

All three are channel-membership content. yt-dlp reports them as `no_captions`, not as
an explicit membership error — that is the recorded observation, and nothing beyond it
is claimed. **No attempt was made to obtain captions for them by any other route.** A
gap in the corpus is a fact about the corpus; paying a creator to look at a video is
not a research obstacle to engineer around.

## Local corpus layout (gitignored)

```
.context/discover-ai/
  manifest.json          channel-corpus-v1: per-video ids, dates, word counts, failures
  raw/                   36 .vtt caption files + 18 .info.json (creator's raw metadata)
  transcripts/<id>.txt   cleaned single-line transcript, 18 files
  descriptions/<id>.md   video description, 18 files
  dossiers/<id>.md       per-video analysis written by scout agents (derived work)
  link-verdicts.json     machine verdict per cited arXiv id and GitHub repo
  capability-matrix.json 59 deduplicated capability rows
```

## Citation verification

Nothing in the capability matrix may cite a link that was not machine-verified.

### arXiv: 27 of 27 ids resolve

Queried in one batched call to `export.arxiv.org/api/query?id_list=`. Every id named
across the 18 dossiers returned an entry with a matching title. Two implementation
notes that cost real debugging time, recorded so the next reader does not repeat them:
the API emits `http://arxiv.org/abs/<id>vN` in `<id>`, so a pattern requiring
`https?://` in the wrong position silently resolves *nothing* — and "no papers this
week" is indistinguishable from a broken parser, which is why
`tests/test_weekly_scout.py::test_https_id_elements_still_resolve` exists.

Verified ids and titles are in `.context/discover-ai/link-verdicts.json`. The spine:

- `2608.29596` Towards a Systems Foundation for Agentic Skills (the six-tuple
  `<A,I,C,P,π,E>` skill formalisation)
- `2608.26263` SKILL.state · `2608.27454` WikiSkill · `2602.02474` MemSkill ·
  `2605.23904` SkillOpt · `2602.12670` SkillsBench
- `2608.11888` Agent Skills Can Be Harmful · `2608.12851` Practice Makes Unsafe
  (skill misevolution)
- `2608.13951` HELIX · `2608.13560` AutoDesign · `2608.20169` Task-CoEvolve ·
  `2607.15524` Recursive Harness Self-Improvement · `2606.09498` Self-Harness
- `2608.24876` Recursive Experiential-Working-Memory Evolution · `2608.22974`
  Dynamic Ontology (OaK) · `2608.21156` Graph Engineering · `2608.27969` openJiuwen
- `2608.17393` LEGO-RL · `2608.17253` Co-RL · `2608.25198` Tunable Tool-Call Rates ·
  `2608.17528`/`2508.03680` Agent Lightning · `2505.24298` AReaL · `2510.12633`
  Laminar · `2602.03439` Ontology-to-tools · `2601.21700` Ontology-Guided Multi-Agent

### GitHub: 23 of 24 repos exist; one is fabricated

Checked with `gh api repos/<org>/<repo>` for existence, stars, licence and last push.
Full table in `link-verdicts.json`. Verified set includes `HKUDS/HELIX`,
`Yaxin9Luo/AutoDesign`, `openJiuwen-ai/jiuwenswarm`, `Agent4Science-UTokyo/Task-CoEvolve`,
`LegoX/Lego-RL`, `Gen-Verse/Recuris`, `ashutoshsinghpr7/wikiskill`,
`milanhorvatovic/skill-system-foundry`, `henrymao2004/misevolve`,
`benchflow-ai/skillsbench`, `microsoft/Agent-Lightning`, `areal-project/AReaL`,
`THUDM/slime`, `verl-project/verl`, `anthropics/skills`, `FoundationAgents/MetaGPT`,
`NousResearch/hermes-agent`, `DEEP-JLU/Awesome-Graph-Engineering`,
`DrStranded/Co-RL`, `EvanZhouDev/ai-model-index`,
`MaurerAnton/artificialanalysis-ai-parser`, `openJiuwen-ai/agent-core-java`.

**`YuqiChen4188/Steering-Tool-Use-Propensity` does not exist.** A scout agent
attributed it to `arXiv:2608.25198` and asserted the URL was "taken from the fetched
arXiv abstract". It was checked three ways: `gh api` returns 404; `gh search repos`
for the slug and for the title returns nothing; and `curl` of the abstract page with
tags stripped contains no `github` string at all. That is a fabricated citation, not a
typo, and it is recorded in the fabrication ledger
(`~/.rig/leases/fabrication-ledger.jsonl`, session `discover-ai-corpus-2026-09-02`)
rather than quietly corrected. The paper `2608.25198` itself is real and verified.

## Derived surface

`.context/discover-ai/capability-matrix.json`: 59 capability rows after cross-video
dedupe — 13 hooks, 11 commands, 9 loops, 8 evals, 6 harnesses, 5 data, 4 skills,
3 tools; 39 upgrades to existing assets and 20 new. 27 rows name an asset that exists
in `capabilities/` today. Each row carries sources, verified papers, verified OSS or
`none`, mechanism, the specific gap in the named RIG asset, and a `done_test`.

## Weekly re-run

`scripts/weekly_capability_scout.py stage` re-runs capture plus citation verification
deterministically and queues the agent pass; the cron spec
`data/capability-scout-weekly-cron.json` is **ACTIVE** (Orca automation
`ba6ba3b5-98dc-476b-a5ef-e9c8572d0a00`, Mondays 17:00 America/Denver, next 2026-09-07), activated
2026-09-04 under Gate-D run id `f2031-scout-weekly-1` (two-approval doctrine satisfied).
Proven runs to date:

| run | window | queued | arXiv | repos |
|---|---|---|---|---|
| `2026-W36` | 3 days | 4 videos, 18,985 words | 1 verified | 1 verified |
| `2026-W36-weekly-proof` | 9 days | 9 videos, 41,124 words | 2 verified | 1 verified |

Both recorded `members_only`/`no_captions` exclusions rather than retries.
