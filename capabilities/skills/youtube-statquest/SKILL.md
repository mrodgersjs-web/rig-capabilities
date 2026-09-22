---
name: youtube-statquest
description: StatQuest (@statquest): L2 depth AI-stack channel (264-video corpus) with transcript-mining commands. Load before digging this channel's transcripts or quoting its frames.
when_to_use: mining @statquest videos; quoting StatQuest as evidence for GTM/agent-engineering work; choosing what to absorb from lab/bridge/rarity tier (L2 depth)
version: 0.1.0
owner: rig
domain: youtube-corpus
status: draft
verified_by: rig-agent
verified_on: 2026-09-08
outcome: Load channel-scope context before mining the statquest corpus or doing GTM/agent work informed by it.
done_when:
  - file:capabilities/skills/youtube-statquest/index.json
  - grep:capabilities/skills/youtube-statquest/SKILL.md:## Top videos
quality_floor: Digest sections complete; top-video table >= 10 rows; corpus paths verified to exist.
metadata:
  ladder_level: 2
  handle: @statquest
  corpus_root: /Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus
hooks: []
---

# youtube-statquest

Channel-scope context for the **@statquest** YouTube corpus — L2 depth tier of the RIG 5-level AI stack.

## What this surface is
## STATQUEST - digest
- **what it is**: Josh Starmer's channel turning stats/ML into "Clearly Explained" visual-oral lessons for builders, students, and prac
- **episode shape**: Two-tier structure — "Main Ideas" explainer → "Mathematical Details" deep-dive; interspersed with interview series (Human Stories in AI, AI Buzz) and hands-on Python code-alongs
- **recurring themes**:
  - Linear models as the unifying backbone (t-tests, ANOVA, regression, design matrices)
  - Transformer architecture decomposed step-by-step (encoder-only, decoder-only, attention, matrix math)
  - Gradient boosting family (XGBoost, random forests, missing data handling)
  - Optimization fundamentals (simplex, SGD, linear programming)
  - Dimensionality reduction (UMAP) and evaluation metrics (FDR, QQ plots, quantiles)
  - Industry-context curation via AI Buzz and Human Stories interviews (ChatGPT, Matics, alignment)
- **signature frames**:
  - "Main Ideas → Mathematical Details" split (separate pitch from proof)
  - Design matrix as the single frame for every linear model
  - "Super Simple Terms" entry ramp before technical ascent
  - Pop! quick-hit analogies (4-6 min mental models)
  - "Start to Finish" code-along as a runnable task chain
- **must-watch**:
  - *The Essence of Linear Regression!!!* — the design-matrix frame that reorganizes every downstream test
  - *The matrix math behind transformer neural networks, one step at a time!!!* — best public decomposition for agent-engineering readers
  - *The Simplex Algorithm, Mathematical Details!!!* — constraint-satisfaction thinking reusable beyond LP
  - *XGBoost in Python from Start to Finish* — compact reference for the boosting task pattern
  - *Decoder-Only Transformers, ChatGPT's specific Transformer, Clearly Explained!!!* — isolates the architecture actually in production
- **mine-for**: The "Main Ideas / Math Details" split is a ready-made GTM artifact pattern (concept pitch vs. technical proof). Design-matrix unification is useful for agents that must dispatch across t-test, ANOVA, and regression without branching. AI Buzz episodes provide citable industry-voice context (alignment, RAG, startup framing) without relying on transcript depth.

