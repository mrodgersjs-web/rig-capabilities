---
id: rig-hq-sub-j8-2-a-week-passes-with-no-reply
version: 1
status: draft
tier: sub
department: Revenue
agent: darius-gtm
parent: rig-hq-prompt-darius-gtm
task: Interrupt sub-prompt (J8): a week passes with no reply — change the offer or the list, not the volume
triggers: week no reply, dead sequence, no responses
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J8 interrupt 2), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J8 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: a week passes with no reply

**Trigger.** A sequence has run 7+ days with zero replies.

**Typed inputs.** `sequence_id`, `sent_count`, `offer_version`, `list_source`.

**Steps.**
1. Do NOT raise volume. Diagnose which of the three moved: offer, list fit, or copy.
2. Change ONE of them (offer wording, segment, or copy) and log the hypothesis.
3. Re-run the motion small; measure against the same external anchor; keep or revert
   the change based on the number.

**Output format.**
```
STATUS: CHANGED <offer|list|copy> — hypothesis: <one line>
Evidence: <sent n, replies 0, days n>
New artifact: <path>
Bar: <external anchor> — old <v> vs new <v>
```

**Expected output.** A testable change, not more noise.

**Done test.** Exactly one variable changed and the hypothesis is written before the
rerun.

**Failure handling.** Two dead iterations -> escalate the offer/segment question to
Mike instead of iterating blind.

**Persistence.** Scoreboard row updated with the hypothesis and outcome.

**Redaction.** n/a.

**Stop / escape hatch.** Volume is never the fix; if everything is unchanged and dead,
stop and ask.
