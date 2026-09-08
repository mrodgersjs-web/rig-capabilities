---
name: youtube-nvidia-developer
description: NVIDIA Developer (@NVIDIADeveloper): L4 lab AI-stack channel (1082-video corpus) with transcript-mining commands. Load before digging this channel's transcripts or quoting its frames.
when_to_use: mining @NVIDIADeveloper videos; quoting NVIDIA Developer as evidence for GTM/agent-engineering work; choosing what to absorb from lab/bridge/rarity tier (L4 lab)
version: 0.1.0
owner: rig
domain: youtube-corpus
status: draft
verified_by: rig-agent
verified_on: 2026-09-08
outcome: Load channel-scope context before mining the nvidia-developer corpus or doing GTM/agent work informed by it.
done_when: >
  Digest + top-video index read from the skill body; grep/locate commands
  demonstrated against the on-disk corpus for at least one landmark video.
great_example: youtube_intel/digests/nvidia-developer_brief.md (this repo, quarantine-rooted)
quality_floor: Digest sections complete; top-video table >= 10 rows; corpus paths verified to exist.
metadata:
  ladder_level: 4
  handle: @NVIDIADeveloper
  corpus_root: /Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus
hooks: []
---

# youtube-nvidia-developer

Channel-scope context for the **@NVIDIADeveloper** YouTube corpus — L4 lab tier of the RIG 5-level AI stack.

## What this surface is
## NVIDIA Developer - digest

- **what it is**: NVIDIA's developer-facing keynotes, architecture deep-dives, and embodied-AI research group meetings (Jetson AI Lab).
- **episode shape**: heterogeneous — GTC stage talks (25–110 min), Jetson Lab group meetings (86–93 min), Grandmaster tutorials (55–66 min), 2–6 min explainers.
- **recurring themes**:
  - Embodied AI & world models: Cosmos, Isaac Sim, LeRobot, H1 humanoid, Stanley
  - Inference scaling: Dynamo (low-latency distributed inference), NeMo Switchyard (agent routing)
  - CUDA architecture: Tile kernels, Nsight Compute, parallel algorithms
  - Agent engineering: continuous distillation, data flywheels, LLM reasoning for data analysis
  - Quantum-ML crossover: quantum-based drug discovery, GTC 2025 fireside chat
  - Jetson edge: DGX Spark, Jetson Nano, NASA JPL ROSA
- **signature frames**:
  - "GPU as the AI operating system" (CUDA-per-everything framing)
  - World models as synthetic data flywheels (Cosmos)
  - Inference economics as the new compute bottleneck (Dynamo)
  - Embodied intelligence as the LLM successor frontier (Jim Fan)
  - "Democratize via kits" — Jetson Nano → Jetson Orin → DGX Spark product ladder
- **must-watch**:
  - "An Introduction to NVIDIA Cosmos World Foundational Models | NVIDIA GTC 2025" — defines the world-model thesis in 36 min
  - "Generally Capable Agents in Open-Ended Worlds, Jim Fan, NVIDIA Lead of Embodied AI | NVIDIA GTC 2024" — clearest articulation of NVIDIA's agent-embodiment bet
  - "Introducing NVIDIA Dynamo: Low-Latency Distributed Inference for Scaling Reasoning LLMs" — the inference-scaling architecture NVIDIA is selling "now"
  - "Optimize AI Agents with Continuous Model Distillation and Evaluation Using a Data Flywheel" — compact GTM framing for agent product teams
  - "Interview with NVIDIA CUDA Architect Stephen Jones" — ground-truth on where CUDA is heading (Warp, Tile, async)
- **mine-for**: Extract NVIDIA's agent-awareness layering (Cosmos = sim/data, Dynamo = runtime, NeMo Switchyard = routing, Nemotron = weights). For GTM, the Jetson→DGX Spark product ladder doubles as an inference-TAM expansion story. For agent engineering, the distillation/flywheel loop and Switchyard routing are the two patterns worth stealing for building agent systems on NVIDIA silicon.

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
