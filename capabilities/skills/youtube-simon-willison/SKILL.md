---
name: youtube-simon-willison
description: Simon Willison (@swillison): L3 credible AI-stack channel (37-video corpus) with transcript-mining commands. Load before digging this channel's transcripts or quoting its frames.
when_to_use: mining @swillison videos; quoting Simon Willison as evidence for GTM/agent-engineering work; choosing what to absorb from lab/bridge/rarity tier (L3 credible)
version: 0.1.0
owner: rig
domain: youtube-corpus
status: draft
verified_by: rig-agent
verified_on: 2026-09-08
outcome: Load channel-scope context before mining the simon-willison corpus or doing GTM/agent work informed by it.
done_when: >
  Digest + top-video index read from the skill body; grep/locate commands
  demonstrated against the on-disk corpus for at least one landmark video.
great_example: youtube_intel/digests/simon-willison_brief.md (this repo, quarantine-rooted)
quality_floor: Digest sections complete; top-video table >= 10 rows; corpus paths verified to exist.
metadata:
  ladder_level: 3
  handle: @swillison
  corpus_root: /Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus
hooks: []
---

# youtube-simon-willison

Channel-scope context for the **@swillison** YouTube corpus — L3 credible tier of the RIG 5-level AI stack.

## What this surface is
## @swillison - digest

- **what it is**: Simon Willison's practical channel bridging small-data tooling (Datasette/SQLite) and emerging LLM agent tooling, with guest-built public-interest projects.
- **episode shape**: Short (1–18 min) solo tool demos and plugin builds; longer (28–48 min) guest-presented "under the hood" project walkthroughs with live demos.
- **recurring themes**:
  - Datasette + SQLite as a sufficient "small data" platform for public-interest work
  - LLM CLI agents (Codex CLI, Claude Code) as composable, pipe-able primitives
  - Prompt injection / security as a first-class design concern for LLM-powered tools
  - Python tooling modernism (uv, sqlite-utils, subprocess-based orchestration)
  - Public-sector data projects (Canada Spends, Congressional Travel, Civic Band)
  - Embeddings and vector search as under-explained primitives for devs
- **signature frames**:
  - "Small data is real data" – SQLite as default, not last resort
  - LLM-as-CLI-harness – treat model calls as subprocesses you can script and chain
  - "Bag of tricks" pragmatism – no silver-bullet architecture, just composable tools
  - Reverse-engineer-by-observation – infer LLM behavior from output traces, not docs
  - Data → SQLite → Web UI → LLM triad as a repeatable project template
- **must-watch**:
  - *FastRender with Wilson Lin - building a web browser with swarms of thousands of coding agents* – clearest look at multi-agent swarm orchestration for UI construction
  - *Embeddings: What they are and why they matter* – best 39-min grounding on when/why to use vector search
  - *Prompt Injection, explained* – the canonical short explanation for why LLM tools need input isolation
  - *Under the hood of Canada Spends with Brendan Samek* – end-to-end public-data pipeline from scrape to interactive web app
  - *My process for upgrading Datasette plugins with uv and OpenAI Codex CLI* – concrete agent-assisted dev workflow pattern
- **mine-for**: Agent-engineering patterns (swarm coordination, CLI agent harnesses, prompt-injection defenses as architectural decisions); practical GTM for indie dev tools (Datasette plugin ecosystem, public-data as marketing); a repeatable "scrape → SQLite → Datasette → LLM → public web" project template for fast, defensible data products.

