---
name: "rigds-export-check"
description: "JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Sub-skill of rigds-dev-handoff for the export assertion harness: the export-check pattern that proves a rig.design-studio.dev-handoff.v1 export against its schema version with runnable assertions (13 in v1). Use when validating an export or when adding a schema version."
tier: sub
parent: rigds-dev-handoff
activation: "Load when checking a dev-handoff export before shipping it, or when a schema bump requires new assertions."
owner: theo-design
status: Stable
acl: internal
outcome: "design-ux: a runnable assertion harness over the serializer output that fails on any drift between schema, data-derived counts/deviations, and rendered labels — green only when every assertion executes"
done_when:
  - grep:capabilities/skills/rigds-export-check/SKILL.md:export-check
  - grep:capabilities/skills/rigds-export-check/SKILL.md:schema
quality_floor: 0.6
great_example: corpus/examples/night-v2/scripts/export-check.mjs
---

# Export check — the assertion-harness pattern

An export is untrusted until its check runs. The pattern (worked reference:
`corpus/examples/night-v2/scripts/export-check.mjs`, 13 assertions, PASS 13/13):

- **Round-trip invariants**: `counts{cards,links,phases}` equals actual array lengths; `phases[]`
  covers every card's phase id; every `phaseLabel`/`kindLabel` resolves from its id.
- **Derivation invariants**: `deviations{min,max,outOfBudget}` recomputed from cards equals the shipped
  values; `outOfBudget` flags agree with the deviation math.
- **Contract invariants**: `schema === 'rig.design-studio.dev-handoff.v1'`; `tokenSet.name` pinned to
  `MASTER-CREATIVE-PROMPT v3.0`; `antiPatterns` non-empty; `EXPORT_FILES` names exact
  (`rig-dev-handoff.json`, `rig-ai-coding-prompts.md`).
- **Link invariants**: every card's `upstream`/`downstream` entries resolve to real cards.

## Rules (binding)

- One assertion harness per schema version; a version bump ADDS assertions and never deletes old ones —
  old versions stay checkable as long as they can be produced.
- The check runs on serializer output (the file), not on in-memory board state: the file is what the
  builder consumes.
- Green means every assertion executed. A skipped assertion is not green; report skips explicitly.
- Exit code is the contract: 0 all pass, non-zero names the failed assertion.

## Lessons from v1/v2 (binding)

- The 13-assertion harness caught label/count drift twice during v2 before the export reached the
  builder. Checks earn their keep at the serializer boundary, not in the UI.
- Assertions assert consumer-visible invariants only — never wiring, never file existence alone.

Outward, paid or destructive steps stop at Gate-D.
