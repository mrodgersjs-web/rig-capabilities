---
name: youtube-yann-lecun
description: Yann LeCun (@YannLeCunPhD): L4 lab AI-stack channel (26-video corpus) with transcript-mining commands. Load before digging this channel's transcripts or quoting its frames.
when_to_use: mining @YannLeCunPhD videos; quoting Yann LeCun as evidence for GTM/agent-engineering work; choosing what to absorb from lab/bridge/rarity tier (L4 lab)
version: 0.1.0
owner: rig
domain: youtube-corpus
status: draft
verified_by: rig-agent
verified_on: 2026-09-08
outcome: Load channel-scope context before mining the yann-lecun corpus or doing GTM/agent work informed by it.
done_when: >
  Digest + top-video index read from the skill body; grep/locate commands
  demonstrated against the on-disk corpus for at least one landmark video.
great_example: youtube_intel/digests/yann-lecun_brief.md (this repo, quarantine-rooted)
quality_floor: Digest sections complete; top-video table >= 10 rows; corpus paths verified to exist.
metadata:
  ladder_level: 4
  handle: @YannLeCunPhD
  corpus_root: /Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus
hooks: []
---

# youtube-yann-lecun

Channel-scope context for the **@YannLeCunPhD** YouTube corpus — L4 lab tier of the RIG 5-level AI stack.

## What this surface is
## @YannLeCunPhD - digest

- **what it is**: Archive of Yann LeCun's talks, demos, and historical research clips (conv-nets, LAGR, JEPA-era vision)
- **episode shape**: Heterogeneous — flagship hour-long talks, 1–3 min raw demo clips, 14-min lecture fragments; no consistent cadence
- **recurring themes**:
  - Convolutional networks from LeNet-5 (1989) through modern pedestrian detection and semantic segmentation demos
  - LAGR (Learning a General Representation) — off-road robot navigation via conv-net feature extraction + metric learning
  - Siamese network embeddings (DrLIM, 2006) as the bridge to contrastive representation learning
  - JEPA / energy-based worldview: predict in latent representation space, avoid pixel-space generation
  - The 6-layer autonomous-machine-intelligence stack (perceiver → world model → cost → predictor → planner → actor)
  - Recurring critique of generative models and attention-only scaling as insufficient for autonomous understanding
- **signature frames**:
  - JEPA test: "can you predict the embedding of a future view, not the pixels?"
  - Energy-based vs. distributional: a good model should lower energy on compatible (x, y) pairs, not just assign high joint probability
  - World-model gap: most learned representations invertible in principle; LeCun wants deliberately *lossy* abstractions
  - Hamiltonian/lagrangian lens: neural energy as a physical potential, gradients as force fields
  - "Perception is easy, understanding is hard" — the core claim that drives the whole autonomous-AI pitch
- **must-watch**:
  - "Yann LeCun: A Path Towards Autonomous AI", Baidu 2022-02-22 — the canonical statement of his post-$1B-Transformer thesis
  - "Q&A sessions for A Path Towards Autonomous AI" — stress-tests and clarifications with Q&A pressure
  - "Convolutional Network Demo from 1989 [restored version]" — origin artifact; shows what "deep learning" looked like pre-backprop-training
  - "DrLIM: learning an embedding with Siamese nets (2006)" — the method that seeded all of Meta AI's contrastive-learning line
  - "Off-Road robot navigation with convolutional networks (LAGR Project 2008)" — applied world-model thinking before the term was mainstream
