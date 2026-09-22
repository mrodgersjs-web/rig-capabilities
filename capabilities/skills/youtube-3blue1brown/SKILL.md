---
name: youtube-3blue1brown
description: 3Blue1Brown (@3blue1brown): L2 depth AI-stack channel (151-video corpus) with transcript-mining commands. Load before digging this channel's transcripts or quoting its frames.
when_to_use: mining @3blue1brown videos; quoting 3Blue1Brown as evidence for GTM/agent-engineering work; choosing what to absorb from lab/bridge/rarity tier (L2 depth)
version: 0.1.0
owner: rig
domain: youtube-corpus
status: draft
verified_by: rig-agent
verified_on: 2026-09-08
outcome: Load channel-scope context before mining the 3blue1brown corpus or doing GTM/agent work informed by it.
done_when:
  - file:capabilities/skills/youtube-3blue1brown/index.json
  - grep:capabilities/skills/youtube-3blue1brown/SKILL.md:## Top videos
quality_floor: Digest sections complete; top-video table >= 10 rows; corpus paths verified to exist.
metadata:
  ladder_level: 2
  handle: @3blue1brown
  corpus_root: /Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus
hooks: []
---

# youtube-3blue1brown

Channel-scope context for the **@3blue1brown** YouTube corpus — L2 depth tier of the RIG 5-level AI stack.

## What this surface is
## 3Blue1Brown - digest
- **what it is**: Grant Sanderson's channel that reduces advanced math and CS concepts to geometric intuition via custom Manim animations, the de-facto reference for "why this works" before "how to compute it."
- **episode shape**: Single-object deep dives (10–60 min) structured as a narrative arc: naive picture → formal definition → surprising consequence, one canonical idea per video.
- **recurring themes**:
  - Fourier/signal decomposition as a universal lens (Laplace transforms, logarithms of images, phase changes)
  - Neural network geometry (gradient descent as surface walking, backprop as chain-rule unfolding, attention as weighted projection)
  - Information → intelligence (entropy, cross-entropy, compression as Bayesian inference)
  - Linear algebra as pure geometry (vectors, rotation matrices, eigenvalues as invariant structure)
  - Quantum superposition and Grover's search as amplitude interference
  - Manim itself as a reusable explainability substrate
- **signature frames**:
  - Geometric-first: every abstract object gets a spatial picture before notation
  - "Surface" metaphor: loss landscapes as 3-D terrain the optimizer walks
  - Signal/frequency decomposition as the master lens across physics, ML, and math
  - Atomic decomposition: one idea, one video, no cross-referencing required
  - "Why before what" narrative gating (motivation precedes formalism)
- **must-watch**:
  - "But what is quantum computing? (Grover's Algorithm)" — the cleanest single-video explainer of amplitude interference and speedup logic; transfers directly to analog-computing arguments.
  - "But what is cross-entropy? | Compression is Intelligence Part 2" — the bridge from Shannon to Bayesian model selection in one sitting; the frame for agent-evaluation metric design.
  - "Attention in transformers, step-by-step | Deep Learning Chapter 6" — the canonical geometric decomposition of Q/K/V; the reference for any "what does attention actually compute" discussion.
  - "Reinventing Entropy | Compression is Intelligence Part 1" — the foundational framing that entropy = expected code length; prerequisite for the entire compression-is-intelligence arc.
  - "How (and why) to take a logarithm of an image" — rare non-ML entry: applies Fourier-domain thinking to pixel data; good transfer-analogy for signal-to-agent mappings.
- **mine-for**: Extract (1) the compression-as-universal-lens frame (entropy → cross-entropy → variational inference → agent grounding), (2) attention-as-geometric-projection as a transferable mental model for retrieval-augmented systems, (3) the Manim source code itself as a template for agent-generated explanatory artifacts. Grounding: the "Compression is Intelligence" pair positions the entire stack as a compression problem, which maps cleanly onto GTM for "the model is a lossy compressor of its context."

