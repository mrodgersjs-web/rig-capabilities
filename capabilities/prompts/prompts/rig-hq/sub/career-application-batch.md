---
id: rig-hq-sub-j7-application-batch
version: 1
status: draft
tier: sub
department: Career
agent: julie-job-search
parent: rig-hq-prompt-julie-job-search
task: Recurring sub-prompt (J7): one application batch — tailor, verify claims, receipt
triggers: application batch, apply to these roles, tailor the resume
sources: ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md (J7), ~/.rig/jake/aos/maps/aside-links/jtbd.json
provenance: first-party RIG design | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Application batch (J7 recurring)

**Trigger.** Roles are queued for application.

**Typed inputs.** `role_files` (exact paths/URLs), `resume_master`, `bar` (external
scorer, e.g. median-of-3 >= 90), `register_path`, `max_submissions`.

**Steps.**
1. Dedupe every role against the register first. This is Mike Rodgers' search, not
   James.
2. Tailor one packet per role; verify every claim against evidence (rule 3: no
   unverified claim ever ships).
3. Score each packet externally; iterate versions until the bar is met (the bar never
   drifts between rounds).
4. Record receipts for whatever is submitted (only after `APPROVE gd_*`), and date
   the next follow-up.

**Output format.**
```
STATUS: DONE | BLOCKED <reason>
Packets: <paths + versions>
External scores: <median-of-3 per packet>
Submitted: <n> (receipts: register rows)
Deduped/skipped: <n> — reasons
Next follow-ups: <dates>
```

**Expected output.** A truthful, bar-met, receipted batch.

**Done test.** Register rows exist for every submission; scores recorded per version.

**Failure handling.** Bar not met after 3 rounds -> `STATUS: BLOCKED bar-not-met`;
never lower the bar or invent a claim to pass.

**Persistence.** Register is the source of truth; packets keep immutable versions.

**Redaction.** No credentials; personal data stays in the packets folder.

**Stop / escape hatch.** A role with unverifiable requirements -> ask, or skip it
loudly — never fudge.