- **mine-for**: The 6-layer autonomous-AI stack is a ready-made agent-architecture checklist (what's your perceiver, what's your world model, what's your cost function). JEPA's "predict the embedding, not the sample" is a direct architectural decision for any system where you want compressed state and don't care about reconstruction. The LAGR pipeline (conv features → metric learning → metric planning) is an early template for perception-to-action pipelines that skip end-to-end "pure end-to-end" SCALING.

## Top videos (signal-sorted)
`DokLw1tILlw`  62m  Yann LeCun: "A Path Towards Autonomous AI", Baidu 2022-02-22  https://www.youtube.com/watch?v=DokLw1tILlw — 
`Qgh2IU_fRMs`  60m  Q&A sessions for "A Path Towards Autonomous AI", by Yann LeCun, Baidu 2022-02-22  https://www.youtube.com/watch?v=Qgh2IU_fRMs — 
`jcREIboRkn0`  14m  DrLIM: learning an embedding with Siamese nets (2006)  https://www.youtube.com/watch?v=jcREIboRkn0 — 
`H0oEr40YhrQ`  1m  Convolutional Network Demo from 1989 [restored version]  https://www.youtube.com/watch?v=H0oEr40YhrQ — 
`fFnqKKRRjCQ`  3m  lagrtest11 nsnyu run3  https://www.youtube.com/watch?v=fFnqKKRRjCQ — 
`0ud0cMdIGIU`  3m  lagrtest11 nsnyu run2  https://www.youtube.com/watch?v=0ud0cMdIGIU — 
`murRdueKbcE`  7m  lagrtest11 nsnyu run1  https://www.youtube.com/watch?v=murRdueKbcE — 
`5nCXaExwNxA`  2m  20060331 mvi 0183 mpeg4  https://www.youtube.com/watch?v=5nCXaExwNxA — 
`XJrv66RGXGQ`  1m  20060331 hoh 00553029001  https://www.youtube.com/watch?v=XJrv66RGXGQ — 
`xFlGfdczIXQ`  2m  20060331 hoh 00535928001  https://www.youtube.com/watch?v=xFlGfdczIXQ — 
`QA3SxM7OPdQ`  3m  20060331 hoh 00503028001  https://www.youtube.com/watch?v=QA3SxM7OPdQ — 
`qnoP9PPTfBE`  8m  Yann's 60th Birthday video from his padawans.  https://www.youtube.com/watch?v=qnoP9PPTfBE — 
`GLgX8ku5TOQ`  5m  Off-Road robot navigation with convolutional networks(LAGR Project 2008))  https://www.youtube.com/watch?v=GLgX8ku5TOQ — 
`yKfMj1EXb04`  3m  20060331 hoh 00440906001  https://www.youtube.com/watch?v=yKfMj1EXb04 — 
`iqBpXLE1Fyg`  2m  20060331 hoh 00370718001  https://www.youtube.com/watch?v=iqBpXLE1Fyg — 
`weeLxT1bdC8`  2m  20060331 hoh 00470903001  https://www.youtube.com/watch?v=weeLxT1bdC8 — 
`cm2VlEGNz5A`  2m  Semantic Segmentation (33 categories)  https://www.youtube.com/watch?v=cm2VlEGNz5A — 
`E_HQSEVsxWA`  1m  Real-Time Object Recognition with Convolutional Net (2008)  https://www.youtube.com/watch?v=E_HQSEVsxWA — 
`QoeftFGrjI4`  1m  20060331 hoh 00484618001  https://www.youtube.com/watch?v=QoeftFGrjI4 — 
`FwFduRA_L6Q`  1m  Convolutional Network Demo from 1989  https://www.youtube.com/watch?v=FwFduRA_L6Q — 
`MnZNSZGNGyc`  1m  Pedestrian detection with convolutional networks, part 1 (CVPR 2013)  https://www.youtube.com/watch?v=MnZNSZGNGyc — 
`aqt2PPZqldk`  1m  Semantic Segmentation (8 categories)  https://www.youtube.com/watch?v=aqt2PPZqldk — 
`Q5m7_I7Bc8Q`  1m  20060331 hoh 00391102001  https://www.youtube.com/watch?v=Q5m7_I7Bc8Q — 
`UPVvd8WNUks`  1m  Pedestrian detection with convolutional networks, part 2 (CVPR 2013)  https://www.youtube.com/watch?v=UPVvd8WNUks — 

## On-disk corpus
- transcripts: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/yann-lecun/transcripts/<id>.txt` (cleaned, one line per cue)
- stats: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/yann-lecun/transcripts.stats.json`

Useful moves:
```sh
G=/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/yann-lecun
# most substantive episodes
python3 -c "import json;d=json.load(open('$G/videos.json'));[print(v['id'],round((v.get('duration') or 0)/60),'m',v['title'][:70]) for v in sorted(d['videos'],key=lambda v:-(v.get('duration') or 0))[:12]]"
# grep a theme across transcripts
grep -ril "scaling" $G/transcripts/ | head -20
# open one transcript
cat $G/transcripts/DokLw1tILlw.txt
```
Known gap: /videos tab only — Shorts: Shorts-heavy, few/indexed.

## One-liner
> Yann LeCun
