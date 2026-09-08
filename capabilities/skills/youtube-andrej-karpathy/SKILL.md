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
## @AndrejKarpathy — digest

- **what it is**: Deep-dive screencast lectures and coding walkthroughs that demystify neural nets, LLMs, and generative models by building them from scratch in code.
- **episode shape**: 1–4 hr single-speaker coding-along sessions with incremental builds (micrograd → makemore → GPT → GPT-2 124M), plus short Stable Diffusion art experiments.
- **recurring themes**:
  - Backpropagation mechanics made explicit (micrograd, makemore Parts 3–4)
  - GPT architecture end-to-end: tokenizer → transformer → 124M reproduction
  - Language modeling as next-token prediction (makemore series)
  - "Spelled-out" pedagogy as the anti-mystery contract for LLM capability
  - Training dynamics: activations, BatchNorm, gradient flow, learning-rate schedules
  - Stable Diffusion as creative texture generator (short experiments, not core)
- **signature frames**:
  - "Spelled out" — no hidden steps; every line justified, the channel's pedagogical contract
  - ~100-line from-scratch build as the litmus test for real understanding
  - Adder/softmax-as-weighted-average framing for attention (from the LLM deep dive)
  - LLM as "amnesiac engineer who read everything" — reframing hallucination as a constraint, not a bug
  - "You can reproduce GPT-2 124M on one GPU" as a barrier-busting claim
- **must-watch**:
  - *Deep Dive into LLMs like ChatGPT* — the single best conceptual map of pretrain → SFT → RLHF pipeline
  - *Let's reproduce GPT-2 (124M)* — proves the smallest real GPT-2 is reproducible; critical for agent-cost reasoning
  - *Let's build GPT: from scratch, in code, spelled out* — canonical ~200-line GPT reference; shapes how engineers reason about transformers
  - *The spelled-out intro to neural networks and backpropagation: building micrograd* — the 24-line autograd engine underpinning everything downstream
  - *How I use LLMs* — practitioner workflow patterns that predate the agent-framework era
- **mine-for**: Tokenizer internals (where inference cost actually lives), the 124M baseline as cheapest honest grounding for agent systems, and the SFT/RLHF breakdown that maps directly to fine-tune-vs-prompt GTM decisions. "How I use LLMs" surfaces prompt-chaining patterns that still inform agent architectures.

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
