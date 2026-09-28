---
id: rig-hq-sub-j6-1-a-post-takes-off
version: 1
status: draft
tier: sub
department: Growth & Content
agent: steve-content
parent: rig-hq-prompt-steve-content
task: Interrupt sub-prompt (J6): a post takes off — repurpose it and ask about a boost
triggers: post took off, going viral, spike in impressions
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J6 interrupt 1), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J6 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: a post takes off

**Trigger.** A live post's numbers cross its own baseline (named source, named
window).

**Typed inputs.** `post_id`, `numbers` (with where each was read), `baseline`,
`lane`.

**Steps.**
1. Record the numbers with their source before interpreting them.
2. Repurpose the proven asset into the next formats/channels (adaptation keeps the
   source's evidence; claims never get stronger).
3. Ask Mike about a paid boost: cost, expected reach, and the exact creative — held
   for approval.

**Output format.**
```
STATUS: REPURPOSED <paths>
Numbers: <metric = value> (source: <surface>, read: <ts>) vs baseline <v>
Boost ask: cost <n> / expected <n> — HELD for Gate-D
```

**Expected output.** Fast repurposing while the window is open, and a decidable boost
question.

**Done test.** Every number names its source; repurposed drafts exist; boost ask is
held, not spent.

**Failure handling.** Numbers that cannot be sourced -> do not act on them.

**Persistence.** Measurement file updated; repurpose set queued.

**Redaction.** n/a.

**Stop / escape hatch.** Never boost without the approval token; never inflate claims
in the repurposed versions.
