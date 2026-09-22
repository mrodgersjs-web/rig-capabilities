---
name: youtube-google-deepmind
description: Google DeepMind (@googledeepmind): L4 lab AI-stack channel (376-video corpus) with transcript-mining commands. Load before digging this channel's transcripts or quoting its frames.
when_to_use: mining @googledeepmind videos; quoting Google DeepMind as evidence for GTM/agent-engineering work; choosing what to absorb from lab/bridge/rarity tier (L4 lab)
version: 0.1.0
owner: rig
domain: youtube-corpus
status: draft
verified_by: rig-agent
verified_on: 2026-09-08
outcome: Load channel-scope context before mining the google-deepmind corpus or doing GTM/agent work informed by it.
done_when:
  - file:capabilities/skills/youtube-google-deepmind/index.json
  - grep:capabilities/skills/youtube-google-deepmind/SKILL.md:## Top videos
quality_floor: Digest sections complete; top-video table >= 10 rows; corpus paths verified to exist.
metadata:
  ladder_level: 4
  handle: @googledeepmind
  corpus_root: /Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus
hooks: []
---

# youtube-google-deepmind

Channel-scope context for the **@googledeepmind** YouTube corpus — L4 lab tier of the RIG 5-level AI stack.

## What this surface is
## @googledeepmind – digest

- **what it is**: Google DeepMind's public research-and-teaching pipeline — RL/deep-learning lecture series, world-model demos, and Gemini product engineering talks.
- **episode shape**: Bimodal — 90–150 min academic lecture blocks (UCL RL course, DL course) vs. 2–5 min product demo clips (Gemini Robotics 2) and 45–60 min keynotes.
- **recurring themes**:
  - David Silver's RL course as the canonical anchor (MDPs, policy gradient, actor-critic, exploration)
  - World models as unifying abstraction: Genie 3 (infinite environments), WeatherNext (forecasting)
  - Gemini as the agentic backbone — from Gemini 2.0 reasoning to Gemini Robotics 2 whole-body control
  - Unsupervised representation learning and embeddings as the bridge between vision and language
  - Uncertainty quantification elevated to a first-class design axis ("mathematics of AI uncertainty")
  - Multi-robot collaboration and dexterity as the near-physical frontier
- **signature frames**:
  - MDP/state-action-reward as the universal planning lens
  - "World model" as the single architecture question (Genie 3, WeatherNext)
  - Agentic AI = RL at scale with a language model as policy (Vinyals framing)
  - Exploration-exploitation tradeoff applied to product roadmap (capable now vs. capability ceiling)
  - Prediction before control (model-free → model-based → hybrid)
- **must-watch**:
  - "Genie 3: An infinite world model | Shlomi Fruchter and Jack Parker-Holder" — the world-model thesis in one 61-min talk
  - "Gemini 2.0 and the evolution of agentic AI | Oriol Vinyals" — connects classic RL to the current product stack
  - "DeepMind x UCL RL Lecture Series - Introduction to Reinforcement Learning [1/13]" — foundational MDP framing
  - "Reinforcement Learning 10: Classic Games Case Study" — grounds theory in AlphaGo/AlphaZero lineage
  - "The mathematics of AI uncertainty" — 45-min signal on where epistemic calibration is heading
- **mine-for**: The latency between UCL RL lectures (research) and Gemini Robotics 2 demo clips (product) is your "research-to-shipping" window — map which demo titles (whole-body control, multi-robot, dexterity) correspond to which lecture topics. Vinyals' agentic framing is the GTM narrative bridge: sell agents, not models. The robotics clips are the "agent-engineering surface" a technical reader should extract for go-to-market.

