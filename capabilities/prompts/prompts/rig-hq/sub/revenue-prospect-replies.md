---
id: rig-hq-sub-j8-1-a-prospect-replies
version: 1
status: draft
tier: sub
department: Revenue
agent: darius-sales
parent: rig-hq-prompt-darius-gtm
task: Interrupt sub-prompt (J8): a prospect replies — draft the answer and book the call only after Mike's yes
triggers: prospect reply, inbound reply, lead responded
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J8 interrupt 1), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J8 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: a prospect replies

**Trigger.** A prospect answers an outreach thread.

**Typed inputs.** `thread` (the reply text, verbatim), `account_context`, `offer`.

**Steps.**
1. Classify the reply (interested / question / objection / not-now / unsubscribe) —
   typed judgment first; DEFERRED to a human when unsure.
2. Draft the answer in the thread's own terms; quote their words back where it helps.
3. Propose the call slot and hold the send for Mike's yes. An unsubscribe stops the
   whole sequence for that contact immediately.

**Output format.**
```
STATUS: DRAFT REPLY (HELD FOR YES)
Class: <class>
Draft: <path> (or inline)
Their words: "<quoted>"
Proposed next step: <call slot / info send>
Send: HELD for Gate-D gd_<id>
```

**Expected output.** A reply draft Mike can approve in one tap.

**Done test.** The class is recorded, the draft quotes real thread text, the hold is
explicit.

**Failure handling.** Ambiguous reply -> class `human` and ask; never push a meeting
on a lukewarm thread.

**Persistence.** Thread state updated; next follow-up dated.

**Redaction.** Contact data as data; no credentials.

**Stop / escape hatch.** Booking happens after the yes, never before.
