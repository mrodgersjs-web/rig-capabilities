---
name: skill-factory
description: "Turn a creator's corpus or a repeated workflow into a governed skill family: choose sources, capture transcripts, distill cited laws, build meta, stage and sub skills, gate them, file them under a meta, and evaluate the routing. Use for 'scrape his videos into skills', 'build a meta-skill from these channels', 'turn this into a skill', or upgrading an existing skill with evidence."
done_when:
  - 'grep:capabilities/skills/skill-factory/SKILL.md:[C]urated beats self-generated'
  - 'grep:capabilities/skills/skill-factory/SKILL.md:[F]ile, never drop'
---

# skill-factory

Full map of children with paths: `LAYERS.md` next to this file. Owner agent: iris-sr-research.

## Route

| Task | Skill |
|---|---|
| A corpus (YouTube channels, courses, docs) becomes a new skill family | `corpus-to-skill-family` |
| Improve an existing skill from outcome evidence; refute its done-test; install and verify | `skill-upgrades` |
| Score sources and extract doctrine | `rig-doctrine-forge` |
| Pull YouTube transcripts | builtin `youtube` skill |

## Rules

- **Curated beats self-generated.** SkillsBench (via Recall card 81d53ac9, SoK: Agentic Skills): curated skills raised task pass rates by 16.2 points; self-generated ones averaged -1.3. Every generated skill passes a gate before it is filed.
- **Focused beats exhaustive.** The same work found focused, detailed skills gain 18.8 points while comprehensive ones lose 2.9. Keep each SKILL.md under 500 lines and move doctrine into a references skill.
- **Every law cites its source** as `CLAIM(<videoId>@mm:ss)`, marked consensus or single-source, with disagreements and dated tool tips kept apart.
- **Raw third-party corpora stay local.** Only synthesis goes into public repos.
- **File, never drop.** New skills enter the surface through `skill-surface file`, so the menu stays at 30.

## Great examples

`design-studio-os` (822 laws across 15 stages, citations checked by a rival model family), `linkedin-viral`, `ss-growth-os`, `google-ads-os`, `fe-system-design-os`.

## Done-test

For a new family: `skill-surface verify` is GREEN and `skill-surface route` picks the new meta and the intended stage skill for at least three of the family's own example tasks.
