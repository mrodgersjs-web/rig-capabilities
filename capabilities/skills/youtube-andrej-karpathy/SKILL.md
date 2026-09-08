---
name: youtube-andrej-karpathy
description: Andrej Karpathy (@AndrejKarpathy): L2 depth AI-stack channel (17-video corpus) with transcript-mining commands. Load before digging this channel's transcripts or quoting its frames.
when_to_use: mining @AndrejKarpathy videos; quoting Andrej Karpathy as evidence for GTM/agent-engineering work; choosing what to absorb from lab/bridge/rarity tier (L2 depth)
version: 0.1.0
owner: rig
domain: youtube-corpus
status: draft
verified_by: rig-agent
verified_on: 2026-09-08
outcome: Load channel-scope context before mining the andrej-karpathy corpus or doing GTM/agent work informed by it.
done_when: >
  Digest + top-video index read from the skill body; grep/locate commands
  demonstrated against the on-disk corpus for at least one landmark video.
great_example: youtube_intel/digests/andrej-karpathy_brief.md (this repo, quarantine-rooted)
quality_floor: Digest sections complete; top-video table >= 10 rows; corpus paths verified to exist.
metadata:
  ladder_level: 2
  handle: @AndrejKarpathy
  corpus_root: /Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus
hooks: []
---

# youtube-andrej-karpathy

Channel-scope context for the **@AndrejKarpathy** YouTube corpus — L2 depth tier of the RIG 5-level AI stack.

## What this surface is
## @AndrejKarpathy - digest
- **what it is**: "Let's build X from scratch" AI code-walkthrough channel; reimplementation of major models (GPT, makemore, micrograd) with live narration.
- **episode shape**: 1–4 hr live-coding sessions and talks; recent longer deep-dives on LLM architecture; older short Stable Diffusion art experiments.
- **recurring themes**:
  - Reimplementation-as-pedagogy: GPT-2, tokenizer, makemore, micrograd — each a standalone minimal-code project
  - LLM internal mechanics: attention, context windows, instructor tokens, multi-token prediction
  - Backprop from first principles (autograd, gradient flow, batchnorm)
  - Tokenizer as the critical abstraction between raw text and model input
  - Practical LLM usage: prompting patterns, fine-tuning vs RAG, model selection
- **signature frames**:
  - "Let's build X" — from-scratch reimplementation as the teaching unit
  - makemore → nanoGPT → GPT-2 progression (char-level → word-level → full transformer)
  - "Spelled out" — every line narrated, zero magic
  - "Backprop ninja" — the micrograd gradient-fill-er walkthrough
  - "Instructor tokens" frame from the LLM deep dive (system prompts as learned ensembles)
- **must-watch**:
  - "Let's reproduce GPT-2 (124M)" — the definitive end-to-end GPT-2 reimplementation
  - "Deep Dive into LLMs like ChatGPT" — best single source on what vendors hide (context mgmt, training pipeline)
  - "The spelled-out intro to neural networks and backpropagation: building micrograd" — canonical backprop explanation
  - "Let's build GPT: from scratch, in code, spelled out." — the nanoGPT foundation everyone forks
  - "How I use LLMs" — compact usage-patterns reference, high signal-to-noise
- **mine-for**: The makemore→nanoGPT→GPT-2 progression maps directly onto agent-engineering primitives (tokenization, context-management, training loops). For GTM: the LLM deep dive is the single best source on instructor tokens, multi-turn context, and what's actually under the hood. "How I use LLMs" is a compact vendor-agnostic usage-patterns reference.

## Top videos (signal-sorted)
`l8pRSuU81PU`  241m  Let's reproduce GPT-2 (124M)  https://www.youtube.com/watch?v=l8pRSuU81PU — 
`7xTGNNLPyMI`  211m  Deep Dive into LLMs like ChatGPT  https://www.youtube.com/watch?v=7xTGNNLPyMI — 
`VMj-3S1tku0`  146m  The spelled-out intro to neural networks and backpropagation: building micrograd  https://www.youtube.com/watch?v=VMj-3S1tku0 — 
`zduSFxRajkE`  134m  Let's build the GPT Tokenizer  https://www.youtube.com/watch?v=zduSFxRajkE — 
`EWvNQjAaOHw`  131m  How I use LLMs  https://www.youtube.com/watch?v=EWvNQjAaOHw — 
`PaCmpygFfXo`  118m  The spelled-out intro to language modeling: building makemore  https://www.youtube.com/watch?v=PaCmpygFfXo — 
`kCc8FmEb1nY`  116m  Let's build GPT: from scratch, in code, spelled out.  https://www.youtube.com/watch?v=kCc8FmEb1nY — 
`P6sfmUTpUmc`  116m  Building makemore Part 3: Activations & Gradients, BatchNorm  https://www.youtube.com/watch?v=P6sfmUTpUmc — 
`q8SA3rM6ckI`  115m  Building makemore Part 4: Becoming a Backprop Ninja  https://www.youtube.com/watch?v=q8SA3rM6ckI — 
`TCH_1BHY58I`  76m  Building makemore Part 2: MLP  https://www.youtube.com/watch?v=TCH_1BHY58I — 
`zjkBMFhNj_g`  60m  [1hr Talk] Intro to Large Language Models  https://www.youtube.com/watch?v=zjkBMFhNj_g — 
`t3YJ5hKiMQ0`  56m  Building makemore Part 5: Building a WaveNet  https://www.youtube.com/watch?v=t3YJ5hKiMQ0 — 
`2oKjtvYslMY`  19m  Stable diffusion dreams of steampunk brains  https://www.youtube.com/watch?v=2oKjtvYslMY — 
`vEnetcj_728`  5m  Stable diffusion dreams of "blueberry spaghetti" for one night  https://www.youtube.com/watch?v=vEnetcj_728 — 
`kVpDARqZdrQ`  4m  Stable diffusion dreams of psychedelic faces  https://www.youtube.com/watch?v=kVpDARqZdrQ — 
`Jv1ayv-04H4`  3m  Stable diffusion dreams of steam punk neural networks  https://www.youtube.com/watch?v=Jv1ayv-04H4 — 
`sM9bozW295Q`  2m  Stable diffusion dreams of tattoos  https://www.youtube.com/watch?v=sM9bozW295Q — 

## On-disk corpus
- transcripts: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/andrej-karpathy/transcripts/<id>.txt` (cleaned, one line per cue)
- stats: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/andrej-karpathy/transcripts.stats.json`

Useful moves:
```sh
G=/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/andrej-karpathy
# most substantive episodes
python3 -c "import json;d=json.load(open('$G/videos.json'));[print(v['id'],round((v.get('duration') or 0)/60),'m',v['title'][:70]) for v in sorted(d['videos'],key=lambda v:-(v.get('duration') or 0))[:12]]"
# grep a theme across transcripts
grep -ril "scaling" $G/transcripts/ | head -20
# open one transcript
cat $G/transcripts/l8pRSuU81PU.txt
```
Known gap: /videos tab only — Shorts: Shorts-heavy, few/indexed.

## One-liner
> Andrej Karpathy
