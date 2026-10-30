---
name: "rigds-stitch-rounds"
description: "JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Main skill of rig-design-studio for stitch rounds: screen specs, per-screen prompts, generated designs, per-screen status (STITCH-OK / PARTIAL / STITCH-R2-BLOCKED / BLOCKED), and R2 repair discipline. Use when generating or repairing screens after the board exists."
tier: main
parent: rig-design-studio
activation: "Load at the start of any task that generates screens from the board: writing DESIGN.md, writing per-screen prompts, running a stitch round, or repairing failed screens in R2."
owner: theo-design
status: Stable
acl: internal
outcome: "design-ux: a .stitch record with DESIGN.md, one prompt per screen, per-screen html/png/raw captures, a manifest with an honest status per screen, and exact error text preserved for any blocked screen"
done_when:
  - grep:capabilities/skills/rigds-stitch-rounds/SKILL.md:STITCH-R2-BLOCKED
  - grep:capabilities/skills/rigds-stitch-rounds/SKILL.md:rigds-manifest-merge
quality_floor: 0.6
great_example: corpus/examples/night-v2/stitch/DESIGN.md
---

# Stitch rounds

Round loop: `DESIGN.md` (spec) -> `prompts/screen-N-<slug>.md` (one per screen) -> `designs/<slug>.html`
+ `.png` + `raw-<slug>.json` -> `designs/manifest.json` (status per screen). Worked reference:
`corpus/examples/night-v2/stitch/` (5 screens, full record).

## Round discipline

1. **Spec first**: DESIGN.md fixes scope (screens, viewports, token set) before any generation.
2. **One prompt per screen**, self-contained: a prompt carries its own context because the consumer
   (or a future run) will not recall the conversation.
3. **Record everything a screen produces**: html, png capture, and the raw generation JSON. The raw
   JSON is what makes R2 repair and audits possible.
4. **Status per screen, exactly one**:
   - `STITCH-OK` — screen done and captured.
   - `PARTIAL` — usable but incomplete (name the gap in the manifest).
   - `STITCH-R2-BLOCKED` — repair round refused; manifest entry preserved WITH the exact error text.
   - `BLOCKED` — not attempted/removed; reason recorded.
5. **R2 repair**: rerun only failed/partial screens. Merge results through `rigds-manifest-merge` —
   failures keep the old entry; good entries are never overwritten by a failed round.

## Lessons from v1/v2 (binding)

- STITCH-R2-BLOCKED must preserve the manifest entry AND the exact error. Losing the error text loses
  the audit trail the next run needs.
- Round status is per screen, never per run: "5/5 STITCH-OK" and "3/5, one PARTIAL, one BLOCKED" both
  describe healthy runs if the statuses are honest.
- Supervisor log noise ("design-studio-serve failed exit 1") was a killed `http.server` artifact — a
  status change needs product evidence, not log tails.
- Screenshots of generated screens are real only if captured from the served/rendered artifact
  (rigds-capture-honesty).

Outward, paid or destructive steps stop at Gate-D.
