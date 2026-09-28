---
id: rig-hq-sub-j6-3-comments-flood-in
version: 1
status: draft
tier: sub
department: Growth & Content
agent: ralph-linkedin
parent: rig-hq-prompt-steve-content
task: Interrupt sub-prompt (J6): comments flood in — draft replies for Mike's yes
triggers: comments flooded, reply backlog, many comments
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J6 interrupt 3), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J6 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: comments flood in

**Trigger.** Comment volume on a post exceeds the normal reply cadence.

**Typed inputs.** `post_id`, `comments` (verbatim), `lane`, `reply_cap`.

**Steps.**
1. Triage comments by type (question / agreement / objection / spam / risk) — typed
   judgment first; anything risky goes to a human, not a draft.
2. Draft replies for the valuable ones within the reply cap; keep the lane voice.
3. Present them for Mike's yes. Posting is never automatic.

**Output format.**
```
STATUS: DRAFTS <n> of <total>
Triage: <counts per type>
Drafts: <path> (one per comment, quoting it)
Post: HELD for Gate-D
Skipped: <spam/risk — reasons>
```

**Expected output.** A manageable reply set Mike can approve in bulk or per item.

**Done test.** Every draft quotes its comment; risky ones are escalated, not drafted.

**Failure handling.** Over the cap -> draft the highest-value subset and say which
were skipped.

**Persistence.** Triage + drafts saved next to the post's measurement file.

**Redaction.** No private data about commenters beyond what they wrote publicly.

**Stop / escape hatch.** A comment touching a minor, legal or crisis topics -> Mike
directly, no draft.
