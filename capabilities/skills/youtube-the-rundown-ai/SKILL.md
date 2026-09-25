---
name: youtube-the-rundown-ai
description: "The Rundown AI (@TheRundownAI): L1 rarity AI-stack channel (10-video corpus) with transcript-mining commands. Load before digging this channel's transcripts or quoting its frames."
when_to_use: mining @TheRundownAI videos; quoting The Rundown AI as evidence for GTM/agent-engineering work; choosing what to absorb from lab/bridge/rarity tier (L1 rarity)
version: 0.1.0
owner: rig
domain: youtube-corpus
status: draft
verified_by: rig-agent
verified_on: 2026-09-08
outcome: Load channel-scope context before mining the the-rundown-ai corpus or doing GTM/agent work informed by it.
done_when:
  - file:capabilities/skills/youtube-the-rundown-ai/index.json
  - grep:capabilities/skills/youtube-the-rundown-ai/SKILL.md:## Top videos
quality_floor: Digest sections complete; top-video table >= 10 rows; corpus paths verified to exist.
metadata:
  ladder_level: 1
  handle: "@TheRundownAI"
  corpus_root: /Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus
hooks: []
---

# youtube-the-rundown-ai

Channel-scope context for the **@TheRundownAI** YouTube corpus — L1 rarity tier of the RIG 5-level AI stack.

## What this surface is
## MEDIAN – digest
- **what it is**: Long-form executive interviews with AI lab and platform leaders, positioned as Level 1 of a 5-level AI stack (daily AI news cycle feed).
- **episode shape**: Single-guest sit-down, 14–57 min, structured around a strategic thesis + technical build + future-of-work cut.
- **recurring themes**:
  - AI agents as the platform-of-record (Dharmesh "AI App Store," Nadella "Rebuilding the Web," Pichai "Agents Replacing Engineers")
  - Open-source positioning as distribution moat (Zuckerberg on Llama 3.1, Shah on AEO)
  - AGI timelines and post-AGI civilization (Hassabis 2030, Altman "Zero-Person Companies")
  - Neural interfaces and superintelligence as the 10-year horizon (Zuckerberg neural control)
  - Companion/memory architectures (Suleyman Copilot Vision, Infinite Memory)
  - "Flip phone moment" framing for AI's inflection (Pichai)
- **signature frames**:
  - The Agent Economy lens – agents as new app store / distribution layer
  - Zero-person company test – can a firm run with no employees?
  - Flip-phone analogy – when does an AI capability leap from incremental to category-defining?
  - Stacked capability levels (RIG 5-level stack) – where does each player sit?
  - "Life after AGI" horizon – what problem does AGI actually solve?
- **must-watch**:
  - *Sam Altman on Zero-Person AI Companies, Sora, AGI Breakthroughs, and more* – cleanest articulation of agent-economy GTM and distribution logic.
  - *Satya Nadella on AI Agents, Rebuilding the Web, the Future of Work, and more* – best map of how a legacy platform re-architects for agent-first.
  - *Dharmesh Shah on AEO, AI Agents, and the 'AI App Store'* – longest (57 min); AEO as the new SEO, agent-commerce thesis.
  - *Mark Zuckerberg on Llama 3.1, Open Source, AI Agents, Safety, and more* – open-source as competitive strategy, not ideology.
  - *Sundar Pichai on Agents Replacing Engineers, Google's Future, AI's Flip Phone Moment, and More* – "flip phone" frame is the sharpest single metaphor in the corpus.
- **mine-for**: Extract the agent-distribution argv: how each exec defines who the agent's user is (dev? end consumer? other agent), what the billing surface looks like (app store, API, embedded interface), and where open-source lowers CAC. The Rhino cut: Nadella's "rebuild the Web" + Pichai's "agents replace engineers" + Altman's "zero-person" form a single thesis – the web's human-UI layer is being replaced by an agent-UI layer, and whoever owns that layer owns the next platform tax.

## Top videos (signal-sorted)
`fKjgKr-kgAY`  57m  Dharmesh Shah on AEO, AI Agents, and the ‘AI App Store’  https://www.youtube.com/watch?v=fKjgKr-kgAY —
`WQvMdmk8IkM`  46m  Logan Kilpatrick on Google’s new Gemini Models, AI Agents, AGI, and more  https://www.youtube.com/watch?v=WQvMdmk8IkM —
`WuTJkFvw70o`  45m  Mark Zuckerberg on AI Glasses, Superintelligence, Neural Control, and More  https://www.youtube.com/watch?v=WuTJkFvw70o —
`Vy3OkbtUa5k`  35m  Mark Zuckerberg on Llama 3.1, Open Source, AI Agents, Safety, and more  https://www.youtube.com/watch?v=Vy3OkbtUa5k —
`zwnVUiwObl8`  31m  Sam Altman on Zero-Person AI Companies, Sora, AGI Breakthroughs, and more  https://www.youtube.com/watch?v=zwnVUiwObl8 —
`dQP2zLYmCG8`  26m  Mustafa Suleyman on Copilot Vision, AI Companions, Infinite Memory, AI Agents, a  https://www.youtube.com/watch?v=dQP2zLYmCG8 —
`_a8EnBX8DSU`  22m  Satya Nadella on AI Agents, Rebuilding the Web, the Future of Work, and more  https://www.youtube.com/watch?v=_a8EnBX8DSU —
`zBOoEpsjWAo`  20m  Sundar Pichai on Agents Replacing Engineers, Google's Future, AI's Flip Phone Mo  https://www.youtube.com/watch?v=zBOoEpsjWAo —
`4tVCHeAv0D4`  17m  Demis Hassabis on AGI by 2030, Curing Every Disease, Life After AGI, and More  https://www.youtube.com/watch?v=4tVCHeAv0D4 —
`HO7oYuqqnjA`  14m  Demis Hassabis on Gemini 2.0, Project Astra, Agents, Gaming with Elon, and more  https://www.youtube.com/watch?v=HO7oYuqqnjA —

## On-disk corpus
- transcripts: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/the-rundown-ai/transcripts/<id>.txt` (cleaned, one line per cue)
- stats: `/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/the-rundown-ai/transcripts.stats.json`

Useful moves:
```sh
G=/Users/rig128gb/orca/workspaces/rig-gtm-studio-v2/youtube-channels/youtube_corpus/the-rundown-ai
# most substantive episodes
python3 -c "import json;d=json.load(open('$G/videos.json'));[print(v['id'],round((v.get('duration') or 0)/60),'m',v['title'][:70]) for v in sorted(d['videos'],key=lambda v:-(v.get('duration') or 0))[:12]]"
# grep a theme across transcripts
grep -ril "scaling" $G/transcripts/ | head -20
# open one transcript
cat $G/transcripts/fKjgKr-kgAY.txt
```
Known gap: /videos tab only — Shorts: Shorts-heavy, few/indexed.

## One-liner
> The Rundown AI
