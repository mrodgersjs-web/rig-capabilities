---
name: youtube-nvidia-developer
description: "NVIDIA Developer (@NVIDIADeveloper): L4 lab AI-stack channel (1082-video corpus) with transcript-mining commands. Load before digging this channel's transcripts or quoting its frames."
when_to_use: mining @NVIDIADeveloper videos; quoting NVIDIA Developer as evidence for GTM/agent-engineering work; choosing what to absorb from lab/bridge/rarity tier (L4 lab)
version: 0.1.0
owner: rig
domain: youtube-corpus
status: draft
verified_by: rig-agent
verified_on: 2026-09-08
outcome: Load channel-scope context before mining the nvidia-developer corpus or doing GTM/agent work informed by it.
done_when:
  - file:capabilities/skills/youtube-nvidia-developer/index.json
  - grep:capabilities/skills/youtube-nvidia-developer/SKILL.md:## Top videos
quality_floor: Digest sections complete; top-video table >= 10 rows; corpus paths verified to exist.
metadata:
  ladder_level: 4
  handle: "@NVIDIADeveloper"
  corpus_root: /Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus
hooks: []
---

# youtube-nvidia-developer

Channel-scope context for the **@NVIDIADeveloper** YouTube corpus — L4 lab tier of the RIG 5-level AI stack.

## What this surface is
## @NVIDIADeveloper - digest

- **what it is**: NVIDIA's developer-facing channel — a heterogeneous mix of research-group recordings, GTC keynotes, short how-to clips, and architect interviews spanning the full stack from CUDA tile kernels to world models.
- **episode shape**: No fixed format; ranges from 2-minute product how-tos to 90-minute Jetson AI Lab research meetings and 55–100-minute GTC sessions.
- **recurring themes**:
  - Jetson AI Lab series (dated research-group meetings; embodied AI, humanoid robots, Isaac Sim)
  - Named model families: Cosmos (world FMs), Dynamo (distributed inference), NeMo Switchyard (agent routing), Nemotron 3.5, Alpamayo 2 Super
  - CUDA architecture deep-dives (tile kernels, Nsight profiling, Stephen Jones interviews)
  - Grandmaster Series (competitive ML / LLM frontiers with Kaggle/GTC grandmasters)
  - Hardware-targeted how-tos (DGX Spark, Jetson Nano, Jetson Orin)
- **signature frames**:
  - Jetson AI Lab as a public "research group meeting" format — episodic, dated, unscripted
  - Grandmaster Series competition framing (treat ML like a esport)
  - GTC keynote → Fireside Chat → 5-minute "In 5 Minutes" teaser as a three-tier narrative bundle
  - "World Foundational Model" as the next-tier product above LLM
  - RIG stack positioning (Level 4 = Dev/Tools above model, below application)
- **must-watch**:
  - "Generally Capable Agents in Open-Ended Worlds, Jim Fan, NVIDIA Lead of Embodied AI | NVIDIA GTC 2024" — Jim Fan's thesis on general embodied agents
  - "Introducing NVIDIA Dynamo: Low-Latency Distributed Inference for Scaling Reasoning LLMs" — the inference-architecture blueprint
  - "An Introduction to NVIDIA Cosmos World Foundational Models | NVIDIA GTC 2025" — world-moel product framing for simulation-to-reality
  - "Deploying AI in Real-World Robots | Aaron Saunders, Boston Dynamics CTO | NVIDIA GTC 2024" — outside validation of the Jetson/Isaac stack
  - "Run NVIDIA Nemotron 3.5 Lightning on DGX Spark" — 5-min product GTM in a single breath
- **mine-for**: The Jetson AI Lab meetings are week-to-week research-group transcripts that expose what embodied-AI labs actually iterate on (ROS2, Isaac Sim, OASIS, Iron Man) before it becomes a slides deck. The 2–6-minute how-tos are the pure GTM layer: each names a model, a hardware target, and a use case in one sentence — ideal for reverse-engineering NVIDIA's product-messaging cadence. The GTC keynotes plus 5-minute re-cuts (e.g., "NVIDIA Dynamo in 5 Minutes") show a deliberate long-form → short-form distillation pipeline you can mirror for agent-engineering content.

