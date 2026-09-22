---
name: youtube-deeplearning-ai
description: DeepLearning.AI (@Deeplearningai): L4 lab AI-stack channel (576-video corpus) with transcript-mining commands. Load before digging this channel's transcripts or quoting its frames.
when_to_use: mining @Deeplearningai videos; quoting DeepLearning.AI as evidence for GTM/agent-engineering work; choosing what to absorb from lab/bridge/rarity tier (L4 lab)
version: 0.1.0
owner: rig
domain: youtube-corpus
status: draft
verified_by: rig-agent
verified_on: 2026-09-08
outcome: Load channel-scope context before mining the deeplearning-ai corpus or doing GTM/agent work informed by it.
done_when:
  - file:capabilities/skills/youtube-deeplearning-ai/index.json
  - grep:capabilities/skills/youtube-deeplearning-ai/SKILL.md:## Top videos
quality_floor: Digest sections complete; top-video table >= 10 rows; corpus paths verified to exist.
metadata:
  ladder_level: 4
  handle: @Deeplearningai
  corpus_root: /Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus
hooks: []
---

# youtube-deeplearning-ai

Channel-scope context for the **@Deeplearningai** YouTube corpus — L4 lab tier of the RIG 5-level AI stack.

## What this surface is
## DeepLearning.AI - digest

- **what it is**: Andrew Ng's org; applied-AI courses, AI Dev conference talks (NYC/SF), and short-form clips — the practitioner-mid layer of the AI stack.
- **episode shape**: Long-form course lectures (12–149 min), AI Dev conference sessions (19–92 min), and 2–6 min promo/clips; conference talks dominate the signal.
- **recurring themes**:
  - Agent memory & context engineering (LangGraph, MemGPT, Oracle AI Database)
  - Coding agents and LLM code quality at enterprise scale
  - Serverless inference & cost optimization (Bedrock, AMD GPUs via Lamini, DeepSeek reasoning)
  - Accuracy/cost/latency tradeoffs in production agents; red-team LLM apps
  - Knowledge graphs for agent grounding; agent discovery
  - AI velocity costs — the hidden tax on teams adopting agents fast
- **signature frames**:
  - Ng's Five Levels of AI (this channel = Level 4, "Narrow AI / Generative")
  - LLMs as Operating Systems (MemGPT framing)
  - "Context Engineering" as the successor to prompt engineering
  - Agent-as-daemon: coding agent calls the developer (from short-form clips)
  - "AI Dev" as a counterweight to research-only conferences — practitioner signal
- **must-watch**:
  - "AI Dev 25 | Harrison Chase: Long Term Memory with LangGraph" — the reference architecture for agent memory in production
  - "AI Dev 26 x SF | Or Dagan: Optimizing Accuracy, Cost, and Latency in Real-World Agents" — the ops cost model every team needs
  - "AI Dev 26 x SF | Tom Howlett: Can LLMs Generate Enterprise Quality Code?" — GTM-signal: when to trust vs. gate LLM output
  - "AI Dev 26 x SF | Barun Singh & Kennith Jackson; The Hidden Cost of AI Velocity and AI Agents" — the counter-argument that resists adoptions
  - "Full AI Prompting Course with Andrew Ng" — the baseline mental model everything else builds on
- **mine-for**: Agent-engineering patterns that have survived conference iterations (2025→2026); the shift from "prompt" to "context engineering" + memory systems; cost/latency as first-class constraints, not afterthoughts. The short clips reveal a new GTM narrative: the agent as a teammate that pings you, not a black box — that's the sales story.

