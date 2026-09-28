---
id: rig-hq-sub-j7-1-an-interview-gets-booked
version: 1
status: draft
tier: sub
department: Career
agent: julie-job-search
parent: rig-hq-prompt-julie-job-search
task: Interrupt sub-prompt (J7): an interview gets booked — build the prep pack and run a mock
triggers: interview booked, interview prep, interview scheduled
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J7 interrupt 1), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J7 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: an interview gets booked

**Trigger.** An interview is confirmed (calendar invite or recruiter message).

**Typed inputs.** `role` (the packet version used), `interviewers`, `datetime`,
`format`.

**Steps.**
1. Build the prep pack: role/company research (sourced), the resume version sent
   (every claim verified), likely questions with evidenced answers, and the questions
   to ask them.
2. Run a mock interview round on a different model family; score answers against the
   same external bar used for the resume (median-of-3 style).
3. File the pack and set the follow-up (thank-you draft ready, held for send).

**Output format.**
```
STATUS: PACK READY <path>
Research: <claims -> sources>
Resume version: <v> (matches what was sent: yes/no)
Mock: <score> vs bar <anchor>
Follow-up draft: <path> — HELD for send
```

**Expected output.** Mike walks in with an evidenced prep pack.

**Done test.** Pack exists, mock score recorded, resume version matches the sent one.

**Failure handling.** Unverifiable company claim -> flagged in the pack, not repeated
as fact.

**Persistence.** Pack + mock record in the search folder; register updated.

**Redaction.** No recruiter contact credentials.

**Stop / escape hatch.** If the interview is in hours, prioritize pack completeness
over the mock and say so.