## Top videos (signal-sorted)
`fgibRb_8T5I`  146m  NVIDIA RecSys Summit 2022 - China Day  https://www.youtube.com/watch?v=fgibRb_8T5I —
`Sdjn9FOkhnA`  125m  Accelerating Applications with Parallel Algorithms | CUDA C++ Class Part 1  https://www.youtube.com/watch?v=Sdjn9FOkhnA —
`9XB-LsfpvCU`  123m  Quantum Computing: Where We Are and Where We’re Headed | NVIDIA GTC 2025 Firesid  https://www.youtube.com/watch?v=9XB-LsfpvCU —
`7w3RHoIIkNE`  111m  JETSON AI LAB | Research Group Meeting (4/3/24)  https://www.youtube.com/watch?v=7w3RHoIIkNE —
`Oyon1QDpU6g`  101m  An Introduction to Building Humanoid Robots | NVIDIA GTC 2025  https://www.youtube.com/watch?v=Oyon1QDpU6g —
`mdDVkBeFy9A`  99m  GPU MODE at NVIDIA GTC 2025  https://www.youtube.com/watch?v=mdDVkBeFy9A —
`pURku7OAWuo`  93m  JETSON AI LAB | Research Group Meeting (7/23/2024)  https://www.youtube.com/watch?v=pURku7OAWuo —
`HfJR3NwsM4M`  92m  JETSON AI LAB | Research Group Meeting (10/1/2024)  https://www.youtube.com/watch?v=HfJR3NwsM4M —
`-C43j2HgQdY`  91m  JETSON AI LAB | NASA JPL ROSA in Isaac Sim & The OASIS Project with IronMan (10/  https://www.youtube.com/watch?v=-C43j2HgQdY —
`3C-6STonTLU`  89m  Introducing NVIDIA Dynamo: Low-Latency Distributed Inference for Scaling Reasoni  https://www.youtube.com/watch?v=3C-6STonTLU —
`Dpe48AVKc4c`  87m  JETSON AI LAB | HuggingFace LeRobot and Stanley the H1 Humanoid (10/15/2024)  https://www.youtube.com/watch?v=Dpe48AVKc4c —
`Ngaq2WCDlZM`  86m  JETSON AI LAB | Research Group Meeting (7/9/2024)  https://www.youtube.com/watch?v=Ngaq2WCDlZM —
`TR8VIjnQXdE`  2m  How to Profile and Optimize CUDA Tile Kernels with NVIDIA Nsight Compute  https://www.youtube.com/watch?v=TR8VIjnQXdE —
`mXYFcz27eDw`  6m  NVIDIA Dynamo in 5 Minutes: What Is It and Why Now?  https://www.youtube.com/watch?v=mXYFcz27eDw —
`MehBUQtb9qM`  3m  How to Connect Two DGX Sparks with NVIDIA Sync  https://www.youtube.com/watch?v=MehBUQtb9qM —
`2Tskr8an1oE`  6m  How to Route AI Agent Workloads Across Models with NVIDIA NeMo Switchyard  https://www.youtube.com/watch?v=2Tskr8an1oE —
`Lhy1Bu8fN8A`  5m  Run NVIDIA Nemotron 3.5 Lightning on DGX Spark  https://www.youtube.com/watch?v=Lhy1Bu8fN8A —
`VeYZ-MrJv3A`  3m  Introducing NVIDIA Alpamayo 2 Super  https://www.youtube.com/watch?v=VeYZ-MrJv3A —
`sYLU40u9L-k`  24m  Inside NVIDIA Cosmos | SIGGRAPH 2026 Keynote  https://www.youtube.com/watch?v=sYLU40u9L-k —
`2mg8tNIKvXE`  3m  Axolotl3D: a Unified Framework for Faithful 3D Shape Completion  https://www.youtube.com/watch?v=2mg8tNIKvXE —
`PXc_SlnT2g0`  66m  Building World-Class NLP Models with Transformers and Hugging Face | Grandmaster  https://www.youtube.com/watch?v=PXc_SlnT2g0 —
`y7FGo8F5bog`  24m  Interview with NVIDIA VP Jonathan Cohen on Reasoning Models for AI Agents  https://www.youtube.com/watch?v=y7FGo8F5bog —
`ZSPEyFqAGDc`  55m  Generally Capable Agents in Open-Ended Worlds, Jim Fan, NVIDIA Lead of Embodied   https://www.youtube.com/watch?v=ZSPEyFqAGDc —
`L1QKTPb6V_I`  55m  How to Build a World-Class ML Model for Melanoma Detection | Grandmaster Series   https://www.youtube.com/watch?v=L1QKTPb6V_I —

## On-disk corpus
- transcripts: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/nvidia-developer/transcripts/<id>.txt` (cleaned, one line per cue)
- stats: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/nvidia-developer/transcripts.stats.json`

Useful moves:
```sh
G=/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/nvidia-developer
# most substantive episodes
python3 -c "import json;d=json.load(open('$G/videos.json'));[print(v['id'],round((v.get('duration') or 0)/60),'m',v['title'][:70]) for v in sorted(d['videos'],key=lambda v:-(v.get('duration') or 0))[:12]]"
# grep a theme across transcripts
grep -ril "scaling" $G/transcripts/ | head -20
# open one transcript
cat $G/transcripts/fgibRb_8T5I.txt
```
Known gap: /videos tab only — Shorts: negligible.

## One-liner
> NVIDIA Developer
