---
name: youtube-yann-lecun
description: "Yann LeCun (@YannLeCunPhD): L4 lab AI-stack channel (26-video corpus) with transcript-mining commands. Load before digging this channel's transcripts or quoting its frames."
when_to_use: mining @YannLeCunPhD videos; quoting Yann LeCun as evidence for GTM/agent-engineering work; choosing what to absorb from lab/bridge/rarity tier (L4 lab)
version: 0.1.0
owner: rig
domain: youtube-corpus
status: draft
verified_by: rig-agent
verified_on: 2026-09-08
outcome: Load channel-scope context before mining the yann-lecun corpus or doing GTM/agent work informed by it.
done_when:
  - file:capabilities/skills/youtube-yann-lecun/index.json
  - grep:capabilities/skills/youtube-yann-lecun/SKILL.md:## Top videos
quality_floor: Digest sections complete; top-video table >= 10 rows; corpus paths verified to exist.
metadata:
  ladder_level: 4
  handle: "@YannLeCunPhD"
  corpus_root: /Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus
hooks: []
---

# youtube-yann-lecun

Channel-scope context for the **@YannLeCunPhD** YouTube corpus — L4 lab tier of the RIG 5-level AI stack.

## What this surface is
## MEDIAN — digest
- **what it is**: Unofficial lecture/demo archive of Yann LeCun's talks and short clips, ranging from a 2022 keynote to 2006 home-video dailies.
- **episode shape**: Heterogeneous — 1-hour talks, 1–8 min focused demos, and unlabeled raw dailies (`hoh`/`mvi` = phone-camera timestamps).
- **recurring themes**:
  - ConvNet lineage: 1989 HMax demo → NEC face detection (2003) → pedestrian detection (CVPR 2013) → video semantic segmentation (2014)
  - Siamese / metric-learning embeddings (DrLIM, 2006)
  - Lagrangian relaxation for combinatorial vision tasks (`lagrtest11` NYU runs)
  - Energy-Based Models as the "next paradigm" beyond GANs/VAEs (core thesis of the Baidu talk)
  - LAGR off-road robot navigation as the applied-robotics anchor
- **signature frames**:
  - HMax hierarchical max-pooling (1989) as the original ConvNet template
  - Twin Siamese network for learned distance metrics
  - Energy function as a unifying object for perception + planning (vs. loss functions in DNN)
  - Lagrangian duality as the "free lunch" for structured prediction in vision
  - Perception–action loop as the definition of autonomous AI (not language)
- **must-watch**:
  - Yann LeCun: "A Path Towards Autonomous AI", Baidu 2022-02-22 — the single clearest statement of his EBM thesis and why he thinks deep learning alone won't reach autonomy
  - Q&A sessions for "A Path Towards Autonomous AI", by Yann LeCun, Baidu 2022-02-22 — where the energy-function argument gets stress-tested by audience objections
  - DrLIM: learning an embedding with Siamese nets (2006) — 14-min explainer on why metric learning predates and outlives deep metric learning
  - Convolutional Network Demo from 1989 [restored version] — the origin artifact; shows how little the architecture has changed in 35 years
  - Off-Road robot navigation with convolutional networks (LAGR Project 2008) — the perception–action loop made tangible, pre-GPT
- **mine-for**: For an agent-engineering lens, extract his repeated claim that *world models + energy minimization* (not autoregressive next-token) is the right architecture for agents operating in continuous spaces. The Baidu talk's opening frames autonomous AI as a closed perception–planning–acting loop where the energy function is the single optimizable object — directly contrast with reward-model + RL pipelines. The `lagrtest` dailies reveal his internal validation loop: run → plot → iterate on relaxation tightness, a primitive "agent eval" long before the term existed.

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
