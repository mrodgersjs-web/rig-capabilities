---
name: youtube-ai-ladder
description: Umbrella for the 18-channel 5-level AI YouTube corpus (rarity→depth→credible→lab→bridge) with webhook ingestion and per-channel skills. Load first to route to the right channel skill.
when_to_use: deciding which tier/channel to mine; setting up or touching the corpus/webhook; auditing coverage
version: 0.1.0
owner: rig
domain: youtube-corpus
status: draft
verified_by: rig-agent
verified_on: 2026-09-08
outcome: One-line-per-channel routing table plus wrist-verified corpus/webhook commands.
done_when: Routing table covers 18 channels; THREE corpus commands demonstrated (catalog read, stats read, transcript grep on TWO different channel skills).
quality_floor: All 18 child skills exist in capabilities/skills/.
metadata:
  corpus_root: /Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus
  webhook_port: 8793
hooks: []
---
# youtube-ai-ladder

RIG's five-level AI stack as 18 YouTube channels + a self-healing corpus.

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

Newsletters NOT in the corpus (manually skimmed): tldr.tech/ai, oneusefulthing.org, deeplearning.ai/the-batch.

Corpus root (worktree, git-tracked): `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus`
- catalog: `youtube_corpus/channels/<slug>/videos.json`
- transcripts: `youtube_corpus/channels/<slug>/transcripts/<id>.txt` (one line per cleaned cue)
- heartbeat: `curl -s http://127.0.0.1:8793/health` → {"ok":true, "corpus_videos": N, "watched": 18}
- force one: `curl -s -XPOST http://127.0.0.1:8793/poll?slug=<slug>`
- force everything: `curl -s -XPOST http://127.0.0.1:8793/poll`
(scratch output — point --target at the rig-capabilities repo to commit: `python3 /Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_intel/make_skills.py --target /Users/rig128gb/Developer/rig-capabilities/capabilities/skills` then `git -C /Users/rig128gb/Developer/rig-capabilities add capabilities/skills/youtube-* && git commit`)