## Top videos (signal-sorted)
`bKrAcTf2pL4`  48m  FastRender with Wilson Lin - building a web browser with swarms of thousands of   https://www.youtube.com/watch?v=bKrAcTf2pL4 — 
`ArnMdc-ICCM`  39m  Embeddings: What they are and why they matter  https://www.youtube.com/watch?v=ArnMdc-ICCM — 
`t_S-loWDGE0`  34m  VERDAD - tracking misinformation in radio broadcasts using Gemini 1.5  https://www.youtube.com/watch?v=t_S-loWDGE0 — 
`OziYd7xcGzc`  29m  Civic Band, presented by Philip James during Datasette Public Office Hours, 15th  https://www.youtube.com/watch?v=OziYd7xcGzc — 
`T8xiMgmb8po`  28m  Under the hood of Canada Spends with Brendan Samek  https://www.youtube.com/watch?v=T8xiMgmb8po — 
`Lig2gxPEZPo`  25m  Datasette - an ecosystem of tools for working with small data  https://www.youtube.com/watch?v=Lig2gxPEZPo — 
`Th5WOyjuRdk`  20m  llm-consortium with Thomas Hughes  https://www.youtube.com/watch?v=Th5WOyjuRdk — 
`qy4ci7AoF9Y`  18m  My process for upgrading Datasette plugins with uv and OpenAI Codex CLI  https://www.youtube.com/watch?v=qy4ci7AoF9Y — 
`7kDFBnXaw-c`  17m  Introduction to Datasette and sqlite-utils  https://www.youtube.com/watch?v=7kDFBnXaw-c — 
`FgxwCaL6UTA`  12m  Prompt Injection, explained  https://www.youtube.com/watch?v=FgxwCaL6UTA — 
`BoPZltKDM-s`  12m  How I automate my Substack newsletter with content from my blog  https://www.youtube.com/watch?v=BoPZltKDM-s — 
`CDilLbFP1DY`  11m  Congressional Travel Explorer with Derek Willis  https://www.youtube.com/watch?v=CDilLbFP1DY — 
`AFZKp6hbFjI`  4m  Datasette Agent - an AI assistant for Datasette to help explore and analyze data  https://www.youtube.com/watch?v=AFZKp6hbFjI — 
`9o1_DL9uNlM`  7m  Reverse engineering Codex CLI to get GPT-5-Codex-Mini to draw me a pelican  https://www.youtube.com/watch?v=9o1_DL9uNlM — 
`GQvMLLrFPVI`  11m  Using Claude Code for web to build a tool to copy-paste share terminal sessions  https://www.youtube.com/watch?v=GQvMLLrFPVI — 
`VC6dmPcin2E`  7m  Using Claude Code to build a GitHub Actions workflow  https://www.youtube.com/watch?v=VC6dmPcin2E — 
`MKbLUb8RaGs`  2m  Datasette ChatGPT Plugin  https://www.youtube.com/watch?v=MKbLUb8RaGs — 
`9pEP6auZmvg`  9m  llm-logs-feedback with Matthias Lübken  https://www.youtube.com/watch?v=9pEP6auZmvg — 
`g3NtJatmQR0`  4m  Extracting unstructured text and images into database tables with GPT-4 Turbo an  https://www.youtube.com/watch?v=g3NtJatmQR0 — 
`lXwfEYXjsak`  3m  llm-questioncache with Nat Knight  https://www.youtube.com/watch?v=lXwfEYXjsak — 
`mpgWH9KulUU`  1m  Gemini 2.0 Flash multi-modal streaming demo  https://www.youtube.com/watch?v=mpgWH9KulUU — 
`QALfRfavrvU`  11m  Using Datasette with Jupyter to publish your data (JupyterCon 2020)  https://www.youtube.com/watch?v=QALfRfavrvU — 
`B55hcKYye_c`  10m  Datasette: a big bag of tricks for solving interesting problems using SQLite  https://www.youtube.com/watch?v=B55hcKYye_c — 
`0SPqMR08VWU`  10m  How to build, test and publish an open source Python library (without sign langu  https://www.youtube.com/watch?v=0SPqMR08VWU — 

## On-disk corpus
- transcripts: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/simon-willison/transcripts/<id>.txt` (cleaned, one line per cue)
- stats: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/simon-willison/transcripts.stats.json`

Useful moves:
```sh
G=/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/simon-willison
# most substantive episodes
python3 -c "import json;d=json.load(open('$G/videos.json'));[print(v['id'],round((v.get('duration') or 0)/60),'m',v['title'][:70]) for v in sorted(d['videos'],key=lambda v:-(v.get('duration') or 0))[:12]]"
# grep a theme across transcripts
grep -ril "scaling" $G/transcripts/ | head -20
# open one transcript
cat $G/transcripts/bKrAcTf2pL4.txt
```
Known gap: /videos tab only — Shorts: Shorts-heavy, few/indexed.

## One-liner
> Simon Willison
