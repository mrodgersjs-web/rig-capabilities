---
name: "rigds-dev-handoff"
description: "JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Main skill of rig-design-studio for the open-design dev-handoff: the app-independent contract rig.design-studio.dev-handoff.v1 — machine JSON, prompt bundle, tokens — that any coding agent can consume without the design app's source. Use when exporting a design for build or when consuming an export as a builder."
tier: main
parent: rig-design-studio
activation: "Load at the start of any task that exports a board for handoff or builds from a rig.design-studio.dev-handoff.v1 export: serializer, prompt bundle, token set, export files."
owner: theo-design
status: Stable
acl: internal
outcome: "design-ux: rig-dev-handoff.json + rig-ai-coding-prompts.md carrying schema rig.design-studio.dev-handoff.v1 with derived counts/deviations, per-card labels and upstream/downstream, and a token set with anti-patterns — consumable app-independently"
done_when:
  - grep:capabilities/skills/rigds-dev-handoff/SKILL.md:rig.design-studio.dev-handoff.v1
  - grep:capabilities/skills/rigds-dev-handoff/SKILL.md:rigds-export-check
quality_floor: 0.6
great_example: corpus/examples/night-v2/export/rig-dev-handoff.json
---

# Open-design dev-handoff

The handoff is the portable core of the method (open design): the contract lives with the skill family,
the app is just one producer, and a builder needs nothing but the two export files.

## Contract `rig.design-studio.dev-handoff.v1`

`BoardExport` = {schema, board, exportedAt, counts{cards,links,phases}, deviations{min,max,outOfBudget},
tokenSet{name:'MASTER-CREATIVE-PROMPT v3.0', colors, type, antiPatterns}, phases[], cards: SerializedCard[],
links}. `SerializedCard` carries `phaseLabel`, `kindLabel`, `outOfBudget`, `upstream`, `downstream` on top
of the card payload.

Export files (fixed names): `EXPORT_FILES = {json: 'rig-dev-handoff.json', md: 'rig-ai-coding-prompts.md'}`.

- `serializeBoard()` produces the JSON — labels derived at serialization, counts/deviations computed.
- `promptBundle()` produces the Markdown: the human/agent-readable build prompts that accompany the JSON.

## Builder's reading order

1. `tokenSet` + `antiPatterns` — what the build must look like and what to fail.
2. `phases` + `cards` — what to build, in decision order; `upstream`/`downstream` explains each screen.
3. `counts`/`deviations` — sanity-check the export before trusting it (rigds-export-check does this).

## Rules (binding)

- **Schema string in every export.** A consumer keys on `rig.design-studio.dev-handoff.v1`, never on
  app internals or filenames alone.
- **App-independent**: no field may reference app-only state (component ids, store shapes). If a builder
  needs it, it goes in the export.
- **Portable by construction**: the two files plus this contract are sufficient. Worked reference:
  `corpus/examples/night-v2/export/` (18.6 KB JSON + 39 KB prompt bundle).
- Bump the schema suffix (v2) on breaking changes; additive fields keep the version. Keep the export
  check in lockstep (rigds-export-check).

## Lessons from v1/v2 (binding)

- Labels at serialization (`phaseLabel`, `kindLabel`) kept JSON and prompt bundle consistent — one
  derivation, two renderings.
- The prompt bundle carries its own context (a builder six months later will not recall the run), the
  same rule as the stitch prompts.

Outward, paid or destructive steps stop at Gate-D.
