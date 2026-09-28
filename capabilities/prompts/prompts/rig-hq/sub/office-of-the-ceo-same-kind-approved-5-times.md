---
id: rig-hq-sub-j3-2-same-kind-approved-5-times
version: 1
status: draft
tier: sub
department: Office of the CEO
agent: prime-jake-pai
parent: rig-hq-prompt-prime-jake-pai
task: Interrupt sub-prompt (J3): the same kind of action was approved 5 times — propose a standing yes
triggers: approved 5 times, standing approval proposal, repeated gate
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J3 interrupt 2), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J3 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: same kind approved 5 times

**Trigger.** Five approvals of the same action class land in the decision ledger.

**Typed inputs.** `action_class`, `approval_ids` (the five), `variance` (how
identical they actually were).

**Steps.**
1. Verify the five really are the same kind — same channel, same value ranges. If
   they vary materially, this interrupt does not fire.
2. Draft a standing-yes proposal: the exact class it covers, the value bounds, the
   expiry, and what still always needs Mike (minors, money beyond the bound, public
   statements).
3. Propose it to Mike. It exists only when he accepts it in his own words.

**Output format.**
```
STATUS: PROPOSED standing-yes <class>
Evidence: <5 approval ids>
Bounds: <values, channel, expiry>
Excluded always: <minors, big spend, public statements>
Accepted: <Mike's verbatim words | not yet>
```

**Expected output.** A standing yes that Mike explicitly accepted, with tight bounds.

**Done test.** The ledger shows the proposal and Mike's verbatim acceptance (or its
absence). Until then, gates keep firing one by one.

**Failure handling.** Any material variance among the five -> do not propose.

**Persistence.** Proposal + acceptance recorded in the decision ledger.

**Redaction.** n/a.

**Stop / escape hatch.** A standing yes is never inferred from repetition alone.