## Top videos (signal-sorted)
`Y5tyrAxhmUc`  74m  The Elements of StatQuest (Webinar)  https://www.youtube.com/watch?v=Y5tyrAxhmUc —
`q90UDEgYqeI`  66m  Classification Trees in Python from Start to Finish  https://www.youtube.com/watch?v=q90UDEgYqeI —
`GrJP9FLV3FE`  57m  XGBoost in Python from Start to Finish  https://www.youtube.com/watch?v=GrJP9FLV3FE —
`wIGOnM6Cf_E`  55m  Human Stories in AI: Abbas Merchant@Matics Analytics  https://www.youtube.com/watch?v=wIGOnM6Cf_E —
`8A7L0GsBiLQ`  45m  Support Vector Machines in Python from Start to Finish.  https://www.youtube.com/watch?v=8A7L0GsBiLQ —
`k3b9Mvtt6lU`  38m  The AI Buzz, Episode #1: ChatGPT, Transformers and Attention  https://www.youtube.com/watch?v=k3b9Mvtt6lU —
`Oekl7K1iwxY`  37m  Human Stories in AI: Simon Stochholm  https://www.youtube.com/watch?v=Oekl7K1iwxY —
`StWY5QWMXCw`  37m  Gradient Boost Part 4 (of 4): Classification Details  https://www.youtube.com/watch?v=StWY5QWMXCw —
`JV0S5f89-Q4`  37m  Human Stories in AI: Tommy Tang  https://www.youtube.com/watch?v=JV0S5f89-Q4 —
`1xBB8iAXxds`  37m  The AI Buzz, Episode #2: Big data, Reinforcement Learning and Aligning Models  https://www.youtube.com/watch?v=1xBB8iAXxds —
`bQ5BoolX9Ag`  37m  Decoder-Only Transformers, ChatGPTs specific Transformer, Clearly Explained!!!  https://www.youtube.com/watch?v=bQ5BoolX9Ag —
`zxQyTK8quyY`  36m  Transformer Neural Networks, ChatGPT's foundation, Clearly Explained!!!  https://www.youtube.com/watch?v=zxQyTK8quyY —
`UwbASFlIS7A`  4m  Another three (3) more lessons from my Pop!  https://www.youtube.com/watch?v=UwbASFlIS7A —
`lgD9lNB9Ums`  27m  The Simplex Algorithm, Mathematical Details!!!  https://www.youtube.com/watch?v=lgD9lNB9Ums —
`h5o1n1QMcmM`  24m  Optimization with Linear Programming (and the Simplex Algorithm), Main Ideas!!!  https://www.youtube.com/watch?v=h5o1n1QMcmM —
`mIlw5j3WyVk`  11m  StatQuest: Random Forests Part 2: Missing data and clustering  https://www.youtube.com/watch?v=mIlw5j3WyVk —
`L3nlGfSyHV0`  18m  False Discovery Rates, FDR, clearly explained  https://www.youtube.com/watch?v=L3nlGfSyHV0 —
`aFDOzpTeg0s`  32m  The Essence of Linear Regression!!!  https://www.youtube.com/watch?v=aFDOzpTeg0s —
`q-BiW5srMFQ`  23m  How AI works in Super Simple Terms!!!  https://www.youtube.com/watch?v=q-BiW5srMFQ —
`WRYk7oZiogg`  6m  StatQuest: Career Advice from Tech Industry Leaders  https://www.youtube.com/watch?v=WRYk7oZiogg —
`C9QSpl5nmrY`  31m  Coding a ChatGPT Like Transformer From Scratch in PyTorch  https://www.youtube.com/watch?v=C9QSpl5nmrY —
`tc4LGTVRXV8`  35m  The AI Buzz, Episode #4: ChatGPT + Bing and How to start an AI company in 3 easy  https://www.youtube.com/watch?v=tc4LGTVRXV8 —
`KphmOJnLAdI`  24m  The matrix math behind transformer neural networks, one step at a time!!!  https://www.youtube.com/watch?v=KphmOJnLAdI —
`GDN649X_acE`  19m  Encoder-Only Transformers (like BERT) for RAG, Clearly Explained!!!  https://www.youtube.com/watch?v=GDN649X_acE —

## On-disk corpus
- transcripts: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/statquest/transcripts/<id>.txt` (cleaned, one line per cue)
- stats: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/statquest/transcripts.stats.json`

Useful moves:
```sh
G=/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/statquest
# most substantive episodes
python3 -c "import json;d=json.load(open('$G/videos.json'));[print(v['id'],round((v.get('duration') or 0)/60),'m',v['title'][:70]) for v in sorted(d['videos'],key=lambda v:-(v.get('duration') or 0))[:12]]"
# grep a theme across transcripts
grep -ril "scaling" $G/transcripts/ | head -20
# open one transcript
cat $G/tran
```
Known gap: /videos tab only — Shorts: negligible.

## One-liner
> StatQuest
