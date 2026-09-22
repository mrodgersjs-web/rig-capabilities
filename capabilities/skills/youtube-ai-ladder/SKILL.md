---
name: youtube-ai-ladder
description: Umbrella for the 21-source AI corpus — 18 tiered YouTube channels plus TLDR AI, One Useful Thing, and The Batch — with full-text mining and webhook ingestion. Load first to route to the right source.
when_to_use: deciding which tier/source to mine; grounding AI/model/agent claims; comparing newsletter framing with primary lab videos; touching or auditing the corpus/webhook
version: 0.2.0
owner: rig
domain: youtube-corpus
status: draft
verified_by: rig-agent
verified_on: 2026-09-08
outcome: Route to one of 18 channel skills or three indexed full-text newsletter corpora before making AI claims.
done_when:
  - cmd:test "$(find capabilities/skills -path '*/youtube-*/index.json' | wc -l | tr -d ' ')" -ge 18
  - grep:capabilities/skills/youtube-ai-ladder/SKILL.md:## Newsletter sources
quality_floor: All 18 child skills exist; all three newsletter indexes and full-text directories exist.
metadata:
  corpus_root: /Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus
  webhook_port: 8793
hooks: []
---
# youtube-ai-ladder

RIG's five-level AI stack as 18 YouTube channels + 3 full-text newsletters + a self-healing corpus.

| L | skill | handle | channel | top-rows |
|---|-------|--------|---------|----------|
| 1 | `youtube-the-rundown-ai` | @TheRundownAI | The Rundown AI | 10 |
| 1 | `youtube-matt-wolfe` | @mreflow | Matt Wolfe | 40 |
| 2 | `youtube-3blue1brown` | @3blue1brown | 3Blue1Brown | 36 |
| 2 | `youtube-andrej-karpathy` | @AndrejKarpathy | Andrej Karpathy | 17 |
| 2 | `youtube-statquest` | @statquest | StatQuest | 40 |
| 2 | `youtube-two-minute-papers` | @TwoMinutePapers | Two Minute Papers | 40 |
| 3 | `youtube-simon-willison` | @swillison | Simon Willison | 36 |
| 3 | `youtube-anthropic` | @anthropic-ai | Anthropic | 40 |
| 3 | `youtube-logan-kilpatrick` | @LoganKilpatrickYT | Logan Kilpatrick | 24 |
| 3 | `youtube-fireship` | @Fireship | Fireship | 40 |
| 4 | `youtube-openai` | @OpenAI | OpenAI | 40 |
| 4 | `youtube-google-deepmind` | @googledeepmind | Google DeepMind | 40 |
| 4 | `youtube-deeplearning-ai` | @Deeplearningai | DeepLearning.AI | 40 |
| 4 | `youtube-yann-lecun` | @YannLeCunPhD | Yann LeCun | 26 |
| 4 | `youtube-nvidia-developer` | @NVIDIADeveloper | NVIDIA Developer | 40 |
| 5 | `youtube-dwarkesh-patel` | @DwarkeshPatel | Dwarkesh Patel | 40 |
| 5 | `youtube-lex-fridman` | @lexfridman | Lex Fridman | 39 |
| 5 | `youtube-ai-explained` | @aiexplained-official | AI Explained | 37 |

L1 rarity: owning names (model press, maker feeds). L2 depth: the actual mechanism (3B1B level math talk). L3 credible: working-practitioner coverage + literature triage. L4 lab: the labs' own channels (OpenAI, DeepMind, Anthropic, NVIDIA, DeeplearningAI / LeCun). L5 bridge: thought-leader interviews that span tiers.

## Newsletter sources (indexed + full text)

| level | source | canonical URL | corpus |
|-------|--------|---------------|--------|
| L1 | `tldr-ai` | [TLDR AI](https://tldr.tech/ai) | `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/newsletters/tldr-ai` |
| L3 | `one-useful-thing` | [One Useful Thing](https://www.oneusefulthing.org) | `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/newsletters/one-useful-thing` |
| L4 | `the-batch` | [The Batch](https://www.deeplearning.ai/the-batch/) | `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/newsletters/the-batch` |

Refresh all three with `make youtube-newsletters`. Each source has an `index.json`, one cleaned article file per indexed issue, and a source-grounded digest under `youtube_intel/digests/<slug>_brief.md`.

Corpus root (worktree, git-tracked): `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus`
- YouTube catalog: `youtube_corpus/channels/<slug>/videos.json`
- YouTube transcripts: `youtube_corpus/channels/<slug>/transcripts/<id>.txt`
- newsletter catalog: `youtube_corpus/newsletters/<slug>/index.json`
- newsletter full text: `youtube_corpus/newsletters/<slug>/texts/<id>.txt`
- local verification: `python3 youtube_intel/scrape.py --stage health`
- heartbeat: `curl -s http://127.0.0.1:8793/health` → {"ok":true, "corpus_videos": N, "watched": 18}
- force one YouTube channel: `curl -s -XPOST http://127.0.0.1:8793/webhook/poll -d '{"channel":"<slug>"}'`
- force every YouTube channel: `curl -s -XPOST http://127.0.0.1:8793/webhook/poll`

