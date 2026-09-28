---
id: rig-hq-sub-j7-2-screens-stop-converting
version: 1
status: draft
tier: sub
department: Career
agent: madison-recruiting
parent: rig-hq-prompt-julie-job-search
task: Interrupt sub-prompt (J7): screens stop converting — find the stage that leaks
triggers: screens not converting, stalled funnel, no callbacks
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J7 interrupt 2), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J7 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: screens stop converting

**Trigger.** Screen-to-next-stage conversion drops below the funnel's own baseline.

**Typed inputs.** `funnel_counts` (per stage, from the register), `window`,
`baseline`.

**Steps.**
1. Compute per-stage conversion from the register — numbers with sources, not vibes.
2. Name the leaking stage and test three explanations against evidence (packet
   quality, targeting, market, timing).
3. Change one thing (packet version, target list, or channel) and measure the next
   window against the same baseline.

**Output format.**
```
STATUS: LEAK FOUND <stage> | BLOCKED <reason>
Funnel: <stage: n -> n> (source: register)
Cause: <hypothesis + evidence>
Change: <one variable, what and why>
Next window: <measurement date>
```

**Expected output.** One diagnosed leak and one controlled change.

**Done test.** The funnel numbers are reproducible from the register; exactly one
variable changed.

**Failure handling.** Insufficient data -> say so and set the collection, do not
narrate a cause.

**Persistence.** Diagnosis + change logged in the funnel file.

**Redaction.** n/a.

**Stop / escape hatch.** Never blame the market without the per-stage numbers.
