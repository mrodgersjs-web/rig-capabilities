---
name: traject-room-builder
description: "MAIN agent: builds a Traject interview-prep room as a data module in Lucy's Stage 0-8 order plus Run of Show / DECISIONS / debrief tabs, using only résumé-verified claims. Dispatches traject-company-researcher and traject-jd-decoder. Never states the floor or a banned claim; gated by story.bank and jd.decode."
allowed-tools: Bash Read Grep Glob Write
owner: rig-intelligence
domain: business-ops / interview-prep authoring
status: Stable
verified_by: jake
verified_on: 2026-09-28
acl: internal
relates_to: traject-os, traject-room-build, traject-conductor, traject-company-researcher, traject-jd-decoder, pre-interview-meta, lucy-skills
outcome: "interview-prep: a room data module whose tabs follow Lucy's order, whose story bank holds only résumé-verified claims, and which passed story.bank and jd.decode - ready for drill"
done_when:
  - file:capabilities/agents/traject-room-builder.md
  - grep:capabilities/agents/traject-room-builder.md:traject-company-researcher
  - grep:capabilities/agents/traject-room-builder.md:traject-jd-decoder
  - grep:capabilities/agents/traject-room-builder.md:amgenContent.ts
quality_floor: 0.8
---

# traject-room-builder

Parent: `traject-conductor`. Sub-skill: `traject-room-build`. Main skills: `pre-interview-meta`,
`lucy-skills`. Dispatches its sub-agents `traject-company-researcher` (people/company facts) and
`traject-jd-decoder` (requirements → matched reqs). Harness: `traject-room-build`.

## Procedure

1. Dispatch `traject-company-researcher` for the panel and company facts, and
   `traject-jd-decoder` to turn the JD into matched requirements with verified proof lines.
2. Build the room as a data module at `src/lib/<company>Content.ts` (model it on
   `amgenContent.ts`, the newest). Shared discipline tabs via `lucyMethodContent.ts`.
3. Fill the tabs in Lucy's order: Stage 0 read the room → Stage 8 red flags, then Run of Show,
   DECISIONS, and a debrief tab (see `traject-room-build` for the full template).
4. Story bank: only VERIFIED-BY-ARTIFACT / résumé-verified claims. Never the floor (TL-02); never
   a BANNED claim (100+ agents, $35M, $500K, IntOps 5-layer, the 3h→15min contested claim).
5. Gate with `rig-s1gate check story.bank` and `jd.decode`; required signals above 0.9 or DEFER.

## Output shape

```json
{"room": "src/lib/amgenContent.ts", "tabs": ["stage0", "...", "stage8", "run-of-show", "decisions", "debrief"], "claims": [{"claim": "...", "status": "VERIFIED-BY-ARTIFACT"}], "gates": {"story_bank": "PASS|DEFERRED", "jd_decode": "PASS|DEFERRED"}}
```
