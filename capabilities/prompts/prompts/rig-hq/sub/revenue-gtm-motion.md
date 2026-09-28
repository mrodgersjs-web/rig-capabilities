---
id: rig-hq-sub-j8-gtm-motion
version: 1
status: draft
tier: sub
department: Revenue
agent: darius-gtm
parent: rig-hq-prompt-darius-gtm
task: Recurring sub-prompt (J8): run one revenue motion step — offer, list, sequence or scorecard
triggers: gtm motion, revenue step, work the pipeline, offers and outreach
sources: ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md (J8), ~/.rig/jake/aos/maps/aside-links/jtbd.json
provenance: first-party RIG design | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# GTM motion step (J8 recurring)

**Trigger.** Revenue work is requested: an offer, a list, a sequence, or a pipeline
scorecard.

**Typed inputs.** `step` (offer|list|sequence|scorecard), `source` (exact file/URL),
`buyer_segment`, `bar` (external anchor), `volume_cap`.

**Steps.**
1. Read the offer/ICP definition and the current pipeline state; dedupe before
   producing anything new.
2. Produce exactly one step's artifact with exact values and counts verified from the
   source file.
3. Judge quality against an external anchor (reply benchmarks, scoring tool), never
   against RIG's own past copy alone.
4. Record every outward step as HELD for Gate-D with exact recipients and text.

**Output format.**
```
STATUS: DONE | BLOCKED <reason>
Artifact: <path>
Counts: <n of n verified from source>
Bar: <external anchor + measured>
Gate-D held: <list or none>
```

**Expected output.** One motion step, countable and externally bar-checked.

**Done test.** Counts match the source file; the hold record is complete.

**Failure handling.** Source mismatch -> BLOCKED with the row numbers. Bar not met in
3 rounds -> `STATUS: BLOCKED bar-not-met`.

**Persistence.** Artifact + scoreboard entry saved; next step reads them first.

**Redaction.** Contact rows: names/emails as data, never credentials.

**Stop / escape hatch.** If the segment is unclear, ask — do not guess a list.
