---
name: "rigds-manifest-merge"
description: "JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Sub-skill of rigds-stitch-rounds for manifest merge semantics after a failed or partial round: failures keep the old entry, STITCH-R2-BLOCKED preserves the entry plus the exact error, good entries are never overwritten. Use when merging any round result into designs/manifest.json."
tier: sub
parent: rigds-stitch-rounds
activation: "Load when a stitch round (R1 or R2) returns per-screen results that must be merged into the manifest, or when auditing an existing manifest for merge damage."
owner: theo-design
status: Stable
acl: internal
outcome: "design-ux: a manifest where every screen has exactly one honest status, prior good entries survive failed rounds, and every blocked screen carries its verbatim error text"
done_when:
  - grep:capabilities/skills/rigds-manifest-merge/SKILL.md:STITCH-R2-BLOCKED
  - grep:capabilities/skills/rigds-manifest-merge/SKILL.md:verbatim
quality_floor: 0.6
great_example: corpus/examples/night-v2/stitch/designs/manifest.json
---

# Manifest merge semantics

Merge rules, in order. These are invariants, not preferences:

1. **Failure keeps the old entry.** A failed/partial result never replaces a previously good entry.
   The manifest only ever moves a screen forward.
2. **STITCH-R2-BLOCKED preserves the entry AND the exact error text**, verbatim, alongside the status.
   The error is the audit trail; paraphrase destroys it.
3. **Good entries are immutable across rounds.** An `STITCH-OK` screen is not reopened by a later round
   that did not target it (R2 reruns failed screens only).
4. **raw-*.json is retained for every screen attempt** — the merge changes the manifest, never the
   raw record.
5. **Statuses are mutually exclusive and total**: exactly one of STITCH-OK / PARTIAL /
   STITCH-R2-BLOCKED / BLOCKED per screen at all times.

## Merge procedure

- Read the old manifest, read the round result, overlay per screen, read back the merged manifest and
  diff it: expect changes ONLY on screens the round targeted. (Overlay, then read back — a whole-object
  write with replace semantics silently drops sibling fields.)
- A screen that regressed to a worse status than it had is a merge bug unless the round explicitly
  targeted it; in that case the regression is recorded as a new attempt with its own raw JSON.

## Lessons from v1/v2 (binding)

- The v2 run's R2 repair worked because failed screens kept their entries and error text: the rerun
  prompt was rebuilt from the preserved error, not from memory.
- Any "merge" that can lose an entry needs a dry-run diff first; the diff is the proof the merge was
  surgical.

Outward, paid or destructive steps stop at Gate-D.
