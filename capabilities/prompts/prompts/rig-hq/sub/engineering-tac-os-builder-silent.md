---
id: rig-hq-sub-j2-1-a-builder-goes-silent
version: 1
status: draft
tier: sub
department: Engineering (TAC OS)
agent: jordan-jr-ai-engineering
parent: rig-hq-prompt-jordan-jr-ai-engineering
task: Interrupt sub-prompt (J2): a builder goes silent — read its log, name the death cause, relaunch once on a probed lane
triggers: builder silent, worker stalled, no output, build hung
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J2 interrupt 1), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J2 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: a builder goes silent

**Trigger.** A builder produces no output beyond its expected cadence (no session log
growth, no artifact change).

**Typed inputs.** `builder_id`, `session_log` (path), `last_output_time`, `worktree`.

**Steps.**
1. Read the builder's session log tail; name the death cause from the evidence (crash
   line, provider error, stuck wait) — never guess from the tab title.
2. Check uncommitted work first: anything staged-but-unlanded is copied out and
   hashed before any relaunch (never tear down unlanded work).
3. Relaunch once, on a probed lane, pinned to the intended model. A second silence is
   a Windshield card, not another relaunch.

**Output format.**
```
STATUS: RELAUNCHED <builder> | ESCALATED
Death cause: <verbatim evidence line>
Unlanded work: <files + hashes | none>
Relaunch lane: <probed: yes/no>
Left to do: <items>
```

**Expected output.** A diagnosed cause and at most one clean relaunch.

**Done test.** The cause names a log line; unlanded work is accounted for; the
relaunch lane shows a real probe response.

**Failure handling.** Unknown cause -> ESCALATED with the logs attached.

**Persistence.** Diagnosis and relaunch record written to the build's status file.

**Redaction.** No credentials in log excerpts.

**Stop / escape hatch.** Never relaunch over unlanded work to save time.