## Top videos (signal-sorted)
`ook46h2Jfb4`  150m  DeepMind x UCL RL Lecture Series - Function Approximation [7/13]  https://www.youtube.com/watch?v=ook46h2Jfb4 —
`aQJP3Z2Ho8U`  130m  DeepMind x UCL RL Lecture Series - Exploration & Control [2/13]  https://www.youtube.com/watch?v=aQJP3Z2Ho8U —
`kZ_AUmFcZtk`  111m  RL Course by David Silver - Lecture 10: Classic Games  https://www.youtube.com/watch?v=kZ_AUmFcZtk —
`ld28AU7DDB4`  110m  Reinforcement Learning 10: Classic Games Case Study  https://www.youtube.com/watch?v=ld28AU7DDB4 —
`Y95JwaynE40`  108m  Deep Learning 6: Deep Learning for NLP  https://www.youtube.com/watch?v=Y95JwaynE40 —
`eM6IBYVqXEA`  108m  Reinforcement Learning 2: Exploration and Exploitation  https://www.youtube.com/watch?v=eM6IBYVqXEA —
`Xrxrd8nl4YI`  107m  Reinforcement Learning 7: Planning and Models  https://www.youtube.com/watch?v=Xrxrd8nl4YI —
`JO0LwmIlWw0`  107m  Deep Learning 2: Introduction to TensorFlow  https://www.youtube.com/watch?v=JO0LwmIlWw0 —
`OfKnA91zs9I`  106m  Deep Learning 4: Beyond Image Recognition, End-to-End Learning, Embeddings  https://www.youtube.com/watch?v=OfKnA91zs9I —
`wAk1lxmiW4c`  105m  Reinforcement Learning 5: Function Approximation and Deep Reinforcement Learning  https://www.youtube.com/watch?v=wAk1lxmiW4c —
`f0s-uvvXvWg`  105m  DeepMind x UCL | Deep Learning Lectures | 10/12 |  Unsupervised Representation L  https://www.youtube.com/watch?v=f0s-uvvXvWg —
`5eAXoPSBgnE`  105m  Deep Learning 3: Neural Networks Foundations  https://www.youtube.com/watch?v=5eAXoPSBgnE —
`_6jZlnRsXXQ`  5m  WeatherNext 3: More accurate, timely, and local weather forecasts  https://www.youtube.com/watch?v=_6jZlnRsXXQ —
`tBjgCj_dGZM`  45m  The mathematics of AI uncertainty  https://www.youtube.com/watch?v=tBjgCj_dGZM —
`fo9WirRIaVs`  2m  Robots working together with Gemini Robotics 2  https://www.youtube.com/watch?v=fo9WirRIaVs —
`nBftSI5mmHA`  2m  Tasks that require whole-body control with Gemini Robotics 2  https://www.youtube.com/watch?v=nBftSI5mmHA —
`wYVHxw2-DP4`  2m  Tough dexterity tasks with Gemini Robotics 2  https://www.youtube.com/watch?v=wYVHxw2-DP4 —
`9MNLEAzA59o`  3m  Intelligent whole-body control with Gemini Robotics 2  https://www.youtube.com/watch?v=9MNLEAzA59o —
`CiTPDm7PKW0`  3m  Multi-robot collaboration with Gemini Robotics 2  https://www.youtube.com/watch?v=CiTPDm7PKW0 —
`O9-650iHAls`  2m  Advanced dexterity with Gemini Robotics 2  https://www.youtube.com/watch?v=O9-650iHAls —
`n5x6yXDj0uo`  61m  Genie 3: An infinite world model | Shlomi Fruchter and Jack Parker-Holder  https://www.youtube.com/watch?v=n5x6yXDj0uo —
`eaWfWoVUTEw`  102m  DeepMind x UCL RL Lecture Series - Model-free Prediction [5/13]  https://www.youtube.com/watch?v=eaWfWoVUTEw —
`t9uf9cuogBo`  101m  DeepMind x UCL RL Lecture Series - Model-free Control [6/13]  https://www.youtube.com/watch?v=t9uf9cuogBo —
`y3oqOjHilio`  99m  DeepMind x UCL RL Lecture Series - Policy-Gradient and Actor-Critic methods [9/1  https://www.youtube.com/watch?v=y3oqOjHilio —

## On-disk corpus
- transcripts: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/google-deepmind/transcripts/<id>.txt` (cleaned, one line per cue)
- stats: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/google-deepmind/transcripts.stats.json`

Useful moves:
```sh
G=/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/google-deepmind
# most substantive episodes
python3 -c "import json;d=json.load(open('$G/videos.json'));[print(v['id'],round((v.get('duration') or 0)/60),'m',v['title'][:70]) for v in sorted(d['videos'],key=lambda v:-(v.get('duration') or 0))[:12]]"
# grep a theme across transcripts
grep -ril "scaling" $G/transcripts/ | head -20
# open one transcript
cat $G/tran
```
Known gap: /videos tab only — Shorts: negligible.

## One-liner
> Google DeepMind
