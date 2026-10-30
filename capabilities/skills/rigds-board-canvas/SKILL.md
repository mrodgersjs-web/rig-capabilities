---
name: "rigds-board-canvas"
description: "JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Main skill of rig-design-studio for the board canvas: Double Diamond board semantics — cards with kind labels, phases, upstream/downstream links, deviations in/out of budget, MASTER-CREATIVE-PROMPT v3.0 tokens. Use when setting up or editing the design board that every later stage exports from."
tier: main
parent: rig-design-studio
activation: "Load at the start of any task that creates or edits the design board: cards, phases, links, deviations, or the token set. Entered through rig-design-studio routing or the /design-studio flow."
owner: theo-design
status: Stable
acl: internal
outcome: "design-ux: a board canvas with kind-labelled cards per Double Diamond phase, explicit upstream/downstream links, computed deviations (min/max/outOfBudget), and the MASTER-CREATIVE-PROMPT v3.0 token set attached"
done_when:
  - grep:capabilities/skills/rigds-board-canvas/SKILL.md:MASTER-CREATIVE-PROMPT
  - grep:capabilities/skills/rigds-board-canvas/SKILL.md:rigds-example-pull
quality_floor: 0.6
great_example: corpus/examples/night-v2/board/seed.ts
---

# Board canvas

The board is the single source of truth for the run; stitch, handoff and verify all read from it.

## Semantics (fixed)

- **Cards**: each has a `kind` with a display `kindLabel`, a phase with a `phaseLabel`, and content.
  Kinds are stable vocabulary (insight, decision, constraint, screen, risk, ...) — a card without a
  kind is not exportable.
- **Phases**: Double Diamond stages (Discover, Define, Develop, Deliver). `counts{cards,links,phases}`
  in every export is derived from data, never typed.
- **Links**: directed `upstream` / `downstream` per card; a screen card traces to the insights and
  decisions that justify it.
- **Deviations**: measured against the token budget; `deviations{min,max,outOfBudget}` computed at
  export; out-of-budget cards are marked (`outOfBudget`) rather than hidden.
- **Tokens**: one token set, `MASTER-CREATIVE-PROMPT v3.0` = {colors, type, antiPatterns}. Anti-patterns
  are first-class: they travel with the handoff so builders can fail them.

## How to work it

1. Pull examples first (`rigds-example-pull`): the night-v2 board (`corpus/examples/night-v2/board/seed.ts`,
   16 cards / 20 links) is the worked reference for card and link shape.
2. Seed the board from evidence (research, audit, prior runs) — every card cites its source or is
   labelled own reasoning. RIG never claims a result, it CITES a result and supplies the reading.
3. Keep phases honest: a card sits where the work actually decided it, not where it looks best.
4. Before handing off, ensure counts and deviations derive from the data (rigds-export-check enforces).

## Lessons from v1/v2 (binding)

- Kind/phase labels are computed at serialization (`kindLabel`, `phaseLabel`) — the board stores ids,
  the export renders labels. Never store both and risk drift.
- `outOfBudget` is data, not an error: an out-of-budget card ships flagged so the builder sees the
  tradeoff the designer accepted.
- Links double as navigation for the builder: `upstream`/`downstream` on every serialized card is what
  makes the handoff readable without the app.

Outward, paid or destructive steps stop at Gate-D.
