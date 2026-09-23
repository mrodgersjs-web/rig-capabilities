---
name: when-producing-media
description: "When generating or editing audio, music, video, or film, use this to route to the right media skill. Routes to 8 skills; read references/routing.md for the full table."
metadata:
  purpose: meta-skill
  generated-by: skillshilp-upgrade
  category: media-production
  skill-count: "8"
---

# when-producing-media

Tier-1 meta-skill. Job to be done: When generating or editing audio, music, video, or film, use this to route to the right media skill.

## Hierarchy
1. **Meta-skill (this file)** — the skill you call up for this job. Routes only; holds no doctrine of its own.
2. **Skills** — load the named child skill's SKILL.md and follow it. Each child is written to route further when it owns a family.
3. **Sub-skills** — a skill whose routing entry lists sub-skills delegates further; load only the one sub-skill the task needs.

## Routing contract (binding)
- MUST route through this meta-skill first for any job in its description; never load a child directly from memory of its name.
- MUST load exactly ONE child skill per task step; never bulk-load children from the index.
- MUST load only the single sub-skill the task needs, only when the loaded child names sub-skills.
- MUST NOT load a second child to "compare"; if two children seem to match, pick by the routing table one-liner in references/routing.md, then load that one.
- The quick index below is a relevance-ordered SAMPLE, not the full set; if no index entry fits the task, scan the full table in references/routing.md before choosing.
- If no child matches the task, load `when-nothing-else-fits` instead of guessing.
- If a child skill fails to load or is missing, report the broken route and stop; do not improvise its content.

## How to route
1. Scan the quick index below. If nothing obviously matches, read `references/routing.md` for the full 8-skill table with one-line descriptions.
2. Load exactly one child skill. If it names sub-skills, load the one relevant sub-skill.
3. Never load more than one skill plus one sub-skill for a single task step.

## Quick index (top skills)
- **audiocraft** — AudioCraft: MusicGen text-to-music, AudioGen text-to-sound." version: 1.0.0 license: MIT m
- **animate** — Build an animation from scratch, making the decisions in the order that determines whether
- **animate-expo** — Build animations in React Native and Expo, making the decisions in the order that determin
- **animation-vocabulary** — Reverse-lookup glossary that turns a vague description of a web animation or motion effect
- **heartmula** — HeartMuLa: Suno-like song generation from lyrics + tags." version: 1.0.0 metadata:   herme
- **hudl-film-pipeline** — Acquire Jacob Rodgers' football film from Hudl or live YouTube and move it through the pri
- **remotion** — Generate walkthrough videos from Stitch projects using Remotion with smooth transitions, z
- **video-editing** — Edit video programmatically with ffmpeg   cuts, concatenation, transcode, audio normalizat

Full table: `references/routing.md`
