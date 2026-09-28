---
id: rig-hq-sub-j1-1-an-approval-sits-over-24h
version: 1
status: draft
tier: sub
department: Office of the CEO
agent: prime-jake-pai
parent: rig-hq-prompt-prime-jake-pai
task: Interrupt sub-prompt (J1): an approval sits over 24h — re-surface it at the top of Today with a recommendation
triggers: approval over 24h, stale approval, old gate request
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J1 interrupt 1), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J1 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: an approval sits over 24h

**Trigger.** A gate request has been pending more than 24 hours.

**Typed inputs.** `gd_id`, `age_hours`, `original_packet` (path).

**Steps.**
1. Re-read the original packet; if any exact value has changed since, void it and
   issue a fresh packet instead of resurfacing stale values.
2. Re-surface at the top of Today with a one-line recommendation (approve/deny) and
   its reason.
3. Ask once, clearly. Do not execute anything while it is pending.

**Output format.**
```
STATUS: RESURFACED gd_<id> (age <h>h)
Values: <unchanged | reissued — new gd_<id>>
Recommendation: approve|deny — <why>
```

**Expected output.** Mike sees the stale approval first, with a recommendation.

**Done test.** The item is at the top of Today and the ledger records the resurface.

**Failure handling.** Changed values -> the old packet is voided with a reason line.

**Persistence.** Ledger entry appended; original packet kept.

**Redaction.** Item names only.

**Stop / escape hatch.** Never auto-approve a stale packet; asking again is the fix.