## Top videos (signal-sorted)
`8ib4Qnh2HFE`  149m  Full AI Prompting Course with Andrew Ng  https://www.youtube.com/watch?v=8ib4Qnh2HFE —
`R0OdB-p-ns4`  92m  AI Dev 25 | Harrison Chase: Long Term Memory with LangGraph  https://www.youtube.com/watch?v=R0OdB-p-ns4 —
`fHz6s0YmNFo`  88m  AI Dev 25 | Justin Uberti: Introduction to the OpenAI Realtime API  https://www.youtube.com/watch?v=fHz6s0YmNFo —
`AMsmgJlVhmg`  87m  AI Dev 25 | João Moura & Graham Steele: Real AI Agents in Action Automate, Adap  https://www.youtube.com/watch?v=AMsmgJlVhmg —
`8yHVfM_E39w`  64m  AI Dev 25 | Mike Chambers: Serverless Agentic Workflows with Amazon Bedrock  https://www.youtube.com/watch?v=8yHVfM_E39w —
`omGyNyMNeGM`  60m  🎧 LoFi Beats for Coding & Focus: Calm Beats to Study, Build, and Think  https://www.youtube.com/watch?v=omGyNyMNeGM —
`MohMkvTRjjA`  58m  AI Dev 25 | Sharon Zhou & Mahdi Ghodsi: Run Deepseek Reasoning and Finetuning on  https://www.youtube.com/watch?v=MohMkvTRjjA —
`-B0zaWoPEFs`  55m  AI Dev 26 x SF | Panel Discussion: Future of Software Engineering  https://www.youtube.com/watch?v=-B0zaWoPEFs —
`qEUxIvaIgsg`  51m  AI Dev 26 x SF | Eli Schilling: Hands On Agent Context & Memory Engineering with  https://www.youtube.com/watch?v=qEUxIvaIgsg —
`bttcJn58J24`  50m  AI Dev 25 x NYC | Panel Discussion: Software Development in the Age of AI  https://www.youtube.com/watch?v=bttcJn58J24 —
`H343JRrncfc`  47m  Heroes of NLP: Chris Manning  https://www.youtube.com/watch?v=H343JRrncfc —
`chs2Xx4JbBs`  43m  AI Dev 26 x SF | Paige Bailey: What's New and What's Next in AI  https://www.youtube.com/watch?v=chs2Xx4JbBs —
`Y_bxMqcCNbU`  4m  AI Dev | San Francisco 2026 | 2,599 AI Developers  https://www.youtube.com/watch?v=Y_bxMqcCNbU —
`MbB1gNIj3G0`  2m  Your coding agent keeps solving the same problem  https://www.youtube.com/watch?v=MbB1gNIj3G0 —
`xUXJuPC7gz0`  2m  Take back control of your AI coding workflow  https://www.youtube.com/watch?v=xUXJuPC7gz0 —
`Z4PB98qZBRU`  2m  3rd Place Winner: Voice AI Prevents Data Loss. Coding Agent Calls Developer Befo  https://www.youtube.com/watch?v=Z4PB98qZBRU —
`BHdin6bLGKQ`  5m  2nd Place Winner: Coding Agent Calls Developer to Pitch Launch Strategy  https://www.youtube.com/watch?v=BHdin6bLGKQ —
`7ZOjMnbxJYE`  6m  1st Place Winner: Coding Agent Calls Developer to Resolve Code Block  https://www.youtube.com/watch?v=7ZOjMnbxJYE —
`zBjdLgvZWag`  2m  AI writes your code. Who reviews it?  https://www.youtube.com/watch?v=zBjdLgvZWag —
`a9V1XgFOa5I`  2m  Fast inference changes what you can build  https://www.youtube.com/watch?v=a9V1XgFOa5I —
`QVawxdMRZtk`  34m  AI Dev 26 x SF | Eda Zhou & Mahdi Ghodsi: Building Personal AI Agents with Open   https://www.youtube.com/watch?v=QVawxdMRZtk —
`RQ5HzSAx27I`  3m  LLMs as Operating Systems: Agent Memory, a new course based on the MemGPT approa  https://www.youtube.com/watch?v=RQ5HzSAx27I —
`8tg8z-Fi0MU`  32m  AI Dev 25 x NYC | Tanveer Mittal, Utkarsh Lamba: Building with the Claude Agent   https://www.youtube.com/watch?v=8tg8z-Fi0MU —
`bDIB8jrNhHc`  26m  AI Dev 26 x SF | Ankit Mathur: The Coding Agent Multiverse of Madness  https://www.youtube.com/watch?v=bDIB8jrNhHc —

## On-disk corpus
- transcripts: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/deeplearning-ai/transcripts/<id>.txt` (cleaned, one line per cue)
- stats: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/deeplearning-ai/transcripts.stats.json`

Useful moves:
```sh
G=/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/deeplearning-ai
# most substantive episodes
python3 -c "import json;d=json.load(open('$G/videos.json'));[print(v['id'],round((v.get('duration') or 0)/60),'m',v['title'][:70]) for v in sorted(d['videos'],key=lambda v:-(v.get('duration') or 0))[:12]]"
# grep a theme across transcripts
grep -ril "scaling" $G/transcripts/ | head -20
# open one transcript
cat $G/tran
```
Known gap: /videos tab only — Shorts: negligible.

## One-liner
> DeepLearning.AI
