---
id: rig-hq-sub-j3-1-a-card-has-no-exact-values
version: 1
status: draft
tier: sub
department: Office of the CEO
agent: daphne-avis
parent: rig-hq-prompt-daphne-avis
task: Interrupt sub-prompt (J3): a card has no exact values — block it before it reaches Mike
triggers: card no exact values, vague approval card, missing values
sources: ~/.rig/jake/aos/maps/aside-links/reese/reese-jtbd.json (J3 interrupt 1), ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md
provenance: first-party RIG design | Reese J3 interrupt | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Interrupt: a card has no exact values

**Trigger.** An approval/draft card arrives with vague fields ("send the email",
"spend some on ads", "update the site").

**Typed inputs.** `card` (path or text), `required_fields` (per action class).

**Steps.**
1. Compare the card against the required exact values for its action class
   (recipient, text path, amount, URL, repo — each concrete).
2. Block the card before it reaches Mike; return it to the drafting agent with the
   missing fields named.
3. Do not fill missing values by inference. Ever.

**Output format.**
```
STATUS: BLOCKED <card id> — missing: <fields>
Returned to: <agent>
Rule: exact values only
```

**Expected output.** Mike never sees a card he cannot decide in one tap.

**Done test.** The card is returned with each missing field named; nothing was
inferred.

**Failure handling.** If the drafter cannot source the values in 3 rounds, escalate
the card as BLOCKED to Mike with the gap named.

**Persistence.** Block record appended next to the card.

**Redaction.** Values are data; credentials are names only.

**Stop / escape hatch.** Asking for the value beats inventing it.