## Top videos (signal-sorted)
`fsLh-NYhOoU`  60m  The most beautiful formula not enough people understand  https://www.youtube.com/watch?v=fsLh-NYhOoU —
`rbu7Zu5X1zI`  54m  How I animate 3Blue1Brown | A Manim demo with Ben Sparks  https://www.youtube.com/watch?v=rbu7Zu5X1zI —
`_BrFKp-U8GI`  52m  Exploration & Epiphany | Guest video by Paul Dancstep  https://www.youtube.com/watch?v=_BrFKp-U8GI —
`EmKQsSDlaa4`  46m  How are holograms possible?  https://www.youtube.com/watch?v=EmKQsSDlaa4 —
`ldxFjLJ3rVY`  45m  How (and why) to take a logarithm of an image  https://www.youtube.com/watch?v=ldxFjLJ3rVY —
`itRV2jEtV8Q`  41m  Simulating and understanding phase change | Guest video by Vilas Winstein  https://www.youtube.com/watch?v=itRV2jEtV8Q —
`ltLUadnCyi0`  40m  A tale of two problem solvers | Average cube shadow area  https://www.youtube.com/watch?v=ltLUadnCyi0 —
`iv-5mZ_9CPY`  37m  But how do AI images and videos actually work? | Guest video by Welch Labs  https://www.youtube.com/watch?v=iv-5mZ_9CPY —
`RQWpF2Gb-gU`  37m  But what is quantum computing?  (Grover's Algorithm)  https://www.youtube.com/watch?v=RQWpF2Gb-gU —
`j0wJBEZdwLs`  35m  But what is a Laplace Transform?  https://www.youtube.com/watch?v=j0wJBEZdwLs —
`bOXCLR3Wric`  35m  Olympiad level counting  (Generating functions)  https://www.youtube.com/watch?v=bOXCLR3Wric —
`GlYgs6v2YfU`  34m  But what is cross-entropy? | Compression is Intelligence Part 2  https://www.youtube.com/watch?v=GlYgs6v2YfU —
`l6DKRf-fAAM`  32m  Reinventing Entropy | Compression is Intelligence Part 1  https://www.youtube.com/watch?v=l6DKRf-fAAM —
`BHdbsHFs2P0`  30m  Why you can't comb a hairy ball, and why we care  https://www.youtube.com/watch?v=BHdbsHFs2P0 —
`FE-hM1kRK4Y`  23m  Why Laplace transforms are so useful  https://www.youtube.com/watch?v=FE-hM1kRK4Y —
`-j8PzkZ70Lg`  28m  The Physics of Euler's Formula | Laplace Transform Prelude  https://www.youtube.com/watch?v=-j8PzkZ70Lg —
`wjZofJX0v4M`  27m  Transformers, the tech behind LLMs | Deep Learning Chapter 5  https://www.youtube.com/watch?v=wjZofJX0v4M —
`eMlx5fFNoYc`  26m  Attention in transformers, step-by-step | Deep Learning Chapter 6  https://www.youtube.com/watch?v=eMlx5fFNoYc —
`ojjzXyQCzso`  24m  Make math videos! | Summer of Math Exposition announcement  https://www.youtube.com/watch?v=ojjzXyQCzso —
`9-Jl0dxWQs8`  23m  How might LLMs store facts | Deep Learning Chapter 7  https://www.youtube.com/watch?v=9-Jl0dxWQs8 —
`MzRCDLre1b4`  22m  Some light quantum mechanics (with minutephysics)  https://www.youtube.com/watch?v=MzRCDLre1b4 —
`6a1fLEToyvU`  22m  25 Math explainers you may enjoy | SoME3 results  https://www.youtube.com/watch?v=6a1fLEToyvU —
`IHZwWFHWa-w`  21m  Gradient descent, how neural networks learn | Deep Learning Chapter 2  https://www.youtube.com/watch?v=IHZwWFHWa-w —
`VYQVlVoWoPY`  19m  How to lie using visual proofs  https://www.youtube.com/watch?v=VYQVlVoWoPY —

## On-disk corpus
- transcripts: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/3blue1brown/transcripts/<id>.txt` (cleaned, one line per cue)
- stats: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/3blue1brown/transcripts.stats.json`

Useful moves:
```sh
G=/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/3blue1brown
# most substantive episodes
python3 -c "import json;d=json.load(open('$G/videos.json'));[print(v['id'],round((v.get('duration') or 0)/60),'m',v['title'][:70]) for v in sorted(d['videos'],key=lambda v:-(v.get('duration') or 0))[:12]]"
# grep a theme across transcripts
grep -ril "scaling" $G/transcripts/ | head -20
# open one transcript
cat $G/tran
```
Known gap: /videos tab only — Shorts: negligible.

## One-liner
> 3Blue1Brown
