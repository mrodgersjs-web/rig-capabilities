---
id: rig-hq-sub-j5-process-map
version: 1
status: draft
tier: sub
department: Intelligence
agent: iris-strategy
parent: rig-hq-prompt-iris-strategy
task: Recurring sub-prompt (J5): lay a fuzzy idea out as a visible, editable process map with its gaps named
triggers: process map, design it out visually, system map, canvas the process
sources: ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md (J5), ~/.rig/jake/aos/maps/aside-links/jtbd.json
provenance: first-party RIG design | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Process map (J5 recurring)

**Trigger.** An idea is fuzzy and needs to be laid out before anyone builds it
("design out the process, visually").

**Typed inputs.** `idea_text`, `boundaries` (in/out of scope), `stakeholders`,
`format` (markdown map, canvas, diagram).

**Steps.**
1. Draw the process as it would actually run: triggers, steps, owners, artifacts,
   decision points.
2. Mark every uncertain link as a red link; do not smooth over gaps.
3. Name what each step needs (input, tool, approval) so blockers are visible before
   build time.
4. Return the map in an editable format; iterate on it rather than rewriting.

**Output format.**
```
STATUS: DONE | BLOCKED <reason>
Map: <path>
Steps: <n> | Decisions: <n> | Red links: <n — list>
Out of scope: <list>
Next: <the one gap worth closing first>
```

**Expected output.** A map Mike can edit, with gaps visible.

**Done test.** Red links are enumerated; every step names its owner and artifact.

**Failure handling.** Unmappable idea -> BLOCKED with the ambiguity named; never draw
a confident map over missing structure.

**Persistence.** Map file saved; edits versioned in place.

**Redaction.** Strip secrets from any pasted config in the map.

**Stop / escape hatch.** Two plausible structures -> draw both briefly and ask.
